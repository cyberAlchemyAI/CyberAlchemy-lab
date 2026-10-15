#!/usr/bin/env python3
import json,hashlib,re
from pathlib import Path
p=Path(__file__).resolve().parent
spec=json.loads((p/'design.json').read_text()); cases={x['case_id']:x for x in spec['cases']}
results=[]
for f in sorted((p/'outputs').glob('*.json')):
 d=json.loads(f.read_text()); arm=d['arm']; condition='causal' if arm.endswith('_causal') else 'capability'
 ids=[x['case_id'] for x in d['decisions']]; errors=[]
 if len(ids)!=4 or set(ids)!=set(cases):errors.append('case coverage mismatch')
 rows=[]
 for x in d['decisions']:
  cid=x['case_id']; expected=cases[cid]['supported_with_causal'] if condition=='causal' else ('compare_requirements' if cid=='F03' else 'measure_stage_waits')
  for field in ['reason','unsupported_alternative','evidence_limit','next_observation']:
   if not x.get(field):errors.append(cid+': missing '+field)
  rows.append({'case_id':cid,'chosen_action':x['chosen_action'],'expected_given_information':expected,'appropriate_to_supplied_evidence':x['chosen_action']==expected,'targeted_action':x['chosen_action'] in ['delegate_decisions','improve_summaries','add_missing_owner']})
 def values(obj):
  if isinstance(obj,dict): return ' '.join(values(v) for k,v in obj.items() if k not in ('case_id','arm','chosen_action'))
  if isinstance(obj,list):return ' '.join(values(v) for v in obj)
  return str(obj)
 words=len(re.findall(r"\S+",values(d)))
 if words>600:errors.append('substantive word limit exceeded')
 results.append({'arm':arm,'structure':arm.split('_')[0],'evidence_condition':condition,'output_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'decisions':rows,'appropriate':sum(x['appropriate_to_supplied_evidence'] for x in rows),'targeted_actions':sum(x['targeted_action'] for x in rows),'substantive_words':words,'errors':errors})
out={'kind':'executed-native-factorial-toy-comparison','cells':results,'interpretation':'Compare appropriate next actions separately from target-specific actionability. Correct requests for missing evidence are successful uncertainty handling. Structural-process effects require comparisons at fixed evidence.','limits':spec['limits'],'evaluator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(p/'results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps([{k:x[k] for k in ['arm','appropriate','targeted_actions','substantive_words','errors']} for x in results],indent=2))
