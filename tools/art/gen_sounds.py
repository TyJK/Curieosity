"""
Synthesises Curieosity's sound effects and writes them to assets/sounds/*.ogg.

Every sound is made here from sine waves, filtered noise and envelopes, so the set is
original to the game and carries no third-party licence. Re-run after changing a recipe:

    python tools/art/gen_sounds.py            # writes assets/sounds/*.ogg (needs ffmpeg)
    python tools/art/gen_sounds.py --wav DIR  # also keeps the .wav files in DIR
    python tools/art/gen_sounds.py --only drop  # rewrites just these sounds

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
    """A substance landing in a vessel: a crisp click, like a piece snapping into its place.
    A sharp, bright tick on top of a short, low knock, no pitch sweep."""
    # the noise the old plop drew, so every sound after this one comes out as it was
    noise(0.22)
    s = 0.09
    n = int(RATE * s)
    own = np.random.default_rng(23)
    tick = bandpass(own.standard_normal(n), 2500, 9000) * env(n, 0.0002, 0.0018)
    knock = sine(1650, s) * env(n, 0.0004, 0.009)
    body = sine(glide(240, 190, s), s) * env(n, 0.0008, 0.016)
    x = 0.9 * tick + 0.45 * knock + 0.7 * body
    return finish(x, -7)


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
    """Something new: a bright two-note chime (E6, B6), kept well under the bench's sounds
    (it plays often)."""
    s = 1.3
    x = np.zeros(int(RATE * s))
    place(x, bell(1318.5, 1.2, 0.5), 0.0)
    place(x, 0.85 * bell(1975.5, 1.2, 0.45), 0.085)
    return finish(x, -14)


def milestone():
    """A milestone: an arpeggio (C5 E5 G5 C6) over a soft swelling chord."""
    s = 2.0
    x = np.zeros(int(RATE * s))
    for i, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
        place(x, 0.7 * bell(f, 1.6, 0.6), i * 0.095)
    pad = sum(sine(f, s) * a for f, a in ((261.63, 0.5), (392.0, 0.35), (523.25, 0.3), (659.25, 0.2)))
    pad *= env(len(x), 0.35, 0.9, sustain=0.0, release=0.5) * 0.35
    return finish(x + pad, -9)


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
    return finish(x, -10)


# --- each kind of vessel: a sound for setting it on the bench and one for reacting -------
# (src/systems/sound.rs maps every vessel to one of these families)
def crackles(seconds, count, lo=2000, hi=8000, spread=(0.0, 1.0), level=(0.3, 1.0)):
    """Short dry pops, scattered: burning wood, an ice crust, a Geiger counter."""
    x = np.zeros(int(RATE * seconds))
    for _ in range(count):
        d = rng.uniform(0.002, 0.008)
        pop = bandpass(noise(d), lo, hi) * env(int(RATE * d), 0.0003, d / 4)
        place(x, rng.uniform(*level) * pop, rng.uniform(*spread) * seconds * 0.95)
    return x


def flicker(n, rate=7.0, depth=0.5):
    """A slow random wobble in loudness, like a flame."""
    knots = rng.uniform(1 - depth, 1, int(n / RATE * rate) + 3)
    return np.interp(np.arange(n), np.linspace(0, n, len(knots)), knots)


def fire_place():
    """A fire catching: a breathy whoosh, then the first pops."""
    s = 0.9
    n = int(RATE * s)
    whoosh = lowpass(noise(s), glide(300, 2400, s, 0.5)) * env(n, 0.06, 0.25)
    x = 0.9 * whoosh + 0.35 * crackles(s, 9, spread=(0.25, 1.0))
    return finish(x, -10)


def fire_react():
    """Something burning: a low roar that flickers, full of crackles."""
    s = 1.4
    n = int(RATE * s)
    roar = lowpass(noise(s), 650) * flicker(n, 8, 0.6) * env(n, 0.15, 0.6, sustain=0.6, release=0.4)
    x = 0.8 * roar + 0.45 * crackles(s, 46)
    return finish(x, -8)


def grind_place():
    """A stone mortar set down: a dull thud, then one gritty turn of the pestle."""
    s = 0.6
    thud = tail_fade(sine(glide(110, 60, 0.12), 0.12) * env(int(RATE * 0.12), 0.002, 0.04), 0.04)
    d = 0.4
    m = int(RATE * d)
    grit = bandpass(noise(d), 250, 2200) * np.abs(rng.standard_normal(m)) ** 0.5
    stroke = grit * np.sin(np.linspace(0, np.pi, m)) ** 1.5
    x = np.zeros(int(RATE * s))
    place(x, thud, 0.0)
    place(x, 0.6 * stroke, 0.12)
    return finish(x, -9)


def grind_react():
    """A pestle grinding: three gritty strokes over a low rumble."""
    s = 1.3
    x = np.zeros(int(RATE * s))
    for i in range(3):
        d = 0.38
        m = int(RATE * d)
        grit = bandpass(noise(d), 250, 2200) * np.abs(rng.standard_normal(m)) ** 0.5
        stroke = grit * np.sin(np.linspace(0, np.pi, m)) ** 1.5
        place(x, stroke, 0.05 + i * 0.4)
    x += 0.3 * lowpass(noise(s), 120) * env(len(x), 0.1, 0.8, sustain=0.5, release=0.3)
    return finish(x, -9)


def cold_place():
    """A cold bath set down: a gust of icy wind, and an ice cube's clink as it settles."""
    s = 0.8
    n = int(RATE * s)
    sweep = np.concatenate([glide(500, 1600, s * 0.4), glide(1600, 700, s - s * 0.4)])[:n]
    x = bandpass(noise(s), sweep * 0.55, sweep) * env(n, 0.18, 0.25, sustain=0.2, release=0.25)
    place(x, 0.2 * bell(3300, 0.3, 0.05, ((1, 1.0), (1.73, 0.5), (2.9, 0.25))), 0.45)
    return finish(x, -10)


def cold_react():
    """Something freezing: frost crackling across a surface and the ice tightening, over a
    thin wind."""
    s = 1.5
    n = int(RATE * s)
    wind = bandpass(noise(s), 500, 1400) * env(n, 0.3, 0.8, sustain=0.3, release=0.4)
    x = 0.5 * wind + 0.6 * crackles(s, 60, 4000, 11000, (0.1, 1.0), (0.2, 0.8))
    for _ in range(5):
        place(x, 0.2 * bell(rng.uniform(3500, 5500), 0.35, 0.06), rng.uniform(0.2, 1.2))
    return finish(x, -9)


def glass_react():
    """Glassware boiling: the bubbling of a reaction, and a drip or two from the condenser."""
    x = react()
    for at in (0.45, 0.85):
        d = 0.06
        drip = tail_fade(sine(glide(1400, 700, d), d) * env(int(RATE * d), 0.001, 0.02), 0.02)
        place(x, 0.3 * drip, at)
    return finish(x, -9)


def bio_place():
    """A wooden vat set down: a hollow knock and a slosh of liquid."""
    s = 0.6
    knock = sum(a * sine(f, 0.25) * np.exp(-t_axis(0.25) / 0.05) for f, a in ((190, 1.0), (430, 0.4), (870, 0.15)))
    slosh = lowpass(noise(0.4), 700) * env(int(RATE * 0.4), 0.08, 0.12)
    x = np.zeros(int(RATE * s))
    place(x, knock, 0.0)
    place(x, 0.5 * slosh, 0.08)
    return finish(x, -9)


def bio_react():
    """Something fermenting: slow, fat bubbles rising through a still liquid."""
    s = 1.5
    x = 0.08 * lowpass(noise(s), 400) * env(int(RATE * s), 0.3, 1.0, sustain=0.5, release=0.4)
    for at in sorted(rng.uniform(0.0, 1.25, 7)):
        d = rng.uniform(0.06, 0.1)
        f0 = rng.uniform(110, 170)
        b = tail_fade(sine(glide(f0, f0 * 2.2, d), d) * env(int(RATE * d), 0.004, d / 2.5), d / 3)
        place(x, rng.uniform(0.5, 0.9) * b, at)
    return finish(x, -9)


def hum(freq, seconds, harmonics=((1, 1.0), (2, 0.5), (3, 0.3), (5, 0.12))):
    return sum(a * sine(freq * k, seconds) for k, a in harmonics)


def electric_place():
    """A cell switched on: a relay's click, then mains hum swelling in."""
    s = 0.7
    n = int(RATE * s)
    relay = bandpass(noise(0.01), 1500, 6000) * env(int(RATE * 0.01), 0.0002, 0.002)
    x = 0.35 * hum(100, s) * env(n, 0.12, 0.25, sustain=0.0, release=0.25)
    place(x, 0.8 * relay, 0.0)
    return finish(x, -14)


def electric_react():
    """Current flowing: a buzzing hum, a fizz at the electrodes and a few sparks."""
    s = 1.3
    n = int(RATE * s)
    buzz = hum(100, s, ((1, 1.0), (2, 0.6), (3, 0.5), (4, 0.3), (6, 0.2))) * env(n, 0.08, 0.7, sustain=0.6, release=0.3)
    fizz = bandpass(noise(s), 3000, 8000) * env(n, 0.2, 0.7, sustain=0.5, release=0.3)
    x = 0.4 * buzz + 0.25 * fizz
    for _ in range(4):
        d = 0.045
        zap = sine(glide(3200, 300, d), d) * env(int(RATE * d), 0.0005, 0.012) + bandpass(noise(d), 2000, 9000) * env(int(RATE * d), 0.0003, 0.006)
        place(x, 0.6 * zap, rng.uniform(0.15, 1.1))
    return finish(x, -10)


def radiation_place():
    """A machine powering up: a rising tone that settles into a soft beep."""
    s = 0.9
    n = int(RATE * s)
    sweep = sine(glide(80, 420, 0.6), 0.6) * env(int(RATE * 0.6), 0.05, 0.4, sustain=0.6, release=0.1)
    x = np.zeros(n)
    place(x, 0.5 * sweep, 0.0)
    place(x, 0.3 * tail_fade(sine(880, 0.12) * env(int(RATE * 0.12), 0.003, 0.05), 0.04), 0.62)
    return finish(x, -17)


def radiation_react():
    """Radiation at work: a Geiger counter quickening over a low drone."""
    s = 1.4
    n = int(RATE * s)
    drone = (sine(60, s) + 0.7 * sine(61.5, s)) * env(n, 0.3, 0.8, sustain=0.6, release=0.3)
    x = 0.25 * drone
    t = 0.05
    while t < s - 0.05:
        click = bandpass(noise(0.003), 1500, 7000) * env(int(RATE * 0.003), 0.0002, 0.0008)
        place(x, rng.uniform(0.5, 1.0) * click, t)
        rate = 8 + 40 * (t / s)
        t += rng.exponential(1 / rate)
    return finish(x, -10)


def pressure_place():
    """A heavy steel vessel set down: a dull metal clank."""
    s = 0.8
    clank = bell(220, s, 0.12, ((1, 1.0), (2.32, 0.6), (3.91, 0.35), (5.43, 0.2), (7.1, 0.1)))
    thud = tail_fade(sine(glide(90, 55, 0.1), 0.1) * env(int(RATE * 0.1), 0.002, 0.03), 0.03)
    x = 0.6 * clank
    place(x, 0.8 * thud, 0.0)
    return finish(x, -10)


def pressure_react():
    """Pressure building: a hiss of steam, a strained creak, a valve letting go."""
    s = 1.4
    n = int(RATE * s)
    hiss = bandpass(noise(s), 2500, 9000) * env(n, 0.06, 0.6, sustain=0.5, release=0.35)
    creak = sine(glide(150, 115, 0.5), 0.5) * (1 + 0.6 * np.sign(np.sin(2 * np.pi * 31 * t_axis(0.5))))
    creak *= env(int(RATE * 0.5), 0.05, 0.2)
    x = 0.5 * hiss
    place(x, 0.25 * creak, 0.3)
    psst = bandpass(noise(0.25), 3000, 10000) * env(int(RATE * 0.25), 0.005, 0.08)
    place(x, 0.7 * psst, 1.05)
    return finish(x, -11)


def spin_place():
    """A centrifuge lid latched: two clicks and a small clunk."""
    s = 0.4
    x = np.zeros(int(RATE * s))
    for at in (0.0, 0.07):
        place(x, bandpass(noise(0.006), 1500, 7000) * env(int(RATE * 0.006), 0.0002, 0.0015), at)
    place(x, 0.7 * tail_fade(sine(glide(160, 120, 0.08), 0.08) * env(int(RATE * 0.08), 0.002, 0.025), 0.03), 0.14)
    return finish(x, -6)


def spin_react():
    """A centrifuge spinning up and down: a rising whine and rushing air."""
    s = 1.5
    n = int(RATE * s)
    f = np.concatenate([glide(160, 1300, 0.75, 0.7), glide(1300, 220, s - 0.75, 1.3)])[:n]
    whine = (sine(f, s) + 0.4 * sine(f * 2, s) + 0.15 * sine(f * 3, s)) * env(n, 0.1, 0.9, sustain=0.6, release=0.35)
    air = bandpass(noise(s), 500, 3000) * np.interp(np.arange(n), [0, n * 0.5, n], [0.1, 1.0, 0.1])
    return finish(0.5 * whine + 0.35 * air, -13)


def crystal_place():
    """A crystal furnace set down: a soft glassy chime."""
    s = 1.0
    x = np.zeros(int(RATE * s))
    place(x, bell(1760, 0.9, 0.3), 0.0)
    place(x, 0.6 * bell(2637, 0.8, 0.25), 0.06)
    return finish(x, -14)


def crystal_react():
    """A crystal growing: a shimmer of tiny chimes over a low hum."""
    s = 1.5
    n = int(RATE * s)
    x = 0.3 * hum(110, s, ((1, 1.0), (2, 0.3))) * env(n, 0.4, 0.8, sustain=0.5, release=0.4)
    for _ in range(16):
        place(x, rng.uniform(0.15, 0.4) * bell(rng.uniform(2000, 5200), 0.5, 0.12), rng.uniform(0.05, 1.2))
    return finish(x, -11)


SOUNDS = {
    "click": click,
    "pickup": pickup,
    "drop": drop,
    "discovery": discovery,
    "milestone": milestone,
    "fizzle": fizzle,
    "era": era,
    "fire_place": fire_place,
    "fire_react": fire_react,
    "grind_place": grind_place,
    "grind_react": grind_react,
    "cold_place": cold_place,
    "cold_react": cold_react,
    "glass_place": place_vessel,
    "glass_react": glass_react,
    "bio_place": bio_place,
    "bio_react": bio_react,
    "electric_place": electric_place,
    "electric_react": electric_react,
    "radiation_place": radiation_place,
    "radiation_react": radiation_react,
    "pressure_place": pressure_place,
    "pressure_react": pressure_react,
    "spin_place": spin_place,
    "spin_react": spin_react,
    "crystal_place": crystal_place,
    "crystal_react": crystal_react,
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
    ap.add_argument("--only", nargs="+", metavar="NAME", help="write only these sounds")
    args = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg is needed to encode the .ogg files")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, make in SOUNDS.items():
            if args.only and name not in args.only:
                continue
            wav = Path(tmp) / f"{name}.wav"
            write_wav(wav, make())
            ogg = OUT / f"{name}.ogg"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis",
                            "-q:a", "5", str(ogg)], check=True)
            if args.wav:
                args.wav.mkdir(parents=True, exist_ok=True)
                shutil.copy(wav, args.wav / wav.name)
            print(f"  {ogg.relative_to(ROOT)}  ({ogg.stat().st_size // 1024 + 1} KB)")
    print(f"{len(args.only) if args.only else len(SOUNDS)} sounds written.")


if __name__ == "__main__":
    main()
