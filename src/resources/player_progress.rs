// src/resources/player_progress.rs
//
// What the player has discovered, and the save file that keeps it between sessions.
//
// Saves are built to survive updates:
//   * every save carries a format version, and older formats are read and upgraded;
//   * a vessel or substance this build doesn't know (content changed since the save) is
//     never an error: it is set aside as "dormant" and written back, so an update that
//     brings it back restores it;
//   * writes are atomic (a temporary file renamed over the save), so a crash mid-write
//     can't leave a half-written save;
//   * the save as it stood when the game started is kept as `progress.ron.bak`, and a
//     save that can't be read is moved aside (never overwritten) and the backup used.
use bevy::app::AppExit;
use bevy::platform::collections::HashSet;
use bevy::prelude::*;
use serde::{Deserialize, Deserializer, Serialize};
use std::path::{Path, PathBuf};

use crate::data::common::ProcessType;
use crate::data::substances::Substances;
use crate::resources::recipe_database::RecipeDatabase;
use crate::ui::process_toolbar::ProcessUnlocks;
use crate::ui::toasts::{Journal, ToastKind, Toasts};
use crate::GameData;

/// The save format this build writes. 1 was the first format (no version field); 2 adds
/// the version, the game version that wrote it, and the dormant lists. (The journal of
/// past notifications came later as an optional field: older saves simply have none.)
pub const SAVE_VERSION: u32 = 2;

/// Seconds after the last change before the save is written (changes come in bursts:
/// a reaction, its discoveries, a milestone and its grants).
pub const AUTOSAVE_DELAY: f32 = 2.0;

/// Tracks what the player has discovered. The inventory renders only these ids,
/// which is both the core discovery mechanic AND the fix for trying to spawn
/// tens of thousands of inventory nodes at once.
///
/// Starts empty: `load_or_seed_progress_system` fills it from the save file, or from the
/// authored starting inventory on a new game, once the content is loaded.
#[derive(Resource, Debug, Default)]
pub struct PlayerProgress {
    pub discovered: HashSet<u32>,
    /// True once the save/start set has been applied. Saving is off until then, so a
    /// half-loaded frame can never overwrite a real save with an empty one.
    pub ready: bool,
    /// discoveries from the save that this build's content doesn't have (kept, not shown)
    pub dormant: Vec<u32>,
    /// unlocked vessels from the save that this build doesn't have (kept, not shown)
    pub dormant_vessels: Vec<String>,
}

impl PlayerProgress {
    /// Returns true if this id was newly discovered (wasn't already known).
    pub fn discover(&mut self, id: u32) -> bool {
        self.discovered.insert(id)
    }
}

/// A save, in this build's terms, whatever version it was read from.
#[derive(Debug, Clone, PartialEq, Default)]
pub struct SaveData {
    /// the version it was read from (SAVE_VERSION once written by this build)
    pub version: u32,
    pub discovered: Vec<u32>,
    pub unlocked: Vec<ProcessType>,
    pub dormant: Vec<u32>,
    pub dormant_vessels: Vec<String>,
    /// past notifications as (kind, text), oldest first
    pub journal: Vec<(String, String)>,
}

/// A vessel as written in a save: a bare name such as `Fire`. Read by name, so a vessel
/// this build doesn't have is kept as text instead of failing the whole save.
struct VesselName(String);

impl<'de> Deserialize<'de> for VesselName {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        struct Ident(String);
        impl<'de> Deserialize<'de> for Ident {
            fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
                struct V;
                impl<'de> serde::de::Visitor<'de> for V {
                    type Value = Ident;
                    fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                        f.write_str("a vessel name")
                    }
                    fn visit_str<E: serde::de::Error>(self, v: &str) -> Result<Ident, E> {
                        Ok(Ident(v.to_string()))
                    }
                }
                d.deserialize_identifier(V)
            }
        }
        struct V;
        impl<'de> serde::de::Visitor<'de> for V {
            type Value = VesselName;
            fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
                f.write_str("a vessel name")
            }
            fn visit_enum<A: serde::de::EnumAccess<'de>>(self, a: A) -> Result<VesselName, A::Error> {
                use serde::de::VariantAccess;
                let (name, rest): (Ident, _) = a.variant()?;
                rest.unit_variant()?;
                Ok(VesselName(name.0))
            }
        }
        d.deserialize_enum("Vessel", &[], V)
    }
}

/// The file as read: any version, every field optional.
#[derive(Deserialize, Default)]
#[serde(default)]
struct SaveFile {
    version: u32,
    discovered: Vec<u32>,
    unlocked: Vec<VesselName>,
    dormant: Vec<u32>,
    dormant_vessels: Vec<String>,
    journal: Vec<(String, String)>,
}

/// The file as written.
#[derive(Serialize)]
struct SaveOut<'a> {
    version: u32,
    game: &'a str,
    discovered: &'a [u32],
    unlocked: &'a [ProcessType],
    dormant: &'a [u32],
    dormant_vessels: &'a [String],
    journal: &'a [(String, String)],
}

impl SaveData {
    /// Read a save of any version. Fails only when the text isn't a save at all.
    pub fn parse(text: &str) -> Result<SaveData, String> {
        let file: SaveFile = ron::from_str(text).map_err(|e| e.to_string())?;
        // version 1 had no version field
        let version = if file.version == 0 { 1 } else { file.version };
        let mut save = SaveData {
            version,
            discovered: file.discovered,
            unlocked: Vec::new(),
            dormant: file.dormant,
            dormant_vessels: file.dormant_vessels,
            journal: file.journal,
        };
        for VesselName(name) in file.unlocked {
            match ron::from_str::<ProcessType>(&name) {
                Ok(p) => save.unlocked.push(p),
                Err(_) => save.dormant_vessels.push(name),
            }
        }
        // a dormant vessel this build knows again comes back
        let mut still = Vec::new();
        for name in std::mem::take(&mut save.dormant_vessels) {
            match ron::from_str::<ProcessType>(&name) {
                Ok(p) => save.unlocked.push(p),
                Err(_) => still.push(name),
            }
        }
        save.dormant_vessels = still;
        // Upgrades between formats go here, oldest first. 1 -> 2 changes no data.
        Ok(save)
    }

    /// Split discoveries into what this build's content has and what it doesn't. Unknown
    /// ids go dormant; dormant ids the content has again come back.
    pub fn settle(mut self, known: impl Fn(u32) -> bool) -> SaveData {
        let mut discovered = Vec::new();
        let mut dormant = Vec::new();
        for id in self.discovered.drain(..).chain(self.dormant.drain(..)) {
            if known(id) {
                discovered.push(id);
            } else {
                dormant.push(id);
            }
        }
        discovered.sort_unstable();
        discovered.dedup();
        dormant.sort_unstable();
        dormant.dedup();
        self.discovered = discovered;
        self.dormant = dormant;
        let mut seen = HashSet::new();
        self.unlocked.retain(|p| seen.insert(p.clone()));
        self.dormant_vessels.sort();
        self.dormant_vessels.dedup();
        self
    }

    /// The save as this build writes it (always the current version).
    pub fn to_text(&self) -> String {
        let out = SaveOut {
            version: SAVE_VERSION,
            game: env!("CARGO_PKG_VERSION"),
            discovered: &self.discovered,
            unlocked: &self.unlocked,
            dormant: &self.dormant,
            dormant_vessels: &self.dormant_vessels,
            journal: &self.journal,
        };
        ron::ser::to_string_pretty(&out, ron::ser::PrettyConfig::default().compact_arrays(true)).unwrap_or_default()
    }
}

/// Whether progress and settings are read from and written to disk. The scripted review
/// playthrough turns this off so it never touches the player's real save.
#[derive(Resource)]
pub struct Persistence(pub bool);

impl Default for Persistence {
    fn default() -> Self {
        Self(true)
    }
}

/// Which authored milestones have fired in this game (cleared by New Game, so they can
/// fire again).
#[derive(Resource, Default)]
pub struct FiredMilestones {
    pub fired: HashSet<usize>,
    /// false until the first pass, which applies a loaded save's milestones silently
    pub primed: bool,
}

/// `%APPDATA%\Curieosity\progress.ron` on Windows, `~/.local/share/curieosity/progress.ron`
/// elsewhere, and the app's own storage on Android and iOS. Kept out of the project folder.
pub fn save_path() -> PathBuf {
    let base = app_storage()
        .or_else(|| std::env::var_os("APPDATA").map(|p| PathBuf::from(p).join("Curieosity")))
        .or_else(|| std::env::var_os("XDG_DATA_HOME").map(|p| PathBuf::from(p).join("curieosity")))
        .or_else(|| std::env::var_os("HOME").map(|p| PathBuf::from(p).join(".local/share/curieosity")))
        .unwrap_or_else(|| PathBuf::from("."));
    base.join("progress.ron")
}

/// Android: the app's private storage, kept until the app is uninstalled.
#[cfg(target_os = "android")]
fn app_storage() -> Option<PathBuf> {
    bevy::android::ANDROID_APP.get().and_then(|app| app.internal_data_path())
}

/// iOS: the app's own Application Support folder (backed up with the device, kept until the
/// app is deleted). HOME is the app's sandbox there.
#[cfg(target_os = "ios")]
fn app_storage() -> Option<PathBuf> {
    std::env::var_os("HOME").map(|home| PathBuf::from(home).join("Library/Application Support/Curieosity"))
}

#[cfg(not(any(target_os = "android", target_os = "ios")))]
fn app_storage() -> Option<PathBuf> {
    None
}

/// The copy of the save taken when the game started.
pub fn backup_path(save: &Path) -> PathBuf {
    save.with_extension("ron.bak")
}

/// Write a file so that it is either the old version or the new one, never half of each:
/// the text goes to a temporary file first, which then replaces the real one.
pub fn write_atomic(path: &Path, text: &str) -> std::io::Result<()> {
    use std::io::Write;
    if let Some(dir) = path.parent() {
        std::fs::create_dir_all(dir)?;
    }
    let tmp = path.with_extension("tmp");
    {
        let mut f = std::fs::File::create(&tmp)?;
        f.write_all(text.as_bytes())?;
        f.sync_all()?;
    }
    std::fs::rename(&tmp, path)
}

/// What reading the save found.
#[derive(Debug)]
pub enum ReadOutcome {
    /// no save yet: a new game
    Missing,
    /// read (from the backup when the save itself couldn't be); `set_aside` is where an
    /// unreadable save was moved
    Loaded { save: SaveData, from_backup: bool, set_aside: Option<PathBuf> },
    /// neither the save nor its backup could be read; the save was moved to `set_aside`
    Lost { set_aside: PathBuf },
}

/// Read the save at `path`, falling back to its backup. A save that can't be read is
/// renamed (`progress.unreadable-<seconds>.ron`), never left where a new save would
/// overwrite it.
pub fn read_progress(path: &Path) -> ReadOutcome {
    let Ok(text) = std::fs::read_to_string(path) else {
        return ReadOutcome::Missing;
    };
    if let Ok(save) = SaveData::parse(&text) {
        return ReadOutcome::Loaded { save, from_backup: false, set_aside: None };
    }
    let stamp = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0);
    let aside = path.with_file_name(format!("progress.unreadable-{stamp}.ron"));
    if std::fs::rename(path, &aside).is_err() {
        let _ = std::fs::copy(path, &aside);
    }
    match std::fs::read_to_string(backup_path(path)).ok().and_then(|t| SaveData::parse(&t).ok()) {
        Some(save) => ReadOutcome::Loaded { save, from_backup: true, set_aside: Some(aside) },
        None => ReadOutcome::Lost { set_aside: aside },
    }
}

/// Once the content is loaded: restore the save if there is one, otherwise start a new
/// game from the authored starting inventory.
#[allow(clippy::too_many_arguments)]
pub fn load_or_seed_progress_system(
    db: Option<Res<RecipeDatabase>>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    persistence: Res<Persistence>,
    mut progress: ResMut<PlayerProgress>,
    mut unlocks: ResMut<ProcessUnlocks>,
    mut toasts: ResMut<Toasts>,
    mut journal: ResMut<Journal>,
) {
    if progress.ready {
        return;
    }
    let Some(db) = db else { return };
    let Some(subs) = substances.get(&game_data.substances) else { return };

    let path = save_path();
    let outcome = if persistence.0 { read_progress(&path) } else { ReadOutcome::Missing };
    let seed = |progress: &mut PlayerProgress| {
        progress.discovered = db.start.iter().copied().collect();
        info!("New game: {} starting substances.", progress.discovered.len());
    };
    match outcome {
        ReadOutcome::Loaded { save, from_backup, set_aside } => {
            let from = save.version;
            let save = save.settle(|id| subs.0.contains_key(&id));
            if save.discovered.is_empty() {
                seed(&mut progress);
            } else {
                progress.discovered = save.discovered.iter().copied().collect();
            }
            progress.dormant = save.dormant.clone();
            progress.dormant_vessels = save.dormant_vessels.clone();
            *journal = Journal::from_pairs(&save.journal);
            for p in save.unlocked {
                unlocks.0.insert(p);
            }
            info!(
                "Loaded save (format {from}): {} discoveries, {} set aside for later content.",
                progress.discovered.len(),
                progress.dormant.len() + progress.dormant_vessels.len()
            );
            if let Some(aside) = set_aside {
                toasts.push(
                    ToastKind::Hint,
                    format!("Your save couldn't be read, so the backup from your last session was restored. The unreadable file was kept as {}.", file_name(&aside)),
                );
            } else if !from_backup {
                // the save as it stood at the start of this session
                if let Err(e) = std::fs::copy(&path, backup_path(&path)) {
                    warn!("Could not back up the save: {e}");
                }
            }
        }
        ReadOutcome::Lost { set_aside } => {
            seed(&mut progress);
            toasts.push(
                ToastKind::Hint,
                format!(
                    "Your save couldn't be read, so this is a new game. The old file was kept as {}.",
                    file_name(&set_aside)
                ),
            );
        }
        ReadOutcome::Missing => seed(&mut progress),
    }
    progress.ready = true;
}

fn file_name(p: &Path) -> String {
    p.file_name().map(|n| n.to_string_lossy().into_owned()).unwrap_or_default()
}

/// When the save has unsaved changes, and since when.
#[derive(Resource, Default)]
pub struct SaveClock {
    pending_since: Option<f32>,
    /// saves written this session (the checks read it)
    pub writes: u32,
}

impl SaveClock {
    /// true while a change is waiting to be written
    pub fn pending(&self) -> bool {
        self.pending_since.is_some()
    }

    fn write(
        &mut self,
        progress: &PlayerProgress,
        unlocks: &ProcessUnlocks,
        journal: &Journal,
        persistence: &Persistence,
    ) {
        self.pending_since = None;
        self.writes += 1;
        if !persistence.0 {
            return;
        }
        let path = save_path();
        if let Err(e) = write_atomic(&path, &current_save(progress, unlocks, journal).to_text()) {
            warn!("Could not write save {}: {}", path.display(), e);
        }
    }
}

/// Autosave: a short while after discoveries, unlocks or the journal change.
pub fn save_progress_system(
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    journal: Res<Journal>,
    persistence: Res<Persistence>,
    time: Res<Time>,
    mut clock: ResMut<SaveClock>,
) {
    if !progress.ready {
        return;
    }
    let now = time.elapsed_secs();
    if progress.is_changed() || unlocks.is_changed() || journal.is_changed() {
        clock.pending_since.get_or_insert(now);
    }
    if clock.pending_since.is_some_and(|since| now - since >= AUTOSAVE_DELAY) {
        clock.write(&progress, &unlocks, &journal, &persistence);
    }
}

/// On the way out (the window closing), anything not yet saved is written. Runs in
/// `Last`, the same frame the exit is requested.
pub fn save_on_exit_system(
    mut exit: MessageReader<AppExit>,
    progress: Res<PlayerProgress>,
    unlocks: Res<ProcessUnlocks>,
    journal: Res<Journal>,
    persistence: Res<Persistence>,
    mut clock: ResMut<SaveClock>,
) {
    if exit.read().count() > 0 && progress.ready && clock.pending() {
        clock.write(&progress, &unlocks, &journal, &persistence);
    }
}

/// The save for the game as it stands.
pub fn current_save(progress: &PlayerProgress, unlocks: &ProcessUnlocks, journal: &Journal) -> SaveData {
    let mut discovered: Vec<u32> = progress.discovered.iter().copied().collect();
    discovered.sort_unstable();
    let mut unlocked: Vec<ProcessType> = unlocks.0.iter().cloned().collect();
    unlocked.sort_by_key(|p| format!("{p:?}"));
    SaveData {
        version: SAVE_VERSION,
        discovered,
        unlocked,
        dormant: progress.dormant.clone(),
        dormant_vessels: progress.dormant_vessels.clone(),
        journal: journal.to_pairs(),
    }
}

/// Before New Game wipes progress, the old save is kept as `progress.before-new-game.ron`.
pub fn keep_copy_before_new_game() {
    let path = save_path();
    if path.exists() {
        let _ = std::fs::copy(&path, path.with_file_name("progress.before-new-game.ron"));
    }
}

/// Wipe progress back to the authored starting inventory (the toolbar's New Game button).
pub fn reset_progress(
    progress: &mut PlayerProgress,
    unlocks: &mut ProcessUnlocks,
    fired: &mut FiredMilestones,
    db: &RecipeDatabase,
) {
    progress.discovered = db.start.iter().copied().collect();
    progress.dormant.clear();
    progress.dormant_vessels.clear();
    *unlocks = ProcessUnlocks::default();
    fired.fired.clear();
    fired.primed = true;
}

#[cfg(test)]
mod tests {
    use super::*;

    fn scratch(name: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!("curieosity-save-test-{name}-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        dir.join("progress.ron")
    }

    #[test]
    fn a_first_format_save_reads_and_upgrades() {
        let v1 = "(discovered:[1,5,8],unlocked:[Mix,Heat])";
        let save = SaveData::parse(v1).unwrap();
        assert_eq!(save.version, 1);
        assert_eq!(save.discovered, vec![1, 5, 8]);
        assert_eq!(save.unlocked, vec![ProcessType::Mix, ProcessType::Heat]);
        let again = SaveData::parse(&save.to_text()).unwrap();
        assert_eq!(again.version, SAVE_VERSION);
        assert_eq!((again.discovered, again.unlocked), (save.discovered, save.unlocked));
    }

    #[test]
    fn unknown_vessels_and_substances_are_kept_not_lost() {
        let save = SaveData::parse("(discovered:[1,5,424242],unlocked:[Mix,Replicator])").unwrap();
        assert_eq!(save.unlocked, vec![ProcessType::Mix]);
        assert_eq!(save.dormant_vessels, vec!["Replicator".to_string()]);
        let settled = save.settle(|id| id != 424242);
        assert_eq!(settled.discovered, vec![1, 5]);
        assert_eq!(settled.dormant, vec![424242]);
        // written back and read by a later build that has the substance again
        let later = SaveData::parse(&settled.to_text()).unwrap().settle(|_| true);
        assert_eq!(later.discovered, vec![1, 5, 424242]);
        assert!(later.dormant.is_empty());
        assert_eq!(later.dormant_vessels, vec!["Replicator".to_string()]);
    }

    #[test]
    fn the_journal_is_saved_and_old_saves_have_none() {
        let mut j = Journal::default();
        j.push(ToastKind::Discovery, "New: Quicklime");
        j.push(ToastKind::Milestone, "Copper! The furnace becomes a smelter.");
        let save = SaveData { version: SAVE_VERSION, discovered: vec![1], journal: j.to_pairs(), ..Default::default() };
        let back = SaveData::parse(&save.to_text()).unwrap();
        assert_eq!(Journal::from_pairs(&back.journal).0, j.0);
        assert!(SaveData::parse("(discovered:[1],unlocked:[Mix])").unwrap().journal.is_empty());
        // only the newest are kept
        let mut long = Journal::default();
        for i in 0..crate::ui::toasts::JOURNAL_MAX + 25 {
            long.push(ToastKind::Discovery, format!("#{i}"));
        }
        assert_eq!(long.0.len(), crate::ui::toasts::JOURNAL_MAX);
        assert_eq!(long.0[0].text, "#25");
    }

    #[test]
    fn writes_are_atomic_and_leave_no_temp_file() {
        let path = scratch("atomic");
        write_atomic(&path, "first").unwrap();
        write_atomic(&path, "second").unwrap();
        assert_eq!(std::fs::read_to_string(&path).unwrap(), "second");
        assert!(!path.with_extension("tmp").exists());
    }

    #[test]
    fn an_unreadable_save_is_moved_aside_and_the_backup_used() {
        let path = scratch("unreadable");
        std::fs::write(backup_path(&path), "(discovered:[1,5],unlocked:[Mix])").unwrap();
        std::fs::write(&path, "this is not a save {{{").unwrap();
        match read_progress(&path) {
            ReadOutcome::Loaded { save, from_backup: true, set_aside: Some(aside) } => {
                assert_eq!(save.discovered, vec![1, 5]);
                assert!(aside.exists(), "the unreadable save is kept");
                assert_eq!(std::fs::read_to_string(aside).unwrap(), "this is not a save {{{");
                assert!(!path.exists(), "nothing is left where the next save would overwrite it");
            }
            other => panic!("expected the backup, got {other:?}"),
        }
    }

    #[test]
    fn an_unreadable_save_without_a_backup_is_still_kept() {
        let path = scratch("lost");
        std::fs::write(&path, "garbage").unwrap();
        match read_progress(&path) {
            ReadOutcome::Lost { set_aside } => assert_eq!(std::fs::read_to_string(set_aside).unwrap(), "garbage"),
            other => panic!("expected Lost, got {other:?}"),
        }
        assert!(matches!(read_progress(&scratch("missing")), ReadOutcome::Missing));
    }
}
