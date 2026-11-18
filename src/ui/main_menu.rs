// src/ui/main_menu.rs
//
// What the game opens on: a moment of title, a notice of the licences and where the
// content comes from, then the menu (Play or Continue, a new game, Settings, Credits and,
// on a desktop, Quit). Any tap, click or key moves past the title and the notice sooner.
// During play Esc (a controller's Start, a phone's Back) brings the menu back, and again
// returns to the game. Review runs and `--skip-title` start straight in the lab.
//
// Behind every stage sits the lab's dot grid with a vessel from each family and a few
// formulas drifting slowly over it; the menu adds a strip of the eras, the player's own
// lit up to where they have reached.
use crate::ui::Interaction;
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
/// A piece of the backdrop that bobs, sways and tilts slowly.
#[derive(Component)]
pub struct MenuFloat {
    period: f32,
    phase: f32,
    bob: f32,
    sway: f32,
    tilt: f32,
}

/// The vessels drifting behind the menu, one per family: where (percent of the screen), how
/// big (percent of its smaller side) and how slowly they move (seconds per cycle).
const FLOATING_VESSELS: &[(ProcessType, f32, f32, f32, f32)] = &[
    (ProcessType::Mix, 7.0, 9.0, 13.0, 9.0),
    (ProcessType::Heat, 19.0, 29.0, 15.0, 11.0),
    (ProcessType::Distillation, 5.0, 49.0, 14.0, 10.0),
    (ProcessType::Electrolysis, 18.0, 66.0, 12.0, 8.5),
    (ProcessType::Fermenter, 6.0, 80.0, 12.0, 12.0),
    (ProcessType::Catalysis, 80.0, 8.0, 12.0, 10.5),
    (ProcessType::Cyclotron, 89.0, 26.0, 14.0, 9.5),
    (ProcessType::Pressurize, 77.0, 45.0, 14.0, 11.5),
    (ProcessType::Cool, 89.0, 63.0, 12.0, 8.0),
    (ProcessType::CrystalPuller, 78.0, 79.0, 13.0, 12.5),
];

/// Formulas drifting among them: text, where (percent), size (px).
const FLOATING_FORMULAS: &[(&str, f32, f32, f32)] = &[
    ("H₂O", 28.0, 13.0, 22.0),
    ("NaCl", 2.0, 34.0, 18.0),
    ("Fe₂O₃", 29.0, 47.0, 20.0),
    ("CO₂", 29.0, 86.0, 18.0),
    ("H₂SO₄", 67.0, 21.0, 20.0),
    ("CaCO₃", 89.0, 47.0, 17.0),
    ("C₆H₁₂O₆", 66.0, 64.0, 18.0),
    ("NH₃", 92.0, 88.0, 18.0),
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
        Pickable::default(),
        // a tap here stays here
        bevy::ui::FocusPolicy::Block,
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
            spawn_decor(p, &fonts, &assets);
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

/// The backdrop: the lab's dot grid, a violet glow behind the title, darker edges, and a
/// vessel of each family with a few formulas drifting over it, all faint enough to read
/// the menu over.
fn spawn_decor(p: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer) {
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
        for (i, (process, x, y, size, period)) in FLOATING_VESSELS.iter().enumerate() {
            let k = i as f32;
            d.spawn((
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Percent(*x),
                    top: Val::Percent(*y),
                    width: Val::VMin(*size),
                    height: Val::VMin(*size),
                    ..default()
                },
                UiTransform::default(),
                MenuFloat { period: *period, phase: k * 0.37, bob: 9.0, sway: 4.0, tilt: 5.0 },
                Pickable::IGNORE,
            ))
            .with_children(|v| {
                for (layer, color) in [
                    ("outline", process_color(process).with_alpha(0.30)),
                    ("accent", accent_glow(process).with_alpha(0.22)),
                ] {
                    v.spawn((
                        ImageNode { image: assets.load(vessel_art_path(process, layer)), color, ..default() },
                        Node {
                            position_type: PositionType::Absolute,
                            width: Val::Percent(100.0),
                            height: Val::Percent(100.0),
                            ..default()
                        },
                        Pickable::IGNORE,
                    ));
                }
            });
        }
        for (i, (text, x, y, size)) in FLOATING_FORMULAS.iter().enumerate() {
            let k = i as f32;
            d.spawn((
                theme::label(fonts, *text, *size, Weight::Semibold, theme::CYAN.with_alpha(0.28)),
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Percent(*x),
                    top: Val::Percent(*y),
                    ..default()
                },
                UiTransform::default(),
                MenuFloat { period: 13.0 + k * 1.3, phase: k * 0.21, bob: 6.0, sway: 10.0, tilt: 0.0 },
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

/// The backdrop's slow drift, while the title or the menu shows.
pub fn menu_float_system(time: Res<Time>, menu: Res<MainMenu>, mut floats: Query<(&MenuFloat, &mut UiTransform)>) {
    if menu.stage == MenuStage::Hidden {
        return;
    }
    let t = time.elapsed_secs();
    for (f, mut tf) in &mut floats {
        let a = std::f32::consts::TAU * (t / f.period + f.phase);
        tf.translation = Val2::px(f.sway * (a * 0.5).cos(), f.bob * a.sin());
        tf.rotation = Rot2::degrees(f.tilt * (a * 0.5 + 0.8).sin());
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
    plays: Query<&Interaction, (Changed<Interaction>, With<MenuPlay>)>,
    settings: Query<&Interaction, (Changed<Interaction>, With<MenuSettings>)>,
    credits: Query<&Interaction, (Changed<Interaction>, With<MenuCredits>)>,
    quits: Query<&Interaction, (Changed<Interaction>, With<MenuQuit>)>,
    mut started: MessageReader<NewGameStarted>,
    mut settings_ui: ResMut<SettingsUi>,
    mut credits_ui: ResMut<CreditsUi>,
    mut exit: MessageWriter<AppExit>,
) {
    let new_game = started.read().count() > 0;
    if menu.stage != MenuStage::Menu {
        return;
    }
    let pressed = |mut it: Vec<&Interaction>| it.drain(..).any(|i| *i == Interaction::Pressed);
    if pressed(plays.iter().collect()) || new_game {
        menu.hide();
    }
    if pressed(settings.iter().collect()) {
        settings_ui.open = true;
    }
    if pressed(credits.iter().collect()) {
        credits_ui.open = true;
    }
    if pressed(quits.iter().collect()) {
        exit.write(AppExit::Success);
    }
}
