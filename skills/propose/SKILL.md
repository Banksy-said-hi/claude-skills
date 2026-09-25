---
name: propose
description: Produce a prioritized, phased ASCII roadmap of everything worth building next, using the current session's understanding as the primary source of truth. Use when the user types /propose.
---

## Sources, in priority order
1. **This conversation** — things discussed, files read, bugs found, decisions, pending work. Use it first and fully.
2. **Targeted lookups**, only for what the session is missing:
   - an item mentioned but not detailed → read that file
   - open issues → `gh issue list --state open --limit 50`
   - `features/` or `lessons/` folders, if present → read them
   - recent momentum → `git log --oneline -15`

No full project survey, no speculative reads.

## Reasoning
Weigh dependencies, risk (architectural impact, shared infra), value per effort, momentum (half-done work), and debt. Group into 3–5 **independently shippable** phases.

## Output

Item format: `[effort] · [VERB] [what] → [measurable result]` — effort S=hours, M=1–2d, L=3–5d, XL=1wk+.
Example: `S · Dynamic-import MetricsSection → /system First Load 200 kB → 90 kB`

```
ROADMAP · <date>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

NOW  · <theme>
  S · <verb> <what> → <impact>

NEXT · <theme>
  M · <verb> <what> → <impact>

SOON · <theme>
  L · <verb> <what> → <impact>

LATER · <theme>
  XL · <verb> <what> → <impact>

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Start here → <item> · <why it unblocks the most>
```

Rules:
- NOW is always stability, debt, and blockers.
- Themes: ≤3 words, outcome-oriented ("Cut render debt", not "Performance phase").
- Impact is concrete: a number, a user behavior, or a removed risk.
- Don't pad: 5 real items → show 5. No dependency map unless a dependency is non-obvious.
