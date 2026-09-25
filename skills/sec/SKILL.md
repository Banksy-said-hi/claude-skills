---
name: sec
description: Autonomous, stack-aware security audit. Studies the project, tests vulnerability hypotheses against real code with realistic exploit paths, runs secret and dangerous-API scans, prints a severity-ranked ASCII report, then plans fixes for HIGH findings in plan mode. Use when the user types /sec.
allowed-tools: Bash, Read, Glob, Grep, Skill, EnterPlanMode, ExitPlanMode
---

Fully autonomous. No questions. Phases in order, then the report. Nothing else.

## 1 · Study
Invoke the `study` skill first (mandatory) unless the project was already studied this session. You need the auth model, request handlers, schema, and external integrations.

## 2 · Hypotheses
List candidate vulnerabilities for THIS stack. Cover what applies:

- **AuthN/AuthZ** — unauthenticated routes (especially admin and mutations), role or tenant checks only in the UI, weak session cookies (no httpOnly/secure/samesite, no rotation), account enumeration in reset flows, OAuth state or redirect URI not validated, JWT pitfalls (alg=none, weak secret, no exp or aud).
- **Injection** — SQL built by string interpolation, shell commands with untrusted input, path traversal, SSRF (user-supplied URLs fetched without a private-IP blocklist), XSS (raw HTML sinks, string-built HTML), open redirects, NoSQL/LDAP/template injection.
- **Secrets & config** — hardcoded keys, committed .env or credential files, secrets in logs, errors, or client bundles (public env prefixes), default credentials reaching production.
- **CSRF/CORS/headers** — state-changing endpoints without CSRF protection, wildcard CORS on authenticated routes, missing CSP/HSTS/frame/nosniff headers.
- **Data exposure** — over-broad responses (internal IDs, hashes, PII), stack traces in production, sensitive data in logs, IDOR.
- **Supply chain** — dependencies with known CVEs at the pinned version, deprecated crypto libraries, postinstall scripts, missing or drifting lockfile.
- **Crypto** — md5/sha1 password hashing, custom crypto, non-cryptographic RNG for tokens, fixed IVs, reused nonces, ECB.
- **Uploads & rendering** — dangerous file types (html, svg with JS, executables), filenames used as paths, unsandboxed rendering of user content (PDF, LaTeX with shell-escape).
- **Containers & infra** — running as root, ports bound to 0.0.0.0, `privileged` or extra capabilities, writable host mounts, secrets copied into image layers, unpinned base images.
- **LLM (if the app calls one)** — user text reaching system prompts or tool calls unisolated, model output executed or fed to shell/SQL/LaTeX unescaped, model access wider than the requesting user's data, indirect injection via fetched pages, OCR, or uploads, no rate or cost cap.
- **Abuse** — no rate limits on login, signup, reset, or expensive endpoints; no audit trail for destructive or privileged actions.

## 3 · Verify
Read the actual code for every hypothesis. A finding needs: file:lines, the quoted pattern, a **realistic exploit path** (who, with what input, to what end), and a concrete fix. Theoretical, or requires an attacker who already has full access → downgrade.

- 🔴 **HIGH** — RCE, auth bypass, SQLi, exposed secrets, SSRF into internal services, cross-tenant IDOR. Realistic path to data loss, account takeover, or compromise.
- 🟡 **MED** — needs an extra condition or has limited blast radius: admin-only stored XSS, CSRF, no rate limit on costly operations, dependency CVE not reachable here, sensitive logs, weak but rotatable crypto.
- 🟢 **LOW** — hardening with no immediate exploit: headers, verbose errors, debug endpoints behind auth, unpinned images, unexposed default passwords.
- ✅ **OK** — already correct; say what you checked.

## 4 · Measure
Safe, non-destructive scans; adapt to the stack:
- Secret shapes: `AKIA`, `sk_live_`, `xoxb-`, `-----BEGIN`, `password=`, `Bearer ` literals
- Tracked secret files: `git ls-files | grep -E '\.env($|\.)|credentials|secrets'`
- Dangerous APIs: `eval(`, `exec(`, `shell=True`, `os.system`, `dangerouslySetInnerHTML`, `innerHTML =`, `Math.random`, `pickle.loads`, unsafe `yaml.load(`
- SQL keywords inside interpolated strings
- Auth coverage: list every route handler and mark which ones check the session
- Containers: `grep -nE 'privileged|cap_add|USER root|0\.0\.0\.0' docker-compose*.yml Dockerfile*`
- Endpoints that fetch user-supplied URLs, and whether they block private IPs

## 5 · Report
Print exactly this, every placeholder filled, nothing truncated:

```
╔══════════════════════════════════════════════════════════════╗
║  SECURITY AUDIT  ·  <project>   ·  Stack: <stack>            ║
╚══════════════════════════════════════════════════════════════╝

SUMMARY   tested N · 🔴 N · 🟡 N · 🟢 N · ✅ N

FINDINGS
[01] 🔴 HIGH · <title>
     File    : <path>:<lines>
     Pattern : <quoted code>
     Exploit : <who, with what input, to what end>
     Fix     : <specific action>
[NN] ✅ OK · <title>
     File    : <path>
     Why OK  : <what was checked>

MEASUREMENTS
  <scan hit counts, unguarded routes, vulnerable versions; if one could not be taken, say why>

TOP FIXES  (highest impact · lowest effort)
  1. [NN] <action>
  2. [NN] <action>
  3. [NN] <action>
```

No 🔴 findings → stop here.

## 6 · Plan HIGH fixes
Call EnterPlanMode. One plan covering every 🔴 finding (MED/LOW are the user's call). For each: finding number and title, exact files and lines, the concrete change (not "sanitize X" — "bind the parameter at `src/foo.py:42` instead of interpolating it"), the exploit it closes, and any risk (other callers, rebuild, migration). End with **EXECUTION ORDER**: batch independent changes, order dependent ones, and put any secret rotation last, marked as something the user must run.

Call ExitPlanMode. Execute only after approval, in that order; honor any changes the user makes.
