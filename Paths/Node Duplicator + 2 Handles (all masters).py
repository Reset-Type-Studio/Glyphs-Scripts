# MenuTitle: 🔘⭕️ Node Duplicator + 2 Handles (All Masters)
# -*- coding: utf-8 -*-
# Version: 1.1
# Description: Duplicates selected nodes and adds overlaped handles without altering the shape in all Masters
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *

Layer = Glyphs.font.selectedLayers[0]

for thisNode in list(Layer.selection):
	if isinstance(thisNode, GSNode) and thisNode.type != OFFCURVE:
		parentPath = thisNode.parent
		index = thisNode.index

		# Crear nodo duplicado
		newNode = thisNode.copy()
		newNode.type = CURVE  # o LINE si no se quiere curva
		newNode.position = thisNode.position

		# Crear manejadores superpuestos
		handle1 = GSNode()
		handle1.type = OFFCURVE
		handle1.position = thisNode.position

		handle2 = GSNode()
		handle2.type = OFFCURVE
		handle2.position = thisNode.position

		# Insertarlos en orden: OFFCURVE - OFFCURVE - CURVE
		parentPath.nodes.insert(index + 1, handle1)
		parentPath.nodes.insert(index + 2, handle2)
		parentPath.nodes.insert(index + 3, newNode)