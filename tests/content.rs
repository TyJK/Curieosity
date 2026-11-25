// tests/content.rs
//
// Content checks: the authored game is loaded exactly as the game loads it (substance
// library + authored substance layer, authored reactions) and checked for the
// things that would break a playthrough or a library page. The scripted in-game
// playthrough (`cargo run --release -- --autoplay`) covers what these can't: the real UI.
//
// Run with `cargo test --release` (the packed substance library is several MB of RON,
// slow to parse in a debug build).
use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use chem_alchemy::data::common::{un_class_name, Grade, ProcessType, Property};
use chem_alchemy::data::pages::Pages;
use chem_alchemy::data::reactions::Reactions;
use chem_alchemy::data::substances::{SubstancePatches, Substances};
use chem_alchemy::resources::player_progress::{SaveData, SAVE_VERSION};
use chem_alchemy::resources::recipe_database::{RecipeDatabase, RecipeKey, MAX_GRANT, MAX_MILESTONE_GAP};
use chem_alchemy::systems::achievements::{achievement_list, achievements_csv};
use chem_alchemy::ui::credits::{text_credit, GIVING, HOW_MADE, MADE_BY, PRIVACY, SECTIONS, TEXT_SOURCES};
use chem_alchemy::ui::hint::{base_materials, decoy_count, makes_target, plan_kit, targets, MAX_STEPS};
use chem_alchemy::ui::process_toolbar::{vessel_art_path, VESSELS};
use chem_alchemy::ui::settings::Settings;
use chem_alchemy::ui::tech_tree::plan_links;

struct Content {
    subs: Substances,
    authored: Reactions,
    db: RecipeDatabase,
    pages: Pages,
}

fn root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

fn load<T: serde::de::DeserializeOwned>(rel: &str) -> T {
    let path = root().join("assets/data").join(rel);
    let bytes = std::fs::read(&path).unwrap_or_else(|e| panic!("reading {}: {e}", path.display()));
    ron::de::from_bytes(&bytes).unwrap_or_else(|e| panic!("parsing {}: {e}", path.display()))
}

fn content() -> &'static Content {
    static C: OnceLock<Content> = OnceLock::new();
    C.get_or_init(|| {
        let mut subs: Substances = load("substances.ron");
        let patches: SubstancePatches = load("authored_substances.ron");
        patches.apply_to(&mut subs);
        let pages: Pages = load("pages.ron");
        pages.apply_values(&mut subs);
        let authored: Reactions = load("authored_reactions.ron");
        let mut db = RecipeDatabase::from_authored(&authored);
        db.note_transients(&subs);
        Content { subs, authored, db, pages }
    })
}

fn name(c: &Content, id: u32) -> String {
    c.subs.0.get(&id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"))
}

#[test]
fn every_referenced_substance_exists() {
    let c = content();
    let mut missing = BTreeSet::new();
    let mut need = |id: u32, why: String| {
        if !c.subs.0.contains_key(&id) {
            missing.insert(format!("{id} ({why})"));
        }
    };
    for &id in &c.authored.start {
        need(id, "start kit".into());
    }
    for m in &c.authored.milestones {
        need(m.on, "milestone trigger".into());
        for &g in &m.grant {
            need(g, "milestone grant".into());
        }
    }
    for r in &c.authored.reactions {
        for sp in r.reactants.iter().chain(r.products.iter()) {
            need(sp.substance_id, format!("reaction {} {}", r.id, r.name));
        }
        if let Some(cat) = r.required_catalyst() {
            need(cat, format!("catalyst of {}", r.id));
        }
    }
    assert!(missing.is_empty(), "substances referenced but not defined: {missing:?}");
}

#[test]
fn every_substance_in_play_has_a_page() {
    let c = content();
    let mut bad = Vec::new();
    for &id in &c.db.canon {
        let Some(s) = c.subs.0.get(&id) else { continue };
        // compounds carry a description; elements carry their overview in element_info
        let desc = s
            .description
            .as_deref()
            .or_else(|| s.element_info.as_ref().and_then(|e| e.overview.as_deref()))
            .map(str::trim)
            .unwrap_or("");
        if desc.is_empty() {
            bad.push(format!("{} ({}): no description", s.name, id));
        }
        if s.primary_reference().is_none() {
            bad.push(format!("{} ({}): no reference", s.name, id));
        }
        if s.name.trim().is_empty() || s.formula.trim().is_empty() {
            bad.push(format!("{id}: missing name or formula"));
        }
    }
    assert!(bad.is_empty(), "{} library pages incomplete:\n{}", bad.len(), bad.join("\n"));
    assert!(c.db.canon.len() >= 1200, "only {} substances in play", c.db.canon.len());
}

#[test]
fn every_authored_reaction_is_written_up() {
    let c = content();
    let bad: Vec<String> =
        c.db.authored
            .iter()
            .filter(|r| r.description.as_deref().is_none_or(|d| d.trim().is_empty()) || r.references.is_empty())
            .map(|r| format!("{} {}", r.id, r.name))
            .collect();
    assert!(bad.is_empty(), "{} authored reactions lack a description or reference: {bad:?}", bad.len());
}

#[test]
fn the_whole_tree_can_be_played_through() {
    let c = content();
    let pt = c.db.playthrough();
    let stuck: Vec<String> = pt
        .unreachable
        .iter()
        .map(|id| {
            let r = c.db.authored.iter().find(|r| r.id == *id).unwrap();
            let missing: Vec<String> = r
                .reactants
                .iter()
                .filter(|s| !pt.known.contains(&s.substance_id))
                .map(|s| name(c, s.substance_id))
                .collect();
            format!("{} {} (never have: {})", r.id, r.name, missing.join(", "))
        })
        .collect();
    assert!(stuck.is_empty(), "{} reactions can never be performed:\n{}", stuck.len(), stuck.join("\n"));
    assert_eq!(pt.steps.len(), c.db.authored.len());
    let canon_unknown: Vec<u32> = c.db.canon.iter().filter(|id| !pt.known.contains(id)).copied().collect();
    assert!(canon_unknown.is_empty(), "substances in play that can never be found: {canon_unknown:?}");
}

/// The tech tree expresses every prerequisite: each ingredient or catalyst a step needs
/// beyond the starting shelf is listed among its needs, comes from a step (and is linked
/// from it) or from a milestone, and is either drawn in the overview or counted on the
/// step's badge.
#[test]
fn every_prerequisite_shows_in_the_tech_tree() {
    let c = content();
    let plan = plan_links(&c.db);
    let links: HashSet<(u32, u32)> = plan.links().into_iter().collect();
    let overview: HashSet<(u32, u32)> = plan.overview.iter().copied().collect();
    let start: HashSet<u32> = c.db.start.iter().copied().collect();
    let mut bad = Vec::new();
    for r in &c.db.authored {
        let needs = plan.needs.get(&r.id).cloned().unwrap_or_default();
        for s in r.reactants.iter().map(|s| s.substance_id).chain(r.required_catalyst()) {
            if start.contains(&s) {
                continue;
            }
            let Some(n) = needs.iter().find(|n| n.substance == s) else {
                bad.push(format!("{}: {} is not among its needs", r.name, name(c, s)));
                continue;
            };
            match n.from {
                Some(p) if !links.contains(&(p, r.id)) => {
                    bad.push(format!("{}: no link from the step that makes {}", r.name, name(c, s)))
                }
                Some(p) if n.drawn && !overview.contains(&(p, r.id)) => {
                    bad.push(format!("{}: {} counts as drawn but has no overview line", r.name, name(c, s)))
                }
                None if !n.granted => bad.push(format!("{}: nothing makes or grants {}", r.name, name(c, s))),
                _ => {}
            }
        }
        let undrawn = needs.iter().filter(|n| !n.drawn).count();
        if plan.undrawn(r.id) != undrawn {
            bad.push(format!("{}: badge {} for {undrawn} needs without a line", r.name, plan.undrawn(r.id)));
        }
    }
    assert!(bad.is_empty(), "{} prerequisites the tech tree doesn't show:\n{}", bad.len(), bad.join("\n"));
}

#[test]
fn authored_recipes_are_unique_and_win_collisions() {
    let c = content();
    let mut seen: HashMap<RecipeKey, u32> = HashMap::new();
    let mut dupes = Vec::new();
    for r in &c.db.authored {
        let key = RecipeKey::new(r.process.clone(), r.reactants.iter().map(|s| s.substance_id).collect());
        if let Some(other) = seen.insert(key.clone(), r.id) {
            dupes.push(format!("{} and {} share {:?}", other, r.id, key));
        }
        let got = c.db.map.get(&key).map(|x| x.id);
        assert_eq!(got, Some(r.id), "the recipe book runs {:?} for {} {}", got, r.id, r.name);
    }
    assert!(dupes.is_empty(), "{dupes:?}");
}

#[test]
fn reaction_ids_are_sequential_and_in_range() {
    let c = content();
    let mut ids: Vec<u32> = c.db.authored.iter().map(|r| r.id).collect();
    ids.sort_unstable();
    let unique: HashSet<u32> = ids.iter().copied().collect();
    assert_eq!(unique.len(), ids.len(), "duplicate authored reaction ids");
    // authored ids start at a million (tools/data/gen_authored.py AUTHORED_REACTION_BASE)
    const BASE: u32 = 1_000_000;
    assert_eq!(ids.first(), Some(&BASE));
    assert_eq!(*ids.last().unwrap() as usize, BASE as usize + ids.len() - 1, "ids have gaps");
    // every reaction the game matches on is an authored one, each under its own key
    assert_eq!(c.db.map.len(), ids.len(), "two reactions share a (vessel, reactant set)");
    assert!(ids.len() >= 1200, "only {} authored reactions", ids.len());
}

#[test]
fn every_reaction_sits_in_an_era() {
    let c = content();
    let n = c.db.epochs.len();
    assert!(n >= 2);
    for r in &c.db.authored {
        let e = r.epoch as usize;
        assert!(e < n, "{} {} is in era {e} of {n}", r.id, r.name);
    }
    for (i, e) in c.db.epochs.iter().enumerate() {
        assert!(c.db.authored.iter().any(|r| r.epoch == i as u8), "era {} ({}) is empty", i, e.name);
    }
}

#[test]
fn milestones_unlock_every_vessel() {
    let c = content();
    let mut have: HashSet<ProcessType> = [ProcessType::Mix, ProcessType::Heat].into_iter().collect();
    for m in &c.db.milestones {
        have.extend(m.unlock.iter().cloned());
    }
    let missing: Vec<&str> = VESSELS.iter().filter(|v| !have.contains(&v.process)).map(|v| v.name).collect();
    assert!(missing.is_empty(), "never unlocked: {missing:?}");
    let used: HashSet<ProcessType> = c.db.authored.iter().map(|r| r.process.clone()).collect();
    for v in VESSELS {
        assert!(used.contains(&v.process), "no authored reaction uses the {}", v.name);
    }
}

/// Every vessel a milestone unlocks says why that discovery makes it possible (the player
/// sees it when it unlocks, and when they tap it while it is locked).
#[test]
fn every_vessel_says_why_it_unlocks() {
    let bad: Vec<&str> = VESSELS
        .iter()
        .filter(|v| v.why.trim().len() < 20 || !v.why.trim_end().ends_with('.'))
        .map(|v| v.name)
        .collect();
    assert!(bad.is_empty(), "vessels without a reason to unlock: {bad:?}");
}

/// Wherever a player is in the game, every target the Hint button offers comes with a kit
/// that can make it: run the route's steps in order from the kit's items alone and the
/// target appears. The kits leave out what they make on the way, stay within MAX_STEPS,
/// and mix in decoys the route doesn't touch: as many as the setting asks for, wherever
/// there are enough raw materials to spare.
#[test]
fn every_hint_target_has_a_kit_that_makes_it() {
    let c = content();
    let db = &c.db;
    let decoys = Settings::default().decoy_range();
    let mut short = 0;
    let pt = db.playthrough();
    let base = base_materials(db);
    let mut known: HashSet<u32> = db.start.iter().copied().collect();
    let mut vessels: HashSet<ProcessType> = [ProcessType::Mix, ProcessType::Heat].into_iter().collect();
    let mut fired = vec![false; db.milestones.len()];
    let (mut checked, mut multi, mut bad) = (0usize, 0usize, Vec::new());
    for (n, id) in pt.steps.iter().enumerate() {
        loop {
            let mut any = false;
            for (i, m) in db.milestones.iter().enumerate() {
                if !fired[i] && known.contains(&m.on) {
                    fired[i] = true;
                    vessels.extend(m.unlock.iter().cloned());
                    known.extend(m.grant.iter().copied());
                    any = true;
                }
            }
            if !any {
                break;
            }
        }
        if n % 25 == 0 {
            let k = |id: u32| known.contains(&id);
            let o = |p: &ProcessType| vessels.contains(p);
            let mut pool: Vec<u32> = known.iter().copied().collect();
            pool.sort_unstable();
            for t in targets(db, &k, &o) {
                checked += 1;
                let Some(kit) = plan_kit(db, &k, &o, &base, &pool, t.product, t.reaction, decoys) else {
                    bad.push(format!("step {n}: no kit for {}", name(c, t.product)));
                    continue;
                };
                multi += usize::from(kit.steps.len() > 1);
                let shelf: HashSet<u32> = kit.shelf().collect();
                if !makes_target(db, &kit) {
                    bad.push(format!("step {n}: the kit for {} can't make it", name(c, t.product)));
                } else if kit.steps.len() > MAX_STEPS {
                    bad.push(format!("step {n}: {} steps to {}", kit.steps.len(), name(c, t.product)));
                } else if kit.intermediates.iter().any(|i| shelf.contains(i)) || shelf.contains(&t.product) {
                    bad.push(format!("step {n}: the kit for {} gives away a step", name(c, t.product)));
                } else if kit.shelf().any(|id| db.transient.contains(&id)) {
                    bad.push(format!("step {n}: the kit for {} puts a transient on the shelf", name(c, t.product)));
                } else if kit.shelf().any(|id| !known.contains(&id)) {
                    bad.push(format!("step {n}: the kit for {} holds something not yet found", name(c, t.product)));
                } else if kit.decoys.iter().any(|d| kit.items.contains(d)) {
                    bad.push(format!("step {n}: a decoy for {} is needed after all", name(c, t.product)));
                } else if kit.decoys.len() > decoy_count(kit.items.len(), decoys) {
                    bad.push(format!("step {n}: {} decoys for {}", kit.decoys.len(), name(c, t.product)));
                }
                short += usize::from(kit.decoys.len() < decoy_count(kit.items.len(), decoys));
            }
        }
        if let Some(r) = db.authored.iter().find(|r| r.id == *id) {
            known.extend(r.products.iter().map(|p| p.substance_id));
        }
    }
    assert!(bad.is_empty(), "{} of {checked} kits are wrong:\n{}", bad.len(), bad.join("\n"));
    assert!(checked > 100 && multi * 4 > checked, "only {multi} of {checked} kits take more than one step");
    // decoys come from the raw materials found so far: the very first targets may run short
    assert!(short * 10 < checked, "{short} of {checked} kits had fewer decoys than the setting asks for");
}

/// Transients (IsTransient) are made and used at once: each has a step that makes it, none
/// is handed out or sits in a catalyst slot, a step takes at most one (one link in), and
/// the step that makes one doesn't need another (one link deep).
#[test]
fn transients_are_made_and_used_at_once() {
    let c = content();
    let db = &c.db;
    assert!(!db.transient.is_empty(), "no transients in play");
    let base = base_materials(db);
    let mut bad = Vec::new();
    for &t in &db.transient {
        if base.contains(&t) {
            bad.push(format!("{} is handed out, but doesn't keep", name(c, t)));
        }
        match db.maker_of(t) {
            None => bad.push(format!("nothing makes {}", name(c, t))),
            Some(m) if m.reactants.iter().any(|s| db.transient.contains(&s.substance_id)) => {
                bad.push(format!("{} is made from another transient", name(c, t)))
            }
            Some(_) => {}
        }
    }
    for r in &db.authored {
        let ins = r.reactants.iter().filter(|s| db.transient.contains(&s.substance_id)).count();
        if ins > 1 {
            bad.push(format!("{} takes {ins} transients", r.name));
        }
        if r.required_catalyst().is_some_and(|x| db.transient.contains(&x)) {
            bad.push(format!("{} has a transient catalyst", r.name));
        }
    }
    assert!(bad.is_empty(), "{}", bad.join("\n"));
    let marked = c.subs.0.values().filter(|s| s.properties.contains(&Property::IsTransient)).count();
    assert!(marked >= db.transient.len(), "{marked} substances marked, {} in play", db.transient.len());
}

/// Every step has a lesson (systems::lessons), and they say different things: the kinds of
/// change are told apart, not one line for everything.
#[test]
fn steps_teach_more_than_one_lesson() {
    let c = content();
    let mut counts: HashMap<String, usize> = HashMap::new();
    for r in &c.db.authored {
        let l = chem_alchemy::systems::lessons::lesson(r, &c.subs);
        assert!(!l.is_empty(), "no lesson for {}", r.name);
        *counts.entry(l).or_default() += 1;
    }
    let most = counts.values().copied().max().unwrap_or(0);
    let mut by: Vec<(usize, String)> = counts.iter().map(|(k, v)| (*v, k.chars().take(40).collect())).collect();
    by.sort();
    assert!(counts.len() >= 15, "only {} different lessons: {by:?}", counts.len());
    assert!(most * 4 < c.db.authored.len(), "one lesson covers {most} of {} steps: {by:?}", c.db.authored.len());
}

#[test]
fn catalyst_recipes_live_in_vessels_with_a_slot() {
    let c = content();
    // a recipe that needs a catalyst must be able to get one in its home vessel...
    let bad: Vec<String> =
        c.db.authored
            .iter()
            .filter(|r| r.required_catalyst().is_some() && !r.process.has_catalyst_slot())
            .map(|r| format!("{} {} (in the {})", r.id, r.name, r.process.family()))
            .collect();
    assert!(bad.is_empty(), "catalyst recipes in vessels without a slot: {bad:?}");
    // ...and in every vessel above it in the family, which can also run it
    for v in VESSELS.iter().filter(|v| v.catalyst_slot) {
        for w in VESSELS.iter().filter(|w| w.category == v.category && w.tier > v.tier) {
            assert!(w.catalyst_slot, "the {} outranks the {} but has no catalyst slot", w.name, v.name);
        }
    }
}

#[test]
fn vessel_tiers_unlock_in_order() {
    let c = content();
    let pt = c.db.playthrough();
    for v in VESSELS {
        let at = *pt.unlocked_at.get(&v.process).unwrap_or_else(|| panic!("the {} never unlocks", v.name));
        for lower in VESSELS.iter().filter(|w| w.category == v.category && w.tier < v.tier) {
            let low_at = pt.unlocked_at.get(&lower.process).copied().unwrap_or(usize::MAX);
            assert!(
                low_at <= at,
                "the {} (tier {}) unlocks at step {at}, before the {} (tier {}) at {low_at}",
                v.name,
                v.tier,
                lower.name,
                lower.tier
            );
        }
    }
    // each tier has its own recipes
    for family in VESSELS.iter().map(|v| v.category).collect::<BTreeSet<_>>() {
        let tiers: BTreeSet<u8> = VESSELS.iter().filter(|v| v.category == family).map(|v| v.tier).collect();
        assert_eq!(
            tiers.iter().copied().collect::<Vec<_>>(),
            (1..=tiers.len() as u8).collect::<Vec<_>>(),
            "{family} tiers have a gap"
        );
    }
}

#[test]
fn every_vessel_has_enough_recipes() {
    let c = content();
    let thin: Vec<String> = VESSELS
        .iter()
        .map(|v| (v, c.db.authored.iter().filter(|r| r.process == v.process).count()))
        .filter(|(_, n)| *n < 5)
        .map(|(v, n)| format!("{} ({n})", v.name))
        .collect();
    assert!(thin.is_empty(), "vessels with fewer than five recipes of their own: {thin:?}");
}

#[test]
fn pacing_stays_within_limits() {
    let c = content();
    let big: Vec<String> =
        c.db.milestones
            .iter()
            .filter(|m| m.grant.len() > MAX_GRANT)
            .map(|m| format!("on {} grants {}", name(c, m.on), m.grant.len()))
            .collect();
    assert!(big.is_empty(), "grants over {MAX_GRANT} materials: {big:?}");
    let pt = c.db.playthrough();
    assert_eq!(pt.milestone_steps.len(), c.db.milestones.len(), "some milestones never fire");
    let long: Vec<String> =
        c.db.milestone_gaps(&pt)
            .into_iter()
            .filter(|g| g.2 > MAX_MILESTONE_GAP)
            .map(|(a, b, g)| format!("{g} era steps from {a} to {b}"))
            .collect();
    assert!(long.is_empty(), "stretches with no milestone (limit {MAX_MILESTONE_GAP}): {long:?}");
    // the Laboratory is side content, not the tail of the game
    assert!(pt.era_steps * 2 > pt.steps.len(), "{} of {} steps are in the eras", pt.era_steps, pt.steps.len());
}

#[test]
fn every_era_has_a_banner_line() {
    let c = content();
    let side = c.db.side_epoch();
    assert!(side.is_some(), "no side era (\"every age\")");
    for (i, e) in c.db.epochs.iter().enumerate() {
        if Some(i as u8) != side {
            assert!(!e.blurb.trim().is_empty(), "era {} ({}) has no banner line", i, e.name);
        }
    }
}

#[test]
fn art_and_icons_are_on_disk() {
    let assets = root().join("assets");
    let mut missing = Vec::new();
    let mut check = |rel: String| {
        if !assets.join(&rel).exists() {
            missing.push(rel);
        }
    };
    for v in VESSELS {
        for layer in ["fill", "outline", "accent"] {
            check(vessel_art_path(&v.process, layer));
        }
    }
    for icon in [
        "bench", "book", "check", "chevron", "clear", "close", "dot", "external", "flask", "gear", "info", "lock",
        "logo", "minus", "plus", "reaction", "search", "spark", "tree", "grid_dot",
    ] {
        check(format!("images/ui/{icon}.png"));
    }
    for font in ["NotoSans-Regular.ttf", "NotoSans-SemiBold.ttf", "NotoSans-Bold.ttf"] {
        check(format!("fonts/{font}"));
    }
    assert!(missing.is_empty(), "missing assets: {missing:?}");
}

#[test]
fn every_compound_in_play_has_a_structure_picture() {
    let c = content();
    let dir = root().join("assets/structures");
    let missing: Vec<String> =
        c.db.canon
            .iter()
            .filter_map(|id| c.subs.0.get(id))
            .filter(|s| s.element_info.is_none() && !chem_alchemy::ui::inventory::is_element_formula(&s.formula))
            .filter(|s| !Path::new(&dir.join(format!("{}.png", s.id))).exists())
            .map(|s| format!("{} ({})", s.name, s.id))
            .collect();
    assert!(missing.is_empty(), "{} compounds have no structures/<id>.png: {:?}", missing.len(), missing);
}

#[test]
fn every_locked_preview_is_a_whole_page_and_nothing_makes_it() {
    let c = content();
    let dir = root().join("assets/structures");
    let mut bad = Vec::new();
    let mut previews = 0;
    for s in c.subs.0.values().filter(|s| s.stage.is_some()) {
        previews += 1;
        if c.db.canon.contains(&s.id) {
            bad.push(format!("{} ({}): a reaction, milestone or the start kit uses it", s.name, s.id));
        }
        if s.description.as_deref().map(str::trim).unwrap_or("").is_empty() {
            bad.push(format!("{} ({}): no description", s.name, s.id));
        }
        if s.primary_reference().is_none() {
            bad.push(format!("{} ({}): no reference", s.name, s.id));
        }
        if !dir.join(format!("{}.png", s.id)).exists() {
            bad.push(format!("{} ({}): no structures/<id>.png", s.name, s.id));
        }
    }
    assert!(bad.is_empty(), "{} locked previews incomplete:\n{}", bad.len(), bad.join("\n"));
    assert!(previews > 0, "no locked previews of later stages");
}

/// The industry facts (foundations for the factory stages) load and make sense: transport
/// classes are real UN classes, tonnages are positive, medicines sell at pharmaceutical grade,
/// and the big commodities carry them.
#[test]
fn industry_facts_are_well_formed() {
    let c = content();
    let mut bad = Vec::new();
    let (mut tons, mut classes, mut graded) = (0, 0, 0);
    for s in c.subs.0.values() {
        if let Some(t) = s.production_t_year {
            tons += 1;
            if !(t > 0.0 && t.is_finite()) {
                bad.push(format!("{} ({}): production {t}", s.name, s.id));
            }
        }
        if let Some(k) = s.transport_class() {
            classes += 1;
            if un_class_name(k).is_none() {
                bad.push(format!("{} ({}): no UN class {k:?}", s.name, s.id));
            }
        }
        if s.properties.contains(&Property::IsMedicine) && !s.grades.contains(&Grade::Pharmaceutical) {
            bad.push(format!("{} ({}): a medicine not sold at pharmaceutical grade", s.name, s.id));
        }
        graded += usize::from(!s.grades.is_empty());
        if s.grades.contains(&Grade::Technical) {
            bad.push(format!("{} ({}): lists technical grade, which everything sells at", s.name, s.id));
        }
    }
    assert!(bad.is_empty(), "{} industry facts wrong:\n{}", bad.len(), bad.join("\n"));
    assert!(tons > 500 && classes > 500 && graded > 500, "{tons} tonnages, {classes} classes, {graded} graded");
    let ethanol = c.subs.0.values().find(|s| s.name == "Ethanol").expect("Ethanol");
    assert_eq!(ethanol.transport_class(), Some("3"));
    assert!(ethanol.production_t_year.is_some());
    // the big commodities the national records miss carry a rough world figure instead
    let worlds: Vec<f32> = c.subs.0.values().filter_map(|s| s.world_t_year).collect();
    assert!(worlds.len() > 40 && worlds.iter().all(|t| *t > 0.0 && t.is_finite()), "{worlds:?}");
    let acid = c.subs.0.values().find(|s| s.name == "Sulfuric Acid").expect("Sulfuric Acid");
    assert!(acid.world_t_year.is_some_and(|t| t > 1.0e8), "sulfuric acid is made by the hundred million tonnes");
    let mut order: Vec<f32> = [Grade::Technical, Grade::Food, Grade::Pharmaceutical, Grade::Electronic]
        .iter()
        .map(|g| g.min_purity())
        .collect();
    order.dedup();
    assert!(order.windows(2).all(|w| w[0] < w[1]), "grades must get stricter in order: {order:?}");
}

#[test]
fn a_save_round_trips() {
    let data = SaveData {
        version: SAVE_VERSION,
        discovered: vec![1, 5, 8, 12, 900, 15000],
        unlocked: vec![ProcessType::Mix, ProcessType::Heat, ProcessType::Smelting, ProcessType::Catalysis],
        dormant: vec![999_999_901],
        dormant_vessels: vec!["Replicator".into()],
        journal: vec![
            ("Discovery".into(), "New: Quicklime".into()),
            ("Milestone".into(), "Copper! The furnace becomes a smelter.".into()),
        ],
        // the order things were found in, newest last (the shelf's "Newest first")
        order: vec![1, 5, 8, 12, 15000, 900],
    };
    let back = SaveData::parse(&data.to_text()).unwrap();
    assert_eq!(back, data);
    // a save from the build that kept a free-play score still reads
    let older = "(version:3,discovered:[1,5],unlocked:[Mix],score:(points:140,hints_since:2))";
    assert_eq!(SaveData::parse(older).unwrap().discovered, vec![1, 5]);
}

/// Every challenge can be made from its kit alone, in its vessels, in its steps' order; each
/// era the challenges cover has a few; and every step's product is one the route needs.
#[test]
fn every_challenge_can_be_made_from_its_kit() {
    let c = content();
    let all = chem_alchemy::resources::challenge::all_challenges(&c.db);
    assert!(all.len() >= 50, "only {} challenges", all.len());
    let mut eras: HashSet<u8> = HashSet::new();
    for ch in &all {
        eras.insert(ch.era);
        let mut have: HashSet<u32> = ch.kit.iter().copied().collect();
        assert!(!have.contains(&ch.target), "{}: the kit holds the target", name(c, ch.target));
        assert!((2..=4).contains(&ch.steps.len()), "{}: {} steps", name(c, ch.target), ch.steps.len());
        assert_eq!(ch.steps.len(), ch.step_products.len());
        for (i, id) in ch.steps.iter().enumerate() {
            let r = c.db.authored.iter().find(|r| r.id == *id).expect("a step exists");
            assert!(ch.vessels.contains(&r.process), "{}: {} is not among its vessels", name(c, ch.target), r.name);
            assert!(
                r.reactants.iter().all(|s| have.contains(&s.substance_id))
                    && r.required_catalyst().is_none_or(|k| have.contains(&k)),
                "{}: step {} ({}) can't run from what came before",
                name(c, ch.target),
                i + 1,
                r.name
            );
            assert!(
                r.products.iter().any(|p| p.substance_id == ch.step_products[i]),
                "{}: step {} doesn't make {}",
                name(c, ch.target),
                i + 1,
                name(c, ch.step_products[i])
            );
            have.extend(r.products.iter().map(|p| p.substance_id));
        }
        assert_eq!(ch.step_products.last(), Some(&ch.target));
        assert!(ch.decoys.iter().all(|d| !ch.kit.contains(d)), "{}: a decoy is in the kit", name(c, ch.target));
    }
    assert!(eras.len() >= 6, "challenges in only {} eras", eras.len());
}

/// Saves written by earlier builds (tests/saves) load against today's content: what the
/// content still has comes back, what it doesn't is kept aside rather than dropped, and
/// the save written back reads the same.
#[test]
fn old_saves_still_load_after_content_changes() {
    let c = content();
    let dir = root().join("tests/saves");
    let mut files: Vec<PathBuf> = std::fs::read_dir(&dir).unwrap().map(|e| e.unwrap().path()).collect();
    files.sort();
    assert!(files.len() >= 2, "expected the old-save fixtures in {}", dir.display());
    for f in files {
        let text = std::fs::read_to_string(&f).unwrap();
        let read = SaveData::parse(&text).unwrap_or_else(|e| panic!("{} no longer loads: {e}", f.display()));
        let before: HashSet<u32> = read.discovered.iter().copied().collect();
        let save = read.settle(|id| c.subs.0.contains_key(&id));
        let kept: HashSet<u32> = save.discovered.iter().chain(save.dormant.iter()).copied().collect();
        assert_eq!(kept, before, "{}: a discovery went missing", f.display());
        assert!(save.discovered.iter().all(|id| c.subs.0.contains_key(id)));
        assert!(!save.discovered.is_empty() && !save.unlocked.is_empty(), "{}: nothing survived", f.display());
        let again = SaveData::parse(&save.to_text()).unwrap().settle(|id| c.subs.0.contains_key(&id));
        assert_eq!(again.discovered, save.discovered, "{}: rewrite changed it", f.display());
        assert_eq!((again.dormant, again.dormant_vessels), (save.dormant, save.dormant_vessels));
    }
    // the finished game from the first build keeps nearly all of it
    let finished = SaveData::parse(&std::fs::read_to_string(dir.join("v1_first_build_finished.ron")).unwrap())
        .unwrap()
        .settle(|id| c.subs.0.contains_key(&id));
    assert!(finished.dormant.len() * 100 <= finished.discovered.len(), "over 1% of an old game went dormant");
    // and an unknown vessel is kept by name
    let odd = SaveData::parse(&std::fs::read_to_string(dir.join("v1_unknown_content.ron")).unwrap()).unwrap();
    assert_eq!(odd.dormant_vessels, vec!["Replicator".to_string()]);
}

#[test]
fn settings_round_trip_and_tolerate_old_files() {
    let s = Settings {
        ui_scale: 1.25,
        reaction_speed: 3.0,
        names_first: true,
        tooltips: false,
        tour_done: true,
        ..Settings::default()
    };
    let text = ron::ser::to_string_pretty(&s, ron::ser::PrettyConfig::default()).unwrap();
    let back: Settings = ron::from_str(&text).unwrap();
    assert_eq!(back, s);
    // a settings file from an older build, with fields missing, still loads
    let old: Settings = ron::from_str("(ui_scale: 1.5)").unwrap();
    assert_eq!(old.ui_scale, 1.5);
    assert_eq!(old.reaction_speed, Settings::default().reaction_speed);
    assert!(old.tooltips && old.next_step && !old.tour_done, "help defaults on for an old settings file");
    assert!(old.kit, "target kits default on for an old settings file");
}

/// Every description the game ships says where it came from, and that source is one whose
/// terms allow it (tools/data/audit_library.py tags the library; authored text is ours).
#[test]
fn every_description_has_a_licensed_source() {
    let c = content();
    let mut bad: Vec<String> = c
        .subs
        .0
        .values()
        .filter(|s| s.description.is_some())
        .filter(|s| !s.text_source.as_deref().is_some_and(|t| TEXT_SOURCES.contains(&t)))
        .map(|s| format!("{} ({}): {:?}", s.name, s.id, s.text_source))
        .collect();
    bad.sort();
    assert!(
        bad.is_empty(),
        "{} descriptions have no licensed source (run python tools/data/audit_library.py --write): {:?}",
        bad.len(),
        &bad[..bad.len().min(20)]
    );
    // and the game can credit every third-party source on the page
    for t in TEXT_SOURCES.iter().filter(|t| **t != "Curieosity") {
        assert!(text_credit(t).is_some(), "no credit line for {t}");
    }
}

/// CREDITS.md in the repository says what the game's Credits screen says.
#[test]
fn credits_md_matches_the_credits_screen() {
    let md = std::fs::read_to_string(root().join("CREDITS.md")).expect("CREDITS.md");
    for (section, credits) in SECTIONS {
        assert!(md.contains(&format!("## {section}")), "CREDITS.md has no section {section:?}");
        for c in *credits {
            let row = md
                .lines()
                .find(|l| l.contains(c.name) && l.starts_with('|'))
                .unwrap_or_else(|| panic!("CREDITS.md doesn't list {}", c.name));
            assert!(row.contains(c.what), "CREDITS.md describes {} differently from the game", c.name);
            assert!(row.contains(c.licence), "CREDITS.md gives {} different terms from the game", c.name);
        }
    }
    for f in ["LICENSE-MIT", "LICENSE-APACHE", "LICENSE-CONTENT.md"] {
        assert!(root().join(f).is_file(), "{f} is missing");
    }
}

/// The README says what the About screen says, in the same words: who made the game and
/// how, what it does with your data, where to give (in the same order, each with its link)
/// and every source it is built from.
#[test]
fn readme_matches_the_about_screen() {
    let md = std::fs::read_to_string(root().join("README.md")).expect("README.md");
    // the README wraps its lines; compare words
    let flat = |s: &str| s.split_whitespace().collect::<Vec<_>>().join(" ");
    let text = flat(&md);
    for (what, words) in [("who made it", MADE_BY), ("how the art is made", HOW_MADE), ("privacy", PRIVACY)] {
        assert!(text.contains(&flat(words)), "the README doesn't say what the About screen says about {what}");
    }
    let mut from = md.find("## If you'd like to give something").expect("the README has no giving section");
    for c in GIVING {
        let at =
            md[from..].find(c.name).unwrap_or_else(|| panic!("the README doesn't list {} (in order)", c.name)) + from;
        let line = md[at..].lines().next().unwrap_or("");
        match c.url {
            Some(url) => assert!(md[at..].contains(url), "the README's {} has no link to {url}", c.name),
            None => assert!(line.contains("coming soon"), "the README should say {} is coming soon", c.name),
        }
        from = at;
    }
    for (_, credits) in SECTIONS {
        for c in credits.iter().filter(|c| c.name != "Curieosity") {
            let name = c.name.split(" (").next().unwrap_or(c.name);
            assert!(md.contains(&format!("[{name}]")), "the README's sources don't link {name}");
        }
    }
}

/// The achievements are unique, fit Steam's limits, and steam/achievements.csv (what is
/// entered in Steamworks, with its icons) lists exactly them. After changing milestones or
/// eras, rewrite it with CURIEOSITY_WRITE_STEAM=1 set and redraw the icons with
/// tools/art/gen_steam_art.py.
#[test]
fn steam_achievements_match_the_content() {
    let c = content();
    let list =
        achievement_list(&c.db, |id| (name(c, id), c.subs.0.get(&id).map(|s| s.formula.clone()).unwrap_or_default()));
    let mut seen = HashSet::new();
    for a in &list {
        assert!(seen.insert(a.id.clone()), "two achievements are called {}", a.id);
        assert!(
            a.id.chars().all(|ch| ch.is_ascii_uppercase() || ch.is_ascii_digit() || ch == '_'),
            "{} is not an API name",
            a.id
        );
        assert!(a.id.len() <= 64 && a.name.len() <= 128 && a.description.len() <= 256, "{} is too long", a.id);
    }
    // Steam allows 100 achievements until the app has been reviewed
    assert!(list.len() <= 100, "{} achievements; Steam allows 100 before review", list.len());
    let csv = achievements_csv(&list);
    let path = root().join("steam/achievements.csv");
    if std::env::var_os("CURIEOSITY_WRITE_STEAM").is_some() {
        std::fs::create_dir_all(path.parent().unwrap()).unwrap();
        std::fs::write(&path, &csv).unwrap();
    }
    let on_disk = std::fs::read_to_string(&path).unwrap_or_default().replace("\r\n", "\n");
    assert!(
        on_disk == csv,
        "steam/achievements.csv is out of date: run the tests with CURIEOSITY_WRITE_STEAM=1 set, then python tools/art/gen_steam_art.py"
    );
}

/// Nothing the game shows boils below its melting point: pages.ron's checked values replace
/// the library's, and a pair that contradicts itself is left out (tools/data/gen_pages.py).
#[test]
fn nothing_boils_below_its_melting_point() {
    let c = content();
    let mut bad = Vec::new();
    for id in c.db.canon.iter().copied().chain(previews(c)) {
        let Some(s) = c.subs.0.get(&id) else { continue };
        if let (Some(m), Some(b)) = (s.melting_point_c, s.boiling_point_c) {
            if m > b + 0.5 {
                bad.push(format!("{} melts at {m}, boils at {b}", s.name));
            }
        }
        if s.phase_note.is_some()
            && s.boiling_point_c.is_some()
            && s.phase_note.as_deref().is_some_and(|n| n.starts_with("Sublimes"))
        {
            bad.push(format!("{} sublimes but has a boiling point", s.name));
        }
    }
    assert!(bad.is_empty(), "{} contradictions: {:?}", bad.len(), &bad[..bad.len().min(20)]);
}

fn previews(c: &Content) -> impl Iterator<Item = u32> + '_ {
    c.subs.0.values().filter(|s| s.stage.is_some()).map(|s| s.id)
}

/// The curriculum links only to its own topics, every topic is a Wikipedia article in one of
/// its units, and every vessel and era has topics behind it.
#[test]
fn the_curriculum_hangs_together() {
    let c = content();
    let p = &c.pages;
    let units: HashSet<&str> = p.units.iter().map(|(k, _)| k.as_str()).collect();
    assert!(p.topics.len() >= 300, "only {} topics", p.topics.len());
    for (k, t) in &p.topics {
        assert!(units.contains(t.unit.as_str()), "{k} is in no unit ({})", t.unit);
        assert!(t.url.starts_with("https://en.wikipedia.org/wiki/"), "{k} doesn't link to Wikipedia: {}", t.url);
    }
    let known = |k: &String| p.topics.contains_key(k);
    for (id, ts) in &p.reactions {
        assert!(
            c.authored.reactions.iter().any(|r| r.id == *id),
            "pages.ron links reaction {id}, which isn't in the game"
        );
        assert!(ts.iter().all(known), "reaction {id} links an unknown topic: {ts:?}");
    }
    for v in VESSELS {
        let ts = p.vessels.get(&v.process).unwrap_or_else(|| panic!("the {} has no topics", v.name));
        assert!(!ts.is_empty() && ts.iter().all(known), "the {}'s topics: {ts:?}", v.name);
    }
    for e in &c.authored.epochs {
        let ts = p.eras.get(&e.name).unwrap_or_else(|| panic!("the {} era has no topics", e.name));
        assert!(ts.iter().all(known), "the {} era's topics: {ts:?}", e.name);
    }
    let linked = p.reactions.len();
    assert!(linked * 2 > c.authored.reactions.len(), "only {linked} reactions link a topic");
}

/// Every page is a Wikipedia article's, credited, readable and short enough for a phone.
#[test]
fn pages_are_well_formed() {
    let c = content();
    for (id, pg) in &c.pages.substances {
        let name = c
            .subs
            .0
            .get(id)
            .map(|s| s.name.as_str())
            .unwrap_or_else(|| panic!("a page for {id}, which isn't in the game"));
        assert!(pg.url.starts_with("https://en.wikipedia.org/wiki/"), "{name}'s page links {}", pg.url);
        assert!(!pg.title.is_empty() && pg.revised.len() == 10, "{name}'s page has no title or revision date");
        assert!(!pg.lead.trim().is_empty() || !pg.sections.is_empty(), "{name}'s page has no text");
        assert!(pg.sections.len() <= 4, "{name}'s page has {} sections", pg.sections.len());
        let total = pg.lead.len() + pg.sections.iter().map(|(h, t)| h.len() + t.len()).sum::<usize>();
        assert!(total <= 8000, "{name}'s page is {total} bytes");
        for (h, t) in &pg.sections {
            assert!(!h.is_empty() && t.trim().len() >= 60, "{name}'s {h} section is empty");
        }
        assert!(!pg.lead.contains("displaystyle"), "{name}'s lead has maths markup in it");
    }
}
