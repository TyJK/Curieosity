// build.rs: a Windows build gets the game's icon on its .exe (assets/icon/curieosity.ico,
// drawn by tools/art/gen_steam_art.py). The running window's icon is set by the game
// itself (platform::window_icon_system); other systems take their icon from the package.
fn main() {
    println!("cargo:rerun-if-changed=assets/icon/curieosity.ico");
    println!("cargo:rerun-if-changed=build.rs");
    #[cfg(windows)]
    if std::env::var("CARGO_CFG_TARGET_OS").as_deref() == Ok("windows") {
        let mut res = winresource::WindowsResource::new();
        res.set_icon("assets/icon/curieosity.ico");
        // no resource compiler (rc.exe) to hand: the game still builds, just without the icon
        if let Err(e) = res.compile() {
            println!("cargo:warning=the .exe gets no icon: {e}");
        }
    }
}
