// src/ui/discovery_card.rs
//
// The discovery card. Each substance the player makes for the first time arrives as a
// sealed card at the top right of the bench: "New discovery: Butter, tap to read". Tapping
// it opens it over the whole lab: a big picture (the Bohr model of an element, the drawn
// structure of a compound), the substance's story (how an element was found, what a
// compound is and where it turns up), how it is made and how many recipes it goes into, its
// facts and uses, and buttons for its Wikipedia article, its Substance Library page and Got
// it; the next card waits its turn behind it. A
// sealed card isn't dismissed unread, unless the "Close by themselves" setting lets it go
// after CARD_TIMEOUT seconds. With cards off (Settings), a discovery is a toast as before.
use std::collections::VecDeque;

use bevy::prelude::*;

use crate::components::format_formula;
use crate::data::substances::{Substance, Substances};
use crate::resources::ui_fonts::UiFonts;
use crate::systems::autoplay::GameEvent;
use crate::ui::codex::CodexState;
use crate::ui::settings::Settings;
use crate::ui::theme::{self, Kind, Weight};
use crate::ui::Clicked;
use crate::GameData;

/// How long a sealed card waits to be opened when cards close by themselves (seconds).
pub const CARD_TIMEOUT: f64 = 15.0;
/// The longest story a card tells, in characters (cut at a sentence).
const STORY_MAX: usize = 1100;
const CARD_W: f32 = 380.0;
/// The open card's widest (it fills the lab up to this).
const PAGE_W: f32 = 860.0;

/// The cards waiting, the front one showing; `open` once it has been tapped.
#[derive(Resource, Default, Debug)]
pub struct DiscoveryCards {
    pub queue: VecDeque<u32>,
    pub open: bool,
    /// when the front card arrived (real seconds), for the timeout
    pub since: f64,
}

impl DiscoveryCards {
    /// Whether a card is open over the lab.
    pub fn is_open(&self) -> bool {
        self.open && !self.queue.is_empty()
    }

    /// Got it, from outside the card (Esc).
    pub fn dismiss(&mut self, now: f64) {
        self.next(now);
    }

    /// The front card is done with: the next one comes up, sealed.
    fn next(&mut self, now: f64) {
        self.queue.pop_front();
        self.open = false;
        self.since = now;
    }
}

#[derive(Component)]
pub struct DiscoveryCardRoot;
/// The sealed card: tap to open.
#[derive(Component)]
pub struct DiscoveryCardSealed;
/// The open card's story.
#[derive(Component)]
pub struct DiscoveryCardStory;
#[derive(Component)]
pub struct DiscoveryCardGotIt;
#[derive(Component)]
pub struct DiscoveryCardReadMore;
#[derive(Component)]
pub struct DiscoveryCardWiki(pub String);

/// What the card tells about a substance: an element's discovery, or the game's own line
/// about it, then the Wikipedia article's lead as far as it fits, cut at a sentence. With no
/// article, an element's overview or the library's description.
pub fn card_story(sub: &Substance, page: Option<&crate::data::pages::SubstancePage>) -> String {
    let ours = sub.text_source.as_deref() == Some(crate::data::substances::CURIEOSITY);
    let mut parts: Vec<String> = Vec::new();
    if let Some(d) = sub.element_info.as_ref().and_then(|e| e.discovery_story.clone()) {
        parts.push(d);
    } else if ours {
        parts.extend(sub.description.clone());
    }
    match page {
        // an article on a related subject is for the Library page, not the card's story
        Some(pg) if pg.about.is_none() => {
            parts.extend(pg.lead.lines().map(str::trim).filter(|l| !l.is_empty()).map(String::from))
        }
        Some(_) => parts.extend(sub.description.clone().filter(|_| !ours)),
        None => {
            parts.extend(sub.element_info.as_ref().and_then(|e| e.overview.clone()).or_else(|| sub.description.clone()))
        }
    }
    let mut out = String::new();
    for part in parts.iter().flat_map(|p| p.lines()).map(str::trim).filter(|l| !l.is_empty()) {
        if out.contains(part) {
            continue;
        }
        let sep = if out.is_empty() { "" } else { "\n\n" };
        if out.chars().count() + sep.len() + part.chars().count() <= STORY_MAX {
            out = format!("{out}{sep}{part}");
            continue;
        }
        // the last full sentence that fits, or (for the first part) a clean cut
        let room = STORY_MAX.saturating_sub(out.chars().count() + sep.len());
        let cut: String = part.chars().take(room).collect();
        match cut.rfind(". ") {
            Some(i) if i > room / 3 => out = format!("{out}{sep}{}", &cut[..=i]),
            _ if out.is_empty() => out = format!("{}…", cut.trim_end()),
            _ => {}
        }
        break;
    }
    out
}

/// New discoveries join the queue (while cards are on).
pub fn discovery_card_feed_system(
    mut events: MessageReader<GameEvent>,
    settings: Option<Res<Settings>>,
    mut cards: ResMut<DiscoveryCards>,
    time: Res<Time<Real>>,
) {
    let on = settings.as_ref().is_none_or(|s| s.discovery_cards);
    if !on {
        events.clear();
        if !cards.queue.is_empty() {
            *cards = DiscoveryCards::default();
        }
        return;
    }
    for ev in events.read() {
        if let GameEvent::Discovery { id } = ev {
            if cards.queue.is_empty() {
                cards.since = time.elapsed_secs_f64();
            }
            if !cards.queue.contains(id) {
                cards.queue.push_back(*id);
            }
        }
    }
}

/// Opening, Got it, Read more, and the timeout.
pub fn discovery_card_input_system(
    mut cards: ResMut<DiscoveryCards>,
    settings: Option<Res<Settings>>,
    time: Res<Time<Real>>,
    sealed: Query<(), (With<Clicked>, With<DiscoveryCardSealed>)>,
    got: Query<(), (With<Clicked>, With<DiscoveryCardGotIt>)>,
    more: Query<(), (With<Clicked>, With<DiscoveryCardReadMore>)>,
    wiki: Query<&DiscoveryCardWiki, With<Clicked>>,
    mut codex: ResMut<CodexState>,
) {
    let now = time.elapsed_secs_f64();
    let Some(&id) = cards.queue.front() else { return };
    for w in &wiki {
        crate::platform::open_url(&w.0);
    }
    if !sealed.is_empty() {
        cards.open = true;
    } else if !got.is_empty() {
        cards.next(now);
    } else if !more.is_empty() {
        codex.open = true;
        codex.selected = Some(id);
        cards.next(now);
    } else if !cards.open
        && settings.as_ref().is_some_and(|s| s.cards_close_themselves)
        && now - cards.since >= CARD_TIMEOUT
    {
        cards.next(now);
    }
}

pub fn spawn_discovery_card_ui(mut commands: Commands) {
    commands.spawn((
        DiscoveryCardRoot,
        GlobalZIndex(650),
        sealed_layout(),
        BackgroundColor(Color::NONE),
        Pickable::IGNORE,
        Name::new("DiscoveryCard"),
    ));
}

/// Where the sealed card sits: the top right of the bench.
fn sealed_layout() -> Node {
    Node {
        position_type: PositionType::Absolute,
        top: Val::Px(theme::HEADER_H + 12.0),
        right: Val::Px(14.0),
        width: Val::Px(CARD_W),
        max_width: Val::Percent(90.0),
        flex_direction: FlexDirection::Column,
        align_items: AlignItems::FlexEnd,
        display: Display::None,
        ..default()
    }
}

/// The open card: over the whole lab, under the header.
fn page_layout() -> Node {
    Node {
        position_type: PositionType::Absolute,
        top: Val::Px(theme::HEADER_H),
        left: Val::Px(0.0),
        right: Val::Px(0.0),
        bottom: Val::Px(0.0),
        flex_direction: FlexDirection::Column,
        align_items: AlignItems::Center,
        padding: UiRect::all(Val::Px(12.0)),
        ..default()
    }
}

/// Builds the front card, sealed or open, whenever the queue or its state changes.
#[allow(clippy::too_many_arguments)]
pub fn discovery_card_view_system(
    mut commands: Commands,
    cards: Res<DiscoveryCards>,
    fonts: Option<Res<UiFonts>>,
    assets: Res<AssetServer>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    db: Option<Res<crate::resources::recipe_database::RecipeDatabase>>,
    pages: Res<Assets<crate::data::pages::Pages>>,
    mut root: Query<(Entity, &mut Node, &mut BackgroundColor, Option<&Children>), With<DiscoveryCardRoot>>,
    mut shown: Local<Option<(u32, bool, usize)>>,
) {
    let Ok((root_e, mut node, mut bg, children)) = root.single_mut() else { return };
    let Some(fonts) = fonts else { return };
    let want = cards.queue.front().map(|id| (*id, cards.open, cards.queue.len()));
    if *shown == want {
        return;
    }
    let subs = game_data.as_ref().and_then(|g| substances.get(&g.substances));
    let Some((id, open, waiting)) = want else {
        *shown = None;
        node.display = Display::None;
        if let Some(c) = children {
            for e in c.iter() {
                commands.entity(e).try_despawn();
            }
        }
        return;
    };
    let Some(sub) = subs.and_then(|s| s.0.get(&id)) else { return };
    let page = crate::ui::codex::page_of(game_data.as_ref().and_then(|g| pages.get(&g.pages)), id);
    *shown = want;
    *node = if open { page_layout() } else { Node { display: Display::Flex, ..sealed_layout() } };
    // open, it covers the lab (and a tap on what's around the card goes nowhere)
    bg.0 = if open { Color::srgba(0.0, 0.0, 0.03, 0.82) } else { Color::NONE };
    commands.entity(root_e).insert(if open { Pickable::default() } else { Pickable::IGNORE });
    if let Some(c) = children {
        for e in c.iter() {
            commands.entity(e).try_despawn();
        }
    }
    let green = theme::GREEN;
    let more = if waiting > 1 { format!("  ·  {} more", waiting - 1) } else { String::new() };
    commands.entity(root_e).with_children(|r| {
        if !open {
            r.spawn((
                theme::button(
                    Kind::Accent(green),
                    Node {
                        padding: UiRect::axes(Val::Px(14.0), Val::Px(9.0)),
                        column_gap: Val::Px(10.0),
                        align_items: AlignItems::Center,
                        max_width: Val::Px(CARD_W),
                        ..default()
                    },
                    theme::R_MD,
                ),
                DiscoveryCardSealed,
                theme::shadow(16.0, 6.0, 0.55),
                crate::ui::onboarding::Tip::Text("New discovery", "Tap to read about it."),
            ))
            .with_children(|b| {
                b.spawn(theme::icon(&assets, "flask", 20.0, green));
                b.spawn((
                    Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, ..default() },
                    Pickable::IGNORE,
                ))
                .with_children(|t| {
                    t.spawn((
                        theme::label(&fonts, format!("NEW DISCOVERY{more}"), theme::XS, Weight::Bold, green),
                        Pickable::IGNORE,
                    ));
                    t.spawn((
                        theme::label(&fonts, sub.name.clone(), theme::MD, Weight::Semibold, theme::TEXT),
                        Pickable::IGNORE,
                    ));
                    t.spawn((
                        theme::label(&fonts, "Tap to read", theme::XS, Weight::Regular, theme::TEXT_2),
                        Pickable::IGNORE,
                    ));
                });
            });
            return;
        }
        r.spawn((
            Node {
                width: Val::Percent(100.0),
                max_width: Val::Px(PAGE_W),
                max_height: Val::Percent(100.0),
                flex_direction: FlexDirection::Column,
                border: UiRect::new(Val::Px(4.0), Val::Px(1.0), Val::Px(1.0), Val::Px(1.0)),
                border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                ..default()
            },
            BackgroundColor(theme::mix(theme::SURFACE, green, 0.05)),
            BorderColor {
                left: green,
                top: green.with_alpha(0.35),
                right: green.with_alpha(0.35),
                bottom: green.with_alpha(0.35),
            },
            theme::shadow(24.0, 8.0, 0.6),
            Pickable::default(),
        ))
        .with_children(|card| {
            // the words scroll; the buttons stay at the foot
            card.spawn((
                ScrollPosition::default(),
                Node {
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(14.0),
                    padding: UiRect::new(Val::Px(22.0), Val::Px(22.0), Val::Px(18.0), Val::Px(8.0)),
                    overflow: Overflow::scroll_y(),
                    flex_shrink: 1.0,
                    min_height: Val::Px(0.0),
                    ..default()
                },
                Pickable::default(),
            ))
            .with_children(|p| {
                p.spawn(theme::label(&fonts, format!("NEW DISCOVERY{more}"), theme::XS, Weight::Bold, green));
                p.spawn(Node {
                    column_gap: Val::Px(20.0),
                    row_gap: Val::Px(12.0),
                    align_items: AlignItems::Center,
                    flex_wrap: FlexWrap::Wrap,
                    ..default()
                })
                .with_children(|hero| {
                    let img = match &sub.element_info {
                        Some(ei) => format!("bohr/{}.png", ei.atomic_number),
                        None => format!("structures/{}.png", sub.id),
                    };
                    hero.spawn((
                        Node {
                            width: Val::Px(176.0),
                            height: Val::Px(176.0),
                            flex_shrink: 0.0,
                            padding: UiRect::all(Val::Px(8.0)),
                            border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                            ..default()
                        },
                        BackgroundColor(theme::mix(theme::BG, green, 0.04)),
                        Pickable::IGNORE,
                    ))
                    .with_child((
                        ImageNode::new(assets.load(img)),
                        Node { width: Val::Percent(100.0), height: Val::Percent(100.0), ..default() },
                        Pickable::IGNORE,
                    ));
                    hero.spawn(Node {
                        flex_direction: FlexDirection::Column,
                        row_gap: Val::Px(6.0),
                        flex_shrink: 1.0,
                        ..default()
                    })
                    .with_children(|t| {
                        t.spawn(theme::para(&fonts, sub.name.clone(), theme::XXL, theme::TEXT, Val::Px(520.0)));
                        t.spawn((
                            Text::new(format_formula(&sub.formula)),
                            TextFont {
                                font: fonts.symbols.clone().into(),
                                font_size: FontSize::Px(theme::XL),
                                ..default()
                            },
                            TextColor(theme::mix(green, theme::TEXT, 0.5)),
                        ));
                        t.spawn(Node { column_gap: Val::Px(6.0), ..default() }).with_children(|chips| {
                            theme::spawn_chip(chips, &fonts, crate::ui::codex::state_name(sub.state), theme::CYAN);
                        });
                    });
                });
                p.spawn((
                    DiscoveryCardStory,
                    theme::para(&fonts, card_story(sub, page), theme::MD, theme::TEXT, Val::Px(PAGE_W - 60.0)),
                ));
                if let Some(pg) = page.filter(|pg| pg.about.is_none()) {
                    p.spawn(theme::para(
                        &fonts,
                        crate::ui::codex::page_credit(pg),
                        theme::XS,
                        theme::TEXT_3,
                        Val::Px(PAGE_W - 60.0),
                    ));
                }
                // how it is made (the earliest recipe for it), and what it leads to
                if let (Some(db), Some(all)) = (db.as_ref(), subs) {
                    let made = db
                        .authored
                        .iter()
                        .filter(|r| r.products.iter().any(|p| p.substance_id == sub.id))
                        .min_by_key(|r| (r.epoch, r.id));
                    let goes_into =
                        db.authored.iter().filter(|r| r.reactants.iter().any(|p| p.substance_id == sub.id)).count();
                    if made.is_some() || goes_into > 0 {
                        p.spawn((
                            Node {
                                flex_direction: FlexDirection::Column,
                                row_gap: Val::Px(5.0),
                                padding: UiRect::all(Val::Px(12.0)),
                                border: UiRect::all(Val::Px(1.0)),
                                border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                                ..default()
                            },
                            BackgroundColor(theme::RAISED.with_alpha(0.6)),
                            BorderColor::all(theme::LINE),
                        ))
                        .with_children(|how| {
                            how.spawn(theme::label(&fonts, "HOW IT'S MADE", 10.0, Weight::Bold, theme::TEXT_3));
                            if let Some(r) = made {
                                how.spawn(theme::label(
                                    &fonts,
                                    format!(
                                        "{}, in the {}",
                                        r.name,
                                        crate::ui::process_toolbar::vessel_name(&r.process)
                                    ),
                                    theme::MD,
                                    Weight::Semibold,
                                    theme::TEXT,
                                ));
                                how.spawn((
                                    Text::new(crate::ui::codex::equation_text(r, all)),
                                    TextFont {
                                        font: fonts.symbols.clone().into(),
                                        font_size: FontSize::Px(theme::SM),
                                        ..default()
                                    },
                                    TextColor(theme::CYAN),
                                ));
                                if let Some(d) = &r.description {
                                    how.spawn(theme::para(
                                        &fonts,
                                        d.clone(),
                                        theme::SM,
                                        theme::TEXT_2,
                                        Val::Px(PAGE_W - 90.0),
                                    ));
                                }
                            }
                            if goes_into > 0 {
                                how.spawn(theme::label(
                                    &fonts,
                                    format!(
                                        "It goes into {goes_into} recipe{}.",
                                        if goes_into == 1 { "" } else { "s" }
                                    ),
                                    theme::SM,
                                    Weight::Regular,
                                    theme::GOLD,
                                ));
                            }
                        });
                    }
                }
                if !sub.uses.is_empty() {
                    let uses: Vec<&str> = sub.uses.iter().map(String::as_str).take(6).collect();
                    p.spawn(theme::para(
                        &fonts,
                        format!("Used for: {}.", uses.join(", ")),
                        theme::SM,
                        theme::TEXT_2,
                        Val::Px(PAGE_W - 60.0),
                    ));
                }
                let facts = crate::ui::codex::facts(sub, page);
                if !facts.is_empty() {
                    crate::ui::codex::spawn_fact_grid(p, &fonts, facts, false);
                }
            });
            let wiki = page
                .map(|pg| pg.url.clone())
                .or_else(|| sub.references.iter().find(|(site, _)| site == "Wikipedia").map(|(_, url)| url.clone()));
            card.spawn(Node {
                justify_content: JustifyContent::FlexEnd,
                flex_wrap: FlexWrap::Wrap,
                column_gap: Val::Px(10.0),
                row_gap: Val::Px(8.0),
                padding: UiRect::new(Val::Px(22.0), Val::Px(22.0), Val::Px(10.0), Val::Px(18.0)),
                flex_shrink: 0.0,
                ..default()
            })
            .with_children(|row| {
                if let Some(url) = wiki {
                    big_button(
                        row,
                        &fonts,
                        &assets,
                        Kind::Secondary,
                        Some("external"),
                        "Wikipedia",
                        DiscoveryCardWiki(url),
                    );
                }
                big_button(row, &fonts, &assets, Kind::Secondary, Some("book"), "Library", DiscoveryCardReadMore);
                big_button(row, &fonts, &assets, Kind::Primary, Some("check"), "Got it", DiscoveryCardGotIt);
            });
        });
    });
}

/// One of the open card's buttons: tall enough for a thumb.
fn big_button(
    row: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    kind: Kind,
    icon: Option<&str>,
    text: &str,
    marker: impl Bundle,
) {
    let ink = if matches!(kind, Kind::Primary) { theme::BG } else { theme::TEXT };
    row.spawn((
        theme::button(
            kind,
            Node {
                height: Val::Px(46.0),
                padding: UiRect::horizontal(Val::Px(18.0)),
                column_gap: Val::Px(8.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                ..default()
            },
            theme::R_MD,
        ),
        marker,
    ))
    .with_children(|b| {
        if let Some(i) = icon {
            b.spawn(theme::icon(assets, i, 16.0, ink));
        }
        b.spawn((theme::label(fonts, text, theme::MD, Weight::Semibold, ink), Pickable::IGNORE));
    });
}

pub struct DiscoveryCardPlugin;

impl Plugin for DiscoveryCardPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<DiscoveryCards>().add_systems(Startup, spawn_discovery_card_ui).add_systems(
            Update,
            (discovery_card_feed_system, discovery_card_input_system, discovery_card_view_system).chain(),
        );
    }
}
