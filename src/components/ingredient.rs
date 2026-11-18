use bevy::prelude::*;

// FIX: Import Property so we can use it
use crate::data::common::{MatterState, Property};

/// Represents a concrete, manipulable chemical “thing” in the game world / UI.
/// This is the ECS-facing counterpart to your data-driven `Substance`.
#[derive(Component, Clone, Debug, PartialEq, Eq, Hash)]
pub struct Ingredient {
    /// A stable ID you can line up with your `Substance` database later.
    pub id: u32,
    pub name: String,
    pub formula: String,
    pub state: MatterState,
    pub properties: Vec<Property>,
    pub amount: u32,
}

/// Format a plain ASCII formula like "H2O" into "H₂O" using Unicode subscripts.
/// This is purely visual; the underlying data stays ASCII.
pub fn format_formula(formula: &str) -> String {
    formula
        .chars()
        .map(|ch| match ch {
            '0' => '₀',
            '1' => '₁',
            '2' => '₂',
            '3' => '₃',
            '4' => '₄',
            '5' => '₅',
            '6' => '₆',
            '7' => '₇',
            '8' => '₈',
            '9' => '₉',
            _ => ch,
        })
        .collect()
}

impl Ingredient {
    pub fn new(
        id: u32,
        name: impl Into<String>,
        formula: impl Into<String>,
        state: MatterState,
        properties: Vec<Property>,
    ) -> Self {
        Self { id, name: name.into(), formula: formula.into(), state, properties, amount: 1 }
    }

    /// Made and used at once, never kept (Property::IsTransient).
    pub fn is_transient(&self) -> bool {
        self.properties.contains(&Property::IsTransient)
    }

    /// Convenience label for UI like: "Hydrogen (H)".
    pub fn label(&self) -> String {
        let base = format_formula(&self.formula);
        if self.amount <= 1 {
            base
        } else {
            // e.g. "H₂O x2"
            format!("{} x{}", base, self.amount)
        }
    }

    /// Temporary hard-coded starting inventory.
    ///
    /// Once your `Substances` data file is populated, we can replace this
    /// with something data-driven (e.g. look up by substance ID).
    pub fn starting_set() -> Vec<Self> {
        use MatterState::*;

        vec![
            // Common ambient gases (substances, not bare elements)
            Self::new(1, "Hydrogen gas (H₂)", "H2", Gas, vec![]), // H2
            Self::new(2, "Helium gas (He)", "He", Gas, vec![]),   // monatomic
            Self::new(3, "Carbon (solid)", "C", Solid, vec![]),   // generic solid C
            Self::new(4, "Nitrogen gas (N₂)", "N2", Gas, vec![]), // N2
            Self::new(5, "Oxygen gas (O₂)", "O2", Gas, vec![]),   // O2
            Self::new(6, "Sodium metal (Na)", "Na", Solid, vec![]), // solid Na
            Self::new(7, "Chlorine gas (Cl₂)", "Cl2", Gas, vec![]), // Cl2
            // Simple liquids so we can see beakers
            Self::new(8, "Water", "H2O", Liquid, vec![]),
            Self::new(9, "Ethanol", "C2H5OH", Liquid, vec![]),
            // --- NEW TEST CATALYST ---
            // We add a new ingredient with the IsCatalystFor property.
            // The `0` is a dummy ID, it just needs to have the property.
            Self::new(10, "Iron (catalyst)", "Fe", Solid, vec![Property::IsCatalystFor(0)]),
        ]
    }

    pub fn from_substance_id(substance_id: u32) -> Option<Self> {
        Self::starting_set().into_iter().find(|ing| ing.id == substance_id)
    }
}
