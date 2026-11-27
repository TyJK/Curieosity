// src/ui/challenges.rs
//
// Challenges: the scored, targeted-synthesis mode (the rules and the challenges themselves
// are in resources::challenge). The free lab is never scored.
//
// The board (from the main menu, or the target button in the header) lists the challenges
// era by era with the stars earned, and the day's challenge with its streak. Starting one
// sets the lab aside: its vessels are hidden where they stand, its discoveries, vessels and
// notifications are kept, and the bench, the shelf and the vessel picker become the
// challenge's (its kit, and the vessels its route needs, with a couple more to choose
// from). Nothing a challenge does is saved to the lab, fires a milestone or earns an
// achievement. Leaving (Give up, or after the finish) brings the lab back as it was.
//
// While it is played a bar on the bench shows the target, the route's steps with what each
// is still worth, and the score; the Hint card helps with the step in hand, at a cost. The
// finish card gives the stars, the score, the best and the next challenge.
use bevy::prelude::*;

use crate::components::ui_markers::{CanvasScrollingPane, Stashed};
use crate::components::{ReactionLink, VesselCard};
use crate::data::common::ProcessType;
use crate::data::substances::Substances;
use crate::resources::challenge::{
    all_challenges, daily, era_open, load_records, save_records, today, Challenge, ChallengeRecords, HintTaken, Run,
    CLEAN_BONUS, FAIL_COST, HINT_COST, STEP_FLOOR, STEP_POINTS,
};
use crate::resources::player_progress::{current_save, Persistence, PlayerProgress, SaveData};
use crate::resources::recipe_database::RecipeDatabase;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::autoplay::GameEvent;
use crate::systems::drag_drop::{pan_bench, pane_offset, ActiveVessel, BenchZoom};
use crate::ui::detail_panel::SelectedSubstance;
use crate::ui::hint::{choose, HintState, Target};
use crate::ui::process_toolbar::ProcessUnlocks;
use crate::ui::settings::Settings;
use crate::ui::theme::{self, Kind, Weight};
use crate::ui::toasts::Journal;
use crate::ui::{Button, Clicked};
use crate::GameData;

/// The mode: the challenges, their records, the board, and the run being played (with the
/// lab it set aside).
#[derive(Resource, Default)]
pub struct ChallengeMode {
    pub challenges: Vec<Challenge>,
    pub records: ChallengeRecords,
    pub board_open: bool,
    /// the finish card is showing
    pub card: bool,
    /// the finished run beat its best
    pub new_best: bool,
    run: Option<Run>,
    saved: Option<SetAside>,
    /// the lab's era when the board was last shown (eras it has reached are open)
    pub lab_era: u8,
}

/// The lab, while a challenge is played.
struct SetAside {
    save: SaveData,
    pane: Vec2,
    zoom: f32,
    /// the lab's Hint target, its hint level and whether its card was folded: it is the
    /// player's until made or let go, so it comes back with the lab
    hint: Option<(Target, u8, bool)>,
}

impl ChallengeMode {
    pub fn playing(&self) -> bool {
        self.run.is_some()
    }

    pub fn run(&self) -> Option<&Run> {
        self.run.as_ref()
    }

    /// The lab's progress while a challenge is played (what a save written now must hold).
    pub fn set_aside(&self) -> Option<&SaveData> {
        self.saved.as_ref().map(|s| &s.save)
    }

    /// Drop the run without the flow (the review's checks start each check afresh): the lab
    /// it set aside, for the caller to put back.
    pub fn abandon(&mut self) -> Option<SaveData> {
        self.run = None;
        self.card = false;
        self.board_open = false;
        self.saved.take().map(|s| s.save)
    }

    pub fn get(&self, id: u32) -> Option<&Challenge> {
        self.challenges.iter().find(|c| c.id == id)
    }

    fn first_era(&self) -> u8 {
        self.challenges.first().map_or(0, |c| c.era)
    }

    pub fn open(&self, c: &Challenge) -> bool {
        era_open(c.era, &self.challenges, &self.records, self.lab_era, self.first_era())
    }

    /// Today's challenge.
    pub fn daily(&self, day: i64) -> Option<&Challenge> {
        let open: Vec<&Challenge> = self.challenges.iter().filter(|c| self.open(c)).collect();
        daily(&open, day)
    }

    /// The next challenge after `id` that is open.
    pub fn next_after(&self, id: u32) -> Option<&Challenge> {
        let i = self.challenges.iter().position(|c| c.id == id)?;
        self.challenges[i + 1..].iter().find(|c| self.open(c))
    }

    pub fn total_stars(&self) -> (u32, u32) {
        let got = self.challenges.iter().map(|c| self.records.stars(c.id) as u32).sum();
        (got, self.challenges.len() as u32 * 3)
    }
}

/// What to do: start a challenge (as the day's or not), leave the one being played.
#[derive(Message, Clone, Copy, Debug)]
pub enum ChallengeAsk {
    Start { id: u32, daily: bool },
    Leave,
}

// --- the UI's parts ---
#[derive(Component)]
pub struct BoardRoot;
#[derive(Component)]
pub struct BoardContent;
#[derive(Component)]
pub struct BoardClose;
/// A challenge on the board (or its daily card): starts it.
#[derive(Component)]
pub struct ChallengeCard {
    pub id: u32,
    pub daily: bool,
}
/// Opens the board (the header's button, the main menu's).
#[derive(Component)]
pub struct OpenBoard;
#[derive(Component)]
pub struct HudRoot;
#[derive(Component)]
pub struct HudGiveUp;
#[derive(Component)]
pub struct FinishRoot;
#[derive(Component)]
pub struct FinishContent;
#[derive(Component)]
pub enum FinishButton {
    Next(u32),
    Again(u32),
    Board,
    Lab,
}

pub struct ChallengesPlugin;

impl Plugin for ChallengesPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<ChallengeMode>().add_message::<ChallengeAsk>().add_message::<HintTaken>().add_systems(
            Update,
            (
                setup_challenges_system,
                challenge_input_system,
                challenge_flow_system,
                challenge_score_system.after(crate::systems::discovery::discovery_system),
                board_view_system,
                hud_view_system,
                finish_view_system,
            )
                .chain(),
        );
    }
}

/// Once the content is in: the challenges, and the records from disk.
fn setup_challenges_system(
    db: Option<Res<RecipeDatabase>>,
    persistence: Res<Persistence>,
    mut mode: ResMut<ChallengeMode>,
    mut done: Local<bool>,
) {
    if *done {
        return;
    }
    let Some(db) = db else { return };
    *done = true;
    mode.challenges = all_challenges(&db);
    if persistence.0 {
        mode.records = load_records();
    }
    info!("{} challenges.", mode.challenges.len());
}

// ---------------------------------------------------------------------------------------
// Input
// ---------------------------------------------------------------------------------------
#[allow(clippy::type_complexity)]
fn challenge_input_system(
    mut mode: ResMut<ChallengeMode>,
    mut asks: MessageWriter<ChallengeAsk>,
    open_board: Query<(), (With<Clicked>, With<OpenBoard>)>,
    close: Query<(), (With<Clicked>, With<BoardClose>)>,
    cards: Query<&ChallengeCard, (With<Clicked>, With<Button>)>,
    give_up: Query<(), (With<Clicked>, With<HudGiveUp>)>,
    finish: Query<&FinishButton, (With<Clicked>, With<Button>)>,
    mut menu: ResMut<crate::ui::main_menu::MainMenu>,
    current_era: Res<crate::ui::onboarding::CurrentEra>,
) {
    if !open_board.is_empty() {
        menu.hide();
        if !mode.playing() {
            mode.lab_era = current_era.index;
        }
        mode.board_open = true;
    }
    if !close.is_empty() {
        mode.board_open = false;
    }
    for c in &cards {
        asks.write(ChallengeAsk::Start { id: c.id, daily: c.daily });
    }
    if !give_up.is_empty() {
        asks.write(ChallengeAsk::Leave);
    }
    for b in &finish {
        mode.card = false;
        match b {
            FinishButton::Next(id) | FinishButton::Again(id) => {
                asks.write(ChallengeAsk::Start { id: *id, daily: false });
            }
            FinishButton::Board => {
                asks.write(ChallengeAsk::Leave);
                mode.board_open = true;
            }
            FinishButton::Lab => {
                asks.write(ChallengeAsk::Leave);
            }
        }
    }
}

// ---------------------------------------------------------------------------------------
// Starting and leaving
// ---------------------------------------------------------------------------------------
/// The lab's state the flow swaps.
type LabState<'a> = (
    ResMut<'a, PlayerProgress>,
    ResMut<'a, ProcessUnlocks>,
    ResMut<'a, Journal>,
    ResMut<'a, HintState>,
    ResMut<'a, SelectedSubstance>,
    ResMut<'a, ActiveVessel>,
    ResMut<'a, BenchZoom>,
);

/// The views a challenge closes.
type Views<'a> = (
    ResMut<'a, crate::ui::codex::CodexState>,
    ResMut<'a, crate::ui::reaction_library::ReactionLibState>,
    ResMut<'a, crate::ui::tech_tree::TechTreeState>,
    ResMut<'a, crate::ui::curriculum::CurriculumState>,
    ResMut<'a, crate::ui::settings::SettingsUi>,
);

#[allow(clippy::too_many_arguments, clippy::type_complexity)]
fn challenge_flow_system(
    mut commands: Commands,
    mut asks: MessageReader<ChallengeAsk>,
    mut mode: ResMut<ChallengeMode>,
    db: Option<Res<RecipeDatabase>>,
    lab: LabState,
    views: Views,
    settings: Res<Settings>,
    mut cards: Query<(Entity, &mut Node, Has<Stashed>), With<VesselCard>>,
    links: Query<(Entity, &ReactionLink)>,
    mut pane: Query<&mut Node, (With<CanvasScrollingPane>, Without<VesselCard>)>,
    bench: Query<&ComputedNode, With<crate::components::ui_markers::ReactionCanvasRoot>>,
) {
    let (mut progress, mut unlocks, mut journal, mut hint, mut selected, mut active, mut zoom) = lab;
    let (mut codex, mut rlib, mut tree, mut learn, mut settings_ui) = views;
    let asks: Vec<ChallengeAsk> = asks.read().copied().collect();
    if asks.is_empty() {
        return;
    }
    if db.is_none() {
        return;
    }
    for ask in asks {
        // whatever happens, the bench the run left goes, and the lab comes back
        if mode.playing() {
            let stashed: Vec<Entity> = cards.iter().filter(|(_, _, s)| *s).map(|(e, _, _)| e).collect();
            for (e, _, s) in &cards {
                if !s {
                    commands.entity(e).despawn();
                }
            }
            for (e, l) in &links {
                if !stashed.contains(&l.from_vessel) || !stashed.contains(&l.to_vessel) {
                    commands.entity(e).despawn();
                }
            }
            if let Some(saved) = mode.saved.as_ref() {
                restore(&saved.save, &mut progress, &mut unlocks, &mut journal);
                zoom.0 = saved.zoom;
                if let Ok(mut p) = pane.single_mut() {
                    let view = bench.iter().next().map(|c| c.size * c.inverse_scale_factor()).unwrap_or(Vec2::ONE);
                    pan_bench(&mut p, view, saved.pane, saved.zoom);
                }
            }
            for (e, mut n, s) in &mut cards {
                if s {
                    n.display = Display::Flex;
                    commands.entity(e).remove::<Stashed>();
                }
            }
            mode.run = None;
            hint.stop();
            hint.challenge_step = None;
            // the lab's own target, as it was left
            if let (Some((t, level, folded)), Some(db)) = (mode.saved.as_ref().and_then(|s| s.hint), db.as_ref()) {
                choose(&mut hint, t, db, &progress, &unlocks, settings.decoy_range());
                hint.level = level;
                hint.collapsed = folded;
            }
            mode.saved = None;
            selected.0 = None;
            active.0 = None;
        }
        let ChallengeAsk::Start { id, daily } = ask else { continue };
        let Some(c) = mode.get(id).cloned() else { continue };
        // the lab, set aside
        let pane_at = pane.single().map(pane_offset).unwrap_or(Vec2::ZERO);
        let lab_target = hint.target.filter(|_| hint.challenge_step.is_none()).map(|t| (t, hint.level, hint.collapsed));
        mode.saved = Some(SetAside {
            save: current_save(&progress, &unlocks, &journal),
            pane: pane_at,
            zoom: zoom.0,
            hint: lab_target,
        });
        for (e, mut n, _) in &mut cards {
            n.display = Display::None;
            commands.entity(e).insert(Stashed);
        }
        // the challenge's shelf and vessels: the route's, and a couple more to choose from
        progress.discovered = c.kit.iter().chain(c.decoys.iter()).copied().collect();
        progress.order.clear();
        progress.goals.clear();
        let mut vessels: Vec<ProcessType> = c.vessels.clone();
        for extra in [ProcessType::Mix, ProcessType::Heat] {
            if !vessels.contains(&extra) {
                vessels.push(extra);
            }
        }
        unlocks.0 = vessels.into_iter().collect();
        zoom.0 = 1.0;
        if let Ok(mut p) = pane.single_mut() {
            let view = bench.iter().next().map(|c| c.size * c.inverse_scale_factor()).unwrap_or(Vec2::ONE);
            pan_bench(&mut p, view, Vec2::ZERO, 1.0);
        }
        hint.stop();
        hint.challenge_step = Some(Target { product: c.step_products[0], reaction: c.steps[0] });
        selected.0 = None;
        active.0 = None;
        mode.run = Some(Run::new(c, daily));
        mode.board_open = false;
        mode.card = false;
        codex.open = false;
        rlib.open = false;
        tree.open = false;
        learn.open = false;
        settings_ui.open = false;
    }
}

/// Put the lab's progress back.
pub fn restore(save: &SaveData, progress: &mut PlayerProgress, unlocks: &mut ProcessUnlocks, journal: &mut Journal) {
    progress.discovered = save.discovered.iter().copied().collect();
    progress.order = save.order.clone();
    progress.goals = save.goals.clone();
    progress.dormant = save.dormant.clone();
    progress.dormant_vessels = save.dormant_vessels.clone();
    unlocks.0 = save.unlocked.iter().cloned().collect();
    *journal = Journal::from_pairs(&save.journal);
}

// ---------------------------------------------------------------------------------------
// Scoring
// ---------------------------------------------------------------------------------------
/// Discoveries finish steps; reactions that don't go and hints cost the step in hand. The
/// Hint card follows the step in hand. At the finish, the records.
#[allow(clippy::too_many_arguments)]
fn challenge_score_system(
    mut mode: ResMut<ChallengeMode>,
    mut events: MessageReader<GameEvent>,
    mut hints: MessageReader<HintTaken>,
    mut hint: ResMut<HintState>,
    db: Option<Res<RecipeDatabase>>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    settings: Res<Settings>,
    persistence: Res<Persistence>,
) {
    if !mode.playing() {
        events.clear();
        hints.clear();
        return;
    }
    let before = mode.run.as_ref().and_then(|r| r.current());
    let mut finished = false;
    {
        let Some(run) = mode.run.as_mut() else { return };
        for ev in events.read() {
            match ev {
                GameEvent::Discovery { id } => finished |= run.found(*id),
                GameEvent::Fizzle { .. } => run.fail(),
                _ => {}
            }
        }
        for _ in hints.read() {
            run.hint();
        }
    }
    let run = mode.run.clone().expect("playing");
    let now = run.current();
    if now != before || finished {
        // (finished, the last step stays the card's subject, so Hint stays the challenge's)
        let i = now.unwrap_or(run.challenge.steps.len() - 1);
        hint.challenge_step =
            Some(Target { product: run.challenge.step_products[i], reaction: run.challenge.steps[i] });
        // the card, if open, moves on to the next step
        match (hint.target.is_some() && !finished, hint.challenge_step, db.as_ref()) {
            (true, Some(t), Some(db)) => {
                let folded = hint.collapsed;
                choose(&mut hint, t, db, &progress, &unlocks, settings.decoy_range());
                hint.collapsed = folded;
            }
            _ => hint.stop(),
        }
    }
    if finished {
        let day = today();
        let better = mode.records.finish(&run, day);
        mode.new_best = better;
        mode.card = true;
        if persistence.0 {
            save_records(&mode.records);
        }
    }
}

// ---------------------------------------------------------------------------------------
// The board
// ---------------------------------------------------------------------------------------
pub fn spawn_challenge_ui(mut commands: Commands, fonts: Res<UiFonts>, assets: Res<AssetServer>) {
    let fonts = &*fonts;
    let assets = &*assets;
    // the board: a view of its own
    commands
        .spawn((BoardRoot, crate::ui::focus::FocusCover, theme::view_root(640), Name::new("ChallengeBoard")))
        .insert(Node {
            position_type: PositionType::Absolute,
            left: Val::Px(0.0),
            right: Val::Px(0.0),
            top: Val::Px(theme::HEADER_H),
            bottom: Val::Px(0.0),
            flex_direction: FlexDirection::Column,
            display: Display::None,
            ..default()
        })
        .with_children(|root| {
            root.spawn((
                crate::ui::shell::PanePad(28.0, 14.0, 0.0),
                Node {
                    width: Val::Percent(100.0),
                    height: Val::Percent(100.0),
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(10.0),
                    ..default()
                },
                BackgroundColor(theme::SURFACE),
            ))
            .with_children(|col| {
                col.spawn(Node {
                    justify_content: JustifyContent::SpaceBetween,
                    align_items: AlignItems::Center,
                    flex_shrink: 0.0,
                    ..default()
                })
                .with_children(|hdr| {
                    hdr.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Center, ..default() })
                        .with_children(|t| {
                            t.spawn(theme::icon(assets, "target", 24.0, theme::GOLD));
                            t.spawn(theme::label(fonts, "Challenges", theme::XL, Weight::Semibold, theme::TEXT));
                        });
                    theme::spawn_icon_button(hdr, assets, "close", 40.0, theme::TEXT_2, BoardClose);
                });
                col.spawn((
                    ScrollPosition::default(),
                    Node {
                        flex_direction: FlexDirection::Column,
                        align_items: AlignItems::Center,
                        flex_grow: 1.0,
                        flex_basis: Val::Px(0.0),
                        min_height: Val::Px(0.0),
                        overflow: Overflow::scroll_y(),
                        padding: UiRect::bottom(Val::Px(24.0)),
                        ..default()
                    },
                ))
                .with_children(|scroll| {
                    scroll.spawn((
                        BoardContent,
                        crate::ui::focus::FocusGroup,
                        Node {
                            width: Val::Percent(100.0),
                            max_width: Val::Px(1180.0),
                            flex_shrink: 0.0,
                            flex_direction: FlexDirection::Column,
                            row_gap: Val::Px(12.0),
                            ..default()
                        },
                    ));
                });
            });
        });
    // the bar on the bench while a challenge is played
    commands.spawn((
        HudRoot,
        // over the bench and its controls, under every view
        GlobalZIndex(560),
        Pickable::default(),
        Node {
            position_type: PositionType::Absolute,
            top: Val::Px(theme::HEADER_H + 8.0),
            left: Val::Px(10.0),
            right: Val::Px(10.0),
            display: Display::None,
            justify_content: JustifyContent::Center,
            ..default()
        },
        Name::new("ChallengeBar"),
    ));
    // the finish card
    commands
        .spawn((
            FinishRoot,
            GlobalZIndex(920),
            Node {
                position_type: PositionType::Absolute,
                left: Val::Px(0.0),
                right: Val::Px(0.0),
                top: Val::Px(0.0),
                bottom: Val::Px(0.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                display: Display::None,
                ..default()
            },
            BackgroundColor(Color::srgba(0.0, 0.0, 0.02, 0.6)),
            Pickable::default(),
            Name::new("ChallengeFinish"),
        ))
        .with_children(|r| {
            r.spawn((
                FinishContent,
                Node {
                    width: Val::Px(460.0),
                    max_width: Val::Percent(94.0),
                    max_height: Val::Percent(92.0),
                    flex_direction: FlexDirection::Column,
                    align_items: AlignItems::Center,
                    row_gap: Val::Px(10.0),
                    padding: UiRect::all(Val::Px(24.0)),
                    border: UiRect::all(Val::Px(1.5)),
                    border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    overflow: Overflow::scroll_y(),
                    ..default()
                },
                ScrollPosition::default(),
                BackgroundColor(theme::SURFACE),
                BorderColor::all(theme::GOLD.with_alpha(0.8)),
                theme::shadow(40.0, 14.0, 0.6),
            ));
        });
}

/// The header's button: the board.
pub fn spawn_board_button(parent: &mut ChildSpawnerCommands, assets: &AssetServer) {
    theme::spawn_icon_button(
        parent,
        assets,
        "target",
        36.0,
        theme::GOLD,
        (
            OpenBoard,
            crate::ui::onboarding::Tip::Text(
                "Challenges",
                "Make a target by its route from a kit of its own, for stars and a score. Your lab waits as you left it.",
            ),
        ),
    );
}

/// Stars as text: filled for those earned, hollow for the rest, out of three.
fn stars(n: u8) -> String {
    (0..3).map(|i| if i < n { '\u{2605}' } else { '\u{2606}' }).collect()
}

fn star_label(fonts: &UiFonts, n: u8, size: f32) -> impl Bundle {
    (
        Text::new(stars(n)),
        TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(size), ..default() },
        TextColor(if n > 0 { theme::GOLD } else { theme::TEXT_3 }),
        Pickable::IGNORE,
    )
}

#[allow(clippy::too_many_arguments)]
fn board_view_system(
    mut commands: Commands,
    mode: Res<ChallengeMode>,
    db: Option<Res<RecipeDatabase>>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    look: (Res<UiFonts>, Res<AssetServer>),
    mut root: Query<&mut Node, With<BoardRoot>>,
    content: Query<Entity, With<BoardContent>>,
    mut built: Local<bool>,
) {
    let (fonts, assets) = look;
    if let Ok(mut n) = root.single_mut() {
        let d = if mode.board_open { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if !mode.board_open {
        *built = false;
        return;
    }
    if *built && !mode.is_changed() {
        return;
    }
    let (Some(db), Ok(content)) = (db, content.single()) else { return };
    let Some(subs) = game_data.as_ref().and_then(|g| substances.get(&g.substances)) else { return };
    *built = true;
    let name = |id: u32| subs.0.get(&id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    let formula = |id: u32| subs.0.get(&id).map(|s| crate::components::format_formula(&s.formula)).unwrap_or_default();
    let day = today();
    commands.entity(content).despawn_children();
    commands.entity(content).with_children(|p| {
        let (got, of) = mode.total_stars();
        let streak = mode.records.streak_now(day);
        p.spawn(theme::para(
            &fonts,
            format!(
                "Make the target by its route, from a kit of its own. Each step is worth {STEP_POINTS}: a reaction that doesn't go costs {FAIL_COST}, a hint {HINT_COST} or more, never below {STEP_FLOOR}. Finish clean for {CLEAN_BONUS} more. Your lab waits as you left it."
            ),
            theme::MD,
            theme::TEXT_2,
            Val::Percent(100.0),
        ));
        p.spawn(Node { column_gap: Val::Px(18.0), row_gap: Val::Px(6.0), flex_wrap: FlexWrap::Wrap, align_items: AlignItems::Center, ..default() })
            .with_children(|row| {
                row.spawn(Node { column_gap: Val::Px(6.0), align_items: AlignItems::Center, ..default() }).with_children(|s| {
                    s.spawn((
                        Text::new("\u{2605}"),
                        TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(20.0), ..default() },
                        TextColor(theme::GOLD),
                    ));
                    s.spawn(theme::label(&fonts, format!("{got} of {of} stars"), theme::MD, Weight::Semibold, theme::TEXT));
                });
                row.spawn(theme::label(
                    &fonts,
                    format!("Daily streak {streak} (best {})", mode.records.best_streak),
                    theme::MD,
                    Weight::Semibold,
                    theme::mix(theme::GOLD, theme::RED, 0.35),
                ));
            });
        // today's challenge
        if let Some(c) = mode.daily(day) {
            let done = mode.records.daily_done(day);
            p.spawn((
                Node {
                    flex_direction: FlexDirection::Column,
                    row_gap: Val::Px(8.0),
                    padding: UiRect::all(Val::Px(16.0)),
                    border: UiRect::all(Val::Px(1.5)),
                    border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                    ..default()
                },
                BackgroundColor(theme::mix(theme::RAISED, theme::GOLD, 0.08)),
                BorderColor::all(theme::GOLD.with_alpha(0.7)),
            ))
            .with_children(|d| {
                d.spawn(theme::label(&fonts, "TODAY'S CHALLENGE", theme::SM, Weight::Bold, theme::GOLD));
                d.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Baseline, flex_wrap: FlexWrap::Wrap, ..default() })
                    .with_children(|t| {
                        t.spawn(theme::label(&fonts, name(c.target), theme::LG, Weight::Semibold, theme::TEXT));
                        t.spawn(theme::label(&fonts, formula(c.target), theme::MD, Weight::Regular, theme::CYAN));
                        t.spawn(theme::label(&fonts, format!("{} steps", c.steps.len()), theme::SM, Weight::Regular, theme::TEXT_2));
                    });
                d.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Center, ..default() }).with_children(|b| {
                    if done {
                        b.spawn(theme::label(&fonts, "Done today. A new one tomorrow.", theme::SM, Weight::Semibold, theme::GREEN));
                    } else {
                        theme::spawn_button(b, &fonts, &assets, Kind::Accent(theme::GOLD), Some("target"), "Play today's", ChallengeCard { id: c.id, daily: true });
                    }
                });
            });
        }
        // era by era
        let mut eras: Vec<u8> = mode.challenges.iter().map(|c| c.era).collect();
        eras.dedup();
        for era in eras {
            let list: Vec<&Challenge> = mode.challenges.iter().filter(|c| c.era == era).collect();
            let open = list.first().is_some_and(|c| mode.open(c));
            let ep = db.epochs.get(era as usize);
            let earned: u32 = list.iter().map(|c| mode.records.stars(c.id) as u32).sum();
            p.spawn(Node { flex_direction: FlexDirection::Column, row_gap: Val::Px(8.0), margin: UiRect::top(Val::Px(8.0)), ..default() })
                .with_children(|g| {
                    g.spawn(Node { column_gap: Val::Px(10.0), align_items: AlignItems::Baseline, flex_wrap: FlexWrap::Wrap, ..default() })
                        .with_children(|h| {
                            h.spawn(theme::label(&fonts, ep.map(|e| e.name.to_uppercase()).unwrap_or_default(), theme::SM, Weight::Bold, if open { theme::GOLD } else { theme::TEXT_3 }));
                            h.spawn(theme::label(&fonts, ep.map(|e| e.era.clone()).unwrap_or_default(), theme::XS, Weight::Regular, theme::TEXT_3));
                            h.spawn((
                                Text::new(format!("\u{2605} {earned} / {}", list.len() * 3)),
                                TextFont { font: fonts.symbols.clone().into(), font_size: FontSize::Px(theme::SM), ..default() },
                                TextColor(if earned > 0 { theme::GOLD } else { theme::TEXT_2 }),
                            ));
                        });
                    if !open {
                        g.spawn(Node { column_gap: Val::Px(8.0), align_items: AlignItems::Center, ..default() }).with_children(|l| {
                            l.spawn(theme::icon(&assets, "lock", 16.0, theme::TEXT_3));
                            l.spawn(theme::para(
                                &fonts,
                                format!(
                                    "Opens with {} stars in the era before, or when your lab reaches this era.",
                                    crate::resources::challenge::STARS_TO_OPEN
                                ),
                                theme::SM,
                                theme::TEXT_2,
                                Val::Percent(100.0),
                            ));
                        });
                        return;
                    }
                    g.spawn(Node { flex_wrap: FlexWrap::Wrap, column_gap: Val::Px(8.0), row_gap: Val::Px(8.0), ..default() })
                        .with_children(|w| {
                            for c in list {
                                let rec = mode.records.records.get(&c.id).copied().unwrap_or_default();
                                w.spawn((
                                    theme::button(
                                        Kind::Row,
                                        Node {
                                            flex_basis: Val::Px(250.0),
                                            flex_grow: 1.0,
                                            max_width: Val::Px(400.0),
                                            min_height: Val::Px(74.0),
                                            flex_direction: FlexDirection::Column,
                                            row_gap: Val::Px(3.0),
                                            padding: UiRect::axes(Val::Px(14.0), Val::Px(9.0)),
                                            ..default()
                                        },
                                        theme::R_MD,
                                    ),
                                    ChallengeCard { id: c.id, daily: false },
                                ))
                                .with_children(|b| {
                                    b.spawn(Node { justify_content: JustifyContent::SpaceBetween, column_gap: Val::Px(8.0), ..default() })
                                        .insert(Pickable::IGNORE)
                                        .with_children(|t| {
                                            t.spawn((theme::para(&fonts, name(c.target), theme::MD, theme::TEXT, Val::Percent(100.0)), Pickable::IGNORE));
                                            t.spawn(star_label(&fonts, rec.stars, 18.0));
                                        });
                                    b.spawn((theme::label(&fonts, formula(c.target), theme::SM, Weight::Regular, theme::CYAN), Pickable::IGNORE));
                                    let best = if rec.best > 0 { format!(" · best {} of {}", rec.best, c.max_score()) } else { String::new() };
                                    b.spawn((theme::label(&fonts, format!("{} steps{best}", c.steps.len()), theme::XS, Weight::Semibold, theme::TEXT_2), Pickable::IGNORE));
                                });
                            }
                        });
                });
        }
    });
}

// ---------------------------------------------------------------------------------------
// The bar on the bench
// ---------------------------------------------------------------------------------------
#[allow(clippy::too_many_arguments, clippy::type_complexity)]
fn hud_view_system(
    mut commands: Commands,
    mode: Res<ChallengeMode>,
    db: Option<Res<RecipeDatabase>>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    look: (Res<UiFonts>, Res<AssetServer>),
    views: (
        Res<crate::ui::codex::CodexState>,
        Res<crate::ui::reaction_library::ReactionLibState>,
        Res<crate::ui::tech_tree::TechTreeState>,
        Res<crate::ui::curriculum::CurriculumState>,
    ),
    mut root: Query<(Entity, &mut Node), With<HudRoot>>,
    mut last: Local<Option<(u32, Vec<u32>, Vec<bool>, u32)>>,
) {
    let (fonts, assets) = look;
    let (codex, rlib, tree, learn) = views;
    let Ok((root_e, mut node)) = root.single_mut() else { return };
    let show = mode.playing() && !mode.board_open && !(codex.open || rlib.open || tree.open || learn.open);
    let d = if show { Display::Flex } else { Display::None };
    if node.display != d {
        node.display = d;
    }
    let Some(run) = mode.run() else {
        *last = None;
        return;
    };
    let key = (run.challenge.id, run.points.clone(), run.done.clone(), run.score());
    if last.as_ref() == Some(&key) {
        return;
    }
    *last = Some(key);
    let Some(subs) = game_data.as_ref().and_then(|g| substances.get(&g.substances)) else { return };
    let name = |id: u32| subs.0.get(&id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    let era = db
        .as_ref()
        .and_then(|db| db.epochs.get(run.challenge.era as usize))
        .map(|e| e.name.clone())
        .unwrap_or_default();
    commands.entity(root_e).despawn_children();
    commands.entity(root_e).with_children(|r| {
        r.spawn((
            Node {
                max_width: Val::Px(900.0),
                flex_grow: 1.0,
                flex_direction: FlexDirection::Column,
                row_gap: Val::Px(7.0),
                padding: UiRect::axes(Val::Px(14.0), Val::Px(10.0)),
                border: UiRect::all(Val::Px(1.0)),
                border_radius: BorderRadius::all(Val::Px(theme::R_LG)),
                ..default()
            },
            BackgroundColor(theme::SURFACE.with_alpha(0.94)),
            BorderColor::all(theme::GOLD.with_alpha(0.55)),
            theme::shadow(16.0, 4.0, 0.45),
        ))
        .with_children(|card| {
            card.spawn(Node {
                justify_content: JustifyContent::SpaceBetween,
                align_items: AlignItems::Center,
                column_gap: Val::Px(10.0),
                ..default()
            })
            .with_children(|top| {
                top.spawn(Node { flex_direction: FlexDirection::Column, flex_shrink: 1.0, ..default() }).with_children(
                    |t| {
                        t.spawn(theme::label(
                            &fonts,
                            format!("{}CHALLENGE · {}", if run.daily { "TODAY'S " } else { "" }, era.to_uppercase()),
                            theme::XS,
                            Weight::Bold,
                            theme::GOLD,
                        ));
                        t.spawn(Node {
                            column_gap: Val::Px(8.0),
                            align_items: AlignItems::Baseline,
                            flex_wrap: FlexWrap::Wrap,
                            ..default()
                        })
                        .with_children(|m| {
                            m.spawn(theme::label(&fonts, "Make", theme::MD, Weight::Regular, theme::TEXT_2));
                            m.spawn(theme::label(
                                &fonts,
                                name(run.challenge.target),
                                theme::LG,
                                Weight::Semibold,
                                theme::TEXT,
                            ));
                            m.spawn(theme::label(
                                &fonts,
                                subs.0
                                    .get(&run.challenge.target)
                                    .map(|s| crate::components::format_formula(&s.formula))
                                    .unwrap_or_default(),
                                theme::MD,
                                Weight::Regular,
                                theme::CYAN,
                            ));
                        });
                    },
                );
                top.spawn(Node {
                    column_gap: Val::Px(10.0),
                    align_items: AlignItems::Center,
                    flex_shrink: 0.0,
                    ..default()
                })
                .with_children(|s| {
                    s.spawn(Node {
                        flex_direction: FlexDirection::Column,
                        align_items: AlignItems::FlexEnd,
                        ..default()
                    })
                    .with_children(|n| {
                        n.spawn(theme::label(&fonts, run.score().to_string(), theme::XL, Weight::Bold, theme::GOLD));
                        n.spawn(theme::label(
                            &fonts,
                            format!("of {}", run.challenge.max_score()),
                            theme::XS,
                            Weight::Regular,
                            theme::TEXT_2,
                        ));
                    });
                    theme::spawn_button(s, &fonts, &assets, Kind::Secondary, None, "Give up", HudGiveUp);
                });
            });
            // the route: each step, what it makes, and what it is still worth
            card.spawn(Node {
                flex_wrap: FlexWrap::Wrap,
                column_gap: Val::Px(6.0),
                row_gap: Val::Px(6.0),
                ..default()
            })
            .with_children(|steps| {
                let current = run.current();
                for (i, product) in run.challenge.step_products.iter().enumerate() {
                    let done = run.done[i];
                    let here = current == Some(i);
                    let c = if done {
                        theme::GREEN
                    } else if here {
                        theme::GOLD
                    } else {
                        theme::TEXT_3
                    };
                    steps
                        .spawn((
                            Node {
                                column_gap: Val::Px(7.0),
                                align_items: AlignItems::Center,
                                padding: UiRect::axes(Val::Px(10.0), Val::Px(5.0)),
                                border: UiRect::all(Val::Px(if here { 1.5 } else { 1.0 })),
                                border_radius: BorderRadius::all(Val::Px(99.0)),
                                ..default()
                            },
                            BackgroundColor(c.with_alpha(if here { 0.16 } else { 0.08 })),
                            BorderColor::all(c.with_alpha(0.8)),
                        ))
                        .with_children(|chip| {
                            chip.spawn((
                                Text::new(if done { "\u{2713}".to_string() } else { (i + 1).to_string() }),
                                TextFont {
                                    font: fonts.symbols.clone().into(),
                                    font_size: FontSize::Px(theme::SM),
                                    ..default()
                                },
                                TextColor(c),
                            ));
                            chip.spawn(theme::label(
                                &fonts,
                                name(*product),
                                theme::SM,
                                Weight::Semibold,
                                if done || here { theme::TEXT } else { theme::TEXT_2 },
                            ));
                            chip.spawn(theme::label(
                                &fonts,
                                run.points[i].to_string(),
                                theme::XS,
                                Weight::Bold,
                                theme::mix(c, theme::TEXT, 0.3),
                            ));
                        });
                }
            });
        });
    });
}

// ---------------------------------------------------------------------------------------
// The finish
// ---------------------------------------------------------------------------------------
#[allow(clippy::too_many_arguments)]
fn finish_view_system(
    mut commands: Commands,
    mode: Res<ChallengeMode>,
    game_data: Option<Res<GameData>>,
    substances: Res<Assets<Substances>>,
    look: (Res<UiFonts>, Res<AssetServer>),
    mut root: Query<&mut Node, With<FinishRoot>>,
    content: Query<Entity, With<FinishContent>>,
    mut shown: Local<bool>,
) {
    let (fonts, assets) = look;
    let want = mode.card && mode.playing();
    if let Ok(mut n) = root.single_mut() {
        let d = if want { Display::Flex } else { Display::None };
        if n.display != d {
            n.display = d;
        }
    }
    if !want {
        *shown = false;
        return;
    }
    if *shown {
        return;
    }
    let (Some(run), Ok(content)) = (mode.run(), content.single()) else { return };
    let Some(subs) = game_data.as_ref().and_then(|g| substances.get(&g.substances)) else { return };
    *shown = true;
    let name = |id: u32| subs.0.get(&id).map(|s| s.name.clone()).unwrap_or_else(|| format!("#{id}"));
    let best = mode.records.records.get(&run.challenge.id).map_or(0, |r| r.best);
    let next = mode.next_after(run.challenge.id).map(|c| c.id);
    let streak = mode.records.streak_now(today());
    commands.entity(content).despawn_children();
    commands.entity(content).with_children(|c| {
        c.spawn(theme::label(&fonts, "CHALLENGE COMPLETE", theme::SM, Weight::Bold, theme::GOLD));
        c.spawn(theme::label(&fonts, name(run.challenge.target), theme::XL, Weight::Semibold, theme::TEXT));
        c.spawn(star_label(&fonts, run.stars(), 46.0));
        c.spawn(theme::label(
            &fonts,
            format!("{} of {}", run.score(), run.challenge.max_score()),
            theme::LG,
            Weight::Bold,
            theme::TEXT,
        ));
        let steps: Vec<String> = run.points.iter().map(|p| p.to_string()).collect();
        let mut lines = vec![format!("Steps: {}", steps.join(" + "))];
        if run.clean() {
            lines.push(format!("Clean finish: +{CLEAN_BONUS}"));
        } else {
            lines.push(format!(
                "{} reaction{} that didn't go, {} hint{}",
                run.fails,
                if run.fails == 1 { "" } else { "s" },
                run.hints_taken,
                if run.hints_taken == 1 { "" } else { "s" }
            ));
        }
        lines.push(if mode.new_best { "A new best!".to_string() } else { format!("Best: {best}") });
        if run.daily {
            lines.push(format!("Daily streak: {streak}"));
        }
        for l in lines {
            c.spawn(theme::label(&fonts, l, theme::MD, Weight::Regular, theme::TEXT_2));
        }
        c.spawn(Node {
            flex_wrap: FlexWrap::Wrap,
            justify_content: JustifyContent::Center,
            column_gap: Val::Px(8.0),
            row_gap: Val::Px(8.0),
            margin: UiRect::top(Val::Px(8.0)),
            ..default()
        })
        .with_children(|b| {
            if let Some(n) = next {
                theme::spawn_button(
                    b,
                    &fonts,
                    &assets,
                    Kind::Accent(theme::GOLD),
                    Some("target"),
                    "Next challenge",
                    FinishButton::Next(n),
                );
            }
            theme::spawn_button(
                b,
                &fonts,
                &assets,
                Kind::Secondary,
                None,
                "Try again",
                FinishButton::Again(run.challenge.id),
            );
            theme::spawn_button(b, &fonts, &assets, Kind::Secondary, None, "All challenges", FinishButton::Board);
            theme::spawn_button(
                b,
                &fonts,
                &assets,
                Kind::Secondary,
                Some("bench"),
                "Back to the lab",
                FinishButton::Lab,
            );
        });
    });
}
