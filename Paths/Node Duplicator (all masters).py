# MenuTitle: 🔘 Node Duplicator (all Masters)
# -*- coding: utf-8 -*-
# Version: 1.3
# Description: Duplicates selected nodes in all Masters
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

# Get the active font
thisFont = Glyphs.font  

# Get the selected glyphs
selectedGlyphs = [thisLayer.parent for thisLayer in thisFont.selectedLayers]

# Check if any nodes are selected
activeLayer = thisFont.selectedLayers[0]  # The currently active layer
selectedNodes = [thisNode for thisNode in activeLayer.selection if isinstance(thisNode, GSNode) and thisNode.type != OFFCURVE]

if selectedNodes:
    # Store positions of selected nodes within their respective paths
    selectedNodeIndices = []
    for pathIndex, thisPath in enumerate(activeLayer.paths):  # Loop through paths
        for nodeIndex, thisNode in enumerate(thisPath.nodes):
            if thisNode in selectedNodes:
                selectedNodeIndices.append((pathIndex, nodeIndex))  # Store path index + node index

    # Iterate through each selected glyph and apply the same changes to all layers
    for thisGlyph in selectedGlyphs:
        for thisLayer in thisGlyph.layers:
            for pathIndex, nodeIndex in reversed(selectedNodeIndices):  # Iterate in reverse order
                try:
                    thisNode = thisLayer.paths[pathIndex].nodes[nodeIndex]  # Get the same node position
                    newNode = thisNode.copy()
                    newNode.type = LINE
                    thisLayer.paths[pathIndex].nodes.insert(nodeIndex + 1, newNode)  # Insert after the original node
                except IndexError:
                    print(f"Skipping invalid node index {nodeIndex} in glyph {thisGlyph.name}")

    # Properly refresh Glyphs UI
    Glyphs.redraw()
else:
    Message("No nodes selected", "Please select one or more nodes to duplicate.")
