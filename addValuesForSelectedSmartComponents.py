# -*- coding: utf-8 -*-
# MenuTitle: 🔢 Values for Smart Components 

import vanilla

class MasterWeightValuesDialog:
    def __init__(self, font):
        self.font = font

        # Set up the window
        self.w = vanilla.FloatingWindow((210, 60 + len(self.font.masters) * 25), "Master Weight Values")

        # Create input fields for each master
        self.input_fields = []
        for i, master in enumerate(self.font.masters):
            setattr(self.w, f'textLabel_{i}', vanilla.TextBox((10, 15 + i * 25, 80, 17), f"{master.name}:"))
            setattr(self.w, f'inputField_{i}', vanilla.EditText((100, 12 + i * 25, 100, 22)))
            self.input_fields.append(getattr(self.w, f'inputField_{i}'))

        # Create "OK" and "Cancel" buttons
        self.w.okButton = vanilla.Button((-110, -30, 40, 20), "OK", callback=self.ok_button_callback)
        self.w.cancelButton = vanilla.Button((-70, -30, 60, 20), "Cancel", callback=self.cancel_button_callback)

        self.w.setDefaultButton(self.w.okButton)
        self.w.open()

    def ok_button_callback(self, sender):
        master_weight_values = {}
        for i, master in enumerate(self.font.masters):
            try:
                value = float(self.input_fields[i].get())
                master_weight_values[master.id] = value
            except ValueError:
                Glyphs.displayDialog(f"Please enter a valid number for {master.name}.")

        if len(master_weight_values) == len(self.font.masters):
            self.w.close()

            ###################

            def find_component_in_layer(layer, name):
                for component in layer.components:
                    if component.name == name:
                        return component
                return None

            selectedGlyphs = [g for g in Font.selectedLayers if len(g.components) > 0]
            processedGlyphs = []

            componentNames = {component.name for layer in selectedGlyphs for component in layer.components}
            smartComponentNames = {name for name in componentNames if not Font.glyphs[name].smartComponentAxes}

            for name in smartComponentNames:
                componentGlyph = Font.glyphs[name]
                for i, axis in enumerate(Font.axes):
                    axisValues = [m.axes[i] for m in Font.masters]
                    newAxis = GSSmartComponentAxis()
                    newAxis.name = axis.name
                    newAxis.bottomValue = min(axisValues)
                    newAxis.topValue = max(axisValues)
                    componentGlyph.smartComponentAxes.append(newAxis)

                    for layer in componentGlyph.layers:
                        if layer.isMasterLayer:
                            master_value = Font.masters[layer.associatedMasterId].axes[i]
                            if master_value == newAxis.bottomValue:
                                layer.smartComponentPoleMapping[componentGlyph.smartComponentAxes[newAxis.name].id] = 1
                            if master_value == newAxis.topValue:
                                layer.smartComponentPoleMapping[componentGlyph.smartComponentAxes[newAxis.name].id] = 2

            for layer in selectedGlyphs:
                for component in layer.components:
                    componentGlyph = Font.glyphs[component.name]
                    for master in Font.masters:
                        masterLayer = layer.parent.layers[master.id]
                        componentMaster = find_component_in_layer(masterLayer, component.name)
                        if componentMaster is not None:
                            for axis in componentGlyph.smartComponentAxes:
                                if axis.name == "Weight":
                                    componentMaster.smartComponentValues[axis.id] = master_weight_values[master.id]

                processedGlyphs.append(layer.parent.name)

            print(f'{", ".join(processedGlyphs)} now have smart components with specific weight values in all masters.')    

            ###################


    def cancel_button_callback(self, sender):
        self.w.close()

if __name__ == "__main__":
    MasterWeightValuesDialog(Glyphs.font)
