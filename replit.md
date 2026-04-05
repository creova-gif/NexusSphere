# NexusSphere — Global Macro Terminal v2

## Overview

A two-page financial intelligence application served via Flask.

## Routes

- `/` — NexusSphere Global Macro Terminal: full-featured financial terminal with market cycle engine, portfolio tracker, news & sentiment, risk analytics, tax/performance, goals, sandbox, earnings, quant models, prediction market bot, and an embedded Big Mac Index tab.
- `/bigmac` — Standalone Big Mac Index Currency Valuation Explorer with interactive world map, bar chart view, trend comparisons, and country rankings.

## Architecture

- **Backend**: Flask (Python), `main.py` on port 5000
- **Frontend**: Two standalone HTML files, each self-contained with embedded CSS, JS, Chart.js, D3.js, and TopoJSON
  - `static_nexussphere.html` — 8868-line NexusSphere terminal
  - `static_bigmac.html` — 1286-line Big Mac Index explorer

## Running

The workflow `Start application` runs `python main.py` on port 5000.
