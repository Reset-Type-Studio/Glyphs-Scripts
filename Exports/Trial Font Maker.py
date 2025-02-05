# MenuTitle: 🎁 Trial Font Maker
# -*- coding: utf-8 -*-
# Version: 1.03
# Description: This script creates the Trial versions of fonts. It works on a duplicate of the glyphs file, adds prefix to the font family name and instances, it removes all features and keeps only a selected set of glyphs before exporting them. 
# Author: Script by Fernando Díaz (Reset Type Studio) with help from AI.

import vanilla
import os
from GlyphsApp import *

class TrialFontMaker:
    """Creates a trial version of the font with a custom glyph set and prefix."""

    def __init__(self):
        """Initialize the UI for selecting glyphs, prefix, and save directory."""
        self.uiWindow = vanilla.FloatingWindow((400, 280), "Trial Font Maker") 

        # Glyphs to keep input
        self.uiWindow.txtGlyphsToKeep = vanilla.TextBox((10, 10, -10, 17), "Glyphs to Keep (space-separated):")
        self.uiWindow.inputGlyphs = vanilla.TextEditor((10, 30, -10, 80),
            ".notdef space A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o p q r s t u v w x y z zero one two three four five six seven eight nine period comma"
        )

        # Prefix input
        self.uiWindow.txtPrefix = vanilla.TextBox((10, 120, -10, 17), "Font Prefix (e.g., TRIAL):")
        self.uiWindow.inputPrefix = vanilla.EditText((10, 140, -10, 22), "TRIAL")

        # Directory selection
        self.uiWindow.txtDirectory = vanilla.TextBox((10, 170, -10, 17), "Save Directory:")
        self.uiWindow.inputDirectory = vanilla.EditText((10, 190, -70, 22), os.path.join(os.path.expanduser("~"), "Desktop"))
        self.uiWindow.btnDirectory = vanilla.Button((-60, 190, -10, 22), "...", callback=self.selectDirectory)

        # Run button
        self.uiWindow.btnRun = vanilla.Button((10, 230, -10, 22), "Generate Trial Font", callback=self.runScript)

        self.uiWindow.open()

    def selectDirectory(self, sender):
        """Open folder selection dialog and update the directory input."""
        import vanilla.dialogs
        listFolderPath = vanilla.dialogs.getFolder("Select save directory")
        if listFolderPath:
            strCleanPath = os.path.abspath(listFolderPath[0].strip())  # Normalize path
            self.uiWindow.inputDirectory.set(strCleanPath)

    def showError(self, strMessage):
        """Display an error message in a Vanilla window."""
        self.errorWindow = vanilla.FloatingWindow((300, 100), "Error")
        self.errorWindow.txtMessage = vanilla.TextBox((10, 10, -10, 40), strMessage)
        self.errorWindow.btnClose = vanilla.Button((10, 60, -10, 20), "OK", callback=self.closeErrorWindow)
        self.errorWindow.open()

    def closeErrorWindow(self, sender):
        """Close the error window."""
        self.errorWindow.close()

    def showReport(self, strMessage):
        """Display a final report window after exporting."""
        self.reportWindow = vanilla.FloatingWindow((350, 100), "Export Report")
        self.reportWindow.txtMessage = vanilla.TextBox((10, 10, -10, 40), strMessage)
        self.reportWindow.btnClose = vanilla.Button((10, 60, -10, 20), "OK", callback=self.closeReportWindow)
        self.reportWindow.open()

    def closeReportWindow(self, sender):
        """Close the report window."""
        self.reportWindow.close()

    def runScript(self, sender):
        """Execute the script to create the trial font."""
        strGlyphsToKeep = self.uiWindow.inputGlyphs.get().strip()
        listGlyphsToKeep = strGlyphsToKeep.split()
        strSaveDirectory = self.uiWindow.inputDirectory.get().strip()
        strPrefix = self.uiWindow.inputPrefix.get().strip()

        if not Glyphs.fonts:
            self.showError("No font is open.")
            return

        if not os.path.exists(strSaveDirectory):
            self.showError("Invalid save directory.")
            return

        if not strPrefix:
            self.showError("Prefix cannot be empty.")
            return

        intTotalExports = 0

        for thisFont in Glyphs.fonts:
            # Step 1: Duplicate the font
            thisTrialFont = thisFont.copy()

            # Step 2: Modify font family name with prefix
            if not thisTrialFont.familyName.startswith(strPrefix + " "):
                thisTrialFont.familyName = f"{strPrefix} {thisTrialFont.familyName}"

            # Step 3: Modify instances and keep glyphs
            for thisInstance in thisTrialFont.instances:
                thisInstance.customParameters['Keep Glyphs'] = listGlyphsToKeep

            # Step 4: Remove OpenType features
            thisTrialFont.featurePrefixes = []
            thisTrialFont.features = []
            thisTrialFont.classes = []

            # Step 5: Enable standard ligature feature
            thisLigaFeature = GSFeature('liga', '')
            thisTrialFont.features.append(thisLigaFeature)
            thisTrialFont.features['liga'].automatic = True
            thisTrialFont.features['liga'].update()

            # Step 6: Check for missing glyphs
            listAllGlyphs = [thisGlyph.name for thisGlyph in thisFont.glyphs]
            listMissingGlyphs = [thisGlyph for thisGlyph in listGlyphsToKeep if thisGlyph not in listAllGlyphs]

            if listMissingGlyphs:
                self.showError("Missing glyphs: " + ", ".join(listMissingGlyphs))

            # Step 7: Export each instance
            for thisInstance in thisTrialFont.instances:
                thisInstance.fontName = f"{strPrefix}-{thisInstance.fontName}"  # Prefix instance name too
                strExportPath = os.path.join(strSaveDirectory, thisInstance.fontName + ".otf")
                thisInstance.generate(OTF, strExportPath)
                intTotalExports += 1

        self.showReport(f"Exported {intTotalExports} instance(s) as OTFs.")
        Glyphs.showNotification('Trial Font Maker', 'The export of the trial fonts was successful.')
        self.uiWindow.close()

# Run the UI Window
TrialFontMaker()
