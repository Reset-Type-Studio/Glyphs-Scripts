# -*- coding: utf-8 -*-
# MenuTitle: 🤯 Selected to Normal Components 

selectedGlyphs = [g.parent for g in Font.selectedLayers if any(c for c in g.components)]
processedGlyphs = []

# Collect component names for all selected glyphs
componentNames = set()
for glyph in selectedGlyphs:
    for component in glyph.layers[0].components:
        if component.componentName in Font.glyphs:
            componentGlyph = Font.glyphs[component.componentName]
            componentNames.add(componentGlyph.name)

# Remove smart components for each used component
for name in componentNames:
    componentGlyph = Font.glyphs[name]
    if componentGlyph.smartComponentAxes:
        # Create a new glyph without smart components
        newGlyph = componentGlyph.copy()
        newGlyph.smartComponentAxes = []
        for layer in newGlyph.layers:
            if layer.isMasterLayer:
                layer.layerId = str(layer.layerId) + "_non-smart"

        # Replace the old glyph with the new one
        Font.glyphs[newGlyph.name] = newGlyph
        processedGlyphs.append(newGlyph.name)

# Renew selection in order to hide smart glyph controls
for glyph in selectedGlyphs:
    glyph.selected = False
    glyph.selected = True

print('%s smart components have been turned off.' % len(processedGlyphs))