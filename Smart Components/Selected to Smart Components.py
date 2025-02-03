# -*- coding: utf-8 -*-
# MenuTitle: 🧠 Selected to Smart Components (all masters)
# Version: 1.01
# Description: Converts selected glyphs into smart components based on font master axes.
# Author: Script by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import Glyphs, GSSmartComponentAxis

def collect_component_names(selected_layers):
    """Collects unique component names from the selected glyphs."""
    return {component.name for layer in selected_layers for component in layer.components}

def find_non_smart_components(font, component_names):
    """Finds components that are NOT already smart components."""
    return {name for name in component_names if not font.glyphs[name].smartComponentAxes}

def create_smart_components(font, smart_component_names):
    """Creates smart components for glyphs that are not already smart."""
    for name in smart_component_names:
        componentGlyph = font.glyphs[name]
        for i, axis in enumerate(font.axes):
            axisValues = [m.axes[i] for m in font.masters]
            newAxis = GSSmartComponentAxis()
            newAxis.name = axis.name
            newAxis.bottomValue = min(axisValues)
            newAxis.topValue = max(axisValues)
            componentGlyph.smartComponentAxes.append(newAxis)

            for layer in componentGlyph.layers:
                if layer.isMasterLayer:
                    master_value = font.masters[layer.associatedMasterId].axes[i]
                    if master_value == newAxis.bottomValue:
                        layer.smartComponentPoleMapping[componentGlyph.smartComponentAxes[newAxis.name].id] = 1
                    if master_value == newAxis.topValue:
                        layer.smartComponentPoleMapping[componentGlyph.smartComponentAxes[newAxis.name].id] = 2

def assign_smart_component_values(selected_layers, smart_component_names, font):
    """Assigns smart component values to components in selected glyphs."""
    processedGlyphs = []
    for layer in selected_layers:
        for component in layer.components:
            if component.name in smart_component_names:
                if not component.smartComponentValues:
                    processedGlyphs.append(layer.parent.name)
    
    return processedGlyphs

def main():
    font = Glyphs.font
    if not font:
        print("❌ No font open.")
        return

    selected_layers = [layer for layer in font.selectedLayers if len(layer.components) > 0]
    
    if not selected_layers:
        print("❌ No components found in selected glyphs.")
        return

    component_names = collect_component_names(selected_layers)
    smart_component_names = find_non_smart_components(font, component_names)

    if not smart_component_names:
        print("⚠️ No new smart components to create.")
        return

    create_smart_components(font, smart_component_names)
    processedGlyphs = assign_smart_component_values(selected_layers, smart_component_names, font)

    if processedGlyphs:
        print(f"✅ {', '.join(processedGlyphs)} are now smart components.")
    else:
        print("⚠️ No components were converted to smart components.")

    Glyphs.redraw()

# Run the script
main()
