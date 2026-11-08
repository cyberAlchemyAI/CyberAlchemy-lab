"""Disposable foreign same-UID RW mount holder; performs no file writes."""

import json
import os
import sys
import time


run_id = sys.argv[1]
if (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) != (20001, 20001, 20001, 20001):
    raise SystemExit("COMPETITOR_ID_CHANGED")
if not os.path.isdir("/lab/instances"):
    raise SystemExit("VOLUME_NOT_MOUNTED")
print(json.dumps({"event": "FOREIGN_RW_READY", "run_id": run_id},
                 sort_keys=True), flush=True)
time.sleep(8)
