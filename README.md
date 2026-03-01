# Paper Boy

Automated morning newspaper generator for e-readers (Kobo, Kindle, etc).

Fetches news from RSS feeds, compiles them into a well-formatted EPUB, and delivers it to your e-reader via Google Drive. Designed to run daily as a GitHub Actions workflow.

## How It Works

1. Fetches articles from configured RSS feeds
2. Extracts full article text using [trafilatura](https://github.com/adbar/trafilatura)
3. Optimizes images for e-ink displays
4. Generates an EPUB with a custom cover, table of contents, and embedded CSS
5. Uploads to Google Drive (syncs automatically to Kobo via built-in integration)
6. Cleans up old issues

## Quick Start

### Local Usage

```bash
# Clone and install
git clone https://github.com/luclacombe/paper-boy.git
cd paper-boy
pip install -e .

# Copy and customize config
cp config.example.yaml config.yaml
# Edit config.yaml with your preferred feeds

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
