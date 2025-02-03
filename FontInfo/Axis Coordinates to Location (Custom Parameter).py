# -*- coding: utf-8 -*-
# MenuTitle: 📊 Copy Axis Coordinates to Location (Custom Parameter)
# Version: 1.01
# Description: Applies the "Axis Location" values as custom parameters to each master and instances.
# Credits: Developed by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import Glyphs

# Get the current font
thisFont = Glyphs.font

if not thisFont:
    print("--- ERROR: No font is open. Please open a font and try again.")
else:
    # Step 1: Apply Axis Location to each master
    for thisMaster in thisFont.masters:
        strMasterName = thisMaster.name
        listAxesValues = thisMaster.axes

        # Initialize list to store axis locations for this master
        listAxisLocations = []

        # Assign axis values to the respective axes
        for thisAxis, intLocation in zip(thisFont.axes, listAxesValues):
            dictAxisInfo = {
                "Axis": thisAxis.name,
                "Location": intLocation
            }
            listAxisLocations.append(dictAxisInfo)

        # Apply the custom parameter to the master
        thisMaster.customParameters["Axis Location"] = listAxisLocations

        # Print confirmation
        print(f"✔ Applied 'Axis Location' custom parameter to master: {strMasterName}")
        print(f"   → Values: {listAxisLocations}\n")

    # Step 2: Apply Axis Location to each export instance
    for thisInstance in thisFont.instances:
        strInstanceName = thisInstance.name
        listInstanceAxes = thisInstance.axes  # Axis coordinates for this export

        # Check if this is a variable font export (no axes coordinates)
        boolIsVariableFont = not bool(listInstanceAxes)

        if boolIsVariableFont:
            print(f"⚠ Skipping variable font export: {strInstanceName} (No axis coordinates found).")
            continue  # Skip setting "Axis Location" for variable fonts

        # Initialize list to store axis locations for this instance
        listInstanceAxisLocations = []

        # Assign axis values to the respective axes
        for thisAxis, intLocation in zip(thisFont.axes, listInstanceAxes):
            dictAxisInfo = {
                "Axis": thisAxis.name,
                "Location": intLocation
            }
            listInstanceAxisLocations.append(dictAxisInfo)

        # Apply the custom parameter to the export instance
        thisInstance.customParameters["Axis Location"] = listInstanceAxisLocations

        # Print confirmation
        print(f"✔ Applied 'Axis Location' custom parameter to export: {strInstanceName}")
        print(f"   → Values: {listInstanceAxisLocations}\n")

    # Notify user
    Glyphs.showNotification(
        "Axis Location Applied",
        "Axis Location custom parameter has been added to all masters and exports."
    )

    print("--- Axis Location custom parameters have been successfully applied to all masters and exports.")
