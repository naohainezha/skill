#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import sys

print("Starting Xiaohongshu Crawler V4.0...")
print("=" * 50)

try:
    subprocess.call([sys.executable, "crawler_v4.py"])
except KeyboardInterrupt:
    print("\nInterrupted by user")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Done!")
input("Press Enter to exit...")
