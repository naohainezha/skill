#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys
import os

print("=" * 50)
print("  Xiaohongshu Crawler V3.0 Launcher")
print("=" * 50)
print()

# Check Python version
print(f"[1/3] Python version: {sys.version.split()[0]}")

# Check dependencies
print("[2/3] Checking dependencies...")
try:
    import playwright
    print("      playwright installed")
except ImportError:
    print("      Installing playwright...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright"])

# Install browser
print("[3/3] Installing Playwright browser...")
try:
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
except Exception as e:
    print(f"      Warning: {e}")

print()
print("Starting crawler V3.0...")
print("=" * 50)
print()

# Run crawler
try:
    subprocess.call([sys.executable, "crawler_v3.py"])
except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"\nError: {e}")

print()
print("=" * 50)
print("Done!")
print("=" * 50)
