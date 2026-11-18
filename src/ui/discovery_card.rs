// src/ui/discovery_card.rs
//
// The discovery card. Each substance the player makes for the first time arrives as a
// sealed card at the top right of the bench: "New discovery: Butter, tap to read". Tapping
// it opens it on the substance's story (how an element was found, what a compound is and
// where it turns up), with Read more (its Substance Library page) and Got it; the next card
// waits its turn behind it. A sealed card isn't dismissed unread, unless the "Close by
// themselves" setting lets it go after CARD_TIMEOUT seconds. With cards off (Settings), a
// discovery is a toast as before.
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
const STORY_MAX: usize = 420;
const CARD_W: f32 = 380.0;

/// The cards waiting, the front one showing; `open` once it has been tapped.
#[derive(Resource, Default, Debug)]
pub struct DiscoveryCards {
    pub queue: VecDeque<u32>,
    pub open: bool,
    /// when the front card arrived (real seconds), for the timeout
    pub since: f64,
}

impl DiscoveryCards {
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

/// What the card tells about a substance: an element's discovery or overview, a
/// compound's description, cut at a sentence once it is long enough.
pub fn card_story(sub: &Substance) -> String {
    let text = sub
        .element_info
        .as_ref()
        .and_then(|e| e.discovery_story.clone().or_else(|| e.overview.clone()))
        .or_else(|| sub.description.clone())
        .unwrap_or_default();
    let first = text.lines().map(str::trim).find(|l| !l.is_empty()).unwrap_or("").to_string();
    if first.chars().count() <= STORY_MAX {
        return first;
    }
    // the last full sentence that fits, or a clean cut with an ellipsis
    let cut: String = first.chars().take(STORY_MAX).collect();
    match cut.rfind(". ") {
        Some(i) if i > STORY_MAX / 3 => cut[..=i].to_string(),
        _ => format!("{}…", cut.trim_end()),
    }
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
    mut codex: ResMut<CodexState>,
) {
    let now = time.elapsed_secs_f64();
    let Some(&id) = cards.queue.front() else { return };
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
        Node {
            position_type: PositionType::Absolute,
            top: Val::Px(theme::HEADER_H + 12.0),
            right: Val::Px(theme::SIDEBAR_W + 14.0),
            width: Val::Px(CARD_W),
            flex_direction: FlexDirection::Column,
            align_items: AlignItems::FlexEnd,
            display: Display::None,
            ..default()
        },
        Pickable::IGNORE,
        Name::new("DiscoveryCard"),
    ));
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
    mut root: Query<(Entity, &mut Node, Option<&Children>), With<DiscoveryCardRoot>>,
    mut shown: Local<Option<(u32, bool, usize)>>,
) {
    let Ok((root_e, mut node, children)) = root.single_mut() else { return };
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
    *shown = want;
    node.display = Display::Flex;
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
                width: Val::Px(CARD_W),
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(8.0),
                padding: UiRect::all(Val::Px(14.0)),
                border: UiRect::new(Val::Px(4.0), Val::Px(1.0), Val::Px(1.0), Val::Px(1.0)),
                border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                ..default()
            },
            BackgroundColor(theme::mix(theme::RAISED, green, 0.08)),
            BorderColor {
                left: green,
                top: green.with_alpha(0.35),
                right: green.with_alpha(0.35),
                bottom: green.with_alpha(0.35),
            },
            theme::shadow(18.0, 6.0, 0.6),
            Pickable::default(),
        ))
        .with_children(|p| {
            p.spawn(theme::label(&fonts, format!("NEW DISCOVERY{more}"), theme::XS, Weight::Bold, green));
            p.spawn(Node { column_gap: Val::Px(12.0), align_items: AlignItems::Center, ..default() }).with_children(
                |hero| {
                    let img = match &sub.element_info {
                        Some(ei) => format!("bohr/{}.png", ei.atomic_number),
                        None => format!("structures/{}.png", sub.id),
                    };
                    hero.spawn((
                        ImageNode::new(assets.load(img)),
                        Node { width: Val::Px(64.0), height: Val::Px(64.0), flex_shrink: 0.0, ..default() },
                        Pickable::IGNORE,
                    ));
                    hero.spawn(Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, ..default() })
                        .with_children(|t| {
                            t.spawn(theme::label(&fonts, sub.name.clone(), theme::LG, Weight::Bold, theme::TEXT));
                            t.spawn((
                                Text::new(format_formula(&sub.formula)),
                                TextFont {
                                    font: fonts.symbols.clone().into(),
                                    font_size: FontSize::Px(theme::MD),
                                    ..default()
                                },
                                TextColor(theme::mix(green, theme::TEXT, 0.5)),
                            ));
                        });
                },
            );
            p.spawn((
                DiscoveryCardStory,
                theme::para(&fonts, card_story(sub), theme::SM, theme::TEXT_2, Val::Px(CARD_W - 32.0)),
            ));
            p.spawn(Node { justify_content: JustifyContent::FlexEnd, column_gap: Val::Px(8.0), ..default() })
                .with_children(|row| {
                    theme::spawn_button(
                        row,
                        &fonts,
                        &assets,
                        Kind::Secondary,
                        Some("book"),
                        "Read more",
                        DiscoveryCardReadMore,
                    );
                    theme::spawn_button(row, &fonts, &assets, Kind::Primary, None, "Got it", DiscoveryCardGotIt);
                });
        });
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
