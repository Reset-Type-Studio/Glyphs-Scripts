#MenuTitle: Move Selected Glyphs Vertically in All Masters
# -*- coding: utf-8 -*-

__doc__="""
Adjusts the y position of the selected glyphs in all masters.
"""

from GlyphsApp import *
import vanilla

class MoveSelectedGlyphsVertically:
    
    def __init__(self):
        # Window 'self.w':
        windowWidth  = 230
        windowHeight = 70
        windowWidthResize  = 230  # adjusted this to match initial size
        windowHeightResize = 70   # adjusted this to match initial size
        self.w = vanilla.FloatingWindow(
            (windowWidth, windowHeight),  # default window size
            "Move Selected Glyphs",      # window title
            minSize = (windowWidthResize, windowHeightResize), # minimum size (for resizing)
            maxSize = (1000, 400), # maximum size (for resizing)
            autosaveName = "com.MoveSelectedGlyphs.mainwindow" # stores last window position and size
        )
        
        # UI Elements
        self.w.text = vanilla.TextBox((15, 12+2, 67, 14), "Move by (y):", sizeStyle='small')
        self.w.valueInput = vanilla.EditText((85, 12, 70, 20), "0", sizeStyle='small', callback=self.textInputCallback)
        
        # Run Button
        self.w.runButton = vanilla.Button((-80, -20, -15, -15), "Move", sizeStyle='small', callback=self.MoveButtonCallback)
        self.w.setDefaultButton(self.w.runButton)
        
        # Open window and focus on it:
        self.w.open()
        self.w.makeKey()
        
    def textInputCallback(self, sender):
        # Just to make sure input is a number
        try:
            float(sender.get())
        except:
            sender.set("0")
        
    def MoveButtonCallback(self, sender):
        font = Glyphs.font
        deltaY = float(self.w.valueInput.get())

        if not font:
            print("No font opened.")
            return

        selectedGlyphs = [layer.parent for layer in font.selectedLayers]
        if not selectedGlyphs:
            print("No glyphs selected.")
            return
        
        for glyph in selectedGlyphs:
            for layer in glyph.layers:
                for path in layer.paths:
                    for node in path.nodes:
                        node.y += deltaY

                for component in layer.components:
                    component.y += deltaY
                
                for anchor in layer.anchors:
                    anchor.y += deltaY

        # Update
        font.update()
        print(f"Moved {len(selectedGlyphs)} glyph(s) by {deltaY} units in y direction across all masters.")

# Run the class
MoveSelectedGlyphsVertically()
