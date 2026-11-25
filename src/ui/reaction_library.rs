// src/ui/reaction_library.rs
//
// The Reaction Library: every reaction the player knows (all reactants and all products
// discovered), grouped by era, searchable. The page on the right shows the vessel, the
// balanced equation, the conditions, the reactants and products (click one to open it in
// the Substance Library), the history blurb and the references.
use crate::ui::{Button, Clicked};
use bevy::prelude::*;
use bevy::ui::Pressed;
use bevy::ui::ScrollPosition;

use crate::components::format_formula;
use crate::data::common::{Condition, StoichPoint};
use crate::data::reactions::Reaction;
use crate::data::substances::{Substance, Substances};
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::reaction_check::accent_glow;
use crate::ui::codex::{equation_text, open_url, CodexState};
use crate::ui::inventory::{element_tile_color, is_element_formula};
use crate::ui::process_toolbar::{vessel_art_path, vessel_name};
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::ui::virtual_list::VirtualList;
use crate::GameData;

#[derive(Resource, Default)]
pub struct ReactionLibState {
    pub open: bool,
    pub selected: Option<u32>,
    pub search: String,
}

const LIST_W: f32 = 400.0;

#[derive(Component)]
pub struct ReactionLibCloseButton;
#[derive(Component)]
pub struct ReactionLibRoot;
#[derive(Component)]
pub struct ReactionLibScrollable {
    pub is_left: bool,
}
#[derive(Component)]
pub struct ReactionLibListContent;
#[derive(Component)]
pub struct ReactionLibDetail;
#[derive(Component)]
pub struct ReactionLibEntry(pub u32);
#[derive(Component)]
pub struct ReactionLibRefLink(pub String);
#[derive(Component)]
pub struct ReactionLibSubstanceLink(pub u32);
#[derive(Component)]
pub struct ReactionLibSearchText;
/// The search field (a tap brings up a phone's keyboard).
#[derive(Component)]
pub struct ReactionLibSearchBox;

/// What the empty search field says.
fn search_prompt() -> &'static str {
    if crate::platform::SOFT_KEYBOARD {
        "Tap to search reactions and vessels"
    } else {
        "Type to search reactions and vessels"
    }
}
#[derive(Component)]
pub struct ReactionLibCountText;
/// An era heading in the list.
#[derive(Component)]
pub struct ReactionLibHeading;
/// "Nothing matches yet.", under the list (outside it: the list's children are its rows).
#[derive(Component)]
pub struct ReactionLibEmptyText;

/// Every list entry is one fixed height, so the list can build only those in sight: a row
/// (vessel picture, name, one line of equation) or an era heading in the same cell.
const ROW_H: f32 = 48.0;
const ROW_GAP: f32 = 4.0;
/// List ids at and above this are era headings (the base plus the epoch); below, reaction ids.
const HEADING_BASE: u32 = u32::MAX - 255;

fn known(r: &Reaction, progress: &PlayerProgress) -> bool {
    r.products.iter().all(|sp| progress.discovered.contains(&sp.substance_id))
        && r.reactants.iter().all(|sp| progress.discovered.contains(&sp.substance_id))
}

fn condition_chip(c: &Condition, subs: &Substances) -> (String, Color) {
    let name = |id: &u32| subs.0.get(id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    match c {
        Condition::Temperature(t) => (format!("{:.0} °C  ({:.0} K)", t - 273.15, t), Color::srgb(1.0, 0.55, 0.30)),
        Condition::Pressure(p) => (
            format!("{} atm", if *p >= 10.0 { format!("{:.0}", p) } else { format!("{:.1}", p) }),
            Color::srgb(0.55, 0.75, 1.0),
        ),
        Condition::RequiresCatalyst(id) => (format!("Catalyst: {}", name(id)), theme::GREEN),
        Condition::RequiresSolvent(id) => (format!("Solvent: {}", name(id)), theme::CYAN),
        Condition::RequiresPurity(p) => (format!("Purity {:.0}%", p * 100.0), theme::VIOLET),
    }
}

pub fn spawn_reaction_library(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((ReactionLibRoot, crate::ui::shell::SplitRoot, theme::view_root(610), Name::new("ReactionLibRoot")))
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
                        t.spawn(theme::label(fonts, "Reaction Library", theme::XL, Weight::Semibold, theme::TEXT));
                        t.spawn((
                            ReactionLibCountText,
                            theme::label(fonts, "", theme::XS, Weight::Regular, theme::TEXT_3),
                        ));
                    });
                    theme::spawn_icon_button(hdr, assets, "close", 32.0, theme::TEXT_2, ReactionLibCloseButton);
                });
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
                    ReactionLibSearchBox,
                ))
                .with_children(|s| {
                    s.spawn(theme::icon(assets, "search", 16.0, theme::TEXT_3));
                    s.spawn((
                        ReactionLibSearchText,
                        theme::label(fonts, search_prompt(), theme::SM, Weight::Regular, theme::TEXT_3),
                    ));
                });
                col.spawn((
                    ReactionLibScrollable { is_left: true },
                    ScrollPosition::default(),
                    Node {
                        flex_direction: FlexDirection::Column,
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
                        ReactionLibListContent,
                        VirtualList::new(Vec2::new(0.0, ROW_H), Vec2::new(0.0, ROW_GAP)),
                        Node { width: Val::Percent(100.0), height: Val::Px(0.0), flex_shrink: 0.0, ..default() },
                    ));
                    scroll.spawn((
                        ReactionLibEmptyText,
                        theme::label(fonts, "Nothing matches yet.", theme::SM, Weight::Regular, theme::TEXT_3),
                        Node { display: Display::None, ..default() },
                    ));
                });
            });
            root.spawn((
                crate::ui::shell::SplitPane,
                ReactionLibScrollable { is_left: false },
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
                    ReactionLibDetail,
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
pub fn reaction_lib_button_system(
    closes: Query<(), (With<Clicked>, With<ReactionLibCloseButton>)>,
    mut state: ResMut<ReactionLibState>,
    mut root_q: Query<&mut Node, With<ReactionLibRoot>>,
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

/// While the library is open, typing edits the search (Backspace deletes). On a phone a tap
/// on the field brings up the keyboard, whose text becomes the search.
pub fn reaction_lib_search_system(
    keys: Res<ButtonInput<KeyCode>>,
    mut state: ResMut<ReactionLibState>,
    mut text_q: Query<(&mut Text, &mut TextColor), With<ReactionLibSearchText>>,
    boxes: Query<(), (With<Clicked>, With<ReactionLibSearchBox>)>,
    mut typing: ResMut<crate::ui::inventory::TypingBox>,
) {
    use crate::ui::inventory::TypingBox;
    if !state.open {
        if *typing == TypingBox::Reactions {
            *typing = TypingBox::None;
            crate::platform::keyboard_hide();
        }
        return;
    }
    if !boxes.is_empty() {
        *typing = TypingBox::Reactions;
        crate::platform::keyboard_show(&state.search);
    }
    let keyboard = crate::platform::keyboard_text().filter(|_| *typing == TypingBox::Reactions);
    let (search, _) = crate::ui::codex::typed(&state.search, &keys, keyboard);
    if search != state.search {
        state.search = search;
        if let Ok((mut text, mut color)) = text_q.single_mut() {
            if state.search.is_empty() {
                text.0 = search_prompt().to_string();
                color.0 = theme::TEXT_3;
            } else {
                text.0 = format!("{}|", state.search);
                color.0 = theme::TEXT;
            }
        }
    }
}

// --- list ---------------------------------------------------------------------------------
pub fn populate_reaction_list_system(
    state: Res<ReactionLibState>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    recipe_db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    mut list_q: Query<&mut VirtualList, With<ReactionLibListContent>>,
    mut empty_q: Query<&mut Node, With<ReactionLibEmptyText>>,
    mut rows: Query<(&ReactionLibEntry, &mut Skin)>,
    mut count_q: Query<&mut Text, With<ReactionLibCountText>>,
    mut list_scroll: Query<(&ReactionLibScrollable, &mut ScrollPosition)>,
    mut prev: Local<(bool, String)>,
) {
    let just_opened = state.open && !prev.0;
    let search_changed = state.search != prev.1;
    prev.0 = state.open;
    prev.1 = state.search.clone();
    if state.is_changed() {
        for (e, mut skin) in &mut rows {
            let a = Some(e.0) == state.selected;
            if skin.active != a {
                skin.active = a;
            }
        }
    }
    if !(state.open && (just_opened || search_changed || progress.is_changed())) {
        return;
    }
    let (Some(db), Some(subs)) = (recipe_db.as_ref(), substances_assets.get(&game_data.substances)) else {
        return;
    };
    let Ok(mut list) = list_q.single_mut() else {
        return;
    };
    if just_opened || search_changed {
        for (marker, mut sp) in &mut list_scroll {
            if marker.is_left {
                sp.0.y = 0.0;
            }
        }
    }

    let q = state.search.to_lowercase();
    let matches = |r: &Reaction| {
        q.is_empty()
            || r.name.to_lowercase().contains(&q)
            || vessel_name(&r.process).to_lowercase().contains(&q)
            || r.reactants.iter().chain(r.products.iter()).any(|sp| {
                subs.0
                    .get(&sp.substance_id)
                    .is_some_and(|s| s.name.to_lowercase().contains(&q) || s.formula.to_lowercase().contains(&q))
            })
    };
    // known reactions by era (db.authored is already in (epoch, id) order), each era headed
    let mut ids = Vec::new();
    let mut last_epoch: Option<u8> = None;
    for r in db.authored.iter().filter(|r| known(r, &progress) && matches(r)) {
        if Some(r.epoch) != last_epoch {
            last_epoch = Some(r.epoch);
            ids.push(HEADING_BASE + r.epoch as u32);
        }
        ids.push(r.id);
    }
    let total_known = db.authored.iter().filter(|r| known(r, &progress)).count();
    if let Ok(mut t) = count_q.single_mut() {
        t.0 = format!("{} of {} reactions known", total_known, db.authored.len());
    }
    if let Ok(mut node) = empty_q.single_mut() {
        let d = if ids.is_empty() { Display::Flex } else { Display::None };
        if node.display != d {
            node.display = d;
        }
    }
    list.set(ids, []);
}

/// Builds the list entries in sight (and a screen either side) and drops the rest; a closed
/// library builds none. Cheap when nothing moved.
#[allow(clippy::too_many_arguments, clippy::type_complexity)]
pub fn reaction_lib_window_system(
    mut commands: Commands,
    state: Res<ReactionLibState>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    recipe_db: Option<Res<RecipeDatabase>>,
    focus: Option<Res<crate::ui::focus::KeyFocus>>,
    mut content_q: Query<(Entity, &mut VirtualList, &mut Node, &ComputedNode), With<ReactionLibListContent>>,
    scroll_q: Query<(&ReactionLibScrollable, &ComputedNode, &ScrollPosition)>,
    mut cells: Query<
        &mut Node,
        (Or<(With<ReactionLibEntry>, With<ReactionLibHeading>)>, Without<ReactionLibListContent>),
    >,
    pressed: Query<(), (With<ReactionLibEntry>, Or<(With<Pressed>, With<Clicked>)>)>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
) {
    let Ok((content, mut list, mut node, cn)) = content_q.single_mut() else {
        return;
    };
    let Some((_, view, scroll)) = scroll_q.iter().find(|(m, _, _)| m.is_left) else {
        return;
    };
    let (Some(db), Some(subs)) = (recipe_db.as_ref(), substances_assets.get(&game_data.substances)) else {
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
        if let Ok(mut n) = cells.get_mut(*e) {
            n.top = Val::Px(at.y);
        }
    }
    for (id, at, _) in &pass.build {
        let e = if *id >= HEADING_BASE {
            let epoch = (*id - HEADING_BASE) as u8;
            let era = db.epochs.get(epoch as usize).map(|d| d.era.as_str()).unwrap_or("");
            spawn_era_heading(&mut commands, &fonts, db.epoch_name(epoch), era, at.y)
        } else {
            let Some(r) = db.authored.iter().find(|r| r.id == *id) else { continue };
            spawn_list_row(&mut commands, &fonts, &assets, r, subs, state.selected == Some(r.id), at.y)
        };
        list.record(*id, e, *at);
    }
    if !pass.build.is_empty() || !pass.drop.is_empty() {
        commands.entity(content).replace_children(&list.order());
    }
}

/// An era heading in a list cell, `top` pixels down the list.
fn spawn_era_heading(commands: &mut Commands, fonts: &UiFonts, name: &str, era: &str, top: f32) -> Entity {
    commands
        .spawn((
            ReactionLibHeading,
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(4.0),
                right: Val::Px(0.0),
                top: Val::Px(top),
                height: Val::Px(ROW_H),
                align_items: AlignItems::FlexEnd,
                column_gap: Val::Px(8.0),
                padding: UiRect::bottom(Val::Px(6.0)),
                ..default()
            },
            Pickable::IGNORE,
        ))
        .with_children(|h| {
            h.spawn(theme::label(fonts, name.to_uppercase(), theme::XS, Weight::Bold, theme::GOLD));
            if !era.is_empty() {
                h.spawn(theme::label(fonts, era, theme::XS, Weight::Regular, theme::TEXT_3));
            }
        })
        .id()
}

/// One reaction in a list cell, `top` pixels down the list: vessel, name, equation (one line
/// each, so every row is the same height; the page shows the whole equation).
fn spawn_list_row(
    commands: &mut Commands,
    fonts: &UiFonts,
    assets: &AssetServer,
    r: &Reaction,
    subs: &Substances,
    selected: bool,
    top: f32,
) -> Entity {
    let accent = theme::process_color(&r.process);
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
        ReactionLibEntry(r.id),
    ));
    if selected {
        row.insert(Skin::active(Kind::Row, true));
    }
    row.with_children(|row| {
        row.spawn((
            Node {
                border_radius: BorderRadius::all(Val::Px(theme::R_SM)),
                width: Val::Px(36.0),
                height: Val::Px(36.0),
                flex_shrink: 0.0,
                padding: UiRect::all(Val::Px(3.0)),
                ..default()
            },
            BackgroundColor(accent.with_alpha(0.12)),
            Pickable::IGNORE,
        ))
        .with_children(|i| {
            i.spawn((
                ImageNode::new(assets.load(vessel_art_path(&r.process, "outline"))).with_color(accent),
                Node { width: Val::Percent(100.0), height: Val::Percent(100.0), ..default() },
                Pickable::IGNORE,
            ));
        });
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
                theme::label(fonts, r.name.clone(), theme::SM, Weight::Semibold, theme::TEXT),
                TextLayout::no_wrap(),
                Pickable::IGNORE,
            ));
            c.spawn((
                Text::new(equation_text(r, subs)),
                TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(11.0), ..default() },
                TextColor(theme::mix(accent, theme::TEXT, 0.55)),
                TextLayout::no_wrap(),
                Pickable::IGNORE,
            ));
        });
    });
    row.id()
}

pub fn reaction_lib_entry_click_system(
    q: Query<&ReactionLibEntry, (With<Clicked>, With<Button>)>,
    mut state: ResMut<ReactionLibState>,
) {
    for entry in &q {
        if state.selected != Some(entry.0) {
            state.selected = Some(entry.0);
        }
    }
}

// --- the reaction page -------------------------------------------------------------------------
pub fn update_reaction_detail_system(
    mut commands: Commands,
    state: Res<ReactionLibState>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    recipe_db: Option<Res<RecipeDatabase>>,
    fonts: Res<UiFonts>,
    asset_server: Res<AssetServer>,
    detail_q: Query<Entity, With<ReactionLibDetail>>,
    mut detail_scroll: Query<(&ReactionLibScrollable, &mut ScrollPosition)>,
    mut prev_sel: Local<Option<Option<u32>>>,
    pages_assets: Res<Assets<crate::data::pages::Pages>>,
) {
    // rebuild only when the selection changes (typing in the search also changes state)
    if *prev_sel == Some(state.selected) {
        return;
    }
    let pages = pages_assets.get(&game_data.pages);
    let Ok(detail) = detail_q.single() else {
        return;
    };
    let (Some(db), Some(subs)) = (recipe_db.as_ref(), substances_assets.get(&game_data.substances)) else {
        return;
    };
    *prev_sel = Some(state.selected);
    for (marker, mut sp) in &mut detail_scroll {
        if !marker.is_left {
            sp.0.y = 0.0;
        }
    }
    commands.entity(detail).despawn_children();
    let fonts = &*fonts;
    let assets = &*asset_server;

    let Some(r) = state.selected.and_then(|sel| db.map.values().find(|r| r.id == sel)) else {
        commands.entity(detail).with_children(|p| {
            p.spawn(Node {
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(8.0),
                margin: UiRect::top(Val::Px(80.0)),
                align_items: AlignItems::Center,
                ..default()
            })
            .with_children(|c| {
                c.spawn(theme::icon(assets, "reaction", 56.0, theme::LINE_STRONG));
                c.spawn(theme::label(fonts, "Pick a reaction", theme::XL, Weight::Semibold, theme::TEXT_2));
                c.spawn(theme::label(
                    fonts,
                    "Every reaction you have run is written up here, era by era.",
                    theme::SM,
                    Weight::Regular,
                    theme::TEXT_3,
                ));
            });
        });
        return;
    };
    let accent = theme::process_color(&r.process);

    commands.entity(detail).with_children(|p| {
        // --- hero: vessel + name, era, vessel name ---
        p.spawn(Node { column_gap: Val::Px(26.0), align_items: AlignItems::Center, ..default() }).with_children(
            |hero| {
                hero.spawn((
                    Node {
                        border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                        width: Val::Px(180.0),
                        height: Val::Px(180.0),
                        flex_shrink: 0.0,
                        padding: UiRect::all(Val::Px(22.0)),
                        border: UiRect::all(Val::Px(1.0)),
                        ..default()
                    },
                    BackgroundGradient::from(RadialGradient {
                        color_space: default(),
                        position: UiPosition::CENTER,
                        shape: RadialGradientShape::FarthestCorner,
                        stops: vec![
                            ColorStop::auto(theme::mix(theme::RAISED, accent, 0.28)),
                            ColorStop::auto(theme::BG),
                        ],
                    }),
                    BorderColor::all(theme::mix(theme::LINE, accent, 0.45)),
                    theme::glow(accent.with_alpha(0.22), 18.0),
                ))
                .with_children(|card| {
                    card.spawn(Node { width: Val::Percent(100.0), height: Val::Percent(100.0), ..default() })
                        .with_children(|art| {
                            for (layer, color) in [
                                ("fill", theme::mix(accent, theme::TEXT, 0.2).with_alpha(0.55)),
                                ("outline", accent),
                                ("accent", accent_glow(&r.process).with_alpha(0.9)),
                            ] {
                                art.spawn((
                                    ImageNode::new(assets.load(vessel_art_path(&r.process, layer))).with_color(color),
                                    Node {
                                        position_type: PositionType::Absolute,
                                        width: Val::Percent(100.0),
                                        height: Val::Percent(100.0),
                                        ..default()
                                    },
                                ));
                            }
                        });
                });
                hero.spawn(Node {
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(8.0),
                    flex_shrink: 1.0,
                    ..default()
                })
                .with_children(|info| {
                    let e = r.epoch;
                    let era = db.epochs.get(e as usize).map(|d| d.era.clone()).unwrap_or_default();
                    let t = if era.is_empty() {
                        db.epoch_name(e).to_uppercase()
                    } else {
                        format!("{}  ·  {}", db.epoch_name(e).to_uppercase(), era)
                    };
                    info.spawn(theme::label(fonts, t, theme::XS, Weight::Bold, theme::GOLD));
                    info.spawn(theme::label(fonts, r.name.clone(), theme::XXL, Weight::Bold, theme::TEXT));
                    info.spawn(Node {
                        flex_wrap: FlexWrap::Wrap,
                        column_gap: Val::Px(6.0),
                        row_gap: Val::Px(6.0),
                        ..default()
                    })
                    .with_children(|chips| {
                        theme::spawn_chip(chips, fonts, vessel_name(&r.process), accent);
                        let (dh, c) = if r.enthalpy_change_kj_mol < 0.0 {
                            (
                                format!("Releases heat  ΔH {:+.0} kJ/mol", r.enthalpy_change_kj_mol),
                                Color::srgb(1.0, 0.55, 0.30),
                            )
                        } else {
                            (
                                format!("Absorbs heat  ΔH {:+.0} kJ/mol", r.enthalpy_change_kj_mol),
                                Color::srgb(0.55, 0.75, 1.0),
                            )
                        };
                        theme::spawn_chip(chips, fonts, &dh, c);
                        for cond in &r.conditions {
                            let (t, c) = condition_chip(cond, subs);
                            theme::spawn_chip(chips, fonts, &t, c);
                        }
                    });
                    if let Some((label, url)) = crate::data::common::primary_reference(&r.references) {
                        info.spawn(Node { margin: UiRect::top(Val::Px(6.0)), ..default() }).with_children(|b| {
                            theme::spawn_button(
                                b,
                                fonts,
                                assets,
                                Kind::Primary,
                                Some("external"),
                                &format!("Read on {label}"),
                                ReactionLibRefLink(url.clone()),
                            );
                        });
                    }
                });
            },
        );

        // --- the equation, big ---
        p.spawn((
            Node {
                border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                padding: UiRect::axes(Val::Px(20.0), Val::Px(16.0)),
                border: UiRect::left(Val::Px(3.0)),
                ..default()
            },
            BackgroundColor(theme::SURFACE),
            BorderColor::all(accent),
        ))
        .with_children(|eq| {
            eq.spawn((
                Text::new(equation_text(r, subs)),
                TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(24.0), ..default() },
                TextColor(theme::TEXT),
            ));
        });

        // --- in and out: substance cards that open the Substance Library ---
        p.spawn(Node {
            column_gap: Val::Px(22.0),
            row_gap: Val::Px(14.0),
            flex_wrap: FlexWrap::Wrap,
            align_items: AlignItems::FlexStart,
            ..default()
        })
        .with_children(|io| {
            for (title, side) in [("Reactants", &r.reactants), ("Products", &r.products)] {
                io.spawn(Node { flex_direction: FlexDirection::Column, row_gap: Val::Px(8.0), ..default() })
                    .with_children(|c| {
                        c.spawn(theme::label(fonts, title.to_uppercase(), theme::XS, Weight::Bold, theme::TEXT_3));
                        c.spawn(Node {
                            column_gap: Val::Px(8.0),
                            row_gap: Val::Px(8.0),
                            flex_wrap: FlexWrap::Wrap,
                            ..default()
                        })
                        .with_children(|row| {
                            for sp in side.iter() {
                                if let Some(s) = subs.0.get(&sp.substance_id) {
                                    substance_card(row, fonts, assets, s, sp);
                                }
                            }
                        });
                    });
            }
        });

        if let Some(desc) = &r.description {
            theme::spawn_section_title(p, fonts, "The story");
            p.spawn(theme::para(fonts, desc.clone(), theme::MD, theme::TEXT_2, Val::Px(820.0)));
        }
        p.spawn(theme::label(
            fonts,
            format!("Activation energy about {:.0} kJ/mol.", r.activation_energy_kj),
            theme::SM,
            Weight::Regular,
            theme::TEXT_3,
        ));

        // --- the ideas behind it, and its vessel's, in Learn ---
        if let Some(pg) = pages {
            let keys = pg.reaction_topics(r.id, &r.process);
            if !keys.is_empty() {
                theme::spawn_section_title(p, fonts, "Learn more");
                crate::ui::curriculum::spawn_learn_row(p, fonts, assets, pg, &keys);
            }
        }

        let others: Vec<&(String, String)> =
            r.references.iter().filter(|x| Some(*x) != crate::data::common::primary_reference(&r.references)).collect();
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
                            ReactionLibRefLink(url.clone()),
                        );
                    }
                });
        }
    });
}

fn substance_card(
    parent: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    s: &Substance,
    sp: &StoichPoint,
) {
    parent
        .spawn((
            theme::button(
                Kind::Secondary,
                Node {
                    width: Val::Px(124.0),
                    flex_direction: FlexDirection::Column,
                    align_items: AlignItems::Center,
                    row_gap: Val::Px(4.0),
                    padding: UiRect::all(Val::Px(8.0)),
                    border: UiRect::all(Val::Px(1.0)),
                    ..default()
                },
                theme::R_MD,
            ),
            ReactionLibSubstanceLink(s.id),
        ))
        .with_children(|c| {
            if is_element_formula(&s.formula) {
                let col = element_tile_color(&s.formula);
                c.spawn((
                    Node {
                        width: Val::Px(64.0),
                        height: Val::Px(64.0),
                        align_items: AlignItems::Center,
                        justify_content: JustifyContent::Center,
                        ..default()
                    },
                    Pickable::IGNORE,
                ))
                .with_children(|t| {
                    t.spawn((
                        theme::label(fonts, format_formula(&s.formula), 30.0, Weight::Semibold, col),
                        Pickable::IGNORE,
                    ));
                });
            } else {
                c.spawn((
                    ImageNode::new(assets.load(format!("structures/{}.png", s.id))),
                    Node { width: Val::Px(64.0), height: Val::Px(64.0), ..default() },
                    Pickable::IGNORE,
                ));
            }
            let f = if sp.moles > 1 {
                format!("{} {}", sp.moles, format_formula(&s.formula))
            } else {
                format_formula(&s.formula)
            };
            c.spawn((theme::label(fonts, f, theme::SM, Weight::Semibold, theme::CYAN), Pickable::IGNORE));
            c.spawn((
                Text::new(s.name.clone()),
                TextFont { font: fonts.main.clone().into(), font_size: FontSize::Px(theme::XS), ..default() },
                TextColor(theme::TEXT_2),
                TextLayout::justify(Justify::Center),
                Node { max_width: Val::Px(108.0), ..default() },
                Pickable::IGNORE,
            ));
        });
}

/// Reference buttons open the browser; substance cards jump to the Substance Library.
pub fn reaction_lib_link_click_system(
    q: Query<&ReactionLibRefLink, (With<Clicked>, With<Button>)>,
    subs: Query<&ReactionLibSubstanceLink, (With<Clicked>, With<Button>)>,
    mut state: ResMut<ReactionLibState>,
    mut codex: ResMut<CodexState>,
) {
    for link in &q {
        open_url(&link.0);
    }
    for link in &subs {
        state.open = false;
        codex.open = true;
        codex.selected = Some(link.0);
    }
}
