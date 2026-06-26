# launchd — Daily Ideas Pipeline

Daily 6am pull from all free trending sources → rescore → `data/ideas/weekly_ideas.md`.

## What it runs

`scripts/daily_ideas.sh` chains:
1. `rss_scraper.py` — Reddit (26 subs across 3 niches)
2. `youtube_scraper.py` — niche channel scraping
3. `fetch_external_feeds.py` — HN + arXiv + Medium tags + DEV.to + GitHub trending + Goodreads + poets.org
4. `fetch_google_suggest.py --quick` — Google + YouTube autocomplete
5. `idea_scorer.py` — rescore + rewrite `weekly_ideas.md`

Each step independent: failure of one doesn't stop pipeline (`set -uo pipefail`, no `-e`).

## Install

```bash
cp docs/com.contentmachine.dailyideas.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.contentmachine.dailyideas.plist
launchctl list | grep dailyideas
```

## Verify

```bash
# Force-run now (skips schedule):
launchctl start com.contentmachine.dailyideas

# Check logs:
tail -50 /tmp/daily_ideas.log
tail -50 /tmp/daily_ideas.error.log

# Inspect outputs:
ls -la data/ideas/
cat data/ideas/weekly_ideas.md | head -40
```

## Uninstall

```bash
launchctl unload ~/Library/LaunchAgents/com.contentmachine.dailyideas.plist
rm ~/Library/LaunchAgents/com.contentmachine.dailyideas.plist
```

## Modify schedule

Edit `Hour`/`Minute` in plist, then:
```bash
launchctl unload ~/Library/LaunchAgents/com.contentmachine.dailyideas.plist
launchctl load ~/Library/LaunchAgents/com.contentmachine.dailyideas.plist
```

## Notes

- Python path hardcoded to `miniconda3/envs/content_engine_env/bin/python3.14` (matches `com.contentmachine.buildkb`). Wrapper falls back to `python3` if missing.
- `data/analytics/` used for any in-script logs; stdout/stderr → `/tmp/daily_ideas*.log`.
- Mac sleep: launchd skips fire if Mac asleep at 6am. Use `pmset` to wake or `StartInterval` instead if needed.
