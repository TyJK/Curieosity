// src/ui/detail_panel.rs
//
// Selecting a substance on the shelf. A click selects it (click it again, press Esc or the
// x to let go): the tile lights up and the shelf header shows what it is, with a button to
// open its page in the Substance Library. While something is selected, clicking a vessel
// puts it in (see drag_drop.rs); dragging works as always. A double-tap on a tile puts it
// straight into the vessel used last.
use crate::ui::Interaction;
use bevy::ecs::system::entity_command::observe;
use bevy::prelude::*;

use crate::components::{format_formula, Draggable, Ingredient};
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::drag_drop::DragMoved;
use crate::ui::codex::CodexState;
use crate::ui::inventory::{element_tile_color, is_element_formula, ShelfTile};
use crate::ui::theme::{self, Weight};
use crate::GameData;

/// The substance selected on the shelf, if any.
#[derive(Resource, Default)]
pub struct SelectedSubstance(pub Option<u32>);

#[derive(Component)]
pub struct SelectionHint;
#[derive(Component)]
pub struct SelectionReadout;
#[derive(Component)]
pub struct SelectionThumb;
#[derive(Component)]
pub struct SelectionName;
#[derive(Component)]
pub struct SelectionFormula;
#[derive(Component)]
pub struct SelectionOpenButton;
#[derive(Component)]
pub struct SelectionClearButton;

/// Each shelf tile and vessel chip, as it spawns, gets the click that selects it. A chip can
/// be gone again before this lands (used up by a reaction in the same frame): it needs no
/// click then, so that is not an error.
pub fn attach_click_observers(mut commands: Commands, new_items: Query<Entity, (Added<Draggable>, With<Ingredient>)>) {
    for entity in &new_items {
        commands.entity(entity).queue_silenced(observe(on_item_click));
    }
}

/// Two taps on one shelf tile within this long (seconds) are a double-tap.
pub const DOUBLE_TAP: f64 = 0.4;

/// The last tap on a shelf tile and when it was (real seconds), for spotting a double-tap.
#[derive(Resource, Default)]
pub struct LastTap(pub Option<(Entity, f64)>);

#[allow(clippy::too_many_arguments)]
fn on_item_click(
    mut trigger: On<PointerClick>,
    ingredients: Query<&Ingredient>,
    tiles: Query<(), With<ShelfTile>>,
    moved: Query<(), With<DragMoved>>,
    mut selected: ResMut<SelectedSubstance>,
    time: Res<Time<Real>>,
    mut last: ResMut<LastTap>,
    mut add: MessageWriter<crate::systems::drag_drop::AddToActive>,
) {
    trigger.propagate(false);
    // a drag that ends back on its own tile is not a click
    if trigger.button != PointerButton::Primary || moved.contains(trigger.entity) {
        return;
    }
    let Ok(ing) = ingredients.get(trigger.entity) else { return };
    let now = time.elapsed_secs_f64();
    let double =
        tiles.contains(trigger.entity) && last.0.is_some_and(|(e, at)| e == trigger.entity && now - at <= DOUBLE_TAP);
    if double {
        // the first tap selected it (or let it go): keep it selected, and fill the vessel
        selected.0 = Some(ing.id);
        add.write(crate::systems::drag_drop::AddToActive(ing.id));
        last.0 = None;
        return;
    }
    last.0 = Some((trigger.entity, now));
    selected.0 = if selected.0 == Some(ing.id) { None } else { Some(ing.id) };
}

/// The right-hand end of the shelf header: a hint, or the selection with its buttons.
pub fn spawn_selection_bar(bar: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer) {
    bar.spawn((
        SelectionHint,
        theme::label(fonts, "tap to select · double-tap to fill", theme::XS, Weight::Regular, theme::TEXT_3),
        Node { margin: UiRect::left(Val::Px(14.0)), ..default() },
    ));
    bar.spawn((
        SelectionReadout,
        Node {
            border_radius: BorderRadius::all(Val::Px(theme::R_MD)),
            display: Display::None,
            align_items: AlignItems::Center,
            column_gap: Val::Px(8.0),
            margin: UiRect::left(Val::Px(12.0)),
            padding: UiRect::new(Val::Px(4.0), Val::Px(4.0), Val::Px(2.0), Val::Px(2.0)),
            border: UiRect::all(Val::Px(1.0)),
            ..default()
        },
        BackgroundColor(theme::mix(theme::SURFACE, theme::CYAN, 0.08)),
        BorderColor::all(theme::CYAN.with_alpha(0.6)),
    ))
    .with_children(|r| {
        r.spawn((
            SelectionThumb,
            Node {
                width: Val::Px(26.0),
                height: Val::Px(26.0),
                align_items: AlignItems::Center,
                justify_content: JustifyContent::Center,
                ..default()
            },
        ));
        // one line each, cut short rather than wrapped
        r.spawn(Node {
            flex_direction: FlexDirection::Column,
            max_width: Val::Px(190.0),
            overflow: Overflow::clip(),
            ..default()
        })
        .with_children(|c| {
            c.spawn((
                SelectionName,
                theme::label(fonts, "", theme::SM, Weight::Semibold, theme::TEXT),
                TextLayout::no_wrap(),
            ));
            c.spawn((
                SelectionFormula,
                theme::label(fonts, "", 10.5, Weight::Regular, theme::CYAN),
                TextLayout::no_wrap(),
            ));
        });
        theme::spawn_icon_button(
            r,
            assets,
            "book",
            26.0,
            theme::TEXT,
            (SelectionOpenButton, crate::ui::onboarding::Tip::Text("Library", "Open it in the Substance Library.")),
        );
        theme::spawn_icon_button(r, assets, "close", 26.0, theme::TEXT_2, SelectionClearButton);
    });
}

/// Keep the header readout and the tile highlight in step with the selection.
pub fn selection_view_system(
    mut commands: Commands,
    mut selected: ResMut<SelectedSubstance>,
    progress: Res<PlayerProgress>,
    game_data: Res<GameData>,
    substances: Res<Assets<Substances>>,
    fonts: Res<UiFonts>,
    assets: Res<AssetServer>,
    mut readout: Query<&mut Node, With<SelectionReadout>>,
    thumb: Query<Entity, With<SelectionThumb>>,
    mut name: Query<&mut Text, (With<SelectionName>, Without<SelectionFormula>)>,
    mut formula: Query<&mut Text, (With<SelectionFormula>, Without<SelectionName>)>,
    mut tiles: Query<(&Ingredient, &ShelfTile, &Interaction, &mut BorderColor, &mut BackgroundColor)>,
    new_tiles: Query<(), Added<ShelfTile>>,
) {
    // a new game can take the selected substance away
    if progress.is_changed() {
        if let Some(id) = selected.0 {
            if !progress.discovered.contains(&id) {
                selected.0 = None;
            }
        }
    }
    if !selected.is_changed() && new_tiles.is_empty() {
        return;
    }
    let sel = selected.0;
    for (ing, tile, i, mut border, mut bg) in &mut tiles {
        let (b, c) = tile.look(*i != Interaction::None, Some(ing.id) == sel);
        bg.0 = b;
        *border = BorderColor::all(c);
    }
    if !selected.is_changed() {
        return;
    }
    let sub = sel.and_then(|id| substances.get(&game_data.substances).and_then(|s| s.0.get(&id)));
    // (the hint's own display is inventory::fit_dock_system's: it also hides on a narrow screen)
    if let Ok(mut n) = readout.single_mut() {
        n.display = if sub.is_some() { Display::Flex } else { Display::None };
    }
    let Some(sub) = sub else { return };
    if let Ok(mut t) = name.single_mut() {
        t.0 = sub.name.clone();
    }
    if let Ok(mut t) = formula.single_mut() {
        t.0 = format_formula(&sub.formula);
    }
    if let Ok(th) = thumb.single() {
        commands.entity(th).despawn_children();
        commands.entity(th).with_children(|t| {
            if sub.element_info.is_some() || is_element_formula(&sub.formula) {
                let c = element_tile_color(&sub.formula);
                let sym: String = sub.formula.chars().filter(|ch| ch.is_alphabetic()).collect();
                t.spawn(theme::label(&fonts, sym, 15.0, Weight::Bold, c));
            } else {
                t.spawn((
                    ImageNode::new(assets.load(format!("structures/{}.png", sub.id))),
                    Node { width: Val::Px(26.0), height: Val::Px(26.0), ..default() },
                ));
            }
        });
    }
}

/// The readout's buttons: open the selection in the Substance Library, or let it go.
pub fn selection_button_system(
    open: Query<&Interaction, (Changed<Interaction>, With<SelectionOpenButton>)>,
    clear: Query<&Interaction, (Changed<Interaction>, With<SelectionClearButton>)>,
    mut selected: ResMut<SelectedSubstance>,
    mut codex: ResMut<CodexState>,
) {
    for i in &open {
        if *i == Interaction::Pressed {
            if let Some(id) = selected.0 {
                codex.open = true;
                codex.selected = Some(id);
            }
        }
    }
    for i in &clear {
        if *i == Interaction::Pressed {
            selected.0 = None;
        }
    }
}
