// src/ui/hint.rs
//
// The Hint button on the bench, and the targets it offers.
//
// Hint opens a short list of things the player could make next (only the products: how to
// get there is theirs to work out). Picking one makes it the target, and the card asks
// before it tells: first the name of the step that makes it, then one ingredient, then all
// of them, then the vessel and the whole route.
//
// While a target is chosen the shelf shows its kit instead of everything discovered: the
// precursors, worked back from the target through up to four steps. The intermediates are
// left out, even when already discovered, so the player makes them again on the way (by
// carrying products from vessel to vessel, or linking the vessels), and a few unrelated
// substances are mixed in to be ruled out. A setting (and the card) turns the kit off.
use crate::ui::Clicked;
use std::collections::{HashSet, VecDeque};

use bevy::prelude::*;

use crate::components::format_formula;
use crate::data::common::ProcessType;
use crate::data::reactions::Reaction;
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::codex::CodexState;
use crate::ui::inventory::Dock;
use crate::ui::process_toolbar::{vessel_name, ProcessUnlocks};
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::settings::Settings;
use crate::ui::tech_tree::TechTreeState;
use crate::ui::theme::{self, Kind, Weight};
use crate::ui::toasts::{ToastKind, ToastRoom, ToastStack, Toasts};
use crate::GameData;

/// How many targets the list offers at once.
pub const MAX_TARGETS: usize = 6;
/// The longest route a kit asks for (the target's own step included).
pub const MAX_STEPS: usize = 4;
/// How far back from the target a kit looks for intermediates to leave out.
pub const MAX_DEPTH: usize = 3;
/// The hint levels: the step's name, one ingredient, all of them, the vessel and route.
pub const LAST_LEVEL: u8 = 3;
const CARD_W: f32 = 300.0;

// ---------------------------------------------------------------------------------------
// Targets and kits (pure, so the content tests can run them over the whole game)
// ---------------------------------------------------------------------------------------
/// Something new to make, and the step that makes it.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Target {
    pub product: u32,
    pub reaction: u32,
}

/// Whether a reaction can be run with what is known and the vessels unlocked.
pub fn can_run(r: &Reaction, known: &dyn Fn(u32) -> bool, open: &dyn Fn(&ProcessType) -> bool) -> bool {
    open(&r.process) && r.reactants.iter().all(|s| known(s.substance_id)) && r.required_catalyst().is_none_or(known)
}

/// The things that could be made next: undiscovered products of steps that can run now,
/// in tech-tree order (the eras first, the side laboratory after).
pub fn targets(db: &RecipeDatabase, known: &dyn Fn(u32) -> bool, open: &dyn Fn(&ProcessType) -> bool) -> Vec<Target> {
    let side = db.side_epoch();
    let mut out: Vec<Target> = Vec::new();
    for pass_side in [false, true] {
        for r in db.authored.iter().filter(|r| (Some(r.epoch) == side) == pass_side) {
            if !can_run(r, known, open) {
                continue;
            }
            for p in &r.products {
                let id = p.substance_id;
                if !known(id) && !out.iter().any(|t| t.product == id) {
                    out.push(Target { product: id, reaction: r.id });
                }
            }
            if out.len() >= MAX_TARGETS {
                out.truncate(MAX_TARGETS);
                return out;
            }
        }
    }
    out
}

/// What the shelf holds while chasing a target, and the route to it.
#[derive(Clone, Debug, PartialEq, Default)]
pub struct Kit {
    pub target: u32,
    /// the reactions to run, in an order that works (the target's own step last)
    pub steps: Vec<u32>,
    /// the precursors and catalysts the route needs
    pub items: Vec<u32>,
    /// substances the route doesn't need, to be ruled out
    pub decoys: Vec<u32>,
    /// what the route makes on the way (left off the shelf)
    pub intermediates: Vec<u32>,
}

impl Kit {
    /// Everything the kit puts on the shelf.
    pub fn shelf(&self) -> impl Iterator<Item = u32> + '_ {
        self.items.iter().chain(self.decoys.iter()).copied()
    }
}

/// How many decoys a kit with `items` precursors mixes in, given the (fewest, most) setting:
/// the most for a one-ingredient recipe, one fewer for each ingredient after that, never
/// below the fewest. A small recipe is otherwise just its answer.
pub fn decoy_count(items: usize, (fewest, most): (usize, usize)) -> usize {
    let (lo, hi) = (fewest.min(most), fewest.max(most));
    hi.saturating_sub(items.saturating_sub(1)).max(lo)
}

/// Plan the kit for making `target` by `final_id`. `base` is what is never worth remaking
/// (the starting kit and the milestones' raw materials); `pool` is every discovered
/// substance, for the decoys; `decoys` is the (fewest, most) setting (decoy_count).
#[allow(clippy::too_many_arguments)]
pub fn plan_kit(
    db: &RecipeDatabase,
    known: &dyn Fn(u32) -> bool,
    open: &dyn Fn(&ProcessType) -> bool,
    base: &HashSet<u32>,
    pool: &[u32],
    target: u32,
    final_id: u32,
    decoys: (usize, usize),
) -> Option<Kit> {
    let by_id = |id: u32| db.authored.iter().find(|r| r.id == id);
    let fin = by_id(final_id)?;
    let mut steps = vec![fin.id];
    let mut expanded: HashSet<u32> = HashSet::from([target]);
    let mut items: Vec<u32> = Vec::new();
    let add_item = |items: &mut Vec<u32>, id: u32| {
        if !items.contains(&id) {
            items.push(id);
        }
    };
    if let Some(c) = fin.required_catalyst() {
        add_item(&mut items, c);
    }
    // a transient's step is taken first, so the steps it can't do without are never crowded out
    let transient_first = |q: &mut VecDeque<(u32, usize)>, r: &Reaction, depth: usize| {
        for x in &r.reactants {
            if db.transient.contains(&x.substance_id) {
                q.push_front((x.substance_id, depth));
            } else {
                q.push_back((x.substance_id, depth));
            }
        }
    };
    let mut queue: VecDeque<(u32, usize)> = VecDeque::new();
    transient_first(&mut queue, fin, 1);
    while let Some((s, depth)) = queue.pop_front() {
        if expanded.contains(&s) || items.contains(&s) {
            continue;
        }
        // a transient is never on the shelf: its step is always part of the route
        let must_make = db.transient.contains(&s);
        let maker = if must_make || (depth <= MAX_DEPTH && steps.len() < MAX_STEPS && !base.contains(&s)) {
            db.authored.iter().find(|r| {
                r.products.iter().any(|p| p.substance_id == s)
                    && can_run(r, known, open)
                    && !steps.contains(&r.id)
                    // no loops: never back through the target or anything already being made
                    && r.reactants.iter().all(|x| !expanded.contains(&x.substance_id) && x.substance_id != s)
                    // a step taking a transient brings the transient's own step: room for both
                    && (must_make
                        || steps.len() + 1 + r.reactants.iter().filter(|x| db.transient.contains(&x.substance_id)).count()
                            <= MAX_STEPS)
            })
        } else {
            None
        };
        match maker {
            Some(r) => {
                steps.push(r.id);
                expanded.insert(s);
                if let Some(c) = r.required_catalyst() {
                    add_item(&mut items, c);
                }
                transient_first(&mut queue, r, depth + 1);
            }
            None => add_item(&mut items, s),
        }
    }
    // the deepest steps first; the target's own step last
    steps.reverse();
    expanded.remove(&target);
    let mut kit = Kit { target, steps, items, decoys: Vec::new(), intermediates: expanded.into_iter().collect() };
    kit.intermediates.sort_unstable();
    if !makes_target(db, &kit) {
        // never expected; a single step from what's known always works
        kit.steps = vec![fin.id];
        kit.items = fin.reactants.iter().map(|s| s.substance_id).collect();
        kit.items.extend(fin.required_catalyst());
        kit.intermediates.clear();
    }
    // decoys: raw materials the route doesn't touch, picked the same way every time
    let used: HashSet<u32> = kit.items.iter().chain(kit.intermediates.iter()).copied().chain([target]).collect();
    let mut spare: Vec<u32> = pool.iter().copied().filter(|id| base.contains(id) && !used.contains(id)).collect();
    spare.sort_by_key(|id| (id.wrapping_mul(2_654_435_761) ^ target.wrapping_mul(40_503)).rotate_left(7));
    kit.decoys = spare.into_iter().take(decoy_count(kit.items.len(), decoys)).collect();
    Some(kit)
}

/// Whether running the kit's steps in order, from its items alone, makes the target.
pub fn makes_target(db: &RecipeDatabase, kit: &Kit) -> bool {
    let mut have: HashSet<u32> = kit.items.iter().copied().collect();
    for id in &kit.steps {
        let Some(r) = db.authored.iter().find(|r| r.id == *id) else { return false };
        if !r.reactants.iter().all(|s| have.contains(&s.substance_id))
            || r.required_catalyst().is_some_and(|c| !have.contains(&c))
        {
            return false;
        }
        have.extend(r.products.iter().map(|p| p.substance_id));
    }
    have.contains(&kit.target)
}

/// The substances never worth remaking: the starting kit and the milestones' grants.
pub fn base_materials(db: &RecipeDatabase) -> HashSet<u32> {
    db.start.iter().copied().chain(db.milestones.iter().flat_map(|m| m.grant.iter().copied())).collect()
}

// ---------------------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------------------
#[derive(Resource, Default)]
pub struct HintState {
    /// the list of targets is showing
    pub list_open: bool,
    /// the targets the list offers (refreshed when it opens)
    pub offered: Vec<Target>,
    /// what is being chased, and how
    pub target: Option<Target>,
    pub kit: Option<Kit>,
    /// how much the card gives away (0 to LAST_LEVEL)
    pub level: u8,
    /// the decoy setting the kit was planned with (a change re-plans it)
    pub decoys: (usize, usize),
    /// what the button suggests trying next: the first target the list would offer
    pub suggested: Option<Target>,
}

impl HintState {
    /// The kit, while it is what the shelf shows.
    pub fn shelf_kit(&self, settings: Option<&Settings>) -> Option<&Kit> {
        if settings.is_some_and(|s| !s.kit || !s.hints) {
            return None;
        }
        self.target.and(self.kit.as_ref())
    }

    pub fn stop(&mut self) {
        self.target = None;
        self.kit = None;
        self.level = 0;
        self.list_open = false;
    }
}

/// Choose a target: plan its kit (with `decoys`, the (fewest, most) setting) and start the
/// hints from the beginning.
pub fn choose(
    state: &mut HintState,
    t: Target,
    db: &RecipeDatabase,
    progress: &PlayerProgress,
    unlocks: &ProcessUnlocks,
    decoys: (usize, usize),
) {
    let known = |id: u32| progress.discovered.contains(&id);
    let open = |p: &ProcessType| unlocks.0.contains(p);
    let mut pool: Vec<u32> = progress.discovered.iter().copied().collect();
    pool.sort_unstable();
    state.kit = plan_kit(db, &known, &open, &base_materials(db), &pool, t.product, t.reaction, decoys);
    state.decoys = decoys;
    state.target = Some(t);
    state.level = 0;
    state.list_open = false;
}

// ---------------------------------------------------------------------------------------
// The UI
// ---------------------------------------------------------------------------------------
#[derive(Component)]
pub struct HintRoot;
/// The closed state: one button.
#[derive(Component)]
pub struct HintButton;
/// The button's words: "Hint", or "Hint · " and the next thing to try.
#[derive(Component)]
pub struct HintButtonText;
/// The tag on the list's first row when it is the suggestion the button named.
#[derive(Component)]
pub struct HintSuggestedTag;
/// The open state: the list or the target card (rebuilt when it changes).
#[derive(Component)]
pub struct HintPanel;
/// A target in the list.
#[derive(Component)]
pub struct HintPick(pub Target);
#[derive(Component)]
pub struct HintMore;
#[derive(Component)]
pub struct HintChange;
#[derive(Component)]
pub struct HintClose;
#[derive(Component)]
pub struct HintKitToggle;
/// Opens the target's step in the tech tree (the last hint).
#[derive(Component)]
pub struct HintShowTree(pub u32);
/// A hint line on the card (the checks read them).
#[derive(Component)]
pub struct HintLine;
/// The lesson under the hints: the kind of change the step is (systems::lessons).
#[derive(Component)]
pub struct HintLesson;

pub fn spawn_hint_ui(
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
    commands
        .spawn((
            HintRoot,
            GlobalZIndex(600),
            Node {
                position_type: PositionType::Absolute,
                right: Val::Px(14.0),
                bottom: Val::Px(theme::DOCK_H + 12.0),
                flex_direction: FlexDirection::Column,
                align_items: AlignItems::FlexEnd,
                display: Display::None,
                ..default()
            },
            Pickable::IGNORE,
            Name::new("Hint"),
        ))
        .with_children(|root| {
            root.spawn((
                theme::button(
                    Kind::Accent(theme::GOLD),
                    Node {
                        height: Val::Px(36.0),
                        max_width: Val::Px(280.0),
                        padding: UiRect::horizontal(Val::Px(14.0)),
                        column_gap: Val::Px(8.0),
                        align_items: AlignItems::Center,
                        overflow: Overflow::clip(),
                        ..default()
                    },
                    99.0,
                ),
                HintButton,
                theme::shadow(14.0, 5.0, 0.5),
                crate::ui::onboarding::Tip::Text(
                    "Hint",
                    "Pick something to make next. The shelf becomes its kit, and hints come one at a time.",
                ),
            ))
            .with_children(|b| {
                b.spawn(theme::icon(&assets, "target", 16.0, theme::GOLD));
                b.spawn((
                    HintButtonText,
                    theme::label(&fonts, "Hint", theme::SM, Weight::Semibold, theme::TEXT),
                    TextLayout::no_wrap(),
                    Pickable::IGNORE,
                ));
            });
            root.spawn((
                HintPanel,
                Node {
                    border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                    width: Val::Px(CARD_W),
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(6.0),
                    padding: UiRect::axes(Val::Px(12.0), Val::Px(10.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    overflow: Overflow::clip_y(),
                    display: Display::None,
                    ..default()
                },
                BackgroundColor(card_look().0),
                BorderColor::all(card_look().1),
                theme::shadow(18.0, 6.0, 0.5),
                // a tap on the card stays on the card
                Pickable::default(),
            ));
        });
}

/// The card's fill and edge.
pub fn card_look() -> (Color, Color) {
    (theme::mix(theme::SURFACE, theme::GOLD, 0.08).with_alpha(0.97), theme::GOLD.with_alpha(0.75))
}

fn names<'a>(subs: Option<&'a Substances>) -> impl Fn(u32) -> String + 'a {
    move |id| subs.and_then(|s| s.0.get(&id)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"))
}

fn formula(subs: Option<&Substances>, id: u32) -> String {
    subs.and_then(|s| s.0.get(&id)).map(|s| format_formula(&s.formula)).unwrap_or_default()
}

/// The hint lines a level gives away.
pub fn hint_lines(
    db: &RecipeDatabase,
    kit: Option<&Kit>,
    t: Target,
    level: u8,
    name: &dyn Fn(u32) -> String,
) -> Vec<String> {
    let Some(r) = db.authored.iter().find(|r| r.id == t.reaction) else { return vec![] };
    let mut out = vec![format!("Made by: {}", r.name)];
    if level >= 1 {
        if let Some(first) = r.reactants.first() {
            out.push(format!("One ingredient: {}", name(first.substance_id)));
        }
    }
    if level >= 2 {
        // with the equation's amounts, for balanced play: "2 Hydrochloric acid + Zinc"
        let all: Vec<String> = r
            .reactants
            .iter()
            .map(|s| if s.moles > 1 { format!("{} {}", s.moles, name(s.substance_id)) } else { name(s.substance_id) })
            .collect();
        out.push(format!("Ingredients: {}", all.join(" + ")));
        if let Some(c) = r.required_catalyst() {
            out.push(format!("Catalyst: {}", name(c)));
        }
        out.extend(transient_lines(db, r, name));
    }
    if level >= LAST_LEVEL {
        out.push(format!("In the {}", vessel_name(&r.process)));
        if let Some(k) = kit.filter(|k| k.steps.len() > 1) {
            out.push("The route:".to_string());
            for (i, id) in k.steps.iter().enumerate() {
                if let Some(s) = db.authored.iter().find(|x| x.id == *id) {
                    let ins: Vec<String> = s.reactants.iter().map(|x| name(x.substance_id)).collect();
                    let mut line =
                        format!("{}. {}: {} in the {}", i + 1, s.name, ins.join(" + "), vessel_name(&s.process));
                    // a transient it makes goes straight on to the step that uses it
                    let fed =
                        k.steps[i + 1..].iter().filter_map(|n| db.authored.iter().find(|x| x.id == *n)).find(|x| {
                            x.reactants.iter().any(|a| {
                                db.transient.contains(&a.substance_id)
                                    && s.products.iter().any(|p| p.substance_id == a.substance_id)
                            })
                        });
                    if let Some(next) = fed {
                        line.push_str(&format!(", linked into the {}", vessel_name(&next.process)));
                    }
                    out.push(line);
                }
            }
        }
    }
    out
}

/// For each transient a step takes: it doesn't keep, so where it comes from and how.
pub fn transient_lines(db: &RecipeDatabase, r: &Reaction, name: &dyn Fn(u32) -> String) -> Vec<String> {
    r.reactants
        .iter()
        .filter(|s| db.transient.contains(&s.substance_id))
        .filter_map(|s| {
            let maker = db.maker_of(s.substance_id)?;
            Some(format!(
                "{} doesn't keep: make it by {} in the {}, linked into the {}.",
                name(s.substance_id),
                maker.name,
                vessel_name(&maker.process),
                vessel_name(&r.process)
            ))
        })
        .collect()
}

/// Opens and closes the hint, picks targets, gives hints.
#[allow(clippy::too_many_arguments)]
pub fn hint_input_system(
    mut state: ResMut<HintState>,
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    mut settings: ResMut<Settings>,
    mut tree: ResMut<TechTreeState>,
    buttons: Query<AnyOf<(&HintButton, &HintMore, &HintChange, &HintClose, &HintKitToggle)>, With<Clicked>>,
    picks: Query<&HintPick, With<Clicked>>,
    show: Query<&HintShowTree, With<Clicked>>,
    mut taken: MessageWriter<crate::resources::score::HintTaken>,
) {
    let Some(db) = db else { return };
    // the decoy setting changed while chasing: the same target, its kit re-planned
    if let Some(t) = state.target.filter(|_| state.decoys != settings.decoy_range()) {
        let level = state.level;
        choose(&mut state, t, &db, &progress, &unlocks, settings.decoy_range());
        state.level = level;
    }
    for (open, more, change, close, kit) in &buttons {
        if open.is_some() || change.is_some() {
            let known = |id: u32| progress.discovered.contains(&id);
            let vessels = |p: &ProcessType| unlocks.0.contains(p);
            state.offered = targets(&db, &known, &vessels);
            // the button's suggestion leads the list
            if let Some(i) = state.suggested.and_then(|t| state.offered.iter().position(|o| *o == t)) {
                let t = state.offered.remove(i);
                state.offered.insert(0, t);
            }
            state.list_open = true;
        } else if more.is_some() {
            if state.level < LAST_LEVEL {
                taken.write(crate::resources::score::HintTaken);
            }
            state.level = (state.level + 1).min(LAST_LEVEL);
        } else if close.is_some() {
            if state.list_open && state.target.is_some() {
                state.list_open = false; // back to the card
            } else {
                state.stop();
            }
        } else if kit.is_some() {
            settings.kit = !settings.kit;
        }
    }
    for pick in &picks {
        choose(&mut state, pick.0, &db, &progress, &unlocks, settings.decoy_range());
        taken.write(crate::resources::score::HintTaken);
    }
    for s in &show {
        tree.open = true;
        tree.selected = Some(s.0);
    }
}

/// A target that has been made ends the chase; a new game ends it too.
pub fn hint_progress_system(
    mut state: ResMut<HintState>,
    progress: Res<PlayerProgress>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    mut toasts: ResMut<Toasts>,
) {
    if !progress.is_changed() {
        return;
    }
    let Some(t) = state.target else { return };
    if progress.discovered.contains(&t.product) {
        let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
        toasts.push(ToastKind::Milestone, format!("Target made: {}. Pick another from Hint.", names(subs)(t.product)));
        state.stop();
    } else if state.kit.as_ref().is_some_and(|k| k.shelf().any(|id| !progress.discovered.contains(&id))) {
        state.stop(); // the kit holds things this game no longer has (a new game)
    }
}

/// How long the button keeps one suggestion before offering another (real seconds).
pub const SUGGEST_FOR: f64 = 75.0;

/// The button names something to try next, so there is something to aim for without
/// opening anything. It takes turns among the targets the list would offer, moving on with
/// each discovery and every SUGGEST_FOR seconds, so one the player isn't drawn to doesn't
/// sit there for the rest of the era.
#[allow(clippy::too_many_arguments)]
pub fn hint_suggest_system(
    mut state: ResMut<HintState>,
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    time: Res<Time<Real>>,
    mut text: Query<&mut Text, With<HintButtonText>>,
    mut done_for: Local<Option<(usize, usize, bool, usize)>>,
    mut turn: Local<(usize, f64)>,
) {
    let Some(db) = db else { return };
    let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
    let key = (progress.discovered.len(), unlocks.0.len(), subs.is_some(), text.iter().count());
    let now = time.elapsed_secs_f64();
    let due = now - turn.1 >= SUGGEST_FOR;
    if *done_for == Some(key) && !progress.is_changed() && !unlocks.is_changed() && !due {
        return;
    }
    if due || done_for.is_some_and(|k| k.0 != key.0) {
        *turn = (turn.0 + 1, now);
    }
    *done_for = Some(key);
    let known = |id: u32| progress.discovered.contains(&id);
    let open = |p: &ProcessType| unlocks.0.contains(p);
    let list = targets(&db, &known, &open);
    let next = (!list.is_empty()).then(|| list[turn.0 % list.len()]);
    if state.suggested != next {
        state.suggested = next;
    }
    let label = match next {
        Some(t) if subs.is_some() => format!("Hint · {}", names(subs)(t.product)),
        _ => "Hint".to_string(),
    };
    for mut t in &mut text {
        if t.0 != label {
            t.0 = label.clone();
        }
    }
}

/// Shows the button, the list or the card, and keeps the pop-ups clear of it.
#[allow(clippy::too_many_arguments)]
pub fn hint_view_system(
    mut commands: Commands,
    state: Res<HintState>,
    settings: Option<Res<Settings>>,
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    look: (Res<UiFonts>, Res<AssetServer>),
    views: (Res<CodexState>, Res<ReactionLibState>, Res<TechTreeState>, Res<crate::ui::curriculum::CurriculumState>),
    room: (Res<Dock>, ResMut<ToastRoom>, Res<crate::resources::score::Score>, Res<Assets<crate::data::pages::Pages>>),
    mut root: Query<(&mut Node, &ComputedNode), With<HintRoot>>,
    mut button: Query<&mut Node, (With<HintButton>, Without<HintRoot>, Without<HintPanel>)>,
    mut panel: Query<(Entity, &mut Node), (With<HintPanel>, Without<HintRoot>, Without<HintButton>)>,
    mut toast_stack: Query<&mut Node, (With<ToastStack>, Without<HintRoot>, Without<HintButton>, Without<HintPanel>)>,
    mut last: Local<Option<(bool, Option<Target>, u8, bool, usize, Option<u32>)>>,
) {
    let (fonts, assets) = look;
    let (codex, rlib, tree, learn) = views;
    let (dock, mut toast_room, score, pages) = room;
    let Ok((mut root_node, computed)) = root.single_mut() else { return };
    let wanted = settings.as_ref().is_none_or(|s| s.hint_button())
        && progress.ready
        && !(codex.open || rlib.open || tree.open || learn.open);
    let d = if wanted { Display::Flex } else { Display::None };
    if root_node.display != d {
        root_node.display = d;
    }
    let bottom = Val::Px(dock.h + crate::ui::bench_controls::BAR_LIFT);
    if root_node.bottom != bottom {
        root_node.bottom = bottom;
    }
    // the open card never grows past the bench
    let max_h = Val::Px((dock.bench - crate::ui::bench_controls::BAR_LIFT - 12.0).max(120.0));
    let open = state.list_open || state.target.is_some();
    if let Ok(mut b) = button.single_mut() {
        let d = if open { Display::None } else { Display::Flex };
        if b.display != d {
            b.display = d;
        }
    }
    let Ok((panel_e, mut panel_node)) = panel.single_mut() else { return };
    let d = if open { Display::Flex } else { Display::None };
    if panel_node.display != d {
        panel_node.display = d;
    }
    if panel_node.max_height != max_h {
        panel_node.max_height = max_h;
    }
    // the pop-ups rise above whatever shows here
    let lift = if wanted {
        let h = computed.size.y * computed.inverse_scale_factor();
        if h > 0.0 {
            h + 10.0
        } else {
            46.0
        }
    } else {
        0.0
    };
    if let Ok(mut t) = toast_stack.single_mut() {
        let want = Val::Px(dock.h + crate::ui::bench_controls::BAR_LIFT + 2.0 + lift);
        if t.bottom != want {
            t.bottom = want;
        }
    }
    let fit = (((dock.bench - lift - 14.0) / 50.0).floor().max(1.0) as usize).min(4);
    if toast_room.0 != fit {
        toast_room.0 = fit;
    }

    let kit_on = settings.as_ref().is_none_or(|s| s.kit);
    // with scoring on, the next clue says what it costs
    let cost = settings.as_ref().is_some_and(|s| s.scoring).then(|| score.next_hint_cost());
    let key = (state.list_open, state.target, state.level, kit_on, state.offered.len(), cost);
    if *last == Some(key) && !state.is_changed() {
        return;
    }
    *last = Some(key);
    let Some(db) = db else { return };
    let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
    let curriculum = game_data.as_ref().and_then(|g| pages.get(&g.pages));
    let name = names(subs);
    commands.entity(panel_e).despawn_children();
    commands.entity(panel_e).with_children(|p| {
        // header: what this is, and how to put it away
        p.spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            align_items: AlignItems::Center,
            column_gap: Val::Px(8.0),
            flex_shrink: 0.0,
            ..default()
        })
        .with_children(|h| {
            let title = match (&state.kit, state.list_open) {
                (_, true) => "WHAT TO MAKE NEXT?".to_string(),
                (Some(k), false) => {
                    let n = k.steps.len();
                    format!("TARGET · {n} STEP{}", if n == 1 { "" } else { "S" })
                }
                (None, false) => "TARGET".to_string(),
            };
            h.spawn((theme::label(&fonts, title, theme::XS, Weight::Bold, theme::GOLD), Pickable::IGNORE));
            h.spawn(Node { column_gap: Val::Px(4.0), align_items: AlignItems::Center, ..default() }).with_children(|b| {
                if state.target.is_some() && !state.list_open {
                    theme::spawn_button(b, &fonts, &assets, Kind::Ghost, None, "Change", HintChange);
                }
                theme::spawn_icon_button(b, &assets, "close", 28.0, theme::TEXT_2, HintClose);
            });
        });
        if state.list_open {
            p.spawn((
                theme::para(
                    &fonts,
                    if kit_on {
                        "Pick a target. The shelf becomes its kit: work out what to make on the way, and leave out what doesn't belong."
                    } else {
                        "Pick a target, then ask for hints when you're stuck."
                    },
                    theme::XS,
                    theme::TEXT_2,
                    Val::Px(CARD_W - 26.0),
                ),
                Pickable::IGNORE,
            ));
            // the rows scroll when the bench is short
            p.spawn((
                Node {
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(4.0),
                    flex_shrink: 1.0,
                    min_height: Val::Px(0.0),
                    overflow: Overflow::scroll_y(),
                    ..default()
                },
                ScrollPosition::default(),
                Pickable::default(),
            ))
            .with_children(|rows| {
                if state.offered.is_empty() {
                    rows.spawn((
                        theme::para(
                            &fonts,
                            "Nothing new can be made from what you have yet. The tech tree shows what each locked step needs.",
                            theme::XS,
                            theme::TEXT_3,
                            Val::Px(CARD_W - 26.0),
                        ),
                        Pickable::IGNORE,
                    ));
                }
                for (i, t) in state.offered.iter().enumerate() {
                    let suggested = i == 0 && state.suggested == Some(*t);
                    rows.spawn((
                        theme::button(
                            Kind::Row,
                            Node {
                                min_height: Val::Px(38.0),
                                flex_shrink: 0.0,
                                flex_direction: FlexDirection::Column,
                                justify_content: JustifyContent::Center,
                                padding: UiRect::axes(Val::Px(10.0), Val::Px(4.0)),
                                ..default()
                            },
                            theme::R_SM,
                        ),
                        HintPick(*t),
                    ))
                    .with_children(|r| {
                        r.spawn((Node { column_gap: Val::Px(8.0), align_items: AlignItems::Baseline, ..default() }, Pickable::IGNORE))
                            .with_children(|top| {
                                top.spawn((theme::label(&fonts, name(t.product), theme::SM, Weight::Semibold, theme::TEXT), Pickable::IGNORE));
                                if suggested {
                                    top.spawn((
                                        HintSuggestedTag,
                                        theme::label(&fonts, "SUGGESTED", 9.5, Weight::Bold, theme::GOLD),
                                        Pickable::IGNORE,
                                    ));
                                }
                            });
                        r.spawn((theme::label(&fonts, formula(subs, t.product), theme::XS, Weight::Regular, theme::CYAN), Pickable::IGNORE));
                    });
                }
            });
            return;
        }
        let Some(t) = state.target else { return };
        p.spawn(Node { column_gap: Val::Px(8.0), align_items: AlignItems::Baseline, flex_wrap: FlexWrap::Wrap, flex_shrink: 0.0, ..default() })
            .with_children(|r| {
                r.spawn((theme::label(&fonts, name(t.product), theme::MD, Weight::Semibold, theme::TEXT), Pickable::IGNORE));
                r.spawn((theme::label(&fonts, formula(subs, t.product), theme::SM, Weight::Regular, theme::CYAN), Pickable::IGNORE));
            });
        p.spawn((
            Node { flex_direction: FlexDirection::Column, row_gap: Val::Px(2.0), flex_shrink: 1.0, min_height: Val::Px(0.0), overflow: Overflow::scroll_y(), ..default() },
            ScrollPosition::default(),
            Pickable::default(),
        ))
        .with_children(|lines| {
            for line in hint_lines(&db, state.kit.as_ref(), t, state.level, &name) {
                lines.spawn((HintLine, theme::para(&fonts, line, theme::XS, theme::TEXT_2, Val::Px(CARD_W - 26.0)), Pickable::IGNORE));
            }
            // from the first hint on, the idea behind the step
            let step = db.authored.iter().find(|r| r.id == t.reaction);
            if let (true, Some(r), Some(subs)) = (state.level >= 1, step, subs) {
                lines.spawn((
                    HintLesson,
                    theme::para(&fonts, crate::systems::lessons::lesson(r, subs), theme::XS, theme::mix(theme::GOLD, theme::TEXT, 0.35), Val::Px(CARD_W - 26.0)),
                    Pickable::IGNORE,
                ));
                // and the idea's own article, in Learn (the reaction's topic, never its
                // vessel's: the vessel is a later hint)
                let topic = curriculum
                    .and_then(|pg| pg.reactions.get(&r.id).and_then(|ts| ts.first()).and_then(|k| pg.topics.get(k).map(|t| (k, t))));
                if let Some((k, topic)) = topic {
                    lines.spawn(Node { margin: UiRect::top(Val::Px(4.0)), ..default() }).with_children(|b| {
                        crate::ui::curriculum::spawn_learn_button(b, &fonts, &assets, k, topic);
                    });
                }
            }
        });
        p.spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            align_items: AlignItems::Center,
            column_gap: Val::Px(6.0),
            flex_shrink: 0.0,
            margin: UiRect::top(Val::Px(2.0)),
            ..default()
        })
        .with_children(|row| {
            let kit_label = if kit_on { "Shelf: kit" } else { "Shelf: everything" };
            theme::spawn_button(row, &fonts, &assets, Kind::Secondary, Some("flask"), kit_label, HintKitToggle);
            if state.level < LAST_LEVEL {
                let more = match cost {
                    Some(c) => format!("More hint (\u{2212}{c})"),
                    None => "More hint".to_string(),
                };
                theme::spawn_button(row, &fonts, &assets, Kind::Accent(theme::GOLD), None, &more, HintMore);
            } else {
                theme::spawn_button(row, &fonts, &assets, Kind::Secondary, Some("tree"), "In the tree", HintShowTree(t.reaction));
            }
        });
    });
}

#[cfg(test)]
mod tests {
    use super::decoy_count;

    #[test]
    fn small_recipes_get_the_most_decoys() {
        let setting = (3, 8);
        assert_eq!(decoy_count(1, setting), 8, "one ingredient: the most");
        assert_eq!(decoy_count(2, setting), 7);
        assert_eq!(decoy_count(6, setting), 3);
        assert_eq!(decoy_count(12, setting), 3, "never below the fewest");
        assert_eq!(decoy_count(0, setting), 8);
        assert_eq!(decoy_count(4, (8, 3)), 5, "the two ends in either order");
        assert_eq!(decoy_count(4, (0, 0)), 0, "none at all");
    }
}
