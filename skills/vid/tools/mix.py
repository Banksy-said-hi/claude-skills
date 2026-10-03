#!/usr/bin/env python3
"""In plain words: Mixes a film's sound from a plan and puts it on the silent picture.

Usage: python3 mix.py audio-plan.json renders/picture.mp4 renders/film.mp4
Writes film.mp4 (picture copied untouched, AAC 256k), film-no-sfx.mp4 (same without effects, to tell an
effect from the music) and <film>-mix-report.txt (each effect's band, reference level and gain).

audio-plan.json (paths relative to the plan file):
{
  "duration": 24.2,
  "music": {"file": "assets/music/track.mp3", "offset": 8.27, "lufs": -20.5, "duck_db": -5, "fade_out": 1.6},
  "vo":    [{"file": "assets/vo/vo1.wav", "t": 0.4}, ...],
  "vo_lufs": -16,
  "sfx":   [{"file": "assets/sfx/pop.mp3", "t": 0.18, "lift": 2.5}, ...],   # lift: dB over music+voice in the effect's band
  "master_lufs": -14, "true_peak": -1.3
}
"music" may be null (no music) and "vo" / "sfx" may be empty.
Rules applied: music ducked under every voice line; each effect band-passed 180 Hz-10 kHz with click-free edges, set
`lift` dB above what plays under it in its own band (centroid/2 .. centroid*2); effects within 0.15 s of another are
softened (x0.6); the 2-8 kHz lift is capped at 4 dB; master levelled to master_lufs, then a soft limiter.
Needs ffmpeg (with ebur128), numpy, scipy.
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000
plan_path, pic, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
plan = json.loads(plan_path.read_text())
root = plan_path.parent
DUR = float(plan['duration'])
N = int(DUR * SR)
tmpdir = out.parent


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(root / path), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def write(path, x):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', str(path)], input=np.clip(x, -1, 1).astype(np.float32).tobytes(), check=True)


def loudness(x):
    tmp = tmpdir / '_lufs.wav'
    write(tmp, x)
    e = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(tmp), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    tmp.unlink(missing_ok=True)
    get = lambda pat, d: float((re.findall(pat, e) or [d])[-1])
    return get(r'I:\s+(-?[\d.]+) LUFS', 'nan'), get(r'Peak:\s+(-?[\d.]+) dBFS', 'nan'), get(r'LRA:\s+([\d.]+) LU', 'nan')


def band(x, lo, hi):
    sos = butter(4, [max(lo, 40), min(hi, 20000)], btype='band', fs=SR, output='sos')
    return sosfilt(sos, x[:, 0] + x[:, 1])


def peak_db(y):
    h = int(0.05 * SR)
    if len(y) < h:
        return 10 * np.log10((y ** 2).mean() + 1e-12)
    return max(10 * np.log10((y[i:i + h] ** 2).mean() + 1e-12) for i in range(0, len(y) - h, h // 2))


def place(bed, clip, t, gain):
    a = int(t * SR)
    b = min(N, a + len(clip))
    if 0 <= a < N:
        bed[a:b] += clip[: b - a] * gain


def duck_curve(spans, depth_db, ramp=0.12):
    t = np.arange(N) / SR
    g = np.zeros(N, np.float32)
    for s, e in spans:
        g = np.maximum(g, np.minimum(np.clip((t - (s - ramp)) / ramp, 0, 1), np.clip(((e + ramp) - t) / ramp, 0, 1)))
    return 10 ** (depth_db * g / 20)


# voice
vo = np.zeros((N, 2), np.float32)
spans = []
for line in plan.get('vo', []):
    clip = load(line['file'])
    place(vo, clip, line['t'], 1.0)
    spans.append((line['t'], line['t'] + len(clip) / SR))
if spans:
    vo *= 10 ** ((plan.get('vo_lufs', -16) - loudness(vo)[0]) / 20)

# music
mus = np.zeros((N, 2), np.float32)
m = plan.get('music')
if m:
    raw = load(m['file'])
    s = int(m.get('offset', 0) * SR)
    seg = raw[s:s + N]
    mus[: len(seg)] = seg
    t = np.arange(N) / SR
    mus *= (np.minimum(1, t / 0.01) * np.clip((DUR - t) / m.get('fade_out', 1.6), 0, 1) ** 1.3)[:, None]
    mus *= 10 ** ((m.get('lufs', -20.5) - loudness(mus)[0]) / 20)
    if spans:
        mus *= duck_curve(spans, m.get('duck_db', -5))[:, None]

# effects
sfx = np.zeros((N, 2), np.float32)
report = []
events = sorted(plan.get('sfx', []), key=lambda e: e['t'])
cache = {}
for ev in events:
    if ev['file'] not in cache:
        clip = sosfilt(butter(2, [180, 10000], btype='band', fs=SR, output='sos'), load(ev['file']), axis=0).astype(np.float32)
        f = int(0.004 * SR)
        clip[:f] *= np.linspace(0, 1, f)[:, None]
        clip[-f:] *= np.linspace(1, 0, f)[:, None]
        cache[ev['file']] = clip
    clip = cache[ev['file']]
    spec = np.abs(np.fft.rfft(clip[:, 0] + clip[:, 1]))
    fr = np.fft.rfftfreq(len(clip), 1 / SR)
    cen = float((spec * fr).sum() / (spec.sum() + 1e-9))
    lo, hi = cen / 2, cen * 2
    a, b = int(ev['t'] * SR), min(N, int(ev['t'] * SR) + len(clip))
    under = mus[a:b] + vo[a:b]
    ref = max(peak_db(band(under, lo, hi)), -50.0)
    gain = ref + ev.get('lift', 3.0) - peak_db(band(clip, lo, hi))
    if any(abs(o['t'] - ev['t']) < 0.15 for o in events if o is not ev):
        gain += 20 * np.log10(0.6)
    hf_ref = max(peak_db(band(under, 2000, 8000)), -50.0)
    over = peak_db(band(clip, 2000, 8000)) + gain - (hf_ref + 4)
    if over > 0:
        gain -= over
    place(sfx, clip, ev['t'], 10 ** (gain / 20))
    report.append(f"{ev['t']:6.2f}s {Path(ev['file']).stem:16s} band {lo:5.0f}-{hi:5.0f} Hz  ref {ref:6.1f} dB  gain {gain:6.1f} dB")


def master(x):
    x = x * 10 ** ((plan.get('master_lufs', -14) - loudness(x)[0]) / 20)
    ceiling = 10 ** (plan.get('true_peak', -1.3) / 20)
    return np.tanh(x / ceiling) * ceiling


def mux(x, dest):
    wav = tmpdir / '_mix.wav'
    write(wav, x)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pic, '-i', str(wav), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', str(dest)], check=True)
    wav.unlink(missing_ok=True)


full = master(mus + vo + sfx)
I, TP, LRA = loudness(full)
mux(full, out)
mux(master(mus + vo), out.with_name(out.stem + '-no-sfx' + out.suffix))
summary = f'{out.name}: integrated {I:.1f} LUFS, true peak {TP:.1f} dBFS, LRA {LRA:.1f} LU'
out.with_name(out.stem + '-mix-report.txt').write_text(summary + '\n' + '\n'.join(report) + '\n')
print(summary)
