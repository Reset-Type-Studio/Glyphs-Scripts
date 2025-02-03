# -*- coding: utf-8 -*-
# MenuTitle: 🔢 Values for Smart Components (all masters)
# Version: 1.02
# Description: Assigns values to smart components in selected glyphs for all axes and masters.
# Author: Script by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import Glyphs, GSSmartComponentAxis
import vanilla

class SmartComponentAxesUI:
    """UI for setting axis values in smart components for selected glyphs across all masters."""

    def __init__(self, font):
        self.font = font
        self.axes = font.axes  # Get all axes in the font
        self.master_count = len(self.font.masters)
        self.axis_count = len(self.axes)

        window_height = 80 + (self.master_count * self.axis_count * 37)  # Dynamic window height

        self.w = vanilla.FloatingWindow((260, window_height), "Smart Component Axes Values", minSize=(260, 400), maxSize=(350, 1000))

        self.input_fields = {}

        y_offset = 15  # Y position tracking
        for i, master in enumerate(self.font.masters):
            # Master Label
            setattr(self.w, f"textLabel_master_{i}", vanilla.TextBox((10, y_offset, 240, 17), f"—— Master: {master.name}"))
            y_offset += 20  # Space between the master name and its first axis

            self.input_fields[master.id] = {}
            for j, axis in enumerate(self.axes):
                setattr(self.w, f"textLabel_{i}_{j}", vanilla.TextBox((10, y_offset, 80, 17), f"{axis.name}:"))
                self.input_fields[master.id][axis.name] = vanilla.EditText((100, y_offset - 2, 120, 22))
                setattr(self.w, f"inputField_{i}_{j}", self.input_fields[master.id][axis.name])
                y_offset += 25  # Normal space between axes

            y_offset += 10  # ✅ Adds extra spacing before the next master

        # Create "OK" and "Cancel" buttons
        self.w.okButton = vanilla.Button((10, -35, 85, 0), "OK", callback=self.ok_button_callback)
        self.w.cancelButton = vanilla.Button((100, -35, 85, 0), "Cancel", callback=self.cancel_button_callback)

        self.w.setDefaultButton(self.w.okButton)
        self.w.open()

    def collect_master_axis_values(self):
        """Collects and validates axis values from the UI."""
        master_axis_values = {}
        for master in self.font.masters:
            master_axis_values[master.id] = {}
            for axis in self.axes:
                try:
                    value = float(self.input_fields[master.id][axis.name].get())
                    master_axis_values[master.id][axis.name] = value
                except ValueError:
                    Glyphs.displayDialog(f"❌ Please enter a valid number for {axis.name} in {master.name}.")
                    return None
        return master_axis_values

    def find_component_in_layer(self, layer, name):
        """Finds a specific component by name in a layer."""
        for component in layer.components:
            if component.name == name:
                return component
        return None

    def apply_smart_component_values(self, master_axis_values):
        """Processes selected glyphs and assigns smart component axis values."""
        font = self.font
        selected_layers = [layer for layer in font.selectedLayers if layer.components]
        processed_glyphs = []

        if not selected_layers:
            Glyphs.displayDialog("❌ No components found in selected glyphs.")
            return

        # Collect component names in selected glyphs
        component_names = {component.name for layer in selected_layers for component in layer.components}

        # Find components that are NOT already smart components
        smart_component_names = {name for name in component_names if not font.glyphs[name].smartComponentAxes}

        # Convert components to smart components
        for name in smart_component_names:
            component_glyph = font.glyphs[name]
            for i, axis in enumerate(font.axes):
                axis_values = [m.axes[i] for m in font.masters]
                new_axis = GSSmartComponentAxis()
                new_axis.name = axis.name
                new_axis.bottomValue = min(axis_values)
                new_axis.topValue = max(axis_values)
                component_glyph.smartComponentAxes.append(new_axis)

                for layer in component_glyph.layers:
                    if layer.isMasterLayer:
                        master_value = font.masters[layer.associatedMasterId].axes[i]
                        if master_value == new_axis.bottomValue:
                            layer.smartComponentPoleMapping[component_glyph.smartComponentAxes[new_axis.name].id] = 1
                        if master_value == new_axis.topValue:
                            layer.smartComponentPoleMapping[component_glyph.smartComponentAxes[new_axis.name].id] = 2

        # Assign smart component values for all axes
        for layer in selected_layers:
            for component in layer.components:
                component_glyph = font.glyphs[component.name]
                for master in font.masters:
                    master_layer = layer.parent.layers[master.id]
                    component_master = self.find_component_in_layer(master_layer, component.name)
                    if component_master is not None:
                        for axis in component_glyph.smartComponentAxes:
                            if axis.name in master_axis_values[master.id]:
                                component_master.smartComponentValues[axis.id] = master_axis_values[master.id][axis.name]

            processed_glyphs.append(layer.parent.name)

        # Update the UI
        Glyphs.redraw()
        print(f"✅ {', '.join(processed_glyphs)} now have smart components with specific values for all axes and masters.")

    def ok_button_callback(self, sender):
        """Handles OK button click: validates input and applies axis values."""
        master_axis_values = self.collect_master_axis_values()
        if master_axis_values:
            self.w.close()
            self.apply_smart_component_values(master_axis_values)

    def cancel_button_callback(self, sender):
        """Closes the UI without applying changes."""
        self.w.close()

# Run the UI
if __name__ == "__main__":
    SmartComponentAxesUI(Glyphs.font)
