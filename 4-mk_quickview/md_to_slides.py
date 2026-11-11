#!/usr/bin/env python3
"""Forwarding shim: md_to_slides.py now lives in 6-ppt-create/ (Markdown input adapter)."""
import os
import sys
from pathlib import Path

target = Path(__file__).resolve().parent.parent / "6-ppt-create" / "md_to_slides.py"
os.execv(sys.executable, [sys.executable, str(target), *sys.argv[1:]])
