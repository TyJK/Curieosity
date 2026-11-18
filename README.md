![Curieosity](steam/store/header_capsule.png)

# Curieosity

A free chemistry discovery game. Start with fire, ore and wood; put substances in vessels
and react them; discover 2,704 substances across 2,683 reactions and 27 vessels, from the
first copper smelted to oganesson. Every substance has a page, written for the game or
drawn from Wikipedia and other open sources, with a link to read more.

Curieosity is free, and always will be.

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

## Licence

The code is licensed under [MIT](LICENSE-MIT) or [Apache-2.0](LICENSE-APACHE), at your
option. The content (data, text, pictures and sounds) is
[CC BY-SA 4.0](LICENSE-CONTENT.md). [CREDITS.md](CREDITS.md) lists the sources and their
terms.
