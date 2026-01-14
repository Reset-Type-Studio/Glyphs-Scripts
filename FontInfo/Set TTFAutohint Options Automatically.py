# MenuTitle: 🖥️ Set TTFAutohint Options Automatically
# -*- coding: utf-8 -*-
# Version: 1.1
# Description: Adds “TTFAutohint options” parameter for every export, calculating every "Fallback Stem Width" from "Stems"
# Author: Fernando Díaz (Reset Type Studio) with help from AI.

import GlyphsApp
from GlyphsApp import GSCustomParameter
from vanilla import Window, TextBox, EditText, CheckBox, PopUpButton, Button

# ────────────────────────────────────────────────────────────────
# Presets: Sans / Serif × UI / Text / Display
# ────────────────────────────────────────────────────────────────
PRESETS = {
    "UI · Sans": {
        "min": "6",
        "max": "48",
        "limit": "50",
        "exceptions": ""
    },
    "Text · Sans": {
        "min": "7",
        "max": "48",
        "limit": "50",
        "exceptions": ""
    },
    "Display · Sans": {
        "min": "8",
        "max": "56",
        "limit": "60",
        "exceptions": ""
    },
    "UI · Serif": {
        "min": "7",
        "max": "48",
        "limit": "50",
        "exceptions": ""
    },
    "Text · Serif": {
        "min": "8",
        "max": "48",
        "limit": "50",
        "exceptions": ""
    },
    "Display · Serif": {
        "min": "9",
        "max": "60",
        "limit": "65",
        "exceptions": ""
    },
    "Custom": {}
}

class TTFHintOptionsWindow:
    def __init__(self):
        self.w = Window((400, 650), "TTFAutohint Options")

        self.font = Glyphs.font
        if not self.font:
            Message("No font open", "Please open a font first.")
            return

        y = 10
        self.w.presetLabel = TextBox((15, y, -15, 20), "Preset:")
        y += 20
        self.w.presetPop = PopUpButton((15, y, -15, 22), list(PRESETS.keys()), callback=self.applyPreset)
        y += 30

        self.w.minLabel = TextBox((15, y, -15, 20), "Hint set range Minimum:")
        y += 22
        self.w.minEdit = EditText((15, y, -15, 22), "")
        y += 30

        self.w.maxLabel = TextBox((15, y, -15, 20), "Hint set range Maximum:")
        y += 22
        self.w.maxEdit = EditText((15, y, -15, 22), "")
        y += 30

        self.w.defaultScriptLabel = TextBox((15, y, -15, 20), "Default Script:")
        y += 22
        self.w.defaultScriptEdit = EditText((15, y, -15, 22), "latn")
        y += 30

        self.w.fallbackScriptLabel = TextBox((15, y, -15, 20), "Fallback Script:")
        y += 22
        self.w.fallbackScriptEdit = EditText((15, y, -15, 22), "latn")
        y += 30

        self.w.limitLabel = TextBox((15, y, -15, 20), "Hinting Limit:")
        y += 22
        self.w.limitEdit = EditText((15, y, -15, 22), "")
        y += 30

        self.w.exceptionsLabel = TextBox((15, y, -15, 20), "xHeight Snapping Exceptions (optional):")
        y += 22
        self.w.exceptionsEdit = EditText((15, y, -15, 22), "")
        y += 30

        # TTFAutohint flag toggles
        self.w.adjustSubglyphs = CheckBox((15, y, -15, 20), "Adjust Subglyphs (--adjust-subglyphs)", value=False)
        y += 24
        self.w.dehint = CheckBox((15, y, -15, 20), "Dehint (--dehint)", value=False)
        y += 24
        self.w.detailedInfo = CheckBox((15, y, -15, 20), "Detailed Info (--detailed-info)", value=False)
        y += 24
        self.w.hintComposites = CheckBox((15, y, -15, 20), "Hint Composites (--composites)", value=False)
        y += 24
        self.w.ignoreRestrictions = CheckBox((15, y, -15, 20), "Ignore Restrictions (--ignore-restrictions)", value=True)
        y += 24
        self.w.noInfo = CheckBox((15, y, -15, 20), "No Autohint Info (--no-info)", value=False)
        y += 24
        self.w.symbolFont = CheckBox((15, y, -15, 20), "Symbol Font (--symbol)", value=False)
        y += 24
        self.w.ttfaTable = CheckBox((15, y, -15, 20), "TTFA Table (--ttfa-table)", value=False)
        y += 24
        self.w.winCompat = CheckBox((15, y, -15, 20), "Windows Compatibility (--windows-compatibility)", value=True)
        y += 30

        self.w.applyButton = Button((15, y, -15, 30), "Apply to All Instances", callback=self.applyOptions)

        self.applyPreset(None)  # Load defaults
        self.w.open()

    def applyPreset(self, sender):
        presetName = self.w.presetPop.getItems()[self.w.presetPop.get()]
        p = PRESETS.get(presetName, {})

        self.w.minEdit.set(p.get("min", "6"))
        self.w.maxEdit.set(p.get("max", "48"))
        self.w.limitEdit.set(p.get("limit", "50"))
        self.w.exceptionsEdit.set(p.get("exceptions", ""))

    def applyOptions(self, sender):
        font = self.font
        opts = [
            f"--hinting-range-min={self.w.minEdit.get()}",
            f"--hinting-range-max={self.w.maxEdit.get()}",
            f"--default-script={self.w.defaultScriptEdit.get()}",
            f"--fallback-script={self.w.fallbackScriptEdit.get()}",
            f"--hinting-limit={self.w.limitEdit.get()}",
        ]

        exceptions = self.w.exceptionsEdit.get().strip()
        if exceptions:
            opts.append(f"--x-height-snapping-exceptions={exceptions}")

        # Boolean flags
        if self.w.adjustSubglyphs.get():
            opts.append("--adjust-subglyphs")
        if self.w.dehint.get():
            opts.append("--dehint")
        if self.w.detailedInfo.get():
            opts.append("--detailed-info")
        if self.w.hintComposites.get():
            opts.append("--composites")
        if self.w.ignoreRestrictions.get():
            opts.append("--ignore-restrictions")
        if self.w.noInfo.get():
            opts.append("--no-info")
        if self.w.symbolFont.get():
            opts.append("--symbol")
        if self.w.ttfaTable.get():
            opts.append("--ttfa-table")
        if self.w.winCompat.get():
            opts.append("--windows-compatibility")

        applied = 0
        for inst in font.instances:
            if not inst.exports:
                continue

            stem = self.getFallbackStem(inst)
            if stem is None:
                continue

            full_opts = opts + [f"--fallback-stem-width={stem}"]

            # Remove existing TTFAutohint options
            inst.customParameters = [
                cp for cp in inst.customParameters
                if cp.name != "TTFAutohint options"
            ]

            inst.customParameters.append(
                GSCustomParameter("TTFAutohint options", " ".join(full_opts))
            )

            applied += 1

        Message(
            "Fallback Stem Widths calculated automatically.",
            f"TTFAutohint options applied."
        )

    def getFallbackStem(self, inst):
        iFont = inst.interpolatedFont
        if not iFont:
            return None
        for metric in iFont.stems:
            if not metric.horizontal:
                master = iFont.masters[0]
                for key in (metric.id, metric.name):
                    try:
                        return int(round(master.stems[key]))
                    except:
                        continue
        return None

TTFHintOptionsWindow()
