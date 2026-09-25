---
name: dump
description: Write a project handoff document (Markdown, plus PDF when pandoc is available) into progress/ covering everything discussed, built, decided, and remaining, so the next agent or developer can continue cold. Use when the user types /dump.
disable-model-invocation: true
allowed-tools: Read, Write, Glob, Grep, Bash
---

Goal: someone picking this up with zero context can continue development.

1. **Scan** — README, manifest, .env.example, entry points, config, folder structure.
2. **Mine the conversation** — the problem, what was decided and why (including rejected approaches), what was built, bugs fixed, open questions, blockers, trade-offs, warnings.
3. **Path** — run `date +"%Y-%m-%d_%H-%M-%S"` once and reuse that value as `$TS`. Write `progress/$TS.md` at the project root (create `progress/` if missing).
4. **Write** these sections:

```
# <Project> — Handoff
*Generated: <date time>*

1. Project overview — what, for whom, which problem
2. Tech stack — with versions where known
3. Architecture — components, data flow, a plain-text diagram if useful
4. Current state — working / partial / broken. Be honest.
5. Done this session — concrete changes and decisions
6. Goals & roadmap — prioritized, with deadlines or constraints
7. Features — implemented / in progress (status, what remains) / backlog
8. Key decisions & context — why, and the alternatives rejected (the most valuable section)
9. Known issues & watch-outs — bugs, edge cases, debt, gotchas
10. How to run — from zero
11. Environment & config — required env vars, services, keys (names and where to get them, never values)
12. Next steps — actionable, in priority order
```

5. **PDF** — using the same `$TS`:
   ```
   pandoc "progress/$TS.md" -o "progress/$TS.pdf" --pdf-engine=wkhtmltopdf 2>/dev/null \
     || pandoc "progress/$TS.md" -o "progress/$TS.pdf" 2>/dev/null \
     || echo "no PDF engine — progress/$TS.md is the handoff"
   ```
6. **Confirm** — print the exact path(s) and name any section left thin for lack of context.
