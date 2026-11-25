// src/ui/curriculum.rs
//
// Learn: Curieosity's chemistry curriculum. The ideas behind the reactions, each one a
// Wikipedia article: laws and rules, concepts, techniques, industrial processes, the
// apparatus the vessels stand for, and the events of chemistry's history, in units in the
// order a course would teach them (data::pages, written by tools/data/gen_pages.py from
// tools/data/curriculum.py). A topic's page gives the article's lead, a link to the whole
// article, and where the topic is in the game: the vessels it is behind, the eras it belongs
// to, and the reactions it explains (the ones discovered so far open in the Reaction
// Library). Previous and Next walk the curriculum in order.
//
// Anything can link a topic with a LearnLink button: the Hint card, a reaction's page, a
// substance's page. Opening Learn closes the other views, and opening one of them closes
// Learn.
use bevy::prelude::*;
use bevy::ui::ScrollPosition;

use crate::data::pages::{Pages, Topic, TopicKind};
use crate::data::reactions::Reaction;
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::codex::{known_reaction, open_url, reaction_row, CodexState};
use crate::ui::process_toolbar::vessel_name;
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::tech_tree::TechTreeState;
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::ui::{Button, Clicked};
use crate::GameData;

#[derive(Resource, Default)]
pub struct CurriculumState {
    pub open: bool,
    /// the topic shown, by key
    pub selected: Option<String>,
}

const LIST_W: f32 = 360.0;

#[derive(Component)]
pub struct CurriculumRoot;
#[derive(Component)]
pub struct CurriculumClose;
#[derive(Component)]
pub struct CurriculumList;
#[derive(Component)]
pub struct CurriculumDetail;
#[derive(Component)]
pub struct CurriculumScroll {
    pub is_left: bool,
}
/// A topic's row in the list.
#[derive(Component)]
pub struct CurriculumEntry(pub String);
/// The topic's article.
#[derive(Component)]
pub struct CurriculumWiki(pub String);
/// A button anywhere that opens Learn at a topic.
#[derive(Component, Clone)]
pub struct LearnLink(pub String);

pub struct CurriculumPlugin;

impl Plugin for CurriculumPlugin {
    fn build(&self, app: &mut App) {
        // (the view itself is spawned with the rest of the interface, once the fonts are in)
        app.init_resource::<CurriculumState>().add_systems(
            Update,
            (learn_link_system, curriculum_input_system, learn_exclusive_system, curriculum_view_system).chain(),
        );
    }
}

/// Each kind's colour, for its dot in the list and its chip on the page.
pub fn kind_color(k: TopicKind) -> Color {
    match k {
        TopicKind::Law => theme::GOLD,
        TopicKind::Concept => theme::CYAN,
        TopicKind::Technique => theme::GREEN,
        TopicKind::Process => theme::mix(theme::GOLD, theme::RED, 0.45),
        TopicKind::Apparatus => theme::VIOLET,
        TopicKind::Event => theme::mix(theme::RED, theme::VIOLET, 0.35),
    }
}

/// Every topic in curriculum order: unit by unit, laws first within a unit.
pub fn ordered(pages: &Pages) -> Vec<(&str, &Topic)> {
    pages.units.iter().flat_map(|(u, _)| pages.unit_topics(u)).collect()
}

/// A button that opens Learn at `key`: "Learn: Le Chatelier's principle".
pub fn spawn_learn_button(
    parent: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    key: &str,
    topic: &Topic,
) -> Entity {
    let c = kind_color(topic.kind);
    parent
        .spawn((
            theme::button(
                Kind::Secondary,
                Node {
                    min_height: Val::Px(34.0),
                    padding: UiRect::axes(Val::Px(12.0), Val::Px(5.0)),
                    column_gap: Val::Px(7.0),
                    align_items: AlignItems::Center,
                    flex_shrink: 1.0,
                    ..default()
                },
                theme::R_MD,
            ),
            LearnLink(key.to_string()),
            crate::ui::onboarding::Tip::Text(
                "Learn",
                "Read about this idea in Learn, with a link to its Wikipedia article.",
            ),
        ))
        .with_children(|b| {
            b.spawn(theme::icon(assets, "info", 15.0, c));
            b.spawn((
                theme::label(fonts, topic.title.clone(), theme::SM, Weight::Semibold, theme::TEXT),
                Pickable::IGNORE,
            ));
        })
        .id()
}

/// A row of Learn buttons for these topic keys (unknown keys skipped).
pub fn spawn_learn_row(
    parent: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    pages: &Pages,
    keys: &[&str],
) {
    parent
        .spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(8.0), row_gap: Val::Px(8.0), ..default() })
        .with_children(|row| {
            for k in keys {
                if let Some(t) = pages.topics.get(*k) {
                    spawn_learn_button(row, fonts, assets, k, t);
                }
            }
        });
}

pub fn spawn_curriculum(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((
            CurriculumRoot,
            crate::ui::focus::FocusCover,
            crate::ui::shell::SplitRoot,
            theme::view_root(612),
            Name::new("CurriculumRoot"),
        ))
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
                        t.spawn(theme::label(fonts, "Learn", theme::XL, Weight::Semibold, theme::TEXT));
                        t.spawn(theme::label(
                            fonts,
                            "The ideas behind the reactions, from Wikipedia",
                            theme::XS,
                            Weight::Regular,
                            theme::TEXT_3,
                        ));
                    });
                    theme::spawn_icon_button(hdr, assets, "close", 32.0, theme::TEXT_2, CurriculumClose);
                });
                col.spawn((
                    CurriculumScroll { is_left: true },
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
                        CurriculumList,
                        crate::ui::focus::FocusGroup,
                        Node {
                            width: Val::Percent(100.0),
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(3.0),
                            ..default()
                        },
                    ));
                });
            });
            root.spawn((
                crate::ui::shell::SplitPane,
                CurriculumScroll { is_left: false },
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
                    CurriculumDetail,
                    Node {
                        width: Val::Percent(100.0),
                        max_width: Val::Px(900.0),
                        flex_direction: FlexDirection::Column,
                        row_gap: Val::Px(14.0),
                        ..default()
                    },
                ));
            });
        });
}

/// A LearnLink anywhere opens Learn at its topic.
pub fn learn_link_system(links: Query<&LearnLink, (With<Clicked>, With<Button>)>, mut state: ResMut<CurriculumState>) {
    if let Some(l) = links.iter().last() {
        state.open = true;
        state.selected = Some(l.0.clone());
    }
}

/// The list's rows, the close button, the article link, Previous and Next.
pub fn curriculum_input_system(
    entries: Query<&CurriculumEntry, (With<Clicked>, With<Button>)>,
    close: Query<(), (With<Clicked>, With<CurriculumClose>)>,
    wiki: Query<&CurriculumWiki, (With<Clicked>, With<Button>)>,
    mut state: ResMut<CurriculumState>,
) {
    if !close.is_empty() {
        state.open = false;
    }
    for e in &entries {
        if state.selected.as_deref() != Some(e.0.as_str()) {
            state.selected = Some(e.0.clone());
        }
    }
    for w in &wiki {
        open_url(&w.0);
    }
}

/// One view at a time: opening Learn closes the others, and another opening closes Learn.
pub fn learn_exclusive_system(
    mut state: ResMut<CurriculumState>,
    mut codex: ResMut<CodexState>,
    mut rlib: ResMut<ReactionLibState>,
    mut tree: ResMut<TechTreeState>,
    mut was: Local<bool>,
) {
    let opened = state.open && !*was;
    if opened {
        if codex.open {
            codex.open = false;
        }
        if rlib.open {
            rlib.open = false;
        }
        if tree.open {
            tree.open = false;
        }
    } else if state.open
        && ((codex.is_changed() && codex.open) || (rlib.is_changed() && rlib.open) || (tree.is_changed() && tree.open))
    {
        state.open = false;
    }
    *was = state.open;
}

/// Shows and hides the view, builds the list once the pages are in, and the page for the
/// topic shown whenever it changes (or progress changes what the player knows).
#[allow(clippy::too_many_arguments)]
pub fn curriculum_view_system(
    mut commands: Commands,
    mut state: ResMut<CurriculumState>,
    game_data: Option<Res<GameData>>,
    pages: Res<Assets<Pages>>,
    substances: Res<Assets<Substances>>,
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    look: (Res<UiFonts>, Res<AssetServer>),
    mut root: Query<&mut Node, With<CurriculumRoot>>,
    list: Query<(Entity, Option<&Children>), With<CurriculumList>>,
    detail: Query<Entity, With<CurriculumDetail>>,
    mut rows: Query<(&CurriculumEntry, &mut Skin)>,
    mut scrolls: Query<(&CurriculumScroll, &mut ScrollPosition, &ComputedNode)>,
    placed: Query<(&CurriculumEntry, &ComputedNode, &bevy::ui::UiGlobalTransform)>,
    list_box: Query<(&ComputedNode, &bevy::ui::UiGlobalTransform), With<CurriculumList>>,
    mut shown: Local<Option<String>>,
) {
    let (fonts, assets) = look;
    if let Ok(mut n) = root.single_mut() {
        let d = if state.open { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if !state.open {
        *shown = None;
        return;
    }
    let Some(pages) = game_data.as_ref().and_then(|g| pages.get(&g.pages)) else { return };
    // the list, once
    if let Ok((list_e, kids)) = list.single() {
        if kids.is_none_or(|k| k.is_empty()) {
            commands.entity(list_e).with_children(|l| spawn_list(l, &fonts, &assets, pages));
        }
    }
    if state.selected.as_ref().is_none_or(|k| !pages.topics.contains_key(k)) {
        state.selected = ordered(pages).first().map(|(k, _)| k.to_string());
    }
    let want = state.selected.clone();
    if *shown == want && !progress.is_changed() {
        return;
    }
    let fresh = *shown != want;
    *shown = want.clone();
    for (row, mut skin) in &mut rows {
        let active = want.as_deref() == Some(row.0.as_str());
        if skin.active != active {
            skin.active = active;
        }
    }
    if fresh {
        // the page starts at its top; the list brings the topic's row into sight
        let row_top = want.as_deref().and_then(|k| {
            let (_, row, at) = placed.iter().find(|(e, _, _)| e.0 == k)?;
            let (list, list_at) = list_box.single().ok()?;
            let s = row.inverse_scale_factor();
            Some(((at.translation.y - row.size.y / 2.0) - (list_at.translation.y - list.size.y / 2.0)) * s)
        });
        for (s, mut sp, view) in &mut scrolls {
            if !s.is_left {
                sp.0.y = 0.0;
            } else if let Some(y) = row_top {
                let h = view.size.y * view.inverse_scale_factor();
                if y < sp.0.y || y > sp.0.y + h - 50.0 {
                    sp.0.y = (y - 60.0).max(0.0);
                }
            }
        }
    }
    let (Ok(detail_e), Some(key)) = (detail.single(), want) else { return };
    let Some(topic) = pages.topics.get(&key) else { return };
    let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
    commands.entity(detail_e).despawn_children();
    commands.entity(detail_e).with_children(|p| {
        spawn_topic_page(p, &fonts, &assets, pages, &key, topic, db.as_deref(), subs, &progress);
    });
}

fn spawn_list(l: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer, pages: &Pages) {
    for (unit, title) in &pages.units {
        let topics = pages.unit_topics(unit);
        if topics.is_empty() {
            continue;
        }
        l.spawn((
            Node { margin: UiRect::new(Val::Px(4.0), Val::Px(0.0), Val::Px(12.0), Val::Px(4.0)), ..default() },
            Pickable::IGNORE,
        ))
        .with_child(theme::label(fonts, title.to_uppercase(), theme::XS, Weight::Bold, theme::TEXT_3));
        for (key, t) in topics {
            l.spawn((
                theme::button(
                    Kind::Row,
                    Node {
                        min_height: Val::Px(38.0),
                        align_items: AlignItems::Center,
                        column_gap: Val::Px(10.0),
                        padding: UiRect::axes(Val::Px(10.0), Val::Px(6.0)),
                        ..default()
                    },
                    theme::R_MD,
                ),
                CurriculumEntry(key.to_string()),
            ))
            .with_children(|r| {
                r.spawn((
                    Node {
                        width: Val::Px(8.0),
                        height: Val::Px(8.0),
                        flex_shrink: 0.0,
                        border_radius: BorderRadius::all(Val::Px(4.0)),
                        ..default()
                    },
                    BackgroundColor(kind_color(t.kind)),
                    Pickable::IGNORE,
                ));
                r.spawn((
                    theme::label(fonts, t.title.clone(), theme::SM, Weight::Regular, theme::TEXT),
                    Pickable::IGNORE,
                ));
            });
        }
    }
    let _ = assets;
}

#[allow(clippy::too_many_arguments)]
fn spawn_topic_page(
    p: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    pages: &Pages,
    key: &str,
    topic: &Topic,
    db: Option<&RecipeDatabase>,
    subs: Option<&Substances>,
    progress: &PlayerProgress,
) {
    let unit = pages.units.iter().find(|(u, _)| *u == topic.unit).map(|(_, t)| t.as_str()).unwrap_or("");
    p.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(6.0), row_gap: Val::Px(6.0), ..default() })
        .with_children(|chips| {
            theme::spawn_chip(chips, fonts, topic.kind.label(), kind_color(topic.kind));
            theme::spawn_chip(chips, fonts, unit, theme::TEXT_3);
        });
    p.spawn(theme::para(fonts, topic.title.clone(), theme::XXL, theme::TEXT, Val::Px(860.0)));
    if topic.lead.trim().is_empty() {
        p.spawn(theme::para(
            fonts,
            "Its article is on Wikipedia.".to_string(),
            theme::MD,
            theme::TEXT_2,
            Val::Px(860.0),
        ));
    }
    for line in topic.lead.lines().map(str::trim).filter(|l| !l.is_empty()) {
        p.spawn(theme::para(fonts, line.to_string(), theme::MD, theme::TEXT_2, Val::Px(860.0)));
    }
    p.spawn(Node { column_gap: Val::Px(10.0), flex_wrap: FlexWrap::Wrap, row_gap: Val::Px(8.0), ..default() })
        .with_children(|b| {
            theme::spawn_button(
                b,
                fonts,
                assets,
                Kind::Primary,
                Some("external"),
                "Read on Wikipedia",
                CurriculumWiki(topic.url.clone()),
            );
        });
    if !topic.lead.trim().is_empty() {
        p.spawn(theme::para(
            fonts,
            format!("From Wikipedia's article \u{201c}{}\u{201d}, shortened. CC BY-SA 4.0.", topic.title),
            theme::XS,
            theme::TEXT_3,
            Val::Px(860.0),
        ));
    }

    // --- where it is in the game ---
    let vessels = pages.vessels_of(key);
    let eras: Vec<&str> =
        pages.eras.iter().filter(|(_, ts)| ts.iter().any(|t| t == key)).map(|(e, _)| e.as_str()).collect();
    let reactions: Vec<&Reaction> = match db {
        Some(db) => {
            let ids = pages.reactions_of(key);
            db.authored.iter().filter(|r| ids.contains(&r.id)).collect()
        }
        None => Vec::new(),
    };
    if !vessels.is_empty() || !eras.is_empty() {
        theme::spawn_section_title(p, fonts, "In the game");
        p.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(6.0), row_gap: Val::Px(6.0), ..default() })
            .with_children(|chips| {
                for v in &vessels {
                    theme::spawn_chip(chips, fonts, vessel_name(v), theme::process_color(v));
                }
                for e in &eras {
                    theme::spawn_chip(chips, fonts, &format!("The {e} era"), theme::GOLD);
                }
            });
    }
    if !reactions.is_empty() {
        theme::spawn_section_title(p, fonts, "Reactions it explains");
        let known: Vec<&&Reaction> = reactions.iter().filter(|r| known_reaction(r, progress)).collect();
        if let Some(subs) = subs {
            for r in known.iter().take(12) {
                reaction_row(p, fonts, assets, r, subs);
            }
        }
        let more = reactions.len() - known.len().min(12);
        if more > 0 {
            p.spawn(theme::label(
                fonts,
                if known.is_empty() {
                    format!("{more} you haven't discovered yet.")
                } else {
                    format!("{more} more{}", if known.len() > 12 { "." } else { " you haven't discovered yet." })
                },
                theme::SM,
                Weight::Regular,
                theme::TEXT_3,
            ));
        }
    }

    // --- walking the curriculum ---
    let order = ordered(pages);
    if let Some(i) = order.iter().position(|(k, _)| *k == key) {
        let prev = i.checked_sub(1).and_then(|j| order.get(j));
        let next = order.get(i + 1);
        p.spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            column_gap: Val::Px(10.0),
            flex_wrap: FlexWrap::Wrap,
            row_gap: Val::Px(8.0),
            margin: UiRect::top(Val::Px(10.0)),
            ..default()
        })
        .with_children(|row| {
            match prev {
                Some((k, t)) => {
                    theme::spawn_button(
                        row,
                        fonts,
                        assets,
                        Kind::Secondary,
                        None,
                        &format!("Back: {}", t.title),
                        CurriculumEntry(k.to_string()),
                    );
                }
                None => {
                    row.spawn(Node::default());
                }
            }
            if let Some((k, t)) = next {
                theme::spawn_button(
                    row,
                    fonts,
                    assets,
                    Kind::Secondary,
                    None,
                    &format!("Next: {}", t.title),
                    CurriculumEntry(k.to_string()),
                );
            }
        });
    }
}
