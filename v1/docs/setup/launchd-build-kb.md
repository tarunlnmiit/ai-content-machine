# launchd: build_knowledge_base Weekly Job

Plist: `~/Library/LaunchAgents/com.contentmachine.buildkb.plist`  
Script: `scripts/build_knowledge_base.py`  
Schedule: Every Sunday at 22:00 local time (Asia/Calcutta)

---

## Load / Unload

```bash
# Load (register + enable on login)
launchctl load ~/Library/LaunchAgents/com.contentmachine.buildkb.plist

# Unload (disable, stop if running)
launchctl unload ~/Library/LaunchAgents/com.contentmachine.buildkb.plist
```

## Run / Stop

```bash
# Trigger immediately (without waiting for schedule)
launchctl start com.contentmachine.buildkb

# Kill a running instance
launchctl stop com.contentmachine.buildkb
```

## Status / Debug

```bash
# Check if registered (shows PID if running, last exit code)
launchctl list | grep contentmachine

# Full job info (last exit status, PID, etc.)
launchctl list com.contentmachine.buildkb

# Watch live output
tail -f /tmp/build_kb.log

# Watch live errors
tail -f /tmp/build_kb.error.log

# Both at once
tail -f /tmp/build_kb.log /tmp/build_kb.error.log
```

Exit code `0` = success. Non-zero = check error log.

## Edit Schedule

Open plist and change `StartCalendarInterval`:

```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Weekday</key>   <!-- 0=Sun 1=Mon … 6=Sat -->
    <integer>0</integer>
    <key>Hour</key>      <!-- 24h local time -->
    <integer>22</integer>
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

After editing, reload:

```bash
launchctl unload ~/Library/LaunchAgents/com.contentmachine.buildkb.plist
launchctl load   ~/Library/LaunchAgents/com.contentmachine.buildkb.plist
```

## Pass CLI Flags

Edit `ProgramArguments` in plist to pass flags like `--engine claude` or `--skip youtube`:

```xml
<key>ProgramArguments</key>
<array>
    <string>/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14</string>
    <string>/Users/tarungupta/Making It Big/Claude/content-machine/scripts/build_knowledge_base.py</string>
    <string>--engine</string>
    <string>claude</string>
</array>
```

Reload after any plist change.

## Permanently Delete

```bash
launchctl unload ~/Library/LaunchAgents/com.contentmachine.buildkb.plist
rm ~/Library/LaunchAgents/com.contentmachine.buildkb.plist
```

## Notes

- Job only fires when Mac is awake and logged in. If Mac is asleep Sunday 22:00, job is skipped (not queued).
- To run even when no user is logged in, move plist to `/Library/LaunchDaemons/` and load with `sudo`.
- Logs are overwritten each run (not appended). Redirect with `>>` if history needed.
