#!/usr/bin/env python3
"""Explicit local Define/Lab successor; no legacy protocol replacement."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from define_lab.cli import main

raise SystemExit(main())
