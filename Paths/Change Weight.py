# MenuTitle: 🎚️ Change Weight (Boldify)
# -*- coding: utf-8 -*-
# Version: 1.2
# Description: Makes letters bold or thin, changes weight via Offset Curve; optionally moderates width growth, keeps sidebearings, updates anchors, and snaps horizontal line segments to vertical metrics within a tolerance.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

import vanilla
import copy
import math
from AppKit import NSAffineTransform

# Optional imports (Glyphs macro environment usually provides these globally)
try:
    from GlyphsApp import Glyphs, Message, OFFCURVE, LINE
except Exception:
    pass

# -------------------------------------------------
# Vanilla window
# -------------------------------------------------

class OffsetWeightTool(object):

    MIN_HORIZONTAL_SEGMENT_LENGTH = 25.0  # typographic units
    EPS = 1e-6

    def __init__(self):
        # Cache node type constants once (avoid repeated try/except in hot loops)
        self.NODE_OFFCURVE = OFFCURVE if "OFFCURVE" in globals() else "offcurve"
        self.NODE_LINE = LINE if "LINE" in globals() else "line"

        self.w = vanilla.FloatingWindow((310, 260), "Change Weight")

        y = 14
        line = 32

        self.w.textH = vanilla.TextBox((15, y, 200, 16), "Horizontal Weight:")
        self.w.offsetH = vanilla.EditText((180, y - 2, 110, 22), "20")
        y += line

        self.w.textV = vanilla.TextBox((15, y, 200, 16), "Vertical Weight:")
        self.w.offsetV = vanilla.EditText((180, y - 2, 110, 22), "20")
        y += line

        self.w.textGrow = vanilla.TextBox((15, y, 200, 16), "Width Growth (%):")
        self.w.widthGrowPercent = vanilla.EditText((180, y - 2, 110, 22), "75")
        y += line

        self.w.textTol = vanilla.TextBox((15, y, 200, 16), "Metrics Snap Tolerance:")
        self.w.metricTolerance = vanilla.EditText((180, y - 2, 110, 22), "15")
        y += line

        self.w.lockWidth = vanilla.CheckBox(
            (15, y, -15, 20),
            "Lock width (keep original width)",
            value=False
        )
        y += 26

        self.w.allMasters = vanilla.CheckBox(
            (15, y, -15, 20),
            "Apply to all masters",
            value=False
        )
        y += 36

        self.w.apply = vanilla.Button(
            (15, y, -15, 34),
            "Apply Offset",
            callback=self.applyOffset
        )

        self.w.open()

    # -------------------------------------------------
    # Utilities
    # -------------------------------------------------

    def _getFloatField(self, field, default=0.0):
        try:
            s = field.get()
            if s is None:
                return float(default)
            s = str(s).strip()
            if not s:
                return float(default)
            return float(s)
        except Exception:
            return None

    def _layerBoundsTuple(self, layer):
        b = layer.bounds
        return (b.origin.x, b.origin.y, b.size.width, b.size.height)

    def _layerHasPaths(self, layer):
        try:
            return bool(layer and layer.paths and len(layer.paths) > 0)
        except Exception:
            return False

    # -------------------------------------------------
    # Offset Curve filter
    # -------------------------------------------------

    def _findOffsetCurveFilter(self):
        for thisFilter in Glyphs.filters:
            if thisFilter.__class__.__name__ == "GlyphsFilterOffsetCurve":
                return thisFilter
        return None

    def _applyOffsetCurveToLayerIfPossible(self, offsetCurve, thisLayer, offsetH, offsetV):
        if not hasattr(offsetCurve, "filter"):
            return False
        try:
            offsetCurve.filter(thisLayer, False, {0: offsetH, 1: offsetV, 2: 0, 3: 0.5})
            return True
        except Exception:
            return False

    # -------------------------------------------------
    # Anchor movement
    # -------------------------------------------------

    def _snapshotAnchors(self, thisLayer):
        """Returns dict: anchorName -> (x, y)"""
        anchors = {}
        try:
            for a in thisLayer.anchors:
                anchors[a.name] = (a.position.x, a.position.y)
        except Exception:
            pass
        return anchors

    def _applyAnchorXTransformKeepY(self, thisLayer, anchorMap, dx=0.0, pivotX=None, scaleX=1.0):
        """Apply dx and a scale around pivotX to anchor X, keep original Y."""
        if not anchorMap:
            return
        if pivotX is None:
            pivotX = thisLayer.bounds.origin.x

        try:
            for a in thisLayer.anchors:
                if a.name not in anchorMap:
                    continue
                ax0, ay0 = anchorMap[a.name]
                ax1 = ax0 + dx
                ax2 = pivotX + (ax1 - pivotX) * scaleX
                a.position = (ax2, ay0)
        except Exception:
            pass

    # -------------------------------------------------
    # Vertical metric snapping (line segments only)
    # -------------------------------------------------

    def _metricYsForLayer(self, thisLayer):
        ys = [0.0]
        try:
            m = thisLayer.master
            ys.extend([m.xHeight, m.capHeight, m.ascender, m.descender])
        except Exception:
            pass
        return sorted(set(y for y in ys if y is not None))

    def _snapHorizontalSegmentsToMetrics(self, thisLayer, tol):
        """Snap only straight LINE segments that are near-horizontal, with sufficient length.
           FIX: Do not wrap last->first for open paths.
        """
        if not self._layerHasPaths(thisLayer):
            return

        metricYs = self._metricYsForLayer(thisLayer)
        if not metricYs:
            return

        OFF = self.NODE_OFFCURVE
        LIN = self.NODE_LINE

        for thisPath in thisLayer.paths:
            try:
                nodes = list(thisPath.nodes)
            except Exception:
                continue

            n = len(nodes)
            if n < 2:
                continue

            try:
                isClosed = bool(thisPath.closed)
            except Exception:
                isClosed = True  # safest fallback

            end = n if isClosed else (n - 1)
            for i in range(end):
                a = nodes[i]
                b = nodes[(i + 1) % n] if isClosed else nodes[i + 1]

                if a.type != LIN or b.type != LIN:
                    continue

                dy = b.position.y - a.position.y
                if abs(dy) > tol:
                    continue

                dx = b.position.x - a.position.x
                segLength = (dx * dx + dy * dy) ** 0.5
                if segLength < self.MIN_HORIZONTAL_SEGMENT_LENGTH:
                    continue

                segY = (a.position.y + b.position.y) * 0.5
                closest = min(metricYs, key=lambda y: abs(y - segY))
                if abs(closest - segY) > tol:
                    continue

                deltaY = closest - segY
                a.position = (a.position.x, a.position.y + deltaY)
                b.position = (b.position.x, b.position.y + deltaY)

                if a.nextNode and a.nextNode.type == OFF:
                    a.nextNode.position = (a.nextNode.position.x, a.nextNode.position.y + deltaY)
                if b.prevNode and b.prevNode.type == OFF:
                    b.prevNode.position = (b.prevNode.position.x, b.prevNode.position.y + deltaY)

    # -------------------------------------------------
    # Node cleanup
    # -------------------------------------------------

    def _snapshotNodeCounts(self, thisLayer):
        try:
            return [len(p.nodes) for p in thisLayer.paths]
        except Exception:
            return []
 
    def _reduceExtraNodesBestEffort(self, thisLayer, desiredCounts):
        """
        Best effort: remove extra LINE nodes with no adjacent offcurves,
        but choose the *safest* candidate (minimizes damage) instead of deleting the first one.

        Heuristics:
        - Never delete endpoints of open paths
        - Prefer nodes that are nearly collinear (angle ~ 180°)
        - Prefer deletions that create a short prev->next segment (avoid long "diagonals")
        - Slightly avoid deleting extrema in Y (helps for bottoms/tops like your f)
        """
        LIN = self.NODE_LINE
        OFF = self.NODE_OFFCURVE

        def dist(a, b):
            dx = b.x - a.x
            dy = b.y - a.y
            return (dx*dx + dy*dy) ** 0.5

        def angle_deviation(prevPt, curPt, nextPt):
            # deviation from straight line (pi). 0 = perfectly collinear.
            v1x = prevPt.x - curPt.x
            v1y = prevPt.y - curPt.y
            v2x = nextPt.x - curPt.x
            v2y = nextPt.y - curPt.y
            n1 = (v1x*v1x + v1y*v1y) ** 0.5
            n2 = (v2x*v2x + v2y*v2y) ** 0.5
            if n1 < 1e-6 or n2 < 1e-6:
                return 0.0
            dot = (v1x*v2x + v1y*v2y) / (n1*n2)
            # clamp to avoid acos domain errors
            dot = max(-1.0, min(1.0, dot))
            ang = math.acos(dot)  # 0..pi
            return abs(math.pi - ang)

        try:
            paths = thisLayer.paths
        except Exception:
            return

        for pIndex, p in enumerate(paths):
            if pIndex >= len(desiredCounts):
                continue

            try:
                target = int(desiredCounts[pIndex])
            except Exception:
                continue

            while True:
                try:
                    current = len(p.nodes)
                except Exception:
                    break
                if current <= target:
                    break

                # Precompute Y extrema (avoid removing bottom/top structure)
                try:
                    ys = [n.position.y for n in p.nodes if hasattr(n, "position")]
                    minY = min(ys) if ys else None
                    maxY = max(ys) if ys else None
                except Exception:
                    minY = None
                    maxY = None

                try:
                    isClosed = bool(p.closed)
                except Exception:
                    isClosed = True

                candidates = []
                try:
                    nodes = list(p.nodes)
                    nCount = len(nodes)

                    for i, n in enumerate(nodes):
                        if n.type != LIN:
                            continue

                        # Do not delete endpoints in open paths
                        if not isClosed and (i == 0 or i == nCount - 1):
                            continue

                        # Avoid line nodes that are part of a curve (adjacent offcurves)
                        if n.prevNode and n.prevNode.type == OFF:
                            continue
                        if n.nextNode and n.nextNode.type == OFF:
                            continue

                        prevN = n.prevNode
                        nextN = n.nextNode
                        if not prevN or not nextN:
                            continue

                        prevPt = prevN.position
                        curPt = n.position
                        nextPt = nextN.position

                        # Score candidate: lower is better
                        angDev = angle_deviation(prevPt, curPt, nextPt)          # 0 best
                        chord = dist(prevPt, nextPt)                              # shorter better (avoid diagonals)
                        legs = dist(prevPt, curPt) + dist(curPt, nextPt)          # local context

                        # Normalize chord against local legs (stable across sizes)
                        chordNorm = chord / max(legs, 1e-6)

                        # Penalty for removing extrema (helps with your bottom node case)
                        extremePenalty = 0.0
                        if minY is not None and abs(curPt.y - minY) < 1e-3:
                            extremePenalty += 0.5
                        if maxY is not None and abs(curPt.y - maxY) < 1e-3:
                            extremePenalty += 0.5

                        # Weighted sum:
                        # - prioritize collinearity strongly
                        # - then avoid long chord connections
                        score = (angDev * 10.0) + (chordNorm * 2.0) + extremePenalty

                        candidates.append((score, i))
                except Exception:
                    break

                if not candidates:
                    break

                candidates.sort(key=lambda x: x[0])
                bestIndex = candidates[0][1]

                try:
                    del p.nodes[bestIndex]
                except Exception:
                    break


    # -------------------------------------------------
    # Outline transforms
    # -------------------------------------------------

    def _applyTransformToPathsOnly(self, thisLayer, t):
        """Prefer path.applyTransform when available; fallback to per-node."""
        try:
            for p in thisLayer.paths:
                try:
                    p.applyTransform(t)
                except Exception:
                    for n in p.nodes:
                        n.position = t.transformPoint_(n.position)
        except Exception:
            pass

    def _restoreBoundsPathsOnly(self, thisLayer, boundsTuple, lockWidth=True):
        """Scale layer paths back to original bounds (height always; width optional), then translate to original origin.
           Returns (dx, dy) translation applied.
           FIX: guard against near-zero original height to avoid collapsing outlines.
        """
        ox, oy, ow, oh = boundsTuple
        b = thisLayer.bounds
        if b.size.width == 0 or b.size.height == 0:
            return (0.0, 0.0)

        scaleX = (ow / b.size.width) if lockWidth else 1.0

        if abs(oh) < self.EPS:
            scaleY = 1.0
        else:
            scaleY = oh / b.size.height

        cx = b.origin.x + b.size.width / 2.0
        cy = b.origin.y + b.size.height / 2.0

        t = NSAffineTransform.alloc().init()
        t.translateXBy_yBy_(-cx, -cy)
        t.scaleXBy_yBy_(scaleX, scaleY)
        t.translateXBy_yBy_(cx, cy)
        self._applyTransformToPathsOnly(thisLayer, t)

        fb = thisLayer.bounds
        dx = ox - fb.origin.x
        dy = oy - fb.origin.y

        move = NSAffineTransform.alloc().init()
        move.translateXBy_yBy_(dx, dy)
        self._applyTransformToPathsOnly(thisLayer, move)

        return (dx, dy)

    def _moderateOutlineWidthChange(self, thisLayer, originalWidth, factor):
        """Moderate outline width change (0..1) and return (pivotX, scaleX) used."""
        b = thisLayer.bounds
        currentWidth = b.size.width
        if currentWidth == 0:
            return (b.origin.x, 1.0)

        targetWidth = originalWidth + (currentWidth - originalWidth) * factor
        if abs(targetWidth - currentWidth) < 0.0001:
            return (b.origin.x, 1.0)

        scaleX = targetWidth / currentWidth
        pivotX = b.origin.x
        yPivot = b.origin.y + b.size.height / 2.0

        t = NSAffineTransform.alloc().init()
        t.translateXBy_yBy_(-pivotX, -yPivot)
        t.scaleXBy_yBy_(scaleX, 1.0)
        t.translateXBy_yBy_(pivotX, yPivot)
        self._applyTransformToPathsOnly(thisLayer, t)

        return (pivotX, scaleX)

    def _restoreLSBandRSBFromBounds(self, thisLayer, lsb, rsb):
        try:
            thisLayer.LSB = lsb
            b = thisLayer.bounds
            thisLayer.width = b.size.width + lsb + rsb
        except Exception:
            pass

    # -------------------------------------------------
    # Backup/restore for fallback mode
    # -------------------------------------------------

    def _backupLayerForFallback(self, layer):
        """More robust than shallow-copying shapes list.
           Preference order: copyDecomposedLayer() -> copy().
        """
        try:
            if hasattr(layer, "copyDecomposedLayer"):
                return layer.copyDecomposedLayer()
        except Exception:
            pass
        try:
            if hasattr(layer, "copy"):
                return layer.copy()
        except Exception:
            pass
        return None

    def _restoreLayerFromBackup(self, layer, backupLayer, anchorsMap=None):
        if not backupLayer:
            return
        try:
            layer.shapes = backupLayer.shapes
        except Exception:
            pass
        try:
            layer.width = backupLayer.width
        except Exception:
            pass

        if anchorsMap:
            try:
                for a in layer.anchors:
                    if a.name in anchorsMap:
                        x, y = anchorsMap[a.name]
                        a.position = (x, y)
            except Exception:
                pass

    # -------------------------------------------------
    # Main
    # -------------------------------------------------

    def applyOffset(self, sender):
        font = Glyphs.font
        if not font:
            return

        offsetH = self._getFloatField(self.w.offsetH, default=20.0)
        offsetV = self._getFloatField(self.w.offsetV, default=20.0)
        growPercent = self._getFloatField(self.w.widthGrowPercent, default=75.0)
        metricTol = self._getFloatField(self.w.metricTolerance, default=15.0)

        if None in (offsetH, offsetV, growPercent, metricTol):
            Message("Error", "All numeric fields must contain numbers.")
            return

        growPercent = max(0.0, min(100.0, float(growPercent)))
        widthGrowthFactor = growPercent / 100.0

        applyToAllMasters = bool(self.w.allMasters.get())
        lockWidth = bool(self.w.lockWidth.get())

        offsetCurve = self._findOffsetCurveFilter()
        if not offsetCurve:
            Message("Error", "Offset Curve filter not found.")
            return

        # Group selected layers by glyph
        glyphMap = {}
        for thisLayer in font.selectedLayers:
            if thisLayer and getattr(thisLayer, "parent", None):
                glyphMap.setdefault(thisLayer.parent, []).append(thisLayer)

        font.disableUpdateInterface()
        try:
            for thisGlyph, selectedLayers in glyphMap.items():

                # Undo grouping is on glyph, not font
                try:
                    thisGlyph.beginUndo()
                except Exception:
                    pass

                try:
                    # Decide target layers
                    if applyToAllMasters:
                        # Preserving original behavior: all layers
                        layersToProcess = list(thisGlyph.layers)
                        # If you strictly want masters only:
                        # layersToProcess = [l for l in thisGlyph.layers if getattr(l, "isMasterLayer", False)]
                    else:
                        layersToProcess = list(selectedLayers)

                    # Cache per-layer data for post-processing
                    cache = {}
                    for lyr in layersToProcess:
                        if not self._layerHasPaths(lyr):
                            continue
                        btuple = self._layerBoundsTuple(lyr)
                        cache[lyr.layerId] = {
                            "bounds": btuple,
                            "ow": btuple[2],
                            "anchors": self._snapshotAnchors(lyr),
                            "nodes": self._snapshotNodeCounts(lyr),
                            "lsb": getattr(lyr, "LSB", 0.0),
                            "rsb": getattr(lyr, "RSB", 0.0),
                        }

                    # Preferred: per-layer API for selected layers mode
                    usedLayerAPI = False
                    if not applyToAllMasters:
                        for lyr in layersToProcess:
                            if self._layerHasPaths(lyr) and self._applyOffsetCurveToLayerIfPossible(offsetCurve, lyr, offsetH, offsetV):
                                usedLayerAPI = True

                    # Fallback: old filter (affects ALL layers) — protect other layers
                    backups = None
                    if (not applyToAllMasters) and (not usedLayerAPI):
                        selectedLayerIDs = set([l.layerId for l in layersToProcess])
                        backups = {}
                        for lyr in thisGlyph.layers:
                            if lyr.layerId in selectedLayerIDs:
                                continue
                            backups[lyr.layerId] = {
                                "backupLayer": self._backupLayerForFallback(lyr),
                                "anchors": self._snapshotAnchors(lyr),
                            }

                    # Apply offset using filter processing if needed
                    if applyToAllMasters or (not usedLayerAPI):
                        offsetCurve.processFont_withArguments_(
                            font,
                            [
                                "GlyphsFilterOffsetCurve",
                                str(offsetH),
                                str(offsetV),
                                "0",
                                "0.5",
                                "include:%s" % thisGlyph.name,
                            ]
                        )

                    # Post-process only target layers
                    for lyr in layersToProcess:
                        data = cache.get(lyr.layerId)
                        if not data:
                            continue

                        dx, dy = self._restoreBoundsPathsOnly(lyr, data["bounds"], lockWidth)

                        pivotX = lyr.bounds.origin.x
                        scaleX = 1.0

                        if not lockWidth:
                            pivotX, scaleX = self._moderateOutlineWidthChange(lyr, data["ow"], widthGrowthFactor)
                            self._restoreLSBandRSBFromBounds(lyr, data["lsb"], data["rsb"])

                        self._applyAnchorXTransformKeepY(
                            lyr,
                            data["anchors"],
                            dx=dx,
                            pivotX=pivotX,
                            scaleX=scaleX,
                        )

                        self._reduceExtraNodesBestEffort(lyr, data["nodes"])
                        self._snapHorizontalSegmentsToMetrics(lyr, tol=float(metricTol))

                    # Restore non-target layers if fallback mode
                    if backups:
                        for lyr in thisGlyph.layers:
                            b = backups.get(lyr.layerId)
                            if not b:
                                continue
                            self._restoreLayerFromBackup(lyr, b.get("backupLayer"), anchorsMap=b.get("anchors"))

                finally:
                    try:
                        thisGlyph.endUndo()
                    except Exception:
                        pass

        finally:
            font.enableUpdateInterface()
            Glyphs.redraw()


OffsetWeightTool()