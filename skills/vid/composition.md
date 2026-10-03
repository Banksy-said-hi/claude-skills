# Building the composition

Rules learned from building and critiquing real films. Follow them on the first pass; each one cost a round when it was missed.

## Structure
- One standalone `index.html` with one root `data-composition-id`, a root `data-duration`, and one full-length `class="clip"` stage. `window.__timelines[id] = tl` only after the whole timeline is built.
- Pixel UI themes (98.css-style): draw the stage at 960x540 inside a `#scaler` with a static CSS `transform: scale(2)`, so every UI pixel lands on exactly two. Inside it, a `#camera` (animated: push, pan) and a `#world`. Never tween the element that carries the static CSS transform.
- Copy the production CSS and fonts into `assets/` and declare every `font-family` with an in-file `@font-face` (emoji: `src: local('Apple Color Emoji')`). If the CSS references its fonts relatively, put the font files next to it.
- 98.css-style buttons draw labels as transparent text plus a shadow: override with `button { color: #222 !important; text-shadow: none !important; }` so checks and renders agree.

## Determinism (renders seek frames out of order in parallel)
- Every text change and on/off state comes from one pure function of time, `state(t)`, driven by a single tween: `tl.fromTo(clock, {t: 0}, {t: END, duration: END, ease: 'none', onUpdate: () => state(clock.t)}, 0)`. Counters, labels, class toggles and badges go there. No `tl.call()` for state.
- Several `fromTo` calls on the same target: give every one but the earliest `immediateRender: false`. Avoid overlapping tweens on the same property.
- Measure layout (`getBoundingClientRect`) once at build time, with the target layout temporarily applied via `gsap.set` and then reset, to hand objects across scenes at exact coordinates.
- No `Math.random`, no `Date.now`, no network.

## Retiming without rewriting
Write positions as `F(t)` with one remap function, e.g. `const F = t => t < 6.2 ? t : t < 8.7 ? 6.2 + (t - 6.2) * 0.32 : t - 1.7;`. Shortening a beat or inserting one is then one line. Use the same `F` in the audio plan.

## Composition
- Frame 0 is a finished, readable scene.
- The lead subject fills 60-85 % of the frame in feature beats; no small window on a big empty field.
- Key text at least ~44 px tall at 1080p (about 9 px on a phone). Body chatter can be smaller, as texture only.
- Change speed: land, let it read, leave fast. No still moment longer than 0.6 s except the end card.
- Every action visibly causes a result (a message becomes a row, a vote fills a bar).
- Show the payoff as its own centred beat, not a toast in a corner.
- The end card appears complete within about half a second and holds the CTA for 3 s or more.

## Cuts
- Never let two semi-transparent scenes overlap. For a scene change: `tl.set(old, {opacity: 0}, T)`, then the new window opens at `T + 0.05` (scale from the carried object's position), with its headline already inside.
- When something "becomes" something else (a bubble becomes a chat line), fade the flyer out in ≤ 0.05 s exactly as the target appears, so there is never a doubled copy.
- Avoid huge scale-ups of DOM text through the camera: they rasterise and pixelate. Move the object into its destination instead.
- Dimming behind a dialog: match the theme (e.g. a 2x2 dither checker for Win98) instead of a generic translucent overlay.

## Checks
- `hyperframes check` reports intended overlaps (dialogs piling up, a lifted message over its row, a dimmed background) as `content_overlap` / `text_occluded`, and dimmed text as contrast warnings. Read them, but judge with snapshots.
- `gsap_callback_dom_measurement` fires when the `state()` updater shares a script with build-time measurement. That's fine if `state()` itself never measures.
- `nested_structure_needs_subcomposition` is a Studio layout suggestion, not a render problem, for a single-stage film.
