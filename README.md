# 🧩 AppExrToPSB — Automated EXR → PSB Conversion & Processing Tool for Photoshop  
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)  
[![Adobe Photoshop](https://img.shields.io/badge/Photoshop-Automation-31A8FF?logo=adobephotoshop&logoColor=white)](https://www.adobe.com/products/photoshop.html)  
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)  
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)]()

**Version:** 7.2.4 (Stable Build)  
**Author:** Phước Nguyễn  
📩 **Email:** huuphuoc12c7@gmail.com  

---

## 🧠 Overview  
AppExrToPSB is a professional automation tool that bridges EXR → PSB workflows for CGI, VFX, and visualization artists.  
It integrates tightly with Adobe Photoshop to automatically:  
- Open `.exr` files  
- Process V-Ray Cryptomatte layers  
- Save `PSB + PNG` outputs  
- Organize results under structured folders (`prepost`, `processed`)  

Perfect for heavy production environments and render pipelines that require consistent layer management and post-processing.

---

## 🚀 Key Features  
- 🖼️ **Auto Open & Convert:** Detects new EXR files and opens them directly in Photoshop.  
- 🎨 **Cryptomatte Handling:** Renames V-Ray Cryptomatte layers (`Mask_0001`, `Mask_0002`, …).  
- 💾 **Smart Save:** Exports PSB + PNG automatically while skipping already processed files.  
- ⏱️ **Timestamp Logic:** Checks PNG creation time — only reprocesses if older by ≥ 30 seconds.  
- ⚙️ **Multi-threaded Architecture:** Parallel threads for UI, Photoshop COM, and file watching.  
- 🧰 **PyQt5 Log Window:** Real-time, scrollable logging interface.  
- 🪶 **Photoshop Dialog Bypass:** Automatically dismisses pop-ups and confirmation boxes.  

---


