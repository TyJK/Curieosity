// src/ui/shell.rs
//
// The frame around everything: the header bar (logo, the four views, the current era, how
// much of the world has been discovered, past notifications, settings), view switching and
// Esc, and the lab
// bench's decoration (dot grid, vignette, the "start here" hint on an empty bench).
use crate::ui::Clicked;
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
/// The bell: opens the journal of past notifications.
#[derive(Component)]
pub struct JournalButton;
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
/// The bench's zoom bar: out, the level, in.
#[derive(Component)]
pub struct BenchZoomOut;
#[derive(Component)]
pub struct BenchZoomIn;
#[derive(Component)]
pub struct BenchZoomLabel;

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

/// The screen is taller than it is wide (a phone held upright): the vessel list becomes a
/// strip above the shelf, the bench takes the full width, and the header keeps its icons.
#[derive(Resource, Default, Debug, Clone, Copy, PartialEq, Eq)]
pub struct Portrait(pub bool);

/// The vessel strip's height, upright.
pub const STRIP_H: f32 = 66.0;

/// The header's name, the nav tabs' words and the progress track: left out upright.
#[derive(Component)]
pub struct HeaderWords;

/// A view of a list beside a page (the Substance and Reaction Libraries): side by side,
/// or upright the list above the page.
#[derive(Component)]
pub struct SplitRoot;
/// The list, and its width side by side.
#[derive(Component)]
pub struct SplitList(pub f32);
#[derive(Component)]
pub struct SplitPane;

pub fn portrait_system(windows: Query<&Window, With<bevy::window::PrimaryWindow>>, mut portrait: ResMut<Portrait>) {
    let Ok(w) = windows.single() else { return };
    if w.width() < 1.0 {
        return;
    }
    let upright = w.height() > w.width() * 1.05;
    if portrait.0 != upright {
        portrait.0 = upright;
    }
}

/// Lays the lab out for the way the screen is held (see Portrait). The bench's and the
/// list's distance from the bottom is fit_dock_system's.
#[allow(clippy::type_complexity)]
pub fn portrait_layout_system(
    portrait: Res<Portrait>,
    mut nodes: Query<
        (
            &mut Node,
            Has<crate::ui::process_toolbar::VesselSidebar>,
            Has<crate::ui::process_toolbar::VesselSidebarHead>,
            Has<crate::components::ui_markers::ReactionCanvasRoot>,
            Has<HeaderWords>,
            Has<crate::ui::toasts::ToastStack>,
            (Has<SplitRoot>, Option<&SplitList>, Has<SplitPane>),
        ),
        Or<(
            With<crate::ui::process_toolbar::VesselSidebar>,
            With<crate::ui::process_toolbar::VesselSidebarHead>,
            With<crate::components::ui_markers::ReactionCanvasRoot>,
            With<HeaderWords>,
            With<crate::ui::toasts::ToastStack>,
            With<crate::ui::hint::HintRoot>,
            With<crate::ui::discovery_card::DiscoveryCardRoot>,
            With<SplitRoot>,
            With<SplitList>,
            With<SplitPane>,
        )>,
    >,
) {
    let up = portrait.0;
    let side = if up { 0.0 } else { theme::SIDEBAR_W };
    for (mut n, list, head, bench, words, toasts, (split, split_list, split_pane)) in &mut nodes {
        let mut want = n.clone();
        if split {
            want.flex_direction = if up { FlexDirection::Column } else { FlexDirection::Row };
        } else if let Some(SplitList(w)) = split_list {
            let list_w = Val::Px(*w);
            want.width = if up { Val::Percent(100.0) } else { list_w };
            want.min_width = if up { Val::Px(0.0) } else { list_w };
            want.height = Val::Percent(if up { 42.0 } else { 100.0 });
            want.border = if up { UiRect::bottom(Val::Px(1.0)) } else { UiRect::right(Val::Px(1.0)) };
        } else if split_pane {
            want.height = if up { Val::Auto } else { Val::Percent(100.0) };
            want.flex_basis = if up { Val::Px(0.0) } else { Val::Auto };
            want.min_height = Val::Px(0.0);
            want.padding = if up {
                UiRect::new(Val::Px(16.0), Val::Px(16.0), Val::Px(14.0), Val::Px(30.0))
            } else {
                UiRect::new(Val::Px(32.0), Val::Px(32.0), Val::Px(26.0), Val::Px(40.0))
            };
        } else if list {
            if up {
                want.left = Val::Px(0.0);
                want.right = Val::Px(0.0);
                want.top = Val::Auto;
                want.width = Val::Auto;
                want.height = Val::Px(STRIP_H);
                want.flex_direction = FlexDirection::Row;
                want.align_items = AlignItems::Center;
                want.column_gap = Val::Px(6.0);
                want.padding = UiRect::all(Val::Px(6.0));
                want.border = UiRect::top(Val::Px(1.0));
                want.overflow = Overflow::scroll_x();
            } else {
                want.left = Val::Auto;
                want.right = Val::Px(0.0);
                want.top = Val::Px(theme::HEADER_H);
                want.width = Val::Px(theme::SIDEBAR_W);
                want.height = Val::Auto;
                want.flex_direction = FlexDirection::Column;
                want.align_items = AlignItems::Stretch;
                want.column_gap = Val::Px(0.0);
                want.padding = UiRect::all(Val::Px(12.0));
                want.border = UiRect::left(Val::Px(1.0));
                want.overflow = Overflow::scroll_y();
            }
        } else if head || words {
            want.display = if up { Display::None } else { Display::Flex };
        } else if bench {
            want.right = Val::Px(side);
        } else {
            // the overlays at the bench's right edge, over the shelf (and the strip, upright)
            want.right = Val::Px(side + 14.0);
            let lift = if up { STRIP_H + crate::ui::inventory::SHELF_ROW } else { 0.0 };
            if toasts {
                want.bottom = Val::Px(theme::DOCK_H + 14.0 + lift);
            } else if n.bottom != Val::Auto {
                want.bottom = Val::Px(theme::DOCK_H + 12.0 + lift);
            }
        }
        if *n != want {
            *n = want;
        }
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
                b.spawn((HeaderWords, theme::label(fonts, "Curieosity", theme::LG, Weight::Bold, theme::TEXT)));
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
                                HeaderWords,
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
                            HeaderWords,
                            Node {
                                border_radius: BorderRadius::all(Val::Px(99.0)),
                                width: Val::Px(140.0),
                                height: Val::Px(5.0),
                                ..default()
                            },
                            BackgroundColor(theme::LINE_STRONG.with_alpha(0.7)),
                        ))
                        .with_children(|track| {
                            track.spawn((
                                CountBar,
                                Node {
                                    border_radius: BorderRadius::all(Val::Px(99.0)),
                                    width: Val::Percent(0.0),
                                    height: Val::Percent(100.0),
                                    ..default()
                                },
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
            theme::spawn_icon_button(h, assets, "bell", 36.0, theme::TEXT, JournalButton);
            theme::spawn_icon_button(h, assets, "gear", 36.0, theme::TEXT, SettingsButton);
        });
}

/// Header tabs, the bell and the gear button.
#[allow(clippy::too_many_arguments)]
pub fn nav_input_system(
    tabs: Query<&NavTab, With<Clicked>>,
    gear: Query<(), (With<Clicked>, With<SettingsButton>)>,
    bell: Query<(), (With<Clicked>, With<JournalButton>)>,
    mut codex: ResMut<CodexState>,
    mut rlib: ResMut<ReactionLibState>,
    mut tree: ResMut<TechTreeState>,
    mut settings_ui: ResMut<SettingsUi>,
    mut journal_ui: ResMut<crate::ui::toasts::JournalUi>,
) {
    for tab in &tabs {
        codex.open = tab.0 == View::Substances;
        rlib.open = tab.0 == View::Reactions;
        tree.open = tab.0 == View::TechTree;
    }
    if !gear.is_empty() {
        settings_ui.open = !settings_ui.open;
    }
    if !bell.is_empty() {
        journal_ui.open = !journal_ui.open;
    }
}

/// Esc closes the shelf search's typing, then the credits, the settings dialog or the
/// journal, then any open view, then lets go of a port picked to link from, then of the
/// shelf selection; with nothing else to close it opens settings.
#[allow(clippy::too_many_arguments)]
pub fn escape_system(
    keys: Res<ButtonInput<KeyCode>>,
    named: Res<ButtonInput<bevy::input::keyboard::Key>>,
    mut codex: ResMut<CodexState>,
    mut rlib: ResMut<ReactionLibState>,
    mut tree: ResMut<TechTreeState>,
    mut settings_ui: ResMut<SettingsUi>,
    mut selected: ResMut<crate::ui::detail_panel::SelectedSubstance>,
    mut credits: ResMut<crate::ui::credits::CreditsUi>,
    mut journal_ui: ResMut<crate::ui::toasts::JournalUi>,
    mut search: ResMut<crate::ui::inventory::ShelfSearch>,
    mut menu: ResMut<crate::ui::main_menu::MainMenu>,
    mut pick: ResMut<crate::systems::drag_drop::LinkPick>,
    pads: Query<&Gamepad>,
) {
    // a controller's B and Start do what Esc does, and so does a phone's Back
    let pad = pads.iter().any(|g| g.just_pressed(GamepadButton::East) || g.just_pressed(GamepadButton::Start));
    let back = named.just_pressed(bevy::input::keyboard::Key::BrowserBack);
    if !keys.just_pressed(KeyCode::Escape) && !pad && !back {
        return;
    }
    use crate::ui::main_menu::MenuStage;
    if matches!(menu.stage, MenuStage::Title | MenuStage::Notice) {
        // (main_menu_system moves past these on any key)
        return;
    }
    if search.typing {
        search.typing = false;
    } else if credits.open {
        credits.open = false;
    } else if journal_ui.open {
        journal_ui.open = false;
    } else if settings_ui.open {
        settings_ui.open = false;
    } else if codex.open || rlib.open || tree.open {
        codex.open = false;
        rlib.open = false;
        tree.open = false;
    } else if menu.stage == MenuStage::Menu {
        // back to the game
        menu.hide();
    } else if pick.0.is_some() {
        pick.0 = None;
    } else if selected.0.is_some() {
        selected.0 = None;
    } else {
        menu.show_menu();
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
                        "Place a vessel from the right, then tap or drag substances from the shelf into it.",
                        theme::SM,
                        Weight::Regular,
                        theme::TEXT_3,
                    ),
                    Pickable::IGNORE,
                ));
            });
            // zoom: out, the level, in (Ctrl and the wheel, or a pinch, do the same)
            r.spawn((
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(12.0),
                    bottom: Val::Px(12.0),
                    align_items: AlignItems::Center,
                    column_gap: Val::Px(2.0),
                    padding: UiRect::all(Val::Px(3.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    border_radius: BorderRadius::all(Val::Px(99.0)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE.with_alpha(0.92)),
                BorderColor::all(theme::LINE),
                Name::new("BenchZoom"),
            ))
            .with_children(|z| {
                theme::spawn_icon_button(
                    z,
                    &assets,
                    "minus",
                    28.0,
                    theme::TEXT,
                    (
                        BenchZoomOut,
                        crate::ui::onboarding::Tip::Text(
                            "Zoom out",
                            "See more of the bench. At 60% and below the vessels fold down to what they hold.",
                        ),
                    ),
                );
                z.spawn((
                    BenchZoomLabel,
                    theme::label(&fonts, "100%", theme::XS, Weight::Semibold, theme::TEXT_2),
                    TextLayout::justify(Justify::Center),
                    Node { min_width: Val::Px(40.0), ..default() },
                    Pickable::IGNORE,
                ));
                theme::spawn_icon_button(
                    z,
                    &assets,
                    "plus",
                    28.0,
                    theme::TEXT,
                    (BenchZoomIn, crate::ui::onboarding::Tip::Text("Zoom in", "Back toward full size.")),
                );
            });
        });
    }
}

/// The zoom bar's buttons and its level, and a two-finger pinch: apart zooms in,
/// together zooms out, a step at a time.
pub fn bench_zoom_controls_system(
    mut zoom: ResMut<crate::systems::drag_drop::BenchZoom>,
    outs: Query<(), (With<Clicked>, With<BenchZoomOut>)>,
    ins: Query<(), (With<Clicked>, With<BenchZoomIn>)>,
    mut label: Query<&mut Text, With<BenchZoomLabel>>,
    touches: Res<Touches>,
    mut pinch: Local<Option<f32>>,
) {
    let mut to = zoom.0;
    if !outs.is_empty() {
        to = zoom.stepped(true);
    }
    if !ins.is_empty() {
        to = zoom.stepped(false);
    }
    let fingers: Vec<Vec2> = touches.iter().map(|t| t.position()).collect();
    if let [a, b] = fingers[..] {
        let d = a.distance(b);
        match *pinch {
            None => *pinch = Some(d),
            Some(start) if d > start * 1.3 => {
                to = zoom.stepped(false);
                *pinch = Some(d);
            }
            Some(start) if d < start / 1.3 => {
                to = zoom.stepped(true);
                *pinch = Some(d);
            }
            _ => {}
        }
    } else {
        *pinch = None;
    }
    if zoom.0 != to {
        zoom.0 = to;
    }
    if zoom.is_changed() {
        for mut t in &mut label {
            t.0 = format!("{:.0}%", zoom.0 * 100.0);
        }
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
    Option<&'static Pickable>,
);

/// The topmost visible node at a point in physical window pixels. Nodes the pointer goes
/// through (pop-ups, labels on buttons) are passed over, as picking passes over them.
fn node_at(p: Vec2, stack: &bevy::ui::UiStack, hits: &Query<HitParts>) -> Option<Entity> {
    stack.uinodes.iter().rev().copied().find(|e| {
        let Ok((node, tf, clip, vis, pick)) = hits.get(*e) else { return false };
        vis.is_none_or(|v| v.get())
            && pick.is_none_or(|p| p.should_block_lower)
            && node.size.x > 0.0
            && node.contains_point(*tf, p)
            && clip.is_none_or(|c| c.contains_point(p))
    })
}

/// Scroll the first panel at or around `e` that can still move by `d` (UI pixels; positive
/// shows what is above and to the left, as the wheel turned up does). At the end of an
/// inner list the movement passes on to the panel around it. A wheel turned up or down
/// over a list that only runs sideways (the vessel strip and the shelf's pills, upright)
/// scrolls it along; a finger moves things the way it moves.
fn scroll_out_from(
    mut e: Entity,
    d: Vec2,
    wheel: bool,
    parents: &Query<&ChildOf>,
    scrollers: &mut Query<(&Node, &ComputedNode, &mut ScrollPosition), Without<CanvasScrollingPane>>,
) -> bool {
    loop {
        if let Ok((node, cn, mut sp)) = scrollers.get_mut(e) {
            let sideways = node.overflow.x == OverflowAxis::Scroll && node.overflow.y != OverflowAxis::Scroll;
            let d = if wheel && sideways && d.x == 0.0 { Vec2::new(d.y, 0.0) } else { d };
            let max = scroll_max(cn);
            let can_x = node.overflow.x == OverflowAxis::Scroll && d.x != 0.0;
            let can_y = node.overflow.y == OverflowAxis::Scroll && d.y != 0.0;
            let want = Vec2::new(if can_x { sp.0.x - d.x } else { sp.0.x }, if can_y { sp.0.y - d.y } else { sp.0.y })
                .clamp(Vec2::ZERO, max);
            if (can_x || can_y) && want != sp.0 {
                sp.0 = want;
                return true;
            }
        }
        match parents.get(e) {
            Ok(c) => e = c.parent(),
            Err(_) => return false,
        }
    }
}

/// The wheel scrolls whatever scrolling panel is under the cursor (Shift scrolls
/// sideways), and never past its end, so there is no dead zone to scroll back through.
/// At the end of an inner list the wheel moves on to the panel around it; on the bench it
/// pans the bench, as dragging does.
#[allow(clippy::too_many_arguments)]
pub fn wheel_scroll_system(
    mut wheel: MessageReader<bevy::input::mouse::MouseWheel>,
    keys: Res<ButtonInput<KeyCode>>,
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    stack: Res<bevy::ui::UiStack>,
    hits: Query<HitParts>,
    parents: Query<&ChildOf>,
    mut scrollers: Query<(&Node, &ComputedNode, &mut ScrollPosition), Without<CanvasScrollingPane>>,
    mut panes: Query<(Entity, &mut Node), With<CanvasScrollingPane>>,
    bench: Query<&ComputedNode, With<ReactionCanvasRoot>>,
    mut zoom: ResMut<crate::systems::drag_drop::BenchZoom>,
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
    let Some(top) = node_at(cursor * win.scale_factor(), &stack, &hits) else { return };
    let ctrl = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);
    if !ctrl && scroll_out_from(top, d, true, &parents, &mut scrollers) {
        return;
    }
    // nothing scrolled: on the bench, pan it (Ctrl zooms it)
    let Ok((pane, mut node)) = panes.single_mut() else { return };
    let mut e = top;
    loop {
        if e == pane || bench.contains(e) {
            if ctrl {
                let z = zoom.stepped(d.y + d.x < 0.0);
                if zoom.0 != z {
                    zoom.0 = z;
                }
                return;
            }
            let at = crate::systems::drag_drop::pane_offset(&node) + d;
            let view = crate::systems::drag_drop::bench_view(&bench);
            crate::systems::drag_drop::pan_bench(&mut node, view, at, zoom.0);
            return;
        }
        match parents.get(e) {
            Ok(c) => e = c.parent(),
            Err(_) => return,
        }
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
    mut scrollers: Query<(&Node, &ComputedNode, &mut ScrollPosition), Without<CanvasScrollingPane>>,
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
                scroll_out_from(e, d / s, false, &parents, &mut scrollers);
            }
        }
    }
    for t in touches.iter_just_released().chain(touches.iter_just_canceled()) {
        held.remove(&t.id());
    }
    for m in swipes.read() {
        scroll_out_from(m.from, m.moved / s, false, &parents, &mut scrollers);
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
