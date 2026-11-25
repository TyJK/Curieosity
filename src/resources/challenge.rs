// src/resources/challenge.rs
//
// Challenges: targeted synthesis, scored. A challenge is one target to make by a route of
// two to four steps, from a kit of its own (the precursors and a few decoys) and only the
// vessels its route needs. The free lab is set aside while it is played and comes back as it
// was: a challenge's discoveries are its own (ui::challenges does the swapping).
//
// The rules, kept here so the content tests can run them over the whole game:
// - each step of the route is worth up to STEP_POINTS. While a step is the one being worked
//   on (the first not yet made), a reaction that doesn't go costs it FAIL_COST and a hint
//   HINT_COST (HINT_COST_AGAIN for every hint after the first on that step), never below
//   STEP_FLOOR: experimenting costs, but never more than a step's worth, and never below
//   zero. A step keeps its points once its product is made.
// - a run with no failed reactions and no hints earns CLEAN_BONUS on top.
// - stars: 3 at 90% of the most a challenge can score, 2 at 60%, 1 for finishing.
// - the best score, the stars and whether it was clean are kept per challenge
//   (challenges.ron, beside the save), and so is a daily challenge's streak.
//
// The challenges come from the game's own content: for each era, up to PER_ERA of its
// reactions whose product takes a route of several steps, spread through the era.
use std::collections::{HashMap, HashSet, VecDeque};

use bevy::prelude::*;
use serde::{Deserialize, Serialize};

use crate::data::common::ProcessType;
use crate::resources::recipe_database::RecipeDatabase;

pub const STEP_POINTS: u32 = 100;
pub const FAIL_COST: u32 = 10;
pub const HINT_COST: u32 = 20;
pub const HINT_COST_AGAIN: u32 = 40;
pub const STEP_FLOOR: u32 = 25;
pub const CLEAN_BONUS: u32 = 50;
/// Challenges in each era, at most.
pub const PER_ERA: usize = 10;
/// Stars earned in an era that open the next one (an era the lab has reached is open anyway).
pub const STARS_TO_OPEN: u32 = 3;

/// One challenge: make `target` by `steps`, from `kit`, in `vessels`.
#[derive(Clone, Debug, PartialEq)]
pub struct Challenge {
    /// its key: the id of the target's own (last) step
    pub id: u32,
    pub era: u8,
    pub target: u32,
    /// the reactions of the route, in an order that works, the target's own step last
    pub steps: Vec<u32>,
    /// what each step makes for the route (the target, for the last)
    pub step_products: Vec<u32>,
    /// what the shelf holds: the precursors and catalysts, and a few decoys
    pub kit: Vec<u32>,
    pub decoys: Vec<u32>,
    /// the vessels the route needs
    pub vessels: Vec<ProcessType>,
}

impl Challenge {
    /// The most it can score.
    pub fn max_score(&self) -> u32 {
        STEP_POINTS * self.steps.len() as u32 + CLEAN_BONUS
    }
}

/// Plan the route to `target` by reaction `final_id` with everything known and every vessel
/// open: work back through the reactions that make each precursor (the first the game
/// introduces), never past the base materials, up to four steps. None when the route is a
/// single step, or doesn't work.
/// `pool` is where the decoys come from: the raw materials of the challenge's era and before.
pub fn plan(
    db: &RecipeDatabase,
    makers: &HashMap<u32, Vec<usize>>,
    base: &HashSet<u32>,
    pool: &[u32],
    final_id: u32,
    target: u32,
) -> Option<Challenge> {
    const MAX_STEPS: usize = 4;
    let fin = db.authored.iter().find(|r| r.id == final_id)?;
    let mut steps = vec![fin.id];
    let mut makes = vec![target];
    let mut expanded: HashSet<u32> = HashSet::from([target]);
    let mut items: Vec<u32> = Vec::new();
    let add = |items: &mut Vec<u32>, id: u32| {
        if !items.contains(&id) {
            items.push(id);
        }
    };
    items.extend(fin.required_catalyst());
    let mut queue: VecDeque<(u32, usize)> = fin.reactants.iter().map(|s| (s.substance_id, 1)).collect();
    while let Some((s, depth)) = queue.pop_front() {
        if expanded.contains(&s) || items.contains(&s) {
            continue;
        }
        let must = db.transient.contains(&s);
        let maker = if must || (depth <= 3 && steps.len() < MAX_STEPS && !base.contains(&s)) {
            makers.get(&s).into_iter().flatten().map(|&i| &db.authored[i]).find(|r| {
                !steps.contains(&r.id)
                    && r.reactants.iter().all(|x| !expanded.contains(&x.substance_id) && x.substance_id != s)
                    && (must || steps.len() < MAX_STEPS)
            })
        } else {
            None
        };
        match maker {
            Some(r) => {
                steps.push(r.id);
                makes.push(s);
                expanded.insert(s);
                if let Some(c) = r.required_catalyst() {
                    add(&mut items, c);
                }
                for x in &r.reactants {
                    queue.push_back((x.substance_id, depth + 1));
                }
            }
            None => add(&mut items, s),
        }
    }
    if steps.len() < 2 || steps.len() > MAX_STEPS {
        return None;
    }
    steps.reverse();
    makes.reverse();
    // it must work from the kit alone, in this order
    let mut have: HashSet<u32> = items.iter().copied().collect();
    for id in &steps {
        let r = db.authored.iter().find(|r| r.id == *id)?;
        if !r.reactants.iter().all(|s| have.contains(&s.substance_id))
            || r.required_catalyst().is_some_and(|c| !have.contains(&c))
        {
            return None;
        }
        have.extend(r.products.iter().map(|p| p.substance_id));
    }
    if !have.contains(&target) || items.contains(&target) {
        return None;
    }
    let mut vessels: Vec<ProcessType> = Vec::new();
    for id in &steps {
        if let Some(r) = db.authored.iter().find(|r| r.id == *id) {
            if !vessels.contains(&r.process) {
                vessels.push(r.process.clone());
            }
        }
    }
    // decoys: raw materials of the era the route doesn't touch, the same ones every time
    let used: HashSet<u32> = items.iter().chain(makes.iter()).copied().collect();
    let mut spare: Vec<u32> = pool.iter().copied().filter(|id| !used.contains(id)).collect();
    spare.sort_by_key(|id| (id.wrapping_mul(2_654_435_761) ^ target.wrapping_mul(40_503)).rotate_left(7));
    let decoys: Vec<u32> = spare.into_iter().take(if items.len() <= 2 { 4 } else { 3 }).collect();
    Some(Challenge { id: final_id, era: fin.epoch, target, steps, step_products: makes, kit: items, decoys, vessels })
}

/// Every challenge, era by era: up to PER_ERA in each, spread through the era's reactions.
pub fn all_challenges(db: &RecipeDatabase) -> Vec<Challenge> {
    let mut makers: HashMap<u32, Vec<usize>> = HashMap::new();
    for (i, r) in db.authored.iter().enumerate() {
        for p in &r.products {
            makers.entry(p.substance_id).or_default().push(i);
        }
    }
    let base: HashSet<u32> = crate::ui::hint::base_materials(db);
    // the era each raw material arrives in: the start kit at the first, a milestone's grant
    // in the era of the first step that makes the milestone's substance
    let first_made: HashMap<u32, u8> =
        db.authored.iter().rev().flat_map(|r| r.products.iter().map(move |p| (p.substance_id, r.epoch))).collect();
    let mut arrives: HashMap<u32, u8> = db.start.iter().map(|id| (*id, 0)).collect();
    for m in &db.milestones {
        let e = first_made.get(&m.on).copied().unwrap_or(0);
        for g in &m.grant {
            let a = arrives.entry(*g).or_insert(e);
            *a = (*a).min(e);
        }
    }
    let side = db.side_epoch();
    let mut out = Vec::new();
    let mut used_targets: HashSet<u32> = HashSet::new();
    for era in 0..db.epochs.len() as u8 {
        if Some(era) == side {
            continue;
        }
        let mut pool: Vec<u32> = arrives.iter().filter(|(_, e)| **e <= era).map(|(id, _)| *id).collect();
        pool.sort_unstable();
        let mut found: Vec<Challenge> = Vec::new();
        for r in db.authored.iter().filter(|r| r.epoch == era) {
            // the step's first product that is something to make (not handed out, not used at once)
            let Some(t) = r
                .products
                .iter()
                .map(|p| p.substance_id)
                .find(|id| !base.contains(id) && !db.transient.contains(id) && !used_targets.contains(id))
            else {
                continue;
            };
            if let Some(c) = plan(db, &makers, &base, &pool, r.id, t) {
                if !found.iter().any(|f| f.target == c.target) {
                    found.push(c);
                }
            }
        }
        // spread through the era, the longest routes favoured where there is a choice
        let n = found.len();
        let pick: Vec<usize> =
            if n <= PER_ERA { (0..n).collect() } else { (0..PER_ERA).map(|k| k * n / PER_ERA).collect() };
        for i in pick {
            used_targets.insert(found[i].target);
            out.push(found[i].clone());
        }
    }
    out
}

// ---------------------------------------------------------------------------------------
// A run
// ---------------------------------------------------------------------------------------
/// A challenge being played: each step's points so far, and what has cost them.
#[derive(Clone, Debug, PartialEq)]
pub struct Run {
    pub challenge: Challenge,
    /// each step's points (falling with failures and hints until it is made)
    pub points: Vec<u32>,
    pub done: Vec<bool>,
    /// hints taken on each step
    pub hints: Vec<u32>,
    pub fails: u32,
    pub hints_taken: u32,
    pub finished: bool,
    /// played as the day's challenge
    pub daily: bool,
}

impl Run {
    pub fn new(challenge: Challenge, daily: bool) -> Self {
        let n = challenge.steps.len();
        Run {
            challenge,
            points: vec![STEP_POINTS; n],
            done: vec![false; n],
            hints: vec![0; n],
            fails: 0,
            hints_taken: 0,
            finished: false,
            daily,
        }
    }

    /// The step being worked on: the first not yet made.
    pub fn current(&self) -> Option<usize> {
        self.done.iter().position(|d| !d)
    }

    /// A reaction that didn't go.
    pub fn fail(&mut self) {
        if self.finished {
            return;
        }
        self.fails += 1;
        if let Some(i) = self.current() {
            self.points[i] = self.points[i].saturating_sub(FAIL_COST).max(STEP_FLOOR);
        }
    }

    /// What the next hint costs.
    pub fn hint_cost(&self) -> u32 {
        match self.current() {
            Some(i) if self.hints[i] > 0 => HINT_COST_AGAIN,
            _ => HINT_COST,
        }
    }

    /// A hint taken.
    pub fn hint(&mut self) {
        if self.finished {
            return;
        }
        self.hints_taken += 1;
        if let Some(i) = self.current() {
            let cost = self.hint_cost();
            self.hints[i] += 1;
            self.points[i] = self.points[i].saturating_sub(cost).max(STEP_FLOOR);
        }
    }

    /// Something was discovered: any step it is the product of is done (and keeps its
    /// points). True if that finished the challenge.
    pub fn found(&mut self, id: u32) -> bool {
        if self.finished {
            return false;
        }
        for (i, p) in self.challenge.step_products.iter().enumerate() {
            if *p == id {
                self.done[i] = true;
            }
        }
        if id == self.challenge.target {
            // the target made by any route finishes it; steps skipped keep their points
            for d in &mut self.done {
                *d = true;
            }
        }
        self.finished = self.done.iter().all(|d| *d);
        self.finished
    }

    pub fn clean(&self) -> bool {
        self.fails == 0 && self.hints_taken == 0
    }

    pub fn score(&self) -> u32 {
        self.points.iter().sum::<u32>() + if self.finished && self.clean() { CLEAN_BONUS } else { 0 }
    }

    pub fn stars(&self) -> u8 {
        if !self.finished {
            return 0;
        }
        let max = self.challenge.max_score().max(1);
        let s = self.score();
        if s * 10 >= max * 9 {
            3
        } else if s * 10 >= max * 6 {
            2
        } else {
            1
        }
    }
}

// ---------------------------------------------------------------------------------------
// What is kept
// ---------------------------------------------------------------------------------------
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(default)]
pub struct Record {
    pub best: u32,
    pub stars: u8,
    pub clean: bool,
}

/// Every challenge's best, and the daily streak.
#[derive(Resource, Clone, Debug, Default, PartialEq, Serialize, Deserialize)]
#[serde(default)]
pub struct ChallengeRecords {
    pub records: HashMap<u32, Record>,
    /// the last day (days since 1970, UTC) a daily challenge was finished
    pub daily_day: i64,
    pub streak: u32,
    pub best_streak: u32,
}

impl ChallengeRecords {
    /// Keep a finished run's result; true if it beat the best.
    pub fn finish(&mut self, run: &Run, today: i64) -> bool {
        let r = self.records.entry(run.challenge.id).or_default();
        let better = run.score() > r.best;
        r.best = r.best.max(run.score());
        r.stars = r.stars.max(run.stars());
        r.clean |= run.clean();
        if run.daily && self.daily_day != today {
            self.streak = if self.daily_day == today - 1 { self.streak + 1 } else { 1 };
            self.daily_day = today;
            self.best_streak = self.best_streak.max(self.streak);
        }
        better
    }

    pub fn stars(&self, id: u32) -> u8 {
        self.records.get(&id).map_or(0, |r| r.stars)
    }

    /// The streak as it stands today: gone if yesterday's daily was missed.
    pub fn streak_now(&self, today: i64) -> u32 {
        if self.daily_day >= today - 1 {
            self.streak
        } else {
            0
        }
    }

    pub fn daily_done(&self, today: i64) -> bool {
        self.daily_day == today
    }
}

/// A hint was taken: a target chosen from the Hint button's list, or one more clue shown
/// (a challenge's hints cost its points).
#[derive(Message, Clone, Copy, Debug)]
pub struct HintTaken;

/// Today, as days since 1970 (UTC).
pub fn today() -> i64 {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| (d.as_secs() / 86_400) as i64)
        .unwrap_or(0)
}

/// Which era's challenges are open: the first always; another once the lab has reached it
/// or STARS_TO_OPEN stars are earned in the era before.
pub fn era_open(era: u8, challenges: &[Challenge], records: &ChallengeRecords, lab_era: u8, first: u8) -> bool {
    if era <= first || era <= lab_era {
        return true;
    }
    let before = challenges.iter().filter(|c| c.era < era).map(|c| c.era).max();
    match before {
        Some(b) => {
            let stars: u32 = challenges.iter().filter(|c| c.era == b).map(|c| records.stars(c.id) as u32).sum();
            stars >= STARS_TO_OPEN && era_open(b, challenges, records, lab_era, first)
        }
        None => true,
    }
}

/// The day's challenge: one of the open ones, the same for everyone on a given day.
pub fn daily<'a>(open: &[&'a Challenge], day: i64) -> Option<&'a Challenge> {
    if open.is_empty() {
        return None;
    }
    let h = (day as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15).rotate_left(17);
    open.get((h % open.len() as u64) as usize).copied()
}

pub fn records_path() -> std::path::PathBuf {
    crate::resources::player_progress::save_path().with_file_name("challenges.ron")
}

pub fn load_records() -> ChallengeRecords {
    std::fs::read_to_string(records_path()).ok().and_then(|t| ron::from_str(&t).ok()).unwrap_or_default()
}

pub fn save_records(r: &ChallengeRecords) {
    let path = records_path();
    match ron::ser::to_string_pretty(r, ron::ser::PrettyConfig::default()) {
        Ok(text) => {
            if let Err(e) = crate::resources::player_progress::write_atomic(&path, &text) {
                warn!("Could not write {}: {}", path.display(), e);
            }
        }
        Err(e) => warn!("Could not serialise the challenge records: {e}"),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn challenge(steps: usize) -> Challenge {
        Challenge {
            id: 9,
            era: 0,
            target: 100 + steps as u32,
            steps: (1..=steps as u32).collect(),
            step_products: (101..=100 + steps as u32).collect(),
            kit: vec![1, 2],
            decoys: vec![3],
            vessels: vec![ProcessType::Mix],
        }
    }

    #[test]
    fn a_clean_run_scores_everything_and_three_stars() {
        let mut r = Run::new(challenge(3), false);
        assert!(!r.found(101));
        assert!(!r.found(102));
        assert!(r.found(103));
        assert_eq!(r.score(), 350);
        assert_eq!(r.stars(), 3);
    }

    #[test]
    fn failures_and_hints_cost_the_step_in_hand_never_below_its_floor() {
        let mut r = Run::new(challenge(2), false);
        r.fail();
        assert_eq!(r.points, vec![90, 100], "the first step pays for it");
        r.hint();
        assert_eq!(r.points[0], 70);
        assert_eq!(r.hint_cost(), HINT_COST_AGAIN, "a second hint on a step costs more");
        for _ in 0..20 {
            r.fail();
        }
        assert_eq!(r.points[0], STEP_FLOOR, "experimenting never costs more than the step");
        r.found(101);
        r.fail();
        assert_eq!(r.points, vec![STEP_FLOOR, 90], "a made step keeps its points");
        r.found(102);
        assert!(r.finished);
        assert_eq!(r.score(), STEP_FLOOR + 90, "no clean bonus");
        assert_eq!(r.stars(), 1);
    }

    #[test]
    fn making_the_target_any_way_finishes() {
        let mut r = Run::new(challenge(3), false);
        assert!(r.found(103));
        assert_eq!(r.done, vec![true, true, true]);
    }

    #[test]
    fn the_daily_streak_counts_days_in_a_row() {
        let mut rec = ChallengeRecords::default();
        let mut run = Run::new(challenge(2), true);
        run.found(102);
        rec.finish(&run, 100);
        rec.finish(&run, 101);
        assert_eq!(rec.streak, 2);
        rec.finish(&run, 101);
        assert_eq!(rec.streak, 2, "twice in a day counts once");
        assert_eq!(rec.streak_now(103), 0, "a missed day ends it");
        rec.finish(&run, 104);
        assert_eq!((rec.streak, rec.best_streak), (1, 2));
        assert_eq!(rec.records[&9].stars, 3);
    }
}
