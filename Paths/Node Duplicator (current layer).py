# MenuTitle: 🔘 Node Duplicator (Current Layer)
# -*- coding: utf-8 -*-
# Version: 1.3
# Description: Duplicates selected nodes in Current Layer
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

# Get the active font and layer
thisFont = Glyphs.font
thisLayer = thisFont.selectedLayers[0]  # Active layer

# Check if there is a selection
if thisLayer.selection:
    # Store selected nodes in reverse order to prevent index shifting issues
    selectedNodes = [thisNode for thisNode in thisLayer.selection if isinstance(thisNode, GSNode) and thisNode.type != OFFCURVE]
    
    for thisNode in reversed(selectedNodes):  
        newNode = thisNode.copy()
        newNode.type = LINE
        thisNode.parent.nodes.insert(thisNode.index + 1, newNode)

    # Refresh the view
    Glyphs.redraw()

else:
    Message("No nodes selected", "Please select one or more nodes to duplicate.")