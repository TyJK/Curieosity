// src/main.rs
// The desktop program. The game itself is built in the library (src/game.rs), which the
// Android build starts too.
// Release builds for players (`--features gui`) open no console window on Windows.
#![cfg_attr(feature = "gui", windows_subsystem = "windows")]

fn main() -> bevy::app::AppExit {
    chem_alchemy::game::run()
}
