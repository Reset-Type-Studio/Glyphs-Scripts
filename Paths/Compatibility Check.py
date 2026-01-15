# MenuTitle: ⚖️ Compatibility Check (Node Report)
# -*- coding: utf-8 -*-
# Version: 1.1
# Description: Reports node and handle counts per master for selected or active glyphs. Highlights master incompatibilities and node mismatches.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *

def compare_path_nodes(ref_path, test_path):
    ref_nodes = [n for n in ref_path.nodes]
    test_nodes = [n for n in test_path.nodes]
    max_len = max(len(ref_nodes), len(test_nodes))
    
    for i in range(max_len):
        if i >= len(ref_nodes):
            return i, None, test_nodes[i].type
        if i >= len(test_nodes):
            return i, ref_nodes[i].type, None
        if ref_nodes[i].type != test_nodes[i].type:
            return i, ref_nodes[i].type, test_nodes[i].type
    return None  # No differences

def report_nodes_detailed():
    Glyphs.clearLog()
    font = Glyphs.font

    if not font:
        print("❌ No font open.")
        return

    # Determine target glyphs
    if font.selectedLayers:
        glyphs_to_check = list({l.parent for l in font.selectedLayers})
    else:
        print("❌ No glyph selected.")
        return

    for glyph in glyphs_to_check:
        print(f"🔠 Glyph: {glyph.name}")
        reference_master = font.masters[0]
        reference_layer = glyph.layers[reference_master.id]
        ref_path_structures = []

        # Collect reference path structures
        for path in reference_layer.paths:
            nodes = [n for n in path.nodes if n.type != OFFCURVE]
            offcurves = [n for n in path.nodes if n.type == OFFCURVE]
            ref_path_structures.append((len(nodes), len(offcurves), path))

        # Per master info
        path_data_by_master = {}
        for master in font.masters:
            layer = glyph.layers[master.id]
            path_data = []

            for path in layer.paths:
                oncurves = [n for n in path.nodes if n.type != OFFCURVE]
                offcurves = [n for n in path.nodes if n.type == OFFCURVE]

                n_lines = sum(1 for n in oncurves if n.type == LINE)
                n_curves = sum(1 for n in oncurves if n.type in (CURVE, QCURVE))
                total = len(oncurves) + len(offcurves)

                path_data.append((len(oncurves), len(offcurves)))

            path_data_by_master[master.name] = path_data

            print(f"  🧱 Master: {master.name}")
            print(f"     • Paths: {len(layer.paths)}")

            for i, path in enumerate(layer.paths):
                oncurves = [n for n in path.nodes if n.type != OFFCURVE]
                offcurves = [n for n in path.nodes if n.type == OFFCURVE]
                n_lines = sum(1 for n in oncurves if n.type == LINE)
                n_curves = sum(1 for n in oncurves if n.type in (CURVE, QCURVE))
                print(f"     • Nodes: {len(oncurves)} (Lines: {n_lines} · Curves: {n_curves})")
                print(f"     • Handles: {len(offcurves)}")
                print(f"     • Total Points: {len(path.nodes)}")

        # Compare against reference
        for master in font.masters[1:]:
            layer = glyph.layers[master.id]
            for i, path in enumerate(layer.paths):
                try:
                    ref_on, ref_off, ref_path = ref_path_structures[i]
                except IndexError:
                    print(f"  ⚠️ Incompatibility in master '{master.name}': Path #{i + 1} → Path missing.")
                    continue

                test_on = sum(1 for n in path.nodes if n.type != OFFCURVE)
                test_off = sum(1 for n in path.nodes if n.type == OFFCURVE)

                if (ref_on, ref_off) != (test_on, test_off):
                    mismatch = compare_path_nodes(ref_path, path)
                    if mismatch:
                        index, expected_type, found_type = mismatch
                        expected_str = str(expected_type).replace("1", "LINE").replace("3", "CURVE").replace("4", "QCURVE") if expected_type is not None else "—"
                        found_str = str(found_type).replace("1", "LINE").replace("3", "CURVE").replace("4", "QCURVE") if found_type is not None else "—"
                        print(f"  ⚠️ Incompatibility in master '{master.name}':")
                        print(f"     • Path #{i + 1} mismatch → Expected ({ref_on}, {ref_off}), Found ({test_on}, {test_off})")
                        print(f"     • First difference at node #{index + 1}: Expected {expected_str}, Found {found_str}")
                    else:
                        print(f"  ⚠️ Incompatibility in master '{master.name}': Path #{i + 1} structure mismatch.")
        print("-" * 50)

# Run the report
report_nodes_detailed()
