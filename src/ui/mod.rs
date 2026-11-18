// src/ui/mod.rs
use bevy::prelude::{Component, Node};

pub mod codex;
pub mod credits;
pub mod detail_panel;
pub mod focus;
pub mod hint;
pub mod inventory;
pub mod main_menu;
pub mod onboarding;
pub mod process_toolbar;
pub mod reaction_canvas;
pub mod reaction_library;
pub mod settings;
pub mod shell;
pub mod tech_tree;
pub mod theme;
pub mod toasts;
pub mod virtual_list;

// Bevy 0.20 deprecates `Interaction` and `Button` in favour of `ui_widgets::Button` with the
// `Hovered` and `Pressed` components. `Interaction` still works (bevy_ui updates it on every
// node that has one) and all uses go through this alias, so moving to the new widgets is one
// deliberate change before Bevy 0.21 removes it, not a warning at every button. The old
// `Button` can no longer be named outside bevy_ui, so the game has its own: the same marker.
#[allow(deprecated)]
pub type Interaction = bevy::ui::Interaction;

/// A pressable node: bevy_ui keeps its `Interaction` up to date, and it blocks the pointer
/// from what lies under it (as Bevy's own `Button` did before 0.20).
#[derive(Component, Debug, Default, Clone, Copy, PartialEq, Eq)]
#[require(Node, bevy::ui::FocusPolicy::Block, Interaction)]
pub struct Button;
