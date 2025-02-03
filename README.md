# Glyphs Scripts Collection by Reset Type Studio 🧑🏻‍💻

(Under construction) This is a collection of scripts designed to streamline workflows in **Glyphs App**. 

---
  
## **Available Scripts:**
 
### **Bracket Layers**

- **💫 Bracket Layers → Alternate Glyphs (Switching Shapes Method)**
  - The Bracket Layer Method does not work in Illustrator and other Adobe apps, to make it work, you need to use the Alternate Glyphs Method instead.
  - This script automates the creation of suffixed glyphs, their components, custom parameters, and feature code for the *Alternate Glyphs* method found in the *Switching Shapes* tutorial: https://glyphsapp.com/learn/switching-shapes

- **🖥️ New Tab with Glyphs containing Bracket Layers**
  - Opens a new tab in Glyphs containing bracket-layered glyphs, followed by glyphs that use these as components.

- **📄 Report Glyphs containing Bracket Layers**
  - Lists glyphs with bracket layers and their affected glyphs (including nested components).

### **Components**

- **🔁 Component Swapper (all masters)**
  - Assigns values to smart components in selected glyphs for all axes and masters.
    
- **⛓️‍💥 Decompose Specific Components (all masters)**
  - Decomposes only the specified component (and nested components) in all masters.

### **Smart Components**

- **🔢 Values for Smart Components (all masters)**
  - Swaps a component in selected glyphs, works in all masters.
    
- **🧠 Selected to Smart Components (all masters)**
  - Converts selected glyphs into smart components based on font master axes.
 
- **🤯 Smart to Normal Components (all masters)**
  - Converts selected smart components back to normal components.

### **Font-Info**

- **📊 Copy Axis Coordinates to Location (Custom Parameter)**
  - Applies the "Axis Location" custom parameter to each master and export instance.
  - Automatically detects variable font exports (skipping them if needed).

### **KernOn**
- **🧨 Delete KernOn**
  - Clears all kerning pairs and resets kerning groups for all masters in Glyphs.

### **Paths**

- **🔘 Node Duplicator (All Masters)**
  - Duplicates selected nodes in all masters.

- **🔘 Node Duplicator (Current Layer)**
  - Duplicates selected nodes only in the current layer.

### **Transformations**

- **🛠️ Transformations Tool (for All Masters)**
  - Apply transformations (scaling, rotation, slanting, translation) across all masters in a font.
 
### **Exports**

- **🎁 Trial Font Maker**
  - This script creates the Trial versions of fonts. It works on a duplicate of the glyphs file, adds prefix to the font family name and instances, it removes all features and keeps only a selected set of glyphs before exporting them. 

---

## Installation & Usage
1. Download or clone this repository.
2. Place the scripts in the Glyphs **Scripts** folder: - `~/Library/Application Support/Glyphs/Scripts/`

## Contributions & Feedback
- Found a bug? Want to add a new feature? 
- Feel free to contribute improvements via Pull Requests.

## Acknowledgements
- Thanks to Peter Nowell for teaching me Python for Glyphs 
- In some scripts I used the help of IA, specially for Vanilla stuff (sorry Peter)

## License
Copyright 2025 Fernando Díaz & Reset Type Studio.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
