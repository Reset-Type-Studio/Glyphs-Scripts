# MenuTitle: 🔁 Component Swapper (all masters)
# -*- coding: utf-8 -*-
# Version: 1.2
# Description: Swaps a component in selected glyphs, works in all masters.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import Glyphs
from vanilla import Window, EditText, Button

class SwapComponentsUI:
    """Vanilla UI for swapping components in selected glyphs across all masters."""

    def __init__(self):
        self.w = Window((300, 140), "Swap Components")
        self.w.original_input = EditText((10, 10, -10, 20), placeholder="Original Component")
        self.w.new_input = EditText((10, 40, -10, 20), placeholder="New Component")
        self.w.swap_button = Button((10, 80, -10, 20), "Swap Components", callback=self.swap_callback)
        self.w.status_message = EditText((10, 110, -10, 20), placeholder="Status: Ready", readOnly=True)
        self.w.open()

    def swap_components(self, original_component, new_component):
        """Swaps one component for another in all masters of selected glyphs."""
        font = Glyphs.font
        if not font:
            self.w.status_message.set("⚠️ No font open")
            print("Error: No font open.")
            return

        selected_glyphs = {layer.parent for layer in font.selectedLayers}
        if not selected_glyphs:
            self.w.status_message.set("⚠️ No glyphs selected")
            print("Error: No glyphs selected.")
            return

        found = False
        for thisMaster in font.masters:
            for thisGlyph in selected_glyphs:
                thisLayer = thisGlyph.layers[thisMaster.id]
                for thisComponent in thisLayer.components:
                    if thisComponent.name == original_component:
                        thisComponent.name = new_component
                        found = True
                        print(f"✔ Swapped '{original_component}' → '{new_component}' in '{thisGlyph.name}' ({thisMaster.name})")

        if found:
            Glyphs.redraw()
            self.w.status_message.set("✅ Swap completed")
            print("✔ Component swap completed successfully.")
            self.w.close()
        else:
            self.w.status_message.set("❌ Component not found")
            print(f"Error: Component '{original_component}' not found in selected glyphs.")

    def swap_callback(self, sender):
        """Callback function to execute swap on button press."""
        original = self.w.original_input.get().strip()
        new = self.w.new_input.get().strip()

        if original and new:
            self.swap_components(original, new)
        else:
            self.w.status_message.set("⚠️ Enter both names")
            print("Error: Please enter both component names.")

# Run the UI
SwapComponentsUI()
