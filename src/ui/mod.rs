// src/ui/mod.rs
use bevy::app::{App, Last, Plugin, PreUpdate};
use bevy::ecs::prelude::*;
use bevy::math::Vec2;
use bevy::picking::events::{PointerClick, PointerPress};
use bevy::picking::hover::Hovered;
use bevy::picking::pointer::{PointerAction, PointerButton, PointerId, PointerInput};
use bevy::picking::PickingSystems;
use bevy::platform::collections::HashMap;
use bevy::prelude::{ChildOf, Node};
use bevy::ui::Pressed;

pub mod bench_controls;
pub mod challenges;
pub mod codex;
pub mod credits;
pub mod curriculum;
pub mod detail_panel;
pub mod discovery_card;
pub mod focus;
pub mod glossary;
pub mod hint;
pub mod inventory;
pub mod main_menu;
pub mod onboarding;
pub mod process_toolbar;
pub mod reaction_canvas;
pub mod reaction_library;
pub mod settings;
pub mod shell;
pub mod tech_tree;
pub mod theme;
pub mod toasts;
pub mod virtual_list;

// ---------------------------------------------------------------------------------------
// Buttons
// ---------------------------------------------------------------------------------------
// Bevy 0.20 retires `Interaction`, one state that mixed how a button looks with whether it
// was used, for picking: `Hovered` and `Pressed` for the look, an event for the use. The
// game's buttons are split the same way:
// - `Hovered` (Bevy's, kept by picking) is true while the mouse is over the button or
//   anything in it. A finger has no hover, so nothing on a phone stays lit after a tap.
// - `Pressed` (Bevy's marker) is on while a pointer holds the button down. It comes off when
//   the pointer lets go, or moves far enough that it is a swipe rather than a press.
// - `Clicked` (ours) is on for the one frame after the button was used: a pointer let go on
//   it without travelling more than `TAP_SLOP` since it went down, or Enter/Space reached it
//   through keyboard focus. Using a button on release, not on press, is what lets a finger
//   swipe a list of buttons to scroll it without using the one it landed on.
// A button's `Hovered` is stamped afresh whenever its `Pressed` comes or goes, so a system
// that styles buttons needs only `Changed<Hovered>` and reads `Has<Pressed>` (see `Look`).

/// A pressable node. Picking finds it, and it blocks the pointer from what lies under it.
#[derive(Component, Debug, Default, Clone, Copy, PartialEq, Eq)]
#[require(Node, Hovered)]
pub struct Button;

/// On a button for the one frame after it was used (see above). Systems that act on a
/// button query `With<Clicked>`; it is gone again in `Last`.
#[derive(Component, Debug, Default, Clone, Copy)]
#[component(storage = "SparseSet")]
pub struct Clicked;

/// How far a pointer may move between going down and letting go and still click, in
/// logical pixels. A finger wobbles a few pixels on a tap; a swipe goes well past this.
pub const TAP_SLOP: f32 = 12.0;

/// What the pointer is doing to a button, for its look.
#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum Look {
    #[default]
    Rest,
    Hover,
    Press,
}

impl Look {
    pub fn of(hovered: &Hovered, pressed: bool) -> Self {
        if pressed {
            Look::Press
        } else if hovered.get() {
            Look::Hover
        } else {
            Look::Rest
        }
    }

    /// hovered or held down
    pub fn lit(self) -> bool {
        self != Look::Rest
    }
}

/// The pointers that are down: where each went down and the furthest it has been from
/// there since, and the button it holds. And the fingers on the screen: two that come down
/// together (within TOGETHER of each other) make a two-finger scroll, and nothing it
/// touches is pressed, tapped or dragged until every finger has lifted. A finger resting on
/// the screen a while (a thumb holding the phone) doesn't make the next tap a scroll, and
/// one the system never reports lifting is let go of after STALE.
#[derive(Resource, Default)]
pub struct Presses {
    travel: HashMap<PointerId, (Vec2, f32)>,
    held: HashMap<PointerId, Entity>,
    /// (finger, when it came down, when it last did anything)
    fingers: Vec<(PointerId, f64, f64)>,
    multi: bool,
}

/// Two fingers landing this close together (seconds) are one gesture.
const TOGETHER: f64 = 0.4;
/// A finger silent this long (seconds) is taken to have lifted.
const STALE: f64 = 10.0;

impl Presses {
    /// How far a pointer has moved since it went down, counting where it is now: for a
    /// picking observer to tell a tap from a drag the way buttons do.
    pub fn travel(&self, id: PointerId, now: Vec2) -> f32 {
        self.travel.get(&id).map_or(0.0, |(start, far)| far.max(now.distance(*start)))
    }

    pub fn is_tap(&self, id: PointerId, now: Vec2) -> bool {
        !self.multi && self.travel(id, now) <= TAP_SLOP
    }

    /// Two or more fingers have been down together since the last time none were: the
    /// gesture only scrolls.
    pub fn multi_touch(&self) -> bool {
        self.multi
    }

    /// How many fingers are on the screen.
    pub fn fingers(&self) -> usize {
        self.fingers.len()
    }
}

pub struct ButtonPlugin;

impl Plugin for ButtonPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<Presses>()
            .add_systems(PreUpdate, button_pointer_system.after(PickingSystems::Last))
            .add_systems(Last, clear_clicked_system);
    }
}

/// Turns picking's presses and clicks into `Pressed` and `Clicked` on the buttons they
/// landed on (or on the button around the text or icon they landed on).
#[allow(clippy::too_many_arguments)]
pub fn button_pointer_system(
    mut commands: Commands,
    mut state: ResMut<Presses>,
    time: Res<bevy::time::Time<bevy::time::Real>>,
    mut inputs: MessageReader<PointerInput>,
    mut presses: MessageReader<PointerPress>,
    mut clicks: MessageReader<PointerClick>,
    buttons: Query<&Hovered, With<Button>>,
    parents: Query<&ChildOf>,
) {
    let button_of = |mut e: Entity| {
        for _ in 0..16 {
            if buttons.contains(e) {
                return Some(e);
            }
            e = parents.get(e).ok()?.parent();
        }
        None
    };
    let mut restyle: Vec<Entity> = Vec::new();
    let mut ended: Vec<PointerId> = Vec::new();

    let now = time.elapsed_secs_f64();
    state.fingers.retain(|(_, _, seen)| now - seen < STALE);
    // a gesture that ended last frame is over now (its lifts' clicks came and were ignored)
    if state.fingers.is_empty() && state.multi {
        state.multi = false;
    }
    for input in inputs.read() {
        let at = input.location.position;
        match input.action {
            PointerAction::Press(PointerButton::Primary) => {
                state.travel.insert(input.pointer_id, (at, 0.0));
                let id = input.pointer_id;
                if matches!(id, PointerId::Touch(_)) && !state.fingers.iter().any(|f| f.0 == id) {
                    let together = state.fingers.iter().any(|(_, down, _)| now - down < TOGETHER);
                    state.fingers.push((id, now, now));
                    if together {
                        state.multi = true;
                    }
                }
            }
            PointerAction::Move { .. } => {
                if let Some((start, far)) = state.travel.get_mut(&input.pointer_id) {
                    *far = far.max(at.distance(*start));
                }
                if let Some(f) = state.fingers.iter_mut().find(|f| f.0 == input.pointer_id) {
                    f.2 = now;
                }
            }
            PointerAction::Release(PointerButton::Primary) => ended.push(input.pointer_id),
            PointerAction::Cancel => {
                if let Some((_, far)) = state.travel.get_mut(&input.pointer_id) {
                    *far = f32::INFINITY;
                }
                ended.push(input.pointer_id);
            }
            _ => {}
        }
    }

    // two fingers: every finger's press is a scroll's, not a tap's
    if state.multi {
        let fingers: Vec<PointerId> = state.fingers.iter().map(|f| f.0).collect();
        for id in fingers {
            if let Some((_, far)) = state.travel.get_mut(&id) {
                *far = f32::INFINITY;
            }
        }
    }
    for p in presses.read() {
        if p.button != PointerButton::Primary {
            continue;
        }
        let Some(b) = button_of(p.entity) else { continue };
        if let Some(old) = state.held.insert(p.pointer.id, b) {
            if old != b {
                commands.entity(old).try_remove::<Pressed>();
                restyle.push(old);
            }
        }
        commands.entity(b).try_insert(Pressed);
        restyle.push(b);
    }

    // a pointer that has moved too far is swiping, not pressing
    let swiping: Vec<PointerId> =
        state.held.keys().filter(|id| state.travel.get(*id).is_some_and(|(_, far)| *far > TAP_SLOP)).copied().collect();
    for id in swiping {
        if let Some(b) = state.held.remove(&id) {
            commands.entity(b).try_remove::<Pressed>();
            restyle.push(b);
        }
    }

    let mut used: Vec<Entity> = Vec::new();
    for c in clicks.read() {
        if c.button != PointerButton::Primary {
            continue;
        }
        if state.travel.get(&c.pointer.id).is_some_and(|(_, far)| *far > TAP_SLOP) {
            continue;
        }
        if let Some(b) = button_of(c.entity) {
            if !used.contains(&b) {
                used.push(b);
                commands.entity(b).try_insert(Clicked);
            }
        }
    }

    for id in ended {
        state.travel.remove(&id);
        state.fingers.retain(|f| f.0 != id);
        if let Some(b) = state.held.remove(&id) {
            commands.entity(b).try_remove::<Pressed>();
            restyle.push(b);
        }
    }

    restyle.sort_unstable_by_key(|e| e.index().index());
    restyle.dedup();
    for b in restyle {
        if let Ok(h) = buttons.get(b) {
            commands.entity(b).try_insert(*h);
        }
    }
}

fn clear_clicked_system(mut commands: Commands, used: Query<Entity, With<Clicked>>) {
    for e in &used {
        commands.entity(e).try_remove::<Clicked>();
    }
}
