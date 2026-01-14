# MenuTitle: 🖥️ New Tab with Glyphs containing Bracket Layers
# -*- coding: utf-8 -*-
# Version: 1.4
# Description: Opens a new tab with glyphs containing bracket layers, followed by glyphs using these as components.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
from collections import deque, defaultdict


def checkBracketLayers(thisGlyph):
    """Check if a glyph has any bracket layers efficiently."""
    return any("[" in thisLayer.name and "]" in thisLayer.name for thisLayer in thisGlyph.layers)


def collectBracketLayerGlyphs(thisFont):
    """Return a set of glyph names that contain bracket layers."""
    return {thisGlyph.name for thisGlyph in thisFont.glyphs if checkBracketLayers(thisGlyph)}


def createComponentMapping(thisFont):
    """Create a mapping of glyphs to the glyphs that use them as components."""
    dictGlyphToComponents = defaultdict(set)
    
    for thisGlyph in thisFont.glyphs:
        for thisLayer in thisGlyph.layers:
            for thisComponent in thisLayer.components:
                if thisComponent.componentName:
                    dictGlyphToComponents[thisComponent.componentName].add(thisGlyph.name)
    
    return dictGlyphToComponents


def identifyAffectedGlyphs(setGlyphNames, dictGlyphToComponents):
    """Find all glyphs that use any of the given glyphs as components using a queue."""
    setAffectedGlyphs = set()
    dequeQueue = deque(setGlyphNames)
    
    while dequeQueue:
        strCurrentGlyph = dequeQueue.popleft()
        for strDependentGlyph in dictGlyphToComponents.get(strCurrentGlyph, []):
            if strDependentGlyph not in setAffectedGlyphs:
                setAffectedGlyphs.add(strDependentGlyph)
                dequeQueue.append(strDependentGlyph)  # Add newly found components to be processed
    
    return setAffectedGlyphs


def openBracketLayerGlyphs():
    """Opens a new tab in Glyphs with bracket-layered glyphs and their components."""
    thisFont = Glyphs.font
    if not thisFont:
        print("--- ERROR: No font is open. Please open a font and try again.")
        return

    # Find bracket-layered glyphs and build the component dependency map
    setBracketGlyphs = collectBracketLayerGlyphs(thisFont)
    dictGlyphToComponents = createComponentMapping(thisFont)

    # Find all components that reference bracket-layered glyphs (including nested)
    setComponentGlyphs = identifyAffectedGlyphs(setBracketGlyphs, dictGlyphToComponents)

    # Sort glyph names
    listAllGlyphs = sorted(setBracketGlyphs) + sorted(setComponentGlyphs)

    # Open a new tab if there are glyphs to show
    if listAllGlyphs:
        thisFont.newTab("Glyphs:\n/" + "/".join(setBracketGlyphs) + "\n\nComponents:\n/" + "/".join(setComponentGlyphs))
    else:
        print("No bracket-layered glyphs or components found.")


# Main Execution
if __name__ == "__main__":
    thisFont = Glyphs.font  
    if not thisFont:
        print("--- ERROR: No font is open. Please open a font and try again.")
    else:
        openBracketLayerGlyphs()
