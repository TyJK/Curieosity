// src/ui/tech_tree.rs
//
// The tech tree: "what can I make next". The authored progression shown either as a node
// GRAPH (eras as columns, reactions as nodes, producer -> consumer lines between them,
// coloured done / available / locked) or a guided LIST (Available now / Completed / Locked).
//
// Design choices that keep this robust and testable:
//   * The graph is laid out ANALYTICALLY. Every node sits at a computed (x, y) inside a
//     fixed-size content node; connectors are axis-aligned elbow segments (plain UI Nodes)
//     whose rects come from those same coordinates. Scrolling moves nodes and lines
//     together and the geometry is deterministic.
//   * Everything is DERIVED from the RecipeDatabase at runtime: nodes = authored reactions;
//     edges = producer -> consumer between them (skipping ubiquitous utility substances and
//     high-fan-in ones so the graph stays a clean spine).
//   * The graph pans with the wheel (Shift for sideways) or by dragging the background.
use bevy::prelude::*;
use bevy::ui::ScrollPosition;
use std::collections::HashMap;

use crate::components::format_formula;
use crate::data::common::StoichPoint;
use crate::data::reactions::Reaction;
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::process_toolbar::{vessel_art_path, vessel_name, ProcessUnlocks};
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::GameData;

// ---------------------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------------------
#[derive(Clone, Copy, PartialEq, Eq, Default, Debug)]
pub enum TechMode {
    #[default]
    Graph,
    List,
}

#[derive(Resource, Default)]
pub struct TechTreeState {
    pub open: bool,
    pub mode: TechMode,
    pub selected: Option<u32>,
}

// --- markers -----------------------------------------------------------------------
#[derive(Component)]
pub struct TechCloseButton;
#[derive(Component)]
pub struct TechRoot;
#[derive(Component)]
pub struct TechModeButton(pub TechMode);
#[derive(Component)]
pub struct TechGraphView;
#[derive(Component)]
pub struct TechListView;
#[derive(Component)]
pub struct TechGraphContent;
#[derive(Component)]
pub struct TechListContent;
#[derive(Component)]
pub struct TechDetailBar;
#[derive(Component)]
pub struct TechSummaryText;
#[derive(Component)]
pub struct TechOpenInLibrary(pub u32);
/// A graph node; remembers its state so the selection/hover look can be recomputed.
#[derive(Component)]
pub struct TechNodeButton(pub u32, NodeState);
#[derive(Component)]
pub struct TechListEntry(pub u32);
/// Scroll viewport marker. `graph == true` for the (x+y) graph viewport, false for the
/// (y only) list viewport.
#[derive(Component)]
pub struct TechScrollable {
    pub graph: bool,
}

// ---------------------------------------------------------------------------------------
// Layout constants (logical px, inside the graph content node)
// ---------------------------------------------------------------------------------------
const PAD: f32 = 24.0;
const NODE_W: f32 = 188.0;
const NODE_H: f32 = 54.0;
const COL_W: f32 = 228.0; // column pitch (node + 40 gutter)
const EPOCH_GAP: f32 = 40.0; // extra space between eras
const ROW_H: f32 = 66.0;
const BAND_H: f32 = 60.0; // era header band
const GUTTER: f32 = 18.0; // right-bump for same/backward edges
const TOOLBAR_H: f32 = 56.0;
const DETAIL_H: f32 = 132.0;

// ---------------------------------------------------------------------------------------
// Domain helpers
// ---------------------------------------------------------------------------------------
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum NodeState {
    Completed,
    Available,
    Locked,
}

/// Done (every product found), ready (vessel unlocked and every reactant found) or locked.
pub fn node_state(r: &Reaction, progress: &PlayerProgress, unlocks: &ProcessUnlocks) -> NodeState {
    if r.products.iter().all(|p| progress.discovered.contains(&p.substance_id)) {
        return NodeState::Completed;
    }
    let ready =
        unlocks.0.contains(&r.process) && r.reactants.iter().all(|s| progress.discovered.contains(&s.substance_id));
    if ready {
        NodeState::Available
    } else {
        NodeState::Locked
    }
}

fn state_accent(s: NodeState) -> Color {
    match s {
        NodeState::Completed => theme::GREEN,
        NodeState::Available => theme::GOLD,
        NodeState::Locked => theme::LINE_STRONG,
    }
}

/// (background, border) for a node in a state.
fn node_look(s: NodeState, selected: bool, hovered: bool) -> (Color, Color) {
    let (bg, border) = match s {
        NodeState::Completed => (theme::mix(theme::RAISED, theme::GREEN, 0.13), theme::GREEN.with_alpha(0.55)),
        NodeState::Available => (theme::mix(theme::RAISED, theme::GOLD, 0.17), theme::GOLD),
        NodeState::Locked => (theme::SURFACE, theme::LINE),
    };
    let bg = if hovered { theme::mix(bg, theme::TEXT, 0.06) } else { bg };
    (bg, if selected { theme::CYAN } else { border })
}

fn state_icon(s: NodeState) -> &'static str {
    match s {
        NodeState::Completed => "check",
        NodeState::Available => "dot",
        NodeState::Locked => "lock",
    }
}

fn state_label(s: NodeState) -> &'static str {
    match s {
        NodeState::Completed => "Completed",
        NodeState::Available => "Ready to make",
        NodeState::Locked => "Locked",
    }
}

fn side_string(points: &[StoichPoint], subs: &Substances) -> String {
    points
        .iter()
        .map(|sp| {
            let label = subs
                .0
                .get(&sp.substance_id)
                .map(|s| format_formula(&s.formula))
                .unwrap_or_else(|| format!("?{}", sp.substance_id));
            if sp.moles <= 1 {
                label
            } else {
                format!("{} {}", sp.moles, label)
            }
        })
        .collect::<Vec<_>>()
        .join(" + ")
}

fn equation_string(r: &Reaction, subs: &Substances) -> String {
    format!("{}  →  {}", side_string(&r.reactants, subs), side_string(&r.products, subs))
}

/// A plain-language hint for how to run a reaction, e.g. "In the Bloomery, combine Hematite + Charcoal."
fn hint_string(r: &Reaction, subs: &Substances) -> String {
    let names: Vec<String> = r
        .reactants
        .iter()
        .map(|sp| {
            subs.0.get(&sp.substance_id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{}", sp.substance_id))
        })
        .collect();
    let catalyst = r
        .required_catalyst()
        .and_then(|c| subs.0.get(&c))
        .map(|c| format!(", with {} in the catalyst slot", c.name))
        .unwrap_or_default();
    format!("In the {}, combine {}{}.", vessel_name(&r.process), names.join(" + "), catalyst)
}

fn era_tag(e: usize, n_epochs: usize) -> String {
    if e + 1 == n_epochs {
        "LAB".into()
    } else {
        format!("ERA {}", e + 1)
    }
}

// ---------------------------------------------------------------------------------------
// Spawn
// ---------------------------------------------------------------------------------------
pub fn spawn_tech_tree(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((TechRoot, theme::view_root(620), Name::new("TechTreeRoot")))
        .insert(Node {
            position_type: PositionType::Absolute,
            left: Val::Px(0.0),
            right: Val::Px(0.0),
            top: Val::Px(theme::HEADER_H),
            bottom: Val::Px(0.0),
            flex_direction: FlexDirection::Column,
            display: Display::None,
            ..default()
        })
        .with_children(|root| {
            // --- toolbar: title + summary, legend, Graph/List, close ---
            root.spawn((
                Node {
                    width: Val::Percent(100.0),
                    height: Val::Px(TOOLBAR_H),
                    flex_shrink: 0.0,
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::SpaceBetween,
                    padding: UiRect::horizontal(Val::Px(18.0)),
                    border: UiRect::bottom(Val::Px(1.0)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE),
            ))
            .with_children(|bar| {
                bar.spawn(Node { align_items: AlignItems::Baseline, column_gap: Val::Px(14.0), ..default() })
                    .with_children(|t| {
                        t.spawn(theme::label(fonts, "Tech Tree", theme::XL, Weight::Semibold, theme::TEXT));
                        t.spawn((TechSummaryText, theme::label(fonts, "", theme::SM, Weight::Regular, theme::TEXT_2)));
                    });
                bar.spawn(Node { align_items: AlignItems::Center, column_gap: Val::Px(18.0), ..default() })
                    .with_children(|r| {
                        // legend
                        r.spawn(Node { align_items: AlignItems::Center, column_gap: Val::Px(14.0), ..default() })
                            .with_children(|lg| {
                                for s in [NodeState::Completed, NodeState::Available, NodeState::Locked] {
                                    lg.spawn(Node {
                                        align_items: AlignItems::Center,
                                        column_gap: Val::Px(6.0),
                                        ..default()
                                    })
                                    .with_children(|i| {
                                        i.spawn(theme::icon(assets, state_icon(s), 14.0, state_accent(s)));
                                        i.spawn(theme::label(
                                            fonts,
                                            state_label(s),
                                            theme::XS,
                                            Weight::Semibold,
                                            theme::TEXT_2,
                                        ));
                                    });
                                }
                            });
                        // segmented Graph / List
                        r.spawn((
                            Node {
                                padding: UiRect::all(Val::Px(3.0)),
                                column_gap: Val::Px(2.0),
                                border: UiRect::all(Val::Px(1.0)),
                                ..default()
                            },
                            BorderRadius::all(Val::Px(99.0)),
                            BackgroundColor(theme::BG),
                            BorderColor::all(theme::LINE),
                        ))
                        .with_children(|seg| {
                            for (label, mode) in [("Graph", TechMode::Graph), ("List", TechMode::List)] {
                                seg.spawn((
                                    theme::button(
                                        Kind::Tab,
                                        Node {
                                            height: Val::Px(26.0),
                                            padding: UiRect::horizontal(Val::Px(14.0)),
                                            align_items: AlignItems::Center,
                                            ..default()
                                        },
                                        99.0,
                                    ),
                                    TechModeButton(mode),
                                ))
                                .with_children(|b| {
                                    b.spawn((
                                        theme::label(fonts, label, theme::SM, Weight::Semibold, theme::TEXT),
                                        Pickable::IGNORE,
                                    ));
                                });
                            }
                        });
                        theme::spawn_icon_button(r, assets, "close", 32.0, theme::TEXT_2, TechCloseButton);
                    });
            });

            // --- body: the two views stacked; only one shown at a time ---
            root.spawn((
                Node { width: Val::Percent(100.0), flex_grow: 1.0, ..default() },
                BackgroundColor(theme::BENCH),
            ))
            .with_children(|body| {
                body.spawn((
                    TechGraphView,
                    TechScrollable { graph: true },
                    ScrollPosition::default(),
                    Node {
                        position_type: PositionType::Absolute,
                        left: Val::Px(0.0),
                        top: Val::Px(0.0),
                        width: Val::Percent(100.0),
                        height: Val::Percent(100.0),
                        overflow: Overflow::scroll(),
                        ..default()
                    },
                ))
                .with_children(|vp| {
                    vp.spawn((
                        TechGraphContent,
                        Node {
                            position_type: PositionType::Relative,
                            width: Val::Px(PAD * 2.0),
                            height: Val::Px(PAD * 2.0),
                            flex_shrink: 0.0,
                            ..default()
                        },
                    ));
                });
                body.spawn((
                    TechListView,
                    TechScrollable { graph: false },
                    ScrollPosition::default(),
                    Node {
                        position_type: PositionType::Absolute,
                        left: Val::Px(0.0),
                        top: Val::Px(0.0),
                        width: Val::Percent(100.0),
                        height: Val::Percent(100.0),
                        overflow: Overflow::scroll_y(),
                        padding: UiRect::axes(Val::Px(28.0), Val::Px(18.0)),
                        justify_content: JustifyContent::Center,
                        display: Display::None,
                        ..default()
                    },
                ))
                .with_children(|vp| {
                    vp.spawn((
                        TechListContent,
                        Node {
                            width: Val::Percent(100.0),
                            max_width: Val::Px(980.0),
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(4.0),
                            ..default()
                        },
                    ));
                });
            });

            // --- detail bar (bottom) ---
            root.spawn((
                TechDetailBar,
                Node {
                    width: Val::Percent(100.0),
                    height: Val::Px(DETAIL_H),
                    flex_shrink: 0.0,
                    align_items: AlignItems::Center,
                    column_gap: Val::Px(18.0),
                    padding: UiRect::axes(Val::Px(20.0), Val::Px(14.0)),
                    border: UiRect::top(Val::Px(1.0)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE),
            ));
        });
}

// ---------------------------------------------------------------------------------------
// Open / close / mode
// ---------------------------------------------------------------------------------------
pub fn tech_button_system(
    closes: Query<&Interaction, (Changed<Interaction>, With<TechCloseButton>)>,
    modes: Query<(&Interaction, &TechModeButton), Changed<Interaction>>,
    opens: Query<(&Interaction, &TechOpenInLibrary), Changed<Interaction>>,
    mut state: ResMut<TechTreeState>,
    mut rlib: ResMut<ReactionLibState>,
    mut root_q: Query<&mut Node, With<TechRoot>>,
) {
    for i in &closes {
        if *i == Interaction::Pressed {
            state.open = false;
        }
    }
    for (i, m) in &modes {
        if *i == Interaction::Pressed && state.mode != m.0 {
            state.mode = m.0;
        }
    }
    for (i, o) in &opens {
        if *i == Interaction::Pressed {
            state.open = false;
            rlib.open = true;
            rlib.selected = Some(o.0);
        }
    }
    if let Ok(mut node) = root_q.single_mut() {
        let d = if state.open { Display::Flex } else { Display::None };
        if node.display != d {
            node.display = d;
        }
    }
}

/// Shows one view, hides the other, and highlights the active mode button.
pub fn tech_mode_system(
    state: Res<TechTreeState>,
    mut graph_q: Query<&mut Node, (With<TechGraphView>, Without<TechListView>)>,
    mut list_q: Query<&mut Node, (With<TechListView>, Without<TechGraphView>)>,
    mut btn_q: Query<(&TechModeButton, &mut Skin)>,
) {
    if !state.is_changed() {
        return;
    }
    if let Ok(mut n) = graph_q.single_mut() {
        n.display = if state.mode == TechMode::Graph { Display::Flex } else { Display::None };
    }
    if let Ok(mut n) = list_q.single_mut() {
        n.display = if state.mode == TechMode::List { Display::Flex } else { Display::None };
    }
    for (b, mut skin) in &mut btn_q {
        let a = b.0 == state.mode;
        if skin.active != a {
            skin.active = a;
        }
    }
}

// ---------------------------------------------------------------------------------------
// Populate both views (rebuilt on open / discovery change)
// ---------------------------------------------------------------------------------------
struct NodeInfo {
    id: u32,
    name: String,
    epoch: usize,
    /// Global column index (eras are split into depth sub-columns).
    col: usize,
    row: usize,
    state: NodeState,
}

/// Left x of a global column, accounting for the extra gap at each era boundary.
fn col_x(col: usize, epoch: usize) -> f32 {
    PAD + col as f32 * COL_W + epoch as f32 * EPOCH_GAP
}

fn node_y(row: usize) -> f32 {
    BAND_H + PAD + row as f32 * ROW_H
}

pub fn populate_tech_views_system(
    mut commands: Commands,
    state: Res<TechTreeState>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    recipe_db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    mut graph_q: Query<(Entity, &mut Node), With<TechGraphContent>>,
    list_q: Query<Entity, With<TechListContent>>,
    mut scroll_q: Query<(&TechScrollable, &mut ScrollPosition)>,
    mut summary_q: Query<&mut Text, With<TechSummaryText>>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    mut prev_open: Local<bool>,
) {
    let just_opened = state.open && !*prev_open;
    let should = state.open && (just_opened || progress.is_changed() || unlocks.is_changed());
    *prev_open = state.open;
    if !should {
        return;
    }
    let (Some(db), Some(subs)) = (recipe_db.as_ref(), substances_assets.get(&game_data.substances)) else {
        return;
    };
    let fonts = &*fonts;
    let assets = &*assets;

    // Authored reactions, already sorted by (epoch, id).
    let rxns: Vec<&Reaction> = db.authored.iter().collect();
    let n_epochs = db.epochs.len().max(1);
    let epoch_of = |r: &Reaction| (r.epoch.unwrap_or(0) as usize).min(n_epochs - 1);

    // Producer map over EARLIER authored reactions only (keeps the depth pass acyclic).
    // Utility substances that appear everywhere never create depth or edges.
    const UTILITY: &[u32] = &[8, 5, 12, 1]; // Water, Oxygen, CO2, Hydrogen
    let mut producers: HashMap<u32, Vec<usize>> = HashMap::new();
    let mut depth: Vec<usize> = vec![0; rxns.len()];
    for (i, r) in rxns.iter().enumerate() {
        let e = epoch_of(r);
        let mut d = 0;
        for sp in &r.reactants {
            if UTILITY.contains(&sp.substance_id) {
                continue;
            }
            if let Some(ps) = producers.get(&sp.substance_id) {
                for &pi in ps {
                    if epoch_of(rxns[pi]) == e {
                        d = d.max(depth[pi] + 1);
                    }
                }
            }
        }
        depth[i] = d.min(5); // cap so a long chain doesn't stretch one era forever
        for p in &r.products {
            producers.entry(p.substance_id).or_default().push(i);
        }
    }

    // Columns: each era gets (max depth + 1) sub-columns, laid out left to right.
    let mut epoch_cols = vec![1usize; n_epochs];
    for (i, r) in rxns.iter().enumerate() {
        let e = epoch_of(r);
        epoch_cols[e] = epoch_cols[e].max(depth[i] + 1);
    }
    let mut epoch_first_col = vec![0usize; n_epochs];
    for e in 1..n_epochs {
        epoch_first_col[e] = epoch_first_col[e - 1] + epoch_cols[e - 1];
    }
    let total_cols: usize = epoch_cols.iter().sum();

    let mut rows_in_col: HashMap<usize, usize> = HashMap::new();
    let mut nodes: Vec<NodeInfo> = Vec::new();
    let mut pos: HashMap<u32, (usize, usize, usize)> = HashMap::new(); // id -> (epoch, col, row)
    for (i, r) in rxns.iter().enumerate() {
        let e = epoch_of(r);
        let col = epoch_first_col[e] + depth[i];
        let row = *rows_in_col.get(&col).unwrap_or(&0);
        rows_in_col.insert(col, row + 1);
        pos.insert(r.id, (e, col, row));
        nodes.push(NodeInfo {
            id: r.id,
            name: r.name.clone(),
            epoch: e,
            col,
            row,
            state: node_state(r, &progress, &unlocks),
        });
    }
    let max_rows = rows_in_col.values().copied().max().unwrap_or(1);
    let done_total = nodes.iter().filter(|n| n.state == NodeState::Completed).count();
    let avail_total = nodes.iter().filter(|n| n.state == NodeState::Available).count();
    if let Ok(mut t) = summary_q.single_mut() {
        t.0 = format!("{} of {} steps done  ·  {} ready to make", done_total, nodes.len(), avail_total);
    }

    // Edges: producer -> consumer, for meaningful (low fan-in, non-utility) intermediates.
    let mut all_producers: HashMap<u32, Vec<u32>> = HashMap::new();
    for r in &rxns {
        for p in &r.products {
            all_producers.entry(p.substance_id).or_default().push(r.id);
        }
    }
    let mut edges: Vec<(u32, u32)> = Vec::new();
    for r in &rxns {
        for sp in &r.reactants {
            let sid = sp.substance_id;
            if UTILITY.contains(&sid) {
                continue;
            }
            if let Some(prods) = all_producers.get(&sid) {
                if prods.len() > 2 {
                    continue; // high fan-in => treat as a utility, skip
                }
                for &p in prods {
                    if p != r.id {
                        edges.push((p, r.id));
                    }
                }
            }
        }
    }
    edges.sort();
    edges.dedup();

    // ---- build the GRAPH ----
    let content_h = BAND_H + PAD * 2.0 + max_rows as f32 * ROW_H;
    if let Ok((graph, mut graph_node)) = graph_q.single_mut() {
        graph_node.width = Val::Px(col_x(total_cols, n_epochs) + PAD);
        graph_node.min_height = Val::Px(content_h);
        graph_node.height = Val::Px(content_h);
        commands.entity(graph).despawn_children();
        let state_by_id: HashMap<u32, NodeState> = nodes.iter().map(|n| (n.id, n.state)).collect();
        commands.entity(graph).with_children(|parent| {
            // era bands: a faint column per era, with its header and a progress bar
            for e in 0..n_epochs {
                let in_epoch: Vec<&NodeInfo> = nodes.iter().filter(|n| n.epoch == e).collect();
                let done = in_epoch.iter().filter(|n| n.state == NodeState::Completed).count();
                let x = col_x(epoch_first_col[e], e) - EPOCH_GAP * 0.4;
                let w = epoch_cols[e] as f32 * COL_W - (COL_W - NODE_W) + EPOCH_GAP * 0.8;
                let current = in_epoch.iter().any(|n| n.state == NodeState::Available);
                parent
                    .spawn((
                        Node {
                            position_type: PositionType::Absolute,
                            left: Val::Px(x),
                            top: Val::Px(8.0),
                            width: Val::Px(w),
                            height: Val::Px(content_h - 16.0),
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(3.0),
                            padding: UiRect::new(Val::Px(14.0), Val::Px(14.0), Val::Px(10.0), Val::Px(0.0)),
                            border: UiRect::all(Val::Px(1.0)),
                            ..default()
                        },
                        BorderRadius::all(Val::Px(theme::R_LG)),
                        BackgroundColor(if e % 2 == 0 {
                            theme::SURFACE.with_alpha(0.45)
                        } else {
                            theme::SURFACE.with_alpha(0.25)
                        }),
                        BorderColor::all(if current {
                            theme::GOLD.with_alpha(0.35)
                        } else {
                            theme::LINE.with_alpha(0.6)
                        }),
                        Pickable::IGNORE,
                    ))
                    .with_children(|h| {
                        let era = db.epochs.get(e).map(|d| d.era.clone()).unwrap_or_default();
                        h.spawn((
                            Node { align_items: AlignItems::Baseline, column_gap: Val::Px(8.0), ..default() },
                            Pickable::IGNORE,
                        ))
                        .with_children(|row| {
                            row.spawn((
                                theme::label(
                                    fonts,
                                    era_tag(e, n_epochs),
                                    10.0,
                                    Weight::Bold,
                                    if current { theme::GOLD } else { theme::TEXT_3 },
                                ),
                                Pickable::IGNORE,
                            ));
                            row.spawn((
                                theme::label(fonts, db.epoch_name(e as u8), theme::MD, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                            row.spawn((
                                theme::label(
                                    fonts,
                                    format!("{}/{}", done, in_epoch.len()),
                                    theme::XS,
                                    Weight::Regular,
                                    theme::TEXT_3,
                                ),
                                Pickable::IGNORE,
                            ));
                        });
                        h.spawn((
                            theme::label(fonts, era, theme::XS, Weight::Regular, theme::TEXT_3),
                            Pickable::IGNORE,
                        ));
                        let frac = if in_epoch.is_empty() { 0.0 } else { done as f32 / in_epoch.len() as f32 };
                        h.spawn((
                            Node {
                                width: Val::Percent(100.0),
                                height: Val::Px(3.0),
                                margin: UiRect::top(Val::Px(3.0)),
                                ..default()
                            },
                            BorderRadius::all(Val::Px(99.0)),
                            BackgroundColor(theme::LINE.with_alpha(0.7)),
                            Pickable::IGNORE,
                        ))
                        .with_children(|b| {
                            b.spawn((
                                Node { width: Val::Percent(frac * 100.0), height: Val::Percent(100.0), ..default() },
                                BorderRadius::all(Val::Px(99.0)),
                                BackgroundColor(theme::GREEN),
                                Pickable::IGNORE,
                            ));
                        });
                    });
            }

            // connectors first (so nodes paint on top)
            for (src, dst) in &edges {
                let (Some(&(se, sc, sr)), Some(&(te, tc, tr))) = (pos.get(src), pos.get(dst)) else {
                    continue;
                };
                let s_state = state_by_id.get(src).copied();
                let d_state = state_by_id.get(dst).copied();
                let line = match (s_state, d_state) {
                    (_, Some(NodeState::Completed)) => theme::GREEN.with_alpha(0.45),
                    (Some(NodeState::Completed), Some(NodeState::Available)) => theme::GOLD.with_alpha(0.6),
                    _ => theme::LINE.with_alpha(0.9),
                };
                let sx2 = col_x(sc, se) + NODE_W;
                let scy = node_y(sr) + NODE_H / 2.0;
                let tx1 = col_x(tc, te);
                let tcy = node_y(tr) + NODE_H / 2.0;
                let midx = if tx1 > sx2 { tx1 - GUTTER } else { sx2 + GUTTER };
                // Elbow: source-right -> midx, midx to target row, midx -> target-left. (left, top, w, h)
                let segs: [(f32, f32, f32, f32); 3] = [
                    (sx2.min(midx), scy - 1.0, (sx2 - midx).abs(), 2.0),
                    (midx - 1.0, scy.min(tcy), 2.0, (tcy - scy).abs()),
                    (midx.min(tx1), tcy - 1.0, (midx - tx1).abs(), 2.0),
                ];
                for (left, top, w, h) in segs {
                    parent.spawn((
                        Node {
                            position_type: PositionType::Absolute,
                            left: Val::Px(left),
                            top: Val::Px(top),
                            width: Val::Px(w.max(2.0)),
                            height: Val::Px(h.max(2.0)),
                            ..default()
                        },
                        BackgroundColor(line),
                        Pickable::IGNORE,
                    ));
                }
            }

            // nodes
            for n in &nodes {
                let Some(r) = rxns.iter().find(|x| x.id == n.id) else {
                    continue;
                };
                let sel = state.selected == Some(n.id);
                let (bg, border) = node_look(n.state, sel, false);
                let accent = theme::process_color(&r.process);
                let mut node = parent.spawn((
                    Button,
                    TechNodeButton(n.id, n.state),
                    Node {
                        position_type: PositionType::Absolute,
                        left: Val::Px(col_x(n.col, n.epoch)),
                        top: Val::Px(node_y(n.row)),
                        width: Val::Px(NODE_W),
                        height: Val::Px(NODE_H),
                        padding: UiRect::axes(Val::Px(8.0), Val::Px(6.0)),
                        column_gap: Val::Px(8.0),
                        align_items: AlignItems::Center,
                        border: UiRect::all(Val::Px(if n.state == NodeState::Available { 1.5 } else { 1.0 })),
                        ..default()
                    },
                    BorderRadius::all(Val::Px(theme::R_MD)),
                    BackgroundColor(bg),
                    BorderColor::all(border),
                ));
                if n.state == NodeState::Available {
                    node.insert(theme::glow(theme::GOLD.with_alpha(0.35), 14.0));
                }
                node.with_children(|b| {
                    let icon_c = if n.state == NodeState::Locked { theme::TEXT_3.with_alpha(0.6) } else { accent };
                    b.spawn((
                        ImageNode::new(assets.load(vessel_art_path(&r.process, "outline"))).with_color(icon_c),
                        Node { width: Val::Px(30.0), height: Val::Px(30.0), flex_shrink: 0.0, ..default() },
                        Pickable::IGNORE,
                    ));
                    b.spawn((
                        Node { flex_direction: FlexDirection::Column, flex_grow: 1.0, flex_shrink: 1.0, ..default() },
                        Pickable::IGNORE,
                    ))
                    .with_children(|c| {
                        let tc = if n.state == NodeState::Locked { theme::TEXT_3 } else { theme::TEXT };
                        c.spawn((
                            Text::new(n.name.clone()),
                            TextFont { font: fonts.semibold.clone(), font_size: 12.0, ..default() },
                            TextColor(tc),
                            Node { max_width: Val::Px(NODE_W - 72.0), ..default() },
                            Pickable::IGNORE,
                        ));
                        c.spawn((
                            theme::label(fonts, vessel_name(&r.process), 10.0, Weight::Regular, theme::TEXT_3),
                            Pickable::IGNORE,
                        ));
                    });
                    b.spawn(theme::icon(assets, state_icon(n.state), 12.0, state_accent(n.state)));
                });
            }
        });
    }

    // On opening, bring the frontier (the first step that is ready to make) into view.
    if just_opened {
        if let Some(n) = nodes.iter().find(|n| n.state == NodeState::Available) {
            for (marker, mut sp) in &mut scroll_q {
                if marker.graph {
                    sp.0.x = (col_x(n.col, n.epoch) - 260.0).max(0.0);
                    sp.0.y = (node_y(n.row) + NODE_H - 380.0).max(0.0);
                }
            }
        }
    }

    // ---- build the LIST ----
    if let Ok(list) = list_q.single() {
        commands.entity(list).despawn_children();
        commands.entity(list).with_children(|parent| {
            for (title, want) in [
                ("Ready to make", NodeState::Available),
                ("Completed", NodeState::Completed),
                ("Locked", NodeState::Locked),
            ] {
                let group: Vec<&NodeInfo> = nodes.iter().filter(|n| n.state == want).collect();
                if group.is_empty() {
                    continue;
                }
                parent
                    .spawn(Node {
                        align_items: AlignItems::Center,
                        column_gap: Val::Px(8.0),
                        margin: UiRect::new(Val::Px(4.0), Val::Px(0.0), Val::Px(14.0), Val::Px(4.0)),
                        ..default()
                    })
                    .with_children(|h| {
                        h.spawn(theme::icon(assets, state_icon(want), 14.0, state_accent(want)));
                        h.spawn(theme::label(fonts, title.to_uppercase(), theme::XS, Weight::Bold, theme::TEXT_2));
                        h.spawn(theme::label(
                            fonts,
                            group.len().to_string(),
                            theme::XS,
                            Weight::Regular,
                            theme::TEXT_3,
                        ));
                    });
                for n in group {
                    let Some(r) = rxns.iter().find(|x| x.id == n.id).copied() else {
                        continue;
                    };
                    let accent = theme::process_color(&r.process);
                    let sub =
                        if n.state == NodeState::Available { hint_string(r, subs) } else { equation_string(r, subs) };
                    let mut row = parent.spawn((
                        theme::button(
                            Kind::Row,
                            Node {
                                width: Val::Percent(100.0),
                                align_items: AlignItems::Center,
                                column_gap: Val::Px(12.0),
                                padding: UiRect::axes(Val::Px(10.0), Val::Px(7.0)),
                                ..default()
                            },
                            theme::R_MD,
                        ),
                        TechListEntry(n.id),
                    ));
                    if state.selected == Some(n.id) {
                        row.insert(Skin::active(Kind::Row, true));
                    }
                    row.with_children(|row| {
                        row.spawn((
                            ImageNode::new(assets.load(vessel_art_path(&r.process, "outline")))
                                .with_color(if n.state == NodeState::Locked { theme::TEXT_3 } else { accent }),
                            Node { width: Val::Px(30.0), height: Val::Px(30.0), flex_shrink: 0.0, ..default() },
                            Pickable::IGNORE,
                        ));
                        row.spawn((
                            Node {
                                flex_direction: FlexDirection::Column,
                                flex_grow: 1.0,
                                flex_shrink: 1.0,
                                ..default()
                            },
                            Pickable::IGNORE,
                        ))
                        .with_children(|c| {
                            c.spawn((
                                Node { column_gap: Val::Px(8.0), align_items: AlignItems::Baseline, ..default() },
                                Pickable::IGNORE,
                            ))
                            .with_children(|t| {
                                t.spawn((
                                    theme::label(
                                        fonts,
                                        n.name.clone(),
                                        theme::SM,
                                        Weight::Semibold,
                                        if n.state == NodeState::Locked { theme::TEXT_2 } else { theme::TEXT },
                                    ),
                                    Pickable::IGNORE,
                                ));
                                t.spawn((
                                    theme::label(
                                        fonts,
                                        db.epoch_name(n.epoch as u8),
                                        theme::XS,
                                        Weight::Regular,
                                        theme::TEXT_3,
                                    ),
                                    Pickable::IGNORE,
                                ));
                            });
                            c.spawn((
                                Text::new(sub),
                                TextFont { font: fonts.symbols.clone(), font_size: 11.5, ..default() },
                                TextColor(if n.state == NodeState::Available {
                                    theme::mix(theme::GOLD, theme::TEXT, 0.4)
                                } else {
                                    theme::TEXT_2
                                }),
                                Pickable::IGNORE,
                            ));
                        });
                        row.spawn(theme::icon(assets, state_icon(n.state), 14.0, state_accent(n.state)));
                    });
                }
            }
        });
    }
}

// ---------------------------------------------------------------------------------------
// Selection + hover look + detail bar
// ---------------------------------------------------------------------------------------
pub fn tech_node_click_system(
    nodes: Query<(&Interaction, &TechNodeButton), (Changed<Interaction>, With<Button>)>,
    entries: Query<(&Interaction, &TechListEntry), (Changed<Interaction>, With<Button>)>,
    mut state: ResMut<TechTreeState>,
    mut looks: Query<(&TechNodeButton, &Interaction, &mut BackgroundColor, &mut BorderColor)>,
    mut rows: Query<(&TechListEntry, &mut Skin)>,
) {
    let mut sel = state.selected;
    for (i, n) in &nodes {
        if *i == Interaction::Pressed {
            sel = Some(n.0);
        }
    }
    for (i, e) in &entries {
        if *i == Interaction::Pressed {
            sel = Some(e.0);
        }
    }
    let changed = sel != state.selected;
    if changed {
        state.selected = sel;
        for (e, mut skin) in &mut rows {
            let a = Some(e.0) == sel;
            if skin.active != a {
                skin.active = a;
            }
        }
    }
    if changed || !nodes.is_empty() {
        for (n, i, mut bg, mut border) in &mut looks {
            let (b, c) = node_look(n.1, Some(n.0) == sel, *i == Interaction::Hovered);
            bg.0 = b;
            *border = BorderColor::all(c);
        }
    }
}

pub fn update_tech_detail_system(
    mut commands: Commands,
    state: Res<TechTreeState>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    recipe_db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    bar_q: Query<Entity, With<TechDetailBar>>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    mut built_for: Local<Option<(Option<u32>, bool)>>,
) {
    let Ok(bar) = bar_q.single() else {
        return;
    };
    let (Some(db), Some(subs)) = (recipe_db.as_ref(), substances_assets.get(&game_data.substances)) else {
        return;
    };
    let key = (state.selected, state.open);
    if *built_for == Some(key) && !progress.is_changed() && !unlocks.is_changed() {
        return;
    }
    *built_for = Some(key);
    commands.entity(bar).despawn_children();
    let fonts = &*fonts;
    let assets = &*assets;

    let Some(r) = state.selected.and_then(|id| db.authored.iter().find(|r| r.id == id)) else {
        commands.entity(bar).with_children(|p| {
            p.spawn(theme::icon(assets, "tree", 40.0, theme::LINE_STRONG));
            p.spawn(Node { flex_direction: FlexDirection::Column, row_gap: Val::Px(4.0), ..default() }).with_children(
                |c| {
                    c.spawn(theme::label(
                        fonts,
                        "Pick a step to see how to make it",
                        theme::LG,
                        Weight::Semibold,
                        theme::TEXT_2,
                    ));
                    c.spawn(theme::label(
                        fonts,
                        "Gold steps are ready now. Drag the map or use the wheel (Shift for sideways) to look around.",
                        theme::SM,
                        Weight::Regular,
                        theme::TEXT_3,
                    ));
                },
            );
        });
        return;
    };

    let st = node_state(r, &progress, &unlocks);
    let accent = theme::process_color(&r.process);
    let e = r.epoch.unwrap_or(0);
    let missing: Vec<String> = r
        .reactants
        .iter()
        .filter(|s| !progress.discovered.contains(&s.substance_id))
        .map(|s| subs.0.get(&s.substance_id).map(|x| x.name.clone()).unwrap_or_else(|| format!("#{}", s.substance_id)))
        .collect();
    let process_locked = !unlocks.0.contains(&r.process);
    let known = r.reactants.iter().chain(r.products.iter()).all(|s| progress.discovered.contains(&s.substance_id));

    commands.entity(bar).with_children(|p| {
        p.spawn((
            Node {
                width: Val::Px(92.0),
                height: Val::Px(92.0),
                flex_shrink: 0.0,
                padding: UiRect::all(Val::Px(10.0)),
                border: UiRect::all(Val::Px(1.0)),
                ..default()
            },
            BorderRadius::all(Val::Px(theme::R_LG)),
            BackgroundColor(theme::mix(theme::BG, accent, 0.12)),
            BorderColor::all(accent.with_alpha(0.5)),
        ))
        .with_children(|c| {
            c.spawn((
                ImageNode::new(assets.load(vessel_art_path(&r.process, "outline")))
                    .with_color(if st == NodeState::Locked { theme::TEXT_3 } else { accent }),
                Node { width: Val::Percent(100.0), height: Val::Percent(100.0), ..default() },
            ));
        });
        p.spawn(Node {
            flex_direction: FlexDirection::Column,
            row_gap: Val::Px(5.0),
            flex_grow: 1.0,
            flex_shrink: 1.0,
            ..default()
        })
        .with_children(|c| {
            c.spawn(Node { align_items: AlignItems::Center, column_gap: Val::Px(8.0), ..default() }).with_children(
                |t| {
                    theme::spawn_chip(t, fonts, state_label(st), state_accent(st));
                    t.spawn(theme::label(
                        fonts,
                        format!("{}  ·  {}", db.epoch_name(e).to_uppercase(), vessel_name(&r.process)),
                        theme::XS,
                        Weight::Bold,
                        theme::TEXT_3,
                    ));
                },
            );
            c.spawn(theme::label(fonts, r.name.clone(), theme::LG, Weight::Bold, theme::TEXT));
            c.spawn((
                Text::new(equation_string(r, subs)),
                TextFont { font: fonts.symbols.clone(), font_size: 14.0, ..default() },
                TextColor(theme::mix(accent, theme::TEXT, 0.55)),
            ));
            let (line, color) = match st {
                NodeState::Locked => {
                    let mut why = String::new();
                    if process_locked {
                        why.push_str(&format!("Unlock the {} first. ", vessel_name(&r.process)));
                    }
                    if !missing.is_empty() {
                        why.push_str(&format!("Still need: {}.", missing.join(", ")));
                    }
                    (why, Color::srgb(1.0, 0.72, 0.55))
                }
                NodeState::Available => (hint_string(r, subs), theme::GOLD),
                NodeState::Completed => (hint_string(r, subs), theme::TEXT_2),
            };
            if !line.is_empty() {
                c.spawn(theme::para(fonts, line, theme::SM, color, Val::Px(900.0)));
            }
        });
        if known {
            theme::spawn_button(
                p,
                fonts,
                assets,
                Kind::Secondary,
                Some("book"),
                "Open in Reaction Library",
                TechOpenInLibrary(r.id),
            );
        }
    });
}

// ---------------------------------------------------------------------------------------
// Scrolling and panning
// ---------------------------------------------------------------------------------------
/// Drag the graph background to pan (a press that starts on a node selects it instead).
pub fn tech_pan_system(
    mouse: Res<ButtonInput<MouseButton>>,
    state: Res<TechTreeState>,
    windows: Query<&Window>,
    ui_scale: Res<UiScale>,
    nodes: Query<&Interaction, With<TechNodeButton>>,
    mut scroll_q: Query<(&TechScrollable, &mut ScrollPosition)>,
    mut last: Local<Option<Vec2>>,
) {
    if !state.open || state.mode != TechMode::Graph {
        *last = None;
        return;
    }
    let Some(win) = windows.iter().next() else {
        return;
    };
    let Some(cursor) = win.cursor_position() else {
        *last = None;
        return;
    };
    let s = ui_scale.0.max(0.01);
    let top = (theme::HEADER_H + TOOLBAR_H) * s;
    let bottom = win.height() - DETAIL_H * s;
    if mouse.just_pressed(MouseButton::Left) {
        let on_node = nodes.iter().any(|i| *i != Interaction::None);
        *last = (!on_node && cursor.y > top && cursor.y < bottom).then_some(cursor);
        return;
    }
    if !mouse.pressed(MouseButton::Left) {
        *last = None;
        return;
    }
    if let Some(prev) = *last {
        let d = (cursor - prev) / s;
        if d != Vec2::ZERO {
            for (marker, mut sp) in &mut scroll_q {
                if marker.graph {
                    sp.0.x = (sp.0.x - d.x).max(0.0);
                    sp.0.y = (sp.0.y - d.y).max(0.0);
                }
            }
        }
        *last = Some(cursor);
    }
}
