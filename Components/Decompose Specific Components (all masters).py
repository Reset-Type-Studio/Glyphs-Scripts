# MenuTitle: ⛓️‍💥 Decompose Specific Components (all masters)
# -*- coding: utf-8 -*-
# Version: 1.4
# Description: Decomposes only the specified component (and nested components) in all masters.
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import Glyphs
from vanilla import Window, EditText, Button, TextBox

class SmartDecomposeComponentsUI:
    """Vanilla UI for decomposing a selected component and its nested components inside the glyph."""

    def __init__(self):
        self.w = Window((320, 180), "Smart Component Swapper", minSize=(320, 180), maxSize=(320, 180))

        # UI Elements
        self.w.label = TextBox((10, 10, -10, 20), "Component to Decompose:")
        self.w.component_input = EditText((10, 30, -10, 20), placeholder="Enter component name")

        self.w.decompose_button = Button((10, 70, -10, 30), "Decompose Component", callback=self.decompose_callback)
        self.w.status_message = TextBox((10, 110, -10, 20), "Status: Ready", sizeStyle="small")

        self.w.open()
        self.w.makeKey()  # Ensures the window stays on top

    def get_nested_components(self, font, component_name):
        """Returns a set of all nested components inside the given component."""
        nested_components = set()
        component_glyph = font.glyphs[component_name]
        if component_glyph:
            for layer in component_glyph.layers:
                for sub_component in layer.components:
                    nested_components.add(sub_component.name)
        return nested_components

    def decompose_smart(self, font, component_to_decompose):
        """Decomposes the specified component and its nested components inside the glyph, keeping all others intact."""
        if not font:
            self.w.status_message.set("⚠️ No font open")
            print("Error: No font open.")
            return

        selected_glyphs = {layer.parent for layer in font.selectedLayers}
        if not selected_glyphs:
            self.w.status_message.set("⚠️ No glyphs selected")
            print("Error: No glyphs selected.")
            return

        # Collect all component names in the font
        all_components = {comp.name for glyph in font.glyphs for layer in glyph.layers for comp in layer.components}

        if component_to_decompose not in all_components:
            self.w.status_message.set(f"❌ '{component_to_decompose}' not found")
            print(f"Error: Component '{component_to_decompose}' does not exist in the font.")
            return

        # **Find nested components inside the component_to_decompose**
        nested_components = self.get_nested_components(font, component_to_decompose)

        found = False
        for thisMaster in font.masters:
            for thisGlyph in selected_glyphs:
                thisLayer = thisGlyph.layers[thisMaster.id]

                # **Step 1: Decompose the main component (component_to_decompose)**
                for i in reversed(range(len(thisLayer.components))):  # Reverse to avoid index errors
                    thisComponent = thisLayer.components[i]
                    if thisComponent.name == component_to_decompose:
                        thisLayer.decomposeComponent_(thisComponent)
                        found = True
                        print(f"✔ Decomposed '{thisComponent.name}' in '{thisGlyph.name}' ({thisMaster.name})")

                # **Step 2: If that component had nested components, decompose them inside the glyph**
                for i in reversed(range(len(thisLayer.components))):  
                    thisComponent = thisLayer.components[i]
                    if thisComponent.name in nested_components:
                        thisLayer.decomposeComponent_(thisComponent)
                        found = True
                        print(f"✔ Decomposed nested '{thisComponent.name}' in '{thisGlyph.name}' ({thisMaster.name})")

        if found:
            Glyphs.redraw()
            self.w.status_message.set("✅ Smart Decomposition completed!")
            print(f"✔ Successfully decomposed '{component_to_decompose}' and its nested components.")
            self.w.close()  
        else:
            self.w.status_message.set("❌ No matching components found")
            print(f"Warning: Component '{component_to_decompose}' was not found in selected glyphs.")

    def decompose_callback(self, sender):
        """Callback function to execute smart decomposition on button press."""
        component_to_decompose = self.w.component_input.get().strip()
        self.decompose_smart(Glyphs.font, component_to_decompose)

# Run the UI
SmartDecomposeComponentsUI()
