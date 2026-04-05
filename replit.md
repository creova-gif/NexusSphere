# NexusSphere — Global Macro Terminal v3

## Overview

A two-page financial intelligence application served via Flask. Features live Wealthsimple trading via SnapTrade, auto-strategy engine, and personal investment advice.

## Routes

- `/` — NexusSphere Global Macro Terminal: full-featured financial terminal with market cycle engine, portfolio tracker, news & sentiment, risk analytics, tax/performance, goals, sandbox, earnings, quant models, prediction market bot, trading engine, and an embedded Big Mac Index tab.
- `/bigmac` — Standalone Big Mac Index Currency Valuation Explorer with interactive world map, bar chart view, trend comparisons, and country rankings.
- `/snap-callback` — SnapTrade OAuth callback (redirects back to the app after broker login).

## Architecture

- **Backend**: Flask (Python), `main.py` on port 5000
- **Frontend**: Two standalone HTML files, each self-contained with embedded CSS, JS, Chart.js, D3.js, TopoJSON
  - `static_nexussphere.html` — NexusSphere terminal (~10,600 lines)
  - `static_bigmac.html` — Big Mac Index explorer

## SnapTrade Integration (Wealthsimple Live Trading)

Requires two environment secrets: `SNAPTRADE_CLIENT_ID` and `SNAPTRADE_CONSUMER_KEY` (from app.snaptrade.com).

### Backend proxy routes (all in `main.py`):
| Route | Method | Purpose |
|---|---|---|
| `/api/snap/status` | GET | Check if credentials are configured |
| `/api/snap/register` | POST | Register a new SnapTrade user |
| `/api/snap/connect` | POST | Get Wealthsimple OAuth URL |
| `/api/snap/accounts` | GET | List user's brokerage accounts |
| `/api/snap/positions` | GET | Get all holdings |
| `/api/snap/balances` | GET | Get account balances |
| `/api/snap/activities` | GET | Get transaction history |
| `/api/snap/symbols` | GET | Symbol search (exchanges: NASDAQ/NYSE/TSX/ARCA) |
| `/api/snap/quote` | GET | Real-time quotes |
| `/api/snap/order/impact` | POST | Preview order (returns trade_id + estimated cost) |
| `/api/snap/order/place` | POST | Confirm order using trade_id |
| `/api/snap/order/force` | POST | Direct order without preview |
| `/api/snap/order/cancel` | POST | Cancel open order |
| `/api/snap/orders` | GET | List orders by state |

### Trading guardrails enforced:
- Max $2,000 CAD per order
- BUY and SELL only (no shorting)
- Preview required before every real order
- Max 30% portfolio concentration per security

## Features

- **Trading Engine tab**: Live Wealthsimple order ticket, auto-strategy rules engine, DCA scheduler, live order history
- **AI Assistant tab**: Personal TFSA advice for AMD/TSM/ORCL/PANW/PLTR/ENB holdings + AI chat
- **Portfolio Tracker**: Auto-populated from live Wealthsimple positions when connected
- **Market Terminal**: Stage classifier, macro tables, mixed Chart.js charts with volume + MA overlay
- **Big Mac Index**: D3.js world map + bar chart, 26 years of data, animated year slider

## Running

Workflow `Start application` runs `python main.py` on port 5000.

## Dependencies

Managed by uv/pyproject.toml. Key packages: `flask`, `requests`, `snaptrade-python-sdk`.
