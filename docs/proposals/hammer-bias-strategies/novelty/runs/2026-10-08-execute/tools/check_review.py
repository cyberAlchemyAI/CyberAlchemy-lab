#!/usr/bin/env python3
import argparse,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser();a.add_argument('phase');a.add_argument('case');a.add_argument('judge');q=a.parse_args()
f=R/'reviews'/f'{q.phase}-{q.case}-{q.judge}.json';d=json.loads(f.read_text());m=json.loads((R/'blinded'/q.phase/q.case/'manifest.json').read_text());errors=[]
family_ids=[x['id'] for x in d['families']]
if len(family_ids)!=len(set(family_ids)):errors.append('duplicate family IDs')
pairs={x['packet_id']:x for x in d['pairs']}
if set(pairs)!={x['packet_id'] for x in m['packets']}:errors.append('pair coverage mismatch')
for pk in m['packets']:
 p=json.loads(Path(pk['file']).read_text());j=pairs.get(p['packet_id'],{});raw=[x for lane in p['raw'] for x in lane['openings']];ids={x['id'] for x in raw}
 for field,key in [('raw','id'),('retention','raw_id')]:
  entries=j.get(field,[])
  if len(entries)!=len(ids) or {x.get(key) for x in entries}!=ids:errors.append(p['packet_id']+': '+field+' coverage')
 for x in j.get('raw',[]):
  if x['family'] not in family_ids:errors.append('unknown family')
  if x['usefulness'] not in [0,1,2] or x['observability'] not in [0,1,2]:errors.append('score enum')
  if x['fit'] not in ['preserves','uncertain','conditional','violates']:errors.append('fit enum')
 for x in j.get('retention',[]):
  if x['status'] not in ['retained','lost','uncertain']:errors.append('retention enum')
print(json.dumps({'valid':not errors,'errors':errors,'pairs':len(pairs),'families':len(family_ids)},indent=2))
raise SystemExit(bool(errors))
