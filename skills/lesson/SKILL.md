---
name: lesson
description: Document the bug or non-obvious challenge just resolved in this session as a file in the project's lessons/ folder, so future sessions (and /study) learn from it. Use when the user types /lesson.
---

1. **Pick the lesson** — the most recent bug, misdiagnosis, or non-obvious challenge solved in this conversation. Several distinct ones → one file each. Never invent one.
2. **Path** — `lessons/YYYY-MM-DD_short-kebab-slug.md` at the project root (create the folder if missing). Slug: 3–6 words naming the problem.
3. **Write** this structure, each section as short as it can be while staying actionable:

```markdown
# <Short title — what went wrong>

**Date:** YYYY-MM-DD
**Project area:** <e.g. frontend, pipeline, database>

## Symptom
What was observed. Quote the exact error or wrong behavior.

## Red herrings
Approaches that looked right but weren't, and why they misled.

## Root cause
One or two sentences. The cause, not the symptom.

## Fix
What changed and why it works. File paths and key snippets if they help.

## Check first next time
2–5 concrete checks for this class of problem.
```

4. **Confirm** — tell the user the filename, the one-line root cause, and the checks, so they can correct it.

Be specific: name files, functions, endpoints, error messages. "Always check your config" is useless.
