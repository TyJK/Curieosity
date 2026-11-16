// src/systems/link_renderer.rs
//
// Draws the vessel-to-vessel links as smooth curves from an output port to an input port,
// plus a live preview while a link is being dragged out of an output port.
//
// Port positions come straight from each port's UiGlobalTransform (Bevy 0.17 keeps UI
// nodes on UiTransform/UiGlobalTransform, not Transform/GlobalTransform), so the lines
// follow vessels as they're dragged and the canvas as it's panned with no layout guesswork.
use bevy::prelude::*;
use bevy::window::PrimaryWindow;

use crate::components::ui_markers::{InputPort, OutputPort, ReactionLink};
use crate::systems::drag_drop::LinkDragState;

const LINK_COLOR: Color = Color::srgb(0.35, 0.95, 1.0);
const PREVIEW_COLOR: Color = Color::srgba(1.0, 0.85, 0.5, 0.9);

/// Logical-pixel centre of a UI node in window space (origin top-left).
fn node_center(gt: &UiGlobalTransform, cn: &ComputedNode) -> Vec2 {
    gt.translation * cn.inverse_scale_factor
}

/// Window space (origin top-left, y down) -> the gizmo camera's world space (origin centre,
/// y up). Both cameras use the default 1-unit-per-logical-pixel projection.
fn to_world(p: Vec2, window: &Window) -> Vec2 {
    Vec2::new(p.x - window.width() / 2.0, window.height() / 2.0 - p.y)
}

/// A horizontal-tangent cubic Bézier between two world points, as a polyline.
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

pub fn draw_links_system(
    mut gizmos: Gizmos,
    link_query: Query<&ReactionLink>,
    ports: Query<(&UiGlobalTransform, &ComputedNode, &InheritedVisibility), Or<(With<InputPort>, With<OutputPort>)>>,
    window_query: Query<&Window, With<PrimaryWindow>>,
    drag: Res<LinkDragState>,
) {
    let Ok(window) = window_query.single() else { return };

    for link in &link_query {
        let (Ok((ga, ca, va)), Ok((gb, cb, vb))) = (ports.get(link.from_port), ports.get(link.to_port)) else {
            continue;
        };
        // Hidden behind an overlay (codex, tech tree)? Don't draw over it.
        if !va.get() || !vb.get() {
            continue;
        }
        let a = to_world(node_center(ga, ca), window);
        let b = to_world(node_center(gb, cb), window);
        gizmos.linestrip_2d(curve(a, b), LINK_COLOR);
        gizmos.circle_2d(Isometry2d::from_translation(a), 5.0, LINK_COLOR);
        gizmos.circle_2d(Isometry2d::from_translation(b), 5.0, LINK_COLOR);
    }

    // Live preview while dragging a new link.
    if let Some(from) = drag.0 {
        if let (Ok((g, c, _)), Some(cursor)) = (ports.get(from), window.cursor_position()) {
            let a = to_world(node_center(g, c), window);
            let b = to_world(cursor, window);
            gizmos.linestrip_2d(curve(a, b), PREVIEW_COLOR);
            gizmos.circle_2d(Isometry2d::from_translation(b), 4.0, PREVIEW_COLOR);
        }
    }
}
