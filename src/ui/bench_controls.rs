// src/ui/bench_controls.rs
//
// The bench's own controls, along its bottom edge: Empty and Remove on the left, Add vessel
// in the middle, one big React on the right. Each acts on the selected vessel: the one last
// placed, tapped, moved or filled, wearing an outline in its colour (a tap on the empty
// bench lets go of it). With no vessel selected, React reacts every vessel that holds
// something, upstream first so the links carry each product on to the next, and Empty and
// Remove ask first, then do it to every vessel.
//
// Also the bench's small "are you sure" pop-up, and the cover the lab's own pop-ups put
// over the bench (the vessel links are drawn on top of everything, so they step aside).
use bevy::prelude::*;

use crate::components::ui_markers::{
    InCatalystZone, InVessel, ProcessVessel, ReactionCanvasRoot, ReactionLink, VesselCard,
};
use crate::resources::ui_fonts::UiFonts;
use crate::systems::drag_drop::ActiveVessel;
use crate::systems::reaction_check::{process_color, CheckVesselReaction, EquationText};
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::ui::{Button, Clicked, Look};

/// The React button's height; Empty, Remove and Add vessel are a little shorter.
pub const BAR_H: f32 = 58.0;
const SMALL_H: f32 = 52.0;
/// The controls' distance from the bench's edges.
pub const BAR_GAP: f32 = 12.0;
/// How far above the shelf the bench's pop-ups (the Hint button, notifications) sit, so
/// they clear the controls.
pub const BAR_LIFT: f32 = BAR_GAP + BAR_H + 10.0;
/// Below this bench width (interface pixels) Empty and Remove show their icons only.
const NARROW_BENCH: f32 = 640.0;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum BenchAction {
    React,
    Empty,
    Remove,
}

/// One of the three buttons.
#[derive(Component, Clone, Copy, Debug)]
pub struct BenchButton(pub BenchAction);
/// A button's label (its words change with the selection).
#[derive(Component, Clone, Copy, Debug)]
pub struct BenchButtonLabel(pub BenchAction);
/// The groups at the bench's bottom corners and in the middle.
#[derive(Component, Clone, Copy, PartialEq, Eq, Debug)]
pub enum BenchBar {
    Left,
    Middle,
    Right,
}

/// What the pop-up is asking before it does it.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum BulkAsk {
    EmptyAll,
    RemoveAll,
}

/// The question the pop-up is asking, if it is up.
#[derive(Resource, Default, Debug)]
pub struct Confirm(pub Option<BulkAsk>);

#[derive(Component)]
pub struct ConfirmRoot;
#[derive(Component)]
pub struct ConfirmText;
#[derive(Component)]
pub struct ConfirmYes;
#[derive(Component)]
pub struct ConfirmYesLabel;
#[derive(Component)]
pub struct ConfirmNo;

pub struct BenchControlsPlugin;

impl Plugin for BenchControlsPlugin {
    fn build(&self, app: &mut App) {
        // (the pop-up itself is spawned with the rest of the interface, once the fonts are in)
        app.init_resource::<Confirm>().add_systems(
            Update,
            (spawn_bench_controls, bench_controls_input_system, confirm_system, bench_controls_view_system).chain(),
        );
    }
}

/// The vessels at the start of what holds something: every vessel with contents that no
/// other vessel with contents feeds from further up its links. Reacting these, the links
/// carry the products on and each vessel downstream reacts as they arrive
/// (propagate_products_system). Vessels in a loop with each other all start. In the order
/// they were made. Pure, so it is unit-tested below.
pub fn react_all_order(filled: &[Entity], links: &[(Entity, Entity)]) -> Vec<Entity> {
    let upstream = |v: Entity| -> Vec<Entity> {
        let mut seen = Vec::new();
        let mut todo = vec![v];
        while let Some(x) = todo.pop() {
            for &(from, to) in links {
                if to == x && from != v && !seen.contains(&from) {
                    seen.push(from);
                    todo.push(from);
                }
            }
        }
        seen
    };
    let mut starts: Vec<Entity> = filled
        .iter()
        .copied()
        .filter(|&v| {
            let up = upstream(v);
            // waits for a vessel with contents strictly above it (not one in a loop with it)
            !up.iter().any(|u| filled.contains(u) && !upstream(*u).contains(&v))
        })
        .collect();
    starts.sort_by_key(|v| v.index().index());
    starts.dedup();
    starts
}

/// Take everything out of a vessel (its contents and its catalyst) and reset its status.
pub fn empty_vessel<F: bevy::ecs::query::QueryFilter>(
    commands: &mut Commands,
    vessel: Entity,
    chips: &Query<(Entity, &InVessel)>,
    catalysts: &Query<(Entity, &InCatalystZone)>,
    status: &mut Query<(&mut Text, &mut TextColor, &ChildOf), F>,
) {
    for (e, iv) in chips {
        if iv.0 == vessel {
            commands.entity(e).try_despawn();
        }
    }
    for (e, iz) in catalysts {
        if iz.0 == vessel {
            commands.entity(e).try_despawn();
        }
    }
    for (mut t, mut c, parent) in status.iter_mut() {
        if parent.parent() == vessel {
            t.0 = crate::systems::reaction_check::READY_TEXT.to_string();
            c.0 = theme::TEXT_3;
        }
    }
}

/// Take a vessel off the bench, with its links.
pub fn remove_vessel(commands: &mut Commands, vessel: Entity, links: &Query<(Entity, &ReactionLink)>) {
    commands.entity(vessel).try_despawn();
    for (e, l) in links {
        if l.from_vessel == vessel || l.to_vessel == vessel {
            commands.entity(e).try_despawn();
        }
    }
}

fn small_button(kind: Kind) -> impl Bundle {
    theme::button(
        kind,
        Node {
            height: Val::Px(SMALL_H),
            min_width: Val::Px(SMALL_H),
            padding: UiRect::horizontal(Val::Px(14.0)),
            column_gap: Val::Px(8.0),
            align_items: AlignItems::Center,
            justify_content: JustifyContent::Center,
            ..default()
        },
        theme::R_MD,
    )
}

/// The three groups, once the bench exists.
pub fn spawn_bench_controls(
    mut commands: Commands,
    fonts: Option<Res<UiFonts>>,
    assets: Res<AssetServer>,
    roots: Query<Entity, Added<ReactionCanvasRoot>>,
) {
    let Some(fonts) = fonts else { return };
    for root in &roots {
        commands.entity(root).with_children(|r| {
            // bottom left: Empty and Remove
            r.spawn((
                BenchBar::Left,
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(BAR_GAP),
                    bottom: Val::Px(BAR_GAP),
                    height: Val::Px(BAR_H),
                    align_items: AlignItems::Center,
                    column_gap: Val::Px(8.0),
                    ..default()
                },
                Pickable::IGNORE,
                Name::new("BenchBarLeft"),
            ))
            .with_children(|g| {
                for (action, icon, text, tip) in [
                    (
                        BenchAction::Empty,
                        "clear",
                        "Empty",
                        "Take everything out of the selected vessel. With none selected, empty them all.",
                    ),
                    (
                        BenchAction::Remove,
                        "close",
                        "Remove",
                        "Take the selected vessel off the bench. With none selected, clear the bench.",
                    ),
                ] {
                    g.spawn((
                        small_button(Kind::Secondary),
                        BenchButton(action),
                        theme::shadow(12.0, 4.0, 0.45),
                        crate::ui::onboarding::Tip::Text(text, tip),
                    ))
                    .with_children(|b| {
                        b.spawn(theme::icon(&assets, icon, 20.0, theme::TEXT));
                        b.spawn((
                            BenchButtonLabel(action),
                            theme::label(&fonts, text, theme::MD, Weight::Semibold, theme::TEXT),
                            TextLayout::no_wrap(),
                            Pickable::IGNORE,
                        ));
                    });
                }
            });
            // the middle: Add vessel
            r.spawn((
                BenchBar::Middle,
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    right: Val::Px(0.0),
                    bottom: Val::Px(BAR_GAP),
                    height: Val::Px(BAR_H),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    ..default()
                },
                Pickable::IGNORE,
                Name::new("BenchBarMiddle"),
            ))
            .with_children(|g| {
                g.spawn((
                    small_button(Kind::Secondary),
                    crate::ui::process_toolbar::AddVesselButton,
                    theme::shadow(12.0, 4.0, 0.45),
                    crate::ui::onboarding::Tip::Text("Add a vessel", "Pick a vessel to put on the bench."),
                ))
                .with_children(|b| {
                    b.spawn(theme::icon(&assets, "plus", 20.0, theme::CYAN));
                    b.spawn((
                        theme::label(&fonts, "Vessel", theme::MD, Weight::Semibold, theme::TEXT),
                        TextLayout::no_wrap(),
                        Pickable::IGNORE,
                    ));
                });
            });
            // bottom right: React
            r.spawn((
                BenchBar::Right,
                Node {
                    position_type: PositionType::Absolute,
                    right: Val::Px(BAR_GAP),
                    bottom: Val::Px(BAR_GAP),
                    height: Val::Px(BAR_H),
                    align_items: AlignItems::Center,
                    ..default()
                },
                Pickable::IGNORE,
                Name::new("BenchBarRight"),
            ))
            .with_children(|g| {
                g.spawn((
                    theme::button(
                        Kind::Accent(theme::CYAN),
                        Node {
                            height: Val::Px(BAR_H),
                            min_width: Val::Px(150.0),
                            padding: UiRect::horizontal(Val::Px(24.0)),
                            column_gap: Val::Px(9.0),
                            align_items: AlignItems::Center,
                            justify_content: JustifyContent::Center,
                            ..default()
                        },
                        theme::R_MD,
                    ),
                    BenchButton(BenchAction::React),
                    theme::shadow(16.0, 5.0, 0.55),
                    crate::ui::onboarding::Tip::Text(
                        "React",
                        "React the selected vessel. With none selected, react every vessel that holds something, upstream first.",
                    ),
                ))
                .with_children(|b| {
                    b.spawn(theme::icon(&assets, "spark", 20.0, theme::TEXT));
                    b.spawn((
                        BenchButtonLabel(BenchAction::React),
                        theme::label(&fonts, "React", theme::LG, Weight::Semibold, theme::TEXT),
                        TextLayout::no_wrap(),
                        Pickable::IGNORE,
                    ));
                });
            });
        });
    }
}

/// What the buttons would do right now.
#[derive(Clone, PartialEq, Debug)]
pub struct BarState {
    /// the selected vessel, and its colour
    target: Option<(Entity, Color)>,
    react: bool,
    empty: bool,
    remove: bool,
    narrow: bool,
    /// a phone's keyboard is up for the shelf search: Empty and Remove show their icons only
    typing: bool,
}

#[allow(clippy::type_complexity)]
fn bar_state(
    active: &ActiveVessel,
    cards: &Query<(Entity, &ProcessVessel), With<VesselCard>>,
    chips: &Query<(Entity, &InVessel)>,
    catalysts: &Query<(Entity, &InCatalystZone)>,
    narrow: bool,
    typing: bool,
) -> BarState {
    let target = active.0.and_then(|e| cards.get(e).ok()).map(|(e, pv)| (e, process_color(&pv.process)));
    let holds = |v: Entity| chips.iter().any(|(_, iv)| iv.0 == v);
    let any_held = || chips.iter().any(|(_, iv)| cards.contains(iv.0));
    let has_catalyst = |v: Entity| catalysts.iter().any(|(_, iz)| iz.0 == v);
    match target {
        Some((v, _)) => {
            BarState { target, react: holds(v), empty: holds(v) || has_catalyst(v), remove: true, narrow, typing }
        }
        None => BarState {
            target,
            react: any_held(),
            empty: any_held() || catalysts.iter().any(|(_, iz)| cards.contains(iz.0)),
            remove: !cards.is_empty(),
            narrow,
            typing,
        },
    }
}

/// The buttons' words, colours and whether they can be used, kept in step with the bench.
#[allow(clippy::type_complexity)]
pub fn bench_controls_view_system(
    active: Res<ActiveVessel>,
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    ui_scale: Res<UiScale>,
    cards: Query<(Entity, &ProcessVessel), With<VesselCard>>,
    chips: Query<(Entity, &InVessel)>,
    catalysts: Query<(Entity, &InCatalystZone)>,
    mut buttons: Query<(
        &BenchButton,
        &mut Skin,
        &bevy::picking::hover::Hovered,
        Has<bevy::ui::Pressed>,
        &mut BackgroundColor,
        &mut BorderColor,
    )>,
    mut labels: Query<(&BenchButtonLabel, &mut Text, &mut Node, &mut TextColor)>,
    typing: (Res<crate::ui::inventory::ShelfSearch>, Res<crate::platform::SoftKeyboard>),
    mut last: Local<Option<BarState>>,
) {
    let width = windows.single().map(|w| w.width() / ui_scale.0.max(0.01)).unwrap_or(1280.0);
    let on_keys = typing.1 .0 && typing.0.typing;
    let state = bar_state(&active, &cards, &chips, &catalysts, width < NARROW_BENCH, on_keys);
    if last.as_ref() == Some(&state) {
        return;
    }
    let all = state.target.is_none();
    for (b, mut skin, hovered, pressed, mut bg, mut border) in &mut buttons {
        let kind = match b.0 {
            BenchAction::React if state.react => Kind::Accent(state.target.map_or(theme::CYAN, |t| t.1)),
            BenchAction::Empty if state.empty => Kind::Secondary,
            BenchAction::Remove if state.remove => Kind::Secondary,
            _ => Kind::Disabled,
        };
        if skin.kind != kind {
            skin.kind = kind;
            let (b, l) = skin.colors(Look::of(hovered, pressed));
            bg.0 = b;
            *border = BorderColor::all(l);
        }
    }
    for (l, mut text, mut node, mut color) in &mut labels {
        let (words, on) = match l.0 {
            BenchAction::React => (if all { "React all" } else { "React" }, state.react),
            BenchAction::Empty => (if all { "Empty all" } else { "Empty" }, state.empty),
            BenchAction::Remove => (if all { "Remove all" } else { "Remove" }, state.remove),
        };
        if text.0 != words {
            text.0 = words.to_string();
        }
        let c = if on { theme::TEXT } else { theme::TEXT_3 };
        if color.0 != c {
            color.0 = c;
        }
        // on a narrow bench, or over a phone's keyboard, Empty and Remove are their icons
        let shown = l.0 == BenchAction::React || !(state.narrow || state.typing);
        let d = if shown { Display::Flex } else { Display::None };
        if node.display != d {
            node.display = d;
        }
    }
    *last = Some(state);
}

/// React, Empty and Remove.
#[allow(clippy::too_many_arguments)]
pub fn bench_controls_input_system(
    mut commands: Commands,
    pressed: Query<&BenchButton, (With<Clicked>, With<Button>)>,
    active: Res<ActiveVessel>,
    cards: Query<(Entity, &ProcessVessel), With<VesselCard>>,
    chips: Query<(Entity, &InVessel)>,
    catalysts: Query<(Entity, &InCatalystZone)>,
    links: Query<(Entity, &ReactionLink)>,
    mut status: Query<(&mut Text, &mut TextColor, &ChildOf), With<EquationText>>,
    mut confirm: ResMut<Confirm>,
    mut react: MessageWriter<CheckVesselReaction>,
) {
    for b in &pressed {
        let state = bar_state(&active, &cards, &chips, &catalysts, false, false);
        let target = state.target.map(|t| t.0);
        match b.0 {
            BenchAction::React if state.react => match target {
                Some(v) => {
                    react.write(CheckVesselReaction(v));
                }
                None => {
                    let mut filled: Vec<Entity> =
                        chips.iter().map(|(_, iv)| iv.0).filter(|v| cards.contains(*v)).collect();
                    filled.sort_by_key(|v| v.index().index());
                    filled.dedup();
                    let pairs: Vec<(Entity, Entity)> =
                        links.iter().map(|(_, l)| (l.from_vessel, l.to_vessel)).collect();
                    for v in react_all_order(&filled, &pairs) {
                        react.write(CheckVesselReaction(v));
                    }
                }
            },
            BenchAction::Empty if state.empty => match target {
                Some(v) => empty_vessel(&mut commands, v, &chips, &catalysts, &mut status),
                None => confirm.0 = Some(BulkAsk::EmptyAll),
            },
            BenchAction::Remove if state.remove => match target {
                Some(v) => remove_vessel(&mut commands, v, &links),
                None => confirm.0 = Some(BulkAsk::RemoveAll),
            },
            _ => {}
        }
    }
}

/// The pop-up: a backdrop over the lab and a small card in the middle.
pub fn spawn_confirm(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    commands
        .spawn((
            ConfirmRoot,
            GlobalZIndex(1500),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(0.0),
                bottom: Val::Px(0.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                padding: UiRect::all(Val::Px(16.0)),
                display: Display::None,
                ..default()
            },
            BackgroundColor(Color::srgba(0.0, 0.0, 0.02, 0.6)),
            // a tap on the backdrop is a "no", and nothing under it hears it
            Pickable::default(),
            Button,
            crate::ui::focus::NoFocus,
            ConfirmNo,
            Name::new("Confirm"),
        ))
        .with_children(|root| {
            root.spawn((
                Node {
                    width: Val::Px(360.0),
                    max_width: Val::Percent(100.0),
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(16.0),
                    padding: UiRect::all(Val::Px(20.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE_STRONG),
                theme::shadow(28.0, 10.0, 0.6),
                // taps on the card itself go nowhere
                Pickable::default(),
                Button,
                crate::ui::focus::NoFocus,
            ))
            .with_children(|card| {
                card.spawn((ConfirmText, theme::para(&fonts, "", theme::MD, theme::TEXT, Val::Px(320.0))));
                card.spawn(Node { justify_content: JustifyContent::FlexEnd, column_gap: Val::Px(10.0), ..default() })
                    .with_children(|row| {
                        row.spawn((small_button(Kind::Secondary), ConfirmNo)).with_children(|b| {
                            b.spawn((
                                theme::label(&fonts, "Cancel", theme::SM, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                        });
                        row.spawn((small_button(Kind::Danger), ConfirmYes)).with_children(|b| {
                            b.spawn(theme::icon(&assets, "close", 14.0, theme::TEXT));
                            b.spawn((
                                ConfirmYesLabel,
                                theme::label(&fonts, "", theme::SM, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                        });
                    });
            });
        });
}

/// Shows the question, and does it on yes.
#[allow(clippy::too_many_arguments)]
pub fn confirm_system(
    mut commands: Commands,
    mut confirm: ResMut<Confirm>,
    yes: Query<(), (With<Clicked>, With<ConfirmYes>)>,
    no: Query<(), (With<Clicked>, With<ConfirmNo>)>,
    cards: Query<Entity, With<VesselCard>>,
    chips: Query<(Entity, &InVessel)>,
    catalysts: Query<(Entity, &InCatalystZone)>,
    links: Query<(Entity, &ReactionLink)>,
    mut status: Query<
        (&mut Text, &mut TextColor, &ChildOf),
        (With<EquationText>, Without<ConfirmText>, Without<ConfirmYesLabel>),
    >,
    mut ui: (
        Query<&mut Node, With<ConfirmRoot>>,
        Query<&mut Text, (With<ConfirmText>, Without<EquationText>, Without<ConfirmYesLabel>)>,
        Query<&mut Text, (With<ConfirmYesLabel>, Without<EquationText>, Without<ConfirmText>)>,
    ),
) {
    if let Some(ask) = confirm.0 {
        if !yes.is_empty() {
            for v in &cards {
                match ask {
                    BulkAsk::EmptyAll => empty_vessel(&mut commands, v, &chips, &catalysts, &mut status),
                    BulkAsk::RemoveAll => {
                        commands.entity(v).try_despawn();
                    }
                }
            }
            if ask == BulkAsk::RemoveAll {
                for (e, _) in &links {
                    commands.entity(e).try_despawn();
                }
            }
            confirm.0 = None;
        } else if !no.is_empty() {
            confirm.0 = None;
        }
    }
    if !confirm.is_changed() {
        return;
    }
    let (mut root, mut text, mut yes_label) = (ui.0.reborrow(), ui.1.reborrow(), ui.2.reborrow());
    let n = cards.iter().count();
    if let Ok(mut node) = root.single_mut() {
        node.display = if confirm.0.is_some() { Display::Flex } else { Display::None };
    }
    let (question, button) = match confirm.0 {
        Some(BulkAsk::EmptyAll) => (
            format!(
                "Empty {}? Everything in {} goes back.",
                if n == 1 { "the vessel".to_string() } else { format!("all {n} vessels") },
                if n == 1 { "it" } else { "them" }
            ),
            "Empty all",
        ),
        Some(BulkAsk::RemoveAll) => (
            format!(
                "Take {} off the bench? {} links go with {}.",
                if n == 1 { "the vessel".to_string() } else { format!("all {n} vessels") },
                if n == 1 { "Its" } else { "Their" },
                if n == 1 { "it" } else { "them" }
            ),
            "Remove all",
        ),
        None => return,
    };
    if let Ok(mut t) = text.single_mut() {
        t.0 = question;
    }
    if let Ok(mut t) = yes_label.single_mut() {
        t.0 = button.to_string();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn e(world: &mut World, n: usize) -> Vec<Entity> {
        (0..n).map(|_| world.spawn_empty().id()).collect()
    }

    #[test]
    fn react_all_starts_upstream() {
        let mut w = World::new();
        let v = e(&mut w, 5);
        // 0 -> 1 -> 2, and 3 on its own; 4 is empty
        let links = [(v[0], v[1]), (v[1], v[2])];
        assert_eq!(react_all_order(&[v[0], v[1], v[2], v[3]], &links), vec![v[0], v[3]]);
        // an empty vessel upstream holds nothing back
        assert_eq!(react_all_order(&[v[1], v[2]], &links), vec![v[1]]);
        // fed through an empty vessel: still waits for the one at the top
        assert_eq!(react_all_order(&[v[0], v[2]], &links), vec![v[0]]);
        assert!(react_all_order(&[], &links).is_empty());
    }

    #[test]
    fn a_loop_reacts_together() {
        let mut w = World::new();
        let v = e(&mut w, 3);
        let links = [(v[0], v[1]), (v[1], v[0]), (v[1], v[2])];
        assert_eq!(react_all_order(&[v[0], v[1], v[2]], &links), vec![v[0], v[1]]);
    }
}
