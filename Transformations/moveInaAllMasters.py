# -*- coding: utf-8 -*-
# MenuTitle: ↕️ Move Selected Glyphs in All Masters
# Version: 1.02
# Description: Moves the selected glyphs in all masters, both horizontally and vertically (paths+components+anchors).
# Credits: Script by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
import vanilla


# =============================
# Vanilla UI
# =============================

class MoveGlyphsInAllMasters:
    
    def __init__(self):
        """Initialize the user interface."""

        # Window settings
        windowWidth  = 270
        windowHeight = 160  
        self.w = vanilla.FloatingWindow(
            (windowWidth, windowHeight),  
            "Move in all Masters", 
            minSize=(windowWidth, windowHeight),
            maxSize=(1000, 160),
            autosaveName="com.MoveGlyphsInAllMasters.mainwindow"
        )
        
        # Move X input field
        self.w.textX = vanilla.TextBox((15, 14, 70, 14), "Move X:", sizeStyle='small')
        self.w.valueInputX = vanilla.EditText((85, 12, 70, 20), "0", sizeStyle='small', callback=self.textInputCallback)

        # Move Y input field
        self.w.textY = vanilla.TextBox((15, 42, 70, 14), "Move Y:", sizeStyle='small')
        self.w.valueInputY = vanilla.EditText((85, 40, 70, 20), "0", sizeStyle='small', callback=self.textInputCallback)
        
        # Move and Close Buttons
        self.w.runButton = vanilla.Button((15, -50, 65, -30), "Move", sizeStyle='small', callback=self.MoveButtonCallback)
        self.w.closeButton = vanilla.Button((85, -50, 70, -30), "Close", sizeStyle='small', callback=self.closeWindow)

        # Status Message
        self.w.statusText = vanilla.TextBox((15, -25, -15, 20), "Ready", sizeStyle='small')
        
        # Set the "Move" button as the default action
        self.w.setDefaultButton(self.w.runButton)
        
        # Open the window and bring it to the front
        self.w.open()
        self.w.makeKey()
        

# =============================
# Functions Section
# =============================

    def textInputCallback(self, sender):
        """Ensure that the user input is a valid number."""

        # Allow negative values and empty input while typing
        value = sender.get()
        if value == "-" or value == "":
            return  # Allow "-" or empty value while typing

        # Try converting input to float; reset to "0" if invalid
        try:
            float(value)  # Validate number
        except ValueError:
            sender.set("0")  # Reset to "0" if input is invalid

        
    def MoveButtonCallback(self, sender):
        """Move selected glyphs by specified X and Y values in all masters."""        

        font = Glyphs.font  # Get the current font
        deltaX = float(self.w.valueInputX.get())  # Get movement value for X
        deltaY = float(self.w.valueInputY.get())  # Get movement value for Y

        # If no font is open, display an error message
        if not font:
            self.w.statusText.set("No font opened.")
            return

        # If no glyphs are selected, display an error message
        selectedGlyphs = [layer.parent for layer in font.selectedLayers]
        if not selectedGlyphs:
            self.w.statusText.set("No glyphs selected.")
            return

        # Move each selected glyph in all masters
        for glyph in selectedGlyphs:
            for layer in glyph.layers:

                for path in layer.paths: # Move paths (outlines)
                    for node in path.nodes:
                        node.x += deltaX
                        node.y += deltaY

                for component in layer.components: # Move components (disable auto-alignment first)
                    component.automaticAlignment = False  # Disable auto-alignment before moving
                    component.x += deltaX
                    component.y += deltaY

                for anchor in layer.anchors: # Move anchors (e.g., baseline marks)
                    anchor.x += deltaX
                    anchor.y += deltaY

        # Refresh the UI to show changes
        Glyphs.redraw()
        
        # Update the status message to confirm movement
        message = f"Moved {len(selectedGlyphs)} glyph(s) by {deltaX} in X, {deltaY} in Y."
        self.w.statusText.set(message)

    def closeWindow(self, sender):
        """Close the plugin window."""
        self.w.close()

# =============================
# Run
# =============================

MoveGlyphsInAllMasters()
