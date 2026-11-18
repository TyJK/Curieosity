// src/ui/process_toolbar.rs
//
// The vessel sidebar on the right of the lab: one card per vessel. Unlocked vessels are
// buttons that put a fresh vessel on the bench; locked ones stay visible, dimmed, with the
// discovery that unlocks them, so the player can see what they are working towards.
// Also: the data-driven milestones, and the New Game button's two-click logic (the button
// itself lives in Settings).
use crate::ui::{Button, Interaction};
use bevy::platform::collections::HashSet;
use bevy::prelude::*;

use crate::data::common::ProcessType;
use crate::data::substances::Substances;
use crate::resources::player_progress::{
    keep_copy_before_new_game, reset_progress, FiredMilestones, Persistence, PlayerProgress,
};
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::autoplay::GameEvent;
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::ui::toasts::{ToastKind, Toasts};
use crate::GameData;

/// Component on each vessel button. Carries the underlying `process` (used for reaction
/// matching) plus the player-facing vessel `name` (the innovation, e.g. "Bloomery").
#[derive(Component, Clone)]
pub struct ProcessButton {
    pub process: ProcessType,
    pub name: String,
}

/// The "Needs ... · why?" line on a locked vessel button (a tap says why).
#[derive(Component)]
pub struct VesselLockText(pub ProcessType);

/// The vessel art on a sidebar button (dimmed while locked).
#[derive(Component)]
pub struct VesselButtonArt(pub ProcessType);

/// The lock icon on a locked vessel button.
#[derive(Component)]
pub struct VesselLockIcon(pub ProcessType);

/// Sent once a new game has wiped the progress (the main menu closes on it).
#[derive(Message, Clone, Copy, Debug)]
pub struct NewGameStarted;

/// The New Game button (in Settings and the main menu): asks for a second click before
/// wiping progress.
#[derive(Component, Default)]
pub struct NewGameButton {
    armed_for: f32,
}

/// A named, tiered vessel. `process` is the engine's ProcessType (what reactions match on);
/// `name` is the innovation shown to the player; `category`/`tier` keep the underlying
/// "type" clear (e.g. a Bloomery is a tier-II Heat vessel that matches the Smelting process).
pub type VesselDef = crate::data::common::VesselSpec;

/// The vessels (the table lives with the data: `crate::data::common::VESSEL_SPECS`).
pub const VESSELS: &[VesselDef] = crate::data::common::VESSEL_SPECS;

/// Asset path of one layer ("outline", "fill" or "accent") of a process's vessel art.
pub fn vessel_art_path(p: &ProcessType, layer: &str) -> String {
    let stem = VESSELS.iter().find(|v| &v.process == p).map(|v| v.art).unwrap_or("mortar");
    format!("images/vessels/{stem}_{layer}.png")
}

/// Player-facing vessel name for a process.
pub fn vessel_name(p: &ProcessType) -> &'static str {
    VESSELS.iter().find(|v| &v.process == p).map(|v| v.name).unwrap_or(match p {
        ProcessType::ApplyCurrent => "Battery",
        ProcessType::Wait => "Rest",
        _ => "Vessel",
    })
}

pub fn roman(tier: u8) -> &'static str {
    match tier {
        1 => "I",
        2 => "II",
        3 => "III",
        4 => "IV",
        _ => "V",
    }
}

/// Which processes the player has unlocked. Starts with the mortar (Mix) and the open fire
/// (Heat); the authored milestones unlock the rest.
#[derive(Resource)]
pub struct ProcessUnlocks(pub HashSet<ProcessType>);

impl Default for ProcessUnlocks {
    fn default() -> Self {
        let mut set = HashSet::new();
        set.insert(ProcessType::Mix);
        set.insert(ProcessType::Heat);
        Self(set)
    }
}

/// The vessel sidebar (scrolls with the wheel when the list is taller than the window).
#[derive(Component)]
pub struct VesselSidebar;

pub fn spawn_process_toolbar(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    commands
        .spawn((
            Node {
                position_type: PositionType::Absolute,
                right: Val::Px(0.0),
                top: Val::Px(theme::HEADER_H),
                bottom: Val::Px(theme::DOCK_H),
                width: Val::Px(theme::SIDEBAR_W),
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(6.0),
                padding: UiRect::new(Val::Px(12.0), Val::Px(12.0), Val::Px(12.0), Val::Px(12.0)),
                border: UiRect::left(Val::Px(1.0)),
                overflow: Overflow::scroll_y(),
                ..default()
            },
            BackgroundColor(theme::SURFACE),
            BorderColor::all(theme::LINE),
            ScrollPosition::default(),
            VesselSidebar,
            Name::new("VesselSidebar"),
        ))
        .with_children(|parent| {
            parent
                .spawn(Node {
                    justify_content: JustifyContent::SpaceBetween,
                    align_items: AlignItems::Center,
                    margin: UiRect::bottom(Val::Px(4.0)),
                    ..default()
                })
                .with_children(|h| {
                    h.spawn(theme::label(&fonts, "VESSELS", theme::XS, Weight::Bold, theme::TEXT_3));
                    h.spawn(theme::label(&fonts, "tap to place", theme::XS, Weight::Regular, theme::TEXT_3));
                });
            for v in VESSELS {
                let accent = theme::process_color(&v.process);
                parent
                    .spawn((
                        theme::button(
                            Kind::Accent(accent),
                            Node {
                                min_height: Val::Px(50.0),
                                flex_shrink: 0.0,
                                flex_direction: FlexDirection::Row,
                                align_items: AlignItems::Center,
                                column_gap: Val::Px(10.0),
                                padding: UiRect::axes(Val::Px(8.0), Val::Px(6.0)),
                                ..default()
                            },
                            theme::R_MD,
                        ),
                        ProcessButton { process: v.process.clone(), name: v.name.to_string() },
                        crate::ui::onboarding::Tip::Vessel(v.process.clone()),
                    ))
                    .with_children(|b| {
                        b.spawn((
                            VesselButtonArt(v.process.clone()),
                            ImageNode::new(assets.load(vessel_art_path(&v.process, "outline"))).with_color(accent),
                            Node { width: Val::Px(36.0), height: Val::Px(36.0), flex_shrink: 0.0, ..default() },
                            Pickable::IGNORE,
                        ));
                        b.spawn((
                            Node { flex_direction: FlexDirection::Column, flex_grow: 1.0, ..default() },
                            Pickable::IGNORE,
                        ))
                        .with_children(|col| {
                            col.spawn((
                                theme::label(&fonts, v.name, theme::MD, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                            col.spawn((
                                theme::label(
                                    &fonts,
                                    format!("{} · {}", v.category, roman(v.tier)),
                                    theme::XS,
                                    Weight::Regular,
                                    theme::mix(accent, theme::TEXT_2, 0.5),
                                ),
                                Pickable::IGNORE,
                            ));
                            col.spawn((
                                VesselLockText(v.process.clone()),
                                theme::label(&fonts, "", theme::XS, Weight::Regular, theme::TEXT_3),
                                Node { display: Display::None, ..default() },
                                Pickable::IGNORE,
                            ));
                        });
                        b.spawn((
                            VesselLockIcon(v.process.clone()),
                            ImageNode::new(assets.load("images/ui/lock.png")).with_color(theme::TEXT_3),
                            Node { width: Val::Px(16.0), height: Val::Px(16.0), display: Display::None, ..default() },
                            Pickable::IGNORE,
                        ));
                    });
            }
        });
}

/// Fires the authored milestones: discovering a milestone's substance unlocks its vessels
/// and hands over its raw materials, with a toast. Milestones already satisfied by a loaded
/// save are applied silently on the first pass.
pub fn milestone_system(
    db: Option<Res<RecipeDatabase>>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    mut progress: ResMut<PlayerProgress>,
    mut unlocks: ResMut<ProcessUnlocks>,
    mut toasts: ResMut<Toasts>,
    mut state: ResMut<FiredMilestones>,
    mut events: MessageWriter<GameEvent>,
) {
    let Some(db) = db else { return };
    if !progress.ready || !(progress.is_changed() || !state.primed) {
        return;
    }
    let FiredMilestones { fired, primed } = &mut *state;
    let subs = substances.get(&game_data.substances);
    let name_of =
        |id: u32| subs.and_then(|s| s.0.get(&id)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{}", id));

    // Grants can satisfy further milestones, so loop until nothing new fires.
    loop {
        let mut any = false;
        for (i, m) in db.milestones.iter().enumerate() {
            if fired.contains(&i) || !progress.discovered.contains(&m.on) {
                continue;
            }
            fired.insert(i);
            any = true;
            let mut new_vessels = Vec::new();
            for p in &m.unlock {
                if unlocks.0.insert(p.clone()) {
                    new_vessels.push((vessel_name(p), p.why()));
                }
            }
            let mut new_materials = Vec::new();
            for g in &m.grant {
                if progress.discovered.insert(*g) {
                    new_materials.push(name_of(*g));
                }
            }
            if !*primed {
                continue; // loading a save: apply quietly
            }
            events.write(GameEvent::Milestone { index: i, on: m.on });
            if let Some(msg) = &m.message {
                toasts.push(ToastKind::Milestone, msg.clone());
            }
            for (v, why) in new_vessels {
                toasts.push(ToastKind::Milestone, format!("New vessel unlocked: {v}. {why}"));
            }
            if !new_materials.is_empty() {
                // a long grant reads better as a count than as a wall of names
                const SHOWN: usize = 5;
                let text = if new_materials.len() > SHOWN {
                    format!(
                        "New materials: {} and {} more on the shelf",
                        new_materials[..SHOWN].join(", "),
                        new_materials.len() - SHOWN
                    )
                } else {
                    format!("New materials: {}", new_materials.join(", "))
                };
                toasts.push(ToastKind::Milestone, text);
            }
        }
        if !any {
            break;
        }
    }
    *primed = true;
}

/// Locked vessels stay in the list, dimmed and disabled, with the discovery that unlocks
/// them. Only touches nodes when something actually changes.
pub fn gate_process_buttons_system(
    unlocks: Res<ProcessUnlocks>,
    db: Option<Res<RecipeDatabase>>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    progress: Res<PlayerProgress>,
    mut buttons: Query<(&ProcessButton, &mut Skin, &Interaction, &mut BackgroundColor, &mut BorderColor)>,
    mut lock_texts: Query<(&VesselLockText, &mut Text, &mut Node), Without<VesselLockIcon>>,
    mut lock_icons: Query<(&VesselLockIcon, &mut Node), Without<VesselLockText>>,
    mut arts: Query<(&VesselButtonArt, &mut ImageNode)>,
    mut done: Local<bool>,
) {
    let Some(db) = db else { return };
    if *done && !unlocks.is_changed() && !progress.is_changed() && !db.is_changed() {
        return;
    }
    *done = true;
    let subs = substances.get(&game_data.substances);
    let unlocked_by = |p: &ProcessType| -> Option<String> {
        let m = db.milestones.iter().find(|m| m.unlock.contains(p))?;
        Some(subs.and_then(|s| s.0.get(&m.on)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{}", m.on)))
    };
    for (btn, mut skin, interaction, mut bg, mut border) in &mut buttons {
        let open = unlocks.0.contains(&btn.process);
        let accent = theme::process_color(&btn.process);
        let kind = if open { Kind::Accent(accent) } else { Kind::Disabled };
        if skin.kind != kind {
            skin.kind = kind;
            let (b, l) = skin.colors(*interaction);
            bg.0 = b;
            *border = BorderColor::all(l);
        }
    }
    for (lt, mut text, mut node) in &mut lock_texts {
        let open = unlocks.0.contains(&lt.0);
        node.display = if open { Display::None } else { Display::Flex };
        if !open {
            text.0 = match unlocked_by(&lt.0) {
                Some(n) => format!("Needs {} · why?", n),
                None => "Locked".to_string(),
            };
        }
    }
    for (a, mut img) in &mut arts {
        let c = theme::process_color(&a.0);
        img.color = if unlocks.0.contains(&a.0) { c } else { c.with_alpha(0.3) };
    }
    for (li, mut node) in &mut lock_icons {
        node.display = if unlocks.0.contains(&li.0) { Display::None } else { Display::Flex };
    }
}

/// What unlocks a vessel, and why, in a sentence ("The Bloomery unlocks with Copper: ...").
pub fn unlock_reason(p: &ProcessType, db: &RecipeDatabase, subs: Option<&Substances>) -> String {
    let by = db
        .milestones
        .iter()
        .find(|m| m.unlock.contains(p))
        .map(|m| subs.and_then(|s| s.0.get(&m.on)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{}", m.on)));
    match by {
        Some(n) => format!("The {} unlocks with {}. {}", vessel_name(p), n, p.why()),
        None => format!("The {} is locked.", vessel_name(p)),
    }
}

/// Tapping a locked vessel says what unlocks it and why (a phone has no hover tooltip).
pub fn locked_vessel_tap_system(
    buttons: Query<(&Interaction, &ProcessButton), Changed<Interaction>>,
    unlocks: Res<ProcessUnlocks>,
    db: Option<Res<RecipeDatabase>>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    mut toasts: ResMut<Toasts>,
) {
    let Some(db) = db else { return };
    for (i, b) in &buttons {
        if *i == Interaction::Pressed && !unlocks.0.contains(&b.process) {
            toasts.push(ToastKind::Hint, unlock_reason(&b.process, &db, substances.get(&game_data.substances)));
        }
    }
}

/// A short bench (a phone held sideways) packs the vessel list tighter, so more of it shows.
pub fn sidebar_fit_system(
    dock: Res<crate::ui::inventory::Dock>,
    new_buttons: Query<(), Added<ProcessButton>>,
    mut buttons: Query<&mut Node, With<ProcessButton>>,
    mut arts: Query<&mut Node, (With<VesselButtonArt>, Without<ProcessButton>)>,
) {
    if !(dock.is_changed() || !new_buttons.is_empty()) {
        return;
    }
    let compact = dock.bench < crate::systems::reaction_check::COMPACT_BENCH;
    let (min_h, pad_y, art) = if compact { (40.0, 3.0, 26.0) } else { (50.0, 6.0, 36.0) };
    for mut n in &mut buttons {
        if n.min_height != Val::Px(min_h) {
            n.min_height = Val::Px(min_h);
            n.padding = UiRect::axes(Val::Px(8.0), Val::Px(pad_y));
        }
    }
    for mut n in &mut arts {
        if n.width != Val::Px(art) {
            n.width = Val::Px(art);
            n.height = Val::Px(art);
        }
    }
}

/// New Game: the first click arms the button for three seconds, the second wipes progress
/// back to the starting inventory and clears the bench.
pub fn new_game_button_system(
    mut commands: Commands,
    time: Res<Time>,
    db: Option<Res<RecipeDatabase>>,
    mut progress: ResMut<PlayerProgress>,
    mut unlocks: ResMut<ProcessUnlocks>,
    mut fired: ResMut<FiredMilestones>,
    mut toasts: ResMut<Toasts>,
    persistence: Res<Persistence>,
    mut buttons: Query<(Ref<Interaction>, &mut NewGameButton, &Children), With<Button>>,
    mut texts: Query<&mut Text>,
    vessels: Query<Entity, With<crate::components::VesselCard>>,
    links: Query<Entity, With<crate::components::ReactionLink>>,
    mut journal: ResMut<crate::ui::toasts::Journal>,
    mut started: MessageWriter<NewGameStarted>,
) {
    for (interaction, mut btn, children) in &mut buttons {
        let was_armed = btn.armed_for > 0.0;
        btn.armed_for = (btn.armed_for - time.delta_secs()).max(0.0);
        let mut label = None;
        if interaction.is_changed() && *interaction == Interaction::Pressed {
            if btn.armed_for > 0.0 {
                if let Some(db) = db.as_ref() {
                    if persistence.0 {
                        keep_copy_before_new_game();
                    }
                    reset_progress(&mut progress, &mut unlocks, &mut fired, db);
                    journal.0.clear();
                    for v in &vessels {
                        commands.entity(v).despawn();
                    }
                    for l in &links {
                        commands.entity(l).despawn();
                    }
                    toasts.push(ToastKind::Milestone, "A fresh start: back to fire and ore.");
                    started.write(NewGameStarted);
                }
                btn.armed_for = 0.0;
                label = Some("Start a new game");
            } else {
                btn.armed_for = 3.0;
                label = Some("Again to wipe your progress");
            }
        } else if was_armed && btn.armed_for == 0.0 {
            label = Some("Start a new game");
        }
        if let Some(label) = label {
            for child in children.iter() {
                if let Ok(mut t) = texts.get_mut(child) {
                    t.0 = label.to_string();
                }
            }
        }
    }
}
