// src/ui/theme.rs
//
// One place for the look of the game: the palette, type sizes, corner radii, and the
// small building blocks (labels, icons, buttons, chips, panels) every screen is made of.
// Buttons carry a `Skin`; `skin_system` recolours them on hover/press and when their
// `active` flag changes, so no screen hand-rolls its own hover logic.
use crate::ui::{Button, Look};
use bevy::picking::hover::Hovered;
use bevy::prelude::*;
use bevy::ui::Pressed;
use bevy::ui::{BoxShadow, ShadowStyle};

use crate::resources::ui_fonts::UiFonts;

// --- palette -----------------------------------------------------------------------------
// A deep blue-black base, lifted in steps for panels, rows and hover; one cyan accent for
// "interactive", violet for brand, and the vessels' process colours for everything chemical.
pub const BG: Color = Color::srgb(0.027, 0.035, 0.078); // app background, docks
pub const BENCH: Color = Color::srgb(0.043, 0.059, 0.130); // the lab bench (canvas)
pub const SURFACE: Color = Color::srgb(0.067, 0.086, 0.169); // panels, sidebars
pub const RAISED: Color = Color::srgb(0.094, 0.122, 0.224); // cards, rows, tiles
pub const HOVER: Color = Color::srgb(0.133, 0.169, 0.300); // hovered rows/buttons
pub const LINE: Color = Color::srgb(0.165, 0.208, 0.376); // hairlines and borders
pub const LINE_STRONG: Color = Color::srgb(0.255, 0.320, 0.540); // input/button borders
pub const TEXT: Color = Color::srgb(0.933, 0.945, 0.980);
pub const TEXT_2: Color = Color::srgb(0.706, 0.737, 0.840);
pub const TEXT_3: Color = Color::srgb(0.520, 0.565, 0.700);
pub const CYAN: Color = Color::srgb(0.353, 0.839, 0.902); // interactive accent
pub const VIOLET: Color = Color::srgb(0.627, 0.439, 1.000); // brand
pub const GREEN: Color = Color::srgb(0.357, 0.890, 0.604); // done / discovery
pub const GOLD: Color = Color::srgb(0.949, 0.757, 0.306); // available / milestone
pub const RED: Color = Color::srgb(1.000, 0.365, 0.424); // danger

// --- metrics -----------------------------------------------------------------------------
pub const HEADER_H: f32 = 52.0;
pub const SIDEBAR_W: f32 = 248.0;
pub const DOCK_H: f32 = 210.0;
pub const R_SM: f32 = 6.0;
pub const R_MD: f32 = 10.0;
pub const R_LG: f32 = 14.0;

pub const XS: f32 = 11.0;
pub const SM: f32 = 13.0;
pub const MD: f32 = 15.0;
pub const LG: f32 = 18.0;
pub const XL: f32 = 24.0;
pub const XXL: f32 = 30.0;

pub fn mix(a: Color, b: Color, t: f32) -> Color {
    let (a, b) = (a.to_srgba(), b.to_srgba());
    Color::srgba(
        a.red + (b.red - a.red) * t,
        a.green + (b.green - a.green) * t,
        a.blue + (b.blue - a.blue) * t,
        a.alpha + (b.alpha - a.alpha) * t,
    )
}

/// A soft drop shadow under a card or panel.
pub fn shadow(blur: f32, y: f32, alpha: f32) -> BoxShadow {
    BoxShadow(vec![ShadowStyle {
        color: Color::srgba(0.0, 0.0, 0.0, alpha),
        x_offset: Val::Px(0.0),
        y_offset: Val::Px(y),
        spread_radius: Val::Px(0.0),
        blur_radius: Val::Px(blur),
    }])
}

/// A coloured glow (a shadow with no offset), for selected or reacting things.
pub fn glow(color: Color, blur: f32) -> BoxShadow {
    BoxShadow(vec![ShadowStyle {
        color,
        x_offset: Val::Px(0.0),
        y_offset: Val::Px(0.0),
        spread_radius: Val::Px(0.0),
        blur_radius: Val::Px(blur),
    }])
}

// --- text ----------------------------------------------------------------------------------
#[derive(Clone, Copy)]
pub enum Weight {
    Regular,
    Semibold,
    Bold,
    /// DejaVu Sans: equations (it has the arrow glyph)
    Symbols,
}

pub fn font(fonts: &UiFonts, w: Weight) -> Handle<Font> {
    match w {
        Weight::Regular => fonts.main.clone(),
        Weight::Semibold => fonts.semibold.clone(),
        Weight::Bold => fonts.bold.clone(),
        Weight::Symbols => fonts.symbols.clone(),
    }
}

/// A text node.
pub fn label(fonts: &UiFonts, text: impl Into<String>, size: f32, w: Weight, color: Color) -> impl Bundle {
    (
        Text::new(text.into()),
        TextFont { font: font(fonts, w).into(), font_size: FontSize::Px(size), ..default() },
        TextColor(color),
    )
}

/// A text node that wraps inside `max_w` pixels.
pub fn para(fonts: &UiFonts, text: impl Into<String>, size: f32, color: Color, max_w: Val) -> impl Bundle {
    (
        Text::new(text.into()),
        TextFont { font: fonts.main.clone().into(), font_size: FontSize::Px(size), ..default() },
        TextColor(color),
        TextLayout::linebreak(LineBreak::WordBoundary),
        Node { max_width: max_w, ..default() },
    )
}

// --- icons ---------------------------------------------------------------------------------
/// One of the white line icons in assets/images/ui, tinted.
pub fn icon(assets: &AssetServer, name: &str, size: f32, color: Color) -> impl Bundle {
    (
        ImageNode::new(assets.load(format!("images/ui/{name}.png"))).with_color(color),
        Node { width: Val::Px(size), height: Val::Px(size), flex_shrink: 0.0, ..default() },
        Pickable::IGNORE,
    )
}

// --- buttons -------------------------------------------------------------------------------
#[derive(Clone, Copy, PartialEq, Debug)]
pub enum Kind {
    /// filled cyan: the one main action on a screen
    Primary,
    /// raised, outlined: ordinary buttons
    Secondary,
    /// no fill until hovered: icon buttons, close buttons
    Ghost,
    /// red outline, red fill on hover: destructive
    Danger,
    /// a tab or pill; `active` fills it
    Tab,
    /// a list row; `active` marks the selection
    Row,
    /// filled with a custom colour (vessel React buttons, process tabs)
    Accent(Color),
    /// not clickable right now (locked vessels): flat, no hover response
    Disabled,
}

/// Visual state of a button. Change `active` to (de)select a tab or row.
#[derive(Component, Clone, Copy, Debug)]
pub struct Skin {
    pub kind: Kind,
    pub active: bool,
}

impl Skin {
    pub fn new(kind: Kind) -> Self {
        Self { kind, active: false }
    }
    pub fn active(kind: Kind, active: bool) -> Self {
        Self { kind, active }
    }

    /// (background, border) for an interaction state
    pub fn colors(&self, look: Look) -> (Color, Color) {
        let hov = look == Look::Hover;
        let prs = look == Look::Press;
        match self.kind {
            Kind::Primary => {
                let bg = if prs {
                    mix(CYAN, Color::BLACK, 0.25)
                } else if hov {
                    mix(CYAN, Color::WHITE, 0.15)
                } else {
                    CYAN
                };
                (bg, bg)
            }
            Kind::Secondary => {
                let bg = if prs {
                    LINE
                } else if hov {
                    HOVER
                } else {
                    RAISED
                };
                (bg, if hov || prs { CYAN.with_alpha(0.8) } else { LINE_STRONG })
            }
            Kind::Ghost => {
                let bg = if prs {
                    LINE
                } else if hov {
                    HOVER
                } else {
                    Color::NONE
                };
                (bg, Color::NONE)
            }
            Kind::Danger => {
                let bg = if prs {
                    mix(RED, Color::BLACK, 0.3)
                } else if hov {
                    RED.with_alpha(0.85)
                } else {
                    RED.with_alpha(0.12)
                };
                (bg, RED.with_alpha(if hov || prs { 1.0 } else { 0.7 }))
            }
            Kind::Tab => {
                if self.active {
                    (CYAN.with_alpha(if hov { 0.32 } else { 0.22 }), CYAN)
                } else {
                    (
                        if prs {
                            LINE
                        } else if hov {
                            HOVER
                        } else {
                            RAISED.with_alpha(0.6)
                        },
                        if hov { LINE_STRONG } else { LINE },
                    )
                }
            }
            Kind::Row => {
                if self.active {
                    (mix(RAISED, CYAN, 0.18), CYAN.with_alpha(0.9))
                } else {
                    (
                        if prs {
                            LINE
                        } else if hov {
                            HOVER
                        } else {
                            RAISED
                        },
                        if hov { LINE_STRONG } else { LINE.with_alpha(0.6) },
                    )
                }
            }
            Kind::Disabled => (RAISED.with_alpha(0.35), LINE.with_alpha(0.6)),
            Kind::Accent(c) => {
                let base = mix(c, Color::BLACK, 0.55);
                let bg = if prs {
                    mix(c, Color::BLACK, 0.35)
                } else if hov {
                    mix(c, Color::BLACK, 0.4)
                } else {
                    base
                };
                (bg, c)
            }
        }
    }
}

/// Recolours every skinned button when it is hovered, pressed, released or (de)selected.
pub fn skin_system(
    mut q: Query<
        (&Hovered, Has<Pressed>, &Skin, &mut BackgroundColor, &mut BorderColor),
        Or<(Changed<Hovered>, Changed<Skin>, Added<Skin>)>,
    >,
) {
    for (h, pressed, skin, mut bg, mut border) in &mut q {
        let (b, l) = skin.colors(Look::of(h, pressed));
        bg.0 = b;
        *border = BorderColor::all(l);
    }
}

/// The node part of a button: rounded, bordered, with its skin's resting colours.
pub fn button(kind: Kind, node: Node, radius: f32) -> impl Bundle {
    let skin = Skin::new(kind);
    let (bg, border) = skin.colors(Look::Rest);
    (
        Button,
        skin,
        Node { border_radius: BorderRadius::all(Val::Px(radius)), border: UiRect::all(Val::Px(1.0)), ..node },
        BackgroundColor(bg),
        BorderColor::all(border),
    )
}

/// A compact button with an optional icon and a label.
pub fn spawn_button(
    parent: &mut ChildSpawnerCommands,
    fonts: &UiFonts,
    assets: &AssetServer,
    kind: Kind,
    icon_name: Option<&str>,
    text: &str,
    marker: impl Bundle,
) -> Entity {
    let text_color = match kind {
        Kind::Primary => BG,
        Kind::Danger => TEXT,
        _ => TEXT,
    };
    parent
        .spawn((
            button(
                kind,
                Node {
                    height: Val::Px(34.0),
                    padding: UiRect::horizontal(Val::Px(14.0)),
                    column_gap: Val::Px(8.0),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    ..default()
                },
                R_SM,
            ),
            marker,
        ))
        .with_children(|b| {
            if let Some(n) = icon_name {
                b.spawn(icon(assets, n, 16.0, text_color));
            }
            if !text.is_empty() {
                b.spawn((label(fonts, text, SM, Weight::Semibold, text_color), Pickable::IGNORE));
            }
        })
        .id()
}

/// A square icon-only button (close, clear, settings...).
pub fn spawn_icon_button(
    parent: &mut ChildSpawnerCommands,
    assets: &AssetServer,
    icon_name: &str,
    size: f32,
    color: Color,
    marker: impl Bundle,
) -> Entity {
    parent
        .spawn((
            button(
                Kind::Ghost,
                Node {
                    width: Val::Px(size),
                    height: Val::Px(size),
                    align_items: AlignItems::Center,
                    justify_content: JustifyContent::Center,
                    ..default()
                },
                R_SM,
            ),
            marker,
        ))
        .with_children(|b| {
            b.spawn(icon(assets, icon_name, size * 0.55, color));
        })
        .id()
}

/// A small rounded label-on-colour chip ("Solid", "450 °C", "Catalyst: Platinum").
pub fn spawn_chip(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, text: &str, color: Color) {
    parent
        .spawn((
            Node {
                border_radius: BorderRadius::all(Val::Px(99.0)),
                padding: UiRect::axes(Val::Px(9.0), Val::Px(3.0)),
                border: UiRect::all(Val::Px(1.0)),
                ..default()
            },
            BackgroundColor(color.with_alpha(0.14)),
            BorderColor::all(color.with_alpha(0.65)),
            Pickable::IGNORE,
        ))
        .with_children(|c| {
            c.spawn((label(fonts, text, XS, Weight::Semibold, mix(color, TEXT, 0.45)), Pickable::IGNORE));
        });
}

/// An uppercase section heading with a hairline under it.
pub fn spawn_section_title(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, text: &str) {
    parent
        .spawn(Node {
            width: Val::Percent(100.0),
            padding: UiRect::bottom(Val::Px(6.0)),
            margin: UiRect::top(Val::Px(6.0)),
            border: UiRect::bottom(Val::Px(1.0)),
            ..default()
        })
        .insert(BorderColor::all(LINE))
        .with_children(|t| {
            t.spawn(label(fonts, text.to_uppercase(), XS, Weight::Bold, TEXT_3));
        });
}

/// The root of a full-screen view (Substances, Reactions, Tech Tree): sits under the
/// header, hidden until opened.
pub fn view_root(z: i32) -> impl Bundle {
    (
        GlobalZIndex(z),
        // a click on the view's background must not reach the lab buttons beneath it
        Pickable::default(),
        Node {
            position_type: PositionType::Absolute,
            left: Val::Px(0.0),
            right: Val::Px(0.0),
            top: Val::Px(HEADER_H),
            bottom: Val::Px(0.0),
            display: Display::None,
            ..default()
        },
        BackgroundColor(BG),
    )
}

/// Process colours, shared by vessels, tabs and chips.
pub use crate::systems::reaction_check::process_color;
