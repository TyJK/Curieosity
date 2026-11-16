// src/systems/autoplay.rs
//
// Gameplay events, and the scripted review playthrough.
//
// `GameEvent` is written by the real game systems (discoveries, milestones, reactions,
// fizzles). The playthrough is off unless the game is started with `--autoplay`:
//
//     cargo run --release -- --autoplay              # the whole tech tree
//     cargo run --release -- --autoplay --steps 40   # just the first 40 reactions
//     options: --every N (checkpoint screenshot every N steps, default 75), --out DIR
//
// First come the interaction checks (systems/input_checks.rs): every click, drag, key and
// wheel a player uses, driven through the real input stack and checked for its effect
// (`--steps 0` runs only these). Then the playthrough: it puts each vessel on the bench,
// drops the reactants (and any catalyst) in, presses React, and waits for the products, in
// the order `RecipeDatabase::playthrough` finds. It never reads or writes the player's save
// or settings. Everything it sees goes to `target/review/run_<time>/`:
//     report.md     summary, interaction checks, failures, pacing, milestones, eras, frame
//                   times, screenshots
//     events.jsonl  one JSON object per event (discovery, milestone, reaction, fizzle,
//                   checkpoint, screenshot), in order
//     state.json    the final state, for diffing between runs
//     shots/*.png   the bench at the start, at every milestone and checkpoint, then a
//                   tour of every view (early in the game and at the end)
// The process exits with code 0 if every check and step worked and 1 if any failed.
use bevy::app::AppExit;
use bevy::ecs::system::SystemParam;
use bevy::prelude::*;
use bevy::render::view::window::screenshot::{save_to_disk, Screenshot};
use std::collections::HashMap;
use std::io::Write;
use std::path::PathBuf;

use crate::components::{
    CanvasScrollingPane, InCatalystZone, InVessel, Ingredient, VesselCard, VesselCatalystZone, VesselIngredientZone,
};
use crate::data::common::ProcessType;
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::recipe_database::{RecipeDatabase, MAX_GRANT, MAX_MILESTONE_GAP};
use crate::resources::ui_fonts::UiFonts;
use crate::systems::input_checks::{InputChecks, InputChecksPlugin};
use crate::systems::reaction_check::{spawn_vessel_card, CheckVesselReaction, VESSEL_W};
use crate::ui::codex::CodexState;
use crate::ui::inventory::{spawn_vessel_chip, ChipRole};
use crate::ui::onboarding::{Coach, CoachStep};
use crate::ui::process_toolbar::{vessel_name, ProcessUnlocks, VESSELS};
use crate::ui::reaction_library::ReactionLibState;
use crate::ui::settings::{Settings, SettingsUi};
use crate::ui::tech_tree::{TechMode, TechTreeState};
use crate::GameData;

/// Something that happened in the game. Written by the game systems; read by the review
/// playthrough (and free for anything else to listen to).
#[derive(Message, Clone, Debug)]
pub enum GameEvent {
    Discovery {
        id: u32,
    },
    Milestone {
        index: usize,
        on: u32,
    },
    Fizzle {
        process: ProcessType,
        reactants: Vec<u32>,
        reason: String,
    },
    Reacted {
        reaction_id: u32,
        vessel: Entity,
    },
    /// the header's era moved on (the banner went up)
    Era {
        index: u8,
    },
}

// ---------------------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------------------
#[derive(Resource, Clone, Debug)]
pub struct AutoplayConfig {
    /// stop after this many reactions (None = the whole tree)
    pub limit: Option<usize>,
    /// a checkpoint screenshot every this many steps
    pub every: usize,
    pub out_dir: PathBuf,
    /// the window size in logical pixels (`--window 915x412` plays at a phone's size)
    pub window: (u32, u32),
    /// true when `--window` was given: the interface size then follows the screen, as it
    /// does on a phone's first run
    pub fit_screen: bool,
    /// `--scale 1.0`: play at this interface size instead (how a phone looks after the
    /// player changes the size)
    pub scale: Option<f32>,
}

impl AutoplayConfig {
    /// `Some` when the game was started with `--autoplay`.
    pub fn from_args() -> Option<Self> {
        let args: Vec<String> = std::env::args().collect();
        if !args.iter().any(|a| a == "--autoplay") {
            return None;
        }
        let value = |flag: &str| args.iter().position(|a| a == flag).and_then(|i| args.get(i + 1)).cloned();
        let out_dir = value("--out")
            .map(PathBuf::from)
            .unwrap_or_else(|| PathBuf::from("target").join("review").join(format!("run_{}", timestamp())));
        let window = value("--window").and_then(|v| {
            let (w, h) = v.split_once('x')?;
            Some((w.trim().parse().ok()?, h.trim().parse().ok()?))
        });
        Some(Self {
            limit: value("--steps").and_then(|s| s.parse().ok()),
            every: value("--every").and_then(|s| s.parse().ok()).unwrap_or(75).max(1),
            out_dir,
            window: window.unwrap_or((1280, 720)),
            scale: value("--scale").and_then(|v| v.parse().ok()),
            fit_screen: window.is_some() && value("--scale").is_none(),
        })
    }
}

/// UTC "YYYYMMDD-HHMMSS" from the system clock (no date crate needed).
fn timestamp() -> String {
    let secs =
        std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs() as i64).unwrap_or(0);
    let (days, rem) = (secs.div_euclid(86_400), secs.rem_euclid(86_400));
    // civil-from-days (Howard Hinnant)
    let z = days + 719_468;
    let era = z.div_euclid(146_097);
    let doe = z - era * 146_097;
    let yoe = (doe - doe / 1460 + doe / 36_524 - doe / 146_096) / 365;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = doy - (153 * mp + 2) / 5 + 1;
    let m = if mp < 10 { mp + 3 } else { mp - 9 };
    let y = yoe + era * 400 + if m <= 2 { 1 } else { 0 };
    format!("{:04}{:02}{:02}-{:02}{:02}{:02}", y, m, d, rem / 3600, rem % 3600 / 60, rem % 60)
}

pub struct AutoplayPlugin(pub AutoplayConfig);

impl Plugin for AutoplayPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(self.0.clone())
            .add_plugins(InputChecksPlugin)
            .init_resource::<Autoplay>()
            .add_systems(Update, (autoplay_log_system, autoplay_drive_system).chain());
    }
}

// ---------------------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------------------
#[derive(Clone, Copy, PartialEq, Debug, Default)]
enum Phase {
    #[default]
    Boot,
    /// the interaction checks (systems/input_checks.rs)
    Checks,
    /// pick the next step's vessel (spawning one if needed)
    Prepare,
    /// drop the reactants in
    Fill,
    /// press React
    Fire,
    /// wait for the reaction (or a fizzle) and the products
    Await,
    /// let a screenshot render, then carry on with `then`
    Shot,
    /// show each view in turn and photograph it
    Tour,
    /// write the report and quit
    Finish,
    Done,
}

#[derive(Clone, Debug)]
struct StepResult {
    step: usize,
    reaction: u32,
    name: String,
    epoch: u8,
    ok: bool,
    note: String,
    frames: u32,
}

#[derive(Clone, Copy, PartialEq, Debug)]
enum TourView {
    Lab,
    TreeGraph,
    TreeList,
    SubstanceCompound,
    SubstanceElement,
    Reactions,
    Settings,
}

const TOUR: [TourView; 7] = [
    TourView::Lab,
    TourView::TreeGraph,
    TourView::TreeList,
    TourView::SubstanceCompound,
    TourView::SubstanceElement,
    TourView::Reactions,
    TourView::Settings,
];

#[derive(Resource, Default)]
pub struct Autoplay {
    phase: Phase,
    /// frames to wait before acting on the current phase
    wait: u32,
    steps: Vec<u32>,
    unreachable: Vec<u32>,
    idx: usize,
    /// vessels on the bench (process, card, slot), least recently used first
    bench: Vec<(ProcessType, Entity, usize)>,
    vessel: Option<Entity>,
    frames_in_step: u32,
    reacted: Option<u32>,
    fizzle: Option<String>,
    results: Vec<StepResult>,
    shots: Vec<(String, String)>,
    shot_after: Option<Phase>,
    pending_shot: Option<String>,
    milestones: Vec<(usize, u32, usize, Option<String>)>, // (index, on, step, shot)
    tour_i: usize,
    tour_label: &'static str,
    early_tour_done: bool,
    last_discovery: Option<u32>,
    log: Option<std::io::BufWriter<std::fs::File>>,
    started: f64,
    fizzles: usize,
    discoveries: usize,
    /// false while the interaction checks run (their milestones are not the playthrough's)
    in_play: bool,
    /// (era index, step) for every era banner during the playthrough
    eras: Vec<(u8, usize)>,
    /// frame times (ms) during the playthrough
    frame_ms: Vec<f32>,
}

// ---------------------------------------------------------------------------------------
// Small JSON writer (no extra dependency)
// ---------------------------------------------------------------------------------------
fn js(s: &str) -> String {
    let mut o = String::with_capacity(s.len() + 2);
    o.push('"');
    for c in s.chars() {
        match c {
            '"' => o.push_str("\\\""),
            '\\' => o.push_str("\\\\"),
            '\n' => o.push_str("\\n"),
            '\r' => o.push_str("\\r"),
            '\t' => o.push_str("\\t"),
            c if (c as u32) < 0x20 => o.push_str(&format!("\\u{:04x}", c as u32)),
            c => o.push(c),
        }
    }
    o.push('"');
    o
}

fn ja<T: ToString>(v: &[T]) -> String {
    format!("[{}]", v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","))
}

impl Autoplay {
    fn emit(&mut self, t: f64, kind: &str, fields: &[(&str, String)]) {
        let Some(log) = self.log.as_mut() else { return };
        let mut line = format!("{{\"t\":{:.3},\"step\":{},\"kind\":{}", t - self.started, self.idx, js(kind));
        for (k, v) in fields {
            line.push_str(&format!(",{}:{}", js(k), v));
        }
        line.push('}');
        let _ = writeln!(log, "{}", line);
    }
}

#[derive(SystemParam)]
pub struct Game<'w, 's> {
    db: Option<Res<'w, RecipeDatabase>>,
    progress: Res<'w, PlayerProgress>,
    unlocks: Res<'w, ProcessUnlocks>,
    game_data: Option<Res<'w, GameData>>,
    substances: Res<'w, Assets<Substances>>,
    fonts: Option<Res<'w, UiFonts>>,
    assets: Res<'w, AssetServer>,
    settings: Option<ResMut<'w, Settings>>,
    time: Res<'w, Time<Real>>,
    pane: Query<'w, 's, Entity, With<CanvasScrollingPane>>,
    cards: Query<'w, 's, &'static Children, With<VesselCard>>,
    ingredient_zones: Query<'w, 's, (), With<VesselIngredientZone>>,
    catalyst_zones: Query<'w, 's, (), With<VesselCatalystZone>>,
    chips: Query<'w, 's, (Entity, Option<&'static InVessel>, Option<&'static InCatalystZone>), With<Ingredient>>,
}

#[derive(SystemParam)]
pub struct Views<'w> {
    codex: ResMut<'w, CodexState>,
    rlib: ResMut<'w, ReactionLibState>,
    tree: ResMut<'w, TechTreeState>,
    settings_ui: ResMut<'w, SettingsUi>,
    coach: ResMut<'w, Coach>,
}

impl Views<'_> {
    fn close_all(&mut self) {
        self.codex.open = false;
        self.rlib.open = false;
        self.tree.open = false;
        self.settings_ui.open = false;
    }
}

// ---------------------------------------------------------------------------------------
// Systems
// ---------------------------------------------------------------------------------------
/// Write every game event to the log as it happens.
fn autoplay_log_system(mut events: MessageReader<GameEvent>, mut ap: ResMut<Autoplay>, game: Game) {
    let now = game.time.elapsed_secs_f64();
    if ap.in_play {
        ap.frame_ms.push(game.time.delta_secs() * 1000.0);
    }
    let subs = game.game_data.as_ref().and_then(|g| game.substances.get(&g.substances));
    let name = |id: u32| subs.and_then(|s| s.0.get(&id)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    for ev in events.read() {
        match ev {
            GameEvent::Discovery { id } => {
                ap.discoveries += 1;
                ap.last_discovery = Some(*id);
                ap.emit(now, "discovery", &[("id", id.to_string()), ("name", js(&name(*id)))]);
            }
            GameEvent::Milestone { index, on } => {
                if ap.in_play {
                    let label = format!("milestone_{:02}_{}", index, slug(&name(*on)));
                    let step = ap.idx;
                    ap.milestones.push((*index, *on, step, None));
                    ap.pending_shot = Some(label);
                }
                let unlocked: Vec<String> = game.unlocks.0.iter().map(|p| js(vessel_name(p))).collect();
                ap.emit(
                    now,
                    "milestone",
                    &[
                        ("index", index.to_string()),
                        ("on", js(&name(*on))),
                        ("discovered", game.progress.discovered.len().to_string()),
                        ("unlocked", format!("[{}]", unlocked.join(","))),
                    ],
                );
            }
            GameEvent::Fizzle { process, reactants, reason } => {
                if ap.in_play {
                    ap.fizzles += 1;
                }
                ap.fizzle = Some(reason.clone());
                ap.emit(
                    now,
                    "fizzle",
                    &[("vessel", js(vessel_name(process))), ("reactants", ja(reactants)), ("reason", js(reason))],
                );
            }
            GameEvent::Reacted { reaction_id, .. } => {
                ap.reacted = Some(*reaction_id);
                let rname = game
                    .db
                    .as_ref()
                    .and_then(|db| {
                        db.authored
                            .iter()
                            .find(|r| r.id == *reaction_id)
                            .or_else(|| db.map.values().find(|r| r.id == *reaction_id))
                    })
                    .map(|r| r.name.clone())
                    .unwrap_or_default();
                ap.emit(now, "reacted", &[("reaction", reaction_id.to_string()), ("name", js(&rname))]);
            }
            GameEvent::Era { index } => {
                if ap.in_play {
                    let step = ap.idx;
                    ap.eras.push((*index, step));
                }
                let name = game.db.as_ref().map(|db| db.epoch_name(*index).to_string()).unwrap_or_default();
                ap.emit(now, "era", &[("index", index.to_string()), ("name", js(&name))]);
            }
        }
    }
}

fn slug(s: &str) -> String {
    let mut o: String = s.to_lowercase().chars().map(|c| if c.is_ascii_alphanumeric() { c } else { '_' }).collect();
    while o.contains("__") {
        o = o.replace("__", "_");
    }
    o.trim_matches('_').chars().take(32).collect()
}

fn autoplay_drive_system(
    mut commands: Commands,
    cfg: Res<AutoplayConfig>,
    mut ap: ResMut<Autoplay>,
    mut game: Game,
    mut views: Views,
    mut check: MessageWriter<CheckVesselReaction>,
    mut exit: MessageWriter<AppExit>,
    mut checks: ResMut<InputChecks>,
) {
    if ap.wait > 0 {
        ap.wait -= 1;
        if ap.phase == Phase::Await {
            ap.frames_in_step += 1;
        }
        return;
    }
    let now = game.time.elapsed_secs_f64();
    match ap.phase {
        Phase::Boot => {
            let ready = game.db.is_some() && game.progress.ready && game.fonts.is_some() && game.pane.single().is_ok();
            if !ready {
                return;
            }
            let _ = std::fs::create_dir_all(cfg.out_dir.join("shots"));
            ap.log = std::fs::File::create(cfg.out_dir.join("events.jsonl")).ok().map(std::io::BufWriter::new);
            ap.started = now;
            let pt = game.db.as_ref().unwrap().playthrough();
            ap.steps = pt.steps;
            ap.unreachable = pt.unreachable;
            if let Some(limit) = cfg.limit {
                ap.steps.truncate(limit);
            }
            // fast reactions; this never reaches the settings file (persistence is off)
            if let Some(s) = game.settings.as_mut() {
                s.reaction_speed = 25.0;
            }
            let steps = ap.steps.len();
            let unreachable = ap.unreachable.clone();
            ap.emit(now, "start", &[("steps", steps.to_string()), ("unreachable", ja(&unreachable))]);
            info!("Autoplay: {} steps, writing to {}", steps, cfg.out_dir.display());
            take_shot(&mut commands, &cfg, &mut ap, "00_start".into(), Phase::Checks, now);
            ap.wait = 90; // let the first frames lay out and the images load
        }

        Phase::Checks => {
            if !checks.requested {
                checks.requested = true;
                checks.out_dir = Some(cfg.out_dir.clone());
                ap.emit(now, "checks_start", &[]);
                return;
            }
            if !checks.done {
                return;
            }
            let results: Vec<_> = checks.results.clone();
            for r in &results {
                ap.emit(
                    now,
                    "check",
                    &[("area", js(r.area)), ("name", js(r.name)), ("ok", r.ok.to_string()), ("note", js(&r.note))],
                );
            }
            // the playthrough starts from a new game, reacting fast, with the first-steps
            // tour put away (the checks cover it)
            if let Some(s) = game.settings.as_mut() {
                s.reaction_speed = 25.0;
                s.tour_done = true;
                s.next_step = true; // the screenshots show the suggestion as the game goes
                s.tooltips = false; // and no tooltip left over from wherever the cursor rests
            }
            views.coach.step = CoachStep::Off;
            ap.bench.clear();
            ap.in_play = true;
            ap.phase = Phase::Prepare;
            ap.wait = 20;
        }

        Phase::Prepare => {
            if ap.idx >= ap.steps.len() {
                ap.tour_i = 0;
                ap.tour_label = "end";
                ap.phase = Phase::Tour;
                return;
            }
            if !ap.early_tour_done && ap.idx == 12.min(ap.steps.len().saturating_sub(1)) && ap.idx > 0 {
                ap.early_tour_done = true;
                ap.tour_i = 0;
                ap.tour_label = "early";
                ap.phase = Phase::Tour;
                return;
            }
            let rid = ap.steps[ap.idx];
            let Some(r) = game.db.as_ref().unwrap().authored.iter().find(|r| r.id == rid).cloned() else {
                fail(&mut ap, rid, "", 0, "reaction id not found");
                return;
            };
            ap.reacted = None;
            ap.fizzle = None;
            ap.frames_in_step = 0;
            if !game.unlocks.0.contains(&r.process) {
                let note = format!("{} is still locked", vessel_name(&r.process));
                fail(&mut ap, rid, &r.name, r.epoch.unwrap_or(0), &note);
                return;
            }
            // reuse this process's vessel, or put one on the bench (at most four, so the
            // bench stays readable in the screenshots)
            let vessel = if let Some(pos) = ap.bench.iter().position(|(p, _, _)| *p == r.process) {
                let v = ap.bench.remove(pos);
                let e = v.1;
                ap.bench.push(v);
                e
            } else {
                let slot = if ap.bench.len() >= 4 {
                    let (_, old, slot) = ap.bench.remove(0);
                    commands.entity(old).despawn();
                    slot
                } else {
                    ap.bench.len()
                };
                let pane = game.pane.single().unwrap();
                let pos = Vec2::new(24.0 + slot as f32 * (VESSEL_W + 28.0), 24.0);
                let e = spawn_vessel_card(
                    &mut commands,
                    pane,
                    &r.process,
                    vessel_name(&r.process),
                    pos,
                    game.fonts.as_ref().unwrap(),
                    &game.assets,
                );
                ap.bench.push((r.process.clone(), e, slot));
                ap.wait = 2; // its zones exist from the next frame
                e
            };
            ap.vessel = Some(vessel);
            ap.phase = Phase::Fill;
        }

        Phase::Fill => {
            let rid = ap.steps[ap.idx];
            let Some(vessel) = ap.vessel else { return };
            let db = game.db.as_ref().unwrap();
            let Some(r) = db.authored.iter().find(|r| r.id == rid).cloned() else { return };
            let Some(subs) = game.game_data.as_ref().and_then(|g| game.substances.get(&g.substances)) else { return };
            let Ok(children) = game.cards.get(vessel) else {
                fail(&mut ap, rid, &r.name, r.epoch.unwrap_or(0), "vessel card missing");
                return;
            };
            let zone = children.iter().find(|c| game.ingredient_zones.contains(*c));
            let cat_zone = children.iter().find(|c| game.catalyst_zones.contains(*c));
            let Some(zone) = zone else {
                fail(&mut ap, rid, &r.name, r.epoch.unwrap_or(0), "vessel has no ingredient zone");
                return;
            };
            // empty the vessel (last step's products stay in it otherwise)
            for (e, iv, ic) in &game.chips {
                if iv.is_some_and(|v| v.0 == vessel) || ic.is_some_and(|v| v.0 == vessel) {
                    commands.entity(e).despawn();
                }
            }
            let missing: Vec<String> = r
                .reactants
                .iter()
                .filter(|s| !game.progress.discovered.contains(&s.substance_id))
                .map(|s| subs.0.get(&s.substance_id).map(|x| x.name.clone()).unwrap_or_default())
                .collect();
            if !missing.is_empty() {
                let note = format!("not yet discovered: {}", missing.join(", "));
                fail(&mut ap, rid, &r.name, r.epoch.unwrap_or(0), &note);
                return;
            }
            let fonts = game.fonts.as_ref().unwrap();
            let ingredient = |id: u32, amount: u32| {
                subs.0.get(&id).map(|s| Ingredient {
                    id,
                    name: s.name.clone(),
                    formula: s.formula.clone(),
                    state: s.state,
                    properties: s.properties.clone(),
                    amount: amount.max(1),
                })
            };
            let reactants: Vec<Ingredient> =
                r.reactants.iter().filter_map(|s| ingredient(s.substance_id, s.moles)).collect();
            commands.entity(zone).with_children(|z| {
                for ing in &reactants {
                    spawn_vessel_chip(z, ing, ChipRole::Ingredient(vessel), fonts, &game.assets);
                }
            });
            if let Some(cat) = r.required_catalyst() {
                match (cat_zone, ingredient(cat, 1)) {
                    (Some(cz), Some(ing)) => {
                        commands.entity(cz).with_children(|z| {
                            spawn_vessel_chip(z, &ing, ChipRole::Catalyst(vessel), fonts, &game.assets);
                        });
                    }
                    _ => {
                        fail(
                            &mut ap,
                            rid,
                            &r.name,
                            r.epoch.unwrap_or(0),
                            "needs a catalyst but the vessel has no catalyst slot",
                        );
                        return;
                    }
                }
            }
            ap.phase = Phase::Fire;
            ap.wait = 1;
        }

        Phase::Fire => {
            if let Some(v) = ap.vessel {
                check.write(CheckVesselReaction(v));
            }
            ap.phase = Phase::Await;
        }

        Phase::Await => {
            ap.frames_in_step += 1;
            let rid = ap.steps[ap.idx];
            let r = game.db.as_ref().unwrap().authored.iter().find(|r| r.id == rid).cloned().unwrap();
            let epoch = r.epoch.unwrap_or(0);
            if let Some(reason) = ap.fizzle.take() {
                fail(&mut ap, rid, &r.name, epoch, &format!("fizzled: {reason}"));
                return;
            }
            if let Some(got) = ap.reacted {
                if got != rid {
                    let note = format!("ran reaction {got} instead");
                    fail(&mut ap, rid, &r.name, epoch, &note);
                    return;
                }
                let made = r.products.iter().all(|p| game.progress.discovered.contains(&p.substance_id));
                if made {
                    let frames = ap.frames_in_step;
                    let step = ap.idx;
                    ap.results.push(StepResult {
                        step,
                        reaction: rid,
                        name: r.name.clone(),
                        epoch,
                        ok: true,
                        note: String::new(),
                        frames,
                    });
                    ap.idx += 1;
                    let done = ap.idx;
                    if done.is_multiple_of(cfg.every) {
                        let unlocked: Vec<String> = game.unlocks.0.iter().map(|p| js(vessel_name(p))).collect();
                        let passed = ap.results.iter().filter(|x| x.ok).count();
                        let fps = done as f64 / (now - ap.started).max(0.001);
                        ap.emit(
                            now,
                            "checkpoint",
                            &[
                                ("passed", passed.to_string()),
                                ("discovered", game.progress.discovered.len().to_string()),
                                ("unlocked", format!("[{}]", unlocked.join(","))),
                                ("steps_per_second", format!("{:.2}", fps)),
                            ],
                        );
                        if ap.pending_shot.is_none() {
                            ap.pending_shot = Some(format!("step_{:04}", done));
                        }
                    }
                    ap.phase = Phase::Prepare;
                    ap.wait = 2; // milestones fire on the frame after a discovery
                    if let Some(label) = ap.pending_shot.take() {
                        ap.wait = 0;
                        ap.phase = Phase::Shot;
                        ap.shot_after = Some(Phase::Prepare);
                        // the shot is taken once the milestone toast and the new
                        // inventory have had a moment to appear
                        ap.pending_shot = Some(label);
                        ap.wait = 20;
                    }
                    return;
                }
            }
            if ap.frames_in_step > 900 {
                fail(&mut ap, rid, &r.name, epoch, "timed out waiting for the products");
            }
        }

        Phase::Shot => {
            if let Some(label) = ap.pending_shot.take() {
                let then = ap.shot_after.take().unwrap_or(Phase::Prepare);
                // milestones carry their screenshot in the report
                if label.starts_with("milestone_") {
                    if let Some(m) = ap.milestones.iter_mut().rev().find(|m| m.3.is_none()) {
                        m.3 = Some(format!("{label}.png"));
                    }
                }
                take_shot(&mut commands, &cfg, &mut ap, label, then, now);
                ap.wait = 6;
            } else {
                let then = ap.shot_after.take().unwrap_or(Phase::Prepare);
                ap.phase = then;
            }
        }

        Phase::Tour => {
            if ap.tour_i >= TOUR.len() {
                views.close_all();
                ap.phase = if ap.tour_label == "end" { Phase::Finish } else { Phase::Prepare };
                ap.wait = 10;
                return;
            }
            let view = TOUR[ap.tour_i];
            let db = game.db.as_ref().unwrap();
            let subs = game.game_data.as_ref().and_then(|g| game.substances.get(&g.substances));
            views.close_all();
            match view {
                TourView::Lab => {}
                TourView::TreeGraph | TourView::TreeList => {
                    views.tree.open = true;
                    views.tree.mode = if view == TourView::TreeGraph { TechMode::Graph } else { TechMode::List };
                    // select the step just done, so the detail bar is populated
                    views.tree.selected =
                        ap.results.iter().rev().find(|x| x.ok).map(|x| x.reaction).or(ap.steps.first().copied());
                }
                TourView::SubstanceCompound | TourView::SubstanceElement => {
                    views.codex.open = true;
                    let want_element = view == TourView::SubstanceElement;
                    // the most recently discovered compound, or a well-known element
                    let pick = if want_element {
                        [1026u32, 1029, 1050, 1079, 1047].into_iter().find(|id| game.progress.discovered.contains(id))
                    } else {
                        ap.results
                            .iter()
                            .rev()
                            .filter(|x| x.ok)
                            .filter_map(|x| db.authored.iter().find(|r| r.id == x.reaction))
                            .flat_map(|r| r.products.iter().map(|p| p.substance_id))
                            .find(|id| {
                                subs.and_then(|s| s.0.get(id))
                                    .is_some_and(|s| s.element_info.is_none() && s.description.is_some())
                            })
                    };
                    views.codex.selected = pick;
                }
                TourView::Reactions => {
                    views.rlib.open = true;
                    views.rlib.selected = ap.results.iter().rev().find(|x| x.ok).map(|x| x.reaction);
                }
                TourView::Settings => {
                    views.settings_ui.open = true;
                }
            }
            let name = match view {
                TourView::Lab => "lab",
                TourView::TreeGraph => "tech_tree_graph",
                TourView::TreeList => "tech_tree_list",
                TourView::SubstanceCompound => "substances_compound",
                TourView::SubstanceElement => "substances_element",
                TourView::Reactions => "reactions",
                TourView::Settings => "settings",
            };
            let n = if ap.tour_label == "end" { 90 } else { 10 };
            ap.tour_i += 1;
            ap.pending_shot = Some(format!("{}_{}_{}", n + ap.tour_i, ap.tour_label, name));
            ap.shot_after = Some(Phase::Tour);
            ap.phase = Phase::Shot;
            ap.wait = 30; // views rebuild and their images load
        }

        Phase::Finish => {
            write_report(&cfg, &mut ap, &game, &checks, now);
            let failed = ap.results.iter().filter(|r| !r.ok).count();
            let checks_failed = checks.results.iter().filter(|r| !r.ok).count();
            for r in checks.results.iter().filter(|r| !r.ok) {
                println!("CHECK FAILED: {} / {}: {}", r.area, r.name, r.note);
            }
            println!(
                "AUTOPLAY DONE: checks {} of {} passed; steps {} of {} passed, {} failed; {} discoveries, {} screenshots -> {}",
                checks.results.len() - checks_failed,
                checks.results.len(),
                ap.results.len() - failed,
                ap.results.len(),
                failed,
                game.progress.discovered.len(),
                ap.shots.len(),
                cfg.out_dir.display()
            );
            ap.phase = Phase::Done;
            ap.wait = 30; // let the last screenshots finish writing
        }

        Phase::Done => {
            let failed = ap.results.iter().any(|r| !r.ok) || checks.results.iter().any(|r| !r.ok);
            exit.write(if failed { AppExit::from_code(1) } else { AppExit::Success });
        }
    }
}

fn fail(ap: &mut Autoplay, rid: u32, name: &str, epoch: u8, note: &str) {
    let step = ap.idx;
    let frames = ap.frames_in_step;
    warn!("Autoplay step {} ({} {}) failed: {}", step, rid, name, note);
    ap.results.push(StepResult {
        step,
        reaction: rid,
        name: name.to_string(),
        epoch,
        ok: false,
        note: note.to_string(),
        frames,
    });
    ap.idx += 1;
    ap.phase = Phase::Prepare;
    ap.wait = 1;
}

fn take_shot(commands: &mut Commands, cfg: &AutoplayConfig, ap: &mut Autoplay, label: String, then: Phase, now: f64) {
    let file = format!("{label}.png");
    let path = cfg.out_dir.join("shots").join(&file);
    commands.spawn(Screenshot::primary_window()).observe(save_to_disk(path));
    ap.emit(now, "screenshot", &[("file", js(&format!("shots/{file}")))]);
    ap.shots.push((label, file));
    ap.phase = Phase::Shot;
    ap.shot_after = Some(then);
}

fn write_report(cfg: &AutoplayConfig, ap: &mut Autoplay, game: &Game, checks: &InputChecks, now: f64) {
    if let Some(log) = ap.log.as_mut() {
        let _ = log.flush();
    }
    let Some(db) = game.db.as_ref() else { return };
    let subs = game.game_data.as_ref().and_then(|g| game.substances.get(&g.substances));
    let name = |id: u32| subs.and_then(|s| s.0.get(&id)).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    let passed = ap.results.iter().filter(|r| r.ok).count();
    let failed: Vec<&StepResult> = ap.results.iter().filter(|r| !r.ok).collect();
    let canon_found = db.canon.iter().filter(|id| game.progress.discovered.contains(*id)).count();
    let mut unlocked: Vec<&'static str> = game.unlocks.0.iter().map(vessel_name).collect();
    unlocked.sort();
    let secs = now - ap.started;

    // --- report.md ---
    let mut md = String::new();
    md.push_str(&format!("# Curieosity review run\n\n`{}`\n\n", cfg.out_dir.display()));
    let checks_ok = checks.results.iter().filter(|r| r.ok).count();
    md.push_str(&format!(
        "| | |\n|---|---|\n| Interaction checks passed | **{} / {}** |\n| Steps passed | **{} / {}** |\n| Failed | {} |\n| Fizzles seen | {} |\n| Never reachable (content) | {} |\n| Discovered | {} of {} substances in play |\n| Vessels unlocked | {} of {}: {} |\n| Milestones fired | {} of {} |\n| Time | {:.0} s ({:.1} steps/s) |\n\n",
        checks_ok,
        checks.results.len(),
        passed,
        ap.results.len(),
        failed.len(),
        ap.fizzles,
        ap.unreachable.len(),
        canon_found,
        db.canon.len(),
        unlocked.len(),
        VESSELS.len(),
        unlocked.join(", "),
        ap.milestones.len(),
        db.milestones.len(),
        secs,
        ap.results.len() as f64 / secs.max(0.001),
    ));
    md.push_str("## Interaction checks\n\n| | Area | Check | What happened |\n|---|---|---|---|\n");
    for r in &checks.results {
        let mark = if r.ok { "pass" } else { "**FAIL**" };
        let note = match (&r.shot, r.ok) {
            (Some(s), false) => format!("{} ([screenshot]({}))", r.note.replace('|', "/"), s),
            _ => r.note.replace('|', "/"),
        };
        md.push_str(&format!("| {} | {} | {} | {} |\n", mark, r.area, r.name, note));
    }
    md.push_str("\nNot exercised: the fullscreen switch (it would take over the screen) and the Wikipedia buttons' browser launch (the link is checked instead).\n\n");
    if !checks.shots.is_empty() {
        md.push_str("### Screens to look over\n\n");
        for (label, file) in &checks.shots {
            md.push_str(&format!("**{}**\n\n![{}](shots/{})\n\n", label, label, file));
        }
    }
    if !failed.is_empty() {
        md.push_str("## Failures\n\n| Step | Reaction | Era | What happened |\n|---|---|---|---|\n");
        for f in &failed {
            md.push_str(&format!(
                "| {} | {} ({}) | {} | {} |\n",
                f.step,
                f.name,
                f.reaction,
                db.epoch_name(f.epoch),
                f.note.replace('|', "/")
            ));
        }
        md.push('\n');
    }
    if !ap.unreachable.is_empty() {
        md.push_str("## Reactions no player can reach\n\n");
        for id in &ap.unreachable {
            let n = db.authored.iter().find(|r| r.id == *id).map(|r| r.name.clone()).unwrap_or_default();
            md.push_str(&format!("- {} ({})\n", n, id));
        }
        md.push('\n');
    }
    // --- pacing: the planner's ladder, checked against the limits the content tests use ---
    let pt = db.playthrough();
    let gaps = db.milestone_gaps(&pt);
    let worst_gap = gaps.iter().map(|g| g.2).max().unwrap_or(0);
    let worst_grant = db.milestones.iter().map(|m| m.grant.len()).max().unwrap_or(0);
    let flag = |bad: bool| if bad { " **over the limit**" } else { "" };
    md.push_str(&format!(
        "## Pacing\n\n{} milestones over {} era steps (the Laboratory's {} side recipes not counted).\n\n| | Worst | Limit |\n|---|---|---|\n| Era steps between milestones | {}{} | {} |\n| Materials in one grant | {}{} | {} |\n\n",
        db.milestones.len(),
        pt.era_steps,
        pt.steps.len() - pt.era_steps,
        worst_gap,
        flag(worst_gap > MAX_MILESTONE_GAP),
        MAX_MILESTONE_GAP,
        worst_grant,
        flag(worst_grant > MAX_GRANT),
        MAX_GRANT,
    ));
    md.push_str("| Vessel | Unlocked at step | Recipes |\n|---|---|---|\n");
    let mut by_step: Vec<_> = VESSELS.iter().map(|v| (pt.unlocked_at.get(&v.process).copied(), v)).collect();
    by_step.sort_by_key(|(s, _)| s.unwrap_or(usize::MAX));
    for (at, v) in by_step {
        let n = db.authored.iter().filter(|r| r.process == v.process).count();
        let at = at.map(|a| a.to_string()).unwrap_or_else(|| "never".into());
        md.push_str(&format!(
            "| {} ({} {}) | {} | {} |\n",
            v.name,
            v.category,
            crate::ui::process_toolbar::roman(v.tier),
            at,
            n
        ));
    }
    md.push('\n');
    md.push_str("## Milestones\n\n| # | On | Unlocks | At step | Screenshot |\n|---|---|---|---|---|\n");
    for (i, on, step, shot) in &ap.milestones {
        let m = &db.milestones[*i];
        let what: Vec<String> = m
            .unlock
            .iter()
            .map(|p| vessel_name(p).to_string())
            .chain(m.grant.iter().map(|g| format!("+{}", name(*g))))
            .collect();
        let link = shot.as_ref().map(|s| format!("[view](shots/{s})")).unwrap_or_default();
        md.push_str(&format!("| {} | {} | {} | {} | {} |\n", i, name(*on), what.join(", "), step, link));
    }
    md.push_str("\n## Eras\n\n| Era | Steps | Passed | Avg frames per step |\n|---|---|---|---|\n");
    let mut by_era: HashMap<u8, (usize, usize, u64)> = HashMap::new();
    for r in &ap.results {
        let e = by_era.entry(r.epoch).or_default();
        e.0 += 1;
        e.1 += r.ok as usize;
        e.2 += r.frames as u64;
    }
    let mut eras: Vec<_> = by_era.into_iter().collect();
    eras.sort_by_key(|(e, _)| *e);
    for (e, (n, ok, frames)) in eras {
        md.push_str(&format!("| {} | {} | {} | {:.1} |\n", db.epoch_name(e), n, ok, frames as f64 / n.max(1) as f64));
    }
    if !ap.eras.is_empty() {
        md.push_str("\n## Era banners\n\n| Era | At step |\n|---|---|\n");
        for (e, step) in &ap.eras {
            md.push_str(&format!("| {} | {} |\n", db.epoch_name(*e), step));
        }
    }
    // --- frame times while playing (the scripted run, so treat as relative numbers) ---
    if !ap.frame_ms.is_empty() {
        let mut f = ap.frame_ms.clone();
        f.sort_by(|a, b| a.total_cmp(b));
        let pct = |p: f32| f[((f.len() - 1) as f32 * p).round() as usize];
        let mean = f.iter().sum::<f32>() / f.len() as f32;
        let slow = f.iter().filter(|x| **x > 33.4).count();
        md.push_str(&format!(
            "\n## Frame time\n\n{} frames. Mean {:.1} ms, median {:.1}, 95th percentile {:.1}, 99th {:.1}, worst {:.1}; {} frames ({:.1}%) slower than 30 fps.\n",
            f.len(), mean, pct(0.5), pct(0.95), pct(0.99), f[f.len() - 1], slow, 100.0 * slow as f32 / f.len() as f32
        ));
    }
    md.push_str("\n## Screenshots\n\n");
    for (label, file) in &ap.shots {
        md.push_str(&format!("### {}\n\n![{}](shots/{})\n\n", label, label, file));
    }
    let _ = std::fs::write(cfg.out_dir.join("report.md"), md);

    // --- state.json ---
    let mut discovered: Vec<u32> = game.progress.discovered.iter().copied().collect();
    discovered.sort_unstable();
    let failures: Vec<String> = failed
        .iter()
        .map(|f| {
            format!(
                "{{\"step\":{},\"reaction\":{},\"name\":{},\"note\":{}}}",
                f.step,
                f.reaction,
                js(&f.name),
                js(&f.note)
            )
        })
        .collect();
    let milestones: Vec<String> = ap
        .milestones
        .iter()
        .map(|(i, on, step, _)| format!("{{\"index\":{},\"on\":{},\"step\":{}}}", i, on, step))
        .collect();
    let check_fails: Vec<String> = checks
        .results
        .iter()
        .filter(|r| !r.ok)
        .map(|r| format!("{{\"area\":{},\"check\":{},\"note\":{}}}", js(r.area), js(r.name), js(&r.note)))
        .collect();
    let json = format!(
        "{{\n  \"checks\": {},\n  \"checks_passed\": {},\n  \"checks_failed\": [{}],\n  \"steps\": {},\n  \"passed\": {},\n  \"failed\": [{}],\n  \"fizzles\": {},\n  \"unreachable\": {},\n  \"discovered_count\": {},\n  \"canon_found\": {},\n  \"canon_total\": {},\n  \"unlocked\": [{}],\n  \"milestones\": [{}],\n  \"seconds\": {:.1},\n  \"discovered\": {}\n}}\n",
        checks.results.len(),
        checks_ok,
        check_fails.join(","),
        ap.results.len(),
        passed,
        failures.join(","),
        ap.fizzles,
        ja(&ap.unreachable),
        discovered.len(),
        canon_found,
        db.canon.len(),
        unlocked.iter().map(|u| js(u)).collect::<Vec<_>>().join(","),
        milestones.join(","),
        secs,
        ja(&discovered),
    );
    let _ = std::fs::write(cfg.out_dir.join("state.json"), json);
}
