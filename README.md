<h1 align="center">Impresario</h1>

<p align="center">
  <strong>Playwright's stage manager</strong>
</p>

<p align="center">
  Pulls strings. Raises curtains. Returns HTML.
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/github/v/tag/Valcrist/impresario?style=flat&label=version&color=brightgreen" alt="Version"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-polyform--nc-orange?style=flat" alt="License"></a>
  <a href="#"><img src="https://img.shields.io/github/languages/top/Valcrist/impresario?style=flat" alt="Top Language"></a>
  <a href="https://peps.python.org/pep-0008/"><img src="https://img.shields.io/badge/code%20style-pep8-73e?style=flat" alt="Code Style"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/req:python-3.10%2B-c47?style=flat" alt="Python Version"></a>
  <a href="https://github.com/Valcrist/impresario/activity"><img src="https://img.shields.io/badge/status-active-green?style=flat" alt="Status"></a>
</p>

---

## Overview

A FastAPI service that renders web pages via Playwright and returns the fully-rendered HTML - ideal for scraping JS-heavy sites that defeat plain HTTP clients.

POST a URL, get back rendered HTML. Impresario manages a single shared Firefox (gets flagged less than Chrome/Chromium) instance - starting it lazily on the first request, capping concurrency at 10 simultaneous tabs, and shutting it down automatically after 15 minutes of inactivity. If a request arrives after shutdown, the browser restarts transparently.

See [app/client.py](app/client.py) for a ready-made async client.

## Features

- **Playwright/Firefox rendering** - executes JS and waits for `domcontentloaded` before returning HTML
- **Concurrent page pool** - configurable max tabs (default: 10) via `asyncio.Semaphore`
- **Lazy browser init** - browser only starts on first request, not at startup
- **Idle auto-shutdown** - browser closes after a configurable idle period (default: 15 min) to free resources
- **API key auth** - all routes protected by `X-API-Key` header
- **Scalar API docs** - interactive docs at `/docs`

## Requirements

- Python 3.10+
- Firefox (installed by Playwright)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install firefox
```

## Configuration

Set these environment variables (defaults shown):

| Variable | Default | Description |
|---|---|---|
| `API_KEY` | *(required)* | Key for `X-API-Key` header auth |
| `API_PORT` | `8080` | Port the server listens on |
| `ENV` | `PROD` | `DEV` enables hot reload and request logging |
| `HOT_RELOAD` | `False` | Uvicorn hot reload (disabled when `ENV=PROD`) |
| `LOG_REQUESTS` | `False` | Log incoming requests in console (enabled when `ENV=DEV`) |
| `LOG_RESPONSE` | `False` | Log outgoing responses in console (enabled when `ENV=DEV`) |
| `MAX_TABS` | `10` | Max concurrent browser tabs (excess requests will wait) |
| `HEADLESS` | `False` | Run Firefox in headless mode (set to `True` for manual captcha, etc) |
| `IDLE_TIMEOUT` | `900` | Seconds before idle browser shutdown (browser restart done to minimize resource/RAM bloat) |

## Running

```bash
python api.py
```

Runs on port `8080` by default (`API_PORT`). Set `ENV=DEV` for development mode with hot reload (or set `HOT_RELOAD`, `LOG_REQUESTS`, and `LOG_RESPONSE` for granular control).

## API

### `POST /fetch`

Fetches a URL using a real browser and returns the rendered HTML.

**Headers**

```
X-API-Key: <your-api-key>
Content-Type: application/json
```

**Request body**

```json
{ "url": "https://example.com" }
```

**Response**

```json
{
  "url": "https://example.com",
  "status_code": 200,
  "title": "Example Domain",
  "html": "<!DOCTYPE html>..."
}
```

| Field | Type | Description |
|---|---|---|
| `url` | string | Final URL after any redirects |
| `status_code` | int | HTTP status code (`0` if navigation failed) |
| `title` | string | Page `<title>` |
| `html` | string | Full rendered HTML, parsed by BeautifulSoup |

## Usage

```python
from app.client import fetch

soup = await fetch("https://example.com")
title = soup.find("h1").text
```

See [app/client.py](app/client.py) for sample implementation.
