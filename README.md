# Brother HL-1200 / GDI Print Helper for Linux & OpenWrt

GUI application written in Python/GTK3 to fix the out of memory / LED error when printing PDFs or images to low-RAM GDI printers (Brother HL-1200, HL-1110) connected via OpenWrt (p910nd) or CUPS.

## Features
- Auto-rotate Landscape to A4.
- Threshold Binarization (1-bit) to trigger RLE compression (<150KB per page).
- Direct CUPS dispatch bypassing desktop environment overrides.

## Author
Developed by Gustavo & Hornero AI Assistant.
License: MIT
