// src/components/mod.rs

// This file acts as the public API for the components module.
// We export everything from its sub-modules.

pub mod ingredient;
pub mod ui_markers;
// We can add other component files here later, like `process.rs` or `reaction.rs`
// if they contain component definitions.

pub use ingredient::{format_formula, Ingredient};
pub use ui_markers::{
    CanvasScrollingPane, Draggable, DropTarget, InCatalystZone, InVessel, InputPort, OnCanvas, OutputPort, PortFilter,
    ProcessVessel, ReactionCanvasRoot, ReactionLink, ReactionOutput, VesselCard, VesselCatalystZone, VesselClearButton,
    VesselDeleteButton, VesselIngredientZone, VesselReactButton,
};
