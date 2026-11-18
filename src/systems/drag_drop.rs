// src/systems/drag_drop.rs
//
// Everything the pointer drags on the bench:
//   * a shelf tile onto a vessel (anywhere on the card: picture, title, contents, button)
//     -> it goes into the vessel; onto a catalyst slot -> it becomes the catalyst
//   * a chip already in a vessel -> onto another vessel moves it there; anywhere off the
//     cards takes it back out
//   * a vessel card -> moves it (snapping to a 20 px grid)
//   * the empty bench -> pans it
//   * a vessel's output port onto another vessel's input port -> links them
// and the click that goes with a selection: with a substance selected on the shelf,
// clicking a vessel puts it in. The vessel last placed, tapped, moved or filled is the
// active one: a double-tap on a shelf tile puts that substance straight into it.
//
// On a touch screen a finger swiping across the shelf scrolls it; holding a tile for a
// moment first lifts it instead (tapping it and then a vessel works too).
//
// Where a drop lands is read from bevy_picking's hover map for the pointer that did the
// dragging, walking up from whatever is under it to the card. That makes the whole card a
// drop target, and it works the same for the mouse and for the review run's virtual
// pointer. Positions from the pointer are window pixels; nodes are UI pixels, so every
// distance is divided by the interface size (UiScale).
use crate::ui::Button;
use bevy::ecs::system::SystemParam;
use bevy::picking::hover::{HoverMap, PreviousHoverMap};
use bevy::picking::pointer::{PointerId, PointerPressState};
use bevy::prelude::*;

use crate::components::ui_markers::{
    CanvasScrollingPane, InCatalystZone, InputPort, OutputPort, ReactionCanvasRoot, ReactionLink, VesselCard,
    VesselCatalystZone, VesselIngredientZone,
};
use crate::components::{format_formula, Draggable, InVessel, Ingredient};
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::detail_panel::SelectedSubstance;
use crate::ui::inventory::{element_tile_color, is_element_formula, spawn_vessel_chip, ChipRole};
use crate::ui::shell::TouchScroll;
use crate::ui::theme::{self, Weight};
use crate::GameData;

pub struct DragDropPlugin;

/// The output port a link is being dragged from.
#[derive(Resource, Default)]
pub struct LinkDragState(pub Option<Entity>);

/// The vessel last placed, tapped, moved or filled: where a double-tapped shelf tile goes.
#[derive(Resource, Default, Debug)]
pub struct ActiveVessel(pub Option<Entity>);

/// Put this substance into the active vessel (a double-tap on its shelf tile).
#[derive(Message, Clone, Copy, Debug)]
pub struct AddToActive(pub u32);

impl Plugin for DragDropPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<LinkDragState>()
            .init_resource::<ActiveVessel>()
            .init_resource::<BenchZoom>()
            .add_message::<AddToActive>()
            // PreUpdate: its commands land before Update can despawn a freshly spawned tile
            // (the shelf rebuilds itself when a milestone grants new substances).
            .add_systems(PreUpdate, attach_drag_observers_to_draggables)
            .add_systems(Update, (sweep_drags_system, add_to_active_system, active_vessel_system, bench_zoom_system));
    }
}

/// A card's layout position when its drag began.
#[derive(Component)]
struct DragStartPos {
    left: f32,
    top: f32,
}

/// The bench pane's offset when a pan began.
#[derive(Component)]
struct PanStartPos {
    left: f32,
    top: f32,
}

/// Set on a card or tile once a drag has really moved it, so the click that bevy_picking
/// sends on release (before DragEnd) is not taken as a click.
#[derive(Component)]
pub struct DragMoved;

/// A dragged shelf tile stays put (it lives in the shelf's clipped, scrolling panel); a
/// floating copy follows the pointer instead. While any tile carries this, the shelf holds
/// off rebuilding itself (a rebuild would despawn the tile mid-drag).
#[derive(Component)]
pub struct DragGhost {
    ghost: Entity,
    half: Vec2,
}

/// The floating copy, and the tile it belongs to.
#[derive(Component)]
pub struct DragGhostNode {
    pub owner: Entity,
}

/// The layer a dragged card or tile is lifted to while the drag lasts (and only then).
const LIFT: i32 = 100;

const GHOST_W: f32 = 132.0;
const GHOST_H: f32 = 40.0;
/// Pointer travel (window px) before a press counts as a drag rather than a click.
const MOVE_SLOP: f32 = 4.0;
/// How long a finger holds a shelf tile before moving for the move to lift it (seconds);
/// a quicker move swipes the shelf.
pub const LIFT_HOLD: f64 = 0.3;

/// When a finger came down on a shelf tile.
#[derive(Component)]
struct FingerDown(f64);

/// A shelf tile a finger is swiping across rather than lifting.
#[derive(Component)]
pub struct Swiping;

fn attach_drag_observers_to_draggables(
    mut commands: Commands,
    new_ingredients: Query<Entity, (Added<Draggable>, With<Ingredient>)>,
    new_vessels: Query<Entity, (Added<Draggable>, With<VesselCard>)>,
    new_panes: Query<Entity, Added<CanvasScrollingPane>>,
    new_output_ports: Query<Entity, (Added<Draggable>, With<OutputPort>)>,
) {
    // No GlobalZIndex at rest: a node with one is drawn as its own root, in an order Bevy
    // does not keep stable between roots on the same layer, so a vessel card could be drawn
    // over its own contents. Only a drag lifts a node (LIFT), and the drop puts it back.
    for entity in &new_ingredients {
        commands
            .entity(entity)
            .try_insert((Outline::default(), Pickable::default()))
            .observe(finger_down)
            .observe(start_drag)
            .observe(update_drag)
            .observe(stop_drag_ingredient);
    }
    for entity in &new_vessels {
        commands
            .entity(entity)
            .insert((Outline::default(), Pickable::default()))
            .observe(start_drag)
            .observe(update_drag)
            .observe(stop_drag_vessel)
            .observe(click_card);
    }
    for entity in &new_panes {
        commands.entity(entity).observe(start_pan_canvas).observe(update_pan_canvas).observe(stop_pan_canvas);
    }
    for entity in &new_output_ports {
        commands.entity(entity).observe(start_draw_link).observe(stop_draw_link);
    }
}

// ---------------------------------------------------------------------------------------
// Where a drop lands
// ---------------------------------------------------------------------------------------
/// What a drop (or a click) lands on.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum DropSpot {
    /// the Catalyst Bed's slot
    Catalyst { zone: Entity, vessel: Entity },
    /// anywhere else on a card: its contents
    Ingredients { zone: Entity, vessel: Entity },
    /// a vessel's input port (for links)
    InputPort { port: Entity, vessel: Entity },
}

/// What one entity on the way up from the pointer is.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Part {
    Card,
    IngredientZone,
    CatalystZone,
    InputPort,
    /// a button or output port inside a card: a click there is that control's, not a drop
    Control,
    Other,
}

/// Walk up from `start` to its card and say what was hit. Pure, so it is unit-tested below.
pub fn classify_chain(
    start: Entity,
    parent: impl Fn(Entity) -> Option<Entity>,
    part: impl Fn(Entity) -> Part,
    ingredient_zone_of: impl Fn(Entity) -> Option<Entity>,
) -> (Option<DropSpot>, bool) {
    let (mut catalyst, mut ingredients, mut port, mut control) = (None, None, None, false);
    let mut e = start;
    for _ in 0..24 {
        match part(e) {
            Part::CatalystZone => catalyst = catalyst.or(Some(e)),
            Part::IngredientZone => ingredients = ingredients.or(Some(e)),
            Part::InputPort => port = port.or(Some(e)),
            Part::Control => control = true,
            Part::Card => {
                let vessel = e;
                let spot = if let Some(zone) = catalyst {
                    Some(DropSpot::Catalyst { zone, vessel })
                } else if let Some(port) = port {
                    Some(DropSpot::InputPort { port, vessel })
                } else {
                    ingredients
                        .or_else(|| ingredient_zone_of(vessel))
                        .map(|zone| DropSpot::Ingredients { zone, vessel })
                };
                return (spot, control);
            }
            Part::Other => {}
        }
        match parent(e) {
            Some(p) => e = p,
            None => break,
        }
    }
    (None, control)
}

#[derive(SystemParam)]
pub struct DropProbe<'w, 's> {
    hover: Res<'w, HoverMap>,
    previous: Res<'w, PreviousHoverMap>,
    parents: Query<'w, 's, &'static ChildOf>,
    children: Query<'w, 's, &'static Children>,
    cards: Query<'w, 's, (), With<VesselCard>>,
    ingredient_zones: Query<'w, 's, (), With<VesselIngredientZone>>,
    catalyst_zones: Query<'w, 's, (), With<VesselCatalystZone>>,
    input_ports: Query<'w, 's, (), With<InputPort>>,
    controls: Query<'w, 's, (), Or<(With<Button>, With<OutputPort>)>>,
}

impl DropProbe<'_, '_> {
    fn part(&self, e: Entity) -> Part {
        if self.cards.contains(e) {
            Part::Card
        } else if self.catalyst_zones.contains(e) {
            Part::CatalystZone
        } else if self.ingredient_zones.contains(e) {
            Part::IngredientZone
        } else if self.input_ports.contains(e) {
            Part::InputPort
        } else if self.controls.contains(e) {
            Part::Control
        } else {
            Part::Other
        }
    }

    pub fn classify(&self, e: Entity) -> (Option<DropSpot>, bool) {
        classify_chain(
            e,
            |x| self.parents.get(x).ok().map(|c| c.parent()),
            |x| self.part(x),
            |card| self.children.get(card).ok().and_then(|c| c.iter().find(|ch| self.ingredient_zones.contains(*ch))),
        )
    }

    /// The drop spot under a pointer right now (topmost hit first). A finger is gone by
    /// the time its lift is handled, so for a finger it is where it was a frame before.
    pub fn under(&self, pointer: PointerId) -> Option<DropSpot> {
        let now = self.hover.get(&pointer).filter(|h| !h.is_empty());
        let hits = match (now, pointer) {
            (Some(h), _) => h,
            (None, PointerId::Touch(_)) => self.previous.get(&pointer)?,
            (None, _) => return None,
        };
        let mut hits: Vec<(Entity, f32)> = hits.iter().map(|(e, h)| (*e, h.depth)).collect();
        hits.sort_by(|a, b| a.1.total_cmp(&b.1));
        hits.into_iter().find_map(|(e, _)| self.classify(e).0)
    }
}

// ---------------------------------------------------------------------------------------
// Dragging
// ---------------------------------------------------------------------------------------
fn finger_down(trigger: On<PointerPress>, mut commands: Commands, time: Res<Time<Real>>) {
    if matches!(trigger.pointer.id, PointerId::Touch(_)) {
        commands.entity(trigger.entity).try_insert(FingerDown(time.elapsed_secs_f64()));
    }
}

#[allow(clippy::too_many_arguments)]
fn start_drag(
    mut trigger: On<PointerDragStart>,
    mut commands: Commands,
    existing: Query<&DragGhost>,
    mut vessel_query: Query<(&mut Outline, &Node), With<VesselCard>>,
    mut tile_query: Query<(&mut Outline, &Ingredient), Without<VesselCard>>,
    chips: Query<(), Or<(With<InVessel>, With<InCatalystZone>)>>,
    fingers: Query<&FingerDown>,
    time: Res<Time<Real>>,
    ui_scale: Res<UiScale>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
) {
    // Don't let the drag bubble up to the bench pane (which would pan it).
    trigger.propagate(false);
    let e = trigger.entity;

    if let Ok((mut outline, node)) = vessel_query.get_mut(e) {
        outline.width = Val::Px(2.0);
        outline.color = theme::CYAN;
        let left = if let Val::Px(px) = node.left { px } else { 0.0 };
        let top = if let Val::Px(px) = node.top { px } else { 0.0 };
        commands.entity(e).insert((DragStartPos { left, top }, GlobalZIndex(LIFT)));
        return;
    }

    // a finger moving straight off a shelf tile swipes the shelf
    if matches!(trigger.pointer.id, PointerId::Touch(_)) && !chips.contains(e) {
        let held = fingers.get(e).map(|f| time.elapsed_secs_f64() - f.0).unwrap_or(0.0);
        if held < LIFT_HOLD {
            commands.entity(e).try_insert(Swiping);
            return;
        }
    }
    let Ok((mut outline, ing)) = tile_query.get_mut(e) else { return };
    // never two copies of one tile
    if let Ok(old) = existing.get(e) {
        commands.entity(old.ghost).despawn();
    }
    outline.width = Val::Px(2.0);
    outline.color = theme::CYAN;

    // The floating copy, centred on the pointer.
    let s = ui_scale.0.max(0.01);
    let half = Vec2::new(GHOST_W, GHOST_H) * 0.5;
    let at = trigger.pointer.position / s - half;
    let accent = if is_element_formula(&ing.formula) { element_tile_color(&ing.formula) } else { theme::CYAN };
    let ghost = commands
        .spawn((
            DragGhostNode { owner: e },
            Node {
                border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                position_type: PositionType::Absolute,
                left: Val::Px(at.x),
                top: Val::Px(at.y),
                width: Val::Px(GHOST_W),
                height: Val::Px(GHOST_H),
                align_items: AlignItems::Center,
                column_gap: Val::Px(8.0),
                padding: UiRect::horizontal(Val::Px(8.0)),
                border: UiRect::all(Val::Px(1.5)),
                ..default()
            },
            BackgroundColor(theme::mix(theme::RAISED, accent, 0.16).with_alpha(0.95)),
            BorderColor::all(accent),
            theme::shadow(18.0, 6.0, 0.55),
            GlobalZIndex(1000),
            // pointer events fall through to whatever is under it
            Pickable::IGNORE,
            Name::new("DragGhost"),
        ))
        .with_children(|c| {
            if is_element_formula(&ing.formula) {
                c.spawn((
                    theme::label(
                        &fonts,
                        ing.formula.chars().filter(|ch| ch.is_alphabetic()).collect::<String>(),
                        18.0,
                        Weight::Bold,
                        accent,
                    ),
                    Pickable::IGNORE,
                ));
            } else {
                c.spawn((
                    ImageNode::new(assets.load(format!("structures/{}.png", ing.id))),
                    Node { width: Val::Px(26.0), height: Val::Px(26.0), flex_shrink: 0.0, ..default() },
                    Pickable::IGNORE,
                ));
            }
            c.spawn((Node { flex_direction: FlexDirection::Column, ..default() }, Pickable::IGNORE)).with_children(
                |t| {
                    t.spawn((
                        theme::label(&fonts, format_formula(&ing.formula), theme::SM, Weight::Semibold, theme::TEXT),
                        Pickable::IGNORE,
                    ));
                    t.spawn((
                        theme::label(&fonts, ing.name.clone(), 10.0, Weight::Regular, theme::TEXT_2),
                        Pickable::IGNORE,
                    ));
                },
            );
        })
        .id();
    commands.entity(e).insert((DragGhost { ghost, half }, GlobalZIndex(LIFT)));
}

fn update_drag(
    trigger: On<PointerDrag>,
    mut commands: Commands,
    mut vessel_query: Query<(&mut Node, &DragStartPos), With<VesselCard>>,
    ghosts: Query<&DragGhost>,
    mut ghost_nodes: Query<&mut Node, Without<VesselCard>>,
    swiping: Query<(), With<Swiping>>,
    mut swipes: MessageWriter<TouchScroll>,
    ui_scale: Res<UiScale>,
    zoom: Res<BenchZoom>,
) {
    let s = ui_scale.0.max(0.01);
    let e = trigger.entity;
    if trigger.distance.length() > MOVE_SLOP {
        commands.entity(e).try_insert(DragMoved);
    }
    if swiping.contains(e) {
        swipes.write(TouchScroll { from: e, moved: trigger.delta });
        return;
    }
    if let Ok((mut node, start)) = vessel_query.get_mut(e) {
        // a card moves in the pane's own units: the pointer's travel, unscaled
        let d = trigger.distance / (s * zoom.0.max(0.01));
        node.left = Val::Px((start.left + d.x).max(0.0));
        node.top = Val::Px((start.top + d.y).max(0.0));
        return;
    }
    if let Ok(g) = ghosts.get(e) {
        if let Ok(mut node) = ghost_nodes.get_mut(g.ghost) {
            let at = trigger.pointer.position / s - g.half;
            node.left = Val::Px(at.x);
            node.top = Val::Px(at.y);
        }
    }
}

/// Dropping a shelf tile: into a catalyst slot (replacing what was there) or into the
/// contents of whatever vessel it lands on. The tile itself never moves.
/// Dropping a chip that is already in a vessel: onto another vessel (or the other zone of
/// its own) moves it; onto its own zone it stays put; anywhere else it is taken out.
#[allow(clippy::too_many_arguments)]
fn stop_drag_ingredient(
    mut trigger: On<PointerDragEnd>,
    mut commands: Commands,
    mut tiles: Query<(&mut Outline, &Ingredient)>,
    homes: Query<(Option<&InVessel>, Option<&InCatalystZone>)>,
    moved: Query<(), With<DragMoved>>,
    ghosts: Query<&DragGhost>,
    swiping: Query<(), With<Swiping>>,
    probe: DropProbe,
    catalysts: Query<(Entity, &InCatalystZone)>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    mut active: ResMut<ActiveVessel>,
) {
    trigger.propagate(false);
    let e = trigger.entity;
    if let Ok(g) = ghosts.get(e) {
        commands.entity(g.ghost).despawn();
        commands.entity(e).remove::<DragGhost>();
    }
    // DragEnd comes after the release's Click, so the flag can go now
    let was_moved = moved.contains(e);
    commands.entity(e).remove::<(DragMoved, FingerDown)>();
    // a swipe across the shelf only scrolled it
    if swiping.contains(e) {
        commands.entity(e).remove::<Swiping>();
        return;
    }
    let Ok((mut outline, ing)) = tiles.get_mut(e) else { return };
    outline.color = Color::NONE;
    commands.entity(e).try_remove::<GlobalZIndex>();
    let ing = ing.clone();
    let spot = probe.under(trigger.pointer.id);
    let home = match homes.get(e) {
        Ok((Some(v), _)) => Some(ChipHome::Contents(v.0)),
        Ok((None, Some(c))) => Some(ChipHome::Catalyst(c.0)),
        _ => None,
    };
    let into = spot_vessel(spot);
    match chip_drop(home, spot, was_moved) {
        ChipDrop::Place => {
            if put_in_vessel(&mut commands, spot, &ing, &catalysts, &fonts, &assets) {
                active.0 = into;
            }
        }
        ChipDrop::Move => {
            if put_in_vessel(&mut commands, spot, &ing, &catalysts, &fonts, &assets) {
                commands.entity(e).despawn();
                active.0 = into;
            }
        }
        ChipDrop::Remove => {
            commands.entity(e).despawn();
        }
        ChipDrop::Stay => {}
    }
}

/// Where a dragged chip lives.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ChipHome {
    Contents(Entity),
    Catalyst(Entity),
}

/// What a drop does.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ChipDrop {
    /// a shelf tile: put a copy in
    Place,
    /// a chip onto another vessel or zone: move it there
    Move,
    /// a chip dropped off every card: take it out
    Remove,
    /// a chip dropped back where it was (or never really dragged)
    Stay,
}

/// The rule for drops, pure so it is unit-tested below.
pub fn chip_drop(home: Option<ChipHome>, spot: Option<DropSpot>, moved: bool) -> ChipDrop {
    let Some(home) = home else { return ChipDrop::Place };
    if !moved {
        return ChipDrop::Stay;
    }
    match (home, spot) {
        (_, None) | (_, Some(DropSpot::InputPort { .. })) => ChipDrop::Remove,
        (ChipHome::Contents(v), Some(DropSpot::Ingredients { vessel, .. })) if v == vessel => ChipDrop::Stay,
        (ChipHome::Catalyst(v), Some(DropSpot::Catalyst { vessel, .. })) if v == vessel => ChipDrop::Stay,
        _ => ChipDrop::Move,
    }
}

/// The vessel a drop spot belongs to.
fn spot_vessel(spot: Option<DropSpot>) -> Option<Entity> {
    match spot {
        Some(DropSpot::Catalyst { vessel, .. })
        | Some(DropSpot::Ingredients { vessel, .. })
        | Some(DropSpot::InputPort { vessel, .. }) => Some(vessel),
        None => None,
    }
}

/// Put a substance into the vessel part `spot` names. Shared by drag-and-drop,
/// click-to-place and the double-tap.
fn put_in_vessel(
    commands: &mut Commands,
    spot: Option<DropSpot>,
    ing: &Ingredient,
    catalysts: &Query<(Entity, &InCatalystZone)>,
    fonts: &UiFonts,
    assets: &AssetServer,
) -> bool {
    match spot {
        Some(DropSpot::Catalyst { zone, vessel }) => {
            for (old, in_zone) in catalysts {
                if in_zone.0 == vessel {
                    commands.entity(old).despawn();
                }
            }
            commands.entity(zone).with_children(|z| {
                spawn_vessel_chip(z, ing, ChipRole::Catalyst(vessel), fonts, assets);
            });
            true
        }
        Some(DropSpot::Ingredients { zone, vessel }) => {
            commands.entity(zone).with_children(|z| {
                spawn_vessel_chip(z, ing, ChipRole::Ingredient(vessel), fonts, assets);
            });
            true
        }
        _ => false,
    }
}

fn stop_drag_vessel(
    trigger: On<PointerDragEnd>,
    mut commands: Commands,
    mut vessels: Query<(&mut Node, &mut Outline), With<VesselCard>>,
    mut active: ResMut<ActiveVessel>,
) {
    let e = trigger.entity;
    let Ok((mut node, mut outline)) = vessels.get_mut(e) else { return };
    active.0 = Some(e);
    let snap = |v: Val| if let Val::Px(px) = v { Val::Px((px / 20.0).round() * 20.0) } else { v };
    node.left = snap(node.left);
    node.top = snap(node.top);
    outline.color = Color::NONE;
    commands.entity(e).remove::<(DragStartPos, DragMoved, GlobalZIndex)>();
}

/// Click-to-place: with a substance selected on the shelf, a click on a vessel (not on one
/// of its buttons or ports) puts it in; on the Catalyst Bed's slot it becomes the catalyst.
fn click_card(
    mut trigger: On<PointerClick>,
    mut commands: Commands,
    moved: Query<(), With<DragMoved>>,
    probe: DropProbe,
    selected: Res<SelectedSubstance>,
    progress: Res<PlayerProgress>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    catalysts: Query<(Entity, &InCatalystZone)>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    mut active: ResMut<ActiveVessel>,
) {
    trigger.propagate(false);
    if trigger.button != PointerButton::Primary
        || moved.contains(trigger.entity)
        || moved.contains(trigger.original_event_target())
    {
        return;
    }
    // any tap on a card makes it the one a double-tap fills
    active.0 = Some(trigger.entity);
    let Some(id) = selected.0.filter(|id| progress.discovered.contains(id)) else { return };
    let (spot, on_control) = probe.classify(trigger.original_event_target());
    if on_control {
        return;
    }
    let Some(sub) = substances.get(&game_data.substances).and_then(|s| s.0.get(&id)) else { return };
    let ing = Ingredient {
        id,
        name: sub.name.clone(),
        formula: sub.formula.clone(),
        state: sub.state,
        properties: sub.properties.clone(),
        amount: 1,
    };
    put_in_vessel(&mut commands, spot, &ing, &catalysts, &fonts, &assets);
}

/// A double-tapped shelf tile goes into the active vessel (or the only one on the bench).
#[allow(clippy::too_many_arguments)]
fn add_to_active_system(
    mut asks: MessageReader<AddToActive>,
    mut commands: Commands,
    mut active: ResMut<ActiveVessel>,
    cards: Query<(Entity, &Children), With<VesselCard>>,
    zones: Query<(), With<VesselIngredientZone>>,
    catalysts: Query<(Entity, &InCatalystZone)>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    mut toasts: ResMut<crate::ui::toasts::Toasts>,
) {
    for ask in asks.read() {
        let vessel = active.0.filter(|e| cards.contains(*e)).or_else(|| {
            let mut all = cards.iter().map(|(e, _)| e);
            match (all.next(), all.next()) {
                (Some(only), None) => Some(only),
                _ => None,
            }
        });
        let Some((vessel, children)) = vessel.and_then(|v| cards.get(v).ok()) else {
            toasts.push(
                crate::ui::toasts::ToastKind::Hint,
                if cards.is_empty() {
                    "Put a vessel on the bench first: a double-tap fills the vessel you used last."
                } else {
                    "Tap the vessel you want first: a double-tap fills the vessel you used last."
                },
            );
            continue;
        };
        let Some(zone) = children.iter().find(|c| zones.contains(*c)) else { continue };
        let Some(sub) = substances.get(&game_data.substances).and_then(|s| s.0.get(&ask.0)) else { continue };
        let ing = Ingredient {
            id: sub.id,
            name: sub.name.clone(),
            formula: sub.formula.clone(),
            state: sub.state,
            properties: sub.properties.clone(),
            amount: 1,
        };
        if put_in_vessel(&mut commands, Some(DropSpot::Ingredients { zone, vessel }), &ing, &catalysts, &fonts, &assets)
        {
            active.0 = Some(vessel);
        }
    }
}

/// With more than one vessel on the bench, the active one wears an outline in its colour
/// (a card being dragged keeps the drag's outline). A vessel that is gone stops being active.
fn active_vessel_system(
    mut active: ResMut<ActiveVessel>,
    all: Query<(), With<VesselCard>>,
    mut cards: Query<
        (Entity, &crate::components::ui_markers::ProcessVessel, &mut Outline),
        (With<VesselCard>, Without<DragStartPos>),
    >,
) {
    if active.0.is_some_and(|e| !all.contains(e)) {
        active.0 = None;
    }
    let several = all.iter().count() > 1;
    for (e, pv, mut outline) in &mut cards {
        let want = if several && active.0 == Some(e) {
            Outline {
                width: Val::Px(2.0),
                offset: Val::Px(3.0),
                color: crate::systems::reaction_check::process_color(&pv.process).with_alpha(0.85),
            }
        } else {
            Outline { width: Val::Px(0.0), offset: Val::Px(0.0), color: Color::NONE }
        };
        if outline.color != want.color || outline.width != want.width {
            *outline = want;
        }
    }
}

/// The safety net: once no pointer is pressed, no drag can be in progress, so anything a
/// drag left behind (a floating copy, a lifted card, a half-drawn link) is put away. Also
/// removes any copy whose tile is gone.
fn sweep_drags_system(
    mut commands: Commands,
    pointers: Query<&PointerPressState>,
    ghosts: Query<(Entity, &DragGhostNode)>,
    owners: Query<&DragGhost>,
    mut tiles: Query<(Entity, &mut Outline), (With<DragGhost>, Without<VesselCard>)>,
    mut cards: Query<(Entity, &mut Node, &mut Outline), (With<DragStartPos>, With<VesselCard>)>,
    moved: Query<Entity, With<DragMoved>>,
    mut link: ResMut<LinkDragState>,
) {
    let pressing = pointers.iter().any(|p| p.is_primary_pressed());
    for (g, node) in &ghosts {
        let owned = owners.get(node.owner).is_ok_and(|d| d.ghost == g);
        if !pressing || !owned {
            commands.entity(g).despawn();
        }
    }
    if pressing {
        return;
    }
    for (e, mut outline) in &mut tiles {
        outline.color = Color::NONE;
        commands.entity(e).remove::<(DragGhost, GlobalZIndex)>();
    }
    for (e, mut node, mut outline) in &mut cards {
        let snap = |v: Val| if let Val::Px(px) = v { Val::Px((px / 20.0).round() * 20.0) } else { v };
        node.left = snap(node.left);
        node.top = snap(node.top);
        outline.color = Color::NONE;
        commands.entity(e).remove::<(DragStartPos, GlobalZIndex)>();
    }
    for e in &moved {
        commands.entity(e).remove::<DragMoved>();
    }
    if link.0.is_some() {
        link.0 = None;
    }
}

// ---------------------------------------------------------------------------------------
// Panning the bench
// ---------------------------------------------------------------------------------------
fn start_pan_canvas(
    trigger: On<PointerDragStart>,
    mut commands: Commands,
    panes: Query<&Node, With<CanvasScrollingPane>>,
) {
    if let Ok(node) = panes.get(trigger.entity) {
        let left = if let Val::Px(px) = node.left { px } else { 0.0 };
        let top = if let Val::Px(px) = node.top { px } else { 0.0 };
        commands.entity(trigger.entity).insert(PanStartPos { left, top });
    }
}

fn update_pan_canvas(
    trigger: On<PointerDrag>,
    mut panes: Query<(&mut Node, &PanStartPos), With<CanvasScrollingPane>>,
    bench: Query<&ComputedNode, With<ReactionCanvasRoot>>,
    ui_scale: Res<UiScale>,
    zoom: Res<BenchZoom>,
) {
    let Ok((mut node, start)) = panes.get_mut(trigger.entity) else { return };
    let d = trigger.distance / ui_scale.0.max(0.01);
    pan_bench(&mut node, bench_view(&bench), Vec2::new(start.left, start.top) + d, zoom.0);
}

/// How large the bench draws its vessels and links (1 is full size). At OVERVIEW and below
/// the vessel cards collapse to their overview form (reaction_check::vessel_fit_system).
#[derive(Resource, Debug, Clone, Copy, PartialEq)]
pub struct BenchZoom(pub f32);

impl Default for BenchZoom {
    fn default() -> Self {
        Self(1.0)
    }
}

/// The zoom steps, nearest first.
pub const ZOOMS: [f32; 4] = [1.0, 0.8, 0.6, 0.45];
/// At this zoom and below, cards show their overview form.
pub const OVERVIEW: f32 = 0.6;

impl BenchZoom {
    /// The next step out (or in), staying within ZOOMS.
    pub fn stepped(self, out: bool) -> f32 {
        let i = ZOOMS.iter().position(|z| (z - self.0).abs() < 0.01).unwrap_or(0) as i32;
        let j = (i + if out { 1 } else { -1 }).clamp(0, ZOOMS.len() as i32 - 1);
        ZOOMS[j as usize]
    }

    pub fn overview(self) -> bool {
        self.0 <= OVERVIEW + 0.001
    }
}

/// Applies a zoom change: the pane is scaled about its top-left corner (bevy_ui scales a
/// node about its middle, so it is moved back by what that shifts), and panned so the
/// middle of the bench stays on the same spot.
pub fn bench_zoom_system(
    zoom: Res<BenchZoom>,
    mut last: Local<Option<f32>>,
    mut panes: Query<(&mut Node, &mut UiTransform), With<CanvasScrollingPane>>,
    bench: Query<&ComputedNode, With<ReactionCanvasRoot>>,
) {
    let z = zoom.0;
    if *last == Some(z) {
        return;
    }
    let Ok((mut node, mut tf)) = panes.single_mut() else { return };
    let old = last.unwrap_or(1.0);
    *last = Some(z);
    let size = pane_size(&node);
    tf.scale = Vec2::splat(z);
    tf.translation = Val2::px(-(1.0 - z) * size.x / 2.0, -(1.0 - z) * size.y / 2.0);
    let view = bench_view(&bench);
    let middle = view / 2.0;
    let spot = (middle - pane_offset(&node)) / old;
    pan_bench(&mut node, view, middle - spot * z, z);
}

/// The pane's size, unscaled (UI px).
fn pane_size(pane: &Node) -> Vec2 {
    let w = if let Val::Px(px) = pane.width { px } else { 5000.0 };
    let h = if let Val::Px(px) = pane.height { px } else { 5000.0 };
    Vec2::new(w, h)
}

/// How much of the pane the bench shows, in UI px.
pub fn bench_view(bench: &Query<&ComputedNode, With<ReactionCanvasRoot>>) -> Vec2 {
    bench.iter().next().map(|c| c.size * c.inverse_scale_factor()).unwrap_or(Vec2::new(1000.0, 500.0))
}

/// Move the bench pane so its top-left sits at `at` (UI px), kept within the pane as drawn
/// at `zoom`: never past its top-left corner (0, 0), never so far that its far edges come
/// into view. The drag, the wheel and zooming all pan through here.
pub fn pan_bench(pane: &mut Node, view: Vec2, at: Vec2, zoom: f32) {
    let size = pane_size(pane) * zoom.max(0.01);
    let min = Vec2::new((view.x - size.x).min(0.0), (view.y - size.y).min(0.0));
    let at = at.clamp(min, Vec2::ZERO);
    if pane.left != Val::Px(at.x) {
        pane.left = Val::Px(at.x);
    }
    if pane.top != Val::Px(at.y) {
        pane.top = Val::Px(at.y);
    }
}

/// Where the bench pane's top-left sits (UI px).
pub fn pane_offset(pane: &Node) -> Vec2 {
    let px = |v: Val| if let Val::Px(p) = v { p } else { 0.0 };
    Vec2::new(px(pane.left), px(pane.top))
}

fn stop_pan_canvas(trigger: On<PointerDragEnd>, mut commands: Commands) {
    commands.entity(trigger.entity).remove::<PanStartPos>();
}

// ---------------------------------------------------------------------------------------
// Linking vessels
// ---------------------------------------------------------------------------------------
fn start_draw_link(mut trigger: On<PointerDragStart>, mut state: ResMut<LinkDragState>) {
    trigger.propagate(false); // not a pan, not a card move
    state.0 = Some(trigger.entity);
}

fn stop_draw_link(
    mut trigger: On<PointerDragEnd>,
    mut commands: Commands,
    mut state: ResMut<LinkDragState>,
    probe: DropProbe,
    links: Query<&ReactionLink>,
) {
    trigger.propagate(false);
    let Some(from_port) = state.0.take() else { return };
    let (Some(DropSpot::InputPort { port: to_port, vessel: to_vessel }), (from, _)) =
        (probe.under(trigger.pointer.id), probe.classify(from_port))
    else {
        return;
    };
    // the vessel the output port belongs to
    let from_vessel = match from {
        Some(DropSpot::Ingredients { vessel, .. })
        | Some(DropSpot::Catalyst { vessel, .. })
        | Some(DropSpot::InputPort { vessel, .. }) => vessel,
        None => return,
    };
    if from_vessel == to_vessel {
        info!("A vessel cannot feed itself.");
        return;
    }
    if links.iter().any(|l| l.from_port == from_port && l.to_port == to_port) {
        return; // already linked
    }
    commands.spawn(ReactionLink { from_vessel, from_port, to_vessel, to_port });
    info!("Linked {:?} -> {:?}", from_vessel, to_vessel);
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A small card: card > [header > title, art > image, zone > chip, react button,
    /// ports row > (in port, out port)], plus a catalyst card with a slot.
    struct Bench {
        w: World,
        card: Entity,
        title: Entity,
        art_image: Entity,
        zone: Entity,
        chip: Entity,
        react: Entity,
        in_port: Entity,
        out_port: Entity,
        cat_card: Entity,
        cat_slot: Entity,
        cat_zone: Entity,
        stray: Entity,
    }

    #[derive(Component)]
    struct Kind(Part);

    fn bench() -> Bench {
        let mut w = World::new();
        let card = w.spawn(Kind(Part::Card)).id();
        let header = w.spawn((Kind(Part::Other), ChildOf(card))).id();
        let title = w.spawn((Kind(Part::Other), ChildOf(header))).id();
        let art = w.spawn((Kind(Part::Other), ChildOf(card))).id();
        let art_image = w.spawn((Kind(Part::Other), ChildOf(art))).id();
        let ports = w.spawn((Kind(Part::Other), ChildOf(card))).id();
        let in_port = w.spawn((Kind(Part::InputPort), ChildOf(ports))).id();
        let out_port = w.spawn((Kind(Part::Control), ChildOf(ports))).id();
        let zone = w.spawn((Kind(Part::IngredientZone), ChildOf(card))).id();
        let chip = w.spawn((Kind(Part::Other), ChildOf(zone))).id();
        let react = w.spawn((Kind(Part::Control), ChildOf(card))).id();
        let cat_card = w.spawn(Kind(Part::Card)).id();
        let cat_zone = w.spawn((Kind(Part::IngredientZone), ChildOf(cat_card))).id();
        let cat_slot = w.spawn((Kind(Part::CatalystZone), ChildOf(cat_card))).id();
        let stray = w.spawn(Kind(Part::Other)).id();
        Bench { w, card, title, art_image, zone, chip, react, in_port, out_port, cat_card, cat_slot, cat_zone, stray }
    }

    fn classify(b: &Bench, e: Entity) -> (Option<DropSpot>, bool) {
        classify_chain(
            e,
            |x| b.w.get::<ChildOf>(x).map(|c| c.parent()),
            |x| b.w.get::<Kind>(x).map(|k| k.0).unwrap_or(Part::Other),
            |card| {
                b.w.get::<Children>(card)
                    .and_then(|c| c.iter().find(|ch| b.w.get::<Kind>(*ch).map(|k| k.0) == Some(Part::IngredientZone)))
            },
        )
    }

    #[test]
    fn anywhere_on_a_card_means_its_contents() {
        let b = bench();
        let want = Some(DropSpot::Ingredients { zone: b.zone, vessel: b.card });
        for e in [b.card, b.title, b.art_image, b.zone, b.chip, b.react] {
            assert_eq!(classify(&b, e).0, want, "dropping on {e:?}");
        }
    }

    #[test]
    fn the_catalyst_slot_wins_over_the_contents() {
        let b = bench();
        assert_eq!(classify(&b, b.cat_slot).0, Some(DropSpot::Catalyst { zone: b.cat_slot, vessel: b.cat_card }));
        assert_eq!(classify(&b, b.cat_zone).0, Some(DropSpot::Ingredients { zone: b.cat_zone, vessel: b.cat_card }));
    }

    #[test]
    fn input_ports_are_link_targets() {
        let b = bench();
        assert_eq!(classify(&b, b.in_port).0, Some(DropSpot::InputPort { port: b.in_port, vessel: b.card }));
    }

    #[test]
    fn buttons_and_output_ports_are_controls() {
        let b = bench();
        assert!(classify(&b, b.react).1);
        assert!(classify(&b, b.out_port).1);
        assert!(!classify(&b, b.art_image).1);
        assert!(!classify(&b, b.chip).1);
    }

    #[test]
    fn chips_move_between_vessels_and_come_out_off_the_cards() {
        let b = bench();
        let home = Some(ChipHome::Contents(b.card));
        let own = Some(DropSpot::Ingredients { zone: b.zone, vessel: b.card });
        let other = Some(DropSpot::Ingredients { zone: b.cat_zone, vessel: b.cat_card });
        let slot = Some(DropSpot::Catalyst { zone: b.cat_slot, vessel: b.cat_card });
        assert_eq!(chip_drop(home, own, true), ChipDrop::Stay);
        assert_eq!(chip_drop(home, other, true), ChipDrop::Move);
        assert_eq!(chip_drop(home, slot, true), ChipDrop::Move);
        assert_eq!(chip_drop(home, None, true), ChipDrop::Remove);
        assert_eq!(chip_drop(home, None, false), ChipDrop::Stay, "a click is not a drag");
        assert_eq!(chip_drop(None, None, true), ChipDrop::Place, "shelf tiles are copies");
        let cat_home = Some(ChipHome::Catalyst(b.cat_card));
        assert_eq!(chip_drop(cat_home, slot, true), ChipDrop::Stay);
        assert_eq!(chip_drop(cat_home, other, true), ChipDrop::Move);
    }

    #[test]
    fn off_the_cards_is_nowhere() {
        let b = bench();
        assert_eq!(classify(&b, b.stray), (None, false));
    }
}
