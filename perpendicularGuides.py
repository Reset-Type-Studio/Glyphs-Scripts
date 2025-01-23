# MenuTitle: ⍿ Perpendicular Guides
# -*- coding: utf-8 -*-
from GlyphsApp import GSGuideLine
from math import atan2, degrees, radians

def bezier_point(t, p0, p1, p2, p3):
    """Calculates a point on a cubic Bezier curve for a given t (0 to 1)."""
    x = (1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * p1.x + 3 * (1 - t) * t ** 2 * p2.x + t ** 3 * p3.x
    y = (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * p1.y + 3 * (1 - t) * t ** 2 * p2.y + t ** 3 * p3.y
    return (x, y)

def calculate_midpoint(nodes):
    """
    Calculate the geometric midpoint of the selected nodes.
    """
    x_coords = [node.x for node in nodes]
    y_coords = [node.y for node in nodes]
    return (sum(x_coords) / len(nodes), sum(y_coords) / len(nodes))

def calculate_tangent_for_path(nodes):
    """
    Calculate the tangent at the midpoint for any number of selected points.
    """
    if len(nodes) == 2:
        # Straight segment
        dx = nodes[1].x - nodes[0].x
        dy = nodes[1].y - nodes[0].y
    else:
        # Approximate tangent for multiple points
        dx = nodes[-1].x - nodes[0].x
        dy = nodes[-1].y - nodes[0].y
    return dx, dy

def create_perpendicular_guide(layer, selected_nodes):
    """
    Creates a perpendicular guide based on selected nodes.
    """
    if len(selected_nodes) < 2:
        print("Please select at least two points.")
        return

    mid_x, mid_y = calculate_midpoint(selected_nodes)
    dx, dy = calculate_tangent_for_path(selected_nodes)
    angle = atan2(dy, dx)
    perp_angle = angle + radians(90)

    guide = GSGuideLine()
    guide.position = (mid_x, mid_y)
    guide.angle = degrees(perp_angle)
    layer.guides.append(guide)
    print(f"Added perpendicular guide at ({mid_x}, {mid_y}) with angle {degrees(perp_angle)}°.")

def create_guides_for_components(layer, selected_components):
    """
    Creates two guides (horizontal and vertical) at the center of selected components.
    """
    for component in selected_components:
        # Get the bounds of the component
        bounds = component.bounds
        comp_x = bounds.origin.x + bounds.size.width / 2
        comp_y = bounds.origin.y + bounds.size.height / 2

        # Horizontal guide
        horizontal_guide = GSGuideLine()
        horizontal_guide.position = (comp_x, comp_y)
        horizontal_guide.angle = 0  # Horizontal
        layer.guides.append(horizontal_guide)

        # Vertical guide
        vertical_guide = GSGuideLine()
        vertical_guide.position = (comp_x, comp_y)
        vertical_guide.angle = 90  # Vertical
        layer.guides.append(vertical_guide)

        print(f"Added horizontal and vertical guides at center ({comp_x}, {comp_y}) for component.")

# Main script
font = Glyphs.font
selected_layer = font.selectedLayers[0]

# Gather all selected nodes and components
selected_nodes = []
selected_components = []

for path in selected_layer.paths:
    for node in path.nodes:
        if node.selected:
            selected_nodes.append(node)

for component in selected_layer.components:
    if component.selected:
        selected_components.append(component)

# Handle guides creation
if selected_nodes:
    create_perpendicular_guide(selected_layer, selected_nodes)

if selected_components:
    create_guides_for_components(selected_layer, selected_components)

if not selected_nodes and not selected_components:
    print("Please select path nodes or components.")
