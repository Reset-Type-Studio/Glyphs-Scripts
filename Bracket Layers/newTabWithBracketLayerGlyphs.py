# -*- coding: utf-8 -*-
# MenuTitle: {🖥️} Open Glyphs with Bracket Layers in a New Tab
# Version: 1.02
# Description: Opens a new tab with glyphs containing bracket layers, followed by glyphs using these as components.
# Credits: Script by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
from collections import deque, defaultdict


def has_bracket_layers(glyph):
    """Check if a glyph has any bracket layers efficiently."""
    return any("[" in layer.name and "]" in layer.name for layer in glyph.layers)


def list_glyphs_with_bracket_layers(font):
    """Return a set of glyph names that contain bracket layers."""
    return {glyph.name for glyph in font.glyphs if has_bracket_layers(glyph)}


def build_component_map(font):
    """Create a mapping of glyphs to the glyphs that use them as components."""
    glyph_to_components = defaultdict(set)
    
    for glyph in font.glyphs:
        for layer in glyph.layers:
            for component in layer.components:
                if component.componentName:
                    glyph_to_components[component.componentName].add(glyph.name)
    
    return glyph_to_components


def find_affected_components(glyph_names, glyph_to_components):
    """Find all glyphs that use any of the given glyphs as components using a queue."""
    affected_glyphs = set()
    queue = deque(glyph_names)
    
    while queue:
        current_glyph = queue.popleft()
        for dependent_glyph in glyph_to_components.get(current_glyph, []):
            if dependent_glyph not in affected_glyphs:
                affected_glyphs.add(dependent_glyph)
                queue.append(dependent_glyph)  # Add newly found components to be processed
    
    return affected_glyphs


def open_glyphs_with_bracket_layers():
    """Opens a new tab in Glyphs with bracket-layered glyphs and their components."""
    font = Glyphs.font
    if not font:
        print("No font open in Glyphs.")
        return

    # Find bracket-layered glyphs and build the component dependency map
    bracket_glyphs = list_glyphs_with_bracket_layers(font)
    glyph_to_components = build_component_map(font)

    # Find all components that reference bracket-layered glyphs (including nested)
    component_glyphs = find_affected_components(bracket_glyphs, glyph_to_components)

    # Sort glyph names
    all_glyphs = sorted(bracket_glyphs) + sorted(component_glyphs)

    # Open a new tab if there are glyphs to show
    if all_glyphs:
        font.newTab("Glyphs:\n/" + "/".join(bracket_glyphs) + "\n\nComponents:\n/" + "/".join(component_glyphs))
    else:
        print("No bracket-layered glyphs or components found.")


# Main Execution
if __name__ == "__main__":
    font = Glyphs.font  
    if not font:
        print("--- ERROR: No font is open. Please open a font and try again.")
    else:
        open_glyphs_with_bracket_layers()
