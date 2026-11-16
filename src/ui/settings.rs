// src/ui/settings.rs
//
// Player settings: what they are, where they are saved (settings.ron next to the save
// file), how they are applied to the window and the game, and the Settings dialog (opened
// from the gear in the header, or Esc).
use bevy::prelude::*;
use bevy::window::{MonitorSelection, PresentMode, PrimaryWindow, WindowMode};
use serde::{Deserialize, Serialize};

use crate::resources::player_progress::{save_path, write_atomic, Persistence};
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::process_toolbar::NewGameButton;
use crate::ui::theme::{self, Kind, Weight};

#[derive(Resource, Clone, Debug, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct Settings {
    /// interface zoom, 0.8 to 1.6
    pub ui_scale: f32,
    pub fullscreen: bool,
    pub vsync: bool,
    /// reactions finish this many times faster (0.5 to 4)
    pub reaction_speed: f32,
    /// inventory tiles lead with the name instead of the formula
    pub names_first: bool,
    /// discovery and milestone pop-ups
    pub notifications: bool,
    /// the faint dot grid on the bench
    pub bench_grid: bool,
    /// hover tooltips on tiles, vessels and the parts of a vessel
    pub tooltips: bool,
    /// the "next step" suggestion on the bench
    pub next_step: bool,
    /// the first-steps tour has been finished or skipped
    pub tour_done: bool,
    /// sound volume, 0 (off) to 1
    pub volume: f32,
    /// the soft tick when a button is pressed
    pub ui_sounds: bool,
}

impl Default for Settings {
    fn default() -> Self {
        Self {
            ui_scale: 1.0,
            fullscreen: false,
            vsync: true,
            reaction_speed: 1.0,
            names_first: false,
            notifications: true,
            bench_grid: true,
            tooltips: true,
            next_step: true,
            tour_done: false,
            volume: 0.6,
            ui_sounds: true,
        }
    }
}

pub fn settings_path() -> std::path::PathBuf {
    save_path().with_file_name("settings.ron")
}

#[derive(Resource, Default)]
pub struct SettingsUi {
    pub open: bool,
}

#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Field {
    UiScale,
    ReactionSpeed,
    Fullscreen,
    Vsync,
    NamesFirst,
    Notifications,
    BenchGrid,
    Tooltips,
    NextStep,
    Volume,
    UiSounds,
}

#[derive(Component)]
pub struct SettingsRoot;
#[derive(Component)]
pub struct SettingsBackdrop;
#[derive(Component)]
pub struct SettingsClose;
#[derive(Component)]
pub struct SettingStep(pub Field, pub f32);
#[derive(Component)]
pub struct SettingValue(pub Field);
#[derive(Component)]
pub struct SettingToggle(pub Field);
#[derive(Component)]
pub struct SettingKnob(pub Field);
#[derive(Component)]
pub struct SettingsAbout;

const SCALES: [f32; 9] = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6];
const SPEEDS: [f32; 5] = [0.5, 1.0, 2.0, 3.0, 4.0];
const VOLUMES: [f32; 11] = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];

impl Settings {
    fn step(&mut self, f: Field, dir: f32) {
        fn next(list: &[f32], v: f32, dir: f32) -> f32 {
            let i = list.iter().position(|x| (x - v).abs() < 0.01).unwrap_or(list.len() / 2) as i32;
            let j = (i + dir.signum() as i32).clamp(0, list.len() as i32 - 1);
            list[j as usize]
        }
        match f {
            Field::UiScale => self.ui_scale = next(&SCALES, self.ui_scale, dir),
            Field::ReactionSpeed => self.reaction_speed = next(&SPEEDS, self.reaction_speed, dir),
            Field::Volume => self.volume = next(&VOLUMES, self.volume, dir),
            _ => {}
        }
    }
    fn toggle(&mut self, f: Field) {
        match f {
            Field::Fullscreen => self.fullscreen = !self.fullscreen,
            Field::Vsync => self.vsync = !self.vsync,
            Field::NamesFirst => self.names_first = !self.names_first,
            Field::Notifications => self.notifications = !self.notifications,
            Field::BenchGrid => self.bench_grid = !self.bench_grid,
            Field::Tooltips => self.tooltips = !self.tooltips,
            Field::NextStep => self.next_step = !self.next_step,
            Field::UiSounds => self.ui_sounds = !self.ui_sounds,
            _ => {}
        }
    }
    fn flag(&self, f: Field) -> bool {
        match f {
            Field::Fullscreen => self.fullscreen,
            Field::Vsync => self.vsync,
            Field::NamesFirst => self.names_first,
            Field::Notifications => self.notifications,
            Field::BenchGrid => self.bench_grid,
            Field::Tooltips => self.tooltips,
            Field::NextStep => self.next_step,
            Field::UiSounds => self.ui_sounds,
            _ => false,
        }
    }
    fn value_text(&self, f: Field) -> String {
        match f {
            Field::UiScale => format!("{:.0}%", self.ui_scale * 100.0),
            Field::ReactionSpeed => format!(
                "{}×",
                if self.reaction_speed < 1.0 { "½".to_string() } else { format!("{:.0}", self.reaction_speed) }
            ),
            Field::Volume => {
                if self.volume <= 0.001 {
                    "Off".to_string()
                } else {
                    format!("{:.0}%", self.volume * 100.0)
                }
            }
            _ => String::new(),
        }
    }
}

/// Startup: read settings.ron (or keep the defaults).
pub fn load_settings(mut commands: Commands, persistence: Res<Persistence>) {
    let s = persistence
        .0
        .then(|| std::fs::read_to_string(settings_path()).ok())
        .flatten()
        .and_then(|t| ron::from_str::<Settings>(&t).ok())
        .unwrap_or_default();
    commands.insert_resource(s);
}

/// Apply settings to the window and UI whenever they change, and save them.
pub fn apply_settings_system(
    settings: Res<Settings>,
    persistence: Res<Persistence>,
    mut ui_scale: ResMut<UiScale>,
    mut windows: Query<&mut Window, With<PrimaryWindow>>,
    mut first: Local<bool>,
) {
    if !settings.is_changed() {
        return;
    }
    ui_scale.0 = settings.ui_scale;
    if let Ok(mut w) = windows.single_mut() {
        let mode = if settings.fullscreen {
            WindowMode::BorderlessFullscreen(MonitorSelection::Current)
        } else {
            WindowMode::Windowed
        };
        if w.mode != mode {
            w.mode = mode;
        }
        let pm = if settings.vsync { PresentMode::AutoVsync } else { PresentMode::AutoNoVsync };
        if w.present_mode != pm {
            w.present_mode = pm;
        }
    }
    // the first run is the load itself: nothing to write back
    if !*first {
        *first = true;
        return;
    }
    if persistence.0 {
        let path = settings_path();
        match ron::ser::to_string_pretty(&*settings, ron::ser::PrettyConfig::default()) {
            Ok(text) => {
                if let Err(e) = write_atomic(&path, &text) {
                    warn!("Could not write settings {}: {}", path.display(), e);
                }
            }
            Err(e) => warn!("Could not serialise settings: {}", e),
        }
    }
}

// --- the dialog ------------------------------------------------------------------------------
pub fn spawn_settings(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((
            SettingsRoot,
            GlobalZIndex(950),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(0.0),
                bottom: Val::Px(0.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                display: Display::None,
                ..default()
            },
            Name::new("Settings"),
        ))
        .with_children(|root| {
            // the backdrop: dims the game, closes the dialog when clicked
            root.spawn((
                SettingsBackdrop,
                Button,
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    right: Val::Px(0.0),
                    top: Val::Px(0.0),
                    bottom: Val::Px(0.0),
                    ..default()
                },
                BackgroundColor(Color::srgba(0.0, 0.0, 0.02, 0.62)),
            ));
            root.spawn((
                Node {
                    width: Val::Px(880.0),
                    max_width: Val::Percent(94.0),
                    max_height: Val::Percent(92.0),
                    flex_direction: FlexDirection::Column,
                    padding: UiRect::all(Val::Px(22.0)),
                    row_gap: Val::Px(10.0),
                    border: UiRect::all(Val::Px(1.0)),
                    overflow: Overflow::scroll_y(),
                    ..default()
                },
                BorderRadius::all(Val::Px(theme::R_LG)),
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE_STRONG),
                theme::shadow(40.0, 14.0, 0.6),
                ScrollPosition::default(),
                Pickable::default(),
                // clicks inside the dialog stay in it (the backdrop behind closes it)
                bevy::ui::FocusPolicy::Block,
            ))
            .with_children(|panel| {
                panel
                    .spawn(Node {
                        justify_content: JustifyContent::SpaceBetween,
                        align_items: AlignItems::Center,
                        ..default()
                    })
                    .with_children(|h| {
                        h.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Center, ..default() })
                            .with_children(|t| {
                                t.spawn(theme::icon(assets, "gear", 22.0, theme::CYAN));
                                t.spawn(theme::label(fonts, "Settings", theme::XL, Weight::Semibold, theme::TEXT));
                            });
                        theme::spawn_icon_button(h, assets, "close", 32.0, theme::TEXT_2, SettingsClose);
                    });

                // two columns: Display and Help on the left; Play and Progress on the right
                panel
                    .spawn(Node { column_gap: Val::Px(32.0), flex_shrink: 0.0, ..default() })
                    .with_children(|cols| {
                        cols.spawn(Node { flex_direction: FlexDirection::Column, flex_basis: Val::Px(0.0), flex_grow: 1.0, row_gap: Val::Px(8.0), ..default() })
                            .with_children(|c| {
                                theme::spawn_section_title(c, fonts, "Display");
                                stepper(c, fonts, assets, Field::UiScale, "Interface size", "Scales every panel, button and label.");
                                toggle(c, fonts, Field::Fullscreen, "Fullscreen", "Borderless, on the current monitor.");
                                toggle(c, fonts, Field::Vsync, "VSync", "Off for lower input lag.");
                                toggle(c, fonts, Field::BenchGrid, "Bench grid", "The faint dot grid on the lab bench.");
                                theme::spawn_section_title(c, fonts, "Help");
                                toggle(c, fonts, Field::Tooltips, "Tooltips", "Explain tiles, vessels and ports on hover.");
                                toggle(c, fonts, Field::NextStep, "Next-step card", "Suggest a step you can make right now.");
                                c.spawn(Node { justify_content: JustifyContent::SpaceBetween, align_items: AlignItems::Center, column_gap: Val::Px(12.0), min_height: Val::Px(44.0), flex_shrink: 0.0, ..default() })
                                    .with_children(|row| {
                                        row_text(row, fonts, "First-steps tour", "The four coach marks of a new game.");
                                        theme::spawn_button(row, fonts, assets, Kind::Secondary, None, "Show it again", crate::ui::onboarding::TourAgainButton);
                                    });
                            });
                        cols.spawn(Node { flex_direction: FlexDirection::Column, flex_basis: Val::Px(0.0), flex_grow: 1.0, row_gap: Val::Px(8.0), ..default() })
                            .with_children(|c| {
                                theme::spawn_section_title(c, fonts, "Play");
                                stepper(c, fonts, assets, Field::ReactionSpeed, "Reaction speed", "How fast vessels finish reacting.");
                                toggle(c, fonts, Field::NamesFirst, "Names before formulas", "Shelf tiles lead with the name.");
                                toggle(c, fonts, Field::Notifications, "Notifications", "Pop-ups for discoveries and milestones.");
                                theme::spawn_section_title(c, fonts, "Sound");
                                stepper(c, fonts, assets, Field::Volume, "Volume", "Reactions, discoveries and milestones.");
                                toggle(c, fonts, Field::UiSounds, "Button clicks", "A soft tick when a button is pressed.");
                                theme::spawn_section_title(c, fonts, "Progress");
                                c.spawn(Node { justify_content: JustifyContent::SpaceBetween, align_items: AlignItems::Center, column_gap: Val::Px(12.0), flex_shrink: 0.0, ..default() })
                                    .with_children(|row| {
                                        row.spawn(Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, ..default() })
                                            .with_children(|t| {
                                                t.spawn(theme::label(fonts, "Saved automatically to", theme::SM, Weight::Regular, theme::TEXT_2));
                                                t.spawn(theme::para(fonts, save_path().display().to_string(), theme::XS, theme::TEXT_3, Val::Px(220.0)));
                                            });
                                        theme::spawn_button(row, fonts, assets, Kind::Danger, None, "Start a new game", NewGameButton::default());
                                    });
                            });
                    });

                theme::spawn_section_title(panel, fonts, "About");
                panel
                    .spawn(Node { justify_content: JustifyContent::SpaceBetween, align_items: AlignItems::Center, column_gap: Val::Px(16.0), flex_shrink: 0.0, ..default() })
                    .with_children(|row| {
                        row.spawn(Node { flex_direction: FlexDirection::Column, row_gap: Val::Px(2.0), flex_shrink: 1.0, ..default() })
                            .with_children(|t| {
                                t.spawn((SettingsAbout, theme::para(fonts, "Curieosity", theme::SM, theme::TEXT_2, Val::Px(560.0))));
                                t.spawn(theme::para(
                                    fonts,
                                    format!(
                                        "Free, always. Code {}; content {}, drawing on Wikipedia, PubChem and other open sources.",
                                        crate::ui::credits::CODE_LICENCE,
                                        crate::ui::credits::CONTENT_LICENCE
                                    ),
                                    theme::XS,
                                    theme::TEXT_3,
                                    Val::Px(560.0),
                                ));
                            });
                        crate::ui::credits::spawn_credits_button(row, fonts, assets);
                    });
            });
        });
}

fn row_text(row: &mut ChildSpawnerCommands, fonts: &UiFonts, title: &str, hint: &str) {
    row.spawn(Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, row_gap: Val::Px(1.0), ..default() })
        .with_children(|c| {
            c.spawn(theme::label(fonts, title, theme::MD, Weight::Semibold, theme::TEXT));
            c.spawn(theme::label(fonts, hint, theme::XS, Weight::Regular, theme::TEXT_3));
        });
}

fn stepper(panel: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer, f: Field, title: &str, hint: &str) {
    panel
        .spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            align_items: AlignItems::Center,
            min_height: Val::Px(44.0),
            flex_shrink: 0.0,
            column_gap: Val::Px(12.0),
            ..default()
        })
        .with_children(|row| {
            row_text(row, fonts, title, hint);
            row.spawn(Node { align_items: AlignItems::Center, column_gap: Val::Px(8.0), ..default() }).with_children(
                |ctl| {
                    step_button(ctl, assets, "minus", SettingStep(f, -1.0));
                    ctl.spawn((Node { width: Val::Px(64.0), justify_content: JustifyContent::Center, ..default() },))
                        .with_children(|v| {
                            v.spawn((
                                SettingValue(f),
                                theme::label(fonts, "", theme::MD, Weight::Semibold, theme::CYAN),
                            ));
                        });
                    step_button(ctl, assets, "plus", SettingStep(f, 1.0));
                },
            );
        });
}

fn step_button(parent: &mut ChildSpawnerCommands, assets: &AssetServer, icon: &str, marker: SettingStep) {
    parent
        .spawn((
            theme::button(
                Kind::Secondary,
                Node {
                    width: Val::Px(32.0),
                    height: Val::Px(32.0),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    ..default()
                },
                theme::R_SM,
            ),
            marker,
        ))
        .with_children(|b| {
            b.spawn(theme::icon(assets, icon, 14.0, theme::TEXT));
        });
}

fn toggle(panel: &mut ChildSpawnerCommands, fonts: &UiFonts, f: Field, title: &str, hint: &str) {
    panel
        .spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            align_items: AlignItems::Center,
            min_height: Val::Px(44.0),
            flex_shrink: 0.0,
            column_gap: Val::Px(12.0),
            ..default()
        })
        .with_children(|row| {
            row_text(row, fonts, title, hint);
            row.spawn((
                Button,
                SettingToggle(f),
                Node {
                    width: Val::Px(48.0),
                    height: Val::Px(26.0),
                    padding: UiRect::all(Val::Px(3.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    align_items: AlignItems::Center,
                    ..default()
                },
                BorderRadius::all(Val::Px(99.0)),
                BackgroundColor(theme::RAISED),
                BorderColor::all(theme::LINE_STRONG),
            ))
            .with_children(|t| {
                t.spawn((
                    SettingKnob(f),
                    Node { width: Val::Px(18.0), height: Val::Px(18.0), ..default() },
                    BorderRadius::all(Val::Px(99.0)),
                    BackgroundColor(theme::TEXT_2),
                    Pickable::IGNORE,
                ));
            });
        });
}

/// A switch's fill and edge: cyan when on; on hover, lifted like every other button.
fn toggle_look(on: bool, hovered: bool) -> (Color, Color) {
    match (on, hovered) {
        (true, false) => (theme::CYAN.with_alpha(0.3), theme::CYAN),
        (true, true) => (theme::CYAN.with_alpha(0.42), theme::mix(theme::CYAN, theme::TEXT, 0.45)),
        (false, false) => (theme::RAISED, theme::LINE_STRONG),
        (false, true) => (theme::HOVER, theme::CYAN.with_alpha(0.8)),
    }
}

/// Open/close the dialog (gear button, Esc, backdrop, close button) and handle its controls.
pub fn settings_input_system(
    mut ui: ResMut<SettingsUi>,
    mut settings: ResMut<Settings>,
    steps: Query<(&Interaction, &SettingStep), Changed<Interaction>>,
    toggles: Query<(&Interaction, &SettingToggle), Changed<Interaction>>,
    closers: Query<&Interaction, (Changed<Interaction>, Or<(With<SettingsClose>, With<SettingsBackdrop>)>)>,
) {
    for (i, s) in &steps {
        if *i == Interaction::Pressed {
            settings.step(s.0, s.1);
        }
    }
    for (i, t) in &toggles {
        if *i == Interaction::Pressed {
            settings.toggle(t.0);
        }
    }
    for i in &closers {
        if *i == Interaction::Pressed {
            ui.open = false;
        }
    }
}

/// Show the dialog when open, and keep its values, switches and About line current.
pub fn settings_view_system(
    ui: Res<SettingsUi>,
    settings: Res<Settings>,
    db: Option<Res<RecipeDatabase>>,
    mut root: Query<&mut Node, With<SettingsRoot>>,
    mut values: Query<(&SettingValue, &mut Text), Without<SettingsAbout>>,
    mut switches: Query<
        (&SettingToggle, &Interaction, &mut BackgroundColor, &mut BorderColor, &mut Node),
        Without<SettingsRoot>,
    >,
    mut knobs: Query<(&SettingKnob, &mut BackgroundColor), Without<SettingToggle>>,
    mut about: Query<&mut Text, With<SettingsAbout>>,
    hovered: Query<(), (Changed<Interaction>, With<SettingToggle>)>,
) {
    if let Ok(mut n) = root.single_mut() {
        let d = if ui.open { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if !(settings.is_changed() || ui.is_changed() || !hovered.is_empty()) {
        return;
    }
    for (v, mut t) in &mut values {
        t.0 = settings.value_text(v.0);
    }
    for (s, i, mut bg, mut border, mut node) in &mut switches {
        let on = settings.flag(s.0);
        let (b, l) = toggle_look(on, *i != Interaction::None);
        bg.0 = b;
        *border = BorderColor::all(l);
        let j = if on { JustifyContent::FlexEnd } else { JustifyContent::FlexStart };
        if node.justify_content != j {
            node.justify_content = j;
        }
    }
    for (k, mut bg) in &mut knobs {
        bg.0 = if settings.flag(k.0) { theme::CYAN } else { theme::TEXT_3 };
    }
    if let (Some(db), Ok(mut t)) = (db, about.single_mut()) {
        t.0 = format!(
            "Curieosity · {} reactions across {} eras · {} substances to discover · built with Bevy 0.17",
            db.authored.len(),
            db.epochs.len(),
            db.canon.len()
        );
    }
}
