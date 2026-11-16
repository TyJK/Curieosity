// src/data/common.rs

use serde::{Deserialize, Serialize};

// ... (ProcessType, Condition, Property, MatterState enums are unchanged) ...

/// The vessels a player can put on the bench. Each belongs to a family (Heat, Mix...)
/// at a tier; see `VESSEL_SPECS`. (The first twelve names are the original processes and
/// stay as they are: saves and the scraped library refer to them.)
#[derive(Debug, Deserialize, Serialize, Clone, PartialEq, Eq, Hash)]
pub enum ProcessType {
    Mix,
    Heat,
    Cool,
    Electrolysis,
    Catalysis,
    Pressurize,
    Smelting,
    Distillation,
    Irradiate,
    Polymerize,
    Wait,
    ApplyCurrent,
    // tier II and up, and the two newer families
    Flask,
    BlastFurnace,
    ArcFurnace,
    AirLiquefier,
    Column,
    ElectrolyticCell,
    NuclearReactor,
    Cyclotron,
    Cracker,
    HighPressure,
    DiamondPress,
    Fermenter,
    Bioreactor,
    CrystalPuller,
    CvdChamber,
}

/// One vessel: its name, family, tier within the family, and art.
#[derive(Debug, Clone)]
pub struct VesselSpec {
    pub name: &'static str,
    pub process: ProcessType,
    /// the family ("Heat", "Mix"...): a vessel can run anything its family does at its tier
    /// or below
    pub category: &'static str,
    pub tier: u8,
    pub art: &'static str,
    /// whether the card has a catalyst slot
    pub catalyst_slot: bool,
}

const fn v(
    name: &'static str,
    process: ProcessType,
    category: &'static str,
    tier: u8,
    art: &'static str,
    catalyst_slot: bool,
) -> VesselSpec {
    VesselSpec { name, process, category, tier, art, catalyst_slot }
}

/// Every vessel, in the order the vessel list shows them (roughly the order they unlock).
pub const VESSEL_SPECS: &[VesselSpec] = &[
    v("Mortar", ProcessType::Mix, "Mix", 1, "mortar", false),
    v("Fire", ProcessType::Heat, "Heat", 1, "fire", false),
    v("Fermenter", ProcessType::Fermenter, "Biology", 1, "fermenter", false),
    v("Bloomery", ProcessType::Smelting, "Heat", 2, "bloomery", false),
    v("Still", ProcessType::Distillation, "Distillation", 1, "still", false),
    v("Ice Bath", ProcessType::Cool, "Cool", 1, "ice_bath", false),
    v("Irradiator", ProcessType::Irradiate, "Radiation", 1, "irradiator", false),
    v("Glass Flask", ProcessType::Flask, "Mix", 2, "flask", false),
    v("Voltaic Cell", ProcessType::Electrolysis, "Electrolysis", 1, "voltaic_cell", false),
    v("Catalyst Bed", ProcessType::Catalysis, "Catalysis", 1, "catalyst_bed", true),
    v("Polymer Reactor", ProcessType::Polymerize, "Polymer", 1, "polymer_reactor", false),
    v("Blast Furnace", ProcessType::BlastFurnace, "Heat", 3, "blast_furnace", false),
    v("Fractionating Column", ProcessType::Column, "Distillation", 2, "column", false),
    v("Electrolytic Cell", ProcessType::ElectrolyticCell, "Electrolysis", 2, "electrolytic_cell", false),
    v("Air Liquefier", ProcessType::AirLiquefier, "Cool", 2, "air_liquefier", false),
    v("Autoclave", ProcessType::Pressurize, "Pressure", 1, "autoclave", false),
    v("Arc Furnace", ProcessType::ArcFurnace, "Heat", 4, "arc_furnace", false),
    v("High-Pressure Reactor", ProcessType::HighPressure, "Pressure", 2, "high_pressure", true),
    v("Catalytic Cracker", ProcessType::Cracker, "Catalysis", 2, "cracker", true),
    v("Bioreactor", ProcessType::Bioreactor, "Biology", 2, "bioreactor", true),
    v("Nuclear Reactor", ProcessType::NuclearReactor, "Radiation", 2, "nuclear_reactor", false),
    v("Crystal Puller", ProcessType::CrystalPuller, "Fabrication", 1, "crystal_puller", false),
    v("Diamond Press", ProcessType::DiamondPress, "Pressure", 3, "diamond_press", true),
    v("CVD Chamber", ProcessType::CvdChamber, "Fabrication", 2, "cvd_chamber", true),
    v("Cyclotron", ProcessType::Cyclotron, "Radiation", 3, "cyclotron", false),
];

impl ProcessType {
    pub fn spec(&self) -> Option<&'static VesselSpec> {
        VESSEL_SPECS.iter().find(|s| &s.process == self)
    }
    /// The family; processes with no vessel are their own family.
    pub fn family(&self) -> &'static str {
        self.spec().map(|s| s.category).unwrap_or("Other")
    }
    pub fn tier(&self) -> u8 {
        self.spec().map(|s| s.tier).unwrap_or(1)
    }
    pub fn has_catalyst_slot(&self) -> bool {
        self.spec().is_some_and(|s| s.catalyst_slot)
    }
    /// The vessels of this one's family, highest tier first.
    pub fn family_members(&self) -> Vec<&'static VesselSpec> {
        let fam = self.family();
        let mut m: Vec<&'static VesselSpec> = VESSEL_SPECS.iter().filter(|s| s.category == fam).collect();
        m.sort_by_key(|x| std::cmp::Reverse(x.tier));
        m
    }
}

/// Specific conditions required for a reaction to occur.
/// Based on the GDD's technical implementation plan and
/// advanced process details.
#[derive(Debug, Deserialize, Clone, PartialEq)]
pub enum Condition {
    Temperature(f32),
    Pressure(f32),
    RequiresCatalyst(u32),
    RequiresSolvent(u32),
    RequiresPurity(f32),
}

/// Chemical properties that can be attached to a substance.
/// Based on the GDD's technical implementation plan and
/// advanced topics sections.
#[derive(Debug, Deserialize, Clone, PartialEq, Eq, Hash)]
pub enum Property {
    IsAcid,
    IsBase,
    IsMetal,
    IsCatalystFor(u32),
    IsRadioactive,
    IsMonomer,
    IsPolymer,
    IsElectrolyte,
    IsPhotochromic,
}

/// A *runtime* calculated state of matter.
/// This is NOT stored in the database.
#[derive(Debug, Deserialize, Clone, Copy, PartialEq, Eq, Hash)]
pub enum MatterState {
    Solid,
    Liquid,
    Gas,
    Plasma,
    Aqueous,
    SupercriticalFluid,
}

//
// THIS IS THE FIX:
// Moved StoichPoint here from reactions.rs to fix the path error.
//
/// Represents a point in the stoichiometric equation.
/// Uses "moles" as the coefficient, as specified in the GDD.
#[derive(Debug, Deserialize, Clone, PartialEq, Eq, Hash)]
pub struct StoichPoint {
    /// The ID of the substance being used/created.
    pub substance_id: u32,
    /// The stoichiometric coefficient (molar ratio).
    pub moles: u32,
}
