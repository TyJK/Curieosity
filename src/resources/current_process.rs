// src/resources/current_process.rs

use bevy::prelude::*;

use crate::data::common::ProcessType;

/// Resource tracking the currently selected process from the toolbar.
#[derive(Resource, Clone)]
pub struct CurrentProcess(pub ProcessType);

impl Default for CurrentProcess {
    fn default() -> Self {
        // Neutral default
        Self(ProcessType::Mix)
    }
}
