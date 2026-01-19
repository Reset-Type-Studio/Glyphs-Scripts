# MenuTitle: 📍 Nodes At Extremes (Italics)
# -*- coding: utf-8 -*-
# Version: 1.2
# Description: Forces Extremes and removes internal diagonal-tangent curve nodes while keeping true inflections and keeping non-smooth (“broken handle”) nodes.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *

# Axis alignment tolerance for tangents (font units)
EPS = 0.01

# If handle vector is too small, fall back to on-curve direction
MIN_VEC = 0.001

# --- Robust inflection detection ---
INFLECT_SAMPLES = (0.06, 0.12, 0.20)   # farther from the join = less numeric noise
CURV_EPS = 1e-7                        # "too close to zero" = unreliable
REQUIRE_STABLE_SIGN = True             # side must have consistent sign across samples


# ----------------------------
# Vector helpers
# ----------------------------

def _vec(a, b):
    return (float(b.x - a.x), float(b.y - a.y))

def _cross_z(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def _is_axis_aligned(vx, vy):
    ax = abs(vx)
    ay = abs(vy)
    if ax <= EPS and ay <= EPS:
        return False
    # horizontal: ay ~ 0, vertical: ax ~ 0
    return (ax <= EPS and ay > EPS) or (ay <= EPS and ax > EPS)

def _sign(v):
    if v > CURV_EPS:
        return 1
    if v < -CURV_EPS:
        return -1
    return 0


# ----------------------------
# Node navigation helpers
# ----------------------------

def _prev_oncurve(n):
    p = n.prevNode
    guard = 0
    while p is not None and p.type == GSOFFCURVE:
        p = p.prevNode
        guard += 1
        if guard > 4000:
            return None
    return p

def _next_oncurve(n):
    p = n.nextNode
    guard = 0
    while p is not None and p.type == GSOFFCURVE:
        p = p.nextNode
        guard += 1
        if guard > 4000:
            return None
    return p


# ----------------------------
# Tangent helpers
# ----------------------------

def _incoming_tangent_vec(oncurve):
    """
    Tangent approaching oncurve:
      prefer (oncurve - prev offcurve)
      fallback (oncurve - prev oncurve)
    """
    prev = oncurve.prevNode
    if prev is None:
        return None

    if prev.type == GSOFFCURVE:
        vx, vy = _vec(prev.position, oncurve.position)
        if abs(vx) > MIN_VEC or abs(vy) > MIN_VEC:
            return (vx, vy)

    p_on = _prev_oncurve(oncurve)
    if p_on is None:
        return None
    vx, vy = _vec(p_on.position, oncurve.position)
    if abs(vx) > MIN_VEC or abs(vy) > MIN_VEC:
        return (vx, vy)

    return None

def _outgoing_tangent_vec(oncurve):
    """
    Tangent leaving oncurve:
      prefer (next offcurve - oncurve)
      fallback (next oncurve - oncurve)
    """
    nxt = oncurve.nextNode
    if nxt is None:
        return None

    if nxt.type == GSOFFCURVE:
        vx, vy = _vec(oncurve.position, nxt.position)
        if abs(vx) > MIN_VEC or abs(vy) > MIN_VEC:
            return (vx, vy)

    n_on = _next_oncurve(oncurve)
    if n_on is None:
        return None
    vx, vy = _vec(oncurve.position, n_on.position)
    if abs(vx) > MIN_VEC or abs(vy) > MIN_VEC:
        return (vx, vy)

    return None


# ----------------------------
# Cubic derivative helpers (inflection)
# ----------------------------

def _cubic_d1(P0, P1, P2, P3, t):
    mt = 1.0 - t
    x = 3.0 * ((P1[0]-P0[0])*(mt*mt) + 2.0*(P2[0]-P1[0])*(mt*t) + (P3[0]-P2[0])*(t*t))
    y = 3.0 * ((P1[1]-P0[1])*(mt*mt) + 2.0*(P2[1]-P1[1])*(mt*t) + (P3[1]-P2[1])*(t*t))
    return (x, y)

def _cubic_d2(P0, P1, P2, P3, t):
    mt = 1.0 - t
    ax = (P2[0] - 2.0*P1[0] + P0[0])
    ay = (P2[1] - 2.0*P1[1] + P0[1])
    bx = (P3[0] - 2.0*P2[0] + P1[0])
    by = (P3[1] - 2.0*P2[1] + P1[1])
    x = 6.0 * (ax*mt + bx*t)
    y = 6.0 * (ay*mt + by*t)
    return (x, y)

def _curv_indicator(P0, P1, P2, P3, t):
    # Sign of cross(d1, d2) corresponds to curvature direction
    d1 = _cubic_d1(P0, P1, P2, P3, t)
    d2 = _cubic_d2(P0, P1, P2, P3, t)
    return _cross_z(d1, d2)


# ----------------------------
# Segment builders around a node
# ----------------------------

def _get_prev_cubic(node):
    # prev_oncurve -> off1 -> off2 -> node
    off2 = node.prevNode
    if off2 is None or off2.type != GSOFFCURVE:
        return None
    off1 = off2.prevNode
    if off1 is None or off1.type != GSOFFCURVE:
        return None
    P0n = _prev_oncurve(node)
    if P0n is None:
        return None

    return (
        (float(P0n.position.x), float(P0n.position.y)),
        (float(off1.position.x), float(off1.position.y)),
        (float(off2.position.x), float(off2.position.y)),
        (float(node.position.x), float(node.position.y)),
    )

def _get_next_cubic(node):
    # node -> off1 -> off2 -> next_oncurve
    off1 = node.nextNode
    if off1 is None or off1.type != GSOFFCURVE:
        return None
    off2 = off1.nextNode
    if off2 is None or off2.type != GSOFFCURVE:
        return None
    P3n = _next_oncurve(node)
    if P3n is None:
        return None

    return (
        (float(node.position.x), float(node.position.y)),
        (float(off1.position.x), float(off1.position.y)),
        (float(off2.position.x), float(off2.position.y)),
        (float(P3n.position.x), float(P3n.position.y)),
    )


def _stable_side_sign(cubic, ts):
    P0, P1, P2, P3 = cubic
    first = None
    for t in ts:
        k = _curv_indicator(P0, P1, P2, P3, t)
        s = _sign(k)
        if s == 0:
            return 0
        if first is None:
            first = s
        elif REQUIRE_STABLE_SIGN and s != first:
            return 0
    return first or 0


def _is_true_inflection_at_join_from_cubics(prev_c, next_c):
    """
    TRUE inflection at the JOIN if:
      - curvature sign on prev segment (near t=1) is stable
      - curvature sign on next segment (near t=0) is stable
      - and they are opposite
    """
    prev_ts = [max(0.0, 1.0 - s) for s in INFLECT_SAMPLES]
    next_ts = [min(1.0, s) for s in INFLECT_SAMPLES]

    s_prev = _stable_side_sign(prev_c, prev_ts)
    s_next = _stable_side_sign(next_c, next_ts)

    return (s_prev != 0 and s_next != 0 and s_prev != s_next)


# ----------------------------
# Removal helpers
# ----------------------------

def _remove_keep_shape(path, node):
    # Prefer "keep shape" method
    try:
        path.removeNodeCheckKeepShape_(node)
        return True
    except Exception:
        pass
    # Fallback
    try:
        path.removeNode_(node)
        return True
    except Exception:
        return False

def _layer_has_selected_curve_oncurves(layer):
    for p in layer.paths:
        for n in p.nodes:
            if n.type == GSCURVE and n.selected:
                return True
    return False

def _first_last_oncurve_nodes(path):
    oncurves = [n for n in path.nodes if n.type != GSOFFCURVE]
    if not oncurves:
        return (None, None)
    return (oncurves[0], oncurves[-1])

def _is_non_smooth(node):
    # In Glyphs: "broken handles"/non-soft connection => node.smooth == False
    try:
        return not bool(node.smooth)
    except Exception:
        return False


# ----------------------------
# Main
# ----------------------------

font = Glyphs.font
if not font:
    raise Exception("No font open.")

undo = None
try:
    undo = font.undoManager()
except Exception:
    undo = None

if undo:
    try:
        undo.beginUndoGrouping()
    except Exception:
        pass

font.disableUpdateInterface()

try:
    removed = 0
    kept_inflect = 0
    kept_nonsmooth = 0
    considered = 0

    for layer in font.selectedLayers:
        if not layer.paths:
            continue

        # 1) Add extrema first
        layer.addNodesAtExtremes(force=False, checkSelection=False)

        restrict = _layer_has_selected_curve_oncurves(layer)

        for path in layer.paths:
            if not path.nodes:
                continue

            open_path = not bool(path.closed)
            first_on, last_on = _first_last_oncurve_nodes(path)

            # Build candidates in O(n)
            indexed = []
            for idx, n in enumerate(path.nodes):
                if n.type != GSCURVE:
                    continue
                if restrict and not n.selected:
                    continue
                indexed.append((idx, n))

            # Remove back-to-front to keep indices stable
            indexed.sort(reverse=True, key=lambda t: t[0])

            for idx, n in indexed:
                # do not touch endpoints of open paths (on-curve endpoints)
                if open_path and (n == first_on or n == last_on):
                    continue

                # Keep any non-smooth ("broken handles") nodes
                if _is_non_smooth(n):
                    kept_nonsmooth += 1
                    continue

                # Must have valid cubic segments around for inflection logic + tangents
                prev_c = _get_prev_cubic(n)
                next_c = _get_next_cubic(n)
                if prev_c is None or next_c is None:
                    continue

                inc = _incoming_tangent_vec(n)
                out = _outgoing_tangent_vec(n)
                if inc is None or out is None:
                    continue

                # Only consider if BOTH sides are diagonal tangents
                if _is_axis_aligned(*inc) or _is_axis_aligned(*out):
                    continue

                considered += 1

                # Keep TRUE inflections
                if _is_true_inflection_at_join_from_cubics(prev_c, next_c):
                    kept_inflect += 1
                    continue

                if _remove_keep_shape(path, n):
                    removed += 1

    print("Nodes At Extremes (Italics)")
    print("Considered diagonal internal nodes:", considered)
    print("Kept (true inflections):", kept_inflect)
    print("Kept (non-smooth/broken handles):", kept_nonsmooth)
    print("Removed:", removed)

finally:
    font.enableUpdateInterface()
    Glyphs.redraw()

    if undo:
        try:
            undo.endUndoGrouping()
        except Exception:
            pass
