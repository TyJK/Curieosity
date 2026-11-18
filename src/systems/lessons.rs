// src/systems/lessons.rs
//
// Little lessons in chemistry, worked out from a reaction itself, so every step in the
// game has one without anyone writing thousands:
//   * lesson(): the kind of change a step is (neutralisation, smelting, displacement,
//     electrolysis...) and what that kind of change needs. The Hint card gives it with the
//     first ingredient, so the player learns the idea along with the answer.
//   * why_not(): when a vessel's contents don't react, why not, where the chemistry can
//     tell (two acids, a metal too weak to push another out, one substance alone, a noble
//     gas), or how near the player is (one ingredient short, one too many).
// Pure functions over the content, so the content tests can run them over every step.
use std::collections::BTreeSet;

use crate::data::common::{ProcessType, Property};
use crate::data::reactions::Reaction;
use crate::data::substances::{Substance, Substances};
use crate::resources::recipe_database::RecipeDatabase;

/// Metals, most reactive first: a metal pushes any below it out of its compounds (hydrogen
/// marks which metals acids dissolve).
const ACTIVITY: [&str; 17] =
    ["K", "Na", "Li", "Ca", "Mg", "Al", "Zn", "Fe", "Ni", "Sn", "Pb", "H", "Cu", "Hg", "Ag", "Pt", "Au"];
const NOBLE_GASES: [&str; 6] = ["He", "Ne", "Ar", "Kr", "Xe", "Rn"];

/// The element symbols in a formula, in order of first appearance.
pub fn symbols(formula: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    let chars: Vec<char> = formula.chars().collect();
    let mut i = 0;
    while i < chars.len() {
        if chars[i].is_ascii_uppercase() {
            let mut sym = chars[i].to_string();
            if i + 1 < chars.len() && chars[i + 1].is_ascii_lowercase() {
                sym.push(chars[i + 1]);
                i += 1;
            }
            if !out.contains(&sym) {
                out.push(sym);
            }
        }
        i += 1;
    }
    out
}

fn is_element(s: &Substance) -> bool {
    s.element_info.is_some() || symbols(&s.formula).len() == 1 && !s.formula.chars().any(|c| c.is_ascii_digit())
}

fn has(s: &Substance, p: Property) -> bool {
    s.properties.contains(&p)
}

fn rank(sym: &str) -> Option<usize> {
    ACTIVITY.iter().position(|m| *m == sym)
}

/// The metal a compound is a salt or oxide of: its first symbol on the activity list.
fn metal_of(s: &Substance) -> Option<String> {
    symbols(&s.formula).into_iter().find(|x| x != "H" && rank(x).is_some())
}

fn lookup<'a>(subs: &'a Substances, ids: &[u32]) -> Vec<&'a Substance> {
    ids.iter().filter_map(|id| subs.0.get(id)).collect()
}

/// The lesson a step teaches: the kind of change it is and what that kind of change needs.
/// The vessel's family decides first where it says it all (electrolysis, distillation...),
/// then the reactants and products (an acid meeting a base, carbon meeting an ore...).
pub fn lesson(r: &Reaction, subs: &Substances) -> String {
    use crate::data::common::MatterState;
    let ins = lookup(subs, &r.reactants.iter().map(|s| s.substance_id).collect::<Vec<_>>());
    let outs = lookup(subs, &r.products.iter().map(|s| s.substance_id).collect::<Vec<_>>());
    let any_in = |f: &dyn Fn(&Substance) -> bool| ins.iter().any(|s| f(s));
    let any_out = |f: &dyn Fn(&Substance) -> bool| outs.iter().any(|s| f(s));
    let formula_in = |f: &str| ins.iter().any(|s| s.formula == f);
    let formula_out = |f: &str| outs.iter().any(|s| s.formula == f);
    let acid = |s: &Substance| has(s, Property::IsAcid);
    let base = |s: &Substance| has(s, Property::IsBase);
    let metal_el = |s: &Substance| is_element(s) && rank(&s.formula).is_some_and(|i| ACTIVITY[i] != "H");
    let organic = |s: &Substance| {
        let sy = symbols(&s.formula);
        sy.iter().any(|x| x == "C") && sy.iter().any(|x| x == "H")
    };
    let carbon = |s: &Substance| {
        let n = s.name.to_lowercase();
        s.formula == "C" || s.formula == "CO" || n.contains("charcoal") || n.contains("coke") || n.contains("coal")
    };
    let carbonate = |s: &Substance| s.formula.contains("CO3");
    let alcohol = |s: &Substance| {
        let n = s.name.to_lowercase();
        organic(s) && (n.ends_with("anol") || n.ends_with("yl alcohol") || n == "glycerol" || n == "ethanol")
    };
    let halogen = |s: &Substance| ["Cl2", "Br2", "I2", "F2"].contains(&s.formula.as_str());
    let oxygen = |s: &Substance| s.formula == "O2" || s.name.eq_ignore_ascii_case("air");
    let heat = r.process.family() == "Heat";
    let text = match r.process.family() {
        "Electrolysis" => "Electrolysis: an electric current pulls a compound apart where heat can't, the metal (or hydrogen) going to one electrode and the rest to the other.",
        "Distillation" => "Distillation: boiling sorts a mixture by boiling point. What boils first rises as vapour and is cooled back to liquid, apart from the rest.",
        "Cool" => "Cooling: as it gets colder, a solid crystallises out of its solution (or a gas condenses), and can be taken away from what stays dissolved.",
        "Biology" => "Living chemistry: yeast, bacteria or moulds do the work, turning sugars and nutrients into what they make, gently and near body heat.",
        "Polymer" => "Polymerisation: small molecules (monomers) join end to end, thousands at a time, into the long chains that make plastics, rubbers and fibres.",
        "Separation" => "Separation: spinning sorts a mixture by density, the heavier parts flung outward from the lighter ones, without changing what any of them is.",
        "Fabrication" => "Fabrication: here the work is the material's form, a perfect crystal or a film atoms thick, laid down slowly so every atom sits where it should.",
        "Radiation" if r.process == ProcessType::Irradiate => "Light as a reactant: a photon of the right energy breaks a bond that heat would leave alone, and the pieces react.",
        "Radiation" => "Nuclear change: no chemistry alters a nucleus, but a neutron or a fast particle can, turning one element (or isotope) into another.",
        "Pressure" => "Pressure: squeezing gases pushes a reaction toward fewer gas molecules, and lets water stay liquid far above its boiling point.",
        "Catalysis" if r.required_catalyst().is_some() => "Catalysis: the catalyst in its slot lets the reaction take an easier path and comes out unchanged, so the right catalyst matters more than more heat.",
        "Catalysis" => "Catalysis: a hot catalyst bed gives molecules an easier path to react, and comes out unchanged to do it again.",
        _ if any_in(&acid) && any_in(&carbonate) && formula_out("CO2") => "An acid frees carbon dioxide from a carbonate: the fizz is the gas escaping, and a salt is left behind.",
        _ if any_in(&acid) && any_in(&base) => "Neutralisation: an acid and a base cancel each other out into a salt and, usually, water.",
        _ if any_in(&acid) && any_in(&metal_el) && formula_out("H2") => "A reactive metal dissolves in acid, giving off hydrogen and leaving its salt behind: the further up the reactivity series, the faster.",
        _ if heat && any_in(&carbon) && any_out(&metal_el) => "Smelting: in a hot enough fire, carbon (charcoal, coke) takes the oxygen from a metal's ore and leaves the metal.",
        _ if any_in(&metal_el) && any_out(&metal_el) => "Displacement: a more reactive metal pushes a less reactive one out of its compound, and takes its place.",
        _ if any_in(&acid) && any_in(&alcohol) && formula_out("H2O") => "Esterification: an acid and an alcohol join and give off water. Esters are the smells of fruit, and of glues and solvents.",
        _ if formula_in("HNO3") && any_in(&organic) => "Nitration: nitric acid (usually with sulfuric acid to drive it) swaps a hydrogen on the molecule for a nitro group, NO2.",
        _ if any_in(&halogen) && any_in(&organic) => "Halogenation: a halogen (chlorine, bromine...) takes a hydrogen's place on the molecule, or adds across a double bond.",
        _ if formula_in("H2") && ins.len() >= 2 => "Hydrogenation: hydrogen adds on, filling double bonds or taking oxygen away. Fats harden and ores give up their metal this way.",
        _ if heat && any_in(&oxygen) => "Burning and oxidation: oxygen from the air combines with what is heated, often giving out heat and light.",
        _ if heat && any_in(&carbonate) && formula_out("CO2") => "Calcination: heat drives carbon dioxide out of a carbonate, the way limestone becomes quicklime.",
        _ if heat && any_in(&organic) && formula_out("CO2") => "Decarboxylation: heat splits carbon dioxide off the molecule, leaving a smaller one behind.",
        _ if heat && ins.len() == 1 && formula_out("H2O") => "Dehydration: heat drives the water out of it, leaving something drier and often quite different.",
        _ if heat && ins.len() == 1 => "Decomposition: heat alone breaks it apart into simpler substances.",
        _ if any_in(&oxygen) => "Oxidation: oxygen combines with it, slowly (like rusting) or fast (like burning).",
        _ if formula_in("H2O") && ins.len() == 2 && outs.len() >= 2 => "Hydrolysis: water splits a bond in it, each half of the water going to one of the pieces.",
        _ if ins.len() >= 2 && formula_out("H2O") && any_in(&organic) => "Condensation: two molecules join into one bigger one and give off water as they link.",
        _ if ins.len() >= 2
            && outs.iter().any(|s| s.state == MatterState::Solid)
            && ins.iter().all(|s| s.state == MatterState::Aqueous) =>
        {
            "Precipitation: two solutions swap partners and one new pairing can't stay dissolved, so it drops out as a solid."
        }
        _ if ins.len() == 2 && outs.len() == 2 && !any_in(&organic) && ins.iter().all(|s| !is_element(s)) => {
            "Double displacement: two compounds swap partners, each metal ending up with the other's partner."
        }
        _ if ins.len() >= 2 && outs.len() == 1 => "Combination: the reactants join into a single product, nothing left over.",
        _ if heat => "Heat gives the molecules enough energy to break their bonds and form new ones; some changes only happen hot.",
        _ if any_in(&organic) => "Organic synthesis: carbon compounds rebuilt one bond at a time, each reagent doing one job on the molecule.",
        _ => "Mixing lets the reactants meet: these react at room temperature as soon as they touch.",
    };
    text.to_string()
}

/// Why a vessel's contents don't react, where the chemistry or the recipes can tell.
pub fn why_not(db: &RecipeDatabase, vessel: &ProcessType, reactants: &[u32], subs: &Substances) -> Option<String> {
    let ins = lookup(subs, reactants);
    let set: BTreeSet<u32> = reactants.iter().copied().collect();
    // how near: a recipe this vessel (or a lower tier of it) knows, one ingredient away
    let tier = vessel.tier();
    let mine = |p: &ProcessType| p == vessel || (p.family() == vessel.family() && p.tier() <= tier);
    for r in db.authored.iter().filter(|r| mine(&r.process)) {
        let rs: BTreeSet<u32> = r.reactants.iter().map(|s| s.substance_id).collect();
        if rs.len() == set.len() + 1 && set.is_subset(&rs) {
            return Some("Close: one more ingredient and these would react here.".into());
        }
        if set.len() == rs.len() + 1 && rs.is_subset(&set) {
            return Some("Close: one of these isn't needed. Take the extra out and try again.".into());
        }
    }
    if let Some(n) = ins.iter().find(|s| NOBLE_GASES.contains(&s.formula.as_str())) {
        return Some(format!(
            "{} is a noble gas: its full shell of electrons leaves it almost nothing to react with.",
            n.name
        ));
    }
    if ins.len() == 1 && vessel.family() == "Mix" {
        return Some(format!(
            "Grinding {} on its own only makes it finer: it needs something to react with, or heat.",
            ins[0].name
        ));
    }
    if ins.len() >= 2 && ins.iter().all(|s| has(s, Property::IsAcid)) {
        return Some(
            "Two acids don't react with each other: an acid wants a base, a carbonate or a reactive metal.".into(),
        );
    }
    if ins.len() >= 2 && ins.iter().all(|s| has(s, Property::IsBase)) {
        return Some("Two bases don't react with each other: a base wants an acid.".into());
    }
    // a metal that can't push the metal of a compound out of it
    let metal = ins.iter().find(|s| is_element(s) && rank(&s.formula).is_some_and(|i| ACTIVITY[i] != "H"));
    if let (Some(m), 2) = (metal, ins.len()) {
        let other = ins.iter().find(|s| s.id != m.id)?;
        if let (Some(a), Some(b)) = (rank(&m.formula), metal_of(other).and_then(|x| rank(&x).map(|r| (r, x)))) {
            if a > b.0 && !is_element(other) {
                return Some(format!(
                    "{} is less reactive than {}: it can't push it out of {}. A metal only displaces one below it in the reactivity series.",
                    m.name, b.1, other.name
                ));
            }
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::symbols;

    #[test]
    fn symbols_read_formulas() {
        assert_eq!(symbols("CuSO4"), vec!["Cu", "S", "O"]);
        assert_eq!(symbols("Ca(OH)2"), vec!["Ca", "O", "H"]);
        assert_eq!(symbols("NaCl"), vec!["Na", "Cl"]);
    }
}
