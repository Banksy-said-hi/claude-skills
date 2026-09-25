---
name: close
description: End-of-session ritual — document the lesson, comment on and close the GitHub issue worked on, then re-prioritize the remaining open issues. Use when the user types /close.
allowed-tools: Bash, Read, Glob, Grep, Skill
---

Do not ask questions. Steps in order.

1. **Lesson** — invoke the `lesson` skill and wait for it.
2. **Identify the issue** resolved this session: an explicit number/title, a described problem matching an open issue, or work that maps to one. If none clearly matches, say so and skip to step 5.
3. **Comment** — `gh issue comment <n> --repo <owner>/<repo> --body "..."` (repo from `git remote get-url origin`). Cover, specifically (files, commands, config values):
   - **Problem** — one sentence
   - **What was implemented** — files changed and why
   - **Key decisions** — non-obvious choices and reasoning
   - **Outcome** — what works now
4. **Close** — `gh issue close <n> --repo <owner>/<repo>`
5. **Re-prioritize** — invoke the `issues` skill. The codebase is already in context, so it skips `study`.
