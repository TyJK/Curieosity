// src/components/ui_markers.rs
use crate::data::common::{MatterState, ProcessType};
use bevy::prelude::*;
// FIX: Add use statement for Ingredient
use crate::components::Ingredient;

#[derive(Component)]
pub struct Draggable;

#[derive(Component)]
pub struct DropTarget;

#[derive(Component)]
pub struct OnCanvas;

/// Top-level blue canvas root node.
#[derive(Component)]
pub struct ReactionCanvasRoot;

#[derive(Component)]
pub struct CanvasScrollingPane;

/// Optional: marks the main node of a vessel card
#[derive(Component)]
pub struct VesselCard;

/// A lab vessel set aside (hidden, untouched) while a challenge is played on the bench.
#[derive(Component)]
pub struct Stashed;

#[derive(Component, Clone, Debug)]
pub struct ProcessVessel {
    pub process: ProcessType,
}

/// Marks that an ingredient is inside a specific vessel
#[derive(Component, Clone, Debug)]
pub struct InVessel(pub Entity);

/// Marks the container node inside a vessel where ingredients are dropped
#[derive(Component)]
pub struct VesselIngredientZone;

// --- NEW COMPONENTS FOR REACTION GRAPH ---

/// Marks a drop-zone for a catalyst
#[derive(Component)]
pub struct VesselCatalystZone;

/// Marks an ingredient as being *in* the catalyst slot
#[derive(Component, Clone, Debug)]
pub struct InCatalystZone(pub Entity); // The vessel entity

/// An input port on a vessel card. This is a DropTarget for ReactionLinks.
#[derive(Component)]
pub struct InputPort;

/// An output port on a vessel card. This is a Draggable for ReactionLinks.
#[derive(Component, Clone, Debug)]
pub struct OutputPort {
    pub filter: PortFilter,
}

/// Defines how an OutputPort filters the products of a reaction.
#[derive(Clone, Debug)]
pub enum PortFilter {
    /// Passes all products.
    Any,
    /// Passes only products in a specific state (e.g., "Gas").
    State(MatterState),
    /// Passes products in order of stoichiometry (0 = main product, 1 = first byproduct, etc.)
    StoichiometricOrder(u8),
}

/// An entity that represents a connection between two vessels.
#[derive(Component)]
pub struct ReactionLink {
    pub from_vessel: Entity,
    pub from_port: Entity,
    pub to_vessel: Entity,
    pub to_port: Entity,
}

/// A temporary component added to a vessel after a successful reaction,
/// holding the products before they are propagated.
#[derive(Component)]
pub struct ReactionOutput(pub Vec<Ingredient>);

#[derive(Component)]
pub struct PendingReaction {
    pub timer: Timer,
    pub products: Vec<Ingredient>,
}
