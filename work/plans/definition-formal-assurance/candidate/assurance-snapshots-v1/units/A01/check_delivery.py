"""Read-only phase delivery integrity check; future phase additions allowed."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
LAB=HERE.parents[6]


def check():
    manifest=json.loads((HERE/'delivery-manifest.json').read_text())
    rows=manifest['files']
    if len({r['path'] for r in rows})!=len(rows):raise ValueError('Duplicate manifest path')
    for row in rows:
        path=(LAB/row['path']).resolve()
        if not path.is_relative_to(LAB):raise ValueError('Manifest path outside repository')
        if path.stat().st_size!=row['size_bytes'] or hashlib.sha256(path.read_bytes()).hexdigest()!=row['sha256']:
            raise ValueError('Changed phase delivery artifact: '+row['path'])
    return {'result':'PASS','files':len(rows),'authority_effect':'none','meaning':'Exact artifacts from foundations and A01 delivery; later phase additions allowed; no semantic assurance claim.'}


if __name__=='__main__':print(json.dumps(check(),indent=2))
