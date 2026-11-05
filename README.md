# 🖨️ Brother HL-1200 / GDI Print Helper for Linux & OpenWrt

A GTK3 GUI utility to print PDFs and images reliably to low-memory GDI printers (such as Brother HL-1200, HL-1110, HL-1210W) connected via OpenWrt (`p910nd`) or CUPS.

---

## 🛑 The Problem

GDI laser printers rely on host-based rendering and have minimal onboard memory (e.g. **1 MB RAM**). 

When printing high-density documents, A3 sheets, or complex PDFs from Linux:
- CUPS / `brlaser` generates large uncompressed raster buffers.
- The printer memory overflows or encounters unexpected data headers.
- The print job fails and the printer flashes its **Error LEDs**.

---

## 💡 The Solution

This tool preprocesses the file before submitting it to the CUPS spooler:

1. **Auto-Rotate Landscape:** Detects landscape orientation (width > height) and rotates page images by -90° to fit A4 paper correctly.
2. **Clean Binarization (1-bit):** Thresholds image content to pure black-and-white. This removes grayscale noise and optimizes the stream for the printer's native RLE raster encoding.
3. **Direct CUPS Dispatch:** Sends the resulting A4 document directly to the printer using `lp` with explicit settings (`-o PageSize=A4 -o Resolution=600dpi`), bypassing desktop environment dialog overrides.

---

## 🚀 Quick Installation

### 1. Install System Dependencies (Debian / Ubuntu / Linux Mint)
```bash
sudo apt update
sudo apt install python3-gi gir1.2-gtk-3.0 python3-pil poppler-utils img2pdf -y
