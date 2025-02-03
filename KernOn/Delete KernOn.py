# -*- coding: utf-8 -*-
# MenuTitle: 🧨 Delete KernOn
# Version: 1.0
# Description: This script clears all kerning pairs and resets kerning groups in Glyphs.
# Author: Developed by Fernando Díaz (Reset Type Studio) with help from AI.

# Get the current font
thisFont = Glyphs.font

if not thisFont:
    print("--- ERROR: No font is open. Please open a font and try again.")
else:
    # Step 1: Clear kerning groups for each glyph
    for thisGlyph in thisFont.glyphs:
        thisGlyph.leftKerningGroup = None
        thisGlyph.rightKerningGroup = None

    # Step 2: Clear all kerning pairs for each master
    for thisMaster in thisFont.masters:
        thisFont.kerning[thisMaster.id] = {}

    # Notify that the process is complete
    Glyphs.showNotification(
        "Kern On Reset",
        "All kerning pairs and groups have been deleted."
    )

    print("--- All kerning pairs and groups have been deleted.")