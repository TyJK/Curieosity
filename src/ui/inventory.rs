// src/ui/inventory.rs
//
// The shelf: every discovered substance, filtered by category, as draggable tiles; and the
// chips that stand for a substance inside a vessel. New tiles and products pop in. Only the
// tiles in sight (and a screen either side) are built: see ui/virtual_list.rs.
use bevy::prelude::*;
use bevy::ui::ScrollPosition;

use crate::components::{Draggable, Ingredient};
use crate::data::common::{MatterState, Property};
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::drag_drop::{DragGhost, Swiping};
use crate::ui::theme::{self, Weight};
use crate::ui::virtual_list::VirtualList;
use crate::GameData;

/// The grid that holds the tiles (a VirtualList: only the tiles in sight are built).
#[derive(Component)]
pub struct InventoryContent;

/// A shelf tile's size, and the gap between tiles.
pub const TILE: Vec2 = Vec2::new(84.0, 104.0);
const TILE_GAP: f32 = 8.0;

/// The clipping viewport that scrolls.
#[derive(Component)]
pub struct InventoryScroll;

/// The shelf dock along the bottom of the screen.
#[derive(Component)]
pub struct ShelfDock;

/// How tall the shelf dock is: its full height on a tall screen, down to one row of tiles
/// on a short one (a phone held sideways), so the bench keeps its room. In interface pixels.
#[derive(Resource, Clone, Copy, PartialEq, Debug)]
pub struct Dock {
    pub h: f32,
    /// the bench's height, between the header and the dock
    pub bench: f32,
}

impl Default for Dock {
    fn default() -> Self {
        Self { h: theme::DOCK_H, bench: 720.0 - theme::HEADER_H - theme::DOCK_H }
    }
}

/// The shelf's bar and one full row of tiles.
const DOCK_MIN: f32 = 156.0;

/// The dock's height on a screen this tall (interface pixels).
pub fn dock_height(screen_h: f32) -> f32 {
    (screen_h * 0.36).clamp(DOCK_MIN, theme::DOCK_H)
}

/// Sizes the dock to the screen, and moves the bench and the vessel list to sit on it.
#[allow(clippy::type_complexity)]
pub fn fit_dock_system(
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    ui_scale: Res<UiScale>,
    mut dock: ResMut<Dock>,
    mut nodes: Query<
        (&mut Node, Has<ShelfDock>),
        Or<(
            With<ShelfDock>,
            With<crate::components::ui_markers::ReactionCanvasRoot>,
            With<crate::ui::process_toolbar::VesselSidebar>,
        )>,
    >,
) {
    let Ok(w) = windows.single() else { return };
    let screen = w.height() / ui_scale.0.max(0.01);
    if screen < 1.0 {
        return;
    }
    let h = dock_height(screen);
    let want = Dock { h, bench: screen - theme::HEADER_H - h };
    if *dock != want {
        *dock = want;
    }
    for (mut node, is_dock) in &mut nodes {
        if is_dock {
            if node.height != Val::Px(h) {
                node.height = Val::Px(h);
            }
        } else if node.bottom != Val::Px(h) {
            node.bottom = Val::Px(h);
        }
    }
}

/// Marks a category tab button.
#[derive(Component)]
pub struct CategoryTab(pub InvCategory);

/// Which category the inventory is currently filtered to. Also a Resource.
#[derive(Resource, Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum InvCategory {
    #[default]
    All,
    Elements,
    Compounds,
    Acids,
    Bases,
    Metals,
    Gas,
    Liquid,
    Solid,
    /// Locked previews from later stages (the Substance Library only; never on the shelf).
    Coming,
}

const TABS: [(InvCategory, &str); 9] = [
    (InvCategory::All, "All"),
    (InvCategory::Elements, "Elements"),
    (InvCategory::Compounds, "Compounds"),
    (InvCategory::Acids, "Acids"),
    (InvCategory::Bases, "Bases"),
    (InvCategory::Metals, "Metals"),
    (InvCategory::Gas, "Gas"),
    (InvCategory::Liquid, "Liquid"),
    (InvCategory::Solid, "Solid"),
];

/// Counts the distinct element symbols in a formula string, e.g.
/// "H2" -> 1 (H), "NaCl" -> 2 (Na, Cl), "(NH4)2CO3" -> 4 (N,H,C,O), "C" -> 1.
/// A substance is an "element" when this is exactly 1.
fn distinct_elements(formula: &str) -> usize {
    let mut seen = std::collections::HashSet::new();
    let bytes = formula.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        let c = bytes[i] as char;
        if c.is_ascii_uppercase() {
            let mut sym = String::from(c);
            i += 1;
            while i < bytes.len() && (bytes[i] as char).is_ascii_lowercase() {
                sym.push(bytes[i] as char);
                i += 1;
            }
            seen.insert(sym);
        } else {
            i += 1; // digits, parentheses, charges, etc.
        }
    }
    seen.len()
}

pub fn matches_category(sub: &crate::data::substances::Substance, cat: InvCategory) -> bool {
    let is_element = distinct_elements(&sub.formula) == 1;
    match cat {
        InvCategory::All => true,
        InvCategory::Elements => is_element,
        InvCategory::Compounds => !is_element,
        InvCategory::Acids => sub.properties.contains(&Property::IsAcid),
        InvCategory::Bases => sub.properties.contains(&Property::IsBase),
        InvCategory::Metals => sub.properties.contains(&Property::IsMetal),
        InvCategory::Gas => sub.state == MatterState::Gas,
        InvCategory::Liquid => sub.state == MatterState::Liquid,
        InvCategory::Solid => sub.state == MatterState::Solid,
        InvCategory::Coming => sub.stage.is_some(),
    }
}

// --- element rendering helpers -----------------------------------------------------
const ELEMENT_SYMBOLS: [&str; 118] = [
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne", "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr", "Y",
    "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I", "Xe", "Cs", "Ba", "La", "Ce",
    "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "Hf", "Ta", "W", "Re", "Os", "Ir",
    "Pt", "Au", "Hg", "Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm",
    "Bk", "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs", "Mt", "Ds", "Rg", "Cn", "Nh", "Fl", "Mc",
    "Lv", "Ts", "Og",
];

/// The single element symbol at the start of a formula ("H2" -> "H", "Na" -> "Na").
fn element_symbol(formula: &str) -> Option<String> {
    let bytes = formula.as_bytes();
    let mut i = 0;
    while i < bytes.len() {
        let c = bytes[i] as char;
        if c.is_ascii_uppercase() {
            let mut sym = String::from(c);
            i += 1;
            while i < bytes.len() && (bytes[i] as char).is_ascii_lowercase() {
                sym.push(bytes[i] as char);
                i += 1;
            }
            return Some(sym);
        }
        i += 1;
    }
    None
}

fn atomic_number(sym: &str) -> Option<u32> {
    ELEMENT_SYMBOLS.iter().position(|&s| s == sym).map(|i| i as u32 + 1)
}

/// Periodic-table block tint (light on the dark UI, like a real table).
fn block_color(z: u32) -> Color {
    let f = (57..=71).contains(&z) || (89..=103).contains(&z);
    let d = (21..=30).contains(&z) || (39..=48).contains(&z) || (72..=80).contains(&z) || (104..=112).contains(&z);
    let s = matches!(z, 1 | 3 | 4 | 11 | 12 | 19 | 20 | 37 | 38 | 55 | 56 | 87 | 88);
    if f {
        Color::srgb(0.741, 0.620, 1.0) // f-block (violet)
    } else if d {
        Color::srgb(1.0, 0.851, 0.420) // d-block (gold)
    } else if s {
        Color::srgb(1.0, 0.520, 0.560) // s-block (coral)
    } else {
        Color::srgb(0.400, 0.880, 0.950) // p-block + noble (cyan)
    }
}

pub fn spawn_inventory_panel(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    commands
        .spawn((
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                bottom: Val::Px(0.0),
                height: Val::Px(theme::DOCK_H),
                flex_direction: FlexDirection::Column,
                border: UiRect::top(Val::Px(1.0)),
                ..default()
            },
            ShelfDock,
            BackgroundColor(theme::BG),
            BorderColor::all(theme::LINE),
            Name::new("InventoryPanel"),
        ))
        .with_children(|panel| {
            // --- shelf header: title, category pills, count ---
            panel
                .spawn((
                    Node {
                        width: Val::Percent(100.0),
                        height: Val::Px(42.0),
                        flex_direction: FlexDirection::Row,
                        align_items: AlignItems::Center,
                        column_gap: Val::Px(6.0),
                        padding: UiRect::axes(Val::Px(14.0), Val::Px(4.0)),
                        ..default()
                    },
                    Name::new("InventoryTabs"),
                ))
                .with_children(|bar| {
                    bar.spawn(Node {
                        align_items: AlignItems::Center,
                        column_gap: Val::Px(7.0),
                        margin: UiRect::right(Val::Px(10.0)),
                        ..default()
                    })
                    .with_children(|t| {
                        t.spawn(theme::icon(&assets, "flask", 16.0, theme::CYAN));
                        t.spawn(theme::label(&fonts, "SHELF", theme::XS, Weight::Bold, theme::TEXT_2));
                    });
                    for (cat, label) in TABS {
                        bar.spawn((
                            theme::button(
                                theme::Kind::Tab,
                                Node {
                                    height: Val::Px(26.0),
                                    padding: UiRect::horizontal(Val::Px(11.0)),
                                    align_items: AlignItems::Center,
                                    justify_content: JustifyContent::Center,
                                    ..default()
                                },
                                99.0,
                            ),
                            CategoryTab(cat),
                        ))
                        .with_children(|b| {
                            b.spawn((
                                theme::label(&fonts, label, 12.0, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                        });
                    }
                    bar.spawn(Node { flex_grow: 1.0, ..default() });
                    bar.spawn((ShelfCount, theme::label(&fonts, "", theme::XS, Weight::Regular, theme::TEXT_3)));
                    crate::ui::detail_panel::spawn_selection_bar(bar, &fonts, &assets);
                });

            // --- scrolling viewport ---
            panel
                .spawn((
                    InventoryScroll,
                    ScrollPosition::default(),
                    Node {
                        width: Val::Percent(100.0),
                        flex_grow: 1.0,
                        overflow: Overflow::scroll_y(),
                        padding: UiRect::new(Val::Px(14.0), Val::Px(14.0), Val::Px(2.0), Val::Px(10.0)),
                        ..default()
                    },
                    Name::new("InventoryScroll"),
                ))
                .with_children(|scroll| {
                    scroll.spawn((
                        InventoryContent,
                        VirtualList::new(TILE, Vec2::splat(TILE_GAP)),
                        // clipped below, so a label spilling out of the last row's tiles never
                        // lengthens the scroll: the shelf's extent is the grid and nothing else
                        Node {
                            width: Val::Percent(100.0),
                            height: Val::Px(0.0),
                            flex_shrink: 0.0,
                            overflow: Overflow::clip_y(),
                            ..default()
                        },
                        Name::new("InventoryContent"),
                    ));
                });
        });
}

/// A shelf tile's resting colours, so hover and selection can light it up and put it back.
#[derive(Component)]
pub struct ShelfTile {
    pub border: Color,
    pub bg: Color,
}

impl ShelfTile {
    /// (background, border) for a tile that is hovered and/or selected.
    pub fn look(&self, hovered: bool, selected: bool) -> (Color, Color) {
        if selected {
            (theme::mix(self.bg, theme::CYAN, 0.22), theme::CYAN)
        } else if hovered {
            (theme::mix(self.bg, theme::TEXT, 0.05), theme::CYAN.with_alpha(0.8))
        } else {
            (self.bg, self.border)
        }
    }
}

/// "N on the shelf" in the shelf header.
#[derive(Component)]
pub struct ShelfCount;

pub fn shelf_hover_system(
    mut q: Query<(&Interaction, &ShelfTile, &Ingredient, &mut BorderColor, &mut BackgroundColor), Changed<Interaction>>,
    selected: Res<crate::ui::detail_panel::SelectedSubstance>,
) {
    for (i, tile, ing, mut border, mut bg) in &mut q {
        let (b, c) = tile.look(*i != Interaction::None, selected.0 == Some(ing.id));
        bg.0 = b;
        *border = BorderColor::all(c);
    }
}

pub(crate) fn short(s: &str, n: usize) -> String {
    if s.chars().count() > n {
        s.chars().take(n - 1).collect::<String>() + "…"
    } else {
        s.to_string()
    }
}

/// Shelf order: elements by atomic number, then compounds by id.
fn shelf_key(s: &crate::data::substances::Substance) -> (u8, u32) {
    match &s.element_info {
        Some(ei) => (0u8, ei.atomic_number),
        None => (1u8, s.id),
    }
}

/// Keeps the shelf's list in step with the discovered set and the category. A new category
/// or tile layout rebuilds it; a discovery only adds the new ids (popping in if they are in
/// sight), so a shelf of a thousand tiles never rebuilds just because one more turned up.
/// Which tiles are built at all is the window's business (`shelf_window_system`).
#[allow(clippy::too_many_arguments)]
pub fn populate_inventory_system(
    mut commands: Commands,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    mut content_query: Query<&mut VirtualList, With<InventoryContent>>,
    mut tabs: Query<(&CategoryTab, &mut theme::Skin)>,
    mut count_q: Query<&mut Text, With<ShelfCount>>,
    settings: Option<Res<crate::ui::settings::Settings>>,
    mut scroll_q: Query<&mut ScrollPosition, With<InventoryScroll>>,
    progress: Res<PlayerProgress>,
    filter: Res<InvCategory>,
    recipe_db: Option<Res<crate::resources::recipe_database::RecipeDatabase>>,
    dragging: Query<(), With<DragGhost>>,
    mut layout: Local<Option<(InvCategory, bool)>>,
    mut pending: Local<bool>,
) {
    // Wait for the authored layer to be applied and the save/start set to be loaded.
    if recipe_db.is_none() || !progress.ready {
        return;
    }
    let Some(substances) = substances_assets.get(&game_data.substances) else {
        return;
    };
    let names_first = settings.as_ref().is_some_and(|s| s.names_first);
    let rebuild = *layout != Some((*filter, names_first));
    if !(rebuild || progress.is_changed() || *pending) {
        return;
    }
    let Ok(mut list) = content_query.single_mut() else {
        return;
    };

    let mut items: Vec<_> =
        substances.0.values().filter(|s| progress.discovered.contains(&s.id) && matches_category(s, *filter)).collect();
    items.sort_by_key(|s| shelf_key(s));
    if let Ok(mut t) = count_q.single_mut() {
        t.0 = format!("{} on the shelf", items.len());
    }
    let ids: Vec<u32> = items.iter().map(|s| s.id).collect();
    let wanted: std::collections::HashSet<u32> = ids.iter().copied().collect();
    let gone = list.ids().iter().any(|id| !wanted.contains(id));

    // Removing tiles (a new game) or rebuilding despawns tiles, possibly one being
    // dragged: its drag would never end. Hold off until the drag is over.
    if (rebuild || gone) && !dragging.is_empty() {
        *pending = true;
        return;
    }
    *pending = false;

    if rebuild {
        // Switching category: jump back to the top so a short list doesn't open parked
        // below its content.
        if layout.is_some_and(|(f, _)| f != *filter) {
            for mut sp in &mut scroll_q {
                sp.0.y = 0.0;
            }
        }
        *layout = Some((*filter, names_first));
        for (tab, mut skin) in &mut tabs {
            let active = tab.0 == *filter;
            if skin.active != active {
                skin.active = active;
            }
        }
        for e in list.clear() {
            commands.entity(e).despawn();
        }
        list.set(ids, []);
        info!("Inventory: {} shown ({:?}), {} discovered", items.len(), *filter, progress.discovered.len());
        return;
    }

    let had: std::collections::HashSet<u32> = list.ids().iter().copied().collect();
    let fresh: Vec<u32> = ids.iter().copied().filter(|id| !had.contains(id)).collect();
    list.set(ids, fresh);
}

/// Builds the shelf tiles in sight (and a screen either side), drops those far out of it,
/// and keeps the built ones in their cells and in shelf order. Cheap when nothing moved.
#[allow(clippy::too_many_arguments, clippy::type_complexity)]
pub fn shelf_window_system(
    mut commands: Commands,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    settings: Option<Res<crate::ui::settings::Settings>>,
    look: (Res<UiFonts>, Res<AssetServer>),
    focus: Option<Res<crate::ui::focus::KeyFocus>>,
    mut content_q: Query<(Entity, &mut VirtualList, &mut Node, &ComputedNode), With<InventoryContent>>,
    scroll_q: Query<(&ComputedNode, &ScrollPosition), With<InventoryScroll>>,
    mut tiles: Query<&mut Node, (With<ShelfTile>, Without<InventoryContent>)>,
    busy: Query<(Has<DragGhost>, Has<Swiping>, &Interaction), With<ShelfTile>>,
) {
    let (fonts, asset_server) = look;
    let Ok((content, mut list, mut node, cn)) = content_q.single_mut() else {
        return;
    };
    let Ok((view, scroll)) = scroll_q.single() else {
        return;
    };
    let Some(substances) = substances_assets.get(&game_data.substances) else {
        return;
    };
    let focused = focus.and_then(|f| f.entity);
    // a tile being dragged, swiped, pressed or focused stays built wherever it scrolls to
    let keep = |e: Entity| {
        Some(e) == focused || busy.get(e).is_ok_and(|(drag, swipe, i)| drag || swipe || *i == Interaction::Pressed)
    };
    let width = cn.size.x * cn.inverse_scale_factor();
    let view_h = view.size.y * view.inverse_scale_factor();
    let Some(pass) = list.plan(width, view_h, scroll.0.y, keep) else {
        return;
    };
    if node.height != Val::Px(pass.height) {
        node.height = Val::Px(pass.height);
    }
    for e in &pass.drop {
        commands.entity(*e).despawn();
    }
    for (e, at) in &pass.moves {
        if let Ok(mut n) = tiles.get_mut(*e) {
            n.left = Val::Px(at.x);
            n.top = Val::Px(at.y);
        }
    }
    let names_first = settings.as_ref().is_some_and(|s| s.names_first);
    let mut popped = 0;
    for (id, at, fresh) in &pass.build {
        let Some(sub) = substances.0.get(id) else { continue };
        let e = spawn_shelf_tile(&mut commands, sub, names_first, &fonts, &asset_server, *at);
        if *fresh {
            commands.entity(e).insert((PopIn::new(popped as f32 * 0.06), NewGlow::default()));
            popped += 1;
        }
        list.record(*id, e, *at);
    }
    if !pass.build.is_empty() || !pass.drop.is_empty() {
        commands.entity(content).replace_children(&list.order());
    }
}

/// Scrolls the shelf so the tile for `id` comes into sight (the window builds it a frame
/// later). False when that substance is not on the shelf under the current category.
pub fn reveal_on_shelf(world: &mut World, id: u32) -> bool {
    let Some(y) = world
        .query_filtered::<(&VirtualList, &ComputedNode), With<InventoryContent>>()
        .iter(world)
        .next()
        .and_then(|(list, cn)| list.offset_of(id, cn.size.x * cn.inverse_scale_factor()))
    else {
        return false;
    };
    for mut sp in world.query_filtered::<&mut ScrollPosition, With<InventoryScroll>>().iter_mut(world) {
        sp.0.y = (y - TILE_GAP).max(0.0);
    }
    true
}

/// One shelf tile, not yet parented, placed at `at` in the shelf's grid: a periodic-table
/// card for an element, the drawn structure with formula and name for a compound.
pub fn spawn_shelf_tile(
    commands: &mut Commands,
    sub: &crate::data::substances::Substance,
    names_first: bool,
    fonts: &UiFonts,
    asset_server: &AssetServer,
    at: Vec2,
) -> Entity {
    let ingredient = Ingredient {
        id: sub.id,
        name: sub.name.clone(),
        formula: sub.formula.clone(),
        state: sub.state,
        properties: sub.properties.clone(),
        amount: 1,
    };
    let label = ingredient.label();
    let symbol = element_symbol(&sub.formula);
    let is_element = symbol.is_some() && distinct_elements(&sub.formula) == 1;
    let block = if is_element {
        let z = sub
            .element_info
            .as_ref()
            .map(|e| e.atomic_number)
            .or_else(|| symbol.as_deref().and_then(atomic_number))
            .unwrap_or(0);
        Some(block_color(z))
    } else {
        None
    };
    let (bg, border) = match block {
        Some(c) => (theme::mix(theme::RAISED, c, 0.10), c.with_alpha(0.55)),
        None => (theme::RAISED, theme::LINE),
    };
    commands
        .spawn((
            ingredient,
            Draggable,
            ShelfTile { border, bg },
            crate::ui::onboarding::Tip::Substance(sub.id),
            Interaction::default(),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(at.x),
                top: Val::Px(at.y),
                width: Val::Px(TILE.x),
                height: Val::Px(TILE.y),
                flex_direction: FlexDirection::Column,
                align_items: AlignItems::Center,
                justify_content: JustifyContent::SpaceBetween,
                padding: UiRect::axes(Val::Px(4.0), Val::Px(6.0)),
                border: UiRect::all(Val::Px(1.0)),
                ..default()
            },
            BorderRadius::all(Val::Px(theme::R_MD)),
            BackgroundColor(bg),
            BorderColor::all(border),
        ))
        .with_children(|item| {
            if let Some(c) = block {
                let sym = symbol.clone().unwrap_or_default();
                let ei = sub.element_info.as_ref();
                let z = ei.map(|e| e.atomic_number).or_else(|| atomic_number(&sym));
                let weight = ei.map(|e| e.atomic_weight).unwrap_or(sub.molar_mass_g_mol);
                item.spawn((
                    Node {
                        width: Val::Percent(100.0),
                        justify_content: JustifyContent::SpaceBetween,
                        padding: UiRect::horizontal(Val::Px(3.0)),
                        ..default()
                    },
                    Pickable::IGNORE,
                ))
                .with_children(|top| {
                    top.spawn((
                        theme::label(fonts, z.map(|z| z.to_string()).unwrap_or_default(), 10.0, Weight::Semibold, c),
                        Pickable::IGNORE,
                    ));
                    top.spawn((
                        theme::label(fonts, format!("{:.2}", weight), 9.0, Weight::Regular, theme::TEXT_3),
                        Pickable::IGNORE,
                    ));
                });
                item.spawn((theme::label(fonts, sym, 30.0, Weight::Semibold, c), Pickable::IGNORE));
                item.spawn((
                    theme::label(fonts, short(&sub.name, 13), theme::XS, Weight::Regular, theme::TEXT),
                    Pickable::IGNORE,
                ));
            } else {
                // compound: the drawn structure (white on transparent), then formula and name
                item.spawn((
                    ImageNode::new(asset_server.load(format!("structures/{}.png", sub.id))),
                    Node { width: Val::Px(54.0), height: Val::Px(54.0), ..default() },
                    Pickable::IGNORE,
                ));
                let size = match sub.formula.chars().count() {
                    0..=8 => 14.0,
                    9..=12 => 11.5,
                    _ => 9.5,
                };
                // names stay readable on a phone: never below 11 px, in near-white
                let name = short(&sub.name, 14);
                if names_first {
                    item.spawn((theme::label(fonts, name, 12.0, Weight::Semibold, theme::TEXT), Pickable::IGNORE));
                    item.spawn((
                        Text::new(label),
                        TextFont { font: fonts.main.clone(), font_size: 11.0, ..default() },
                        TextColor(theme::TEXT_2),
                        Node { max_width: Val::Px(80.0), ..default() },
                        Pickable::IGNORE,
                    ));
                } else {
                    item.spawn((
                        Text::new(label),
                        TextFont { font: fonts.semibold.clone(), font_size: size, ..default() },
                        TextColor(theme::TEXT),
                        Node { max_width: Val::Px(80.0), ..default() },
                        Pickable::IGNORE,
                    ));
                    item.spawn((theme::label(fonts, name, theme::XS, Weight::Regular, theme::TEXT), Pickable::IGNORE));
                }
            }
        })
        .id()
}

// ---------------------------------------------------------------------------------------
// Arrivals: new tiles and fresh products pop in
// ---------------------------------------------------------------------------------------
/// Scales a node up from small with a little overshoot, after an optional delay.
#[derive(Component)]
pub struct PopIn {
    pub t: f32,
}

impl PopIn {
    pub const DURATION: f32 = 0.32;
    /// `delay` seconds before it starts (staggers a row of arrivals)
    pub fn new(delay: f32) -> Self {
        Self { t: -delay }
    }
}

/// A new shelf tile's border glows green and fades back to its usual colour.
#[derive(Component, Default)]
pub struct NewGlow {
    pub t: f32,
}

const GLOW_SECS: f32 = 2.4;

pub fn pop_in_system(
    mut commands: Commands,
    time: Res<Time>,
    mut pops: Query<(Entity, &mut PopIn, &mut UiTransform)>,
    mut glows: Query<(Entity, &mut NewGlow, &ShelfTile, &mut BorderColor, &Interaction)>,
) {
    let dt = time.delta_secs();
    for (e, mut p, mut tf) in &mut pops {
        p.t += dt;
        let x = (p.t / PopIn::DURATION).clamp(0.0, 1.0);
        // ease-out-back: overshoot a little, settle at 1
        let c = 1.70158;
        let k = 1.0 + (c + 1.0) * (x - 1.0).powi(3) + c * (x - 1.0).powi(2);
        let scale = if p.t <= 0.0 { 0.35 } else { 0.35 + 0.65 * k };
        tf.scale = Vec2::splat(scale);
        if x >= 1.0 {
            tf.scale = Vec2::ONE;
            commands.entity(e).try_remove::<PopIn>();
        }
    }
    for (e, mut g, tile, mut border, interaction) in &mut glows {
        g.t += dt;
        let a = (1.0 - g.t / GLOW_SECS).clamp(0.0, 1.0);
        if *interaction == Interaction::None {
            *border = BorderColor::all(theme::mix(tile.border, theme::GREEN, a));
        }
        if a <= 0.0 {
            commands.entity(e).try_remove::<NewGlow>();
        }
    }
}

/// Clicking a category tab sets the active filter.
pub fn category_tab_system(
    interaction_q: Query<(&Interaction, &CategoryTab), (Changed<Interaction>, With<Button>)>,
    mut filter: ResMut<InvCategory>,
) {
    for (interaction, tab) in &interaction_q {
        if *interaction == Interaction::Pressed && *filter != tab.0 {
            *filter = tab.0;
        }
    }
}

/// True when a formula is a single element (H2, Na, Cl2, Fe) -- shown as a periodic tile
/// rather than a structure diagram.
pub fn is_element_formula(formula: &str) -> bool {
    element_symbol(formula).is_some() && distinct_elements(formula) == 1
}

/// Periodic-block colour for a single-element formula.
pub fn element_tile_color(formula: &str) -> Color {
    let z = element_symbol(formula).as_deref().and_then(atomic_number).unwrap_or(0);
    block_color(z)
}

/// What a chip is doing inside a vessel (the Entity is the VesselCard).
#[derive(Clone, Copy)]
pub enum ChipRole {
    Ingredient(Entity),
    Product(Entity),
    Catalyst(Entity),
}

/// One ingredient inside a vessel: a small icon (periodic tile for elements, the 2D
/// structure for compounds), the formula, the name, and the amount. Used for anything
/// dropped into a vessel and for every reaction product.
pub fn spawn_vessel_chip(
    zone: &mut ChildSpawnerCommands,
    ing: &Ingredient,
    role: ChipRole,
    fonts: &UiFonts,
    asset_server: &AssetServer,
) -> Entity {
    let accent = match role {
        ChipRole::Product(_) => theme::GREEN,
        ChipRole::Catalyst(_) => theme::GOLD,
        ChipRole::Ingredient(_) => theme::CYAN,
    };
    let mut chip_cmd = zone.spawn((
        ing.clone(),
        // drag a chip out to take it back, or onto another vessel to move it
        Draggable,
        Node {
            width: Val::Percent(100.0),
            min_height: Val::Px(34.0),
            align_items: AlignItems::Center,
            column_gap: Val::Px(7.0),
            padding: UiRect::new(Val::Px(4.0), Val::Px(6.0), Val::Px(2.0), Val::Px(2.0)),
            border: UiRect::new(Val::Px(3.0), Val::Px(1.0), Val::Px(1.0), Val::Px(1.0)),
            ..default()
        },
        BorderRadius::all(Val::Px(theme::R_SM)),
        BackgroundColor(theme::mix(theme::RAISED, accent, 0.10)),
        BorderColor {
            left: accent,
            top: accent.with_alpha(0.3),
            right: accent.with_alpha(0.3),
            bottom: accent.with_alpha(0.3),
        },
        Name::new(format!("Chip-{}", ing.name)),
    ));
    // Reactants and products are InVessel (they react and get consumed); a catalyst is
    // InCatalystZone, so it's never counted as a reactant.
    match role {
        ChipRole::Ingredient(v) | ChipRole::Product(v) => {
            chip_cmd.insert(crate::components::InVessel(v));
        }
        ChipRole::Catalyst(v) => {
            chip_cmd.insert(crate::components::ui_markers::InCatalystZone(v));
        }
    }
    chip_cmd.with_children(|chip| {
        if is_element_formula(&ing.formula) {
            chip.spawn((
                Node {
                    width: Val::Px(28.0),
                    height: Val::Px(28.0),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    ..default()
                },
                BorderRadius::all(Val::Px(5.0)),
                BackgroundColor(theme::mix(theme::RAISED, element_tile_color(&ing.formula), 0.15)),
                Pickable::IGNORE,
            ))
            .with_children(|t| {
                t.spawn((
                    Text::new(element_symbol(&ing.formula).unwrap_or_default()),
                    TextFont { font: fonts.semibold.clone(), font_size: 14.0, ..default() },
                    TextColor(element_tile_color(&ing.formula)),
                    Pickable::IGNORE,
                ));
            });
        } else {
            chip.spawn((
                ImageNode::new(asset_server.load(format!("structures/{}.png", ing.id))),
                Node { width: Val::Px(28.0), height: Val::Px(28.0), ..default() },
                Pickable::IGNORE,
            ));
        }
        chip.spawn((Node { flex_direction: FlexDirection::Column, flex_grow: 1.0, ..default() }, Pickable::IGNORE))
            .with_children(|col| {
                let formula = if ing.amount > 1 {
                    format!("{} {}", ing.amount, crate::components::format_formula(&ing.formula))
                } else {
                    crate::components::format_formula(&ing.formula)
                };
                col.spawn((
                    Text::new(formula),
                    TextFont { font: fonts.semibold.clone(), font_size: 13.0, ..default() },
                    TextColor(theme::TEXT),
                    Pickable::IGNORE,
                ));
                col.spawn((
                    Text::new(ing.name.clone()),
                    TextFont { font: fonts.main.clone(), font_size: theme::XS, ..default() },
                    TextColor(theme::TEXT),
                    Node { max_width: Val::Px(150.0), ..default() },
                    Pickable::IGNORE,
                ));
            });
    });
    chip_cmd.id()
}
