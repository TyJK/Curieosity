"""
Synthesises Curieosity's sound effects and writes them to assets/sounds/*.ogg.

Every sound is made here from sine waves, filtered noise and envelopes, so the set is
original to the game and carries no third-party licence. Re-run after changing a recipe:

    python tools/art/gen_sounds.py            # writes assets/sounds/*.ogg (needs ffmpeg)
    python tools/art/gen_sounds.py --wav DIR  # also keeps the .wav files in DIR

Requires numpy, and ffmpeg with libvorbis on the PATH.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

RATE = 44100
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets" / "sounds"
rng = np.random.default_rng(7)


# --- building blocks --------------------------------------------------------------------
def t_axis(seconds):
    return np.arange(int(RATE * seconds)) / RATE


def env(n, attack, decay, sustain=0.0, release=None):
    """Attack-then-exponential-decay envelope over n samples (times in seconds)."""
    t = np.arange(n) / RATE
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = np.exp(-np.maximum(t - attack, 0) / max(decay, 1e-4))
    e = a * (sustain + (1 - sustain) * d)
    if release:
        tail = int(release * RATE)
        if tail < n:
            e[-tail:] *= np.linspace(1, 0, tail)
    return e


def sine(freq, seconds, phase=0.0):
    t = t_axis(seconds)
    f = np.broadcast_to(np.asarray(freq, dtype=float), t.shape) if np.ndim(freq) else freq
    if np.ndim(f):
        return np.sin(2 * np.pi * np.cumsum(f) / RATE + phase)
    return np.sin(2 * np.pi * f * t + phase)


def glide(f0, f1, seconds, curve=1.0):
    """A frequency track from f0 to f1 (exponential when curve=1)."""
    x = np.linspace(0, 1, int(RATE * seconds)) ** curve
    return f0 * (f1 / f0) ** x


def bell(freq, seconds, decay, partials=((1, 1.0), (2.76, 0.42), (5.40, 0.18), (8.93, 0.07))):
    """A struck-bell tone: inharmonic partials, the higher ones dying faster."""
    t = t_axis(seconds)
    out = np.zeros_like(t)
    for ratio, amp in partials:
        out += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / (decay / ratio ** 0.6))
    return tail_fade(out * np.clip(t / 0.002, 0, 1), seconds * 0.3)


def tail_fade(x, seconds):
    """Fade the last `seconds` out, so nothing stops while still ringing (an audible click)."""
    n = min(len(x), int(seconds * RATE))
    if n > 1:
        x = x.copy()
        x[-n:] *= np.linspace(1, 0, n) ** 2
    return x


def noise(seconds):
    return rng.standard_normal(int(RATE * seconds))


def lowpass(x, cutoff):
    """One-pole low-pass; cutoff may be a per-sample array."""
    c = np.broadcast_to(np.asarray(cutoff, dtype=float), x.shape)
    a = 1 - np.exp(-2 * np.pi * c / RATE)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc)
        y[i] = acc
    return y


def bandpass(x, lo, hi):
    return lowpass(x, hi) - lowpass(x, lo)


def place(dst, src, at):
    i = int(at * RATE)
    end = min(len(dst), i + len(src))
    dst[i:end] += src[: end - i]


def finish(x, peak_db):
    """Remove DC, fade the edges, and normalise to a peak level in dBFS."""
    x = x - np.mean(x)
    fade = min(len(x) // 4, int(0.004 * RATE))
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade * 3:] *= np.linspace(1, 0, fade * 3)
    return x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)


# --- the sounds -------------------------------------------------------------------------
def click():
    """A soft tick for buttons."""
    s = 0.05
    tone = sine(2100, s) * env(int(RATE * s), 0.0005, 0.006)
    tick = bandpass(noise(s), 1500, 6000) * env(int(RATE * s), 0.0002, 0.0025)
    return finish(tone + 0.6 * tick, -14)


def pickup():
    """Lifting a substance off the shelf: a small rising blip."""
    s = 0.09
    x = sine(glide(520, 880, s), s) * env(int(RATE * s), 0.004, 0.035)
    return finish(x, -10)


def drop():
    """A substance landing in a vessel: a liquid plop."""
    s = 0.22
    body = sine(glide(560, 170, s, 0.6), s) * env(int(RATE * s), 0.002, 0.05)
    splash = bandpass(noise(s), 800, 4000) * env(int(RATE * s), 0.001, 0.012)
    return finish(body + 0.35 * splash, -6)


def place_vessel():
    """A vessel set down on the bench: a glassy clink over a soft thunk."""
    s = 0.6
    clink = bell(1320, s, 0.22, ((1, 1.0), (2.01, 0.5), (3.43, 0.25), (5.12, 0.1)))
    thunk = tail_fade(sine(glide(170, 110, 0.09), 0.09) * env(int(RATE * 0.09), 0.002, 0.025), 0.03)
    x = 0.55 * clink
    place(x, 0.9 * thunk, 0.0)
    return finish(x, -6)


def react():
    """A reaction starting: bubbles rising through a fizzing liquid."""
    s = 1.1
    x = np.zeros(int(RATE * s))
    bed = bandpass(noise(s), 900, 3200) * env(len(x), 0.25, 0.5, sustain=0.3, release=0.35)
    x += 0.1 * bed
    for _ in range(18):
        at = rng.uniform(0.0, 0.85)
        d = rng.uniform(0.025, 0.05)
        f0 = rng.uniform(280, 520)
        b = tail_fade(sine(glide(f0, f0 * rng.uniform(1.6, 2.4), d), d) * env(int(RATE * d), 0.002, d / 3), d / 3)
        place(x, rng.uniform(0.35, 0.8) * b, at)
    return finish(x, -5)


def discovery():
    """Something new: a bright two-note chime (E6, B6)."""
    s = 1.3
    x = np.zeros(int(RATE * s))
    place(x, bell(1318.5, 1.2, 0.5), 0.0)
    place(x, 0.85 * bell(1975.5, 1.2, 0.45), 0.085)
    return finish(x, -4)


def milestone():
    """A milestone: an arpeggio (C5 E5 G5 C6) over a soft swelling chord."""
    s = 2.0
    x = np.zeros(int(RATE * s))
    for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        place(x, 0.7 * bell(f, 1.6, 0.6), i * 0.095)
    pad = sum(sine(f, s) * a for f, a in ((261.63, 0.5), (392.0, 0.35), (523.25, 0.3), (659.25, 0.2)))
    pad *= env(len(x), 0.35, 0.9, sustain=0.0, release=0.5) * 0.35
    return finish(x + pad, -3)


def fizzle():
    """No reaction: a gentle, falling 'pfft'."""
    s = 0.5
    n = int(RATE * s)
    hiss = lowpass(noise(s), glide(5000, 300, s)) * env(n, 0.01, 0.12)
    sag = sine(glide(240, 110, s), s) * env(n, 0.01, 0.15)
    return finish(0.9 * hiss + 0.5 * sag, -8)


def era():
    """A new era: a low struck gong and a warm A-major chord swelling under it."""
    s = 3.4
    n = int(RATE * s)
    x = np.zeros(n)
    gong = bell(110, s, 1.4, ((1, 1.0), (1.49, 0.5), (2.02, 0.35), (2.74, 0.2), (3.76, 0.12)))
    x += 0.7 * gong
    chord = sum(sine(f, s) * a for f, a in ((110.0, 0.5), (164.81, 0.4), (220.0, 0.35),
                                            (277.18, 0.3), (329.63, 0.25)))
    x += 0.4 * chord * env(n, 0.9, 1.4, sustain=0.0, release=1.0)
    place(x, 0.25 * bell(1760, 2.0, 0.7), 0.45)
    return finish(x, -3)


SOUNDS = {
    "click": click,
    "pickup": pickup,
    "drop": drop,
    "place": place_vessel,
    "react": react,
    "discovery": discovery,
    "milestone": milestone,
    "fizzle": fizzle,
    "era": era,
}


def write_wav(path, x):
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(pcm.tobytes())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wav", type=Path, help="also keep the .wav files in this folder")
    args = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is needed to encode the .ogg files")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, make in SOUNDS.items():
            wav = Path(tmp) / f"{name}.wav"
            write_wav(wav, make())
            ogg = OUT / f"{name}.ogg"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis",
                            "-q:a", "5", str(ogg)], check=True)
            if args.wav:
                args.wav.mkdir(parents=True, exist_ok=True)
                shutil.copy(wav, args.wav / wav.name)
            print(f"  {ogg.relative_to(ROOT)}  ({ogg.stat().st_size // 1024 + 1} KB)")
    print(f"{len(SOUNDS)} sounds written.")


if __name__ == "__main__":
    main()
