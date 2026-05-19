# Zemail Dashboard

Real-time web dashboard for monitoring zemail Gmail semantic search indexing progress.

## Features

- **Live Sync Monitoring** — Track email indexing progress in real-time
- **TKE Design System** — 19 curated themes, light/dark mode, consistent with TKE MCP
- **Multi-Section Navigation** — Dashboard, Logs, Settings, API Status, Vector DB, Changelog
- **Responsive** — Works on desktop, tablet, and mobile
- **Zero Dependencies** — Pure HTML/CSS/JS frontend, Python stdlib backend

## Quick Start

```bash
# Start the dashboard server
python3 server.py 8080

# Or with custom zemail data directory
ZEMAIL_DATA_DIR=/path/to/zemail/data python3 server.py 8080
```

Access at `http://localhost:8080` or via Tailscale at `http://100.106.122.86:8080`.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `ZEMAIL_DATA_DIR` | `~/.zemail` | Path to zemail data (state, logs, PIDs) |

## Dashboard Sections

- **Dashboard** — Live stats, progress bar, indexing velocity chart
- **Sync Logs** — Real-time log viewer with syntax highlighting
- **Settings** — Sync configuration (batch size, models, sleep times)
- **API Status** — Gmail, ZeroEntropy, Qdrant health indicators
- **Vector DB** — Qdrant collection status and point count
- **Changelog** — Version history and feature updates

## Theme System

19 curated themes across 6 categories:
- **TKE Core** — Branded, Ocean Breeze, Northern Lights, Mocha Mousse, Nature
- **Clean & Minimal** — Modern Minimal, Mono
- **Rich & Atmospheric** — Cosmic Night, Starry Night, Darkmatter
- **Bold & Vibrant** — Cyberpunk, Neo Brutalism, Bold Tech
- **Colorful & Playful** — Quantum Rose, Candyland
- **Warm & Inviting** — Sunset Horizon
- **Character & Craft** — Matrix, Catppuccin, Vintage Paper

Click the **Theme** button in the header to switch. Preferences persist in localStorage.

## Architecture

```
zemail-dashboard/
├── index.html      # Self-contained frontend (all CSS/JS inline)
├── server.py       # Python HTTP server + API endpoint
└── README.md       # This file
```

The frontend is a single HTML file with no external dependencies. It fetches `/api/status` every 30 seconds for live updates.

The backend reads zemail sync state from:
- `full_sync_state.json` — batch/page progress
- `full_sync_v2.log` — live log tail
- `full_sync_v2.pid` — process status

## Integration with zemail

This dashboard is designed to work alongside the [zemail](https://github.com/zeroentropy-ai/zemail) Gmail semantic search tool. It monitors the sync process and provides visibility into indexing progress.

## License

Internal use at The Kidney Experts, PLLC.
