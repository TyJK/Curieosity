// src/ui/process_toolbar.rs
//
// The vessel picker: the bench's Add vessel button opens it over the lab, one card per
// family of vessels (Heat, Mix, Pressure...). A card shows the family's best vessel
// unlocked so far, and a tap puts that one on the bench; where the family has more than one
// unlocked, its tier button opens the list of them to pick a lower tier (a lower tier makes
// the plainer product where two tiers know the same mix). A family with nothing unlocked
// stays in the grid, dimmed, with the discovery that unlocks it, so the player can see what
// they are working towards. Also: the data-driven milestones, and the New Game button's
// two-click logic (the button itself lives in Settings).
use crate::ui::{Button, Clicked};
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
use crate::ui::theme::{self, Kind, Weight};
use crate::ui::toasts::{ToastKind, Toasts};
use crate::GameData;

/// Sent once a new game has wiped the progress (the main menu closes on it).
#[derive(Message, Clone, Copy, Debug)]
pub struct NewGameStarted;

/// Put a fresh vessel of this kind on the bench (reaction_check::place_vessel_system).
#[derive(Message, Clone, Debug)]
pub struct PlaceVessel(pub ProcessType);

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

/// The families in the order they first unlock (the order of VESSELS).
pub fn families() -> Vec<&'static str> {
    let mut out: Vec<&'static str> = Vec::new();
    for v in VESSELS {
        if !out.contains(&v.category) {
            out.push(v.category);
        }
    }
    out
}

/// A family's vessels, highest tier first.
pub fn family_vessels(family: &str) -> Vec<&'static VesselDef> {
    let mut m: Vec<&'static VesselDef> = VESSELS.iter().filter(|v| v.category == family).collect();
    m.sort_by_key(|v| std::cmp::Reverse(v.tier));
    m
}

/// The vessel a family's card offers: its highest unlocked tier, or (nothing unlocked yet)
/// its first.
pub fn family_pick(family: &str, unlocks: &ProcessUnlocks) -> Option<&'static VesselDef> {
    let m = family_vessels(family);
    m.iter().copied().find(|v| unlocks.0.contains(&v.process)).or_else(|| m.last().copied())
}

/// The bench's Add vessel button (bench_controls spawns it).
#[derive(Component)]
pub struct AddVesselButton;

/// Whether the picker is up, and which family's tier list is open in it.
#[derive(Resource, Default, Debug)]
pub struct VesselPicker {
    pub open: bool,
    pub tiers: Option<&'static str>,
}

#[derive(Component)]
pub struct VesselPickerRoot;
/// The grid of family cards (rebuilt when the picker opens or changes).
#[derive(Component)]
pub struct VesselPickerGrid;
#[derive(Component)]
pub struct VesselPickerClose;
/// A family's card: a tap places its best unlocked vessel (or says what unlocks it).
#[derive(Component, Clone, Copy, Debug)]
pub struct PickFamily(pub &'static str);
/// A family card's tier button: opens or closes its list of vessels.
#[derive(Component, Clone, Copy, Debug)]
pub struct PickTiers(pub &'static str);
/// One vessel in an open tier list.
#[derive(Component, Clone, Debug)]
pub struct PickVessel(pub ProcessType);

pub struct VesselPickerPlugin;

impl Plugin for VesselPickerPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<VesselPicker>()
            .add_message::<PlaceVessel>()
            // (the picker is spawned with the rest of the interface, once the fonts are in)
            .add_systems(Update, (vessel_picker_input_system, vessel_picker_view_system).chain());
    }
}

pub fn spawn_vessel_picker(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    commands
        .spawn((
            VesselPickerRoot,
            GlobalZIndex(850),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(theme::HEADER_H),
                bottom: Val::Px(0.0),
                justify_content: JustifyContent::Center,
                align_items: AlignItems::FlexStart,
                padding: UiRect::all(Val::Px(12.0)),
                display: Display::None,
                ..default()
            },
            BackgroundColor(Color::srgba(0.0, 0.0, 0.03, 0.78)),
            // a tap on the backdrop closes it, and reaches nothing underneath
            Pickable::default(),
            Button,
            crate::ui::focus::NoFocus,
            VesselPickerClose,
            Name::new("VesselPicker"),
        ))
        .with_children(|root| {
            root.spawn((
                Node {
                    width: Val::Percent(100.0),
                    max_width: Val::Px(960.0),
                    max_height: Val::Percent(100.0),
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(12.0),
                    padding: UiRect::all(Val::Px(16.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE_STRONG),
                theme::shadow(28.0, 10.0, 0.6),
                Pickable::default(),
                Button,
                crate::ui::focus::NoFocus,
            ))
            .with_children(|panel| {
                panel
                    .spawn(Node {
                        justify_content: JustifyContent::SpaceBetween,
                        align_items: AlignItems::Center,
                        flex_shrink: 0.0,
                        ..default()
                    })
                    .with_children(|h| {
                        h.spawn(theme::label(&fonts, "Add a vessel", theme::XL, Weight::Semibold, theme::TEXT));
                        theme::spawn_icon_button(h, &assets, "close", 40.0, theme::TEXT_2, VesselPickerClose);
                    });
                panel.spawn((
                    VesselPickerGrid,
                    ScrollPosition::default(),
                    Node {
                        flex_wrap: FlexWrap::Wrap,
                        align_content: AlignContent::FlexStart,
                        column_gap: Val::Px(10.0),
                        row_gap: Val::Px(10.0),
                        min_height: Val::Px(0.0),
                        overflow: Overflow::scroll_y(),
                        ..default()
                    },
                    Name::new("VesselPickerGrid"),
                ));
            });
        });
}

/// The discovery that unlocks a vessel, by name.
fn unlocked_by(p: &ProcessType, db: &RecipeDatabase, subs: Option<&Substances>) -> Option<String> {
    let m = db.milestones.iter().find(|m| m.unlock.contains(p))?;
    Some(subs.and_then(|s| s.0.get(&m.on)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{}", m.on)))
}

/// Opening and closing it, the tier lists, and placing a vessel.
#[allow(clippy::too_many_arguments)]
pub fn vessel_picker_input_system(
    mut picker: ResMut<VesselPicker>,
    add: Query<(), (With<Clicked>, With<AddVesselButton>)>,
    close: Query<(), (With<Clicked>, With<VesselPickerClose>)>,
    families: Query<&PickFamily, With<Clicked>>,
    tiers: Query<&PickTiers, With<Clicked>>,
    vessels: Query<&PickVessel, With<Clicked>>,
    unlocks: Res<ProcessUnlocks>,
    db: Option<Res<RecipeDatabase>>,
    names: (Res<GameData>, Res<Assets<Substances>>),
    mut toasts: ResMut<Toasts>,
    mut place: MessageWriter<PlaceVessel>,
) {
    if !add.is_empty() {
        picker.open = true;
        picker.tiers = None;
    }
    if !picker.open {
        return;
    }
    let subs = names.1.get(&names.0.substances);
    let mut chosen: Option<ProcessType> = None;
    if let Some(t) = tiers.iter().next() {
        // (the tier button sits on its card, and only the button hears the tap)
        picker.tiers = if picker.tiers == Some(t.0) { None } else { Some(t.0) };
        return;
    }
    for v in &vessels {
        if unlocks.0.contains(&v.0) {
            chosen = Some(v.0.clone());
        } else if let Some(db) = db.as_ref() {
            toasts.push(ToastKind::Hint, unlock_reason(&v.0, db, subs));
        }
    }
    if chosen.is_none() && vessels.is_empty() {
        for f in &families {
            match family_pick(f.0, &unlocks) {
                Some(v) if unlocks.0.contains(&v.process) => chosen = Some(v.process.clone()),
                Some(v) => {
                    if let Some(db) = db.as_ref() {
                        toasts.push(ToastKind::Hint, unlock_reason(&v.process, db, subs));
                    }
                }
                None => {}
            }
        }
    }
    if let Some(p) = chosen {
        place.write(PlaceVessel(p));
        picker.open = false;
        picker.tiers = None;
    } else if !close.is_empty() && families.is_empty() && vessels.is_empty() {
        picker.open = false;
        picker.tiers = None;
    }
}

/// Builds the cards when the picker opens, a tier list opens or closes, or a vessel unlocks
/// while it is up; and sizes them to the screen (two across on a phone held upright).
#[allow(clippy::too_many_arguments)]
pub fn vessel_picker_view_system(
    mut commands: Commands,
    picker: Res<VesselPicker>,
    unlocks: Res<ProcessUnlocks>,
    db: Option<Res<RecipeDatabase>>,
    names: (Res<GameData>, Res<Assets<Substances>>),
    look: (Res<UiFonts>, Res<AssetServer>),
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    ui_scale: Res<UiScale>,
    mut root: Query<&mut Node, With<VesselPickerRoot>>,
    mut grid: Query<(Entity, Option<&Children>, &mut Node), (With<VesselPickerGrid>, Without<VesselPickerRoot>)>,
    mut built: Local<Option<(Option<&'static str>, usize, u32)>>,
) {
    let Ok(mut root_node) = root.single_mut() else { return };
    let d = if picker.open { Display::Flex } else { Display::None };
    if root_node.display != d {
        root_node.display = d;
    }
    if !picker.open {
        *built = None;
        return;
    }
    let Some(db) = db else { return };
    let width = windows.single().map(|w| w.width() / ui_scale.0.max(0.01)).unwrap_or(1280.0);
    let cols = (((width.min(960.0) - 56.0) / 220.0).floor() as usize).clamp(2, 4);
    let key = (picker.tiers, unlocks.0.len(), cols as u32);
    if *built == Some(key) {
        return;
    }
    *built = Some(key);
    let Ok((grid_e, children, mut grid_node)) = grid.single_mut() else { return };
    // a tier list open on the last row hangs below the cards: room for it to scroll to
    let fams = families();
    let last_row = picker
        .tiers
        .and_then(|f| fams.iter().position(|x| *x == f))
        .is_some_and(|i| i / cols == (fams.len() - 1) / cols);
    let room = if last_row { picker.tiers.map_or(0.0, |f| family_vessels(f).len() as f32 * 48.0 + 20.0) } else { 0.0 };
    if grid_node.padding.bottom != Val::Px(room) {
        grid_node.padding.bottom = Val::Px(room);
    }
    if let Some(c) = children {
        for e in c.iter() {
            commands.entity(e).try_despawn();
        }
    }
    let subs = names.1.get(&names.0.substances);
    let (fonts, assets) = look;
    let card_w = Val::Percent((100.0 - 1.6 * (cols as f32 - 1.0)) / cols as f32 - 0.2);
    commands.entity(grid_e).with_children(|g| {
        for fam in families() {
            let Some(pick) = family_pick(fam, &unlocks) else { continue };
            let members = family_vessels(fam);
            let open_n = members.iter().filter(|v| unlocks.0.contains(&v.process)).count();
            let open = open_n > 0;
            let accent = theme::process_color(&pick.process);
            // an open tier list hangs over the cards below it
            let open_list = picker.tiers == Some(fam);
            g.spawn((
                Node { width: card_w, flex_direction: FlexDirection::Column, ..default() },
                ZIndex(if open_list { 10 } else { 0 }),
            ))
                .with_children(|col| {
                    col.spawn((
                        theme::button(
                            if open { Kind::Accent(accent) } else { Kind::Disabled },
                            Node {
                                min_height: Val::Px(68.0),
                                align_items: AlignItems::Center,
                                column_gap: Val::Px(10.0),
                                padding: UiRect::axes(Val::Px(10.0), Val::Px(8.0)),
                                ..default()
                            },
                            theme::R_MD,
                        ),
                        PickFamily(fam),
                        crate::ui::onboarding::Tip::Vessel(pick.process.clone()),
                        Name::new(format!("Pick-{fam}")),
                    ))
                    .with_children(|b| {
                        b.spawn((
                            ImageNode::new(assets.load(vessel_art_path(&pick.process, "outline")))
                                .with_color(if open { accent } else { accent.with_alpha(0.3) }),
                            Node { width: Val::Px(44.0), height: Val::Px(44.0), flex_shrink: 0.0, ..default() },
                            Pickable::IGNORE,
                        ));
                        b.spawn((
                            Node { flex_direction: FlexDirection::Column, flex_grow: 1.0, flex_shrink: 1.0, ..default() },
                            Pickable::IGNORE,
                        ))
                        .with_children(|t| {
                            t.spawn((
                                theme::label(&fonts, pick.name, theme::MD, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                            let sub = if open {
                                format!("{} · {}", pick.category, roman(pick.tier))
                            } else {
                                match unlocked_by(&pick.process, &db, subs) {
                                    Some(n) => format!("Needs {n}"),
                                    None => "Locked".to_string(),
                                }
                            };
                            t.spawn((
                                theme::label(
                                    &fonts,
                                    sub,
                                    theme::XS,
                                    Weight::Regular,
                                    if open { theme::mix(accent, theme::TEXT_2, 0.5) } else { theme::TEXT_3 },
                                ),
                                Pickable::IGNORE,
                            ));
                        });
                        if !open {
                            b.spawn((
                                ImageNode::new(assets.load("images/ui/lock.png")).with_color(theme::TEXT_3),
                                Node { width: Val::Px(16.0), height: Val::Px(16.0), flex_shrink: 0.0, ..default() },
                                Pickable::IGNORE,
                            ));
                        } else if members.len() > 1 {
                            // the family's tiers: a dropdown of the lower ones
                            b.spawn((
                                theme::button(
                                    if picker.tiers == Some(fam) { Kind::Tab } else { Kind::Secondary },
                                    Node {
                                        height: Val::Px(36.0),
                                        min_width: Val::Px(52.0),
                                        padding: UiRect::horizontal(Val::Px(8.0)),
                                        column_gap: Val::Px(4.0),
                                        align_items: AlignItems::Center,
                                        justify_content: JustifyContent::Center,
                                        flex_shrink: 0.0,
                                        ..default()
                                    },
                                    theme::R_SM,
                                ),
                                PickTiers(fam),
                                crate::ui::onboarding::Tip::Text(
                                    "Tiers",
                                    "Pick a lower tier: where two tiers know the same mix, the lower one makes the plainer product.",
                                ),
                            ))
                            .with_children(|t| {
                                t.spawn((
                                    theme::label(&fonts, roman(pick.tier), theme::SM, Weight::Semibold, theme::TEXT),
                                    Pickable::IGNORE,
                                ));
                                t.spawn(theme::icon_down(&assets, 12.0, theme::TEXT_2));
                            });
                        }
                    });
                    if open_list {
                        col.spawn((
                            Node {
                                position_type: PositionType::Absolute,
                                top: Val::Percent(100.0),
                                left: Val::Px(0.0),
                                right: Val::Px(0.0),
                                margin: UiRect::top(Val::Px(4.0)),
                                flex_direction: FlexDirection::Column,
                                row_gap: Val::Px(4.0),
                                padding: UiRect::all(Val::Px(6.0)),
                                border: UiRect::all(Val::Px(1.0)),
                                border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                                ..default()
                            },
                            BackgroundColor(theme::SURFACE),
                            BorderColor::all(theme::LINE_STRONG),
                            theme::shadow(20.0, 6.0, 0.6),
                        ))
                        .with_children(|list| {
                        for v in &members {
                            let on = unlocks.0.contains(&v.process);
                            let c = theme::process_color(&v.process);
                            list.spawn((
                                theme::button(
                                    if on { Kind::Row } else { Kind::Disabled },
                                    Node {
                                        min_height: Val::Px(44.0),
                                        align_items: AlignItems::Center,
                                        column_gap: Val::Px(8.0),
                                        padding: UiRect::axes(Val::Px(10.0), Val::Px(4.0)),
                                        ..default()
                                    },
                                    theme::R_SM,
                                ),
                                PickVessel(v.process.clone()),
                                crate::ui::onboarding::Tip::Vessel(v.process.clone()),
                            ))
                            .with_children(|r| {
                                r.spawn((
                                    ImageNode::new(assets.load(vessel_art_path(&v.process, "outline")))
                                        .with_color(if on { c } else { c.with_alpha(0.3) }),
                                    Node { width: Val::Px(28.0), height: Val::Px(28.0), flex_shrink: 0.0, ..default() },
                                    Pickable::IGNORE,
                                ));
                                let text = if on {
                                    format!("{}  ·  {}", v.name, roman(v.tier))
                                } else {
                                    match unlocked_by(&v.process, &db, subs) {
                                        Some(n) => format!("{}  ·  needs {n}", v.name),
                                        None => v.name.to_string(),
                                    }
                                };
                                r.spawn((
                                    theme::label(&fonts, text, theme::SM, Weight::Regular, if on { theme::TEXT } else { theme::TEXT_3 }),
                                    Pickable::IGNORE,
                                ));
                            });
                        }
                        });
                    }
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
    challenge: Option<Res<crate::ui::challenges::ChallengeMode>>,
) {
    let Some(db) = db else { return };
    // a challenge's discoveries fire nothing: its kit is all it gets
    if challenge.is_some_and(|c| c.playing()) {
        return;
    }
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

/// What unlocks a vessel, and why, in a sentence ("The Bloomery unlocks with Copper: ...").
pub fn unlock_reason(p: &ProcessType, db: &RecipeDatabase, subs: Option<&Substances>) -> String {
    match unlocked_by(p, db, subs) {
        Some(n) => format!("The {} unlocks with {}. {}", vessel_name(p), n, p.why()),
        None => format!("The {} is locked.", vessel_name(p)),
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
    mut buttons: Query<(Has<Clicked>, &mut NewGameButton, &Children), With<Button>>,
    mut texts: Query<&mut Text>,
    vessels: Query<Entity, With<crate::components::VesselCard>>,
    links: Query<Entity, With<crate::components::ReactionLink>>,
    mut journal: ResMut<crate::ui::toasts::Journal>,
    mut started: MessageWriter<NewGameStarted>,
    challenge: Option<Res<crate::ui::challenges::ChallengeMode>>,
) {
    // a new game is the lab's: not from inside a challenge (its lab is set aside)
    if challenge.is_some_and(|c| c.playing()) {
        if buttons.iter().any(|(clicked, _, _)| clicked) {
            toasts.push(ToastKind::Hint, "Leave the challenge first: a new game starts the lab over.");
        }
        return;
    }
    for (clicked, mut btn, children) in &mut buttons {
        let was_armed = btn.armed_for > 0.0;
        btn.armed_for = (btn.armed_for - time.delta_secs()).max(0.0);
        let mut label = None;
        if clicked {
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn every_family_offers_its_best_unlocked_vessel() {
        let mut unlocks = ProcessUnlocks::default();
        assert_eq!(family_pick("Heat", &unlocks).map(|v| v.name), Some("Fire"));
        unlocks.0.insert(ProcessType::Smelting);
        unlocks.0.insert(ProcessType::BlastFurnace);
        assert_eq!(family_pick("Heat", &unlocks).map(|v| v.name), Some("Blast Furnace"));
        // nothing unlocked yet: the family's first vessel, to say what unlocks it
        assert_eq!(family_pick("Pressure", &unlocks).map(|v| v.name), Some("Autoclave"));
        let fams = families();
        assert_eq!(fams.first(), Some(&"Mix"));
        assert_eq!(fams.len(), 12);
        assert!(fams.iter().all(|f| !family_vessels(f).is_empty()));
    }
}
