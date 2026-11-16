// src/systems/sound.rs
//
// The game's sounds: a small set of short cues (assets/sounds, made by
// tools/art/gen_sounds.py) played for what happens on the bench and in the menus.
//
// Nothing else in the game plays audio directly. Cues come from the game's own events
// (`GameEvent`: reactions, fizzles, discoveries, milestones, eras) and from what appears
// on screen (a vessel placed, a substance picked up or dropped in, a button pressed),
// so new features get sounds by emitting the events they already emit. Within one frame
// only the most important cue of each kind plays, so a reaction that discovers three
// things and fires a milestone sounds like one milestone, not five overlapping chimes.
use bevy::audio::{AudioPlayer, AudioSource, PlaybackSettings, Volume};
use bevy::prelude::*;

use crate::components::{Draggable, InCatalystZone, InVessel, VesselCard};
use crate::systems::autoplay::GameEvent;
use crate::systems::drag_drop::DragGhostNode;
use crate::ui::inventory::PopIn;
use crate::ui::settings::Settings;

#[derive(Clone, Copy, PartialEq, Eq, Hash, Debug)]
pub enum Cue {
    Click,
    Pickup,
    Drop,
    Place,
    React,
    Fizzle,
    Discovery,
    Milestone,
    Era,
}

impl Cue {
    pub const ALL: [Cue; 9] = [
        Cue::Click,
        Cue::Pickup,
        Cue::Drop,
        Cue::Place,
        Cue::React,
        Cue::Fizzle,
        Cue::Discovery,
        Cue::Milestone,
        Cue::Era,
    ];

    pub fn file(self) -> &'static str {
        match self {
            Cue::Click => "sounds/click.ogg",
            Cue::Pickup => "sounds/pickup.ogg",
            Cue::Drop => "sounds/drop.ogg",
            Cue::Place => "sounds/place.ogg",
            Cue::React => "sounds/react.ogg",
            Cue::Fizzle => "sounds/fizzle.ogg",
            Cue::Discovery => "sounds/discovery.ogg",
            Cue::Milestone => "sounds/milestone.ogg",
            Cue::Era => "sounds/era.ogg",
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
    bank.0 = Cue::ALL.iter().map(|c| (*c, assets.load(c.file()))).collect();
}

/// Cues from what happened in play this frame.
#[allow(clippy::type_complexity)]
fn cues_from_play_system(
    mut events: MessageReader<GameEvent>,
    mut out: MessageWriter<PlayCue>,
    placed: Query<(), Added<VesselCard>>,
    lifted: Query<(), Added<DragGhostNode>>,
    landed: Query<(), (Or<(Changed<InVessel>, Added<InCatalystZone>)>, Without<PopIn>)>,
    pressed: Query<&Interaction, (Changed<Interaction>, With<Button>, Without<Draggable>)>,
) {
    for e in events.read() {
        out.write(PlayCue(match e {
            GameEvent::Discovery { .. } => Cue::Discovery,
            GameEvent::Milestone { .. } => Cue::Milestone,
            GameEvent::Fizzle { .. } => Cue::Fizzle,
            GameEvent::Reacted { .. } => Cue::React,
            GameEvent::Era { .. } => Cue::Era,
        }));
    }
    if !placed.is_empty() {
        out.write(PlayCue(Cue::Place));
    }
    if !lifted.is_empty() {
        out.write(PlayCue(Cue::Pickup));
    }
    if !landed.is_empty() {
        out.write(PlayCue(Cue::Drop));
    }
    if pressed.iter().any(|i| *i == Interaction::Pressed) {
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
        assert_eq!(pick_cues(&[Click, React]), vec![React]);
        assert_eq!(pick_cues(&[Click]), vec![Click]);
        assert_eq!(pick_cues(&[Drop, Discovery]), vec![Drop, Discovery]);
    }

    #[test]
    fn every_cue_has_its_sound_file() {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("assets");
        for c in Cue::ALL {
            assert!(root.join(c.file()).is_file(), "missing {}", c.file());
        }
    }
}
