// src/systems/input_checks.rs
//
// The interaction checks: every way a player touches the game, performed through the real
// input stack and checked for its effect. They run at the start of every `--autoplay`
// run (`--steps 0` runs only these), each from a clean bench, and land in the review
// report with a screenshot of anything that failed.
//
// A virtual mouse and keyboard drive the game through its real input paths: bevy_ui's
// buttons see the window cursor and mouse-button state; bevy_picking (tile clicks, drags,
// drops, links) sees a pointer of its own, so the real mouse cannot interfere with it; the
// game's wheel and key handling see ordinary wheel and key messages. While the checks run
// the window moves the system cursor around, so leave the mouse alone for a minute or two.
//
// Besides one check per interaction there are three data-driven groups, built from the
// authored content when the checks start: reactions from every era (covering every
// vessel) performed entirely by hand, chains of two to four linked vessels where each
// reaction's product travels down the line and sets off the next, and the vessel tiers
// (a higher tier runs the recipes below it; a lower one says which vessel it needs).
use std::collections::{HashMap, VecDeque};
use std::path::PathBuf;

use bevy::asset::uuid::Uuid;
use bevy::camera::NormalizedRenderTarget;
use bevy::ecs::world::CommandQueue;
use bevy::input::keyboard::{Key, KeyboardInput, NativeKey};
use bevy::input::mouse::{MouseButtonInput, MouseScrollUnit, MouseWheel};
use bevy::input::touch::TouchPhase;
use bevy::input::ButtonState;
use bevy::picking::pointer::{Location, PointerAction, PointerButton as PickButton, PointerId, PointerInput};
use bevy::prelude::*;
use bevy::render::view::window::screenshot::{save_to_disk, Screenshot};
use bevy::window::{CursorMoved, PresentMode, PrimaryWindow, WindowRef};

use crate::components::ui_markers::{
    CanvasScrollingPane, InCatalystZone, InVessel, InputPort, OutputPort, ProcessVessel, ReactionCanvasRoot,
    ReactionLink, VesselCard, VesselCatalystZone, VesselClearButton, VesselDeleteButton, VesselIngredientZone,
    VesselReactButton,
};
use crate::components::Ingredient;
use crate::data::common::ProcessType;
use crate::data::reactions::Reaction;
use crate::data::substances::Substances;
use crate::resources::player_progress::{reset_progress, FiredMilestones, PlayerProgress};
use crate::resources::recipe_database::Lookup;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::drag_drop::{DragGhostNode, LinkDragState};
use crate::systems::reaction_check::{spawn_vessel_card, EquationText, VesselArtBig, VesselArtSmall, VESSEL_W};
use crate::ui::codex::{
    CodexCategoryTab, CodexDetail, CodexEntry, CodexFilter, CodexIndustryCard, CodexListContent, CodexReactionLink,
    CodexRefLink, CodexScrollable, CodexState, URL_SINK,
};
use crate::ui::credits::CreditsUi;
use crate::ui::detail_panel::{SelectedSubstance, SelectionClearButton, SelectionOpenButton};
use crate::ui::focus::KeyFocus;
use crate::ui::inventory::{
    is_element_formula, CategoryTab, InvCategory, InventoryContent, InventoryScroll, ShelfTile,
};
use crate::ui::onboarding::{
    Coach, CoachBubble, CoachNext, CoachSkip, CoachStep, EraBanner, TooltipNode, TooltipTitle, TourAgainButton,
};
use crate::ui::process_toolbar::{vessel_name, NewGameButton, ProcessButton, ProcessUnlocks, VesselSidebar, VESSELS};
use crate::ui::reaction_library::{
    ReactionLibEntry, ReactionLibListContent, ReactionLibScrollable, ReactionLibState, ReactionLibSubstanceLink,
};
use crate::ui::settings::{Field, SettingStep, SettingToggle, Settings, SettingsAbout, SettingsUi};
use crate::ui::shell::scroll_max;
use crate::ui::shell::{BenchGrid, NavTab, SettingsButton, View};
use crate::ui::tech_tree::{
    SelectionLink, TechCloseButton, TechGraphView, TechLinks, TechListView, TechMode, TechModeButton, TechNeedBadge,
    TechNeedButton, TechNodeButton, TechOpenInLibrary, TechScrollable, TechTreeState,
};
use crate::ui::toasts::{ToastKind, Toasts};
use crate::ui::virtual_list::VirtualList;
use crate::GameData;

// Sound, keyboard and controller, hover states, saves, credits and achievements.
mod polish;

/// The checks' own picking pointer (the real mouse keeps PointerId::Mouse).
const CHECK_POINTER: PointerId = PointerId::Custom(Uuid::from_u128(0x000c_0ffe_e0c4_ec4b_5a9d_3e5c_u128));

type Probe = Box<dyn Fn(&mut World) -> Option<Vec2> + Send + Sync>;
type Verify = Box<dyn Fn(&mut World) -> Result<(), String> + Send + Sync>;
type Setup = Box<dyn Fn(&mut World) + Send + Sync>;

/// Something on screen to point at.
pub struct Target {
    name: String,
    find: Probe,
}

enum Op {
    Do(Setup),
    Click(Target),
    /// two clicks in quick succession (a double-tap)
    DoubleClick(Target),
    Drag(Target, Target),
    DragBy(Target, Vec2),
    Wheel(Target, f32),
    /// press on a target and start dragging (hold the button)
    Press(Target),
    /// move the held pointer onto a target
    MoveTo(Target),
    /// let go
    Release,
    Key(KeyCode),
    Wait(u32),
    /// let this many real seconds pass (frames can be quick or slow)
    Pause(f64),
    /// poll every frame until it holds, failing after this many frames
    Until(Verify, u32),
    Expect(Verify),
    /// a screenshot for the report (the help overlays, which only a picture can review)
    Shot(&'static str),
}

pub struct Check {
    pub area: &'static str,
    pub name: &'static str,
    ops: Vec<Op>,
}

#[derive(Clone, Debug)]
pub struct CheckResult {
    pub area: &'static str,
    pub name: &'static str,
    pub ok: bool,
    pub note: String,
    pub shot: Option<String>,
}

/// One frame of input.
enum Prim {
    Move(Vec2),
    Press,
    Release,
    Wheel(f32),
    KeyDown(KeyCode),
    KeyUp(KeyCode),
    Idle,
}

#[derive(Resource, Default)]
pub struct InputChecks {
    /// set by the review run to start the checks
    pub requested: bool,
    pub done: bool,
    pub out_dir: Option<PathBuf>,
    pub results: Vec<CheckResult>,
    /// (label, file) of the screenshots the checks took on purpose
    pub shots: Vec<(String, String)>,
    checks: Vec<Check>,
    started: bool,
    i: usize,
    op: usize,
    prims: VecDeque<Prim>,
    wait: u32,
    polls: u32,
    cursor: Vec2,
    pressed: bool,
    pause_until: Option<f64>,
}

/// Values a check remembers between its steps (a card's position before a drag...).
#[derive(Resource, Default)]
pub struct Scratch(pub HashMap<&'static str, f32>);

pub struct InputChecksPlugin;

impl Plugin for InputChecksPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<InputChecks>()
            .init_resource::<Scratch>()
            .add_systems(PreUpdate, input_checks_system.before(bevy::input::InputSystems));
    }
}

// ---------------------------------------------------------------------------------------
// The runner
// ---------------------------------------------------------------------------------------
enum Flow {
    Next,
    Again,
    Fail(String),
}

pub fn input_checks_system(world: &mut World) {
    let Some(mut st) = world.remove_resource::<InputChecks>() else { return };
    if st.requested && !st.done {
        step(world, &mut st);
    }
    world.insert_resource(st);
}

fn step(world: &mut World, st: &mut InputChecks) {
    if !st.started {
        st.started = true;
        world.spawn((CHECK_POINTER, Name::new("CheckPointer")));
        st.checks = all_checks(world);
        // `--only a,b` runs just the checks whose area or name contains one of those words
        let args: Vec<String> = std::env::args().collect();
        if let Some(only) = args.iter().position(|a| a == "--only").and_then(|i| args.get(i + 1)) {
            let want: Vec<String> = only.to_lowercase().split(',').map(|w| w.trim().to_string()).collect();
            st.checks.retain(|c| {
                let label = format!("{} {}", c.area, c.name).to_lowercase();
                want.iter().any(|w| label.contains(w))
            });
        }
        if let Ok(mut sink) = URL_SINK.lock() {
            *sink = Some(Vec::new());
        }
        let c = world
            .query_filtered::<&Window, With<PrimaryWindow>>()
            .iter(world)
            .next()
            .map(|w| Vec2::new(w.width(), w.height()) / 2.0);
        st.cursor = c.unwrap_or(Vec2::new(640.0, 360.0));
        info!("Interaction checks: {}", st.checks.len());
    }
    if st.wait > 0 {
        st.wait -= 1;
        return;
    }
    if let Some(p) = st.prims.pop_front() {
        apply(world, st, p);
        return;
    }
    if st.i >= st.checks.len() {
        fresh(world);
        new_game(world);
        // the checks' pointer leaves with them (a pointer parked over a button would keep
        // its tooltip up through the rest of the run)
        let pointers: Vec<Entity> = world
            .query::<(Entity, &PointerId)>()
            .iter(world)
            .filter(|(_, id)| **id == CHECK_POINTER)
            .map(|(e, _)| e)
            .collect();
        for e in pointers {
            world.despawn(e);
        }
        if let Ok(mut sink) = URL_SINK.lock() {
            *sink = None;
        }
        st.done = true;
        let failed = st.results.iter().filter(|r| !r.ok).count();
        info!("Interaction checks done: {} passed, {} failed", st.results.len() - failed, failed);
        return;
    }
    let checks = std::mem::take(&mut st.checks);
    let check = &checks[st.i];
    if st.op >= check.ops.len() {
        st.results.push(CheckResult { area: check.area, name: check.name, ok: true, note: String::new(), shot: None });
        next_check(st);
        st.checks = checks;
        return;
    }
    let flow = run_op(world, st, &check.ops[st.op]);
    match flow {
        Flow::Next => {
            st.op += 1;
            st.polls = 0;
        }
        Flow::Again => {
            st.polls += 1;
        }
        Flow::Fail(note) => {
            let file = format!("check_{:02}_{}.png", st.i + 1, slug(check.name));
            let shot = st.out_dir.as_ref().map(|d| {
                let path = d.join("shots").join(&file);
                world.spawn(Screenshot::primary_window()).observe(save_to_disk(path));
                format!("shots/{file}")
            });
            warn!("Check failed: {} / {}: {}", check.area, check.name, note);
            st.results.push(CheckResult { area: check.area, name: check.name, ok: false, note, shot });
            if st.pressed {
                st.prims.push_back(Prim::Release);
            }
            st.wait = 4; // let the screenshot render before the next check tidies up
            next_check(st);
        }
    }
    st.checks = checks;
}

fn next_check(st: &mut InputChecks) {
    st.i += 1;
    st.op = 0;
    st.polls = 0;
    st.pause_until = None;
}

const FIND_FRAMES: u32 = 30;

fn run_op(world: &mut World, st: &mut InputChecks, op: &Op) -> Flow {
    let find =
        |world: &mut World, t: &Target| (t.find)(world).ok_or_else(|| format!("could not find {} on screen", t.name));
    // a target can need a frame or two (a list scrolling to it, a page being built)
    let missing = |st: &InputChecks, e: String| if st.polls < FIND_FRAMES { Flow::Again } else { Flow::Fail(e) };
    match op {
        Op::Do(f) => {
            f(world);
            Flow::Next
        }
        Op::Click(t) => match find(world, t) {
            Ok(p) => {
                st.prims.extend([
                    Prim::Move(p),
                    Prim::Idle,
                    Prim::Press,
                    Prim::Idle,
                    Prim::Release,
                    Prim::Idle,
                    Prim::Idle,
                ]);
                Flow::Next
            }
            Err(e) => missing(st, e),
        },
        Op::DoubleClick(t) => match find(world, t) {
            Ok(p) => {
                st.prims.extend([
                    Prim::Move(p),
                    Prim::Idle,
                    Prim::Press,
                    Prim::Release,
                    Prim::Press,
                    Prim::Release,
                    Prim::Idle,
                    Prim::Idle,
                ]);
                Flow::Next
            }
            Err(e) => missing(st, e),
        },
        Op::Drag(a, b) => match (find(world, a), find(world, b)) {
            (Ok(pa), Ok(pb)) => {
                push_drag(st, pa, pb);
                Flow::Next
            }
            (Err(e), _) | (_, Err(e)) => missing(st, e),
        },
        Op::DragBy(a, d) => match find(world, a) {
            Ok(pa) => {
                push_drag(st, pa, pa + *d);
                Flow::Next
            }
            Err(e) => missing(st, e),
        },
        Op::Wheel(t, dy) => match find(world, t) {
            Ok(p) => {
                st.prims.extend([Prim::Move(p), Prim::Idle, Prim::Wheel(*dy), Prim::Idle, Prim::Idle]);
                Flow::Next
            }
            Err(e) => missing(st, e),
        },
        Op::Press(t) => match find(world, t) {
            Ok(p) => {
                // the small nudge is what makes it a drag
                st.prims.extend([
                    Prim::Move(p),
                    Prim::Idle,
                    Prim::Press,
                    Prim::Idle,
                    Prim::Move(p + Vec2::new(10.0, -10.0)),
                    Prim::Idle,
                ]);
                Flow::Next
            }
            Err(e) => missing(st, e),
        },
        Op::MoveTo(t) => match find(world, t) {
            Ok(p) => {
                let from = st.cursor;
                for f in [0.25, 0.5, 0.75, 1.0] {
                    st.prims.push_back(Prim::Move(from.lerp(p, f)));
                }
                st.prims.push_back(Prim::Idle);
                Flow::Next
            }
            Err(e) => missing(st, e),
        },
        Op::Release => {
            st.prims.extend([Prim::Release, Prim::Idle, Prim::Idle]);
            Flow::Next
        }
        Op::Key(k) => {
            st.prims.extend([Prim::KeyDown(*k), Prim::KeyUp(*k), Prim::Idle]);
            Flow::Next
        }
        Op::Wait(n) => {
            st.wait = *n;
            Flow::Next
        }
        Op::Pause(secs) => {
            let now = world.resource::<Time<Real>>().elapsed_secs_f64();
            match st.pause_until {
                None => {
                    st.pause_until = Some(now + secs);
                    Flow::Again
                }
                Some(until) if now >= until => {
                    st.pause_until = None;
                    Flow::Next
                }
                Some(_) => Flow::Again,
            }
        }
        Op::Until(v, max) => match v(world) {
            Ok(()) => Flow::Next,
            Err(e) if st.polls >= *max => Flow::Fail(e),
            Err(_) => Flow::Again,
        },
        Op::Expect(v) => match v(world) {
            Ok(()) => Flow::Next,
            Err(e) => Flow::Fail(e),
        },
        Op::Shot(label) => {
            if let Some(d) = st.out_dir.clone() {
                let file = format!("help_{:02}_{}.png", st.shots.len() + 1, slug(label));
                world.spawn(Screenshot::primary_window()).observe(save_to_disk(d.join("shots").join(&file)));
                st.shots.push((label.to_string(), file));
            }
            st.wait = 6; // let it render before the next step changes the screen
            Flow::Next
        }
    }
}

fn push_drag(st: &mut InputChecks, a: Vec2, b: Vec2) {
    st.prims.extend([Prim::Move(a), Prim::Idle, Prim::Press, Prim::Idle]);
    for t in [0.2, 0.4, 0.6, 0.8, 1.0] {
        st.prims.push_back(Prim::Move(a.lerp(b, t)));
    }
    st.prims.extend([Prim::Idle, Prim::Idle, Prim::Release, Prim::Idle, Prim::Idle]);
}

fn apply(world: &mut World, st: &mut InputChecks, p: Prim) {
    let Some(window) = world.query_filtered::<Entity, With<PrimaryWindow>>().iter(world).next() else { return };
    let Some(target) = WindowRef::Primary.normalize(Some(window)).map(NormalizedRenderTarget::Window) else { return };
    let new_pos = if let Prim::Move(pos) = p { pos } else { st.cursor };
    // Every frame, put the window cursor where the checks want it: a stray real mouse
    // movement since the last frame is overridden before bevy_ui looks at it.
    if let Ok(mut w) = world.query_filtered::<&mut Window, With<PrimaryWindow>>().single_mut(world) {
        if w.cursor_position() != Some(new_pos) {
            w.set_cursor_position(Some(new_pos));
        }
    }
    let location = Location { target, position: new_pos };
    match p {
        Prim::Move(pos) => {
            let delta = pos - st.cursor;
            st.cursor = pos;
            world.write_message(CursorMoved { window, position: pos, delta: Some(delta) });
            world.write_message(PointerInput::new(CHECK_POINTER, location, PointerAction::Move { delta }));
        }
        Prim::Press | Prim::Release => {
            let down = matches!(p, Prim::Press);
            st.pressed = down;
            let state = if down { ButtonState::Pressed } else { ButtonState::Released };
            world.write_message(MouseButtonInput { button: MouseButton::Left, state, window });
            let action = if down {
                PointerAction::Press(PickButton::Primary)
            } else {
                PointerAction::Release(PickButton::Primary)
            };
            world.write_message(PointerInput::new(CHECK_POINTER, location, action));
        }
        Prim::Wheel(dy) => {
            world.write_message(MouseWheel {
                unit: MouseScrollUnit::Line,
                x: 0.0,
                y: dy,
                window,
                phase: TouchPhase::Moved,
            });
        }
        Prim::KeyDown(k) | Prim::KeyUp(k) => {
            let state = if matches!(p, Prim::KeyDown(_)) { ButtonState::Pressed } else { ButtonState::Released };
            let ev = KeyboardInput {
                key_code: k,
                logical_key: Key::Unidentified(NativeKey::Unidentified),
                state,
                text: None,
                repeat: false,
                window,
            };
            world.write_message(ev);
        }
        Prim::Idle => {}
    }
}

fn slug(s: &str) -> String {
    s.to_lowercase()
        .chars()
        .map(|c| if c.is_ascii_alphanumeric() { c } else { '_' })
        .collect::<String>()
        .split('_')
        .filter(|p| !p.is_empty())
        .collect::<Vec<_>>()
        .join("_")
}

// ---------------------------------------------------------------------------------------
// Finding things on screen
// ---------------------------------------------------------------------------------------
/// A point inside a UI node, in window pixels (fx, fy from 0 to 1 across the node). A node
/// scrolled out of its list is scrolled into view first (None this frame; the step retries).
fn point_in(world: &mut World, e: Entity, fx: f32, fy: f32) -> Option<Vec2> {
    let sf = world
        .query_filtered::<&Window, With<PrimaryWindow>>()
        .iter(world)
        .next()
        .map(|w| w.scale_factor())
        .unwrap_or(1.0);
    let (node, tf, vis) =
        world.query::<(&ComputedNode, &UiGlobalTransform, Option<&InheritedVisibility>)>().get(world, e).ok()?;
    if node.size.x <= 0.0 || node.size.y <= 0.0 || vis.is_some_and(|v| !v.get()) {
        return None;
    }
    let (centre, size) = (tf.translation, node.size);
    if !reveal(world, e, centre) {
        return None;
    }
    // through the node's transform, so a zoomed bench's cards are pointed at where they show
    let tf = *world.get::<UiGlobalTransform>(e)?;
    let p = tf.affine().transform_point2((Vec2::new(fx, fy) - 0.5) * size) / sf;
    // on screen, or it can't be pointed at
    let size = world
        .query_filtered::<&Window, With<PrimaryWindow>>()
        .iter(world)
        .next()
        .map(|w| Vec2::new(w.width(), w.height()))?;
    (p.x >= 0.0 && p.y >= 0.0 && p.x < size.x && p.y < size.y).then_some(p)
}

/// If a scrolling ancestor hides `centre` (physical px), scroll it there and say so.
fn reveal(world: &mut World, e: Entity, centre: Vec2) -> bool {
    let mut a = e;
    while let Some(parent) = world.get::<ChildOf>(a).map(|c| c.parent()) {
        a = parent;
        let Some(node) = world.get::<Node>(a) else { continue };
        let (sx, sy) = (node.overflow.x == OverflowAxis::Scroll, node.overflow.y == OverflowAxis::Scroll);
        if !sx && !sy {
            continue;
        }
        let Ok((cn, tf)) = world.query::<(&ComputedNode, &UiGlobalTransform)>().get(world, a) else { continue };
        let (vc, half, inv) = (tf.translation, cn.size / 2.0, cn.inverse_scale_factor());
        let d = centre - vc;
        let out_x = sx && d.x.abs() > half.x - 8.0;
        let out_y = sy && d.y.abs() > half.y - 8.0;
        if !out_x && !out_y {
            continue;
        }
        if let Some(mut sp) = world.get_mut::<ScrollPosition>(a) {
            if out_x {
                sp.0.x = (sp.0.x + d.x * inv).max(0.0);
            }
            if out_y {
                sp.0.y = (sp.0.y + d.y * inv).max(0.0);
            }
        }
        return false;
    }
    true
}

fn first<C: Component>(world: &mut World, pred: impl Fn(&C) -> bool) -> Option<Entity> {
    let mut found: Vec<Entity> =
        world.query::<(Entity, &C)>().iter(world).filter(|(_, c)| pred(c)).map(|(e, _)| e).collect();
    found.sort();
    found.first().copied()
}

/// The first descendant of `root` carrying `C` (breadth first).
fn descendant<C: Component>(world: &mut World, root: Entity) -> Option<Entity> {
    let mut queue = VecDeque::from([root]);
    while let Some(e) = queue.pop_front() {
        if e != root && world.get::<C>(e).is_some() {
            return Some(e);
        }
        if let Some(ch) = world.get::<Children>(e) {
            queue.extend(ch.iter());
        }
    }
    None
}

fn card(world: &mut World, p: ProcessType) -> Option<Entity> {
    let mut cards: Vec<Entity> = world
        .query_filtered::<(Entity, &ProcessVessel), With<VesselCard>>()
        .iter(world)
        .filter(|(_, v)| v.process == p)
        .map(|(e, _)| e)
        .collect();
    cards.sort();
    cards.first().copied()
}

fn sub_id(world: &World, name: &str) -> Option<u32> {
    let gd = world.get_resource::<GameData>()?;
    let subs = world.resource::<Assets<Substances>>().get(&gd.substances)?;
    subs.0.values().filter(|s| s.name == name).map(|s| s.id).min()
}

fn target(name: impl Into<String>, f: impl Fn(&mut World) -> Option<Vec2> + Send + Sync + 'static) -> Target {
    Target { name: name.into(), find: Box::new(f) }
}

fn tile(name: &'static str) -> Target {
    target(format!("the {name} tile on the shelf"), move |w| {
        let mut tiles: Vec<Entity> = w
            .query_filtered::<(Entity, &Ingredient), With<ShelfTile>>()
            .iter(w)
            .filter(|(_, i)| i.name == name)
            .map(|(e, _)| e)
            .collect();
        tiles.sort();
        match tiles.first() {
            Some(e) => point_in(w, *e, 0.5, 0.5),
            // the shelf builds only what is near the view: scroll there and look again
            None => {
                let id = sub_id(w, name)?;
                crate::ui::inventory::reveal_on_shelf(w, id);
                None
            }
        }
    })
}

#[derive(Clone, Copy)]
enum CardPart {
    Art,
    Title,
    Zone,
    CatalystSlot,
    React,
    Clear,
    Close,
    InPort,
    OutPort,
    FirstChip,
}

/// A shelf tile by substance id (scrolled into view if the shelf is long).
fn tile_id(id: u32, label: String) -> Target {
    target(format!("the {label} tile on the shelf"), move |w| {
        let e = w.query_filtered::<(Entity, &Ingredient), With<ShelfTile>>().iter(w).find(|(_, i)| i.id == id);
        match e {
            Some((e, _)) => point_in(w, e, 0.5, 0.5),
            None => {
                crate::ui::inventory::reveal_on_shelf(w, id);
                None
            }
        }
    })
}

fn card_part(p: ProcessType, part: CardPart) -> Target {
    let label = match part {
        CardPart::Art => "picture",
        CardPart::Title => "title",
        CardPart::Zone => "contents",
        CardPart::CatalystSlot => "catalyst slot",
        CardPart::React => "React button",
        CardPart::Clear => "clear button",
        CardPart::Close => "close button",
        CardPart::InPort => "input port",
        CardPart::OutPort => "output port",
        CardPart::FirstChip => "first substance",
    };
    let pp = p.clone();
    target(format!("the {}'s {}", vessel_name(&p), label), move |w| {
        let c = card(w, pp.clone())?;
        match part {
            CardPart::Art => {
                for art in [descendant::<VesselArtBig>(w, c), descendant::<VesselArtSmall>(w, c)].into_iter().flatten()
                {
                    if let Some(p) = point_in(w, art, 0.5, 0.5) {
                        return Some(p);
                    }
                }
                None
            }
            CardPart::Title => {
                let header = w.get::<Children>(c)?.iter().next()?;
                point_in(w, header, 0.2, 0.5)
            }
            CardPart::Zone => {
                let z = descendant::<VesselIngredientZone>(w, c)?;
                point_in(w, z, 0.5, 0.8)
            }
            CardPart::CatalystSlot => {
                let z = descendant::<VesselCatalystZone>(w, c)?;
                point_in(w, z, 0.5, 0.5)
            }
            CardPart::React => {
                let b = descendant::<VesselReactButton>(w, c)?;
                point_in(w, b, 0.5, 0.5)
            }
            CardPart::Clear => {
                let b = descendant::<VesselClearButton>(w, c)?;
                point_in(w, b, 0.5, 0.5)
            }
            CardPart::Close => {
                let b = descendant::<VesselDeleteButton>(w, c)?;
                point_in(w, b, 0.5, 0.5)
            }
            CardPart::InPort => {
                let b = descendant::<InputPort>(w, c)?;
                point_in(w, b, 0.5, 0.5)
            }
            CardPart::OutPort => {
                let b = descendant::<OutputPort>(w, c)?;
                point_in(w, b, 0.5, 0.5)
            }
            CardPart::FirstChip => {
                let z = descendant::<VesselIngredientZone>(w, c)?;
                let chip = w.get::<Children>(z)?.iter().find(|e| w.get::<Ingredient>(*e).is_some())?;
                point_in(w, chip, 0.6, 0.5)
            }
        }
    })
}

fn marked<C: Component>(name: &str) -> Target {
    target(name.to_string(), |w| {
        let e = first::<C>(w, |_| true)?;
        point_in(w, e, 0.5, 0.5)
    })
}

/// The Tech Tree's built graph steps and list rows.
fn tech_built(w: &mut World) -> (usize, usize) {
    let steps = w.query::<&TechNodeButton>().iter(w).count();
    let rows = w.query::<&crate::ui::tech_tree::TechListEntry>().iter(w).count();
    (steps, rows)
}

/// Scroll the Tech Tree's graph to a fraction of its size.
fn scroll_tech_graph(w: &mut World, at: Vec2) {
    let size = w.resource::<crate::ui::tech_tree::TechLayout>().size();
    for (m, mut sp) in w.query::<(&TechScrollable, &mut ScrollPosition)>().iter_mut(w) {
        if m.graph {
            sp.0 = size * at;
        }
    }
}

/// Every step whose place overlaps the graph's view is built.
fn tech_view_complete(w: &mut World) -> Result<(), String> {
    let view = w
        .query::<(&TechScrollable, &ComputedNode, &ScrollPosition)>()
        .iter(w)
        .find(|(m, _, _)| m.graph)
        .map(|(_, cn, sp)| Rect::from_corners(sp.0, sp.0 + cn.size * cn.inverse_scale_factor()))
        .ok_or("no graph view")?;
    let want = w.resource::<crate::ui::tech_tree::TechLayout>().steps_in(view);
    let built: std::collections::HashSet<u32> = w.query::<&TechNodeButton>().iter(w).map(|b| b.0).collect();
    let missing: Vec<u32> = want.iter().copied().filter(|id| !built.contains(id)).collect();
    if missing.is_empty() {
        Ok(())
    } else {
        Err(format!("{} of the {} steps in view not built (view {view:?})", missing.len(), want.len()))
    }
}

/// How many steps the tech tree's needs check looks at.
const TECH_SAMPLES: usize = 8;

/// A step the tech tree checks pick to select: the six with the most needs, then the first
/// and the last step of the tree.
fn sampled_step(w: &mut World, i: usize) -> Option<u32> {
    let mut by_needs: Vec<(usize, u32)> = w.resource::<TechLinks>().needs.iter().map(|(&k, v)| (v.len(), k)).collect();
    by_needs.sort_by(|a, b| b.cmp(a));
    let db = w.resource::<RecipeDatabase>();
    let mut picks: Vec<u32> = by_needs.iter().take(TECH_SAMPLES - 2).map(|&(_, k)| k).collect();
    picks.extend(db.authored.first().map(|r| r.id));
    picks.extend(db.authored.last().map(|r| r.id));
    picks.get(i).copied()
}

/// The selected step shows everything it needs: a selection line for each of its links, a
/// chip for each need in the detail bar, and a badge counting the needs with no overview line.
fn needs_shown(w: &mut World, i: usize) -> Result<(), String> {
    let Some(step) = sampled_step(w, i) else { return Ok(()) };
    let links = w.resource::<TechLinks>();
    let touching = links.all.iter().filter(|(a, b)| *a == step || *b == step).count();
    let needs = links.needs.get(&step).cloned().unwrap_or_default();
    let undrawn = needs.iter().filter(|n| !n.drawn).count();
    let segments = w.query_filtered::<(), With<SelectionLink>>().iter(w).count();
    let chips = w.query::<&TechNeedButton>().iter(w).count();
    let badge = w.query::<&TechNeedBadge>().iter(w).find(|b| b.step == step).map(|b| b.count);
    let mut wrong = Vec::new();
    if segments != touching * 3 {
        wrong.push(format!("{segments} line segments for {touching} links"));
    }
    if chips != needs.len() {
        wrong.push(format!("{chips} need chips for {} needs", needs.len()));
    }
    if badge.unwrap_or(0) != undrawn {
        wrong.push(format!("badge {badge:?} for {undrawn} needs without a line"));
    }
    match wrong.is_empty() {
        true => Ok(()),
        false => Err(format!("step {step}: {}", wrong.join("; "))),
    }
}

/// The step a tapped need should lead to.
#[derive(Resource)]
struct ExpectedStep(Option<u32>);

fn sidebar_button(p: ProcessType) -> Target {
    target(format!("the {} button in the vessel list", vessel_name(&p)), move |w| {
        let e = first::<ProcessButton>(w, |b| b.process == p)?;
        point_in(w, e, 0.5, 0.5)
    })
}

fn nav(v: View) -> Target {
    target(format!("the {v:?} tab"), move |w| {
        let e = first::<NavTab>(w, |t| t.0 == v)?;
        point_in(w, e, 0.5, 0.5)
    })
}

fn bench_spot() -> Target {
    target("an empty spot on the bench", |w| {
        let e = first::<ReactionCanvasRoot>(w, |_| true)?;
        point_in(w, e, 0.85, 0.8)
    })
}

// ---------------------------------------------------------------------------------------
// Setting the stage (direct, so each check starts from the same place)
// ---------------------------------------------------------------------------------------
/// Close everything, clear the bench and the selection, default settings.
fn fresh(world: &mut World) {
    world.resource_mut::<CodexState>().open = false;
    world.resource_mut::<ReactionLibState>().open = false;
    world.resource_mut::<ReactionLibState>().search.clear();
    world.resource_mut::<TechTreeState>().open = false;
    world.resource_mut::<SettingsUi>().open = false;
    world.resource_mut::<CreditsUi>().open = false;
    *world.resource_mut::<KeyFocus>() = KeyFocus::default();
    world.resource_mut::<SelectedSubstance>().0 = None;
    world.resource_mut::<crate::ui::detail_panel::LastTap>().0 = None;
    world.resource_mut::<crate::systems::drag_drop::ActiveVessel>().0 = None;
    world.resource_mut::<crate::ui::hint::HintState>().stop();
    *world.resource_mut::<crate::ui::inventory::ShelfSearch>() = Default::default();
    world.resource_mut::<crate::ui::toasts::JournalUi>().open = false;
    *world.resource_mut::<InvCategory>() = InvCategory::All;
    {
        let mut f = world.resource_mut::<CodexFilter>();
        f.category = InvCategory::All;
        f.search.clear();
    }
    // the tour and the next-step card stay out of the way unless a check wants them
    *world.resource_mut::<Settings>() =
        Settings { reaction_speed: 4.0, tour_done: true, next_step: false, ..Settings::default() };
    world.resource_mut::<Coach>().step = CoachStep::Off;
    world.resource_mut::<LinkDragState>().0 = None;
    let cards: Vec<Entity> = world.query_filtered::<Entity, With<VesselCard>>().iter(world).collect();
    for c in cards {
        world.despawn(c);
    }
    let links: Vec<Entity> = world.query_filtered::<Entity, With<ReactionLink>>().iter(world).collect();
    for l in links {
        world.despawn(l);
    }
    if let Ok(mut n) = world.query_filtered::<&mut Node, With<CanvasScrollingPane>>().single_mut(world) {
        n.left = Val::Px(0.0);
        n.top = Val::Px(0.0);
    }
    world.resource_mut::<crate::systems::drag_drop::BenchZoom>().0 = 1.0;
    world.resource_mut::<crate::ui::main_menu::MainMenu>().hide();
    for mut sp in
        world.query_filtered::<&mut ScrollPosition, Or<(With<VesselSidebar>, With<InventoryScroll>)>>().iter_mut(world)
    {
        sp.0 = Vec2::ZERO;
    }
    world.resource_mut::<Scratch>().0.clear();
}

/// Back to the starting kit, the first two vessels, no milestones fired.
fn new_game(world: &mut World) {
    world.resource_scope(|world, db: Mut<RecipeDatabase>| {
        world.resource_scope(|world, mut fired: Mut<FiredMilestones>| {
            world.resource_scope(|world, mut unlocks: Mut<ProcessUnlocks>| {
                let mut progress = world.resource_mut::<PlayerProgress>();
                reset_progress(&mut progress, &mut unlocks, &mut fired, &db);
            });
        });
    });
}

/// Put a vessel on the bench in slot `slot` (directly, not through the sidebar).
fn place(world: &mut World, p: ProcessType, slot: usize) {
    world.resource_mut::<ProcessUnlocks>().0.insert(p.clone());
    let Some(pane) = world.query_filtered::<Entity, With<CanvasScrollingPane>>().iter(world).next() else { return };
    let fonts = world.resource::<UiFonts>().clone();
    let assets = world.resource::<AssetServer>().clone();
    let mut queue = CommandQueue::default();
    {
        let mut commands = Commands::new(&mut queue, world);
        let pos = Vec2::new(24.0 + slot as f32 * (VESSEL_W + 28.0), 24.0);
        spawn_vessel_card(&mut commands, pane, &p, vessel_name(&p), pos, &fonts, &assets);
    }
    queue.apply(world);
}

fn discover(world: &mut World, names: &[&str]) {
    let ids: Vec<u32> = names.iter().filter_map(|n| sub_id(world, n)).collect();
    let mut progress = world.resource_mut::<PlayerProgress>();
    for id in ids {
        progress.discover(id);
    }
}

fn discover_everything(world: &mut World) {
    let canon: Vec<u32> = world.resource::<RecipeDatabase>().canon.iter().copied().collect();
    let mut progress = world.resource_mut::<PlayerProgress>();
    for id in canon {
        progress.discover(id);
    }
}

// ---------------------------------------------------------------------------------------
// Reading the outcome
// ---------------------------------------------------------------------------------------
fn chips(world: &mut World, p: ProcessType) -> Vec<String> {
    let Some(c) = card(world, p) else { return vec![] };
    world
        .query::<(&Ingredient, &InVessel)>()
        .iter(world)
        .filter(|(_, v)| v.0 == c)
        .map(|(i, _)| i.name.clone())
        .collect()
}

fn catalysts(world: &mut World, p: ProcessType) -> Vec<String> {
    let Some(c) = card(world, p) else { return vec![] };
    world
        .query::<(&Ingredient, &InCatalystZone)>()
        .iter(world)
        .filter(|(_, v)| v.0 == c)
        .map(|(i, _)| i.name.clone())
        .collect()
}

fn all_chips(world: &mut World) -> usize {
    world.query_filtered::<(), Or<(With<InVessel>, With<InCatalystZone>)>>().iter(world).count()
}

fn left_top(world: &mut World, e: Entity) -> Option<Vec2> {
    let n = world.get::<Node>(e)?;
    match (n.left, n.top) {
        (Val::Px(l), Val::Px(t)) => Some(Vec2::new(l, t)),
        _ => None,
    }
}

fn verify(f: impl Fn(&mut World) -> Result<(), String> + Send + Sync + 'static) -> Verify {
    Box::new(f)
}

fn has_chip(p: ProcessType, name: &'static str) -> Verify {
    verify(move |w| {
        let got = chips(w, p.clone());
        if got.iter().any(|c| c == name) {
            Ok(())
        } else {
            Err(format!("{} holds {:?}, not {}", vessel_name(&p), got, name))
        }
    })
}

fn chip_ids(world: &mut World, p: ProcessType) -> Vec<u32> {
    let Some(c) = card(world, p) else { return vec![] };
    world.query::<(&Ingredient, &InVessel)>().iter(world).filter(|(_, v)| v.0 == c).map(|(i, _)| i.id).collect()
}

/// Every one of `ids` is in the vessel.
fn has_ids(p: ProcessType, ids: Vec<u32>, what: String) -> Verify {
    verify(move |w| {
        let got = chip_ids(w, p.clone());
        let missing: Vec<u32> = ids.iter().filter(|i| !got.contains(i)).copied().collect();
        if missing.is_empty() {
            Ok(())
        } else {
            Err(format!("{} is missing {} (ids {:?}; holds {:?})", vessel_name(&p), what, missing, got))
        }
    })
}

fn no_ghosts() -> Verify {
    verify(|w| {
        let n = w.query_filtered::<(), With<DragGhostNode>>().iter(w).count();
        if n == 0 {
            Ok(())
        } else {
            Err(format!("{n} floating drag copies left on screen"))
        }
    })
}

fn unlock_all(world: &mut World) {
    let mut u = world.resource_mut::<ProcessUnlocks>();
    for v in VESSELS {
        u.0.insert(v.process.clone());
    }
}

fn chip_count(p: ProcessType, n: usize) -> Verify {
    verify(move |w| {
        let got = chips(w, p.clone());
        if got.len() == n {
            Ok(())
        } else {
            Err(format!("{} holds {:?}, expected {} item(s)", vessel_name(&p), got, n))
        }
    })
}

fn selected_is(name: Option<&'static str>) -> Verify {
    verify(move |w| {
        let want = name.and_then(|n| sub_id(w, n));
        let got = w.resource::<SelectedSubstance>().0;
        if got == want {
            Ok(())
        } else {
            Err(format!("selection is {:?}, expected {:?}", got, name))
        }
    })
}

fn state(name: &'static str, f: impl Fn(&World) -> bool + Send + Sync + 'static) -> Verify {
    verify(move |w| if f(w) { Ok(()) } else { Err(format!("expected: {name}")) })
}

/// The tooltip is up and its title starts with `want`.
fn tooltip_says(want: &'static str) -> Verify {
    verify(move |w| {
        let shown = w
            .query_filtered::<&Visibility, With<TooltipNode>>()
            .iter(w)
            .next()
            .is_some_and(|v| *v != Visibility::Hidden);
        let title =
            w.query_filtered::<&Text, With<TooltipTitle>>().iter(w).next().map(|t| t.0.clone()).unwrap_or_default();
        if shown && title.starts_with(want) {
            Ok(())
        } else {
            Err(format!("tooltip shown={shown}, title {title:?}, expected {want:?}"))
        }
    })
}

/// A pop-up on screen (or queued this frame) starts with `want`.
fn toast_says(want: &'static str) -> Verify {
    verify(move |w| {
        let mut seen: Vec<String> = w.resource::<Toasts>().0.iter().map(|(_, t)| t.clone()).collect();
        let stack: Vec<Entity> = w.query_filtered::<Entity, With<crate::ui::toasts::ToastStack>>().iter(w).collect();
        for s in stack {
            let mut queue = VecDeque::from([s]);
            while let Some(e) = queue.pop_front() {
                if let Some(t) = w.get::<Text>(e) {
                    seen.push(t.0.clone());
                }
                if let Some(ch) = w.get::<Children>(e) {
                    queue.extend(ch.iter());
                }
            }
        }
        if seen.iter().any(|t| t.starts_with(want)) {
            Ok(())
        } else {
            Err(format!("no pop-up starting {want:?}; showing {seen:?}"))
        }
    })
}

fn tooltip_hidden() -> Verify {
    verify(|w| {
        let shown = w
            .query_filtered::<&Visibility, With<TooltipNode>>()
            .iter(w)
            .next()
            .is_some_and(|v| *v != Visibility::Hidden);
        if shown {
            Err("a tooltip is showing".into())
        } else {
            Ok(())
        }
    })
}

fn coach_at(want: CoachStep) -> Verify {
    verify(move |w| {
        let got = w.resource::<Coach>().step;
        if got != want {
            return Err(format!("the tour is at {got:?}, expected {want:?}"));
        }
        let shown = w
            .query_filtered::<&Visibility, With<CoachBubble>>()
            .iter(w)
            .next()
            .is_some_and(|v| *v != Visibility::Hidden);
        if want != CoachStep::Off && !shown {
            Err(format!("the {want:?} coach mark is not showing"))
        } else {
            Ok(())
        }
    })
}

/// Scroll a list far past its end, then back a notch: it must move at once (no dead zone
/// left over from the overshoot) and never sit past its limit.
fn overscroll_check<M: Component>(area: &'static str, name: &'static str, list: &'static str, prep: Vec<Op>) -> Check {
    let read = |w: &mut World| -> Option<(f32, f32)> {
        let (cn, sp) = w.query_filtered::<(&ComputedNode, &ScrollPosition), With<M>>().iter(w).next()?;
        Some((sp.0.y, scroll_max(cn).y))
    };
    let mut ops = prep;
    // far past the end whatever the list's length: 4,000 lines is about 190,000 px, ten times
    // the full shelf
    ops.push(Op::Wheel(marked::<M>(list), -4000.0));
    ops.push(Op::Until(
        verify(move |w| {
            let (y, max) = read(w).ok_or("no list")?;
            if max <= 1.0 {
                return Err(format!("the list is too short to scroll (limit {max})"));
            }
            if (y - max).abs() < 1.0 {
                Ok(())
            } else {
                Err(format!("at {y} of {max} after scrolling far past the end"))
            }
        }),
        40,
    ));
    ops.push(setup(move |w| {
        if let Some((y, _)) = read(w) {
            w.resource_mut::<Scratch>().0.insert("y", y);
        }
    }));
    ops.push(Op::Wheel(marked::<M>(list), 1.0));
    ops.push(Op::Until(
        verify(move |w| {
            let (y, _) = read(w).ok_or("no list")?;
            let before = w.resource::<Scratch>().0.get("y").copied().unwrap_or(0.0);
            if y < before - 1.0 {
                Ok(())
            } else {
                Err(format!("one notch back moved it from {before} to {y}: a dead zone"))
            }
        }),
        20,
    ));
    check(area, name, ops)
}

// ---------------------------------------------------------------------------------------
// The checks
// ---------------------------------------------------------------------------------------
fn check(area: &'static str, name: &'static str, mut ops: Vec<Op>) -> Check {
    ops.insert(0, Op::Do(Box::new(fresh)));
    ops.insert(1, Op::Wait(3));
    Check { area, name, ops }
}

fn setup(f: impl Fn(&mut World) + Send + Sync + 'static) -> Op {
    Op::Do(Box::new(f))
}

const WAIT: u32 = 240;

pub fn all_checks(world: &mut World) -> Vec<Check> {
    use CardPart::*;
    use ProcessType::{Catalysis, Heat, Mix, Smelting};
    let mut v = Vec::new();

    // --- the vessel list ---
    v.push(check(
        "Lab: vessels",
        "Clicking an unlocked vessel puts it on the bench",
        vec![
            setup(new_game),
            Op::Wait(3),
            Op::Click(sidebar_button(Mix)),
            Op::Until(
                verify(|w| {
                    let n = w.query::<&ProcessVessel>().iter(w).filter(|p| p.process == Mix).count();
                    if n == 1 {
                        Ok(())
                    } else {
                        Err(format!("{n} Mortars on the bench"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Lab: vessels",
        "Clicking a locked vessel places nothing, and says what unlocks it and why",
        vec![
            setup(new_game),
            Op::Wait(3),
            Op::Click(sidebar_button(Smelting)),
            Op::Until(toast_says("The Bloomery unlocks with Copper. Copper smelted"), 30),
            Op::Expect(verify(|w| {
                if card(w, Smelting).is_none() {
                    Ok(())
                } else {
                    Err("a locked Bloomery was placed".into())
                }
            })),
        ],
    ));
    v.push(check(
        "Lab: vessels",
        "The vessel list scrolls with the wheel",
        vec![
            Op::Wheel(marked::<VesselSidebar>("the vessel list"), -3.0),
            Op::Until(
                verify(|w| {
                    let y = w
                        .query_filtered::<&ScrollPosition, With<VesselSidebar>>()
                        .iter(w)
                        .next()
                        .map(|s| s.0.y)
                        .unwrap_or(0.0);
                    if y > 0.0 {
                        Ok(())
                    } else {
                        Err("the vessel list did not scroll".into())
                    }
                }),
                30,
            ),
        ],
    ));

    // --- selecting on the shelf ---
    v.push(check(
        "Lab: shelf",
        "Clicking a tile selects it (and opens nothing)",
        vec![
            Op::Click(tile("Oxygen")),
            Op::Until(selected_is(Some("Oxygen")), 30),
            Op::Expect(state("no library page opened", |w| !w.resource::<CodexState>().open)),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "Clicking another tile moves the selection",
        vec![Op::Click(tile("Oxygen")), Op::Click(tile("Water")), Op::Until(selected_is(Some("Water")), 30)],
    ));
    v.push(check(
        "Lab: shelf",
        "Clicking the selected tile again lets go",
        vec![
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            // a moment apart: two quick taps are a double-tap
            Op::Pause(crate::ui::detail_panel::DOUBLE_TAP + 0.15),
            Op::Click(tile("Water")),
            Op::Until(selected_is(None), 30),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "The Library button opens the selection's page",
        vec![
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            Op::Click(marked::<SelectionOpenButton>("the selection's Library button")),
            Op::Until(
                verify(|w| {
                    let want = sub_id(w, "Water");
                    let c = w.resource::<CodexState>();
                    if c.open && c.selected == want {
                        Ok(())
                    } else {
                        Err(format!("library open={} on {:?}", c.open, c.selected))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "The x and Esc let go of the selection",
        vec![
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            Op::Click(marked::<SelectionClearButton>("the selection's x")),
            Op::Until(selected_is(None), 30),
            Op::Click(tile("Oxygen")),
            Op::Until(selected_is(Some("Oxygen")), 30),
            Op::Key(KeyCode::Escape),
            Op::Until(selected_is(None), 30),
            Op::Expect(state("Esc only let go (settings stayed shut)", |w| !w.resource::<SettingsUi>().open)),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "Category pills filter the shelf",
        vec![
            Op::Click(target("the Elements pill", |w| {
                let e = first::<CategoryTab>(w, |t| t.0 == InvCategory::Elements)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    if *w.resource::<InvCategory>() != InvCategory::Elements {
                        return Err("the filter did not change".into());
                    }
                    let tiles: Vec<String> =
                        w.query_filtered::<&Ingredient, With<ShelfTile>>().iter(w).map(|i| i.formula.clone()).collect();
                    if tiles.is_empty() {
                        return Err("the shelf is empty".into());
                    }
                    match tiles.iter().find(|f| !is_element_formula(f)) {
                        Some(f) => Err(format!("{f} is on the Elements shelf")),
                        None => Ok(()),
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "The shelf scrolls with the wheel",
        vec![
            setup(discover_everything),
            Op::Wait(20),
            Op::Wheel(marked::<InventoryScroll>("the shelf"), -3.0),
            Op::Until(
                verify(|w| {
                    let y = w
                        .query_filtered::<&ScrollPosition, With<InventoryScroll>>()
                        .iter(w)
                        .next()
                        .map(|s| s.0.y)
                        .unwrap_or(0.0);
                    if y > 0.0 {
                        Ok(())
                    } else {
                        Err("the shelf did not scroll".into())
                    }
                }),
                30,
            ),
            setup(new_game),
            Op::Wait(10),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "With everything found, only the tiles near the view are built",
        vec![
            setup(discover_everything),
            Op::Wait(20),
            Op::Until(
                verify(|w| {
                    let total = w.resource::<PlayerProgress>().discovered.len();
                    let built = w.query_filtered::<(), With<ShelfTile>>().iter(w).count();
                    if total < 400 {
                        Err(format!("only {total} substances: too few to tell"))
                    } else if built == 0 {
                        Err("no tiles built".into())
                    } else if built * 4 > total {
                        Err(format!("{built} of {total} tiles built"))
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            setup(new_game),
            Op::Wait(10),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "Scrolled to the end, the shelf builds the last tiles and lets go of the first",
        vec![
            setup(discover_everything),
            Op::Wait(20),
            setup(|w| {
                for mut sp in w.query_filtered::<&mut ScrollPosition, With<InventoryScroll>>().iter_mut(w) {
                    sp.0.y = 1.0e7;
                }
            }),
            Op::Until(
                verify(|w| {
                    let ends = w
                        .query_filtered::<&VirtualList, With<InventoryContent>>()
                        .iter(w)
                        .next()
                        .and_then(|l| Some((*l.ids().first()?, *l.ids().last()?)));
                    let (first, last) = ends.ok_or("the shelf is empty")?;
                    let built: Vec<u32> =
                        w.query_filtered::<&Ingredient, With<ShelfTile>>().iter(w).map(|i| i.id).collect();
                    if !built.contains(&last) {
                        Err("the last tile is not built".into())
                    } else if built.contains(&first) {
                        Err("the first tile is still built".into())
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            setup(new_game),
            Op::Wait(10),
        ],
    ));

    // --- putting substances in ---
    for (part, name) in [
        (Art, "Dropping a tile on a vessel's picture puts it in"),
        (Title, "Dropping a tile on a vessel's title puts it in"),
        (Zone, "Dropping a tile on a vessel's contents puts it in"),
        (React, "Dropping a tile on a vessel's React button puts it in"),
    ] {
        v.push(check(
            "Lab: drag and drop",
            name,
            vec![
                setup(|w| place(w, Mix, 0)),
                Op::Wait(5),
                Op::Drag(tile("Oxygen"), card_part(Mix, part)),
                Op::Until(has_chip(Mix, "Oxygen"), 30),
                Op::Expect(chip_count(Mix, 1)),
            ],
        ));
    }
    v.push(check(
        "Lab: drag and drop",
        "Dropping a tile on a substance already inside adds it",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Zone)),
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            Op::Drag(tile("Water"), card_part(Mix, FirstChip)),
            Op::Until(has_chip(Mix, "Water"), 30),
            Op::Expect(chip_count(Mix, 2)),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "Dropping a tile on the empty bench does nothing",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), bench_spot()),
            Op::Wait(5),
            Op::Expect(verify(|w| if all_chips(w) == 0 { Ok(()) } else { Err("a substance landed somewhere".into()) })),
            Op::Expect(verify(|w| {
                let n = w.query_filtered::<(), With<DragGhostNode>>().iter(w).count();
                if n == 0 {
                    Ok(())
                } else {
                    Err(format!("{n} drag ghost(s) left behind"))
                }
            })),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "Dropping a tile back on the shelf does nothing",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), tile("Water")),
            Op::Wait(5),
            Op::Expect(verify(|w| if all_chips(w) == 0 { Ok(()) } else { Err("a substance landed somewhere".into()) })),
            Op::Expect(state("no library page opened", |w| !w.resource::<CodexState>().open)),
            Op::Expect(selected_is(None)),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "The Catalyst Bed's slot takes a catalyst and swaps it",
        vec![
            setup(|w| place(w, Catalysis, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Catalysis, CatalystSlot)),
            Op::Until(
                verify(|w| {
                    let c = catalysts(w, Catalysis);
                    if c == ["Oxygen"] {
                        Ok(())
                    } else {
                        Err(format!("catalyst slot holds {c:?}"))
                    }
                }),
                30,
            ),
            Op::Drag(tile("Water"), card_part(Catalysis, CatalystSlot)),
            Op::Until(
                verify(|w| {
                    let c = catalysts(w, Catalysis);
                    if c == ["Water"] {
                        Ok(())
                    } else {
                        Err(format!("catalyst slot holds {c:?} after the swap"))
                    }
                }),
                30,
            ),
            Op::Expect(chip_count(Catalysis, 0)),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "A discovery in the middle of a drag doesn't break it",
        vec![
            setup(new_game),
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Press(tile("Oxygen")),
            Op::MoveTo(bench_spot()),
            // a reaction finishing elsewhere: the shelf wants to rebuild under the drag
            setup(|w| discover(w, &["Charcoal"])),
            Op::Wait(6),
            Op::MoveTo(card_part(Mix, Art)),
            Op::Release,
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            Op::Expect(no_ghosts()),
            Op::Until(
                verify(|w| {
                    let shelf_has =
                        w.query_filtered::<&Ingredient, With<ShelfTile>>().iter(w).any(|i| i.name == "Charcoal");
                    if shelf_has {
                        Ok(())
                    } else {
                        Err("the shelf never caught up with the discovery".into())
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "Nothing from a drag shows over the other views",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), bench_spot()),
            Op::Drag(tile("Water"), card_part(Mix, Art)),
            Op::Click(nav(View::Substances)),
            Op::Wait(3),
            Op::Expect(no_ghosts()),
            Op::Click(nav(View::TechTree)),
            Op::Wait(3),
            Op::Expect(no_ghosts()),
            Op::Expect(verify(|w| {
                let lifted = w.query::<&GlobalZIndex>().iter(w).filter(|z| z.0 > 0 && z.0 < 500).count();
                if lifted == 0 {
                    Ok(())
                } else {
                    Err(format!("{lifted} item(s) still lifted above the bench"))
                }
            })),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "A stray floating copy is swept away",
        vec![
            setup(|w| {
                w.spawn((
                    DragGhostNode { owner: Entity::PLACEHOLDER },
                    Node { width: Val::Px(40.0), height: Val::Px(20.0), ..default() },
                    GlobalZIndex(1000),
                ));
            }),
            Op::Wait(3),
            Op::Expect(no_ghosts()),
        ],
    ));
    v.push(check(
        "Lab: click to place",
        "With a tile selected, clicking a vessel puts it in",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            Op::Click(card_part(Mix, Art)),
            Op::Until(has_chip(Mix, "Water"), 30),
            Op::Click(card_part(Mix, Title)),
            Op::Until(chip_count(Mix, 2), 30),
        ],
    ));
    v.push(check(
        "Lab: click to place",
        "Clicking a vessel's buttons does not put the selection in",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            Op::Click(card_part(Mix, React)),
            Op::Click(card_part(Mix, Clear)),
            Op::Wait(5),
            Op::Expect(chip_count(Mix, 0)),
        ],
    ));

    // --- reacting ---
    v.push(check(
        "Lab: reactions",
        "React runs a reaction and its products appear",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            Op::Wait(5),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            Op::Click(card_part(Heat, React)),
            Op::Until(has_chip(Heat, "Charcoal"), WAIT),
            Op::Expect(verify(|w| {
                let id = sub_id(w, "Charcoal").ok_or("no Charcoal")?;
                if w.resource::<PlayerProgress>().discovered.contains(&id) {
                    Ok(())
                } else {
                    Err("Charcoal was not discovered".into())
                }
            })),
        ],
    ));
    v.push(check(
        "Lab: reactions",
        "A mix that does not react says so",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Art)),
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            Op::Click(card_part(Mix, React)),
            Op::Until(
                verify(|w| {
                    let c = card(w, Mix).ok_or("no Mortar")?;
                    let status = w
                        .query_filtered::<(&Text, &ChildOf), With<EquationText>>()
                        .iter(w)
                        .find(|(_, p)| p.parent() == c)
                        .map(|(t, _)| t.0.clone())
                        .unwrap_or_default();
                    if !status.is_empty() && !status.starts_with("Drop") {
                        Ok(())
                    } else {
                        Err(format!("status reads {status:?}"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Lab: reactions",
        "Clear empties a vessel",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Zone)),
            Op::Drag(tile("Water"), card_part(Mix, Zone)),
            Op::Until(chip_count(Mix, 2), 30),
            Op::Click(card_part(Mix, Clear)),
            Op::Until(chip_count(Mix, 0), 30),
        ],
    ));

    // --- moving things ---
    for (part, name) in
        [(Art, "Dragging a vessel by its picture moves it"), (Title, "Dragging a vessel by its title moves it")]
    {
        v.push(check(
            "Lab: moving",
            name,
            vec![
                setup(|w| place(w, Mix, 0)),
                Op::Wait(5),
                setup(|w| {
                    let c = card(w, Mix).unwrap();
                    let p = left_top(w, c).unwrap_or_default();
                    w.resource_mut::<Scratch>().0.extend([("x", p.x), ("y", p.y)]);
                }),
                Op::DragBy(card_part(Mix, part), Vec2::new(160.0, 80.0)),
                Op::Until(
                    verify(|w| {
                        let c = card(w, Mix).ok_or("the Mortar vanished")?;
                        let p = left_top(w, c).ok_or("no position")?;
                        let s = w.resource::<Scratch>().0.clone();
                        let scale = w.resource::<UiScale>().0;
                        let d = p - Vec2::new(s["x"], s["y"]);
                        let want = Vec2::new(160.0, 80.0) / scale;
                        if (d - want).abs().max_element() <= 20.0 {
                            Ok(())
                        } else {
                            Err(format!("moved by {d}, expected about {want}"))
                        }
                    }),
                    30,
                ),
            ],
        ));
    }
    v.push(check(
        "Lab: moving",
        "Dragging the empty bench pans it",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::DragBy(bench_spot(), Vec2::new(-200.0, -100.0)),
            Op::Until(
                verify(|w| {
                    let pane =
                        w.query_filtered::<Entity, With<CanvasScrollingPane>>().iter(w).next().ok_or("no pane")?;
                    let p = left_top(w, pane).ok_or("no position")?;
                    if (p - Vec2::new(-200.0, -100.0)).abs().max_element() <= 2.0 {
                        Ok(())
                    } else {
                        Err(format!("bench offset {p}, expected (-200, -100)"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Lab: moving",
        "At 125% interface size, drops and moves still line up",
        vec![
            setup(|w| w.resource_mut::<Settings>().ui_scale = 1.25),
            Op::Wait(5),
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Art)),
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            setup(|w| {
                let c = card(w, Mix).unwrap();
                let p = left_top(w, c).unwrap_or_default();
                w.resource_mut::<Scratch>().0.extend([("x", p.x), ("y", p.y)]);
            }),
            Op::DragBy(card_part(Mix, Title), Vec2::new(250.0, 0.0)),
            Op::Until(
                verify(|w| {
                    let c = card(w, Mix).ok_or("the Mortar vanished")?;
                    let p = left_top(w, c).ok_or("no position")?;
                    let s = w.resource::<Scratch>().0.clone();
                    let d = p.x - s["x"];
                    if (d - 200.0).abs() <= 20.0 {
                        Ok(())
                    } else {
                        Err(format!("a 250 px drag moved it {d} UI px, expected 200"))
                    }
                }),
                30,
            ),
        ],
    ));

    // --- linking ---
    v.push(check(
        "Lab: links",
        "Dragging an output port onto an input port links two vessels",
        vec![
            setup(|w| place(w, Mix, 0)),
            setup(|w| place(w, Heat, 1)),
            Op::Wait(5),
            Op::Drag(card_part(Mix, OutPort), card_part(Heat, InPort)),
            Op::Until(
                verify(|w| {
                    let (m, h) = (card(w, Mix), card(w, Heat));
                    let ok =
                        w.query::<&ReactionLink>().iter(w).any(|l| Some(l.from_vessel) == m && Some(l.to_vessel) == h);
                    if ok {
                        Ok(())
                    } else {
                        Err("no Mortar -> Fire link".into())
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Lab: links",
        "Products travel along a link",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            setup(|w| place(w, Mix, 1)),
            Op::Wait(5),
            Op::Drag(card_part(Heat, OutPort), card_part(Mix, InPort)),
            Op::Until(
                verify(
                    |w| if w.query::<&ReactionLink>().iter(w).count() == 1 { Ok(()) } else { Err("no link".into()) },
                ),
                30,
            ),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            Op::Click(card_part(Heat, React)),
            Op::Until(has_chip(Mix, "Charcoal"), WAIT),
        ],
    ));
    v.push(check(
        "Lab: links",
        "Removing a vessel removes its links",
        vec![
            setup(|w| place(w, Mix, 0)),
            setup(|w| place(w, Heat, 1)),
            Op::Wait(5),
            Op::Drag(card_part(Mix, OutPort), card_part(Heat, InPort)),
            Op::Until(
                verify(
                    |w| if w.query::<&ReactionLink>().iter(w).count() == 1 { Ok(()) } else { Err("no link".into()) },
                ),
                30,
            ),
            Op::Click(card_part(Heat, Close)),
            Op::Until(
                verify(|w| {
                    let links = w.query::<&ReactionLink>().iter(w).count();
                    if card(w, Heat).is_none() && links == 0 {
                        Ok(())
                    } else {
                        Err(format!("Fire still there or {links} link(s) left"))
                    }
                }),
                30,
            ),
        ],
    ));

    // --- header and views ---
    v.push(check(
        "Header",
        "Each tab opens its view; Lab closes them",
        vec![
            Op::Click(nav(View::Substances)),
            Op::Until(state("Substance Library open", |w| w.resource::<CodexState>().open), 30),
            Op::Click(nav(View::Reactions)),
            Op::Until(
                state("Reaction Library open, Substances closed", |w| {
                    w.resource::<ReactionLibState>().open && !w.resource::<CodexState>().open
                }),
                30,
            ),
            Op::Click(nav(View::TechTree)),
            Op::Until(
                state("Tech Tree open alone", |w| {
                    w.resource::<TechTreeState>().open && !w.resource::<ReactionLibState>().open
                }),
                30,
            ),
            Op::Click(nav(View::Lab)),
            Op::Until(
                state("everything closed", |w| {
                    !w.resource::<TechTreeState>().open
                        && !w.resource::<CodexState>().open
                        && !w.resource::<ReactionLibState>().open
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Header",
        "A click on an open view never reaches the lab behind it",
        vec![
            setup(|w| w.resource_mut::<CodexState>().open = true),
            Op::Wait(5),
            Op::Click(sidebar_button(Mix)),
            Op::Wait(5),
            Op::Expect(verify(|w| {
                if card(w, Mix).is_none() {
                    Ok(())
                } else {
                    Err("the click went through to the vessel list".into())
                }
            })),
        ],
    ));
    v.push(check(
        "Header",
        "Esc closes a view",
        vec![
            Op::Click(nav(View::Reactions)),
            Op::Until(state("Reaction Library open", |w| w.resource::<ReactionLibState>().open), 30),
            Op::Key(KeyCode::Escape),
            Op::Until(state("Reaction Library closed", |w| !w.resource::<ReactionLibState>().open), 30),
        ],
    ));

    // --- settings ---
    v.push(check(
        "Settings",
        "The gear opens settings and Esc closes them",
        vec![
            Op::Click(marked::<SettingsButton>("the gear")),
            Op::Until(state("settings open", |w| w.resource::<SettingsUi>().open), 30),
            Op::Key(KeyCode::Escape),
            Op::Until(state("settings closed", |w| !w.resource::<SettingsUi>().open), 30),
        ],
    ));
    v.push(check(
        "Settings",
        "A click inside the dialog keeps it open; the backdrop closes it",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(marked::<SettingsAbout>("the About line")),
            Op::Wait(3),
            Op::Expect(state("settings still open", |w| w.resource::<SettingsUi>().open)),
            Op::Click(target("the backdrop", |_| Some(Vec2::new(24.0, 300.0)))),
            Op::Until(state("settings closed", |w| !w.resource::<SettingsUi>().open), 30),
        ],
    ));
    let step = |f: Field, dir: f32, label: &'static str| {
        target(label, move |w| {
            let e = first::<SettingStep>(w, |s| s.0 == f && s.1 == dir)?;
            point_in(w, e, 0.5, 0.5)
        })
    };
    let toggle = |f: Field, label: &'static str| {
        target(label, move |w| {
            let e = first::<SettingToggle>(w, |s| s.0 == f)?;
            point_in(w, e, 0.5, 0.5)
        })
    };
    v.push(check(
        "Settings",
        "Interface size steps up and down",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(step(Field::UiScale, 1.0, "interface size +")),
            Op::Until(
                verify(|w| {
                    let (s, u) = (w.resource::<Settings>().ui_scale, w.resource::<UiScale>().0);
                    if (s - 1.1).abs() < 0.01 && (u - 1.1).abs() < 0.01 {
                        Ok(())
                    } else {
                        Err(format!("setting {s}, applied {u}"))
                    }
                }),
                30,
            ),
            Op::Click(step(Field::UiScale, -1.0, "interface size -")),
            Op::Until(
                verify(|w| {
                    let u = w.resource::<UiScale>().0;
                    if (u - 1.0).abs() < 0.01 {
                        Ok(())
                    } else {
                        Err(format!("applied {u}"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Settings",
        "Reaction speed steps",
        vec![
            setup(|w| {
                w.resource_mut::<Settings>().reaction_speed = 1.0;
                w.resource_mut::<SettingsUi>().open = true;
            }),
            Op::Wait(5),
            Op::Click(step(Field::ReactionSpeed, 1.0, "reaction speed +")),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<Settings>().reaction_speed;
                    if s > 1.0 {
                        Ok(())
                    } else {
                        Err(format!("speed {s}"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Settings",
        "Names before formulas changes the shelf tiles",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(toggle(Field::NamesFirst, "the names-first switch")),
            Op::Until(
                verify(|w| {
                    if !w.resource::<Settings>().names_first {
                        return Err("the switch did not flip".into());
                    }
                    let water = w
                        .query_filtered::<(Entity, &Ingredient), With<ShelfTile>>()
                        .iter(w)
                        .find(|(_, i)| i.name == "Water")
                        .map(|(e, _)| e)
                        .ok_or("no Water tile")?;
                    let first_text = w
                        .get::<Children>(water)
                        .and_then(|c| c.iter().find_map(|e| w.get::<Text>(e).map(|t| t.0.clone())));
                    if first_text.as_deref() == Some("Water") {
                        Ok(())
                    } else {
                        Err(format!("the Water tile leads with {first_text:?}"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Settings",
        "Notifications off silences the pop-ups",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(toggle(Field::Notifications, "the notifications switch")),
            Op::Until(state("notifications off", |w| !w.resource::<Settings>().notifications), 30),
            setup(|w| w.resource_mut::<Toasts>().push(ToastKind::Hint, "check: this should not show")),
            Op::Wait(5),
            Op::Expect(verify(|w| {
                let shown = w.query::<&Text>().iter(w).filter(|t| t.0.contains("this should not show")).count();
                if shown == 0 {
                    Ok(())
                } else {
                    Err("a pop-up appeared".into())
                }
            })),
        ],
    ));
    v.push(check(
        "Settings",
        "Bench grid off hides the grid",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(toggle(Field::BenchGrid, "the bench grid switch")),
            Op::Until(
                verify(|w| {
                    let hidden =
                        w.query_filtered::<&Visibility, With<BenchGrid>>().iter(w).all(|v| *v == Visibility::Hidden);
                    if hidden && !w.resource::<Settings>().bench_grid {
                        Ok(())
                    } else {
                        Err("the grid is still showing".into())
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Settings",
        "VSync switches the present mode",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(toggle(Field::Vsync, "the VSync switch")),
            Op::Until(
                verify(|w| {
                    let pm = w.query_filtered::<&Window, With<PrimaryWindow>>().iter(w).next().map(|w| w.present_mode);
                    if pm == Some(PresentMode::AutoNoVsync) {
                        Ok(())
                    } else {
                        Err(format!("present mode {pm:?}"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Settings",
        "New game wipes progress only on the second click",
        vec![
            setup(new_game),
            setup(|w| discover(w, &["Charcoal"])),
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(marked::<NewGameButton>("the New game button")),
            Op::Wait(5),
            Op::Expect(verify(|w| {
                let id = sub_id(w, "Charcoal").ok_or("no Charcoal")?;
                if w.resource::<PlayerProgress>().discovered.contains(&id) {
                    Ok(())
                } else {
                    Err("one click already wiped the game".into())
                }
            })),
            Op::Click(marked::<NewGameButton>("the New game button")),
            Op::Until(
                verify(|w| {
                    let id = sub_id(w, "Charcoal").ok_or("no Charcoal")?;
                    if !w.resource::<PlayerProgress>().discovered.contains(&id) {
                        Ok(())
                    } else {
                        Err("the second click did not wipe the game".into())
                    }
                }),
                30,
            ),
        ],
    ));

    // --- Substance Library ---
    let open_codex = |sel: Option<&'static str>| {
        setup(move |w| {
            let id = sel.and_then(|n| sub_id(w, n));
            let mut c = w.resource_mut::<CodexState>();
            c.open = true;
            c.selected = id;
        })
    };
    v.push(check(
        "Substance Library",
        "Category pills filter the list",
        vec![
            open_codex(None),
            Op::Wait(5),
            Op::Click(target("the library's Elements pill", |w| {
                let e = first::<CodexCategoryTab>(w, |t| t.0 == InvCategory::Elements)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    if w.resource::<CodexFilter>().category != InvCategory::Elements {
                        return Err("the filter did not change".into());
                    }
                    let ids: Vec<u32> = w.query::<&CodexEntry>().iter(w).map(|e| e.0).collect();
                    let gd = w.resource::<GameData>().substances.clone();
                    let subs = w.resource::<Assets<Substances>>().get(&gd).ok_or("no substances")?;
                    let bad: Vec<String> = ids
                        .iter()
                        .filter_map(|id| subs.0.get(id))
                        .filter(|s| s.element_info.is_none() && !is_element_formula(&s.formula))
                        .map(|s| s.name.clone())
                        .collect();
                    if ids.is_empty() {
                        Err("the list is empty".into())
                    } else if bad.is_empty() {
                        Ok(())
                    } else {
                        Err(format!("not elements: {bad:?}"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Substance Library",
        "With everything found, the list builds only the rows near the view, and the last ones at the end",
        vec![
            setup(discover_everything),
            open_codex(None),
            Op::Wait(20),
            Op::Until(
                verify(|w| {
                    let total = w.resource::<PlayerProgress>().discovered.len();
                    let rows = w.query::<&CodexEntry>().iter(w).count();
                    if total < 400 {
                        Err(format!("only {total} substances: too few to tell"))
                    } else if rows == 0 || rows * 4 > total {
                        Err(format!("{rows} of {total} rows built"))
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            setup(|w| {
                for (m, mut sp) in w.query::<(&CodexScrollable, &mut ScrollPosition)>().iter_mut(w) {
                    if m.is_left {
                        sp.0.y = 1.0e7;
                    }
                }
            }),
            Op::Until(
                verify(|w| {
                    let last = w
                        .query_filtered::<&VirtualList, With<CodexListContent>>()
                        .iter(w)
                        .next()
                        .and_then(|l| l.ids().last().copied())
                        .ok_or("the list is empty")?;
                    if w.query::<&CodexEntry>().iter(w).any(|e| e.0 == last) {
                        Ok(())
                    } else {
                        Err("the last row is not built".into())
                    }
                }),
                60,
            ),
            setup(new_game),
            Op::Wait(10),
        ],
    ));
    v.push(check(
        "Substance Library",
        "The Coming later pill lists the locked previews of later stages, each with a page",
        vec![
            open_codex(None),
            Op::Wait(5),
            Op::Click(target("the library's Coming later pill", |w| {
                let e = first::<CodexCategoryTab>(w, |t| t.0 == InvCategory::Coming)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    if w.resource::<CodexFilter>().category != InvCategory::Coming {
                        return Err("the filter did not change".into());
                    }
                    let ids: Vec<u32> = w.query::<&CodexEntry>().iter(w).map(|e| e.0).collect();
                    let gd = w.resource::<GameData>().substances.clone();
                    let subs = w.resource::<Assets<Substances>>().get(&gd).ok_or("no substances")?;
                    let bad: Vec<String> = ids
                        .iter()
                        .filter_map(|id| subs.0.get(id))
                        .filter(|s| s.stage.is_none())
                        .map(|s| s.name.clone())
                        .collect();
                    if ids.is_empty() {
                        Err("the list is empty".into())
                    } else if bad.is_empty() {
                        Ok(())
                    } else {
                        Err(format!("not locked previews: {bad:?}"))
                    }
                }),
                60,
            ),
            Op::Click(marked::<CodexEntry>("the first locked preview")),
            Op::Until(
                verify(|w| {
                    let sel = w.resource::<CodexState>().selected.ok_or("nothing selected")?;
                    let gd = w.resource::<GameData>().substances.clone();
                    let subs = w.resource::<Assets<Substances>>().get(&gd).ok_or("no substances")?;
                    match subs.0.get(&sel) {
                        Some(s) if s.stage.is_some() => Ok(()),
                        _ => Err("the selection is not a locked preview".into()),
                    }
                }),
                30,
            ),
            setup(|w| w.resource_mut::<CodexFilter>().category = InvCategory::All),
        ],
    ));
    v.push(check(
        "Substance Library",
        "A page says what industry does with it: tonnage, transport class, handling",
        vec![
            open_codex(Some("Ethanol")),
            Op::Until(
                verify(|w| {
                    let cards = w.query::<&CodexIndustryCard>().iter(w).count();
                    if cards >= 3 {
                        Ok(())
                    } else {
                        Err(format!("{cards} industry cards on Ethanol's page"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Substance Library",
        "Typing searches the list; Backspace undoes it",
        vec![
            open_codex(None),
            Op::Wait(5),
            Op::Key(KeyCode::KeyW),
            Op::Key(KeyCode::KeyA),
            Op::Key(KeyCode::KeyT),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<CodexFilter>().search.clone();
                    let gd = w.resource::<GameData>().substances.clone();
                    let names: Vec<String> = {
                        let ids: Vec<u32> = w.query::<&CodexEntry>().iter(w).map(|e| e.0).collect();
                        let subs = w.resource::<Assets<Substances>>().get(&gd).ok_or("no substances")?;
                        ids.iter().filter_map(|id| subs.0.get(id)).map(|s| s.name.to_lowercase()).collect()
                    };
                    if s != "wat" {
                        Err(format!("search reads {s:?}"))
                    } else if names.is_empty() || names.iter().any(|n| !n.contains("wat")) {
                        Err(format!("list shows {names:?}"))
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            Op::Key(KeyCode::Backspace),
            Op::Key(KeyCode::Backspace),
            Op::Key(KeyCode::Backspace),
            Op::Until(state("search cleared", |w| w.resource::<CodexFilter>().search.is_empty()), 30),
        ],
    ));
    v.push(check(
        "Substance Library",
        "Clicking a row opens its page",
        vec![
            open_codex(None),
            Op::Wait(8),
            Op::Click(target("the Water row", |w| {
                let id = sub_id(w, "Water")?;
                let e = first::<CodexEntry>(w, |c| c.0 == id)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    let want = sub_id(w, "Water");
                    let sel = w.resource::<CodexState>().selected;
                    let page =
                        w.query_filtered::<&Children, With<CodexDetail>>().iter(w).next().map(|c| c.len()).unwrap_or(0);
                    if sel == want && page > 0 {
                        Ok(())
                    } else {
                        Err(format!("selected {sel:?}, page has {page} parts"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Substance Library",
        "A reaction on a page opens it in the Reaction Library",
        vec![
            setup(new_game),
            setup(|w| discover(w, &["Charcoal"])),
            open_codex(Some("Charcoal")),
            Op::Wait(10),
            Op::Click(marked::<CodexReactionLink>("a reaction on Charcoal's page")),
            Op::Until(
                verify(|w| {
                    let r = w.resource::<ReactionLibState>();
                    if r.open && r.selected.is_some() && !w.resource::<CodexState>().open {
                        Ok(())
                    } else {
                        Err(format!("reaction library open={} on {:?}", r.open, r.selected))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Substance Library",
        "The Wikipedia button opens the article",
        vec![
            open_codex(Some("Water")),
            Op::Wait(10),
            Op::Click(marked::<CodexRefLink>("the Wikipedia button")),
            Op::Until(
                verify(|_| {
                    let last = URL_SINK.lock().ok().and_then(|s| s.as_ref().and_then(|v| v.last().cloned()));
                    match last {
                        Some(u) if u.contains("wikipedia.org") => Ok(()),
                        other => Err(format!("opened {other:?}")),
                    }
                }),
                30,
            ),
        ],
    ));

    // --- Reaction Library ---
    let open_rlib = || {
        setup(|w| {
            discover(w, &["Charcoal"]);
            w.resource_mut::<ReactionLibState>().open = true;
        })
    };
    v.push(check(
        "Reaction Library",
        "With everything found, the list builds only the rows near the view, and the last ones at the end",
        vec![
            setup(discover_everything),
            setup(|w| w.resource_mut::<ReactionLibState>().open = true),
            Op::Wait(20),
            Op::Until(
                verify(|w| {
                    let total = w
                        .query_filtered::<&VirtualList, With<ReactionLibListContent>>()
                        .iter(w)
                        .next()
                        .map(|l| l.ids().len())
                        .unwrap_or(0);
                    let rows = w.query::<&ReactionLibEntry>().iter(w).count();
                    if total < 400 {
                        Err(format!("only {total} entries: too few to tell"))
                    } else if rows == 0 || rows * 4 > total {
                        Err(format!("{rows} of {total} rows built"))
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            setup(|w| {
                for (m, mut sp) in w.query::<(&ReactionLibScrollable, &mut ScrollPosition)>().iter_mut(w) {
                    if m.is_left {
                        sp.0.y = 1.0e7;
                    }
                }
            }),
            Op::Until(
                verify(|w| {
                    let last = w
                        .query_filtered::<&VirtualList, With<ReactionLibListContent>>()
                        .iter(w)
                        .next()
                        .and_then(|l| l.ids().last().copied())
                        .ok_or("the list is empty")?;
                    if w.query::<&ReactionLibEntry>().iter(w).any(|e| e.0 == last) {
                        Ok(())
                    } else {
                        Err("the last row is not built".into())
                    }
                }),
                60,
            ),
            setup(new_game),
            Op::Wait(10),
        ],
    ));
    v.push(check(
        "Reaction Library",
        "Typing searches the list",
        vec![
            setup(new_game),
            open_rlib(),
            Op::Wait(8),
            Op::Key(KeyCode::KeyC),
            Op::Key(KeyCode::KeyH),
            Op::Key(KeyCode::KeyA),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<ReactionLibState>().search.clone();
                    let n = w.query::<&ReactionLibEntry>().iter(w).count();
                    if s == "cha" && n >= 1 {
                        Ok(())
                    } else {
                        Err(format!("search {s:?}, {n} rows"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Reaction Library",
        "Clicking a row opens its page",
        vec![
            setup(new_game),
            open_rlib(),
            Op::Wait(8),
            Op::Click(marked::<ReactionLibEntry>("the first reaction row")),
            Op::Until(state("a reaction selected", |w| w.resource::<ReactionLibState>().selected.is_some()), 30),
        ],
    ));
    v.push(check(
        "Reaction Library",
        "A substance card opens its page in the Substance Library",
        vec![
            setup(new_game),
            open_rlib(),
            Op::Wait(8),
            Op::Click(marked::<ReactionLibEntry>("the first reaction row")),
            Op::Wait(8),
            Op::Click(marked::<ReactionLibSubstanceLink>("a reactant card")),
            Op::Until(
                verify(|w| {
                    let c = w.resource::<CodexState>();
                    if c.open && c.selected.is_some() && !w.resource::<ReactionLibState>().open {
                        Ok(())
                    } else {
                        Err(format!("substance library open={} on {:?}", c.open, c.selected))
                    }
                }),
                30,
            ),
        ],
    ));

    // --- Tech Tree ---
    let open_tree = || setup(|w| w.resource_mut::<TechTreeState>().open = true);
    v.push(check(
        "Tech Tree",
        "Graph / List switch views",
        vec![
            open_tree(),
            Op::Wait(8),
            Op::Click(target("the List button", |w| {
                let e = first::<TechModeButton>(w, |b| b.0 == TechMode::List)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    let shown = w
                        .query_filtered::<&Node, With<TechListView>>()
                        .iter(w)
                        .next()
                        .map(|n| n.display == Display::Flex)
                        .unwrap_or(false);
                    if w.resource::<TechTreeState>().mode == TechMode::List && shown {
                        Ok(())
                    } else {
                        Err("the list is not showing".into())
                    }
                }),
                30,
            ),
            Op::Click(target("the Graph button", |w| {
                let e = first::<TechModeButton>(w, |b| b.0 == TechMode::Graph)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(state("graph mode", |w| w.resource::<TechTreeState>().mode == TechMode::Graph), 30),
        ],
    ));
    v.push(check(
        "Tech Tree",
        "Clicking a step shows it in the bar below",
        vec![
            setup(new_game),
            open_tree(),
            Op::Wait(10),
            Op::Click(target("a step in sight on the graph", |w| {
                let view = first::<TechGraphView>(w, |_| true)?;
                let (lo, hi) = (point_in(w, view, 0.05, 0.05)?, point_in(w, view, 0.95, 0.95)?);
                let steps: Vec<Entity> = w.query_filtered::<Entity, With<TechNodeButton>>().iter(w).collect();
                steps.into_iter().find_map(|e| {
                    let p = point_in(w, e, 0.5, 0.5)?;
                    (p.x > lo.x && p.y > lo.y && p.x < hi.x && p.y < hi.y).then_some(p)
                })
            })),
            Op::Until(state("a step selected", |w| w.resource::<TechTreeState>().selected.is_some()), 30),
        ],
    ));
    // Every prerequisite is expressed: checked on the steps that need the most (and the
    // first and last), whatever the content holds.
    let mut ops = vec![
        setup(new_game),
        setup(|w| w.resource_mut::<TechTreeState>().open = true),
        Op::Until(state("the tree's links worked out", |w| !w.resource::<TechLinks>().needs.is_empty()), 60),
    ];
    for i in 0..TECH_SAMPLES {
        ops.push(setup(move |w| {
            let id = sampled_step(w, i);
            w.resource_mut::<TechTreeState>().selected = id;
            // only the steps in sight are built: bring it into view, badge and all
            if let Some(id) = id {
                w.resource_mut::<TechLinks>().reveal(id);
            }
        }));
        ops.push(Op::Wait(3));
        ops.push(Op::Until(verify(move |w| needs_shown(w, i)), 30));
    }
    ops.push(Op::Shot("a selected step: its links, badge and needs"));
    v.push(check("Tech Tree", "Every step shows all it needs: links when selected, a badge, a chip each", ops));
    v.push(check(
        "Tech Tree",
        "Tapping a need goes to the step that makes it",
        vec![
            setup(new_game),
            setup(|w| {
                w.resource_mut::<TechTreeState>().open = true;
            }),
            Op::Until(state("the tree's links worked out", |w| !w.resource::<TechLinks>().needs.is_empty()), 60),
            setup(|w| {
                let id = sampled_step(w, 0);
                w.resource_mut::<TechTreeState>().selected = id;
            }),
            Op::Wait(4),
            setup(|w| {
                let maker = first::<TechNeedButton>(w, |b| b.0.is_some())
                    .and_then(|e| w.get::<TechNeedButton>(e))
                    .and_then(|b| b.0);
                w.insert_resource(ExpectedStep(maker));
            }),
            Op::Click(target("the first need with a maker".to_string(), |w| {
                let e = first::<TechNeedButton>(w, |b| b.0.is_some())?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    let want = w.get_resource::<ExpectedStep>().and_then(|x| x.0);
                    let got = w.resource::<TechTreeState>().selected;
                    if want.is_some() && got == want {
                        Ok(())
                    } else {
                        Err(format!("selected {got:?}, wanted the maker {want:?}"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Tech Tree",
        "Open in Reaction Library goes to that reaction",
        vec![
            setup(new_game),
            setup(|w| {
                discover(w, &["Charcoal"]);
                let id =
                    w.resource::<RecipeDatabase>().authored.iter().find(|r| r.name == "Charcoal Burning").map(|r| r.id);
                let mut t = w.resource_mut::<TechTreeState>();
                t.open = true;
                t.selected = id;
            }),
            Op::Wait(10),
            Op::Click(marked::<TechOpenInLibrary>("Open in Reaction Library")),
            Op::Until(
                verify(|w| {
                    let want = w
                        .resource::<RecipeDatabase>()
                        .authored
                        .iter()
                        .find(|r| r.name == "Charcoal Burning")
                        .map(|r| r.id);
                    let r = w.resource::<ReactionLibState>();
                    if r.open && r.selected == want {
                        Ok(())
                    } else {
                        Err(format!("reaction library open={} on {:?}", r.open, r.selected))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Tech Tree",
        "Dragging the map pans it",
        vec![
            setup(|w| {
                let mut t = w.resource_mut::<TechTreeState>();
                t.open = true;
                t.mode = TechMode::Graph;
            }),
            Op::Wait(10),
            setup(|w| {
                let x = w
                    .query::<(&TechScrollable, &ScrollPosition)>()
                    .iter(w)
                    .find(|(m, _)| m.graph)
                    .map(|(_, s)| s.0.x)
                    .unwrap_or(0.0);
                w.resource_mut::<Scratch>().0.insert("x", x);
            }),
            Op::DragBy(
                target("the map's era headings", |w| {
                    let e = first::<TechGraphView>(w, |_| true)?;
                    let top = point_in(w, e, 0.6, 0.0)?;
                    Some(top + Vec2::new(0.0, 30.0))
                }),
                Vec2::new(-300.0, 0.0),
            ),
            Op::Until(
                verify(|w| {
                    let x = w
                        .query::<(&TechScrollable, &ScrollPosition)>()
                        .iter(w)
                        .find(|(m, _)| m.graph)
                        .map(|(_, s)| s.0.x)
                        .unwrap_or(0.0);
                    let start = w.resource::<Scratch>().0.get("x").copied().unwrap_or(0.0);
                    if x > start + 150.0 {
                        Ok(())
                    } else {
                        Err(format!("scrolled from {start} to {x}"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Tech Tree",
        "Only the steps in sight are built: panning builds more, closing lets go of all",
        vec![
            setup(new_game),
            setup(|w| {
                let mut t = w.resource_mut::<TechTreeState>();
                t.open = true;
                t.mode = TechMode::Graph;
                t.selected = None;
            }),
            Op::Until(verify(|w| if tech_built(w).0 > 0 { Ok(()) } else { Err("no step built".into()) }), 60),
            Op::Expect(verify(tech_view_complete)),
            Op::Expect(verify(|w| {
                let (steps, rows) = tech_built(w);
                let all = w.resource::<crate::ui::tech_tree::TechLayout>().steps();
                if steps * 4 < all && rows == 0 {
                    Ok(())
                } else {
                    Err(format!("{steps} of {all} steps built, {rows} list rows built behind the graph"))
                }
            })),
            // the last step of the tree, far from where it opens
            setup(|w| {
                let last = w.resource::<RecipeDatabase>().authored.last().map(|r| r.id);
                if let Some(id) = last {
                    w.resource_mut::<TechLinks>().reveal(id);
                }
            }),
            Op::Until(
                verify(|w| {
                    let last = w.resource::<RecipeDatabase>().authored.last().map(|r| r.id);
                    if w.query::<&TechNodeButton>().iter(w).any(|b| Some(b.0) == last) {
                        Ok(())
                    } else {
                        Err(format!("the last step ({last:?}) is not built after scrolling to it"))
                    }
                }),
                60,
            ),
            Op::Until(verify(tech_view_complete), 30),
            // the middle of the map, and deep down the tallest columns
            setup(|w| scroll_tech_graph(w, Vec2::new(0.5, 0.5))),
            Op::Wait(3),
            Op::Until(verify(tech_view_complete), 30),
            setup(|w| scroll_tech_graph(w, Vec2::new(0.3, 0.9))),
            Op::Wait(3),
            Op::Until(verify(tech_view_complete), 30),
            setup(|w| w.resource_mut::<TechTreeState>().mode = TechMode::List),
            Op::Until(
                verify(|w| match tech_built(w) {
                    (0, rows) if rows > 0 => Ok(()),
                    built => Err(format!("(graph steps, list rows) built: {built:?}")),
                }),
                60,
            ),
            Op::Expect(verify(|w| {
                let rows = tech_built(w).1;
                let all = w.resource::<crate::ui::tech_tree::TechLayout>().steps();
                if rows * 4 < all {
                    Ok(())
                } else {
                    Err(format!("{rows} of {all} list rows built"))
                }
            })),
            setup(|w| w.resource_mut::<TechTreeState>().open = false),
            Op::Until(
                verify(|w| match tech_built(w) {
                    (0, 0) => Ok(()),
                    built => Err(format!("still built once closed: {built:?}")),
                }),
                60,
            ),
            setup(|w| w.resource_mut::<TechTreeState>().mode = TechMode::Graph),
        ],
    ));
    v.push(check(
        "Tech Tree",
        "The x closes it",
        vec![
            open_tree(),
            Op::Wait(5),
            Op::Click(marked::<TechCloseButton>("the Tech Tree's x")),
            Op::Until(state("tech tree closed", |w| !w.resource::<TechTreeState>().open), 30),
        ],
    ));

    // --- scrolling: no dead zone after scrolling past the end ---
    v.push(overscroll_check::<InventoryScroll>(
        "Scrolling",
        "The shelf scrolls back at once after over-scrolling",
        "the shelf",
        vec![setup(discover_everything), Op::Wait(20)],
    ));
    v.push(overscroll_check::<VesselSidebar>(
        "Scrolling",
        "The vessel list scrolls back at once after over-scrolling",
        "the vessel list",
        vec![],
    ));

    // --- moving substances between vessels ---
    v.push(check(
        "Lab: drag and drop",
        "Dragging a substance out of a vessel takes it out",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Zone)),
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            Op::Drag(card_part(Mix, FirstChip), bench_spot()),
            Op::Until(chip_count(Mix, 0), 30),
            Op::Expect(no_ghosts()),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "Dragging a substance onto another vessel moves it",
        vec![
            setup(|w| place(w, Mix, 0)),
            setup(|w| place(w, Heat, 1)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Zone)),
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            Op::Drag(card_part(Mix, FirstChip), card_part(Heat, Art)),
            Op::Until(has_chip(Heat, "Oxygen"), 30),
            Op::Expect(chip_count(Mix, 0)),
            Op::Expect(chip_count(Heat, 1)),
            Op::Expect(no_ghosts()),
        ],
    ));
    v.push(check(
        "Lab: drag and drop",
        "Dropping a substance back in its own vessel keeps it",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Zone)),
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            Op::Drag(card_part(Mix, FirstChip), card_part(Mix, Art)),
            Op::Wait(5),
            Op::Expect(chip_count(Mix, 1)),
        ],
    ));
    v.push(check(
        "Lab: reactions",
        "Products pop into the vessel",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            Op::Wait(5),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            Op::Click(card_part(Heat, React)),
            Op::Until(
                verify(|w| {
                    // popping now, or popped already (on slow frames the pop can be over
                    // before the check looks)
                    let popped = w
                        .query_filtered::<(), (
                            With<InVessel>,
                            Or<(With<crate::ui::inventory::PopIn>, With<crate::ui::inventory::Popped>)>,
                        )>()
                        .iter(w)
                        .count();
                    if popped > 0 {
                        Ok(())
                    } else {
                        Err("no product chip popped in".into())
                    }
                }),
                WAIT,
            ),
            Op::Until(has_chip(Heat, "Charcoal"), WAIT),
            Op::Until(
                verify(|w| {
                    let still = w.query_filtered::<(), With<crate::ui::inventory::PopIn>>().iter(w).count();
                    let odd = w
                        .query_filtered::<&UiTransform, With<InVessel>>()
                        .iter(w)
                        .filter(|t| (t.scale - Vec2::ONE).length() > 0.01)
                        .count();
                    if still == 0 && odd == 0 {
                        Ok(())
                    } else {
                        Err(format!("{still} still popping, {odd} not at full size"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "A discovery adds its tile in place without rebuilding the shelf",
        vec![
            setup(new_game),
            Op::Wait(10),
            setup(|w| {
                let tiles: Vec<Entity> = w.query_filtered::<Entity, With<ShelfTile>>().iter(w).collect();
                let first = tiles.iter().map(|e| e.index().index()).min().map(|i| i as f32).unwrap_or(0.0);
                w.resource_mut::<Scratch>().0.insert("n", tiles.len() as f32);
                w.resource_mut::<Scratch>().0.insert("first", first);
            }),
            setup(|w| discover(w, &["Charcoal"])),
            Op::Until(
                verify(|w| {
                    let n = w.resource::<Scratch>().0.get("n").copied().unwrap_or(0.0) as usize;
                    let tiles: Vec<(Entity, String)> = w
                        .query_filtered::<(Entity, &Ingredient), With<ShelfTile>>()
                        .iter(w)
                        .map(|(e, i)| (e, i.name.clone()))
                        .collect();
                    if tiles.len() != n + 1 || !tiles.iter().any(|(_, name)| name == "Charcoal") {
                        return Err(format!("{} tiles, expected {} with Charcoal", tiles.len(), n + 1));
                    }
                    let first = w.resource::<Scratch>().0.get("first").copied().unwrap_or(0.0);
                    let kept = tiles.iter().any(|(e, _)| e.index().index() as f32 == first);
                    if kept {
                        Ok(())
                    } else {
                        Err("the old tiles were rebuilt".into())
                    }
                }),
                60,
            ),
            Op::Expect(verify(|w| {
                // in shelf order: elements first by number, then compounds by id
                let content = first::<crate::ui::inventory::InventoryContent>(w, |_| true).ok_or("no shelf")?;
                let kids: Vec<Entity> = w.get::<Children>(content).map(|c| c.iter().collect()).unwrap_or_default();
                let gd = w.resource::<GameData>().substances.clone();
                let subs = w.resource::<Assets<Substances>>().get(&gd).ok_or("no substances")?;
                let keys: Vec<(u8, u32)> = kids
                    .iter()
                    .filter_map(|e| w.get::<Ingredient>(*e))
                    .filter_map(|i| subs.0.get(&i.id))
                    .map(|s| match &s.element_info {
                        Some(ei) => (0u8, ei.atomic_number),
                        None => (1u8, s.id),
                    })
                    .collect();
                if keys.windows(2).all(|p| p[0] <= p[1]) {
                    Ok(())
                } else {
                    Err("the new tile is out of order".into())
                }
            })),
        ],
    ));

    // --- help: tooltips, the tour, the era banner (the Hint button's checks are in polish.rs) ---
    v.push(check(
        "Help",
        "Hovering a shelf tile explains it",
        vec![Op::MoveTo(tile("Water")), Op::Until(tooltip_says("Water"), 120), Op::Shot("tooltip on a shelf tile")],
    ));
    v.push(check(
        "Help",
        "Hovering a vessel button says what it runs and what unlocks it",
        vec![
            setup(new_game),
            Op::Wait(3),
            Op::MoveTo(sidebar_button(ProcessType::BlastFurnace)),
            Op::Until(tooltip_says("Blast Furnace"), 120),
            Op::Shot("tooltip on a locked vessel"),
            Op::Expect(verify(|w| {
                let body = w
                    .query_filtered::<&Text, With<crate::ui::onboarding::TooltipBody>>()
                    .iter(w)
                    .next()
                    .map(|t| t.0.clone())
                    .unwrap_or_default();
                if body.contains("Locked") {
                    Ok(())
                } else {
                    Err(format!("the tooltip reads {body:?}"))
                }
            })),
        ],
    ));
    v.push(check(
        "Help",
        "Hovering a vessel's catalyst slot explains it",
        vec![
            setup(|w| place(w, Catalysis, 0)),
            Op::Wait(5),
            Op::MoveTo(card_part(Catalysis, CatalystSlot)),
            Op::Until(tooltip_says("Catalyst slot"), 120),
        ],
    ));
    v.push(check(
        "Help",
        "Tooltips off keeps them away",
        vec![
            setup(|w| w.resource_mut::<Settings>().tooltips = false),
            Op::MoveTo(tile("Water")),
            Op::Wait(60),
            Op::Expect(tooltip_hidden()),
        ],
    ));
    v.push(check(
        "Help",
        "The first-steps tour walks through the first loop",
        vec![
            setup(new_game),
            setup(|w| {
                w.resource_mut::<Settings>().tour_done = false;
                w.resource_mut::<Coach>().restart(0.0);
            }),
            Op::Until(coach_at(CoachStep::Place), 60),
            Op::Shot("tour 1: place a vessel"),
            Op::Click(sidebar_button(Heat)),
            Op::Until(coach_at(CoachStep::DragIn), 60),
            Op::Shot("tour 2: drag a substance in"),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(coach_at(CoachStep::React), 60),
            Op::Shot("tour 3: press React"),
            Op::Click(card_part(Heat, React)),
            Op::Until(coach_at(CoachStep::Discovery), WAIT),
            Op::Wait(20),
            Op::Shot("tour 4: the discovery"),
            Op::Click(marked::<CoachNext>("the tour's Got it button")),
            Op::Until(coach_at(CoachStep::Off), 30),
            Op::Expect(state("the tour is marked done", |w| w.resource::<Settings>().tour_done)),
        ],
    ));
    v.push(check(
        "Help",
        "Skipping the tour puts it away",
        vec![
            setup(|w| {
                w.resource_mut::<Settings>().tour_done = false;
                w.resource_mut::<Coach>().restart(0.0);
            }),
            Op::Until(coach_at(CoachStep::Place), 60),
            Op::Click(marked::<CoachSkip>("the tour's Skip button")),
            Op::Until(coach_at(CoachStep::Off), 30),
            Op::Expect(state("the tour is marked done", |w| w.resource::<Settings>().tour_done)),
        ],
    ));
    v.push(check(
        "Help",
        "Settings can replay the tour",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(marked::<TourAgainButton>("Show it again")),
            Op::Until(
                verify(|w| {
                    let step = w.resource::<Coach>().step;
                    let open = w.resource::<SettingsUi>().open;
                    if step == CoachStep::Place && !open && !w.resource::<Settings>().tour_done {
                        Ok(())
                    } else {
                        Err(format!("tour at {step:?}, settings open={open}"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Help",
        "Reaching a new era raises its banner",
        vec![
            setup(new_game),
            Op::Wait(10),
            setup(|w| {
                let n = w.query_filtered::<Entity, With<EraBanner>>().iter(w).collect::<Vec<_>>();
                for e in n {
                    w.despawn(e);
                }
            }),
            setup(discover_everything),
            Op::Until(
                verify(|w| {
                    let last = {
                        let db = w.resource::<RecipeDatabase>();
                        db.epochs.len().saturating_sub(1)
                    };
                    let want = w
                        .resource::<RecipeDatabase>()
                        .epochs
                        .get(last.saturating_sub(1))
                        .map(|e| e.name.clone())
                        .unwrap_or_default();
                    let banner = first::<EraBanner>(w, |_| true).ok_or("no era banner")?;
                    let mut texts = Vec::new();
                    let mut stack = vec![banner];
                    while let Some(e) = stack.pop() {
                        if let Some(t) = w.get::<Text>(e) {
                            texts.push(t.0.clone());
                        }
                        if let Some(c) = w.get::<Children>(e) {
                            stack.extend(c.iter());
                        }
                    }
                    if texts.contains(&want) {
                        Ok(())
                    } else {
                        Err(format!("the banner reads {texts:?}, expected {want}"))
                    }
                }),
                60,
            ),
            Op::Wait(15),
            Op::Shot("the era banner"),
            setup(new_game),
            Op::Wait(10),
        ],
    ));

    v.extend(polish::polish_checks());
    v.extend(tier_checks(world));
    v.extend(era_checks(world));
    v.extend(chain_checks(world));
    v
}

// ---------------------------------------------------------------------------------------
// Data-driven: reactions from every era, and linked chains
// ---------------------------------------------------------------------------------------
fn names(world: &World, ids: &[u32]) -> String {
    let Some(gd) = world.get_resource::<GameData>() else { return String::new() };
    let Some(subs) = world.resource::<Assets<Substances>>().get(&gd.substances) else { return String::new() };
    ids.iter()
        .map(|id| subs.0.get(id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}")))
        .collect::<Vec<_>>()
        .join(" + ")
}

fn sub_name(world: &World, id: u32) -> String {
    names(world, &[id])
}

/// The product a vessel passes down a link: the largest amount, first listed on a tie
/// (the order reaction_check sorts its products into).
fn first_product(r: &Reaction) -> u32 {
    let mut ps: Vec<(u32, u32)> = r.products.iter().map(|p| (p.substance_id, p.moles)).collect();
    ps.sort_by_key(|p| std::cmp::Reverse(p.1));
    ps[0].0
}

/// Everything a hand-run reaction needs: a clean bench, every substance on the shelf and
/// every vessel unlocked (so later eras can be reached directly).
fn stage_everything() -> Vec<Op> {
    vec![setup(new_game), setup(discover_everything), setup(unlock_all), Op::Wait(20)]
}

/// Drag a reaction's reactants (and catalyst) into its vessel, skipping `except`.
fn load(world: &World, r: &Reaction, except: Option<u32>) -> Vec<Op> {
    let p = r.process.clone();
    let mut ops = Vec::new();
    for sp in &r.reactants {
        if Some(sp.substance_id) == except {
            continue;
        }
        let id = sp.substance_id;
        let label = sub_name(world, id);
        ops.push(Op::Drag(tile_id(id, label.clone()), card_part(p.clone(), CardPart::Art)));
        ops.push(Op::Until(has_ids(p.clone(), vec![id], label), 40));
    }
    if let Some(c) = r.required_catalyst() {
        let label = sub_name(world, c);
        let pc = p.clone();
        ops.push(Op::Drag(tile_id(c, label.clone()), card_part(p.clone(), CardPart::CatalystSlot)));
        ops.push(Op::Until(
            verify(move |w| {
                let cards = card(w, pc.clone());
                let ok =
                    w.query::<(&Ingredient, &InCatalystZone)>().iter(w).any(|(i, z)| i.id == c && Some(z.0) == cards);
                if ok {
                    Ok(())
                } else {
                    Err(format!("{label} is not in the catalyst slot"))
                }
            }),
            40,
        ));
    }
    ops
}

fn reacted(p: ProcessType, name: String) -> Verify {
    verify(move |w| {
        let c = card(w, p.clone()).ok_or("the vessel is gone")?;
        let status = w
            .query_filtered::<(&Text, &ChildOf), With<EquationText>>()
            .iter(w)
            .find(|(_, cp)| cp.parent() == c)
            .map(|(t, _)| t.0.clone())
            .unwrap_or_default();
        if status.starts_with(&name) {
            Ok(())
        } else {
            Err(format!("{} reads {:?}, expected {}", vessel_name(&p), status, name))
        }
    })
}

/// The tiers, by hand: a recipe homed in a higher tier, tried in the tier below, fizzles
/// with a hint naming the vessel it needs; a recipe from the bottom of a family runs in a
/// vessel at the top of it.
fn tier_checks(world: &mut World) -> Vec<Check> {
    let Some(db) = world.get_resource::<RecipeDatabase>() else { return vec![] };
    let mut out = Vec::new();
    // (vessel to try in, recipe homed above it)
    let mut fizzles: Vec<(ProcessType, Reaction)> = Vec::new();
    // (higher vessel, recipe homed below it)
    let mut runs: Vec<(ProcessType, Reaction)> = Vec::new();
    for family in ["Heat", "Pressure", "Radiation", "Biology", "Distillation", "Electrolysis"] {
        let members: Vec<ProcessType> =
            VESSELS.iter().filter(|v| v.category == family).map(|v| v.process.clone()).collect();
        let (Some(low), Some(high)) =
            (members.iter().min_by_key(|p| p.tier()), members.iter().max_by_key(|p| p.tier()))
        else {
            continue;
        };
        if let Some(r) = db.authored.iter().find(|r| {
            r.process == *high
                && r.required_catalyst().is_none()
                && matches!(db.lookup(low, r.reactants.iter().map(|s| s.substance_id).collect()), Lookup::NeedsTier(x) if x == r.process)
        }) {
            fizzles.push((low.clone(), r.clone()));
        }
        if let Some(r) = db.authored.iter().find(|r| {
            r.process == *low
                && r.required_catalyst().is_none()
                && matches!(db.lookup(high, r.reactants.iter().map(|s| s.substance_id).collect()), Lookup::Runs(x) if x.id == r.id)
        }) {
            runs.push((high.clone(), r.clone()));
        }
    }
    for (p, r) in fizzles.into_iter().take(3) {
        let need = vessel_name(&r.process).to_string();
        let name: &'static str =
            Box::leak(format!("{} in the {} asks for the {}", r.name, vessel_name(&p), need).into_boxed_str());
        let mut ops = stage_everything();
        ops.push(setup({
            let p = p.clone();
            move |w| place(w, p.clone(), 0)
        }));
        ops.push(Op::Wait(5));
        let mut tried = r.clone();
        tried.process = p.clone();
        ops.extend(load(world, &tried, None));
        ops.push(Op::Click(card_part(p.clone(), CardPart::React)));
        ops.push(Op::Until(
            verify({
                let p = p.clone();
                move |w| {
                    let c = card(w, p.clone()).ok_or("the vessel is gone")?;
                    let status = w
                        .query_filtered::<(&Text, &ChildOf), With<EquationText>>()
                        .iter(w)
                        .find(|(_, cp)| cp.parent() == c)
                        .map(|(t, _)| t.0.clone())
                        .unwrap_or_default();
                    if status.contains(&format!("needs the {need}")) {
                        Ok(())
                    } else {
                        Err(format!("status reads {status:?}"))
                    }
                }
            }),
            WAIT,
        ));
        out.push(check("Tiers", name, ops));
    }
    for (p, r) in runs.into_iter().take(3) {
        let name: &'static str = Box::leak(format!("{} runs in the {}", r.name, vessel_name(&p)).into_boxed_str());
        let mut ops = stage_everything();
        ops.push(setup({
            let p = p.clone();
            move |w| place(w, p.clone(), 0)
        }));
        ops.push(Op::Wait(5));
        let mut tried = r.clone();
        tried.process = p.clone();
        ops.extend(load(world, &tried, None));
        ops.push(Op::Click(card_part(p.clone(), CardPart::React)));
        let products: Vec<u32> = r.products.iter().map(|s| s.substance_id).collect();
        let what = names(world, &products);
        ops.push(Op::Until(has_ids(p.clone(), products, what), WAIT));
        ops.push(Op::Expect(reacted(p, r.name.clone())));
        out.push(check("Tiers", name, ops));
    }
    out
}

/// One reaction per era at its start, middle and end, plus one for any vessel not yet
/// covered, each performed by hand: place the vessel from the list, drag everything in,
/// React, and check the products.
fn era_checks(world: &mut World) -> Vec<Check> {
    let Some(db) = world.get_resource::<RecipeDatabase>() else { return vec![] };
    let authored = db.authored.clone();
    let epochs: Vec<String> = db.epochs.iter().map(|e| e.name.clone()).collect();
    let mut picked: Vec<Reaction> = Vec::new();
    for e in 0..epochs.len() {
        let era: Vec<&Reaction> = authored.iter().filter(|r| r.epoch == e as u8).collect();
        if era.is_empty() {
            continue;
        }
        let mut idx = vec![0, era.len() / 2, era.len() - 1];
        idx.dedup();
        for i in idx {
            if !picked.iter().any(|p| p.id == era[i].id) {
                picked.push(era[i].clone());
            }
        }
    }
    for v in VESSELS {
        if !picked.iter().any(|r| r.process == v.process) {
            if let Some(r) = authored.iter().rev().find(|r| r.process == v.process) {
                picked.push(r.clone());
            }
        }
    }
    let mut out = Vec::new();
    for r in picked {
        let era = epochs.get(r.epoch as usize).cloned().unwrap_or_default();
        let area: &'static str = Box::leak(format!("Tech tree: {era}").into_boxed_str());
        let name: &'static str = Box::leak(format!("{} in the {}", r.name, vessel_name(&r.process)).into_boxed_str());
        let p = r.process.clone();
        let mut ops = stage_everything();
        ops.push(Op::Click(sidebar_button(p.clone())));
        ops.push(Op::Until(
            verify({
                let p = p.clone();
                move |w| {
                    if card(w, p.clone()).is_some() {
                        Ok(())
                    } else {
                        Err(format!("no {} on the bench", vessel_name(&p)))
                    }
                }
            }),
            30,
        ));
        ops.extend(load(world, &r, None));
        ops.push(Op::Click(card_part(p.clone(), CardPart::React)));
        let products: Vec<u32> = r.products.iter().map(|s| s.substance_id).collect();
        let what = names(world, &products);
        ops.push(Op::Until(has_ids(p.clone(), products, what), WAIT));
        ops.push(Op::Expect(reacted(p, r.name.clone())));
        out.push(check(area, name, ops));
    }
    out
}

/// Chains of linked vessels where each reaction's passed-on product is an ingredient of the
/// next: everything else is preloaded, the first vessel is started by hand, and the last
/// one must end up with its products. Two to four vessels long, from late eras first.
fn chain_checks(world: &mut World) -> Vec<Check> {
    let Some(db) = world.get_resource::<RecipeDatabase>() else { return vec![] };
    let authored = db.authored.clone();
    // r -> the reactions that can take r's passed-on product, in another vessel
    let next = |r: &Reaction| -> Vec<&Reaction> {
        let fp = first_product(r);
        authored
            .iter()
            .filter(|s| s.process != r.process && s.id != r.id)
            .filter(|s| s.reactants.iter().filter(|x| x.substance_id == fp).count() == 1)
            .filter(|s| s.required_catalyst() != Some(fp))
            .take(4)
            .collect()
    };
    let mut chains: Vec<Vec<Reaction>> = Vec::new();
    let mut starts: Vec<&Reaction> = authored.iter().collect();
    starts.sort_by_key(|r| std::cmp::Reverse((r.epoch, r.id)));
    for len in [4usize, 3, 2] {
        let want = match len {
            4 => 4,
            3 => 4,
            _ => 4,
        };
        let mut found = 0;
        for s in &starts {
            if found >= want {
                break;
            }
            // depth-first, distinct vessels along the chain
            let mut stack: Vec<Vec<&Reaction>> = vec![vec![*s]];
            let mut hit: Option<Vec<&Reaction>> = None;
            while let Some(path) = stack.pop() {
                if path.len() == len {
                    hit = Some(path);
                    break;
                }
                for n in next(path.last().unwrap()) {
                    if path.iter().all(|x| x.process != n.process) {
                        let mut np = path.clone();
                        np.push(n);
                        stack.push(np);
                    }
                }
            }
            if let Some(h) = hit {
                // prefer chains that bring in a vessel the others haven't used
                let used: Vec<ProcessType> = chains.iter().flatten().map(|r| r.process.clone()).collect();
                let fresh_vessel = h.iter().any(|r| !used.contains(&r.process));
                let overlap = chains.iter().any(|c| c.iter().any(|r| h.iter().any(|x| x.id == r.id)));
                if (fresh_vessel || found < 2) && !overlap {
                    chains.push(h.into_iter().cloned().collect());
                    found += 1;
                }
            }
        }
    }
    let mut out = Vec::new();
    for chain in chains {
        let label = chain.iter().map(|r| vessel_name(&r.process)).collect::<Vec<_>>().join(" -> ");
        let name: &'static str = Box::leak(
            format!("{} ({})", chain.iter().map(|r| r.name.as_str()).collect::<Vec<_>>().join(", then "), label)
                .into_boxed_str(),
        );
        let area: &'static str = Box::leak(format!("Chains: {} vessels", chain.len()).into_boxed_str());
        let mut ops = stage_everything();
        // the vessels, from the list, left to right
        for r in &chain {
            let p = r.process.clone();
            ops.push(Op::Click(sidebar_button(p.clone())));
            ops.push(Op::Until(
                verify(move |w| {
                    if card(w, p.clone()).is_some() {
                        Ok(())
                    } else {
                        Err(format!("no {} on the bench", vessel_name(&p)))
                    }
                }),
                30,
            ));
        }
        // preload everything but the ingredient that will arrive down the link
        for i in 1..chain.len() {
            ops.extend(load(world, &chain[i], Some(first_product(&chain[i - 1]))));
        }
        // link them
        for i in 0..chain.len() - 1 {
            ops.push(Op::Drag(
                card_part(chain[i].process.clone(), CardPart::OutPort),
                card_part(chain[i + 1].process.clone(), CardPart::InPort),
            ));
        }
        let links = chain.len() - 1;
        ops.push(Op::Until(
            verify(move |w| {
                let n = w.query::<&ReactionLink>().iter(w).count();
                if n == links {
                    Ok(())
                } else {
                    Err(format!("{n} of {links} links made"))
                }
            }),
            30,
        ));
        // start the first vessel by hand
        ops.extend(load(world, &chain[0], None));
        ops.push(Op::Click(card_part(chain[0].process.clone(), CardPart::React)));
        let last = chain.last().unwrap();
        let products: Vec<u32> = last.products.iter().map(|s| s.substance_id).collect();
        let what = names(world, &products);
        ops.push(Op::Until(has_ids(last.process.clone(), products, what), WAIT * chain.len() as u32));
        for r in &chain {
            ops.push(Op::Expect(reacted(r.process.clone(), r.name.clone())));
        }
        out.push(check(area, name, ops));
    }
    out
}
