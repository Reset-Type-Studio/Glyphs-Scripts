# MenuTitle: 📄 Report Glyphs containing Bracket Layers
# -*- coding: utf-8 -*-
# Version: 1.4
# Description: Lists glyphs with bracket layers and all affected glyphs, including nested components, in a scrollable Vanilla window with optimized performance.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
from collections import deque, defaultdict
from vanilla import Window, TextEditor


def checkBracketLayers(thisGlyph):
    """Check if a glyph has any bracket layers efficiently."""
    return any("[" in thisLayer.name and "]" in thisLayer.name for thisLayer in thisGlyph.layers)


def collectBracketLayerGlyphs(thisFont):
    """Return a set of glyph names that contain bracket layers."""
    return {thisGlyph.name for thisGlyph in thisFont.glyphs if checkBracketLayers(thisGlyph)}


def createComponentMapping(thisFont):
    """Create a mapping of glyphs to the glyphs that use them as components."""
    glyphToComponentsMap = defaultdict(set)
    
    for thisGlyph in thisFont.glyphs:
        for thisLayer in thisGlyph.layers:
            for thisComponent in thisLayer.components:
                glyphToComponentsMap[thisComponent.componentName].add(thisGlyph.name)
    
    return glyphToComponentsMap


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


class BracketLayerReport:
    def __init__(self, thisFont):
        """Initialize the report by identifying glyphs with bracket layers and affected components."""
        self.thisFont = thisFont
        self.setBracketGlyphs = collectBracketLayerGlyphs(thisFont)
        dictGlyphToComponents = createComponentMapping(thisFont)
        self.setComponentGlyphs = identifyAffectedGlyphs(self.setBracketGlyphs, dictGlyphToComponents)
        
        # Total number of affected glyphs (bracket glyphs + components using them)
        self.intTotalAffectedGlyphs = len(self.setBracketGlyphs) + len(self.setComponentGlyphs)
        self.createWindow()

    def createWindow(self):
        """Create and display the Vanilla UI window containing the report."""
        self.uiWindow = Window((500, 400), "Bracket Layer Report", minSize=(500, 400))
        
        strReportText = (
            f"Glyphs with Bracket Layers ({len(self.setBracketGlyphs)}):\n"
            + ", ".join(sorted(self.setBracketGlyphs)) +
            f"\n\nAffected Components ({len(self.setComponentGlyphs)}):\n"
            + ", ".join(sorted(self.setComponentGlyphs)) +
            f"\n\nTotal affected glyphs: {self.intTotalAffectedGlyphs}"
        )
        
        # Display the report in a scrollable, read-only text field
        self.uiWindow.report = TextEditor((10, 10, -10, -10), strReportText, readOnly=True)
        
        self.uiWindow.open()


# Main Execution
thisFont = Glyphs.font  # Access the currently open font in Glyphs
if not thisFont:
    print("--- ERROR: No font is open. Please open a font and try again.")
else:
    BracketLayerReport(thisFont)
