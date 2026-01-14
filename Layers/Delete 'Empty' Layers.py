# MenuTitle: 🕳️ Delete (empty) Layers
# -*- coding: utf-8 -*-
# Version: 1.2
# Description: Deletes "(empty)"" layers that might brake other scripts
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from vanilla import Window, TextBox
import GlyphsApp

font = Glyphs.font
deletedLayersCount = 0

for thisGlyph in font.glyphs:
    layersToDelete = []
    for thisLayer in thisGlyph.layers:
        if thisLayer.name is None and not thisLayer.isMasterLayer:
            layersToDelete.append(thisLayer)
    for thisLayer in layersToDelete:
        thisGlyph.layers.remove(thisLayer)
        deletedLayersCount += 1

# Display result in floating window
class DeleteEmptyLayersReport:
    def __init__(self):
        self.w = Window((300, 60), "Delete Empty Layers", minSize=(300, 60), maxSize=(500, 100))
        self.w.resultText = TextBox((15, 15, -15, 20), f"Deleted {deletedLayersCount} 'Empty' layers.")
        self.w.open()

DeleteEmptyLayersReport()