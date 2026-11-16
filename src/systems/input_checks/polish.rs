// src/systems/input_checks/polish.rs
//
// Interaction checks for sound, the keyboard and controllers, hover states, saves, the
// credits and achievements. A child of input_checks.rs, so it shares its check language
// (targets, ops, verifies) and helpers.
use bevy::input::gamepad::{GamepadConnection, GamepadConnectionEvent, RawGamepadButtonChangedEvent, RawGamepadEvent};

use super::*;
use crate::resources::player_progress::SaveClock;
use crate::systems::achievements::Achievements;
use crate::systems::sound::{Cue, SoundLog};
use crate::ui::codex::{CodexCloseButton, CodexTextCredit};
use crate::ui::credits::{CreditLink, CreditsButton, CreditsRoot, SECTIONS};
use crate::ui::focus::{FocusRing, NoFocus};
use crate::ui::onboarding::next_step_look;
use crate::ui::settings::SettingsRoot;
use crate::ui::theme::Skin;

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

pub(super) fn polish_checks() -> Vec<Check> {
    use CardPart::*;
    use ProcessType::{Heat, Mix};
    let mut v = Vec::new();

    // --- sound (the review run is silent; what would play is logged) ---
    v.push(check(
        "Sound",
        "Placing a vessel, lifting a substance and dropping it in each make a sound",
        vec![
            setup(new_game),
            Op::Wait(3),
            clear_log(),
            Op::Click(sidebar_button(Heat)),
            Op::Until(heard(&[Cue::Place]), 30),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(heard(&[Cue::Pickup, Cue::Drop]), 60),
        ],
    ));
    v.push(check(
        "Sound",
        "A reaction bubbles, then its discovery chimes",
        vec![
            setup(new_game),
            setup(|w| place(w, Heat, 0)),
            Op::Wait(5),
            Op::Drag(tile("Wood"), card_part(Heat, Art)),
            Op::Until(has_chip(Heat, "Wood"), 30),
            clear_log(),
            Op::Click(card_part(Heat, React)),
            Op::Until(heard(&[Cue::React]), 30),
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
                let e = focused(w).map(|e| e.index() as f32).unwrap_or(-1.0);
                w.resource_mut::<Scratch>().0.insert("first", e);
            }),
            Op::Key(KeyCode::Tab),
            Op::Until(
                verify(|w| {
                    let was = w.resource::<Scratch>().0.get("first").copied().unwrap_or(-1.0);
                    let now = focused(w).map(|e| e.index() as f32).unwrap_or(-2.0);
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
                        Has<NextStepCard>,
                        Has<NoFocus>,
                    ), With<Button>>()
                    .iter(w)
                    .filter(|(_, _, a, b, c, d, e, f)| !(*a || *b || *c || *d || *e || *f))
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
            Op::MoveTo(marked::<NextStepCard>("the next-step card")),
            Op::Until(
                verify(|w| {
                    let e = first::<NextStepCard>(w, |_| true).ok_or("no card")?;
                    if border_of(w, e) == Some(next_step_look(true).1) {
                        Ok(())
                    } else {
                        Err("the card didn't light up under the pointer".into())
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
        "Settings opens the credits; every source is listed with a link",
        vec![
            setup(|w| w.resource_mut::<SettingsUi>().open = true),
            Op::Wait(5),
            Op::Click(marked::<CreditsButton>("Credits and licences")),
            Op::Until(
                verify(|w| {
                    let shown = w
                        .query_filtered::<&Node, With<CreditsRoot>>()
                        .iter(w)
                        .next()
                        .is_some_and(|n| n.display != Display::None);
                    let links = w.query::<&CreditLink>().iter(w).count();
                    let want: usize = SECTIONS.iter().map(|(_, c)| c.len()).sum();
                    if shown && links == want {
                        Ok(())
                    } else {
                        Err(format!("shown={shown}, {links} of {want} sources listed"))
                    }
                }),
                30,
            ),
            Op::Wait(10),
            Op::Shot("the credits"),
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
    v
}
