// src/ui/toasts.rs
//
// Short-lived notifications stacked at the top of the lab bench: new discoveries, unlocked
// vessels, milestone messages, and "no reaction" hints. Anything can queue one through
// `ResMut<Toasts>`; `spawn_toasts_system` turns the queue into UI and `fade_toasts_system`
// slides them in and ages them out.
use bevy::prelude::*;

use crate::resources::ui_fonts::UiFonts;
use crate::ui::settings::Settings;
use crate::ui::theme;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum ToastKind {
    Discovery,
    Milestone,
    Hint,
}

impl ToastKind {
    fn accent(self) -> Color {
        match self {
            ToastKind::Discovery => theme::GREEN,
            ToastKind::Milestone => theme::GOLD,
            ToastKind::Hint => theme::CYAN,
        }
    }
    fn icon(self) -> &'static str {
        match self {
            ToastKind::Discovery => "flask",
            ToastKind::Milestone => "spark",
            ToastKind::Hint => "info",
        }
    }
    fn lifetime(self) -> f32 {
        match self {
            ToastKind::Discovery => 4.0,
            ToastKind::Milestone => 6.0,
            ToastKind::Hint => 4.5,
        }
    }
}

#[derive(Resource, Default)]
pub struct Toasts(pub Vec<(ToastKind, String)>);

impl Toasts {
    pub fn push(&mut self, kind: ToastKind, text: impl Into<String>) {
        self.0.push((kind, text.into()));
    }
}

#[derive(Component)]
pub struct ToastStack;

#[derive(Component)]
pub struct Toast {
    age: f32,
    lifetime: f32,
}

const MAX_VISIBLE: usize = 4;

pub fn spawn_toast_stack(mut commands: Commands) {
    commands.spawn((
        ToastStack,
        GlobalZIndex(900),
        Pickable::IGNORE,
        // bottom-right of the bench, just above the shelf where discoveries land; newest
        // at the bottom, older ones rising above it
        Node {
            position_type: PositionType::Absolute,
            right: Val::Px(theme::SIDEBAR_W + 14.0),
            bottom: Val::Px(theme::DOCK_H + 14.0),
            width: Val::Px(460.0),
            flex_direction: FlexDirection::Column,
            align_items: AlignItems::FlexEnd,
            row_gap: Val::Px(6.0),
            ..default()
        },
        Name::new("ToastStack"),
    ));
}

pub fn spawn_toasts_system(
    mut commands: Commands,
    mut toasts: ResMut<Toasts>,
    settings: Option<Res<Settings>>,
    fonts: Option<Res<UiFonts>>,
    assets: Res<AssetServer>,
    stack_q: Query<(Entity, Option<&Children>), With<ToastStack>>,
) {
    if toasts.0.is_empty() {
        return;
    }
    if settings.as_ref().is_some_and(|s| !s.notifications) {
        toasts.0.clear();
        return;
    }
    let (Some(fonts), Ok((stack, children))) = (fonts, stack_q.single()) else { return };

    // Drop the oldest visible toasts if the queue would overflow the stack.
    let visible = children.map(|c| c.len()).unwrap_or(0);
    let incoming = toasts.0.len().min(MAX_VISIBLE);
    let excess = (visible + incoming).saturating_sub(MAX_VISIBLE);
    if let Some(children) = children {
        for child in children.iter().take(excess) {
            commands.entity(child).despawn();
        }
    }

    let queued: Vec<(ToastKind, String)> = toasts.0.drain(..).collect();
    let skip = queued.len().saturating_sub(MAX_VISIBLE);
    commands.entity(stack).with_children(|parent| {
        for (kind, text) in queued.into_iter().skip(skip) {
            let accent = kind.accent();
            parent
                .spawn((
                    Toast { age: 0.0, lifetime: kind.lifetime() },
                    Pickable::IGNORE,
                    Node {
                        padding: UiRect::new(Val::Px(12.0), Val::Px(16.0), Val::Px(9.0), Val::Px(9.0)),
                        border: UiRect::new(Val::Px(4.0), Val::Px(1.0), Val::Px(1.0), Val::Px(1.0)),
                        column_gap: Val::Px(10.0),
                        align_items: AlignItems::Center,
                        max_width: Val::Percent(100.0),
                        ..default()
                    },
                    BorderRadius::all(Val::Px(theme::R_MD)),
                    BackgroundColor(theme::mix(theme::SURFACE, accent, 0.10)),
                    BorderColor {
                        left: accent,
                        top: accent.with_alpha(0.35),
                        right: accent.with_alpha(0.35),
                        bottom: accent.with_alpha(0.35),
                    },
                    theme::shadow(18.0, 6.0, 0.5),
                    UiTransform::from_translation(Val2::px(0.0, 10.0)),
                ))
                .with_children(|t| {
                    t.spawn(theme::icon(&assets, kind.icon(), 18.0, accent));
                    t.spawn((
                        Text::new(text),
                        TextFont { font: fonts.semibold.clone(), font_size: 14.0, ..default() },
                        TextColor(theme::TEXT),
                        TextLayout::new_with_linebreak(LineBreak::WordBoundary),
                        Node { max_width: Val::Px(400.0), ..default() },
                        Pickable::IGNORE,
                    ));
                });
        }
    });
}

/// Age toasts: slide them in, fade them over their last second, despawn them when they expire.
pub fn fade_toasts_system(
    mut commands: Commands,
    time: Res<Time>,
    mut toasts: Query<(Entity, &mut Toast, &mut BackgroundColor, &mut BorderColor, &mut UiTransform, &Children)>,
    mut texts: Query<&mut TextColor>,
    mut images: Query<&mut ImageNode>,
) {
    for (entity, mut toast, mut bg, mut border, mut tf, children) in &mut toasts {
        toast.age += time.delta_secs();
        if toast.age >= toast.lifetime {
            commands.entity(entity).despawn();
            continue;
        }
        let slide = (toast.age / 0.18).min(1.0);
        tf.translation = Val2::px(0.0, 10.0 * (1.0 - slide));
        let alpha = (toast.lifetime - toast.age).clamp(0.0, 1.0).min(slide);
        bg.0.set_alpha(alpha * 0.97);
        let b = &mut *border;
        b.left.set_alpha(alpha);
        b.top.set_alpha(alpha * 0.35);
        b.right.set_alpha(alpha * 0.35);
        b.bottom.set_alpha(alpha * 0.35);
        for child in children.iter() {
            if let Ok(mut tc) = texts.get_mut(child) {
                tc.0.set_alpha(alpha);
            }
            if let Ok(mut img) = images.get_mut(child) {
                img.color.set_alpha(alpha);
            }
        }
    }
}
