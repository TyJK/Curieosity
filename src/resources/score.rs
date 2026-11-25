// src/resources/score.rs
//
// The score, for a player who turns it on (Settings: Score). Each discovery is worth 10
// points; a reaction that doesn't go costs 2; a hint costs more the more of them are taken
// in a row: the first since the last discovery 2, the next 4, then 6, and so on, so a hint
// or two stays cheap and leaning on them doesn't pay. The score never goes below zero.
//
// It counts only while it is on, is saved with the progress, and starts over with New
// Game. The rules are kept apart from the lab so the chain mode can score the same way.
use bevy::prelude::*;
use serde::{Deserialize, Serialize};

use crate::resources::player_progress::PlayerProgress;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::autoplay::GameEvent;
use crate::ui::settings::Settings;
use crate::ui::theme::{self, Weight};

/// Points for each new substance.
pub const DISCOVERY_POINTS: u32 = 10;
/// Points off for a reaction that doesn't go.
pub const FIZZLE_COST: u32 = 2;
/// Each hint since the last discovery costs this much more than the one before.
pub const HINT_STEP: u32 = 2;

#[derive(Resource, Debug, Clone, Copy, Default, PartialEq, Eq, Serialize, Deserialize)]
#[serde(default)]
pub struct Score {
    pub points: u32,
    /// hints taken since the last discovery (the next one costs HINT_STEP more)
    pub hints_since: u32,
}

impl Score {
    pub fn discovery(&mut self) {
        self.points += DISCOVERY_POINTS;
        self.hints_since = 0;
    }

    pub fn fizzle(&mut self) {
        self.points = self.points.saturating_sub(FIZZLE_COST);
    }

    /// What the next hint will cost.
    pub fn next_hint_cost(&self) -> u32 {
        HINT_STEP * (self.hints_since + 1)
    }

    pub fn hint(&mut self) {
        self.points = self.points.saturating_sub(self.next_hint_cost());
        self.hints_since += 1;
    }
}

/// A hint was taken: a target chosen from the Hint button's list, or one more clue shown.
#[derive(Message, Clone, Copy, Debug)]
pub struct HintTaken;

/// The header's score (shown while scoring is on).
#[derive(Component)]
pub struct ScorePill;
#[derive(Component)]
pub struct ScoreText;

pub struct ScorePlugin;

impl Plugin for ScorePlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<Score>().add_message::<HintTaken>().add_systems(
            Update,
            (score_system, score_view_system).chain().after(crate::systems::discovery::discovery_system),
        );
    }
}

/// Discoveries, reactions that don't go, and hints, onto the score (while scoring is on).
pub fn score_system(
    settings: Option<Res<Settings>>,
    progress: Res<PlayerProgress>,
    mut events: MessageReader<GameEvent>,
    mut hints: MessageReader<HintTaken>,
    mut score: ResMut<Score>,
) {
    if !progress.ready || !settings.is_some_and(|s| s.scoring) {
        events.clear();
        hints.clear();
        return;
    }
    for ev in events.read() {
        match ev {
            GameEvent::Discovery { .. } => score.discovery(),
            GameEvent::Fizzle { .. } => score.fizzle(),
            _ => {}
        }
    }
    for _ in hints.read() {
        score.hint();
    }
}

/// The header's pill, for the header: a star and the points.
pub fn spawn_score_pill(parent: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer) {
    parent
        .spawn((
            ScorePill,
            Node {
                display: Display::None,
                height: Val::Px(30.0),
                padding: UiRect::horizontal(Val::Px(12.0)),
                column_gap: Val::Px(6.0),
                align_items: AlignItems::Center,
                border: UiRect::all(Val::Px(1.0)),
                border_radius: BorderRadius::all(Val::Px(99.0)),
                ..default()
            },
            BackgroundColor(theme::mix(theme::SURFACE, theme::GOLD, 0.12)),
            BorderColor::all(theme::mix(theme::LINE, theme::GOLD, 0.5)),
            Pickable::default(),
            crate::ui::onboarding::Tip::Text(
                "Score",
                "10 points a discovery. A reaction that doesn't go costs 2; each hint since your last discovery costs 2 more than the one before. Never below zero.",
            ),
            Name::new("ScorePill"),
        ))
        .with_children(|p| {
            p.spawn(theme::icon(assets, "spark", 14.0, theme::GOLD));
            p.spawn((ScoreText, theme::label(fonts, "0", theme::SM, Weight::Bold, theme::GOLD), Pickable::IGNORE));
        });
}

/// The pill shows while scoring is on, with the points (written only when they change).
pub fn score_view_system(
    settings: Option<Res<Settings>>,
    score: Res<Score>,
    mut pills: Query<&mut Node, With<ScorePill>>,
    mut texts: Query<&mut Text, With<ScoreText>>,
) {
    let on = settings.as_ref().is_some_and(|s| s.scoring);
    let d = if on { Display::Flex } else { Display::None };
    for mut n in &mut pills {
        if n.display != d {
            n.display = d;
        }
    }
    let words = thousands(score.points);
    for mut t in &mut texts {
        if t.0 != words {
            t.0 = words.clone();
        }
    }
}

/// 12345 -> "12,345".
pub fn thousands(n: u32) -> String {
    let s = n.to_string();
    let mut out = String::new();
    for (i, c) in s.chars().enumerate() {
        if i > 0 && (s.len() - i).is_multiple_of(3) {
            out.push(',');
        }
        out.push(c);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn discoveries_score_and_failures_and_hints_cost() {
        let mut s = Score::default();
        s.fizzle();
        assert_eq!(s.points, 0, "never below zero");
        s.discovery();
        s.discovery();
        assert_eq!(s.points, 20);
        s.fizzle();
        assert_eq!(s.points, 18);
        // hints in a row cost 2, 4, 6
        assert_eq!(s.next_hint_cost(), 2);
        s.hint();
        s.hint();
        assert_eq!(s.points, 12);
        assert_eq!(s.next_hint_cost(), 6);
        // a discovery starts the hints' cost over
        s.discovery();
        assert_eq!(s.points, 22);
        assert_eq!(s.next_hint_cost(), 2);
        for _ in 0..10 {
            s.hint();
        }
        assert_eq!(s.points, 0);
    }

    #[test]
    fn points_read_in_thousands() {
        assert_eq!(thousands(0), "0");
        assert_eq!(thousands(999), "999");
        assert_eq!(thousands(1000), "1,000");
        assert_eq!(thousands(1234567), "1,234,567");
    }
}
