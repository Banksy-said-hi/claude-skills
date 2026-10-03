---
name: vid
description: Make a short, code-built motion-graphic film (teaser, launch, feature or explainer) for the current project, end to end - story, voiceover, music, sound effects, HTML/GSAP build on HyperFrames, measured quality bar, independent critic rounds, 1080p60 MP4. Flags set theme, scope, example, length, aspect, voice, music, footage model and more. Use when the user types /vid.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, Skill, Agent, WebFetch, WebSearch
---

Make one finished film without stopping for approval at each step: plan visibly, build, measure, get it judged, fix, deliver. Ask a question only when the project gives no way to infer the scope.

## Flags (all optional)

| Flag | Values | Default |
|---|---|---|
| `--scope` | `product` (the core value proposition) · `feature:<name>` · `launch` · `changelog` · `explainer:<topic>` | `product` |
| `--example` | the one tangible situation the film follows, e.g. `"friends buying a birthday gift"` | pick the most relatable one from the project |
| `--theme` | `match` (the project's production UI: its CSS, tokens, fonts) · `<named look>` (e.g. `win98`, `swiss`, `neo-brutalist`) · `palette:#hex,#hex;font:<name>` | `match` |
| `--mood` | the feeling to land, e.g. `playful`, `calm`, `bold`, `nostalgic` | inferred from the theme |
| `--length` | seconds, 10-60 | `25` |
| `--aspect` | `16:9` · `1:1` · `9:16` | from `--dest` |
| `--dest` | `x` · `linkedin` · `youtube` · `tiktok` · `instagram` · `site` | `x` (16:9) |
| `--fps` / `--res` | `30` · `60` / `1080` · `4k` | `60` / `1080` |
| `--voice` | `none` · `kokoro:<voice>` (local) · `heygen:<voice>` (signed in) · `file:<path>` | `kokoro:af_heart` |
| `--vo` | `auto` (write the script) · `"<verbatim script>"` | `auto` |
| `--music` | mood words · `none` · `mixkit:<id>` · `file:<path>` | from `--mood` |
| `--sfx` | `sparse` · `dense` · `none` | `sparse` |
| `--footage` | `none` (everything code-built) · `ai:<model>` (AI stills/clips for supporting shots, e.g. via an image/video MCP) | `none` |
| `--cta` | end-card line and link, e.g. `"Coming soon · example.com"` | from the project |
| `--truth` | `real` (only what exists) · `concept` (labelled concept film) | `real`; unbuilt features labelled "coming soon" |
| `--critics` | number of independent critic rounds, 0-4 | `2` |
| `--storyboard` | `yes` (show the plan and wait) · `no` | `no` |
| `--out` | output folder | `./videos/<slug>/` |

Echo the resolved flags as a one-line plan before starting.

## Pipeline

### 1 · Understand the project
Read the README, landing copy and core flows to state the value proposition in one sentence and list what actually exists vs what is planned (for `--truth`). With `--theme match`: find the production design system (global CSS, tokens, component library, font files) and plan to copy the real CSS and fonts into the film, not imitate them. Note the product's own wording and tagline.

### 2 · Brief and story
Write `BRIEF.md` (scope, example, message in one line, audience, destination, theme, truth rules). Then a storyboard table (time · viewer sees · job · what survives the cut · VO line):
- Arc: **hook** (frame 0 already a finished, familiar scene) → **challenge** (the pain, shown not told) → **turn** (the product arrives, visibly causing it) → **solution** beats (each action produces a result) → **payoff** (the outcome; unbuilt parts labelled) → **end card** (brand, line, CTA).
- One **persistent actor** (a window, card or object) carries the whole film; scenes change what happens to it.
- Name three **signature transformations** (e.g. "a message lifts out of the chat and becomes a list row").
- VO: about 2.3 words per second, short lines, one per beat; leave air on the turn.
With `--storyboard yes`, present it and wait; otherwise post it as a heads-up and continue.

### 3 · Tools
Check and install what is missing: `ffmpeg`, Node ≥ 22, Chrome, Python 3 with `numpy` + `scipy`. Scaffold with `npx hyperframes init <out> --example blank --non-interactive --resolution <preset>` and load the `hyperframes` skill family (`hyperframes`, `hyperframes-core`, `hyperframes-animation`); if an install command hangs, rerun it with `< /dev/null`. For `--voice kokoro:*`: `pip install kokoro-onnx soundfile` (use the same Python that has numpy). Copy GSAP, CSS and fonts into `assets/` so rendering never needs the network.

### 4 · Audio sourcing
- **Music** (`--music` words): human-made library music beats AI scores. For Mixkit, read tag pages' JSON-LD (`"name","genre","byArtist","url"`) to shortlist; avoid children's/ukulele/whistling stock unless asked. Download 3-6, then run `python3 <skill>/tools/music.py <file>`: it prints short-term loudness per second, tempo, and dead stops/drops. Pick a track that is steady from its first second, and choose the start offset so a drop lands on the turn beat. Credit the track.
- **Voiceover**: one file per line, `npx hyperframes tts "<line>" --voice <id> -o vo<N>.wav < /dev/null`; measure each with `ffprobe` and fit the storyboard to real durations.
- **Sound effects**: start from HyperFrames' bundled library (`media-use/audio/assets/sfx/`); screen with `python3 <skill>/tools/sfx_screen.py *.mp3` and drop boomy, hissy or long ones (a long one is fine once, e.g. a single confirmation chime). Sounds only on real actions; one soft whoosh per transition.

### 5 · Build
Read `composition.md` in this skill folder before writing HTML, then follow `hyperframes-core`'s contract. One composition, one paused GSAP timeline, the stage drawn at half size and scaled ×2 when the theme is pixel UI.

### 6 · Check frames
`npx hyperframes lint` (0 errors), `npx hyperframes check`, then `npx hyperframes snapshot --at <every beat midpoint and both sides of every cut>` and look at the contact sheets yourself. Fix what you see before rendering. Known false positives are listed in `composition.md`.

### 7 · Render and mix
- Render the silent picture: `npx hyperframes render --fps <fps> --quality delivery -o renders/picture.mp4`.
- Write `audio-plan.json` (format in `tools/mix.py`'s header): music file and offset, the VO lines with times, the sound effects with times and in-band lift.
- Run `python3 <skill>/tools/mix.py audio-plan.json renders/picture.mp4 renders/<slug>.mp4`. It ducks the music under the voice, levels each effect in its own frequency band, caps harsh 2-8 kHz lifts, masters to −14 LUFS with true peak ≤ −1 dBFS, and writes a `-no-sfx` version too.
- Save `renders/poster.png` from the payoff frame.

### 8 · Measure
`bash <skill>/tools/measure.sh renders/<slug>.mp4`. Bar: near-frozen time ≤ ~1 s per 30 s and no hold > 0.6 s except the end card; integrated −14 LUFS (±1) for social, true peak ≤ −1 dBFS, loudness range ≥ 3 LU; no near-silent gaps except the final fade. Fix and re-render until it passes.

### 9 · Critics (`--critics` rounds)
The builder never grades its own work. Each round spawns a **fresh** agent with the prompts in `critics.md`: round 1 the full-film critic, later rounds a verification critic given the previous findings. Give it only the MP4, the brief, the destination and the bar, never your reasoning. Fix the highest-impact items, re-render, re-measure, repeat. Stop at SHIP, at the round limit, or when what is left is cosmetic.

### 10 · Deliver
Write `review/LEDGER.md` (deliverables, credits and licences, each critic round → findings → changes → measured result). Open the master (`open` on macOS, `xdg-open` on Linux). Report: path, specs, the story in 5-7 lines, the measured numbers, what was not verified (e.g. nobody listened, last fixes checked only on frames), and the knobs worth changing next.

## Never
- Claim users, numbers, results or features that do not exist; label anything planned.
- Ship translucent double exposures at cuts, frames with an empty key window, or text that cannot be read at phone size where it carries the message.
- Use names, logos or footage of real brands or people the project does not own.
