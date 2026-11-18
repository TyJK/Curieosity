// src/systems/sound.rs
//
// The game's sounds: a small set of short cues (assets/sounds, made by
// tools/art/gen_sounds.py) played for what happens on the bench and in the menus. Each
// kind of vessel sounds like itself: a fire catches and crackles, a mortar grinds, an ice
// bath clinks and blows cold (see Family).
//
// Nothing else in the game plays audio directly. Cues come from the game's own events
// (`GameEvent`: reactions, fizzles, discoveries, milestones, eras) and from what appears
// on screen (a vessel placed, a substance picked up or dropped in, a button pressed),
// so new features get sounds by emitting the events they already emit. Within one frame
// only the most important cue of each kind plays, so a reaction that discovers three
// things and fires a milestone sounds like one milestone, not five overlapping chimes.
use crate::ui::{Button, Clicked};
use bevy::audio::{AudioPlayer, AudioSource, PlaybackSettings, Volume};
use bevy::prelude::*;

use crate::components::ui_markers::ProcessVessel;
use crate::components::{Draggable, InCatalystZone, InVessel, VesselCard};
use crate::data::common::ProcessType;
use crate::systems::autoplay::GameEvent;
use crate::systems::drag_drop::DragGhostNode;
use crate::ui::inventory::PopIn;
use crate::ui::settings::Settings;

/// How a vessel sounds: each family has a sound for being set on the bench and one for
/// reacting.
#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
pub enum Family {
    Fire,
    Grind,
    Cold,
    Glass,
    Bio,
    Electric,
    Radiation,
    Pressure,
    Spin,
    Crystal,
}

impl Family {
    pub const ALL: [Family; 10] = [
        Family::Fire,
        Family::Grind,
        Family::Cold,
        Family::Glass,
        Family::Bio,
        Family::Electric,
        Family::Radiation,
        Family::Pressure,
        Family::Spin,
        Family::Crystal,
    ];

    /// The family of a vessel, by its process.
    pub fn of(p: &ProcessType) -> Family {
        use ProcessType::*;
        match p {
            Heat | Smelting | BlastFurnace | Cracker => Family::Fire,
            Mix => Family::Grind,
            Cool | AirLiquefier => Family::Cold,
            Distillation | Column | Flask => Family::Glass,
            Fermenter | Bioreactor | Wait => Family::Bio,
            Electrolysis | ApplyCurrent | ElectrolyticCell | ArcFurnace => Family::Electric,
            Irradiate | NuclearReactor | Cyclotron => Family::Radiation,
            Pressurize | HighPressure | DiamondPress | Catalysis | Polymerize => Family::Pressure,
            Centrifuge | Ultracentrifuge => Family::Spin,
            CrystalPuller | CvdChamber => Family::Crystal,
        }
    }

    fn name(self) -> &'static str {
        match self {
            Family::Fire => "fire",
            Family::Grind => "grind",
            Family::Cold => "cold",
            Family::Glass => "glass",
            Family::Bio => "bio",
            Family::Electric => "electric",
            Family::Radiation => "radiation",
            Family::Pressure => "pressure",
            Family::Spin => "spin",
            Family::Crystal => "crystal",
        }
    }
}

#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
pub enum Cue {
    Click,
    Pickup,
    Drop,
    /// a vessel set on the bench
    Place(Family),
    /// a vessel reacting
    React(Family),
    Fizzle,
    Discovery,
    Milestone,
    Era,
}

impl Cue {
    /// Every cue there is (one file each).
    pub fn all() -> Vec<Cue> {
        let mut v = vec![Cue::Click, Cue::Pickup, Cue::Drop, Cue::Fizzle, Cue::Discovery, Cue::Milestone, Cue::Era];
        v.extend(Family::ALL.iter().map(|f| Cue::Place(*f)));
        v.extend(Family::ALL.iter().map(|f| Cue::React(*f)));
        v
    }

    pub fn file(self) -> String {
        match self {
            Cue::Click => "sounds/click.ogg".into(),
            Cue::Pickup => "sounds/pickup.ogg".into(),
            Cue::Drop => "sounds/drop.ogg".into(),
            Cue::Place(f) => format!("sounds/{}_place.ogg", f.name()),
            Cue::React(f) => format!("sounds/{}_react.ogg", f.name()),
            Cue::Fizzle => "sounds/fizzle.ogg".into(),
            Cue::Discovery => "sounds/discovery.ogg".into(),
            Cue::Milestone => "sounds/milestone.ogg".into(),
            Cue::Era => "sounds/era.ogg".into(),
        }
    }

    /// Progress cues outrank each other (an era beats a milestone beats a discovery); the
    /// rest are independent.
    fn progress_rank(self) -> Option<u8> {
        match self {
            Cue::Discovery => Some(1),
            Cue::Milestone => Some(2),
            Cue::Era => Some(3),
            _ => None,
        }
    }
}

/// Ask for a cue from anywhere: `MessageWriter<PlayCue>`.
#[derive(Message, Clone, Copy, Debug)]
pub struct PlayCue(pub Cue);

#[derive(Resource, Default)]
pub struct SoundBank(Vec<(Cue, Handle<AudioSource>)>);

/// Whether cues reach the speakers. Off for the scripted review run (it would play for
/// hours); the cues are still decided and logged, so the checks can test them.
#[derive(Resource)]
pub struct SoundOutput(pub bool);

impl Default for SoundOutput {
    fn default() -> Self {
        Self(true)
    }
}

/// The cues played so far this session, newest last (the checks read it).
#[derive(Resource, Default)]
pub struct SoundLog(pub Vec<Cue>);

pub struct SoundPlugin;

impl Plugin for SoundPlugin {
    fn build(&self, app: &mut App) {
        app.add_message::<PlayCue>()
            .init_resource::<SoundBank>()
            .init_resource::<SoundOutput>()
            .init_resource::<SoundLog>()
            .add_systems(Startup, load_sounds)
            .add_systems(PostUpdate, (cues_from_play_system, play_cues_system).chain());
    }
}

fn load_sounds(mut bank: ResMut<SoundBank>, assets: Res<AssetServer>) {
    bank.0 = Cue::all().into_iter().map(|c| (c, assets.load(c.file()))).collect();
}

/// Cues from what happened in play this frame.
#[allow(clippy::type_complexity)]
fn cues_from_play_system(
    mut events: MessageReader<GameEvent>,
    mut out: MessageWriter<PlayCue>,
    placed: Query<&ProcessVessel, Added<VesselCard>>,
    vessels: Query<&ProcessVessel>,
    lifted: Query<(), Added<DragGhostNode>>,
    landed: Query<(), (Or<(Changed<InVessel>, Added<InCatalystZone>)>, Without<PopIn>)>,
    clicked: Query<(), (With<Clicked>, With<Button>, Without<Draggable>)>,
) {
    for e in events.read() {
        out.write(PlayCue(match e {
            GameEvent::Discovery { .. } => Cue::Discovery,
            GameEvent::Milestone { .. } => Cue::Milestone,
            GameEvent::Fizzle { .. } => Cue::Fizzle,
            GameEvent::Reacted { vessel, .. } => {
                Cue::React(vessels.get(*vessel).map_or(Family::Glass, |v| Family::of(&v.process)))
            }
            GameEvent::Era { .. } => Cue::Era,
        }));
    }
    for v in &placed {
        out.write(PlayCue(Cue::Place(Family::of(&v.process))));
    }
    if !lifted.is_empty() {
        out.write(PlayCue(Cue::Pickup));
    }
    if !landed.is_empty() {
        out.write(PlayCue(Cue::Drop));
    }
    if !clicked.is_empty() {
        out.write(PlayCue(Cue::Click));
    }
}

/// The frame's cues, after the rules: one of each, the top progress cue only, and a
/// button click only when nothing else sounds (the button's own result speaks for it).
pub fn pick_cues(asked: &[Cue]) -> Vec<Cue> {
    let mut picked: Vec<Cue> = Vec::new();
    for c in asked {
        if !picked.contains(c) {
            picked.push(*c);
        }
    }
    if let Some(top) = picked.iter().filter_map(|c| c.progress_rank()).max() {
        picked.retain(|c| c.progress_rank().is_none_or(|r| r == top));
    }
    if picked.len() > 1 {
        picked.retain(|c| *c != Cue::Click);
    }
    picked
}

fn play_cues_system(
    mut commands: Commands,
    mut asked: MessageReader<PlayCue>,
    bank: Res<SoundBank>,
    output: Res<SoundOutput>,
    settings: Res<Settings>,
    mut log: ResMut<SoundLog>,
) {
    let asked: Vec<Cue> = asked.read().map(|p| p.0).collect();
    if asked.is_empty() {
        return;
    }
    for cue in pick_cues(&asked) {
        if cue == Cue::Click && !settings.ui_sounds {
            continue;
        }
        log.0.push(cue);
        if log.0.len() > 256 {
            log.0.drain(..128);
        }
        let volume = settings.volume.clamp(0.0, 1.0);
        if !output.0 || volume <= 0.0 {
            continue;
        }
        if let Some((_, handle)) = bank.0.iter().find(|(c, _)| *c == cue) {
            commands.spawn((
                AudioPlayer::new(handle.clone()),
                PlaybackSettings::DESPAWN.with_volume(Volume::Linear(volume)),
                Name::new("Sound"),
            ));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn one_cue_per_kind_and_the_biggest_moment_wins() {
        use Cue::*;
        assert_eq!(pick_cues(&[Discovery, Discovery, Discovery]), vec![Discovery]);
        assert_eq!(pick_cues(&[Discovery, Milestone, Discovery]), vec![Milestone]);
        assert_eq!(pick_cues(&[Discovery, Era, Milestone]), vec![Era]);
        assert_eq!(pick_cues(&[Click, React(Family::Fire)]), vec![React(Family::Fire)]);
        assert_eq!(
            pick_cues(&[React(Family::Fire), React(Family::Cold)]),
            vec![React(Family::Fire), React(Family::Cold)]
        );
        assert_eq!(pick_cues(&[Click]), vec![Click]);
        assert_eq!(pick_cues(&[Drop, Discovery]), vec![Drop, Discovery]);
    }

    #[test]
    fn every_cue_has_its_sound_file() {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("assets");
        for c in Cue::all() {
            assert!(root.join(c.file()).is_file(), "missing {}", c.file());
        }
    }
}
