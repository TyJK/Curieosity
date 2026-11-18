// src/ui/codex.rs
//
// The Substance Library: every substance the player has discovered, searchable and
// filterable on the left; on the right, its page: structure (or Bohr model), formula,
// state and tags, the description, physical data, what industry does with it (how much is
// made, how it travels and is kept, the grades it sells at), the known reactions that make it
// and use it (click one to open it in the Reaction Library), and its references.
use crate::ui::{Button, Clicked};
use bevy::prelude::*;
use bevy::ui::Pressed;
use bevy::ui::ScrollPosition;

use crate::components::format_formula;
use crate::data::common::{handling, un_class_name, MatterState, Property};
use crate::data::reactions::Reaction;
use crate::data::substances::{Substance, Substances};
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::inventory::{element_tile_color, is_element_formula, matches_category, short, InvCategory};
use crate::ui::process_toolbar::{vessel_art_path, vessel_name};
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::ui::virtual_list::VirtualList;
use crate::GameData;

#[derive(Resource, Default)]
pub struct CodexState {
    pub open: bool,
    pub selected: Option<u32>,
}

#[derive(Resource, Default)]
pub struct CodexFilter {
    pub category: InvCategory,
    pub search: String,
}

const CODEX_TABS: [(InvCategory, &str); 10] = [
    (InvCategory::All, "All"),
    (InvCategory::Elements, "Elements"),
    (InvCategory::Compounds, "Compounds"),
    (InvCategory::Acids, "Acids"),
    (InvCategory::Bases, "Bases"),
    (InvCategory::Metals, "Metals"),
    (InvCategory::Gas, "Gas"),
    (InvCategory::Liquid, "Liquid"),
    (InvCategory::Solid, "Solid"),
    (InvCategory::Coming, "Coming later"),
];

const LIST_W: f32 = 380.0;

#[derive(Component)]
pub struct CodexCloseButton;
#[derive(Component)]
pub struct CodexRoot;
#[derive(Component)]
pub struct CodexScrollable {
    pub is_left: bool,
}
#[derive(Component)]
pub struct CodexListContent;
/// The "Text: Wikipedia, CC BY-SA 4.0." line under a page's text.
#[derive(Component)]
pub struct CodexTextCredit;
/// One card of a page's "In industry" section.
#[derive(Component)]
pub struct CodexIndustryCard;
#[derive(Component)]
pub struct CodexDetail;
#[derive(Component)]
pub struct CodexCategoryTab(pub InvCategory);
#[derive(Component)]
pub struct CodexSearchText;
/// The search field (a tap brings up a phone's keyboard).
#[derive(Component)]
pub struct CodexSearchBox;
#[derive(Component)]
pub struct CodexCountText;
#[derive(Component)]
pub struct CodexEntry(pub u32);

/// "Nothing matches yet.", under the list (outside it: the list's children are its rows).
#[derive(Component)]
pub struct CodexEmptyText;

/// A list row's height (one line of name, one of formula, beside a 36 px picture), and the
/// gap between rows. Rows are one fixed height so the list can build only those in sight.
const ROW_H: f32 = 48.0;
const ROW_GAP: f32 = 4.0;
#[derive(Component)]
pub struct CodexRefLink(pub String);
/// A reaction row on a substance page: opens it in the Reaction Library.
#[derive(Component)]
pub struct CodexReactionLink(pub u32);

// Links open through the platform layer (a browser command on a desktop, an intent on
// Android); the review run's URL sink lives there too.
pub use crate::platform::{open_url, URL_SINK};

fn state_name(s: MatterState) -> &'static str {
    match s {
        MatterState::Solid => "Solid",
        MatterState::Liquid => "Liquid",
        MatterState::Gas => "Gas",
        MatterState::Plasma => "Plasma",
        MatterState::Aqueous => "In solution",
        MatterState::SupercriticalFluid => "Supercritical",
    }
}

fn state_color(s: MatterState) -> Color {
    match s {
        MatterState::Solid => Color::srgb(0.80, 0.78, 0.95),
        MatterState::Liquid | MatterState::Aqueous => Color::srgb(0.40, 0.72, 1.0),
        MatterState::Gas => Color::srgb(0.70, 0.92, 0.95),
        _ => theme::VIOLET,
    }
}

/// (label, value) cards for a substance's physical data.
fn facts(sub: &Substance) -> Vec<(&'static str, String)> {
    let mut f = Vec::new();
    if let Some(ei) = &sub.element_info {
        f.push(("Atomic number", ei.atomic_number.to_string()));
        f.push(("Atomic weight", format!("{:.4}", ei.atomic_weight)));
        if let Some(g) = ei.group {
            f.push(("Group", g.to_string()));
        }
        if let Some(p) = ei.period {
            f.push(("Period", p.to_string()));
        }
        if let Some(b) = &ei.block {
            f.push(("Block", b.clone()));
        }
        if let Some(ec) = &ei.electron_config {
            f.push(("Configuration", ec.clone()));
        }
        if let Some(en) = ei.electronegativity_pauling {
            f.push(("Electronegativity", format!("{:.2}", en)));
        }
        if let Some(i) = ei.first_ionization_kj_mol {
            f.push(("1st ionisation", format!("{:.0} kJ/mol", i)));
        }
        if let Some(r) = ei.atomic_radius_pm {
            f.push(("Atomic radius", format!("{:.0} pm", r)));
        }
        if let Some(d) = &ei.discoverer {
            f.push(("Discovered by", d.clone()));
        }
        if let Some(y) = ei.discovery_year {
            f.push(("Discovered", y.to_string()));
        }
    } else if sub.molar_mass_g_mol > 0.0 {
        f.push(("Molar mass", format!("{:.2} g/mol", sub.molar_mass_g_mol)));
    }
    if let Some(mp) = sub.melting_point_c {
        f.push(("Melts at", format!("{:.0} °C", mp)));
    }
    if let Some(bp) = sub.boiling_point_c {
        f.push(("Boils at", format!("{:.0} °C", bp)));
    }
    if let Some(d) = sub.density_g_cm3 {
        f.push(("Density", format!("{:.2} g/cm³", d)));
    }
    if let Some(s) = sub.solubility_g_per_100ml_h2o {
        f.push(("Solubility", format!("{:.1} g/100 mL", s)));
    }
    if let Some(h) = sub.enthalpy_formation_kj_mol {
        f.push(("ΔHf°", format!("{:.0} kJ/mol", h)));
    }
    if let Some(a) = &sub.appearance {
        f.push(("Appearance", a.clone()));
    }
    f
}

/// The name a chemical index files a substance under: leading locants, stereo descriptors and
/// position prefixes don't count, so "(+)-Glaucine" sits under G, "1,4-Dioxane" under D,
/// "L-Lysine" under L and "p-Xylene" under X.
pub fn index_name(name: &str) -> String {
    let lower = name.to_lowercase();
    let mut s = lower.as_str();
    loop {
        let t = s.trim_start_matches(|c: char| !c.is_alphabetic());
        let next = match t.find('-') {
            Some(i) if is_name_prefix(&t[..i]) => &t[i + 1..],
            _ => t,
        };
        if next.len() == s.len() || next.is_empty() {
            break;
        }
        s = next;
    }
    if s.chars().any(char::is_alphabetic) {
        s.to_string()
    } else {
        lower.clone()
    }
}

/// A prefix an index skips: tert-, cis-, or locants and descriptors such as N,N'-, 2R,3S-, D-, α-.
fn is_name_prefix(p: &str) -> bool {
    if matches!(p, "tert" | "sec" | "cis" | "trans" | "exo" | "endo" | "meso" | "rac") {
        return true;
    }
    let p: String = p.chars().filter(|c| !matches!(c, '(' | ')' | '[' | ']')).collect();
    !p.is_empty()
        && p.split(',').all(|part| {
            let letters = part.chars().filter(|c| c.is_alphabetic()).count();
            !part.is_empty()
                && part.chars().count() <= 3
                && letters <= 1
                && part.chars().all(|c| c.is_alphanumeric() || matches!(c, '\'' | '′' | '+' | '±' | '−'))
        })
}

/// A yearly tonnage, rounded the way people say it ("47.6 million t").
fn tonnes(t: f32) -> String {
    if t >= 1.0e9 {
        format!("{:.1} billion t", t / 1.0e9)
    } else if t >= 1.0e6 {
        format!("{:.1} million t", t / 1.0e6)
    } else if t >= 1.0e4 {
        format!("{:.0} thousand t", t / 1.0e3)
    } else {
        format!("{:.0} t", t)
    }
}

/// A rough world tonnage, at two significant figures ("270 million t", "3,300 t").
fn rough_tonnes(t: f32) -> String {
    let (v, unit) = if t >= 1.0e12 {
        (t / 1.0e12, " trillion t")
    } else if t >= 1.0e9 {
        (t / 1.0e9, " billion t")
    } else if t >= 1.0e6 {
        (t / 1.0e6, " million t")
    } else {
        (t, " t")
    };
    let two = if v >= 100.0 {
        format!("{:.0}", (v / 10.0).round() * 10.0)
    } else if v >= 10.0 {
        format!("{:.0}", v)
    } else {
        format!("{:.1}", v).trim_end_matches(".0").to_string()
    };
    if unit == " t" && v >= 1000.0 {
        // thousands separators for the small totals (precious metals)
        let n = v.round() as u64;
        return format!("{},{:03} t", n / 1000, n % 1000);
    }
    format!("{two}{unit}")
}

/// (label, value) cards for what industry does with a substance: how much is made, how it
/// travels and is kept, and the stricter grades it also sells at. Empty for substances
/// industry doesn't trade in.
fn industry(sub: &Substance) -> Vec<(&'static str, String)> {
    let mut f = Vec::new();
    if let Some(t) = sub.world_t_year {
        f.push(("Made a year (world)", format!("about {}", rough_tonnes(t))));
    }
    if let Some(t) = sub.production_t_year {
        f.push(("Made a year (US)", tonnes(t)));
    }
    let class = sub.transport_class();
    if let Some(c) = class {
        f.push(("Transport", format!("UN class {} · {}", c, un_class_name(c).unwrap_or("Dangerous goods"))));
    }
    if !f.is_empty() {
        f.push(("Handling", handling(sub.state, class).to_string()));
    }
    if !sub.grades.is_empty() {
        let grades: Vec<&str> = sub.grades.iter().map(|g| g.label()).collect();
        f.push(("Also sold as", format!("{} grade", grades.join(", "))));
    }
    f
}

/// Under the industry cards when a tonnage shows: what the figure is.
const PRODUCTION_NOTE: &str = "US figures: the production and imports reported to regulators, \
often the low end of a reporting band.";

/// Under the industry cards when a world figure shows.
const WORLD_NOTE: &str = "World figures are rough estimates, rounded: totals this big are too large to \
track precisely.";

/// A wrapping grid of (label, value) cards; the industry ones carry `CodexIndustryCard`.
fn spawn_fact_grid(p: &mut ChildSpawnerCommands, fonts: &UiFonts, facts: Vec<(&'static str, String)>, industry: bool) {
    p.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(10.0), row_gap: Val::Px(10.0), ..default() })
        .with_children(|grid| {
            for (k, v) in facts {
                grid.spawn((
                    Node {
                        border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                        min_width: Val::Px(150.0),
                        max_width: Val::Px(320.0),
                        flex_direction: FlexDirection::Column,
                        row_gap: Val::Px(2.0),
                        padding: UiRect::axes(Val::Px(12.0), Val::Px(9.0)),
                        border: UiRect::all(Val::Px(1.0)),
                        ..default()
                    },
                    BackgroundColor(theme::RAISED),
                    BorderColor::all(theme::LINE),
                ))
                .insert_if(CodexIndustryCard, || industry)
                .with_children(|c| {
                    c.spawn(theme::label(fonts, k.to_uppercase(), 10.0, Weight::Bold, theme::TEXT_3));
                    c.spawn(theme::para(fonts, v, theme::MD, theme::TEXT, Val::Px(296.0)));
                });
            }
        });
}

/// Shown under every medicine's story: the game teaches how medicines are made, not how to use them.
const MEDICINE_NOTE: &str = "Medicines are shown here for how they are made and what they do. Real medicines \
are made under licence to strict purity standards, and taken only as a doctor or pharmacist directs.";

/// Shown under a transient: why it isn't on the shelf, and how it is used.
const TRANSIENT_NOTE: &str = "This doesn't keep: it is made and used at once, so it never goes on the \
shelf. Link the vessel that makes it to the one that uses it (drag or tap from the first one's output port \
to the second vessel), put the other ingredients in that second vessel, and react the first: it flows \
straight across. Left where it was made, it breaks down.";

/// Shown under a class of compounds: why its formula is one member's.
const CLASS_NOTE: &str = "A family of closely related compounds, made and used as one. \
The formula and structure shown are a typical member's.";

fn tags(sub: &Substance) -> Vec<(&'static str, Color)> {
    let mut t = Vec::new();
    for p in &sub.properties {
        match p {
            Property::IsAcid => t.push(("Acid", theme::GOLD)),
            Property::IsBase => t.push(("Base", Color::srgb(0.55, 0.75, 1.0))),
            Property::IsMetal if sub.element_info.is_some() || is_element_formula(&sub.formula) => {
                t.push(("Metal", Color::srgb(0.80, 0.82, 0.90)))
            }
            Property::IsRadioactive => t.push(("Radioactive", theme::GREEN)),
            Property::IsPolymer => t.push(("Polymer", Color::srgb(1.0, 0.5, 0.8))),
            Property::IsMonomer => t.push(("Monomer", Color::srgb(1.0, 0.65, 0.85))),
            Property::IsMedicine => t.push(("Medicine", Color::srgb(0.45, 0.90, 0.80))),
            Property::IsClass => t.push(("Class", Color::srgb(0.75, 0.70, 1.0))),
            Property::IsTransient => t.push(("Used at once", Color::srgb(1.0, 0.55, 0.35))),
            _ => {}
        }
    }
    t
}

pub fn spawn_codex(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((CodexRoot, crate::ui::shell::SplitRoot, theme::view_root(600), Name::new("CodexRoot")))
        .insert(Node {
            position_type: PositionType::Absolute,
            left: Val::Px(0.0),
            right: Val::Px(0.0),
            top: Val::Px(theme::HEADER_H),
            bottom: Val::Px(0.0),
            flex_direction: FlexDirection::Row,
            display: Display::None,
            ..default()
        })
        .with_children(|root| {
            // --- left column: header, search, categories, list ---
            root.spawn((
                crate::ui::shell::SplitList(LIST_W),
                Node {
                    width: Val::Px(LIST_W),
                    min_width: Val::Px(LIST_W),
                    flex_shrink: 0.0,
                    height: Val::Percent(100.0),
                    flex_direction: FlexDirection::Column,
                    padding: UiRect::new(Val::Px(16.0), Val::Px(12.0), Val::Px(14.0), Val::Px(0.0)),
                    row_gap: Val::Px(10.0),
                    border: UiRect::right(Val::Px(1.0)),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE),
            ))
            .with_children(|col| {
                col.spawn(Node {
                    justify_content: JustifyContent::SpaceBetween,
                    align_items: AlignItems::Center,
                    flex_shrink: 0.0,
                    ..default()
                })
                .with_children(|hdr| {
                    hdr.spawn(Node { flex_direction: FlexDirection::Column, ..default() }).with_children(|t| {
                        t.spawn(theme::label(fonts, "Substance Library", theme::XL, Weight::Semibold, theme::TEXT));
                        t.spawn((CodexCountText, theme::label(fonts, "", theme::XS, Weight::Regular, theme::TEXT_3)));
                    });
                    theme::spawn_icon_button(hdr, assets, "close", 32.0, theme::TEXT_2, CodexCloseButton);
                });
                // search field (type anywhere while the library is open; on a phone, tap it
                // for the keyboard)
                col.spawn((
                    theme::button(
                        Kind::Secondary,
                        Node {
                            height: Val::Px(38.0),
                            flex_shrink: 0.0,
                            align_items: AlignItems::Center,
                            column_gap: Val::Px(9.0),
                            padding: UiRect::horizontal(Val::Px(11.0)),
                            ..default()
                        },
                        theme::R_MD,
                    ),
                    CodexSearchBox,
                ))
                .with_children(|s| {
                    s.spawn(theme::icon(assets, "search", 16.0, theme::TEXT_3));
                    s.spawn((
                        CodexSearchText,
                        theme::label(fonts, search_prompt(), theme::SM, Weight::Regular, theme::TEXT_3),
                    ));
                });
                col.spawn(Node {
                    flex_wrap: FlexWrap::Wrap,
                    column_gap: Val::Px(5.0),
                    row_gap: Val::Px(5.0),
                    flex_shrink: 0.0,
                    ..default()
                })
                .with_children(|bar| {
                    for (cat, label) in CODEX_TABS {
                        bar.spawn((
                            theme::button(
                                Kind::Tab,
                                Node {
                                    height: Val::Px(24.0),
                                    padding: UiRect::horizontal(Val::Px(10.0)),
                                    align_items: AlignItems::Center,
                                    ..default()
                                },
                                99.0,
                            ),
                            CodexCategoryTab(cat),
                        ))
                        .with_children(|b| {
                            b.spawn((
                                theme::label(fonts, label, 11.5, Weight::Semibold, theme::TEXT),
                                Pickable::IGNORE,
                            ));
                        });
                    }
                });
                col.spawn((
                    CodexScrollable { is_left: true },
                    ScrollPosition::default(),
                    Node {
                        flex_grow: 1.0,
                        flex_basis: Val::Px(0.0),
                        min_height: Val::Px(0.0),
                        overflow: Overflow::scroll_y(),
                        padding: UiRect::bottom(Val::Px(12.0)),
                        ..default()
                    },
                ))
                .with_children(|scroll| {
                    scroll.spawn((
                        CodexListContent,
                        VirtualList::new(Vec2::new(0.0, ROW_H), Vec2::new(0.0, ROW_GAP)),
                        Node { width: Val::Percent(100.0), height: Val::Px(0.0), flex_shrink: 0.0, ..default() },
                    ));
                    scroll.spawn((
                        CodexEmptyText,
                        theme::label(fonts, "Nothing matches yet.", theme::SM, Weight::Regular, theme::TEXT_3),
                        Node { display: Display::None, ..default() },
                    ));
                });
            });
            // --- right column: the substance page ---
            root.spawn((
                crate::ui::shell::SplitPane,
                CodexScrollable { is_left: false },
                ScrollPosition::default(),
                Node {
                    flex_grow: 1.0,
                    height: Val::Percent(100.0),
                    overflow: Overflow::scroll_y(),
                    padding: UiRect::new(Val::Px(32.0), Val::Px(32.0), Val::Px(26.0), Val::Px(40.0)),
                    ..default()
                },
            ))
            .with_children(|pane| {
                pane.spawn((
                    CodexDetail,
                    Node {
                        width: Val::Percent(100.0),
                        max_width: Val::Px(980.0),
                        flex_direction: FlexDirection::Column,
                        row_gap: Val::Px(14.0),
                        ..default()
                    },
                ));
            });
        });
}

/// Show/hide the library; the close button returns to the lab.
pub fn codex_button_system(
    closes: Query<(), (With<Clicked>, With<CodexCloseButton>)>,
    mut state: ResMut<CodexState>,
    mut root_q: Query<&mut Node, With<CodexRoot>>,
) {
    if !closes.is_empty() {
        state.open = false;
    }
    if let Ok(mut node) = root_q.single_mut() {
        let d = if state.open { Display::Flex } else { Display::None };
        if node.display != d {
            node.display = d;
        }
    }
}

// --- list ---------------------------------------------------------------------------------
pub fn populate_codex_list_system(
    state: Res<CodexState>,
    filter: Res<CodexFilter>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    progress: Res<PlayerProgress>,
    mut list_q: Query<&mut VirtualList, With<CodexListContent>>,
    mut empty_q: Query<&mut Node, With<CodexEmptyText>>,
    mut tabs: Query<(&CodexCategoryTab, &mut Skin)>,
    mut rows: Query<(&CodexEntry, &mut Skin), Without<CodexCategoryTab>>,
    mut count_q: Query<&mut Text, With<CodexCountText>>,
    mut list_scroll: Query<(&CodexScrollable, &mut ScrollPosition)>,
    mut prev_open: Local<bool>,
) {
    let just_opened = state.open && !*prev_open;
    *prev_open = state.open;
    // keep the selection highlight current without rebuilding the list
    if state.is_changed() {
        for (e, mut skin) in &mut rows {
            let a = Some(e.0) == state.selected;
            if skin.active != a {
                skin.active = a;
            }
        }
    }
    let should = state.open && (just_opened || progress.is_changed() || filter.is_changed());
    if !should {
        return;
    }
    let Some(subs) = substances_assets.get(&game_data.substances) else {
        return;
    };
    let Ok(mut list) = list_q.single_mut() else {
        return;
    };

    if just_opened || filter.is_changed() {
        for (marker, mut sp) in &mut list_scroll {
            if marker.is_left {
                sp.0.y = 0.0;
            }
        }
    }
    for (tab, mut skin) in &mut tabs {
        let a = tab.0 == filter.category;
        if skin.active != a {
            skin.active = a;
        }
    }

    let q = filter.search.to_lowercase();
    // "Coming later" lists the locked previews of later stages; every other tab, what has been found
    let coming = filter.category == InvCategory::Coming;
    let mut items: Vec<&Substance> = subs
        .0
        .values()
        .filter(|s| {
            (if coming { s.stage.is_some() } else { progress.discovered.contains(&s.id) })
                && matches_category(s, filter.category)
                && (q.is_empty() || s.name.to_lowercase().contains(&q) || s.formula.to_lowercase().contains(&q))
        })
        .collect();
    // elements by atomic number, then everything else as a chemical index files it
    items.sort_by_cached_key(|s| match &s.element_info {
        Some(e) => (0u8, e.atomic_number, String::new(), String::new()),
        None => (1, 0, index_name(&s.name), s.name.to_lowercase()),
    });
    if let Ok(mut t) = count_q.single_mut() {
        t.0 = if coming {
            let total = subs.0.values().filter(|s| s.stage.is_some()).count();
            format!("{} of {} coming in later stages shown", items.len(), total)
        } else {
            format!("{} of {} discovered shown", items.len(), progress.discovered.len())
        };
    }

    if let Ok(mut node) = empty_q.single_mut() {
        let d = if items.is_empty() { Display::Flex } else { Display::None };
        if node.display != d {
            node.display = d;
        }
    }
    list.set(items.iter().map(|s| s.id).collect(), []);
}

/// Builds the list rows in sight (and a screen either side) and drops the rest; a closed
/// library builds none and lets go of its pictures. Cheap when nothing moved.
#[allow(clippy::too_many_arguments, clippy::type_complexity)]
pub fn codex_window_system(
    mut commands: Commands,
    state: Res<CodexState>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    focus: Option<Res<crate::ui::focus::KeyFocus>>,
    mut content_q: Query<(Entity, &mut VirtualList, &mut Node, &ComputedNode), With<CodexListContent>>,
    scroll_q: Query<(&CodexScrollable, &ComputedNode, &ScrollPosition)>,
    mut rows: Query<&mut Node, (With<CodexEntry>, Without<CodexListContent>)>,
    pressed: Query<(), (With<CodexEntry>, Or<(With<Pressed>, With<Clicked>)>)>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
) {
    let Ok((content, mut list, mut node, cn)) = content_q.single_mut() else {
        return;
    };
    let Some((_, view, scroll)) = scroll_q.iter().find(|(m, _, _)| m.is_left) else {
        return;
    };
    let Some(subs) = substances_assets.get(&game_data.substances) else {
        return;
    };
    let focused = focus.and_then(|f| f.entity);
    let keep = |e: Entity| Some(e) == focused || pressed.contains(e);
    let (width, view_h) = if state.open {
        (cn.size.x * cn.inverse_scale_factor(), view.size.y * view.inverse_scale_factor())
    } else {
        (0.0, 0.0)
    };
    let Some(pass) = list.plan(width, view_h, scroll.0.y, keep) else {
        return;
    };
    if state.open && node.height != Val::Px(pass.height) {
        node.height = Val::Px(pass.height);
    }
    for e in &pass.drop {
        commands.entity(*e).despawn();
    }
    for (e, at) in &pass.moves {
        if let Ok(mut n) = rows.get_mut(*e) {
            n.top = Val::Px(at.y);
        }
    }
    for (id, at, _) in &pass.build {
        let Some(sub) = subs.0.get(id) else { continue };
        let e = spawn_codex_row(&mut commands, sub, Some(sub.id) == state.selected, at.y, &fonts, &assets);
        list.record(*id, e, *at);
    }
    if !pass.build.is_empty() || !pass.drop.is_empty() {
        commands.entity(content).replace_children(&list.order());
    }
}

/// One list row, not yet parented, `top` pixels down the list: picture, name, formula.
fn spawn_codex_row(
    commands: &mut Commands,
    sub: &Substance,
    selected: bool,
    top: f32,
    fonts: &UiFonts,
    assets: &AssetServer,
) -> Entity {
    let mut row = commands.spawn((
        theme::button(
            Kind::Row,
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(top),
                height: Val::Px(ROW_H),
                align_items: AlignItems::Center,
                column_gap: Val::Px(10.0),
                padding: UiRect::axes(Val::Px(8.0), Val::Px(6.0)),
                ..default()
            },
            theme::R_MD,
        ),
        CodexEntry(sub.id),
    ));
    if selected {
        row.insert(Skin::active(Kind::Row, true));
    }
    row.with_children(|row| {
        spawn_thumb(row, fonts, assets, sub, 36.0);
        // one line each, so every row is the same height; the page shows the full name
        row.spawn((
            Node {
                flex_direction: FlexDirection::Column,
                flex_shrink: 1.0,
                min_width: Val::Px(0.0),
                overflow: Overflow::clip(),
                ..default()
            },
            Pickable::IGNORE,
        ))
        .with_children(|c| {
            c.spawn((
                theme::label(fonts, short(&sub.name, 40), theme::SM, Weight::Semibold, theme::TEXT),
                TextLayout::no_wrap(),
                Pickable::IGNORE,
            ));
            c.spawn((
                theme::label(fonts, format_formula(&sub.formula), theme::XS, Weight::Regular, theme::CYAN),
                TextLayout::no_wrap(),
                Pickable::IGNORE,
            ));
        });
    });
    row.id()
}

/// A small picture of a substance: its element symbol in block colour, or its structure.
fn spawn_thumb(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer, sub: &Substance, size: f32) {
    if sub.element_info.is_some() || is_element_formula(&sub.formula) {
        let c = element_tile_color(&sub.formula);
        parent
            .spawn((
                Node {
                    border_radius: BorderRadius::all(Val::Px(theme::R_SM)),
                    width: Val::Px(size),
                    height: Val::Px(size),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    flex_shrink: 0.0,
                    border: UiRect::all(Val::Px(1.0)),
                    ..default()
                },
                BackgroundColor(theme::mix(theme::RAISED, c, 0.12)),
                BorderColor::all(c.with_alpha(0.5)),
                Pickable::IGNORE,
            ))
            .with_children(|t| {
                let sym: String = sub.formula.chars().filter(|ch| ch.is_alphabetic()).collect();
                t.spawn((theme::label(fonts, sym, size * 0.45, Weight::Semibold, c), Pickable::IGNORE));
            });
    } else {
        parent.spawn((
            ImageNode::new(assets.load(format!("structures/{}.png", sub.id))),
            Node { width: Val::Px(size), height: Val::Px(size), flex_shrink: 0.0, ..default() },
            Pickable::IGNORE,
        ));
    }
}

pub fn codex_entry_click_system(q: Query<&CodexEntry, (With<Clicked>, With<Button>)>, mut state: ResMut<CodexState>) {
    for entry in &q {
        state.selected = Some(entry.0);
    }
}

pub fn codex_category_tab_system(
    q: Query<&CodexCategoryTab, (With<Clicked>, With<Button>)>,
    mut filter: ResMut<CodexFilter>,
) {
    for tab in &q {
        if filter.category != tab.0 {
            filter.category = tab.0;
        }
    }
}

/// Map a physical key to the character it types (lowercase; search is case-insensitive).
pub fn keycode_to_char(k: KeyCode) -> Option<char> {
    use KeyCode::*;
    Some(match k {
        KeyA => 'a',
        KeyB => 'b',
        KeyC => 'c',
        KeyD => 'd',
        KeyE => 'e',
        KeyF => 'f',
        KeyG => 'g',
        KeyH => 'h',
        KeyI => 'i',
        KeyJ => 'j',
        KeyK => 'k',
        KeyL => 'l',
        KeyM => 'm',
        KeyN => 'n',
        KeyO => 'o',
        KeyP => 'p',
        KeyQ => 'q',
        KeyR => 'r',
        KeyS => 's',
        KeyT => 't',
        KeyU => 'u',
        KeyV => 'v',
        KeyW => 'w',
        KeyX => 'x',
        KeyY => 'y',
        KeyZ => 'z',
        Digit0 | Numpad0 => '0',
        Digit1 | Numpad1 => '1',
        Digit2 | Numpad2 => '2',
        Digit3 | Numpad3 => '3',
        Digit4 | Numpad4 => '4',
        Digit5 | Numpad5 => '5',
        Digit6 | Numpad6 => '6',
        Digit7 | Numpad7 => '7',
        Digit8 | Numpad8 => '8',
        Digit9 | Numpad9 => '9',
        Space => ' ',
        Minus => '-',
        _ => return None,
    })
}

/// What the empty search field says.
fn search_prompt() -> &'static str {
    if crate::platform::SOFT_KEYBOARD {
        "Tap to search names and formulas"
    } else {
        "Type to search names and formulas"
    }
}

/// While the library is open, typing edits the search (Backspace deletes). On a phone a tap
/// on the field brings up the keyboard, whose text becomes the search.
pub fn codex_search_input_system(
    keys: Res<ButtonInput<KeyCode>>,
    state: Res<CodexState>,
    mut filter: ResMut<CodexFilter>,
    mut text_q: Query<(&mut Text, &mut TextColor), With<CodexSearchText>>,
    boxes: Query<(), (With<Clicked>, With<CodexSearchBox>)>,
    mut typing: ResMut<crate::ui::inventory::TypingBox>,
) {
    use crate::ui::inventory::TypingBox;
    if !state.open {
        if *typing == TypingBox::Codex {
            *typing = TypingBox::None;
            crate::platform::keyboard_hide();
        }
        return;
    }
    let mut changed = false;
    if !boxes.is_empty() {
        *typing = TypingBox::Codex;
        crate::platform::keyboard_show(&filter.search);
    }
    if *typing == TypingBox::Codex {
        if let Some(t) = crate::platform::keyboard_text() {
            if t != filter.search {
                filter.search = t;
                changed = true;
            }
        }
    }
    for k in keys.get_just_pressed() {
        match k {
            KeyCode::Backspace | KeyCode::Delete => {
                filter.search.pop();
                changed = true;
            }
            _ => {
                if let Some(c) = keycode_to_char(*k) {
                    filter.search.push(c);
                    changed = true;
                }
            }
        }
    }
    if changed {
        if let Ok((mut text, mut color)) = text_q.single_mut() {
            if filter.search.is_empty() {
                text.0 = search_prompt().to_string();
                color.0 = theme::TEXT_3;
            } else {
                text.0 = format!("{}|", filter.search);
                color.0 = theme::TEXT;
            }
        }
    }
}

// --- the substance page ----------------------------------------------------------------------
fn known_reaction(r: &Reaction, progress: &PlayerProgress) -> bool {
    r.reactants.iter().all(|s| progress.discovered.contains(&s.substance_id))
        && r.products.iter().all(|s| progress.discovered.contains(&s.substance_id))
}

pub fn equation_text(r: &Reaction, subs: &Substances) -> String {
    let side = |pts: &[crate::data::common::StoichPoint]| {
        pts.iter()
            .map(|p| {
                let f = subs
                    .0
                    .get(&p.substance_id)
                    .map(|s| format_formula(&s.formula))
                    .unwrap_or_else(|| format!("#{}", p.substance_id));
                if p.moles > 1 {
                    format!("{} {}", p.moles, f)
                } else {
                    f
                }
            })
            .collect::<Vec<_>>()
            .join(" + ")
    };
    format!("{}  →  {}", side(&r.reactants), side(&r.products))
}

pub fn update_codex_detail_system(
    mut commands: Commands,
    state: Res<CodexState>,
    progress: Res<PlayerProgress>,
    db: Option<Res<RecipeDatabase>>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    fonts: Res<UiFonts>,
    asset_server: Res<AssetServer>,
    detail_q: Query<Entity, With<CodexDetail>>,
    mut detail_scroll: Query<(&CodexScrollable, &mut ScrollPosition)>,
) {
    // only while the library is showing (opening it is itself a change)
    if !state.open || !(state.is_changed() || progress.is_changed()) {
        return;
    }
    let Ok(detail) = detail_q.single() else {
        return;
    };
    if state.is_changed() {
        for (marker, mut sp) in &mut detail_scroll {
            if !marker.is_left {
                sp.0.y = 0.0;
            }
        }
    }
    commands.entity(detail).despawn_children();
    let fonts = &*fonts;
    let assets = &*asset_server;

    let Some(subs) = substances_assets.get(&game_data.substances) else {
        return;
    };
    let Some(sub) = state.selected.and_then(|sel| subs.0.get(&sel)) else {
        commands.entity(detail).with_children(|p| {
            p.spawn(Node {
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(8.0),
                margin: UiRect::top(Val::Px(80.0)),
                align_items: AlignItems::Center,
                ..default()
            })
            .with_children(|c| {
                c.spawn(theme::icon(assets, "book", 56.0, theme::LINE_STRONG));
                c.spawn(theme::label(fonts, "Pick a substance", theme::XL, Weight::Semibold, theme::TEXT_2));
                c.spawn(theme::label(
                    fonts,
                    "Everything you discover is written up here, with links to read more.",
                    theme::SM,
                    Weight::Regular,
                    theme::TEXT_3,
                ));
            });
        });
        return;
    };

    let tint = sub
        .color_hex
        .as_deref()
        .and_then(|h| u32::from_str_radix(h.trim_start_matches('#'), 16).ok())
        .map(|v| Color::srgb_u8((v >> 16) as u8, (v >> 8) as u8, v as u8))
        .unwrap_or(theme::CYAN);
    let img_path = match &sub.element_info {
        Some(ei) => format!("bohr/{}.png", ei.atomic_number),
        None => format!("structures/{}.png", sub.id),
    };

    commands.entity(detail).with_children(|p| {
        // --- hero: picture + name, formula, tags, link ---
        p.spawn(Node { column_gap: Val::Px(26.0), align_items: AlignItems::Center, ..default() }).with_children(
            |hero| {
                hero.spawn((
                    Node {
                        border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                        width: Val::Px(230.0),
                        height: Val::Px(230.0),
                        flex_shrink: 0.0,
                        padding: UiRect::all(Val::Px(16.0)),
                        border: UiRect::all(Val::Px(1.0)),
                        ..default()
                    },
                    BackgroundGradient::from(RadialGradient {
                        color_space: default(),
                        position: UiPosition::CENTER,
                        shape: RadialGradientShape::FarthestCorner,
                        stops: vec![ColorStop::auto(theme::mix(theme::RAISED, tint, 0.22)), ColorStop::auto(theme::BG)],
                    }),
                    BorderColor::all(theme::mix(theme::LINE, tint, 0.3)),
                ))
                .with_children(|card| {
                    card.spawn((
                        ImageNode::new(assets.load(img_path)),
                        Node { width: Val::Percent(100.0), height: Val::Percent(100.0), ..default() },
                    ));
                    // elements also carry their periodic tile in the corner
                    if let Some(ei) = &sub.element_info {
                        let c = element_tile_color(&sub.formula);
                        card.spawn((
                            Node {
                                border_radius: BorderRadius::all(Val::Px(theme::R_SM)),
                                position_type: PositionType::Absolute,
                                left: Val::Px(10.0),
                                top: Val::Px(10.0),
                                width: Val::Px(54.0),
                                height: Val::Px(60.0),
                                flex_direction: FlexDirection::Column,
                                align_items: AlignItems::Center,
                                justify_content: JustifyContent::Center,
                                border: UiRect::all(Val::Px(1.0)),
                                ..default()
                            },
                            BackgroundColor(theme::mix(theme::BG, c, 0.16)),
                            BorderColor::all(c.with_alpha(0.7)),
                        ))
                        .with_children(|t| {
                            t.spawn(theme::label(
                                fonts,
                                ei.atomic_number.to_string(),
                                10.0,
                                Weight::Regular,
                                theme::TEXT_2,
                            ));
                            t.spawn(theme::label(fonts, sub.formula.clone(), 24.0, Weight::Bold, c));
                        });
                    }
                });
                hero.spawn(Node {
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(8.0),
                    flex_shrink: 1.0,
                    ..default()
                })
                .with_children(|info| {
                    info.spawn(theme::label(fonts, sub.name.clone(), theme::XXL, Weight::Bold, theme::TEXT));
                    info.spawn(theme::label(
                        fonts,
                        format_formula(&sub.formula),
                        theme::LG,
                        Weight::Semibold,
                        theme::CYAN,
                    ));
                    info.spawn(Node {
                        flex_wrap: FlexWrap::Wrap,
                        column_gap: Val::Px(6.0),
                        row_gap: Val::Px(6.0),
                        ..default()
                    })
                    .with_children(|chips| {
                        theme::spawn_chip(chips, fonts, state_name(sub.state), state_color(sub.state));
                        for (t, c) in tags(sub) {
                            theme::spawn_chip(chips, fonts, t, c);
                        }
                        if sub.stage.is_some() {
                            theme::spawn_chip(chips, fonts, "Coming later", theme::GOLD);
                        }
                    });
                    if let Some((label, url)) = crate::data::common::primary_reference(&sub.references) {
                        info.spawn(Node { margin: UiRect::top(Val::Px(6.0)), ..default() }).with_children(|b| {
                            theme::spawn_button(
                                b,
                                fonts,
                                assets,
                                Kind::Primary,
                                Some("external"),
                                &format!("Read on {label}"),
                                CodexRefLink(url.clone()),
                            );
                        });
                    }
                });
            },
        );

        // --- a locked preview says what it is waiting for ---
        if let Some(stage) = &sub.stage {
            p.spawn(theme::para(
                fonts,
                format!(
                    "Coming later: nothing in the game makes {} yet. It arrives with the {} stage.",
                    sub.name, stage
                ),
                theme::MD,
                theme::GOLD,
                Val::Px(820.0),
            ));
        }

        // --- the story ---
        let mut story: Vec<String> = Vec::new();
        if let Some(d) = &sub.description {
            story.push(d.clone());
        }
        if let Some(ei) = &sub.element_info {
            if let Some(o) = &ei.overview {
                story.push(o.clone());
            }
            if let Some(ds) = &ei.discovery_story {
                story.push(ds.clone());
            }
        }
        // one paragraph per line of text (scraped text can carry stray blank lines)
        for s in &story {
            for line in s.lines().map(str::trim).filter(|l| !l.is_empty()) {
                p.spawn(theme::para(fonts, line.to_string(), theme::MD, theme::TEXT_2, Val::Px(820.0)));
            }
        }
        if sub.properties.contains(&Property::IsClass) {
            p.spawn(theme::para(fonts, CLASS_NOTE.to_string(), theme::SM, theme::TEXT_3, Val::Px(820.0)));
        }
        if sub.is_transient() {
            p.spawn(theme::para(fonts, TRANSIENT_NOTE.to_string(), theme::SM, theme::GOLD, Val::Px(820.0)));
        }
        if sub.properties.contains(&Property::IsMedicine) {
            p.spawn(theme::para(fonts, MEDICINE_NOTE.to_string(), theme::SM, theme::GOLD, Val::Px(820.0)));
        }
        // where the text comes from, as its licence asks
        let mut credit: Vec<String> =
            sub.text_source.as_deref().and_then(crate::ui::credits::text_credit).into_iter().collect();
        if sub.element_info.as_ref().is_some_and(|e| e.overview.is_some())
            && sub.text_source.as_deref() != Some("Wikipedia")
        {
            credit.push("Overview: Wikipedia, CC BY-SA 4.0.".to_string());
        }
        if !credit.is_empty() {
            p.spawn((CodexTextCredit, theme::para(fonts, credit.join("  "), theme::XS, theme::TEXT_3, Val::Px(820.0))));
        }

        // --- facts ---
        let facts = facts(sub);
        if !facts.is_empty() {
            theme::spawn_section_title(p, fonts, "Properties");
            spawn_fact_grid(p, fonts, facts, false);
        }

        // --- industry ---
        let industry = industry(sub);
        if !industry.is_empty() {
            theme::spawn_section_title(p, fonts, "In industry");
            spawn_fact_grid(p, fonts, industry, true);
            if sub.world_t_year.is_some() {
                p.spawn(theme::para(fonts, WORLD_NOTE.to_string(), theme::XS, theme::TEXT_3, Val::Px(820.0)));
            }
            if sub.production_t_year.is_some() {
                p.spawn(theme::para(fonts, PRODUCTION_NOTE.to_string(), theme::XS, theme::TEXT_3, Val::Px(820.0)));
            }
        }

        // --- reactions that make it / use it ---
        if let Some(db) = db.as_ref() {
            let makes: Vec<&Reaction> =
                db.authored.iter().filter(|r| r.products.iter().any(|s| s.substance_id == sub.id)).collect();
            let uses: Vec<&Reaction> =
                db.authored.iter().filter(|r| r.reactants.iter().any(|s| s.substance_id == sub.id)).collect();
            for (title, list) in [("How it is made", makes), ("What it is used for", uses)] {
                if list.is_empty() {
                    continue;
                }
                theme::spawn_section_title(p, fonts, title);
                let known: Vec<&&Reaction> = list.iter().filter(|r| known_reaction(r, &progress)).collect();
                for r in &known {
                    reaction_row(p, fonts, assets, r, subs);
                }
                let hidden = list.len() - known.len();
                if hidden > 0 {
                    p.spawn(theme::label(
                        fonts,
                        format!(
                            "{} more you have not discovered yet{}",
                            hidden,
                            if known.is_empty() { "" } else { "." }
                        ),
                        theme::SM,
                        Weight::Regular,
                        theme::TEXT_3,
                    ));
                }
            }
        }

        // --- the small print ---
        let mut extra: Vec<String> = Vec::new();
        if !sub.uses.is_empty() {
            extra.push(format!("Uses: {}", sub.uses.join(", ")));
        }
        if let Some(h) = &sub.hazard_summary {
            extra.push(format!("Hazards (GHS, via PubChem): {}", h));
        }
        if !sub.synonyms.is_empty() {
            let syn: Vec<String> = sub.synonyms.iter().take(8).cloned().collect();
            extra.push(format!("Also known as: {}", syn.join(", ")));
        }
        if !extra.is_empty() {
            theme::spawn_section_title(p, fonts, "Notes");
            for e in extra {
                p.spawn(theme::para(fonts, e, theme::SM, theme::TEXT_2, Val::Px(820.0)));
            }
        }
        let others: Vec<&(String, String)> = sub
            .references
            .iter()
            .filter(|x| Some(*x) != crate::data::common::primary_reference(&sub.references))
            .collect();
        if !others.is_empty() {
            theme::spawn_section_title(p, fonts, "References");
            p.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(8.0), row_gap: Val::Px(8.0), ..default() })
                .with_children(|row| {
                    for (l, url) in others {
                        theme::spawn_button(
                            row,
                            fonts,
                            assets,
                            Kind::Secondary,
                            Some("external"),
                            l,
                            CodexRefLink(url.clone()),
                        );
                    }
                });
        }
    });
}

/// One reaction on a substance page: vessel, name, equation; opens the Reaction Library.
fn reaction_row(p: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer, r: &Reaction, subs: &Substances) {
    let accent = theme::process_color(&r.process);
    p.spawn((
        theme::button(
            Kind::Row,
            Node {
                align_items: AlignItems::Center,
                column_gap: Val::Px(12.0),
                padding: UiRect::axes(Val::Px(10.0), Val::Px(7.0)),
                max_width: Val::Px(820.0),
                ..default()
            },
            theme::R_MD,
        ),
        CodexReactionLink(r.id),
    ))
    .with_children(|row| {
        row.spawn((
            ImageNode::new(assets.load(vessel_art_path(&r.process, "outline"))).with_color(accent),
            Node { width: Val::Px(34.0), height: Val::Px(34.0), flex_shrink: 0.0, ..default() },
            Pickable::IGNORE,
        ));
        row.spawn((Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, ..default() }, Pickable::IGNORE))
            .with_children(|c| {
                c.spawn((
                    theme::label(
                        fonts,
                        format!("{}  ·  {}", r.name, vessel_name(&r.process)),
                        theme::SM,
                        Weight::Semibold,
                        theme::TEXT,
                    ),
                    Pickable::IGNORE,
                ));
                c.spawn((
                    Text::new(equation_text(r, subs)),
                    TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(12.0), ..default() },
                    TextColor(theme::mix(accent, theme::TEXT, 0.5)),
                    Pickable::IGNORE,
                ));
            });
    });
}

pub fn codex_link_click_system(
    q: Query<&CodexRefLink, (With<Clicked>, With<Button>)>,
    reactions: Query<&CodexReactionLink, (With<Clicked>, With<Button>)>,
    mut codex: ResMut<CodexState>,
    mut rlib: ResMut<ReactionLibState>,
) {
    for link in &q {
        open_url(&link.0);
    }
    for link in &reactions {
        codex.open = false;
        rlib.open = true;
        rlib.selected = Some(link.0);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn index_names_skip_locants_and_descriptors() {
        for (name, filed) in [
            ("(+)-Glaucine", "glaucine"),
            ("1,4-Dioxane", "dioxane"),
            ("L-Lysine", "lysine"),
            ("p-Xylene", "xylene"),
            ("N,N-Dimethylformamide", "dimethylformamide"),
            ("α-Hexylcinnamaldehyde", "hexylcinnamaldehyde"),
            ("tert-Butanol", "butanol"),
            ("(2R,3S)-Isocitric acid", "isocitric acid"),
            ("1H-Indole", "indole"),
            // real words and multipliers stay
            ("Co-trimoxazole", "co-trimoxazole"),
            ("Di-tert-butyl peroxide", "di-tert-butyl peroxide"),
            ("Sodium 2-ethylhexanoate", "sodium 2-ethylhexanoate"),
            ("Water", "water"),
            // nothing left to file under: the whole name
            ("U-238", "u-238"),
        ] {
            assert_eq!(index_name(name), filed, "{name}");
        }
    }

    #[test]
    fn rough_tonnages_read_at_two_figures() {
        for (t, said) in [
            (4.0e12, "4 trillion t"),
            (5.0e10, "50 billion t"),
            (1.9e9, "1.9 billion t"),
            (2.7e8, "270 million t"),
            (9.5e7, "95 million t"),
            (3.5e6, "3.5 million t"),
            (1.2e6, "1.2 million t"),
            (3.7e5, "370,000 t"),
            (3.3e3, "3,300 t"),
            (180.0, "180 t"),
        ] {
            assert_eq!(rough_tonnes(t), said, "{t}");
        }
    }
}
