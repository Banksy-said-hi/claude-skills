#!/usr/bin/env python3
"""In plain words: A UserPromptSubmit hook. On every message of six words or more that is not a slash command, it
adds one line to Claude's context: when the message describes a new feature, idea or behaviour change, run /spec
first and ask about gaps instead of guessing. Short replies ("yes", "B") and slash commands get nothing.
"""
import json, sys

try:
    prompt = (json.load(sys.stdin).get('prompt') or '').strip()
except Exception:
    prompt = ''
if prompt and not prompt.startswith('/') and len(prompt.split()) >= 6:
    print('[spec] If this message describes a new feature, idea or behaviour change, run the /spec skill before planning '
          'or editing: read the code, find the gaps, ask the owner about them, and do not fill them with guesses. '
          'Small changes take its small path.')
