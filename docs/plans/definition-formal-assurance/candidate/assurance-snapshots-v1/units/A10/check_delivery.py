"""Check sealed/prior review bytes and exact pending owner boundaries."""
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;sys.path.insert(0,str(UNIT));import validate_review as v


def main():
    manifests={}
    for path in [v.BASE/'units/A09/delivery-manifest.json',UNIT/'delivery-manifest.json']:
        rows=json.loads(path.read_bytes())['files']
        if len({row['path'] for row in rows})!=len(rows):raise ValueError('Duplicate delivery identity')
        for row in rows:v.bound(row)
        manifests[path.relative_to(v.ROOT).as_posix()]=len(rows)
    receipt=json.loads((UNIT/'receipt.json').read_bytes())
    for row in receipt['inputs']+receipt['outputs']:v.bound(row)
    if receipt['unit_id']!='A10.1' or receipt['authority_effect']!='none' or receipt['goal_status']!='active' or receipt['owner_review_disposition']['status']!='pending' or receipt['owner_review_disposition']['reviewer_principal_ref'] is not None:raise ValueError('False completion or owner review')
    v.main()
    print(json.dumps({'delivery_status':'PASS','authority_effect':'none','delivery_manifests':manifests,'owner_review':'pending','task_disposition':'Exact packet prepared and pending-review alternative recorded; actual owner review not complete.','semantic_admission':'not-requested','goal_status':'active','next_ready_unit':'E04.1'},indent=2,sort_keys=True))


if __name__=='__main__':main()
