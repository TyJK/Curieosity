// src/ui/inventory.rs
//
// The shelf: every discovered substance, filtered by category (or newest first), as
// draggable tiles; and the chips that stand for a substance inside a vessel. New tiles and
// products pop in. Only the tiles in sight (and a screen either side) are built: see
// ui/virtual_list.rs. The grip on the shelf's top edge gives the bench more room or less;
// while a phone's keyboard types into the search, the shelf sits on the keyboard with the
// search box at its foot and the results just above, and the bench stays in sight.
use crate::ui::{Button, Clicked};
use bevy::picking::hover::Hovered;
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
pub const DOCK_MIN: f32 = 156.0;
/// The least the bench keeps when the shelf is dragged up.
const BENCH_MIN: f32 = 150.0;

/// The dock's height on a screen this tall (interface pixels), unless the player has set it
/// with the grip.
pub fn dock_height(screen_h: f32) -> f32 {
    (screen_h * 0.36).clamp(DOCK_MIN, theme::DOCK_H)
}

/// The tallest the shelf may be dragged on a screen this tall.
pub fn dock_max(screen_h: f32) -> f32 {
    (screen_h - theme::HEADER_H - BENCH_MIN).max(DOCK_MIN)
}

/// Below this width (interface pixels) the shelf's header leaves out its how-to line.
pub const NARROW_W: f32 = 1240.0;

/// The grip on the shelf's top edge: drag it up for a bigger shelf, down for a bigger bench.
#[derive(Component)]
pub struct ShelfGrip;

/// The shelf's height while the grip is being dragged (it is saved when the drag ends).
#[derive(Resource, Default, Debug)]
pub struct ShelfDrag {
    pub live: Option<f32>,
    start: f32,
}

/// Sizes the dock (the height the player set with the grip, or one to suit the screen) and
/// moves the bench to sit on it. On a narrow screen the shelf header drops its how-to line.
/// While a phone's keyboard types into the shelf search, the shelf sits on the keyboard,
/// its search box at the foot and a couple of rows of results above, and the bench keeps
/// the rest of the screen.
#[allow(clippy::type_complexity)]
pub fn fit_dock_system(
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    ui_scale: Res<UiScale>,
    mut dock: ResMut<Dock>,
    mut how_to: Query<
        &mut Node,
        (
            With<crate::ui::detail_panel::SelectionHint>,
            Without<ShelfDock>,
            Without<crate::components::ui_markers::ReactionCanvasRoot>,
        ),
    >,
    sizing: (Res<crate::ui::settings::Settings>, Res<ShelfDrag>),
    typing: (Res<ShelfSearch>, Res<crate::platform::SoftKeyboard>, Res<crate::platform::KeyboardInset>),
    mut nodes: Query<
        (&mut Node, Has<ShelfDock>),
        Or<(With<ShelfDock>, With<crate::components::ui_markers::ReactionCanvasRoot>)>,
    >,
    results: Query<(&VirtualList, &ComputedNode), With<InventoryContent>>,
) {
    let Ok(w) = windows.single() else { return };
    let screen = w.height() / ui_scale.0.max(0.01);
    if screen < 1.0 {
        return;
    }
    let narrow = w.width() / ui_scale.0.max(0.01) < NARROW_W;
    for mut n in &mut how_to {
        let want = if narrow { Display::None } else { Display::Flex };
        if n.display != want {
            n.display = want;
        }
    }
    let (settings, drag) = sizing;
    let (search, soft, inset) = typing;
    let set = drag.live.or((settings.shelf_h > 0.0).then_some(settings.shelf_h));
    let mut h = set.map_or(dock_height(screen), |h| h.clamp(DOCK_MIN, dock_max(screen)));
    let mut lift = 0.0;
    // a phone's keyboard is up for the shelf search: on it, two rows of results and the box
    let on_keys = soft.0 && search.typing;
    if on_keys {
        lift = inset.0.clamp(0.0, (screen - theme::HEADER_H - DOCK_MIN).max(0.0));
        // as many rows as the results take, up to two, right above the box
        let width = results.single().map(|(_, cn)| cn.size.x * cn.inverse_scale_factor()).unwrap_or(0.0);
        let cols = (((width + TILE_GAP) / (TILE.x + TILE_GAP)).floor() as usize).max(1);
        let n = results.single().map(|(l, _)| l.ids().len()).unwrap_or(0);
        let rows = n.div_ceil(cols).clamp(1, 2) as f32;
        let want = SHELF_HEAD_H + rows * (TILE.y + TILE_GAP) + 12.0;
        h = want.min(screen - theme::HEADER_H - lift - 96.0).max(SHELF_HEAD_H + TILE.y + 12.0);
    }
    let want = Dock { h: h + lift, bench: screen - theme::HEADER_H - h - lift };
    if *dock != want {
        *dock = want;
    }
    for (mut node, is_dock) in &mut nodes {
        if is_dock {
            let (height, bottom) = (Val::Px(h), Val::Px(lift));
            let dir = if on_keys { FlexDirection::ColumnReverse } else { FlexDirection::Column };
            if node.height != height || node.bottom != bottom || node.flex_direction != dir {
                node.height = height;
                node.bottom = bottom;
                node.flex_direction = dir;
            }
        } else {
            let bottom = Val::Px(h + lift);
            if node.bottom != bottom {
                node.bottom = bottom;
            }
        }
    }
}

/// Dragging the grip resizes the shelf; letting go keeps the size (Settings: shelf_h).
fn grip_drag_start(mut t: On<PointerDragStart>, dock: Res<Dock>, mut drag: ResMut<ShelfDrag>) {
    t.propagate(false);
    drag.start = dock.h;
    drag.live = Some(dock.h);
}

fn grip_drag(
    mut t: On<PointerDrag>,
    mut drag: ResMut<ShelfDrag>,
    ui_scale: Res<UiScale>,
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
) {
    t.propagate(false);
    let screen = windows.single().map(|w| w.height() / ui_scale.0.max(0.01)).unwrap_or(720.0);
    let h = (drag.start - t.distance.y / ui_scale.0.max(0.01)).clamp(DOCK_MIN, dock_max(screen));
    if drag.live != Some(h) {
        drag.live = Some(h);
    }
}

fn grip_drag_end(
    mut t: On<PointerDragEnd>,
    mut drag: ResMut<ShelfDrag>,
    mut settings: ResMut<crate::ui::settings::Settings>,
) {
    t.propagate(false);
    if let Some(h) = drag.live.take() {
        settings.shelf_h = h.round();
    }
}

/// The shelf's category list (a dropdown), whether it is open.
#[derive(Resource, Default, Debug)]
pub struct ShelfMenu(pub bool);

/// The button that opens the category list, its label, the list, and the backdrop around it.
#[derive(Component)]
pub struct ShelfCategoryButton;
#[derive(Component)]
pub struct ShelfCategoryLabel;
#[derive(Component)]
pub struct ShelfCategoryMenu;
#[derive(Component)]
pub struct ShelfMenuBackdrop;

pub fn spawn_shelf_menu(mut commands: Commands, fonts: Res<UiFonts>) {
    commands
        .spawn((
            ShelfMenuBackdrop,
            GlobalZIndex(800),
            crate::ui::Button,
            crate::ui::focus::NoFocus,
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(0.0),
                bottom: Val::Px(0.0),
                display: Display::None,
                ..default()
            },
            Pickable::default(),
            Name::new("ShelfMenu"),
        ))
        .with_children(|b| {
            b.spawn((
                ShelfCategoryMenu,
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    bottom: Val::Px(0.0),
                    width: Val::Px(176.0),
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(3.0),
                    padding: UiRect::all(Val::Px(6.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE_STRONG),
                theme::shadow(20.0, 6.0, 0.6),
            ))
            .with_children(|list| {
                for (cat, label) in TABS {
                    list.spawn((
                        theme::button(
                            theme::Kind::Row,
                            Node {
                                height: Val::Px(38.0),
                                padding: UiRect::horizontal(Val::Px(12.0)),
                                align_items: AlignItems::Center,
                                ..default()
                            },
                            theme::R_SM,
                        ),
                        CategoryTab(cat),
                    ))
                    .with_children(|r| {
                        r.spawn((
                            theme::label(&fonts, label, theme::SM, Weight::Semibold, theme::TEXT),
                            Pickable::IGNORE,
                        ));
                    });
                }
            });
        });
}

/// Opens and closes the category list, under (or rather over) its button.
#[allow(clippy::type_complexity)]
pub fn shelf_menu_system(
    mut menu: ResMut<ShelfMenu>,
    opener: Query<(), (With<Clicked>, With<ShelfCategoryButton>)>,
    backdrop_tap: Query<(), (With<Clicked>, With<ShelfMenuBackdrop>)>,
    chosen: Query<(), (With<Clicked>, With<CategoryTab>)>,
    button: Query<(&ComputedNode, &UiGlobalTransform), With<ShelfCategoryButton>>,
    windows: Query<&Window, With<bevy::window::PrimaryWindow>>,
    ui_scale: Res<UiScale>,
    mut backdrop: Query<&mut Node, (With<ShelfMenuBackdrop>, Without<ShelfCategoryMenu>)>,
    mut list: Query<&mut Node, (With<ShelfCategoryMenu>, Without<ShelfMenuBackdrop>)>,
) {
    if !opener.is_empty() {
        menu.0 = !menu.0;
    } else if menu.0 && (!backdrop_tap.is_empty() || !chosen.is_empty()) {
        menu.0 = false;
    }
    if let Ok(mut n) = backdrop.single_mut() {
        let d = if menu.0 { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if !menu.0 {
        return;
    }
    // just above its button, lined up with it
    let (Ok((cn, gt)), Ok(w), Ok(mut n)) = (button.single(), windows.single(), list.single_mut()) else { return };
    let k = cn.inverse_scale_factor();
    let top_left = (gt.translation - cn.size * 0.5) * k;
    let screen_h = w.height() / ui_scale.0.max(0.01);
    let (left, bottom) = (Val::Px(top_left.x.max(4.0)), Val::Px(screen_h - top_left.y + 4.0));
    if n.left != left || n.bottom != bottom {
        n.left = left;
        n.bottom = bottom;
    }
}

/// Marks a category tab button.
#[derive(Component)]
pub struct CategoryTab(pub InvCategory);

/// The shelf's search: what is typed, and whether typing goes to it.
#[derive(Resource, Default, Debug, Clone)]
pub struct ShelfSearch {
    pub typing: bool,
    pub text: String,
}

impl ShelfSearch {
    /// Whether a substance matches what is typed (names and formulas, any case).
    pub fn matches(&self, sub: &crate::data::substances::Substance) -> bool {
        let q = self.text.trim().to_lowercase();
        q.is_empty() || sub.name.to_lowercase().contains(&q) || sub.formula.to_lowercase().contains(&q)
    }
}

/// Which search box the on-screen keyboard is typing into (a phone's keyboard types into
/// one text field; on a desktop, typing arrives as key presses and this stays None).
#[derive(Resource, Default, Debug, Clone, Copy, PartialEq, Eq)]
pub enum TypingBox {
    #[default]
    None,
    Shelf,
    Codex,
    Reactions,
}

/// The shelf's search box, its text and its clear button.
#[derive(Component)]
pub struct ShelfSearchBox;
#[derive(Component)]
pub struct ShelfSearchText;
#[derive(Component)]
pub struct ShelfSearchClear;
/// "Done": puts a phone's keyboard away and brings the bench back.
#[derive(Component)]
pub struct ShelfSearchDone;
/// "SHELF", or "KIT" while a target's kit is showing.
#[derive(Component)]
pub struct ShelfTitle;
/// The shelf's header: its title, the category dropdown and the search, then the how-to
/// line and the Library button. One row, held either way.
#[derive(Component)]
pub struct ShelfHead;

/// The shelf header's height.
pub const SHELF_HEAD_H: f32 = 46.0;

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
    /// Everything, newest discovery first (the shelf only).
    New,
}

impl InvCategory {
    /// The shelf's word for it.
    pub fn label(self) -> &'static str {
        TABS.iter().find(|(c, _)| *c == self).map(|(_, l)| *l).unwrap_or("All")
    }
}

const TABS: [(InvCategory, &str); 10] = [
    (InvCategory::New, "Newest first"),
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
        InvCategory::All | InvCategory::New => true,
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
            // the grip on the top edge: drag it to share the screen between bench and shelf
            panel
                .spawn((
                    ShelfGrip,
                    // lit under the pointer like any button, but dragged, never focused
                    theme::button(
                        theme::Kind::Ghost,
                        Node {
                            position_type: PositionType::Absolute,
                            top: Val::Px(-13.0),
                            left: Val::Percent(50.0),
                            margin: UiRect::left(Val::Px(-34.0)),
                            width: Val::Px(68.0),
                            height: Val::Px(26.0),
                            align_items: AlignItems::Center,
                            justify_content: JustifyContent::Center,
                            ..default()
                        },
                        99.0,
                    ),
                    crate::ui::focus::NoFocus,
                    // over the bench's edge as well as the shelf's (under every pop-up)
                    GlobalZIndex(550),
                    Pickable::default(),
                    crate::ui::onboarding::Tip::Text("Resize", "Drag up for a bigger shelf, down for a bigger bench."),
                    Name::new("ShelfGrip"),
                ))
                .observe(grip_drag_start)
                .observe(grip_drag)
                .observe(grip_drag_end)
                .with_children(|g| {
                    g.spawn((
                        Node {
                            width: Val::Px(52.0),
                            height: Val::Px(14.0),
                            border: UiRect::all(Val::Px(1.0)),
                            border_radius: BorderRadius::all(Val::Px(99.0)),
                            align_items: AlignItems::Center,
                            justify_content: JustifyContent::Center,
                            ..default()
                        },
                        BackgroundColor(theme::SURFACE),
                        BorderColor::all(theme::LINE_STRONG),
                        Pickable::IGNORE,
                    ))
                    .with_child((
                        Node {
                            width: Val::Px(26.0),
                            height: Val::Px(3.0),
                            border_radius: BorderRadius::all(Val::Px(99.0)),
                            ..default()
                        },
                        BackgroundColor(theme::TEXT_3),
                        Pickable::IGNORE,
                    ));
                });
            // --- shelf header: title, category, search; the how-to line and Library ---
            panel
                .spawn((
                    ShelfHead,
                    Node {
                        width: Val::Percent(100.0),
                        height: Val::Px(SHELF_HEAD_H),
                        flex_shrink: 0.0,
                        flex_direction: FlexDirection::Row,
                        align_items: AlignItems::Center,
                        column_gap: Val::Px(8.0),
                        padding: UiRect::axes(Val::Px(14.0), Val::Px(4.0)),
                        ..default()
                    },
                    Name::new("InventoryTabs"),
                ))
                .with_children(|bar| {
                    bar.spawn(Node {
                        align_items: AlignItems::Center,
                        flex_shrink: 0.0,
                        column_gap: Val::Px(7.0),
                        ..default()
                    })
                    .with_children(|t| {
                        t.spawn(theme::icon(&assets, "flask", 16.0, theme::CYAN));
                        t.spawn((ShelfTitle, theme::label(&fonts, "SHELF", theme::XS, Weight::Bold, theme::TEXT_2)));
                    });
                    // the category: a dropdown
                    bar.spawn((
                        theme::button(
                            theme::Kind::Secondary,
                            Node {
                                height: Val::Px(34.0),
                                padding: UiRect::new(Val::Px(12.0), Val::Px(9.0), Val::Px(0.0), Val::Px(0.0)),
                                column_gap: Val::Px(7.0),
                                align_items: AlignItems::Center,
                                flex_shrink: 0.0,
                                ..default()
                            },
                            theme::R_MD,
                        ),
                        ShelfCategoryButton,
                        crate::ui::onboarding::Tip::Text(
                            "Show",
                            "Pick which substances the shelf shows, or the newest first.",
                        ),
                    ))
                    .with_children(|b| {
                        b.spawn((
                            ShelfCategoryLabel,
                            theme::label(&fonts, "All", theme::SM, Weight::Semibold, theme::TEXT),
                            TextLayout::no_wrap(),
                            Pickable::IGNORE,
                        ));
                        b.spawn(theme::icon_down(&assets, 12.0, theme::TEXT_2));
                    });
                    // the search: tap to type (a phone's keyboard comes up), the x clears it
                    bar.spawn((
                        theme::button(
                            theme::Kind::Secondary,
                            Node {
                                height: Val::Px(34.0),
                                min_width: Val::Px(110.0),
                                max_width: Val::Px(360.0),
                                flex_grow: 1.0,
                                flex_shrink: 1.0,
                                padding: UiRect::new(Val::Px(10.0), Val::Px(3.0), Val::Px(0.0), Val::Px(0.0)),
                                column_gap: Val::Px(7.0),
                                align_items: AlignItems::Center,
                                ..default()
                            },
                            99.0,
                        ),
                        ShelfSearchBox,
                        crate::ui::onboarding::Tip::Text(
                            "Search the shelf",
                            "Tap and type part of a name or a formula.",
                        ),
                    ))
                    .with_children(|b| {
                        b.spawn(theme::icon(&assets, "search", 14.0, theme::TEXT_3));
                        b.spawn((
                            ShelfSearchText,
                            theme::label(&fonts, "Search", theme::SM, Weight::Regular, theme::TEXT_3),
                            TextLayout::no_wrap(),
                            Node { flex_grow: 1.0, overflow: Overflow::clip(), ..default() },
                            Pickable::IGNORE,
                        ));
                        b.spawn((
                            theme::button(
                                theme::Kind::Ghost,
                                Node {
                                    width: Val::Px(30.0),
                                    height: Val::Px(30.0),
                                    flex_shrink: 0.0,
                                    align_items: AlignItems::Center,
                                    justify_content: JustifyContent::Center,
                                    display: Display::None,
                                    ..default()
                                },
                                99.0,
                            ),
                            ShelfSearchClear,
                            crate::ui::onboarding::Tip::Text("Clear", "Clear the search."),
                        ))
                        .with_children(|x| {
                            x.spawn(theme::icon(&assets, "close", 14.0, theme::TEXT));
                        });
                    });
                    // a phone's keyboard: Done puts it away
                    bar.spawn((
                        theme::button(
                            theme::Kind::Primary,
                            Node {
                                height: Val::Px(34.0),
                                padding: UiRect::horizontal(Val::Px(16.0)),
                                align_items: AlignItems::Center,
                                flex_shrink: 0.0,
                                display: Display::None,
                                ..default()
                            },
                            theme::R_MD,
                        ),
                        ShelfSearchDone,
                    ))
                    .with_children(|d| {
                        d.spawn((
                            theme::label(&fonts, "Done", theme::SM, Weight::Semibold, theme::BG),
                            Pickable::IGNORE,
                        ));
                    });
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
    /// (background, border) for a tile that is hovered and/or selected. The selection is
    /// white (with an outline, see `shelf_selection_outline_system`): no element tile,
    /// whatever its block colour, looks like it.
    pub fn look(&self, hovered: bool, selected: bool) -> (Color, Color) {
        if selected {
            (theme::mix(self.bg, theme::TEXT, 0.12), theme::TEXT)
        } else if hovered {
            (theme::mix(self.bg, theme::TEXT, 0.05), theme::CYAN.with_alpha(0.8))
        } else {
            (self.bg, self.border)
        }
    }
}

pub fn shelf_hover_system(
    mut q: Query<(&Hovered, &ShelfTile, &Ingredient, &mut BorderColor, &mut BackgroundColor), Changed<Hovered>>,
    selected: Res<crate::ui::detail_panel::SelectedSubstance>,
) {
    for (h, tile, ing, mut border, mut bg) in &mut q {
        let (b, c) = tile.look(h.get(), selected.0 == Some(ing.id));
        bg.0 = b;
        *border = BorderColor::all(c);
    }
}

/// The selected tile wears a white outline as well as its white edge (a dragged tile's
/// outline belongs to the drag).
pub fn shelf_selection_outline_system(
    selected: Res<crate::ui::detail_panel::SelectedSubstance>,
    mut tiles: Query<(&Ingredient, &mut Outline), (With<ShelfTile>, Without<DragGhost>)>,
) {
    for (ing, mut outline) in &mut tiles {
        let want = if selected.0 == Some(ing.id) {
            Outline { width: Val::Px(2.0), offset: Val::Px(2.0), color: theme::TEXT }
        } else {
            Outline { width: Val::Px(0.0), offset: Val::Px(0.0), color: Color::NONE }
        };
        if outline.color != want.color || outline.width != want.width {
            *outline = want;
        }
    }
}

/// The shelf's search box: a tap starts typing into it (and brings up a phone's keyboard),
/// another tap, Enter or Esc (see shell::escape_system) stops; the x clears it. Typing
/// letters and digits adds to it, Backspace takes away. With a phone's keyboard up the shelf
/// sits on it (fit_dock_system): a tap on the box brings the keyboard back if it was put
/// away, the x clears and carries on typing, each result tapped goes into the selected
/// vessel (detail_panel), and Done ends it.
#[allow(clippy::too_many_arguments)]
pub fn shelf_search_system(
    keys: Res<ButtonInput<KeyCode>>,
    mut search: ResMut<ShelfSearch>,
    mut typing_box: ResMut<TypingBox>,
    views: (
        Res<crate::ui::codex::CodexState>,
        Res<crate::ui::reaction_library::ReactionLibState>,
        Res<crate::ui::tech_tree::TechTreeState>,
    ),
    pressed: (
        Query<(), (With<Clicked>, With<ShelfSearchBox>)>,
        Query<(), (With<Clicked>, With<ShelfSearchClear>)>,
        Query<(), (With<Clicked>, With<ShelfSearchDone>)>,
    ),
    soft: Res<crate::platform::SoftKeyboard>,
    mut text_q: Query<(&mut Text, &mut TextColor), With<ShelfSearchText>>,
    mut clear_q: Query<&mut Node, (With<ShelfSearchClear>, Without<ShelfSearchDone>)>,
    mut done_q: Query<&mut Node, (With<ShelfSearchDone>, Without<crate::ui::detail_panel::SelectionOpenButton>)>,
    mut library_q: Query<
        &mut Node,
        (With<crate::ui::detail_panel::SelectionOpenButton>, Without<ShelfSearchDone>, Without<ShelfSearchClear>),
    >,
) {
    let (boxes, clears, done) = pressed;
    if !done.is_empty() {
        search.typing = false;
    } else if !clears.is_empty() {
        search.text.clear();
        search.typing = soft.0 && search.typing;
        if search.typing {
            crate::platform::keyboard_show("");
        }
    } else if !boxes.is_empty() {
        search.typing = (soft.0 && search.typing) || !search.typing;
        if search.typing {
            crate::platform::keyboard_show(&search.text);
        }
    }
    let (codex, rlib, tree) = views;
    if search.typing && (codex.open || rlib.open || tree.open) {
        search.typing = false;
    }
    if search.typing {
        let (text, enter) = crate::ui::codex::typed(&search.text, &keys, crate::platform::keyboard_text());
        if enter {
            search.typing = false;
        }
        if text != search.text {
            search.text = text;
        }
    }
    // the on-screen keyboard follows the box it is typing for
    let want = if search.typing {
        TypingBox::Shelf
    } else if *typing_box == TypingBox::Shelf {
        TypingBox::None
    } else {
        *typing_box
    };
    if *typing_box != want {
        if want == TypingBox::None {
            crate::platform::keyboard_hide();
        }
        *typing_box = want;
    }
    if !(search.is_changed() || soft.is_changed()) {
        return;
    }
    // on a phone's keyboard Done takes the Library button's place
    let on_keys = soft.0 && search.typing;
    if let Ok(mut n) = done_q.single_mut() {
        let d = if on_keys { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if let Ok(mut n) = library_q.single_mut() {
        let d = if on_keys { Display::None } else { Display::Flex };
        if n.display != d {
            n.display = d;
        }
    }
    if let Ok((mut t, mut c)) = text_q.single_mut() {
        let (text, color) = match (search.typing, search.text.is_empty()) {
            (true, _) => (format!("{}|", search.text), theme::TEXT),
            (false, true) => ("Search".to_string(), theme::TEXT_3),
            (false, false) => (search.text.clone(), theme::TEXT),
        };
        t.0 = text;
        c.0 = color;
    }
    if let Ok(mut n) = clear_q.single_mut() {
        let d = if search.text.is_empty() { Display::None } else { Display::Flex };
        if n.display != d {
            n.display = d;
        }
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
    mut cat_label: Query<&mut Text, (With<ShelfCategoryLabel>, Without<ShelfTitle>)>,
    settings: Option<Res<crate::ui::settings::Settings>>,
    mut scroll_q: Query<&mut ScrollPosition, With<InventoryScroll>>,
    progress: Res<PlayerProgress>,
    filter: Res<InvCategory>,
    recipe_db: Option<Res<crate::resources::recipe_database::RecipeDatabase>>,
    dragging: Query<(), With<DragGhost>>,
    narrowing: (Res<ShelfSearch>, Res<crate::ui::hint::HintState>),
    mut title_q: Query<(&mut Text, &mut TextColor), (With<ShelfTitle>, Without<ShelfCategoryLabel>)>,
    mut layout: Local<Option<(InvCategory, bool, String, Option<u32>)>>,
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
    // while a target is chosen the shelf is its kit (unless the kit is switched off)
    let (search, hint) = narrowing;
    let kit = hint.shelf_kit(settings.as_deref());
    let kit_ids: Option<std::collections::HashSet<u32>> = kit.map(|k| k.shelf().collect());
    let key = (*filter, names_first, search.text.trim().to_lowercase(), kit.map(|k| k.target));
    let rebuild = layout.as_ref() != Some(&key);
    // newest first: a discovery goes to the front, so the list is laid out again
    let reorder = *filter == InvCategory::New && progress.is_changed();
    if !(rebuild || reorder || progress.is_changed() || *pending) {
        return;
    }
    let Ok(mut list) = content_query.single_mut() else {
        return;
    };

    let mut items: Vec<_> = substances
        .0
        .values()
        .filter(|s| {
            // a transient is used the moment it is made: there's nothing to keep
            progress.discovered.contains(&s.id)
                && !s.is_transient()
                && matches_category(s, *filter)
                && search.matches(s)
                && kit_ids.as_ref().is_none_or(|k| k.contains(&s.id))
        })
        .collect();
    if *filter == InvCategory::New {
        let rank = progress.recency();
        items.sort_by_key(|s| (std::cmp::Reverse(rank.get(&s.id).copied().unwrap_or(0)), shelf_key(s)));
    } else {
        items.sort_by_key(|s| shelf_key(s));
    }
    if let Ok((mut t, mut c)) = title_q.single_mut() {
        let (text, color) = if kit.is_some() { ("KIT", theme::GOLD) } else { ("SHELF", theme::TEXT_2) };
        if t.0 != text {
            t.0 = text.to_string();
            c.0 = color;
        }
    }
    let ids: Vec<u32> = items.iter().map(|s| s.id).collect();
    let wanted: std::collections::HashSet<u32> = ids.iter().copied().collect();
    let gone = list.ids().iter().any(|id| !wanted.contains(id));

    // Removing tiles (a new game) or rebuilding despawns tiles, possibly one being
    // dragged: its drag would never end. Hold off until the drag is over.
    if (rebuild || reorder || gone) && !dragging.is_empty() {
        *pending = true;
        return;
    }
    *pending = false;

    if rebuild || reorder {
        // A new category, search or kit: jump back to the top so a short list doesn't open
        // parked below its content.
        if layout.as_ref().is_some_and(|l| l.0 != key.0 || l.2 != key.2 || l.3 != key.3) {
            for mut sp in &mut scroll_q {
                sp.0.y = 0.0;
            }
        }
        // laid out again because a discovery jumped the queue: the newcomers still pop in
        let had: std::collections::HashSet<u32> =
            if reorder && !rebuild { list.ids().iter().copied().collect() } else { Default::default() };
        *layout = Some(key);
        for (tab, mut skin) in &mut tabs {
            let active = tab.0 == *filter;
            if skin.active != active {
                skin.active = active;
            }
        }
        if let Ok(mut t) = cat_label.single_mut() {
            let words = if *filter == InvCategory::New { "Newest" } else { filter.label() };
            if t.0 != words {
                t.0 = words.to_string();
            }
        }
        for e in list.clear() {
            commands.entity(e).despawn();
        }
        let fresh: Vec<u32> =
            if had.is_empty() { Vec::new() } else { ids.iter().copied().filter(|id| !had.contains(id)).collect() };
        list.set(ids, fresh);
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
    busy: Query<(), (With<ShelfTile>, Or<(With<DragGhost>, With<Swiping>)>)>,
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
    // a tile being dragged, swiped or focused stays built wherever it scrolls to
    let keep = |e: Entity| Some(e) == focused || busy.contains(e);
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
    // an element's block colour is in its tint and its symbol; its edge stays neutral like
    // every other tile's, so only the selection ever has a lit edge
    let (bg, border) = match block {
        Some(c) => (theme::mix(theme::RAISED, c, 0.10), theme::LINE),
        None => (theme::RAISED, theme::LINE),
    };
    commands
        .spawn((
            ingredient,
            Draggable,
            ShelfTile { border, bg },
            crate::ui::onboarding::Tip::Substance(sub.id),
            Hovered::default(),
            Node {
                border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
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
                        TextFont { font: fonts.main.clone().into(), font_size: FontSize::Px(11.0), ..default() },
                        TextColor(theme::TEXT_2),
                        Node { max_width: Val::Px(80.0), ..default() },
                        Pickable::IGNORE,
                    ));
                } else {
                    item.spawn((
                        Text::new(label),
                        TextFont { font: fonts.semibold.clone().into(), font_size: FontSize::Px(size), ..default() },
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

/// Left on a node whose pop-in has played (the checks read it: a pop can come and go
/// between two slow frames).
#[derive(Component)]
pub struct Popped;

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
    mut glows: Query<(Entity, &mut NewGlow, &ShelfTile, &mut BorderColor, &Hovered)>,
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
            commands.entity(e).try_remove::<PopIn>().try_insert(Popped);
        }
    }
    for (e, mut g, tile, mut border, hovered) in &mut glows {
        g.t += dt;
        let a = (1.0 - g.t / GLOW_SECS).clamp(0.0, 1.0);
        if !hovered.get() {
            *border = BorderColor::all(theme::mix(tile.border, theme::GREEN, a));
        }
        if a <= 0.0 {
            commands.entity(e).try_remove::<NewGlow>();
        }
    }
}

/// Clicking a category tab sets the active filter.
pub fn category_tab_system(
    clicked: Query<&CategoryTab, (With<Clicked>, With<Button>)>,
    mut filter: ResMut<InvCategory>,
) {
    for tab in &clicked {
        if *filter != tab.0 {
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

/// A chip's picture (the bench's overview leaves it out).
#[derive(Component)]
pub struct ChipIcon;
/// A chip's formula line (larger in the bench's overview).
#[derive(Component)]
pub struct ChipFormulaText;
/// A chip's name line (the bench's overview leaves it out).
#[derive(Component)]
pub struct ChipNameText;

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
        Node {
            border_radius: BorderRadius::all(Val::Px(theme::R_SM)),
            width: Val::Percent(100.0),
            min_height: Val::Px(34.0),
            align_items: AlignItems::Center,
            column_gap: Val::Px(7.0),
            padding: UiRect::new(Val::Px(4.0), Val::Px(6.0), Val::Px(2.0), Val::Px(2.0)),
            border: UiRect::new(Val::Px(3.0), Val::Px(1.0), Val::Px(1.0), Val::Px(1.0)),
            ..default()
        },
        BackgroundColor(theme::mix(theme::RAISED, accent, 0.10)),
        BorderColor {
            left: accent,
            top: accent.with_alpha(0.3),
            right: accent.with_alpha(0.3),
            bottom: accent.with_alpha(0.3),
        },
        Name::new(format!("Chip-{}", ing.name)),
    ));
    // drag a chip out to take it back, or onto another vessel to move it; a transient can't
    // be kept or carried by hand, and breaks down unless something uses it at once
    if ing.is_transient() {
        chip_cmd.insert(crate::systems::reaction_check::Decay::default());
    } else {
        chip_cmd.insert(Draggable);
    }
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
                ChipIcon,
                Node {
                    border_radius: BorderRadius::all(Val::Px(5.0)),
                    width: Val::Px(28.0),
                    height: Val::Px(28.0),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    ..default()
                },
                BackgroundColor(theme::mix(theme::RAISED, element_tile_color(&ing.formula), 0.15)),
                Pickable::IGNORE,
            ))
            .with_children(|t| {
                t.spawn((
                    Text::new(element_symbol(&ing.formula).unwrap_or_default()),
                    TextFont { font: fonts.semibold.clone().into(), font_size: FontSize::Px(14.0), ..default() },
                    TextColor(element_tile_color(&ing.formula)),
                    Pickable::IGNORE,
                ));
            });
        } else {
            chip.spawn((
                ChipIcon,
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
                    ChipFormulaText,
                    Text::new(formula),
                    TextFont { font: fonts.semibold.clone().into(), font_size: FontSize::Px(13.0), ..default() },
                    TextColor(theme::TEXT),
                    Pickable::IGNORE,
                ));
                col.spawn((
                    ChipNameText,
                    Text::new(ing.name.clone()),
                    TextFont { font: fonts.main.clone().into(), font_size: FontSize::Px(theme::XS), ..default() },
                    TextColor(theme::TEXT),
                    Node { max_width: Val::Px(130.0), ..default() },
                    Pickable::IGNORE,
                ));
            });
    });
    chip_cmd.id()
}
