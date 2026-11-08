#!/usr/bin/env python3
"""Host must verify runner/helper bytes against reviewed pins before invocation."""
from pathlib import Path
import sys

ROOT = Path(__file__).absolute().parents[1]
DEPS = Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps')
sys.path[:0] = [str(ROOT / 'contracts'), str(ROOT / 'selectors'), str(DEPS)]
from lab_selectors.runner import main

if __name__ == '__main__':
    raise SystemExit(main())
