// src/ui/tech_tree.rs
//
// The tech tree: "what can I make next". The authored progression shown either as a node
// GRAPH (eras as columns, reactions as nodes, producer -> consumer lines between them) or a
// guided LIST. A step's recipe shows once it has been made: until then the tree gives its
// name, era and vessel, and whether its vessel is unlocked, so working out the recipe stays
// the player's. The "Show what's ready" setting (free play only) marks the steps that can be
// made now and shows every recipe. Any step not yet made can be aimed for: a goal, which Hint
// then leads toward.
//
// Design choices that keep this robust and testable:
//   * The graph is laid out ANALYTICALLY. Every node sits at a computed (x, y) inside a
//     fixed-size content node; connectors are axis-aligned elbow segments (plain UI Nodes)
//     whose rects come from those same coordinates. Scrolling moves nodes and lines
//     together and the geometry is deterministic.
//   * Everything is DERIVED from the RecipeDatabase at runtime: nodes = authored reactions;
//     edges = producer -> consumer between them (skipping ubiquitous utility substances and
//     high-fan-in ones so the graph stays a clean spine).
//   * Every prerequisite is expressed (plan_links): each ingredient or catalyst a step needs
//     beyond the starting shelf either has a line in the overview, or is counted on the
//     step's "+N" badge. Selecting a step draws all its links on top in the selection colour
//     (from the earliest step that makes each one), and the detail bar lists each need with
//     the step it comes from, one tap away.
//   * The graph pans with the wheel (Shift for sideways) or by dragging the background, and
//     zooms out with its zoom bar, Ctrl and the wheel, or a pinch.
use crate::ui::{Button, Clicked, Look};
use bevy::picking::hover::Hovered;
use bevy::prelude::*;
use bevy::ui::Pressed;
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
use crate::ui::virtual_list::{VirtualCanvas, VirtualList};
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
/// Between the graph's scroll view and its canvas: the canvas's size at the zoom, so the view
/// scrolls over the graph as drawn.
#[derive(Component)]
pub struct TechGraphSizer;
/// The graph's zoom bar (shown with the graph): out, the level, in.
#[derive(Component)]
pub struct TechZoomBar;
#[derive(Component)]
pub struct TechZoomOut;
#[derive(Component)]
pub struct TechZoomIn;
#[derive(Component)]
pub struct TechZoomLabel;

/// How far the graph is zoomed (1 is full size; it only zooms out from there).
#[derive(Resource, Clone, Copy, Debug, PartialEq)]
pub struct TechZoom(pub f32);

impl Default for TechZoom {
    fn default() -> Self {
        Self(1.0)
    }
}

/// The graph's zoom steps, full size first.
pub const TECH_ZOOMS: [f32; 6] = [1.0, 0.8, 0.65, 0.5, 0.4, 0.3];

impl TechZoom {
    /// The next step out (or in), staying within TECH_ZOOMS.
    pub fn stepped(self, out: bool) -> f32 {
        let i = TECH_ZOOMS.iter().position(|z| (z - self.0).abs() < 0.01).unwrap_or(0) as i32;
        let j = (i + if out { 1 } else { -1 }).clamp(0, TECH_ZOOMS.len() as i32 - 1);
        TECH_ZOOMS[j as usize]
    }
}
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
/// The toolbar, its title and counts, and its legend with Graph / List: one row, or held
/// upright two (tech_toolbar_fit_system).
#[derive(Component)]
pub struct TechToolbar;
#[derive(Component)]
pub struct TechToolbarTitle;
#[derive(Component)]
pub struct TechToolbarTools;
#[derive(Component)]
pub struct TechOpenInLibrary(pub u32);
/// One of the legend's states (which show depends on TreeReveal).
#[derive(Component)]
pub struct TechLegendItem(pub NodeState);
/// Aim for a step: its goal substance joins the goals, first.
#[derive(Component)]
pub struct TechAim(pub u32);
/// Stop aiming for a goal substance.
#[derive(Component)]
pub struct TechStopAim(pub u32);
/// Make a goal the first priority.
#[derive(Component)]
pub struct TechAimFirst(pub u32);
/// The flag on a step the player is aiming for.
#[derive(Component)]
pub struct TechGoalFlag;
/// A graph node; remembers its state so the selection/hover look can be recomputed.
#[derive(Component)]
pub struct TechNodeButton(pub u32, pub NodeState);
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
#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum NodeState {
    Completed,
    /// can be made now (shown only with "Show what's ready")
    Available,
    /// not made yet, its vessel unlocked: whether it can be made now isn't shown
    Open,
    #[default]
    Locked,
}

/// Whether the tree shows what is ready and every recipe: the setting, in free play only.
#[derive(Resource, Default, Clone, Copy, PartialEq, Eq)]
pub struct TreeReveal(pub bool);

pub fn tree_reveal_system(
    settings: Res<crate::ui::settings::Settings>,
    challenge: Res<crate::ui::challenges::ChallengeMode>,
    mut reveal: ResMut<TreeReveal>,
) {
    let want = TreeReveal(settings.tree_ready && !challenge.playing());
    if *reveal != want {
        *reveal = want;
    }
}

/// The substance aiming at a step sets as a goal: its first product not yet found.
pub fn goal_of(r: &Reaction, progress: &PlayerProgress) -> Option<u32> {
    r.products.iter().map(|p| p.substance_id).find(|id| !progress.discovered.contains(id))
}

/// How many goals the player can hold at once; a new one past this lets the last go.
pub const MAX_GOALS: usize = 3;

/// Done (every product found), ready (vessel unlocked and every reactant found) or locked.
/// Unrevealed, ready and not-ready steps whose vessel is unlocked look the same (Open).
pub fn node_state(r: &Reaction, progress: &PlayerProgress, unlocks: &ProcessUnlocks, reveal: bool) -> NodeState {
    if r.products.iter().all(|p| progress.discovered.contains(&p.substance_id)) {
        return NodeState::Completed;
    }
    let vessel = unlocks.0.contains(&r.process);
    if !reveal {
        return if vessel { NodeState::Open } else { NodeState::Locked };
    }
    if vessel && r.reactants.iter().all(|s| progress.discovered.contains(&s.substance_id)) {
        NodeState::Available
    } else {
        NodeState::Locked
    }
}

fn state_accent(s: NodeState) -> Color {
    match s {
        NodeState::Completed => theme::GREEN,
        NodeState::Available => theme::GOLD,
        NodeState::Open => theme::CYAN,
        NodeState::Locked => theme::LINE_STRONG,
    }
}

/// (background, border) for a node in a state.
fn node_look(s: NodeState, selected: bool, hovered: bool) -> (Color, Color) {
    let (bg, border) = match s {
        NodeState::Completed => (theme::mix(theme::RAISED, theme::GREEN, 0.13), theme::GREEN.with_alpha(0.55)),
        NodeState::Available => (theme::mix(theme::RAISED, theme::GOLD, 0.17), theme::GOLD),
        NodeState::Open => (theme::RAISED, theme::LINE_STRONG),
        NodeState::Locked => (theme::SURFACE, theme::LINE),
    };
    let bg = if hovered { theme::mix(bg, theme::TEXT, 0.06) } else { bg };
    (bg, if selected { theme::CYAN } else { border })
}

fn state_icon(s: NodeState) -> &'static str {
    match s {
        NodeState::Completed => "check",
        NodeState::Available => "dot",
        NodeState::Open => "dot",
        NodeState::Locked => "lock",
    }
}

fn state_label(s: NodeState) -> &'static str {
    match s {
        NodeState::Completed => "Completed",
        NodeState::Available => "Ready to make",
        NodeState::Open => "Not made yet",
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
                TechToolbar,
                Node {
                    width: Val::Percent(100.0),
                    height: Val::Px(TOOLBAR_H),
                    flex_shrink: 0.0,
                    align_items: AlignItems::Center,
                    column_gap: Val::Px(18.0),
                    padding: UiRect::horizontal(Val::Px(18.0)),
                    border: UiRect::bottom(Val::Px(1.0)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE),
            ))
            .with_children(|bar| {
                bar.spawn((
                    TechToolbarTitle,
                    Node { flex_grow: 1.0, align_items: AlignItems::Baseline, column_gap: Val::Px(14.0), ..default() },
                ))
                .with_children(|t| {
                    t.spawn(theme::label(fonts, "Tech Tree", theme::XL, Weight::Semibold, theme::TEXT));
                    t.spawn((TechSummaryText, theme::label(fonts, "", theme::SM, Weight::Regular, theme::TEXT_2)));
                });
                bar.spawn((
                    TechToolbarTools,
                    Node { align_items: AlignItems::Center, column_gap: Val::Px(18.0), ..default() },
                ))
                .with_children(|r| {
                    // legend
                    r.spawn(Node { align_items: AlignItems::Center, column_gap: Val::Px(14.0), ..default() })
                        .with_children(|lg| {
                            for s in [NodeState::Completed, NodeState::Available, NodeState::Open, NodeState::Locked] {
                                lg.spawn((
                                    TechLegendItem(s),
                                    Node {
                                        align_items: AlignItems::Center,
                                        column_gap: Val::Px(6.0),
                                        // tech_legend_system shows Ready or Not made yet
                                        display: if s == NodeState::Available { Display::None } else { Display::Flex },
                                        ..default()
                                    },
                                ))
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
                            border_radius: BorderRadius::all(Val::Px(99.0)),
                            padding: UiRect::all(Val::Px(3.0)),
                            column_gap: Val::Px(2.0),
                            border: UiRect::all(Val::Px(1.0)),
                            ..default()
                        },
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
                });
                theme::spawn_icon_button(bar, assets, "close", 32.0, theme::TEXT_2, TechCloseButton);
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
                        TechGraphSizer,
                        Node {
                            position_type: PositionType::Relative,
                            width: Val::Px(PAD * 2.0),
                            height: Val::Px(PAD * 2.0),
                            flex_shrink: 0.0,
                            ..default()
                        },
                    ))
                    .with_children(|sz| {
                        sz.spawn((
                            TechGraphContent,
                            // only what is in sight is built (tech_graph_window_system)
                            VirtualCanvas::default(),
                            // scaled to the zoom about its top-left corner (tech_zoom_apply_system)
                            UiTransform::default(),
                            Node {
                                position_type: PositionType::Absolute,
                                left: Val::Px(0.0),
                                top: Val::Px(0.0),
                                width: Val::Px(PAD * 2.0),
                                height: Val::Px(PAD * 2.0),
                                ..default()
                            },
                        ));
                    });
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
                        // rows sit in fixed cells; only those in sight are built
                        VirtualList::new(Vec2::new(0.0, LIST_ROW_H), Vec2::new(0.0, LIST_ROW_GAP)),
                        Node {
                            position_type: PositionType::Relative,
                            width: Val::Percent(100.0),
                            max_width: Val::Px(980.0),
                            flex_shrink: 0.0,
                            ..default()
                        },
                    ));
                });
                // the graph's zoom: out, the level, in (Ctrl and the wheel, or a pinch, do the same)
                body.spawn((
                    TechZoomBar,
                    Node {
                        position_type: PositionType::Absolute,
                        right: Val::Px(12.0),
                        top: Val::Px(12.0),
                        align_items: AlignItems::Center,
                        column_gap: Val::Px(2.0),
                        padding: UiRect::all(Val::Px(3.0)),
                        border: UiRect::all(Val::Px(1.0)),
                        border_radius: BorderRadius::all(Val::Px(99.0)),
                        ..default()
                    },
                    BackgroundColor(theme::SURFACE.with_alpha(0.92)),
                    BorderColor::all(theme::LINE),
                ))
                .with_children(|z| {
                    theme::spawn_icon_button(
                        z,
                        assets,
                        "minus",
                        34.0,
                        theme::TEXT,
                        (TechZoomOut, crate::ui::onboarding::Tip::Text("Zoom out", "See more of the tree.")),
                    );
                    z.spawn((
                        TechZoomLabel,
                        theme::label(fonts, "100%", theme::XS, Weight::Semibold, theme::TEXT_2),
                        TextLayout::justify(Justify::Center),
                        Node { min_width: Val::Px(40.0), ..default() },
                        Pickable::IGNORE,
                    ));
                    theme::spawn_icon_button(
                        z,
                        assets,
                        "plus",
                        34.0,
                        theme::TEXT,
                        (TechZoomIn, crate::ui::onboarding::Tip::Text("Zoom in", "Back toward full size.")),
                    );
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
    closes: Query<(), (With<Clicked>, With<TechCloseButton>)>,
    modes: Query<&TechModeButton, With<Clicked>>,
    opens: Query<&TechOpenInLibrary, With<Clicked>>,
    mut state: ResMut<TechTreeState>,
    mut rlib: ResMut<ReactionLibState>,
    mut root_q: Query<&mut Node, With<TechRoot>>,
) {
    if !closes.is_empty() {
        state.open = false;
    }
    for m in &modes {
        if state.mode != m.0 {
            state.mode = m.0;
        }
    }
    for o in &opens {
        state.open = false;
        rlib.show(o.0);
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

/// The legend shows "Ready to make" or "Not made yet", as the tree does.
pub fn tech_legend_system(reveal: Res<TreeReveal>, mut items: Query<(&TechLegendItem, &mut Node)>) {
    if !reveal.is_changed() {
        return;
    }
    for (item, mut node) in &mut items {
        let shown = match item.0 {
            NodeState::Available => reveal.0,
            NodeState::Open => !reveal.0,
            _ => true,
        };
        let d = if shown { Display::Flex } else { Display::None };
        if node.display != d {
            node.display = d;
        }
    }
}

/// Aiming: a step's goal joins the goals first (the last lets go past MAX_GOALS), stops, or
/// moves to the front.
#[allow(clippy::type_complexity)]
pub fn tech_goal_system(
    aims: Query<&TechAim, With<Clicked>>,
    stops: Query<&TechStopAim, With<Clicked>>,
    firsts: Query<&TechAimFirst, With<Clicked>>,
    mut progress: ResMut<PlayerProgress>,
) {
    for a in &aims {
        if !progress.goals.contains(&a.0) && !progress.discovered.contains(&a.0) {
            progress.goals.insert(0, a.0);
            progress.goals.truncate(MAX_GOALS);
        }
    }
    for s in &stops {
        if progress.goals.contains(&s.0) {
            progress.goals.retain(|g| *g != s.0);
        }
    }
    for f in &firsts {
        if let Some(i) = progress.goals.iter().position(|g| *g == f.0).filter(|i| *i > 0) {
            let g = progress.goals.remove(i);
            progress.goals.insert(0, g);
        }
    }
}

// ---------------------------------------------------------------------------------------
// Populate both views (rebuilt on open / discovery change)
// ---------------------------------------------------------------------------------------
/// Substances so common an overview line from their makers would knot the graph: water,
/// oxygen, carbon dioxide, hydrogen. They are still prerequisites (see plan_links).
const UTILITY: &[u32] = &[8, 5, 12, 1];

/// One ingredient or catalyst a step needs that the shelf does not start with.
#[derive(Clone, Debug, PartialEq)]
pub struct Need {
    pub substance: u32,
    pub catalyst: bool,
    /// the earliest other step that makes it
    pub from: Option<u32>,
    /// a milestone hands it out
    pub granted: bool,
    /// an overview line already shows where it comes from
    pub drawn: bool,
}

/// The tech graph's links, worked out from the content alone.
#[derive(Default)]
pub struct LinkPlan {
    /// the lines the overview always draws (producer, consumer): reactants made by at most
    /// two steps, apart from the utility substances
    pub overview: Vec<(u32, u32)>,
    /// step -> everything it needs beyond the starting shelf, in recipe order
    pub needs: HashMap<u32, Vec<Need>>,
}

impl LinkPlan {
    /// Every link: the overview's, and one from the earliest maker of each need.
    pub fn links(&self) -> Vec<(u32, u32)> {
        let mut all = self.overview.clone();
        for (&step, needs) in &self.needs {
            all.extend(needs.iter().filter_map(|n| n.from.map(|p| (p, step))));
        }
        all.sort();
        all.dedup();
        all
    }

    /// How many of a step's needs have no overview line: the number on its badge.
    pub fn undrawn(&self, step: u32) -> usize {
        self.needs.get(&step).map_or(0, |n| n.iter().filter(|n| !n.drawn).count())
    }
}

/// Every prerequisite of every step, and which of them the overview draws.
pub fn plan_links(db: &RecipeDatabase) -> LinkPlan {
    let start: std::collections::HashSet<u32> = db.start.iter().copied().collect();
    let granted: std::collections::HashSet<u32> = db.milestones.iter().flat_map(|m| m.grant.iter().copied()).collect();
    // makers of each substance, in tree order (era, then id)
    let mut makers: HashMap<u32, Vec<u32>> = HashMap::new();
    for r in &db.authored {
        for p in &r.products {
            let v = makers.entry(p.substance_id).or_default();
            if !v.contains(&r.id) {
                v.push(r.id);
            }
        }
    }
    let mut plan = LinkPlan::default();
    for r in &db.authored {
        let inputs =
            r.reactants.iter().map(|s| (s.substance_id, false)).chain(r.required_catalyst().map(|c| (c, true)));
        let mut seen = Vec::new();
        for (s, catalyst) in inputs {
            if seen.contains(&s) {
                continue;
            }
            seen.push(s);
            let all = makers.get(&s).map_or(&[][..], |v| v.as_slice());
            let others: Vec<u32> = all.iter().copied().filter(|&p| p != r.id).collect();
            let drawn = !catalyst && !UTILITY.contains(&s) && all.len() <= 2 && !others.is_empty();
            if drawn {
                plan.overview.extend(others.iter().map(|&p| (p, r.id)));
            }
            if !start.contains(&s) {
                plan.needs.entry(r.id).or_default().push(Need {
                    substance: s,
                    catalyst,
                    from: others.first().copied(),
                    granted: granted.contains(&s),
                    drawn,
                });
            }
        }
    }
    plan.overview.sort();
    plan.overview.dedup();
    plan
}

/// The last graph build's links and where each step sits, so a selection can draw its own
/// links and the detail bar can list its needs without rebuilding the graph.
#[derive(Resource, Default)]
pub struct TechLinks {
    /// (producer, consumer): every link (LinkPlan::links)
    pub all: Vec<(u32, u32)>,
    /// step -> what it needs
    pub needs: HashMap<u32, Vec<Need>>,
    /// step id -> (era, column, row)
    at: HashMap<u32, (usize, usize, usize)>,
    graph: Option<Entity>,
    /// a step to scroll into view (a need's chip was tapped)
    reveal: Option<u32>,
}

impl TechLinks {
    /// Scroll the graph to a step (centring it), as tapping a need does.
    pub fn reveal(&mut self, step: u32) {
        self.reveal = Some(step);
    }
}

/// The "+N" on a step: how many of its needs have no overview line.
#[derive(Component)]
pub struct TechNeedBadge {
    pub step: u32,
    pub count: usize,
}

/// A need in the detail bar; tapping it goes to the step that makes it.
#[derive(Component)]
pub struct TechNeedButton(pub Option<u32>);

/// One segment of a selected step's links.
#[derive(Component)]
pub struct SelectionLink;

/// The three segments of the elbow from one step's right edge to another's left edge, as
/// (left, top, width, height), `t` thick.
fn elbow(
    (se, sc, sr): (usize, usize, usize),
    (te, tc, tr): (usize, usize, usize),
    t: f32,
) -> [(f32, f32, f32, f32); 3] {
    let sx2 = col_x(sc, se) + NODE_W;
    let scy = node_y(sr) + NODE_H / 2.0;
    let tx1 = col_x(tc, te);
    let tcy = node_y(tr) + NODE_H / 2.0;
    let midx = if tx1 > sx2 { tx1 - GUTTER } else { sx2 + GUTTER };
    let h = t / 2.0;
    [
        (sx2.min(midx), scy - h, (sx2 - midx).abs().max(t), t),
        (midx - h, scy.min(tcy) - h, t, (tcy - scy).abs() + t),
        (midx.min(tx1), tcy - h, (midx - tx1).abs().max(t), t),
    ]
}

struct NodeInfo {
    id: u32,
    name: String,
    epoch: usize,
    /// Global column index (eras are split into depth sub-columns).
    col: usize,
    row: usize,
    state: NodeState,
    /// needs with no overview line: the number on the step's badge
    undrawn: usize,
    /// the step makes one of the player's goals: its priority (0 = first)
    goal: Option<usize>,
}

/// An era's band behind its columns, with its heading and progress.
struct Band {
    epoch: usize,
    x: f32,
    w: f32,
    done: usize,
    total: usize,
    current: bool,
}

/// One overview line: the elbow's three segments (left, top, width, height) and its colour.
struct Edge {
    segments: [(f32, f32, f32, f32); 3],
    color: Color,
}

/// Something on the graph that is built when it comes near the view.
#[derive(Clone, Copy, Debug)]
enum GraphItem {
    Band(usize),
    Edge(usize),
    Node(usize),
}

/// The list's groups, in order: (title, state), what is ready first when that is shown.
fn groups(reveal: bool) -> [(&'static str, NodeState); 3] {
    if reveal {
        [("Ready to make", NodeState::Available), ("Completed", NodeState::Completed), ("Locked", NodeState::Locked)]
    } else {
        [("Not made yet", NodeState::Open), ("Completed", NodeState::Completed), ("Vessel locked", NodeState::Locked)]
    }
}
/// A list id at or above this is a group heading (HEADING_BASE + its index in GROUPS).
const HEADING_BASE: u32 = u32::MAX - 15;
const LIST_ROW_H: f32 = 52.0;
const LIST_ROW_GAP: f32 = 4.0;

/// Everything the graph and the list show, worked out from the content and the player's
/// progress: each step, line and era band with its place, and the list's order. Working it
/// out is cheap; only what is in sight gets built (tech_graph_window_system and
/// tech_list_window_system), so the tree opens at once however many steps it holds.
#[derive(Resource, Default)]
pub struct TechLayout {
    nodes: Vec<NodeInfo>,
    bands: Vec<Band>,
    edges: Vec<Edge>,
    items: Vec<GraphItem>,
    rects: Vec<Rect>,
    width: f32,
    height: f32,
    /// node index by step id
    index: HashMap<u32, usize>,
    /// the list: group headings and step ids, in order
    list: Vec<u32>,
    /// how many steps each list group holds
    group_len: [usize; 3],
    /// the list's groups (titles and states), as revealed or not
    groups: [(&'static str, NodeState); 3],
}

/// Left x of a global column, accounting for the extra gap at each era boundary.
fn col_x(col: usize, epoch: usize) -> f32 {
    PAD + col as f32 * COL_W + epoch as f32 * EPOCH_GAP
}

fn node_y(row: usize) -> f32 {
    BAND_H + PAD + row as f32 * ROW_H
}

impl TechLayout {
    /// Lay out every authored step: eras as columns (split by depth within the era), steps
    /// down each column, the overview's lines between them, and the list's groups.
    fn work_out(
        db: &RecipeDatabase,
        plan: &LinkPlan,
        progress: &PlayerProgress,
        unlocks: &ProcessUnlocks,
        reveal: bool,
    ) -> Self {
        // Authored reactions, already sorted by (epoch, id).
        let rxns: &[Reaction] = &db.authored;
        let n_epochs = db.epochs.len().max(1);
        let epoch_of = |r: &Reaction| (r.epoch as usize).min(n_epochs - 1);

        // Producer map over EARLIER authored reactions only (keeps the depth pass acyclic).
        // Utility substances that appear everywhere never create depth or edges.
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
                        if epoch_of(&rxns[pi]) == e {
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

        let mut out = TechLayout { groups: groups(reveal), ..default() };
        let mut rows_in_col: HashMap<usize, usize> = HashMap::new();
        for (i, r) in rxns.iter().enumerate() {
            let e = epoch_of(r);
            let col = epoch_first_col[e] + depth[i];
            let row = *rows_in_col.get(&col).unwrap_or(&0);
            rows_in_col.insert(col, row + 1);
            out.index.insert(r.id, out.nodes.len());
            out.nodes.push(NodeInfo {
                id: r.id,
                name: r.name.clone(),
                epoch: e,
                col,
                row,
                state: node_state(r, progress, unlocks, reveal),
                undrawn: plan.undrawn(r.id),
                goal: progress.goals.iter().position(|g| r.products.iter().any(|p| p.substance_id == *g)),
            });
        }
        let max_rows = rows_in_col.values().copied().max().unwrap_or(1);
        out.height = BAND_H + PAD * 2.0 + max_rows as f32 * ROW_H;
        out.width = col_x(total_cols, n_epochs) + PAD;

        // era bands: a faint column per era, with its header and a progress bar; the current
        // era holds something ready (shown), or else the first step not made yet
        let frontier = out.nodes.iter().find(|n| n.state == NodeState::Open).map(|n| n.epoch);
        for e in 0..n_epochs {
            let in_epoch = out.nodes.iter().filter(|n| n.epoch == e);
            let (mut done, mut total, mut current) = (0, 0, false);
            for n in in_epoch {
                total += 1;
                done += usize::from(n.state == NodeState::Completed);
                current |= n.state == NodeState::Available;
            }
            current |= !reveal && frontier == Some(e);
            out.bands.push(Band {
                epoch: e,
                x: col_x(epoch_first_col[e], e) - EPOCH_GAP * 0.4,
                w: epoch_cols[e] as f32 * COL_W - (COL_W - NODE_W) + EPOCH_GAP * 0.8,
                done,
                total,
                current,
            });
        }

        // the overview's lines, coloured by how far along each end is
        for (src, dst) in &plan.overview {
            let (Some(&si), Some(&di)) = (out.index.get(src), out.index.get(dst)) else { continue };
            let (s, d) = (&out.nodes[si], &out.nodes[di]);
            let color = match (s.state, d.state) {
                (_, NodeState::Completed) => theme::GREEN.with_alpha(0.45),
                (NodeState::Completed, NodeState::Available) => theme::GOLD.with_alpha(0.6),
                _ => theme::LINE.with_alpha(0.9),
            };
            let segments = elbow((s.epoch, s.col, s.row), (d.epoch, d.col, d.row), 2.0)
                .map(|(l, t, w, h)| (l, t, w.max(2.0), h.max(2.0)));
            out.edges.push(Edge { segments, color });
        }

        // what the window places: bands, lines, steps (each with the rect it covers)
        for (i, b) in out.bands.iter().enumerate() {
            out.items.push(GraphItem::Band(i));
            out.rects.push(Rect::new(b.x, 8.0, b.x + b.w, out.height - 8.0));
        }
        for (i, e) in out.edges.iter().enumerate() {
            out.items.push(GraphItem::Edge(i));
            out.rects.push(edge_bounds(&e.segments));
        }
        for (i, n) in out.nodes.iter().enumerate() {
            let (x, y) = (col_x(n.col, n.epoch), node_y(n.row));
            out.items.push(GraphItem::Node(i));
            // the badge pokes out to the left
            out.rects.push(Rect::new(x - 12.0, y, x + NODE_W, y + NODE_H));
        }

        // the list: each group under its heading
        for (g, (_, want)) in out.groups.iter().enumerate() {
            let ids: Vec<u32> = out.nodes.iter().filter(|n| n.state == *want).map(|n| n.id).collect();
            out.group_len[g] = ids.len();
            if !ids.is_empty() {
                out.list.push(HEADING_BASE + g as u32);
                out.list.extend(ids);
            }
        }
        out
    }

    /// Where a step sits: (era, column, row).
    fn at(&self) -> HashMap<u32, (usize, usize, usize)> {
        self.nodes.iter().map(|n| (n.id, (n.epoch, n.col, n.row))).collect()
    }

    /// How many steps are laid out (for the checks).
    pub fn steps(&self) -> usize {
        self.nodes.len()
    }

    /// The steps whose place overlaps `view` (content pixels): all of them must be built
    /// while it is in sight (for the checks).
    pub fn steps_in(&self, view: Rect) -> Vec<u32> {
        self.nodes
            .iter()
            .filter(|n| {
                let (x, y) = (col_x(n.col, n.epoch), node_y(n.row));
                x < view.max.x && view.min.x < x + NODE_W && y < view.max.y && view.min.y < y + NODE_H
            })
            .map(|n| n.id)
            .collect()
    }

    /// The graph's full size (for the checks).
    pub fn size(&self) -> Vec2 {
        Vec2::new(self.width, self.height)
    }
}

/// The rect an elbow's segments cover.
fn edge_bounds(segments: &[(f32, f32, f32, f32); 3]) -> Rect {
    let mut r = Rect::new(segments[0].0, segments[0].1, segments[0].0 + segments[0].2, segments[0].1 + segments[0].3);
    for &(l, t, w, h) in &segments[1..] {
        r = r.union(Rect::new(l, t, l + w, t + h));
    }
    r
}

/// Works the layout out again when the tree opens and when progress changes while it is
/// open; the window systems then build what is in sight.
#[allow(clippy::too_many_arguments)]
pub fn populate_tech_views_system(
    mut commands: Commands,
    state: Res<TechTreeState>,
    recipe_db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    mut graph_q: Query<(&mut Node, &mut VirtualCanvas), With<TechGraphContent>>,
    graph_e: Query<Entity, With<TechGraphContent>>,
    mut list_q: Query<&mut VirtualList, With<TechListContent>>,
    mut scroll_q: Query<(&TechScrollable, &mut ScrollPosition, &ComputedNode)>,
    mut summary_q: Query<&mut Text, With<TechSummaryText>>,
    mut prev_open: Local<bool>,
    mut links: ResMut<TechLinks>,
    mut layout: ResMut<TechLayout>,
    reveal: Res<TreeReveal>,
    zoom: Res<TechZoom>,
) {
    let just_opened = state.open && !*prev_open;
    let should = state.open && (just_opened || progress.is_changed() || unlocks.is_changed() || reveal.is_changed());
    *prev_open = state.open;
    if !should {
        return;
    }
    let Some(db) = recipe_db.as_ref() else {
        return;
    };

    // Links: the overview's lines, and everything each step needs (plan_links).
    let plan = plan_links(db);
    *layout = TechLayout::work_out(db, &plan, &progress, &unlocks, reveal.0);
    let done = layout.nodes.iter().filter(|n| n.state == NodeState::Completed).count();
    let ready = layout.nodes.iter().filter(|n| n.state == NodeState::Available).count();
    if let Ok(mut t) = summary_q.single_mut() {
        t.0 = if reveal.0 {
            format!("{} of {} steps done  ·  {} ready to make", done, layout.nodes.len(), ready)
        } else {
            format!("{} of {} steps done", done, layout.nodes.len())
        };
    }
    links.all = plan.links();
    links.needs = plan.needs;
    links.at = layout.at();
    links.graph = graph_e.single().ok();

    // the graph: full size (so it scrolls as before), nothing built until it is in sight
    if let Ok((mut node, mut canvas)) = graph_q.single_mut() {
        node.width = Val::Px(layout.width);
        node.min_height = Val::Px(layout.height);
        node.height = Val::Px(layout.height);
        for e in canvas.set(layout.rects.clone()) {
            commands.entity(e).try_despawn();
        }
    }
    // the list: rebuilt rows (a step's group and look follow its state)
    if let Ok(mut list) = list_q.single_mut() {
        for e in list.clear() {
            commands.entity(e).try_despawn();
        }
        list.set(layout.list.clone(), []);
    }

    // On opening, bring the selected step (opened from a hint) or else the frontier (the
    // first step that is ready to make) into view.
    if just_opened {
        let selected = state.selected.and_then(|id| layout.index.get(&id)).map(|&i| &layout.nodes[i]);
        let frontier = |n: &&NodeInfo| matches!(n.state, NodeState::Available | NodeState::Open);
        if let Some(n) = selected.or_else(|| layout.nodes.iter().find(frontier)) {
            let centred = selected.is_some();
            for (marker, mut sp, cn) in &mut scroll_q {
                if marker.graph {
                    // (graph px times the zoom: where it sits as drawn)
                    let z = zoom.0;
                    if centred {
                        let view = cn.size * cn.inverse_scale_factor();
                        let centre = Vec2::new(col_x(n.col, n.epoch) + NODE_W / 2.0, node_y(n.row) + NODE_H / 2.0);
                        sp.0 = (centre * z - view / 2.0).max(Vec2::ZERO);
                    } else {
                        sp.0.x = (col_x(n.col, n.epoch) * z - 260.0).max(0.0);
                        sp.0.y = ((node_y(n.row) + NODE_H) * z - 380.0).max(0.0);
                    }
                }
            }
        }
    }
}

/// Builds the graph's bands, lines and steps within a screen of the view, and drops those
/// more than two screens away; a closed tree, or the list showing, builds none.
#[allow(clippy::too_many_arguments)]
pub fn tech_graph_window_system(
    mut commands: Commands,
    state: Res<TechTreeState>,
    layout: Res<TechLayout>,
    recipe_db: Option<Res<RecipeDatabase>>,
    focus: Option<Res<crate::ui::focus::KeyFocus>>,
    mut graph_q: Query<(Entity, &mut VirtualCanvas), With<TechGraphContent>>,
    view_q: Query<(&TechScrollable, &ComputedNode, &ScrollPosition)>,
    pressed: Query<(), (With<TechNodeButton>, Or<(With<Pressed>, With<Clicked>)>)>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    zoom: Res<TechZoom>,
) {
    let Ok((graph, mut canvas)) = graph_q.single_mut() else {
        return;
    };
    let z = zoom.0.max(0.01);
    let view = if state.open && state.mode == TechMode::Graph {
        view_q
            .iter()
            .find(|(m, _, _)| m.graph)
            .map(|(_, cn, sp)| Rect::from_corners(sp.0 / z, (sp.0 + cn.size * cn.inverse_scale_factor()) / z))
            .unwrap_or_default()
    } else {
        Rect::default()
    };
    let focused = focus.and_then(|f| f.entity);
    let keep = |e: Entity| Some(e) == focused || pressed.contains(e);
    let Some(pass) = canvas.plan(view, keep) else {
        return;
    };
    for e in pass.drop {
        commands.entity(e).try_despawn();
    }
    let Some(db) = recipe_db.as_ref() else {
        return;
    };
    for i in pass.build {
        let Some(&item) = layout.items.get(i) else { continue };
        let e = match item {
            GraphItem::Band(b) => spawn_band(&mut commands, &fonts, db, &layout.bands[b], layout.height),
            GraphItem::Edge(k) => spawn_edge(&mut commands, &layout.edges[k]),
            GraphItem::Node(n) => {
                let info = &layout.nodes[n];
                let Some(r) = db.authored.get(n).filter(|r| r.id == info.id) else { continue };
                spawn_node(&mut commands, &fonts, &assets, info, r, state.selected == Some(info.id))
            }
        };
        commands.entity(graph).add_child(e);
        canvas.record(i, e);
    }
}

/// An era's band: a faint column with the era's name, its done/total and a progress bar.
fn spawn_band(commands: &mut Commands, fonts: &UiFonts, db: &RecipeDatabase, b: &Band, height: f32) -> Entity {
    let n_epochs = db.epochs.len().max(1);
    let era = db.epochs.get(b.epoch).map(|d| d.era.clone()).unwrap_or_default();
    commands
        .spawn((
            Node {
                border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                position_type: PositionType::Absolute,
                left: Val::Px(b.x),
                top: Val::Px(8.0),
                width: Val::Px(b.w),
                height: Val::Px(height - 16.0),
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(3.0),
                padding: UiRect::new(Val::Px(14.0), Val::Px(14.0), Val::Px(10.0), Val::Px(0.0)),
                border: UiRect::all(Val::Px(1.0)),
                ..default()
            },
            // under the lines and the steps
            ZIndex(-1),
            BackgroundColor(if b.epoch.is_multiple_of(2) {
                theme::SURFACE.with_alpha(0.45)
            } else {
                theme::SURFACE.with_alpha(0.25)
            }),
            BorderColor::all(if b.current { theme::GOLD.with_alpha(0.35) } else { theme::LINE.with_alpha(0.6) }),
            Pickable::IGNORE,
        ))
        .with_children(|h| {
            h.spawn((
                Node { align_items: AlignItems::Baseline, column_gap: Val::Px(8.0), ..default() },
                Pickable::IGNORE,
            ))
            .with_children(|row| {
                row.spawn((
                    theme::label(
                        fonts,
                        era_tag(b.epoch, n_epochs),
                        10.0,
                        Weight::Bold,
                        if b.current { theme::GOLD } else { theme::TEXT_3 },
                    ),
                    Pickable::IGNORE,
                ));
                row.spawn((
                    theme::label(fonts, db.epoch_name(b.epoch as u8), theme::MD, Weight::Semibold, theme::TEXT),
                    Pickable::IGNORE,
                ));
                row.spawn((
                    theme::label(fonts, format!("{}/{}", b.done, b.total), theme::XS, Weight::Regular, theme::TEXT_3),
                    Pickable::IGNORE,
                ));
            });
            h.spawn((theme::label(fonts, era, theme::XS, Weight::Regular, theme::TEXT_3), Pickable::IGNORE));
            let frac = if b.total == 0 { 0.0 } else { b.done as f32 / b.total as f32 };
            h.spawn((
                Node {
                    border_radius: BorderRadius::all(Val::Px(99.0)),
                    width: Val::Percent(100.0),
                    height: Val::Px(3.0),
                    margin: UiRect::top(Val::Px(3.0)),
                    ..default()
                },
                BackgroundColor(theme::LINE.with_alpha(0.7)),
                Pickable::IGNORE,
            ))
            .with_children(|bar| {
                bar.spawn((
                    Node {
                        border_radius: BorderRadius::all(Val::Px(99.0)),
                        width: Val::Percent(frac * 100.0),
                        height: Val::Percent(100.0),
                        ..default()
                    },
                    BackgroundColor(theme::GREEN),
                    Pickable::IGNORE,
                ));
            });
        })
        .id()
}

/// One overview line: its three segments inside a box that covers them.
fn spawn_edge(commands: &mut Commands, edge: &Edge) -> Entity {
    let r = edge_bounds(&edge.segments);
    commands
        .spawn((
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(r.min.x),
                top: Val::Px(r.min.y),
                width: Val::Px(r.width()),
                height: Val::Px(r.height()),
                ..default()
            },
            Pickable::IGNORE,
        ))
        .with_children(|e| {
            for (left, top, w, h) in edge.segments {
                e.spawn((
                    Node {
                        position_type: PositionType::Absolute,
                        left: Val::Px(left - r.min.x),
                        top: Val::Px(top - r.min.y),
                        width: Val::Px(w),
                        height: Val::Px(h),
                        ..default()
                    },
                    BackgroundColor(edge.color),
                    Pickable::IGNORE,
                ));
            }
        })
        .id()
}

/// One step on the graph: its vessel, name, state and the "+N" badge for needs drawn
/// without a line.
fn spawn_node(
    commands: &mut Commands,
    fonts: &UiFonts,
    assets: &AssetServer,
    n: &NodeInfo,
    r: &Reaction,
    selected: bool,
) -> Entity {
    let (bg, border) = node_look(n.state, selected, false);
    let accent = theme::process_color(&r.process);
    let mut node = commands.spawn((
        Button,
        TechNodeButton(n.id, n.state),
        // over every line, including a selection's
        ZIndex(2),
        Node {
            border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
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
                TextFont { font: fonts.semibold.clone().into(), font_size: FontSize::Px(12.0), ..default() },
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
        // a goal wears its flag, with its priority
        if let Some(rank) = n.goal {
            b.spawn((
                TechGoalFlag,
                Node {
                    position_type: PositionType::Absolute,
                    right: Val::Px(-8.0),
                    top: Val::Px(-9.0),
                    align_items: AlignItems::Center,
                    column_gap: Val::Px(2.0),
                    padding: UiRect::axes(Val::Px(5.0), Val::Px(1.0)),
                    border_radius: BorderRadius::all(Val::Px(9.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    ..default()
                },
                BackgroundColor(theme::mix(theme::BG, theme::GOLD, 0.3)),
                BorderColor::all(theme::GOLD),
                Pickable::IGNORE,
            ))
            .with_children(|f| {
                f.spawn(theme::icon(assets, "flag", 11.0, theme::GOLD));
                f.spawn((
                    theme::label(fonts, (rank + 1).to_string(), 10.0, Weight::Bold, theme::TEXT),
                    Pickable::IGNORE,
                ));
            });
        }
        // needs with no line here: select the step to see them all
        if n.undrawn > 0 {
            b.spawn((
                TechNeedBadge { step: n.id, count: n.undrawn },
                Node {
                    border_radius: BorderRadius::all(Val::Px(10.0)),
                    position_type: PositionType::Absolute,
                    left: Val::Px(-11.0),
                    top: Val::Px(NODE_H / 2.0 - 10.0),
                    min_width: Val::Px(20.0),
                    height: Val::Px(20.0),
                    padding: UiRect::horizontal(Val::Px(4.0)),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    border: UiRect::all(Val::Px(1.0)),
                    ..default()
                },
                BackgroundColor(theme::mix(theme::BG, theme::CYAN, 0.25)),
                BorderColor::all(theme::CYAN),
                Pickable::IGNORE,
            ))
            .with_children(|t| {
                t.spawn((
                    theme::label(fonts, format!("+{}", n.undrawn), 10.0, Weight::Bold, theme::TEXT),
                    Pickable::IGNORE,
                ));
            });
        }
    });
    node.id()
}

/// A group heading in the list ("READY TO MAKE  12").
#[derive(Component)]
pub struct TechListHeading;

/// Builds the list rows in sight (and a screen either side) and drops the rest; a closed
/// tree, or the graph showing, builds none.
#[allow(clippy::too_many_arguments, clippy::type_complexity)]
pub fn tech_list_window_system(
    mut commands: Commands,
    state: Res<TechTreeState>,
    layout: Res<TechLayout>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    recipe_db: Option<Res<RecipeDatabase>>,
    focus: Option<Res<crate::ui::focus::KeyFocus>>,
    mut content_q: Query<(Entity, &mut VirtualList, &mut Node, &ComputedNode), With<TechListContent>>,
    view_q: Query<(&TechScrollable, &ComputedNode, &ScrollPosition)>,
    mut cells: Query<&mut Node, (Or<(With<TechListEntry>, With<TechListHeading>)>, Without<TechListContent>)>,
    pressed: Query<(), (With<TechListEntry>, Or<(With<Pressed>, With<Clicked>)>)>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    reveal: Res<TreeReveal>,
) {
    let Ok((content, mut list, mut node, cn)) = content_q.single_mut() else {
        return;
    };
    let Some((_, view, scroll)) = view_q.iter().find(|(m, _, _)| !m.graph) else {
        return;
    };
    let focused = focus.and_then(|f| f.entity);
    let keep = |e: Entity| Some(e) == focused || pressed.contains(e);
    let (width, view_h) = if state.open && state.mode == TechMode::List {
        (cn.size.x * cn.inverse_scale_factor(), view.size.y * view.inverse_scale_factor())
    } else {
        (0.0, 0.0)
    };
    let Some(pass) = list.plan(width, view_h, scroll.0.y, keep) else {
        return;
    };
    if width > 0.0 && node.height != Val::Px(pass.height) {
        node.height = Val::Px(pass.height);
    }
    for e in &pass.drop {
        commands.entity(*e).try_despawn();
    }
    for (e, at) in &pass.moves {
        if let Ok(mut n) = cells.get_mut(*e) {
            n.top = Val::Px(at.y);
        }
    }
    let (Some(db), Some(subs)) = (recipe_db.as_ref(), substances_assets.get(&game_data.substances)) else {
        return;
    };
    for (id, at, _) in &pass.build {
        let e = if *id >= HEADING_BASE {
            let g = ((*id - HEADING_BASE) as usize).min(layout.groups.len() - 1);
            spawn_list_heading(&mut commands, &fonts, &assets, layout.groups[g], layout.group_len[g], at.y)
        } else {
            let Some(&i) = layout.index.get(id) else { continue };
            let n = &layout.nodes[i];
            let Some(r) = db.authored.get(i).filter(|r| r.id == n.id) else { continue };
            let look = (state.selected == Some(n.id), reveal.0);
            spawn_list_row(&mut commands, &fonts, &assets, db, subs, n, r, look, at.y)
        };
        list.record(*id, e, *at);
    }
    if !pass.build.is_empty() || !pass.drop.is_empty() {
        commands.entity(content).replace_children(&list.order());
    }
}

/// A list group's heading, `top` pixels down the list.
fn spawn_list_heading(
    commands: &mut Commands,
    fonts: &UiFonts,
    assets: &AssetServer,
    (title, want): (&str, NodeState),
    count: usize,
    top: f32,
) -> Entity {
    commands
        .spawn((
            TechListHeading,
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(4.0),
                right: Val::Px(0.0),
                top: Val::Px(top),
                height: Val::Px(LIST_ROW_H),
                align_items: AlignItems::FlexEnd,
                column_gap: Val::Px(8.0),
                padding: UiRect::bottom(Val::Px(6.0)),
                ..default()
            },
            Pickable::IGNORE,
        ))
        .with_children(|h| {
            h.spawn(theme::icon(assets, state_icon(want), 14.0, state_accent(want)));
            h.spawn(theme::label(fonts, title.to_uppercase(), theme::XS, Weight::Bold, theme::TEXT_2));
            h.spawn(theme::label(fonts, count.to_string(), theme::XS, Weight::Regular, theme::TEXT_3));
        })
        .id()
}

/// One step in a list cell, `top` pixels down the list: vessel, name and era, then what it
/// takes (ready steps) or its equation (one line each, so every row is the same height).
#[allow(clippy::too_many_arguments)]
fn spawn_list_row(
    commands: &mut Commands,
    fonts: &UiFonts,
    assets: &AssetServer,
    db: &RecipeDatabase,
    subs: &Substances,
    n: &NodeInfo,
    r: &Reaction,
    (selected, revealed): (bool, bool),
    top: f32,
) -> Entity {
    let accent = theme::process_color(&r.process);
    let sub = match n.state {
        NodeState::Available => hint_string(r, subs),
        NodeState::Completed => equation_string(r, subs),
        NodeState::Locked if revealed => equation_string(r, subs),
        // a recipe not yet made stays the player's to work out
        NodeState::Locked => format!("Needs the {}", vessel_name(&r.process)),
        NodeState::Open => format!("In the {}", vessel_name(&r.process)),
    };
    let mut row = commands.spawn((
        theme::button(
            Kind::Row,
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(top),
                height: Val::Px(LIST_ROW_H),
                align_items: AlignItems::Center,
                column_gap: Val::Px(12.0),
                padding: UiRect::axes(Val::Px(10.0), Val::Px(6.0)),
                ..default()
            },
            theme::R_MD,
        ),
        TechListEntry(n.id),
    ));
    if selected {
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
                min_width: Val::Px(0.0),
                overflow: Overflow::clip(),
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
                    TextLayout::no_wrap(),
                    Pickable::IGNORE,
                ));
                t.spawn((
                    theme::label(fonts, db.epoch_name(n.epoch as u8), theme::XS, Weight::Regular, theme::TEXT_3),
                    TextLayout::no_wrap(),
                    Pickable::IGNORE,
                ));
            });
            c.spawn((
                Text::new(sub),
                TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(11.5), ..default() },
                TextColor(if n.state == NodeState::Available {
                    theme::mix(theme::GOLD, theme::TEXT, 0.4)
                } else {
                    theme::TEXT_2
                }),
                TextLayout::no_wrap(),
                Pickable::IGNORE,
            ));
        });
        row.spawn(theme::icon(assets, state_icon(n.state), 14.0, state_accent(n.state)));
    });
    row.id()
}

// ---------------------------------------------------------------------------------------
// Selection + hover look + detail bar
// ---------------------------------------------------------------------------------------
/// Scrolls the graph to a step asked for (a need's chip was tapped), centring it.
pub fn tech_reveal_system(
    mut links: ResMut<TechLinks>,
    mut scroll_q: Query<(&TechScrollable, &mut ScrollPosition, &ComputedNode)>,
    zoom: Res<TechZoom>,
) {
    let Some(id) = links.reveal else { return };
    links.reveal = None;
    let Some(&(e, c, r)) = links.at.get(&id) else { return };
    let centre = Vec2::new(col_x(c, e) + NODE_W / 2.0, node_y(r) + NODE_H / 2.0) * zoom.0;
    for (m, mut sp, cn) in &mut scroll_q {
        if m.graph {
            let view = cn.size * cn.inverse_scale_factor();
            sp.0 = (centre - view / 2.0).max(Vec2::ZERO);
        }
    }
}

/// The selected step's links, over the overview's: brighter and thicker, under the steps.
/// Redrawn when the selection changes or the graph is rebuilt.
pub fn tech_selection_links_system(
    mut commands: Commands,
    state: Res<TechTreeState>,
    links: Res<TechLinks>,
    old: Query<Entity, With<SelectionLink>>,
) {
    if !state.is_changed() && !links.is_changed() {
        return;
    }
    for e in &old {
        commands.entity(e).try_despawn();
    }
    let (Some(sel), Some(graph)) = (state.selected, links.graph) else { return };
    let Ok(mut g) = commands.get_entity(graph) else { return };
    g.with_children(|g| {
        for &(a, b) in links.all.iter().filter(|(a, b)| *a == sel || *b == sel) {
            let (Some(&pa), Some(&pb)) = (links.at.get(&a), links.at.get(&b)) else { continue };
            for (left, top, w, h) in elbow(pa, pb, 3.0) {
                g.spawn((
                    SelectionLink,
                    Node {
                        position_type: PositionType::Absolute,
                        left: Val::Px(left),
                        top: Val::Px(top),
                        width: Val::Px(w),
                        height: Val::Px(h),
                        ..default()
                    },
                    BackgroundColor(theme::CYAN),
                    ZIndex(1),
                    Pickable::IGNORE,
                ));
            }
        }
    });
}

pub fn tech_node_click_system(
    nodes: Query<&TechNodeButton, (With<Clicked>, With<Button>)>,
    entries: Query<&TechListEntry, (With<Clicked>, With<Button>)>,
    needs: Query<&TechNeedButton, (With<Clicked>, With<Button>)>,
    restyled: Query<(), (Changed<Hovered>, With<TechNodeButton>)>,
    mut links: ResMut<TechLinks>,
    mut state: ResMut<TechTreeState>,
    mut looks: Query<(&TechNodeButton, &Hovered, Has<Pressed>, &mut BackgroundColor, &mut BorderColor)>,
    mut rows: Query<(&TechListEntry, &mut Skin)>,
) {
    let mut sel = state.selected;
    for n in &nodes {
        sel = Some(n.0);
    }
    for e in &entries {
        sel = Some(e.0);
    }
    // a need's chip: select the step that makes it, and bring it into view
    for n in &needs {
        if let Some(p) = n.0 {
            sel = Some(p);
            links.reveal = Some(p);
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
    if changed || !restyled.is_empty() {
        for (n, h, pressed, mut bg, mut border) in &mut looks {
            let (b, c) = node_look(n.1, Some(n.0) == sel, Look::of(h, pressed) == Look::Hover);
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
    mut built_for: Local<Option<(Option<u32>, bool, bool)>>,
    links: Res<TechLinks>,
    reveal: Res<TreeReveal>,
) {
    let Ok(bar) = bar_q.single() else {
        return;
    };
    let (Some(db), Some(subs)) = (recipe_db.as_ref(), substances_assets.get(&game_data.substances)) else {
        return;
    };
    let key = (state.selected, state.open, reveal.0);
    if *built_for == Some(key) && !progress.is_changed() && !unlocks.is_changed() && !links.is_changed() {
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
                        if reveal.0 {
                            "Gold steps are ready now. Drag the map or use the wheel (Shift for sideways) to look around; pinch or Ctrl and the wheel to zoom."
                        } else {
                            "Aim for a step and Hint leads the way. Drag the map or use the wheel (Shift for sideways) to look around; pinch or Ctrl and the wheel to zoom."
                        },
                        theme::SM,
                        Weight::Regular,
                        theme::TEXT_3,
                    ));
                },
            );
        });
        return;
    };

    let st = node_state(r, &progress, &unlocks, reveal.0);
    // a recipe shows once made, or with "Show what's ready"
    let recipe = st == NodeState::Completed || reveal.0;
    let accent = theme::process_color(&r.process);
    let e = r.epoch;
    let needs = links.needs.get(&r.id).cloned().unwrap_or_default();
    let process_locked = !unlocks.0.contains(&r.process);
    let known = r.reactants.iter().chain(r.products.iter()).all(|s| progress.discovered.contains(&s.substance_id));

    commands.entity(bar).with_children(|p| {
        p.spawn((
            Node {
                border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                width: Val::Px(92.0),
                height: Val::Px(92.0),
                flex_shrink: 0.0,
                padding: UiRect::all(Val::Px(10.0)),
                border: UiRect::all(Val::Px(1.0)),
                ..default()
            },
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
        // what doesn't fit the bar (a step with many needs, held upright) scrolls in it
        p.spawn(Node {
            flex_direction: FlexDirection::Column,
            row_gap: Val::Px(5.0),
            flex_grow: 1.0,
            flex_shrink: 1.0,
            max_height: Val::Percent(100.0),
            overflow: Overflow::scroll_y(),
            ..default()
        })
        .with_children(|c| {
            c.spawn(Node {
                align_items: AlignItems::Center,
                column_gap: Val::Px(8.0),
                row_gap: Val::Px(4.0),
                flex_wrap: FlexWrap::Wrap,
                ..default()
            })
            .with_children(|t| {
                theme::spawn_chip(t, fonts, state_label(st), state_accent(st));
                t.spawn(theme::label(
                    fonts,
                    format!("{}  ·  {}", db.epoch_name(e).to_uppercase(), vessel_name(&r.process)),
                    theme::XS,
                    Weight::Bold,
                    theme::TEXT_3,
                ));
                // aiming: a step not made yet can be a goal (in this row, so the needs below
                // keep the bar's width)
                if let (false, Some(g)) = (st == NodeState::Completed, goal_of(r, &progress)) {
                    match progress.goals.iter().position(|x| *x == g) {
                        Some(rank) => {
                            let words = format!("Goal {} of {}", rank + 1, progress.goals.len());
                            theme::spawn_chip(t, fonts, &words, theme::GOLD);
                            if rank > 0 {
                                theme::spawn_button(
                                    t,
                                    fonts,
                                    assets,
                                    Kind::Ghost,
                                    None,
                                    "Make it first",
                                    TechAimFirst(g),
                                );
                            }
                            theme::spawn_button(t, fonts, assets, Kind::Ghost, None, "Stop aiming", TechStopAim(g));
                        }
                        None => {
                            let aim = TechAim(g);
                            theme::spawn_button(
                                t,
                                fonts,
                                assets,
                                Kind::Accent(theme::GOLD),
                                Some("flag"),
                                "Aim here",
                                aim,
                            );
                        }
                    }
                }
            });
            c.spawn(theme::label(fonts, r.name.clone(), theme::LG, Weight::Bold, theme::TEXT));
            if recipe {
                c.spawn((
                    Text::new(equation_string(r, subs)),
                    TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(14.0), ..default() },
                    TextColor(theme::mix(accent, theme::TEXT, 0.55)),
                ));
            } else {
                c.spawn(theme::para(
                    fonts,
                    "Its recipe shows once you've made it. Aim for it and Hint leads the way.",
                    theme::SM,
                    theme::TEXT_2,
                    Val::Px(900.0),
                ));
            }
            let warm = Color::srgb(1.0, 0.72, 0.55);
            if process_locked && st == NodeState::Locked {
                c.spawn(theme::para(
                    fonts,
                    format!("Unlock the {} first.", vessel_name(&r.process)),
                    theme::SM,
                    warm,
                    Val::Px(900.0),
                ));
            }
            if !recipe {
                // what it takes stays the player's to work out
            } else if needs.is_empty() {
                // everything it takes is on the shelf from the start
                let color = if st == NodeState::Available { theme::GOLD } else { theme::TEXT_2 };
                c.spawn(theme::para(fonts, hint_string(r, subs), theme::SM, color, Val::Px(900.0)));
            } else {
                // every need, with the step it comes from: green once on the shelf
                c.spawn(Node {
                    flex_wrap: FlexWrap::Wrap,
                    align_items: AlignItems::Center,
                    column_gap: Val::Px(6.0),
                    row_gap: Val::Px(4.0),
                    ..default()
                })
                .with_children(|row| {
                    row.spawn(theme::label(fonts, "NEEDS", theme::XS, Weight::Bold, theme::TEXT_3));
                    for n in &needs {
                        let name = subs
                            .0
                            .get(&n.substance)
                            .map(|x| x.name.clone())
                            .unwrap_or_else(|| format!("#{}", n.substance));
                        let from = match n.from {
                            Some(p) => {
                                db.authored.iter().find(|x| x.id == p).map(|x| x.name.clone()).unwrap_or_default()
                            }
                            None if n.granted => "a milestone".to_string(),
                            None => "no step yet".to_string(),
                        };
                        let what = if n.catalyst {
                            format!("{name} (catalyst)")
                        } else if db.transient.contains(&n.substance) {
                            // it doesn't keep: a link brings it in from the step that makes it
                            format!("{name} (linked in)")
                        } else {
                            name
                        };
                        let have = progress.discovered.contains(&n.substance);
                        let accent = if have { theme::GREEN } else { warm };
                        row.spawn((
                            Button,
                            TechNeedButton(n.from),
                            Node {
                                border_radius: BorderRadius::all(Val::Px(10.0)),
                                padding: UiRect::axes(Val::Px(8.0), Val::Px(3.0)),
                                border: UiRect::all(Val::Px(1.0)),
                                ..default()
                            },
                            BackgroundColor(theme::mix(theme::BG, accent, 0.14)),
                            BorderColor::all(accent.with_alpha(0.7)),
                        ))
                        .with_children(|t| {
                            t.spawn((
                                theme::label(
                                    fonts,
                                    format!("{what}  ·  from {from}"),
                                    theme::XS,
                                    Weight::Regular,
                                    theme::TEXT,
                                ),
                                Pickable::IGNORE,
                            ));
                        });
                    }
                });
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
/// Held upright the toolbar takes two rows: the title and its counts above (the close
/// button stays in the corner), the legend and Graph / List below.
#[allow(clippy::type_complexity)]
pub fn tech_toolbar_fit_system(
    portrait: Res<crate::ui::shell::Portrait>,
    mut nodes: Query<
        (&mut Node, Has<TechToolbar>, Has<TechToolbarTitle>, Has<TechToolbarTools>),
        Or<(With<TechToolbar>, With<TechToolbarTitle>, With<TechToolbarTools>, With<TechCloseButton>)>,
    >,
) {
    let up = portrait.0;
    for (mut n, bar, title, tools) in &mut nodes {
        let mut want = n.clone();
        if bar {
            want.height = if up { Val::Auto } else { Val::Px(TOOLBAR_H) };
            want.flex_wrap = if up { FlexWrap::Wrap } else { FlexWrap::NoWrap };
            want.row_gap = Val::Px(8.0);
            want.padding = if up {
                UiRect::new(Val::Px(16.0), Val::Px(16.0), Val::Px(10.0), Val::Px(10.0))
            } else {
                UiRect::horizontal(Val::Px(18.0))
            };
        } else if title {
            // room on its right for the close button
            want.width = if up { Val::Percent(100.0) } else { Val::Auto };
            want.padding = UiRect::right(Val::Px(if up { 40.0 } else { 0.0 }));
        } else if tools {
            want.width = if up { Val::Percent(100.0) } else { Val::Auto };
            want.justify_content = if up { JustifyContent::SpaceBetween } else { JustifyContent::Default };
        } else {
            // the close button: in the top corner upright, at the end of the row otherwise
            want.position_type = if up { PositionType::Absolute } else { PositionType::Relative };
            want.right = if up { Val::Px(10.0) } else { Val::Auto };
            want.top = if up { Val::Px(6.0) } else { Val::Auto };
        }
        if *n != want {
            *n = want;
        }
    }
}

/// The graph's zoom bar (shown with the graph), Ctrl and the wheel over the tree, and a
/// two-finger pinch: apart zooms in, together zooms out, a step at a time.
#[allow(clippy::too_many_arguments)]
pub fn tech_zoom_controls_system(
    state: Res<TechTreeState>,
    mut zoom: ResMut<TechZoom>,
    clicks: (Query<(), (With<Clicked>, With<TechZoomOut>)>, Query<(), (With<Clicked>, With<TechZoomIn>)>),
    mut wheel: MessageReader<bevy::input::mouse::MouseWheel>,
    keys: Res<ButtonInput<KeyCode>>,
    touches: Res<Touches>,
    mut pinch: Local<Option<f32>>,
    mut bar: Query<&mut Node, With<TechZoomBar>>,
    mut label: Query<&mut Text, With<TechZoomLabel>>,
) {
    let on = state.open && state.mode == TechMode::Graph;
    for mut n in &mut bar {
        let d = if on { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    let mut to = zoom.0;
    if on {
        let (outs, ins) = clicks;
        if !outs.is_empty() {
            to = zoom.stepped(true);
        }
        if !ins.is_empty() {
            to = zoom.stepped(false);
        }
        let ctrl = keys.pressed(KeyCode::ControlLeft) || keys.pressed(KeyCode::ControlRight);
        let turned: f32 = wheel.read().map(|e| e.y + e.x).sum();
        if ctrl && turned != 0.0 {
            to = TechZoom(to).stepped(turned < 0.0);
        }
        let fingers: Vec<Vec2> = touches.iter().map(|t| t.position()).collect();
        if let [a, b] = fingers[..] {
            let d = a.distance(b);
            match *pinch {
                None => *pinch = Some(d),
                Some(start) if d > start * 1.3 => {
                    to = TechZoom(to).stepped(false);
                    *pinch = Some(d);
                }
                Some(start) if d < start / 1.3 => {
                    to = TechZoom(to).stepped(true);
                    *pinch = Some(d);
                }
                _ => {}
            }
        } else {
            *pinch = None;
        }
    } else {
        wheel.clear();
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

/// Scales the graph's canvas to the zoom about its top-left corner (bevy_ui scales a node
/// about its middle, so it is moved back by what that shifts), sizes the scroll range to the
/// graph as drawn, and keeps the middle of the view on the same spot of the graph.
#[allow(clippy::type_complexity)]
pub fn tech_zoom_apply_system(
    zoom: Res<TechZoom>,
    mut last: Local<Option<f32>>,
    mut content: Query<(Ref<Node>, &mut UiTransform), (With<TechGraphContent>, Without<TechGraphSizer>)>,
    mut sizer: Query<&mut Node, (With<TechGraphSizer>, Without<TechGraphContent>)>,
    mut scroll_q: Query<(&TechScrollable, &mut ScrollPosition, &ComputedNode)>,
) {
    let Ok((node, mut tf)) = content.single_mut() else { return };
    let z = zoom.0;
    let old = last.unwrap_or(1.0);
    if *last == Some(z) && !node.is_changed() {
        return;
    }
    *last = Some(z);
    let px = |v: Val| if let Val::Px(p) = v { p } else { 0.0 };
    let size = Vec2::new(px(node.width), px(node.height));
    tf.scale = Vec2::splat(z);
    tf.translation = Val2::px(-(1.0 - z) * size.x / 2.0, -(1.0 - z) * size.y / 2.0);
    if let Ok(mut n) = sizer.single_mut() {
        n.width = Val::Px(size.x * z);
        n.height = Val::Px(size.y * z);
    }
    if (old - z).abs() > 0.001 {
        for (m, mut sp, cn) in &mut scroll_q {
            if m.graph {
                let view = cn.size * cn.inverse_scale_factor();
                let spot = (sp.0 + view / 2.0) / old.max(0.01);
                sp.0 = (spot * z - view / 2.0).max(Vec2::ZERO);
            }
        }
    }
}

/// Drag the graph background to pan (a press that starts on a node selects it instead).
pub fn tech_pan_system(
    mouse: Res<ButtonInput<MouseButton>>,
    state: Res<TechTreeState>,
    windows: Query<&Window>,
    ui_scale: Res<UiScale>,
    nodes: Query<(&Hovered, Has<Pressed>), With<TechNodeButton>>,
    mut scroll_q: Query<(&TechScrollable, &mut ScrollPosition)>,
    graph: Query<(&ComputedNode, &UiGlobalTransform), With<TechGraphView>>,
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
    // where the graph starts, under the toolbar however many rows it takes
    let top = graph
        .iter()
        .next()
        .map(|(cn, gt)| (gt.translation.y - cn.size.y / 2.0) / win.scale_factor())
        .unwrap_or((theme::HEADER_H + TOOLBAR_H) * s);
    let bottom = win.height() - DETAIL_H * s;
    if mouse.just_pressed(MouseButton::Left) {
        let on_node = nodes.iter().any(|(h, pressed)| h.get() || pressed);
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
