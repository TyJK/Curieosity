// tests/content.rs
//
// Content checks: the authored game is loaded exactly as the game loads it (substance
// library + authored substance layer, scraped + authored reactions) and checked for the
// things that would break a playthrough or a library page. The scripted in-game
// playthrough (`cargo run --release -- --autoplay`) covers what these can't: the real UI.
//
// Run with `cargo test --release` (the scraped library is ~75 MB of RON, slow to parse in
// a debug build).
use std::collections::{BTreeSet, HashMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::OnceLock;

use chem_alchemy::data::common::ProcessType;
use chem_alchemy::data::reactions::Reactions;
use chem_alchemy::data::substances::{SubstancePatches, Substances};
use chem_alchemy::resources::player_progress::{SaveData, SAVE_VERSION};
use chem_alchemy::resources::recipe_database::{RecipeDatabase, RecipeKey, MAX_GRANT, MAX_MILESTONE_GAP};
use chem_alchemy::systems::achievements::{achievement_list, achievements_csv};
use chem_alchemy::ui::credits::{text_credit, SECTIONS, TEXT_SOURCES};
use chem_alchemy::ui::process_toolbar::{vessel_art_path, VESSELS};
use chem_alchemy::ui::settings::Settings;

struct Content {
    subs: Substances,
    authored: Reactions,
    db: RecipeDatabase,
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
        let scraped: Reactions = load("reactions.ron");
        let authored: Reactions = load("authored_reactions.ron");
        let db = RecipeDatabase::from_parts(&scraped, &authored);
        Content { subs, authored, db }
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
        if s.wikipedia().is_none() {
            bad.push(format!("{} ({}): no Wikipedia reference", s.name, id));
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
    assert!(ids.iter().all(|id| (100..2000).contains(id)), "ids outside 100..2000");
    assert_eq!(ids.first(), Some(&100));
    assert_eq!(*ids.last().unwrap() as usize, 100 + ids.len() - 1, "ids have gaps");
    assert!(ids.len() >= 1200, "only {} authored reactions", ids.len());
}

#[test]
fn every_reaction_sits_in_an_era() {
    let c = content();
    let n = c.db.epochs.len();
    assert!(n >= 2);
    for r in &c.db.authored {
        let e = r.epoch.expect("authored reactions carry an era") as usize;
        assert!(e < n, "{} {} is in era {e} of {n}", r.id, r.name);
    }
    for (i, e) in c.db.epochs.iter().enumerate() {
        assert!(c.db.authored.iter().any(|r| r.epoch == Some(i as u8)), "era {} ({}) is empty", i, e.name);
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
fn a_save_round_trips() {
    let data = SaveData {
        version: SAVE_VERSION,
        discovered: vec![1, 5, 8, 12, 900, 15000],
        unlocked: vec![ProcessType::Mix, ProcessType::Heat, ProcessType::Smelting, ProcessType::Catalysis],
        dormant: vec![999_999_901],
        dormant_vessels: vec!["Centrifuge".into()],
    };
    let back = SaveData::parse(&data.to_text()).unwrap();
    assert_eq!(back, data);
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
    assert_eq!(odd.dormant_vessels, vec!["Centrifuge".to_string()]);
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
