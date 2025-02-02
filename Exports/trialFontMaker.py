# -*- coding: utf-8 -*-
# MenuTitle: 🎁 Trial Font Maker
# Version: 1.01
# Description: This script creates the Trial versions of fonts. It works on a duplicate of the glyphs file, adds prefix to the font family name and instances, it removes all features and keeps only a selected set of glyphs before exporting them. 
# Credits: Script by Fernando Díaz (Reset Type Studio) with help from AI.

import vanilla
import os
from GlyphsApp import *

class TrialFontMaker:
    def __init__(self):
        self.w = vanilla.FloatingWindow((400, 280), "Trial Font Maker") 

        # Glyphs to keep label
        self.w.textBox = vanilla.TextBox((10, 10, -10, 17), "Glyphs to Keep (space-separated):")

        # Scrollable glyphs input field using TextEditor
        self.w.inputGlyphs = vanilla.TextEditor((10, 30, -10, 80),
            ".notdef space A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c d e f g h i j k l m n o p q r s t u v w x y z zero one two three four five six seven eight nine period comma colon semicolon exclam question hyphen fi fl")

        # Prefix input field
        self.w.prefixBox = vanilla.TextBox((10, 120, -10, 17), "Font Prefix (e.g., (TRIAL):")
        self.w.prefixInput = vanilla.EditText((10, 140, -10, 22), "(TRIAL)", readOnly=False)

        # Directory selection
        self.w.dirBox = vanilla.TextBox((10, 170, -10, 17), "Save Directory:")
        self.w.dirInput = vanilla.EditText((10, 190, -70, 22), os.path.join(os.path.expanduser("~"), "Desktop"), readOnly=False)
        self.w.dirButton = vanilla.Button((-60, 190, -10, 22), "...", callback=self.selectDirectory)

        # Run button
        self.w.runButton = vanilla.Button((10, 230, -10, 22), "Run Script", callback=self.runScript)

        self.w.open()
    
    def selectDirectory(self, sender):
        import vanilla.dialogs
        folderPath = vanilla.dialogs.getFolder("Select save directory")
        if folderPath:
            cleanPath = os.path.abspath(folderPath[0].strip())  # Normalize the path
            self.w.dirInput.set(cleanPath)

    def showError(self, message):
        """ Show an error in a vanilla window. """
        self.errorWindow = vanilla.FloatingWindow((300, 100), "Error")
        self.errorWindow.textBox = vanilla.TextBox((10, 10, -10, 40), message)
        self.errorWindow.okButton = vanilla.Button((10, 60, -10, 20), "OK", callback=self.closeErrorWindow)
        self.errorWindow.open()

    def closeErrorWindow(self, sender):
        """ Close the error window. """
        self.errorWindow.close()

    def showReport(self, message):
        """ Show a final report window after exporting. """
        self.reportWindow = vanilla.FloatingWindow((350, 100), "Export Report")
        self.reportWindow.textBox = vanilla.TextBox((10, 10, -10, 40), message)
        self.reportWindow.okButton = vanilla.Button((10, 60, -10, 20), "OK", callback=self.closeReportWindow)
        self.reportWindow.open()

    def closeReportWindow(self, sender):
        """ Close the report window. """
        self.reportWindow.close()

    def runScript(self, sender):
        glyphsToKeep = self.w.inputGlyphs.get()
        glyphsToKeepList = list(glyphsToKeep.split(' '))
        saveDirectory = self.w.dirInput.get().strip()  # Remove extra spaces
        prefix = self.w.prefixInput.get().strip()  # Get user-defined prefix

        if not Glyphs.fonts:
            self.showError("No font is open.")
            return

        if not os.path.exists(saveDirectory):
            self.showError("Invalid save directory.")
            return

        if not prefix:
            self.showError("Prefix cannot be empty.")
            return

        totalExports = 0
        
        for thisFont in Glyphs.fonts:
            productionFont = thisFont.copy()

            # Ensure we don't add the prefix multiple times
            if not productionFont.familyName.startswith(prefix + " "):
                productionFont.familyName = f"{prefix} {productionFont.familyName}"
            
            for thisInstance in productionFont.instances:
                thisInstance.customParameters['Keep Glyphs'] = glyphsToKeepList
            
            productionFont.featurePrefixes = []
            productionFont.features = []
            productionFont.classes = []
            
            ligaFeature = GSFeature('liga', '')
            productionFont.features.append(ligaFeature)
            productionFont.features['liga'].automatic = True
            productionFont.features['liga'].update()
            
            allGlyphs = [g.name for g in thisFont.glyphs]
            missingGlyphs = [g for g in glyphsToKeepList if g not in allGlyphs]
            
            if missingGlyphs:
                self.showError("Missing glyphs: " + ", ".join(missingGlyphs))
            
            for thisInstance in productionFont.instances:
                thisInstance.fontName = f"{prefix}-{thisInstance.fontName}"  # Prefix instance name too
                exportPath = os.path.join(saveDirectory, thisInstance.fontName + ".otf")
                thisInstance.generate(OTF, exportPath)
                totalExports += 1

        self.showReport(f"Exported {totalExports} instance/s as OTFs.")
        Glyphs.showNotification('Trial Font Maker', 'The export of the trial fonts was successful.')
        self.w.close()

TrialFontMaker()
