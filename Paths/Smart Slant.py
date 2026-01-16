# MenuTitle: ⚡️ Smart Italic
# -*- coding: utf-8 -*-
# Version: 1.4
# Description: Applies optical slant algorythm, approximating cursivy behavior (sorry Rainer) by modulating horizontal shift across the vertical axis. Preserves spacing, metrics keys, and anchors, with optional master-level italic angle support.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

import vanilla
import math
from AppKit import NSAffineTransform
from GlyphsApp import Glyphs, GSLayer


# -------------------------
# Helpers
# -------------------------

def _anchors_iter(layer):
    a = layer.anchors
    if not a:
        return []
    if hasattr(a, "values"):
        return list(a.values())
    return list(a)


def _apply_path_transform(path, t):
    path.applyTransform(t.transformStruct())


def _associated_master(layer):
    font = Glyphs.font
    mid = getattr(layer, "associatedMasterId", None)
    if not font or not mid:
        return None
    for m in font.masters:
        if m.id == mid:
            return m
    return None


def _glyph_is_avoided(glyph, avoidColor):
    if avoidColor < 0:
        return False
    try:
        return glyph.color == avoidColor
    except Exception:
        return False


# -------------------------
# Core slant logic
# -------------------------

def _slant_one_layer(layer, italicAngleDeg, setItalicAngle):
    master = _associated_master(layer)
    if not master:
        return

    # --- STORE SPACING ---
    originalLSB = float(layer.LSB)
    originalRSB = float(layer.RSB)

    leftKey = layer.leftMetricsKey
    rightKey = layer.rightMetricsKey
    widthKey = layer.widthMetricsKey

    layer.leftMetricsKey = None
    layer.rightMetricsKey = None
    layer.widthMetricsKey = None

    if setItalicAngle:
        master.italicAngle = float(italicAngleDeg)

    shear = math.tan(math.radians(float(italicAngleDeg)))

    # --- BOUNDS & REFERENCE ---
    b0 = layer.bounds
    yRef = float(b0.origin.y) + float(b0.size.height) * 0.335

    # --- APPLY AFFINE SHEAR ---
    for path in layer.paths:
        for node in path.nodes:
            node.x += shear * (node.y - yRef)

    for a in _anchors_iter(layer):
        a.position = (
            a.position.x + shear * (a.position.y - yRef),
            a.position.y
        )

    # --- RECENTER ---
    centerX = float(b0.origin.x) + float(b0.size.width) * 0.5
    b1 = layer.bounds
    newCenterX = float(b1.origin.x) + float(b1.size.width) * 0.5

    dx = centerX - newCenterX
    if abs(dx) > 1e-6:
        shift = NSAffineTransform.transform()
        shift.translateXBy_yBy_(dx, 0.0)

        for path in layer.paths:
            _apply_path_transform(path, shift)
        for a in _anchors_iter(layer):
            a.position = shift.transformPoint_(a.position)

    # --- RESTORE ---
    layer.LSB = originalLSB
    layer.RSB = originalRSB
    layer.leftMetricsKey = leftKey
    layer.rightMetricsKey = rightKey
    layer.widthMetricsKey = widthKey


# -------------------------
# UI
# -------------------------

class SimpleSlantUI(object):
    def __init__(self):
        self.w = vanilla.FloatingWindow((330, 240), "Simple Slant")

        y = 15

        self.w.t1 = vanilla.TextBox((15, y, 140, 17), "Italic angle (°)")
        self.w.angle = vanilla.EditText((170, y - 2, 130, 22), "9")
        y += 35

        self.w.setAngle = vanilla.CheckBox(
            (15, y, 300, 20),
            "Add Italic Angle in Font Info (per master)",
            value=True
        )
        y += 30

        self.w.avoidColor = vanilla.CheckBox(
            (15, y, 300, 20),
            "Avoid glyphs color: Red",
            value=True
        )
        y += 35

        self.w.applySel = vanilla.Button(
            (15, y, 300, 24),
            "Apply to selection",
            callback=self.applySelection
        )
        y += 30

        self.w.applyMaster = vanilla.Button(
            (15, y, 300, 24),
            "Apply to current master",
            callback=self.applyMaster
        )
        y += 30

        self.w.applyAll = vanilla.Button(
            (15, y, 300, 24),
            "Apply to all masters",
            callback=self.applyAll
        )

        self.w.open()

    # -------------------------

    def _run(self, layers):
        font = Glyphs.font
        if not font:
            return

        try:
            angle = float(self.w.angle.get())
        except Exception:
            Glyphs.showNotification("Simple Slant", "Invalid angle")
            return

        setItalicAngle = bool(self.w.setAngle.get())
        avoidRed = bool(self.w.avoidColor.get())
        avoidColor = 0 if avoidRed else -1  # Red = 0

        try:
            font.disableUpdateInterface()
        except Exception:
            pass

        try:
            for layer in layers:
                if not isinstance(layer, GSLayer):
                    continue

                glyph = layer.parent
                if _glyph_is_avoided(glyph, avoidColor):
                    continue

                began = False
                try:
                    glyph.beginUndo()
                    began = True
                except Exception:
                    pass

                _slant_one_layer(layer, angle, setItalicAngle)

                if began:
                    try:
                        glyph.endUndo()
                    except Exception:
                        pass
        finally:
            try:
                font.enableUpdateInterface()
            except Exception:
                pass

        Glyphs.showNotification(
            "Simple Slant",
            "Done (%d layer(s))" % len(layers)
        )

    # -------------------------

    def applySelection(self, sender):
        font = Glyphs.font
        if not font or not font.selectedLayers:
            return
        self._run(list(font.selectedLayers))

    def applyMaster(self, sender):
        font = Glyphs.font
        if not font:
            return
        master = font.selectedFontMaster
        layers = []
        for g in font.glyphs:
            l = g.layers[master.id]
            if l:
                layers.append(l)
        self._run(layers)

    def applyAll(self, sender):
        font = Glyphs.font
        if not font:
            return
        layers = []
        for g in font.glyphs:
            for m in font.masters:
                l = g.layers[m.id]
                if l:
                    layers.append(l)
        self._run(layers)


SimpleSlantUI()
