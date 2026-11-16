// src/systems/discovery.rs
//
// Marks substances as "discovered" the moment they appear inside a vessel --
// which is exactly when a reaction produces a new product (and, harmlessly, when
// you drag an already-known ingredient in). Kept out of reaction_check.rs so that
// big file never has to be touched for progression.
use bevy::prelude::*;

use crate::components::{format_formula, InVessel, Ingredient};
use crate::resources::player_progress::PlayerProgress;
use crate::systems::autoplay::GameEvent;
use crate::ui::toasts::{ToastKind, Toasts};

pub fn discovery_system(
    // `Added<InVessel>` fires the frame an ingredient first lands in a vessel
    // (products are spawned with InVessel, so this catches every new creation).
    newly_in_vessel: Query<&Ingredient, Added<InVessel>>,
    mut progress: ResMut<PlayerProgress>,
    mut toasts: ResMut<Toasts>,
    mut events: MessageWriter<GameEvent>,
) {
    if !progress.ready {
        return;
    }
    for ingredient in &newly_in_vessel {
        // Only touch ResMut when it's genuinely new, so the inventory/tech tree rebuilds
        // fire on real discoveries rather than every drag.
        if !progress.discovered.contains(&ingredient.id) {
            progress.discover(ingredient.id);
            events.write(GameEvent::Discovery { id: ingredient.id });
            toasts.push(
                ToastKind::Discovery,
                format!("New discovery: {}  ({})", ingredient.name, format_formula(&ingredient.formula)),
            );
        }
    }
}
