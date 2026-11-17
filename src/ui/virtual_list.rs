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

#[cfg(test)]
mod tests {
    use super::*;

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
