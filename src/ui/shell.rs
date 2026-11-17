// src/ui/shell.rs
//
// The frame around everything: the header bar (logo, the four views, the current era, how
// much of the world has been discovered, settings), view switching and Esc, and the lab
// bench's decoration (dot grid, vignette, the "start here" hint on an empty bench).
use bevy::prelude::*;

use crate::components::ui_markers::{CanvasScrollingPane, ReactionCanvasRoot};
use crate::components::{Draggable, VesselCard};
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::codex::CodexState;
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::settings::{Settings, SettingsUi};
use crate::ui::tech_tree::TechTreeState;
use crate::ui::theme::{self, Kind, Skin, Weight};

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum View {
    Lab,
    Substances,
    Reactions,
    TechTree,
}

#[derive(Component)]
pub struct NavTab(pub View);
#[derive(Component)]
pub struct SettingsButton;
#[derive(Component)]
pub struct EraText;
#[derive(Component)]
pub struct CountText;
#[derive(Component)]
pub struct CountBar;
#[derive(Component)]
pub struct BenchGrid;
#[derive(Component)]
pub struct EmptyBenchHint;

pub fn current_view(codex: &CodexState, rlib: &ReactionLibState, tree: &TechTreeState) -> View {
    if codex.open {
        View::Substances
    } else if rlib.open {
        View::Reactions
    } else if tree.open {
        View::TechTree
    } else {
        View::Lab
    }
}

pub fn spawn_header(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((
            GlobalZIndex(700),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(0.0),
                height: Val::Px(theme::HEADER_H),
                align_items: AlignItems::Center,
                padding: UiRect::horizontal(Val::Px(14.0)),
                column_gap: Val::Px(18.0),
                border: UiRect::bottom(Val::Px(1.0)),
                ..default()
            },
            BackgroundGradient::from(LinearGradient::to_right(vec![
                ColorStop::auto(theme::mix(theme::SURFACE, theme::VIOLET, 0.10)),
                ColorStop::auto(theme::SURFACE),
                ColorStop::auto(theme::mix(theme::SURFACE, theme::CYAN, 0.06)),
            ])),
            BorderColor::all(theme::LINE),
            Name::new("Header"),
        ))
        .with_children(|h| {
            // brand
            h.spawn(Node {
                align_items: AlignItems::Center,
                column_gap: Val::Px(8.0),
                margin: UiRect::right(Val::Px(10.0)),
                ..default()
            })
            .with_children(|b| {
                b.spawn((
                    ImageNode::new(assets.load("images/ui/logo.png")),
                    Node { width: Val::Px(30.0), height: Val::Px(30.0), ..default() },
                ));
                b.spawn(theme::label(fonts, "Curieosity", theme::LG, Weight::Bold, theme::TEXT));
            });
            // views
            h.spawn(Node { column_gap: Val::Px(6.0), align_items: AlignItems::Center, ..default() }).with_children(
                |nav| {
                    for (view, icon, text) in [
                        (View::Lab, "bench", "Lab"),
                        (View::Substances, "book", "Substances"),
                        (View::Reactions, "reaction", "Reactions"),
                        (View::TechTree, "tree", "Tech Tree"),
                    ] {
                        nav.spawn((
                            theme::button(
                                Kind::Tab,
                                Node {
                                    height: Val::Px(34.0),
                                    padding: UiRect::horizontal(Val::Px(12.0)),
                                    column_gap: Val::Px(7.0),
                                    align_items: AlignItems::Center,
                                    ..default()
                                },
                                theme::R_SM,
                            ),
                            NavTab(view),
                        ))
                        .with_children(|t| {
                            t.spawn(theme::icon(assets, icon, 16.0, theme::TEXT));
                            t.spawn((
                                theme::label(fonts, text, theme::SM, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                        });
                    }
                },
            );
            // spacer
            h.spawn(Node { flex_grow: 1.0, ..default() });
            // era + discovery progress
            h.spawn(Node {
                flex_direction: FlexDirection::Column,
                align_items: AlignItems::FlexEnd,
                row_gap: Val::Px(3.0),
                ..default()
            })
            .with_children(|c| {
                c.spawn((EraText, theme::label(fonts, "", theme::SM, Weight::Semibold, theme::GOLD)));
                c.spawn(Node { align_items: AlignItems::Center, column_gap: Val::Px(8.0), ..default() }).with_children(
                    |r| {
                        r.spawn((
                            Node { width: Val::Px(140.0), height: Val::Px(5.0), ..default() },
                            BorderRadius::all(Val::Px(99.0)),
                            BackgroundColor(theme::LINE_STRONG.with_alpha(0.7)),
                        ))
                        .with_children(|track| {
                            track.spawn((
                                CountBar,
                                Node { width: Val::Percent(0.0), height: Val::Percent(100.0), ..default() },
                                BorderRadius::all(Val::Px(99.0)),
                                BackgroundGradient::from(LinearGradient::to_right(vec![
                                    ColorStop::auto(theme::VIOLET),
                                    ColorStop::auto(theme::CYAN),
                                ])),
                            ));
                        });
                        r.spawn((CountText, theme::label(fonts, "", theme::XS, Weight::Regular, theme::TEXT_2)));
                    },
                );
            });
            theme::spawn_icon_button(h, assets, "gear", 36.0, theme::TEXT, SettingsButton);
        });
}

/// Header tabs and the gear button.
pub fn nav_input_system(
    tabs: Query<(&Interaction, &NavTab), Changed<Interaction>>,
    gear: Query<&Interaction, (Changed<Interaction>, With<SettingsButton>)>,
    mut codex: ResMut<CodexState>,
    mut rlib: ResMut<ReactionLibState>,
    mut tree: ResMut<TechTreeState>,
    mut settings_ui: ResMut<SettingsUi>,
) {
    for (i, tab) in &tabs {
        if *i == Interaction::Pressed {
            codex.open = tab.0 == View::Substances;
            rlib.open = tab.0 == View::Reactions;
            tree.open = tab.0 == View::TechTree;
        }
    }
    for i in &gear {
        if *i == Interaction::Pressed {
            settings_ui.open = !settings_ui.open;
        }
    }
}

/// Esc closes the settings dialog, then any open view, then lets go of the shelf
/// selection; with nothing else to close it opens settings.
pub fn escape_system(
    keys: Res<ButtonInput<KeyCode>>,
    named: Res<ButtonInput<bevy::input::keyboard::Key>>,
    mut codex: ResMut<CodexState>,
    mut rlib: ResMut<ReactionLibState>,
    mut tree: ResMut<TechTreeState>,
    mut settings_ui: ResMut<SettingsUi>,
    mut selected: ResMut<crate::ui::detail_panel::SelectedSubstance>,
    mut credits: ResMut<crate::ui::credits::CreditsUi>,
    pads: Query<&Gamepad>,
) {
    // a controller's B and Start do what Esc does, and so does a phone's Back
    let pad = pads.iter().any(|g| g.just_pressed(GamepadButton::East) || g.just_pressed(GamepadButton::Start));
    let back = named.just_pressed(bevy::input::keyboard::Key::BrowserBack);
    if !keys.just_pressed(KeyCode::Escape) && !pad && !back {
        return;
    }
    if credits.open {
        credits.open = false;
    } else if settings_ui.open {
        settings_ui.open = false;
    } else if codex.open || rlib.open || tree.open {
        codex.open = false;
        rlib.open = false;
        tree.open = false;
    } else if selected.0.is_some() {
        selected.0 = None;
    } else {
        settings_ui.open = true;
    }
}

/// Highlight the tab of the view that is showing.
pub fn nav_highlight_system(
    codex: Res<CodexState>,
    rlib: Res<ReactionLibState>,
    tree: Res<TechTreeState>,
    mut tabs: Query<(&NavTab, &mut Skin)>,
) {
    if !(codex.is_changed() || rlib.is_changed() || tree.is_changed()) {
        return;
    }
    let v = current_view(&codex, &rlib, &tree);
    for (tab, mut skin) in &mut tabs {
        let active = tab.0 == v;
        if skin.active != active {
            skin.active = active;
        }
    }
}

/// The era is the latest age with at least a quarter of its steps done; the bar is the share
/// of the world's substances the player has found.
pub fn header_stats_system(
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    mut current: ResMut<crate::ui::onboarding::CurrentEra>,
    mut era: Query<&mut Text, (With<EraText>, Without<CountText>)>,
    mut count: Query<&mut Text, (With<CountText>, Without<EraText>)>,
    mut bar: Query<&mut Node, With<CountBar>>,
) {
    let Some(db) = db else { return };
    if !(progress.is_changed() || db.is_changed()) {
        return;
    }
    let known = |id: &u32| progress.discovered.contains(id);
    // The current era: the latest one with at least a quarter of its steps done. (A single
    // "done" step proves little: common products like water complete later steps early.)
    let n_eras = db.epochs.len().saturating_sub(1).max(1); // the Laboratory is not an era
    let mut done = vec![(0usize, 0usize); n_eras];
    for r in &db.authored {
        let e = r.epoch as usize;
        if e >= n_eras {
            continue;
        }
        done[e].1 += 1;
        if r.reactants.iter().all(|s| known(&s.substance_id)) && r.products.iter().all(|s| known(&s.substance_id)) {
            done[e].0 += 1;
        }
    }
    let e = done.iter().rposition(|(d, n)| *n > 0 && *d * 4 >= *n && *d > 0).unwrap_or(0) as u8;
    if current.index != e {
        current.index = e; // the era banner watches this
    }
    let era_label = db.epochs.get(e as usize).map(|ep| format!("{} · {}", ep.name, ep.era)).unwrap_or_default();
    if let Ok(mut t) = era.single_mut() {
        t.0 = era_label;
    }
    let found = db.canon.iter().filter(|id| known(id)).count();
    let total = db.canon.len().max(1);
    if let Ok(mut t) = count.single_mut() {
        t.0 = format!("{} / {} discovered", found, total);
    }
    if let Ok(mut n) = bar.single_mut() {
        n.width = Val::Percent(100.0 * found as f32 / total as f32);
    }
}

/// The bench: a tiled dot grid on the scrolling pane (it pans with the vessels), a soft
/// vignette over the edges, and a hint while the bench is empty.
pub fn decorate_bench_system(
    mut commands: Commands,
    fonts: Option<Res<UiFonts>>,
    assets: Res<AssetServer>,
    panes: Query<Entity, Added<CanvasScrollingPane>>,
    roots: Query<Entity, Added<ReactionCanvasRoot>>,
) {
    let Some(fonts) = fonts else { return };
    for pane in &panes {
        commands.entity(pane).with_children(|p| {
            p.spawn((
                BenchGrid,
                ImageNode {
                    image: assets.load("images/ui/grid_dot.png"),
                    color: Color::srgba(0.55, 0.65, 1.0, 0.16),
                    image_mode: NodeImageMode::Tiled { tile_x: true, tile_y: true, stretch_value: 1.0 },
                    ..default()
                },
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    top: Val::Px(0.0),
                    width: Val::Percent(100.0),
                    height: Val::Percent(100.0),
                    ..default()
                },
                Pickable::IGNORE,
            ));
        });
    }
    for root in &roots {
        // the vignette goes first, so it shades the bench but not the vessels on it
        let vignette = commands
            .spawn((
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    right: Val::Px(0.0),
                    top: Val::Px(0.0),
                    bottom: Val::Px(0.0),
                    ..default()
                },
                BackgroundGradient::from(RadialGradient {
                    color_space: default(),
                    position: UiPosition::CENTER,
                    shape: RadialGradientShape::FarthestCorner,
                    stops: vec![
                        ColorStop::new(Color::NONE, Val::Percent(55.0)),
                        ColorStop::new(Color::srgba(0.0, 0.0, 0.03, 0.55), Val::Percent(100.0)),
                    ],
                }),
                Pickable::IGNORE,
            ))
            .id();
        commands.entity(root).insert_children(0, &[vignette]);
        commands.entity(root).with_children(|r| {
            r.spawn((
                EmptyBenchHint,
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    right: Val::Px(0.0),
                    top: Val::Percent(38.0),
                    flex_direction: FlexDirection::Column,
                    align_items: AlignItems::Center,
                    row_gap: Val::Px(6.0),
                    ..default()
                },
                Pickable::IGNORE,
            ))
            .with_children(|h| {
                h.spawn((
                    theme::label(&fonts, "Your bench is empty", theme::XL, Weight::Semibold, theme::TEXT_2),
                    Pickable::IGNORE,
                ));
                h.spawn((
                    theme::label(
                        &fonts,
                        "Place a vessel from the right, then drag substances from the shelf below into it.",
                        theme::SM,
                        Weight::Regular,
                        theme::TEXT_3,
                    ),
                    Pickable::IGNORE,
                ));
            });
        });
    }
}

pub fn bench_state_system(
    settings: Res<Settings>,
    vessels: Query<(), With<VesselCard>>,
    mut grid: Query<&mut Visibility, (With<BenchGrid>, Without<EmptyBenchHint>)>,
    mut hint: Query<&mut Node, With<EmptyBenchHint>>,
) {
    let want = if settings.bench_grid { Visibility::Inherited } else { Visibility::Hidden };
    for mut v in &mut grid {
        if *v != want {
            *v = want;
        }
    }
    let empty = vessels.is_empty();
    for mut n in &mut hint {
        let d = if empty { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
}

// ---------------------------------------------------------------------------------------
// Scrolling: one wheel handler for every scrolling panel
// ---------------------------------------------------------------------------------------
/// The furthest a scrolling node can scroll, in the logical pixels ScrollPosition uses
/// (the same limit bevy_ui clamps to when it draws).
pub fn scroll_max(node: &ComputedNode) -> Vec2 {
    ((node.content_size - node.size + node.scrollbar_size) * node.inverse_scale_factor()).max(Vec2::ZERO)
}

/// What hit testing reads of a node.
type HitParts = (
    &'static ComputedNode,
    &'static UiGlobalTransform,
    Option<&'static bevy::ui::CalculatedClip>,
    Option<&'static InheritedVisibility>,
);

/// The topmost visible node at a point in physical window pixels.
fn node_at(p: Vec2, stack: &bevy::ui::UiStack, hits: &Query<HitParts>) -> Option<Entity> {
    stack.uinodes.iter().rev().copied().find(|e| {
        let Ok((node, tf, clip, vis)) = hits.get(*e) else { return false };
        vis.is_none_or(|v| v.get())
            && node.size.x > 0.0
            && node.contains_point(*tf, p)
            && clip.is_none_or(|c| c.clip.contains(p))
    })
}

/// Scroll the first panel at or around `e` that can still move by `d` (UI pixels; positive
/// shows what is above and to the left, as the wheel turned up does). At the end of an
/// inner list the movement passes on to the panel around it.
fn scroll_out_from(
    mut e: Entity,
    d: Vec2,
    parents: &Query<&ChildOf>,
    scrollers: &mut Query<(&Node, &ComputedNode, &mut ScrollPosition)>,
) {
    loop {
        if let Ok((node, cn, mut sp)) = scrollers.get_mut(e) {
            let max = scroll_max(cn);
            let can_x = node.overflow.x == OverflowAxis::Scroll && d.x != 0.0;
            let can_y = node.overflow.y == OverflowAxis::Scroll && d.y != 0.0;
            let want = Vec2::new(if can_x { sp.0.x - d.x } else { sp.0.x }, if can_y { sp.0.y - d.y } else { sp.0.y })
                .clamp(Vec2::ZERO, max);
            if (can_x || can_y) && want != sp.0 {
                sp.0 = want;
                return;
            }
        }
        match parents.get(e) {
            Ok(c) => e = c.parent(),
            Err(_) => return,
        }
    }
}

/// The wheel scrolls whatever scrolling panel is under the cursor (Shift scrolls
/// sideways), and never past its end, so there is no dead zone to scroll back through.
/// At the end of an inner list the wheel moves on to the panel around it.
pub fn wheel_scroll_system(
    mut wheel: MessageReader<bevy::input::mouse::MouseWheel>,
    keys: Res<ButtonInput<KeyCode>>,
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    stack: Res<bevy::ui::UiStack>,
    hits: Query<HitParts>,
    parents: Query<&ChildOf>,
    mut scrollers: Query<(&Node, &ComputedNode, &mut ScrollPosition)>,
) {
    use bevy::input::mouse::MouseScrollUnit;
    let mut d = Vec2::ZERO;
    for ev in wheel.read() {
        let step = match ev.unit {
            MouseScrollUnit::Line => 48.0,
            MouseScrollUnit::Pixel => 1.0,
        };
        d += Vec2::new(ev.x, ev.y) * step;
    }
    if d == Vec2::ZERO {
        return;
    }
    if keys.pressed(KeyCode::ShiftLeft) || keys.pressed(KeyCode::ShiftRight) {
        d = Vec2::new(d.x + d.y, 0.0);
    }
    let Some(win) = windows.iter().next() else { return };
    let Some(cursor) = win.cursor_position() else { return };
    if let Some(top) = node_at(cursor * win.scale_factor(), &stack, &hits) {
        scroll_out_from(top, d, &parents, &mut scrollers);
    }
}

/// A finger that swiped a shelf tile instead of lifting it (see systems/drag_drop.rs):
/// the panel around the tile scrolls by this much.
#[derive(Message, Clone, Copy, Debug)]
pub struct TouchScroll {
    pub from: Entity,
    /// how far the finger moved, in window pixels
    pub moved: Vec2,
}

/// A finger drags the list or panel it lands on, the way the wheel scrolls it. Things that
/// are dragged around (shelf tiles, vessels, the chips in them, the bench itself) are left
/// to the drag code, which hands a swiped shelf tile back here as a TouchScroll.
pub fn touch_scroll_system(
    touches: Res<Touches>,
    mut held: Local<bevy::platform::collections::HashMap<u64, Entity>>,
    mut swipes: MessageReader<TouchScroll>,
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    ui_scale: Res<UiScale>,
    stack: Res<bevy::ui::UiStack>,
    hits: Query<HitParts>,
    dragged: Query<(), Or<(With<Draggable>, With<CanvasScrollingPane>)>>,
    parents: Query<&ChildOf>,
    mut scrollers: Query<(&Node, &ComputedNode, &mut ScrollPosition)>,
) {
    let s = ui_scale.0.max(0.01);
    if let Some(win) = windows.iter().next() {
        for t in touches.iter_just_pressed() {
            let Some(top) = node_at(t.position() * win.scale_factor(), &stack, &hits) else { continue };
            let mut e = top;
            let on_dragged = loop {
                if dragged.contains(e) {
                    break true;
                }
                match parents.get(e) {
                    Ok(c) => e = c.parent(),
                    Err(_) => break false,
                }
            };
            if !on_dragged {
                held.insert(t.id(), top);
            }
        }
    }
    for t in touches.iter() {
        if let Some(&e) = held.get(&t.id()) {
            let d = t.delta();
            if d != Vec2::ZERO {
                scroll_out_from(e, d / s, &parents, &mut scrollers);
            }
        }
    }
    for t in touches.iter_just_released().chain(touches.iter_just_canceled()) {
        held.remove(&t.id());
    }
    for m in swipes.read() {
        scroll_out_from(m.from, m.moved / s, &parents, &mut scrollers);
    }
}

/// Anything that set a scroll position past the end (a list that got shorter, code that
/// scrolls something into view) is pulled back to the end.
pub fn clamp_scroll_system(
    mut q: Query<(&ComputedNode, &mut ScrollPosition), Or<(Changed<ComputedNode>, Changed<ScrollPosition>)>>,
) {
    for (cn, mut sp) in &mut q {
        let c = sp.0.clamp(Vec2::ZERO, scroll_max(cn));
        if c != sp.0 {
            sp.0 = c;
        }
    }
}
