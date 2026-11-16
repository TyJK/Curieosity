// src/ui/reaction_library.rs
//
// The Reaction Library: every reaction the player knows (all reactants and all products
// discovered), grouped by era, searchable. The page on the right shows the vessel, the
// balanced equation, the conditions, the reactants and products (click one to open it in
// the Substance Library), the history blurb and the references.
use bevy::prelude::*;
use bevy::ui::ScrollPosition;

use crate::components::format_formula;
use crate::data::common::{Condition, StoichPoint};
use crate::data::reactions::Reaction;
use crate::data::substances::{Substance, Substances};
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::reaction_check::accent_glow;
use crate::ui::codex::{equation_text, keycode_to_char, open_url, CodexState};
use crate::ui::inventory::{element_tile_color, is_element_formula};
use crate::ui::process_toolbar::{vessel_art_path, vessel_name};
use crate::ui::theme::{self, Kind, Skin, Weight};
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
#[derive(Component)]
pub struct ReactionLibCountText;

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
        .spawn((ReactionLibRoot, theme::view_root(610), Name::new("ReactionLibRoot")))
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
                    Node {
                        height: Val::Px(38.0),
                        flex_shrink: 0.0,
                        align_items: AlignItems::Center,
                        column_gap: Val::Px(9.0),
                        padding: UiRect::horizontal(Val::Px(11.0)),
                        border: UiRect::all(Val::Px(1.0)),
                        ..default()
                    },
                    BorderRadius::all(Val::Px(theme::R_MD)),
                    BackgroundColor(theme::BG),
                    BorderColor::all(theme::LINE_STRONG),
                ))
                .with_children(|s| {
                    s.spawn(theme::icon(assets, "search", 16.0, theme::TEXT_3));
                    s.spawn((
                        ReactionLibSearchText,
                        theme::label(
                            fonts,
                            "Type to search reactions and vessels",
                            theme::SM,
                            Weight::Regular,
                            theme::TEXT_3,
                        ),
                    ));
                });
                col.spawn((
                    ReactionLibScrollable { is_left: true },
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
                        ReactionLibListContent,
                        Node {
                            width: Val::Percent(100.0),
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(4.0),
                            ..default()
                        },
                    ));
                });
            });
            root.spawn((
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
    closes: Query<&Interaction, (Changed<Interaction>, With<ReactionLibCloseButton>)>,
    mut state: ResMut<ReactionLibState>,
    mut root_q: Query<&mut Node, With<ReactionLibRoot>>,
) {
    for i in &closes {
        if *i == Interaction::Pressed {
            state.open = false;
        }
    }
    if let Ok(mut node) = root_q.single_mut() {
        let d = if state.open { Display::Flex } else { Display::None };
        if node.display != d {
            node.display = d;
        }
    }
}

/// While the library is open, typing edits the search (Backspace deletes).
pub fn reaction_lib_search_system(
    keys: Res<ButtonInput<KeyCode>>,
    mut state: ResMut<ReactionLibState>,
    mut text_q: Query<(&mut Text, &mut TextColor), With<ReactionLibSearchText>>,
) {
    if !state.open {
        return;
    }
    let mut search = state.search.clone();
    for k in keys.get_just_pressed() {
        match k {
            KeyCode::Backspace | KeyCode::Delete => {
                search.pop();
            }
            _ => {
                if let Some(c) = keycode_to_char(*k) {
                    search.push(c);
                }
            }
        }
    }
    if search != state.search {
        state.search = search;
        if let Ok((mut text, mut color)) = text_q.single_mut() {
            if state.search.is_empty() {
                text.0 = "Type to search reactions and vessels".to_string();
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
    mut commands: Commands,
    state: Res<ReactionLibState>,
    game_data: Res<GameData>,
    substances_assets: Res<Assets<Substances>>,
    recipe_db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    list_q: Query<Entity, With<ReactionLibListContent>>,
    mut rows: Query<(&ReactionLibEntry, &mut Skin)>,
    mut count_q: Query<&mut Text, With<ReactionLibCountText>>,
    mut list_scroll: Query<(&ReactionLibScrollable, &mut ScrollPosition)>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
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
    let Ok(list) = list_q.single() else {
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
    // authored reactions by era (db.authored is already in (epoch, id) order) ...
    let authored: Vec<&Reaction> = db.authored.iter().filter(|r| known(r, &progress) && matches(r)).collect();
    // ... then any scraped reaction the player has effectively met, alphabetically.
    let mut other: Vec<&Reaction> =
        db.map.values().filter(|r| !r.is_authored() && known(r, &progress) && matches(r)).collect();
    other.sort_by_key(|r| r.name.to_lowercase());
    let total_known = db.authored.iter().filter(|r| known(r, &progress)).count();
    if let Ok(mut t) = count_q.single_mut() {
        t.0 = format!("{} of {} reactions known", total_known, db.authored.len());
    }

    commands.entity(list).despawn_children();
    commands.entity(list).with_children(|parent| {
        let mut last_epoch: Option<u8> = None;
        for r in &authored {
            if r.epoch != last_epoch {
                last_epoch = r.epoch;
                let e = r.epoch.unwrap_or(0);
                era_heading(
                    parent,
                    &fonts,
                    db.epoch_name(e),
                    db.epochs.get(e as usize).map(|d| d.era.as_str()).unwrap_or(""),
                );
            }
            list_row(parent, &fonts, &assets, r, subs, state.selected == Some(r.id));
        }
        if !other.is_empty() {
            era_heading(parent, &fonts, "Other reactions", "");
            for r in &other {
                list_row(parent, &fonts, &assets, r, subs, state.selected == Some(r.id));
            }
        }
        if authored.is_empty() && other.is_empty() {
            parent.spawn(theme::label(&fonts, "Nothing matches yet.", theme::SM, Weight::Regular, theme::TEXT_3));
        }
    });
}

fn era_heading(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, name: &str, era: &str) {
    parent
        .spawn(Node {
            align_items: AlignItems::Baseline,
            column_gap: Val::Px(8.0),
            margin: UiRect::new(Val::Px(4.0), Val::Px(0.0), Val::Px(10.0), Val::Px(2.0)),
            ..default()
        })
        .with_children(|h| {
            h.spawn(theme::label(fonts, name.to_uppercase(), theme::XS, Weight::Bold, theme::GOLD));
            if !era.is_empty() {
                h.spawn(theme::label(fonts, era, theme::XS, Weight::Regular, theme::TEXT_3));
            }
        });
}

fn list_row(
    parent: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    r: &Reaction,
    subs: &Substances,
    selected: bool,
) {
    let accent = theme::process_color(&r.process);
    let mut row = parent.spawn((
        theme::button(
            Kind::Row,
            Node {
                width: Val::Percent(100.0),
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
                width: Val::Px(36.0),
                height: Val::Px(36.0),
                flex_shrink: 0.0,
                padding: UiRect::all(Val::Px(3.0)),
                ..default()
            },
            BorderRadius::all(Val::Px(theme::R_SM)),
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
        row.spawn((Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, ..default() }, Pickable::IGNORE))
            .with_children(|c| {
                c.spawn((
                    theme::label(fonts, r.name.clone(), theme::SM, Weight::Semibold, theme::TEXT),
                    Pickable::IGNORE,
                ));
                c.spawn((
                    Text::new(equation_text(r, subs)),
                    TextFont { font: fonts.symbols.clone(), font_size: 11.0, ..default() },
                    TextColor(theme::mix(accent, theme::TEXT, 0.55)),
                    Node { max_width: Val::Px(LIST_W - 90.0), ..default() },
                    Pickable::IGNORE,
                ));
            });
    });
}

pub fn reaction_lib_entry_click_system(
    q: Query<(&Interaction, &ReactionLibEntry), (Changed<Interaction>, With<Button>)>,
    mut state: ResMut<ReactionLibState>,
) {
    for (interaction, entry) in &q {
        if *interaction == Interaction::Pressed && state.selected != Some(entry.0) {
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
) {
    // rebuild only when the selection changes (typing in the search also changes state)
    if *prev_sel == Some(state.selected) {
        return;
    }
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
                        width: Val::Px(180.0),
                        height: Val::Px(180.0),
                        flex_shrink: 0.0,
                        padding: UiRect::all(Val::Px(22.0)),
                        border: UiRect::all(Val::Px(1.0)),
                        ..default()
                    },
                    BorderRadius::all(Val::Px(theme::R_LG)),
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
                    if let Some(e) = r.epoch {
                        let era = db.epochs.get(e as usize).map(|d| d.era.clone()).unwrap_or_default();
                        let t = if era.is_empty() {
                            db.epoch_name(e).to_uppercase()
                        } else {
                            format!("{}  ·  {}", db.epoch_name(e).to_uppercase(), era)
                        };
                        info.spawn(theme::label(fonts, t, theme::XS, Weight::Bold, theme::GOLD));
                    }
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
                    if let Some((_, url)) = r.references.iter().find(|(l, _)| l.to_lowercase().contains("wiki")) {
                        info.spawn(Node { margin: UiRect::top(Val::Px(6.0)), ..default() }).with_children(|b| {
                            theme::spawn_button(
                                b,
                                fonts,
                                assets,
                                Kind::Primary,
                                Some("external"),
                                "Read on Wikipedia",
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
                padding: UiRect::axes(Val::Px(20.0), Val::Px(16.0)),
                border: UiRect::left(Val::Px(3.0)),
                ..default()
            },
            BorderRadius::all(Val::Px(theme::R_MD)),
            BackgroundColor(theme::SURFACE),
            BorderColor::all(accent),
        ))
        .with_children(|eq| {
            eq.spawn((
                Text::new(equation_text(r, subs)),
                TextFont { font: fonts.symbols.clone(), font_size: 24.0, ..default() },
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

        let others: Vec<&(String, String)> =
            r.references.iter().filter(|(l, _)| !l.to_lowercase().contains("wiki")).collect();
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
                TextFont { font: fonts.main.clone(), font_size: theme::XS, ..default() },
                TextColor(theme::TEXT_2),
                TextLayout::new_with_justify(Justify::Center),
                Node { max_width: Val::Px(108.0), ..default() },
                Pickable::IGNORE,
            ));
        });
}

/// Reference buttons open the browser; substance cards jump to the Substance Library.
pub fn reaction_lib_link_click_system(
    q: Query<(&Interaction, &ReactionLibRefLink), (Changed<Interaction>, With<Button>)>,
    subs: Query<(&Interaction, &ReactionLibSubstanceLink), (Changed<Interaction>, With<Button>)>,
    mut state: ResMut<ReactionLibState>,
    mut codex: ResMut<CodexState>,
) {
    for (interaction, link) in &q {
        if *interaction == Interaction::Pressed {
            open_url(&link.0);
        }
    }
    for (interaction, link) in &subs {
        if *interaction == Interaction::Pressed {
            state.open = false;
            codex.open = true;
            codex.selected = Some(link.0);
        }
    }
}
