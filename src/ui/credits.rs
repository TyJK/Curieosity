// src/ui/credits.rs
//
// About Curieosity: who made it and how (AI use included), what it is built from and
// under which terms, that it is free and open for good, where to give instead, and what it
// does with your data (nothing). The source list is also the per-page "Text:" line in the
// Substance Library and CREDITS.md in the repository; the ways to give are also in the
// README. Content tests keep both files in step with this one.
use crate::ui::{Button, Clicked};
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

/// Where the source code lives.
pub const REPO_URL: &str = "https://github.com/TyJK/Curieosity";

/// Who made the game, and how: the AI use, and whose decisions it carries out.
pub const MADE_BY: &str = "Curieosity is my game. What it teaches and how, which substances and reactions are in it, and how it looks and plays are my decisions. I built it with AI: the code, and the pages and reactions written for the game, were written by Claude, an AI model made by Anthropic, to my design and direction. The facts come from the open sources further down, and every substance page names the source of its text.";

/// How the pictures and sounds were made (no image or sound generator).
pub const HOW_MADE: &str = "Nothing in the game was made by an image or sound generator. The vessels and icons are line art drawn by a program from plain geometry (lines, arcs and curves set by numbers), so they share one stroke and one light. The molecule pictures are drawn by RDKit from each compound's recorded structure, the atom diagrams from each element's electron configuration, and the sounds are synthesised from sine waves and filtered noise. Those programs were written with Claude too; they are in the source code, under tools/art.";

/// Free for good, and why.
pub const FREE: &str = "Curieosity will never cost money: no price, no ads, no in-app purchases, nothing locked. It is open source, so anyone can read it, change it and share it. Most of what is in it is other people's work: the chemists who ran these reactions, the scientists, editors and volunteers behind PubChem, Wikipedia and the other sources, and the people who wrote the tools it is built with. I have only repackaged their labour into a new form, and everyone should be able to use it.";

/// What the game does with your data.
pub const PRIVACY: &str = "Curieosity collects nothing about you: no account, no analytics, no ads, and nothing is sent anywhere. Your progress is saved only on your device. Links open in your browser, where those sites' own policies apply. A copy played through Steam tells Steam which achievements you have earned.";

/// Somewhere to give, instead of paying for the game.
pub struct Cause {
    pub name: &'static str,
    pub what: &'static str,
    /// None for one that isn't set up yet (shown as "Coming soon")
    pub url: Option<&'static str>,
    /// Shown in the phone builds too. Those go to the App Store and Google Play, which want
    /// tips to a developer taken as in-app purchases, and allow links out only to charities.
    pub on_phones: bool,
}

/// The causes this build shows (all of them on a desktop; the charities on a phone).
pub fn shown_causes() -> impl Iterator<Item = &'static Cause> {
    GIVING.iter().filter(|c| c.on_phones || !crate::platform::PHONE)
}

/// In the order they are shown: Jarred Younger's lab first, Ko-fi last (and not on phones).
pub const GIVING: &[Cause] = &[
    Cause {
        name: "Neuroinflammation, Pain and Fatigue Laboratory",
        what: "Jarred Younger's lab at the University of Alabama at Birmingham, researching how inflammation in the brain drives chronic pain and fatigue, in ME/CFS, fibromyalgia, long COVID and related illnesses.",
        url: Some("https://go.uab.edu/youngerlab"),
        on_phones: true,
    },
    Cause {
        name: "#MEAction",
        what: "The Myalgic Encephalomyelitis Action Network: a worldwide community campaigning for the care, research and recognition people with ME need.",
        url: Some("https://funraise.org/give/Myalgic-Encephalomyelitis-Action-Network-Inc/0645f869-e3b1-49cd-8cf3-5eec044e97b1/"),
        on_phones: true,
    },
    Cause {
        name: "IACFS/ME",
        what: "The International Association for Chronic Fatigue Syndrome/Myalgic Encephalomyelitis: clinicians and scientists advancing research and care.",
        url: Some("https://www.iacfsme.org/55671-2/"),
        on_phones: true,
    },
    Cause { name: "Ko-fi", what: "To give to me directly.", url: Some("https://ko-fi.com/T5T52AWOGC"), on_phones: false },
];

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
                what: "The vessel art, interface icons and sounds, and the reactions and pages written for the game, are made for it.",
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
            ))
            .with_children(|panel| {
                panel
                    .spawn(Node { justify_content: JustifyContent::SpaceBetween, align_items: AlignItems::Center, flex_shrink: 0.0, ..default() })
                    .with_children(|h| {
                        h.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Center, ..default() })
                            .with_children(|t| {
                                t.spawn(theme::icon(assets, "book", 22.0, theme::CYAN));
                                t.spawn(theme::label(fonts, "About Curieosity", theme::XL, Weight::Semibold, theme::TEXT));
                            });
                        theme::spawn_icon_button(h, assets, "close", 32.0, theme::TEXT_2, CreditsClose);
                    });
                // who made it, and how
                theme::spawn_section_title(panel, fonts, "Made by Tyler Kolody, with AI");
                about_para(panel, fonts, MADE_BY);
                theme::spawn_section_title(panel, fonts, "How the pictures and sounds are made");
                about_para(panel, fonts, HOW_MADE);
                // what it is built from
                for (title, credits) in SECTIONS {
                    theme::spawn_section_title(panel, fonts, title);
                    for c in *credits {
                        credit_row(panel, fonts, assets, c);
                    }
                }
                // free for good
                theme::spawn_section_title(panel, fonts, "Free, always");
                about_para(panel, fonts, FREE);
                link_row(
                    panel,
                    fonts,
                    assets,
                    "The source code",
                    &format!("Code {CODE_LICENCE}; content (data, text, pictures and sounds) {CONTENT_LICENCE}, as its sources require."),
                    Some(REPO_URL),
                );
                // where to give instead
                theme::spawn_section_title(panel, fonts, "If you'd like to give something");
                about_para(panel, fonts, "You never need to. If you want to, I'd rather it went to one of these:");
                for c in shown_causes() {
                    link_row(panel, fonts, assets, c.name, c.what, c.url);
                }
                theme::spawn_section_title(panel, fonts, "Privacy");
                about_para(panel, fonts, PRIVACY);
            });
        });
}

/// A paragraph of the About screen's own text.
fn about_para(panel: &mut ChildSpawnerCommands, fonts: &UiFonts, text: &str) {
    panel.spawn(Node { flex_shrink: 0.0, margin: UiRect::bottom(Val::Px(4.0)), ..default() }).with_children(|t| {
        t.spawn(theme::para(fonts, text, theme::MD, theme::TEXT_2, Val::Px(760.0)));
    });
}

/// A name and a line about it, and its link (or "Coming soon" while there is none).
fn link_row(
    panel: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    name: &str,
    what: &str,
    url: Option<&'static str>,
) {
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
                t.spawn(theme::label(fonts, name, theme::MD, Weight::Semibold, theme::TEXT));
                t.spawn(theme::para(fonts, what, theme::SM, theme::TEXT_2, Val::Px(560.0)));
            });
            row.spawn(Node { align_items: AlignItems::Center, flex_shrink: 0.0, ..default() }).with_children(|r| {
                match url {
                    Some(url) => {
                        theme::spawn_icon_button(r, assets, "external", 30.0, theme::TEXT, CreditLink(url));
                    }
                    None => theme::spawn_chip(r, fonts, "Coming soon", theme::TEXT_3),
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

/// Open from Settings > About or the title menu; close with the x, the backdrop or Esc (see
/// shell.rs); the link buttons open their pages in the browser.
#[allow(clippy::type_complexity)]
pub fn credits_system(
    mut ui: ResMut<CreditsUi>,
    mut root: Query<&mut Node, With<CreditsRoot>>,
    opens: Query<(), (With<Clicked>, With<CreditsButton>)>,
    closes: Query<(), (With<Clicked>, Or<(With<CreditsClose>, With<CreditsBackdrop>)>)>,
    links: Query<&CreditLink, With<Clicked>>,
) {
    if !opens.is_empty() {
        ui.open = true;
    }
    if !closes.is_empty() {
        ui.open = false;
    }
    for l in &links {
        open_url(l.0);
    }
    if let Ok(mut n) = root.single_mut() {
        let d = if ui.open { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
}

/// The settings row that opens the About screen.
pub fn spawn_credits_button(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer) {
    theme::spawn_button(parent, fonts, assets, Kind::Secondary, Some("book"), "About and credits", CreditsButton);
}
