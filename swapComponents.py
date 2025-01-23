# Swap one component for another in every master

from GlyphsApp import Glyphs

def main():
    # Get the active Glyphs App document
    font = Glyphs.font

    # Get the selected glyphs
    selected_glyphs = [x.parent for x in font.selectedLayers]

    # Define the component names
    original_component = "circled"
    new_component = "blackCircled"

    # Iterate through each master
    for master in font.masters:
        # Iterate through each selected glyph
        for glyph in selected_glyphs:
            # Check if the glyph has the component we want to substitute
            if has_component(glyph, master, original_component):
                # Substitute the component
                substitute_component(glyph, master, original_component, new_component)

def has_component(glyph, master, component_name):
    """Check if a glyph has a specific component in a specific master."""
    layer = glyph.layers[master.id]
    for component in layer.components:
        if component.name == component_name:
            return True
    return False

def substitute_component(glyph, master, original_component, new_component):
    """Substitute a component in a glyph for another component."""
    layer = glyph.layers[master.id]
    for component in layer.components:
        if component.name == original_component:
            component.name = new_component
            print(f"Substituted {original_component} with {new_component} in glyph '{glyph.name}' for master '{master.name}'")

if __name__ == "__main__":
    main()
