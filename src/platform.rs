// src/platform.rs
//
// The few things the game asks of the system around it: opening a link in the browser,
// on a desktop the window's icon, and on a phone the on-screen keyboard for the search
// boxes.
//
// Desktop systems open links with their usual command. Android has no such command: the
// link goes to the browser as an ACTION_VIEW intent, started from the game's activity over
// JNI. Android's keyboard types into the GameActivity's text field rather than sending key
// presses, so while a search box is listening its text is read back from that field. iOS
// opens links through UIApplication (the webbrowser crate) from the main thread, and its
// keyboard is winit's: typed characters arrive as key presses and are collected here.
use bevy::prelude::*;

/// While the review run checks the link buttons, the URLs they would open are collected
/// here instead of starting a browser.
pub static URL_SINK: std::sync::Mutex<Option<Vec<String>>> = std::sync::Mutex::new(None);

/// Open a web page in the system's browser.
pub fn open_url(url: &str) {
    if let Ok(mut sink) = URL_SINK.lock() {
        if let Some(urls) = sink.as_mut() {
            urls.push(url.to_string());
            return;
        }
    }
    #[cfg(target_os = "android")]
    if let Err(e) = android::open_url(url) {
        warn!("Could not open {url}: {e}");
    }
    #[cfg(target_os = "windows")]
    let _ = std::process::Command::new("cmd").args(["/C", "start", "", url]).spawn();
    #[cfg(target_os = "macos")]
    let _ = std::process::Command::new("open").arg(url).spawn();
    #[cfg(target_os = "ios")]
    if let Ok(mut queue) = IOS_URLS.lock() {
        queue.push(url.to_string());
    }
    #[cfg(all(unix, not(target_os = "macos"), not(target_os = "android"), not(target_os = "ios")))]
    let _ = std::process::Command::new("xdg-open").arg(url).spawn();
    let _ = url;
}

/// iOS opens links through UIApplication, which may only be touched from the main thread,
/// and button systems run on worker threads: `open_url` queues the link here and
/// `ios_open_url_system` opens it.
#[cfg(target_os = "ios")]
static IOS_URLS: std::sync::Mutex<Vec<String>> = std::sync::Mutex::new(Vec::new());

#[cfg(target_os = "ios")]
pub fn ios_open_url_system(_main_thread: bevy::ecs::system::NonSendMarker) {
    let urls = match IOS_URLS.lock() {
        Ok(mut queue) => std::mem::take(&mut *queue),
        Err(_) => return,
    };
    for url in urls {
        if let Err(e) = webbrowser::open(&url) {
            warn!("Could not open {url}: {e}");
        }
    }
}

/// The desktop window's icon: assets/icon/curieosity.png, set once it has loaded and the
/// window exists (winit's windows are only reachable from the main thread). A phone's icon
/// comes from its app package; the Windows .exe carries its own (build.rs).
#[cfg(not(any(target_os = "android", target_os = "ios")))]
pub fn window_icon_system(
    _main_thread: bevy::ecs::system::NonSendMarker,
    assets: Res<AssetServer>,
    images: Res<Assets<Image>>,
    windows: Query<Entity, With<bevy::window::PrimaryWindow>>,
    mut state: Local<(Option<Handle<Image>>, bool)>,
) {
    if state.1 {
        return;
    }
    let handle = state.0.get_or_insert_with(|| assets.load("icon/curieosity.png")).clone();
    let Some(image) = images.get(&handle) else { return };
    let Ok(entity) = windows.single() else { return };
    let (Some(rgba), w, h) = (image.data.clone(), image.width(), image.height()) else {
        state.1 = true;
        return;
    };
    let Ok(icon) = winit::window::Icon::from_rgba(rgba, w, h) else {
        warn!("The window icon could not be made from icon/curieosity.png");
        state.1 = true;
        return;
    };
    bevy::winit::WINIT_WINDOWS.with_borrow(|winit_windows| {
        if let Some(window) = winit_windows.get_window(entity) {
            window.set_window_icon(Some(icon));
            state.1 = true;
        }
    });
}

/// True on a phone or tablet (Android, iOS): the window is the whole screen, the game draws
/// only when something changes, and the interface first sizes itself to the screen.
pub const PHONE: bool = cfg!(any(target_os = "android", target_os = "ios"));

/// True where typing comes from an on-screen keyboard (a phone) rather than key presses.
pub const SOFT_KEYBOARD: bool = PHONE;

/// Whether typing brings up an on-screen keyboard, so the shelf search clears the screen for
/// it (SOFT_KEYBOARD; a resource so the review run can play a phone on a desktop).
#[derive(Resource, Clone, Copy, Debug, PartialEq, Eq)]
pub struct SoftKeyboard(pub bool);

impl Default for SoftKeyboard {
    fn default() -> Self {
        Self(SOFT_KEYBOARD)
    }
}

/// Show the on-screen keyboard, starting from `text` (does nothing on a desktop).
pub fn keyboard_show(text: &str) {
    #[cfg(target_os = "android")]
    android::keyboard_show(text);
    #[cfg(target_os = "ios")]
    if let Ok(mut typed) = IOS_TYPED.lock() {
        *typed = Some(text.to_string());
    }
    let _ = text;
}

/// Put the on-screen keyboard away (does nothing on a desktop).
pub fn keyboard_hide() {
    #[cfg(target_os = "android")]
    android::keyboard_hide();
    #[cfg(target_os = "ios")]
    if let Ok(mut typed) = IOS_TYPED.lock() {
        *typed = None;
    }
}

/// How much of the bottom of the screen the on-screen keyboard covers, in interface pixels
/// (0 while it is down, and on a desktop). The shelf search sits just above it.
#[derive(Resource, Default, Debug, Clone, Copy, PartialEq)]
pub struct KeyboardInset(pub f32);

/// While a search box is listening on a phone, keeps KeyboardInset in step with the keyboard:
/// on Android its height is asked of the window (its IME inset) a few times a second; iOS
/// gives no height to ask for here, so a typical keyboard's share of the screen stands in.
pub fn keyboard_inset_system(
    typing: Res<crate::ui::inventory::TypingBox>,
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    ui_scale: Res<UiScale>,
    time: Res<Time<Real>>,
    mut inset: ResMut<KeyboardInset>,
    mut last_ask: Local<f64>,
) {
    if !PHONE {
        return;
    }
    let Ok(w) = windows.single() else { return };
    let interface = |physical: f32| physical / w.scale_factor() / ui_scale.0.max(0.01);
    let want = if *typing == crate::ui::inventory::TypingBox::None {
        0.0
    } else {
        let now = time.elapsed_secs_f64();
        if now - *last_ask < 0.15 {
            return;
        }
        *last_ask = now;
        // (no answer: a keyboard's usual share of a phone's screen)
        keyboard_height().map(|h| interface(h as f32)).unwrap_or_else(|| {
            let upright = w.height() > w.width();
            interface(w.physical_height() as f32) * if upright { 0.40 } else { 0.55 }
        })
    };
    if (inset.0 - want).abs() > 0.5 {
        inset.0 = want;
    }
}

/// The on-screen keyboard's height in physical pixels, where the system says (Android).
fn keyboard_height() -> Option<i32> {
    #[cfg(target_os = "android")]
    return android::keyboard_height();
    #[cfg(not(target_os = "android"))]
    None
}

/// What the on-screen keyboard has typed so far (None on a desktop, where typing arrives as
/// key presses).
pub fn keyboard_text() -> Option<String> {
    #[cfg(target_os = "android")]
    return android::keyboard_text();
    #[cfg(target_os = "ios")]
    return IOS_TYPED.lock().ok().and_then(|typed| typed.clone());
    #[cfg(not(any(target_os = "android", target_os = "ios")))]
    None
}

/// iOS: the text typed since the keyboard came up, while it is up. winit raises the keyboard
/// when the window accepts text input (`ime_enabled`) and hands each typed character over as a
/// key press with no physical key, so `ios_keyboard_system` collects them here.
#[cfg(target_os = "ios")]
static IOS_TYPED: std::sync::Mutex<Option<String>> = std::sync::Mutex::new(None);

/// iOS: raise or lower the keyboard to match `keyboard_show`/`keyboard_hide`, and collect what
/// it types. Runs after Bevy's input systems. The keyboard's delete key also arrives as a
/// Backspace press, which the search boxes would apply a second time, so it is consumed here.
#[cfg(target_os = "ios")]
pub fn ios_keyboard_system(
    mut typed_keys: MessageReader<bevy::input::keyboard::KeyboardInput>,
    mut keys: ResMut<ButtonInput<KeyCode>>,
    mut windows: Query<&mut Window, With<bevy::window::PrimaryWindow>>,
) {
    use bevy::input::keyboard::Key;
    let Ok(mut typed) = IOS_TYPED.lock() else { return };
    if let Ok(mut window) = windows.single_mut() {
        if window.ime_enabled != typed.is_some() {
            window.ime_enabled = typed.is_some();
        }
    }
    let Some(text) = typed.as_mut() else {
        typed_keys.clear();
        return;
    };
    for key in typed_keys.read() {
        if key.state != bevy::input::ButtonState::Pressed {
            continue;
        }
        match &key.logical_key {
            Key::Character(s) => text.extend(s.chars().filter(|c| !c.is_control())),
            Key::Space => text.push(' '),
            Key::Backspace => {
                text.pop();
            }
            _ => {}
        }
    }
    keys.clear_just_pressed(KeyCode::Backspace);
}

/// How long the game sleeps between ticks while nothing on screen changes. A still screen
/// drawn 60 times a second runs a phone's battery down for nothing; this is often enough for
/// timers (a pop-up's time running out) and slow enough to cost next to nothing.
pub const IDLE_TICK: std::time::Duration = std::time::Duration::from_millis(250);

/// Whether the screen changed this frame, and for how many frames it hasn't.
#[derive(Resource, Default, Debug)]
pub struct Drawing {
    pub quiet_frames: u32,
    /// what changed this frame (for the review, when the screen won't settle)
    pub changed: Vec<&'static str>,
}

/// While anything on screen moves, or a pointer goes down, lifts or a finger moves, ask for
/// the next frame straight away; otherwise the game sleeps until the next input or
/// `IDLE_TICK`. Runs last, so it sees every change the frame made.
#[allow(clippy::type_complexity)]
pub fn keep_drawing_system(
    nodes: (
        Query<(), Changed<Node>>,
        Query<(), Changed<UiTransform>>,
        Query<(), Changed<BackgroundColor>>,
        Query<(), Changed<BorderColor>>,
        Query<(), Changed<TextColor>>,
        Query<(), Changed<Text>>,
        Query<(), Changed<ImageNode>>,
        Query<(), Changed<ScrollPosition>>,
        Query<(), Changed<Visibility>>,
    ),
    mouse: Res<ButtonInput<MouseButton>>,
    touches: Res<Touches>,
    mut drawing: ResMut<Drawing>,
    mut redraw: MessageWriter<bevy::window::RequestRedraw>,
) {
    let (node, transform, background, border, text_color, text, image, scroll, visibility) = nodes;
    let mut changed = Vec::new();
    for (what, any) in [
        ("layout", !node.is_empty()),
        ("transform", !transform.is_empty()),
        ("background", !background.is_empty()),
        ("border", !border.is_empty()),
        ("text colour", !text_color.is_empty()),
        ("text", !text.is_empty()),
        ("image", !image.is_empty()),
        ("scroll", !scroll.is_empty()),
        ("visibility", !visibility.is_empty()),
        // a press or a lift, or a finger moving: a pointer merely held down (or a touch the
        // system never reported the end of) doesn't keep the screen drawing
        (
            "pointer",
            mouse.get_just_pressed().next().is_some()
                || mouse.get_just_released().next().is_some()
                || touches.any_just_pressed()
                || touches.any_just_released()
                || touches.any_just_canceled()
                || touches.iter().any(|t| t.delta() != Vec2::ZERO),
        ),
    ] {
        if any {
            changed.push(what);
        }
    }
    if changed.is_empty() {
        drawing.quiet_frames = drawing.quiet_frames.saturating_add(1);
    } else {
        drawing.quiet_frames = 0;
        redraw.write(bevy::window::RequestRedraw);
    }
    drawing.changed = changed;
}

#[cfg(target_os = "android")]
mod android {
    use bevy::android::android_activity::input::{TextInputState, TextSpan};
    use bevy::android::ANDROID_APP;
    use jni::objects::{JObject, JValue};
    use jni::JavaVM;

    /// `startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)))` on the game's activity.
    pub fn open_url(url: &str) -> Result<(), String> {
        let app = ANDROID_APP.get().ok_or("no Android app")?;
        // SAFETY: both pointers come from the running activity and outlive this call; the
        // activity is a global reference held by android-activity, never freed here.
        let vm = unsafe { JavaVM::from_raw(app.vm_as_ptr() as *mut jni::sys::JavaVM) }.map_err(|e| e.to_string())?;
        let activity = unsafe { JObject::from_raw(app.activity_as_ptr() as jni::sys::jobject) };
        let mut env = vm.attach_current_thread().map_err(|e| e.to_string())?;
        let result = (|| -> jni::errors::Result<()> {
            let jurl = env.new_string(url)?;
            let uri = env
                .call_static_method(
                    "android/net/Uri",
                    "parse",
                    "(Ljava/lang/String;)Landroid/net/Uri;",
                    &[JValue::Object(&jurl)],
                )?
                .l()?;
            let action = env.new_string("android.intent.action.VIEW")?;
            let intent = env.new_object(
                "android/content/Intent",
                "(Ljava/lang/String;Landroid/net/Uri;)V",
                &[JValue::Object(&action), JValue::Object(&uri)],
            )?;
            env.call_method(&activity, "startActivity", "(Landroid/content/Intent;)V", &[JValue::Object(&intent)])?;
            Ok(())
        })();
        if result.is_err() && env.exception_check().unwrap_or(false) {
            // no browser installed, say: clear the Java exception so the activity carries on
            let _ = env.exception_describe();
            let _ = env.exception_clear();
        }
        result.map_err(|e| e.to_string())
    }

    pub fn keyboard_show(text: &str) {
        let Some(app) = ANDROID_APP.get() else { return };
        let end = text.len();
        app.set_text_input_state(TextInputState {
            text: text.to_string(),
            selection: TextSpan { start: end, end },
            compose_region: None,
        });
        app.show_soft_input(true);
    }

    pub fn keyboard_hide() {
        if let Some(app) = ANDROID_APP.get() {
            app.hide_soft_input(false);
        }
    }

    pub fn keyboard_text() -> Option<String> {
        ANDROID_APP.get().map(|app| app.text_input_state().text)
    }

    /// The keyboard's height in physical pixels: the window's IME inset,
    /// `getWindow().getDecorView().getRootWindowInsets().getInsets(WindowInsets.Type.ime()).bottom`
    /// (API 30 and up; the game needs 31). None if the window can't say.
    pub fn keyboard_height() -> Option<i32> {
        let app = ANDROID_APP.get()?;
        // SAFETY: as in open_url: both pointers come from the running activity.
        let vm = unsafe { JavaVM::from_raw(app.vm_as_ptr() as *mut jni::sys::JavaVM) }.ok()?;
        let activity = unsafe { JObject::from_raw(app.activity_as_ptr() as jni::sys::jobject) };
        let mut env = vm.attach_current_thread().ok()?;
        let result = (|| -> jni::errors::Result<i32> {
            let window = env.call_method(&activity, "getWindow", "()Landroid/view/Window;", &[])?.l()?;
            let decor = env.call_method(&window, "getDecorView", "()Landroid/view/View;", &[])?.l()?;
            let insets = env.call_method(&decor, "getRootWindowInsets", "()Landroid/view/WindowInsets;", &[])?.l()?;
            if insets.is_null() {
                return Ok(0);
            }
            let ime = env.call_static_method("android/view/WindowInsets$Type", "ime", "()I", &[])?.i()?;
            let ins =
                env.call_method(&insets, "getInsets", "(I)Landroid/graphics/Insets;", &[JValue::Int(ime)])?.l()?;
            env.get_field(&ins, "bottom", "I")?.i()
        })();
        if result.is_err() && env.exception_check().unwrap_or(false) {
            let _ = env.exception_clear();
        }
        result.ok()
    }
}
