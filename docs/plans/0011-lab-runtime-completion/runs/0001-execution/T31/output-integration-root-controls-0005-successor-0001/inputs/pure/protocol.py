"""Owned inert test namespace only; never an API import or production alias."""
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T31/output-integration-preparation-0005/postimages/product/lab/release-candidates/v1/interface/api-integration-v17'

import json
def compact(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
