from itertools import permutations


def _volume(dims):
    return dims[0] * dims[1] * dims[2]


def _rotations(dims):
    # sorted so the result is deterministic (a plain set has arbitrary order)
    return sorted(set(permutations(dims)))


def _split(space, placed):
    """Cut the leftover of `space` into 3 non-overlapping pieces after
    putting an item of size `placed` in its corner. Empty pieces are dropped."""
    sl, sw, sh = space
    pl, pw, ph = placed
    pieces = [
        (sl - pl, sw, sh),   # slab beside the item (full width and height)
        (pl, sw - pw, sh),   # slab in front of the item (item's length only)
        (pl, pw, sh - ph),   # space above the item (item's footprint only)
    ]
    return [p for p in pieces if p[0] > 0 and p[1] > 0 and p[2] > 0]


def _try_pack(items, box_dims):
    """Place items (in the given order) into box_dims. True if all fit."""
    spaces = [box_dims]
    for item in items:
        best = None  # (wasted_volume, space_index, rotation)
        for index, space in enumerate(spaces):
            for rotation in _rotations(item):
                if all(rotation[i] <= space[i] for i in range(3)):
                    wasted = _volume(space) - _volume(rotation)
                    if best is None or wasted < best[0]:
                        best = (wasted, index, rotation)
        if best is None:
            return False
        _, index, rotation = best
        space = spaces.pop(index)
        spaces.extend(_split(space, rotation))
    return True


def can_pack(items, box_dims):
    """Pure function, no database. `items` is a list of (l, w, h) tuples,
    one entry per physical unit. `box_dims` is the box's inner (l, w, h)."""
    orderings = [
        sorted(items, key=_volume, reverse=True),
        sorted(items, key=lambda d: max(d), reverse=True),
        sorted(items, key=lambda d: min(d), reverse=True),
    ]
    return any(_try_pack(order, box_dims) for order in orderings)


def recommend_box(order):
    """Return the cheapest Box that fits the order, or None if none does."""
    from .models import Box  # local import keeps this module easy to test

    units = []
    total_weight = 0
    for item in order.items.select_related("product"):
        p = item.product
        total_weight += p.weight * item.quantity
        units.extend([(p.length, p.width, p.height)] * item.quantity)

    if not units:
        raise ValueError("Order has no items.")

    total_volume = sum(_volume(u) for u in units)

    # Cheapest first; ties broken by smaller box, then id, so it's deterministic.
    boxes = sorted(
        Box.objects.all(),
        key=lambda b: (b.cost, b.inner_length * b.inner_width * b.inner_height, b.pk),
    )
    for box in boxes:
        dims = (box.inner_length, box.inner_width, box.inner_height)
        if total_weight > box.max_weight:
            continue                      # cheap check first
        if total_volume > _volume(dims):
            continue                      # necessary condition, still cheap
        if can_pack(units, dims):         # the real geometric check
            return box
    return None