// src/ui/credits.rs
//
// Credits and licences: who made what the game is built from, and under which terms.
// The same list is the in-game Credits screen (Settings > About), the per-page "Text:"
// line in the Substance Library, and CREDITS.md in the repository; a content test keeps
// CREDITS.md in step with it.
use crate::ui::{Button, Interaction};
use bevy::prelude::*;

use crate::resources::ui_fonts::UiFonts;
use crate::ui::codex::open_url;
use crate::ui::theme::{self, Kind, Weight};

/// One thing the game uses and its terms.
pub struct Credit {
    pub name: &'static str,
    pub what: &'static str,
    pub licence: &'static str,
    /// where to read more (the source, or its licence)
    pub url: &'static str,
}

pub const CODE_LICENCE: &str = "MIT or Apache-2.0";
pub const CONTENT_LICENCE: &str = "CC BY-SA 4.0";
pub const CONTENT_LICENCE_URL: &str = "https://creativecommons.org/licenses/by-sa/4.0/";

pub const SECTIONS: &[(&str, &[Credit])] = &[
    (
        "Text and data",
        &[
            Credit {
                name: "Wikipedia",
                what: "Element overviews and many substance descriptions are taken from Wikipedia articles; each page links its article, whose history lists its authors.",
                licence: "CC BY-SA 4.0",
                url: "https://en.wikipedia.org/",
            },
            Credit {
                name: "PubChem",
                what: "Names, formulas, properties and synonyms of the compounds (NCBI, U.S. National Library of Medicine), with GHS hazard statements as notified to the ECHA C&L Inventory and use categories from the U.S. EPA's Chemical Data Reporting.",
                licence: "Public domain (U.S. government)",
                url: "https://pubchem.ncbi.nlm.nih.gov/",
            },
            Credit {
                name: "CAMEO Chemicals",
                what: "Short descriptions of what chemicals look like, from NOAA, with appearance notes from the U.S. National Toxicology Program and Coast Guard.",
                licence: "Public domain (U.S. government)",
                url: "https://cameochemicals.noaa.gov/",
            },
            Credit {
                name: "ChEBI",
                what: "Definitions of some compounds, from Chemical Entities of Biological Interest (EMBL-EBI).",
                licence: "CC BY 4.0",
                url: "https://www.ebi.ac.uk/chebi/",
            },
            Credit {
                name: "Wikidata",
                what: "Identifiers and links that tie the substances to their articles and records.",
                licence: "CC0",
                url: "https://www.wikidata.org/",
            },
            Credit {
                name: "Chemical Reaction Database (CRD)",
                what: "The library of reactions from patents and the literature, compiled by Rik van der Lingen from Daniel Lowe's reactions extracted from U.S. patents (CC0) and from academic papers.",
                licence: "Open dataset (figshare)",
                url: "https://kmt.vander-lingen.nl/",
            },
        ],
    ),
    (
        "Pictures, sounds and type",
        &[
            Credit {
                name: "Curieosity",
                what: "The vessel art, interface icons, sounds and the hand-written reactions and pages are made for the game.",
                licence: "CC BY-SA 4.0",
                url: "https://creativecommons.org/licenses/by-sa/4.0/",
            },
            Credit {
                name: "RDKit",
                what: "Draws the molecule pictures from each compound's structure.",
                licence: "BSD 3-Clause",
                url: "https://www.rdkit.org/",
            },
            Credit {
                name: "Noto Sans",
                what: "The interface type (The Noto Project Authors).",
                licence: "SIL Open Font License 1.1",
                url: "https://openfontlicense.org/",
            },
            Credit {
                name: "DejaVu Sans",
                what: "The type of equations and symbols (Bitstream Vera, with DejaVu's changes).",
                licence: "Bitstream Vera License; changes public domain",
                url: "https://dejavu-fonts.github.io/License.html",
            },
            Credit {
                name: "Liberation Sans",
                what: "Fallback type.",
                licence: "SIL Open Font License 1.1",
                url: "https://openfontlicense.org/",
            },
        ],
    ),
    (
        "Built with",
        &[
            Credit {
                name: "Bevy",
                what: "The game engine, by the Bevy contributors.",
                licence: "MIT or Apache-2.0",
                url: "https://bevy.org/",
            },
            Credit {
                name: "Rust crates",
                what: "serde, ron, thiserror and the open-source crates Bevy builds on, each under its own licence.",
                licence: "MIT or Apache-2.0, mostly",
                url: "https://crates.io/",
            },
        ],
    ),
];

/// The credit line for a page's text source ("Text: Wikipedia, CC BY-SA 4.0"), or None for
/// the game's own writing.
pub fn text_credit(source: &str) -> Option<String> {
    let (name, licence) = match source {
        "Wikipedia" => ("Wikipedia", "CC BY-SA 4.0"),
        "CAMEO Chemicals" => ("CAMEO Chemicals (NOAA)", "public domain"),
        "ChEBI" => ("ChEBI (EMBL-EBI)", "CC BY 4.0"),
        "LOTUS" => ("LOTUS", "CC0"),
        _ => return None,
    };
    Some(format!("Text: {name}, {licence}."))
}

/// The text sources the library may carry (see tools/data/audit_library.py).
pub const TEXT_SOURCES: [&str; 5] =
    ["Wikipedia", "CAMEO Chemicals", "ChEBI", "LOTUS", crate::data::substances::CURIEOSITY];

#[derive(Resource, Default)]
pub struct CreditsUi {
    pub open: bool,
}

#[derive(Component)]
pub struct CreditsRoot;
#[derive(Component)]
pub struct CreditsBackdrop;
#[derive(Component)]
pub struct CreditsClose;
/// Settings > About: opens the credits.
#[derive(Component)]
pub struct CreditsButton;
#[derive(Component)]
pub struct CreditLink(pub &'static str);

pub struct CreditsPlugin;

impl Plugin for CreditsPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<CreditsUi>()
            .add_systems(Startup, spawn_credits.after(crate::resources::ui_fonts::load_ui_fonts))
            .add_systems(Update, credits_system);
    }
}

pub fn spawn_credits(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    commands
        .spawn((
            CreditsRoot,
            GlobalZIndex(960),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(0.0),
                bottom: Val::Px(0.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                display: Display::None,
                ..default()
            },
            Name::new("Credits"),
        ))
        .with_children(|root| {
            root.spawn((
                CreditsBackdrop,
                Button,
                crate::ui::focus::NoFocus,
                Node {
                    position_type: PositionType::Absolute,
                    left: Val::Px(0.0),
                    right: Val::Px(0.0),
                    top: Val::Px(0.0),
                    bottom: Val::Px(0.0),
                    ..default()
                },
                BackgroundColor(Color::srgba(0.0, 0.0, 0.02, 0.7)),
            ));
            root.spawn((
                Node { border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    width: Val::Px(820.0),
                    max_width: Val::Percent(94.0),
                    max_height: Val::Percent(90.0),
                    flex_direction: FlexDirection::Column,
                    padding: UiRect::all(Val::Px(22.0)),
                    row_gap: Val::Px(8.0),
                    border: UiRect::all(Val::Px(1.0)),
                    overflow: Overflow::scroll_y(),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::LINE_STRONG),
                theme::shadow(40.0, 14.0, 0.6),
                ScrollPosition::default(),
                Pickable::default(),
                bevy::ui::FocusPolicy::Block,
            ))
            .with_children(|panel| {
                panel
                    .spawn(Node { justify_content: JustifyContent::SpaceBetween, align_items: AlignItems::Center, flex_shrink: 0.0, ..default() })
                    .with_children(|h| {
                        h.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Center, ..default() })
                            .with_children(|t| {
                                t.spawn(theme::icon(assets, "book", 22.0, theme::CYAN));
                                t.spawn(theme::label(fonts, "Credits and licences", theme::XL, Weight::Semibold, theme::TEXT));
                            });
                        theme::spawn_icon_button(h, assets, "close", 32.0, theme::TEXT_2, CreditsClose);
                    });
                panel
                    .spawn(Node { flex_shrink: 0.0, margin: UiRect::bottom(Val::Px(4.0)), ..default() })
                    .with_children(|t| {
                        t.spawn(theme::para(
                            fonts,
                            format!(
                                "Curieosity is free, and always will be. Its code is licensed {CODE_LICENCE}; its content (the data, text, pictures and sounds) is {CONTENT_LICENCE}, as the sources it draws on require. It is built from these:"
                            ),
                            theme::MD,
                            theme::TEXT_2,
                            Val::Px(760.0),
                        ));
                    });
                for (title, credits) in SECTIONS {
                    theme::spawn_section_title(panel, fonts, title);
                    for c in *credits {
                        credit_row(panel, fonts, assets, c);
                    }
                }
            });
        });
}

fn credit_row(panel: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer, c: &'static Credit) {
    panel
        .spawn(Node {
            justify_content: JustifyContent::SpaceBetween,
            align_items: AlignItems::Center,
            column_gap: Val::Px(16.0),
            padding: UiRect::vertical(Val::Px(6.0)),
            flex_shrink: 0.0,
            ..default()
        })
        .with_children(|row| {
            row.spawn(Node {
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(2.0),
                flex_shrink: 1.0,
                ..default()
            })
            .with_children(|t| {
                t.spawn(theme::label(fonts, c.name, theme::MD, Weight::Semibold, theme::TEXT));
                t.spawn(theme::para(fonts, c.what, theme::SM, theme::TEXT_2, Val::Px(520.0)));
            });
            row.spawn(Node {
                align_items: AlignItems::Center,
                column_gap: Val::Px(8.0),
                flex_shrink: 0.0,
                ..default()
            })
            .with_children(|r| {
                theme::spawn_chip(r, fonts, c.licence, theme::CYAN);
                theme::spawn_icon_button(r, assets, "external", 30.0, theme::TEXT, CreditLink(c.url));
            });
        });
}

/// Open from Settings > About; close with the x, the backdrop or Esc (see shell.rs); the
/// link buttons open their pages in the browser.
#[allow(clippy::type_complexity)]
pub fn credits_system(
    mut ui: ResMut<CreditsUi>,
    mut root: Query<&mut Node, With<CreditsRoot>>,
    opens: Query<&Interaction, (Changed<Interaction>, With<CreditsButton>)>,
    closes: Query<&Interaction, (Changed<Interaction>, Or<(With<CreditsClose>, With<CreditsBackdrop>)>)>,
    links: Query<(&Interaction, &CreditLink), Changed<Interaction>>,
) {
    if opens.iter().any(|i| *i == Interaction::Pressed) {
        ui.open = true;
    }
    if closes.iter().any(|i| *i == Interaction::Pressed) {
        ui.open = false;
    }
    for (i, l) in &links {
        if *i == Interaction::Pressed {
            open_url(l.0);
        }
    }
    if let Ok(mut n) = root.single_mut() {
        let d = if ui.open { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
}

/// The settings row that opens the credits.
pub fn spawn_credits_button(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer) {
    theme::spawn_button(parent, fonts, assets, Kind::Secondary, Some("book"), "Credits and licences", CreditsButton);
}
