// src/ui/reaction_canvas.rs
use crate::components::ui_markers::{CanvasScrollingPane, ReactionCanvasRoot};
use crate::components::DropTarget;
use crate::UiCameraEntity;
use bevy::prelude::*;
use bevy::ui::UiTargetCamera; // Standard component for multi-camera UI

pub fn spawn_reaction_canvas(mut commands: Commands, ui_camera_res: Option<Res<UiCameraEntity>>) {
    let Some(camera_res) = ui_camera_res else {
        error!("UiCameraEntity missing! Canvas cannot target specific camera.");
        return;
    };

    commands
        .spawn((
            ReactionCanvasRoot,
            DropTarget,
            // FIX: Force this UI to only appear on the background camera
            UiTargetCamera(camera_res.0),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                top: Val::Px(crate::ui::theme::HEADER_H),
                right: Val::Px(crate::ui::theme::SIDEBAR_W),
                bottom: Val::Px(crate::ui::theme::DOCK_H),
                overflow: Overflow::scroll(),
                ..default()
            },
            BackgroundColor(crate::ui::theme::BENCH),
            Name::new("ReactionCanvas"),
            // Keep these for layout calculation
            ComputedNode::default(),
            GlobalTransform::default(),
            Transform::default(),
            Visibility::default(),
            InheritedVisibility::default(),
            ViewVisibility::default(),
        ))
        .with_children(|parent| {
            parent.spawn((
                CanvasScrollingPane,
                Pickable::default(),
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    top: Val::Px(0.0),
                    width: Val::Px(5000.0),
                    height: Val::Px(5000.0),
                    ..default()
                },
                Name::new("ScrollingPane"),
                ComputedNode::default(),
                GlobalTransform::default(),
                Transform::default(),
                Visibility::default(),
                InheritedVisibility::default(),
                ViewVisibility::default(),
            ));
        });
}
