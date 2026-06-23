---
name: medium-stats-export
description: >
  Exports Medium.com account stats (views, reads, claps, earnings) to a CSV file
  using Chrome DevTools MCP via network interception — no DOM scraping, minimal
  token usage. Use this skill whenever the user wants to pull, export, download,
  or save their Medium stats, analytics, or article performance data. Triggers on
  phrases like "export my Medium stats", "get my Medium analytics", "save Medium
  data", or "monthly Medium report".
compatibility:
  tools: [mcp__chrome-devtools]
  requires: Chrome launched with --remote-debugging-port=9222
---

# Medium Stats Export

Exports your Medium account stats to a CSV by intercepting Medium's internal
API response — no DOM scraping, low token usage.

## Pre-flight Checklist

Before running, confirm:
- [ ] Chrome was launched with `chrome-debug` alias (port 9222)
- [ ] User is logged into Medium in that Chrome window
- [ ] `https://medium.com/me/stats` is open and **fully loaded**

If the page is not open yet, navigate there first and wait for it to load.

## Step-by-Step Instructions

### 1. Connect to Chrome DevTools
Connect to `localhost:9222` via the Chrome DevTools MCP.

### 2. Intercept the Stats API Response (preferred — lowest tokens)
Look in the Network tab for requests matching any of these patterns:
- `statsTotals`
- `/v1/stats`
- `_/api/users/` + `stats`
- `graphql` with operation name containing `stats`

Grab the **JSON response body** of the matching request. Do NOT read the page DOM.

### 3. Fallback — if page already loaded before interception
If the network request already fired and is not visible:
1. Reload the page (`Cmd+R` / `Ctrl+R`) via DevTools
2. Immediately watch the Network tab for the stats API call
3. Capture the response JSON

### 4. Parse and Export
From the JSON response, extract for each article:
- Title
- Views
- Reads
- Read ratio (reads/views)
- Claps
- Earnings (if available)
- Published date

Save as `medium-stats-YYYY-MM.csv` using the current month and year in the filename.

## Output Format

```
title,views,reads,read_ratio,claps,earnings,published_date
"My Article Title",1200,430,0.36,87,4.21,2024-11-03
...
```

## Token-Saving Rules

- **Never** read full page HTML or DOM
- **Always** target the network JSON response directly
- One prompt → one execution → file saved
- If the API path has changed, search Network tab filtered by "stats" or "api"

## Monthly Usage

Run this the same way each month:
1. `chrome-debug` to open Chrome
2. Log in to Medium, open `https://medium.com/me/stats`
3. Start Claude Code: `claude`
4. Say: **"Export my Medium stats to CSV"**

The skill handles the rest.
