# -*- coding: utf-8 -*-
# MenuTitle: 🤯 Smart to Normal Components (all masters)
# Version: 1.1
# Description: Converts selected smart components back to normal components.
# Author: Script by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import Glyphs

def find_smart_components(font, selected_layers):
    """Finds all smart components in the selected glyphs."""
    smart_components = set()
    for layer in selected_layers:
        for component in layer.components:
            component_glyph = font.glyphs[component.name]
            if component_glyph and component_glyph.smartComponentAxes:
                smart_components.add(component.name)
    return smart_components

def remove_smart_settings(font, smart_components):
    """Removes smart component axes and pole mappings from selected smart components."""
    processed_glyphs = []
    for name in smart_components:
        component_glyph = font.glyphs[name]
        if component_glyph and component_glyph.smartComponentAxes:
            component_glyph.smartComponentAxes = []  # Remove smart component axes
            for layer in component_glyph.layers:
                if hasattr(layer, "smartComponentPoleMapping") and layer.smartComponentPoleMapping:
                    layer.smartComponentPoleMapping.clear() 
            processed_glyphs.append(name)
    
    return processed_glyphs

def main():
    font = Glyphs.font
    if not font:
        print("❌ No font open.")
        return

    selected_layers = [layer for layer in font.selectedLayers if layer.components]
    
    if not selected_layers:
        print("❌ No components found in selected glyphs.")
        return

    smart_components = find_smart_components(font, selected_layers)

    if not smart_components:
        print("⚠️ No smart components found in selected glyphs.")
        return

    processed_glyphs = remove_smart_settings(font, smart_components)

    if processed_glyphs:
        print(f"✅ {len(processed_glyphs)} smart components have been converted to normal components: {', '.join(processed_glyphs)}.")
    else:
        print("⚠️ No changes were made.")

    Glyphs.redraw()


# Run the script
main()
