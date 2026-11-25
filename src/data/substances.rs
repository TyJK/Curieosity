// src/data/substances.rs

use super::common::{Grade, MatterState, Property};
use bevy::{asset::Asset, reflect::TypePath};
use serde::Deserialize;
use std::collections::HashMap;

/// The Asset definition. This is what Bevy's AssetServer will load.
#[derive(Debug, Deserialize, Asset, TypePath, Clone, Default)]
pub struct Substances(pub HashMap<u32, Substance>);

/// Rich, element-only physics (present for element substances, `None` for compounds).
#[derive(Debug, Deserialize, Clone)]
pub struct ElementInfo {
    pub atomic_number: u32,
    pub atomic_weight: f32,
    #[serde(default)]
    pub group: Option<u32>,
    #[serde(default)]
    pub period: Option<u32>,
    #[serde(default)]
    pub block: Option<String>,
    #[serde(default)]
    pub electron_config: Option<String>,
    #[serde(default)]
    pub electronegativity_pauling: Option<f32>,
    #[serde(default)]
    pub first_ionization_kj_mol: Option<f32>,
    #[serde(default)]
    pub electron_affinity_kj_mol: Option<f32>,
    #[serde(default)]
    pub atomic_radius_pm: Option<f32>,
    #[serde(default)]
    pub discoverer: Option<String>,
    #[serde(default)]
    pub discovery_year: Option<i64>,

    // --- Narrative + nuclear enrichment (fills out the element pages) ---
    #[serde(default)]
    pub overview: Option<String>,
    #[serde(default)]
    pub discovery_story: Option<String>,
    #[serde(default)]
    pub isotopes_summary: Option<String>,
    #[serde(default)]
    pub magnetic_ordering: Option<String>,
}

/// Defines a single chemical substance (element or compound).
#[derive(Debug, Deserialize, Clone)]
pub struct Substance {
    pub id: u32,
    pub name: String,
    pub formula: String,

    pub state: MatterState,
    pub molar_mass_g_mol: f32,

    // --- Appearance ---
    pub color_hex: Option<String>,

    // --- Thermodynamic Properties ---
    pub melting_point_c: Option<f32>,
    pub boiling_point_c: Option<f32>,
    pub density_g_cm3: Option<f32>,

    // --- State-Specific Properties ---
    pub heat_capacity_solid_j_g_c: Option<f32>,
    pub heat_capacity_liquid_j_g_c: Option<f32>,
    pub heat_capacity_gas_j_g_c: Option<f32>,

    // --- Phase Change Properties ---
    pub enthalpy_fusion_kj_mol: Option<f32>,
    pub enthalpy_vaporization_kj_mol: Option<f32>,

    // --- Chemical Properties ---
    pub enthalpy_formation_kj_mol: Option<f32>,
    pub solubility_g_per_100ml_h2o: Option<f32>,

    // --- Advanced Topic Properties ---
    pub standard_potential_v: Option<f32>,
    pub half_life_seconds: Option<f64>,
    pub decay_product_id: Option<u32>,
    pub decay_particle_id: Option<u32>,

    #[serde(default)]
    pub properties: Vec<Property>,

    // --- Enrichment: detail-panel richness for compounds (pass 1) ---
    // All optional + serde(default), so old RON without them still loads.
    /// One-line/paragraph description of the compound (from the source JSON).
    #[serde(default)]
    pub description: Option<String>,
    /// Where `description` comes from ("Wikipedia", "CAMEO Chemicals", "ChEBI", "LOTUS" or
    /// "Curieosity"); set by tools/data/audit_library.py, shown under the text, and listed
    /// in the credits. A description without one isn't shipped.
    #[serde(default)]
    pub text_source: Option<String>,
    /// Short hazard summary, e.g. "H317: May cause an allergic skin reaction".
    #[serde(default)]
    pub hazard_summary: Option<String>,
    /// A few consumer/industrial uses.
    #[serde(default)]
    pub uses: Vec<String>,
    /// Octanol-water partition coefficient (lipophilicity).
    #[serde(default)]
    pub logp: Option<f32>,
    /// Appearance / physical description.
    #[serde(default)]
    pub appearance: Option<String>,

    // --- Codex layer (pass 2) ---
    /// Alternative names for this substance.
    #[serde(default)]
    pub synonyms: Vec<String>,
    /// External reference links as (label, url) pairs (Wikipedia, PubChem, ChEBI, …).
    #[serde(default)]
    pub references: Vec<(String, String)>,

    /// Present for elements; carries atomic number, electronegativity, discovery, etc.
    #[serde(default)]
    pub element_info: Option<ElementInfo>,

    /// The later stage of the game this substance belongs to ("Pharmaceuticals"). While it is
    /// set the substance is a locked preview: it has a page in the Substance Library, under
    /// "Coming later", but no reaction makes it yet.
    #[serde(default)]
    pub stage: Option<String>,

    // --- Industry: foundations for the factory stages ---
    /// Tonnes made a year: the US production and imports reported to regulators (often the
    /// low end of a reporting band).
    #[serde(default)]
    pub production_t_year: Option<f32>,
    /// Tonnes made a year worldwide, for the big commodities the national records miss: a rough
    /// figure entered by hand (two significant figures), too big a total to track precisely.
    #[serde(default)]
    pub world_t_year: Option<f32>,
    /// UN dangerous-goods transport class ("3", "6.1"); None: not regulated, or not known.
    #[serde(default)]
    pub transport_class: Option<String>,
    /// The stricter grades it is also sold at (everything sells at technical grade).
    #[serde(default)]
    pub grades: Vec<Grade>,
    /// Said instead of a melting or boiling point it never reaches ("Decomposes at 132 °C"),
    /// from the checked values in pages.ron (data::pages).
    #[serde(default)]
    pub phase_note: Option<String>,
}

impl Substance {
    /// A bare substance with only identity fields set; authored patches fill in the rest.
    pub fn blank(id: u32) -> Self {
        Self {
            id,
            name: format!("#{}", id),
            formula: String::new(),
            state: MatterState::Solid,
            molar_mass_g_mol: 0.0,
            color_hex: None,
            melting_point_c: None,
            boiling_point_c: None,
            density_g_cm3: None,
            heat_capacity_solid_j_g_c: None,
            heat_capacity_liquid_j_g_c: None,
            heat_capacity_gas_j_g_c: None,
            enthalpy_fusion_kj_mol: None,
            enthalpy_vaporization_kj_mol: None,
            enthalpy_formation_kj_mol: None,
            solubility_g_per_100ml_h2o: None,
            standard_potential_v: None,
            half_life_seconds: None,
            decay_product_id: None,
            decay_particle_id: None,
            properties: Vec::new(),
            description: None,
            text_source: None,
            hazard_summary: None,
            uses: Vec::new(),
            logp: None,
            appearance: None,
            synonyms: Vec::new(),
            references: Vec::new(),
            element_info: None,
            stage: None,
            production_t_year: None,
            world_t_year: None,
            transport_class: None,
            grades: Vec::new(),
            phase_note: None,
        }
    }

    /// Made and used at once, never kept (Property::IsTransient).
    pub fn is_transient(&self) -> bool {
        self.properties.contains(&Property::IsTransient)
    }

    /// Its UN transport class: radioactive substances travel as class 7 whatever else they are.
    pub fn transport_class(&self) -> Option<&str> {
        if self.properties.contains(&Property::IsRadioactive) {
            return Some("7");
        }
        self.transport_class.as_deref()
    }

    /// The reference the page leads with (see `common::primary_reference`).
    pub fn primary_reference(&self) -> Option<&(String, String)> {
        super::common::primary_reference(&self.references)
    }
}

/// The `text_source` of the game's own writing.
pub const CURIEOSITY: &str = "Curieosity";

/// The authored (canon) substance layer: `assets/data/authored_substances.ron`, generated by
/// `tools/data/gen_authored.py`. Each entry patches the scraped library entry with the same
/// id (cleaning its name/formula, adding narrative and links) or, when the id is new, creates
/// the substance outright. Only the fields an entry sets are applied.
#[derive(Debug, Deserialize, Asset, TypePath, Clone, Default)]
pub struct SubstancePatches(pub HashMap<u32, SubstancePatch>);

#[derive(Debug, Deserialize, Clone, Default)]
#[serde(default)]
pub struct SubstancePatch {
    pub name: Option<String>,
    pub formula: Option<String>,
    pub state: Option<MatterState>,
    pub molar_mass_g_mol: Option<f32>,
    pub color_hex: Option<String>,
    pub melting_point_c: Option<f32>,
    pub boiling_point_c: Option<f32>,
    pub density_g_cm3: Option<f32>,
    pub enthalpy_formation_kj_mol: Option<f32>,
    pub properties: Option<Vec<Property>>,
    pub description: Option<String>,
    pub hazard_summary: Option<String>,
    pub uses: Option<Vec<String>>,
    pub appearance: Option<String>,
    pub synonyms: Option<Vec<String>>,
    pub references: Option<Vec<(String, String)>>,
    pub stage: Option<String>,
    pub production_t_year: Option<f32>,
    pub world_t_year: Option<f32>,
    pub transport_class: Option<String>,
    pub grades: Option<Vec<Grade>>,
}

impl SubstancePatches {
    /// Apply every patch onto `subs`, creating substances whose ids don't exist yet.
    /// Returns (patched, created).
    pub fn apply_to(&self, subs: &mut Substances) -> (usize, usize) {
        let (mut patched, mut created) = (0, 0);
        for (&id, p) in &self.0 {
            let entry = subs.0.entry(id).or_insert_with(|| {
                created += 1;
                Substance::blank(id)
            });
            patched += 1;
            if let Some(v) = &p.name {
                entry.name = v.clone();
            }
            if let Some(v) = &p.formula {
                entry.formula = v.clone();
            }
            if let Some(v) = p.state {
                entry.state = v;
            }
            if let Some(v) = p.molar_mass_g_mol {
                entry.molar_mass_g_mol = v;
            }
            if let Some(v) = &p.color_hex {
                entry.color_hex = Some(v.clone());
            }
            if let Some(v) = p.melting_point_c {
                entry.melting_point_c = Some(v);
            }
            if let Some(v) = p.boiling_point_c {
                entry.boiling_point_c = Some(v);
            }
            if let Some(v) = p.density_g_cm3 {
                entry.density_g_cm3 = Some(v);
            }
            if let Some(v) = p.enthalpy_formation_kj_mol {
                entry.enthalpy_formation_kj_mol = Some(v);
            }
            if let Some(v) = &p.properties {
                entry.properties = v.clone();
            }
            if let Some(v) = &p.description {
                entry.description = Some(v.clone());
                entry.text_source = Some(CURIEOSITY.to_string());
            }
            if let Some(v) = &p.hazard_summary {
                entry.hazard_summary = Some(v.clone());
            }
            if let Some(v) = &p.uses {
                entry.uses = v.clone();
            }
            if let Some(v) = &p.appearance {
                entry.appearance = Some(v.clone());
            }
            if let Some(v) = &p.synonyms {
                entry.synonyms = v.clone();
            }
            if let Some(v) = &p.references {
                // Authored links go first; keep any library links the patch didn't repeat.
                let mut refs = v.clone();
                for r in &entry.references {
                    if !refs.iter().any(|(_, url)| url == &r.1) {
                        refs.push(r.clone());
                    }
                }
                entry.references = refs;
            }
            if let Some(v) = &p.stage {
                entry.stage = Some(v.clone());
            }
            if let Some(v) = p.production_t_year {
                entry.production_t_year = Some(v);
            }
            if let Some(v) = p.world_t_year {
                entry.world_t_year = Some(v);
            }
            if let Some(v) = &p.transport_class {
                entry.transport_class = Some(v.clone());
            }
            if let Some(v) = &p.grades {
                entry.grades = v.clone();
            }
        }
        (patched, created)
    }
}
