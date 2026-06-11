# Recording Guide — Talking-Head Videos (Life, Poetry, DS)

## Physical Setup

```
[MONITOR — eye level, teleprompter full-screen]
      ↑
[iPhone — tripod, between you and monitor, slightly below eye line]
      ↑
[You — 2-3 feet back, head + chest in frame, 20% headroom]
```

- iPhone 15 Pro Max on tripod, mounted between you and monitor
- Eye contact with camera = looking at monitor naturally
- Move 3-4 feet from background for natural depth separation

---

## Pre-Record Checklist (2 min)

- [ ] Generate teleprompter: `python3 scripts/generate_teleprompter.py --script content/scripts/[slug]_yt.md --open`
- [ ] Teleprompter open full-screen on monitor — adjust speed with `↑↓`, test scroll before hitting record
- [ ] Lark M2 receiver → iPhone USB-C
- [ ] iPhone: Do Not Disturb ON
- [ ] iPhone: Auto-Lock → Never (`Settings → Display & Brightness → Auto-Lock`)
- [ ] iPhone camera: 4K 30fps, standard video (not cinematic mode)
- [ ] QuickTime on Mac → New Movie Recording → select iPhone as source → confirm framing
- [ ] Speak a few words — check Lark M2 LED is green

---

## Recording

1. Hit record on iPhone
2. Pause 3 seconds silent before speaking — edit handle
3. Read at ~130 wpm, natural pace
4. Clap once at every `[PAUSE]` marker — creates visible audio spike for editor
5. `[BROLL:]` markers — keep talking, don't stop (editor handles cutaway)
6. Flub a line → clap once, pause 2s, repeat from sentence start (don't restart whole take)
7. Pause 3 seconds silent at end before stopping

---

## Post-Record

- iPhone: Auto-Lock → back to normal
- Transfer via AirDrop or USB → `assets/raw/[slug].mov`
- Record Life first, Poetry second — same session while setup is live

---

## File Output

| Niche | Save to |
|-------|---------|
| Life | `assets/raw/[life_slug].mov` |
| Poetry | `assets/raw/[poetry_slug].mov` |
| DS (talking-head) | `assets/raw/[ds_slug].mov` |
| DS (screen) | `assets/raw/[ds_slug]_screen.mov` |

Next step after recording: `docs/saturday.md` (auto-edit + captions)
