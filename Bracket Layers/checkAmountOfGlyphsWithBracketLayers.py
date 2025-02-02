# -*- coding: utf-8 -*-
# MenuTitle: {📄} List Glyphs with Bracket Layers and Affected Components
# Version: 1.01
# Description: Lists glyphs with bracket layers and all affected glyphs, including nested components, in a scrollable Vanilla window with optimized performance.
# Credits: Script by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
from collections import deque, defaultdict
from vanilla import Window, TextEditor


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


class BracketLayerReport:
    def __init__(self, font):
        """Initialize the report by identifying glyphs with bracket layers and affected components."""
        self.font = font
        self.bracket_glyphs = list_glyphs_with_bracket_layers(font)
        glyph_to_components = build_component_map(font)
        self.component_glyphs = find_affected_components(self.bracket_glyphs, glyph_to_components)
        
        # Total number of affected glyphs (bracket glyphs + components using them)
        self.total_affected_glyphs = len(self.bracket_glyphs) + len(self.component_glyphs)
        self.build_window()

    def build_window(self):
        """Create and display the Vanilla UI window containing the report."""
        self.w = Window((500, 400), "Bracket Layer Report", minSize=(500, 400))
        
        report_text = (
            f"Glyphs with Bracket Layers ({len(self.bracket_glyphs)}):\n"
            + ", ".join(sorted(self.bracket_glyphs)) +
            f"\n\nAffected Components ({len(self.component_glyphs)}):\n"
            + ", ".join(sorted(self.component_glyphs)) +
            f"\n\nTotal affected glyphs: {self.total_affected_glyphs}"
        )
        
        # Display the report in a scrollable, read-only text field
        self.w.report = TextEditor((10, 10, -10, -10), report_text, readOnly=True)
        
        self.w.open()


# Main Execution
font = Glyphs.font  # Access the currently open font in Glyphs
if not font:
    print("--- ERROR: No font is open. Please open a font and try again.")
else:
    BracketLayerReport(font)
