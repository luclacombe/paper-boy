# Paper Boy

Automated morning newspaper generator for e-readers (Kobo, Kindle, etc).

## Project Overview

Paper Boy fetches news from RSS feeds, compiles them into a well-formatted EPUB with proper metadata, and delivers it to e-readers via Google Drive (Kobo). Designed to run as a GitHub Actions workflow on a daily schedule (6:00 AM UTC).

## Tech Stack

- **Python 3.9+** with `pyproject.toml` (PEP 621), built with setuptools
- **feedparser** — RSS/Atom feed parsing
- **trafilatura** — Article text extraction from URLs
- **ebooklib** — EPUB creation
- **Pillow** — Cover image generation
- **google-api-python-client + google-auth-oauthlib + google-auth-httplib2** — Google Drive upload
- **click** — CLI framework
- **pyyaml** — Config file parsing

## Project Structure

```
src/paper_boy/
├── __init__.py        # Package init (__version__)
├── cli.py             # CLI entry point (click commands: build, deliver)
├── config.py          # YAML config loading + validation (dataclasses)
├── feeds.py           # RSS fetching + article text extraction + image optimization
├── epub.py            # EPUB generation with metadata + embedded CSS
├── cover.py           # Cover image generation (600x900px, Pillow)
├── delivery.py        # Google Drive upload + old issue cleanup
└── main.py            # Orchestration: fetch → build → deliver

tests/
├── test_config.py     # Config loading + validation tests
├── test_cover.py      # Cover image generation tests
└── test_epub.py       # EPUB creation + metadata tests

.github/workflows/
└── daily-news.yml     # Daily cron (6:00 AM UTC) + manual dispatch
```

## Commands

```bash
# Install in development mode
pip install -e ".[dev]"

# Build newspaper locally
paper-boy build

# Build and deliver to Google Drive
paper-boy deliver

# Build with custom config
paper-boy build --config my-config.yaml --output ./output/

# Verbose logging
paper-boy -v build

# Run tests
pytest
```

## Conventions

- All source code lives in `src/paper_boy/`
- Config is YAML-based (`config.yaml`, see `config.example.yaml`)
- EPUB metadata uses `calibre:series` for Kobo series grouping
- EPUB3 standard series metadata also included
- Cover images are 600x900px, generated with Pillow
- Google Drive delivery targets the "Rakuten Kobo" folder
- Google credentials: `GOOGLE_CREDENTIALS` env var (GitHub Actions) or `credentials.json` file (local)
- GitHub Actions secrets store credentials (never commit secrets)
- Tests use pytest, located in `tests/`
- Imports use the `paper_boy` package namespace
- Delivery methods implemented: `google_drive`, `local`

## Key Design Decisions

- **EPUB format** for cloud delivery (Kobo native sync supports EPUB reliably)
- **Google Drive** as primary delivery (native Kobo integration, 15GB free)
- **Free RSS sources** for default config (Guardian, Ars Technica, NPR)
- **calibre:series metadata** included for NickelSeries mod compatibility
- **trafilatura** for full article extraction, with RSS content as fallback
- **Image optimization** in feeds.py — resize + JPEG compression for e-reader
- **Automatic cleanup** of old issues on Google Drive (`keep_days` config)
- **No paywall handling in MVP** — future enhancement with cookie/Playwright auth
