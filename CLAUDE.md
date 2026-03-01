# Paper Boy

Automated morning newspaper generator for e-readers (Kobo, Kindle, etc).

## Project Overview

Paper Boy fetches news from RSS feeds, compiles them into a well-formatted EPUB with proper metadata, and delivers it to e-readers via Google Drive (Kobo). Available as both a **CLI tool** and a **Streamlit web app**.

- **CLI**: Build and deliver newspapers from the command line
- **Web App**: Visual interface with onboarding wizard, source management, build dashboard, and edition history
- **GitHub Actions**: Scheduled daily builds (6:00 AM UTC)

## Tech Stack

### Core Library
- **Python 3.9+** with `pyproject.toml` (PEP 621), built with setuptools
- **feedparser** — RSS/Atom feed parsing
- **trafilatura** — Article text extraction from URLs
- **ebooklib** — EPUB creation
- **Pillow** — Cover image generation
- **google-api-python-client + google-auth-oauthlib + google-auth-httplib2** — Google Drive upload
- **click** — CLI framework
- **pyyaml** — Config file parsing

### Web App
- **streamlit** — Web UI framework
- **requests** — GitHub Actions API integration

## Project Structure

```
src/paper_boy/                     # Core library + CLI
├── __init__.py                    # Package init (__version__)
├── cli.py                         # CLI entry point (click commands: build, deliver)
├── config.py                      # YAML config loading + validation (dataclasses)
├── feeds.py                       # RSS fetching + article text extraction + image optimization
├── epub.py                        # EPUB generation with metadata + embedded CSS
├── cover.py                       # Cover image generation (600x900px, Pillow)
├── delivery.py                    # Google Drive upload + old issue cleanup
└── main.py                        # Orchestration: fetch → build → deliver

web/                               # Streamlit web app
├── app.py                         # Main entry point + page routing
├── requirements.txt               # Web-specific dependencies
├── components/                    # Reusable UI components
│   ├── theme.py                   # CSS design system (newspaper aesthetic)
│   ├── masthead.py                # Newspaper header component
│   ├── navigation.py              # Horizontal nav bar
│   ├── cards.py                   # Status, headline, source, edition cards
│   └── loading.py                 # Empty states + build progress messages
├── pages/                         # Multi-page app
│   ├── landing.py                 # Intro page (pre-onboarding)
│   ├── onboarding.py              # 3-step setup wizard
│   ├── dashboard.py               # "Today's Edition" — build + status
│   ├── sources.py                 # "My Sources" — feed management
│   ├── delivery.py                # "Delivery" — settings
│   └── history.py                 # "Past Editions" — archive
├── services/                      # Backend logic
│   ├── database.py                # User config + history persistence (JSON)
│   ├── builder.py                 # Bridge to paper_boy build pipeline
│   ├── feed_catalog.py            # Curated feed library management
│   └── github_actions.py          # GitHub Actions workflow trigger + status
└── data/
    └── feed_catalog.yaml          # Curated feed catalog (40+ feeds, 7 categories)

.streamlit/
└── config.toml                    # Streamlit theme config (newspaper colors)

tests/
├── test_config.py                 # Config loading + validation tests
├── test_cover.py                  # Cover image generation tests
└── test_epub.py                   # EPUB creation + metadata tests

.github/workflows/
└── daily-news.yml                 # Daily cron (6:00 AM UTC) + manual dispatch
```

## Commands

```bash
# Install core library in development mode
pip install -e ".[dev]"

# Run Streamlit web app
pip install -r web/requirements.txt
streamlit run web/app.py

# CLI: Build newspaper locally
paper-boy build

# CLI: Build and deliver to Google Drive
paper-boy deliver

# CLI: Build with custom config
paper-boy build --config my-config.yaml --output ./output/

# CLI: Verbose logging
paper-boy -v build

# Run tests
pytest
```

## Conventions

- Core library source code lives in `src/paper_boy/`
- Web app source code lives in `web/`
- Web app dependencies are in `web/requirements.txt` (separate from `pyproject.toml`)
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

## Web App Architecture

### Page Flow
- **Not onboarded**: Landing → Onboarding (3-step wizard) → Dashboard
- **Onboarded**: Dashboard → Sources → Delivery → History (4-page nav)

### Onboarding Steps
1. Choose path (Free Sources vs Paid Subscriptions — only Free enabled)
2. Pick sources (starter bundles, category browsing, or custom RSS)
3. Configure delivery (method, schedule, newspaper settings)

### Services Layer
- `builder.py` bridges web UI config → `paper_boy.Config` → EPUB build
- `database.py` persists user config + delivery history as JSON files
- `feed_catalog.py` loads the curated feed catalog from `web/data/feed_catalog.yaml`
- `github_actions.py` provides infrastructure for triggering/monitoring GitHub Actions builds

### Design System
- Newspaper aesthetic: Playfair Display + Libre Baskerville (serif), Source Sans 3 (sans)
- Color palette: newsprint (#FAF8F5), ink (#1B1B1B), edition red (#C23B22)
- All CSS is in `web/components/theme.py`

## Key Design Decisions

- **EPUB format** for cloud delivery (Kobo native sync supports EPUB reliably)
- **Google Drive** as primary delivery (native Kobo integration, 15GB free)
- **Free RSS sources** for default config (Guardian, Ars Technica, NPR)
- **calibre:series metadata** included for NickelSeries mod compatibility
- **trafilatura** for full article extraction, with RSS content as fallback
- **Image optimization** in feeds.py — resize + JPEG compression for e-reader
- **Automatic cleanup** of old issues on Google Drive (`keep_days` config)
- **Streamlit web app** as the primary user-facing interface (CLI remains for automation)
- **Separate dependency specs** — web app has its own `requirements.txt`, core library uses `pyproject.toml`
- **JSON file persistence** for web app state (Phase 1), Supabase planned for Phase 1.5
- **Curated feed catalog** with 40+ feeds across 7 categories and 3 starter bundles
