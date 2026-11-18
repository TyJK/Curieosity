// src/ui/virtual_list.rs
//
// Long lists that build only what is in sight. The content node keeps the full height of
// every entry, so the scrollbar, the wheel and a finger scroll it exactly as before; each
// entry sits in a fixed cell, placed absolutely, and is built while it is within a screen of
// the view and dropped (letting go of its picture) once it is more than two screens away.
// The gap between the two margins keeps a list from building and dropping the same row as
// it is scrolled back and forth. The shelf and the Substance Library list use it: with every
// substance found they would otherwise hold two thousand entries, each with its own picture.
use bevy::prelude::*;
use std::collections::{HashMap, HashSet};

/// A windowed list or grid, on its content node. The owning view keeps `ids` in order and
/// builds the entries a pass asks for.
#[derive(Component)]
pub struct VirtualList {
    /// an entry's size in interface pixels; a width of 0 stretches one column across the list
    pub cell: Vec2,
    /// between columns (x) and rows (y)
    pub gap: Vec2,
    ids: Vec<u32>,
    index: HashMap<u32, usize>,
    /// the built entries: id -> (entity, the cell it sits in)
    built: HashMap<u32, (Entity, Vec2)>,
    /// entries that just arrived: built with a flourish if they are in sight
    fresh: HashSet<u32>,
    /// bumped whenever `ids` changes, so the next pass re-plans
    version: u64,
    /// (columns, build range, version) the last pass planned for
    last: Option<(usize, usize, usize, u64)>,
}

/// What one pass asks the view to do.
#[derive(Default, Debug)]
pub struct Pass {
    /// entries to build: (id, the cell's top-left, just arrived)
    pub build: Vec<(u32, Vec2, bool)>,
    /// entries to drop
    pub drop: Vec<Entity>,
    /// built entries whose cell changed (a new entry ahead of them, or a new column count)
    pub moves: Vec<(Entity, Vec2)>,
    /// the content node's full height
    pub height: f32,
}

impl VirtualList {
    pub fn new(cell: Vec2, gap: Vec2) -> Self {
        Self {
            cell,
            gap,
            ids: Vec::new(),
            index: HashMap::new(),
            built: HashMap::new(),
            fresh: HashSet::new(),
            version: 0,
            last: None,
        }
    }

    /// Every entry, in order.
    pub fn ids(&self) -> &[u32] {
        &self.ids
    }

    /// Replace the entries. `fresh` are the ones that just arrived (a discovery): built with
    /// a flourish if they come into sight on the next pass.
    pub fn set(&mut self, ids: Vec<u32>, fresh: impl IntoIterator<Item = u32>) {
        if ids == self.ids {
            return;
        }
        self.index = ids.iter().enumerate().map(|(i, id)| (*id, i)).collect();
        self.ids = ids;
        self.fresh.extend(fresh);
        self.version += 1;
    }

    /// Forget every built entry (the view is rebuilding); returns them for despawning.
    pub fn clear(&mut self) -> Vec<Entity> {
        self.version += 1;
        self.last = None;
        self.built.drain().map(|(_, (e, _))| e).collect()
    }

    /// Record an entry the view built for this pass.
    pub fn record(&mut self, id: u32, entity: Entity, at: Vec2) {
        self.built.insert(id, (entity, at));
    }

    /// The built entries in list order: the content node's children.
    pub fn order(&self) -> Vec<Entity> {
        let mut v: Vec<(usize, Entity)> =
            self.built.iter().filter_map(|(id, (e, _))| self.index.get(id).map(|i| (*i, *e))).collect();
        v.sort_unstable_by_key(|(i, _)| *i);
        v.into_iter().map(|(_, e)| e).collect()
    }

    /// Where an entry's cell starts, in interface pixels from the top, in a list `width` wide.
    pub fn offset_of(&self, id: u32, width: f32) -> Option<f32> {
        let i = *self.index.get(&id)?;
        Some((i / self.columns(width)) as f32 * (self.cell.y + self.gap.y))
    }

    /// How many entries are built (for tests and the log).
    pub fn built_len(&self) -> usize {
        self.built.len()
    }

    fn columns(&self, width: f32) -> usize {
        if self.cell.x <= 0.0 {
            return 1;
        }
        (((width + self.gap.x) / (self.cell.x + self.gap.x)).floor() as usize).max(1)
    }

    /// Plan a pass for a list `width` wide in a view `view_h` tall, scrolled to `scroll_y`
    /// (interface pixels). `keep` says whether an entry out of range must stay built anyway
    /// (it is being dragged, pressed or has the keyboard focus). None when nothing changed.
    pub fn plan(&mut self, width: f32, view_h: f32, scroll_y: f32, keep: impl Fn(Entity) -> bool) -> Option<Pass> {
        if width <= 0.0 || view_h <= 0.0 {
            // not laid out, or hidden: let go of everything, pictures included
            if self.built.is_empty() {
                return None;
            }
            self.last = None;
            return Some(Pass { drop: self.built.drain().map(|(_, (e, _))| e).collect(), ..default() });
        }
        let cols = self.columns(width);
        let n = self.ids.len();
        let pitch = self.cell + self.gap;
        let rows = n.div_ceil(cols);
        let height = if rows == 0 { 0.0 } else { rows as f32 * pitch.y - self.gap.y };
        let in_view = (view_h / pitch.y).ceil() as usize + 1;
        let first = (scroll_y.max(0.0) / pitch.y).floor() as usize;
        // build within one screen of the view, drop beyond two
        let lo = first.saturating_sub(in_view) * cols;
        let hi = ((first + 2 * in_view) * cols).min(n);
        let keep_lo = first.saturating_sub(2 * in_view) * cols;
        let keep_hi = ((first + 3 * in_view) * cols).min(n);
        let key = (cols, lo, hi, self.version);
        if self.last == Some(key) {
            return None;
        }
        self.last = Some(key);

        let cell_at = |i: usize| {
            let x = if self.cell.x <= 0.0 { 0.0 } else { (i % cols) as f32 * pitch.x };
            Vec2::new(x, (i / cols) as f32 * pitch.y)
        };
        let mut pass = Pass { height, ..default() };
        let mut keep_built = HashMap::new();
        for (id, (e, at)) in self.built.drain() {
            match self.index.get(&id) {
                Some(&i) if (keep_lo..keep_hi).contains(&i) || keep(e) => {
                    let want = cell_at(i);
                    if at != want {
                        pass.moves.push((e, want));
                    }
                    keep_built.insert(id, (e, want));
                }
                _ => pass.drop.push(e),
            }
        }
        self.built = keep_built;
        for i in lo..hi {
            let id = self.ids[i];
            if !self.built.contains_key(&id) {
                pass.build.push((id, cell_at(i), self.fresh.contains(&id)));
            }
        }
        self.fresh.clear();
        Some(pass)
    }
}

/// A windowed canvas: items placed anywhere on a big content node (a map you pan both ways),
/// each built while its rect is within a screen of the view and dropped once it is more than
/// two screens away. The owning view keeps the items' rects, by index, and builds the ones a
/// pass asks for. The Tech Tree's graph uses it: thousands of steps and their lines.
#[derive(Component, Default)]
pub struct VirtualCanvas {
    rects: Vec<Rect>,
    /// the built items: index -> entity
    built: HashMap<usize, Entity>,
    /// bumped whenever the items change, so the next pass re-plans
    version: u64,
    /// (the view, rounded, and the version) the last pass planned for
    last: Option<(IVec4, u64)>,
}

/// What one canvas pass asks the view to do.
#[derive(Default, Debug)]
pub struct CanvasPass {
    /// items to build, by index
    pub build: Vec<usize>,
    /// entities to drop
    pub drop: Vec<Entity>,
}

impl VirtualCanvas {
    /// Replace every item (the view is rebuilding); returns the built entities for
    /// despawning. The next pass builds what is in sight.
    pub fn set(&mut self, rects: Vec<Rect>) -> Vec<Entity> {
        self.rects = rects;
        self.version += 1;
        self.last = None;
        self.built.drain().map(|(_, e)| e).collect()
    }

    /// Record an entity the view built for an item.
    pub fn record(&mut self, item: usize, entity: Entity) {
        self.built.insert(item, entity);
    }

    /// How many items are built (for tests and the checks).
    pub fn built_len(&self) -> usize {
        self.built.len()
    }

    /// How many items there are in all.
    pub fn len(&self) -> usize {
        self.rects.len()
    }

    /// True when it holds no items.
    pub fn is_empty(&self) -> bool {
        self.rects.is_empty()
    }

    /// Plan a pass for a view `view` (content pixels: the scroll position and the view's
    /// size). An empty view (hidden, not laid out) lets go of everything. `keep` says whether
    /// a built item out of range must stay anyway (pressed, focused). None when nothing changed.
    pub fn plan(&mut self, view: Rect, keep: impl Fn(Entity) -> bool) -> Option<CanvasPass> {
        if view.width() <= 0.0 || view.height() <= 0.0 {
            if self.built.is_empty() {
                return None;
            }
            self.last = None;
            return Some(CanvasPass { drop: self.built.drain().map(|(_, e)| e).collect(), ..default() });
        }
        // re-plan once the view has moved a little (16 px), not every pixel of a pan
        let key = (
            IVec4::new(
                (view.min.x / 16.0).floor() as i32,
                (view.min.y / 16.0).floor() as i32,
                (view.width() / 16.0).ceil() as i32,
                (view.height() / 16.0).ceil() as i32,
            ),
            self.version,
        );
        if self.last == Some(key) {
            return None;
        }
        self.last = Some(key);
        let size = view.size();
        // build within one screen of the view, drop beyond two
        let near = Rect::from_corners(view.min - size, view.max + size);
        let far = Rect::from_corners(view.min - size * 2.0, view.max + size * 2.0);
        let touches =
            |a: &Rect, b: &Rect| a.min.x < b.max.x && b.min.x < a.max.x && a.min.y < b.max.y && b.min.y < a.max.y;
        let mut pass = CanvasPass::default();
        self.built.retain(|&i, e| {
            let stay = self.rects.get(i).is_some_and(|r| touches(r, &far)) || keep(*e);
            if !stay {
                pass.drop.push(*e);
            }
            stay
        });
        for (i, r) in self.rects.iter().enumerate() {
            if !self.built.contains_key(&i) && touches(r, &near) {
                pass.build.push(i);
            }
        }
        Some(pass)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// A 100 x 100 grid of 50 px items, 100 px apart (10,000 px square).
    fn canvas() -> VirtualCanvas {
        let mut c = VirtualCanvas::default();
        let rects = (0..10_000)
            .map(|i| {
                let at = Vec2::new((i % 100) as f32 * 100.0, (i / 100) as f32 * 100.0);
                Rect::from_corners(at, at + Vec2::splat(50.0))
            })
            .collect();
        c.set(rects);
        c
    }

    fn apply_canvas(c: &mut VirtualCanvas, p: &CanvasPass, next: &mut u32) {
        for &i in &p.build {
            *next += 1;
            c.record(i, Entity::from_raw_u32(*next).unwrap());
        }
    }

    #[test]
    fn a_canvas_builds_only_what_is_near_the_view() {
        let mut c = canvas();
        // a 400 x 300 view at the top left: built out to 800 x 600 (a screen right and down)
        let p = c.plan(Rect::new(0.0, 0.0, 400.0, 300.0), |_| false).unwrap();
        assert_eq!(p.build.len(), 8 * 6, "8 columns by 6 rows of items");
        let mut n = 0;
        apply_canvas(&mut c, &p, &mut n);
        assert!(c.plan(Rect::new(0.0, 0.0, 400.0, 300.0), |_| false).is_none(), "nothing moved");
        assert!(c.plan(Rect::new(5.0, 5.0, 405.0, 305.0), |_| false).is_none(), "a few pixels is not a move");
    }

    #[test]
    fn panning_a_canvas_builds_ahead_and_drops_far_behind() {
        let mut c = canvas();
        let mut n = 0;
        let p = c.plan(Rect::new(0.0, 0.0, 400.0, 300.0), |_| false).unwrap();
        apply_canvas(&mut c, &p, &mut n);
        // across the map: everything from the corner goes, the new neighbourhood is built
        let at = Vec2::new(5000.0, 5000.0);
        let p = c.plan(Rect::from_corners(at, at + Vec2::new(400.0, 300.0)), |_| false).unwrap();
        assert_eq!(p.drop.len(), 48);
        assert_eq!(p.build.len(), 12 * 9, "a screen each side: 1200 x 900 of items");
        apply_canvas(&mut c, &p, &mut n);
        assert_eq!(c.built_len(), 108);
    }

    #[test]
    fn a_hidden_canvas_lets_go_and_a_new_set_starts_over() {
        let mut c = canvas();
        let mut n = 0;
        let p = c.plan(Rect::new(0.0, 0.0, 400.0, 300.0), |_| false).unwrap();
        apply_canvas(&mut c, &p, &mut n);
        let p = c.plan(Rect::default(), |_| false).unwrap();
        assert_eq!(p.drop.len(), 48);
        assert_eq!(c.built_len(), 0);
        let p = c.plan(Rect::new(0.0, 0.0, 400.0, 300.0), |_| false).unwrap();
        apply_canvas(&mut c, &p, &mut n);
        let old = c.set(vec![Rect::new(0.0, 0.0, 10.0, 10.0)]);
        assert_eq!(old.len(), 48, "the old items are handed back for despawning");
        let p = c.plan(Rect::new(0.0, 0.0, 400.0, 300.0), |_| false).unwrap();
        assert_eq!(p.build, vec![0]);
    }

    #[test]
    fn a_long_item_is_built_wherever_it_passes() {
        let mut c = VirtualCanvas::default();
        // a line from x 0 to x 9000 (a link across eras)
        c.set(vec![Rect::new(0.0, 100.0, 9000.0, 102.0)]);
        let p = c.plan(Rect::new(4000.0, 0.0, 4400.0, 300.0), |_| false).unwrap();
        assert_eq!(p.build, vec![0]);
    }

    fn grid(n: u32) -> VirtualList {
        let mut v = VirtualList::new(Vec2::new(84.0, 104.0), Vec2::splat(8.0));
        v.set((0..n).collect(), []);
        v
    }

    /// Builds the pass's entries with made-up entities, as a view would.
    fn apply(v: &mut VirtualList, p: &Pass, next: &mut u32) {
        for (id, at, _) in &p.build {
            *next += 1;
            v.record(*id, Entity::from_raw_u32(*next).unwrap(), *at);
        }
    }

    #[test]
    fn builds_only_the_rows_near_the_view() {
        let mut v = grid(2000);
        // 1000 wide: 10 columns of 84 + 8; a 230-tall view touches 4 rows (ceil(230/112) + 1)
        let p = v.plan(1000.0, 230.0, 0.0, |_| false).unwrap();
        assert_eq!(p.build.len(), 80, "this screen and the next: 8 rows of 10");
        assert_eq!(p.height, 200.0 * 112.0 - 8.0);
        assert_eq!(p.build[11].1, Vec2::new(92.0, 112.0));
        let mut n = 0;
        apply(&mut v, &p, &mut n);
        assert!(v.plan(1000.0, 230.0, 0.0, |_| false).is_none(), "nothing changed, nothing to do");
    }

    #[test]
    fn scrolling_builds_ahead_and_drops_far_behind() {
        let mut v = grid(2000);
        let mut n = 0;
        let p = v.plan(1000.0, 230.0, 0.0, |_| false).unwrap();
        apply(&mut v, &p, &mut n);
        // one row down: a row more ahead, nothing dropped yet (within two screens)
        let p = v.plan(1000.0, 230.0, 112.0, |_| false).unwrap();
        assert_eq!(p.build.len(), 10);
        assert!(p.drop.is_empty());
        apply(&mut v, &p, &mut n);
        // far down: everything from the top is dropped, the new window is built
        let p = v.plan(1000.0, 230.0, 112.0 * 100.0, |_| false).unwrap();
        assert_eq!(p.drop.len(), 90);
        assert_eq!(p.build.len(), 120, "a screen above, this one, a screen below");
        apply(&mut v, &p, &mut n);
        assert_eq!(v.built_len(), 120);
        assert_eq!(v.order().len(), 120);
    }

    #[test]
    fn a_kept_entry_survives_scrolling_away() {
        let mut v = grid(2000);
        let mut n = 0;
        let p = v.plan(1000.0, 230.0, 0.0, |_| false).unwrap();
        apply(&mut v, &p, &mut n);
        let held = v.order()[0];
        let p = v.plan(1000.0, 230.0, 112.0 * 100.0, |e| e == held).unwrap();
        assert!(!p.drop.contains(&held));
        assert_eq!(v.order()[0], held, "still first in list order");
    }

    #[test]
    fn an_arrival_moves_the_entries_after_it_and_is_fresh() {
        let mut v = VirtualList::new(Vec2::new(84.0, 104.0), Vec2::splat(8.0));
        v.set(vec![1, 3, 5], []);
        let mut n = 0;
        let p = v.plan(1000.0, 230.0, 0.0, |_| false).unwrap();
        apply(&mut v, &p, &mut n);
        v.set(vec![1, 2, 3, 5], [2]);
        let p = v.plan(1000.0, 230.0, 0.0, |_| false).unwrap();
        assert_eq!(p.build, vec![(2, Vec2::new(92.0, 0.0), true)]);
        assert_eq!(p.moves.len(), 2, "3 and 5 shift one cell along");
        assert!(p.drop.is_empty());
    }

    #[test]
    fn a_hidden_list_lets_go_of_everything() {
        let mut v = grid(50);
        let mut n = 0;
        let p = v.plan(1000.0, 230.0, 0.0, |_| false).unwrap();
        apply(&mut v, &p, &mut n);
        let p = v.plan(0.0, 0.0, 0.0, |_| false).unwrap();
        assert_eq!(p.drop.len(), 50);
        assert_eq!(v.built_len(), 0);
        // shown again: built again
        let p = v.plan(1000.0, 230.0, 0.0, |_| false).unwrap();
        assert_eq!(p.build.len(), 50);
    }

    #[test]
    fn an_entry_is_found_by_its_row() {
        let v = grid(2000);
        assert_eq!(v.offset_of(0, 1000.0), Some(0.0));
        assert_eq!(v.offset_of(25, 1000.0), Some(2.0 * 112.0), "10 to a row: entry 25 is in row 2");
        assert_eq!(v.offset_of(99_999, 1000.0), None);
    }

    #[test]
    fn one_stretched_column_for_a_list() {
        let mut v = VirtualList::new(Vec2::new(0.0, 48.0), Vec2::new(0.0, 4.0));
        v.set((0..500).collect(), []);
        let p = v.plan(350.0, 520.0, 0.0, |_| false).unwrap();
        assert_eq!(p.build.len(), 22, "11 rows touch the view, 11 more below");
        assert!(p.build.iter().all(|(_, at, _)| at.x == 0.0));
        assert_eq!(p.build[2].1.y, 104.0);
        assert_eq!(p.height, 500.0 * 52.0 - 4.0);
    }
}
