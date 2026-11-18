// src/lib.rs
use bevy::prelude::*;
use data::{
    reactions::Reactions,
    substances::{SubstancePatches, Substances},
};

pub mod assets;
pub mod components;
pub mod data;
pub mod game;
pub mod platform;
pub mod resources;
pub mod systems;
pub mod ui;

#[derive(States, Debug, Clone, PartialEq, Eq, Hash, Default)]
pub enum AppState {
    #[default]
    Loading,
    MainMenu,
    InGame,
}

#[derive(Resource)]
pub struct GameData {
    pub substances: Handle<Substances>,
    /// The game's reactions: every one is authored (real names + stoichiometry), with the
    /// eras, start kit and milestones they progress through.
    pub authored_reactions: Handle<Reactions>,
    /// The authored substance layer (canon names, formulas, narrative, links), applied
    /// over `substances` when the RecipeDatabase is built.
    pub authored_substances: Handle<SubstancePatches>,
}

// FIX: New resource to store the UI Camera ID
#[derive(Resource)]
pub struct UiCameraEntity(pub Entity);
