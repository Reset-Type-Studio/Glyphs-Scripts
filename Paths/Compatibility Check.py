# MenuTitle: ⚖️ Compatibility Check (Node Report)
# -*- coding: utf-8 -*-
# Version: 1.2
# Description: Reports node and handle counts per master for selected glyphs. Highlights master incompatibilities and node mismatches.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
import vanilla

# ----------------------------
# Utility
# ----------------------------

def compare_path_nodes(ref_path, test_path):
    ref_nodes = list(ref_path.nodes)
    test_nodes = list(test_path.nodes)
    max_len = max(len(ref_nodes), len(test_nodes))

    for i in range(max_len):
        if i >= len(ref_nodes):
            return i, None, test_nodes[i].type
        if i >= len(test_nodes):
            return i, ref_nodes[i].type, None
        if ref_nodes[i].type != test_nodes[i].type:
            return i, ref_nodes[i].type, test_nodes[i].type
    return None  # No differences


def nodeTypeName(t):
    if t is None:
        return "—"
    if t == LINE:
        return "LINE"
    if t == CURVE:
        return "CURVE"
    if t == QCURVE:
        return "QCURVE"
    if t == OFFCURVE:
        return "OFFCURVE"
    return str(t)


# ----------------------------
# UI
# ----------------------------

class CompatibilityReportWindow(object):
    def __init__(self, text):
        self.w = vanilla.FloatingWindow(
            (500, 500),
            "Compatibility Check – Node Report"
        )

        self.w.report = vanilla.TextEditor(
            (10, 10, -10, -10),
            text,
            readOnly=True
        )

        self.w.open()


# ----------------------------
# Report logic
# ----------------------------

class CompatibilityReporter(object):
    def __init__(self):
        self.lines = []

    def write(self, text=""):
        self.lines.append(text)

    def run(self):
        Glyphs.clearLog()
        font = Glyphs.font

        if not font:
            self.write("❌ No font open.")
            return

        if font.selectedLayers:
            glyphs_to_check = list({l.parent for l in font.selectedLayers})
        else:
            self.write("❌ No glyph selected.")
            return

        for glyph in glyphs_to_check:
            glyph_is_compatible = True

            self.write(f"🔠 Glyph: {glyph.name}")

            reference_master = font.masters[0]
            reference_layer = glyph.layers[reference_master.id]
            ref_path_structures = []

            for path in reference_layer.paths:
                oncurves = [n for n in path.nodes if n.type != OFFCURVE]
                offcurves = [n for n in path.nodes if n.type == OFFCURVE]
                ref_path_structures.append((len(oncurves), len(offcurves), path))

            # Per master report
            for master in font.masters:
                layer = glyph.layers[master.id]
                self.write(f"\n    ⭕️ Master: {master.name}")
                self.write(f"     • Paths: {len(layer.paths)}")

                for path in layer.paths:
                    oncurves = [n for n in path.nodes if n.type != OFFCURVE]
                    offcurves = [n for n in path.nodes if n.type == OFFCURVE]

                    n_lines = sum(1 for n in oncurves if n.type == LINE)
                    n_curves = sum(1 for n in oncurves if n.type in (CURVE, QCURVE))

                    self.write(f"     • Nodes: {len(oncurves)} (Lines: {n_lines} · Curves: {n_curves})")
                    self.write(f"     • Handles: {len(offcurves)}")
                    self.write(f"     • Total Points: {len(path.nodes)}")

            # Compare against reference
            for master in font.masters[1:]:
                layer = glyph.layers[master.id]

                for i, path in enumerate(layer.paths):
                    try:
                        ref_on, ref_off, ref_path = ref_path_structures[i]
                    except IndexError:
                        glyph_is_compatible = False
                        self.write(
                            f"  ⚠️ Incompatibility in master '{master.name}': "
                            f"Path #{i + 1} → Path missing."
                        )
                        continue

                    test_on = sum(1 for n in path.nodes if n.type != OFFCURVE)
                    test_off = sum(1 for n in path.nodes if n.type == OFFCURVE)

                    if (ref_on, ref_off) != (test_on, test_off):
                        glyph_is_compatible = False
                        mismatch = compare_path_nodes(ref_path, path)

                        self.write(f"  ⚠️ Incompatibility in master '{master.name}':")
                        self.write(
                            f"     • Path #{i + 1} mismatch → "
                            f"Expected ({ref_on}, {ref_off}), "
                            f"Found ({test_on}, {test_off})"
                        )

                        if mismatch:
                            index, expected_type, found_type = mismatch
                            self.write(
                                f"     • First difference at node #{index + 1}: "
                                f"Expected {nodeTypeName(expected_type)}, "
                                f"Found {nodeTypeName(found_type)}"
                            )

            if glyph_is_compatible:
                self.write("\n")
                self.write("-" * 100)
                self.write("  ✅ All masters are fully compatible with the reference master.")

        CompatibilityReportWindow("\n".join(self.lines))


# ----------------------------
# Run
# ----------------------------

CompatibilityReporter().run()
