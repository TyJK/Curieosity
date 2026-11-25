// src/resources/recipe_database.rs

use crate::data::common::ProcessType;
use crate::data::{
    reactions::{EpochDef, Milestone, Reaction, Reactions},
    substances::{SubstancePatches, Substances},
};
use crate::GameData;
use bevy::prelude::*;
use std::collections::{BTreeSet, HashMap, HashSet};

/// A key for our reaction HashMap.
/// It consists of the process used and a sorted list of
/// reactant IDs. This ensures (Water + Salt) and (Salt + Water)
/// produce the same key.
#[derive(PartialEq, Eq, Hash, Clone, Debug)]
pub struct RecipeKey {
    /// The process applied (e.g., Heat, Mix).
    pub process: ProcessType,
    /// A sorted, unique set of reactant substance IDs.
    /// We use a BTreeSet to guarantee the order is always
    /// the same, regardless of how the user added them.
    pub reactants: BTreeSet<u32>,
}

impl RecipeKey {
    /// A helper function to create a new RecipeKey from a
    /// list of reactant substance IDs and a process.
    pub fn new(process: ProcessType, reactant_ids: Vec<u32>) -> Self {
        Self { process, reactants: reactant_ids.into_iter().collect() }
    }
}

/// What a vessel would do with what is in it.
#[derive(Debug)]
pub enum Lookup<'a> {
    /// it reacts: the vessel or a lower tier of its family knows this recipe
    Runs(&'a Reaction),
    /// a higher tier of the same family could (this vessel is not enough)
    NeedsTier(ProcessType),
    /// a vessel of another family could
    OtherVessel(ProcessType),
    Nothing,
}

/// The main "Recipe Book" resource, plus the progression that ships with the authored
/// reactions. Its existence means all game content is loaded and the authored substance
/// layer has been applied, so UI systems can gate on `Option<Res<RecipeDatabase>>`.
#[derive(Resource, Debug, Default)]
pub struct RecipeDatabase {
    /// The HashMap mapping the player's input (RecipeKey)
    /// to a specific Reaction.
    pub map: HashMap<RecipeKey, Reaction>,
    /// Reactant set -> every process that reacts it. Used to hint "right ingredients,
    /// wrong vessel" when a combination fizzles.
    pub by_reactants: HashMap<BTreeSet<u32>, Vec<ProcessType>>,
    /// Authored reactions in (epoch, id) order: the tech tree's nodes.
    pub authored: Vec<Reaction>,
    pub epochs: Vec<EpochDef>,
    pub start: Vec<u32>,
    pub milestones: Vec<Milestone>,
    /// Every substance the authored game can reach: the start kit, the milestone grants,
    /// and everything the authored reactions use or make (catalysts included).
    pub canon: HashSet<u32>,
    /// The substances in play that are made and used at once, never kept (note_transients).
    pub transient: HashSet<u32>,
}

impl RecipeDatabase {
    /// What `vessel` makes of `reactants`. A vessel runs its own recipes and every recipe of
    /// its family at a lower tier; where two tiers know the same mix, the highest tier the
    /// vessel reaches wins ("a hotter furnace makes the better product").
    pub fn lookup(&self, vessel: &ProcessType, reactants: Vec<u32>) -> Lookup<'_> {
        let key = RecipeKey::new(vessel.clone(), reactants);
        let tier = vessel.tier();
        let members = vessel.family_members();
        if members.is_empty() {
            return match self.map.get(&key) {
                Some(r) => Lookup::Runs(r),
                None => self.elsewhere(vessel, &key),
            };
        }
        for m in members.iter().filter(|m| m.tier <= tier) {
            let k = RecipeKey { process: m.process.clone(), reactants: key.reactants.clone() };
            if let Some(r) = self.map.get(&k) {
                return Lookup::Runs(r);
            }
        }
        for m in members.iter().rev().filter(|m| m.tier > tier) {
            let k = RecipeKey { process: m.process.clone(), reactants: key.reactants.clone() };
            if self.map.contains_key(&k) {
                return Lookup::NeedsTier(m.process.clone());
            }
        }
        self.elsewhere(vessel, &key)
    }

    fn elsewhere(&self, vessel: &ProcessType, key: &RecipeKey) -> Lookup<'_> {
        let fam = vessel.family();
        match self
            .by_reactants
            .get(&key.reactants)
            .and_then(|ps| ps.iter().find(|p| p.family() != fam || fam == "Other"))
        {
            Some(p) => Lookup::OtherVessel(p.clone()),
            None => Lookup::Nothing,
        }
    }

    pub fn epoch_name(&self, epoch: u8) -> &str {
        self.epochs.get(epoch as usize).map(|e| e.name.as_str()).unwrap_or("Unsorted")
    }

    /// Build the database from the authored reactions and their progression.
    /// gen_authored.py guarantees no two reactions share a (process, reactant set).
    pub fn from_authored(authored: &Reactions) -> Self {
        let mut map = HashMap::new();
        for reaction in &authored.reactions {
            let reactant_ids: Vec<u32> = reaction.reactants.iter().map(|sp| sp.substance_id).collect();
            map.insert(RecipeKey::new(reaction.process.clone(), reactant_ids), reaction.clone());
        }

        let mut by_reactants: HashMap<BTreeSet<u32>, Vec<ProcessType>> = HashMap::new();
        for key in map.keys() {
            by_reactants.entry(key.reactants.clone()).or_default().push(key.process.clone());
        }

        let mut authored_list: Vec<Reaction> = authored.reactions.clone();
        authored_list.sort_by_key(|r| (r.epoch, r.id));

        let mut canon: HashSet<u32> = authored.start.iter().copied().collect();
        for m in &authored.milestones {
            canon.insert(m.on);
            canon.extend(m.grant.iter().copied());
        }
        for r in &authored_list {
            canon.extend(r.reactants.iter().map(|s| s.substance_id));
            canon.extend(r.products.iter().map(|s| s.substance_id));
            if let Some(c) = r.required_catalyst() {
                canon.insert(c);
            }
        }

        Self {
            map,
            by_reactants,
            authored: authored_list,
            epochs: authored.epochs.clone(),
            start: authored.start.clone(),
            milestones: authored.milestones.clone(),
            canon,
            transient: HashSet::new(),
        }
    }

    /// Records which substances in play are transients (Property::IsTransient).
    pub fn note_transients(&mut self, substances: &Substances) {
        self.transient =
            self.canon.iter().copied().filter(|id| substances.0.get(id).is_some_and(|s| s.is_transient())).collect();
    }

    /// The step that makes a substance (the first in tech-tree order).
    pub fn maker_of(&self, id: u32) -> Option<&Reaction> {
        self.authored.iter().find(|r| r.products.iter().any(|p| p.substance_id == id))
    }

    /// One order in which a player could perform every authored reaction, following the
    /// real rules: start with the starting kit and the Mortar and Fire; a reaction can run
    /// once its vessel is unlocked and its reactants (and catalyst) are known; milestones
    /// unlock vessels and grant materials. Reactions are taken in tech-tree order whenever
    /// several are possible. Also returns any reactions that can never be performed.
    pub fn playthrough(&self) -> Playthrough {
        let mut known: HashSet<u32> = self.start.iter().copied().collect();
        let mut vessels: HashSet<ProcessType> = [ProcessType::Mix, ProcessType::Heat].into_iter().collect();
        let mut fired = vec![false; self.milestones.len()];
        let mut done = vec![false; self.authored.len()];
        let mut steps = Vec::new();
        let side = self.side_epoch();
        let mut era_steps = 0usize;
        let mut milestone_steps = Vec::new();
        let mut unlocked_at: HashMap<ProcessType, usize> = vessels.iter().map(|p| (p.clone(), 0)).collect();
        loop {
            // milestones first, so grants are in hand before the next reaction
            let mut changed = true;
            while changed {
                changed = false;
                for (i, m) in self.milestones.iter().enumerate() {
                    if !fired[i] && known.contains(&m.on) {
                        fired[i] = true;
                        for p in &m.unlock {
                            if vessels.insert(p.clone()) {
                                unlocked_at.insert(p.clone(), steps.len());
                            }
                        }
                        known.extend(m.grant.iter().copied());
                        milestone_steps.push((i, steps.len(), era_steps));
                        changed = true;
                    }
                }
            }
            let next = self.authored.iter().enumerate().find(|(i, r)| {
                !done[*i]
                    && vessels.contains(&r.process)
                    && r.reactants.iter().all(|s| known.contains(&s.substance_id))
                    && r.required_catalyst().is_none_or(|c| known.contains(&c))
            });
            let Some((i, r)) = next else { break };
            done[i] = true;
            known.extend(r.products.iter().map(|s| s.substance_id));
            steps.push(r.id);
            if Some(r.epoch) != side {
                era_steps += 1;
            }
        }
        let unreachable = self.authored.iter().zip(done.iter()).filter(|(_, d)| !**d).map(|(r, _)| r.id).collect();
        Playthrough { steps, unreachable, known, milestone_steps, era_steps, unlocked_at }
    }

    /// The era of side content that belongs to every age ("The Laboratory"), if any: its
    /// recipes don't count toward pacing, and the header never names it as the current era.
    pub fn side_epoch(&self) -> Option<u8> {
        self.epochs.iter().position(|e| e.era == "every age").map(|i| i as u8)
    }

    /// Era-step gaps between consecutive milestones (and from the last one to the end), as
    /// (from, to, gap): the pacing the review report and the content tests look at.
    pub fn milestone_gaps(&self, pt: &Playthrough) -> Vec<(String, String, usize)> {
        let mut out = Vec::new();
        let (mut prev, mut at) = ("start".to_string(), 0usize);
        for (i, _, era) in &pt.milestone_steps {
            let on = format!("#{}", self.milestones[*i].on);
            out.push((prev, on.clone(), era - at));
            prev = on;
            at = *era;
        }
        out.push((prev, "end".to_string(), pt.era_steps - at));
        out
    }
}

/// The result of `RecipeDatabase::playthrough`.
#[derive(Debug, Default)]
pub struct Playthrough {
    /// authored reaction ids, in a performable order
    pub steps: Vec<u32>,
    /// authored reaction ids that can never be performed
    pub unreachable: Vec<u32>,
    /// every substance known by the end
    pub known: HashSet<u32>,
    /// (milestone index, step, era step) in the order the milestones fire
    pub milestone_steps: Vec<(usize, usize, usize)>,
    /// steps outside the side era ("The Laboratory")
    pub era_steps: usize,
    /// the step each vessel becomes available at (0 for the starting pair)
    pub unlocked_at: HashMap<ProcessType, usize>,
}

/// Pacing limits, shared by the content tests, the review report and gen_authored.py.
pub const MAX_GRANT: usize = 12;
pub const MAX_MILESTONE_GAP: usize = 90;

/// A one-time system that runs when assets are loaded.
/// It applies the authored substance layer onto the substance library, then builds the
/// fast-lookup RecipeDatabase from the authored reactions.
pub fn build_recipe_database(
    mut commands: Commands,
    game_data: Option<Res<GameData>>,
    reactions_assets: Res<Assets<Reactions>>,
    mut substances_assets: ResMut<Assets<Substances>>,
    patches_assets: Res<Assets<SubstancePatches>>,
    pages_assets: Res<Assets<crate::data::pages::Pages>>,
    recipe_db: Option<Res<RecipeDatabase>>,
) {
    // If the database is already built, or if the game_data resource
    // isn't available yet, do nothing.
    if recipe_db.is_some() {
        return;
    }
    let Some(game_data) = game_data else { return };

    // Wait until every content asset is loaded.
    let (Some(authored), Some(patches), Some(pages)) = (
        reactions_assets.get(&game_data.authored_reactions),
        patches_assets.get(&game_data.authored_substances),
        pages_assets.get(&game_data.pages),
    ) else {
        return;
    };
    let Some(mut substances) = substances_assets.get_mut(&game_data.substances) else {
        return;
    };

    let (patched, created) = patches.apply_to(&mut substances);
    info!("Authored substance layer applied: {} entries ({} new).", patched, created);
    let checked = pages.apply_values(&mut substances);
    info!(
        "Checked values applied to {} substances; {} pages, {} curriculum topics.",
        checked,
        pages.substances.len(),
        pages.topics.len()
    );

    let mut db = RecipeDatabase::from_authored(authored);
    db.note_transients(&substances);
    info!(
        "Recipe database built: {} entries ({} authored, {} milestones, {} epochs, {} substances in play).",
        db.map.len(),
        db.authored.len(),
        db.milestones.len(),
        db.epochs.len(),
        db.canon.len()
    );
    commands.insert_resource(db);
}
