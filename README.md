# Paper Boy

Automated morning newspaper generator for e-readers (Kobo, Kindle, etc).

Fetches news from RSS feeds, compiles them into a well-formatted EPUB, and delivers it to your e-reader via Google Drive. Use the **web app** for a visual experience or the **CLI** for automation.

## How It Works

1. Pick your sources from 40+ curated feeds or add your own RSS URLs
2. Build your newspaper — articles are extracted, images optimized for e-ink
3. Download the EPUB or deliver automatically to your Kobo via Google Drive

## Quick Start

### Web App (Recommended)

```bash
# Clone and install
git clone https://github.com/luclacombe/paper-boy.git
cd paper-boy
pip install -r web/requirements.txt

# Run the app
streamlit run web/app.py
```

The app walks you through setup with an onboarding wizard — pick your sources, configure delivery, and build your first edition.

### CLI

```bash
# Install
pip install -e .

# Copy and customize config
cp config.example.yaml config.yaml

# Build a newspaper locally
paper-boy build

# Build and deliver to Google Drive
paper-boy deliver
```

### Automated Daily Delivery (GitHub Actions)

This repo includes a workflow that runs at 6:00 AM UTC daily.

1. **Fork this repo** (or use it as-is)
2. **Set up Google Drive credentials** — see [Google Drive Setup](#google-drive-setup)
3. **Add the secret** to your repo: Settings > Secrets > Actions > `GOOGLE_CREDENTIALS`
4. **(Optional)** Commit a custom `config.yaml` to override the default feeds
5. The workflow runs automatically, or trigger it manually from the Actions tab

## Web App Features

- **Onboarding wizard** — 3-step setup: choose sources, configure delivery, build your first edition
- **Dashboard** — View today's edition status, trigger builds, download EPUBs
- **Source management** — Browse a curated catalog of 40+ feeds across 7 categories, or add custom RSS URLs
- **Starter bundles** — Morning Briefing, Tech & Science, Business & Finance
- **Delivery settings** — Configure Google Drive or local download, schedule, and newspaper preferences
- **Edition history** — Browse and download past editions

## Configuration

Copy `config.example.yaml` to `config.yaml` and customize:

```yaml
newspaper:
  title: "Morning Digest"
  language: "en"
  max_articles_per_feed: 10
  include_images: true

feeds:
  - name: "World News"
    url: "https://www.theguardian.com/world/rss"
  - name: "Technology"
    url: "https://feeds.arstechnica.com/arstechnica/index"

delivery:
  method: "google_drive"  # or "local"
  google_drive:
    folder_name: "Rakuten Kobo"
  keep_days: 30
```

## CLI Reference

```bash
paper-boy build                          # Build EPUB locally
paper-boy deliver                        # Build + deliver to Google Drive
paper-boy build --config my-config.yaml  # Use custom config
paper-boy build --output ./output/       # Custom output path
paper-boy -v build                       # Verbose logging
```

## Google Drive Setup

Paper Boy uses a Google service account to upload EPUBs to Google Drive.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or use an existing one)
3. Enable the **Google Drive API**
4. Create a **Service Account** (IAM & Admin > Service Accounts)
5. Create a JSON key for the service account
6. **Share your Google Drive folder** (e.g., "Rakuten Kobo") with the service account email
7. For GitHub Actions: add the JSON key contents as a repo secret named `GOOGLE_CREDENTIALS`
8. For local use: save the JSON file as `credentials.json` in the project root

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT
