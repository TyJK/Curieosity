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
    pub reactions: Handle<Reactions>,
    /// Hand-authored tech-tree reactions (real names + stoichiometry), merged into the
    /// RecipeDatabase alongside the scraped `reactions`.
    pub authored_reactions: Handle<Reactions>,
    /// The authored substance layer (canon names, formulas, narrative, links), applied
    /// over `substances` when the RecipeDatabase is built.
    pub authored_substances: Handle<SubstancePatches>,
}

// FIX: New resource to store the UI Camera ID
#[derive(Resource)]
pub struct UiCameraEntity(pub Entity);
