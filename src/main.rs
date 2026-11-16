// src/main.rs
// Release builds for players (`--features gui`) open no console window on Windows.
#![cfg_attr(feature = "gui", windows_subsystem = "windows")]
use bevy::camera::ClearColorConfig;
use bevy::gizmos::config::{DefaultGizmoConfigGroup, GizmoConfigStore};
use bevy::prelude::*;
use bevy::ui::UiSystems;

use bevy::prelude::ApplyDeferred;
use chem_alchemy::ui::codex::{
    codex_button_system, codex_category_tab_system, codex_entry_click_system, codex_link_click_system,
    codex_search_input_system, populate_codex_list_system, spawn_codex, update_codex_detail_system, CodexFilter,
    CodexState,
};
use chem_alchemy::ui::detail_panel::{
    attach_click_observers, selection_button_system, selection_view_system, SelectedSubstance,
};
use chem_alchemy::ui::inventory::{
    category_tab_system, pop_in_system, populate_inventory_system, shelf_hover_system, spawn_inventory_panel,
    InvCategory,
};
use chem_alchemy::ui::reaction_library::{
    populate_reaction_list_system, reaction_lib_button_system, reaction_lib_entry_click_system,
    reaction_lib_link_click_system, reaction_lib_search_system, spawn_reaction_library, update_reaction_detail_system,
    ReactionLibState,
};
use chem_alchemy::ui::tech_tree::{
    populate_tech_views_system, spawn_tech_tree, tech_button_system, tech_mode_system, tech_node_click_system,
    tech_pan_system, update_tech_detail_system, TechTreeState,
};
use chem_alchemy::{
    assets::RonAssetLoader,
    data::{
        reactions::Reactions,
        substances::{SubstancePatches, Substances},
    },
    resources::{
        current_process::CurrentProcess,
        player_progress::{
            load_or_seed_progress_system, save_on_exit_system, save_progress_system, FiredMilestones, Persistence,
            PlayerProgress, SaveClock,
        },
        recipe_database::build_recipe_database,
        ui_fonts::load_ui_fonts,
    },
    systems::{
        achievements::AchievementsPlugin,
        autoplay::{AutoplayConfig, AutoplayPlugin, GameEvent},
        discovery::discovery_system,
        drag_drop::DragDropPlugin,
        link_renderer::draw_links_system,
        reaction_check::{
            fizzle_system, handle_reaction_timers_system, process_button_system, propagate_products_system,
            reaction_check_system, vessel_art_system, vessel_clear_button_system, vessel_delete_button_system,
            vessel_react_button_system, CheckVesselReaction,
        },
        sound::{SoundOutput, SoundPlugin},
    },
    ui::{
        credits::CreditsPlugin, focus::FocusPlugin, onboarding::OnboardingPlugin, process_toolbar, reaction_canvas,
        settings, shell, theme, toasts,
    },
    GameData, UiCameraEntity,
};

fn main() -> AppExit {
    // `--autoplay` runs the scripted review playthrough (see systems/autoplay.rs). It never
    // touches the real save or settings.
    let autoplay = AutoplayConfig::from_args();
    let mut window = Window { title: "Curieosity".to_string(), ..default() };
    if autoplay.is_some() {
        window.resolution = (1280u32, 720u32).into();
        window.title = "Curieosity (review playthrough)".to_string();
    }

    let mut app = App::new();
    // A UI tile or chip despawned in the same frame a command targets it is harmless;
    // log it instead of crashing the game.
    app.set_error_handler(bevy::ecs::error::warn)
        .add_plugins((
            DefaultPlugins.set(WindowPlugin { primary_window: Some(window), ..default() }),
            DragDropPlugin,
            OnboardingPlugin,
            SoundPlugin,
            FocusPlugin,
            CreditsPlugin,
            AchievementsPlugin,
        ))
        .insert_resource(Persistence(autoplay.is_none()))
        // the review run is silent unless asked (`--sound`); its cues are still logged
        .insert_resource(SoundOutput(autoplay.is_none() || std::env::args().any(|a| a == "--sound")))
        .insert_resource(ClearColor(theme::BG))
        .init_asset::<Substances>()
        .init_asset::<Reactions>()
        .init_asset::<SubstancePatches>()
        .init_asset_loader::<RonAssetLoader<Substances>>()
        .init_asset_loader::<RonAssetLoader<Reactions>>()
        .init_asset_loader::<RonAssetLoader<SubstancePatches>>()
        .init_resource::<CurrentProcess>()
        .init_resource::<PlayerProgress>()
        .init_resource::<FiredMilestones>()
        .init_resource::<SaveClock>()
        .init_resource::<InvCategory>()
        .init_resource::<SelectedSubstance>()
        .init_resource::<CodexState>()
        .init_resource::<CodexFilter>()
        .init_resource::<ReactionLibState>()
        .init_resource::<TechTreeState>()
        .init_resource::<settings::SettingsUi>()
        .init_resource::<process_toolbar::ProcessUnlocks>()
        .init_resource::<toasts::Toasts>()
        .add_message::<CheckVesselReaction>()
        .add_message::<GameEvent>()
        .add_systems(
            Startup,
            (
                settings::load_settings,
                load_ui_fonts,
                setup,
                // Run UI spawning AFTER setup so UiCameraEntity is available
                (
                    shell::spawn_header,
                    spawn_inventory_panel,
                    reaction_canvas::spawn_reaction_canvas,
                    process_toolbar::spawn_process_toolbar,
                    spawn_codex,
                    spawn_reaction_library,
                    spawn_tech_tree,
                    settings::spawn_settings,
                    toasts::spawn_toast_stack,
                ),
            )
                .chain(),
        )
        // Content: build the recipe book (applying the authored substance layer), then load
        // the save or seed a new game, then fire milestones.
        .add_systems(
            Update,
            (
                build_recipe_database,
                load_or_seed_progress_system,
                process_toolbar::milestone_system,
                save_progress_system,
            )
                .chain(),
        )
        .add_systems(
            Update,
            (
                populate_inventory_system,
                category_tab_system,
                shelf_hover_system,
                discovery_system,
                attach_click_observers,
                selection_view_system,
                selection_button_system,
                ApplyDeferred,
                vessel_clear_button_system,
                vessel_delete_button_system,
                process_button_system,
                vessel_react_button_system,
                (
                    reaction_check_system,
                    handle_reaction_timers_system,
                    ApplyDeferred,
                    propagate_products_system,
                    ApplyDeferred,
                )
                    .chain(),
                fizzle_system,
                vessel_art_system,
            ),
        )
        .add_systems(
            Update,
            (
                codex_button_system,
                populate_codex_list_system,
                update_codex_detail_system,
                codex_entry_click_system,
                codex_link_click_system,
                codex_category_tab_system,
                codex_search_input_system,
                reaction_lib_button_system,
                reaction_lib_search_system,
                populate_reaction_list_system,
                update_reaction_detail_system,
                reaction_lib_entry_click_system,
                reaction_lib_link_click_system,
            ),
        )
        .add_systems(
            Update,
            (
                tech_button_system,
                tech_mode_system,
                populate_tech_views_system,
                tech_node_click_system,
                update_tech_detail_system,
                tech_pan_system,
            ),
        )
        .add_systems(
            Update,
            (
                process_toolbar::gate_process_buttons_system,
                process_toolbar::new_game_button_system,
                toasts::spawn_toasts_system,
                toasts::fade_toasts_system,
                pop_in_system,
            ),
        )
        // The frame: header, view switching, settings, and the shared button skins (last,
        // so every state change made this frame is reflected in the colours).
        .add_systems(
            Update,
            (
                shell::nav_input_system,
                shell::escape_system,
                shell::nav_highlight_system,
                shell::header_stats_system,
                shell::decorate_bench_system,
                shell::bench_state_system,
                shell::wheel_scroll_system,
                shell::clamp_scroll_system,
                settings::settings_input_system,
                settings::settings_view_system,
                settings::apply_settings_system,
                theme::skin_system,
            )
                .chain(),
        )
        .add_systems(PostUpdate, draw_links_system.after(UiSystems::Layout))
        .add_systems(Last, save_on_exit_system);

    if let Some(cfg) = autoplay {
        app.add_plugins(AutoplayPlugin(cfg));
    }
    // the review run's verdict becomes the process exit code
    app.run()
}

fn setup(mut commands: Commands, asset_server: Res<AssetServer>, mut config_store: ResMut<GizmoConfigStore>) {
    // --- Camera 1: UI (Background) ---
    let ui_cam = commands
        .spawn((
            Camera2d,
            Camera {
                order: 0, // Runs First
                ..default()
            },
        ))
        .id();

    commands.insert_resource(UiCameraEntity(ui_cam));

    // --- Camera 2: Gizmos (Overlay) ---
    commands.spawn((
        Camera2d,
        Camera {
            order: 1,                            // Runs Second (on top)
            clear_color: ClearColorConfig::None, // Transparent
            ..default()
        },
    ));

    // Link curves read better a little thicker than the 1px default.
    let (config, _) = config_store.config_mut::<DefaultGizmoConfigGroup>();
    config.depth_bias = 0.0;
    config.line.width = 2.5;

    commands.insert_resource(GameData {
        substances: asset_server.load("data/substances.ron"),
        reactions: asset_server.load("data/reactions.ron"),
        authored_reactions: asset_server.load("data/authored_reactions.ron"),
        authored_substances: asset_server.load("data/authored_substances.ron"),
    });
}
