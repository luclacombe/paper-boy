# Security

## Reporting Vulnerabilities

If you discover a security vulnerability, please report it privately by opening a [GitHub security advisory](https://github.com/your-username/paper-boy/security/advisories/new) on this repository. Do **not** open a public issue.

## Sensitive Files

Paper Boy stores credentials locally. These files are gitignored and must never be committed:

| File | Contains |
|---|---|
| `config.yaml` | SMTP password, email addresses |
| `.streamlit/secrets.toml` | Google OAuth client ID and secret |
| `credentials.json` / `client_secret*.json` | Google service account or OAuth credentials |
| `user_config.json` | OAuth refresh tokens, email settings |
| `delivery_history.json` | Delivery log with email addresses |

## Local Token Storage

OAuth2 tokens (including `refresh_token`, `client_id`, and `client_secret`) are stored as plain JSON in `user_config.json`. This is the same trust model used by tools like `gcloud` CLI (`~/.config/gcloud/`). Anyone with read access to this file can act as your Google account within the granted scopes (`drive.file`, `gmail.send`).

To revoke access at any time:
1. Go to https://myaccount.google.com/permissions
2. Find the Paper Boy app and click **Remove Access**

## Scope of Access

Paper Boy requests the minimum Google OAuth scopes needed:

- **`drive.file`** — can only access files it creates (not your entire Drive)
- **`gmail.send`** — can send email as you (used for Send-to-Kindle delivery only)

## Best Practices

- Never commit `config.yaml`, `secrets.toml`, or `user_config.json`
- Use Gmail App Passwords instead of your main Google password for SMTP
- Review connected apps periodically at https://myaccount.google.com/permissions
- If you fork this repo, check that `.gitignore` is intact before pushing
