"""Delivery backends — upload generated EPUB to cloud storage."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from paper_boy.config import Config

logger = logging.getLogger(__name__)


def deliver(epub_path: Path, config: Config) -> None:
    """Deliver the generated EPUB using the configured method."""
    method = config.delivery.method

    if method == "google_drive":
        deliver_google_drive(epub_path, config)
    elif method == "email":
        deliver_email(epub_path, config)
    elif method == "local":
        logger.info("Local delivery: file at %s", epub_path)
    else:
        raise ValueError(f"Unknown delivery method: {method}")


def deliver_google_drive(epub_path: Path, config: Config) -> None:
    """Upload EPUB to Google Drive 'Rakuten Kobo' folder."""
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        raise RuntimeError(
            "Google Drive libraries not installed. "
            "Install with: pip install google-api-python-client google-auth-oauthlib"
        )

    creds = _get_google_credentials(config)
    service = build("drive", "v3", credentials=creds)

    # Find or create the target folder
    folder_name = config.delivery.google_drive.folder_name
    folder_id = _find_or_create_folder(service, folder_name)

    # Upload the EPUB
    file_metadata = {
        "name": epub_path.name,
        "parents": [folder_id],
    }
    media = MediaFileUpload(
        str(epub_path),
        mimetype="application/epub+zip",
        resumable=True,
    )

    uploaded = service.files().create(
        body=file_metadata, media_body=media, fields="id,name"
    ).execute()

    logger.info(
        "Uploaded %s to Google Drive folder '%s' (id: %s)",
        uploaded["name"],
        folder_name,
        uploaded["id"],
    )

    # Clean up old issues
    _cleanup_old_issues(service, folder_id, config.delivery.keep_days)


def deliver_email(epub_path: Path, config: Config) -> None:
    """Send EPUB via email (Send-to-Kindle, etc.)."""
    import smtplib
    from email import encoders
    from email.mime.base import MIMEBase
    from email.mime.multipart import MIMEMultipart

    email_cfg = config.delivery.email
    if not email_cfg.sender or not email_cfg.recipient:
        raise ValueError(
            "Email delivery requires sender and recipient addresses. "
            "Configure these in your delivery settings."
        )
    if not email_cfg.password:
        raise ValueError(
            "Email delivery requires an app password for the sender account."
        )

    msg = MIMEMultipart()
    msg["From"] = email_cfg.sender
    msg["To"] = email_cfg.recipient
    msg["Subject"] = config.newspaper.title

    part = MIMEBase("application", "epub+zip")
    with open(epub_path, "rb") as f:
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f'attachment; filename="{epub_path.name}"',
    )
    msg.attach(part)

    with smtplib.SMTP_SSL(email_cfg.smtp_host, email_cfg.smtp_port) as server:
        server.login(email_cfg.sender, email_cfg.password)
        server.send_message(msg)

    logger.info(
        "Emailed %s to %s via %s",
        epub_path.name,
        email_cfg.recipient,
        email_cfg.smtp_host,
    )


def _get_google_credentials(config: Config):
    """Get Google service account credentials from file or environment."""
    from google.oauth2 import service_account

    scopes = ["https://www.googleapis.com/auth/drive.file"]

    # Check for credentials in environment variable (GitHub Actions)
    env_creds = os.environ.get("GOOGLE_CREDENTIALS")
    if env_creds:
        info = json.loads(env_creds)
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)

    # Fall back to credentials file
    creds_path = Path(config.delivery.google_drive.credentials_file)
    if creds_path.exists():
        return service_account.Credentials.from_service_account_file(
            str(creds_path), scopes=scopes
        )

    raise FileNotFoundError(
        "Google credentials not found. Either set the GOOGLE_CREDENTIALS "
        "environment variable or provide a credentials_file in config."
    )


def _find_or_create_folder(service, folder_name: str) -> str:
    """Find an existing folder by name, or create it."""
    query = (
        f"name = '{folder_name}' "
        f"and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if folders:
        folder_id = folders[0]["id"]
        logger.debug("Found existing folder '%s' (id: %s)", folder_name, folder_id)
        return folder_id

    # Create the folder
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    folder_id = folder["id"]
    logger.info("Created folder '%s' (id: %s)", folder_name, folder_id)
    return folder_id


def _cleanup_old_issues(service, folder_id: str, keep_days: int) -> None:
    """Remove Paper Boy EPUBs older than keep_days from the folder."""
    if keep_days <= 0:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=keep_days)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S")

    query = (
        f"'{folder_id}' in parents "
        f"and name contains 'paper-boy-' "
        f"and mimeType = 'application/epub+zip' "
        f"and createdTime < '{cutoff_str}' "
        f"and trashed = false"
    )

    results = service.files().list(q=query, fields="files(id, name)").execute()
    old_files = results.get("files", [])

    for f in old_files:
        service.files().delete(fileId=f["id"]).execute()
        logger.info("Cleaned up old issue: %s", f["name"])

    if old_files:
        logger.info("Removed %d old issue(s)", len(old_files))
