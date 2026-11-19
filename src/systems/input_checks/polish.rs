// src/systems/input_checks/polish.rs
//
// Interaction checks for sound, the keyboard and controllers, hover states, saves, the
// credits, achievements and touch screens, and for playing on a phone: the Hint button and
// its kits, the shelf search, double-tap, taking things out of a vessel, why vessels unlock,
// the notification history and compact vessel cards. A child of input_checks.rs, so it
// shares its check language (targets, ops, verifies) and helpers.
use crate::ui::Button;
use bevy::input::gamepad::{GamepadConnection, GamepadConnectionEvent, RawGamepadButtonChangedEvent, RawGamepadEvent};
use bevy::input::keyboard::NativeKeyCode;
use bevy::input::touch::{TouchInput, TouchPhase};

use super::*;
use crate::resources::player_progress::SaveClock;
use crate::systems::achievements::Achievements;
use crate::systems::drag_drop::{LinkPick, Swiping, LIFT_HOLD};
use crate::systems::sound::{Cue, Family, SoundLog};
use crate::ui::codex::{CodexCloseButton, CodexScrollable, CodexTextCredit};
use crate::ui::credits::{CreditLink, CreditsButton, CreditsRoot, SECTIONS};
use crate::ui::focus::{FocusRing, NoFocus};
use crate::ui::hint::{
    base_materials, choose, decoy_count, plan_kit, targets, HintButton, HintChange, HintKitToggle, HintLine, HintMore,
    HintPick, HintShowTree, HintState, Target as Goal,
};
use crate::ui::inventory::{
    ShelfSearch, ShelfSearchBox, ShelfSearchClear, ShelfSearchDone, ShelfTitle, VesselChipRemove,
};
use crate::ui::settings::SettingsRoot;
use crate::ui::shell::JournalButton;
use crate::ui::theme::Skin;
use crate::ui::toasts::{Journal, JournalRow, JournalUi};
use bevy::ui::ComputedStackIndex;

use crate::systems::drag_drop::BenchZoom;
use crate::systems::reaction_check::VesselChainButton;
use crate::ui::detail_panel::SelectionName;
use crate::ui::hint::{HintButtonText, HintSuggestedTag};
use crate::ui::main_menu::{MainMenu, MenuPlay, MenuRoot, MenuSettings, MenuStage};
use crate::ui::process_toolbar::VesselSidebar;
use crate::ui::shell::{BenchZoomIn, BenchZoomOut};

// ---------------------------------------------------------------------------------------
// Sound, keyboard, hover states, saves and credits
// ---------------------------------------------------------------------------------------
fn heard(cues: &'static [Cue]) -> Verify {
    verify(move |w| {
        let log = &w.resource::<SoundLog>().0;
        let missing: Vec<&Cue> = cues.iter().filter(|c| !log.contains(c)).collect();
        if missing.is_empty() {
            Ok(())
        } else {
            Err(format!("not heard: {missing:?}; heard {log:?}"))
        }
    })
}

fn heard_any(cues: &'static [Cue]) -> Verify {
    verify(move |w| {
        let log = &w.resource::<SoundLog>().0;
        if cues.iter().any(|c| log.contains(c)) {
            Ok(())
        } else {
            Err(format!("none of {cues:?}; heard {log:?}"))
        }
    })
}

fn clear_log() -> Op {
    setup(|w| w.resource_mut::<SoundLog>().0.clear())
}

fn focused(w: &World) -> Option<Entity> {
    w.resource::<KeyFocus>().entity
}

fn ring_shows(w: &mut World) -> bool {
    w.query_filtered::<&Node, With<FocusRing>>().iter(w).next().is_some_and(|n| n.display != Display::None)
}

fn is_inside<C: Component>(w: &mut World, e: Entity) -> bool {
    let Some(root) = first::<C>(w, |_| true) else { return false };
    let mut cur = e;
    loop {
        if cur == root {
            return true;
        }
        match w.get::<ChildOf>(cur) {
            Some(p) => cur = p.parent(),
            None => return false,
        }
    }
}

fn shelf_tile_entity(w: &mut World, name: &str) -> Option<Entity> {
    w.query_filtered::<(Entity, &Ingredient), With<ShelfTile>>().iter(w).find(|(_, i)| i.name == name).map(|(e, _)| e)
}

fn focus_on(f: impl Fn(&mut World) -> Option<Entity> + Send + Sync + 'static) -> Op {
    setup(move |w| {
        let e = f(w);
        let mut k = w.resource_mut::<KeyFocus>();
        k.entity = e;
        k.visible = true;
    })
}

fn border_of(w: &World, e: Entity) -> Option<Color> {
    w.get::<BorderColor>(e).map(|b| b.top)
}

/// The checks' virtual controller: connected the first time it is used.
fn check_pad(w: &mut World) -> Entity {
    if let Some(e) = w.query_filtered::<Entity, With<CheckPad>>().iter(w).next() {
        return e;
    }
    let e = w.spawn((CheckPad, Name::new("CheckPad"))).id();
    w.write_message(GamepadConnectionEvent::new(
        e,
        GamepadConnection::Connected { name: "the checks' controller".into(), vendor_id: None, product_id: None },
    ));
    e
}

#[derive(Component)]
struct CheckPad;

/// Press and release a controller button.
fn pad_press(button: GamepadButton) -> Vec<Op> {
    vec![
        setup(move |w| {
            let pad = check_pad(w);
            w.write_message(RawGamepadEvent::Button(RawGamepadButtonChangedEvent::new(pad, button, 1.0)));
        }),
        Op::Wait(2),
        setup(move |w| {
            let pad = check_pad(w);
            w.write_message(RawGamepadEvent::Button(RawGamepadButtonChangedEvent::new(pad, button, 0.0)));
        }),
        Op::Wait(2),
    ]
}

fn earned(ids: &'static [&'static str]) -> Verify {
    verify(move |w| {
        let a = w.resource::<Achievements>();
        let missing: Vec<&&str> = ids.iter().filter(|id| !a.earned.contains(**id)).collect();
        if missing.is_empty() {
            Ok(())
        } else {
            Err(format!("not earned: {missing:?}"))
        }
    })
}

// ---------------------------------------------------------------------------------------
// Touch screens: the checks' finger sends the touch messages a phone's window would
// ---------------------------------------------------------------------------------------
const FINGER: u64 = 7;

/// Where the checks' finger is, where it is heading, and when it came down.
#[derive(Resource, Clone, Copy)]
struct Finger {
    at: Vec2,
    from: Vec2,
    to: Vec2,
    since: f64,
}

fn finger(w: &mut World, phase: TouchPhase, at: Vec2) {
    let Some(window) = w.query_filtered::<Entity, With<PrimaryWindow>>().iter(w).next() else { return };
    // the window sends both: input reads the one, picking the other
    let ev = TouchInput { phase, position: at, window, force: None, id: FINGER };
    w.write_message(ev);
    w.write_message(bevy::window::WindowEvent::TouchInput(ev));
    let now = w.resource::<Time<Real>>().elapsed_secs_f64();
    let mut f = w.get_resource::<Finger>().copied().unwrap_or(Finger { at, from: at, to: at, since: now });
    if phase == TouchPhase::Started {
        f = Finger { at, from: at, to: at, since: now };
    }
    f.at = at;
    w.insert_resource(f);
}

/// Where a finger goes after it lands.
enum Slide {
    To(Target),
    By(Vec2),
}

/// A finger lands on `from`, rests `hold` seconds, slides (in six moves, a frame apart)
/// and lifts.
fn finger_slide(from: Target, slide: Slide, hold: f64) -> Vec<Op> {
    let mut ops = vec![Op::Until(
        verify(move |w| {
            let p = (from.find)(w).ok_or_else(|| format!("could not find {} on screen", from.name))?;
            finger(w, TouchPhase::Started, p);
            Ok(())
        }),
        30,
    )];
    ops.push(match slide {
        Slide::To(t) => Op::Until(
            verify(move |w| {
                let p = (t.find)(w).ok_or_else(|| format!("could not find {} on screen", t.name))?;
                w.resource_mut::<Finger>().to = p;
                Ok(())
            }),
            30,
        ),
        Slide::By(d) => setup(move |w| {
            let mut f = w.resource_mut::<Finger>();
            f.to = f.from + d;
        }),
    });
    if hold > 0.0 {
        ops.push(Op::Until(
            verify(move |w| {
                let held = w.resource::<Time<Real>>().elapsed_secs_f64() - w.resource::<Finger>().since;
                if held >= hold {
                    Ok(())
                } else {
                    Err(format!("the finger was held only {held:.2} s"))
                }
            }),
            600,
        ));
    }
    for i in 1..=6 {
        ops.push(setup(move |w| {
            let f = *w.resource::<Finger>();
            finger(w, TouchPhase::Moved, f.from.lerp(f.to, i as f32 / 6.0));
        }));
    }
    ops.push(Op::Wait(2));
    ops.push(setup(|w| {
        let at = w.resource::<Finger>().at;
        finger(w, TouchPhase::Ended, at);
    }));
    ops.push(Op::Wait(3));
    ops
}

/// A finger taps a target.
fn finger_tap(t: Target) -> Vec<Op> {
    vec![
        Op::Until(
            verify(move |w| {
                let p = (t.find)(w).ok_or_else(|| format!("could not find {} on screen", t.name))?;
                finger(w, TouchPhase::Started, p);
                Ok(())
            }),
            30,
        ),
        Op::Wait(2),
        setup(|w| {
            let at = w.resource::<Finger>().at;
            finger(w, TouchPhase::Ended, at);
        }),
        Op::Wait(3),
    ]
}

/// A phone's Back button, pressed and let go.
fn back_button() -> Vec<Op> {
    let key = |state: ButtonState| {
        setup(move |w| {
            let Some(window) = w.query_filtered::<Entity, With<PrimaryWindow>>().iter(w).next() else { return };
            w.write_message(KeyboardInput {
                key_code: KeyCode::Unidentified(NativeKeyCode::Android(4)),
                logical_key: Key::BrowserBack,
                state,
                text: None,
                repeat: false,
                window,
            });
        })
    };
    vec![key(ButtonState::Pressed), Op::Wait(1), key(ButtonState::Released), Op::Wait(2)]
}

fn shelf_scroll(w: &mut World) -> f32 {
    w.query_filtered::<&ScrollPosition, With<InventoryScroll>>().iter(w).next().map_or(0.0, |s| s.0.y)
}

fn touch_checks() -> Vec<Check> {
    use CardPart::*;
    use ProcessType::Heat;
    let mut v = Vec::new();
    v.push(check(
        "Touch",
        "A finger swiping up the shelf scrolls it and lifts nothing",
        vec![
            setup(discover_everything),
            Op::Wait(20),
            setup(|w| {
                for mut sp in w.query_filtered::<&mut ScrollPosition, With<InventoryScroll>>().iter_mut(w) {
                    sp.0 = Vec2::ZERO;
                }
            }),
            Op::Wait(2),
        ]
        .into_iter()
        // Hydrogen sits at the top left of a shelf scrolled to the top; any built tile could be a
        // row below the view (the shelf builds a screen either side), at its very edge
        .chain(finger_slide(tile("Hydrogen"), Slide::By(Vec2::new(0.0, -120.0)), 0.0))
        .chain([
            Op::Until(
                verify(|w| if shelf_scroll(w) > 20.0 { Ok(()) } else { Err("the shelf did not scroll".into()) }),
                30,
            ),
            Op::Expect(verify(|w| {
                let ghosts = w.query::<&DragGhostNode>().iter(w).count();
                let swiping = w.query::<&Swiping>().iter(w).count();
                match (ghosts, swiping) {
                    (0, 0) => Ok(()),
                    _ => Err(format!("{ghosts} tile copies following the finger, {swiping} tiles still swiping")),
                }
            })),
        ])
        .collect(),
    ));
    v.push(check(
        "Touch",
        "Holding a shelf tile lifts it, and dropped on a vessel it goes in",
        vec![setup(new_game), setup(|w| place(w, Heat, 0)), Op::Wait(5)]
            .into_iter()
            .chain(finger_slide(tile("Wood"), Slide::To(card_part(Heat, Art)), LIFT_HOLD + 0.15))
            .chain([Op::Until(has_chip(Heat, "Wood"), 30)])
            .collect(),
    ));
    v.push(check(
        "Touch",
        "Tapping a tile and then a vessel puts it in",
        vec![setup(new_game), setup(|w| place(w, Heat, 0)), Op::Wait(5)]
            .into_iter()
            .chain(finger_tap(tile("Wood")))
            .chain([Op::Until(
                verify(|w| match (w.resource::<SelectedSubstance>().0, sub_id(w, "Wood")) {
                    (Some(a), Some(b)) if a == b => Ok(()),
                    (s, _) => Err(format!("selected {s:?} after tapping Wood")),
                }),
                30,
            )])
            .chain(finger_tap(card_part(Heat, Art)))
            .chain([Op::Until(has_chip(Heat, "Wood"), 30)])
            .collect(),
    ));
    v.push(check(
        "Touch",
        "A finger dragging the substance list scrolls it",
        vec![
            setup(discover_everything),
            Op::Wait(10),
            Op::Click(nav(View::Substances)),
            Op::Until(state("Substance Library open", |w| w.resource::<CodexState>().open), 30),
            Op::Wait(10),
        ]
        .into_iter()
        .chain(finger_slide(
            marked::<CodexEntry>("the first entry in the list"),
            Slide::By(Vec2::new(0.0, -150.0)),
            0.0,
        ))
        .chain([
            Op::Until(
                verify(|w| {
                    let y = w
                        .query::<(&CodexScrollable, &ScrollPosition)>()
                        .iter(w)
                        .find(|(c, _)| c.is_left)
                        .map_or(0.0, |(_, s)| s.0.y);
                    if y > 20.0 {
                        Ok(())
                    } else {
                        Err(format!("the list is at {y}"))
                    }
                }),
                30,
            ),
            Op::Key(KeyCode::Escape),
            Op::Wait(3),
        ])
        .collect(),
    ));
    v.push(check(
        "Touch",
        "A phone's Back button closes a view",
        vec![
            Op::Click(nav(View::Reactions)),
            Op::Until(state("Reaction Library open", |w| w.resource::<ReactionLibState>().open), 30),
        ]
        .into_iter()
        .chain(back_button())
        .chain([Op::Until(state("Reaction Library closed", |w| !w.resource::<ReactionLibState>().open), 30)])
        .collect(),
    ));
    v
}

pub(super) fn polish_checks() -> Vec<Check> {
    use CardPart::*;
    use ProcessType::{Heat, Mix};
    let mut v = Vec::new();

    // --- sound (the review run is silent; what would play is logged) ---
    v.push(check(
        "Sound",
        "Placing a vessel (in its own family's sound), lifting a substance and dropping it in each make a sound",
        vec![
            setup(new_game),
            Op::Wait(3),
            clear_log(),
            Op::Click(sidebar_button(Heat)),
            Op::Until(heard(&[Cue::Place(Family::Fire)]), 30),
            clear_log(),
            Op::Click(sidebar_button(Mix)),
            Op::Until(heard(&[Cue::Place(Family::Grind)]), 30),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(heard(&[Cue::Pickup, Cue::Drop]), 60),
        ],
    ));
    v.push(check(
        "Sound",
        "A reaction sounds like its vessel (a fire crackles), then its discovery chimes",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            Op::Wait(5),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            clear_log(),
            Op::Click(card_part(Heat, React)),
            Op::Until(heard(&[Cue::React(Family::Fire)]), 30),
            Op::Until(heard_any(&[Cue::Discovery, Cue::Milestone]), WAIT),
        ],
    ));
    v.push(check(
        "Sound",
        "A mix that doesn't react falls flat",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Oxygen"), card_part(Mix, Art)),
            Op::Until(has_chip(Mix, "Oxygen"), 30),
            clear_log(),
            Op::Click(card_part(Mix, React)),
            Op::Until(heard(&[Cue::Fizzle]), 60),
        ],
    ));
    v.push(check(
        "Sound",
        "Button clicks tick, and stop when switched off",
        vec![
            clear_log(),
            Op::Click(marked::<SettingsButton>("the gear")),
            Op::Until(heard(&[Cue::Click]), 30),
            setup(|w| w.resource_mut::<Settings>().ui_sounds = false),
            clear_log(),
            Op::Click(marked::<crate::ui::settings::SettingsClose>("the settings x")),
            Op::Until(state("settings closed", |w| !w.resource::<SettingsUi>().open), 30),
            Op::Wait(5),
            Op::Expect(verify(|w| {
                let log = &w.resource::<SoundLog>().0;
                if log.contains(&Cue::Click) {
                    Err(format!("clicks are off but heard {log:?}"))
                } else {
                    Ok(())
                }
            })),
        ],
    ));
    let volume_step = |down: bool| {
        target(if down { "the volume -" } else { "the volume +" }, move |w| {
            let e = first::<SettingStep>(w, |s| s.0 == Field::Volume && (s.1 < 0.0) == down)?;
            point_in(w, e, 0.5, 0.5)
        })
    };
    let mut ops = vec![setup(|w| w.resource_mut::<SettingsUi>().open = true), Op::Wait(5)];
    for _ in 0..7 {
        ops.push(Op::Click(volume_step(true)));
    }
    ops.push(Op::Until(
        verify(|w| {
            let v = w.resource::<Settings>().volume;
            let shown = w
                .query::<(&crate::ui::settings::SettingValue, &Text)>()
                .iter(w)
                .find(|(f, _)| f.0 == Field::Volume)
                .map(|(_, t)| t.0.clone());
            if v == 0.0 && shown.as_deref() == Some("Off") {
                Ok(())
            } else {
                Err(format!("volume {v}, shown {shown:?}"))
            }
        }),
        30,
    ));
    ops.push(Op::Click(volume_step(false)));
    ops.push(Op::Until(
        verify(|w| {
            let v = w.resource::<Settings>().volume;
            if (v - 0.1).abs() < 1e-4 {
                Ok(())
            } else {
                Err(format!("volume {v} after one step up"))
            }
        }),
        30,
    ));
    v.push(check("Settings", "Volume steps down to Off and back up", ops));

    // --- keyboard ---
    v.push(check(
        "Keyboard",
        "Tab moves through the controls, with a ring on the focused one",
        vec![
            Op::Key(KeyCode::Tab),
            Op::Until(
                verify(|w| {
                    let e = focused(w).ok_or("nothing focused")?;
                    if w.get::<NavTab>(e).is_none() {
                        return Err("the first Tab stop is not in the header".into());
                    }
                    if ring_shows(w) {
                        Ok(())
                    } else {
                        Err("no focus ring".into())
                    }
                }),
                30,
            ),
            setup(|w| {
                let e = focused(w).map(|e| e.index().index() as f32).unwrap_or(-1.0);
                w.resource_mut::<Scratch>().0.insert("first", e);
            }),
            Op::Key(KeyCode::Tab),
            Op::Until(
                verify(|w| {
                    let was = w.resource::<Scratch>().0.get("first").copied().unwrap_or(-1.0);
                    let now = focused(w).map(|e| e.index().index() as f32).unwrap_or(-2.0);
                    if now != was && ring_shows(w) {
                        Ok(())
                    } else {
                        Err("the second Tab didn't move focus".into())
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Keyboard",
        "Enter presses the focused button",
        vec![
            focus_on(|w| first::<SettingsButton>(w, |_| true)),
            Op::Key(KeyCode::Enter),
            Op::Until(state("settings open", |w| w.resource::<SettingsUi>().open), 30),
        ],
    ));
    let mut ops = vec![setup(|w| w.resource_mut::<SettingsUi>().open = true), Op::Wait(5)];
    for _ in 0..8 {
        ops.push(Op::Key(KeyCode::Tab));
        ops.push(Op::Expect(verify(|w| {
            let e = focused(w).ok_or("nothing focused")?;
            let name = w.get::<Name>(e).map(|n| n.to_string()).unwrap_or_default();
            if is_inside::<SettingsRoot>(w, e) {
                Ok(())
            } else {
                Err(format!("focus left the dialog for {e} {name}"))
            }
        })));
    }
    v.push(check("Keyboard", "Tab stays inside an open dialog", ops));
    v.push(check(
        "Keyboard",
        "The shelf is one Tab stop, and the arrows move along it",
        vec![
            setup(new_game),
            Op::Wait(5),
            focus_on(|w| shelf_tile_entity(w, "Water")),
            Op::Key(KeyCode::ArrowRight),
            Op::Until(
                verify(|w| {
                    let e = focused(w).ok_or("nothing focused")?;
                    let name = w.get::<Ingredient>(e).map(|i| i.name.clone());
                    match name {
                        Some(n) if n != "Water" && w.get::<ShelfTile>(e).is_some() => Ok(()),
                        other => Err(format!("focus on {other:?}")),
                    }
                }),
                30,
            ),
            Op::Wait(3),
            Op::Shot("keyboard focus on the shelf"),
            Op::Key(KeyCode::Enter),
            Op::Until(
                verify(|w| {
                    let e = focused(w).ok_or("nothing focused")?;
                    let id = w.get::<Ingredient>(e).map(|i| i.id);
                    let sel = w.resource::<SelectedSubstance>().0;
                    if id.is_some() && sel == id {
                        Ok(())
                    } else {
                        Err(format!("selected {sel:?}, focused tile {id:?}"))
                    }
                }),
                30,
            ),
            Op::Key(KeyCode::Tab),
            Op::Until(
                verify(|w| {
                    let e = focused(w).ok_or("nothing focused")?;
                    if w.get::<ShelfTile>(e).is_none() {
                        Ok(())
                    } else {
                        Err("Tab stayed on the shelf".into())
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Keyboard",
        "A mouse click hides the focus ring",
        vec![
            focus_on(|w| first::<SettingsButton>(w, |_| true)),
            Op::Until(verify(|w| if ring_shows(w) { Ok(()) } else { Err("no ring to start with".into()) }), 30),
            Op::Click(bench_spot()),
            Op::Until(verify(|w| if ring_shows(w) { Err("the ring is still showing".into()) } else { Ok(()) }), 30),
        ],
    ));
    v.push(check(
        "Keyboard",
        "Space types into a search box; Enter still presses",
        vec![
            setup(|w| w.resource_mut::<CodexState>().open = true),
            Op::Wait(5),
            focus_on(|w| first::<CodexCloseButton>(w, |_| true)),
            Op::Key(KeyCode::Space),
            Op::Wait(3),
            Op::Expect(state("the library stays open", |w| w.resource::<CodexState>().open)),
            Op::Key(KeyCode::Enter),
            Op::Until(state("the library closed", |w| !w.resource::<CodexState>().open), 30),
        ],
    ));

    // --- hover states ---
    v.push(check(
        "Polish",
        "Every button answers the pointer the same way",
        vec![
            setup(|w| {
                w.resource_mut::<SettingsUi>().open = true;
                w.resource_mut::<Settings>().next_step = true;
            }),
            Op::Wait(5),
            Op::Expect(verify(|w| {
                let odd: Vec<String> = w
                    .query_filtered::<(
                        Entity,
                        Option<&Name>,
                        Has<Skin>,
                        Has<ShelfTile>,
                        Has<TechNodeButton>,
                        Has<SettingToggle>,
                        Has<NoFocus>,
                    ), With<Button>>()
                    .iter(w)
                    .filter(|(_, _, a, b, c, d, e)| !(*a || *b || *c || *d || *e))
                    .map(|(e, n, ..)| format!("{e} {}", n.map(|n| n.to_string()).unwrap_or_default()))
                    .collect();
                if odd.is_empty() {
                    Ok(())
                } else {
                    Err(format!("{} buttons with no hover look: {odd:?}", odd.len()))
                }
            })),
            setup(|w| {
                let e = first::<SettingToggle>(w, |_| true);
                let c = e.and_then(|e| border_of(w, e)).map(|c| c.to_srgba().red).unwrap_or(-1.0);
                w.resource_mut::<Scratch>().0.insert("rest", c);
            }),
            Op::MoveTo(marked::<SettingToggle>("a settings switch")),
            Op::Until(
                verify(|w| {
                    let rest = w.resource::<Scratch>().0.get("rest").copied().unwrap_or(-1.0);
                    let e = first::<SettingToggle>(w, |_| true).ok_or("no switch")?;
                    let now = border_of(w, e).map(|c| c.to_srgba().red).unwrap_or(-1.0);
                    if (now - rest).abs() > 1e-3 {
                        Ok(())
                    } else {
                        Err("the switch didn't change under the pointer".into())
                    }
                }),
                30,
            ),
            setup(|w| w.resource_mut::<SettingsUi>().open = false),
            setup(new_game),
            Op::Wait(10),
            setup(|w| {
                let e = first::<HintButton>(w, |_| true);
                let c = e.and_then(|e| w.get::<BackgroundColor>(e)).map(|c| c.0.to_srgba().red).unwrap_or(-1.0);
                w.resource_mut::<Scratch>().0.insert("hint", c);
            }),
            Op::MoveTo(marked::<HintButton>("the Hint button")),
            Op::Until(
                verify(|w| {
                    let rest = w.resource::<Scratch>().0.get("hint").copied().unwrap_or(-1.0);
                    let e = first::<HintButton>(w, |_| true).ok_or("no Hint button")?;
                    let now = w.get::<BackgroundColor>(e).map(|c| c.0.to_srgba().red).unwrap_or(-1.0);
                    if (now - rest).abs() > 1e-3 {
                        Ok(())
                    } else {
                        Err("the Hint button didn't light up under the pointer".into())
                    }
                }),
                30,
            ),
        ],
    ));

    // --- saves ---
    v.push(check(
        "Saves",
        "A discovery is saved a moment later",
        vec![
            setup(new_game),
            Op::Wait(200),
            setup(|w| {
                let n = w.resource::<SaveClock>().writes as f32;
                w.resource_mut::<Scratch>().0.insert("writes", n);
            }),
            setup(|w| discover(w, &["Charcoal"])),
            Op::Wait(1),
            Op::Expect(verify(|w| {
                if w.resource::<SaveClock>().pending() {
                    Ok(())
                } else {
                    Err("the change isn't waiting to be saved".into())
                }
            })),
            Op::Until(
                verify(|w| {
                    let before = w.resource::<Scratch>().0.get("writes").copied().unwrap_or(0.0);
                    let now = w.resource::<SaveClock>().writes as f32;
                    if now > before && !w.resource::<SaveClock>().pending() {
                        Ok(())
                    } else {
                        Err(format!("{now} saves, {before} before"))
                    }
                }),
                WAIT,
            ),
        ],
    ));

    // --- credits ---
    v.push(check(
        "Credits",
        "Settings opens About: every source, the source code and every cause with a link",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(marked::<CreditsButton>("About and credits")),
            Op::Until(
                verify(|w| {
                    let shown = w
                        .query_filtered::<&Node, With<CreditsRoot>>()
                        .iter(w)
                        .next()
                        .is_some_and(|n| n.display != Display::None);
                    let links = w.query::<&CreditLink>().iter(w).count();
                    let causes = crate::ui::credits::shown_causes().filter(|c| c.url.is_some()).count();
                    let want: usize = SECTIONS.iter().map(|(_, c)| c.len()).sum::<usize>() + 1 + causes;
                    let soon = w.query::<&Text>().iter(w).filter(|t| t.0 == "Coming soon").count();
                    let pending = crate::ui::credits::shown_causes().count() - causes;
                    if shown && links == want && soon == pending {
                        Ok(())
                    } else {
                        Err(format!("shown={shown}, {links} of {want} links, {soon} of {pending} marked coming soon"))
                    }
                }),
                30,
            ),
            Op::Wait(10),
            Op::Shot("the About screen"),
            // and its end: free for good, where to give, privacy
            setup(|w| {
                let Some(root) = first::<CreditsRoot>(w, |_| true) else { return };
                let panels: Vec<Entity> = w.get::<Children>(root).map(|c| c.iter().collect()).unwrap_or_default();
                for p in panels {
                    if let Some(mut sp) = w.get_mut::<ScrollPosition>(p) {
                        sp.0.y = 1.0e6;
                    }
                }
            }),
            Op::Wait(10),
            Op::Shot("the end of the About screen: free, giving, privacy"),
            Op::Click(target("the Wikipedia credit's link", |w| {
                let e = first::<CreditLink>(w, |l| l.0 == SECTIONS[0].1[0].url)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|_| {
                    let last = URL_SINK.lock().ok().and_then(|s| s.as_ref().and_then(|v| v.last().cloned()));
                    if last.as_deref() == Some(SECTIONS[0].1[0].url) {
                        Ok(())
                    } else {
                        Err(format!("opened {last:?}"))
                    }
                }),
                30,
            ),
            Op::Key(KeyCode::Escape),
            Op::Until(
                verify(|w| {
                    let (c, s) = (w.resource::<CreditsUi>().open, w.resource::<SettingsUi>().open);
                    if !c && s {
                        Ok(())
                    } else {
                        Err(format!("credits open={c}, settings open={s}"))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Credits",
        "A library page names the source of its text",
        vec![
            setup(|w| {
                let id = sub_id(w, "Styrene");
                let mut c = w.resource_mut::<CodexState>();
                c.open = true;
                c.selected = id;
            }),
            Op::Until(
                verify(|w| {
                    let line = w.query_filtered::<&Text, With<CodexTextCredit>>().iter(w).next().map(|t| t.0.clone());
                    match line {
                        Some(l) if l.contains("Wikipedia") && l.contains("CC BY-SA") => Ok(()),
                        other => Err(format!("the page's credit reads {other:?}")),
                    }
                }),
                60,
            ),
            Op::Shot("a page's text credit"),
        ],
    ));
    // --- controllers ---
    let mut ops = vec![
        setup(|w| {
            check_pad(w);
        }),
        Op::Wait(5),
        focus_on(|w| first::<SettingsButton>(w, |_| true)),
    ];
    ops.extend(pad_press(GamepadButton::South));
    ops.push(Op::Until(state("A opened settings", |w| w.resource::<SettingsUi>().open), 30));
    ops.extend(pad_press(GamepadButton::RightTrigger));
    ops.push(Op::Until(
        verify(|w| {
            let e = focused(w).ok_or("nothing focused")?;
            if is_inside::<SettingsRoot>(w, e) {
                Ok(())
            } else {
                Err("the bumper didn't move focus into the dialog".into())
            }
        }),
        30,
    ));
    ops.extend(pad_press(GamepadButton::East));
    ops.push(Op::Until(state("B closed settings", |w| !w.resource::<SettingsUi>().open), 30));
    ops.push(focus_on(|w| first::<NavTab>(w, |t| t.0 == View::Lab)));
    ops.extend(pad_press(GamepadButton::DPadDown));
    ops.push(Op::Until(
        verify(|w| {
            let e = focused(w).ok_or("nothing focused")?;
            if w.get::<NavTab>(e).is_none() {
                Ok(())
            } else {
                Err("the D-pad didn't leave the header".into())
            }
        }),
        30,
    ));
    v.push(check("Controller", "A presses, the bumpers tab, B backs out, the D-pad moves", ops));

    // --- achievements ---
    v.push(check(
        "Achievements",
        "A milestone earns its achievement",
        vec![
            setup(new_game),
            Op::Wait(5),
            setup(|w| w.resource_mut::<Achievements>().earned.clear()),
            setup(|w| discover(w, &["Copper"])),
            Op::Until(earned(&["MILESTONE_COPPER"]), 60),
            Op::Expect(verify(|w| {
                let a = w.resource::<Achievements>();
                if a.earned.contains("MILESTONE_IRON") {
                    Err("Iron was earned without making iron".into())
                } else {
                    Ok(())
                }
            })),
        ],
    ));
    v.push(check(
        "Achievements",
        "Every era, every vessel and every substance are earned at the end",
        vec![
            setup(|w| w.resource_mut::<Achievements>().earned.clear()),
            setup(discover_everything),
            Op::Until(
                earned(&["ERA_ANTIQUITY", "ERA_FRONTIER", "EVERY_VESSEL", "EVERY_SUBSTANCE", "MILESTONE_OGANESSON"]),
                120,
            ),
            Op::Expect(verify(|w| {
                let a = w.resource::<Achievements>();
                let all = a.list.len();
                if a.earned.len() == all {
                    Ok(())
                } else {
                    Err(format!("{} of {all} earned", a.earned.len()))
                }
            })),
            setup(new_game),
            Op::Wait(10),
        ],
    ));
    v.extend(touch_checks());
    v.extend(play_checks());
    v.extend(menu_and_bench_checks());
    v.extend(tap_and_link_checks());
    v.extend(teaching_checks());
    v.extend(balanced_checks());
    v
}

// ---------------------------------------------------------------------------------------
// Playing on a phone: hints and kits, search, double-tap, the x, why vessels unlock, the
// journal, compact cards
// ---------------------------------------------------------------------------------------
/// Play the first `n` steps of the playthrough at once, milestones included, quietly.
fn play_ahead(w: &mut World, n: usize) {
    use bevy::platform::collections::HashSet as BevySet;
    let (known, vessels, fired) = {
        let db = w.resource::<RecipeDatabase>();
        let pt = db.playthrough();
        let mut known: std::collections::HashSet<u32> = db.start.iter().copied().collect();
        let mut vessels: Vec<ProcessType> = vec![ProcessType::Mix, ProcessType::Heat];
        let mut fired: Vec<usize> = Vec::new();
        let fire =
            |known: &mut std::collections::HashSet<u32>, vessels: &mut Vec<ProcessType>, fired: &mut Vec<usize>| loop {
                let mut any = false;
                for (i, m) in db.milestones.iter().enumerate() {
                    if !fired.contains(&i) && known.contains(&m.on) {
                        fired.push(i);
                        vessels.extend(m.unlock.iter().cloned());
                        known.extend(m.grant.iter().copied());
                        any = true;
                    }
                }
                if !any {
                    break;
                }
            };
        for id in pt.steps.iter().take(n) {
            fire(&mut known, &mut vessels, &mut fired);
            if let Some(r) = db.authored.iter().find(|r| r.id == *id) {
                known.extend(r.products.iter().map(|p| p.substance_id));
            }
        }
        fire(&mut known, &mut vessels, &mut fired);
        (known, vessels, fired)
    };
    w.resource_mut::<PlayerProgress>().discovered = known.into_iter().collect::<BevySet<u32>>();
    w.resource_mut::<ProcessUnlocks>().0 = vessels.into_iter().collect();
    let mut f = w.resource_mut::<FiredMilestones>();
    f.fired = fired.into_iter().collect();
    f.primed = true;
}

/// A target whose kit takes more than one step, at the current progress.
fn multi_step_target(w: &mut World) -> Option<Goal> {
    let db = w.resource::<RecipeDatabase>();
    let progress = w.resource::<PlayerProgress>();
    let unlocks = w.resource::<ProcessUnlocks>();
    let known = |id: u32| progress.discovered.contains(&id);
    let open = |p: &ProcessType| unlocks.0.contains(p);
    let base = crate::ui::hint::base_materials(db);
    let pool: Vec<u32> = progress.discovered.iter().copied().collect();
    targets(db, &known, &open).into_iter().find(|t| {
        plan_kit(db, &known, &open, &base, &pool, t.product, t.reaction, Settings::default().decoy_range())
            .is_some_and(|k| k.steps.len() >= 2)
    })
}

/// Play ahead until some target needs a route of several steps, and chase it.
fn chase_a_multi_step_target(w: &mut World) {
    let total = w.resource::<RecipeDatabase>().playthrough().steps.len();
    let mut n = 20;
    let found = loop {
        play_ahead(w, n);
        if let Some(t) = multi_step_target(w) {
            break Some(t);
        }
        if n >= total {
            break None;
        }
        n = (n + 20).min(total);
    };
    if let Some(t) = found {
        chase(w, t);
    }
}

/// Make `t` the target, as picking it in the list does.
fn chase(w: &mut World, t: Goal) {
    w.resource_scope(|w, mut state: Mut<HintState>| {
        let db = w.resource::<RecipeDatabase>();
        let decoys = w.resource::<Settings>().decoy_range();
        choose(&mut state, t, db, w.resource::<PlayerProgress>(), w.resource::<ProcessUnlocks>(), decoys);
    });
}

/// The substance ids of the shelf tiles that are built.
fn shelf_ids(w: &mut World) -> std::collections::BTreeSet<u32> {
    w.query_filtered::<&Ingredient, With<ShelfTile>>().iter(w).map(|i| i.id).collect()
}

/// The card's hint lines (in no particular order: the checks look for a line, or count them).
fn hint_lines_now(w: &mut World) -> Vec<String> {
    w.query_filtered::<&Text, With<HintLine>>().iter(w).map(|t| t.0.clone()).collect()
}

fn hint_says(want: &'static str) -> Verify {
    verify(move |w| {
        let lines = hint_lines_now(w);
        if lines.iter().any(|l| l.starts_with(want)) {
            Ok(())
        } else {
            Err(format!("the card reads {lines:?}, with no line starting {want:?}"))
        }
    })
}

/// The shelf shows exactly the kit (every item and decoy, nothing else).
fn shelf_is_the_kit() -> Verify {
    verify(|w| {
        let kit = w.resource::<HintState>().kit.clone().ok_or("no kit")?;
        let want: std::collections::BTreeSet<u32> = kit.shelf().collect();
        let got = shelf_ids(w);
        let title =
            w.query_filtered::<&Text, With<ShelfTitle>>().iter(w).next().map(|t| t.0.clone()).unwrap_or_default();
        if got == want && title == "KIT" {
            Ok(())
        } else {
            Err(format!("shelf {got:?} titled {title:?}, kit {want:?}"))
        }
    })
}

/// Put on a vessel card by a check only, to move it into fresh storage (as hovering it or
/// clipping it can).
#[derive(Component)]
struct Restored;

/// Every substance in a vessel is drawn after (over) its card, and nothing at rest is
/// lifted onto a layer of its own.
fn contents_drawn_over_cards() -> Verify {
    verify(|w| {
        let chips: Vec<(Entity, Entity)> = w
            .query::<(Entity, Option<&InVessel>, Option<&InCatalystZone>)>()
            .iter(w)
            .filter_map(|(e, v, c)| v.map(|v| v.0).or(c.map(|c| c.0)).map(|card| (e, card)))
            .collect();
        if chips.is_empty() {
            return Err("no substance in any vessel".into());
        }
        let mut under = Vec::new();
        for (chip, card) in chips {
            let (Some(a), Some(b)) = (w.get::<ComputedStackIndex>(chip), w.get::<ComputedStackIndex>(card)) else {
                continue;
            };
            if a.0 <= b.0 {
                under.push(w.get::<Ingredient>(chip).map(|i| i.name.clone()).unwrap_or_default());
            }
        }
        let lifted = w
            .query_filtered::<(), (With<GlobalZIndex>, Or<(With<InVessel>, With<InCatalystZone>, With<VesselCard>)>)>()
            .iter(w)
            .count();
        if under.is_empty() && lifted == 0 {
            Ok(())
        } else {
            Err(format!("drawn under their vessel: {under:?}; lifted at rest: {lifted}"))
        }
    })
}

/// The kit being chased was planned with the decoy setting, and holds as many decoys as it
/// asks for (or every raw material found so far that the route leaves free).
fn kit_decoys_right(w: &mut World) -> Result<(), String> {
    let range = w.resource::<Settings>().decoy_range();
    let hint = w.resource::<HintState>();
    let (planned, kit) = (hint.decoys, hint.kit.clone().ok_or("no kit")?);
    if planned != range {
        return Err(format!("the kit was planned with {planned:?}, the setting is {range:?}"));
    }
    let found = &w.resource::<PlayerProgress>().discovered;
    let spare = base_materials(w.resource::<RecipeDatabase>())
        .into_iter()
        .filter(|id| {
            found.contains(id) && !kit.items.contains(id) && !kit.intermediates.contains(id) && *id != kit.target
        })
        .count();
    let want = decoy_count(kit.items.len(), range).min(spare);
    if kit.decoys.len() == want {
        Ok(())
    } else {
        Err(format!(
            "{} decoys for {} ingredients with {range:?} ({spare} to spare): wanted {want}",
            kit.decoys.len(),
            kit.items.len()
        ))
    }
}

fn play_checks() -> Vec<Check> {
    use CardPart::*;
    use ProcessType::{Heat, Mix};
    let mut v = Vec::new();

    // --- the Hint button and its kits ---
    v.push(check(
        "Hint",
        "Hint lists targets; picking one shows what makes it, and the shelf becomes its kit",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            Op::Wait(5),
            Op::Click(marked::<HintButton>("the Hint button")),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<HintState>();
                    let (open, n) = (s.list_open, s.offered.len());
                    let rows = w.query::<&HintPick>().iter(w).count();
                    if open && n > 0 && rows == n {
                        Ok(())
                    } else {
                        Err(format!("list open={open}, {n} targets, {rows} rows"))
                    }
                }),
                30,
            ),
            Op::Shot("the Hint list"),
            Op::Click(marked::<HintPick>("the first target")),
            Op::Until(
                verify(|w| match &w.resource::<HintState>().target {
                    Some(_) => Ok(()),
                    None => Err("no target chosen".into()),
                }),
                30,
            ),
            Op::Until(hint_says("Made by: "), 30),
            Op::Expect(verify(|w| {
                let lines = hint_lines_now(w);
                if lines.len() == 1 {
                    Ok(())
                } else {
                    Err(format!("the first hint gives away more than the step's name: {lines:?}"))
                }
            })),
            Op::Until(shelf_is_the_kit(), 60),
        ],
    ));
    v.push(check(
        "Hint",
        "More hint gives one ingredient, then all of them, then the vessel and the route",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            setup(chase_a_multi_step_target),
            Op::Wait(5),
            Op::Click(marked::<HintMore>("More hint")),
            Op::Until(hint_says("One ingredient: "), 30),
            Op::Click(marked::<HintMore>("More hint")),
            Op::Until(hint_says("Ingredients: "), 30),
            Op::Click(marked::<HintMore>("More hint")),
            Op::Until(hint_says("In the "), 30),
            Op::Until(hint_says("The route:"), 10),
            Op::Expect(verify(|w| match w.query_filtered::<(), With<HintMore>>().iter(w).count() {
                0 => Ok(()),
                n => Err(format!("{n} More buttons after the last hint")),
            })),
            Op::Shot("a target with every hint shown"),
            Op::Click(marked::<HintShowTree>("In the tree")),
            Op::Until(
                verify(|w| {
                    let want = w.resource::<HintState>().target.map(|t| t.reaction);
                    let t = w.resource::<TechTreeState>();
                    if t.open && t.selected.is_some() && t.selected == want {
                        Ok(())
                    } else {
                        Err(format!("tree open={} on {:?}, target step {want:?}", t.open, t.selected))
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Hint",
        "A kit holds every precursor and a few decoys, and none of the steps in between",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            setup(chase_a_multi_step_target),
            Op::Until(shelf_is_the_kit(), 60),
            Op::Expect(verify(|w| {
                let kit = w.resource::<HintState>().kit.clone().ok_or("no kit")?;
                let shelf = shelf_ids(w);
                let db = w.resource::<RecipeDatabase>();
                let mut wrong = Vec::new();
                if kit.steps.len() < 2 {
                    wrong.push(format!("a {}-step route", kit.steps.len()));
                }
                if kit.intermediates.is_empty() || kit.intermediates.iter().any(|i| shelf.contains(i)) {
                    wrong.push(format!("intermediates {:?} on the shelf {shelf:?}", kit.intermediates));
                }
                if kit.decoys.is_empty() {
                    wrong.push("no decoys".into());
                }
                if !crate::ui::hint::makes_target(db, &kit) {
                    wrong.push("the kit can't make the target".into());
                }
                if wrong.is_empty() {
                    Ok(())
                } else {
                    Err(wrong.join("; "))
                }
            })),
            // as many decoys as the setting asks for
            Op::Expect(verify(kit_decoys_right)),
        ],
    ));
    v.push(check(
        "Hint",
        "The card's switch shows the whole shelf, and back to the kit",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            setup(chase_a_multi_step_target),
            Op::Until(shelf_is_the_kit(), 60),
            Op::Click(marked::<HintKitToggle>("the card's shelf switch")),
            Op::Until(
                verify(|w| {
                    let n = w.resource::<PlayerProgress>().discovered.len();
                    let count = w
                        .query_filtered::<&Text, With<crate::ui::inventory::ShelfCount>>()
                        .iter(w)
                        .next()
                        .map(|t| t.0.clone())
                        .unwrap_or_default();
                    if !w.resource::<Settings>().kit && count == format!("{n} on the shelf") {
                        Ok(())
                    } else {
                        Err(format!("the shelf says {count:?} with {n} discovered"))
                    }
                }),
                60,
            ),
            Op::Click(marked::<HintKitToggle>("the card's shelf switch")),
            Op::Until(shelf_is_the_kit(), 60),
        ],
    ));
    let decoy_step = |f: Field, down: bool| {
        target(format!("{f:?} {}", if down { "-" } else { "+" }), move |w| {
            let e = first::<SettingStep>(w, |s| s.0 == f && (s.1 < 0.0) == down)?;
            point_in(w, e, 0.5, 0.5)
        })
    };
    let mut ops = vec![
        setup(new_game),
        setup(|w| {
            let mut s = w.resource_mut::<Settings>();
            (s.next_step, s.kit, s.decoys_min, s.decoys_max) = (true, true, 3, 8);
        }),
        Op::Wait(5),
        setup(|w| {
            let db = w.resource::<RecipeDatabase>();
            let (progress, unlocks) = (w.resource::<PlayerProgress>(), w.resource::<ProcessUnlocks>());
            let first =
                targets(db, &|id| progress.discovered.contains(&id), &|p| unlocks.0.contains(p)).first().copied();
            if let Some(t) = first {
                chase(w, t);
            }
        }),
        Op::Until(verify(kit_decoys_right), 30),
        Op::Until(shelf_is_the_kit(), 60),
        setup(|w| w.resource_mut::<SettingsUi>().open = true),
        Op::Wait(5),
    ];
    // most 8 -> 5, fewest 3 -> 0: the chase's kit is planned again
    for _ in 0..3 {
        ops.push(Op::Click(decoy_step(Field::DecoysMax, true)));
        ops.push(Op::Click(decoy_step(Field::DecoysMin, true)));
    }
    ops.push(Op::Until(
        verify(|w| match w.resource::<Settings>().decoy_range() {
            (0, 5) => kit_decoys_right(w),
            r => Err(format!("the setting is {r:?} after three steps down each")),
        }),
        30,
    ));
    // fewest up past the most carries the most with it
    for _ in 0..7 {
        ops.push(Op::Click(decoy_step(Field::DecoysMin, false)));
    }
    ops.push(Op::Until(
        verify(|w| match w.resource::<Settings>().decoy_range() {
            (7, 7) => kit_decoys_right(w),
            r => Err(format!("the setting is {r:?} after raising the fewest to 7")),
        }),
        30,
    ));
    ops.push(setup(|w| {
        let mut s = w.resource_mut::<Settings>();
        (s.decoys_min, s.decoys_max) = (3, 8);
        w.resource_mut::<SettingsUi>().open = false;
    }));
    v.push(check("Hint", "The decoy settings set how many decoys a kit mixes in, and re-plan it", ops));
    v.push(check(
        "Hint",
        "Making the target ends the chase, and the whole shelf comes back",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            setup(chase_a_multi_step_target),
            Op::Until(shelf_is_the_kit(), 60),
            setup(|w| {
                let t = w.resource::<HintState>().target;
                if let Some(t) = t {
                    w.resource_mut::<PlayerProgress>().discover(t.product);
                }
            }),
            Op::Until(
                verify(|w| match w.resource::<HintState>().target {
                    None => Ok(()),
                    Some(t) => Err(format!("still chasing {t:?}")),
                }),
                30,
            ),
            Op::Until(toast_says("Target made: "), 30),
            Op::Until(
                verify(|w| {
                    let title = w
                        .query_filtered::<&Text, With<ShelfTitle>>()
                        .iter(w)
                        .next()
                        .map(|t| t.0.clone())
                        .unwrap_or_default();
                    if title == "SHELF" {
                        Ok(())
                    } else {
                        Err(format!("the shelf is titled {title:?}"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Hint",
        "Change goes back to the list, and its x back to the target",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            setup(|w| {
                let t = {
                    let db = w.resource::<RecipeDatabase>();
                    let p = w.resource::<PlayerProgress>();
                    let u = w.resource::<ProcessUnlocks>();
                    targets(db, &|id| p.discovered.contains(&id), &|x| u.0.contains(x)).first().copied()
                };
                if let Some(t) = t {
                    chase(w, t);
                }
            }),
            Op::Wait(5),
            Op::Click(marked::<HintChange>("Change")),
            Op::Until(state("the list is open", |w| w.resource::<HintState>().list_open), 30),
            Op::Click(target("the list's close button", |w| {
                let e = first::<crate::ui::hint::HintClose>(w, |_| true)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                state("back on the target card", |w| {
                    let s = w.resource::<HintState>();
                    !s.list_open && s.target.is_some()
                }),
                30,
            ),
        ],
    ));

    // --- the shelf: search, double-tap, the selection's look ---
    v.push(check(
        "Lab: shelf",
        "Typing in the shelf search filters the tiles; the x clears it",
        vec![
            setup(new_game),
            Op::Wait(5),
            Op::Click(marked::<ShelfSearchBox>("the shelf's search box")),
            Op::Until(state("the search is listening", |w| w.resource::<ShelfSearch>().typing), 30),
            Op::Key(KeyCode::KeyW),
            Op::Key(KeyCode::KeyA),
            Op::Key(KeyCode::KeyT),
            Op::Until(
                verify(|w| {
                    let text = w.resource::<ShelfSearch>().text.clone();
                    let names: Vec<String> = w
                        .query_filtered::<&Ingredient, With<ShelfTile>>()
                        .iter(w)
                        .map(|i| i.name.to_lowercase())
                        .collect();
                    if text == "wat" && !names.is_empty() && names.iter().all(|n| n.contains("wat")) {
                        Ok(())
                    } else {
                        Err(format!("search {text:?} shows {names:?}"))
                    }
                }),
                60,
            ),
            Op::Key(KeyCode::Backspace),
            Op::Until(state("Backspace took a letter away", |w| w.resource::<ShelfSearch>().text == "wa"), 30),
            Op::Click(marked::<ShelfSearchClear>("the search's clear button")),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<ShelfSearch>().clone();
                    let n = w.resource::<PlayerProgress>().discovered.len();
                    let built = shelf_ids(w).len();
                    if s.text.is_empty() && !s.typing && built == n {
                        Ok(())
                    } else {
                        Err(format!("search {:?} typing={}, {built} of {n} tiles", s.text, s.typing))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "Double-tapping a tile puts it in the vessel used last",
        vec![
            setup(new_game),
            setup(|w| {
                place(w, Mix, 0);
                place(w, Heat, 1);
            }),
            Op::Wait(5),
            Op::Click(card_part(Heat, Title)),
            Op::Until(
                verify(|w| {
                    let heat = card(w, Heat);
                    if w.resource::<crate::systems::drag_drop::ActiveVessel>().0 == heat {
                        Ok(())
                    } else {
                        Err("tapping the Fire didn't make it the active vessel".into())
                    }
                }),
                30,
            ),
            Op::DoubleClick(tile("Wood")),
            Op::Until(has_chip(Heat, "Wood"), 30),
            Op::Expect(chip_count(Mix, 0)),
            Op::Expect(selected_is(Some("Wood"))),
        ],
    ));
    v.push(check(
        "Lab: shelf",
        "A selected tile looks nothing like an element tile",
        vec![
            setup(new_game),
            Op::Wait(5),
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            Op::Wait(3),
            Op::Expect(verify(|w| {
                let look = |w: &mut World, name: &str| {
                    let e = shelf_tile_entity(w, name)?;
                    let border = border_of(w, e)?;
                    let outline = w.get::<Outline>(e).map(|o| o.width)?;
                    Some((border, outline))
                };
                let (sel_border, sel_outline) = look(w, "Water").ok_or("no Water tile")?;
                let (el_border, el_outline) = look(w, "Oxygen").ok_or("no Oxygen tile")?;
                if sel_border != el_border && sel_outline == Val::Px(2.0) && el_outline == Val::Px(0.0) {
                    Ok(())
                } else {
                    Err(format!(
                        "selected Water: {sel_border:?} / {sel_outline:?}; Oxygen at rest: {el_border:?} / {el_outline:?}"
                    ))
                }
            })),
        ],
    ));

    // --- the x on a substance in a vessel ---
    v.push(check(
        "Lab: vessels",
        "The x on a substance in a vessel takes it out, and puts nothing in",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            Op::Wait(5),
            Op::Drag(tile("Wood"), card_part(Heat, Zone)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            Op::Click(target("the x on the Wood in the Fire", |w| {
                let c = card(w, Heat)?;
                let x = descendant::<VesselChipRemove>(w, c)?;
                point_in(w, x, 0.5, 0.5)
            })),
            Op::Until(chip_count(Heat, 0), 30),
            Op::Wait(5),
            Op::Expect(chip_count(Heat, 0)),
            Op::Expect(selected_is(Some("Water"))),
        ],
    ));

    // --- contents stay drawn over their vessel ---
    v.push(check(
        "Lab: vessels",
        "A vessel's contents are drawn over it and take taps, whatever happened to the card",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            Op::Wait(5),
            Op::Drag(tile("Wood"), card_part(Heat, Zone)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            // Bevy moves an entity to new storage whenever it gains a component (its hover
            // and clipping bookkeeping do so unprompted). A card moved after its contents had
            // been stored used to be drawn over them: they took up room but could not be seen.
            setup(|w| {
                let cards: Vec<Entity> = w.query_filtered::<Entity, With<VesselCard>>().iter(w).collect();
                for c in cards {
                    w.entity_mut(c).insert(Restored);
                }
            }),
            Op::Click(tile("Water")),
            Op::Until(selected_is(Some("Water")), 30),
            Op::Click(card_part(Heat, Title)),
            Op::Until(chip_count(Heat, 2), 30),
            Op::Wait(3),
            Op::Expect(contents_drawn_over_cards()),
            Op::Click(target("the x on a substance in the Fire", |w| {
                let c = card(w, Heat)?;
                let x = descendant::<VesselChipRemove>(w, c)?;
                point_in(w, x, 0.5, 0.5)
            })),
            Op::Until(chip_count(Heat, 1), 30),
        ],
    ));

    // --- the notification history ---
    v.push(check(
        "Notifications",
        "The bell lists past discoveries and milestones, newest first; Esc closes it",
        vec![
            setup(new_game),
            setup(|w| {
                w.resource_mut::<Journal>().0.clear();
                let mut t = w.resource_mut::<Toasts>();
                t.push(ToastKind::Discovery, "New: Quicklime (check one)");
                t.push(ToastKind::Hint, "a hint, which the history leaves out");
                t.push(ToastKind::Milestone, "A milestone (check two)");
            }),
            Op::Wait(5),
            Op::Click(marked::<JournalButton>("the bell")),
            Op::Until(
                verify(|w| {
                    // the rows in the order the list shows them (entity ids say nothing about order)
                    let list = first::<crate::ui::toasts::JournalList>(w, |_| true).ok_or("no list")?;
                    let kids: Vec<Entity> = w.get::<Children>(list).map(|c| c.iter().collect()).unwrap_or_default();
                    let order: Vec<usize> = kids.iter().filter_map(|e| w.get::<JournalRow>(*e).map(|r| r.0)).collect();
                    let open = w.resource::<JournalUi>().open;
                    let texts: Vec<String> = w.resource::<Journal>().0.iter().map(|e| e.text.clone()).collect();
                    if open && order == vec![1, 0] && texts.len() == 2 && texts[1].starts_with("A milestone") {
                        Ok(())
                    } else {
                        Err(format!("open={open}, rows {order:?}, journal {texts:?}"))
                    }
                }),
                30,
            ),
            Op::Shot("the notification history"),
            Op::Key(KeyCode::Escape),
            Op::Until(state("the history closed", |w| !w.resource::<JournalUi>().open), 30),
        ],
    ));

    // --- a short screen ---
    v.push(check(
        "Lab: vessels",
        "On a short screen a vessel card goes compact and fits the bench",
        vec![
            setup(new_game),
            // a big interface makes any screen short (and holds even where a phone's size
            // would otherwise be fitted)
            setup(|w| {
                w.resource_mut::<crate::ui::settings::FitInterface>().0 = false;
                w.resource_mut::<Settings>().ui_scale = 1.6;
            }),
            Op::Wait(10),
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Water"), card_part(Mix, Zone)),
            Op::Drag(tile("Wood"), card_part(Mix, Zone)),
            Op::Until(chip_count(Mix, 2), 30),
            Op::Wait(5),
            Op::Shot("a compact vessel card"),
            Op::Expect(verify(|w| {
                let bench = w.resource::<crate::ui::inventory::Dock>().bench;
                let c = card(w, Mix).ok_or("no Mortar")?;
                let h = w.get::<ComputedNode>(c).map(|n| n.size.y * n.inverse_scale_factor()).unwrap_or(0.0);
                let small = descendant::<crate::systems::reaction_check::VesselArtSmall>(w, c)
                    .and_then(|e| w.get::<Node>(e))
                    .is_some_and(|n| n.display != Display::None);
                if bench < crate::systems::reaction_check::COMPACT_BENCH && small && h > 0.0 && h <= bench {
                    Ok(())
                } else {
                    Err(format!("card {h:.0} px tall on a {bench:.0} px bench, small picture shown={small}"))
                }
            })),
        ],
    ));
    v
}

// ---------------------------------------------------------------------------------------
// The title and menu, zooming and panning the bench, running a chain, the selection bar
// ---------------------------------------------------------------------------------------
fn menu_is(stage: MenuStage) -> Verify {
    verify(move |w| {
        let now = w.resource::<MainMenu>().stage;
        if now == stage {
            Ok(())
        } else {
            Err(format!("the menu is at {now:?}, expected {stage:?}"))
        }
    })
}

fn zoom_is(z: f32) -> Verify {
    verify(move |w| {
        let now = w.resource::<BenchZoom>().0;
        if (now - z).abs() < 0.01 {
            Ok(())
        } else {
            Err(format!("zoom {now}, expected {z}"))
        }
    })
}

fn bench_offset(w: &mut World) -> Option<Vec2> {
    let pane = w.query_filtered::<Entity, With<CanvasScrollingPane>>().iter(w).next()?;
    left_top(w, pane)
}

/// The bench sits where drags adding up to `dragged` screen px left it: that many interface
/// px over, at any interface size (a phone's is fitted to its screen).
fn bench_at(dragged: Vec2) -> Verify {
    verify(move |w| {
        let want = dragged / w.resource::<UiScale>().0;
        let p = bench_offset(w).ok_or("no bench pane")?;
        let root = w.query_filtered::<&ScrollPosition, With<ReactionCanvasRoot>>().iter(w).next().map(|s| s.0);
        if (p - want).abs().max_element() > 1.0 {
            Err(format!("bench offset {p}, expected {want}"))
        } else if root.is_some_and(|r| r != Vec2::ZERO) {
            Err(format!("the bench itself scrolled to {root:?}: its background no longer lines up"))
        } else {
            Ok(())
        }
    })
}

/// Shown (not folded away) on `p`'s card.
fn card_shows<C: Component>(p: ProcessType, what: &'static str, want: bool) -> Verify {
    verify(move |w| {
        let c = card(w, p.clone()).ok_or("no card")?;
        let e = descendant::<C>(w, c).ok_or(format!("no {what}"))?;
        let shown = w.get::<Node>(e).is_some_and(|n| n.display != Display::None);
        if shown == want {
            Ok(())
        } else {
            Err(format!("{what} shown={shown}, expected {want}"))
        }
    })
}

fn chain_button(p: ProcessType) -> Target {
    let label = format!("the {}'s run-chain button", vessel_name(&p));
    target(label, move |w| {
        let c = card(w, p.clone())?;
        let b = descendant::<VesselChainButton>(w, c)?;
        point_in(w, b, 0.5, 0.5)
    })
}

/// Link two cards' ports directly, the way a drag between them does.
fn link(w: &mut World, from: ProcessType, to: ProcessType) {
    let (Some(a), Some(b)) = (card(w, from), card(w, to)) else { return };
    let (Some(out), Some(inp)) = (descendant::<OutputPort>(w, a), descendant::<InputPort>(w, b)) else { return };
    w.spawn(ReactionLink { from_vessel: a, from_port: out, to_vessel: b, to_port: inp });
}

fn menu_and_bench_checks() -> Vec<Check> {
    use CardPart::*;
    use ProcessType::{Heat, Mix};
    let mut v = Vec::new();

    // --- the title, the notice and the menu ---
    v.push(check(
        "Menu",
        "The title and the licence notice lead to the menu, and Play goes to the lab",
        vec![
            // (the title moves on by itself after a moment, so each stage is set up fresh; a
            // stage ignores keys for its first 0.2 s, a time, so the waits are times too:
            // frames go by many times faster on a fast machine)
            setup(|w| *w.resource_mut::<MainMenu>() = MainMenu::starting(false)),
            Op::Until(menu_is(MenuStage::Title), 10),
            Op::Shot("the title"),
            setup(|w| *w.resource_mut::<MainMenu>() = MainMenu::starting(false)),
            Op::Pause(0.4),
            Op::Key(KeyCode::Enter),
            Op::Until(menu_is(MenuStage::Notice), 30),
            setup(|w| {
                let mut menu = MainMenu::starting(false);
                menu.advance();
                *w.resource_mut::<MainMenu>() = menu;
            }),
            Op::Wait(5),
            Op::Shot("the licence and sources notice"),
            Op::Pause(0.4),
            Op::Key(KeyCode::Enter),
            Op::Until(menu_is(MenuStage::Menu), 30),
            Op::Wait(5),
            Op::Shot("the menu"),
            Op::Click(marked::<MenuPlay>("Play / Continue")),
            Op::Until(menu_is(MenuStage::Hidden), 30),
        ],
    ));
    v.push(check(
        "Menu",
        "Left alone, the title moves on to the notice and then the menu",
        vec![
            // (1.6 s and then 6 s: frame limits generous enough for any frame rate)
            setup(|w| *w.resource_mut::<MainMenu>() = MainMenu::starting(false)),
            Op::Until(menu_is(MenuStage::Notice), 4000),
            Op::Until(menu_is(MenuStage::Menu), 12000),
        ],
    ));
    v.push(check(
        "Menu",
        "Esc in the lab opens the menu; Esc or Continue goes back",
        vec![
            Op::Key(KeyCode::Escape),
            Op::Until(menu_is(MenuStage::Menu), 30),
            Op::Key(KeyCode::Escape),
            Op::Until(menu_is(MenuStage::Hidden), 30),
            Op::Key(KeyCode::Escape),
            Op::Until(menu_is(MenuStage::Menu), 30),
            Op::Click(marked::<MenuPlay>("Continue")),
            Op::Until(menu_is(MenuStage::Hidden), 30),
            Op::Expect(state("settings stayed shut", |w| !w.resource::<SettingsUi>().open)),
        ],
    ));
    v.push(check(
        "Menu",
        "Settings from the menu closes back to the menu",
        vec![
            setup(|w| w.resource_mut::<MainMenu>().show_menu()),
            Op::Wait(5),
            Op::Click(marked::<MenuSettings>("Settings in the menu")),
            Op::Until(state("settings open", |w| w.resource::<SettingsUi>().open), 30),
            Op::Key(KeyCode::Escape),
            Op::Until(state("settings closed", |w| !w.resource::<SettingsUi>().open), 30),
            Op::Expect(menu_is(MenuStage::Menu)),
            Op::Until(
                verify(|w| {
                    let e = first::<MenuRoot>(w, |_| true).ok_or("no menu")?;
                    if w.get::<Node>(e).is_some_and(|n| n.display != Display::None) {
                        Ok(())
                    } else {
                        Err("the menu did not come back".into())
                    }
                }),
                30,
            ),
        ],
    ));

    // --- the Hint button names a target ---
    v.push(check(
        "Hint",
        "The Hint button names the next target, and the list opens with it on top",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            Op::Wait(10),
            Op::Until(
                verify(|w| {
                    let label = w
                        .query_filtered::<&Text, With<HintButtonText>>()
                        .iter(w)
                        .next()
                        .map(|t| t.0.clone())
                        .unwrap_or_default();
                    let s = w.resource::<HintState>().suggested;
                    match (s, label.strip_prefix("Hint · ")) {
                        (Some(_), Some(name)) if !name.is_empty() => Ok(()),
                        _ => Err(format!("the button says {label:?}, suggestion {s:?}")),
                    }
                }),
                30,
            ),
            Op::Shot("the Hint button naming a target"),
            Op::Click(marked::<HintButton>("the Hint button")),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<HintState>();
                    let (open, first, suggested) = (s.list_open, s.offered.first().copied(), s.suggested);
                    let tags = w.query::<&HintSuggestedTag>().iter(w).count();
                    if open && first.is_some() && first == suggested && tags == 1 {
                        Ok(())
                    } else {
                        Err(format!("open={open}, first {first:?}, suggested {suggested:?}, {tags} SUGGESTED tag(s)"))
                    }
                }),
                30,
            ),
            Op::Shot("the Hint list with its suggestion on top"),
        ],
    ));

    // --- running a chain ---
    v.push(check(
        "Lab: links",
        "The run-chain button shows only on a vessel something feeds",
        vec![
            setup(|w| place(w, Heat, 0)),
            setup(|w| place(w, Mix, 1)),
            Op::Wait(5),
            Op::Expect(card_shows::<VesselChainButton>(Mix, "the run-chain button", false)),
            Op::Drag(card_part(Heat, OutPort), card_part(Mix, InPort)),
            Op::Until(card_shows::<VesselChainButton>(Mix, "the run-chain button", true), 30),
            Op::Expect(card_shows::<VesselChainButton>(Heat, "the run-chain button (on the first vessel)", false)),
        ],
    ));
    v.push(check(
        "Lab: links",
        "Run chain reacts the chain from its start: Fire makes Charcoal, which reaches the Mortar",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            setup(|w| place(w, Mix, 1)),
            Op::Wait(5),
            setup(|w| link(w, Heat, Mix)),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            Op::Click(chain_button(Mix)),
            Op::Until(has_chip(Mix, "Charcoal"), WAIT),
        ],
    ));

    // --- zooming the bench ---
    v.push(check(
        "Lab: zoom",
        "Zooming out shrinks the bench and folds the cards; zooming back restores them",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            setup(|w| place(w, Mix, 1)),
            Op::Wait(5),
            Op::Drag(tile("Water"), card_part(Mix, Zone)),
            Op::Until(has_chip(Mix, "Water"), 30),
            Op::Expect(card_shows::<VesselReactButton>(Mix, "the React button", true)),
            Op::Click(marked::<BenchZoomOut>("zoom out")),
            Op::Until(zoom_is(0.8), 30),
            Op::Wait(5),
            // still a working bench at 80%: a drop lands where the card shows
            Op::Drag(tile("Wood"), card_part(Mix, Zone)),
            Op::Until(has_chip(Mix, "Wood"), 30),
            Op::Click(marked::<BenchZoomOut>("zoom out")),
            Op::Until(zoom_is(0.6), 30),
            Op::Until(card_shows::<VesselReactButton>(Mix, "the React button", false), 30),
            Op::Expect(card_shows::<EquationText>(Mix, "the equation", false)),
            Op::Expect(verify(|w| {
                let c = card(w, Mix).ok_or("no Mortar")?;
                let scale = w.get::<UiGlobalTransform>(c).map(|t| t.to_scale_angle_translation().0.x).unwrap_or(1.0);
                let ui = w.resource::<UiScale>().0;
                if (scale / ui - 0.6).abs() < 0.05 || (scale - 0.6).abs() < 0.05 {
                    Ok(())
                } else {
                    Err(format!("the card is drawn at {scale:.2}, not 0.6"))
                }
            })),
            Op::Shot("the bench zoomed out, cards folded"),
            Op::Click(marked::<BenchZoomOut>("zoom out")),
            Op::Until(zoom_is(0.45), 30),
            Op::Click(marked::<BenchZoomOut>("zoom out")),
            Op::Wait(3),
            Op::Expect(zoom_is(0.45)),
            Op::Click(marked::<BenchZoomIn>("zoom in")),
            Op::Click(marked::<BenchZoomIn>("zoom in")),
            Op::Click(marked::<BenchZoomIn>("zoom in")),
            Op::Until(zoom_is(1.0), 30),
            Op::Until(card_shows::<VesselReactButton>(Mix, "the React button", true), 30),
            Op::Expect(has_chip(Mix, "Wood")),
        ],
    ));

    // --- panning the bench comes back to where it started ---
    v.push(check(
        "Lab: moving",
        "Dragging the bench back returns it exactly to the start, background and all",
        vec![
            setup(|w| place(w, Mix, 0)),
            Op::Wait(5),
            Op::DragBy(bench_spot(), Vec2::new(-300.0, -150.0)),
            Op::Until(bench_at(Vec2::new(-300.0, -150.0)), 30),
            // past the start: it stops there instead of going on, or stopping short
            Op::DragBy(bench_spot(), Vec2::new(500.0, 400.0)),
            Op::Until(bench_at(Vec2::ZERO), 30),
            Op::Wheel(bench_spot(), -3.0),
            Op::Until(
                verify(|w| {
                    let p = bench_offset(w).ok_or("no bench pane")?;
                    if p.y < -50.0 {
                        Ok(())
                    } else {
                        Err(format!("the wheel did not pan the bench: {p}"))
                    }
                }),
                30,
            ),
            Op::Wheel(bench_spot(), 10.0),
            Op::Until(bench_at(Vec2::ZERO), 30),
            Op::DragBy(bench_spot(), Vec2::new(-400.0, -200.0)),
            Op::Until(bench_at(Vec2::new(-400.0, -200.0)), 30),
            Op::Shot("the bench panned: the background still lines up"),
            Op::DragBy(bench_spot(), Vec2::new(400.0, 200.0)),
            Op::Until(bench_at(Vec2::ZERO), 30),
        ],
    ));

    // --- the selection bar ---
    v.push(check(
        "Lab: shelf",
        "The selection bar keeps the name on one line, and its book opens the library there",
        vec![
            setup(|w| discover(w, &["Chloroauric Acid"])),
            Op::Wait(5),
            Op::Click(tile("Chloroauric Acid")),
            Op::Until(selected_is(Some("Chloroauric Acid")), 30),
            Op::MoveTo(bench_spot()),
            Op::Wait(15),
            Op::Expect(verify(|w| {
                let e = first::<SelectionName>(w, |_| true).ok_or("no name")?;
                let (h, font) = (
                    w.get::<ComputedNode>(e).map(|n| n.size.y * n.inverse_scale_factor()).unwrap_or(0.0),
                    w.get::<TextFont>(e).map(|f| f.font_size),
                );
                if h > 0.0 && h < 30.0 {
                    Ok(())
                } else {
                    Err(format!("the name is {h:.0} px tall ({font:?}): it wrapped"))
                }
            })),
            Op::Shot("the selection bar"),
            Op::Click(marked::<SelectionOpenButton>("the selection's book")),
            Op::Until(
                verify(|w| {
                    let open = w.resource::<CodexState>().open;
                    if open {
                        Ok(())
                    } else {
                        Err("the library did not open".into())
                    }
                }),
                30,
            ),
            setup(new_game),
            Op::Wait(5),
        ],
    ));
    v
}

// ---------------------------------------------------------------------------------------
// Buttons fire on a tap, not a swipe; linking by tap and onto a whole card
// ---------------------------------------------------------------------------------------
/// How far the vessel list is scrolled along its length (down it, or across the strip it
/// is upright).
fn sidebar_scroll(w: &mut World) -> f32 {
    w.query_filtered::<&ScrollPosition, With<VesselSidebar>>().iter(w).next().map_or(0.0, |s| s.0.x.max(s.0.y))
}

/// 100 px along the vessel list from its Mortar button: up the list, or across the strip.
fn along_sidebar() -> Target {
    target("100 px along the vessel list", |w| {
        let e = first::<ProcessButton>(w, |b| b.process == ProcessType::Mix)?;
        let from = point_in(w, e, 0.5, 0.5)?;
        let across = w
            .query_filtered::<&Node, With<VesselSidebar>>()
            .iter(w)
            .next()
            .is_some_and(|n| n.overflow.x == OverflowAxis::Scroll && n.overflow.y != OverflowAxis::Scroll);
        Some(from + if across { Vec2::new(-100.0, 0.0) } else { Vec2::new(0.0, -100.0) })
    })
}

fn no_vessels() -> Verify {
    verify(|w| match w.query::<&VesselCard>().iter(w).count() {
        0 => Ok(()),
        n => Err(format!("{n} vessel(s) on the bench")),
    })
}

fn linked(from: ProcessType, to: ProcessType) -> Verify {
    verify(move |w| {
        let (a, b) = (card(w, from.clone()), card(w, to.clone()));
        let ok = w.query::<&ReactionLink>().iter(w).any(|l| Some(l.from_vessel) == a && Some(l.to_vessel) == b);
        if ok {
            Ok(())
        } else {
            Err(format!("no {} -> {} link", vessel_name(&from), vessel_name(&to)))
        }
    })
}

fn picked(want: bool) -> Verify {
    verify(move |w| match (w.resource::<LinkPick>().0.is_some(), want) {
        (true, true) | (false, false) => Ok(()),
        (true, false) => Err("a port is still picked to link from".into()),
        (false, true) => Err("no port picked to link from".into()),
    })
}

/// The shelf has the screen (a phone's keyboard is up): it reaches up to the header, the
/// bench is hidden and Done shows; or it is back to normal.
fn shelf_only(want: bool) -> Verify {
    verify(move |w| {
        let typing = w.resource::<ShelfSearch>().typing;
        let bench = w
            .query_filtered::<&InheritedVisibility, With<ReactionCanvasRoot>>()
            .iter(w)
            .next()
            .is_some_and(|v| v.get());
        let done = first::<ShelfSearchDone>(w, |_| true)
            .and_then(|e| w.get::<ComputedNode>(e))
            .is_some_and(|n| n.size.x > 0.0);
        let dock_h = first::<crate::ui::inventory::ShelfDock>(w, |_| true)
            .and_then(|e| w.get::<ComputedNode>(e).map(|n| n.size.y * n.inverse_scale_factor()))
            .unwrap_or(0.0);
        let screen = w
            .query_filtered::<&Window, With<PrimaryWindow>>()
            .iter(w)
            .next()
            .map_or(0.0, |win| win.height() / w.resource::<UiScale>().0);
        let tall = dock_h > screen - crate::ui::theme::HEADER_H - 2.0;
        let got = (typing, !bench, done, tall);
        if got == (want, want, want, want) {
            Ok(())
        } else {
            Err(format!("typing, bench hidden, Done showing, shelf full height: {got:?}"))
        }
    })
}

fn tap_and_link_checks() -> Vec<Check> {
    use CardPart::*;
    use ProcessType::{Heat, Mix};
    let mut v = Vec::new();
    v.push(check(
        "Touch",
        "A finger swiping the vessel list scrolls it and puts no vessel on the bench",
        vec![
            setup(new_game),
            Op::Wait(5),
            setup(|w| {
                for mut sp in w.query_filtered::<&mut ScrollPosition, With<VesselSidebar>>().iter_mut(w) {
                    sp.0 = Vec2::ZERO;
                }
            }),
            Op::Wait(2),
        ]
        .into_iter()
        .chain(finger_slide(sidebar_button(Mix), Slide::To(along_sidebar()), 0.0))
        .chain([
            Op::Until(
                verify(|w| match sidebar_scroll(w) {
                    y if y > 20.0 => Ok(()),
                    y => Err(format!("the vessel list is at {y:.0}")),
                }),
                30,
            ),
            Op::Expect(no_vessels()),
        ])
        .collect(),
    ));
    v.push(check(
        "Lab: vessels",
        "Pressing a vessel button and sliding off it before letting go places nothing",
        vec![
            setup(new_game),
            Op::Wait(5),
            Op::Press(sidebar_button(Mix)),
            Op::MoveTo(bench_spot()),
            Op::Release,
            Op::Wait(5),
            Op::Expect(no_vessels()),
            Op::Click(sidebar_button(Mix)),
            Op::Until(verify(|w| card(w, Mix).map(|_| ()).ok_or_else(|| "a click placed nothing".to_string())), 30),
        ],
    ));
    v.push(check(
        "Lab: links",
        "Tapping an output port and then another vessel links them",
        vec![
            setup(|w| place(w, Mix, 0)),
            setup(|w| place(w, Heat, 1)),
            Op::Wait(5),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(true), 30),
            Op::Shot("an output port picked to link from"),
            Op::Click(card_part(Heat, Art)),
            Op::Until(linked(Mix, Heat), 30),
            Op::Expect(picked(false)),
        ],
    ));
    v.push(check(
        "Lab: links",
        "A link dragged onto the middle of a vessel links them",
        vec![
            setup(|w| place(w, Mix, 0)),
            setup(|w| place(w, Heat, 1)),
            Op::Wait(5),
            Op::Drag(card_part(Mix, OutPort), card_part(Heat, Zone)),
            Op::Until(linked(Mix, Heat), 30),
            Op::Shot("a link between two vessels"),
        ],
    ));
    v.push(check(
        "Touch",
        "With a phone's keyboard up the shelf has the screen; a substance tapped, or Done, gives the bench back",
        vec![
            setup(new_game),
            setup(|w| *w.resource_mut::<crate::platform::SoftKeyboard>() = crate::platform::SoftKeyboard(true)),
            Op::Wait(3),
            Op::Click(marked::<ShelfSearchBox>("the shelf's search box")),
            Op::Until(shelf_only(true), 30),
            Op::Key(KeyCode::KeyW),
            Op::Key(KeyCode::KeyO),
            Op::Wait(3),
            Op::Shot("the shelf alone while a phone's keyboard is up"),
            Op::Click(tile("Wood")),
            Op::Until(shelf_only(false), 30),
            Op::Expect(verify(|w| match (w.resource::<SelectedSubstance>().0, sub_id(w, "Wood")) {
                (Some(a), Some(b)) if a == b => Ok(()),
                (s, _) => Err(format!("selected {s:?} after tapping Wood")),
            })),
            Op::Click(marked::<ShelfSearchBox>("the shelf's search box")),
            Op::Until(shelf_only(true), 30),
            Op::Click(marked::<ShelfSearchDone>("Done")),
            Op::Until(shelf_only(false), 30),
        ],
    ));
    v.push(check(
        "Hint",
        "The button's suggestion moves on with a discovery, even one that isn't it",
        vec![
            setup(new_game),
            Op::Wait(5),
            Op::Until(
                verify(|w| {
                    let was = w.resource::<HintState>().suggested.ok_or("nothing suggested")?;
                    w.resource_mut::<Scratch>().0.insert("was", was.product as f32);
                    // discover something no target is: the suggestion should still move on
                    let db = w.resource::<RecipeDatabase>();
                    let progress = w.resource::<PlayerProgress>();
                    let unlocks = w.resource::<ProcessUnlocks>();
                    let known = |id: u32| progress.discovered.contains(&id);
                    let open = |p: &ProcessType| unlocks.0.contains(p);
                    let list = targets(db, &known, &open);
                    if list.len() < 2 {
                        return Err(format!("only {} target(s) to take turns between", list.len()));
                    }
                    let gd = w.resource::<GameData>();
                    let subs = w.resource::<Assets<Substances>>().get(&gd.substances).ok_or("no substances")?;
                    let other = subs
                        .0
                        .keys()
                        .copied()
                        .filter(|id| !known(*id) && !list.iter().any(|t| t.product == *id))
                        .min()
                        .ok_or("nothing else to discover")?;
                    w.resource_mut::<PlayerProgress>().discovered.insert(other);
                    Ok(())
                }),
                30,
            ),
            Op::Until(
                verify(|w| {
                    let was = w.resource::<Scratch>().0.get("was").copied().unwrap_or(-1.0) as u32;
                    match w.resource::<HintState>().suggested {
                        Some(t) if t.product != was => Ok(()),
                        s => Err(format!("still suggesting {s:?}")),
                    }
                }),
                30,
            ),
            setup(new_game),
            Op::Wait(3),
        ],
    ));
    v.push(check(
        "Lab: links",
        "A picked port is let go by a tap on the bench, by tapping it again, or by Esc",
        vec![
            setup(|w| place(w, Mix, 0)),
            setup(|w| place(w, Heat, 1)),
            Op::Wait(5),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(true), 30),
            Op::Click(bench_spot()),
            Op::Until(picked(false), 30),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(true), 30),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(false), 30),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(true), 30),
            Op::Key(KeyCode::Escape),
            Op::Until(picked(false), 30),
            Op::Expect(verify(|w| match w.query::<&ReactionLink>().iter(w).count() {
                0 => Ok(()),
                n => Err(format!("{n} link(s) made")),
            })),
        ],
    ));
    v.push(check(
        "Lab: links",
        "Picking a port again shows its notice once, not a stack of copies",
        vec![
            setup(|w| place(w, Mix, 0)),
            setup(|w| place(w, Heat, 1)),
            Op::Wait(5),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(true), 30),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(false), 30),
            Op::Click(card_part(Mix, OutPort)),
            Op::Until(picked(true), 30),
            Op::Wait(5),
            Op::Expect(verify(|w| {
                let notices = w
                    .query::<(&Text, &ChildOf)>()
                    .iter(w)
                    .filter(|(t, parent)| {
                        t.0.contains("Now tap the vessel")
                            && w.get::<crate::ui::toasts::Toast>(parent.parent()).is_some()
                    })
                    .count();
                if notices == 1 {
                    Ok(())
                } else {
                    Err(format!("{notices} copies of the notice showing"))
                }
            })),
        ],
    ));
    // the line is drawn by its own camera from the ports' screen positions: it has to stay
    // on the dots whatever size the bench and the interface are drawn at
    let zoom = |z: f32| setup(move |w| w.resource_mut::<BenchZoom>().0 = z);
    let size = |s: f32| setup(move |w| w.resource_mut::<crate::ui::settings::Settings>().ui_scale = s);
    let mut ops = vec![
        setup(|w| place(w, Mix, 0)),
        setup(|w| place(w, Heat, 1)),
        Op::Wait(5),
        Op::Click(card_part(Mix, OutPort)),
        Op::Click(card_part(Heat, Art)),
        Op::Until(linked(Mix, Heat), 30),
        Op::Expect(links_on_dots()),
    ];
    for z in [0.8, 0.6, 0.45, 1.0] {
        ops.extend([zoom(z), Op::Wait(4), Op::Expect(links_on_dots())]);
    }
    for s in [1.25, 0.8, 1.0] {
        ops.extend([size(s), Op::Wait(6), Op::Expect(links_on_dots())]);
    }
    // and as a vessel is moved, and the bench panned
    ops.extend([
        Op::DragBy(card_part(Heat, Art), Vec2::new(140.0, 90.0)),
        Op::Wait(4),
        Op::Expect(links_on_dots()),
        Op::DragBy(bench_spot(), Vec2::new(-120.0, -60.0)),
        Op::Wait(4),
        Op::Expect(links_on_dots()),
    ]);
    v.push(check("Lab: links", "A link's ends stay on its ports at every bench zoom and interface size", ops));
    // zooming keeps the middle of the bench in place; where that runs into the bench's edge,
    // coming back must not drift (vessels near the top-left used to leave the screen)
    let at_screen = |w: &mut World| {
        let c = card(w, Mix)?;
        w.get::<UiGlobalTransform>(c).map(|g| g.translation)
    };
    let mut ops = vec![
        setup(|w| place(w, Mix, 0)),
        Op::Wait(5),
        setup(move |w| {
            if let Some(p) = at_screen(w) {
                w.resource_mut::<Scratch>().0.extend([("x", p.x), ("y", p.y)]);
            }
        }),
    ];
    for z in [0.8, 0.6, 0.45, 0.6, 0.8, 1.0] {
        ops.extend([zoom(z), Op::Wait(3)]);
    }
    ops.push(Op::Expect(verify(move |w| {
        let s = &w.resource::<Scratch>().0;
        let was = Vec2::new(s.get("x").copied().unwrap_or(f32::NAN), s.get("y").copied().unwrap_or(f32::NAN));
        let now = at_screen(w).ok_or("no Mortar on the bench")?;
        if was.distance(now) < 1.0 {
            Ok(())
        } else {
            Err(format!("the Mortar was at {was:.0}, and after zooming out and back it is at {now:.0}"))
        }
    })));
    v.push(check("Lab: moving", "Zooming out to the least and back in comes back to the same view", ops));
    v
}

/// Every drawn link ends on its ports' dots: each end, projected back through the camera
/// that draws the links, lands within 3 px of the middle of the dot it belongs to.
fn links_on_dots() -> Verify {
    verify(|w| {
        let window = w.query_filtered::<&Window, With<PrimaryWindow>>().iter(w).next().cloned().ok_or("no window")?;
        let (cam, at) = w
            .query::<(&Camera, &GlobalTransform)>()
            .iter(w)
            .find(|(c, _)| c.order == 1)
            .map(|(c, g)| (c.clone(), *g))
            .ok_or("no camera for the links")?;
        let scale = cam.target_scaling_factor().unwrap_or(1.0);
        let ports: Vec<Entity> = w.query::<&ReactionLink>().iter(w).flat_map(|l| [l.from_port, l.to_port]).collect();
        if ports.is_empty() {
            return Err("no links on the bench".into());
        }
        let mut off = Vec::new();
        for port in ports {
            let gt = *w.get::<UiGlobalTransform>(port).ok_or("a link's port is gone")?;
            let end = crate::systems::link_renderer::port_point(&gt, &window);
            let seen =
                cam.world_to_viewport(&at, end.extend(0.0)).map_err(|e| format!("a link end is off camera: {e:?}"))?;
            let dot = w
                .get::<Children>(port)
                .and_then(|c| c.iter().find(|d| w.get::<BackgroundColor>(*d).is_some()))
                .ok_or("a port has no dot")?;
            let middle = w.get::<UiGlobalTransform>(dot).ok_or("a dot has no place")?.translation / scale;
            let d = seen.distance(middle);
            if d > 3.0 {
                off.push(format!("{d:.1} px from its dot (end {seen:.0}, dot {middle:.0})"));
            }
        }
        if off.is_empty() {
            Ok(())
        } else {
            let z = w.resource::<BenchZoom>().0;
            let s = w.resource::<UiScale>().0;
            Err(format!("at zoom {z}, interface {s}: {}", off.join("; ")))
        }
    })
}

// ---------------------------------------------------------------------------------------
// Transients: made and used at once
// ---------------------------------------------------------------------------------------
/// The vessel's status line says it.
fn status_says(p: ProcessType, want: &'static str) -> Verify {
    verify(move |w| {
        let Some(c) = card(w, p.clone()) else { return Err(format!("no {} on the bench", vessel_name(&p))) };
        let text: Vec<String> = w
            .query_filtered::<(&Text, &ChildOf), With<crate::systems::reaction_check::EquationText>>()
            .iter(w)
            .filter(|(_, parent)| parent.parent() == c)
            .map(|(t, _)| t.0.clone())
            .collect();
        if text.iter().any(|t| t.contains(want)) {
            Ok(())
        } else {
            Err(format!("the {} says {text:?}", vessel_name(&p)))
        }
    })
}

/// For each transient: its maker linked by a tap into the first step that uses it (in
/// another vessel), started from the maker. And once: a transient nothing takes breaks
/// down where it was made, and is never on the shelf even when known.
pub(super) fn transient_checks(world: &mut World) -> Vec<Check> {
    use CardPart::*;
    let Some(db) = world.get_resource::<RecipeDatabase>() else { return vec![] };
    let mut transient: Vec<u32> = db.transient.iter().copied().collect();
    transient.sort_unstable();
    let pairs: Vec<(u32, Reaction, Reaction)> = transient
        .iter()
        .filter_map(|&t| {
            let maker = db.maker_of(t)?.clone();
            let user = db
                .authored
                .iter()
                .find(|r| r.process != maker.process && r.reactants.iter().any(|s| s.substance_id == t))?
                .clone();
            Some((t, maker, user))
        })
        .collect();
    let mut out = Vec::new();
    for (t, maker, user) in &pairs {
        let (mp, up) = (maker.process.clone(), user.process.clone());
        let name: &'static str = Box::leak(
            format!(
                "{} from {} is tapped into {} and set off from the first vessel ({} -> {})",
                sub_name(world, *t),
                maker.name,
                user.name,
                vessel_name(&mp),
                vessel_name(&up)
            )
            .into_boxed_str(),
        );
        let mut ops = stage_everything();
        for p in [mp.clone(), up.clone()] {
            ops.push(Op::Click(sidebar_button(p.clone())));
            ops.push(Op::Until(
                verify(move |w| {
                    card(w, p.clone()).map(|_| ()).ok_or_else(|| format!("no {} on the bench", vessel_name(&p)))
                }),
                30,
            ));
        }
        ops.extend(load(world, user, Some(*t)));
        ops.push(Op::Click(card_part(mp.clone(), OutPort)));
        ops.push(Op::Until(picked(true), 30));
        ops.push(Op::Click(card_part(up.clone(), Art)));
        ops.push(Op::Until(linked(mp.clone(), up.clone()), 30));
        ops.extend(load(world, maker, None));
        ops.push(Op::Click(card_part(mp.clone(), React)));
        let products: Vec<u32> = user.products.iter().map(|s| s.substance_id).collect();
        let what = names(world, &products);
        ops.push(Op::Until(has_ids(up.clone(), products, what), WAIT * 2));
        ops.push(Op::Expect(reacted(up.clone(), user.name.clone())));
        out.push(check("Transients", name, ops));
    }
    if let Some((t, maker, _)) = pairs.first() {
        let (t, mp) = (*t, maker.process.clone());
        let label = sub_name(world, t);
        let mut ops = stage_everything();
        ops.push(Op::Expect(verify(move |w| {
            let known = w.resource::<PlayerProgress>().discovered.contains(&t);
            let shelved = w.query_filtered::<&Ingredient, With<ShelfTile>>().iter(w).any(|i| i.id == t);
            match (known, shelved) {
                (true, false) => Ok(()),
                (false, _) => Err("not discovered".into()),
                (true, true) => Err("on the shelf".into()),
            }
        })));
        ops.push(Op::Click(sidebar_button(mp.clone())));
        ops.push(Op::Until(
            verify({
                let mp = mp.clone();
                move |w| card(w, mp.clone()).map(|_| ()).ok_or_else(|| "no vessel".to_string())
            }),
            30,
        ));
        ops.extend(load(world, maker, None));
        ops.push(Op::Click(card_part(mp.clone(), React)));
        ops.push(Op::Until(has_ids(mp.clone(), vec![t], label.clone()), WAIT));
        ops.push(Op::Until(
            verify({
                let mp = mp.clone();
                let label = label.clone();
                move |w| {
                    if chips(w, mp.clone()).contains(&label) {
                        Err(format!("{label} is still in the vessel"))
                    } else {
                        Ok(())
                    }
                }
            }),
            WAIT,
        ));
        ops.push(Op::Expect(status_says(mp, "doesn't keep")));
        out.push(check(
            "Transients",
            "A transient nothing takes breaks down where it was made, and is never on the shelf",
            ops,
        ));
    }
    out
}

// ---------------------------------------------------------------------------------------
// Teaching: discovery cards, lessons, why nothing happened
// ---------------------------------------------------------------------------------------
fn cards_showing(want_open: Option<bool>) -> Verify {
    verify(move |w| {
        let cards = w.resource::<crate::ui::discovery_card::DiscoveryCards>();
        let (n, open) = (cards.queue.len(), cards.open);
        let sealed = first::<crate::ui::discovery_card::DiscoveryCardSealed>(w, |_| true).is_some();
        let story = first::<crate::ui::discovery_card::DiscoveryCardStory>(w, |_| true)
            .and_then(|e| w.get::<Text>(e).map(|t| t.0.clone()))
            .unwrap_or_default();
        match want_open {
            None if n == 0 && !sealed && story.is_empty() => Ok(()),
            Some(false) if n > 0 && !open && sealed => Ok(()),
            Some(true) if open && !sealed && story.len() > 20 => Ok(()),
            _ => Err(format!("{n} card(s), open={open}, sealed card shown={sealed}, story={story:?}")),
        }
    })
}

fn discover_event(name: &'static str) -> Op {
    setup(move |w| {
        if let Some(id) = sub_id(w, name) {
            w.write_message(crate::systems::autoplay::GameEvent::Discovery { id });
        }
    })
}

pub(super) fn teaching_checks() -> Vec<Check> {
    use CardPart::*;
    let mut v = Vec::new();
    v.push(check(
        "Teaching",
        "A discovery comes as a sealed card that stays until it is opened; open, it tells its story, and Got it puts it away",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().discovery_cards = true),
            Op::Wait(3),
            discover_event("Quicklime"),
            Op::Until(cards_showing(Some(false)), 30),
            Op::Wait(30),
            Op::Expect(cards_showing(Some(false))),
            Op::Shot("a sealed discovery card"),
            Op::Click(marked::<crate::ui::discovery_card::DiscoveryCardSealed>("the sealed card")),
            Op::Until(cards_showing(Some(true)), 30),
            Op::Shot("an open discovery card"),
            Op::Click(marked::<crate::ui::discovery_card::DiscoveryCardGotIt>("Got it")),
            Op::Until(cards_showing(None), 30),
        ],
    ));
    v.push(check(
        "Teaching",
        "With cards set to close by themselves, an unread card goes after a while; with cards off, a discovery is a toast",
        vec![
            setup(new_game),
            setup(|w| {
                let mut s = w.resource_mut::<Settings>();
                s.discovery_cards = true;
                s.cards_close_themselves = true;
            }),
            Op::Wait(3),
            discover_event("Quicklime"),
            Op::Until(cards_showing(Some(false)), 30),
            Op::Until(cards_showing(None), 2400),
            setup(|w| w.resource_mut::<Settings>().discovery_cards = false),
            Op::Wait(2),
            discover_event("Slaked Lime"),
            Op::Wait(10),
            Op::Expect(cards_showing(None)),
        ],
    ));
    v.push(check(
        "Teaching",
        "From the first More hint on, the Hint card says what kind of change the step is",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().next_step = true),
            setup(chase_a_multi_step_target),
            Op::Wait(5),
            Op::Expect(verify(|w| match first::<crate::ui::hint::HintLesson>(w, |_| true) {
                None => Ok(()),
                Some(_) => Err("a lesson before any hint".into()),
            })),
            Op::Click(marked::<HintMore>("More hint")),
            Op::Until(
                verify(|w| {
                    let t = first::<crate::ui::hint::HintLesson>(w, |_| true)
                        .and_then(|e| w.get::<Text>(e).map(|t| t.0.clone()))
                        .unwrap_or_default();
                    if t.len() > 30 {
                        Ok(())
                    } else {
                        Err(format!("lesson: {t:?}"))
                    }
                }),
                30,
            ),
        ],
    ));
    // one ingredient short of a two-ingredient recipe in the Mortar
    v.push(check(
        "Teaching",
        "One ingredient short of a recipe, the vessel says it is close",
        vec![
            setup(new_game),
            setup(discover_everything),
            setup(|w| place(w, ProcessType::Mix, 0)),
            Op::Wait(5),
            setup(|w| {
                let first = w
                    .resource::<RecipeDatabase>()
                    .authored
                    .iter()
                    .find(|r| r.process == ProcessType::Mix && r.reactants.len() == 2)
                    .map(|r| r.reactants[0].substance_id);
                if let (Some(id), Some(c)) = (first, card(w, ProcessType::Mix)) {
                    put_in(w, c, id);
                }
            }),
            Op::Wait(3),
            Op::Click(card_part(ProcessType::Mix, React)),
            Op::Until(status_says(ProcessType::Mix, "Close: one more ingredient"), 60),
        ],
    ));
    v.push(check(
        "Teaching",
        "Two acids in the Mortar: the vessel says an acid wants a base",
        vec![
            setup(new_game),
            setup(discover_everything),
            setup(|w| place(w, ProcessType::Mix, 0)),
            Op::Wait(5),
            setup(|w| {
                // two acids in play that no Mortar recipe takes together
                let acids: Vec<u32> = {
                    let db = w.resource::<RecipeDatabase>();
                    let gd = w.resource::<GameData>();
                    let subs = w.resource::<Assets<Substances>>().get(&gd.substances);
                    let mut ids: Vec<u32> = db
                        .canon
                        .iter()
                        .copied()
                        .filter(|id| {
                            subs.and_then(|s| s.0.get(id))
                                .is_some_and(|s| s.properties.contains(&crate::data::common::Property::IsAcid))
                        })
                        .collect();
                    ids.sort_unstable();
                    let pair = ids.iter().enumerate().find_map(|(i, a)| {
                        ids[i + 1..]
                            .iter()
                            .find(|b| {
                                // nothing near a recipe: no Mix recipe of one of them alone, or of both and one more
                                !db.authored.iter().any(|r| {
                                    let has = |x: u32| r.reactants.iter().any(|s| s.substance_id == x);
                                    r.process.family() == "Mix"
                                        && ((r.reactants.len() == 3 && has(*a) && has(**b))
                                            || (r.reactants.len() == 1 && (has(*a) || has(**b))))
                                })
                            })
                            .map(|b| vec![*a, *b])
                    });
                    pair.unwrap_or_default()
                };
                if let Some(c) = card(w, ProcessType::Mix) {
                    for id in acids {
                        put_in(w, c, id);
                    }
                }
            }),
            Op::Wait(3),
            Op::Click(card_part(ProcessType::Mix, React)),
            Op::Until(status_says(ProcessType::Mix, "Two acids"), 60),
        ],
    ));
    v
}

/// Puts a substance straight into a vessel (as a drag would).
fn put_in(w: &mut World, card: Entity, id: u32) {
    put_in_n(w, card, id, 1);
}

/// Puts `amount` of a substance straight into a vessel, as one chip.
fn put_in_n(w: &mut World, card: Entity, id: u32, amount: u32) {
    let Some(ing) = ({
        let gd = w.resource::<GameData>();
        w.resource::<Assets<Substances>>().get(&gd.substances).and_then(|s| s.0.get(&id)).map(|s| Ingredient {
            id,
            name: s.name.clone(),
            formula: s.formula.clone(),
            state: s.state,
            properties: s.properties.clone(),
            amount,
        })
    }) else {
        return;
    };
    let zone = w.get::<Children>(card).and_then(|c| {
        let kids: Vec<Entity> = c.iter().collect();
        kids.into_iter().find(|k| w.get::<crate::components::VesselIngredientZone>(*k).is_some())
    });
    let Some(zone) = zone else { return };
    let fonts = w.resource::<UiFonts>().clone();
    let assets = w.resource::<AssetServer>().clone();
    let mut queue = CommandQueue::default();
    {
        let mut commands = Commands::new(&mut queue, w);
        commands.entity(zone).with_children(|z| {
            crate::ui::inventory::spawn_vessel_chip(
                z,
                &ing,
                crate::ui::inventory::ChipRole::Ingredient(card),
                &fonts,
                &assets,
            );
        });
    }
    queue.apply(w);
}

// ---------------------------------------------------------------------------------------
// Balanced amounts (off by default)
// ---------------------------------------------------------------------------------------
/// A Mortar recipe of two reactants, one taken twice: (2x reactant, 1x reactant).
fn two_to_one(w: &World) -> Option<(u32, u32)> {
    let db = w.resource::<RecipeDatabase>();
    db.authored
        .iter()
        .filter(|r| r.process == ProcessType::Mix && r.reactants.len() == 2 && r.required_catalyst().is_none())
        .filter(|r| r.products.iter().all(|p| !db.transient.contains(&p.substance_id)))
        .find_map(|r| {
            let (a, b) = (&r.reactants[0], &r.reactants[1]);
            match (a.moles, b.moles) {
                (2, 1) => Some((a.substance_id, b.substance_id)),
                (1, 2) => Some((b.substance_id, a.substance_id)),
                _ => None,
            }
        })
}

fn balanced_try(two: u32, one: u32) -> Vec<Op> {
    vec![
        setup(new_game),
        setup(discover_everything),
        setup(|w| w.resource_mut::<Settings>().balanced_amounts = true),
        setup(|w| place(w, ProcessType::Mix, 0)),
        Op::Wait(5),
        setup(move |w| {
            if let (Some((a, b)), Some(c)) = (two_to_one(w), card(w, ProcessType::Mix)) {
                put_in_n(w, c, a, two);
                put_in_n(w, c, b, one);
            }
        }),
        Op::Wait(3),
        Op::Click(card_part(ProcessType::Mix, CardPart::React)),
    ]
}

fn balanced_checks() -> Vec<Check> {
    let mut v = Vec::new();
    v.push(check(
        "Balanced amounts",
        "With balanced amounts on, a second drop of the same substance counts up its chip",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<Settings>().balanced_amounts = true),
            setup(|w| place(w, ProcessType::Mix, 0)),
            Op::Wait(5),
            Op::Drag(tile("Water"), card_part(ProcessType::Mix, CardPart::Art)),
            Op::Wait(5),
            Op::Drag(tile("Water"), card_part(ProcessType::Mix, CardPart::Art)),
            Op::Until(
                verify(|w| {
                    let c = card(w, ProcessType::Mix);
                    let water: Vec<u32> = w
                        .query::<(&Ingredient, &InVessel)>()
                        .iter(w)
                        .filter(|(i, v)| Some(v.0) == c && i.name == "Water")
                        .map(|(i, _)| i.amount)
                        .collect();
                    if water == [2] {
                        Ok(())
                    } else {
                        Err(format!("water chips: {water:?}"))
                    }
                }),
                40,
            ),
        ],
    ));
    let mut short = balanced_try(1, 1);
    short.push(Op::Until(status_says(ProcessType::Mix, "Not enough"), 60));
    v.push(check(
        "Balanced amounts",
        "Short of the equation's amounts, nothing reacts and the vessel says what's short",
        short,
    ));
    let mut exact = balanced_try(2, 1);
    exact.push(Op::Until(status_says(ProcessType::Mix, "Balanced"), 120));
    v.push(check("Balanced amounts", "The equation's amounts react in full", exact));
    let mut dud = balanced_try(3, 1);
    dud.push(Op::Until(status_says(ProcessType::Mix, "Unbalanced"), 120));
    dud.push(Op::Until(
        verify(|w| {
            let Some((a, _)) = two_to_one(w) else { return Err("no 2:1 recipe".into()) };
            let c = card(w, ProcessType::Mix);
            let back = w
                .query::<(&Ingredient, &InVessel)>()
                .iter(w)
                .any(|(i, v)| Some(v.0) == c && i.id == a && i.amount == 1);
            if back {
                Ok(())
            } else {
                Err("the extra wasn't handed back".into())
            }
        }),
        60,
    ));
    v.push(check("Balanced amounts", "A wrong ratio is a dud: half the yield, and the excess handed back", dud));
    v
}
