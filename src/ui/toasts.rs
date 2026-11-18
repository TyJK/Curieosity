// src/ui/toasts.rs
//
// Short-lived notifications stacked at the top of the lab bench: new discoveries, unlocked
// vessels, milestone messages, and "no reaction" hints. Anything can queue one through
// `ResMut<Toasts>`; `spawn_toasts_system` turns the queue into UI and `fade_toasts_system`
// slides them in and ages them out.
//
// The discoveries and milestones also go into the journal (kept in the save), which the
// bell in the header opens: every past notification, newest first. Hints about the reaction
// in hand are left out of it.
use crate::ui::{Button, Clicked};
use bevy::prelude::*;

use crate::resources::ui_fonts::UiFonts;
use crate::ui::settings::Settings;
use crate::ui::theme;

#[derive(Clone, Copy, PartialEq, Eq, Debug, Hash)]
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

/// One past notification.
#[derive(Clone, Debug, PartialEq)]
pub struct JournalEntry {
    pub kind: ToastKind,
    pub text: String,
}

/// The past discoveries and milestones, oldest first (the save keeps the latest ones).
#[derive(Resource, Default, Debug)]
pub struct Journal(pub Vec<JournalEntry>);

/// How many entries the journal keeps.
pub const JOURNAL_MAX: usize = 300;

impl Journal {
    pub fn push(&mut self, kind: ToastKind, text: impl Into<String>) {
        self.0.push(JournalEntry { kind, text: text.into() });
        let over = self.0.len().saturating_sub(JOURNAL_MAX);
        if over > 0 {
            self.0.drain(..over);
        }
    }

    /// As the save writes it: (kind, text) pairs.
    pub fn to_pairs(&self) -> Vec<(String, String)> {
        self.0.iter().map(|e| (format!("{:?}", e.kind), e.text.clone())).collect()
    }

    /// From the save (an entry of a kind this build doesn't know is read as a milestone).
    pub fn from_pairs(pairs: &[(String, String)]) -> Self {
        let mut j = Journal::default();
        for (k, t) in pairs {
            let kind = if k == "Discovery" { ToastKind::Discovery } else { ToastKind::Milestone };
            j.push(kind, t.clone());
        }
        j
    }
}

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
    /// what it says: the same words again keep this one up instead of stacking a copy
    text: String,
}

const MAX_VISIBLE: usize = 4;

/// How many pop-ups fit on the bench right now: four on a tall screen, fewer on a phone so
/// the stack never climbs over the header. Kept by the next-step card's system, which
/// knows how much room it takes itself.
#[derive(Resource)]
pub struct ToastRoom(pub usize);

impl Default for ToastRoom {
    fn default() -> Self {
        Self(MAX_VISIBLE)
    }
}

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
    room: Res<ToastRoom>,
    mut journal: ResMut<Journal>,
    mut showing: Query<&mut Toast>,
) {
    let cap = room.0.clamp(1, MAX_VISIBLE);
    // the room shrank (a smaller screen, a bigger interface): the oldest go first
    if let Ok((_, Some(children))) = stack_q.single() {
        for child in children.iter().take(children.len().saturating_sub(cap)) {
            commands.entity(child).try_despawn();
        }
    }
    if toasts.0.is_empty() {
        return;
    }
    // the journal keeps every discovery and milestone, pop-ups or not
    for (kind, text) in &toasts.0 {
        if *kind != ToastKind::Hint {
            journal.push(*kind, text.clone());
        }
    }
    if settings.as_ref().is_some_and(|s| !s.notifications) {
        toasts.0.clear();
        return;
    }
    // discovery cards announce discoveries themselves (ui::discovery_card)
    if settings.as_ref().is_none_or(|s| s.discovery_cards) {
        toasts.0.retain(|(kind, _)| *kind != ToastKind::Discovery);
        if toasts.0.is_empty() {
            return;
        }
    }
    // the same words as a pop-up still up (a port tapped twice): it starts its time over,
    // still sliding in if it hasn't yet, and no copy stacks under it
    toasts.0.retain(|(_, text)| {
        let Some(mut t) = showing.iter_mut().find(|t| t.text == *text && t.age < t.lifetime - 1.0) else {
            return true;
        };
        t.age = t.age.min(0.3);
        false
    });
    if toasts.0.is_empty() {
        return;
    }
    let (Some(fonts), Ok((stack, children))) = (fonts, stack_q.single()) else { return };

    // Drop the oldest visible toasts if the queue would overflow the stack.
    let visible = children.map(|c| c.len()).unwrap_or(0).min(cap);
    let incoming = toasts.0.len().min(cap);
    let excess = (visible + incoming).saturating_sub(cap);
    if let Some(children) = children {
        for child in children.iter().take(excess) {
            commands.entity(child).try_despawn();
        }
    }

    let queued = std::mem::take(&mut toasts.0);
    let skip = queued.len().saturating_sub(cap);
    commands.entity(stack).with_children(|parent| {
        for (kind, text) in queued.into_iter().skip(skip) {
            let accent = kind.accent();
            parent
                .spawn((
                    Toast { age: 0.0, lifetime: kind.lifetime(), text: text.clone() },
                    Pickable::IGNORE,
                    Node {
                        border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                        padding: UiRect::new(Val::Px(12.0), Val::Px(16.0), Val::Px(9.0), Val::Px(9.0)),
                        border: UiRect::new(Val::Px(4.0), Val::Px(1.0), Val::Px(1.0), Val::Px(1.0)),
                        column_gap: Val::Px(10.0),
                        align_items: AlignItems::Center,
                        max_width: Val::Percent(100.0),
                        ..default()
                    },
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
                        TextFont { font: fonts.semibold.clone().into(), font_size: FontSize::Px(14.0), ..default() },
                        TextColor(theme::TEXT),
                        TextLayout::linebreak(LineBreak::WordBoundary),
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
            commands.entity(entity).try_despawn();
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

// ---------------------------------------------------------------------------------------
// The journal: every past notification
// ---------------------------------------------------------------------------------------
#[derive(Resource, Default)]
pub struct JournalUi {
    pub open: bool,
}

#[derive(Component)]
pub struct JournalRoot;
#[derive(Component)]
pub struct JournalBackdrop;
#[derive(Component)]
pub struct JournalClose;
/// The list (rebuilt while the dialog is open and the journal changes).
#[derive(Component)]
pub struct JournalList;
/// One entry in the list (the checks read them).
#[derive(Component)]
pub struct JournalRow(pub usize);

pub fn spawn_journal(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    commands
        .spawn((
            JournalRoot,
            // the keyboard stays inside the dialog while it shows
            crate::ui::focus::FocusCover,
            GlobalZIndex(940),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(0.0),
                bottom: Val::Px(0.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                display: Display::None,
                ..default()
            },
            Name::new("Journal"),
        ))
        .with_children(|root| {
            root.spawn((
                JournalBackdrop,
                Button,
                crate::ui::focus::NoFocus,
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    right: Val::Px(0.0),
                    top: Val::Px(0.0),
                    bottom: Val::Px(0.0),
                    ..default()
                },
                BackgroundColor(Color::srgba(0.0, 0.0, 0.02, 0.62)),
            ));
            root.spawn((
                Node {
                    border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    width: Val::Px(620.0),
                    max_width: Val::Percent(94.0),
                    max_height: Val::Percent(90.0),
                    flex_direction: FlexDirection::Column,
                    padding: UiRect::all(Val::Px(20.0)),
                    row_gap: Val::Px(10.0),
                    border: UiRect::all(Val::Px(1.0)),
                    overflow: Overflow::clip(),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE_STRONG),
                theme::shadow(40.0, 14.0, 0.6),
                Pickable::default(),
            ))
            .with_children(|dialog| {
                dialog
                    .spawn(Node {
                        justify_content: JustifyContent::SpaceBetween,
                        align_items: AlignItems::Center,
                        flex_shrink: 0.0,
                        ..default()
                    })
                    .with_children(|h| {
                        h.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Center, ..default() })
                            .with_children(|t| {
                                t.spawn(theme::icon(&assets, "bell", 22.0, theme::GOLD));
                                t.spawn(theme::label(
                                    &fonts,
                                    "Notifications",
                                    theme::XL,
                                    theme::Weight::Semibold,
                                    theme::TEXT,
                                ));
                            });
                        theme::spawn_icon_button(h, &assets, "close", 32.0, theme::TEXT_2, JournalClose);
                    });
                dialog.spawn(theme::label(
                    &fonts,
                    "Every discovery and milestone so far, newest first.",
                    theme::XS,
                    theme::Weight::Regular,
                    theme::TEXT_3,
                ));
                dialog.spawn((
                    JournalList,
                    Node {
                        flex_direction: FlexDirection::Column,
                        row_gap: Val::Px(6.0),
                        flex_shrink: 1.0,
                        min_height: Val::Px(0.0),
                        overflow: Overflow::scroll_y(),
                        ..default()
                    },
                    ScrollPosition::default(),
                    Pickable::default(),
                ));
            });
        });
}

pub fn journal_input_system(
    mut ui: ResMut<JournalUi>,
    closers: Query<(), (With<Clicked>, Or<(With<JournalClose>, With<JournalBackdrop>)>)>,
) {
    if !closers.is_empty() {
        ui.open = false;
    }
}

/// Shows the dialog while open, and lists the journal newest first.
pub fn journal_view_system(
    mut commands: Commands,
    ui: Res<JournalUi>,
    journal: Res<Journal>,
    fonts: Option<Res<UiFonts>>,
    assets: Res<AssetServer>,
    mut root: Query<&mut Node, With<JournalRoot>>,
    mut list: Query<(Entity, &mut ScrollPosition), With<JournalList>>,
) {
    if let Ok(mut n) = root.single_mut() {
        let d = if ui.open { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if !ui.open || !(ui.is_changed() || journal.is_changed()) {
        return;
    }
    let (Some(fonts), Ok((list, mut scroll))) = (fonts, list.single_mut()) else { return };
    if ui.is_changed() {
        scroll.0 = Vec2::ZERO;
    }
    commands.entity(list).despawn_children();
    commands.entity(list).with_children(|l| {
        if journal.0.is_empty() {
            l.spawn(theme::label(
                &fonts,
                "Nothing yet: your discoveries will be listed here.",
                theme::SM,
                theme::Weight::Regular,
                theme::TEXT_3,
            ));
        }
        for (i, e) in journal.0.iter().enumerate().rev() {
            let accent = e.kind.accent();
            l.spawn((
                JournalRow(i),
                Node {
                    border_radius: BorderRadius::all(Val::Px(theme::R_SM)),
                    flex_shrink: 0.0,
                    column_gap: Val::Px(10.0),
                    align_items: AlignItems::Center,
                    padding: UiRect::new(Val::Px(10.0), Val::Px(10.0), Val::Px(6.0), Val::Px(6.0)),
                    border: UiRect::left(Val::Px(3.0)),
                    ..default()
                },
                BackgroundColor(theme::mix(theme::RAISED, accent, 0.06)),
                BorderColor::all(accent),
            ))
            .with_children(|r| {
                r.spawn(theme::icon(&assets, e.kind.icon(), 16.0, accent));
                r.spawn((
                    Text::new(e.text.clone()),
                    TextFont { font: fonts.main.clone().into(), font_size: FontSize::Px(theme::SM), ..default() },
                    TextColor(theme::TEXT),
                    TextLayout::linebreak(LineBreak::WordBoundary),
                    Node { flex_shrink: 1.0, ..default() },
                ));
            });
        }
    });
}
