// src/ui/detail_panel.rs
//
// Selecting a substance on the shelf. A click selects it (click it again, press Esc or the
// x to let go): the tile lights up and the shelf header shows what it is, with a button to
// open its page in the Substance Library. While something is selected, clicking a vessel
// puts it in (see drag_drop.rs); dragging works as always.
use bevy::prelude::*;

use crate::components::{format_formula, Draggable, Ingredient};
use crate::data::substances::Substances;
use crate::resources::player_progress::PlayerProgress;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::drag_drop::DragMoved;
use crate::ui::codex::CodexState;
use crate::ui::inventory::{element_tile_color, is_element_formula, ShelfTile};
use crate::ui::theme::{self, Kind, Weight};
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

/// Each shelf tile, as it spawns, gets the click that selects it.
pub fn attach_click_observers(mut commands: Commands, new_items: Query<Entity, (Added<Draggable>, With<Ingredient>)>) {
    for entity in &new_items {
        commands.entity(entity).observe(on_item_click);
    }
}

fn on_item_click(
    mut trigger: On<Pointer<Click>>,
    ingredients: Query<&Ingredient>,
    moved: Query<(), With<DragMoved>>,
    mut selected: ResMut<SelectedSubstance>,
) {
    trigger.propagate(false);
    // a drag that ends back on its own tile is not a click
    if trigger.button != PointerButton::Primary || moved.contains(trigger.entity) {
        return;
    }
    if let Ok(ing) = ingredients.get(trigger.entity) {
        selected.0 = if selected.0 == Some(ing.id) { None } else { Some(ing.id) };
    }
}

/// The right-hand end of the shelf header: a hint, or the selection with its buttons.
pub fn spawn_selection_bar(bar: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer) {
    bar.spawn((
        SelectionHint,
        theme::label(fonts, "drag onto a vessel · click to select", theme::XS, Weight::Regular, theme::TEXT_3),
        Node { margin: UiRect::left(Val::Px(14.0)), ..default() },
    ));
    bar.spawn((
        SelectionReadout,
        Node {
            display: Display::None,
            align_items: AlignItems::Center,
            column_gap: Val::Px(8.0),
            margin: UiRect::left(Val::Px(12.0)),
            padding: UiRect::new(Val::Px(4.0), Val::Px(4.0), Val::Px(2.0), Val::Px(2.0)),
            border: UiRect::all(Val::Px(1.0)),
            ..default()
        },
        BorderRadius::all(Val::Px(theme::R_MD)),
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
        r.spawn(Node { flex_direction: FlexDirection::Column, ..default() }).with_children(|c| {
            c.spawn((SelectionName, theme::label(fonts, "", theme::SM, Weight::Semibold, theme::TEXT)));
            c.spawn((SelectionFormula, theme::label(fonts, "", 10.5, Weight::Regular, theme::CYAN)));
        });
        r.spawn(theme::label(fonts, "click a vessel to add", 10.5, Weight::Regular, theme::TEXT_3));
        theme::spawn_button(r, fonts, assets, Kind::Secondary, Some("book"), "Library", SelectionOpenButton);
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
    mut hint: Query<&mut Node, (With<SelectionHint>, Without<SelectionReadout>)>,
    mut readout: Query<&mut Node, (With<SelectionReadout>, Without<SelectionHint>)>,
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
    if let Ok(mut n) = hint.single_mut() {
        n.display = if sub.is_some() { Display::None } else { Display::Flex };
    }
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
