// android/src/lib.rs
// The Android entry point: `#[bevy_main]` makes the `android_main` the activity calls,
// which hands the app to Bevy and starts the same game the desktop program does.
use bevy::prelude::*;

#[bevy_main]
fn main() {
    let _ = chem_alchemy::game::run();
}
