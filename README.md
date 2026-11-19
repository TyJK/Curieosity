![Curieosity](steam/store/header_capsule.png)

# Curieosity

A free chemistry discovery game. Start with fire, ore and wood; put substances in vessels
and react them; discover 2,704 substances across 2,683 reactions and 27 vessels, from the
first copper smelted to oganesson. Every substance has a page, written for the game or
drawn from Wikipedia and other open sources, with a link to read more.

Curieosity is free, and always will be: see [Free, always](#free-always).

## Made by Tyler Kolody, with AI

Curieosity is my game. What it teaches and how, which substances and reactions are in it,
and how it looks and plays are my decisions. I built it with AI: the code, and the pages
and reactions written for the game, were written by Claude, an AI model made by Anthropic,
to my design and direction. The facts come from the open sources further down, and every
substance page names the source of its text.

Nothing in the game was made by an image or sound generator. The vessels and icons are line
art drawn by a program from plain geometry (lines, arcs and curves set by numbers), so they
share one stroke and one light. The molecule pictures are drawn by RDKit from each
compound's recorded structure, the atom diagrams from each element's electron
configuration, and the sounds are synthesised from sine waves and filtered noise. Those
programs were written with Claude too; they are in the source code, under tools/art. See
[`gen_vessels.py`](tools/art/gen_vessels.py), [`gen_bohr.py`](tools/art/gen_bohr.py) and
[`gen_sounds.py`](tools/art/gen_sounds.py).

## Play

- **Windows, macOS, Linux:** download your system's zip from the
  [latest release](https://github.com/TyJK/Curieosity/releases/latest), unzip it, and run
  `Curieosity`.
- **Android** (12 or later, 64-bit): on your phone, download
  [Curieosity-android.apk](https://github.com/TyJK/Curieosity/releases/latest/download/Curieosity-android.apk)
  and open it. Allow installing from your browser when Android asks. Later versions install
  over it and keep your progress.
- **iPhone and iPad** (iOS 15 or later): download
  [Curieosity-ios.ipa](https://github.com/TyJK/Curieosity/releases/latest/download/Curieosity-ios.ipa)
  on a Windows or Mac computer and install it with [Sideloadly](https://sideloadly.io):
  1. Plug the device into the computer, open Sideloadly, drop the .ipa on it, enter your
     Apple ID and press Start.
  2. On iOS 16 and later, turn on Settings > Privacy & Security > Developer Mode on the
     device (the switch appears after the first install; it restarts the device).
  3. On the device, open Settings > General > VPN & Device Management, tap your Apple ID
     and tap Trust.

  With a free Apple ID the app stops opening after 7 days: install it again the same way
  (don't delete it first, or its progress goes with it).

Progress saves itself. Mouse, keyboard (Tab, arrows, Enter, Esc) and controllers all work.
On a phone, swipe the shelf to scroll it; hold a tile a moment to lift it onto a vessel, or
tap a tile and then a vessel. Back works as Esc.

## Build from source

You need [Rust](https://rustup.rs) (stable). On Linux, Bevy also needs
`libasound2-dev libudev-dev libwayland-dev libxkbcommon-dev`.

```
cargo run --release
```

## Tests and the review run

```
cargo test --release                                    unit tests and content checks
cargo run --release -- --autoplay --steps 0             the interaction checks
cargo run --release -- --autoplay --steps 0 --only keyboard,sound   some of them
cargo run --release -- --autoplay                       the checks, then the whole tech tree
cargo run --release -- --autoplay --window 915x412      the same at a phone's size
```

The review run plays the game through its real input, writes a report with screenshots to
`target/review/run_<time>/report.md`, and exits with an error if anything failed. GitHub
Actions runs the tests and a short review on every pull request, and the whole tech tree
weekly.

## Content

The reactions, substances, eras and milestones are written in `tools/data/`
(`authored_content.py`, `authored_tiers.py`, `authored_pages.py`) and built into
`assets/data/` by `python tools/data/gen_authored.py`, which checks that every equation
balances and the whole tree can be played through. It also packs the game's share of the
full scraped library, which is too big for this repository and lives in `library/`
(see `tools/data/pack_library.py`).

## Android and iOS

`android/` holds the Android build: a small library crate that starts the game, and the
Gradle project that packs it with `assets/` into an APK. `ios/` holds the iOS app's
Info.plist and icon. GitHub's runners build both (the Android SDK, and Xcode on macOS)
whenever CI passes, and for each release; the APK and the .ipa are the runs' artifacts,
and a release carries them as `Curieosity-android.apk` and `Curieosity-ios.ipa`. Either
can also be built from the Actions tab ("Android" or "iOS", then "Run workflow").

Every merge to main publishes a release by itself (`.github/workflows/release.yml`),
numbered from the version in `Cargo.toml`: 0.2.0, then 0.2.1, 0.2.2 and so on. To start a
new series, change that version.

To build the APK yourself you need the Android SDK and NDK, the `aarch64-linux-android`
Rust target and `cargo install cargo-ndk`; then, in `android/`, run the two build steps
from `.github/workflows/android.yml`. The iOS app needs a Mac with Xcode and the
`aarch64-apple-ios` Rust target; `.github/workflows/ios.yml` has the steps.

## Steam

`cargo run --release --features steam` builds with Steam achievements. Steam has to be
running. The build uses the app id in `CURIEOSITY_STEAM_APP_ID` at build time, or 480
(Valve's test app) until the game has its own. The
achievement list and its icons are in `steam/`, with the store art
(`tools/art/gen_steam_art.py` draws them).

## Built from other people's work

Every source, with what the game takes from it and its terms, is in
[CREDITS.md](CREDITS.md) and on the game's About screen. In short:

- **Text and data:** [Wikipedia](https://en.wikipedia.org/) (CC BY-SA 4.0),
  [PubChem](https://pubchem.ncbi.nlm.nih.gov/) and
  [CAMEO Chemicals](https://cameochemicals.noaa.gov/) (public domain, U.S. government),
  [ChEBI](https://www.ebi.ac.uk/chebi/) (CC BY 4.0), [Wikidata](https://www.wikidata.org/)
  (CC0), and the [Chemical Reaction Database](https://kmt.vander-lingen.nl/), built on
  Daniel Lowe's reactions from U.S. patents.
- **Pictures and type:** molecules drawn with [RDKit](https://www.rdkit.org/); type in
  [Noto Sans](https://notofonts.github.io/), [DejaVu Sans](https://dejavu-fonts.github.io/)
  and [Liberation Sans](https://github.com/liberationfonts).
- **Built with:** [Bevy](https://bevy.org/) and the open-source [Rust crates](https://crates.io/)
  it stands on.

## Free, always

Curieosity will never cost money: no price, no ads, no in-app purchases, nothing locked. It
is open source, so anyone can read it, change it and share it. Most of what is in it is
other people's work: the chemists who ran these reactions, the scientists, editors and
volunteers behind PubChem, Wikipedia and the other sources, and the people who wrote the
tools it is built with. I have only repackaged their labour into a new form, and everyone
should be able to use it.

## If you'd like to give something

You never need to. If you want to, I'd rather it went to one of these:

1. [Neuroinflammation, Pain and Fatigue Laboratory](https://go.uab.edu/youngerlab): Jarred
   Younger's lab at the University of Alabama at Birmingham, researching how inflammation in
   the brain drives chronic pain and fatigue, in ME/CFS, fibromyalgia, long COVID and related
   illnesses.
2. [#MEAction](https://funraise.org/give/Myalgic-Encephalomyelitis-Action-Network-Inc/0645f869-e3b1-49cd-8cf3-5eec044e97b1/):
   the Myalgic Encephalomyelitis Action Network, a worldwide community campaigning for the
   care, research and recognition people with ME need.
3. [IACFS/ME](https://www.iacfsme.org/55671-2/): the International Association for Chronic
   Fatigue Syndrome/Myalgic Encephalomyelitis, clinicians and scientists advancing research
   and care.

## Privacy

Curieosity collects nothing about you: no account, no analytics, no ads, and nothing is
sent anywhere. Your progress is saved only on your device. Links open in your browser,
where those sites' own policies apply. A copy played through Steam tells Steam which
achievements you have earned.

## Licence

The code is licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your
option. The content (data, text, pictures and sounds) is
[CC BY-SA 4.0](LICENSE-CONTENT.md). [CREDITS.md](CREDITS.md) lists the sources and their
terms.
