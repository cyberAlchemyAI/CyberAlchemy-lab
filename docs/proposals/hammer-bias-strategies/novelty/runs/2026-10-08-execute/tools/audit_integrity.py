#!/usr/bin/env python3
"""Inspect exact persisted evidence; does not infer method effectiveness."""
import argparse,hashlib,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 errors=[];pending=[];counts={'frozen_files':0,'native_spawns':0,'native_joins':0,'valid_role_outputs':0,'complete_units':0,'scored_complete_units':0}
 for manifest in ['freeze-manifest.json','assessment-tool-manifest.json']:
  if not (R/manifest).exists():pending.append(manifest);continue
  for row in read(manifest)['files']:
   f=R/row['path'];counts['frozen_files']+=1
   if not f.is_file() or sha(f)!=row['sha256']:errors.append('frozen bytes changed: '+row['path'])
 for row in read('inputs/manifest.json'):
  f=R/row['snapshot']
  if sha(f)!=row['sha256']:errors.append('source snapshot changed: '+row['snapshot'])
 schedule=read('schedule.json');units=[dict(schedule['preflight'],phase='preflight')]+schedule['units']
 if (R/'confirmation-schedule.json').exists():units+=read('confirmation-schedule.json')['units']
 events=[json.loads(x) for x in (R/'receipts/events.jsonl').read_text().splitlines()] if (R/'receipts/events.jsonl').exists() else []
 index={}
 for e in events:
  key=(e['unit_id'],e['role']);index.setdefault(key,[]).append(e)
  if e['event']=='spawn':counts['native_spawns']+=1
  if e['event']=='join':counts['native_joins']+=1
 for u in units:
  complete=True
  for role in u['roles']:
   uid=u['unit_id'];key=(uid,role);es=index.get(key,[]);sp=[x for x in es if x['event']=='spawn'];jo=[x for x in es if x['event']=='join']
   if len(sp)>1:errors.append(f'{uid}/{role}: repeated spawn under zero retry rule')
   if len(jo)>1:errors.append(f'{uid}/{role}: repeated join record')
   if jo and not sp:errors.append(f'{uid}/{role}: join without spawn')
   if sp and jo and (sp[0]['agent_id']!=jo[0]['agent_id'] or sp[0]['observed_at_utc']>jo[0]['observed_at_utc']):errors.append(f'{uid}/{role}: native event mismatch')
   receipt=R/'receipts'/f'{uid}-{role}.json'
   if not receipt.exists():complete=False;pending.append(f'{uid}/{role}: no terminal receipt');continue
   rc=json.loads(receipt.read_text());v=rc.get('artifact_validation',{})
   if rc['join_status']!='completed':complete=False;pending.append(f'{uid}/{role}: noncompleted join');continue
   if not v.get('valid'):complete=False;pending.append(f'{uid}/{role}: execution quality failure');continue
   of=R/v['output']
   if not of.is_file() or sha(of)!=v['sha256']:errors.append(f'{uid}/{role}: recorded output hash differs')
   pm=R/'prompts/jobs'/f'{uid}-{role}.manifest.json';pf=R/'prompts/jobs'/f'{uid}-{role}.txt'
   if not pm.exists() or not pf.exists():errors.append(f'{uid}/{role}: missing prompt binding');continue
   m=json.loads(pm.read_text())
   if sha(pf)!=m['prompt_sha256']:errors.append(f'{uid}/{role}: prompt hash differs')
   if m['case_id']!=u['case_id'] or sha(R/'cases'/f'{u["case_id"]}.json')!=m['case_sha256']:errors.append(f'{uid}/{role}: case binding differs')
   refs=m['source_outputs'];expected=[] if role in ['Z','A'] else (['Z','A'] if role=='Q' else [x for x in u['roles'] if x!='D'])
   actual=[Path(x['path']).stem for x in refs]
   if actual!=expected:errors.append(f'{uid}/{role}: incorrect prior-role sources')
   for x in refs:
    path=Path(x['path'])
    if not path.is_file() or sha(path)!=x['sha256']:errors.append(f'{uid}/{role}: prior output differs')
    if path.parent!=R/'outputs'/uid:errors.append(f'{uid}/{role}: source from another unit')
    prior_events=index.get((uid,path.stem),[]);prior_joins=[e for e in prior_events if e['event']=='join']
    if sp and (not prior_joins or prior_joins[-1]['observed_at_utc']>sp[0]['observed_at_utc']):errors.append(f'{uid}/{role}: dependent role started before prior join')
   if str(of.resolve())!=m['expected_output']:errors.append(f'{uid}/{role}: output binding differs')
   counts['valid_role_outputs']+=1
  if complete:
   counts['complete_units']+=1
   if u['phase']!='preflight':counts['scored_complete_units']+=1
 return {'status':'fail' if errors else ('in_progress' if pending else 'pass_for_generation_integrity'),'counts':counts,'errors':errors,'pending_count':len(pending),'pending':pending,'limits':['Native events are orchestrator-recorded observed handles, not platform attestation.','Read contracts plus fresh contexts do not establish OS access isolation.','This verifies persistence and ordering, not semantic novelty or empirical effectiveness.']}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--save',action='store_true');a.add_argument('--compact',action='store_true');args=a.parse_args();d=audit()
 if args.save:(R/'reports/integrity-audit.json').write_text(json.dumps(d,indent=2)+'\n')
 if args.compact:d.pop('pending')
 print(json.dumps(d,indent=2));raise SystemExit(bool(d['errors']))
