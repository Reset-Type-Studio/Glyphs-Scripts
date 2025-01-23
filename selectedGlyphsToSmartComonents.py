# -*- coding: utf-8 -*-
# MenuTitle: 🧠 Selected to Smart Components 

selectedGlyphs = [g for g in Font.selectedLayers if len(g.components) > 0]
processedGlyphs = []

# Collect component names for all selected glyphs
componentNames = {component.name for layer in selectedGlyphs for component in layer.components}

# Check if any components are already smart
smartComponentNames = {name for name in componentNames if not Font.glyphs[name].smartComponentAxes}

# Create smart components for each new component
for name in smartComponentNames:
    componentGlyph = Font.glyphs[name]
    for i, axis in enumerate(Font.axes):
        axisValues = [m.axes[i] for m in Font.masters]
        newAxis = GSSmartComponentAxis()
        newAxis.name = axis.name
        newAxis.bottomValue = min(axisValues)
        newAxis.topValue = max(axisValues)
        componentGlyph.smartComponentAxes.append(newAxis)

        for layer in componentGlyph.layers:
            if layer.isMasterLayer:
                master_value = Font.masters[layer.associatedMasterId].axes[i]
                if master_value == newAxis.bottomValue:
                    layer.smartComponentPoleMapping[componentGlyph.smartComponentAxes[newAxis.name].id] = 1
                if master_value == newAxis.topValue:
                    layer.smartComponentPoleMapping[componentGlyph.smartComponentAxes[newAxis.name].id] = 2

# Assign smart component values to each component
for layer in selectedGlyphs:
    for component in layer.components:
        if component.name in smartComponentNames:
            if not component.smartComponentValues:
                componentGlyph = Font.glyphs[component.name]

    processedGlyphs.append(layer.parent.name)

print(f'{", ".join(processedGlyphs)} are now smart components.')
