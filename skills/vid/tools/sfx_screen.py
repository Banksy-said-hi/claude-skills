#!/usr/bin/env python3
"""In plain words: Ranks sound-effect files before anyone listens. For each file: how long it really sounds,
how fast it rises, where its energy sits, how much is rumble (<150 Hz) and hiss/click (>6 kHz), and a verdict.
Reject boomy (>50 % rumble), hissy (>40 % highs), or long (>0.8 s) sounds for repeated use; a long one can still
serve once (a single confirmation chime).
Usage: python3 sfx_screen.py a.mp3 b.wav ...   (needs ffmpeg and numpy)
"""
import subprocess, sys
import numpy as np

SR = 44100
for f in sys.argv[1:]:
    y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)
    if len(y) == 0:
        print(f'{f}: unreadable')
        continue
    env = np.sqrt(np.convolve(y ** 2, np.ones(441) / 441, 'same'))
    on = np.where(env > env.max() * 0.05)[0]
    dur = (on[-1] - on[0]) / SR
    rise = (np.argmax(env) - on[0]) / SR * 1000
    spec = np.abs(np.fft.rfft(y)) ** 2
    fr = np.fft.rfftfreq(len(y), 1 / SR)
    tot = spec.sum()
    low, high = spec[fr < 150].sum() / tot, spec[fr > 6000].sum() / tot
    why = [w for w, bad in (('boomy', low > 0.5), ('hissy/clicky', high > 0.4), ('long', dur > 0.8)) if bad]
    print(f"{f}: {dur:.2f}s rise {rise:.0f}ms centroid {(spec * fr).sum() / tot:.0f}Hz <150Hz {low:.0%} >6k {high:.0%} -> {'REJECT: ' + ', '.join(why) if why else 'ok'}")
