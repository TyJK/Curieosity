// src/systems/achievements.rs
//
// Achievements: one for every milestone, one for reaching each era, and two for finishing
// (every vessel, every substance). The list is worked out from the content, so new
// milestones and eras become achievements without touching this file; `cargo test` keeps
// steam/achievements.csv (what gets entered in Steamworks) in step with it.
//
// What has been earned is worked out from the game's own state (milestones fired, the era
// reached, vessels unlocked, substances found), not from events, so a save made before
// achievements existed, or made in a build without Steam, unlocks everything it has earned
// the first time it loads under Steam.
//
// Built with `--features steam`, earned achievements are set on Steam (the scripted review
// run never touches Steam). Without it the game keeps the list to itself.
use bevy::platform::collections::HashSet;
use bevy::prelude::*;

use crate::data::substances::Substances;
use crate::resources::player_progress::{FiredMilestones, PlayerProgress};
use crate::resources::recipe_database::RecipeDatabase;
use crate::ui::onboarding::CurrentEra;
use crate::ui::process_toolbar::{ProcessUnlocks, VESSELS};
use crate::GameData;

/// One achievement as Steamworks needs it.
#[derive(Clone, Debug, PartialEq)]
pub struct AchievementDef {
    /// the API name, e.g. MILESTONE_COPPER (stable: entered once in Steamworks)
    pub id: String,
    pub name: String,
    pub description: String,
    pub kind: AchievementKind,
    /// what the icon shows (tools/art/gen_steam_art.py): `vessel:<art stem>`,
    /// `substance:<id>:<formula>`, `era:<roman numeral>` or `count:<number>`
    pub art: String,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AchievementKind {
    /// the milestone with this index fired
    Milestone(usize),
    /// the header reached this era
    Era(u8),
    EveryVessel,
    EverySubstance,
}

/// Roman numerals for the eras (I is Fire & Ore).
fn numeral(n: usize) -> String {
    let mut n = n;
    let mut out = String::new();
    for (v, s) in [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")] {
        while n >= v {
            out.push_str(s);
            n -= v;
        }
    }
    out
}

/// UPPER_SNAKE_CASE from a display name ("Nylon 6,6" -> "NYLON_6_6").
pub fn api_slug(name: &str) -> String {
    let mut out = String::new();
    for c in name.chars() {
        if c.is_ascii_alphanumeric() {
            out.push(c.to_ascii_uppercase());
        } else if !out.ends_with('_') && !out.is_empty() {
            out.push('_');
        }
    }
    out.trim_end_matches('_').to_string()
}

/// Every achievement, in the order a player meets them. `describe` gives a substance's
/// name and formula.
pub fn achievement_list(db: &RecipeDatabase, describe: impl Fn(u32) -> (String, String)) -> Vec<AchievementDef> {
    let mut out = Vec::new();
    for (i, m) in db.milestones.iter().enumerate() {
        let (name, formula) = describe(m.on);
        // a milestone that unlocks a vessel shows the vessel; otherwise its substance
        let art = match m.unlock.first() {
            Some(p) => {
                format!("vessel:{}", VESSELS.iter().find(|v| &v.process == p).map(|v| v.art).unwrap_or("mortar"))
            }
            None => format!("substance:{}:{formula}", m.on),
        };
        out.push(AchievementDef {
            id: format!("MILESTONE_{}", api_slug(&name)),
            description: m.message.clone().unwrap_or_else(|| format!("Make {name}.")),
            name,
            kind: AchievementKind::Milestone(i),
            art,
        });
    }
    let side = db.side_epoch();
    for (i, e) in db.epochs.iter().enumerate().skip(1) {
        if Some(i as u8) == side {
            continue;
        }
        out.push(AchievementDef {
            id: format!("ERA_{}", api_slug(&e.name)),
            name: format!("A new era: {}", e.name),
            description: if e.blurb.is_empty() { format!("Reach {}.", e.name) } else { e.blurb.clone() },
            kind: AchievementKind::Era(i as u8),
            art: format!("era:{}", numeral(i + 1)),
        });
    }
    out.push(AchievementDef {
        id: "EVERY_VESSEL".into(),
        name: "Fully equipped".into(),
        description: format!("Unlock all {} vessels.", VESSELS.len()),
        kind: AchievementKind::EveryVessel,
        art: format!("count:{}", VESSELS.len()),
    });
    out.push(AchievementDef {
        id: "EVERY_SUBSTANCE".into(),
        name: "The whole of chemistry".into(),
        description: format!("Discover all {} substances in the game.", db.canon.len()),
        kind: AchievementKind::EverySubstance,
        art: format!("count:{}", db.canon.len()),
    });
    out
}

/// The achievements, and which this player has earned.
#[derive(Resource, Default)]
pub struct Achievements {
    pub list: Vec<AchievementDef>,
    pub earned: HashSet<String>,
}

/// An achievement earned just now (Steam listens for these).
#[derive(Message, Clone, Debug)]
pub struct AchievementEarned(pub String);

pub struct AchievementsPlugin;

impl Plugin for AchievementsPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<Achievements>()
            .add_message::<AchievementEarned>()
            .add_systems(Update, achievements_system.after(crate::ui::shell::header_stats_system));
        #[cfg(feature = "steam")]
        app.add_plugins(steam::SteamPlugin);
    }
}

/// Build the list once the content is in, then re-check what's earned whenever the game's
/// state moves.
pub fn achievements_system(
    db: Option<Res<RecipeDatabase>>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    state: (Res<PlayerProgress>, Res<FiredMilestones>, Res<CurrentEra>, Res<ProcessUnlocks>),
    mut ach: ResMut<Achievements>,
    mut earned_now: MessageWriter<AchievementEarned>,
    challenge: Option<Res<crate::ui::challenges::ChallengeMode>>,
) {
    let Some(db) = db else { return };
    // a challenge's discoveries are not the lab's
    if challenge.is_some_and(|c| c.playing()) {
        return;
    }
    let (progress, fired, era, unlocks) = state;
    if ach.list.is_empty() {
        let Some(subs) = substances.get(&game_data.substances) else { return };
        ach.list = achievement_list(&db, |id| {
            subs.0
                .get(&id)
                .map(|s| (s.name.clone(), s.formula.clone()))
                .unwrap_or_else(|| (format!("#{id}"), String::new()))
        });
    } else if !(progress.is_changed() || fired.is_changed() || era.is_changed() || unlocks.is_changed()) {
        return;
    }
    if !progress.ready || !fired.primed {
        return;
    }
    let have = |k: AchievementKind| match k {
        AchievementKind::Milestone(i) => fired.fired.contains(&i),
        AchievementKind::Era(e) => era.index >= e,
        AchievementKind::EveryVessel => VESSELS.iter().all(|v| unlocks.0.contains(&v.process)),
        AchievementKind::EverySubstance => db.canon.iter().all(|id| progress.discovered.contains(id)),
    };
    let new: Vec<String> =
        ach.list.iter().filter(|a| !ach.earned.contains(&a.id) && have(a.kind)).map(|a| a.id.clone()).collect();
    for id in new {
        info!("Achievement earned: {id}");
        ach.earned.insert(id.clone());
        earned_now.write(AchievementEarned(id));
    }
}

/// The steam/achievements.csv the Steamworks entry is made from.
pub fn achievements_csv(list: &[AchievementDef]) -> String {
    let q = |s: &str| format!("\"{}\"", s.replace('"', "\"\""));
    let mut out = String::from("api_name,name,description,icon,art\n");
    for a in list {
        out.push_str(&format!("{},{},{},{}_ACHIEVED.png,{}\n", a.id, q(&a.name), q(&a.description), a.id, a.art));
    }
    out
}

#[cfg(feature = "steam")]
mod steam {
    //! The Steam side: start the Steam client API, pump its callbacks, and set each earned
    //! achievement. Steam must be running; without it the game carries on and logs why.
    use super::AchievementEarned;
    use bevy::prelude::*;

    /// The Steam App ID, set at build time (`CURIEOSITY_STEAM_APP_ID`); 480 is Valve's
    /// test app, Spacewar, for trying the integration before the game has its own.
    pub fn app_id() -> u32 {
        option_env!("CURIEOSITY_STEAM_APP_ID").and_then(|s| s.parse().ok()).unwrap_or(480)
    }

    #[derive(Resource)]
    pub struct Steam(pub steamworks::Client);

    pub struct SteamPlugin;

    impl Plugin for SteamPlugin {
        fn build(&self, app: &mut App) {
            app.add_systems(Startup, start_steam).add_systems(First, pump).add_systems(Update, set_earned);
        }
    }

    fn start_steam(mut commands: Commands, review: Option<Res<crate::systems::autoplay::AutoplayConfig>>) {
        if review.is_some() {
            info!("Review run: Steam is left alone.");
            return;
        }
        match steamworks::Client::init_app(app_id()) {
            Ok(client) => {
                info!("Steam is running (app {}); achievements will be set there.", app_id());
                commands.insert_resource(Steam(client));
            }
            Err(e) => warn!("Steam isn't available ({e}); achievements are kept in the game only."),
        }
    }

    fn pump(steam: Option<Res<Steam>>) {
        if let Some(s) = steam {
            s.0.run_callbacks();
        }
    }

    fn set_earned(steam: Option<Res<Steam>>, mut earned: MessageReader<AchievementEarned>) {
        let Some(steam) = steam else {
            earned.clear();
            return;
        };
        let stats = steam.0.user_stats();
        let mut any = false;
        for AchievementEarned(id) in earned.read() {
            match stats.achievement(id).set() {
                Ok(()) => any = true,
                Err(()) => {
                    warn!("Steam doesn't know the achievement {id}: enter it in Steamworks (steam/achievements.csv)")
                }
            }
        }
        if any && stats.store_stats().is_err() {
            warn!("Steam didn't store the achievements; it will retry on the next one.");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn era_numerals() {
        let got: Vec<String> = (1..=8).map(numeral).collect();
        assert_eq!(got, ["I", "II", "III", "IV", "V", "VI", "VII", "VIII"]);
    }

    #[test]
    fn api_names_are_upper_snake_case() {
        assert_eq!(api_slug("Nylon 6,6"), "NYLON_6_6");
        assert_eq!(api_slug("Copper"), "COPPER");
        assert_eq!(api_slug("Steam & Revolution"), "STEAM_REVOLUTION");
        assert_eq!(api_slug("Mobil's ZSM-5"), "MOBIL_S_ZSM_5");
    }

    #[test]
    fn the_csv_quotes_names_and_descriptions() {
        let list = vec![AchievementDef {
            id: "MILESTONE_X".into(),
            name: "X, \"quoted\"".into(),
            description: "Make X.".into(),
            kind: AchievementKind::Milestone(0),
            art: "substance:1:X".into(),
        }];
        assert_eq!(
            achievements_csv(&list),
            "api_name,name,description,icon,art\nMILESTONE_X,\"X, \"\"quoted\"\"\",\"Make X.\",MILESTONE_X_ACHIEVED.png,substance:1:X\n"
        );
    }
}
