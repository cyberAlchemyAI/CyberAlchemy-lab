#!/usr/bin/env python3
"""Report observed artifact word burden; no token or equal-compute inference."""
import datetime,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
schedule=read(R/'schedule.json');units=[dict(schedule['preflight'],phase='preflight',repetition=0)]+schedule['units']
if (R/'confirmation-schedule.json').exists():units+=read(R/'confirmation-schedule.json')['units']
rows=[];above=[];maximum=0
for u in units:
 roles=[]
 for role in u['roles']:
  p=R/'receipts'/f'{u["unit_id"]}-{role}.json';m=R/'prompts/jobs'/f'{u["unit_id"]}-{role}.manifest.json'
  if not p.exists():continue
  receipt=read(p);manifest=read(m);sources=[Path(x['path']) for x in manifest['source_outputs']]
  proxy=manifest['prompt_words']+sum(len(x.read_text().split()) for x in sources)
  maximum=max(maximum,proxy)
  if proxy>2500:above.append({'unit_id':u['unit_id'],'role':role,'task_input_word_proxy':proxy})
  roles.append({'role':role,'valid':receipt['artifact_validation']['valid'],'output_words':receipt['artifact_validation'].get('words'),'task_input_word_proxy':proxy})
 complete=len(roles)==len(u['roles'])
 words=[x['output_words'] for x in roles]
 rows.append({'unit_id':u['unit_id'],'phase':u['phase'],'case_id':u['case_id'],'condition':u['condition'],'repetition':u['repetition'],'all_roles_joined':complete,'roles':roles,'output_words':sum(words) if complete and all(x is not None for x in words) else None})
result={'generated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'units':rows,'max_observed_task_input_word_proxy':maximum,'above_2500_word_instruction':above,'limits':['Word counts include JSON artifact representation and are proxies, not actual token counts.','Input proxy includes task prompt and explicitly referenced source artifacts, not runtime/tool overhead.','Matched soft instructions do not establish equal compute.','Pending or missing burden is null, never zero.']}
(R/'reports/burden.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'all_roles_joined_units':sum(x['all_roles_joined'] for x in rows),'joined_roles':sum(len(x['roles']) for x in rows),'max_observed_task_input_word_proxy':maximum,'above_2500_word_instruction':above},indent=2))
