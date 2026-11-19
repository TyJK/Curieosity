// src/ui/focus.rs
//
// Keyboard and controller focus. Tab and Shift+Tab move between the controls on screen in
// reading order;
// Enter (or Space, when no search box is taking typing) presses the focused one, exactly as
// a click would; a ring shows where focus is. The ring appears once the keyboard is used
// and hides again at the next mouse click.
//
// What can be focused is worked out from the screen itself, so new buttons join in
// without registering anywhere:
//   * any visible `Button`, shelf tile or vessel on the bench (not `NoFocus`, and not a
//     disabled skin), in tree order;
//   * while a view or dialog covers the lab (`FocusCover`), only what sits in the topmost
//     cover or above it (the header stays reachable from a view; nothing behind Settings);
//   * a long list or grid (`FocusGroup`: the shelf, the vessel picker, the library lists,
//     the tech tree) is one Tab stop; the arrow keys move inside it.
use crate::ui::{Button, Clicked};
use bevy::camera::NormalizedRenderTarget;
use bevy::picking::backend::HitData;
use bevy::picking::events::{Pointer, PointerClick};
use bevy::picking::pointer::{Location, PointerButton, PointerId};
use bevy::platform::collections::HashMap;
use bevy::prelude::*;
use bevy::ui::UiSystems;
use bevy::window::{PrimaryWindow, WindowRef};

use crate::components::{Draggable, VesselCard};
use crate::ui::codex::{CodexListContent, CodexRoot, CodexState};
use crate::ui::credits::CreditsRoot;
use crate::ui::inventory::{InventoryContent, ShelfTile};
use crate::ui::process_toolbar::{VesselPickerGrid, VesselPickerRoot};
use crate::ui::reaction_library::{ReactionLibListContent, ReactionLibRoot, ReactionLibState};
use crate::ui::settings::{SettingsBackdrop, SettingsRoot};
use crate::ui::tech_tree::{TechGraphContent, TechListContent, TechRoot};
use crate::ui::theme::{self, Kind, Skin};

/// Where keyboard focus is.
#[derive(Resource, Default, Debug)]
pub struct KeyFocus {
    pub entity: Option<Entity>,
    /// the ring shows (the keyboard was used since the last click)
    pub visible: bool,
    /// the member each group had focused last, so Tab returns to it
    remembered: HashMap<Entity, Entity>,
}

/// A button Tab skips.
#[derive(Component)]
pub struct NoFocus;

/// A list or grid that is one Tab stop; arrows move inside it.
#[derive(Component)]
pub struct FocusGroup;

/// A view or dialog that covers what is beneath it while it shows.
#[derive(Component)]
pub struct FocusCover;

#[derive(Component)]
pub struct FocusRing;

pub struct FocusPlugin;

impl Plugin for FocusPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<KeyFocus>()
            .add_systems(Startup, spawn_focus_ring)
            .add_systems(PreUpdate, (mark_focus_roles, key_focus_system).chain().after(UiSystems::Focus))
            .add_systems(Update, focus_ring_system);
    }
}

fn spawn_focus_ring(mut commands: Commands) {
    commands.spawn((
        FocusRing,
        Node {
            border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
            position_type: PositionType::Absolute,
            border: UiRect::all(Val::Px(2.5)),
            display: Display::None,
            ..default()
        },
        // light, not cyan: cyan already marks hover and selection, so focus must differ
        BorderColor::all(theme::TEXT),
        GlobalZIndex(1950),
        Pickable::IGNORE,
        Name::new("FocusRing"),
    ));
}

/// Lists become groups, views and dialogs become covers, the settings backdrop is skipped.
#[allow(clippy::type_complexity)]
fn mark_focus_roles(
    mut commands: Commands,
    groups: Query<
        Entity,
        (
            Or<(
                With<InventoryContent>,
                With<VesselPickerGrid>,
                With<CodexListContent>,
                With<ReactionLibListContent>,
                With<TechListContent>,
                With<TechGraphContent>,
            )>,
            Without<FocusGroup>,
        ),
    >,
    covers: Query<
        Entity,
        (
            Or<(
                With<CodexRoot>,
                With<ReactionLibRoot>,
                With<TechRoot>,
                With<SettingsRoot>,
                With<CreditsRoot>,
                With<crate::ui::main_menu::MenuRoot>,
                With<VesselPickerRoot>,
                With<crate::ui::bench_controls::ConfirmRoot>,
            )>,
            Without<FocusCover>,
        ),
    >,
    backdrops: Query<Entity, (With<SettingsBackdrop>, Without<NoFocus>)>,
) {
    for e in &groups {
        commands.entity(e).insert(FocusGroup);
    }
    for e in &covers {
        commands.entity(e).insert(FocusCover);
    }
    for e in &backdrops {
        commands.entity(e).insert(NoFocus);
    }
}

/// A place focus can land.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Stop {
    pub entity: Entity,
    pub group: Option<Entity>,
}

/// The parts of the UI tree the focus order is read from.
#[derive(bevy::ecs::system::SystemParam)]
pub struct FocusTree<'w, 's> {
    roots: Query<
        'w,
        's,
        (Entity, &'static UiGlobalTransform, &'static ComputedNode),
        (With<Node>, Without<ChildOf>, Without<FocusRing>),
    >,
    nodes: Query<
        'w,
        's,
        (&'static Node, &'static ComputedNode, Option<&'static InheritedVisibility>, Option<&'static GlobalZIndex>),
        Without<FocusRing>,
    >,
    children: Query<'w, 's, &'static Children>,
    buttons:
        Query<'w, 's, Option<&'static Skin>, (Or<(With<Button>, With<ShelfTile>, With<VesselCard>)>, Without<NoFocus>)>,
    groups: Query<'w, 's, (), With<FocusGroup>>,
    covers:
        Query<'w, 's, (Entity, &'static Node, Option<&'static GlobalZIndex>), (With<FocusCover>, Without<FocusRing>)>,
    rects: Query<'w, 's, (&'static ComputedNode, &'static UiGlobalTransform)>,
    parents: Query<'w, 's, &'static ChildOf>,
}

impl FocusTree<'_, '_> {
    /// Every focusable control on screen, in reading order, with the group it belongs to.
    pub fn members(&self) -> Vec<Stop> {
        let top = self
            .covers
            .iter()
            .filter(|(_, n, _)| n.display != Display::None)
            .max_by_key(|(_, _, z)| z.map_or(0, |z| z.0))
            .map(|(e, _, z)| (e, z.map_or(0, |z| z.0)));
        let mut roots: Vec<(Entity, Vec2)> =
            self.roots.iter().map(|(e, tf, cn)| (e, tf.translation - cn.size * 0.5)).collect();
        roots.sort_by(|a, b| (a.1.y, a.1.x).partial_cmp(&(b.1.y, b.1.x)).unwrap_or(std::cmp::Ordering::Equal));
        let mut out = Vec::new();
        for (root, _) in roots {
            self.walk(root, 0, false, None, top, &mut out);
        }
        out
    }

    fn walk(
        &self,
        e: Entity,
        z: i32,
        in_top: bool,
        group: Option<Entity>,
        top: Option<(Entity, i32)>,
        out: &mut Vec<Stop>,
    ) {
        let Ok((node, cn, vis, gz)) = self.nodes.get(e) else { return };
        if node.display == Display::None || vis.is_some_and(|v| !v.get()) {
            return;
        }
        let z = gz.map_or(z, |g| g.0);
        let in_top = in_top || top.is_some_and(|(t, _)| t == e);
        if let Ok(skin) = self.buttons.get(e) {
            let allowed = match top {
                None => true,
                Some((_, tz)) => in_top || z > tz,
            };
            let enabled = skin.is_none_or(|s| s.kind != Kind::Disabled);
            if allowed && enabled && cn.size.x > 0.0 && cn.size.y > 0.0 {
                out.push(Stop { entity: e, group });
            }
        }
        let group = if self.groups.contains(e) { Some(e) } else { group };
        if let Ok(children) = self.children.get(e) {
            for c in children.iter() {
                self.walk(c, z, in_top, group, top, out);
            }
        }
    }

    /// The Tab stops: each group collapsed to one stop (its remembered member, else its first).
    pub fn stops(&self, focus: &KeyFocus) -> Vec<Stop> {
        let members = self.members();
        let mut out: Vec<Stop> = Vec::new();
        for m in &members {
            match m.group {
                None => out.push(*m),
                Some(g) => {
                    if out.iter().any(|s| s.group == Some(g)) {
                        continue;
                    }
                    let pick = focus
                        .remembered
                        .get(&g)
                        .copied()
                        .filter(|r| members.iter().any(|x| x.entity == *r))
                        .unwrap_or(m.entity);
                    out.push(Stop { entity: pick, group: Some(g) });
                }
            }
        }
        out
    }

    /// The rectangle of a node in logical pixels (min corner, size).
    pub fn rect(&self, e: Entity) -> Option<(Vec2, Vec2)> {
        let (cn, tf) = self.rects.get(e).ok()?;
        let k = cn.inverse_scale_factor();
        let size = cn.size * k;
        Some((tf.translation * k - size * 0.5, size))
    }

    /// The first stop inside the topmost cover, if one is open.
    fn first_in_cover(&self, stops: &[Stop]) -> Option<Entity> {
        let (top, _, _) = self
            .covers
            .iter()
            .filter(|(_, n, _)| n.display != Display::None)
            .max_by_key(|(_, _, z)| z.map_or(0, |z| z.0))?;
        stops.iter().map(|s| s.entity).find(|e| self.parents.iter_ancestors(*e).any(|a| a == top))
    }
}

/// The next stop from `current` (wrapping), or the first/last when focus is elsewhere.
pub fn step(stops: &[Stop], current: Option<Entity>, back: bool) -> Option<Entity> {
    if stops.is_empty() {
        return None;
    }
    let n = stops.len();
    let at = current.and_then(|c| stops.iter().position(|s| s.entity == c));
    let i = match (at, back) {
        (Some(i), false) => (i + 1) % n,
        (Some(i), true) => (i + n - 1) % n,
        (None, false) => 0,
        (None, true) => n - 1,
    };
    Some(stops[i].entity)
}

/// Inside a group: Left/Right go to the previous/next member, Up/Down to the nearest
/// member above or below.
pub fn arrow(members: &[(Entity, Vec2)], current: Entity, dir: IVec2) -> Option<Entity> {
    let i = members.iter().position(|(e, _)| *e == current)?;
    if dir.y == 0 {
        let j = i as i32 + dir.x;
        return (0..members.len() as i32).contains(&j).then(|| members[j as usize].0);
    }
    let here = members[i].1;
    members
        .iter()
        .filter(|(e, c)| *e != current && (c.y - here.y) * dir.y as f32 > 4.0)
        .min_by(|a, b| {
            let score = |c: Vec2| (c.y - here.y).abs() + 2.0 * (c.x - here.x).abs();
            score(a.1).partial_cmp(&score(b.1)).unwrap_or(std::cmp::Ordering::Equal)
        })
        .map(|(e, _)| *e)
}

/// The nearest control in a direction on screen: the smallest distance along it, with
/// sideways distance counting double, so moving down a column stays in the column.
pub fn spatial(cands: &[(Entity, Vec2)], from: Vec2, dir: IVec2) -> Option<Entity> {
    let d = dir.as_vec2();
    cands
        .iter()
        .filter(|(_, c)| (*c - from).dot(d) > 4.0)
        .min_by(|a, b| {
            let score = |c: Vec2| {
                let v = c - from;
                v.dot(d) + 2.0 * (v - d * v.dot(d)).length()
            };
            score(a.1).partial_cmp(&score(b.1)).unwrap_or(std::cmp::Ordering::Equal)
        })
        .map(|(e, _)| *e)
}

/// The left stick held in one direction repeats, like a held arrow key.
#[derive(Default)]
pub struct StickRepeat {
    held: Option<IVec2>,
    next: f32,
}

/// What any connected controller asked for this frame: the D-pad or left stick move, A
/// presses, the bumpers act as Tab and Shift+Tab. (B and Start are the Esc key: see
/// shell::escape_system.)
#[derive(Default, Debug)]
pub struct PadInput {
    pub dir: Option<IVec2>,
    pub press: bool,
    pub tab: bool,
    pub back_tab: bool,
}

impl PadInput {
    fn read(pads: &Query<&Gamepad>, now: f32, stick: &mut StickRepeat) -> PadInput {
        let mut out = PadInput::default();
        let mut held = None;
        for g in pads {
            for (b, d) in [
                (GamepadButton::DPadLeft, IVec2::new(-1, 0)),
                (GamepadButton::DPadRight, IVec2::new(1, 0)),
                (GamepadButton::DPadUp, IVec2::new(0, -1)),
                (GamepadButton::DPadDown, IVec2::new(0, 1)),
            ] {
                if g.just_pressed(b) {
                    out.dir = Some(d);
                }
            }
            out.press |= g.just_pressed(GamepadButton::South);
            out.tab |= g.just_pressed(GamepadButton::RightTrigger);
            out.back_tab |= g.just_pressed(GamepadButton::LeftTrigger);
            let v = g.left_stick();
            if v.length() > 0.6 {
                // screen y grows downwards; the stick's grows upwards
                held = Some(if v.x.abs() > v.y.abs() {
                    IVec2::new(v.x.signum() as i32, 0)
                } else {
                    IVec2::new(0, -v.y.signum() as i32)
                });
            }
        }
        match held {
            Some(d) if stick.held != Some(d) => {
                stick.held = Some(d);
                stick.next = now + 0.4;
                out.dir = out.dir.or(Some(d));
            }
            Some(d) if now >= stick.next => {
                stick.next = now + 0.12;
                out.dir = out.dir.or(Some(d));
            }
            Some(_) => {}
            None => stick.held = None,
        }
        out
    }
}

/// Tab, arrows, Enter and Space (and a controller's); and releasing last frame's press.
#[allow(clippy::too_many_arguments)]
fn key_focus_system(
    mut commands: Commands,
    keys: Res<ButtonInput<KeyCode>>,
    mouse: Res<ButtonInput<MouseButton>>,
    mut focus: ResMut<KeyFocus>,
    tree: FocusTree,
    buttons: Query<(), With<Button>>,
    draggable: Query<(), With<Draggable>>,
    typing: (Res<CodexState>, Res<ReactionLibState>, Res<crate::ui::inventory::ShelfSearch>),
    mut scrollers: Query<(&Node, &ComputedNode, &UiGlobalTransform, &mut ScrollPosition)>,
    window: Query<Entity, With<PrimaryWindow>>,
    pads: Query<&Gamepad>,
    time: Res<Time>,
    mut stick: Local<StickRepeat>,
) {
    if mouse.get_just_pressed().next().is_some() && focus.visible {
        focus.visible = false;
    }
    let pad = PadInput::read(&pads, time.elapsed_secs(), &mut stick);
    let shift = keys.pressed(KeyCode::ShiftLeft) || keys.pressed(KeyCode::ShiftRight) || pad.back_tab;
    let tab = keys.just_pressed(KeyCode::Tab) || pad.tab || pad.back_tab;
    let dir = if pad.dir.is_some() {
        pad.dir
    } else if keys.just_pressed(KeyCode::ArrowLeft) {
        Some(IVec2::new(-1, 0))
    } else if keys.just_pressed(KeyCode::ArrowRight) {
        Some(IVec2::new(1, 0))
    } else if keys.just_pressed(KeyCode::ArrowUp) {
        Some(IVec2::new(0, -1))
    } else if keys.just_pressed(KeyCode::ArrowDown) {
        Some(IVec2::new(0, 1))
    } else {
        None
    };
    let searching = typing.0.open || typing.1.open || typing.2.typing;
    let press = keys.just_pressed(KeyCode::Enter)
        || keys.just_pressed(KeyCode::NumpadEnter)
        || (!searching && keys.just_pressed(KeyCode::Space))
        || pad.press;
    if !tab && dir.is_none() && !press {
        return;
    }

    let members = tree.members();
    let current = focus.entity.filter(|e| members.iter().any(|m| m.entity == *e));
    let mut moved_to = None;
    if tab {
        let stops = tree.stops(&focus);
        moved_to = match current {
            None if !shift => tree.first_in_cover(&stops).or_else(|| step(&stops, None, false)),
            _ => {
                // from inside a group, Tab moves on from the group's stop
                let from = current.and_then(|c| {
                    let g = members.iter().find(|m| m.entity == c)?.group?;
                    stops.iter().find(|s| s.group == Some(g)).map(|s| s.entity)
                });
                step(&stops, from.or(current), shift)
            }
        };
    } else if let Some(d) = dir {
        let centre = |e: Entity| tree.rect(e).map(|(min, size)| min + size * 0.5);
        let group = current.and_then(|c| members.iter().find(|m| m.entity == c)).and_then(|m| m.group);
        if let (Some(c), Some(g)) = (current, group) {
            let in_group: Vec<(Entity, Vec2)> = members
                .iter()
                .filter(|m| m.group == Some(g))
                .filter_map(|m| centre(m.entity).map(|p| (m.entity, p)))
                .collect();
            moved_to = arrow(&in_group, c, d);
        }
        // off the end of a list, or not in one: the nearest control that way on screen
        if moved_to.is_none() {
            let stops = tree.stops(&focus);
            moved_to = match current.and_then(centre) {
                Some(from) => {
                    let others: Vec<(Entity, Vec2)> = stops
                        .iter()
                        .filter(|s| s.group.is_none() || s.group != group)
                        .filter_map(|s| centre(s.entity).map(|p| (s.entity, p)))
                        .collect();
                    spatial(&others, from, d)
                }
                None => tree.first_in_cover(&stops).or_else(|| step(&stops, None, false)),
            };
        }
    }
    if let Some(next) = moved_to {
        focus.entity = Some(next);
        focus.visible = true;
        if let Some(g) = members.iter().find(|m| m.entity == next).and_then(|m| m.group) {
            focus.remembered.insert(g, next);
        }
        scroll_into_view(next, &tree, &mut scrollers);
        return;
    }

    if press {
        let Some(c) = current else { return };
        focus.visible = true;
        if draggable.contains(c) {
            // shelf tiles and vessels answer clicks through picking
            let (Ok(win), Some((min, size))) = (window.single(), tree.rect(c)) else { return };
            let Some(target) = WindowRef::Primary.normalize(Some(win)).map(NormalizedRenderTarget::Window) else {
                return;
            };
            let location = Location { target, position: min + size * 0.5 };
            let hit = HitData { camera: Entity::PLACEHOLDER, depth: 0.0, position: None, normal: None, extra: None };
            commands.trigger(PointerClick {
                entity: c,
                pointer: Pointer::new(PointerId::Mouse, location),
                button: PointerButton::Primary,
                hit,
                duration: std::time::Duration::ZERO,
                count: 1,
            });
        } else if buttons.contains(c) {
            commands.entity(c).insert(Clicked);
        }
    }
}

/// Scroll the panels around `e` so it is in sight.
fn scroll_into_view(
    e: Entity,
    tree: &FocusTree,
    scrollers: &mut Query<(&Node, &ComputedNode, &UiGlobalTransform, &mut ScrollPosition)>,
) {
    let Some((min, size)) = tree.rect(e) else { return };
    for a in tree.parents.iter_ancestors(e) {
        let Ok((node, cn, tf, mut sp)) = scrollers.get_mut(a) else { continue };
        let k = cn.inverse_scale_factor();
        let csize = cn.size * k;
        let cmin = tf.translation * k - csize * 0.5;
        let pad = 8.0;
        if node.overflow.y == OverflowAxis::Scroll {
            if min.y < cmin.y + pad {
                sp.0.y -= cmin.y + pad - min.y;
            } else if min.y + size.y > cmin.y + csize.y - pad {
                sp.0.y += min.y + size.y - (cmin.y + csize.y - pad);
            }
            sp.0.y = sp.0.y.max(0.0);
        }
        if node.overflow.x == OverflowAxis::Scroll {
            if min.x < cmin.x + pad {
                sp.0.x -= cmin.x + pad - min.x;
            } else if min.x + size.x > cmin.x + csize.x - pad {
                sp.0.x += min.x + size.x - (cmin.x + csize.x - pad);
            }
            sp.0.x = sp.0.x.max(0.0);
        }
    }
}

/// The ring follows the focused control; it hides when focus is gone or not in use.
fn focus_ring_system(mut focus: ResMut<KeyFocus>, tree: FocusTree, mut ring: Query<&mut Node, With<FocusRing>>) {
    let Ok(mut node) = ring.single_mut() else { return };
    let gone = focus.entity.is_some_and(|e| tree.rect(e).is_none_or(|(_, s)| s.x <= 0.0));
    if gone {
        focus.entity = None;
    }
    let shown = focus.visible.then_some(focus.entity).flatten().and_then(|e| tree.rect(e));
    match shown {
        Some((min, size)) => {
            let grow = 4.0;
            node.display = Display::Flex;
            node.left = Val::Px(min.x - grow);
            node.top = Val::Px(min.y - grow);
            node.width = Val::Px(size.x + grow * 2.0);
            node.height = Val::Px(size.y + grow * 2.0);
        }
        None => {
            if node.display != Display::None {
                node.display = Display::None;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn e(i: u32) -> Entity {
        Entity::from_raw_u32(i).unwrap()
    }

    #[test]
    fn tab_wraps_both_ways_and_starts_at_an_end() {
        let stops: Vec<Stop> = (1..=3).map(|i| Stop { entity: e(i), group: None }).collect();
        assert_eq!(step(&stops, Some(e(3)), false), Some(e(1)));
        assert_eq!(step(&stops, Some(e(1)), true), Some(e(3)));
        assert_eq!(step(&stops, None, false), Some(e(1)));
        assert_eq!(step(&stops, None, true), Some(e(3)));
        assert_eq!(step(&[], None, false), None);
    }

    #[test]
    fn the_nearest_control_that_way_wins() {
        let at = |x: f32, y: f32| Vec2::new(x, y);
        let cands =
            vec![(e(1), at(0.0, 100.0)), (e(2), at(300.0, 40.0)), (e(3), at(20.0, 300.0)), (e(4), at(0.0, -80.0))];
        assert_eq!(spatial(&cands, at(0.0, 0.0), IVec2::new(0, 1)), Some(e(1)));
        assert_eq!(spatial(&cands, at(0.0, 0.0), IVec2::new(1, 0)), Some(e(2)));
        assert_eq!(spatial(&cands, at(0.0, 0.0), IVec2::new(0, -1)), Some(e(4)));
        assert_eq!(spatial(&cands, at(0.0, 0.0), IVec2::new(-1, 0)), None);
    }

    #[test]
    fn arrows_move_through_a_grid() {
        // a 3 x 2 grid of tiles, 100 px apart
        let grid: Vec<(Entity, Vec2)> =
            (0..6).map(|i| (e(i + 1), Vec2::new((i % 3) as f32 * 100.0, (i / 3) as f32 * 100.0))).collect();
        assert_eq!(arrow(&grid, e(1), IVec2::new(1, 0)), Some(e(2)));
        assert_eq!(arrow(&grid, e(1), IVec2::new(-1, 0)), None);
        assert_eq!(arrow(&grid, e(2), IVec2::new(0, 1)), Some(e(5)));
        assert_eq!(arrow(&grid, e(5), IVec2::new(0, -1)), Some(e(2)));
        assert_eq!(arrow(&grid, e(5), IVec2::new(0, 1)), None);
    }
}
