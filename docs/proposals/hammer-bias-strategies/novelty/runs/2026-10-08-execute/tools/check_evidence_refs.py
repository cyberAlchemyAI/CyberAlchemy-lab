#!/usr/bin/env python3
"""Check candidate citation identity only; semantic support requires review."""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def identifiers(value):
 out=set()
 if isinstance(value,dict):
  if isinstance(value.get('id'),str):out.add(value['id'])
  for v in value.values():out|=identifiers(v)
 elif isinstance(value,list):
  for v in value:out|=identifiers(v)
 return out
rows=[];bad=[]
for receipt in sorted((R/'receipts').glob('*.json')):
 try:r=json.loads(receipt.read_text())
 except json.JSONDecodeError:continue
 if not isinstance(r,dict) or not r.get('artifact_validation',{}).get('valid'):continue
 if r.get('role') not in ['Z','A','Q']:continue
 path=R/r['artifact_validation']['output'];d=json.loads(path.read_text());case=json.loads((R/'cases'/f'{d["case_id"]}.json').read_text());allowed=identifiers(case)
 for c in d.get('openings',[]):
  missing=[x for x in c.get('refs',[]) if x not in allowed];row={'unit_id':r['unit_id'],'role':r['role'],'candidate_id':c['id'],'reference_count':len(c.get('refs',[])),'unknown_refs':missing};rows.append(row)
  if missing:bad.append(row)
report={'kind':'citation-identity-check','status':'flag' if bad else 'pass_for_checked_ids','candidates_checked':len(rows),'references_checked':sum(x['reference_count'] for x in rows),'unknown_reference_rows':bad,'records':rows,'limits':['Known ID does not establish semantic support or empirical truth.','Only terminal joined valid raw-role artifacts checked; pending outputs excluded.']}
(R/'reports/evidence-reference-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))
