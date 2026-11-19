// src/systems/link_renderer.rs
//
// Draws the vessel-to-vessel links as smooth curves from an output port to an input port,
// plus a live preview while a link is being made: dragged out of an output port (the line
// follows the mouse or finger), or picked by a tap on the port (a ring pulses on it and on
// every input port it could feed, and with a mouse the line follows the cursor).
//
// Port positions come straight from each port's UiGlobalTransform, so the lines follow
// vessels as they're dragged and the bench as it's panned and zoomed. That transform is in
// physical pixels; the gizmo camera works in the window's logical pixels, so it is divided
// by the window's scale factor (not by the node's, which also carries the interface size).
// A link leaves its output port's dot at the dot's right edge and meets the input's at its
// left edge, so the words in the dots stay clear. A link tapped once lights up for a moment
// (a second tap cuts it: drag_drop::tap_bench). The links are drawn over everything, so
// while one of the lab's pop-ups covers the bench (the vessel picker, the "are you sure",
// an open discovery card) they step aside.
use bevy::picking::pointer::{PointerLocation, PointerPressState};
use bevy::prelude::*;
use bevy::window::PrimaryWindow;

use crate::components::ui_markers::{InputPort, OutputPort, ReactionLink};
use crate::systems::drag_drop::{LinkDragState, LinkPick, LinkTap};
use crate::systems::reaction_check::{PORT_DOT, PORT_HIT};

const LINK_COLOR: Color = Color::srgb(0.35, 0.95, 1.0);
const PREVIEW_COLOR: Color = Color::srgba(1.0, 0.85, 0.5, 0.9);
const TAPPED_COLOR: Color = Color::srgb(1.0, 0.78, 0.32);

/// A node's centre in window logical pixels (origin top-left).
fn node_center(gt: &UiGlobalTransform, window: &Window) -> Vec2 {
    gt.translation / window.scale_factor()
}

/// Window space (origin top-left, y down) -> the gizmo camera's world space (origin centre,
/// y up). Both cameras use the default 1-unit-per-logical-pixel projection.
fn to_world(p: Vec2, window: &Window) -> Vec2 {
    Vec2::new(p.x - window.width() / 2.0, window.height() / 2.0 - p.y)
}

/// Where a link's end is drawn for a port, in the gizmo camera's world space (the review
/// projects it back through that camera to check it lands on the port's dot).
pub fn port_point(gt: &UiGlobalTransform, window: &Window) -> Vec2 {
    to_world(node_center(gt, window), window)
}

/// The radius of a port's dot in window logical pixels (the port node is its touch area).
fn dot_radius(cn: &ComputedNode, window: &Window) -> f32 {
    cn.size.x * (PORT_DOT / 2.0 - 1.0) / PORT_HIT / window.scale_factor()
}

/// A link's two ends in window logical pixels (origin top-left): the right edge of the
/// output port's dot and the left edge of the input port's.
pub fn link_ends(
    from: (&UiGlobalTransform, &ComputedNode),
    to: (&UiGlobalTransform, &ComputedNode),
    window: &Window,
) -> (Vec2, Vec2) {
    let a = node_center(from.0, window) + Vec2::new(dot_radius(from.1, window), 0.0);
    let b = node_center(to.0, window) - Vec2::new(dot_radius(to.1, window), 0.0);
    (a, b)
}

/// How far a point (window logical pixels) is from the link drawn between these ends.
pub fn distance_to_link(a: Vec2, b: Vec2, p: Vec2) -> f32 {
    // the curve has horizontal tangents, so it is the same in window and world space
    let pts = curve(a, b);
    pts.windows(2)
        .map(|s| {
            let (u, v) = (s[0], s[1]);
            let d = v - u;
            let t = if d.length_squared() > 0.0 { ((p - u).dot(d) / d.length_squared()).clamp(0.0, 1.0) } else { 0.0 };
            p.distance(u + d * t)
        })
        .fold(f32::INFINITY, f32::min)
}

/// The middle of the link drawn between these ends.
pub fn link_midpoint(a: Vec2, b: Vec2) -> Vec2 {
    curve(a, b)[12]
}

/// A horizontal-tangent cubic Bézier between two points, as a polyline.
fn curve(a: Vec2, b: Vec2) -> Vec<Vec2> {
    let pull = ((b.x - a.x).abs() * 0.5).max(60.0);
    let c1 = a + Vec2::new(pull, 0.0);
    let c2 = b - Vec2::new(pull, 0.0);
    (0..=24)
        .map(|i| {
            let t = i as f32 / 24.0;
            let u = 1.0 - t;
            a * u * u * u + c1 * 3.0 * u * u * t + c2 * 3.0 * u * t * t + b * t * t * t
        })
        .collect()
}

#[allow(clippy::too_many_arguments)]
pub fn draw_links_system(
    mut gizmos: Gizmos,
    link_query: Query<(Entity, &ReactionLink)>,
    outputs: Query<(&UiGlobalTransform, &ComputedNode, &InheritedVisibility), With<OutputPort>>,
    inputs: Query<(Entity, &UiGlobalTransform, &ComputedNode, &InheritedVisibility), With<InputPort>>,
    window_query: Query<&Window, With<PrimaryWindow>>,
    drag: Res<LinkDragState>,
    pick: Res<LinkPick>,
    tapped: Res<LinkTap>,
    covers: (
        Res<crate::ui::process_toolbar::VesselPicker>,
        Res<crate::ui::bench_controls::Confirm>,
        Res<crate::ui::discovery_card::DiscoveryCards>,
    ),
    pointers: Query<(&PointerLocation, &PointerPressState)>,
    parents: Query<&ChildOf>,
    time: Res<Time<Real>>,
) {
    let Ok(window) = window_query.single() else { return };
    let (picker, confirm, cards) = covers;
    if picker.open || confirm.0.is_some() || cards.is_open() {
        return;
    }
    let at = |gt: &UiGlobalTransform| port_point(gt, window);
    let world = |p: Vec2| to_world(p, window);
    let now = time.elapsed_secs_f64();

    for (e, link) in &link_query {
        let (Ok((ga, ca, va)), Ok((_, gb, cb, vb))) = (outputs.get(link.from_port), inputs.get(link.to_port)) else {
            continue;
        };
        // Hidden behind an overlay (codex, tech tree)? Don't draw over it.
        if !va.get() || !vb.get() {
            continue;
        }
        let (a, b) = link_ends((ga, ca), (gb, cb), window);
        let lit = tapped.0.is_some_and(|(t, when)| t == e && now - when <= crate::ui::detail_panel::DOUBLE_TAP * 2.0);
        let color = if lit { TAPPED_COLOR } else { LINK_COLOR };
        gizmos.linestrip_2d(curve(world(a), world(b)), color);
        gizmos.circle_2d(Isometry2d::from_translation(world(a)), 3.5, color);
        gizmos.circle_2d(Isometry2d::from_translation(world(b)), 3.5, color);
    }

    // a link being dragged: the line follows whichever pointer is holding it
    if let Some(from) = drag.0 {
        let held = pointers
            .iter()
            .find(|(_, p)| p.is_primary_pressed())
            .and_then(|(l, _)| l.location.as_ref().map(|l| l.position));
        if let (Ok((g, _, _)), Some(to)) = (outputs.get(from), held.or(window.cursor_position())) {
            let (a, b) = (at(g), to_world(to, window));
            gizmos.linestrip_2d(curve(a, b), PREVIEW_COLOR);
            gizmos.circle_2d(Isometry2d::from_translation(b), 4.0, PREVIEW_COLOR);
        }
    }

    // a port picked by a tap: it pulses, and so does every input port it could feed (the
    // ports of one vessel share a row)
    if let Some(from) = pick.0 {
        let Ok((g, _, vis)) = outputs.get(from) else { return };
        if !vis.get() {
            return;
        }
        let a = at(g);
        let row = parents.get(from).ok().map(|c| c.parent());
        let beat = (time.elapsed_secs() * 4.0).sin() * 0.5 + 0.5;
        gizmos.circle_2d(Isometry2d::from_translation(a), 9.0 + 4.0 * beat, PREVIEW_COLOR);
        for (i, gi, _, vi) in &inputs {
            if vi.get() && parents.get(i).ok().map(|c| c.parent()) != row {
                gizmos.circle_2d(Isometry2d::from_translation(at(gi)), 8.0 + 3.0 * beat, PREVIEW_COLOR.with_alpha(0.6));
            }
        }
        if let Some(c) = window.cursor_position() {
            gizmos.linestrip_2d(curve(a, to_world(c, window)), PREVIEW_COLOR.with_alpha(0.5));
        }
    }
}
