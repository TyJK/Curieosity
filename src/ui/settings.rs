// src/ui/settings.rs
//
// Player settings: what they are, where they are saved (settings.ron next to the save
// file), how they are applied to the window and the game, and the Settings dialog (opened
// from the gear in the header, or Esc).
use crate::ui::{Button, Clicked, Look};
use bevy::picking::hover::Hovered;
use bevy::prelude::*;
use bevy::ui::Pressed;
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
    /// interface zoom, 0.6 to 1.6
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
    /// hints at all: off, there is no Hint button, no target kit, and a mix that doesn't
    /// react says only that (no tip at what would)
    pub hints: bool,
    /// the Hint button on the bench (named for the next-step card it replaced, so older
    /// settings files keep their choice)
    pub next_step: bool,
    /// while a target is chosen, the shelf shows only its kit
    pub kit: bool,
    /// a kit mixes in this many decoys for its biggest recipes...
    pub decoys_min: u8,
    /// ...and this many for a one-ingredient recipe (fewer ingredients, more decoys)
    pub decoys_max: u8,
    /// the first-steps tour has been finished or skipped
    pub tour_done: bool,
    /// sound volume, 0 (off) to 1
    pub volume: f32,
    /// the soft tick when a button is pressed
    pub ui_sounds: bool,
    /// a new discovery arrives as a card to tap and read (ui::discovery_card), not a toast
    pub discovery_cards: bool,
    /// an unread discovery card goes by itself after a while
    pub cards_close_themselves: bool,
    /// amounts count: reactants go in as many times as the equation says, and a wrong ratio
    /// is a dud (half the yield, the excess handed back); a short one doesn't react
    pub balanced_amounts: bool,
    /// the shelf's height as set with its grip (interface pixels); 0 sizes it to the screen
    pub shelf_h: f32,
    /// free play: the tech tree marks the steps that can be made now and shows every
    /// step's recipe (off, a step's recipe shows once it has been made)
    pub tree_ready: bool,
}

impl Settings {
    /// Whether the Hint button shows (hints on, and the button itself on).
    pub fn hint_button(&self) -> bool {
        self.hints && self.next_step
    }
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
            hints: true,
            next_step: true,
            kit: true,
            decoys_min: 3,
            decoys_max: 8,
            tour_done: false,
            volume: 0.6,
            ui_sounds: true,
            discovery_cards: true,
            cards_close_themselves: false,
            balanced_amounts: false,
            shelf_h: 0.0,
            tree_ready: false,
        }
    }
}

pub fn settings_path() -> std::path::PathBuf {
    save_path().with_file_name("settings.ron")
}

/// While true, the interface size follows the screen: set on a phone's first run (no
/// settings saved yet) and in review runs played at a set window size. Choosing a size in
/// the dialog ends it.
#[derive(Resource, Default)]
pub struct FitInterface(pub bool);

/// A review run's `--scale`: the interface size it plays at, whatever is saved.
#[derive(Resource, Default)]
pub struct ScaleOverride(pub Option<f32>);

/// The smallest screen, in interface pixels, the layout is made for (and held upright).
const FIT_W: f32 = 1100.0;
const FIT_H: f32 = 500.0;
const FIT_W_UPRIGHT: f32 = 560.0;
const FIT_H_UPRIGHT: f32 = 860.0;

/// The largest interface size (one of the dialog's steps, never above 100%) at which a
/// window of this logical size still holds the layout.
pub fn fit_scale(window: Vec2) -> f32 {
    let (w, h) = if window.y > window.x * 1.05 { (FIT_W_UPRIGHT, FIT_H_UPRIGHT) } else { (FIT_W, FIT_H) };
    let want = (window.x / w).min(window.y / h);
    SCALES.iter().copied().rfind(|s| *s <= want + 0.001 && *s <= 1.0).unwrap_or(SCALES[0])
}

pub fn fit_interface_system(
    fit: Res<FitInterface>,
    mut settings: ResMut<Settings>,
    windows: Query<&Window, With<PrimaryWindow>>,
) {
    if !fit.0 {
        return;
    }
    let Ok(w) = windows.single() else { return };
    if w.width() < 1.0 || w.height() < 1.0 {
        return;
    }
    let s = fit_scale(Vec2::new(w.width(), w.height()));
    if (settings.ui_scale - s).abs() > 0.001 {
        settings.ui_scale = s;
    }
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
    Hints,
    Hint,
    Kit,
    DecoysMin,
    DecoysMax,
    Volume,
    UiSounds,
    DiscoveryCards,
    CardsCloseThemselves,
    BalancedAmounts,
    TreeReady,
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

const SCALES: [f32; 11] = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6];
const SPEEDS: [f32; 5] = [0.5, 1.0, 2.0, 3.0, 4.0];
const VOLUMES: [f32; 11] = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
/// The most decoys a kit can be set to mix in.
pub const MOST_DECOYS: u8 = 12;

impl Settings {
    /// How many decoys a kit mixes in: (for its biggest recipes, for a one-ingredient one).
    pub fn decoy_range(&self) -> (usize, usize) {
        let (a, b) = (self.decoys_min.min(MOST_DECOYS), self.decoys_max.min(MOST_DECOYS));
        (a.min(b) as usize, a.max(b) as usize)
    }

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
            // the two stay in order: raising the fewest past the most raises the most too
            Field::DecoysMin => {
                self.decoys_min = (self.decoys_min as f32 + dir.signum()).clamp(0.0, MOST_DECOYS as f32) as u8;
                self.decoys_max = self.decoys_max.max(self.decoys_min);
            }
            Field::DecoysMax => {
                self.decoys_max = (self.decoys_max as f32 + dir.signum()).clamp(0.0, MOST_DECOYS as f32) as u8;
                self.decoys_min = self.decoys_min.min(self.decoys_max);
            }
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
            Field::Hints => self.hints = !self.hints,
            Field::Hint => self.next_step = !self.next_step,
            Field::Kit => self.kit = !self.kit,
            Field::UiSounds => self.ui_sounds = !self.ui_sounds,
            Field::DiscoveryCards => self.discovery_cards = !self.discovery_cards,
            Field::CardsCloseThemselves => self.cards_close_themselves = !self.cards_close_themselves,
            Field::BalancedAmounts => self.balanced_amounts = !self.balanced_amounts,
            Field::TreeReady => self.tree_ready = !self.tree_ready,
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
            Field::Hints => self.hints,
            Field::Hint => self.next_step,
            Field::Kit => self.kit,
            Field::UiSounds => self.ui_sounds,
            Field::DiscoveryCards => self.discovery_cards,
            Field::CardsCloseThemselves => self.cards_close_themselves,
            Field::BalancedAmounts => self.balanced_amounts,
            Field::TreeReady => self.tree_ready,
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
            Field::DecoysMin => self.decoys_min.to_string(),
            Field::DecoysMax => self.decoys_max.to_string(),
            _ => String::new(),
        }
    }
}

/// Startup: read settings.ron (or keep the defaults). With nothing saved yet, a phone
/// fits the interface to its screen.
pub fn load_settings(
    mut commands: Commands,
    persistence: Res<Persistence>,
    mut fit: ResMut<FitInterface>,
    scale: Res<ScaleOverride>,
) {
    let saved = persistence
        .0
        .then(|| std::fs::read_to_string(settings_path()).ok())
        .flatten()
        .and_then(|t| ron::from_str::<Settings>(&t).ok());
    if saved.is_none() && persistence.0 && crate::platform::PHONE {
        fit.0 = true;
    }
    let mut settings = saved.unwrap_or_default();
    if let Some(s) = scale.0 {
        settings.ui_scale = s;
    }
    commands.insert_resource(settings);
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
    // a phone's window is always the whole screen: its mode and vsync are not ours to set
    if let (false, Ok(mut w)) = (crate::platform::PHONE, windows.single_mut()) {
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
            // The dialog never grows past the screen: on a short one (a phone sideways) the
            // title and close button stay put and the rest scrolls.
            root.spawn((
                Node {
                    border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    width: Val::Px(1000.0),
                    max_width: Val::Percent(96.0),
                    max_height: Val::Percent(94.0),
                    flex_direction: FlexDirection::Column,
                    padding: UiRect::all(Val::Px(22.0)),
                    row_gap: Val::Px(10.0),
                    border: UiRect::all(Val::Px(1.0)),
                    overflow: Overflow::clip(),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE_STRONG),
                theme::shadow(40.0, 14.0, 0.6),
                // clicks inside the dialog stay in it (the backdrop behind closes it)
                Pickable::default(),
            ))
            .with_children(|dialog| {
                dialog
                    .spawn(Node {
                        justify_content: JustifyContent::SpaceBetween,
                        align_items: AlignItems::Center,
                        flex_shrink: 0.0,
                        ..default()
                    })
                    .with_children(|h| {
                        h.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Center, ..default() })
                            .with_children(|t| {
                                t.spawn(theme::icon(assets, "gear", 22.0, theme::CYAN));
                                t.spawn(theme::label(fonts, "Settings", theme::XL, Weight::Semibold, theme::TEXT));
                            });
                        theme::spawn_icon_button(h, assets, "close", 40.0, theme::TEXT_2, SettingsClose);
                    });
                dialog
                    .spawn((
                        Node {
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(10.0),
                            flex_shrink: 1.0,
                            min_height: Val::Px(0.0),
                            overflow: Overflow::scroll_y(),
                            ..default()
                        },
                        ScrollPosition::default(),
                        Pickable::default(),
                    ))
                    .with_children(|panel| {
                        // two columns: Display, Help and Sound on the left; Play, Hints and Progress
                        // on the right. Where two don't fit (a phone, a large interface size) the
                        // second goes under the first, so nothing runs off the dialog's edge.
                        panel
                            .spawn(Node {
                                column_gap: Val::Px(36.0),
                                row_gap: Val::Px(6.0),
                                flex_wrap: FlexWrap::Wrap,
                                flex_shrink: 0.0,
                                ..default()
                            })
                            .with_children(|cols| {
                                cols.spawn(column()).with_children(|c| {
                                    theme::spawn_section_title(c, fonts, "Display");
                                    stepper(
                                        c,
                                        fonts,
                                        assets,
                                        Field::UiScale,
                                        "Interface size",
                                        "Scales every panel, button and label.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::Fullscreen,
                                        "Fullscreen",
                                        "Borderless, on the current monitor.",
                                    );
                                    toggle(c, fonts, Field::Vsync, "VSync", "Off for lower input lag.");
                                    toggle(
                                        c,
                                        fonts,
                                        Field::BenchGrid,
                                        "Bench grid",
                                        "The faint dot grid on the lab bench.",
                                    );
                                    theme::spawn_section_title(c, fonts, "Help");
                                    toggle(
                                        c,
                                        fonts,
                                        Field::Tooltips,
                                        "Tooltips",
                                        "Explain tiles, vessels and ports on hover.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::DiscoveryCards,
                                        "Discovery cards",
                                        "Each new substance comes as a card to tap and read.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::CardsCloseThemselves,
                                        "Cards close by themselves",
                                        "An unread card goes after 15 seconds.",
                                    );
                                    c.spawn(Node {
                                        justify_content: JustifyContent::SpaceBetween,
                                        align_items: AlignItems::Center,
                                        column_gap: Val::Px(14.0),
                                        min_height: Val::Px(54.0),
                                        flex_shrink: 0.0,
                                        ..default()
                                    })
                                    .with_children(|row| {
                                        row_text(row, fonts, "First-steps tour", "The four coach marks of a new game.");
                                        theme::spawn_button(
                                            row,
                                            fonts,
                                            assets,
                                            Kind::Secondary,
                                            None,
                                            "Show it again",
                                            crate::ui::onboarding::TourAgainButton,
                                        );
                                    });
                                    theme::spawn_section_title(c, fonts, "Sound");
                                    stepper(
                                        c,
                                        fonts,
                                        assets,
                                        Field::Volume,
                                        "Volume",
                                        "Reactions, discoveries and milestones.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::UiSounds,
                                        "Button clicks",
                                        "A soft tick when a button is pressed.",
                                    );
                                });
                                cols.spawn(column()).with_children(|c| {
                                    theme::spawn_section_title(c, fonts, "Play");
                                    stepper(
                                        c,
                                        fonts,
                                        assets,
                                        Field::ReactionSpeed,
                                        "Reaction speed",
                                        "How fast vessels finish reacting.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::NamesFirst,
                                        "Names before formulas",
                                        "Shelf tiles lead with the name.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::BalancedAmounts,
                                        "Balanced amounts",
                                        "Put each in as often as the equation says; wrong ratios waste half.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::Notifications,
                                        "Notifications",
                                        "Pop-ups for discoveries and milestones.",
                                    );
                                    theme::spawn_section_title(c, fonts, "Hints");
                                    toggle(
                                        c,
                                        fonts,
                                        Field::Hints,
                                        "Hints",
                                        "Off: no Hint button, no kits, and no tips when a mix doesn't react.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::Hint,
                                        "Hint button",
                                        "Pick something to make next; hints come one at a time.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::Kit,
                                        "Target kits",
                                        "While you chase a target, the shelf shows only its kit.",
                                    );
                                    toggle(
                                        c,
                                        fonts,
                                        Field::TreeReady,
                                        "Show what's ready",
                                        "Free play: the tech tree marks what you can make now and shows every recipe.",
                                    );
                                    stepper(
                                        c,
                                        fonts,
                                        assets,
                                        Field::DecoysMax,
                                        "Most decoys",
                                        "Items to rule out in a one-ingredient kit.",
                                    );
                                    stepper(
                                        c,
                                        fonts,
                                        assets,
                                        Field::DecoysMin,
                                        "Fewest decoys",
                                        "One fewer per extra ingredient, down to this.",
                                    );
                                    theme::spawn_section_title(c, fonts, "Progress");
                                    c.spawn(Node {
                                        justify_content: JustifyContent::SpaceBetween,
                                        align_items: AlignItems::Center,
                                        column_gap: Val::Px(12.0),
                                        flex_shrink: 0.0,
                                        ..default()
                                    })
                                    .with_children(|row| {
                                        row.spawn(Node {
                                            flex_direction: FlexDirection::Column,
                                            flex_shrink: 1.0,
                                            ..default()
                                        })
                                        .with_children(|t| {
                                            t.spawn(theme::label(
                                                fonts,
                                                "Saved automatically to",
                                                theme::SM,
                                                Weight::Regular,
                                                theme::TEXT_2,
                                            ));
                                            t.spawn(theme::para(
                                                fonts,
                                                save_path().display().to_string(),
                                                theme::XS,
                                                theme::TEXT_2,
                                                Val::Percent(100.0),
                                            ));
                                        });
                                        theme::spawn_button(
                                            row,
                                            fonts,
                                            assets,
                                            Kind::Danger,
                                            None,
                                            "Start a new game",
                                            NewGameButton::default(),
                                        );
                                    });
                                });
                            });

                        theme::spawn_section_title(panel, fonts, "About");
                        panel
                            .spawn(Node {
                                justify_content: JustifyContent::SpaceBetween,
                                align_items: AlignItems::Center,
                                column_gap: Val::Px(16.0),
                                flex_shrink: 0.0,
                                ..default()
                            })
                            .with_children(|row| {
                                row.spawn(Node {
                                    flex_direction: FlexDirection::Column,
                                    row_gap: Val::Px(2.0),
                                    flex_shrink: 1.0,
                                    ..default()
                                })
                                .with_children(|t| {
                                    t.spawn((
                                        SettingsAbout,
                                        theme::para(fonts, "Curieosity", theme::SM, theme::TEXT_2, Val::Percent(100.0)),
                                    ));
                                    t.spawn(theme::para(
                                        fonts,
                                        format!(
                                        "Code {}; content {}, drawing on Wikipedia, PubChem and other open sources.",
                                        crate::ui::credits::CODE_LICENCE,
                                        crate::ui::credits::CONTENT_LICENCE
                                    ),
                                        theme::XS,
                                        theme::TEXT_2,
                                        Val::Percent(100.0),
                                    ));
                                });
                                crate::ui::credits::spawn_credits_button(row, fonts, assets);
                            });
                    });
            });
        });
}

/// One of the dialog's two columns: half the width, or all of it when two don't fit.
fn column() -> Node {
    Node {
        flex_direction: FlexDirection::Column,
        flex_basis: Val::Px(380.0),
        flex_grow: 1.0,
        min_width: Val::Px(0.0),
        row_gap: Val::Px(6.0),
        ..default()
    }
}

/// A setting's name and what it does, wrapping in whatever room the control leaves.
fn row_text(row: &mut ChildSpawnerCommands, fonts: &UiFonts, title: &str, hint: &str) {
    row.spawn(Node {
        flex_direction: FlexDirection::Column,
        flex_shrink: 1.0,
        flex_grow: 1.0,
        min_width: Val::Px(0.0),
        row_gap: Val::Px(2.0),
        ..default()
    })
    .with_children(|c| {
        c.spawn((
            Text::new(title),
            TextFont { font: fonts.semibold.clone().into(), font_size: FontSize::Px(16.0), ..default() },
            TextColor(theme::TEXT),
            TextLayout::linebreak(LineBreak::WordBoundary),
        ));
        c.spawn(theme::para(fonts, hint, theme::SM, theme::TEXT_2, Val::Percent(100.0)));
    });
}

fn stepper(panel: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer, f: Field, title: &str, hint: &str) {
    panel
        .spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            align_items: AlignItems::Center,
            min_height: Val::Px(54.0),
            flex_shrink: 0.0,
            column_gap: Val::Px(14.0),
            ..default()
        })
        .with_children(|row| {
            row_text(row, fonts, title, hint);
            row.spawn(Node {
                align_items: AlignItems::Center,
                column_gap: Val::Px(8.0),
                flex_shrink: 0.0,
                ..default()
            })
            .with_children(|ctl| {
                step_button(ctl, assets, "minus", SettingStep(f, -1.0));
                ctl.spawn((Node { width: Val::Px(66.0), justify_content: JustifyContent::Center, ..default() },))
                    .with_children(|v| {
                        v.spawn((SettingValue(f), theme::label(fonts, "", theme::LG, Weight::Semibold, theme::CYAN)));
                    });
                step_button(ctl, assets, "plus", SettingStep(f, 1.0));
            });
        });
}

fn step_button(parent: &mut ChildSpawnerCommands, assets: &AssetServer, icon: &str, marker: SettingStep) {
    parent
        .spawn((
            theme::button(
                Kind::Secondary,
                Node {
                    width: Val::Px(40.0),
                    height: Val::Px(40.0),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    ..default()
                },
                theme::R_SM,
            ),
            marker,
        ))
        .with_children(|b| {
            b.spawn(theme::icon(assets, icon, 16.0, theme::TEXT));
        });
}

fn toggle(panel: &mut ChildSpawnerCommands, fonts: &UiFonts, f: Field, title: &str, hint: &str) {
    panel
        .spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            align_items: AlignItems::Center,
            min_height: Val::Px(54.0),
            flex_shrink: 0.0,
            column_gap: Val::Px(14.0),
            ..default()
        })
        .with_children(|row| {
            row_text(row, fonts, title, hint);
            row.spawn((
                Button,
                SettingToggle(f),
                Node {
                    border_radius: BorderRadius::all(Val::Px(99.0)),
                    width: Val::Px(56.0),
                    height: Val::Px(32.0),
                    flex_shrink: 0.0,
                    padding: UiRect::all(Val::Px(4.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    align_items: AlignItems::Center,
                    ..default()
                },
                BackgroundColor(theme::RAISED),
                BorderColor::all(theme::LINE_STRONG),
            ))
            .with_children(|t| {
                t.spawn((
                    SettingKnob(f),
                    Node {
                        border_radius: BorderRadius::all(Val::Px(99.0)),
                        width: Val::Px(22.0),
                        height: Val::Px(22.0),
                        ..default()
                    },
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
    mut fit: ResMut<FitInterface>,
    steps: Query<&SettingStep, With<Clicked>>,
    toggles: Query<&SettingToggle, With<Clicked>>,
    closers: Query<(), (With<Clicked>, Or<(With<SettingsClose>, With<SettingsBackdrop>)>)>,
) {
    for s in &steps {
        settings.step(s.0, s.1);
        // a size chosen by hand stays
        if s.0 == Field::UiScale {
            fit.0 = false;
        }
    }
    for t in &toggles {
        settings.toggle(t.0);
    }
    if !closers.is_empty() {
        ui.open = false;
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
        (&SettingToggle, &Hovered, Has<Pressed>, &mut BackgroundColor, &mut BorderColor, &mut Node),
        Without<SettingsRoot>,
    >,
    mut knobs: Query<(&SettingKnob, &mut BackgroundColor), Without<SettingToggle>>,
    mut about: Query<&mut Text, With<SettingsAbout>>,
    hovered: Query<(), (Changed<Hovered>, With<SettingToggle>)>,
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
    for (s, h, pressed, mut bg, mut border, mut node) in &mut switches {
        let on = settings.flag(s.0);
        let (b, l) = toggle_look(on, Look::of(h, pressed).lit());
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
            "Curieosity · {} reactions across {} eras · {} substances to discover · built with Bevy 0.20",
            db.authored.len(),
            db.epochs.len(),
            db.canon.len()
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_interface_fits_the_screen() {
        // a phone held sideways (Pixel-sized, in its logical pixels)
        assert_eq!(fit_scale(Vec2::new(915.0, 412.0)), 0.8);
        // a smaller phone
        assert_eq!(fit_scale(Vec2::new(780.0, 360.0)), 0.7);
        // the desktop window, and a big monitor: never above 100%
        assert_eq!(fit_scale(Vec2::new(1280.0, 720.0)), 1.0);
        assert_eq!(fit_scale(Vec2::new(2560.0, 1440.0)), 1.0);
        // anything smaller still gets the smallest step
        assert_eq!(fit_scale(Vec2::new(400.0, 200.0)), 0.6);
    }
}
