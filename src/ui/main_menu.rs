// src/ui/main_menu.rs
//
// What the game opens on: a moment of title, a notice of the licences and where the
// content comes from, then the menu (Play or Continue, a new game, Settings, Credits and,
// on a desktop, Quit). Any tap, click or key moves past the title and the notice sooner.
// During play Esc (a controller's Start, a phone's Back) brings the menu back, and again
// returns to the game. Review runs and `--skip-title` start straight in the lab.
//
// Behind every stage sits the lab's dot grid with a vessel from each family drifting over it,
// its contents glowing and bubbling, and molecules turning among them; the menu adds a strip
// of the eras, the player's own lit up to where they have reached.
use crate::ui::Clicked;
use bevy::prelude::*;

use crate::data::common::ProcessType;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::reaction_check::{accent_glow, process_color};
use crate::ui::credits::CreditsUi;
use crate::ui::onboarding::CurrentEra;
use crate::ui::process_toolbar::vessel_art_path;
use crate::ui::process_toolbar::{NewGameButton, NewGameStarted};
use crate::ui::settings::SettingsUi;
use crate::ui::theme::{self, Kind, Weight};

/// Seconds the title shows on its own, and the notice after it.
const TITLE_SECS: f32 = 1.6;
const NOTICE_SECS: f32 = 6.0;

#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum MenuStage {
    #[default]
    Title,
    Notice,
    Menu,
    /// playing
    Hidden,
}

#[derive(Resource, Debug, Default)]
pub struct MainMenu {
    pub stage: MenuStage,
    /// seconds in this stage
    t: f32,
    /// the stage the root's contents were built for
    built: Option<MenuStage>,
}

impl MainMenu {
    /// Where the game starts: the title, or straight in the lab (review runs, `--skip-title`).
    pub fn starting(skip: bool) -> Self {
        Self { stage: if skip { MenuStage::Hidden } else { MenuStage::Title }, ..default() }
    }

    /// On from the title to the notice, and from the notice to the menu.
    pub fn advance(&mut self) {
        self.stage = match self.stage {
            MenuStage::Title => MenuStage::Notice,
            MenuStage::Notice => MenuStage::Menu,
            s => s,
        };
        self.t = 0.0;
    }

    pub fn show_menu(&mut self) {
        self.stage = MenuStage::Menu;
        self.t = 0.0;
        // built again, so Play reads Continue once there is progress and the eras are current
        self.built = None;
    }

    pub fn hide(&mut self) {
        self.stage = MenuStage::Hidden;
    }
}

#[derive(Component)]
pub struct MenuRoot;
#[derive(Component)]
pub struct MenuPlay;
#[derive(Component)]
pub struct MenuSettings;
#[derive(Component)]
pub struct MenuCredits;
#[derive(Component)]
pub struct MenuQuit;
/// The drifting backdrop, built once and kept behind every stage.
#[derive(Component)]
pub struct MenuDecor;
/// The column each stage is built into.
#[derive(Component)]
pub struct MenuContent;
/// A piece of the backdrop that bobs, sways and tilts slowly (and turns, for a molecule).
#[derive(Component)]
pub struct MenuFloat {
    period: f32,
    phase: f32,
    bob: f32,
    sway: f32,
    tilt: f32,
    /// degrees per second, for a steady turn
    spin: f32,
}
/// A layer that brightens and dims: a vessel's contents, its glow, its flame or spark.
#[derive(Component)]
pub struct MenuPulse {
    color: Color,
    period: f32,
    phase: f32,
    /// how far it dims, 0..1
    depth: f32,
}
/// A bubble rising through a vessel's contents: a layer the size of the vessel moves up, and
/// the dot in it (MenuBubbleDot, on the same cycle) fades as it goes.
#[derive(Component)]
pub struct MenuBubble {
    period: f32,
    phase: f32,
    /// how far it rises, as a share of the vessel's height
    rise: f32,
}
#[derive(Component)]
pub struct MenuBubbleDot {
    color: Color,
    period: f32,
    phase: f32,
}

/// A vessel behind the menu: where (percent of the screen), how big (percent of the screen's
/// smaller side), seconds per drift, the colour of what it holds, and where its liquid is
/// (left, right, bottom, top, as shares of the art) if bubbles should rise in it.
struct Floating {
    process: ProcessType,
    x: f32,
    y: f32,
    size: f32,
    period: f32,
    contents: Color,
    liquid: Option<(f32, f32, f32, f32)>,
}

const fn vessel(
    process: ProcessType,
    (x, y, size, period): (f32, f32, f32, f32),
    contents: Color,
    liquid: Option<(f32, f32, f32, f32)>,
) -> Floating {
    Floating { process, x, y, size, period, contents, liquid }
}

/// A vessel of each family, glowing, with bubbles where there is liquid.
const FLOATING_VESSELS: &[Floating] = &[
    vessel(ProcessType::Flask, (3.0, 3.0, 18.0, 9.0), Color::srgb(0.30, 0.55, 0.95), Some((0.34, 0.66, 0.78, 0.60))),
    vessel(ProcessType::Heat, (18.0, 21.0, 20.0, 11.0), Color::srgb(0.95, 0.60, 0.20), None),
    vessel(
        ProcessType::Distillation,
        (2.0, 41.0, 19.0, 10.0),
        Color::srgb(0.85, 0.30, 0.45),
        Some((0.20, 0.40, 0.84, 0.71)),
    ),
    vessel(
        ProcessType::Electrolysis,
        (19.0, 58.0, 17.0, 8.5),
        Color::srgb(0.40, 0.75, 0.95),
        Some((0.30, 0.70, 0.80, 0.52)),
    ),
    vessel(
        ProcessType::Bioreactor,
        (3.0, 73.0, 19.0, 12.0),
        Color::srgb(0.85, 0.75, 0.35),
        Some((0.33, 0.67, 0.82, 0.42)),
    ),
    vessel(ProcessType::Catalysis, (67.0, 2.0, 16.0, 10.5), Color::srgb(0.90, 0.50, 0.20), None),
    vessel(ProcessType::Cyclotron, (83.0, 17.0, 19.0, 9.5), Color::srgb(0.80, 0.80, 0.90), None),
    vessel(ProcessType::Pressurize, (66.0, 38.0, 18.0, 11.5), Color::srgb(0.95, 0.85, 0.40), None),
    vessel(ProcessType::Cool, (84.0, 55.0, 17.0, 8.0), Color::srgb(0.40, 0.65, 1.00), None),
    vessel(ProcessType::CrystalPuller, (67.0, 72.0, 18.0, 12.5), Color::srgb(0.80, 0.85, 0.95), None),
];

/// Molecules turning slowly among them (the game's own skeletal drawings): substance id,
/// where (percent), size (percent of the smaller side), colour, degrees per second.
const FLOATING_MOLECULES: &[(u32, f32, f32, f32, Color, f32)] = &[
    (42, 27.0, 2.0, 16.0, Color::srgb(0.45, 0.52, 1.00), 3.0), // indigo
    (153, 88.0, 1.0, 12.0, Color::srgb(1.00, 0.45, 0.35), -4.0), // alizarin, madder red
    (6591, 29.0, 37.0, 13.0, Color::srgb(0.85, 0.88, 1.00), 2.5), // morphine
    (232, 29.0, 74.0, 14.0, Color::srgb(0.55, 0.95, 0.60), -3.0), // penicillin G
    (425, 82.0, 84.0, 11.0, Color::srgb(0.85, 0.88, 1.00), 4.0), // salicin, from willow bark
    (1484, 75.5, 23.0, 10.0, Color::srgb(0.75, 0.55, 1.00), -2.5), // benzanthrone, a vat dye
    (1236, 17.5, 86.0, 9.0, Color::srgb(0.35, 0.84, 0.90), 5.0), // uracil
];

pub fn spawn_main_menu(mut commands: Commands) {
    commands.spawn((
        MenuRoot,
        // over everything, the coach marks and tooltips included
        GlobalZIndex(2500),
        Node {
            position_type: PositionType::Absolute,
            left: Val::Px(0.0),
            right: Val::Px(0.0),
            top: Val::Px(0.0),
            bottom: Val::Px(0.0),
            flex_direction: FlexDirection::Column,
            align_items: AlignItems::Center,
            justify_content: JustifyContent::Center,
            row_gap: Val::Px(14.0),
            padding: UiRect::all(Val::Px(24.0)),
            display: Display::None,
            ..default()
        },
        BackgroundColor(theme::BG),
        // a tap here stays here
        Pickable::default(),
        Name::new("MainMenu"),
    ));
}

/// Times the title and the notice, moves past them on any tap, click or key, and shows
/// the stage (hidden while Settings or the Credits, opened from the menu, are on top).
#[allow(clippy::too_many_arguments)]
pub fn main_menu_system(
    mut commands: Commands,
    mut menu: ResMut<MainMenu>,
    time: Res<Time>,
    keys: Res<ButtonInput<KeyCode>>,
    mouse: Res<ButtonInput<MouseButton>>,
    touches: Res<Touches>,
    pads: Query<&Gamepad>,
    settings_ui: Res<SettingsUi>,
    credits: Res<CreditsUi>,
    progress: Res<PlayerProgress>,
    db: Option<Res<RecipeDatabase>>,
    fonts: Option<Res<UiFonts>>,
    assets: Res<AssetServer>,
    era: Option<Res<CurrentEra>>,
    mut root: Query<(Entity, &mut Node), With<MenuRoot>>,
    contents: Query<Entity, With<MenuContent>>,
) {
    let Ok((root_e, mut node)) = root.single_mut() else { return };
    menu.t += time.delta_secs();
    let any_input = keys.get_just_pressed().next().is_some()
        || mouse.get_just_pressed().next().is_some()
        || touches.any_just_pressed()
        || pads.iter().any(|g| g.get_just_pressed().next().is_some());
    match menu.stage {
        MenuStage::Title if menu.t > TITLE_SECS || (any_input && menu.t > 0.2) => menu.advance(),
        MenuStage::Notice if menu.t > NOTICE_SECS || (any_input && menu.t > 0.2) => menu.advance(),
        _ => {}
    }
    let shown = menu.stage != MenuStage::Hidden && !(settings_ui.open || credits.open);
    let d = if shown { Display::Flex } else { Display::None };
    if node.display != d {
        node.display = d;
    }
    let Some(fonts) = fonts else { return };
    if menu.built == Some(menu.stage) || menu.stage == MenuStage::Hidden {
        return;
    }
    let Ok(content) = contents.single() else {
        // the first time: the backdrop, and the column the stages go in (built next frame)
        commands.entity(root_e).with_children(|p| {
            spawn_decor(p, &assets);
            p.spawn((
                MenuContent,
                Node {
                    width: Val::Percent(100.0),
                    height: Val::Percent(100.0),
                    flex_direction: FlexDirection::Column,
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    row_gap: Val::Px(14.0),
                    ..default()
                },
                Pickable::IGNORE,
            ));
        });
        return;
    };
    menu.built = Some(menu.stage);
    let started = db.as_ref().is_some_and(|db| progress.discovered.len() > db.start.len());
    let eras: Vec<String> = db
        .as_ref()
        .map(|db| db.epochs.iter().filter(|e| e.era != "every age").map(|e| e.name.clone()).collect())
        .unwrap_or_default();
    let reached = era.map(|e| e.index as usize).unwrap_or(0);
    commands.entity(content).despawn_children();
    commands.entity(content).with_children(|p| match menu.stage {
        MenuStage::Title => spawn_title(p, &fonts, &assets, 1.0),
        MenuStage::Notice => {
            spawn_title(p, &fonts, &assets, 0.6);
            spawn_notice(p, &fonts);
            p.spawn((
                theme::label(&fonts, "tap or press any key", theme::XS, Weight::Regular, theme::TEXT_3),
                Node { margin: UiRect::top(Val::Px(10.0)), ..default() },
                Pickable::IGNORE,
            ));
        }
        MenuStage::Menu => {
            spawn_title(p, &fonts, &assets, 0.6);
            p.spawn(Node {
                flex_direction: FlexDirection::Column,
                align_items: AlignItems::Stretch,
                row_gap: Val::Px(8.0),
                width: Val::Px(280.0),
                margin: UiRect::top(Val::Px(14.0)),
                ..default()
            })
            .with_children(|col| {
                menu_button(
                    col,
                    &fonts,
                    Kind::Accent(theme::CYAN),
                    if started { "Continue" } else { "Play" },
                    MenuPlay,
                );
                if started {
                    // asks for a second tap before wiping progress, as in Settings
                    menu_button(col, &fonts, Kind::Secondary, "Start a new game", NewGameButton::default());
                }
                menu_button(col, &fonts, Kind::Secondary, "Settings", MenuSettings);
                menu_button(col, &fonts, Kind::Secondary, "Credits", MenuCredits);
                if !crate::platform::PHONE {
                    menu_button(col, &fonts, Kind::Ghost, "Quit", MenuQuit);
                }
            });
            spawn_eras(p, &fonts, &eras, reached);
        }
        MenuStage::Hidden => {}
    });
}

/// The backdrop: the lab's dot grid, a violet glow behind the title, darker edges, a vessel of
/// each family glowing with its contents (bubbling where they are liquid), and some of the
/// molecules the game draws, turning slowly.
fn spawn_decor(p: &mut ChildSpawnerCommands, assets: &AssetServer) {
    let full = || Node {
        position_type: PositionType::Absolute,
        left: Val::Px(0.0),
        right: Val::Px(0.0),
        top: Val::Px(0.0),
        bottom: Val::Px(0.0),
        ..default()
    };
    p.spawn((MenuDecor, full(), Pickable::IGNORE)).with_children(|d| {
        d.spawn((
            ImageNode {
                image: assets.load("images/ui/grid_dot.png"),
                color: Color::srgba(0.55, 0.65, 1.0, 0.10),
                image_mode: NodeImageMode::Tiled { tile_x: true, tile_y: true, stretch_value: 1.0 },
                ..default()
            },
            full(),
            Pickable::IGNORE,
        ));
        d.spawn((
            full(),
            BackgroundGradient::from(RadialGradient::new(
                UiPosition::anchor(Vec2::new(0.0, -0.14)),
                RadialGradientShape::FarthestCorner,
                vec![
                    ColorStop::new(Color::srgba(0.45, 0.30, 0.85, 0.20), Val::Percent(0.0)),
                    ColorStop::new(Color::NONE, Val::Percent(38.0)),
                ],
            )),
            Pickable::IGNORE,
        ));
        let layer = || Node {
            position_type: PositionType::Absolute,
            width: Val::Percent(100.0),
            height: Val::Percent(100.0),
            ..default()
        };
        for (i, f) in FLOATING_VESSELS.iter().enumerate() {
            let k = i as f32;
            let family = process_color(&f.process);
            d.spawn((
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Percent(f.x),
                    top: Val::Percent(f.y),
                    width: Val::VMin(f.size),
                    height: Val::VMin(f.size),
                    ..default()
                },
                UiTransform::default(),
                MenuFloat { period: f.period, phase: k * 0.37, bob: 10.0, sway: 5.0, tilt: 5.0, spin: 0.0 },
                Pickable::IGNORE,
            ))
            .with_children(|v| {
                // a soft glow of the family's colour behind it
                v.spawn((
                    Node {
                        position_type: PositionType::Absolute,
                        left: Val::Percent(-30.0),
                        top: Val::Percent(-30.0),
                        width: Val::Percent(160.0),
                        height: Val::Percent(160.0),
                        ..default()
                    },
                    BackgroundGradient::from(RadialGradient::new(
                        UiPosition::CENTER,
                        RadialGradientShape::ClosestSide,
                        vec![
                            ColorStop::new(family.with_alpha(0.16), Val::Percent(0.0)),
                            ColorStop::new(Color::NONE, Val::Percent(100.0)),
                        ],
                    )),
                    Pickable::IGNORE,
                ));
                // what it holds, glowing; the vessel; its flame, spark or frost, flickering
                let flicker = if f.process == ProcessType::Heat { 0.9 } else { 2.6 };
                for (art, color, pulse) in [
                    ("fill", f.contents.with_alpha(0.6), Some((3.4, 0.35))),
                    ("outline", family.with_alpha(0.72), None),
                    ("accent", accent_glow(&f.process).with_alpha(0.75), Some((flicker, 0.55))),
                ] {
                    let mut e = v.spawn((
                        ImageNode { image: assets.load(vessel_art_path(&f.process, art)), color, ..default() },
                        layer(),
                        Pickable::IGNORE,
                    ));
                    if let Some((period, depth)) = pulse {
                        e.insert(MenuPulse { color, period, phase: k * 0.23, depth });
                    }
                }
                // bubbles rising through the liquid
                let Some((left, right, bottom, top)) = f.liquid else { return };
                let light = f.contents.mix(&Color::WHITE, 0.55).with_alpha(0.85);
                for b in 0..4 {
                    let bf = b as f32;
                    let x = left + (right - left) * (0.15 + 0.7 * ((bf * 0.37 + k * 0.13) % 1.0));
                    let (period, phase) = (2.0 + 0.45 * bf, bf * 0.27 + k * 0.11);
                    v.spawn((
                        layer(),
                        UiTransform::default(),
                        MenuBubble { period, phase, rise: bottom - top },
                        Pickable::IGNORE,
                    ))
                    .with_children(|w| {
                        w.spawn((
                            Node {
                                position_type: PositionType::Absolute,
                                left: Val::Percent(x * 100.0 - 1.6),
                                top: Val::Percent(bottom * 100.0 - 4.0),
                                width: Val::Percent(3.2),
                                height: Val::Percent(3.2),
                                border_radius: BorderRadius::MAX,
                                ..default()
                            },
                            BackgroundColor(Color::NONE),
                            MenuBubbleDot { color: light, period, phase },
                            Pickable::IGNORE,
                        ));
                    });
                }
            });
        }
        // molecules, turning slowly
        for (i, (id, x, y, size, color, spin)) in FLOATING_MOLECULES.iter().enumerate() {
            let k = i as f32;
            d.spawn((
                ImageNode {
                    image: assets.load(format!("structures/{id}.png")),
                    color: color.with_alpha(0.42),
                    ..default()
                },
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Percent(*x),
                    top: Val::Percent(*y),
                    width: Val::VMin(*size),
                    height: Val::VMin(*size),
                    ..default()
                },
                UiTransform::default(),
                MenuFloat { period: 14.0 + k * 1.7, phase: k * 0.29, bob: 8.0, sway: 10.0, tilt: 0.0, spin: *spin },
                Pickable::IGNORE,
            ));
        }
        // darker towards the edges, over the drifting things too
        d.spawn((
            full(),
            BackgroundGradient::from(RadialGradient::new(
                UiPosition::CENTER,
                RadialGradientShape::FarthestCorner,
                vec![
                    ColorStop::new(Color::NONE, Val::Percent(55.0)),
                    ColorStop::new(Color::srgba(0.0, 0.0, 0.03, 0.6), Val::Percent(100.0)),
                ],
            )),
            Pickable::IGNORE,
        ));
    });
}

/// The eras along the foot of the menu: those reached in full colour, the current one in
/// gold, those still ahead faint.
fn spawn_eras(p: &mut ChildSpawnerCommands, fonts: &UiFonts, eras: &[String], reached: usize) {
    p.spawn((
        Node {
            position_type: PositionType::Absolute,
            bottom: Val::Px(4.0),
            left: Val::Px(0.0),
            right: Val::Px(0.0),
            flex_wrap: FlexWrap::Wrap,
            justify_content: JustifyContent::Center,
            align_items: AlignItems::Center,
            column_gap: Val::Px(10.0),
            row_gap: Val::Px(4.0),
            ..default()
        },
        Pickable::IGNORE,
    ))
    .with_children(|row| {
        for (i, name) in eras.iter().enumerate() {
            if i > 0 {
                row.spawn((theme::label(fonts, "·", theme::XS, Weight::Regular, theme::TEXT_3), Pickable::IGNORE));
            }
            let (weight, color) = match i.cmp(&reached) {
                std::cmp::Ordering::Less => (Weight::Regular, theme::TEXT_2),
                std::cmp::Ordering::Equal => (Weight::Semibold, theme::GOLD),
                std::cmp::Ordering::Greater => (Weight::Regular, theme::TEXT_3.with_alpha(0.55)),
            };
            row.spawn((theme::label(fonts, name.to_uppercase(), theme::XS, weight, color), Pickable::IGNORE));
        }
    });
}

/// The backdrop's life while the title or the menu shows: everything drifts, molecules turn,
/// vessels' contents and flames pulse, and bubbles rise and fade.
pub fn menu_float_system(
    time: Res<Time>,
    menu: Res<MainMenu>,
    mut floats: Query<(&MenuFloat, &mut UiTransform), Without<MenuBubble>>,
    mut pulses: Query<(&MenuPulse, &mut ImageNode)>,
    mut bubbles: Query<(&MenuBubble, &mut UiTransform), Without<MenuFloat>>,
    mut dots: Query<(&MenuBubbleDot, &mut BackgroundColor)>,
) {
    if menu.stage == MenuStage::Hidden {
        return;
    }
    let t = time.elapsed_secs();
    let tau = std::f32::consts::TAU;
    for (f, mut tf) in &mut floats {
        let a = tau * (t / f.period + f.phase);
        tf.translation = Val2::px(f.sway * (a * 0.5).cos(), f.bob * a.sin());
        tf.rotation = Rot2::degrees(f.tilt * (a * 0.5 + 0.8).sin() + f.spin * t);
    }
    for (p, mut img) in &mut pulses {
        let w = 0.5 + 0.5 * (tau * (t / p.period + p.phase)).sin();
        img.color = p.color.with_alpha(p.color.alpha() * (1.0 - p.depth * w));
    }
    // a bubble's place in its rise, 0 at the bottom to 1 at the top
    let rise = |period: f32, phase: f32| (t / period + phase).fract();
    for (b, mut tf) in &mut bubbles {
        tf.translation = Val2::percent(0.0, -rise(b.period, b.phase) * b.rise * 100.0);
    }
    for (d, mut bg) in &mut dots {
        let u = rise(d.period, d.phase);
        let fade = if u < 0.15 { u / 0.15 } else { 1.0 - (u - 0.15) / 0.85 };
        bg.0 = d.color.with_alpha(d.color.alpha() * fade);
    }
}

/// One of the menu's buttons: a wide button with its label as the only child (New Game's
/// system rewrites that label while it waits for the second tap).
fn menu_button(col: &mut ChildSpawnerCommands, fonts: &UiFonts, kind: Kind, label: &str, marker: impl Bundle) {
    col.spawn((
        theme::button(
            kind,
            Node {
                height: Val::Px(44.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                ..default()
            },
            theme::R_MD,
        ),
        marker,
    ))
    .with_children(|t| {
        t.spawn((theme::label(fonts, label, theme::MD, Weight::Semibold, theme::TEXT), Pickable::IGNORE));
    });
}

/// The flask and the name, at `scale` of their full size.
fn spawn_title(p: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer, scale: f32) {
    p.spawn((
        // the bare flask (the app icon's dark plate would show against the glow)
        ImageNode::new(assets.load("images/ui/logo.png")),
        Node { width: Val::Px(128.0 * scale), height: Val::Px(128.0 * scale), ..default() },
        Pickable::IGNORE,
    ));
    p.spawn((theme::label(fonts, "Curieosity", 64.0 * scale, Weight::Semibold, theme::TEXT), Pickable::IGNORE));
    p.spawn((
        theme::label(fonts, "Chemistry through the ages", 20.0 * scale.max(0.8), Weight::Regular, theme::CYAN),
        Pickable::IGNORE,
    ));
}

/// Where everything comes from, and the terms it comes under (the full list is the
/// Credits screen, built from the same sources as CREDITS.md).
fn spawn_notice(p: &mut ChildSpawnerCommands, fonts: &UiFonts) {
    // on a panel, so the drifting backdrop never runs through the text
    p.spawn((
        Node {
            flex_direction: FlexDirection::Column,
            align_items: AlignItems::Center,
            row_gap: Val::Px(8.0),
            max_width: Val::Px(660.0),
            margin: UiRect::top(Val::Px(18.0)),
            padding: UiRect::axes(Val::Px(20.0), Val::Px(14.0)),
            border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
            ..default()
        },
        BackgroundColor(theme::BG.with_alpha(0.9)),
    ))
    .with_children(|c| {
        for (text, color) in [
            ("Free and open source, and always will be.", theme::TEXT),
            ("The code is MIT or Apache-2.0. The content (data, text, pictures and sounds) is CC BY-SA 4.0, as its sources require.", theme::TEXT_2),
            ("Text adapted from Wikipedia (CC BY-SA 4.0). Data from PubChem and CAMEO Chemicals (public domain, U.S. government), ChEBI (CC BY 4.0), Wikidata (CC0) and the Chemical Reaction Database. Molecule pictures drawn with RDKit; made with Bevy.", theme::TEXT_2),
            ("Every substance page names its source. The full credits are under Credits.", theme::TEXT_3),
        ] {
            c.spawn((
                Text::new(text),
                TextFont { font: fonts.main.clone().into(), font_size: FontSize::Px(theme::SM), ..default() },
                TextColor(color),
                TextLayout::justify(Justify::Center),
                Pickable::IGNORE,
            ));
        }
    });
}

/// The menu's buttons, and closing the menu once a new game has started from it.
#[allow(clippy::type_complexity)]
pub fn main_menu_button_system(
    mut menu: ResMut<MainMenu>,
    plays: Query<(), (With<Clicked>, With<MenuPlay>)>,
    settings: Query<(), (With<Clicked>, With<MenuSettings>)>,
    credits: Query<(), (With<Clicked>, With<MenuCredits>)>,
    quits: Query<(), (With<Clicked>, With<MenuQuit>)>,
    mut started: MessageReader<NewGameStarted>,
    mut settings_ui: ResMut<SettingsUi>,
    mut credits_ui: ResMut<CreditsUi>,
    mut exit: MessageWriter<AppExit>,
) {
    let new_game = started.read().count() > 0;
    if menu.stage != MenuStage::Menu {
        return;
    }
    if !plays.is_empty() || new_game {
        menu.hide();
    }
    if !settings.is_empty() {
        settings_ui.open = true;
    }
    if !credits.is_empty() {
        credits_ui.open = true;
    }
    if !quits.is_empty() {
        exit.write(AppExit::Success);
    }
}
