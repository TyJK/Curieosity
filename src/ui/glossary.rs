// src/ui/glossary.rs
//
// The glossary on the pages: the chemistry words a substance's page or a lesson uses
// (data::pages, from tools/data/glossary.py) are underlined where the text first uses them,
// and listed in a row under the text. A tap on a word in the row opens its definition right
// there, with its Wikipedia article and the lesson that teaches it; a second tap closes it.
// Lessons also lists every term in a Glossary section of its own (ui::curriculum).
use bevy::prelude::*;

use crate::data::pages::Pages;
use crate::resources::ui_fonts::UiFonts;
use crate::ui::codex::open_url;
use crate::ui::theme::{self, Kind, Skin, Weight};
use crate::ui::{Button, Clicked};
use crate::GameData;

/// How a glossary word stands out in running text.
pub const TERM_COLOR: Color = Color::srgb(0.78, 0.90, 1.0);

/// A page's row of terms, with the definition card under it.
#[derive(Component)]
pub struct TermRow;
/// One term's button in a row.
#[derive(Component)]
pub struct TermChip(pub String);
/// Where a row shows the definition of the term open in it.
#[derive(Component)]
pub struct TermCard;
/// A button that opens a Wikipedia article.
#[derive(Component)]
pub struct WikiLink(pub String);

/// The term whose definition is open, and in which row.
#[derive(Resource, Default, PartialEq)]
pub struct OpenTerm(pub Option<(Entity, String)>);

pub struct GlossaryPlugin;

impl Plugin for GlossaryPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<OpenTerm>().add_systems(Update, (term_input_system, term_card_system).chain());
    }
}

/// A paragraph with the terms it uses underlined, the first time the page uses each: the
/// words already marked higher up the page are in `seen`, and this adds its own.
#[allow(clippy::too_many_arguments)]
pub fn spawn_glossed_para(
    parent: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    pages: Option<&Pages>,
    keys: &[String],
    seen: &mut Vec<String>,
    text: &str,
    size: f32,
    color: Color,
    max_w: Val,
) {
    let spans: Vec<(usize, usize, &str)> = match pages {
        Some(p) => p.term_spans(text, keys).into_iter().filter(|(_, _, k)| !seen.iter().any(|s| s == k)).collect(),
        None => Vec::new(),
    };
    // only each term's first use
    let mut marked: Vec<(usize, usize)> = Vec::new();
    for (a, b, k) in &spans {
        if !seen.iter().any(|s| s == k) {
            seen.push(k.to_string());
            marked.push((*a, *b));
        }
    }
    if marked.is_empty() {
        parent.spawn(theme::para(fonts, text.to_string(), size, color, max_w));
        return;
    }
    // (a paragraph with an arrow or maths in it is drawn in DejaVu throughout)
    let body = crate::ui::theme::text_font(fonts, text);
    let plain = |t: &str| {
        (
            TextSpan::new(t.to_string()),
            TextFont { font: body.clone().into(), font_size: FontSize::Px(size), ..default() },
            TextColor(color),
        )
    };
    parent.spawn(theme::para(fonts, String::new(), size, color, max_w)).with_children(|p| {
        let mut at = 0;
        for (a, b) in marked {
            if a > at {
                p.spawn(plain(&text[at..a]));
            }
            let strong = if crate::ui::theme::needs_symbols(text) { body.clone() } else { fonts.semibold.clone() };
            p.spawn((
                TextSpan::new(text[a..b].to_string()),
                TextFont { font: strong.into(), font_size: FontSize::Px(size), ..default() },
                TextColor(TERM_COLOR),
                Underline,
                UnderlineColor(TERM_COLOR.with_alpha(0.55)),
            ));
            at = b;
        }
        if at < text.len() {
            p.spawn(plain(&text[at..]));
        }
    });
}

/// "Words on this page": a button for each term, and the card a tap opens under them.
pub fn spawn_term_row(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, pages: &Pages, keys: &[String]) {
    let terms: Vec<(&String, &crate::data::pages::Term)> =
        keys.iter().filter_map(|k| pages.glossary.get(k).map(|t| (k, t))).collect();
    if terms.is_empty() {
        return;
    }
    parent
        .spawn((
            TermRow,
            Node {
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(10.0),
                width: Val::Percent(100.0),
                ..default()
            },
        ))
        .with_children(|row| {
            theme::spawn_section_title(row, fonts, "Words on this page");
            row.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(7.0), row_gap: Val::Px(7.0), ..default() })
                .with_children(|chips| {
                    for (k, t) in terms {
                        chips
                            .spawn((
                                theme::button(
                                    Kind::Tab,
                                    Node {
                                        min_height: Val::Px(34.0),
                                        padding: UiRect::axes(Val::Px(13.0), Val::Px(5.0)),
                                        align_items: AlignItems::Center,
                                        ..default()
                                    },
                                    99.0,
                                ),
                                TermChip(k.clone()),
                            ))
                            .with_children(|c| {
                                c.spawn((
                                    theme::label(fonts, t.term.clone(), theme::SM, Weight::Semibold, TERM_COLOR),
                                    Pickable::IGNORE,
                                ));
                            });
                    }
                });
            row.spawn((TermCard, Node { display: Display::None, width: Val::Percent(100.0), ..default() }));
        });
}

/// A tap on a term opens its definition (or closes it, if it was open); the card's links.
pub fn term_input_system(
    chips: Query<(&TermChip, &ChildOf), (With<Clicked>, With<Button>)>,
    parents: Query<&ChildOf>,
    rows: Query<(), With<TermRow>>,
    wiki: Query<&WikiLink, (With<Clicked>, With<Button>)>,
    mut open: ResMut<OpenTerm>,
) {
    for (chip, parent) in &chips {
        // chip -> the chips' wrap -> the row
        let Some(row) = parents.get(parent.parent()).ok().map(|p| p.parent()).filter(|r| rows.contains(*r)) else {
            continue;
        };
        let want = Some((row, chip.0.clone()));
        open.0 = if open.0 == want { None } else { want };
    }
    for w in &wiki {
        open_url(&w.0);
    }
}

/// Fills the open row's card with the term's definition, and keeps the chips' look in step.
/// Runs only when the open term changes.
#[allow(clippy::too_many_arguments)]
pub fn term_card_system(
    mut commands: Commands,
    open: Res<OpenTerm>,
    game_data: Option<Res<GameData>>,
    pages: Res<Assets<Pages>>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    rows: Query<&Children, With<TermRow>>,
    mut cards: Query<(Entity, &mut Node), With<TermCard>>,
    mut chips: Query<(&TermChip, &ChildOf, &mut Skin)>,
    parents: Query<&ChildOf>,
) {
    if !open.is_changed() {
        return;
    }
    let Some(pages) = game_data.as_ref().and_then(|g| pages.get(&g.pages)) else { return };
    for (chip, parent, mut skin) in &mut chips {
        let row = parents.get(parent.parent()).ok().map(|p| p.parent());
        let active = open.0.as_ref().is_some_and(|(r, k)| Some(*r) == row && *k == chip.0);
        if skin.active != active {
            skin.active = active;
        }
    }
    let open_card = open.0.as_ref().and_then(|(r, k)| {
        let kids = rows.get(*r).ok()?;
        kids.iter().find(|e| cards.contains(*e)).map(|c| (c, k))
    });
    for (e, mut n) in &mut cards {
        let showing = open_card.is_some_and(|(c, _)| c == e);
        let d = if showing { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
        if !showing {
            commands.entity(e).despawn_children();
        }
    }
    let Some((card, key)) = open_card else { return };
    let Some(term) = pages.glossary.get(key) else { return };
    commands.entity(card).despawn_children();
    commands.entity(card).with_children(|c| spawn_definition(c, &fonts, &assets, pages, term));
}

/// A term's definition as a card: the word, what it means, and where to read more.
pub fn spawn_definition(
    parent: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    pages: &Pages,
    term: &crate::data::pages::Term,
) {
    parent
        .spawn((
            Node {
                width: Val::Percent(100.0),
                max_width: Val::Px(760.0),
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(10.0),
                padding: UiRect::all(Val::Px(16.0)),
                border: UiRect::left(Val::Px(3.0)),
                border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
                ..default()
            },
            BackgroundColor(theme::mix(theme::RAISED, TERM_COLOR, 0.06)),
            BorderColor::all(TERM_COLOR.with_alpha(0.8)),
        ))
        .with_children(|card| {
            card.spawn(theme::label(fonts, term.term.clone(), theme::LG, Weight::Semibold, theme::TEXT));
            card.spawn(theme::para(fonts, term.text.clone(), theme::MD, theme::TEXT, Val::Percent(100.0)));
            card.spawn(Node {
                flex_wrap: FlexWrap::Wrap,
                column_gap: Val::Px(8.0),
                row_gap: Val::Px(8.0),
                ..default()
            })
            .with_children(|b| {
                if let Some((k, t)) = term.lesson.as_ref().and_then(|k| pages.topics.get(k).map(|t| (k, t))) {
                    crate::ui::curriculum::spawn_learn_button(b, fonts, assets, k, t);
                }
                theme::spawn_button(
                    b,
                    fonts,
                    assets,
                    Kind::Secondary,
                    Some("external"),
                    "Wikipedia",
                    WikiLink(term.url.clone()),
                );
            });
        });
}
