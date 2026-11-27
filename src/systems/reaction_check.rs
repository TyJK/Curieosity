// src/systems/reaction_check.rs
use bevy::platform::collections::{HashMap, HashSet};
use bevy::prelude::*;

use crate::components::ui_markers::{
    CanvasScrollingPane, InCatalystZone, InputPort, OutputPort, PendingReaction, PortFilter, ProcessVessel,
    ReactionLink, ReactionOutput, VesselCard, VesselCatalystZone,
};
use crate::components::{format_formula, Draggable, DropTarget, InVessel, Ingredient, VesselIngredientZone};
use crate::data::common::{ProcessType, StoichPoint};
use crate::data::reactions::Reaction;
use crate::data::substances::Substances;
use crate::resources::{
    recipe_database::{Lookup, RecipeDatabase},
    ui_fonts::UiFonts,
};
use crate::systems::autoplay::GameEvent;
use crate::ui::inventory::{spawn_vessel_chip, ChipRole};
use crate::ui::onboarding::Tip;
use crate::ui::process_toolbar::{vessel_art_path, vessel_name, PlaceVessel};
use crate::ui::settings::Settings;
use crate::ui::theme;
use crate::ui::toasts::{ToastKind, Toasts};
use crate::GameData;

#[derive(Message)]
pub struct CheckVesselReaction(pub Entity);

#[derive(Component)]
pub struct EquationText;

/// The thin bar under a vessel's title that fills while a reaction runs.
#[derive(Component)]
pub struct ReactionProgressBar;

/// A short red flash on a vessel whose contents didn't react.
#[derive(Component)]
pub struct Fizzle(pub Timer);

/// The contents layer of a vessel's art: tinted with the colour of what is inside.
#[derive(Component)]
pub struct VesselArtFill;

/// The accent layer of a vessel's art (flame, frost, rays...): glows while reacting.
#[derive(Component)]
pub struct VesselArtAccent;

/// The vessel's big picture, under its title (hidden on a short bench).
#[derive(Component)]
pub struct VesselArtBig;

/// The small picture beside the title, shown instead of the big one on a short bench.
#[derive(Component)]
pub struct VesselArtSmall;

/// The vessel's name in its header (larger in the overview form).
#[derive(Component)]
pub struct VesselTitleText;

/// A vessel's status line while it is ready for something to go in.
pub const READY_TEXT: &str = "Put substances in, then React.";

const ART_SIZE: f32 = 104.0;
const ART_SMALL: f32 = 30.0;

/// Below this bench height (interface pixels: a phone held sideways) vessel cards are built
/// compact, so a whole card fits on the bench.
pub const COMPACT_BENCH: f32 = 420.0;

pub const VESSEL_W: f32 = 216.0;
/// A full-size card's height, near enough, for laying cards out in rows.
const VESSEL_ROW_H: f32 = 370.0;

/// Where the `count`th new vessel goes, in the pane's units: across the top of what the
/// bench shows (`shown` is its top-left, `view` its size, both in pane units), as many as
/// fit side by side, and on a bench tall enough for two rows (a phone held upright) on to a
/// second row. Once the slots are used up the next round sits a little lower.
pub fn vessel_slot(count: usize, shown: Vec2, view: Vec2, margin: f32) -> Vec2 {
    let step = VESSEL_W + 28.0;
    let cols = (((view.x - 24.0) / step).floor() as usize).clamp(1, 4);
    let rows = if view.y - margin >= 2.0 * VESSEL_ROW_H { 2 } else { 1 };
    let (col, down) = if rows == 2 {
        let per = cols * 2;
        let slot = count % per;
        (slot % cols, (slot / cols) as f32 * VESSEL_ROW_H + (count / per) as f32 * 16.0)
    } else {
        // one row: a second round staggers below the first, then each round a little lower
        let slot = count % (cols * 2);
        (slot % cols, (slot / cols) as f32 * 30.0 + (count / (cols * 2)) as f32 * 16.0)
    };
    shown + Vec2::new(24.0 + col as f32 * step, margin + down)
}
const VESSEL_BG: Color = Color::srgb(0.035, 0.047, 0.110);

/// One colour per family of vessels (Heat, Cool, Pressure and so on). Every vessel of a
/// family wears it, so the colour alone says what kind of vessel it is; the tier numeral
/// tells a family's vessels apart. The twelve are picked to stay distinct from each other.
pub fn family_color(family: &str) -> Color {
    match family {
        "Mix" => Color::srgb(0.35, 0.85, 0.80),
        "Heat" => Color::srgb(1.00, 0.42, 0.20),
        "Cool" => Color::srgb(0.50, 0.82, 1.00),
        "Distillation" => Color::srgb(0.75, 0.55, 1.00),
        "Electrolysis" => Color::srgb(1.00, 0.88, 0.30),
        "Catalysis" => Color::srgb(0.45, 0.95, 0.45),
        "Pressure" => Color::srgb(0.70, 0.70, 0.74),
        "Polymer" => Color::srgb(1.00, 0.50, 0.80),
        "Separation" => Color::srgb(1.00, 0.70, 0.38),
        "Biology" => Color::srgb(0.75, 0.90, 0.38),
        "Radiation" => Color::srgb(0.95, 0.45, 1.00),
        "Fabrication" => Color::srgb(0.88, 0.92, 1.00),
        _ => Color::srgb(0.70, 0.70, 0.70),
    }
}

/// Accent colour per process: vessel border, progress bar, and the reaction glow. It is
/// the vessel's family colour (the battery a reaction may ask for counts as electrolysis).
pub fn process_color(p: &ProcessType) -> Color {
    match p {
        ProcessType::ApplyCurrent => family_color("Electrolysis"),
        other => family_color(other.family()),
    }
}

/// Colour of a vessel's accent layer: the flame is orange, the frost blue, the gauge
/// needle red, and so on. Details may differ within a family (the arc furnace's arc burns
/// blue-white) while the vessel itself wears the family colour.
pub fn accent_glow(p: &ProcessType) -> Color {
    match p {
        ProcessType::Heat => Color::srgb(1.0, 0.62, 0.18),
        ProcessType::Smelting => Color::srgb(1.0, 0.55, 0.15),
        ProcessType::Cool => Color::srgb(0.55, 0.80, 1.0),
        ProcessType::Irradiate => Color::srgb(1.0, 0.92, 0.45),
        ProcessType::Pressurize => Color::srgb(1.0, 0.35, 0.30),
        ProcessType::Electrolysis => Color::srgb(1.0, 0.95, 0.55),
        ProcessType::BlastFurnace => Color::srgb(1.0, 0.50, 0.12),
        ProcessType::ArcFurnace => Color::srgb(0.70, 0.85, 1.0),
        ProcessType::AirLiquefier => Color::srgb(0.70, 0.95, 1.0),
        ProcessType::Cryostat => Color::srgb(0.80, 0.97, 1.0),
        ProcessType::NuclearReactor => Color::srgb(0.35, 0.80, 1.0),
        ProcessType::Cyclotron => Color::srgb(1.0, 0.55, 1.0),
        ProcessType::HighPressure | ProcessType::DiamondPress => Color::srgb(1.0, 0.35, 0.30),
        ProcessType::Fermenter | ProcessType::Bioreactor => Color::srgb(0.75, 1.0, 0.55),
        ProcessType::CvdChamber => Color::srgb(1.0, 0.60, 1.0),
        other => {
            let c = process_color(other).to_srgba();
            Color::srgb(0.5 + c.red * 0.5, 0.5 + c.green * 0.5, 0.5 + c.blue * 0.5)
        }
    }
}

fn hex_color(h: &str) -> Option<Color> {
    let h = h.trim_start_matches('#');
    if h.len() != 6 {
        return None;
    }
    let v = u32::from_str_radix(h, 16).ok()?;
    Some(Color::srgb_u8((v >> 16) as u8, (v >> 8) as u8, v as u8))
}

/// What a substance looks like in a vessel: its authored colour, or a default for its state.
fn content_color(ing: &Ingredient, subs: Option<&Substances>) -> Color {
    if let Some(c) = subs.and_then(|s| s.0.get(&ing.id)).and_then(|s| s.color_hex.as_deref()).and_then(hex_color) {
        return c;
    }
    use crate::data::common::MatterState as M;
    match ing.state {
        M::Gas => Color::srgb(0.80, 0.86, 0.95),
        M::Liquid | M::Aqueous => Color::srgb(0.45, 0.70, 0.95),
        M::Plasma => Color::srgb(0.95, 0.60, 1.0),
        M::SupercriticalFluid => Color::srgb(0.70, 0.80, 1.0),
        M::Solid => Color::srgb(0.82, 0.80, 0.76),
    }
}

/// Tints each vessel's contents with the average colour of what is in it (empty vessels
/// show nothing), and makes the accent layer glow and flicker while a reaction runs.
pub fn vessel_art_system(
    time: Res<Time>,
    game_data: Option<Res<GameData>>,
    substances_assets: Res<Assets<Substances>>,
    chips: Query<(&InVessel, &Ingredient)>,
    vessels: Query<(&ProcessVessel, Has<PendingReaction>), With<VesselCard>>,
    parents: Query<&ChildOf>,
    cards: Query<(), With<VesselCard>>,
    mut fills: Query<(Entity, &mut ImageNode), (With<VesselArtFill>, Without<VesselArtAccent>)>,
    mut accents: Query<(Entity, &mut ImageNode), (With<VesselArtAccent>, Without<VesselArtFill>)>,
) {
    let subs = game_data.as_ref().and_then(|g| substances_assets.get(&g.substances));
    let mut sums: bevy::platform::collections::HashMap<Entity, (Vec3, f32)> = default();
    for (iv, ing) in &chips {
        let c = content_color(ing, subs).to_srgba();
        let e = sums.entry(iv.0).or_insert((Vec3::ZERO, 0.0));
        e.0 += Vec3::new(c.red, c.green, c.blue);
        e.1 += 1.0;
    }
    for (e, mut img) in &mut fills {
        let Some(v) = vessel_of(e, &parents, &cards) else { continue };
        let target = match sums.get(&v) {
            Some((sum, n)) if *n > 0.0 => {
                let c = *sum / *n;
                Color::srgba(c.x, c.y, c.z, 0.9)
            }
            _ => Color::NONE,
        };
        if img.color != target {
            img.color = target;
        }
    }
    let t = time.elapsed_secs();
    for (e, mut img) in &mut accents {
        let Some(v) = vessel_of(e, &parents, &cards) else { continue };
        let Ok((pv, reacting)) = vessels.get(v) else { continue };
        let alpha = if reacting { 0.65 + 0.35 * (t * 9.0).sin().abs() * (0.6 + 0.4 * (t * 23.0).sin()) } else { 0.3 };
        // (only when it changes: an idle vessel's glow stays put, and the screen can rest)
        let want = accent_glow(&pv.process).with_alpha(alpha);
        if img.color != want {
            img.color = want;
        }
    }
}

/// A port's dot: big enough to say what it is inside it.
pub const PORT_DOT: f32 = 30.0;
/// A port's touch area (the port node itself), around its dot.
pub const PORT_HIT: f32 = 44.0;

/// A port's touch area: wider than its dot, overhanging the row by the difference.
fn port_hit_area() -> Node {
    let (dot, hit) = (PORT_DOT, PORT_HIT);
    Node {
        width: Val::Px(hit),
        height: Val::Px(hit),
        margin: UiRect::all(Val::Px(-(hit - dot) / 2.0)),
        align_items: AlignItems::Center,
        justify_content: JustifyContent::Center,
        ..default()
    }
}

/// The dot a port shows, with what it is ("IN", "OUT") inside it.
fn spawn_port_dot(port: &mut ChildSpawnerCommands, fonts: &UiFonts, fill: Color, edge: Color, text: &str, ink: Color) {
    port.spawn((
        Node {
            border_radius: BorderRadius::all(Val::Px(PORT_DOT / 2.0)),
            width: Val::Px(PORT_DOT),
            height: Val::Px(PORT_DOT),
            border: UiRect::all(Val::Px(2.0)),
            flex_shrink: 0.0,
            align_items: AlignItems::Center,
            justify_content: JustifyContent::Center,
            ..default()
        },
        BackgroundColor(fill),
        BorderColor::all(edge),
        Pickable::IGNORE,
    ))
    .with_child((theme::label(fonts, text, 8.5, theme::Weight::Bold, ink), Pickable::IGNORE));
}

fn dim(c: Color, f: f32) -> Color {
    let s = c.to_srgba();
    Color::srgb(s.red * f, s.green * f, s.blue * f)
}

/// A vessel picked in the vessel picker goes on the bench, in the next free slot of the
/// visible area, and becomes the selected one.
#[allow(clippy::too_many_arguments)]
pub fn place_vessel_system(
    mut asks: MessageReader<PlaceVessel>,
    vessels_q: Query<(), (With<VesselCard>, Without<crate::components::ui_markers::Stashed>)>,
    unlocks: Res<crate::ui::process_toolbar::ProcessUnlocks>,
    mut commands: Commands,
    scrolling_panes: Query<(Entity, &Node), With<CanvasScrollingPane>>,
    fonts: Option<Res<UiFonts>>,
    asset_server: Res<AssetServer>,
    mut active: ResMut<crate::systems::drag_drop::ActiveVessel>,
    dock: Res<crate::ui::inventory::Dock>,
    zoom: Res<crate::systems::drag_drop::BenchZoom>,
    bench: Query<&ComputedNode, With<crate::components::ui_markers::ReactionCanvasRoot>>,
) {
    let Ok((pane, pane_node)) = scrolling_panes.single() else { return };
    // a compact card starts higher, so the whole of it fits a short bench
    let margin = if dock.bench < COMPACT_BENCH { 10.0 } else { 24.0 };
    let Some(fonts) = fonts.as_ref() else { return };
    let mut count = vessels_q.iter().count();
    for ask in asks.read() {
        if !unlocks.0.contains(&ask.0) {
            continue;
        }
        // what the bench shows, in the pane's own units (it may be zoomed)
        let z = zoom.0.max(0.01);
        let shown = -crate::systems::drag_drop::pane_offset(pane_node) / z;
        let view = crate::systems::drag_drop::bench_view(&bench) / z;
        let at = vessel_slot(count, shown, view, margin);
        let card = spawn_vessel_card(&mut commands, pane, &ask.0, vessel_name(&ask.0), at, fonts, &asset_server);
        active.0 = Some(card); // what goes in next goes into the vessel just placed
        count += 1;
    }
}

/// Spawn one vessel card on the bench pane at `pos`; returns the card entity. Used by the
/// sidebar and by the scripted review playthrough.
pub fn spawn_vessel_card(
    commands: &mut Commands,
    pane: Entity,
    process: &ProcessType,
    name: &str,
    pos: Vec2,
    fonts: &UiFonts,
    asset_server: &AssetServer,
) -> Entity {
    let accent = process_color(process);
    let mut card = Entity::PLACEHOLDER;
    commands.entity(pane).with_children(|parent| {
        card = parent
            .spawn((
                VesselCard,
                Draggable,
                DropTarget,
                ProcessVessel { process: process.clone() },
                Node { border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    position_type: PositionType::Absolute,
                    left: Val::Px(pos.x),
                    top: Val::Px(pos.y),
                    width: Val::Px(VESSEL_W),
                    border: UiRect::all(Val::Px(1.5)),
                    flex_direction: FlexDirection::Column,
                    align_items: AlignItems::Center,
                    padding: UiRect::all(Val::Px(10.0)),
                    row_gap: Val::Px(7.0),
                    ..default()
                },
                BackgroundGradient::from(LinearGradient::to_bottom(vec![
                    ColorStop::auto(theme::mix(theme::SURFACE, accent, 0.10)),
                    ColorStop::auto(VESSEL_BG),
                ])),
                BorderColor::all(dim(accent, 0.8)),
                theme::shadow(24.0, 8.0, 0.55),
                Name::new(format!("Vessel_{:?}", process)),
            ))
            .with_children(|vessel| {
                // --- header: the title (and, on a short bench, the small picture) ---
                vessel
                    .spawn((
                        Node { width: Val::Percent(100.0), align_items: AlignItems::Center, column_gap: Val::Px(7.0), ..default() },
                        Pickable::IGNORE,
                    ))
                    .with_children(|t| {
                        // the small picture (a short bench shows this instead of the big one)
                        t.spawn((
                            VesselArtSmall,
                            Node { width: Val::Px(ART_SMALL), height: Val::Px(ART_SMALL), display: Display::None, ..default() },
                            Pickable::IGNORE,
                        ))
                        .with_children(|art| spawn_art_layers(art, process, asset_server));
                        t.spawn((
                            VesselTitleText,
                            theme::label(fonts, name, theme::LG, theme::Weight::Semibold, accent),
                            TextLayout::no_wrap(),
                            Pickable::IGNORE,
                        ));
                    });

                // --- the vessel itself: outline, contents and accent layers ---
                vessel
                    .spawn((
                        VesselArtBig,
                        Node { width: Val::Px(ART_SIZE), height: Val::Px(ART_SIZE), ..default() },
                        Pickable::IGNORE,
                        Name::new("VesselArt"),
                    ))
                    .with_children(|art| spawn_art_layers(art, process, asset_server));

                // --- progress bar (fills while the reaction runs) ---
                vessel
                    .spawn((
                        Node { border_radius: BorderRadius::all(Val::Px(99.0)), width: Val::Percent(100.0), height: Val::Px(4.0), ..default() },
                        BackgroundColor(theme::RAISED),
                    ))
                    .with_children(|bar| {
                        bar.spawn((
                            ReactionProgressBar,
                            Node { border_radius: BorderRadius::all(Val::Px(99.0)), width: Val::Percent(0.0), height: Val::Percent(100.0), ..default() },
                            BackgroundColor(accent),
                        ));
                    });

                // --- ports: input left, output right ---
                vessel
                    .spawn((
                        Node {
                            width: Val::Percent(100.0),
                            justify_content: JustifyContent::SpaceBetween,
                            align_items: AlignItems::Center,
                            ..default()
                        },
                        Name::new("PortWrapper"),
                    ))
                    .with_children(|row| {
                        // each port is a dot in a touch area that overhangs the row, so a
                        // finger finds it without the card growing
                        row.spawn((
                            InputPort, DropTarget, Pickable::default(), port_hit_area(),
                            Tip::Text("Input port", "Products of the vessel linked here flow in and react. Link by dragging from another vessel's output port onto this vessel, or tap that port and then this vessel."),
                            Name::new("InputPort"),
                        ))
                        .with_children(|p| spawn_port_dot(p, fonts, theme::BG, theme::CYAN, "IN", theme::CYAN));
                        row.spawn((
                            OutputPort { filter: PortFilter::Any }, Draggable, Pickable::default(), port_hit_area(),
                            Tip::Text("Output port", "Drag from here onto another vessel to chain them, or tap here and then tap the vessel to feed. Double-tap a link to cut it."),
                            Name::new("OutputPort"),
                        ))
                        .with_children(|p| spawn_port_dot(p, fonts, theme::GOLD.with_alpha(0.3), theme::GOLD, "OUT", theme::TEXT));
                    });

                // --- ingredient zone ---
                vessel.spawn((
                    VesselIngredientZone,
                    DropTarget,
                    Pickable::default(),
                    Tip::Text(
                        "Contents",
                        "Put substances here, then press React. Double-tap a substance to take it out, or drag it onto another vessel to move it.",
                    ),
                    Node { border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                        width: Val::Percent(100.0),
                        min_height: Val::Px(84.0),
                        max_height: Val::Px(240.0),
                        flex_direction: FlexDirection::Column,
                        align_items: AlignItems::Stretch,
                        row_gap: Val::Px(4.0),
                        padding: UiRect::all(Val::Px(5.0)),
                        border: UiRect::all(Val::Px(1.0)),
                        overflow: Overflow::clip_y(),
                        ..default()
                    },
                    BackgroundColor(Color::srgba(0.0, 0.0, 0.03, 0.55)),
                    BorderColor::all(theme::LINE),
                    Name::new("IngredientZone"),
                ));

                // --- catalyst zone (Catalyst Bed only) ---
                if process.has_catalyst_slot() {
                    vessel
                        .spawn((
                            VesselCatalystZone,
                            DropTarget,
                            Pickable::default(),
                            Tip::Text("Catalyst slot", "A catalyst speeds a reaction without being used up. It stays here between reactions."),
                            Node { border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                                width: Val::Percent(100.0),
                                min_height: Val::Px(42.0),
                                flex_direction: FlexDirection::Column,
                                align_items: AlignItems::Stretch,
                                padding: UiRect::all(Val::Px(5.0)),
                                border: UiRect::all(Val::Px(1.0)),
                                ..default()
                            },
                            BackgroundColor(theme::GREEN.with_alpha(0.06)),
                            BorderColor::all(theme::GREEN.with_alpha(0.55)),
                            Name::new("CatalystZone"),
                        ))
                        .with_children(|zone| {
                            zone.spawn((
                                theme::label(fonts, "CATALYST SLOT", theme::XS, theme::Weight::Bold, theme::GREEN.with_alpha(0.85)),
                                Pickable::IGNORE,
                            ));
                        });
                }

                // --- equation / status ---
                vessel.spawn((
                    EquationText,
                    Text::new(READY_TEXT),
                    TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(12.0), ..default() },
                    TextColor(theme::TEXT_3),
                    Node { max_width: Val::Px(VESSEL_W - 24.0), ..default() },
                    Pickable::IGNORE,
                ));

            })
            .id();
    });
    card
}

/// A vessel picture's three layers: the contents (tinted with what is inside), the outline,
/// and the accent that glows while it reacts.
fn spawn_art_layers(art: &mut ChildSpawnerCommands, process: &ProcessType, asset_server: &AssetServer) {
    let layer = |path: String, color: Color| {
        (
            ImageNode::new(asset_server.load(path)).with_color(color),
            Node {
                position_type: PositionType::Absolute,
                width: Val::Percent(100.0),
                height: Val::Percent(100.0),
                ..default()
            },
            Pickable::IGNORE,
        )
    };
    art.spawn((VesselArtFill, layer(vessel_art_path(process, "fill"), Color::NONE)));
    art.spawn(layer(vessel_art_path(process, "outline"), process_color(process)));
    art.spawn((VesselArtAccent, layer(vessel_art_path(process, "accent"), accent_glow(process).with_alpha(0.3))));
}

/// On a short bench (a phone held sideways), or zoomed out, vessel cards go compact: the
/// small picture beside the title instead of the big one, a shorter contents area, less
/// padding. Zoomed out to the overview (drag_drop::OVERVIEW and below) they fold down to
/// what they hold: the name and the formulas of the contents, in larger type so they stay
/// readable small, and the ports (the links stay put); the art, the equation and each
/// substance's name step aside. Applied to new cards and new contents, and to everything
/// when the bench changes size or zoom.
#[allow(clippy::type_complexity)]
pub fn vessel_fit_system(
    dock: Res<crate::ui::inventory::Dock>,
    zoom: Res<crate::systems::drag_drop::BenchZoom>,
    new_cards: Query<(), Added<VesselCard>>,
    new_chips: Query<(), Or<(Added<InVessel>, Added<InCatalystZone>)>>,
    mut nodes: Query<
        (
            &mut Node,
            Has<VesselCard>,
            Has<VesselArtBig>,
            Has<VesselArtSmall>,
            Has<VesselIngredientZone>,
            Has<EquationText>,
            Has<crate::ui::inventory::ChipIcon>,
            Has<crate::ui::inventory::ChipNameText>,
        ),
        Or<(
            With<VesselCard>,
            With<VesselArtBig>,
            With<VesselArtSmall>,
            With<VesselIngredientZone>,
            With<EquationText>,
            With<crate::ui::inventory::ChipIcon>,
            With<crate::ui::inventory::ChipNameText>,
        )>,
    >,
    mut fonts: Query<
        (&mut TextFont, Has<VesselTitleText>),
        Or<(With<VesselTitleText>, With<crate::ui::inventory::ChipFormulaText>)>,
    >,
) {
    if !(dock.is_changed() || zoom.is_changed() || !new_cards.is_empty() || !new_chips.is_empty()) {
        return;
    }
    let overview = zoom.overview();
    let compact = dock.bench < COMPACT_BENCH || zoom.0 < 0.99;
    let (pad, gap, zone_h) = if compact { (8.0, 4.0, 44.0) } else { (10.0, 7.0, 84.0) };
    let shown = |on: bool| if on { Display::Flex } else { Display::None };
    for (mut n, card, big, small, zone, equation, chip_icon, chip_name) in &mut nodes {
        let display = if card {
            if n.row_gap != Val::Px(gap) {
                n.row_gap = Val::Px(gap);
                n.padding = UiRect::all(Val::Px(pad));
            }
            None
        } else if big {
            Some(shown(!compact))
        } else if small {
            Some(shown(compact))
        } else if zone {
            let h = if overview { 0.0 } else { zone_h };
            if n.min_height != Val::Px(h) {
                n.min_height = Val::Px(h);
            }
            None
        } else if equation || chip_icon || chip_name {
            Some(shown(!overview))
        } else {
            None
        };
        if let Some(d) = display {
            if n.display != d {
                n.display = d;
            }
        }
    }
    for (mut f, title) in &mut fonts {
        let size = match (title, overview) {
            (true, true) => 26.0,
            (true, false) => theme::LG,
            (false, true) => 22.0,
            (false, false) => 13.0,
        };
        if f.font_size != FontSize::Px(size) {
            f.font_size = FontSize::Px(size);
        }
    }
}

/// Walk up from a node inside a vessel card to the card.
fn vessel_of(mut e: Entity, parents: &Query<&ChildOf>, cards: &Query<(), With<VesselCard>>) -> Option<Entity> {
    for _ in 0..6 {
        if cards.contains(e) {
            return Some(e);
        }
        e = parents.get(e).ok()?.0;
    }
    None
}

/// Set a vessel's status line (the EquationText under its contents).
pub(crate) fn set_status(
    eq_q: &mut Query<(&mut Text, &mut TextColor, &ChildOf), With<EquationText>>,
    vessel: Entity,
    text: &str,
    color: Color,
) {
    for (mut t, mut c, parent) in eq_q.iter_mut() {
        if parent.0 == vessel {
            t.0 = text.to_string();
            c.0 = color;
        }
    }
}

/// System 1: Checks for valid reactions and starts the timer. A combination that doesn't
/// react gets a red flash and, where we can tell, a hint at what's wrong.
pub fn reaction_check_system(
    mut ev_check: MessageReader<CheckVesselReaction>,
    recipe_db: Option<Res<RecipeDatabase>>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    mut commands: Commands,
    vessel_ingredients: Query<(Entity, &Ingredient, &InVessel)>,
    catalyst_q: Query<(&Ingredient, &InCatalystZone)>,
    vessels: Query<&ProcessVessel, With<VesselCard>>,
    pending: Query<(), With<PendingReaction>>,
    mut eq_q: Query<(&mut Text, &mut TextColor, &ChildOf), With<EquationText>>,
    mut toasts: ResMut<Toasts>,
    settings: Option<Res<Settings>>,
    mut events: MessageWriter<GameEvent>,
    unlocks: Res<crate::ui::process_toolbar::ProcessUnlocks>,
    hand_back: (Res<UiFonts>, Res<AssetServer>, Query<(Entity, &ChildOf), With<VesselIngredientZone>>),
) {
    let speed = settings.as_ref().map(|s| s.reaction_speed).unwrap_or(1.0).max(0.05);
    let balanced = settings.as_ref().is_some_and(|s| s.balanced_amounts);
    // hints off: a mix that doesn't react says only that
    let hints = settings.as_ref().is_none_or(|s| s.hints);
    let (fonts, assets, zones) = hand_back;
    let Some(recipe_db) = recipe_db else {
        ev_check.clear();
        return;
    };
    let Some(substances_db) = substances_assets.get(&game_data.substances) else {
        return;
    };

    // If the same vessel is triggered twice in one frame (e.g. from 2 incoming links),
    // we only process it once.
    let mut processed_vessels = HashSet::new();

    for ev in ev_check.read() {
        let vessel_entity = ev.0;
        if !processed_vessels.insert(vessel_entity) || pending.contains(vessel_entity) {
            continue;
        }
        let Ok(process_vessel) = vessels.get(vessel_entity) else { continue };

        let reactant_ids: Vec<u32> = vessel_ingredients
            .iter()
            .filter(|(_, _, in_vessel)| in_vessel.0 == vessel_entity)
            .map(|(_, ing, _)| ing.id)
            .collect();
        if reactant_ids.is_empty() {
            set_status(&mut eq_q, vessel_entity, "The vessel is empty.", theme::TEXT_3);
            continue;
        }
        let catalyst_id: Option<u32> =
            catalyst_q.iter().find(|(_, in_zone)| in_zone.0 == vessel_entity).map(|(ing, _)| ing.id);

        let process = &process_vessel.process;

        let name_of = |id: u32| substances_db.0.get(&id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{}", id));

        let found = recipe_db.lookup(process, reactant_ids.clone());
        let Lookup::Runs(reaction) = found else {
            // --- fizzle: say why if we can (and hints are on) ---
            let hint = if !hints {
                None
            } else {
                match &found {
                    Lookup::NeedsTier(p) => Some(format!(
                        "Too much for the {}: this needs the {} ({} {}){}.",
                        vessel_name(process),
                        vessel_name(p),
                        p.family(),
                        crate::ui::process_toolbar::roman(p.tier()),
                        if unlocks.0.contains(p) { "" } else { ", which you haven't unlocked yet" },
                    )),
                    Lookup::OtherVessel(p) => {
                        let other = vessel_name(p);
                        Some(format!(
                            "These don't react in the {}, but try {} {other}.",
                            vessel_name(process),
                            crate::data::common::article(other)
                        ))
                    }
                    // what the chemistry, or the recipes, can tell
                    _ => crate::systems::lessons::why_not(&recipe_db, process, &reactant_ids, substances_db),
                }
            };
            let status = hint.clone().unwrap_or_else(|| "No reaction.".to_string());
            set_status(&mut eq_q, vessel_entity, &status, theme::RED);
            events.write(GameEvent::Fizzle {
                process: process.clone(),
                reactants: reactant_ids.clone(),
                reason: status.clone(),
            });
            if let Some(h) = hint {
                toasts.push(ToastKind::Hint, h);
            }
            commands.entity(vessel_entity).insert(Fizzle(Timer::from_seconds(0.6, TimerMode::Once)));
            continue;
        };

        if let Some(needed) = reaction.required_catalyst() {
            if catalyst_id != Some(needed) {
                let msg = if hints {
                    format!("Almost: this needs {} in the catalyst slot.", name_of(needed))
                } else {
                    "No reaction.".to_string()
                };
                set_status(&mut eq_q, vessel_entity, &msg, if hints { theme::GOLD } else { theme::RED });
                events.write(GameEvent::Fizzle {
                    process: process.clone(),
                    reactants: reactant_ids.clone(),
                    reason: msg.clone(),
                });
                if hints {
                    toasts.push(ToastKind::Hint, msg);
                }
                commands.entity(vessel_entity).insert(Fizzle(Timer::from_seconds(0.6, TimerMode::Once)));
                continue;
            }
        }

        // With balanced amounts on, the amounts are weighed against the equation: short of
        // one equation's worth doesn't react; n times over makes n times the products; any
        // other ratio is a dud, making half and handing the excess back.
        let mut times = 1;
        let mut leftover: Vec<(u32, u32)> = Vec::new();
        let mut note: Option<String> = None;
        if balanced {
            let mut placed: HashMap<u32, u32> = HashMap::new();
            for (_, ing, iv) in vessel_ingredients.iter() {
                if iv.0 == vessel_entity {
                    *placed.entry(ing.id).or_default() += ing.amount.max(1);
                }
            }
            let (n, exact, short) = weigh(reaction, &placed);
            if n == 0 {
                let (id, m) = short.unwrap_or((reactant_ids[0], 1));
                let others: Vec<String> = reaction
                    .reactants
                    .iter()
                    .filter(|x| x.substance_id != id)
                    .map(|x| format!("{} {}", x.moles.max(1), name_of(x.substance_id)))
                    .collect();
                let msg = if others.is_empty() {
                    format!("Not enough {}: the equation takes {m} of it.", name_of(id))
                } else {
                    format!("Not enough {}: the equation takes {m} for every {}.", name_of(id), others.join(" and "))
                };
                set_status(&mut eq_q, vessel_entity, &msg, theme::GOLD);
                events.write(GameEvent::Fizzle {
                    process: process.clone(),
                    reactants: reactant_ids.clone(),
                    reason: msg.clone(),
                });
                toasts.push(ToastKind::Hint, msg);
                commands.entity(vessel_entity).insert(Fizzle(Timer::from_seconds(0.6, TimerMode::Once)));
                continue;
            }
            times = n;
            if !exact {
                leftover = reaction
                    .reactants
                    .iter()
                    .map(|x| (x.substance_id, placed.get(&x.substance_id).copied().unwrap_or(0) - n * x.moles.max(1)))
                    .filter(|(_, left)| *left > 0)
                    .collect();
                let left: Vec<String> = leftover.iter().map(|(id, k)| format!("{k} {}", name_of(*id))).collect();
                note = Some(format!(
                    "Unbalanced: half the yield, and {} left over. Match the equation's amounts for all of it.",
                    left.join(" and ")
                ));
            }
        }

        // Consume ingredients (a transient may be breaking down this same frame: try).
        for (entity, _, in_vessel) in vessel_ingredients.iter() {
            if in_vessel.0 == vessel_entity {
                commands.entity(entity).try_despawn();
            }
        }
        // ...and hand back what an unbalanced batch didn't use
        if let Some((zone, _)) = zones.iter().find(|(_, parent)| parent.parent() == vessel_entity) {
            for (id, k) in &leftover {
                let Some(sub) = substances_db.0.get(id) else { continue };
                let ing = Ingredient {
                    id: *id,
                    name: sub.name.clone(),
                    formula: sub.formula.clone(),
                    state: sub.state,
                    properties: sub.properties.clone(),
                    amount: *k,
                };
                commands.entity(zone).with_children(|z| {
                    spawn_vessel_chip(z, &ing, ChipRole::Ingredient(vessel_entity), &fonts, &assets);
                });
            }
        }

        let equation = format!("{}\n{}", reaction.name, build_equation_string(reaction, substances_db));
        match &note {
            Some(n) => {
                set_status(&mut eq_q, vessel_entity, &format!("{equation}\n{n}"), theme::GOLD);
                toasts.push(ToastKind::Hint, n.clone());
            }
            None if balanced => {
                let times_note = if times > 1 { format!(", {times} times over") } else { String::new() };
                set_status(
                    &mut eq_q,
                    vessel_entity,
                    &format!("{equation}\nBalanced{times_note}: the full yield."),
                    theme::TEXT,
                );
            }
            None => set_status(&mut eq_q, vessel_entity, &equation, theme::TEXT),
        }
        events.write(GameEvent::Reacted { reaction_id: reaction.id, vessel: vessel_entity });

        // Prepare products (n batches; half, rounded up, for a dud).
        let mut products = Vec::new();
        for sp in &reaction.products {
            if let Some(sub) = substances_db.0.get(&sp.substance_id) {
                let full = sp.moles.max(1) * times;
                products.push(Ingredient {
                    id: sub.id,
                    name: sub.name.clone(),
                    formula: sub.formula.clone(),
                    state: sub.state,
                    properties: sub.properties.clone(),
                    amount: if note.is_some() { full.div_ceil(2) } else { full },
                });
            }
        }
        products.sort_by_key(|p| std::cmp::Reverse(p.amount));

        // Products appear after a short "reacting" beat (the progress bar fills).
        commands
            .entity(vessel_entity)
            .insert(PendingReaction { timer: Timer::from_seconds(1.0 / speed, TimerMode::Once), products });
    }
}

/// Ticks running reactions: fills the progress bar, pulses the vessel border in its
/// process colour, and releases the products when done.
pub fn handle_reaction_timers_system(
    mut commands: Commands,
    time: Res<Time>,
    mut query: Query<(Entity, &mut PendingReaction, &ProcessVessel, &mut BorderColor, &Children)>,
    children_q: Query<&Children>,
    mut bars: Query<&mut Node, With<ReactionProgressBar>>,
) {
    for (entity, mut pending, pv, mut border, children) in &mut query {
        pending.timer.tick(time.delta());
        let frac = pending.timer.fraction();
        let accent = process_color(&pv.process);
        let pulse = 0.65 + 0.35 * (frac * std::f32::consts::TAU * 2.0).sin().abs();
        *border = BorderColor::all(dim(accent, pulse.min(1.0) + 0.0));

        // The bar is a grandchild (vessel -> bar track -> bar).
        for c in children.iter() {
            if let Ok(grand) = children_q.get(c) {
                for g in grand.iter() {
                    if let Ok(mut n) = bars.get_mut(g) {
                        n.width = Val::Percent(if pending.timer.is_finished() { 0.0 } else { frac * 100.0 });
                    }
                }
            }
        }

        if pending.timer.is_finished() {
            *border = BorderColor::all(dim(accent, 0.8));
            commands.entity(entity).remove::<PendingReaction>().insert(ReactionOutput(pending.products.clone()));
        }
    }
}

/// How long a transient lasts in a vessel before it breaks down (and at least DECAY_FRAMES
/// frames, so a slow frame can't take it before the reaction waiting for it has looked).
pub const DECAY_SECS: f32 = 1.6;
const DECAY_FRAMES: u32 = 6;

/// On a transient's chip (Property::IsTransient): unless a reaction takes it within
/// DECAY_SECS it breaks down, its edge going from green to red first.
#[derive(Component)]
pub struct Decay {
    timer: Timer,
    frames: u32,
}

impl Default for Decay {
    fn default() -> Self {
        Self { timer: Timer::from_seconds(DECAY_SECS, TimerMode::Once), frames: 0 }
    }
}

/// Breaks down transients that nothing used, and says how to use one.
pub fn decay_system(
    mut commands: Commands,
    time: Res<Time>,
    mut chips: Query<(Entity, &mut Decay, &Ingredient, &InVessel, &mut BorderColor)>,
    mut eq_q: Query<(&mut Text, &mut TextColor, &ChildOf), With<EquationText>>,
    mut toasts: ResMut<Toasts>,
) {
    for (e, mut d, ing, in_vessel, mut border) in &mut chips {
        d.timer.tick(time.delta());
        d.frames += 1;
        border.left = theme::mix(theme::GREEN, theme::RED, d.timer.fraction());
        if d.timer.is_finished() && d.frames >= DECAY_FRAMES {
            commands.entity(e).try_despawn();
            let msg = format!(
                "{} doesn't keep: it broke down. Link this vessel into the one that uses it, and it flows straight there.",
                ing.name
            );
            set_status(&mut eq_q, in_vessel.0, &msg, theme::GOLD);
            toasts.push(ToastKind::Hint, msg);
        }
    }
}

/// With balanced amounts on, a substance put into a vessel that already holds it adds to
/// that chip's count ("2 HCl") instead of sitting beside it.
pub fn merge_chips_system(
    mut commands: Commands,
    settings: Option<Res<Settings>>,
    mut chips: Query<(Entity, Ref<InVessel>, &mut Ingredient, Option<&Children>)>,
    children_q: Query<&Children>,
    mut texts: Query<&mut Text, With<crate::ui::inventory::ChipFormulaText>>,
) {
    if !settings.as_ref().is_some_and(|s| s.balanced_amounts) || !chips.iter().any(|c| c.1.is_added()) {
        return;
    }
    // the new chips, and for each (vessel, substance) the chip that was there first
    let mut new: Vec<(Entity, Entity, u32, u32)> = Vec::new();
    let mut keep: Vec<(Entity, u32, Entity)> = Vec::new();
    let mut seen: Vec<_> = chips.iter().map(|(e, v, i, _)| (e, v.0, i.id, i.amount, v.is_added())).collect();
    seen.sort_by_key(|c| (c.4, c.0.index().index()));
    for (e, vessel, id, amount, added) in seen {
        if let Some(k) = keep.iter().find(|k| k.0 == vessel && k.1 == id) {
            if added {
                new.push((e, k.2, id, amount));
            }
        } else {
            keep.push((vessel, id, e));
        }
    }
    for (e, into, _, amount) in new {
        commands.entity(e).try_despawn();
        let Ok((_, _, mut ing, kids)) = chips.get_mut(into) else { continue };
        ing.amount += amount;
        let label = format!("{} {}", ing.amount, crate::components::format_formula(&ing.formula));
        let mut todo: Vec<Entity> = kids.map(|k| k.iter().collect()).unwrap_or_default();
        while let Some(c) = todo.pop() {
            if let Ok(mut t) = texts.get_mut(c) {
                t.0 = label.clone();
            }
            if let Ok(k) = children_q.get(c) {
                todo.extend(k.iter());
            }
        }
    }
}

/// With balanced amounts on: how many times over the equation the vessel holds (n), and
/// whether the amounts match it exactly. n = 0 means a reactant is short of one equation's
/// worth (which one, and how many it takes).
pub fn weigh(reaction: &Reaction, placed: &HashMap<u32, u32>) -> (u32, bool, Option<(u32, u32)>) {
    let need: Vec<(u32, u32)> = reaction.reactants.iter().map(|s| (s.substance_id, s.moles.max(1))).collect();
    let have = |id: u32| placed.get(&id).copied().unwrap_or(0);
    let n = need.iter().map(|(id, m)| have(*id) / m).min().unwrap_or(0);
    let short = need.iter().find(|(id, m)| have(*id) < *m).copied();
    let exact = n > 0 && need.iter().all(|(id, m)| have(*id) == n * m);
    (n, exact, short)
}

/// Fades a fizzle's red flash back to the vessel's normal border.
pub fn fizzle_system(
    mut commands: Commands,
    time: Res<Time>,
    mut q: Query<(Entity, &mut Fizzle, &ProcessVessel, &mut BorderColor)>,
) {
    for (e, mut f, pv, mut border) in &mut q {
        f.0.tick(time.delta());
        let normal = dim(process_color(&pv.process), 0.8).to_srgba();
        let t = f.0.fraction();
        let red = Srgba::new(1.0, 0.25, 0.2, 1.0);
        let mix = |a: f32, b: f32| a + (b - a) * t;
        *border = BorderColor::all(Color::srgb(
            mix(red.red, normal.red),
            mix(red.green, normal.green),
            mix(red.blue, normal.blue),
        ));
        if f.0.is_finished() {
            commands.entity(e).remove::<Fizzle>();
        }
    }
}

pub fn propagate_products_system(
    mut commands: Commands,
    product_q: Query<(Entity, &ReactionOutput, &Children), With<VesselCard>>,
    all_vessels: Query<&Children, With<VesselCard>>,
    link_q: Query<&ReactionLink>,
    port_q: Query<&OutputPort>,
    ingredient_zones: Query<Entity, With<VesselIngredientZone>>,
    fonts: Res<UiFonts>,
    asset_server: Res<AssetServer>,
    mut ev_check: MessageWriter<CheckVesselReaction>,
) {
    for (from_vessel, reaction_output, from_vessel_children) in &product_q {
        let mut available_products = reaction_output.0.clone();
        let outgoing_links: Vec<&ReactionLink> = link_q.iter().filter(|link| link.from_vessel == from_vessel).collect();
        for link in outgoing_links {
            let to_vessel = link.to_vessel;
            let Ok(port) = port_q.get(link.from_port) else { continue };
            // a transient goes first: it is what the link is there for
            let product_index = available_products
                .iter()
                .position(|product| product.is_transient() && matches_filter(product, &port.filter))
                .or_else(|| available_products.iter().position(|product| matches_filter(product, &port.filter)));
            if let Some(index) = product_index {
                let product_to_move = available_products.remove(index);
                if let Ok(children) = all_vessels.get(to_vessel) {
                    spawn_products_in_vessel(
                        &mut commands,
                        to_vessel,
                        children,
                        &[product_to_move],
                        &ingredient_zones,
                        &fonts,
                        &asset_server,
                    );
                }
                ev_check.write(CheckVesselReaction(to_vessel));
            }
        }
        if !available_products.is_empty() {
            spawn_products_in_vessel(
                &mut commands,
                from_vessel,
                from_vessel_children,
                &available_products,
                &ingredient_zones,
                &fonts,
                &asset_server,
            );
        }
        commands.entity(from_vessel).remove::<ReactionOutput>();
    }
}

fn matches_filter(product: &Ingredient, filter: &PortFilter) -> bool {
    match filter {
        PortFilter::Any => true,
        PortFilter::State(state) => product.state == *state,
        PortFilter::StoichiometricOrder(_) => true,
    }
}

fn spawn_products_in_vessel(
    commands: &mut Commands,
    vessel_entity: Entity,
    vessel_children: &Children,
    products: &[Ingredient],
    ingredient_zones: &Query<Entity, With<VesselIngredientZone>>,
    fonts: &UiFonts,
    asset_server: &AssetServer,
) {
    let Some(ingredient_zone) = vessel_children.iter().find(|child| ingredient_zones.contains(*child)) else {
        return;
    };
    commands.entity(ingredient_zone).with_children(|zone| {
        for (i, product) in products.iter().enumerate() {
            let chip = spawn_vessel_chip(zone, product, ChipRole::Product(vessel_entity), fonts, asset_server);
            // products pop into the vessel one after another
            zone.commands().entity(chip).insert(crate::ui::inventory::PopIn::new(i as f32 * 0.09));
        }
    });
}

fn format_side(points: &[StoichPoint], substances: &Substances) -> String {
    let mut terms = Vec::new();
    for sp in points {
        if let Some(sub) = substances.0.get(&sp.substance_id) {
            let label = format_formula(&sub.formula);
            if sp.moles <= 1 {
                terms.push(label);
            } else {
                terms.push(format!("{} {}", sp.moles, label));
            }
        } else {
            terms.push(format!("?{}", sp.substance_id));
        }
    }
    terms.join(" + ")
}

fn build_equation_string(reaction: &Reaction, substances: &Substances) -> String {
    let lhs = format_side(&reaction.reactants, substances);
    let rhs = format_side(&reaction.products, substances);
    format!("{} → {}", lhs, rhs)
}

#[cfg(test)]
mod tests {
    #[test]
    fn each_family_has_its_own_colour_and_every_vessel_wears_it() {
        use super::{family_color, process_color};
        use crate::data::common::VESSEL_SPECS;
        let grey = family_color("Other");
        let mut families: Vec<&str> = VESSEL_SPECS.iter().map(|s| s.category).collect();
        families.sort();
        families.dedup();
        for f in &families {
            assert_ne!(family_color(f), grey, "{f} has no colour of its own");
        }
        for (i, a) in families.iter().enumerate() {
            for b in &families[i + 1..] {
                let (x, y) = (family_color(a).to_srgba(), family_color(b).to_srgba());
                let d = ((x.red - y.red).powi(2) + (x.green - y.green).powi(2) + (x.blue - y.blue).powi(2)).sqrt();
                assert!(d > 0.12, "{a} and {b} look alike");
            }
        }
        for s in VESSEL_SPECS {
            assert_eq!(process_color(&s.process), family_color(s.category), "{} wears another colour", s.name);
        }
    }
}
