#!/usr/bin/env python3
"""In plain words: Sizes up a music track for editing to picture: short-term loudness per second (look for a
steady start and no sleepy intro), the tempo, and dead stops followed by drops (a dip of 5 dB or more for under a
second, then a strong onset), which are the places to land the film's turn on.
Usage: python3 music.py track.mp3 [seconds=60]   (needs ffmpeg and numpy)
To land a drop at film time T, start the track at offset = drop_time - T.
"""
import subprocess, sys
import numpy as np

f = sys.argv[1]
span = float(sys.argv[2]) if len(sys.argv) > 2 else 60.0
SR = 22050
y = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-t', str(span), '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32)

half = SR // 2
rms = 20 * np.log10(np.sqrt((y[: len(y) // half * half].reshape(-1, half) ** 2).mean(1)) + 1e-9)
print('loudness per 0.5 s (dBFS):')
print(' '.join(f'{i / 2:.1f}:{r:.0f}' for i, r in enumerate(rms)))

hop = 256
frames = y[: len(y) // hop * hop].reshape(-1, hop)
flux = np.maximum(0, np.diff(np.log1p(np.abs(np.fft.rfft(frames * np.hanning(hop), axis=1))), axis=0)).sum(1)
flux = (flux - flux.mean()) / (flux.std() + 1e-9)
fps = SR / hop
ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
best = max(((ac[int(round(60 / b * fps))] + 0.5 * ac[int(round(120 / b * fps))], b) for b in np.arange(70, 181, 0.5)), key=lambda x: x[0])
print(f'tempo ~ {best[1]:.1f} BPM (beat every {60 / best[1]:.3f} s)')

print('dead stops -> drops:')
t = np.arange(len(flux)) / fps
for i in range(2, len(rms) - 2):
    if rms[i] < min(rms[i - 1], rms[i + 1]) - 5:
        win = (t > (i + 1) / 2 - 0.2) & (t < (i + 1) / 2 + 0.8)
        if win.any():
            drop = t[win][np.argmax(flux[win])]
            print(f'  dip at {i / 2:.1f}s ({rms[i]:.0f} dB), drop at {drop:.2f}s')
