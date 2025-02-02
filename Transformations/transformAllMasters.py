# -*- coding: utf-8 -*-
# MenuTitle: 🛠️ Transformations in All Masters
# Version: 2.2
# Description: Transformations tools but for all Master
# Credits: Based on script by Fernando Díaz (Reset Type Studio) 

from GlyphsApp import *
import vanilla
import math

class TransformGlyphsInAllMasters:
    
    def __init__(self):
        """Initialize the user interface with placeholders."""
        windowWidth = 180
        windowHeight = 280  
        self.w = vanilla.FloatingWindow(
            (windowWidth, windowHeight),  
            "Transform in All Masters", 
            minSize=(windowWidth, windowHeight),
            autosaveName="com.TransformGlyphsInAllMasters.mainwindow"
        )

        # Translate
        self.w.textX = vanilla.TextBox((20, 22, 80, 22), "Translate x", sizeStyle='regular')
        self.w.inputX = vanilla.EditText((100, 20, 60, 22), "0", sizeStyle='regular')
        # Translate
        self.w.textY = vanilla.TextBox((20, 52, 80, 22), "Translate y", sizeStyle='regular')
        self.w.inputY = vanilla.EditText((100, 50, 60, 22), "0", sizeStyle='regular')
        # Scale
        self.w.textScale = vanilla.TextBox((20, 82, 80, 22), "Scale (%)", sizeStyle='regular')
        self.w.inputScale = vanilla.EditText((100, 80, 60, 22), "100", sizeStyle='regular')
        # Rotate
        self.w.textRotate = vanilla.TextBox((20, 112, 80, 22), "Rotate (°)", sizeStyle='regular')
        self.w.inputRotate = vanilla.EditText((100, 110, 60, 22), "0", sizeStyle='regular')
        # Slant
        self.w.textSlant = vanilla.TextBox((20, 142, 80, 22), "Slant (°)", sizeStyle='regular')
        self.w.inputSlant = vanilla.EditText((100, 140, 60, 22), "0", sizeStyle='regular')
        # Apply
        self.w.applyButton = vanilla.Button((20, 190, 140, 22), "Apply", callback=self.applyTransformations)
        self.w.applyButton.getNSButton().setKeyEquivalent_("\r")
        # Close
        self.w.cancelButton = vanilla.Button((20, 220, 140, 22), "Close", callback=self.cancel)

        self.w.open() # Open window
        self.w.makeKey()  # Bring window to front


    def get_valid_number(self, value, default):
        """Converts input to float if valid, otherwise returns the default value."""
        try:
            return float(value)
        except ValueError:
            return default

    def cancel(self, sender):
        """Closes the window when the Cancel button is clicked."""
        self.w.close()

    def applyTransformations(self, sender):
        """Applies the transformations to selected glyphs across all masters."""
        font = Glyphs.font
        selected_glyphs = [l.parent for l in font.selectedLayers]

        # Validate inputs
        move_x = self.get_valid_number(self.w.inputX.get(), 0)
        move_y = self.get_valid_number(self.w.inputY.get(), 0)
        scale = self.get_valid_number(self.w.inputScale.get(), 100) / 100.0
        rotate = self.get_valid_number(self.w.inputRotate.get(), 0)  # Clockwise
        slant = math.tan(math.radians(self.get_valid_number(self.w.inputSlant.get(), 0)))  # Horizontal skew

        for glyph in selected_glyphs:
            for layer in glyph.layers:
                # Find the exact center of the glyph using bounds
                layer_bounds = layer.bounds
                center_x = layer_bounds.origin.x + (layer_bounds.size.width / 2)
                center_y = layer_bounds.origin.y + (layer_bounds.size.height / 2)

                # Move the glyph to (0,0) before applying transformations
                moveToOriginMatrix = [
                    1, 0, 0, 1,
                    -center_x, -center_y
                ]
                layer.applyTransform(moveToOriginMatrix)

                # Apply rotation first, centered on (0,0)
                if rotate != 0:
                    rotationMatrix = NSAffineTransform.alloc().init()
                    rotationMatrix.rotateByDegrees_(-rotate)  # Clockwise rotation
                    layer.applyTransform(rotationMatrix.transformStruct())

                # Initialize transformation matrix with default values
                transformMatrix = [1, 0, 0, 1, 0, 0]  # Identity matrix (no transformation)

                # Apply Scale
                if scale != 1.0:
                    transformMatrix[0] = scale  # Scale X
                    transformMatrix[3] = scale  # Scale Y

                # Apply Slant (only horizontal skew)
                if slant != 0:
                    transformMatrix[2] = slant  # Skew X

                # Apply Move
                if move_x != 0:
                    transformMatrix[4] = move_x  # Move X
                if move_y != 0:
                    transformMatrix[5] = move_y  # Move Y

                # Apply the final transformation matrix to the layer (if modified)
                if transformMatrix != [1, 0, 0, 1, 0, 0]:  # Only apply if not identity matrix
                    layer.applyTransform(transformMatrix)

                # Move the glyph back to its original position
                moveBackMatrix = [
                    1, 0, 0, 1,
                    center_x, center_y
                ]
                layer.applyTransform(moveBackMatrix)

        Glyphs.redraw()  # Ensure UI updates

# Run the UI
TransformGlyphsInAllMasters()
