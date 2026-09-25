---
name: study
description: Deeply study the current project so you are ready to implement features. Builds a mental model of stack, structure, architecture, conventions, recent activity, and past lessons. Use when the user types /study or at the start of work on an unfamiliar repo.
---

Explore autonomously. Do not ask questions.

1. **Identity** — read README, CLAUDE.md/AGENTS.md, and the manifest (package.json, pyproject.toml, Cargo.toml, go.mod…). Name, purpose, stack.
2. **Structure** — top-level layout, entry points, config (.env.example, compose, CI).
3. **Architecture** — trace input → processing → output/storage. Modules, layers, external integrations.
4. **Core logic** — read entry points, core modules, shared utilities. Domain types and how features are wired (routing, events, state).
5. **Conventions** — naming, folder patterns, test runner and test locations, anything project-specific.
6. **Current state** — `git log --oneline -10`; TODO/FIXME in code.
7. **Past lessons** — only when this is the first substantial turn of the session: if `lessons/` exists, read every file. Treat lessons as hard facts; surface the ones relevant to upcoming work.

## Output

**Project:** name + one-line purpose
**Stack:** languages, frameworks, runtimes
**Architecture:** 2–4 sentences
**Key modules:** bullets, path + one line each
**Patterns to follow:** bullets
**Hot areas:** bullets from git log
**Ready to build:** confirm, or flag blockers/ambiguities

Depth of understanding over length of report.
