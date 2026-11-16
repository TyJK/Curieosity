// src/ui/onboarding.rs
//
// Helping a player along without getting in the way:
//   * tooltips on shelf tiles, the vessel buttons and the parts of a vessel, after a short
//     hover (off in Settings)
//   * the first-steps tour: four coach marks through the first loop (place a vessel, drag
//     a substance in, press React, see the discovery). Skippable; Settings can replay it.
//   * the next-step card on the bench: the first step of the tech tree that can be made now
//   * the era banner when the player reaches a new age
//
// Everything here reads the game; nothing else depends on it except Settings (its
// switches) and the review run's checks.
use bevy::ecs::system::SystemParam;
use bevy::picking::hover::HoverMap;
use bevy::picking::pointer::{PointerId, PointerLocation, PointerPress};
use bevy::prelude::*;
use bevy::window::PrimaryWindow;

use crate::components::{InVessel, Ingredient, ProcessVessel, VesselCard, VesselReactButton};
use crate::data::common::ProcessType;
use crate::data::reactions::Reaction;
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::autoplay::GameEvent;
use crate::ui::codex::CodexState;
use crate::ui::inventory::{InventoryScroll, ShelfTile};
use crate::ui::process_toolbar::{roman, vessel_name, ProcessButton, ProcessUnlocks};
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::settings::{Settings, SettingsUi};
use crate::ui::tech_tree::{node_state, NodeState, TechTreeState};
use crate::ui::theme::{self, Kind, Weight};
use crate::GameData;

pub struct OnboardingPlugin;

impl Plugin for OnboardingPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<TooltipState>().init_resource::<Coach>().init_resource::<CurrentEra>().add_systems(
            Update,
            (
                spawn_onboarding_ui,
                tooltip_system,
                coach_input_system,
                coach_system,
                next_step_system,
                next_step_input_system,
                era_banner_system,
                fade_system,
            )
                .chain(),
        );
    }
}

// ---------------------------------------------------------------------------------------
// Tooltips
// ---------------------------------------------------------------------------------------
/// What the tooltip over an entity says. Put it on the hovered node or any ancestor.
#[derive(Component, Clone, Debug)]
pub enum Tip {
    /// a fixed title and body
    Text(&'static str, &'static str),
    /// a substance, described from the library
    Substance(u32),
    /// a vessel button: what it runs, or what unlocks it
    Vessel(ProcessType),
}

#[derive(Resource, Default)]
pub struct TooltipState {
    /// the entity with the Tip under the pointer
    pub target: Option<Entity>,
    pub since: f64,
    /// the target whose text is showing, if the tooltip is up
    pub shown: Option<Entity>,
}

#[derive(Component)]
pub struct TooltipNode;
#[derive(Component)]
pub struct TooltipTitle;
#[derive(Component)]
pub struct TooltipBody;

/// Hover this long before a tooltip appears.
pub const TIP_DELAY: f64 = 0.45;
const TIP_W: f32 = 270.0;

/// The pointer a tooltip follows: the review run's virtual pointer while it has something
/// under it, otherwise the mouse.
fn tip_pointer(hover: &HoverMap) -> PointerId {
    hover
        .iter()
        .find(|(id, hits)| matches!(id, PointerId::Custom(_)) && !hits.is_empty())
        .map(|(id, _)| *id)
        .unwrap_or(PointerId::Mouse)
}

/// The topmost entity under a pointer that carries a Tip (or has an ancestor that does).
pub fn tip_under(
    hover: &HoverMap,
    pointer: PointerId,
    parents: &Query<&ChildOf>,
    tips: &Query<&Tip>,
) -> Option<Entity> {
    let hits = hover.get(&pointer)?;
    let mut hits: Vec<(Entity, f32)> = hits.iter().map(|(e, h)| (*e, h.depth)).collect();
    hits.sort_by(|a, b| a.1.total_cmp(&b.1));
    for (mut e, _) in hits {
        for _ in 0..12 {
            if tips.contains(e) {
                return Some(e);
            }
            match parents.get(e) {
                Ok(p) => e = p.parent(),
                Err(_) => break,
            }
        }
    }
    None
}

fn first_sentence(text: &str, max: usize) -> String {
    let cut = text.find(". ").map(|i| i + 1).unwrap_or(text.len());
    let s: String = text[..cut].chars().take(max).collect();
    if s.chars().count() < text[..cut].chars().count() {
        format!("{}…", s.trim_end())
    } else {
        s
    }
}

/// Title and body for a tip.
pub fn tip_text(
    tip: &Tip,
    db: Option<&RecipeDatabase>,
    subs: Option<&Substances>,
    unlocks: &ProcessUnlocks,
) -> (String, String) {
    match tip {
        Tip::Text(t, b) => (t.to_string(), b.to_string()),
        Tip::Substance(id) => {
            let Some(s) = subs.and_then(|s| s.0.get(id)) else { return (format!("#{id}"), String::new()) };
            let mut body = format!("{}  ·  {:?}", crate::components::format_formula(&s.formula), s.state);
            if let Some(d) = s.description.as_deref() {
                body.push('\n');
                body.push_str(&first_sentence(d, 150));
            }
            body.push_str("\nDrag it onto a vessel, or click to select it.");
            (s.name.clone(), body)
        }
        Tip::Vessel(p) => {
            let title = format!("{}  ·  {} {}", vessel_name(p), p.family(), roman(p.tier()));
            let homed = db.map(|db| db.authored.iter().filter(|r| &r.process == p).count()).unwrap_or(0);
            let mut body = if unlocks.0.contains(p) {
                "Click to put one on your bench.".to_string()
            } else {
                let by = db
                    .and_then(|db| db.milestones.iter().find(|m| m.unlock.contains(p)))
                    .and_then(|m| subs.and_then(|s| s.0.get(&m.on)).map(|s| s.name.clone()));
                match by {
                    Some(n) => format!("Locked: discover {n} to unlock it."),
                    None => "Locked.".to_string(),
                }
            };
            if p.tier() > 1 {
                body.push_str(&format!("\nAlso runs the lower-tier {} recipes.", p.family()));
            }
            if p.has_catalyst_slot() {
                body.push_str("\nHas a catalyst slot: the catalyst is never used up.");
            }
            body.push_str(&format!("\n{homed} recipes call for it."));
            (title, body)
        }
    }
}

#[allow(clippy::too_many_arguments)]
pub fn tooltip_system(
    time: Res<Time<Real>>,
    hover: Res<HoverMap>,
    pointers: Query<(&PointerId, &PointerLocation, &PointerPress)>,
    parents: Query<&ChildOf>,
    tips: Query<&Tip>,
    settings: Option<Res<Settings>>,
    db: Option<Res<RecipeDatabase>>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    unlocks: Res<ProcessUnlocks>,
    screen: (Res<UiScale>, Query<&Window, With<PrimaryWindow>>),
    mut state: ResMut<TooltipState>,
    coach: Res<Coach>,
    mut node_q: Query<(&mut Node, &mut Visibility), With<TooltipNode>>,
    mut title_q: Query<&mut Text, (With<TooltipTitle>, Without<TooltipBody>)>,
    mut body_q: Query<&mut Text, (With<TooltipBody>, Without<TooltipTitle>)>,
) {
    let Ok((mut node, mut vis)) = node_q.single_mut() else { return };
    let now = time.elapsed_secs_f64();
    // the tour does the explaining while it runs
    let enabled = settings.as_ref().is_none_or(|s| s.tooltips) && coach.step == CoachStep::Off;
    let pressing = pointers.iter().any(|(_, _, p)| p.is_primary_pressed());
    let pointer = tip_pointer(&hover);
    let target = if enabled && !pressing { tip_under(&hover, pointer, &parents, &tips) } else { None };
    if target != state.target {
        state.target = target;
        state.since = now;
    }
    let show = target.is_some() && now - state.since >= TIP_DELAY;
    if !show {
        state.shown = None;
        if *vis != Visibility::Hidden {
            *vis = Visibility::Hidden;
        }
        return;
    }
    let target = target.unwrap();
    if state.shown != Some(target) {
        let Ok(tip) = tips.get(target) else { return };
        let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
        let (t, b) = tip_text(tip, db.as_deref(), subs, &unlocks);
        if let Ok(mut tt) = title_q.single_mut() {
            tt.0 = t;
        }
        if let Ok(mut bt) = body_q.single_mut() {
            bt.0 = b;
        }
        state.shown = Some(target);
    }
    // follow the pointer, kept on screen
    let (ui_scale, windows) = screen;
    let s = ui_scale.0.max(0.01);
    let at = pointers
        .iter()
        .find(|(id, _, _)| **id == pointer)
        .and_then(|(_, loc, _)| loc.location().map(|l| l.position))
        .unwrap_or_default()
        / s;
    let (w, h) = windows.single().map(|w| (w.width() / s, w.height() / s)).unwrap_or((1280.0, 720.0));
    let mut x = at.x + 16.0;
    let mut y = at.y + 20.0;
    if x + TIP_W > w - 8.0 {
        x = (at.x - TIP_W - 12.0).max(8.0);
    }
    if y + 120.0 > h {
        y = (at.y - 130.0).max(8.0);
    }
    node.left = Val::Px(x);
    node.top = Val::Px(y);
    if *vis != Visibility::Inherited {
        *vis = Visibility::Inherited;
    }
}

// ---------------------------------------------------------------------------------------
// The first-steps tour
// ---------------------------------------------------------------------------------------
#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum CoachStep {
    #[default]
    Off,
    Place,
    DragIn,
    React,
    Discovery,
}

#[derive(Resource, Default)]
pub struct Coach {
    pub step: CoachStep,
    /// whether this game has decided to run the tour (once the save has loaded)
    pub decided: bool,
    pub since: f64,
    /// what the first reaction made, for the last coach mark
    pub made: Vec<u32>,
}

impl Coach {
    /// Start the tour from the first step (Settings: "Show the first-steps tour again").
    pub fn restart(&mut self, now: f64) {
        self.step = CoachStep::Place;
        self.decided = true;
        self.since = now;
        self.made.clear();
    }
}

#[derive(Component)]
pub struct CoachBubble;
#[derive(Component)]
pub struct CoachTitle;
#[derive(Component)]
pub struct CoachText;
#[derive(Component)]
pub struct CoachRing;
#[derive(Component)]
pub struct CoachSkip;
#[derive(Component)]
pub struct CoachNext;
/// The Settings button that replays the tour.
#[derive(Component, Default)]
pub struct TourAgainButton;

/// The last coach mark stays this long unless dismissed.
const DISCOVERY_HOLD: f64 = 15.0;

pub fn coach_input_system(
    time: Res<Time<Real>>,
    mut coach: ResMut<Coach>,
    mut settings: Option<ResMut<Settings>>,
    mut settings_ui: ResMut<SettingsUi>,
    buttons: Query<
        (&Interaction, Option<&CoachSkip>, Option<&CoachNext>, Option<&TourAgainButton>),
        Changed<Interaction>,
    >,
) {
    for (i, skip, next, again) in &buttons {
        if *i != Interaction::Pressed {
            continue;
        }
        if skip.is_some() || next.is_some() {
            coach.step = CoachStep::Off;
            if let Some(s) = settings.as_mut() {
                if !s.tour_done {
                    s.tour_done = true;
                }
            }
        }
        if again.is_some() {
            coach.restart(time.elapsed_secs_f64());
            settings_ui.open = false;
            if let Some(s) = settings.as_mut() {
                s.tour_done = false;
            }
        }
    }
}

/// What the coach marks can point at.
#[derive(SystemParam)]
pub struct CoachTargets<'w, 's> {
    buttons: Query<'w, 's, (Entity, &'static ProcessButton)>,
    tiles: Query<'w, 's, (Entity, &'static Ingredient), With<ShelfTile>>,
    chips: Query<'w, 's, &'static InVessel, With<Ingredient>>,
    reacts: Query<'w, 's, (Entity, &'static ChildOf), With<VesselReactButton>>,
    cards: Query<'w, 's, (Entity, &'static ProcessVessel), With<VesselCard>>,
    next_card: Query<'w, 's, (Entity, &'static Node), With<NextStepCard>>,
    shelf: Query<'w, 's, Entity, With<InventoryScroll>>,
    rects: Query<'w, 's, (&'static ComputedNode, &'static UiGlobalTransform)>,
}

impl CoachTargets<'_, '_> {
    /// The next-step card, if it is showing.
    fn card(&self) -> Option<Entity> {
        self.next_card.iter().find(|(_, n)| n.display != Display::None).map(|(e, _)| e)
    }

    /// The node a coach mark points at, if there is one.
    fn target(&self, step: CoachStep, db: &RecipeDatabase, made: &[u32]) -> Option<Entity> {
        match step {
            CoachStep::Off => None,
            CoachStep::Place => self.buttons.iter().find(|(_, b)| b.process == ProcessType::Heat).map(|(e, _)| e),
            CoachStep::DragIn => {
                let first = *db.start.first()?;
                self.tiles.iter().find(|(_, i)| i.id == first).map(|(e, _)| e).or_else(|| self.shelf.iter().next())
            }
            CoachStep::React => {
                let vessel =
                    self.chips.iter().next().map(|c| c.0).or_else(|| self.cards.iter().next().map(|(e, _)| e))?;
                self.reacts.iter().find(|(_, p)| p.parent() == vessel).map(|(e, _)| e)
            }
            CoachStep::Discovery => self
                .card()
                .or_else(|| made.first().and_then(|id| self.tiles.iter().find(|(_, i)| i.id == *id).map(|(e, _)| e)))
                .or_else(|| self.shelf.iter().next()),
        }
    }

    /// A node's rectangle in UI pixels (top-left, size).
    fn rect(&self, e: Entity) -> Option<(Vec2, Vec2)> {
        let (c, g) = self.rects.get(e).ok()?;
        let k = c.inverse_scale_factor();
        let size = c.size * k;
        let center = g.translation * k;
        (size.x > 0.0).then_some((center - size * 0.5, size))
    }
}

/// The coach mark's own nodes.
#[derive(SystemParam)]
pub struct CoachNodes<'w, 's> {
    bubble: Query<
        'w,
        's,
        (&'static mut Node, &'static mut Visibility),
        (With<CoachBubble>, Without<CoachRing>, Without<NextStepCard>, Without<CoachNext>),
    >,
    ring: Query<
        'w,
        's,
        (&'static mut Node, &'static mut Visibility, &'static mut BorderColor),
        (With<CoachRing>, Without<CoachBubble>, Without<NextStepCard>, Without<CoachNext>),
    >,
    title: Query<'w, 's, &'static mut Text, (With<CoachTitle>, Without<CoachText>)>,
    text: Query<'w, 's, &'static mut Text, (With<CoachText>, Without<CoachTitle>)>,
    next_btn: Query<
        'w,
        's,
        &'static mut Node,
        (With<CoachNext>, Without<CoachBubble>, Without<CoachRing>, Without<NextStepCard>),
    >,
}

#[allow(clippy::too_many_arguments)]
pub fn coach_system(
    time: Res<Time<Real>>,
    mut coach: ResMut<Coach>,
    mut settings: Option<ResMut<Settings>>,
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    names: (Option<Res<GameData>>, Res<Assets<Substances>>),
    mut events: MessageReader<GameEvent>,
    views: (Res<CodexState>, Res<ReactionLibState>, Res<TechTreeState>, Res<SettingsUi>),
    targets: CoachTargets,
    mut nodes: CoachNodes,
    ui_scale: Res<UiScale>,
    windows: Query<&Window, With<PrimaryWindow>>,
) {
    let now = time.elapsed_secs_f64();
    let Some(db) = db else { return };
    let reacted: Vec<u32> = events
        .read()
        .filter_map(|e| match e {
            GameEvent::Reacted { reaction_id, .. } => Some(*reaction_id),
            _ => None,
        })
        .collect();

    // Decide once the save has loaded: a new game gets the tour, a game in progress doesn't.
    if !coach.decided && progress.ready {
        coach.decided = true;
        let done = settings.as_ref().is_some_and(|s| s.tour_done);
        if !done && progress.discovered.len() <= db.start.len() {
            coach.restart(now);
        } else if !done {
            if let Some(s) = settings.as_mut() {
                s.tour_done = true;
            }
        }
    }

    // Advance through the first loop.
    let before = coach.step;
    match coach.step {
        CoachStep::Off => {}
        CoachStep::Place if !targets.cards.is_empty() => coach.step = CoachStep::DragIn,
        CoachStep::DragIn if !targets.chips.is_empty() => coach.step = CoachStep::React,
        CoachStep::React if !reacted.is_empty() => {
            let r = reacted[0];
            // what was new (water from the starting kit is no discovery)
            coach.made = db
                .authored
                .iter()
                .find(|x| x.id == r)
                .map(|x| x.products.iter().map(|p| p.substance_id).filter(|id| !db.start.contains(id)).collect())
                .unwrap_or_default();
            coach.step = CoachStep::Discovery;
        }
        CoachStep::Discovery if now - coach.since > DISCOVERY_HOLD => coach.step = CoachStep::Off,
        _ => {}
    }
    if coach.step != before {
        coach.since = now;
        if coach.step == CoachStep::Off {
            if let Some(s) = settings.as_mut() {
                s.tour_done = true;
            }
        }
    }

    // Draw it: hidden away from the lab, and while a step's target is off screen.
    let (codex, rlib, tree, sui) = views;
    let in_lab = !(codex.open || rlib.open || tree.open || sui.open);
    let target = if in_lab { targets.target(coach.step, &db, &coach.made) } else { None };
    let rect = target.and_then(|t| targets.rect(t));
    let CoachNodes { bubble, ring, title: title_q, text: text_q, next_btn } = &mut nodes;
    let (Ok((mut bn, mut bv)), Ok((mut rn, mut rv, mut rb))) = (bubble.single_mut(), ring.single_mut()) else { return };
    let Some((min, size)) = rect else {
        if *bv != Visibility::Hidden {
            *bv = Visibility::Hidden;
            *rv = Visibility::Hidden;
        }
        return;
    };
    let (game_data, substances) = names;
    let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
    let name = |id: u32| subs.and_then(|s| s.0.get(&id)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    let (title, text) = match coach.step {
        CoachStep::Place => ("First steps  ·  1 of 4", "Click the Fire to put it on your bench.".to_string()),
        CoachStep::DragIn => (
            "First steps  ·  2 of 4",
            format!("Drag {} from the shelf onto the Fire.", db.start.first().map(|id| name(*id)).unwrap_or_default()),
        ),
        CoachStep::React => ("First steps  ·  3 of 4", "Press React and see what you get.".to_string()),
        CoachStep::Discovery => (
            "First steps  ·  4 of 4",
            format!(
                "New on your shelf: {}. Every discovery opens up more recipes. {}",
                if coach.made.is_empty() {
                    "your first product".to_string()
                } else {
                    coach.made.iter().map(|id| name(*id)).collect::<Vec<_>>().join(", ")
                },
                if targets.card().is_some() {
                    "This card always suggests one you can make now; the Tech Tree shows the whole map."
                } else {
                    "The Tech Tree shows what you can make next."
                }
            ),
        ),
        CoachStep::Off => ("", String::new()),
    };
    if let Ok(mut t) = title_q.single_mut() {
        if t.0 != title {
            t.0 = title.to_string();
        }
    }
    if let Ok(mut t) = text_q.single_mut() {
        if t.0 != text {
            t.0 = text;
        }
    }
    if let Ok(mut n) = next_btn.single_mut() {
        let d = if coach.step == CoachStep::Discovery { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    // the ring hugs the target and pulses
    let pad = 5.0;
    rn.left = Val::Px(min.x - pad);
    rn.top = Val::Px(min.y - pad);
    rn.width = Val::Px(size.x + pad * 2.0);
    rn.height = Val::Px(size.y + pad * 2.0);
    let pulse = 0.55 + 0.45 * ((now * 4.0).sin() as f32).abs();
    *rb = BorderColor::all(theme::CYAN.with_alpha(pulse));
    // the bubble sits beside the target, on the first side with room for it
    let s = ui_scale.0.max(0.01);
    let (w, h) = windows.single().map(|w| (w.width() / s, w.height() / s)).unwrap_or((1280.0, 720.0));
    let (x, y) = bubble_spot(min, size, Vec2::new(w, h));
    bn.left = Val::Px(x);
    bn.top = Val::Px(y);
    if *bv != Visibility::Inherited {
        *bv = Visibility::Inherited;
        *rv = Visibility::Inherited;
    }
}

/// The bubble's size (its text wraps inside this width; the height allows four lines).
const BUBBLE: Vec2 = Vec2::new(300.0, 150.0);

/// Where the bubble goes for a target at `min` of `size` on a `screen`: right of it, left of
/// it, above, then below, whichever fits first; failing all, as near the right as fits.
pub fn bubble_spot(min: Vec2, size: Vec2, screen: Vec2) -> (f32, f32) {
    let gap = 16.0;
    let top_edge = theme::HEADER_H + 4.0;
    let clamp_y = |y: f32| y.clamp(top_edge, (screen.y - BUBBLE.y - 8.0).max(top_edge));
    let clamp_x = |x: f32| x.clamp(8.0, (screen.x - BUBBLE.x - 8.0).max(8.0));
    let right = min.x + size.x + gap;
    if right + BUBBLE.x <= screen.x - 8.0 {
        return (right, clamp_y(min.y));
    }
    let left = min.x - gap - BUBBLE.x;
    if left >= 8.0 {
        return (left, clamp_y(min.y));
    }
    let above = min.y - gap - BUBBLE.y;
    if above >= top_edge {
        return (clamp_x(min.x), above);
    }
    let below = min.y + size.y + gap;
    if below + BUBBLE.y <= screen.y - 8.0 {
        return (clamp_x(min.x), below);
    }
    (clamp_x(right), clamp_y(min.y))
}

// ---------------------------------------------------------------------------------------
// The next-step card
// ---------------------------------------------------------------------------------------
#[derive(Component)]
pub struct NextStepCard;
#[derive(Component)]
pub struct NextStepTitle;
#[derive(Component)]
pub struct NextStepBody;
/// The reaction the card is showing (it opens that step in the tech tree).
#[derive(Component)]
pub struct NextStepShow(pub Option<u32>);

/// The suggestion: the first step of the tech tree that can be made right now, preferring
/// the eras over the side laboratory.
pub fn next_step<'a>(
    db: &'a RecipeDatabase,
    progress: &PlayerProgress,
    unlocks: &ProcessUnlocks,
) -> Option<&'a Reaction> {
    let side = db.side_epoch();
    let ready = |r: &&Reaction| node_state(r, progress, unlocks) == NodeState::Available;
    db.authored.iter().filter(|r| r.epoch != side).find(ready).or_else(|| db.authored.iter().find(ready))
}

#[allow(clippy::too_many_arguments, clippy::type_complexity)]
pub fn next_step_system(
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    settings: Option<Res<Settings>>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    views: (Res<CodexState>, Res<ReactionLibState>, Res<TechTreeState>),
    mut card: Query<(&mut Node, &mut NextStepShow, &ComputedNode), With<NextStepCard>>,
    mut toast_stack: Query<&mut Node, (With<crate::ui::toasts::ToastStack>, Without<NextStepCard>)>,
    mut title_q: Query<&mut Text, (With<NextStepTitle>, Without<NextStepBody>)>,
    mut body_q: Query<&mut Text, (With<NextStepBody>, Without<NextStepTitle>)>,
    mut last: Local<Option<(u32, bool)>>,
    room: (Res<crate::ui::inventory::Dock>, ResMut<crate::ui::toasts::ToastRoom>),
) {
    let Some(db) = db else { return };
    let Ok((mut node, mut show, computed)) = card.single_mut() else { return };
    let (dock, mut toast_room) = room;
    let card_bottom = Val::Px(dock.h + 12.0);
    if node.bottom != card_bottom {
        node.bottom = card_bottom;
    }
    let (codex, rlib, tree) = views;
    let wanted =
        settings.as_ref().is_none_or(|s| s.next_step) && progress.ready && !(codex.open || rlib.open || tree.open);
    let step = if wanted { next_step(&db, &progress, &unlocks) } else { None };
    let d = if step.is_some() { Display::Flex } else { Display::None };
    if node.display != d {
        node.display = d;
    }
    // the pop-ups rise above the card while it shows
    let lift = if step.is_some() {
        let h = computed.size.y * computed.inverse_scale_factor();
        if h > 0.0 {
            h + 10.0
        } else {
            84.0
        }
    } else {
        0.0
    };
    if let Ok(mut t) = toast_stack.single_mut() {
        let want = Val::Px(dock.h + 14.0 + lift);
        if t.bottom != want {
            t.bottom = want;
        }
    }
    // each pop-up takes about 50 px: as many as fit between the card and the header
    let fit = (((dock.bench - lift - 14.0) / 50.0).floor().max(1.0) as usize).min(4);
    if toast_room.0 != fit {
        toast_room.0 = fit;
    }
    let Some(r) = step else {
        *last = None;
        return;
    };
    show.0 = Some(r.id);
    let key = (r.id, progress.is_changed() || unlocks.is_changed());
    if last.is_some_and(|(id, _)| id == r.id) && !key.1 {
        return;
    }
    *last = Some(key);
    let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
    let name = |id: u32| subs.and_then(|s| s.0.get(&id)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    let inputs: Vec<String> = r.reactants.iter().map(|s| name(s.substance_id)).collect();
    let mut body = format!("{} in the {}", inputs.join(" + "), vessel_name(&r.process));
    if let Some(c) = r.required_catalyst() {
        body.push_str(&format!("\ncatalyst: {}", name(c)));
    }
    if let Ok(mut t) = title_q.single_mut() {
        t.0 = r.name.clone();
    }
    if let Ok(mut t) = body_q.single_mut() {
        t.0 = body;
    }
}

/// "Show in the tree" on the card opens the tech tree on that step.
pub fn next_step_input_system(
    mut buttons: Query<(&Interaction, &NextStepShow, &mut BackgroundColor, &mut BorderColor), Changed<Interaction>>,
    mut tree: ResMut<TechTreeState>,
) {
    for (i, show, mut bg, mut border) in &mut buttons {
        // the same hover response as every other button: lifted fill, brighter edge
        let (b, l) = next_step_look(*i != Interaction::None);
        bg.0 = b;
        *border = BorderColor::all(l);
        if *i == Interaction::Pressed {
            if let Some(id) = show.0 {
                tree.open = true;
                tree.selected = Some(id);
            }
        }
    }
}

/// The next-step card's fill and edge, resting or hovered.
pub fn next_step_look(hovered: bool) -> (Color, Color) {
    if hovered {
        (theme::mix(theme::SURFACE, theme::GOLD, 0.16).with_alpha(0.98), theme::GOLD)
    } else {
        (theme::mix(theme::SURFACE, theme::GOLD, 0.08).with_alpha(0.96), theme::GOLD.with_alpha(0.7))
    }
}

// ---------------------------------------------------------------------------------------
// The era banner
// ---------------------------------------------------------------------------------------
/// The era the header shows (set by shell::header_stats_system).
#[derive(Resource, Default)]
pub struct CurrentEra {
    pub index: u8,
}

#[derive(Component)]
pub struct EraBanner;

/// Fades a node (and the text under it) in, holds, and fades it out, then despawns it.
#[derive(Component)]
pub struct Fade {
    pub age: f32,
    pub hold: f32,
}

/// A text colour that fades with its banner.
#[derive(Component)]
pub struct FadeText(pub Color);

/// The banner's panel: its fill fades with it.
#[derive(Component)]
pub struct FadeBox(pub Color);

const FADE_IN: f32 = 0.35;
const FADE_OUT: f32 = 0.8;
pub const BANNER_HOLD: f32 = 3.6;

#[allow(clippy::too_many_arguments)]
pub fn era_banner_system(
    mut commands: Commands,
    era: Res<CurrentEra>,
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    fonts: Option<Res<UiFonts>>,
    banners: Query<Entity, With<EraBanner>>,
    mut events: MessageWriter<GameEvent>,
    mut last: Local<Option<u8>>,
) {
    let (Some(db), Some(fonts)) = (db, fonts) else { return };
    if !progress.ready {
        return;
    }
    let Some(prev) = *last else {
        *last = Some(era.index); // the loaded game's era: no banner
        return;
    };
    if era.index == prev {
        return;
    }
    *last = Some(era.index);
    if era.index < prev {
        return; // a new game
    }
    let Some(ep) = db.epochs.get(era.index as usize) else { return };
    for b in &banners {
        commands.entity(b).despawn();
    }
    events.write(GameEvent::Era { index: era.index });
    commands
        .spawn((
            EraBanner,
            Fade { age: 0.0, hold: BANNER_HOLD },
            GlobalZIndex(900),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(theme::SIDEBAR_W),
                top: Val::Px(theme::HEADER_H + 48.0),
                justify_content: JustifyContent::Center,
                ..default()
            },
            Pickable::IGNORE,
            Name::new("EraBanner"),
        ))
        .with_children(|root| {
            root.spawn((
                Node {
                    flex_direction: FlexDirection::Column,
                    align_items: AlignItems::Center,
                    row_gap: Val::Px(4.0),
                    padding: UiRect::axes(Val::Px(34.0), Val::Px(16.0)),
                    border: UiRect::all(Val::Px(1.5)),
                    ..default()
                },
                BorderRadius::all(Val::Px(theme::R_LG)),
                BackgroundColor(theme::mix(theme::SURFACE, theme::GOLD, 0.10).with_alpha(0.0)),
                BorderColor::all(theme::GOLD.with_alpha(0.0)),
                FadeBox(theme::mix(theme::SURFACE, theme::GOLD, 0.10)),
                theme::glow(theme::GOLD.with_alpha(0.25), 30.0),
                Pickable::IGNORE,
            ))
            .with_children(|b| {
                let t = |b: &mut ChildSpawnerCommands, text: String, size: f32, w: Weight, c: Color| {
                    b.spawn((theme::label(&fonts, text, size, w, c.with_alpha(0.0)), FadeText(c), Pickable::IGNORE));
                };
                t(b, format!("A NEW ERA  ·  {}", ep.era.to_uppercase()), theme::XS, Weight::Bold, theme::GOLD);
                t(b, ep.name.clone(), theme::XXL, Weight::Bold, theme::TEXT);
                if !ep.blurb.is_empty() {
                    t(b, ep.blurb.clone(), theme::SM, Weight::Regular, theme::TEXT_2);
                }
            });
        });
}

pub fn fade_system(
    mut commands: Commands,
    time: Res<Time<Real>>,
    mut roots: Query<(Entity, &mut Fade, &Children)>,
    children: Query<&Children>,
    mut boxes: Query<(&FadeBox, &mut BackgroundColor, &mut BorderColor)>,
    mut texts: Query<(&FadeText, &mut TextColor)>,
) {
    for (e, mut f, kids) in &mut roots {
        f.age += time.delta_secs();
        let a = if f.age < FADE_IN {
            f.age / FADE_IN
        } else if f.age < FADE_IN + f.hold {
            1.0
        } else {
            1.0 - (f.age - FADE_IN - f.hold) / FADE_OUT
        };
        if a <= 0.0 {
            commands.entity(e).despawn();
            continue;
        }
        let mut stack: Vec<Entity> = kids.iter().collect();
        while let Some(c) = stack.pop() {
            if let Ok((fb, mut bg, mut border)) = boxes.get_mut(c) {
                bg.0 = fb.0.with_alpha(0.96 * a);
                *border = BorderColor::all(theme::GOLD.with_alpha(a));
            }
            if let Ok((ft, mut tc)) = texts.get_mut(c) {
                tc.0 = ft.0.with_alpha(ft.0.alpha() * a);
            }
            if let Ok(more) = children.get(c) {
                stack.extend(more.iter());
            }
        }
    }
}

// ---------------------------------------------------------------------------------------
// The nodes (spawned once the fonts are in)
// ---------------------------------------------------------------------------------------
pub fn spawn_onboarding_ui(
    mut commands: Commands,
    fonts: Option<Res<UiFonts>>,
    assets: Res<AssetServer>,
    mut done: Local<bool>,
) {
    let Some(fonts) = fonts else { return };
    if *done {
        return;
    }
    *done = true;
    let fonts = &*fonts;
    // the tooltip
    commands
        .spawn((
            TooltipNode,
            GlobalZIndex(2000),
            Visibility::Hidden,
            Node {
                position_type: PositionType::Absolute,
                width: Val::Px(TIP_W),
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(3.0),
                padding: UiRect::axes(Val::Px(11.0), Val::Px(8.0)),
                border: UiRect::all(Val::Px(1.0)),
                ..default()
            },
            BorderRadius::all(Val::Px(theme::R_MD)),
            BackgroundColor(theme::RAISED.with_alpha(0.98)),
            BorderColor::all(theme::LINE_STRONG),
            theme::shadow(18.0, 6.0, 0.6),
            Pickable::IGNORE,
            Name::new("Tooltip"),
        ))
        .with_children(|t| {
            t.spawn((
                TooltipTitle,
                theme::label(fonts, "", theme::SM, Weight::Semibold, theme::TEXT),
                Pickable::IGNORE,
            ));
            t.spawn((
                TooltipBody,
                theme::para(fonts, "", theme::XS, theme::TEXT_2, Val::Px(TIP_W - 22.0)),
                Pickable::IGNORE,
            ));
        });

    // the coach ring and bubble
    commands.spawn((
        CoachRing,
        GlobalZIndex(1500),
        Visibility::Hidden,
        Node { position_type: PositionType::Absolute, border: UiRect::all(Val::Px(2.5)), ..default() },
        BorderRadius::all(Val::Px(theme::R_MD + 4.0)),
        BorderColor::all(theme::CYAN),
        Pickable::IGNORE,
        Name::new("CoachRing"),
    ));
    commands
        .spawn((
            CoachBubble,
            GlobalZIndex(1600),
            Visibility::Hidden,
            Node {
                position_type: PositionType::Absolute,
                width: Val::Px(300.0),
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(6.0),
                padding: UiRect::all(Val::Px(14.0)),
                border: UiRect::all(Val::Px(1.5)),
                ..default()
            },
            BorderRadius::all(Val::Px(theme::R_LG)),
            BackgroundColor(theme::mix(theme::SURFACE, theme::CYAN, 0.10)),
            BorderColor::all(theme::CYAN),
            theme::shadow(26.0, 8.0, 0.6),
            bevy::ui::FocusPolicy::Block,
            Name::new("CoachBubble"),
        ))
        .with_children(|b| {
            b.spawn((CoachTitle, theme::label(fonts, "", theme::XS, Weight::Bold, theme::CYAN), Pickable::IGNORE));
            b.spawn((CoachText, theme::para(fonts, "", theme::MD, theme::TEXT, Val::Px(272.0)), Pickable::IGNORE));
            b.spawn(Node {
                justify_content: JustifyContent::SpaceBetween,
                align_items: AlignItems::Center,
                margin: UiRect::top(Val::Px(4.0)),
                ..default()
            })
            .with_children(|row| {
                theme::spawn_button(row, fonts, &assets, Kind::Ghost, None, "Skip the tour", CoachSkip);
                theme::spawn_button(row, fonts, &assets, Kind::Primary, None, "Got it", CoachNext);
            });
        });

    // the next-step card, bottom right of the bench (vessels fill the bench from the top
    // left)
    commands
        .spawn((
            NextStepCard,
            NextStepShow(None),
            Button,
            GlobalZIndex(600),
            Node {
                position_type: PositionType::Absolute,
                right: Val::Px(theme::SIDEBAR_W + 14.0),
                bottom: Val::Px(theme::DOCK_H + 12.0),
                width: Val::Px(280.0),
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(3.0),
                padding: UiRect::axes(Val::Px(12.0), Val::Px(10.0)),
                border: UiRect::all(Val::Px(1.0)),
                display: Display::None,
                ..default()
            },
            BorderRadius::all(Val::Px(theme::R_MD)),
            BackgroundColor(next_step_look(false).0),
            BorderColor::all(next_step_look(false).1),
            theme::shadow(18.0, 6.0, 0.5),
            Tip::Text(
                "Next step",
                "The first step on the tech tree you can make right now. Click to see it in the tree.",
            ),
            Name::new("NextStepCard"),
        ))
        .with_children(|c| {
            c.spawn(Node {
                justify_content: JustifyContent::SpaceBetween,
                align_items: AlignItems::Center,
                ..default()
            })
            .with_children(|h| {
                h.spawn((theme::label(fonts, "NEXT STEP", theme::XS, Weight::Bold, theme::GOLD), Pickable::IGNORE));
                h.spawn((
                    theme::label(fonts, "show in tree  ›", theme::XS, Weight::Regular, theme::TEXT_3),
                    Pickable::IGNORE,
                ));
            });
            c.spawn((
                NextStepTitle,
                theme::label(fonts, "", theme::MD, Weight::Semibold, theme::TEXT),
                Pickable::IGNORE,
            ));
            c.spawn((NextStepBody, theme::para(fonts, "", theme::XS, theme::TEXT_2, Val::Px(256.0)), Pickable::IGNORE));
        });
}

#[cfg(test)]
mod tests {
    use super::*;

    const SCREEN: Vec2 = Vec2::new(1280.0, 720.0);

    fn overlaps(spot: (f32, f32), min: Vec2, size: Vec2) -> bool {
        let (x, y) = spot;
        x < min.x + size.x && x + BUBBLE.x > min.x && y < min.y + size.y && y + BUBBLE.y > min.y
    }

    #[test]
    fn the_bubble_never_covers_what_it_points_at() {
        for (min, size) in [
            (Vec2::new(1045.0, 145.0), Vec2::new(222.0, 48.0)), // a sidebar button
            (Vec2::new(198.0, 552.0), Vec2::new(84.0, 104.0)),  // a shelf tile
            (Vec2::new(36.0, 382.0), Vec2::new(192.0, 34.0)),   // a React button
            (Vec2::new(738.0, 424.0), Vec2::new(280.0, 74.0)),  // the next-step card
            (Vec2::new(14.0, 552.0), Vec2::new(1250.0, 150.0)), // the whole shelf
        ] {
            let spot = bubble_spot(min, size, SCREEN);
            assert!(!overlaps(spot, min, size), "bubble at {spot:?} covers {min:?} {size:?}");
            assert!(spot.0 >= 8.0 && spot.0 + BUBBLE.x <= SCREEN.x - 8.0, "off screen sideways at {spot:?}");
            assert!(spot.1 >= theme::HEADER_H && spot.1 + BUBBLE.y <= SCREEN.y, "off screen vertically at {spot:?}");
        }
    }
}
