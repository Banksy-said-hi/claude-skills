#!/usr/bin/env python3
"""In plain words: The spec gate, a PreToolUse hook. In a git repo it denies writing code (Edit, Write,
MultiEdit, NotebookEdit, file-writing Bash commands) and leaving plan mode until docs/specs/ holds a spec for
the current branch with `status: ready` and no [NEEDS CLARIFICATION] marker. Always allowed: files under
docs/specs/, *.md and *.txt files, paths outside any git repo, and repos holding docs/specs/.off. Any error in
the hook itself lets the call through (stderr says why), so a broken gate never locks the owner out.
Reads the hook's JSON on stdin; prints a deny decision as JSON, or nothing to allow.
"""
import json, os, re, shlex, subprocess, sys

FREE_EXT = {'.md', '.txt'}
SCRATCH = ('/tmp/', '/private/tmp/', '/private/var/folders/', '/var/folders/', '/dev/')
MARK = '[NEEDS CLARIFICATION'


def git(cwd, *args):
    r = subprocess.run(['git', '-C', cwd, *args], capture_output=True, text=True, timeout=5)
    return r.stdout.strip() if r.returncode == 0 else None


def existing_dir(path):
    d = path if os.path.isdir(path) else os.path.dirname(path)
    while d and not os.path.isdir(d):
        d = os.path.dirname(d)
    return d or '/'


def front(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(':')
        out[k.strip()] = v.split('#')[0].strip()
    return out


def check_repo(root, branch):
    """None when a ready spec covers the branch, else the reason for the deny."""
    specs = os.path.join(root, 'docs', 'specs')
    if os.path.exists(os.path.join(specs, '.off')):
        return None
    drafts = []
    if os.path.isdir(specs):
        for name in sorted(os.listdir(specs)):
            if not name.endswith('.md') or name in ('CHECKS.md', 'README.md'):
                continue
            text = open(os.path.join(specs, name), encoding='utf-8').read()
            fm = front(text)
            if fm.get('branch') != branch:
                continue
            open_q = text.count(MARK)
            if fm.get('status') == 'ready' and open_q == 0:
                return None
            drafts.append(f"{name} (status {fm.get('status', '?')}, {open_q} open)")
    have = ('Specs on this branch that are not ready: ' + ', '.join(drafts) + '. ') if drafts else ''
    return (f"Spec gate: no ready spec for branch '{branch}' in {specs}. {have}"
            "Run the /spec skill for this work: find the gaps, ask the owner, and set status: ready only after the "
            "owner agrees (a small change takes the small path, a 6-line spec). Do not try another way to write the file.")


def check_path(path):
    if os.path.splitext(path)[1].lower() in FREE_EXT or path.startswith(SCRATCH):
        return None
    root = git(existing_dir(path), 'rev-parse', '--show-toplevel')
    if not root:
        return None
    if os.path.realpath(path).startswith(os.path.realpath(os.path.join(root, 'docs', 'specs')) + os.sep):
        return None
    branch = git(root, 'branch', '--show-current') or 'HEAD'
    return check_repo(root, branch)


def bash_targets(cmd, cwd):
    """Paths a shell command writes to, as far as a simple reading can tell."""
    targets = []
    for m in re.finditer(r'(?<![0-9&>])>>?\s*([^\s;&|<>()]+)', cmd):
        targets.append(m.group(1))
    for m in re.finditer(r'\btee\s+(?:-a\s+)?([^\s;&|]+)', cmd):
        targets.append(m.group(1))
    try:
        words = shlex.split(cmd)
    except ValueError:
        words = cmd.split()
    for i, w in enumerate(words):
        if w in ('sed', 'perl', 'gsed') and any(a.startswith('-i') or a.startswith('-pi') for a in words[i + 1:i + 4]):
            files = [a for a in words[i + 1:] if a and not a.startswith('-') and not re.match(r'^[sy]/', a)
                     and (os.path.isfile(os.path.join(cwd, os.path.expanduser(a))) or re.search(r'\.\w+$', a))]
            targets += files or [os.path.join(cwd, '_')]
        if w in ('patch',) or (w == 'git' and i + 1 < len(words) and words[i + 1] == 'apply'):
            targets.append(os.path.join(cwd, '_'))
    out = []
    for t in targets:
        t = os.path.expanduser(t.strip('\'"'))
        if t.startswith('$') or t.startswith('&'):
            continue
        out.append(t if os.path.isabs(t) else os.path.join(cwd, t))
    return out


def main():
    data = json.load(sys.stdin)
    tool, inp, cwd = data.get('tool_name', ''), data.get('tool_input') or {}, data.get('cwd') or os.getcwd()
    if tool == 'ExitPlanMode':
        root = git(cwd, 'rev-parse', '--show-toplevel')
        reasons = [check_repo(root, git(root, 'branch', '--show-current') or 'HEAD')] if root else []
    elif tool in ('Edit', 'Write', 'MultiEdit', 'NotebookEdit'):
        p = inp.get('file_path') or inp.get('notebook_path') or ''
        reasons = [check_path(p if os.path.isabs(p) else os.path.join(cwd, p))] if p else []
    elif tool == 'Bash':
        reasons = [check_path(p) for p in bash_targets(inp.get('command', ''), cwd)]
    else:
        reasons = []
    reason = next((r for r in reasons if r), None)
    if reason:
        print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': 'deny', 'permissionDecisionReason': reason}}))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:  # a broken gate must not lock the owner out
        print(f'spec gate error, call allowed: {e}', file=sys.stderr)
