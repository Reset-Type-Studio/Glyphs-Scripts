# MenuTitle: 🛠️ Transformations Tool (for All Masters)
# -*- coding: utf-8 -*-
# Version: 1.03
# Description: Transformations tools but for all Master
# Author: Script by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
import vanilla
import math
from AppKit import NSAffineTransform

class TransformGlyphsInAllMasters:
    
    def __init__(self):
        """Initialize the user interface for transformation settings."""
        intWindowWidth = 180
        intWindowHeight = 280  
        
        self.uiWindow = vanilla.FloatingWindow(
            (intWindowWidth, intWindowHeight),  
            "Transform in All Masters", 
            minSize=(intWindowWidth, intWindowHeight),
            autosaveName="com.TransformGlyphsInAllMasters.mainwindow"
        )

        # Translate X
        self.uiWindow.txtTranslateX = vanilla.TextBox((20, 22, 80, 22), "Translate X", sizeStyle='regular')
        self.uiWindow.inputTranslateX = vanilla.EditText((100, 20, 60, 22), "0", sizeStyle='regular')

        # Translate Y
        self.uiWindow.txtTranslateY = vanilla.TextBox((20, 52, 80, 22), "Translate Y", sizeStyle='regular')
        self.uiWindow.inputTranslateY = vanilla.EditText((100, 50, 60, 22), "0", sizeStyle='regular')

        # Scale
        self.uiWindow.txtScale = vanilla.TextBox((20, 82, 80, 22), "Scale (%)", sizeStyle='regular')
        self.uiWindow.inputScale = vanilla.EditText((100, 80, 60, 22), "100", sizeStyle='regular')

        # Rotate
        self.uiWindow.txtRotate = vanilla.TextBox((20, 112, 80, 22), "Rotate (°)", sizeStyle='regular')
        self.uiWindow.inputRotate = vanilla.EditText((100, 110, 60, 22), "0", sizeStyle='regular')

        # Slant
        self.uiWindow.txtSlant = vanilla.TextBox((20, 142, 80, 22), "Slant (°)", sizeStyle='regular')
        self.uiWindow.inputSlant = vanilla.EditText((100, 140, 60, 22), "0", sizeStyle='regular')

        # Apply Button
        self.uiWindow.btnApply = vanilla.Button((20, 190, 140, 22), "Apply", callback=self.applyTransformations)
        self.uiWindow.btnApply.getNSButton().setKeyEquivalent_("\r")

        # Close Button
        self.uiWindow.btnClose = vanilla.Button((20, 220, 140, 22), "Close", callback=self.cancel)

        self.uiWindow.open()  # Open window
        self.uiWindow.makeKey()  # Bring window to front

    def getValidNumber(self, strValue, floatDefault):
        """Converts input to float if valid, otherwise returns the default value."""
        try:
            return float(strValue)
        except ValueError:
            return floatDefault

    def cancel(self, sender):
        """Closes the window when the Close button is clicked."""
        self.uiWindow.close()

    def applyTransformations(self, sender):
        """Applies transformations to selected glyphs across all masters."""
        thisFont = Glyphs.font
        listSelectedGlyphs = [thisLayer.parent for thisLayer in thisFont.selectedLayers]

        # Validate input values
        floatMoveX = self.getValidNumber(self.uiWindow.inputTranslateX.get(), 0)
        floatMoveY = self.getValidNumber(self.uiWindow.inputTranslateY.get(), 0)
        floatScale = self.getValidNumber(self.uiWindow.inputScale.get(), 100) / 100.0
        floatRotate = self.getValidNumber(self.uiWindow.inputRotate.get(), 0)  # Clockwise
        floatSlant = math.tan(math.radians(self.getValidNumber(self.uiWindow.inputSlant.get(), 0)))  # Horizontal skew

        for thisGlyph in listSelectedGlyphs:
            for thisLayer in thisGlyph.layers:
                # Compute the center of the glyph using bounds
                rectBounds = thisLayer.bounds
                floatCenterX = rectBounds.origin.x + (rectBounds.size.width / 2)
                floatCenterY = rectBounds.origin.y + (rectBounds.size.height / 2)

                # Move glyph to (0,0) before applying transformations
                listMoveToOrigin = [
                    1, 0, 0, 1,
                    -floatCenterX, -floatCenterY
                ]
                thisLayer.applyTransform(listMoveToOrigin)

                # Apply rotation first, centered on (0,0)
                if floatRotate != 0:
                    objRotationMatrix = NSAffineTransform.alloc().init()
                    objRotationMatrix.rotateByDegrees_(-floatRotate)  # Clockwise rotation
                    thisLayer.applyTransform(objRotationMatrix.transformStruct())

                # Initialize transformation matrix with default values (identity matrix)
                listTransformMatrix = [1, 0, 0, 1, 0, 0]

                # Apply Scale
                if floatScale != 1.0:
                    listTransformMatrix[0] = floatScale  # Scale X
                    listTransformMatrix[3] = floatScale  # Scale Y

                # Apply Slant (only horizontal skew)
                if floatSlant != 0:
                    listTransformMatrix[2] = floatSlant  # Skew X

                # Apply Move
                if floatMoveX != 0:
                    listTransformMatrix[4] = floatMoveX  # Move X
                if floatMoveY != 0:
                    listTransformMatrix[5] = floatMoveY  # Move Y

                # Apply the final transformation matrix to the layer (if modified)
                if listTransformMatrix != [1, 0, 0, 1, 0, 0]:  # Only apply if not an identity matrix
                    thisLayer.applyTransform(listTransformMatrix)

                # Move the glyph back to its original position
                listMoveBackMatrix = [
                    1, 0, 0, 1,
                    floatCenterX, floatCenterY
                ]
                thisLayer.applyTransform(listMoveBackMatrix)

        Glyphs.redraw()  # Ensure UI updates

# Run the UI
TransformGlyphsInAllMasters()
