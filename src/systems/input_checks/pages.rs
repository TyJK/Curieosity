// src/systems/input_checks/pages.rs
//
// Interaction checks for the one-pane views (the Substance and Reaction Libraries and
// Lessons: a list across the screen, a page in its place, Back to the list where it was),
// Lessons' search and the glossary, two-finger touch, and challenges. A child of
// input_checks.rs, so it shares its check language (targets, ops, verifies) and helpers.
use bevy::input::touch::{TouchInput, TouchPhase};

use super::*;
use crate::systems::autoplay::GameEvent;
use crate::ui::challenges::{ChallengeAsk, ChallengeCard, ChallengeMode, FinishButton, HudRoot, OpenBoard};
use crate::ui::curriculum::{
    CurriculumEntry, CurriculumScroll, CurriculumState, CurriculumWiki, LearnLink, LessonsSearchBox, TERM_PREFIX,
};
use crate::ui::glossary::{OpenTerm, TermCard, TermChip, WikiLink};
use crate::ui::hint::{HintButton, HintMore};
use crate::ui::shell::PaneBack;

/// Lessons shows a page, with its Wikipedia link laid out (and, given a key, that page).
fn lesson_shows(key: Option<&'static str>) -> Verify {
    verify(move |w| {
        let s = w.resource::<CurriculumState>();
        if !s.open || !s.page {
            return Err(format!("Lessons open: {}, on a page: {}", s.open, s.page));
        }
        if let Some(k) = key {
            if s.selected.as_deref() != Some(k) {
                return Err(format!("showing {:?}, not {k}", s.selected));
            }
        }
        let wiki = first::<CurriculumWiki>(w, |_| true)
            .or_else(|| first::<WikiLink>(w, |_| true))
            .ok_or("the page has no Wikipedia link")?;
        if w.get::<ComputedNode>(wiki).is_some_and(|n| n.size.x > 0.0) {
            Ok(())
        } else {
            Err("the Wikipedia link isn't laid out".into())
        }
    })
}

/// The entries of the Lessons list that are showing, by key.
fn lessons_shown(w: &mut World) -> Vec<String> {
    w.query::<(&CurriculumEntry, &Node, &ComputedNode)>()
        .iter(w)
        .filter(|(_, n, c)| n.display != Display::None && c.size.x > 0.0)
        .map(|(e, _, _)| e.0.clone())
        .collect()
}

/// How far the list of a one-pane view is scrolled.
fn list_scroll<M: Component>(w: &mut World, is_list: impl Fn(&M) -> bool) -> f32 {
    w.query::<(&M, &ScrollPosition)>().iter(w).find(|(m, _)| is_list(m)).map(|(_, s)| s.0.y).unwrap_or(-1.0)
}

/// A substance whose page lists the glossary term `key`.
fn substance_with_term(w: &World, key: &str) -> Option<u32> {
    let gd = w.resource::<GameData>().pages.clone();
    let pages = w.resource::<Assets<crate::data::pages::Pages>>().get(&gd)?;
    let mut ids: Vec<u32> =
        pages.substance_terms.iter().filter(|(_, ks)| ks.iter().any(|k| k == key)).map(|(id, _)| *id).collect();
    ids.sort_unstable();
    ids.first().copied()
}

/// The first `C` that is laid out (another view's may be there, hidden).
fn shown<C: Component>(name: &str) -> Target {
    target(name.to_string(), |w| {
        let mut q = w.query_filtered::<(Entity, &ComputedNode), With<C>>();
        let mut found: Vec<Entity> = q.iter(w).filter(|(_, c)| c.size.x > 0.0).map(|(e, _)| e).collect();
        found.sort();
        let e = *found.first()?;
        point_in(w, e, 0.5, 0.5)
    })
}

/// The checks' two fingers: (id, where) each, sent as a phone's window would.
fn fingers(w: &mut World, phase: TouchPhase, at: [Vec2; 2]) {
    let Some(window) = w.query_filtered::<Entity, With<PrimaryWindow>>().iter(w).next() else { return };
    for (i, p) in at.into_iter().enumerate() {
        let ev = TouchInput { phase, position: p, window, force: None, id: 20 + i as u64 };
        w.write_message(ev);
        w.write_message(bevy::window::WindowEvent::TouchInput(ev));
    }
}

/// Two fingers land on `a` and `b`, move together by `by` in six steps, and lift.
fn two_finger_swipe(a: Target, b: Target, by: Vec2) -> Vec<Op> {
    let mut ops = vec![Op::Until(
        verify(move |w| {
            let pa = (a.find)(w).ok_or_else(|| format!("could not find {} on screen", a.name))?;
            let pb = (b.find)(w).ok_or_else(|| format!("could not find {} on screen", b.name))?;
            w.insert_resource(TwoFingers([pa, pb]));
            fingers(w, TouchPhase::Started, [pa, pb]);
            Ok(())
        }),
        30,
    )];
    ops.push(Op::Wait(2));
    for i in 1..=6 {
        ops.push(setup(move |w| {
            let at = w.resource::<TwoFingers>().0;
            let d = by * i as f32 / 6.0;
            fingers(w, TouchPhase::Moved, [at[0] + d, at[1] + d]);
        }));
        ops.push(Op::Wait(1));
    }
    ops.push(setup(move |w| {
        let at = w.resource::<TwoFingers>().0;
        fingers(w, TouchPhase::Ended, [at[0] + by, at[1] + by]);
    }));
    ops.push(Op::Wait(4));
    ops
}

/// Another shelf tile in sight, beside Water (two fingers land on tiles side by side).
fn next_tile() -> Target {
    target("a second shelf tile in sight", |w| {
        let water = sub_id(w, "Water")?;
        let size = w
            .query_filtered::<&Window, With<PrimaryWindow>>()
            .iter(w)
            .next()
            .map(|w| Vec2::new(w.width(), w.height()))?;
        let sf =
            w.query_filtered::<&Window, With<PrimaryWindow>>().iter(w).next().map(|w| w.scale_factor()).unwrap_or(1.0);
        let mut q = w.query_filtered::<(&Ingredient, &ComputedNode, &UiGlobalTransform), With<ShelfTile>>();
        let mut seen: Vec<Vec2> = q
            .iter(w)
            .filter(|(i, c, _)| i.id != water && c.size.x > 0.0)
            .map(|(_, _, t)| t.translation / sf)
            .filter(|p| p.x > 20.0 && p.y > 20.0 && p.x < size.x - 20.0 && p.y < size.y - 20.0)
            .collect();
        seen.sort_by(|a, b| a.x.total_cmp(&b.x).then(a.y.total_cmp(&b.y)));
        seen.first().copied()
    })
}

/// Where the checks' two fingers came down.
#[derive(Resource, Clone, Copy)]
struct TwoFingers([Vec2; 2]);

pub fn pages_checks() -> Vec<Check> {
    let mut v = Vec::new();

    // --- Lessons ---
    v.push(check(
        "Lessons",
        "The Lessons tab shows the curriculum across the screen; a lesson opens in its place, Back returns to the list where it was, and Esc steps back then closes",
        vec![
            setup(new_game),
            Op::Wait(5),
            Op::Click(nav(View::Learn)),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<CurriculumState>();
                    let (open, page) = (s.open, s.page);
                    let n = lessons_shown(w).len();
                    if open && !page && n >= 400 {
                        Ok(())
                    } else {
                        Err(format!("open {open}, page {page}, {n} entries showing"))
                    }
                }),
                60,
            ),
            Op::Shot("Lessons, the list"),
            // a lesson well down the list: the list scrolls to it
            Op::Click(target("the 80th lesson", |w| {
                let mut entries: Vec<(Entity, f32)> = w
                    .query::<(Entity, &CurriculumEntry, &UiGlobalTransform)>()
                    .iter(w)
                    .filter(|(_, c, _)| !c.0.starts_with(TERM_PREFIX))
                    .map(|(e, _, t)| (e, t.translation.y))
                    .collect();
                entries.sort_by(|a, b| a.1.total_cmp(&b.1));
                let e = entries.get(80)?.0;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(lesson_shows(None), 60),
            setup(|w| {
                let y = list_scroll::<CurriculumScroll>(w, |m| m.is_left);
                w.insert_resource(Scratch([("list", y)].into_iter().collect()));
            }),
            Op::Shot("a lesson"),
            Op::Click(shown::<PaneBack>("the page's Back button")),
            Op::Until(
                verify(|w| {
                    let was = w.resource::<Scratch>().0.get("list").copied().unwrap_or(-1.0);
                    let now = list_scroll::<CurriculumScroll>(w, |m| m.is_left);
                    let page = w.resource::<CurriculumState>().page;
                    if page {
                        Err("still on the page".into())
                    } else if was <= 0.0 {
                        Err(format!("the list wasn't scrolled ({was})"))
                    } else if (now - was).abs() > 1.0 {
                        Err(format!("the list was at {was:.0} and came back at {now:.0}"))
                    } else {
                        Ok(())
                    }
                }),
                30,
            ),
            setup(|w| w.resource_mut::<CurriculumState>().show("Catalysis")),
            Op::Until(lesson_shows(Some("Catalysis")), 60),
            Op::Key(KeyCode::Escape),
            Op::Until(
                state("Esc went back to the list", |w| {
                    let s = w.resource::<CurriculumState>();
                    s.open && !s.page
                }),
                30,
            ),
            Op::Key(KeyCode::Escape),
            Op::Until(state("Lessons closed", |w| !w.resource::<CurriculumState>().open), 30),
        ],
    ));
    v.push(check(
        "Lessons",
        "Typing searches the lessons and the glossary's words (by what they mean too); Backspace brings them all back",
        vec![
            setup(|w| w.resource_mut::<CurriculumState>().open = true),
            Op::Wait(10),
            Op::Click(marked::<LessonsSearchBox>("the search box")),
            Op::Key(KeyCode::KeyN),
            Op::Key(KeyCode::KeyI),
            Op::Key(KeyCode::KeyT),
            Op::Key(KeyCode::KeyR),
            Op::Until(
                verify(|w| {
                    let s = w.resource::<CurriculumState>().search.clone();
                    let shown = lessons_shown(w);
                    let has = |k: &str| shown.iter().any(|x| x == k);
                    if s != "nitr" {
                        Err(format!("search reads {s:?}"))
                    } else if !has("term:Nitrite") || !has("term:Nitrate") {
                        Err(format!("showing {shown:?}"))
                    } else if shown.len() > 40 {
                        Err(format!("{} still showing", shown.len()))
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            Op::Shot("Lessons, searched"),
            Op::Key(KeyCode::Backspace),
            Op::Key(KeyCode::Backspace),
            Op::Key(KeyCode::Backspace),
            Op::Key(KeyCode::Backspace),
            Op::Until(
                verify(|w| {
                    let n = lessons_shown(w).len();
                    if n >= 600 {
                        Ok(())
                    } else {
                        Err(format!("{n} showing after clearing the search"))
                    }
                }),
                60,
            ),
        ],
    ));
    v.push(check(
        "Lessons",
        "A glossary word's page defines it and links its Wikipedia article",
        vec![
            setup(|w| w.resource_mut::<CurriculumState>().show("term:Nitrite")),
            Op::Until(lesson_shows(Some("term:Nitrite")), 60),
            Op::Shot("a glossary word"),
            Op::Click(marked::<WikiLink>("the word's Wikipedia button")),
            Op::Until(
                verify(|_| {
                    let last = URL_SINK.lock().ok().and_then(|s| s.as_ref().and_then(|v| v.last().cloned()));
                    match last {
                        Some(u) if u.contains("wikipedia.org") && u.contains("Nitrite") => Ok(()),
                        other => Err(format!("opened {other:?}")),
                    }
                }),
                30,
            ),
        ],
    ));
    v.push(check(
        "Lessons",
        "A reaction's page links the ideas behind it; one opens in Lessons and the Reaction Library steps aside",
        vec![
            setup(new_game),
            setup(|w| w.resource_mut::<ReactionLibState>().show(1_000_000)),
            Op::Wait(5),
            Op::Until(
                verify(|w| {
                    let detail =
                        first::<crate::ui::reaction_library::ReactionLibDetail>(w, |_| true).ok_or("no page")?;
                    if descendant::<LearnLink>(w, detail).is_some() {
                        Ok(())
                    } else {
                        Err("the reaction's page links no ideas".into())
                    }
                }),
                60,
            ),
            Op::Click(target("the page's first lesson link", |w| {
                let detail = first::<crate::ui::reaction_library::ReactionLibDetail>(w, |_| true)?;
                let e = descendant::<LearnLink>(w, detail)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    let open = w.resource::<CurriculumState>().open;
                    let rlib = w.resource::<ReactionLibState>().open;
                    if open && !rlib {
                        Ok(())
                    } else {
                        Err(format!("Lessons open: {open}, Reaction Library open: {rlib}"))
                    }
                }),
                30,
            ),
            Op::Until(lesson_shows(None), 60),
        ],
    ));

    // --- the glossary on a substance's page ---
    v.push(check(
        "Glossary",
        "A substance's page marks the chemistry words it uses and lists them; a tap defines one, a second tap closes it",
        vec![
            setup(|w| {
                if let Some(id) = substance_with_term(w, "Nitrite") {
                    w.resource_mut::<CodexState>().show(id);
                }
            }),
            Op::Until(
                verify(|w| {
                    let chip = first::<TermChip>(w, |c| c.0 == "Nitrite").ok_or("no Nitrite in the page's words")?;
                    let laid = w.get::<ComputedNode>(chip).is_some_and(|n| n.size.x > 0.0);
                    let marked = w.query::<&bevy::text::Underline>().iter(w).count();
                    if !laid {
                        Err("the word isn't laid out".into())
                    } else if marked == 0 {
                        Err("no word is marked in the text".into())
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            Op::Click(target("the Nitrite word", |w| {
                let e = first::<TermChip>(w, |c| c.0 == "Nitrite")?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    let open = w.resource::<OpenTerm>().0.as_ref().map(|(_, k)| k.clone());
                    let card = w
                        .query::<(&TermCard, &Node, Option<&Children>)>()
                        .iter(w)
                        .find(|(_, n, _)| n.display != Display::None)
                        .map(|(_, _, c)| c.map_or(0, |c| c.len()));
                    match (open.as_deref(), card) {
                        (Some("Nitrite"), Some(n)) if n > 0 => Ok(()),
                        _ => Err(format!("open {open:?}, card {card:?}")),
                    }
                }),
                30,
            ),
            Op::Shot("a word defined on a substance's page"),
            Op::Click(target("the Nitrite word again", |w| {
                let e = first::<TermChip>(w, |c| c.0 == "Nitrite")?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    let shown = w.query::<(&TermCard, &Node)>().iter(w).any(|(_, n)| n.display != Display::None);
                    if shown {
                        Err("the definition is still open".into())
                    } else {
                        Ok(())
                    }
                }),
                30,
            ),
        ],
    ));

    // --- the libraries: one pane at a time ---
    v.push(check(
        "Substance Library",
        "A row opens its page in the list's place; Back returns to the list where it was",
        vec![
            setup(discover_everything),
            setup(|w| w.resource_mut::<CodexState>().open = true),
            Op::Wait(20),
            Op::Click(target("a row well down the list", |w| {
                let (want, at) = {
                    let mut q = w.query_filtered::<(&VirtualList, &ComputedNode), With<CodexListContent>>();
                    let (list, cn) = q.iter(w).next()?;
                    let want = *list.ids().get(60)?;
                    (want, list.offset_of(want, cn.size.x * cn.inverse_scale_factor()))
                };
                match first::<CodexEntry>(w, |c| c.0 == want) {
                    Some(e) => point_in(w, e, 0.5, 0.5),
                    // the list builds only the rows near the view: scroll there and look again
                    None => {
                        let mut q = w.query::<(&CodexScrollable, &mut ScrollPosition)>();
                        if let (Some(y), Some((_, mut sp))) = (at, q.iter_mut(w).find(|(m, _)| m.is_left)) {
                            sp.0.y = (y - 40.0).max(0.0);
                        }
                        None
                    }
                }
            })),
            Op::Until(
                verify(|w| {
                    let c = w.resource::<CodexState>();
                    let (page, sel) = (c.page, c.selected);
                    let parts =
                        w.query_filtered::<&Children, With<CodexDetail>>().iter(w).next().map(|c| c.len()).unwrap_or(0);
                    if page && sel.is_some() && parts > 0 {
                        Ok(())
                    } else {
                        Err(format!("page {page}, selected {sel:?}, {parts} parts"))
                    }
                }),
                30,
            ),
            setup(|w| {
                let y = list_scroll::<CodexScrollable>(w, |m| m.is_left);
                w.insert_resource(Scratch([("list", y)].into_iter().collect()));
            }),
            Op::Click(shown::<PaneBack>("the page's Back button")),
            Op::Until(
                verify(|w| {
                    let was = w.resource::<Scratch>().0.get("list").copied().unwrap_or(-1.0);
                    let now = list_scroll::<CodexScrollable>(w, |m| m.is_left);
                    let rows = w.query::<&CodexEntry>().iter(w).count();
                    if w.resource::<CodexState>().page {
                        Err("still on the page".into())
                    } else if was <= 0.0 {
                        Err(format!("the list wasn't scrolled ({was})"))
                    } else if (now - was).abs() > 1.0 || rows == 0 {
                        Err(format!("the list was at {was:.0} and came back at {now:.0} with {rows} rows"))
                    } else {
                        Ok(())
                    }
                }),
                30,
            ),
            Op::Shot("the Substance Library, back on its list"),
            setup(new_game),
            Op::Wait(10),
        ],
    ));

    // --- two fingers only scroll ---
    v.push(check(
        "Touch",
        "Two fingers on the bench pan it: the vessel under one doesn't move, lift or get selected",
        vec![
            setup(|w| place(w, ProcessType::Mix, 0)),
            Op::Wait(5),
            setup(|w| {
                let c = card(w, ProcessType::Mix);
                let at = c.and_then(|c| left_top(w, c)).unwrap_or(Vec2::NAN);
                let pane = w
                    .query_filtered::<&Node, With<crate::components::ui_markers::CanvasScrollingPane>>()
                    .iter(w)
                    .next()
                    .map(crate::systems::drag_drop::pane_offset)
                    .unwrap_or(Vec2::NAN);
                w.insert_resource(Scratch(
                    [("cx", at.x), ("cy", at.y), ("px", pane.x), ("py", pane.y)].into_iter().collect(),
                ));
            }),
        ]
        .into_iter()
        .chain(two_finger_swipe(card_part(ProcessType::Mix, CardPart::Title), bench_spot(), Vec2::new(-90.0, -50.0)))
        .chain([Op::Expect(verify(|w| {
            let s = w.resource::<Scratch>().0.clone();
            let c = card(w, ProcessType::Mix).ok_or("no Mortar")?;
            let at = left_top(w, c).ok_or("no Mortar position")?;
            let pane = w
                .query_filtered::<&Node, With<crate::components::ui_markers::CanvasScrollingPane>>()
                .iter(w)
                .next()
                .map(crate::systems::drag_drop::pane_offset)
                .ok_or("no bench")?;
            let was_card = Vec2::new(s["cx"], s["cy"]);
            let was_pane = Vec2::new(s["px"], s["py"]);
            let active = w.resource::<crate::systems::drag_drop::ActiveVessel>().0;
            if at.distance(was_card) > 0.5 {
                Err(format!("the Mortar moved from {was_card:.0} to {at:.0}"))
            } else if active.is_some() {
                Err("the Mortar was selected".into())
            } else if pane.distance(was_pane) < 1.0 {
                Err(format!("the bench stayed at {pane:.0}"))
            } else {
                Ok(())
            }
        }))])
        .collect(),
    ));
    v.push(check(
        "Touch",
        "Two fingers lifting off shelf tiles select nothing",
        vec![setup(|w| w.resource_mut::<SelectedSubstance>().0 = None)]
            .into_iter()
            .chain(two_finger_swipe(tile("Water"), next_tile(), Vec2::ZERO))
            .chain([Op::Expect(selected_is(None))])
            .collect(),
    ));

    // --- challenges ---
    v.push(check(
        "Challenges",
        "The board lists the challenges; starting one sets the lab aside: its kit on the shelf, its vessels, and a bar with its route",
        vec![
            setup(new_game),
            setup(|w| place(w, ProcessType::Mix, 0)),
            Op::Wait(5),
            Op::Click(marked::<OpenBoard>("the header's Challenges button")),
            Op::Until(
                verify(|w| {
                    let n = w.query::<&ChallengeCard>().iter(w).count();
                    if w.resource::<ChallengeMode>().board_open && n >= 6 {
                        Ok(())
                    } else {
                        Err(format!("{n} challenges on the board"))
                    }
                }),
                60,
            ),
            Op::Shot("the challenges"),
            Op::Click(target("the first challenge", |w| {
                let id = w.resource::<ChallengeMode>().challenges.first()?.id;
                let e = first::<ChallengeCard>(w, |c| c.id == id && !c.daily)?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(challenge_set_up(), 60),
            Op::Shot("a challenge"),
        ],
    ));
    v.push(check(
        "Challenges",
        "A challenge scores: a reaction that doesn't go costs the step in hand 10, More hint 20; made steps keep their points; the finish gives stars and keeps the best; the lab comes back as it was",
        vec![
            setup(new_game),
            setup(|w| place(w, ProcessType::Mix, 0)),
            setup(|w| {
                let mut s = w.resource_mut::<Settings>();
                s.hints = true;
                s.next_step = true;
            }),
            Op::Wait(5),
            setup(|w| {
                let lab: Vec<u32> = w.resource::<PlayerProgress>().discovered.iter().copied().collect();
                w.insert_resource(LabBefore(lab));
                let id = w.resource::<ChallengeMode>().challenges.first().map(|c| c.id).unwrap_or(0);
                w.write_message(ChallengeAsk::Start { id, daily: false });
            }),
            Op::Until(challenge_set_up(), 60),
            setup(|w| {
                w.write_message(GameEvent::Fizzle {
                    process: ProcessType::Mix,
                    reactants: Vec::new(),
                    reason: String::new(),
                });
            }),
            Op::Until(points_are(|p| p.first() == Some(&90)), 30),
            Op::Click(marked::<HintButton>("the Hint button")),
            Op::Until(super::polish::more_hint_costs(20), 30),
            Op::Click(marked::<HintMore>("More hint")),
            Op::Until(points_are(|p| p.first() == Some(&70)), 30),
            Op::Shot("a challenge's bar, a step cheaper"),
            // the route's products, one by one
            setup(|w| {
                let products = w.resource::<ChallengeMode>().run().map(|r| r.challenge.step_products.clone()).unwrap_or_default();
                for id in products {
                    w.resource_mut::<PlayerProgress>().discover(id);
                    w.write_message(GameEvent::Discovery { id });
                }
            }),
            Op::Until(
                verify(|w| {
                    let shown = w
                        .query_filtered::<&Node, With<crate::ui::challenges::FinishRoot>>()
                        .iter(w)
                        .any(|n| n.display != Display::None);
                    let m = w.resource::<ChallengeMode>();
                    let run = m.run().ok_or("not playing")?;
                    let rec = m.records.records.get(&run.challenge.id).copied().unwrap_or_default();
                    if !run.finished || !m.card || !shown {
                        Err(format!("finished {}, card {} (shown {shown})", run.finished, m.card))
                    } else if rec.best != run.score() || rec.stars == 0 {
                        Err(format!("kept best {} and {} stars, scored {}", rec.best, rec.stars, run.score()))
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
            Op::Shot("a challenge finished"),
            Op::Click(target("Back to the lab", |w| {
                let e = first::<FinishButton>(w, |b| matches!(b, FinishButton::Lab))?;
                point_in(w, e, 0.5, 0.5)
            })),
            Op::Until(
                verify(|w| {
                    let want = w.resource::<LabBefore>().0.clone();
                    let now: std::collections::BTreeSet<u32> =
                        w.resource::<PlayerProgress>().discovered.iter().copied().collect();
                    let want: std::collections::BTreeSet<u32> = want.into_iter().collect();
                    let playing = w.resource::<ChallengeMode>().playing();
                    let mortar = card(w, ProcessType::Mix).ok_or("the lab's Mortar is gone")?;
                    let shows = w.get::<Node>(mortar).is_some_and(|n| n.display != Display::None);
                    let cards = w.query_filtered::<(), With<VesselCard>>().iter(w).count();
                    if playing {
                        Err("still playing".into())
                    } else if now != want {
                        Err(format!("the lab has {} discoveries, had {}", now.len(), want.len()))
                    } else if !shows || cards != 1 {
                        Err(format!("the lab's Mortar shows: {shows}; {cards} vessels on the bench"))
                    } else {
                        Ok(())
                    }
                }),
                60,
            ),
        ],
    ));
    v
}

/// The lab's discoveries before a challenge.
#[derive(Resource)]
struct LabBefore(Vec<u32>);

/// A challenge is being played: the shelf holds exactly its kit, the vessels are its own,
/// the lab's are hidden, and its bar is up.
fn challenge_set_up() -> Verify {
    verify(|w| {
        let m = w.resource::<ChallengeMode>();
        let run = m.run().ok_or("no challenge is being played")?;
        let kit: std::collections::BTreeSet<u32> =
            run.challenge.kit.iter().chain(run.challenge.decoys.iter()).copied().collect();
        let vessels = run.challenge.vessels.clone();
        let have: std::collections::BTreeSet<u32> = w.resource::<PlayerProgress>().discovered.iter().copied().collect();
        let open = w.resource::<ProcessUnlocks>().0.clone();
        let hidden = w
            .query_filtered::<&Node, With<crate::components::ui_markers::Stashed>>()
            .iter(w)
            .all(|n| n.display == Display::None);
        let bar = w.query_filtered::<&Node, With<HudRoot>>().iter(w).any(|n| n.display != Display::None);
        if have != kit {
            Err(format!("the shelf holds {} things, the kit {}", have.len(), kit.len()))
        } else if vessels.iter().any(|v| !open.contains(v)) {
            Err("a vessel the route needs is locked".into())
        } else if !hidden {
            Err("the lab's vessels still show".into())
        } else if !bar {
            Err("no challenge bar".into())
        } else {
            Ok(())
        }
    })
}

/// The run's step points satisfy `f`.
fn points_are(f: impl Fn(&[u32]) -> bool + Send + Sync + 'static) -> Verify {
    verify(move |w| {
        let m = w.resource::<ChallengeMode>();
        let p = m.run().map(|r| r.points.clone()).ok_or("not playing")?;
        if f(&p) {
            Ok(())
        } else {
            Err(format!("step points are {p:?}"))
        }
    })
}

/// Numbers a check keeps between its steps.
#[derive(Resource, Default, Clone)]
struct Scratch(std::collections::HashMap<&'static str, f32>);
