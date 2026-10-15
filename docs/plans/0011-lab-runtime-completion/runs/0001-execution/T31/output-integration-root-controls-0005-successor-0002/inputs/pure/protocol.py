"""Owned inert test namespace only; never an API import or production alias."""
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent.parent/'postimages/product/lab/release-candidates/v1/interface/api-integration-v17'

import json
def compact(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
