// src/systems/reaction_check.rs
use bevy::platform::collections::HashSet;
use bevy::prelude::*;

use crate::components::ui_markers::{
    CanvasScrollingPane, InCatalystZone, InputPort, OutputPort, PendingReaction, PortFilter, ProcessVessel,
    ReactionLink, ReactionOutput, VesselCard, VesselCatalystZone,
};
use crate::components::{
    format_formula, Draggable, DropTarget, InVessel, Ingredient, VesselClearButton, VesselDeleteButton,
    VesselIngredientZone, VesselReactButton,
};
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
use crate::ui::process_toolbar::{vessel_art_path, vessel_name, ProcessButton};
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

const ART_SIZE: f32 = 104.0;

pub const VESSEL_W: f32 = 216.0;
const VESSEL_BG: Color = Color::srgb(0.035, 0.047, 0.110);

/// Accent colour per process: vessel border, progress bar, and the reaction glow.
pub fn process_color(p: &ProcessType) -> Color {
    match p {
        ProcessType::Mix => Color::srgb(0.35, 0.85, 0.80),
        ProcessType::Heat => Color::srgb(1.00, 0.55, 0.20),
        ProcessType::Cool => Color::srgb(0.55, 0.80, 1.00),
        ProcessType::Smelting => Color::srgb(0.95, 0.30, 0.15),
        ProcessType::Distillation => Color::srgb(0.70, 0.55, 1.00),
        ProcessType::Electrolysis => Color::srgb(1.00, 0.90, 0.30),
        ProcessType::Irradiate => Color::srgb(1.00, 0.97, 0.70),
        ProcessType::Catalysis => Color::srgb(0.45, 0.95, 0.45),
        ProcessType::Pressurize => Color::srgb(0.60, 0.70, 0.85),
        ProcessType::Polymerize => Color::srgb(1.00, 0.50, 0.80),
        ProcessType::ApplyCurrent => Color::srgb(1.00, 0.90, 0.30),
        ProcessType::Wait => Color::srgb(0.70, 0.70, 0.70),
        ProcessType::Flask => Color::srgb(0.40, 0.92, 0.95),
        ProcessType::BlastFurnace => Color::srgb(1.00, 0.42, 0.22),
        ProcessType::ArcFurnace => Color::srgb(0.75, 0.70, 1.00),
        ProcessType::AirLiquefier => Color::srgb(0.62, 0.92, 1.00),
        ProcessType::Column => Color::srgb(0.80, 0.62, 1.00),
        ProcessType::ElectrolyticCell => Color::srgb(1.00, 0.80, 0.30),
        ProcessType::NuclearReactor => Color::srgb(0.40, 0.85, 1.00),
        ProcessType::Cyclotron => Color::srgb(0.95, 0.45, 1.00),
        ProcessType::Cracker => Color::srgb(0.65, 0.95, 0.35),
        ProcessType::HighPressure => Color::srgb(0.55, 0.78, 1.00),
        ProcessType::DiamondPress => Color::srgb(0.85, 0.95, 1.00),
        ProcessType::Fermenter => Color::srgb(0.90, 0.75, 0.40),
        ProcessType::Bioreactor => Color::srgb(0.55, 1.00, 0.70),
        ProcessType::CrystalPuller => Color::srgb(0.70, 0.80, 1.00),
        ProcessType::CvdChamber => Color::srgb(1.00, 0.55, 0.95),
    }
}

/// Colour of a vessel's accent layer: the flame is orange, the frost blue, the gauge
/// needle red, and so on.
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
        img.color = accent_glow(&pv.process).with_alpha(alpha);
    }
}

fn dim(c: Color, f: f32) -> Color {
    let s = c.to_srgba();
    Color::srgb(s.red * f, s.green * f, s.blue * f)
}

/// Clicking an unlocked vessel in the sidebar puts a fresh vessel on the bench, in the next
/// free slot of the visible area.
pub fn process_button_system(
    vessels_q: Query<(), With<VesselCard>>,
    interaction_q: Query<(&Interaction, &ProcessButton), (Changed<Interaction>, With<Button>)>,
    unlocks: Res<crate::ui::process_toolbar::ProcessUnlocks>,
    mut commands: Commands,
    scrolling_panes: Query<(Entity, &Node), With<CanvasScrollingPane>>,
    fonts: Option<Res<UiFonts>>,
    asset_server: Res<AssetServer>,
) {
    let Ok((pane, pane_node)) = scrolling_panes.single() else { return };
    let Some(fonts) = fonts.as_ref() else { return };

    for (interaction, button) in &interaction_q {
        if *interaction != Interaction::Pressed || !unlocks.0.contains(&button.process) {
            continue;
        }
        let count = vessels_q.iter().count();
        let pan_x = if let Val::Px(v) = pane_node.left { -v } else { 0.0 };
        let pan_y = if let Val::Px(v) = pane_node.top { -v } else { 0.0 };
        let slot = count % 8;
        let left = pan_x + 24.0 + (slot % 4) as f32 * (VESSEL_W + 28.0);
        let top = pan_y + 24.0 + (slot / 4) as f32 * 30.0 + (count / 8) as f32 * 16.0;
        spawn_vessel_card(
            &mut commands,
            pane,
            &button.process,
            &button.name,
            Vec2::new(left, top),
            fonts,
            &asset_server,
        );
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
                Node {
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
                BorderRadius::all(Val::Px(theme::R_LG)),
                BackgroundGradient::from(LinearGradient::to_bottom(vec![
                    ColorStop::auto(theme::mix(theme::SURFACE, accent, 0.10)),
                    ColorStop::auto(VESSEL_BG),
                ])),
                BorderColor::all(dim(accent, 0.8)),
                theme::shadow(24.0, 8.0, 0.55),
                Name::new(format!("Vessel_{:?}", process)),
            ))
            .with_children(|vessel| {
                // --- header: title + clear / remove ---
                vessel
                    .spawn(Node {
                        width: Val::Percent(100.0),
                        justify_content: JustifyContent::SpaceBetween,
                        align_items: AlignItems::Center,
                        ..default()
                    })
                    .with_children(|hdr| {
                        hdr.spawn((theme::label(fonts, name, theme::LG, theme::Weight::Semibold, accent), Pickable::IGNORE));
                        hdr.spawn(Node { column_gap: Val::Px(2.0), ..default() }).with_children(|btns| {
                            theme::spawn_icon_button(btns, asset_server, "clear", 26.0, theme::TEXT_2, VesselClearButton);
                            theme::spawn_icon_button(btns, asset_server, "close", 26.0, theme::TEXT_2, VesselDeleteButton);
                        });
                    });

                // --- the vessel itself: outline, contents and accent layers ---
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
                vessel
                    .spawn((
                        Node { width: Val::Px(ART_SIZE), height: Val::Px(ART_SIZE), ..default() },
                        Pickable::IGNORE,
                        Name::new("VesselArt"),
                    ))
                    .with_children(|art| {
                        art.spawn((VesselArtFill, layer(vessel_art_path(process, "fill"), Color::NONE)));
                        art.spawn(layer(vessel_art_path(process, "outline"), accent));
                        art.spawn((
                            VesselArtAccent,
                            layer(vessel_art_path(process, "accent"), accent_glow(process).with_alpha(0.3)),
                        ));
                    });

                // --- progress bar (fills while the reaction runs) ---
                vessel
                    .spawn((
                        Node { width: Val::Percent(100.0), height: Val::Px(4.0), ..default() },
                        BorderRadius::all(Val::Px(99.0)),
                        BackgroundColor(theme::RAISED),
                    ))
                    .with_children(|bar| {
                        bar.spawn((
                            ReactionProgressBar,
                            Node { width: Val::Percent(0.0), height: Val::Percent(100.0), ..default() },
                            BorderRadius::all(Val::Px(99.0)),
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
                        row.spawn((
                            InputPort, DropTarget, Pickable::default(), Interaction::default(),
                            Tip::Text("Input port", "Drag a link here from another vessel's output port: its products will flow in and react."),
                            Node { width: Val::Px(18.0), height: Val::Px(18.0), border: UiRect::all(Val::Px(2.0)), ..default() },
                            BorderRadius::all(Val::Px(9.0)),
                            BackgroundColor(theme::BG), BorderColor::all(theme::CYAN),
                            Name::new("InputPort"),
                        ));
                        row.spawn((
                            theme::label(fonts, "in  ·  drag out to chain  ·  out", 9.5, theme::Weight::Regular, theme::TEXT_3),
                            Pickable::IGNORE,
                        ));
                        row.spawn((
                            OutputPort { filter: PortFilter::Any }, Draggable, Pickable::default(),
                            Tip::Text("Output port", "Drag from here to another vessel's input port to chain them."),
                            Node { width: Val::Px(18.0), height: Val::Px(18.0), border: UiRect::all(Val::Px(2.0)), ..default() },
                            BorderRadius::all(Val::Px(9.0)),
                            BackgroundColor(theme::GOLD.with_alpha(0.35)), BorderColor::all(theme::GOLD),
                            Name::new("OutputPort"),
                        ));
                    });

                // --- ingredient zone ---
                vessel.spawn((
                    VesselIngredientZone,
                    DropTarget,
                    Pickable::default(),
                    Interaction::default(),
                    Tip::Text(
                        "Contents",
                        "Drop substances here, then press React. Drag one out to remove it, or onto another vessel to move it.",
                    ),
                    Node {
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
                    BorderRadius::all(Val::Px(theme::R_MD)),
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
                            Interaction::default(),
                            Tip::Text("Catalyst slot", "A catalyst speeds a reaction without being used up. It stays here between reactions."),
                            Node {
                                width: Val::Percent(100.0),
                                min_height: Val::Px(42.0),
                                flex_direction: FlexDirection::Column,
                                align_items: AlignItems::Stretch,
                                padding: UiRect::all(Val::Px(5.0)),
                                border: UiRect::all(Val::Px(1.0)),
                                ..default()
                            },
                            BorderRadius::all(Val::Px(theme::R_MD)),
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
                    Text::new("Drop ingredients in, then React."),
                    TextFont { font: fonts.symbols.clone(), font_size: 12.0, ..default() },
                    TextColor(theme::TEXT_3),
                    Node { max_width: Val::Px(VESSEL_W - 24.0), ..default() },
                    Pickable::IGNORE,
                ));

                // --- react button ---
                vessel
                    .spawn((
                        theme::button(
                            theme::Kind::Accent(accent),
                            Node {
                                width: Val::Percent(100.0),
                                height: Val::Px(34.0),
                                align_items: AlignItems::Center,
                                justify_content: JustifyContent::Center,
                                column_gap: Val::Px(7.0),
                                ..default()
                            },
                            theme::R_MD,
                        ),
                        VesselReactButton,
                        Tip::Text("React", "Run whatever is in the vessel. If nothing happens, the status line says why."),
                    ))
                    .with_children(|btn| {
                        btn.spawn(theme::icon(asset_server, "spark", 15.0, theme::TEXT));
                        btn.spawn((theme::label(fonts, "React", theme::MD, theme::Weight::Semibold, theme::TEXT), Pickable::IGNORE));
                    });
            })
            .id();
    });
    card
}

pub fn vessel_react_button_system(
    interaction_q: Query<(&Interaction, &ChildOf), (Changed<Interaction>, With<VesselReactButton>, With<Button>)>,
    mut ev_check: MessageWriter<CheckVesselReaction>,
) {
    for (interaction, parent) in &interaction_q {
        if *interaction == Interaction::Pressed {
            ev_check.write(CheckVesselReaction(parent.0));
        }
    }
}

/// Walk up from a vessel button to its VesselCard.
fn vessel_of(mut e: Entity, parents: &Query<&ChildOf>, cards: &Query<(), With<VesselCard>>) -> Option<Entity> {
    for _ in 0..6 {
        if cards.contains(e) {
            return Some(e);
        }
        e = parents.get(e).ok()?.0;
    }
    None
}

pub fn vessel_clear_button_system(
    mut commands: Commands,
    button_q: Query<(Entity, &Interaction), (Changed<Interaction>, With<VesselClearButton>)>,
    parent_q: Query<&ChildOf>,
    cards: Query<(), With<VesselCard>>,
    ingredients_q: Query<(Entity, &InVessel)>,
    catalysts_q: Query<(Entity, &InCatalystZone)>,
    mut eq_q: Query<(&mut Text, &mut TextColor, &ChildOf), With<EquationText>>,
) {
    for (btn, interaction) in &button_q {
        if *interaction != Interaction::Pressed {
            continue;
        }
        let Some(vessel) = vessel_of(btn, &parent_q, &cards) else { continue };
        for (e, in_vessel) in &ingredients_q {
            if in_vessel.0 == vessel {
                commands.entity(e).despawn();
            }
        }
        for (e, in_zone) in &catalysts_q {
            if in_zone.0 == vessel {
                commands.entity(e).despawn();
            }
        }
        set_status(&mut eq_q, vessel, "Drop ingredients in, then React.", Color::srgb(0.6, 0.64, 0.75));
    }
}

pub fn vessel_delete_button_system(
    mut commands: Commands,
    button_q: Query<(Entity, &Interaction), (Changed<Interaction>, With<VesselDeleteButton>)>,
    parent_q: Query<&ChildOf>,
    cards: Query<(), With<VesselCard>>,
    links_q: Query<(Entity, &ReactionLink)>,
) {
    for (btn, interaction) in &button_q {
        if *interaction != Interaction::Pressed {
            continue;
        }
        let Some(vessel) = vessel_of(btn, &parent_q, &cards) else { continue };
        commands.entity(vessel).despawn();
        for (link_entity, link) in &links_q {
            if link.from_vessel == vessel || link.to_vessel == vessel {
                commands.entity(link_entity).despawn();
            }
        }
    }
}

/// Set a vessel's status line (the EquationText under its contents).
fn set_status(
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
) {
    let speed = settings.as_ref().map(|s| s.reaction_speed).unwrap_or(1.0).max(0.05);
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
            // --- fizzle: say why if we can ---
            let hint = match &found {
                Lookup::NeedsTier(p) => Some(format!(
                    "Too much for the {}: this needs the {} ({} {}){}.",
                    vessel_name(process),
                    vessel_name(p),
                    p.family(),
                    crate::ui::process_toolbar::roman(p.tier()),
                    if unlocks.0.contains(p) { "" } else { ", which you haven't unlocked yet" },
                )),
                Lookup::OtherVessel(p) => {
                    Some(format!("These don't react in the {}, but try a {}.", vessel_name(process), vessel_name(p)))
                }
                _ => None,
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
                let msg = format!("Almost: this needs {} in the catalyst slot.", name_of(needed));
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
        }

        // Consume ingredients.
        for (entity, _, in_vessel) in vessel_ingredients.iter() {
            if in_vessel.0 == vessel_entity {
                commands.entity(entity).despawn();
            }
        }

        let equation = format!("{}\n{}", reaction.name, build_equation_string(reaction, substances_db));
        set_status(&mut eq_q, vessel_entity, &equation, theme::TEXT);
        events.write(GameEvent::Reacted { reaction_id: reaction.id, vessel: vessel_entity });

        // Prepare products.
        let mut products = Vec::new();
        for sp in &reaction.products {
            if let Some(sub) = substances_db.0.get(&sp.substance_id) {
                products.push(Ingredient {
                    id: sub.id,
                    name: sub.name.clone(),
                    formula: sub.formula.clone(),
                    state: sub.state,
                    properties: sub.properties.clone(),
                    amount: sp.moles.max(1),
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
            let product_index = available_products.iter().position(|product| matches_filter(product, &port.filter));
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
