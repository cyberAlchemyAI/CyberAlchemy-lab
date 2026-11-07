#!/usr/bin/env python3
"""Source-distribution launcher. Installed users use define-standalone or define-api."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from define_core import main
raise SystemExit(main())
