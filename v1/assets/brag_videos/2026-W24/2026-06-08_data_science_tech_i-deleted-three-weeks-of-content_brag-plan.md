# Brag Plan: "I Deleted Three Weeks of Content"

**Chosen hook:** *"git status said everything was fine. 188MB was already gone."*
**Hook formula:** Cold open (result-adjacent shock) + Negativity bias (the loss stated up front, false-safety dread)
**Tone preset:** cinematic
**Angle (one line):** One misread `filter-branch` path silently wipes three weeks of unbacked-up work from every commit; the video walks the 40-second gut-drop and the methodical reflog → dangling-commit → blob-extraction rescue as a quiet disaster-and-recovery arc.

---

## What is this?
Not an app — a personal/technical essay by a ten-year data scientist who ran a "standard repo hygiene" `git filter-branch` command, misread the path, and erased his entire `assets/` directory (188MB of production-ready content: slides, carousels, worksheets, blog images) from the repo's whole history. None of it was backed up externally. Working with Claude, he recovered every byte through three descending git-forensics layers. The brag is the recovery itself: real disaster, real byte-perfect rescue, and the humility of "I knew these layers existed and still would not have navigated them alone under pressure."

## The angle
A cinematic disaster-and-rescue arc, played straight. The essay's own dramatic structure IS the storyboard: the deceptively reasonable command → the silent wipe (`git status` shows nothing) → the 40-second gut-drop of the empty folder → then a calm, methodical descent through git's recovery layers (reflog, then `fsck --dangling`, then blob extraction) → full recovery, 188MB, byte-perfect. Specific to this piece, not generic: it uses the actual command, the actual `HEAD@{19}` / hash `6d30a69` reflog line, the actual dangling commit `f5d9a38`, and the real byte totals. The emotional turn — panic resolved by staying systematic — is the closing beat.

## Hook (first 2-3 seconds)
Full-bleed terminal-dark frame. The real destructive command sits on screen in monospace, calm and innocent-looking. Over it, the cold-open line lands in large cinematic type: **"git status said everything was fine."** — then a beat — **"188MB was already gone."** The command is the visual villain; the second line is the negativity-bias gut-punch. Holds the longest of any scene so both halves read completely.

## Key moments (the middle)
- **The silent wipe:** the `filter-branch` command on screen, then the `assets/` folder rendered empty — `git status` reporting "nothing wrong" while everything is already lost. The horror is the calm.
- **The reflog anchor:** `git reflog` output scrolls; the line **`HEAD@{19}: commit: feat: add week 2 content assets`** and hash **`6d30a69`** highlight — the last intact commit. `git checkout 6d30a69 -- assets/` → **"186MB came back."**
- **The forensics layer:** two PDFs still missing → `git fsck --dangling` surfaces one orphaned commit **`f5d9a38`** → blob extraction by hash restores the last two files. **"Byte-perfect."**

## Outro / punchline
Black frame. The count-up resolves: **"188MB. Everything."** Then the essay's real reframe, held clean: **"Staying systematic in someone else's crisis is a different skill than generating from scratch."** Beat. Small line: *"I'd been underestimating that use case."* Fade to black.

## User flow worth showing
none — no app or product flow. The centerpiece is a recreated **terminal/git session**: the destructive command, the empty folder, and the three recovery commands with their real output. This IS the "product doing its thing" equivalent — the recovery being performed on screen, command by command, is the strongest material.

## Tone
- Preset: cinematic
- Creative direction: a quiet technical disaster movie — trailer-scale gravity applied to a terminal
- Interpretation: 5 scenes, 3-5s each, dramatic reveals not quick cuts. Big monospace/type, full-bleed dark frames, significant scale on the numbers. Pacing is deliberate and weighted — the dread in the first half earns the relief in the second. No jokes, no chaos; the drama is real and played straight.

## Format: vertical — 1080x1920
## Duration: ~22s
Sits at the upper-middle of the window: the hook is a two-part line that needs full room, and three distinct recovery commands each need a readable beat. Scene durations below sum to 22s.

## Visual identity (from the DS/Tech niche + terminal subject)
- Background: near-black terminal `#0d1117` (GitHub-dark); card/panel `#161b22`
- Accent: loss/alarm amber-red `#f85149` for the wipe + "gone" beat; recovery green `#3fb950` for the "came back" / "byte-perfect" beats; cool blue `#58a6ff` for command highlights
- Text: `#e6edf3` (light grey-white); muted `#8b949e` for secondary/comment lines
- Display font: a heavy geometric sans (Inter / Space Grotesk 700) for the cinematic lines
- Mono font: a real code face (JetBrains Mono / SF Mono) for all terminal content — the commands and reflog output must look like a genuine terminal
- Strongest visual element: the recreated terminal itself — the destructive command, the empty `assets/` listing, and the reflog/fsck/blob commands with their real hashes and byte counts. Subtle scanline/grain + vignette for cinematic weight; the amber→green color shift carries the emotional arc.

## Share copy (draft)
I misread one git path and wiped 188MB of unbacked-up content from every commit in my repo's history. `git status` said everything was fine. Here's how reflog, dangling commits, and blob extraction brought all of it back — byte-perfect.

## Audio direction
- Role: cinematic support — a low, tense bed under the disaster half that resolves into something warmer/steadier under the recovery half
- Music: a restrained cinematic/ambient track with a low drone; a subtle swell at the "188MB was already gone" reveal, then a quieter, resolving progression through the recovery beats and a final settle under the outro
- Music treatment: enter low under the command, dip to near-silence on the "gone" beat (let the loss land in silence), rebuild gently as each recovery command succeeds, fade under the closing line so the words land last
- Music cue guidance: track/tempo to be selected at composition time. Target strong cues at (1) the two-part hook reveal ~1.8s, (2) the empty-folder "gone" moment, and (3) the "188MB. Everything." resolution. Beat-grid window for the three recovery commands: hold each command + its result to its read floor (~1.2s each), reveal them in sequence rather than snapping to a fast beat.
- Audio-reactive treatment: subtle — a faint terminal-glow/vignette breath on music energy; no waveform bars.
- SFX posture: sparse, motion-matched. A single dry keystroke/enter-thunk as the destructive command "runs"; a hollow low tone on the empty-folder reveal; a soft, clean confirmation tick as each recovery command restores files. Professional restraint — no stingers.
- Audio-coupled moments: the destructive command "executing" (enter-thunk); the empty-folder reveal (hollow drop); each of the three recovery commands succeeding (clean tick); the "188MB / Everything" count-up settle.
- Restraint rule: the "gone" beat must not be scored loud — the loss lands in near-silence, not on a hit. No comedic or triumphant SFX; the recovery is relief, not a victory lap.

## Storyboard

### Scene 1 — The reasonable command (hook) — 5.5s
Full-bleed `#0d1117` terminal. The real destructive command sits in mono, calm: `git filter-branch --index-filter 'git rm -rf --cached ... assets/' ... --all`. Cinematic line lands over/under it in two parts: **"git status said everything was fine."** (hold) → **"188MB was already gone."** ("gone" in alarm `#f85149`). Given the most room of any scene so both halves read.
Sequential/interaction: yes — the command appears, a keystroke/enter "runs" it, then the second line drops.
Audio intent: low tense bed enters under the command, dips toward silence as "gone" lands.
Audio-coupled idea: dry enter-thunk as the command runs; hollow low tone on "gone."
Music: tense low drone, restrained.
Transition mood: dramatic → Scene 2

### Scene 2 — The empty folder — 3.5s
The `assets/` directory rendered as an empty listing (or `ls assets/` returning nothing) with `git status` beside it reporting "nothing to commit, working tree clean." Muted `#8b949e` comment line: *"Three weeks of production work. Not backed up anywhere."* The dread beat — the calm is the horror.
Sequential/interaction: none — a held, still frame; the emptiness is the point.
Audio intent: near-silence; let the loss sit.
Audio-coupled idea: a single hollow drop as the empty listing settles, then quiet.
Music: dropped to near-silence.
Transition mood: slow, weighted crossfade → Scene 3

### Scene 3 — The reflog anchor — 4.5s
`git reflog` output scrolls in mono. The line **`HEAD@{19}: commit: feat: add week 2 content assets`** and hash **`6d30a69`** highlight in blue `#58a6ff`. Command types: `git checkout 6d30a69 -- assets/`. Result in green `#3fb950`: **"186MB came back."** The first turn from loss to hope.
Sequential/interaction: yes — reflog scrolls, the target line highlights, the checkout command runs, the "186MB" result confirms. Hold each to its read floor.
Audio intent: music begins its gentle rebuild; first note of relief.
Audio-coupled idea: clean confirmation tick as "186MB came back" lands.
Music: rebuilding, steadier.
Transition mood: clean → Scene 4

### Scene 4 — The forensics layer — 4.5s
Muted line: *"Two PDFs still missing."* Then `git fsck --dangling` surfaces one orphaned commit **`f5d9a38`** (highlighted). Blob extraction: `git cat-file blob <hash> > worksheet1.pdf`. Result green: **"Byte-perfect."** The deepest recovery layer — git's forensics, played as the methodical final descent.
Sequential/interaction: yes — the "still missing" line, then fsck reveals the dangling commit, then the blob command restores the files. Each held to read floor.
Audio intent: steady, resolving — the calm competence of working the problem.
Audio-coupled idea: clean tick on "Byte-perfect."
Music: resolved, warmer.
Transition mood: dramatic → Scene 5

### Scene 5 — What it actually was (outro) — 4s
Near-black frame. Count-up resolves large: **"188MB. Everything."** (green). Beat. The essay's real reframe in cinematic type: **"Staying systematic in someone else's crisis is a different skill than generating from scratch."** Small closing line, muted: *"I'd been underestimating that use case."* Fade to black.
Sequential/interaction: yes — the "188MB / Everything" count settles, then the reframe line lands, then the small closer.
Audio intent: bed settles and fades so the words land last.
Audio-coupled idea: soft count-up settle on "188MB. Everything."; then let it breathe.
Music: final settle, fade to near-silence under the closing line.
Transition mood: slow crossfade to end.

**Music mood for this video:** cinematic — tense low drone through the disaster half, resolving to a steadier, warmer progression through the recovery; not upbeat, not triumphant.
**Audio summary:** A low tense bed enters under the destructive command and dips to near-silence as the loss lands, then rebuilds gently with each successful recovery command and fades under the closing reframe so the last words carry alone.
