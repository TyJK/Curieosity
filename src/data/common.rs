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
    Centrifuge,
    Ultracentrifuge,
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
    v("Centrifuge", ProcessType::Centrifuge, "Separation", 1, "centrifuge", false),
    v("Air Liquefier", ProcessType::AirLiquefier, "Cool", 2, "air_liquefier", false),
    v("Autoclave", ProcessType::Pressurize, "Pressure", 1, "autoclave", false),
    v("Arc Furnace", ProcessType::ArcFurnace, "Heat", 4, "arc_furnace", false),
    v("High-Pressure Reactor", ProcessType::HighPressure, "Pressure", 2, "high_pressure", true),
    v("Catalytic Cracker", ProcessType::Cracker, "Catalysis", 2, "cracker", true),
    v("Bioreactor", ProcessType::Bioreactor, "Biology", 2, "bioreactor", true),
    v("Ultracentrifuge", ProcessType::Ultracentrifuge, "Separation", 2, "ultracentrifuge", false),
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

/// The reference a page leads with: its Wikipedia article if it has one, else its first
/// reference (PubChem, for compounds without an article of their own).
pub fn primary_reference(refs: &[(String, String)]) -> Option<&(String, String)> {
    refs.iter().find(|(_, url)| url.contains("wikipedia.org")).or_else(|| refs.first())
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
    /// A medicine: the Codex marks it and says how medicines are really made and taken.
    IsMedicine,
    /// A family of closely related compounds treated as one; its formula is a typical member's.
    IsClass,
}

/// A commercial grade: how pure buyers of that grade expect it to be. Everything is sold at
/// technical grade; a substance's `grades` list the stricter ones it is also sold at. The
/// purities are the game's round figures for the usual standards (food codices,
/// pharmacopoeias, semiconductor specifications), whose real limits differ substance by substance.
#[derive(Debug, Deserialize, Clone, Copy, PartialEq, Eq, Hash)]
pub enum Grade {
    Technical,
    Food,
    Pharmaceutical,
    Electronic,
}

impl Grade {
    /// The lowest purity (mass fraction) that still sells at this grade.
    pub fn min_purity(self) -> f32 {
        match self {
            Grade::Technical => 0.95,
            Grade::Food => 0.99,
            Grade::Pharmaceutical => 0.995,
            Grade::Electronic => 0.99999,
        }
    }

    pub fn label(self) -> &'static str {
        match self {
            Grade::Technical => "Technical",
            Grade::Food => "Food",
            Grade::Pharmaceutical => "Pharmaceutical",
            Grade::Electronic => "Electronic",
        }
    }
}

/// The name of a UN dangerous-goods transport class ("3" is "Flammable liquid").
pub fn un_class_name(class: &str) -> Option<&'static str> {
    Some(match class {
        "1" => "Explosive",
        "2.1" => "Flammable gas",
        "2.2" => "Compressed gas",
        "2.3" => "Toxic gas",
        "3" => "Flammable liquid",
        "4.1" => "Flammable solid",
        "4.2" => "Spontaneously combustible",
        "4.3" => "Dangerous when wet",
        "5.1" => "Oxidiser",
        "5.2" => "Organic peroxide",
        "6.1" => "Toxic",
        "7" => "Radioactive",
        "8" => "Corrosive",
        "9" => "Miscellaneous (environmental hazard)",
        _ => return None,
    })
}

/// How a plant stores and moves a substance, from its state and transport class.
pub fn handling(state: MatterState, class: Option<&str>) -> &'static str {
    match class {
        Some("1") => "Licensed magazines, small lots, no sparks or friction",
        Some("2.3") => "Cylinders in closed, gas-detected rooms; breathing sets on hand",
        Some("2.1") => "Pressure cylinders or tanks, away from flames, earthed",
        Some("2.2") => "Pressure cylinders, chained upright",
        Some("3") => "Earthed drums or tanks, away from sparks and heat",
        Some("4.1") => "Dry and cool, away from flames",
        Some("4.2") => "Under nitrogen or oil, away from air",
        Some("4.3") => "Bone dry, sealed, under nitrogen",
        Some("5.1") => "Apart from fuels and organics",
        Some("5.2") => "Refrigerated, apart from fuels, in vented packs",
        Some("6.1") => "Sealed containers, gloves, ventilated rooms",
        Some("7") => "Shielded, licensed containers",
        Some("8") => "Lined or plastic containers, face shield and gloves",
        Some("9") => "Bunded, kept out of drains and water",
        _ => match state {
            MatterState::Gas => "Pressure cylinders",
            MatterState::Liquid | MatterState::Aqueous => "Drums, totes or tankers",
            _ => "Bags, drums or bulk",
        },
    }
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
