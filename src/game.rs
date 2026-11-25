// src/game.rs
//
// The whole game as one App. It lives in the library so that both the desktop program
// (src/main.rs) and the Android build (android/src/lib.rs) start the same thing.
use bevy::camera::ClearColorConfig;
use bevy::gizmos::config::{DefaultGizmoConfigGroup, GizmoConfigStore};
use bevy::prelude::*;
use bevy::ui::UiSystems;

use crate::ui::codex::{
    codex_button_system, codex_category_tab_system, codex_entry_click_system, codex_link_click_system,
    codex_search_input_system, populate_codex_list_system, spawn_codex, update_codex_detail_system, CodexFilter,
    CodexState,
};
use crate::ui::detail_panel::{
    attach_click_observers, selection_button_system, selection_view_system, SelectedSubstance,
};
use crate::ui::inventory::{
    category_tab_system, pop_in_system, populate_inventory_system, shelf_hover_system, spawn_inventory_panel,
    InvCategory,
};
use crate::ui::reaction_library::{
    populate_reaction_list_system, reaction_lib_button_system, reaction_lib_entry_click_system,
    reaction_lib_link_click_system, reaction_lib_search_system, spawn_reaction_library, update_reaction_detail_system,
    ReactionLibState,
};
use crate::ui::tech_tree::{
    populate_tech_views_system, spawn_tech_tree, tech_button_system, tech_mode_system, tech_node_click_system,
    tech_pan_system, tech_reveal_system, tech_selection_links_system, update_tech_detail_system, TechLinks,
    TechTreeState,
};
use crate::{
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
            fizzle_system, handle_reaction_timers_system, place_vessel_system, propagate_products_system,
            reaction_check_system, vessel_art_system, CheckVesselReaction,
        },
        sound::{SoundOutput, SoundPlugin},
    },
    ui::{
        credits::CreditsPlugin, focus::FocusPlugin, onboarding::OnboardingPlugin, process_toolbar, reaction_canvas,
        settings, shell, theme, toasts,
    },
    GameData, UiCameraEntity,
};
use bevy::prelude::ApplyDeferred;

pub fn run() -> AppExit {
    // `--autoplay` runs the scripted review playthrough (see systems/autoplay.rs). It never
    // touches the real save or settings.
    let autoplay = AutoplayConfig::from_args();
    let mut window = Window { title: "Curieosity".to_string(), ..default() };
    if let Some(cfg) = &autoplay {
        window.resolution = cfg.window.into();
        window.title = "Curieosity (review playthrough)".to_string();
    }
    if crate::platform::PHONE {
        window.mode = bevy::window::WindowMode::BorderlessFullscreen(MonitorSelection::Primary);
        window.resizable = false;
    }

    let mut app = App::new();
    // Draw only while something changes (keep_drawing_system asks for each frame), and tick
    // slowly otherwise: a phone or laptop then barely spends battery on a still screen. A
    // review drives its own frames, so it runs flat out; and Steam's overlay draws over the
    // game's frames, so a Steam build keeps drawing too.
    if autoplay.is_none() && !cfg!(feature = "steam") {
        app.insert_resource(bevy::winit::WinitSettings {
            focused_mode: bevy::winit::UpdateMode::reactive(crate::platform::IDLE_TICK),
            unfocused_mode: bevy::winit::UpdateMode::reactive_low_power(std::time::Duration::from_secs(1)),
        });
    }
    // A UI tile or chip despawned in the same frame a command targets it is harmless;
    // log it instead of crashing the game.
    app.set_error_handler(bevy::ecs::error::warn)
        .add_plugins((
            DefaultPlugins.set(WindowPlugin { primary_window: Some(window), ..default() }),
            DragDropPlugin,
            OnboardingPlugin,
            SoundPlugin,
            FocusPlugin,
            crate::ui::ButtonPlugin,
            crate::ui::discovery_card::DiscoveryCardPlugin,
            CreditsPlugin,
            AchievementsPlugin,
            crate::ui::bench_controls::BenchControlsPlugin,
            process_toolbar::VesselPickerPlugin,
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
        .init_asset::<crate::data::pages::Pages>()
        .init_asset_loader::<RonAssetLoader<crate::data::pages::Pages>>()
        .init_resource::<CurrentProcess>()
        .init_resource::<PlayerProgress>()
        .init_resource::<FiredMilestones>()
        .init_resource::<SaveClock>()
        .init_resource::<InvCategory>()
        .init_resource::<SelectedSubstance>()
        .init_resource::<crate::ui::detail_panel::LastTap>()
        .init_resource::<CodexState>()
        .init_resource::<CodexFilter>()
        .init_resource::<ReactionLibState>()
        .init_resource::<TechTreeState>()
        .init_resource::<TechLinks>()
        .init_resource::<crate::ui::tech_tree::TechLayout>()
        .init_resource::<settings::SettingsUi>()
        .insert_resource(settings::FitInterface(autoplay.as_ref().is_some_and(|c| c.fit_screen)))
        .insert_resource(settings::ScaleOverride(autoplay.as_ref().and_then(|c| c.scale)))
        .init_resource::<process_toolbar::ProcessUnlocks>()
        .init_resource::<toasts::Toasts>()
        .init_resource::<toasts::ToastRoom>()
        .init_resource::<toasts::Journal>()
        .init_resource::<toasts::JournalUi>()
        .init_resource::<crate::ui::hint::HintState>()
        .init_resource::<crate::ui::inventory::ShelfSearch>()
        .init_resource::<crate::ui::inventory::TypingBox>()
        .init_resource::<crate::platform::SoftKeyboard>()
        .init_resource::<crate::ui::shell::Portrait>()
        .init_resource::<crate::ui::inventory::Dock>()
        .init_resource::<crate::ui::inventory::ShelfDrag>()
        .init_resource::<crate::ui::inventory::ShelfMenu>()
        .init_resource::<crate::platform::KeyboardInset>()
        .add_plugins(crate::resources::score::ScorePlugin)
        .add_plugins(crate::ui::curriculum::CurriculumPlugin)
        .add_message::<CheckVesselReaction>()
        .add_message::<GameEvent>()
        .add_message::<shell::TouchScroll>()
        .add_message::<process_toolbar::NewGameStarted>()
        // the title, the notice and the menu; review runs and `--skip-title` start in the lab
        .insert_resource(crate::ui::main_menu::MainMenu::starting(
            autoplay.is_some() || std::env::args().any(|a| a == "--skip-title"),
        ))
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
                    crate::ui::inventory::spawn_shelf_menu,
                    process_toolbar::spawn_vessel_picker,
                    crate::ui::bench_controls::spawn_confirm,
                    spawn_codex,
                    spawn_reaction_library,
                    crate::ui::curriculum::spawn_curriculum,
                    spawn_tech_tree,
                    settings::spawn_settings,
                    toasts::spawn_toast_stack,
                    toasts::spawn_journal,
                    crate::ui::main_menu::spawn_main_menu,
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
                crate::resources::player_progress::discovery_order_system,
                save_progress_system,
            )
                .chain(),
        )
        .add_systems(
            Update,
            (
                (populate_inventory_system, crate::ui::inventory::shelf_window_system).chain(),
                (crate::platform::keyboard_inset_system, crate::ui::inventory::fit_dock_system).chain(),
                (category_tab_system, crate::ui::inventory::shelf_menu_system).chain(),
                crate::ui::inventory::shelf_search_system,
                shelf_hover_system,
                crate::ui::inventory::shelf_selection_outline_system,
                discovery_system,
                attach_click_observers,
                selection_view_system,
                selection_button_system,
                ApplyDeferred,
                place_vessel_system,
                (
                    reaction_check_system,
                    handle_reaction_timers_system,
                    ApplyDeferred,
                    propagate_products_system,
                    ApplyDeferred,
                )
                    .chain(),
                (
                    fizzle_system,
                    crate::systems::reaction_check::decay_system,
                    crate::systems::reaction_check::merge_chips_system,
                ),
                vessel_art_system,
                crate::systems::reaction_check::vessel_fit_system,
            ),
        )
        .add_systems(
            Update,
            (
                codex_button_system,
                (populate_codex_list_system, crate::ui::codex::codex_window_system).chain(),
                update_codex_detail_system,
                codex_entry_click_system,
                codex_link_click_system,
                codex_category_tab_system,
                codex_search_input_system,
                reaction_lib_button_system,
                reaction_lib_search_system,
                (populate_reaction_list_system, crate::ui::reaction_library::reaction_lib_window_system).chain(),
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
                crate::ui::tech_tree::tech_graph_window_system,
                crate::ui::tech_tree::tech_list_window_system,
                tech_node_click_system,
                tech_reveal_system,
                tech_selection_links_system,
                update_tech_detail_system,
                tech_pan_system,
                crate::ui::tech_tree::tech_toolbar_fit_system,
            )
                .chain(),
        )
        .add_systems(
            Update,
            (
                process_toolbar::new_game_button_system,
                (
                    crate::ui::hint::spawn_hint_ui,
                    crate::ui::hint::hint_input_system,
                    crate::ui::hint::hint_progress_system,
                    crate::ui::hint::hint_suggest_system,
                    crate::ui::hint::hint_view_system,
                )
                    .chain(),
                toasts::spawn_toasts_system,
                toasts::fade_toasts_system,
                toasts::journal_input_system,
                toasts::journal_view_system,
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
                shell::bench_zoom_controls_system,
                crate::ui::main_menu::main_menu_system,
                crate::ui::main_menu::main_menu_button_system,
                crate::ui::main_menu::menu_float_system,
                shell::wheel_scroll_system,
                shell::touch_scroll_system,
                shell::clamp_scroll_system,
                (shell::portrait_system, shell::portrait_layout_system).chain(),
                settings::settings_input_system,
                settings::fit_interface_system,
                settings::settings_view_system,
                settings::apply_settings_system,
                theme::skin_system,
            )
                .chain(),
        )
        .add_systems(PostUpdate, draw_links_system.after(UiSystems::Layout))
        .add_systems(Last, save_on_exit_system)
        .init_resource::<crate::platform::Drawing>()
        .add_systems(Last, crate::platform::keep_drawing_system);

    #[cfg(not(any(target_os = "android", target_os = "ios")))]
    app.add_systems(Update, crate::platform::window_icon_system);
    #[cfg(target_os = "ios")]
    app.add_systems(PreUpdate, crate::platform::ios_keyboard_system.after(bevy::input::InputSystems))
        .add_systems(Last, crate::platform::ios_open_url_system);
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
        authored_reactions: asset_server.load("data/authored_reactions.ron"),
        authored_substances: asset_server.load("data/authored_substances.ron"),
        pages: asset_server.load("data/pages.ron"),
    });
}
