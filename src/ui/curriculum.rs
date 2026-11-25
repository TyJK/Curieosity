// src/ui/curriculum.rs
//
// Lessons: Curieosity's chemistry curriculum. The ideas behind the reactions, each one a
// Wikipedia article: laws and rules, concepts, techniques, industrial processes, the
// apparatus the vessels stand for, and the events of chemistry's history, in units in the
// order a course would teach them (data::pages, written by tools/data/gen_pages.py from
// tools/data/curriculum.py); then the Glossary, every chemistry word the pages define
// (tools/data/glossary.py). A search box narrows both.
//
// The list fills the screen; a tap opens a lesson in its place (Back returns to the list
// where it was left). A lesson's page gives the article's lead with its chemistry words
// marked and defined (ui::glossary), a link to the whole article, and where the topic is in
// the game: the vessels it is behind, the eras it belongs to, and the reactions it explains
// (the ones discovered so far open in the Reaction Library). Back and Next walk the
// curriculum in order. A glossary word's page gives its definition and its links.
//
// Anything can link a topic with a LearnLink button: the Hint card, a reaction's page, a
// substance's page, a definition. Opening Lessons closes the other views, and opening one of
// them closes Lessons. (In the code the view is still `Learn`, its first name.)
use bevy::prelude::*;
use bevy::ui::ScrollPosition;

use crate::data::pages::{Pages, Term, Topic, TopicKind};
use crate::data::reactions::Reaction;
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::codex::{known_reaction, open_url, reaction_row, typed, CodexState, PAGE_W};
use crate::ui::glossary::{spawn_definition, spawn_glossed_para, spawn_term_row, TERM_COLOR};
use crate::ui::process_toolbar::vessel_name;
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::shell::{PaneList, PanePad, PanePage, View};
use crate::ui::tech_tree::TechTreeState;
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::ui::{Button, Clicked};
use crate::GameData;

#[derive(Resource, Default)]
pub struct CurriculumState {
    pub open: bool,
    /// the lesson shown, by topic key, or a glossary word's as "term:" and its key
    pub selected: Option<String>,
    /// showing the selected lesson's page, rather than the list
    pub page: bool,
    /// what the search box holds
    pub search: String,
}

impl CurriculumState {
    /// Open Lessons at a topic's (or a "term:" key's) page.
    pub fn show(&mut self, key: &str) {
        self.open = true;
        self.selected = Some(key.to_string());
        self.page = true;
    }
}

/// A glossary word's key in the list: its term key after this.
pub const TERM_PREFIX: &str = "term:";

/// How wide the list runs at most on a big screen.
const LIST_MAX_W: f32 = 1180.0;

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
/// A lesson's (or a glossary word's) entry in the list, by key.
#[derive(Component)]
pub struct CurriculumEntry(pub String);
/// What a search matches an entry by, lowercase: its title, and a word's definition.
#[derive(Component)]
pub struct LessonText(pub String);
/// A unit's heading and its entries, hidden as a whole when a search leaves none of them.
#[derive(Component)]
pub struct LessonGroup;
/// The search box, and its text.
#[derive(Component)]
pub struct LessonsSearchBox;
#[derive(Component)]
pub struct LessonsSearchText;
/// "447 lessons and 207 words", or how many a search found.
#[derive(Component)]
pub struct LessonsCount;
/// "Nothing matches.", under the list.
#[derive(Component)]
pub struct LessonsEmpty;
/// The topic's article.
#[derive(Component)]
pub struct CurriculumWiki(pub String);
/// A button anywhere that opens Lessons at a topic.
#[derive(Component, Clone)]
pub struct LearnLink(pub String);

pub struct CurriculumPlugin;

impl Plugin for CurriculumPlugin {
    fn build(&self, app: &mut App) {
        // (the view itself is spawned with the rest of the interface, once the fonts are in)
        app.init_resource::<CurriculumState>().add_systems(
            Update,
            (
                learn_link_system,
                curriculum_input_system,
                learn_exclusive_system,
                lessons_search_system,
                curriculum_view_system,
                lessons_filter_system,
            )
                .chain(),
        );
    }
}

/// Each kind's colour, for its mark in the list and its chip on the page.
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

/// Every glossary word, alphabetically (the "-ate and -ite" endings by their letters).
pub fn glossary_order(pages: &Pages) -> Vec<(&str, &Term)> {
    let mut v: Vec<(&str, &Term)> = pages.glossary.iter().map(|(k, t)| (k.as_str(), t)).collect();
    v.sort_by_cached_key(|(_, t)| t.term.trim_start_matches('-').to_lowercase());
    v
}

/// A button that opens Lessons at `key`: "Le Chatelier's principle", with the lesson mark.
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
                    min_height: Val::Px(38.0),
                    padding: UiRect::axes(Val::Px(12.0), Val::Px(5.0)),
                    column_gap: Val::Px(8.0),
                    align_items: AlignItems::Center,
                    flex_shrink: 1.0,
                    ..default()
                },
                theme::R_MD,
            ),
            LearnLink(key.to_string()),
            crate::ui::onboarding::Tip::Text(
                "Lessons",
                "Read about this idea in Lessons, with a link to its Wikipedia article.",
            ),
        ))
        .with_children(|b| {
            b.spawn(theme::icon(assets, "info", 16.0, c));
            b.spawn((
                theme::label(fonts, topic.title.clone(), theme::SM, Weight::Semibold, theme::TEXT),
                Pickable::IGNORE,
            ));
        })
        .id()
}

/// A row of lesson buttons for these topic keys (unknown keys skipped).
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

/// What the empty search box says.
fn search_prompt() -> &'static str {
    if crate::platform::SOFT_KEYBOARD {
        "Tap to search lessons and words"
    } else {
        "Type to search lessons and words"
    }
}

pub fn spawn_curriculum(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((CurriculumRoot, crate::ui::focus::FocusCover, theme::view_root(612), Name::new("CurriculumRoot")))
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
            // --- the list: header, search, the units and the glossary ---
            root.spawn((
                PaneList(View::Learn),
                PanePad(28.0, 14.0, 0.0),
                Node {
                    width: Val::Percent(100.0),
                    height: Val::Percent(100.0),
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(10.0),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
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
                        t.spawn(theme::label(fonts, "Lessons", theme::XL, Weight::Semibold, theme::TEXT));
                        t.spawn((
                            LessonsCount,
                            theme::label(
                                fonts,
                                "The ideas behind the reactions, from Wikipedia",
                                theme::XS,
                                Weight::Regular,
                                theme::TEXT_3,
                            ),
                        ));
                    });
                    theme::spawn_icon_button(hdr, assets, "close", 40.0, theme::TEXT_2, CurriculumClose);
                });
                col.spawn((
                    theme::button(
                        Kind::Secondary,
                        Node {
                            height: Val::Px(42.0),
                            max_width: Val::Px(620.0),
                            flex_shrink: 0.0,
                            align_items: AlignItems::Center,
                            column_gap: Val::Px(9.0),
                            padding: UiRect::horizontal(Val::Px(12.0)),
                            ..default()
                        },
                        theme::R_MD,
                    ),
                    LessonsSearchBox,
                ))
                .with_children(|s| {
                    s.spawn(theme::icon(assets, "search", 17.0, theme::TEXT_3));
                    s.spawn((
                        LessonsSearchText,
                        theme::label(fonts, search_prompt(), theme::SM, Weight::Regular, theme::TEXT_3),
                    ));
                });
                col.spawn((
                    CurriculumScroll { is_left: true },
                    ScrollPosition::default(),
                    Node {
                        flex_direction: FlexDirection::Column,
                        align_items: AlignItems::Center,
                        flex_grow: 1.0,
                        flex_basis: Val::Px(0.0),
                        min_height: Val::Px(0.0),
                        overflow: Overflow::scroll_y(),
                        padding: UiRect::bottom(Val::Px(20.0)),
                        ..default()
                    },
                ))
                .with_children(|scroll| {
                    scroll.spawn((
                        CurriculumList,
                        crate::ui::focus::FocusGroup,
                        Node {
                            width: Val::Percent(100.0),
                            max_width: Val::Px(LIST_MAX_W),
                            flex_shrink: 0.0,
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(4.0),
                            ..default()
                        },
                    ));
                    scroll.spawn((
                        LessonsEmpty,
                        theme::label(fonts, "Nothing matches.", theme::SM, Weight::Regular, theme::TEXT_3),
                        Node { display: Display::None, margin: UiRect::top(Val::Px(20.0)), ..default() },
                    ));
                });
            });
            // --- the page, in the list's place ---
            root.spawn((
                PanePage(View::Learn),
                Node {
                    width: Val::Percent(100.0),
                    height: Val::Percent(100.0),
                    flex_direction: FlexDirection::Column,
                    display: Display::None,
                    ..default()
                },
            ))
            .with_children(|page| {
                crate::ui::shell::spawn_page_bar(page, fonts, assets, View::Learn, "Lessons", CurriculumClose);
                page.spawn((
                    CurriculumScroll { is_left: false },
                    ScrollPosition::default(),
                    PanePad(32.0, 22.0, 40.0),
                    Node {
                        flex_grow: 1.0,
                        flex_basis: Val::Px(0.0),
                        min_height: Val::Px(0.0),
                        flex_direction: FlexDirection::Column,
                        align_items: AlignItems::Center,
                        overflow: Overflow::scroll_y(),
                        ..default()
                    },
                ))
                .with_children(|pane| {
                    pane.spawn((
                        CurriculumDetail,
                        Node {
                            width: Val::Percent(100.0),
                            max_width: Val::Px(PAGE_W),
                            flex_shrink: 0.0,
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(14.0),
                            ..default()
                        },
                    ));
                });
            });
        });
}

/// A LearnLink anywhere opens Lessons at its topic's page.
pub fn learn_link_system(links: Query<&LearnLink, (With<Clicked>, With<Button>)>, mut state: ResMut<CurriculumState>) {
    if let Some(l) = links.iter().last() {
        state.show(&l.0);
    }
}

/// The list's entries, the close button, the article link, Back and Next.
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
        if state.selected.as_deref() != Some(e.0.as_str()) || !state.page {
            state.show(&e.0);
        }
    }
    for w in &wiki {
        open_url(&w.0);
    }
}

/// One view at a time: opening Lessons closes the others, and another opening closes it.
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

/// While the list is showing, typing edits the search (Backspace deletes); on a phone a tap
/// on the box brings up the keyboard, whose text becomes the search.
pub fn lessons_search_system(
    keys: Res<ButtonInput<KeyCode>>,
    mut state: ResMut<CurriculumState>,
    mut text_q: Query<(&mut Text, &mut TextColor), With<LessonsSearchText>>,
    boxes: Query<(), (With<Clicked>, With<LessonsSearchBox>)>,
    mut typing: ResMut<crate::ui::inventory::TypingBox>,
) {
    use crate::ui::inventory::TypingBox;
    if !state.open || state.page {
        if *typing == TypingBox::Lessons {
            *typing = TypingBox::None;
            crate::platform::keyboard_hide();
        }
        return;
    }
    if !boxes.is_empty() {
        *typing = TypingBox::Lessons;
        crate::platform::keyboard_show(&state.search);
    }
    let keyboard = crate::platform::keyboard_text().filter(|_| *typing == TypingBox::Lessons);
    let (search, _) = typed(&state.search, &keys, keyboard);
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

/// Shows and hides the view, builds the list once the pages are in, and the page for the
/// entry shown whenever it changes (or progress changes what the player knows).
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
    mut scrolls: Query<(&CurriculumScroll, &mut ScrollPosition)>,
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
        return;
    }
    let Some(pages) = game_data.as_ref().and_then(|g| pages.get(&g.pages)) else { return };
    // the list, once
    if let Ok((list_e, kids)) = list.single() {
        if kids.is_none_or(|k| k.is_empty()) {
            commands.entity(list_e).with_children(|l| spawn_list(l, &fonts, pages));
        }
    }
    let valid = |k: &str| match k.strip_prefix(TERM_PREFIX) {
        Some(t) => pages.glossary.contains_key(t),
        None => pages.topics.contains_key(k),
    };
    if state.selected.as_deref().is_some_and(|k| !valid(k)) {
        state.selected = None;
        state.page = false;
    }
    if state.page && state.selected.is_none() {
        state.page = false;
    }
    let want = state.selected.clone();
    if !state.page || (*shown == want && !progress.is_changed()) {
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
        // a page starts at its top (the list keeps its place)
        for (s, mut sp) in &mut scrolls {
            if !s.is_left && sp.0.y != 0.0 {
                sp.0.y = 0.0;
            }
        }
    }
    let (Ok(detail_e), Some(key)) = (detail.single(), want) else { return };
    commands.entity(detail_e).despawn_children();
    if let Some(term_key) = key.strip_prefix(TERM_PREFIX) {
        let Some(term) = pages.glossary.get(term_key) else { return };
        commands.entity(detail_e).with_children(|p| spawn_term_page(p, &fonts, &assets, pages, term_key, term));
        return;
    }
    let Some(topic) = pages.topics.get(&key) else { return };
    let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
    commands.entity(detail_e).with_children(|p| {
        spawn_topic_page(p, &fonts, &assets, pages, &key, topic, db.as_deref(), subs, &progress);
    });
}

/// The search narrows the list: entries whose title (or a word's definition) holds it, and
/// the units that still have any. Writes only when the search changes.
#[allow(clippy::type_complexity)]
pub fn lessons_filter_system(
    state: Res<CurriculumState>,
    mut entries: Query<(&LessonText, &mut Node), (Without<LessonGroup>, Without<LessonsEmpty>)>,
    mut groups: Query<(&Children, &mut Node), (With<LessonGroup>, Without<LessonsEmpty>)>,
    kids: Query<&Children>,
    mut empty: Query<&mut Node, (With<LessonsEmpty>, Without<LessonText>, Without<LessonGroup>)>,
    mut count: Query<&mut Text, With<LessonsCount>>,
    added: Query<(), Added<LessonText>>,
    mut last: Local<Option<String>>,
) {
    if last.as_deref() == Some(state.search.as_str()) && added.is_empty() {
        return;
    }
    *last = Some(state.search.clone());
    let q = state.search.trim().to_lowercase();
    let mut shown = 0;
    for (text, mut n) in &mut entries {
        let hit = q.is_empty() || text.0.contains(&q);
        shown += hit as usize;
        let d = if hit { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    let total = entries.iter().count();
    for (children, mut n) in &mut groups {
        // the group's wrap of entries is its last child
        let any = children
            .iter()
            .filter_map(|c| kids.get(c).ok())
            .flat_map(|w| w.iter())
            .any(|e| entries.get(e).is_ok_and(|(_, n)| n.display != Display::None));
        let d = if any { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if let Ok(mut n) = empty.single_mut() {
        let d = if shown == 0 && total > 0 { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if let Ok(mut t) = count.single_mut() {
        if total > 0 {
            t.0 = if q.is_empty() {
                "The ideas behind the reactions, and the words they use, from Wikipedia".to_string()
            } else {
                format!("{shown} of {total} lessons and words match")
            };
        }
    }
}

/// The units, each a heading over its lessons as cards that fill the width; then the
/// Glossary, every word as a smaller card.
fn spawn_list(l: &mut ChildSpawnerCommands, fonts: &UiFonts, pages: &Pages) {
    let heading = |g: &mut ChildSpawnerCommands, title: &str, sub: &str| {
        g.spawn((
            Node {
                margin: UiRect::new(Val::Px(2.0), Val::Px(0.0), Val::Px(16.0), Val::Px(6.0)),
                column_gap: Val::Px(10.0),
                align_items: AlignItems::Baseline,
                flex_wrap: FlexWrap::Wrap,
                ..default()
            },
            Pickable::IGNORE,
        ))
        .with_children(|h| {
            h.spawn(theme::label(fonts, title.to_uppercase(), theme::SM, Weight::Bold, theme::GOLD));
            if !sub.is_empty() {
                h.spawn(theme::label(fonts, sub, theme::XS, Weight::Regular, theme::TEXT_3));
            }
        });
    };
    let wrap = || Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(8.0), row_gap: Val::Px(8.0), ..default() };
    for (unit, title) in &pages.units {
        let topics = pages.unit_topics(unit);
        if topics.is_empty() {
            continue;
        }
        l.spawn((LessonGroup, Node { flex_direction: FlexDirection::Column, ..default() })).with_children(|g| {
            heading(g, title, &format!("{} lessons", topics.len()));
            g.spawn(wrap()).with_children(|w| {
                for (key, t) in topics {
                    let find = t.title.to_lowercase();
                    spawn_lesson_card(w, fonts, key, &t.title, kind_color(t.kind), t.kind.label(), 250.0, find);
                }
            });
        });
    }
    let words = glossary_order(pages);
    if !words.is_empty() {
        l.spawn((LessonGroup, Node { flex_direction: FlexDirection::Column, ..default() })).with_children(|g| {
            heading(g, "Glossary", "the chemistry words the pages use, defined");
            g.spawn(wrap()).with_children(|w| {
                for (key, t) in words {
                    // a word is found by what it means too
                    let find = format!("{} {}", t.term, t.text).to_lowercase();
                    spawn_lesson_card(w, fonts, &format!("{TERM_PREFIX}{key}"), &t.term, TERM_COLOR, "", 170.0, find);
                }
            });
        });
    }
}

/// One entry: a mark in its kind's colour and the title; it grows to share its row. A
/// search finds it by `find`.
#[allow(clippy::too_many_arguments)]
fn spawn_lesson_card(
    w: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    key: &str,
    title: &str,
    color: Color,
    kind: &str,
    basis: f32,
    find: String,
) {
    w.spawn((
        theme::button(
            Kind::Row,
            Node {
                min_height: Val::Px(46.0),
                flex_basis: Val::Px(basis),
                flex_grow: 1.0,
                max_width: Val::Px(basis * 1.6),
                align_items: AlignItems::Center,
                column_gap: Val::Px(10.0),
                padding: UiRect::new(Val::Px(8.0), Val::Px(12.0), Val::Px(7.0), Val::Px(7.0)),
                ..default()
            },
            theme::R_MD,
        ),
        CurriculumEntry(key.to_string()),
        LessonText(find),
    ))
    .with_children(|r| {
        // its kind's mark: a bar down the left
        r.spawn((
            Node {
                width: Val::Px(4.0),
                align_self: AlignSelf::Stretch,
                flex_shrink: 0.0,
                border_radius: BorderRadius::all(Val::Px(2.0)),
                ..default()
            },
            BackgroundColor(color.with_alpha(0.9)),
            Pickable::IGNORE,
        ));
        r.spawn((Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, ..default() }, Pickable::IGNORE))
            .with_children(|c| {
                c.spawn((
                    theme::para(fonts, title.to_string(), theme::MD, theme::TEXT, Val::Percent(100.0)),
                    Pickable::IGNORE,
                ));
                if !kind.is_empty() {
                    c.spawn((
                        theme::label(fonts, kind, theme::XS, Weight::Semibold, theme::mix(color, theme::TEXT, 0.3)),
                        Pickable::IGNORE,
                    ));
                }
            });
    });
}

/// Back and Next along a list of (key, title).
fn spawn_walk(
    p: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    prev: Option<(String, String)>,
    next: Option<(String, String)>,
) {
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
                    &format!("Back: {t}"),
                    CurriculumEntry(k),
                );
            }
            None => {
                row.spawn(Node::default());
            }
        }
        if let Some((k, t)) = next {
            theme::spawn_button(row, fonts, assets, Kind::Secondary, None, &format!("Next: {t}"), CurriculumEntry(k));
        }
    });
}

/// A glossary word's page: its definition and links, and Back and Next through the words.
fn spawn_term_page(
    p: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    pages: &Pages,
    key: &str,
    term: &Term,
) {
    p.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(6.0), row_gap: Val::Px(6.0), ..default() })
        .with_children(|chips| theme::spawn_chip(chips, fonts, "Glossary", TERM_COLOR));
    spawn_definition(p, fonts, assets, pages, term);
    let order = glossary_order(pages);
    if let Some(i) = order.iter().position(|(k, _)| *k == key) {
        let at = |j: usize| order.get(j).map(|(k, t)| (format!("{TERM_PREFIX}{k}"), t.term.clone()));
        spawn_walk(p, fonts, assets, i.checked_sub(1).and_then(at), at(i + 1));
    }
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
    let full = Val::Percent(100.0);
    let unit = pages.units.iter().find(|(u, _)| *u == topic.unit).map(|(_, t)| t.as_str()).unwrap_or("");
    p.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(6.0), row_gap: Val::Px(6.0), ..default() })
        .with_children(|chips| {
            theme::spawn_chip(chips, fonts, topic.kind.label(), kind_color(topic.kind));
            theme::spawn_chip(chips, fonts, unit, theme::TEXT_3);
        });
    p.spawn(theme::para(fonts, topic.title.clone(), theme::XXL, theme::TEXT, full));
    if topic.lead.trim().is_empty() {
        p.spawn(theme::para(fonts, "Its article is on Wikipedia.".to_string(), theme::MD, theme::TEXT_2, full));
    }
    let no_terms = Vec::new();
    let terms = pages.topic_terms.get(key).unwrap_or(&no_terms);
    let mut seen = Vec::new();
    for line in topic.lead.lines().map(str::trim).filter(|l| !l.is_empty()) {
        spawn_glossed_para(p, fonts, Some(pages), terms, &mut seen, line, theme::MD, theme::TEXT, full);
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
            full,
        ));
    }
    spawn_term_row(p, fonts, pages, terms);

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
        let at = |j: usize| order.get(j).map(|(k, t)| (k.to_string(), t.title.clone()));
        spawn_walk(p, fonts, assets, i.checked_sub(1).and_then(at), at(i + 1));
    }
}
