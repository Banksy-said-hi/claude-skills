---
name: issues
description: Fetch all open GitHub issues, ground them in the codebase, and give each a root cause, proposed fix, downstream effects, and a value-to-effort priority ranking. Use when the user types /issues.
allowed-tools: Bash, Read, Glob, Grep, Skill
---

Structured GitHub issue audit grounded in the actual code. Do not ask questions.

## 1. Context
If the codebase has not already been studied in this session, invoke the `study` skill and wait for it. Otherwise reuse what is in context.

## 2. Fetch
- Repo: parse `owner/repo` from `git remote get-url origin`.
- `gh issue list --repo <owner>/<repo> --state open --limit 100 --json number,title,labels,body,comments`

## 3. Classify
- **Bugs** — label `bug`, or something currently broken
- **Features** — label `enhancement`, new capability
- **Questions** — label `question`, open design question

## 4. Analyze each issue, by group

**#N — Title**
- **What's happening** — in terms of the real components involved
- **Root cause / answer** — files and line numbers
- **Proposed solution** — exact files and functions to change
- **Downstream effects** — what else changes or unlocks

## 5. Priority table

| Priority | # | Title | Effort (S/M/L) | Value (High/Med/Low) | Blocks |
|---|---|---|---|---|---|

Rank by value-to-effort for the current code state; flag dependency chains. End with one sentence: **Start here →** issue + why.
