// src/ui/detail_panel.rs
//
// Selecting a substance on the shelf. A click selects it (click it again or press Esc to let
// go): the tile lights up, and the shelf header's Library button opens its page. While
// something is selected, clicking a vessel puts it in (see drag_drop.rs); dragging works as
// always. A double-tap on a tile puts it straight into the selected vessel, and while a
// phone's keyboard is up for the shelf search a single tap does, so several results can go
// in without leaving the search. A tap on a substance in a vessel selects it too; a
// double-tap takes it out. Pin keeps the selection at the front of the shelf (saved with the
// game) until it is unpinned.
use crate::ui::Clicked;
use bevy::ecs::system::entity_command::observe;
use bevy::picking::hover::Hovered;
use bevy::prelude::*;

use crate::components::{Draggable, Ingredient};
use crate::resources::player_progress::PlayerProgress;
use crate::resources::ui_fonts::UiFonts;
use crate::systems::drag_drop::DragMoved;
use crate::ui::codex::CodexState;
use crate::ui::inventory::ShelfTile;
use crate::ui::theme::{self, Weight};

/// The substance selected on the shelf, if any.
#[derive(Resource, Default)]
pub struct SelectedSubstance(pub Option<u32>);

/// The shelf header's how-to line (wide screens only).
#[derive(Component)]
pub struct SelectionHint;
/// The shelf header's Library button: opens the selected substance's page.
#[derive(Component)]
pub struct SelectionOpenButton;
/// Its icon and word (dimmed with nothing selected).
#[derive(Component)]
pub struct SelectionOpenInk;
/// The shelf header's Pin button: pins the selected substance to the front of the shelf, or
/// unpins it.
#[derive(Component)]
pub struct SelectionPinButton;
/// Its icon and word ("Pin", or "Unpin" for a pinned selection; dimmed with nothing selected).
#[derive(Component)]
pub struct SelectionPinInk;

/// Each shelf tile and vessel chip, as it spawns, gets the click that selects it. A chip can
/// be gone again before this lands (used up by a reaction in the same frame): it needs no
/// click then, so that is not an error.
pub fn attach_click_observers(mut commands: Commands, new_items: Query<Entity, (Added<Draggable>, With<Ingredient>)>) {
    for entity in &new_items {
        commands.entity(entity).queue_silenced(observe(on_item_click));
    }
}

/// Two taps on one tile or chip within this long (seconds) are a double-tap.
pub const DOUBLE_TAP: f64 = 0.4;

/// The last tap on a shelf tile or vessel chip, when it was (real seconds), and what was
/// selected before it, for spotting a double-tap.
#[derive(Resource, Default)]
pub struct LastTap(pub Option<(Entity, f64, Option<u32>)>);

#[allow(clippy::too_many_arguments)]
fn on_item_click(
    mut trigger: On<PointerClick>,
    mut commands: Commands,
    ingredients: Query<&Ingredient>,
    tiles: Query<(), With<ShelfTile>>,
    chips: Query<(), Or<(With<crate::components::InVessel>, With<crate::components::InCatalystZone>)>>,
    moved: Query<(), With<DragMoved>>,
    mut selected: ResMut<SelectedSubstance>,
    time: Res<Time<Real>>,
    mut last: ResMut<LastTap>,
    mut add: MessageWriter<crate::systems::drag_drop::AddToActive>,
    searching: (Res<crate::ui::inventory::ShelfSearch>, Res<crate::platform::SoftKeyboard>),
    presses: Res<crate::ui::Presses>,
) {
    trigger.propagate(false);
    // a drag that ends back on its own tile is not a click, and nor is a two-finger scroll
    if trigger.button != PointerButton::Primary || moved.contains(trigger.entity) || presses.multi_touch() {
        return;
    }
    let e = trigger.entity;
    let Ok(ing) = ingredients.get(e) else { return };
    let now = time.elapsed_secs_f64();
    let double = last.0.is_some_and(|(t, at, _)| t == e && now - at <= DOUBLE_TAP);
    if double && chips.contains(e) {
        // a double-tap on a substance in a vessel takes it out (and the selection is as it was)
        selected.0 = last.0.and_then(|l| l.2);
        commands.entity(e).try_despawn();
        last.0 = None;
        return;
    }
    let tile = tiles.contains(e);
    if double && tile {
        // the first tap selected it (or let it go): keep it selected, and fill the vessel
        selected.0 = Some(ing.id);
        add.write(crate::systems::drag_drop::AddToActive(ing.id));
        last.0 = None;
        return;
    }
    let (search, soft) = searching;
    if tile && soft.0 && search.typing {
        // searching on a phone: each result tapped goes straight in, and the keyboard stays
        selected.0 = Some(ing.id);
        add.write(crate::systems::drag_drop::AddToActive(ing.id));
        commands.entity(e).try_insert(crate::ui::inventory::NewGlow::default());
        last.0 = None;
        return;
    }
    last.0 = Some((e, now, selected.0));
    selected.0 = if selected.0 == Some(ing.id) { None } else { Some(ing.id) };
}

/// The right-hand end of the shelf header: the how-to line, and the Library button.
pub fn spawn_selection_bar(bar: &mut ChildSpawnerCommands, fonts: &UiFonts, assets: &AssetServer) {
    bar.spawn((
        SelectionHint,
        theme::label(fonts, "tap to select · double-tap to fill", theme::XS, Weight::Regular, theme::TEXT_3),
        Node { margin: UiRect::left(Val::Auto), ..default() },
    ));
    bar.spawn((
        theme::button(
            theme::Kind::Disabled,
            Node {
                height: Val::Px(34.0),
                padding: UiRect::horizontal(Val::Px(12.0)),
                column_gap: Val::Px(7.0),
                align_items: AlignItems::Center,
                margin: UiRect::left(Val::Px(10.0)),
                flex_shrink: 0.0,
                ..default()
            },
            theme::R_MD,
        ),
        SelectionOpenButton,
        crate::ui::onboarding::Tip::Text("Library", "Open the selected substance in the Substance Library."),
    ))
    .with_children(|b| {
        b.spawn((SelectionOpenInk, theme::icon(assets, "book", 16.0, theme::TEXT_3)));
        b.spawn((
            SelectionOpenInk,
            theme::label(fonts, "Library", theme::SM, Weight::Semibold, theme::TEXT_3),
            Pickable::IGNORE,
        ));
    });
    bar.spawn((
        theme::button(
            theme::Kind::Disabled,
            Node {
                height: Val::Px(34.0),
                padding: UiRect::horizontal(Val::Px(12.0)),
                column_gap: Val::Px(7.0),
                align_items: AlignItems::Center,
                margin: UiRect::left(Val::Px(8.0)),
                flex_shrink: 0.0,
                ..default()
            },
            theme::R_MD,
        ),
        SelectionPinButton,
        crate::ui::onboarding::Tip::Text("Pin", "Keep the selected substance at the front of the shelf."),
    ))
    .with_children(|b| {
        b.spawn((SelectionPinInk, theme::icon(assets, "pin", 16.0, theme::TEXT_3)));
        b.spawn((
            SelectionPinInk,
            theme::label(fonts, "Pin", theme::SM, Weight::Semibold, theme::TEXT_3),
            Pickable::IGNORE,
        ));
    });
}

/// Keep the tile highlight and the Library and Pin buttons in step with the selection.
#[allow(clippy::type_complexity, clippy::too_many_arguments)]
pub fn selection_view_system(
    mut selected: ResMut<SelectedSubstance>,
    progress: Res<PlayerProgress>,
    mut tiles: Query<
        (&Ingredient, &ShelfTile, &Hovered, &mut BorderColor, &mut BackgroundColor),
        (Without<SelectionOpenButton>, Without<SelectionPinButton>),
    >,
    mut open: Query<
        (&mut theme::Skin, &Hovered, Has<bevy::ui::Pressed>, &mut BackgroundColor, &mut BorderColor),
        Or<(With<SelectionOpenButton>, With<SelectionPinButton>)>,
    >,
    mut ink: (
        Query<&mut TextColor, Or<(With<SelectionOpenInk>, With<SelectionPinInk>)>>,
        Query<(&mut ImageNode, Has<SelectionPinInk>), Or<(With<SelectionOpenInk>, With<SelectionPinInk>)>>,
        Query<&mut Text, With<SelectionPinInk>>,
    ),
    assets: Res<AssetServer>,
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
    if !selected.is_changed() && new_tiles.is_empty() && !progress.is_changed() {
        return;
    }
    let sel = selected.0;
    let pinned = sel.is_some_and(|id| progress.pinned.contains(&id));
    for mut t in &mut ink.2 {
        let word = if pinned { "Unpin" } else { "Pin" };
        if t.0 != word {
            t.0 = word.to_string();
        }
    }
    let pin_icon: Handle<Image> = assets.load(if pinned { "images/ui/pinned.png" } else { "images/ui/pin.png" });
    for (ing, tile, h, mut border, mut bg) in &mut tiles {
        let (b, c) = tile.look(h.get(), Some(ing.id) == sel);
        bg.0 = b;
        *border = BorderColor::all(c);
    }
    let kind = if sel.is_some() { theme::Kind::Secondary } else { theme::Kind::Disabled };
    let c = if sel.is_some() { theme::TEXT } else { theme::TEXT_3 };
    for mut t in &mut ink.0 {
        t.0 = c;
    }
    for (mut i, is_pin) in &mut ink.1 {
        i.color = c;
        if is_pin && i.image.id() != pin_icon.id() {
            i.image = pin_icon.clone();
        }
    }
    for (mut skin, h, pressed, mut bg, mut border) in &mut open {
        if skin.kind != kind {
            skin.kind = kind;
            let (b, l) = skin.colors(crate::ui::Look::of(h, pressed));
            bg.0 = b;
            *border = BorderColor::all(l);
        }
    }
}

/// The Pin button pins the selection to the front of the shelf, or unpins it.
pub fn selection_pin_system(
    pin: Query<(), (With<Clicked>, With<SelectionPinButton>)>,
    selected: Res<SelectedSubstance>,
    mut progress: ResMut<PlayerProgress>,
) {
    if pin.is_empty() {
        return;
    }
    if let Some(id) = selected.0 {
        if let Some(i) = progress.pinned.iter().position(|&p| p == id) {
            progress.pinned.remove(i);
        } else {
            progress.pinned.push(id);
        }
    }
}

/// The Library button opens the selection in the Substance Library.
pub fn selection_button_system(
    open: Query<(), (With<Clicked>, With<SelectionOpenButton>)>,
    selected: Res<SelectedSubstance>,
    mut codex: ResMut<CodexState>,
) {
    if !open.is_empty() {
        if let Some(id) = selected.0 {
            codex.show(id);
        }
    }
}
