# -*- coding: utf-8 -*-
# MenuTitle: {💫} Bracket Layers → Alternate Glyphs (Method from Switching Shapes)
# Version: 1.023
# Description: Automates the creation of suffixed glyphs, their components, custom parameters and feature code for the Alternate Glyphs method found in Switching Shapes tutorial.
# Credits: Developed by Fernando Díaz (Reset Type Studio) with help from AI.

# =============================
# Issues
# =============================
# The feature code can create duplicates when glyphs have: paths + components affected by BL (ex: ligatures f_l, "l" has BL).
# Right now "Rename Glyphs" custom parameter adds every glyph, it should add affected glyphs acording to its weight in each instance.

from GlyphsApp import *
import vanilla
from collections import defaultdict

# =============================
# Constants Section
# =============================

DEFAULT_SUFFIX = ".switch"  # Default suffix for alternate glyphs
REMOVE_GLYPHS = "Remove Glyphs"  # Parameter name for glyph removal
RENAME_GLYPHS = "Rename Glyphs"  # Parameter name for glyph renaming
MAIN_COLOR = 6  # Color Purple for visual distinction in Glyphs 
COMPONENT_COLOR = 7  # Color Blue for visual distinction in Glyphs 

# =============================
# Functions Section
# =============================

def has_bracket_layers(glyph):
    """Check if a glyph has any bracket layers."""
    return any("[" in layer.name and "]" in layer.name for layer in glyph.layers)

def check_and_collect_bracket_glyphs(font):
    """Collect glyphs with bracket layers."""
    return [glyph for glyph in font.glyphs if has_bracket_layers(glyph)]

def build_component_map(font):
    """Build a map of glyphs and the glyphs that use them as components."""
    component_map = {}
    for glyph in font.glyphs:
        for layer in glyph.layers:
            for component in layer.components:
                if component.componentName not in component_map:
                    component_map[component.componentName] = set()
                component_map[component.componentName].add(glyph.name)
    return component_map

def find_nested_affected_components_iterative(glyph, component_map):
    """Find glyphs that use the given glyph as a component, iteratively."""
    stack = [glyph.name]  # Start with the initial glyph
    visited = set()
    affected_glyphs = set()

    while stack:
        current_glyph_name = stack.pop()
        if current_glyph_name in visited:
            continue
        visited.add(current_glyph_name)

        # Add all glyphs that use the current glyph as a component
        if current_glyph_name in component_map:
            for dependent_glyph in component_map[current_glyph_name]:
                if dependent_glyph not in visited:
                    stack.append(dependent_glyph)
                affected_glyphs.add(dependent_glyph)

    return affected_glyphs

def create_and_update_glyphs_with_suffix(bracket_glyphs, font, suffix):
    """Create new glyphs with a suffix and update their layers more efficiently."""
    suffixed_glyphs = []
    existing_glyph_names = {glyph.name for glyph in font.glyphs}  # Cache existing glyph names

    for source_glyph in bracket_glyphs:
        new_glyph_name = source_glyph.name + suffix

        # Skip if the source glyph already has the suffix or the new glyph exists
        if source_glyph.name.endswith(suffix) or new_glyph_name in existing_glyph_names:
            continue

        # Create and configure the new glyph
        new_glyph = source_glyph.copy()
        new_glyph.name = new_glyph_name
        new_glyph.color = COMPONENT_COLOR
        font.glyphs.append(new_glyph)

        # Copy and update only bracket layers
        for layer in source_glyph.layers:
            if "[" in layer.name and "]" in layer.name:
                new_layer = new_glyph.layers[layer.associatedMasterId]
                if layer.shapes:
                    new_layer.shapes = [shape.copy() for shape in layer.shapes]
                    new_layer.width = layer.width

        suffixed_glyphs.append(new_glyph)

        # Remove bracket layers from suffix glyphs
        layers_to_remove = [layer for layer in new_glyph.layers if "[" in layer.name or "]" in layer.name]
        for layer in layers_to_remove:
            del new_glyph.layers[layer.layerId]

    return suffixed_glyphs

def update_components_in_suffixed_glyphs(font, suffix):
    """Updates components in suffixed glyphs so they correctly reference their respective suffixed originals."""
    for glyph in font.glyphs:
        if glyph.name.endswith(suffix):  # Only process suffixed glyphs
            base_name = glyph.name.replace(suffix, "")  # Get the base glyph name
            base_glyph = font.glyphs[base_name]

            if not base_glyph:
                continue  # Skip if no original base glyph exists
            
            for layer in glyph.layers:
                for component in layer.components:
                    original_component_name = component.componentName
                    if original_component_name.endswith(suffix):
                        continue  # If already correct, skip

                    suffixed_component_name = original_component_name + suffix
                    if font.glyphs[suffixed_component_name]:  # Check if suffixed version exists
                        component.componentName = suffixed_component_name

def erase_bracket_layers_from_glyphs(glyphs):
    """Erase bracket layers from the provided glyphs with less redundant processing."""
    for glyph in glyphs:
        glyph.layers = [layer for layer in glyph.layers if "[" not in layer.name and "]" not in layer.name]

def add_custom_parameters_to_instances(font, suffix, bracket_glyphs_list, component_glyphs_list):
    """Generate custom parameters for all instances."""
    remove_glyphs_value = f"*.{suffix.lstrip('.')}"
    rename_glyphs_value = []

    # Extract names from glyph lists
    bracket_glyph_names = [glyph.name.replace(suffix, "") for glyph in bracket_glyphs_list]
    component_glyph_names = [glyph.replace(suffix, "") for glyph in component_glyphs_list]

    # Rename Glyphs parameter: Combine bracket and component glyphs
    rename_glyphs_value += [f"{name}={name}{suffix}" for name in bracket_glyph_names]
    rename_glyphs_value += [f"{name}={name}{suffix}" for name in component_glyph_names]

    # Add the custom parameters to all exportable instances
    for instance in font.instances:
        if instance.type == 0:  # Exportable instance
            if REMOVE_GLYPHS not in {param.name for param in instance.customParameters}:
                instance.customParameters.append(GSCustomParameter(REMOVE_GLYPHS, remove_glyphs_value))
            if RENAME_GLYPHS not in {param.name for param in instance.customParameters}:
                instance.customParameters.append(GSCustomParameter(RENAME_GLYPHS, ", ".join(rename_glyphs_value)))

def create_new_tab_with_switch_glyphs(font, suffixed_glyphs, component_glyphs):
    """Open a new tab in Glyphs with .switch glyphs organized into Non-Component and Component sections."""
    suffixed_glyph_names = {glyph.name for glyph in suffixed_glyphs}
    non_component_glyphs = sorted(suffixed_glyph_names - set(component_glyphs))
    component_glyphs = sorted(component_glyphs)

    non_component_header = "Created Glyphs:\n" + " ".join(f"/{name}" for name in non_component_glyphs)
    component_header = "Components:\n" + " ".join(f"/{name}" for name in component_glyphs)
    tab_content = f"{non_component_header}\n\n{component_header}"

    font.newTab(tab_content)

def extract_suffix(layer_name, suffix):
    """Function to extract the suffix from a layer name."""
    parts = layer_name.split('[')[0].split('.')
    return parts[-1] if len(parts) > 1 and parts[-1] != suffix.strip('.') else suffix.strip('.')

def get_original_components(glyph_name, cache={}):
    """Recursively find all base component glyphs for a given glyph with memoization."""
    if glyph_name in cache:
        return cache[glyph_name]

    base_components = set()
    glyph = Font.glyphs[glyph_name]
    if not glyph:
        cache[glyph_name] = base_components
        return base_components

    for layer in glyph.layers:
        for component in layer.components:
            base_glyph_name = component.componentName
            if base_glyph_name not in base_components:
                base_components.add(base_glyph_name)
                base_components.update(get_original_components(base_glyph_name, cache))  # Recursive call

    cache[glyph_name] = base_components  # Store result in cache
    return base_components

def generate_feature_code(suffix):
    """Creates rlig and rvrn feature code automatically from suffix, accounting for nested components efficiently."""
    bracket_layer_dict = defaultdict(list)
    font_glyphs = Font.glyphs  # Cache the glyphs

    # Step 1: Precompute Bracket Layer Glyphs
    glyph_bracket_layers = {}
    for glyph in font_glyphs:
        bracket_layers = [layer for layer in glyph.layers if '[' in layer.name and ']' in layer.name]
        if bracket_layers:
            glyph_bracket_layers[glyph.name] = bracket_layers

    # Step 2: Populate Substitution Dictionary
    for glyph_name, bracket_layers in glyph_bracket_layers.items():
        for layer in bracket_layers:
            condition_values = layer.name.split('[')[1].split(']')[0]

            suffix2 = extract_suffix(layer.name, suffix)
            glyph_name_with_suffix = f"{glyph_name}.{suffix2}"

            if glyph_name_with_suffix not in bracket_layer_dict[condition_values]:
                bracket_layer_dict[condition_values].append(glyph_name_with_suffix)

    # Step 3: Process Components Efficiently Using Precomputed Base Glyphs
    component_cache = {}  # Cache to store component mappings
    for glyph in font_glyphs:
        if glyph.name not in component_cache:
            component_cache[glyph.name] = get_original_components(glyph.name)  # Compute components once

        for base_glyph_name in component_cache[glyph.name]:
            if base_glyph_name in glyph_bracket_layers:
                for condition, glyph_names in bracket_layer_dict.items():
                    for glyph_name_with_suffix in glyph_names:
                        base_name_parts = glyph_name_with_suffix.split('.')
                        base_name = ".".join(base_name_parts[:-1])
                        suffix2 = base_name_parts[-1]

                        if base_name == base_glyph_name and f"{glyph.name}.{suffix2}" not in bracket_layer_dict[condition]:
                            bracket_layer_dict[condition].append(f"{glyph.name}.{suffix2}")

    # Step 4: Generate the Feature Code
    rlig_output = ["#ifdef VARIABLE"]
    rvrn_output = ["#ifdef VARIABLE"]

    for condition, glyph_names in bracket_layer_dict.items():
        condition = condition.replace('‹', ' < ').replace('wg', 'wght').replace('wd', 'wdth').replace('oz', 'opsz').replace('it', 'ital').replace('sl', 'slnt').replace('\u2009', ' ')
        rlig_output.append(f"condition {condition};")
        rvrn_output.append(f"condition {condition};")

        for glyph_name_with_suffix in sorted(glyph_names):
            original_glyph_name = ".".join(glyph_name_with_suffix.split('.')[:-1])
            rlig_output.append(f"sub {original_glyph_name} by {glyph_name_with_suffix};")
            rvrn_output.append(f"sub {original_glyph_name} by {glyph_name_with_suffix};")

        rlig_output.append("")
        rvrn_output.append("")

    rlig_output.append("#endif")
    rvrn_output.append("#endif")

    # Step 5: Add the feature to the font
    add_or_update_feature(Font, "rlig", "\n".join(rlig_output))
    add_or_update_feature(Font, "rvrn", "\n".join(rvrn_output))

def add_or_update_feature(font, feature_tag, feature_code):
    """Adds or updates a feature with the given tag and code in the font."""
    feature = font.features[feature_tag] if feature_tag in {f.name for f in font.features} else GSFeature(feature_tag)
    feature.code = feature_code
    if feature_tag not in {f.name for f in font.features}:
        font.features.append(feature)

def show_final_report(total_bracket_glyphs, total_components, suffixed_glyphs, component_glyphs, font, erase_brackets, add_custom_params, add_features):
    """Display the final report in a Vanilla window."""
    erase_brackets_text = "On" if erase_brackets else "Off"
    add_custom_params_text = "On" if add_custom_params else "Off"
    add_features_text = "On" if add_features else "Off"

    bracket_glyphs_list = ", ".join(sorted(glyph.name for glyph in suffixed_glyphs))
    component_glyphs_list = ", ".join(sorted(component_glyphs))

    rename_glyphs_text = ""
    if add_custom_params and len(font.instances) > 1:
        second_instance = font.instances[1]
        for param in second_instance.customParameters:
            if param.name == RENAME_GLYPHS:
                rename_glyphs_text = param.value
                break

    custom_params_text = ""
    if add_custom_params:
        custom_params_text = (
            f"Custom Parameters:\n"
            f"Added '{REMOVE_GLYPHS}': *.switch\n"
            f"Added '{RENAME_GLYPHS}': {rename_glyphs_text}\n"
        )

    report_text = (
        f"INITIAL SEARCH:\n"
        f"Glyphs with Bracket Layers: {total_bracket_glyphs}\n"
        f"Components from Bracket Layers: {total_components}\n"
        f"Total Glyphs + Components with Bracket Layers = {total_bracket_glyphs + total_components}\n\n"
        f"CREATED GLYPHS:\n"
        f"· Suffixed glyphs created: {len(suffixed_glyphs)}\n"
        f"· Suffixed glyphs from components created: {total_components}\n"
        f"· Total Suffixed Glyphs + Components created = {len(suffixed_glyphs) + total_components}\n\n"
        f"OTHER ACTIONS:\n"
        +
        (f"· Added custom parameters\n" if add_custom_params_text == "On" else "") +
        (f"· Add rlig & rvr features\n" if add_features_text == "On" else "") +
        (f"· Erased existing bracket layers\n" if erase_brackets_text == "On" else "") +
        "\n\n"
        "Note: Please determine if you need to switch in the alternate glyph or not, in the 'Rename Glyphs' custom parameter."
    )

    class FinalReportWindow:
        def __init__(self):
            self.w = vanilla.Window((600, 500), "Final Report", minSize=(600, 500))
            self.w.textEditor = vanilla.TextEditor((10, 10, -10, -40), report_text, readOnly=True)
            self.w.closeButton = vanilla.Button((-100, -30, -10, 20), "Close", callback=self.close_window)
            self.w.open()
        def close_window(self, sender):
            self.w.close()

    FinalReportWindow()

# =============================
# Main Execution
# =============================

def execute_main_script(suffix, add_features, add_custom_params, erase_brackets, open_in_new_tab):
    font = Glyphs.font  # Ensure the font is accessed in the function scope
    if not font:
        print("--- ERROR: No font is open. Please open a font and try again.")
        return

    bracket_glyphs = check_and_collect_bracket_glyphs(font)
    if not bracket_glyphs:
        print("--- ERROR: No bracket layers found.")
        return

    component_map = build_component_map(font)

    affected_components = set()
    for glyph in bracket_glyphs:
        affected_components.update(find_nested_affected_components_iterative(glyph, component_map))

    if add_features:
        generate_feature_code(suffix)

    suffixed_glyphs = create_and_update_glyphs_with_suffix(bracket_glyphs, font, suffix)

    component_glyphs_created = set()
    for glyph_name in affected_components:
        glyph = font.glyphs[glyph_name]
        new_glyph_name = glyph_name + suffix
        if glyph and new_glyph_name not in font.glyphs:
            duplicated_glyph = glyph.copy()
            duplicated_glyph.name = new_glyph_name
            font.glyphs.append(duplicated_glyph)
            component_glyphs_created.add(duplicated_glyph.name)

    update_components_in_suffixed_glyphs(font, suffix)

    if add_custom_params:
        add_custom_parameters_to_instances(font, suffix, suffixed_glyphs, component_glyphs_created)

    if erase_brackets:
        erase_bracket_layers_from_glyphs(bracket_glyphs)

    if open_in_new_tab:
        create_new_tab_with_switch_glyphs(font, suffixed_glyphs, component_glyphs_created)

    show_final_report(
        len(suffixed_glyphs),
        len(component_glyphs_created),
        suffixed_glyphs,
        component_glyphs_created,
        font,
        erase_brackets,
        add_custom_params,
        add_features,
    )

class SuffixInputWindow:
    def __init__(self):
        self.w = vanilla.Window((300, 240), "Set Alternate Glyphs Options", minSize=(300, 240))
        self.w.textLabel = vanilla.TextBox((15, 15, -15, 20), "Enter the desired suffix for alternate glyphs:")
        self.w.inputField = vanilla.EditText((15, 40, -15, 20), DEFAULT_SUFFIX)
        self.w.customParamCheckbox = vanilla.CheckBox((15, 70, -15, 20), "Add custom parameters to instances", value=True)
        self.w.featuresCheckbox = vanilla.CheckBox((15, 100, -15, 20), "Add features code", value=True)
        self.w.openTabCheckbox = vanilla.CheckBox((15, 130, -15, 20), "Open in a new tab", value=True)
        self.w.eraseCheckbox = vanilla.CheckBox((15, 160, -15, 20), "Erase existing bracket layers", value=False)
        self.w.generateButton = vanilla.Button((15, 200, -15, 20), "Generate Alternate Glyphs", callback=self.generate_output)
        self.w.open()

    def generate_output(self, sender):
        suffix = self.w.inputField.get()
        erase_brackets = self.w.eraseCheckbox.get()
        add_custom_params = self.w.customParamCheckbox.get()
        add_features = self.w.featuresCheckbox.get()
        open_in_new_tab = self.w.openTabCheckbox.get()
        self.w.close()

        execute_main_script(suffix, add_features, add_custom_params, erase_brackets, open_in_new_tab)

SuffixInputWindow()