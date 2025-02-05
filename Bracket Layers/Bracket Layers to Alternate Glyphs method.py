# MenuTitle: 💫 Bracket Layers → Alternate Glyphs (Switching Shapes Method)
# -*- coding: utf-8 -*-
# Version: 1.024
# Description: Automates the creation of suffixed glyphs, their components, custom parameters, and feature code for the Alternate Glyphs method found in the Switching Shapes tutorial.
# Author: Developed by Fernando Díaz (Reset Type Studio) with help from AI.

from GlyphsApp import *
import vanilla
from collections import defaultdict

# =============================
# Constants Section
# =============================

STR_DEFAULT_SUFFIX = ".switch"  # Default suffix for alternate glyphs
STR_REMOVE_GLYPHS = "Remove Glyphs"  # Parameter name for glyph removal
STR_RENAME_GLYPHS = "Rename Glyphs"  # Parameter name for glyph renaming
INT_MAIN_COLOR = 6  # Color Purple for visual distinction in Glyphs
INT_COMPONENT_COLOR = 7  # Color Blue for visual distinction in Glyphs

# =============================
# Functions Section
# =============================

def checkBracketLayers(thisGlyph):
    """Check if a glyph has any bracket layers."""
    return any("[" in thisLayer.name and "]" in thisLayer.name for thisLayer in thisGlyph.layers)

def collectBracketLayerGlyphs(thisFont):
    """Collect glyphs with bracket layers."""
    return [thisGlyph for thisGlyph in thisFont.glyphs if checkBracketLayers(thisGlyph)]

def createComponentMapping(thisFont):
    """Build a mapping of glyphs and the glyphs that use them as components."""
    dictComponentMap = defaultdict(set)
    
    for thisGlyph in thisFont.glyphs:
        for thisLayer in thisGlyph.layers:
            for thisComponent in thisLayer.components:
                dictComponentMap[thisComponent.componentName].add(thisGlyph.name)
    
    return dictComponentMap

def identifyAffectedComponents(thisGlyph, dictComponentMap):
    """Find glyphs that use the given glyph as a component iteratively."""
    listStack = [thisGlyph.name]
    setVisited = set()
    setAffectedGlyphs = set()

    while listStack:
        strCurrentGlyph = listStack.pop()
        if strCurrentGlyph in setVisited:
            continue
        setVisited.add(strCurrentGlyph)

        # Add all glyphs that use the current glyph as a component
        if strCurrentGlyph in dictComponentMap:
            for strDependentGlyph in dictComponentMap[strCurrentGlyph]:
                if strDependentGlyph not in setVisited:
                    listStack.append(strDependentGlyph)
                setAffectedGlyphs.add(strDependentGlyph)

    return setAffectedGlyphs

def createSuffixedGlyphs(listBracketGlyphs, thisFont, strSuffix):
    """Create new suffixed glyphs and copy bracket layers."""
    listSuffixedGlyphs = []
    setExistingGlyphNames = {thisGlyph.name for thisGlyph in thisFont.glyphs}  # Cache existing glyph names

    for thisSourceGlyph in listBracketGlyphs:
        strNewGlyphName = thisSourceGlyph.name + strSuffix

        # Skip if the source glyph already has the suffix or the new glyph exists
        if thisSourceGlyph.name.endswith(strSuffix) or strNewGlyphName in setExistingGlyphNames:
            continue

        # Create and configure the new glyph
        thisNewGlyph = thisSourceGlyph.copy()
        thisNewGlyph.name = strNewGlyphName
        thisNewGlyph.color = INT_COMPONENT_COLOR
        thisFont.glyphs.append(thisNewGlyph)

        # Copy and update only bracket layers
        for thisLayer in thisSourceGlyph.layers:
            if "[" in thisLayer.name and "]" in thisLayer.name:
                thisNewLayer = thisNewGlyph.layers[thisLayer.associatedMasterId]
                if thisLayer.shapes:
                    thisNewLayer.shapes = [thisShape.copy() for thisShape in thisLayer.shapes]
                    thisNewLayer.width = thisLayer.width

        listSuffixedGlyphs.append(thisNewGlyph)

        # Remove bracket layers from suffixed glyphs
        listLayersToRemove = [thisLayer for thisLayer in thisNewGlyph.layers if "[" in thisLayer.name or "]" in thisLayer.name]
        for thisLayer in listLayersToRemove:
            del thisNewGlyph.layers[thisLayer.layerId]

    return listSuffixedGlyphs

def updateComponentsInSuffixedGlyphs(thisFont, strSuffix):
    """Update components in suffixed glyphs so they correctly reference their respective suffixed originals."""
    for thisGlyph in thisFont.glyphs:
        if thisGlyph.name.endswith(strSuffix):  # Only process suffixed glyphs
            strBaseName = thisGlyph.name.replace(strSuffix, "")  # Get the base glyph name
            thisBaseGlyph = thisFont.glyphs[strBaseName]

            if not thisBaseGlyph:
                continue  # Skip if no original base glyph exists
            
            for thisLayer in thisGlyph.layers:
                for thisComponent in thisLayer.components:
                    strOriginalComponentName = thisComponent.componentName
                    if strOriginalComponentName.endswith(strSuffix):
                        continue  # If already correct, skip

                    strSuffixedComponentName = strOriginalComponentName + strSuffix
                    if thisFont.glyphs[strSuffixedComponentName]:  # Check if suffixed version exists
                        thisComponent.componentName = strSuffixedComponentName

def eraseBracketLayers(listGlyphs):
    """Erase bracket layers from the provided glyphs."""
    for thisGlyph in listGlyphs:
        thisGlyph.layers = [thisLayer for thisLayer in thisGlyph.layers if "[" not in thisLayer.name and "]" not in thisLayer.name]

def addCustomParametersToInstances(thisFont, strSuffix, listBracketGlyphs, listComponentGlyphs):
    """Generate custom parameters for all instances."""
    strRemoveGlyphsValue = f"*.{strSuffix.lstrip('.')}"
    listRenameGlyphsValue = []

    # Extract names from glyph lists
    listBracketGlyphNames = [thisGlyph.name.replace(strSuffix, "") for thisGlyph in listBracketGlyphs]
    listComponentGlyphNames = [thisGlyph.replace(strSuffix, "") for thisGlyph in listComponentGlyphs]

    # Rename Glyphs parameter: Combine bracket and component glyphs
    listRenameGlyphsValue += [f"{strName}={strName}{strSuffix}" for strName in listBracketGlyphNames]
    listRenameGlyphsValue += [f"{strName}={strName}{strSuffix}" for strName in listComponentGlyphNames]

    # Add the custom parameters to all exportable instances
    for thisInstance in thisFont.instances:
        if thisInstance.type == 0:  # Exportable instance
            if STR_REMOVE_GLYPHS not in {thisParam.name for thisParam in thisInstance.customParameters}:
                thisInstance.customParameters.append(GSCustomParameter(STR_REMOVE_GLYPHS, strRemoveGlyphsValue))
            if STR_RENAME_GLYPHS not in {thisParam.name for thisParam in thisInstance.customParameters}:
                thisInstance.customParameters.append(GSCustomParameter(STR_RENAME_GLYPHS, ", ".join(listRenameGlyphsValue)))

def createNewTabWithSwitchGlyphs(thisFont, listSuffixedGlyphs, listComponentGlyphs):
    """Open a new tab in Glyphs with .switch glyphs organized into Non-Component and Component sections."""
    setSuffixedGlyphNames = {thisGlyph.name for thisGlyph in listSuffixedGlyphs}
    listNonComponentGlyphs = sorted(setSuffixedGlyphNames - set(listComponentGlyphs))
    listComponentGlyphs = sorted(listComponentGlyphs)

    strNonComponentHeader = "Created Glyphs:\n" + " ".join(f"/{strName}" for strName in listNonComponentGlyphs)
    strComponentHeader = "Components:\n" + " ".join(f"/{strName}" for strName in listComponentGlyphs)
    strTabContent = f"{strNonComponentHeader}\n\n{strComponentHeader}"

    thisFont.newTab(strTabContent)

def extractSuffix(strLayerName, strSuffix):
    """Extract the suffix from a layer name."""
    listParts = strLayerName.split('[')[0].split('.')
    return listParts[-1] if len(listParts) > 1 and listParts[-1] != strSuffix.strip('.') else strSuffix.strip('.')

def getOriginalComponents(strGlyphName, dictCache={}):
    """Recursively find all base component glyphs for a given glyph with memoization."""
    if strGlyphName in dictCache:
        return dictCache[strGlyphName]

    setBaseComponents = set()
    thisGlyph = Font.glyphs[strGlyphName]
    if not thisGlyph:
        dictCache[strGlyphName] = setBaseComponents
        return setBaseComponents

    for thisLayer in thisGlyph.layers:
        for thisComponent in thisLayer.components:
            strBaseGlyphName = thisComponent.componentName
            if strBaseGlyphName not in setBaseComponents:
                setBaseComponents.add(strBaseGlyphName)
                setBaseComponents.update(getOriginalComponents(strBaseGlyphName, dictCache))  # Recursive call

    dictCache[strGlyphName] = setBaseComponents  # Store result in cache
    return setBaseComponents

def generateFeatureCode(strSuffix):
    """Create rlig and rvrn feature code automatically from suffix, accounting for nested components efficiently."""
    dictBracketLayerGlyphs = defaultdict(list)
    listFontGlyphs = Font.glyphs  # Cache the glyphs

    # Step 1: Precompute Bracket Layer Glyphs
    dictGlyphBracketLayers = {}
    for thisGlyph in listFontGlyphs:
        listBracketLayers = [thisLayer for thisLayer in thisGlyph.layers if '[' in thisLayer.name and ']' in thisLayer.name]
        if listBracketLayers:
            dictGlyphBracketLayers[thisGlyph.name] = listBracketLayers

    # Step 2: Populate Substitution Dictionary
    for strGlyphName, listBracketLayers in dictGlyphBracketLayers.items():
        for thisLayer in listBracketLayers:
            strConditionValues = thisLayer.name.split('[')[1].split(']')[0]

            strSuffixExtracted = extractSuffix(thisLayer.name, strSuffix)
            strGlyphWithSuffix = f"{strGlyphName}.{strSuffixExtracted}"

            if strGlyphWithSuffix not in dictBracketLayerGlyphs[strConditionValues]:
                dictBracketLayerGlyphs[strConditionValues].append(strGlyphWithSuffix)

    # Step 3: Process Components Efficiently Using Precomputed Base Glyphs
    dictComponentCache = {}  # Cache to store component mappings
    for thisGlyph in listFontGlyphs:
        if thisGlyph.name not in dictComponentCache:
            dictComponentCache[thisGlyph.name] = getOriginalComponents(thisGlyph.name)  # Compute components once

        for strBaseGlyphName in dictComponentCache[thisGlyph.name]:
            if strBaseGlyphName in dictGlyphBracketLayers:
                for strCondition, listGlyphNames in dictBracketLayerGlyphs.items():
                    for strGlyphWithSuffix in listGlyphNames:
                        listBaseNameParts = strGlyphWithSuffix.split('.')
                        strBaseName = ".".join(listBaseNameParts[:-1])
                        strSuffixExtracted = listBaseNameParts[-1]

                        if strBaseName == strBaseGlyphName and f"{thisGlyph.name}.{strSuffixExtracted}" not in dictBracketLayerGlyphs[strCondition]:
                            dictBracketLayerGlyphs[strCondition].append(f"{thisGlyph.name}.{strSuffixExtracted}")

    # Step 4: Generate the Feature Code
    listRligOutput = ["#ifdef VARIABLE"]
    listRvrnOutput = ["#ifdef VARIABLE"]

    for strCondition, listGlyphNames in dictBracketLayerGlyphs.items():
        strCondition = strCondition.replace('‹', ' < ').replace('wg', 'wght').replace('wd', 'wdth').replace('oz', 'opsz').replace('it', 'ital').replace('sl', 'slnt').replace('\u2009', ' ')
        listRligOutput.append(f"condition {strCondition};")
        listRvrnOutput.append(f"condition {strCondition};")

        for strGlyphWithSuffix in sorted(listGlyphNames):
            strOriginalGlyphName = ".".join(strGlyphWithSuffix.split('.')[:-1])
            listRligOutput.append(f"sub {strOriginalGlyphName} by {strGlyphWithSuffix};")
            listRvrnOutput.append(f"sub {strOriginalGlyphName} by {strGlyphWithSuffix};")

        listRligOutput.append("")
        listRvrnOutput.append("")

    listRligOutput.append("#endif")
    listRvrnOutput.append("#endif")

    # Step 5: Add the feature to the font
    addOrUpdateFeature(Font, "rlig", "\n".join(listRligOutput))
    addOrUpdateFeature(Font, "rvrn", "\n".join(listRvrnOutput))

def addOrUpdateFeature(thisFont, strFeatureTag, strFeatureCode):
    """Adds or updates a feature with the given tag and code in the font."""
    thisFeature = thisFont.features[strFeatureTag] if strFeatureTag in {thisFeature.name for thisFeature in thisFont.features} else GSFeature(strFeatureTag)
    thisFeature.code = strFeatureCode
    if strFeatureTag not in {thisFeature.name for thisFeature in thisFont.features}:
        thisFont.features.append(thisFeature)

def showFinalReport(intTotalBracketGlyphs, intTotalComponents, listSuffixedGlyphs, listComponentGlyphs, thisFont, boolEraseBrackets, boolAddCustomParams, boolAddFeatures):
    """Display the final report in a Vanilla window."""
    strEraseBracketsStatus = "On" if boolEraseBrackets else "Off"
    strAddCustomParamsStatus = "On" if boolAddCustomParams else "Off"
    strAddFeaturesStatus = "On" if boolAddFeatures else "Off"

    strBracketGlyphsList = ", ".join(sorted(thisGlyph.name for thisGlyph in listSuffixedGlyphs))
    strComponentGlyphsList = ", ".join(sorted(listComponentGlyphs))

    strRenameGlyphsText = ""
    if boolAddCustomParams and len(thisFont.instances) > 1:
        thisInstance = thisFont.instances[1]
        for thisParam in thisInstance.customParameters:
            if thisParam.name == STR_RENAME_GLYPHS:
                strRenameGlyphsText = thisParam.value
                break

    strCustomParamsText = ""
    if boolAddCustomParams:
        strCustomParamsText = (
            f"Custom Parameters:\n"
            f"Added '{STR_REMOVE_GLYPHS}': *.switch\n"
            f"Added '{STR_RENAME_GLYPHS}': {strRenameGlyphsText}\n"
        )

    strReportText = (
        f"INITIAL SEARCH:\n"
        f"Glyphs with Bracket Layers: {intTotalBracketGlyphs}\n"
        f"Components from Bracket Layers: {intTotalComponents}\n"
        f"Total Glyphs + Components with Bracket Layers = {intTotalBracketGlyphs + intTotalComponents}\n\n"
        f"CREATED GLYPHS:\n"
        f"· Suffixed glyphs created: {len(listSuffixedGlyphs)}\n"
        f"· Suffixed glyphs from components created: {intTotalComponents}\n"
        f"· Total Suffixed Glyphs + Components created = {len(listSuffixedGlyphs) + intTotalComponents}\n\n"
        f"OTHER ACTIONS:\n"
        +
        (f"· Added custom parameters\n" if strAddCustomParamsStatus == "On" else "") +
        (f"· Add rlig & rvr features\n" if strAddFeaturesStatus == "On" else "") +
        (f"· Erased existing bracket layers\n" if strEraseBracketsStatus == "On" else "") +
        "\n\n"
        "Note: Please determine if you need to switch in the alternate glyph or not, in the 'Rename Glyphs' custom parameter."
    )

    class FinalReportWindow:
        """Display a Vanilla UI window showing the final report."""
        def __init__(self):
            self.uiWindow = vanilla.Window((600, 500), "Final Report", minSize=(600, 500))
            self.uiWindow.txtReport = vanilla.TextEditor((10, 10, -10, -40), strReportText, readOnly=True)
            self.uiWindow.btnClose = vanilla.Button((-100, -30, -10, 20), "Close", callback=self.closeWindow)
            self.uiWindow.open()
        
        def closeWindow(self, sender):
            """Close the report window."""
            self.uiWindow.close()

    FinalReportWindow()

# =============================
# Main Execution
# =============================

def executeMainScript(strSuffix, boolAddFeatures, boolAddCustomParams, boolEraseBrackets, boolOpenInNewTab):
    """Main function to execute the entire process of alternate glyph generation."""
    thisFont = Glyphs.font  # Ensure the font is accessed in the function scope
    if not thisFont:
        print("--- ERROR: No font is open. Please open a font and try again.")
        return

    # Step 1: Collect glyphs with bracket layers
    listBracketGlyphs = collectBracketLayerGlyphs(thisFont)
    if not listBracketGlyphs:
        print("--- ERROR: No bracket layers found.")
        return

    # Step 2: Build a component dependency map
    dictComponentMap = createComponentMapping(thisFont)

    # Step 3: Find all affected components
    setAffectedComponents = set()
    for thisGlyph in listBracketGlyphs:
        setAffectedComponents.update(identifyAffectedComponents(thisGlyph, dictComponentMap))

    # Step 4: Generate feature code if required
    if boolAddFeatures:
        generateFeatureCode(strSuffix)

    # Step 5: Create and update suffixed glyphs
    listSuffixedGlyphs = createSuffixedGlyphs(listBracketGlyphs, thisFont, strSuffix)

    # Step 6: Create new component glyphs from affected components
    setComponentGlyphsCreated = set()
    for strGlyphName in setAffectedComponents:
        thisGlyph = thisFont.glyphs[strGlyphName]
        strNewGlyphName = strGlyphName + strSuffix
        if thisGlyph and strNewGlyphName not in thisFont.glyphs:
            thisDuplicatedGlyph = thisGlyph.copy()
            thisDuplicatedGlyph.name = strNewGlyphName
            thisFont.glyphs.append(thisDuplicatedGlyph)
            setComponentGlyphsCreated.add(thisDuplicatedGlyph.name)

    # Step 7: Update components in suffixed glyphs
    updateComponentsInSuffixedGlyphs(thisFont, strSuffix)

    # Step 8: Add custom parameters to instances if enabled
    if boolAddCustomParams:
        addCustomParametersToInstances(thisFont, strSuffix, listSuffixedGlyphs, setComponentGlyphsCreated)

    # Step 9: Erase bracket layers from original glyphs if enabled
    if boolEraseBrackets:
        eraseBracketLayers(listBracketGlyphs)

    # Step 10: Open new tab with generated glyphs if enabled
    if boolOpenInNewTab:
        createNewTabWithSwitchGlyphs(thisFont, listSuffixedGlyphs, setComponentGlyphsCreated)

    # Step 11: Show final report
    showFinalReport(
        len(listSuffixedGlyphs),
        len(setComponentGlyphsCreated),
        listSuffixedGlyphs,
        setComponentGlyphsCreated,
        thisFont,
        boolEraseBrackets,
        boolAddCustomParams,
        boolAddFeatures,
    )

class SuffixInputWindow:
    """Vanilla UI window for user input options."""
    def __init__(self):
        self.uiWindow = vanilla.Window((300, 240), "Set Alternate Glyphs Options", minSize=(300, 240))

        # UI Elements
        self.uiWindow.txtLabel = vanilla.TextBox((15, 15, -15, 20), "Enter the desired suffix for alternate glyphs:")
        self.uiWindow.inputField = vanilla.EditText((15, 40, -15, 20), STR_DEFAULT_SUFFIX)
        self.uiWindow.chkCustomParams = vanilla.CheckBox((15, 70, -15, 20), "Add custom parameters to instances", value=True)
        self.uiWindow.chkFeatures = vanilla.CheckBox((15, 100, -15, 20), "Add feature code", value=True)
        self.uiWindow.chkOpenTab = vanilla.CheckBox((15, 130, -15, 20), "Open in a new tab", value=True)
        self.uiWindow.chkErase = vanilla.CheckBox((15, 160, -15, 20), "Erase existing bracket layers", value=False)
        self.uiWindow.btnGenerate = vanilla.Button((15, 200, -15, 20), "Generate Alternate Glyphs", callback=self.generateOutput)

        self.uiWindow.open()

    def generateOutput(self, sender):
        """Extract input values and execute the process."""
        strSuffix = self.uiWindow.inputField.get()
        boolEraseBrackets = self.uiWindow.chkErase.get()
        boolAddCustomParams = self.uiWindow.chkCustomParams.get()
        boolAddFeatures = self.uiWindow.chkFeatures.get()
        boolOpenInNewTab = self.uiWindow.chkOpenTab.get()
        self.uiWindow.close()

        executeMainScript(strSuffix, boolAddFeatures, boolAddCustomParams, boolEraseBrackets, boolOpenInNewTab)

# Run the UI Window
SuffixInputWindow()