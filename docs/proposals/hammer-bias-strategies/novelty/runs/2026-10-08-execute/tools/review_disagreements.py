#!/usr/bin/env python3
"""Expose differences between locked anonymous reviews; never resolve semantics.

Exact family membership agreement is recorded, not used as a transitive merge.
Wording differences alone are not treated as evidence of a new mechanism.
"""
import argparse,hashlib,json
from collections import defaultdict
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(manifest,judgments):
 expected={x['packet_id'] for x in manifest['packets']}
 views={};partitions={}
 for jid,j in judgments.items():
  assert j['case_id']==manifest['case_id'] and j['judge_id']==jid
  families={f['id']:f for f in j['families']};pairs={p['packet_id']:p for p in j['pairs']}
  assert len(pairs)==len(j['pairs']) and set(pairs)==expected
  members=defaultdict(list);raw={};retention={}
  for pid,p in pairs.items():
   for x in p['raw']:
    key=(pid,x['id']);assert key not in raw;raw[key]=x;members[x['family']].append(key)
   for x in p['retention']:
    key=(pid,x['raw_id']);assert key not in retention;retention[key]=x
  assert set(raw)==set(retention)
  views[jid]={'families':families,'pairs':pairs,'raw':raw,'retention':retention,'members':{f:tuple(sorted(m)) for f,m in members.items()}}
  partitions[jid]=[{'family_id':f,'members':[{'packet_id':p,'raw_id':i} for p,i in sorted(m)],'definition':families[f]} for f,m in sorted(members.items())]
 assert set(views['J1']['raw'])==set(views['J2']['raw'])
 disagreements=defaultdict(lambda:{'raw':[],'post':[]});agreed=[]
 for key in sorted(views['J1']['raw']):
  payload={};reasons=[]
  for jid,v in views.items():
   x=v['raw'][key];f=v['families'][x['family']]
   payload[jid]={'assessment':x,'retention':v['retention'][key],'family_definition':f,'family_members':[{'packet_id':p,'raw_id':i} for p,i in v['members'][x['family']]]}
  a,b=payload['J1'],payload['J2']
  for field in ['usefulness','fit','observability','support']:
   if a['assessment'][field]!=b['assessment'][field]:reasons.append(field)
  for field in ['novelty','kind']:
   if a['family_definition'][field]!=b['family_definition'][field]:reasons.append(field)
  if a['family_members']!=b['family_members']:reasons.append('family_partition')
  if sorted(a['family_definition']['archive_matches'])!=sorted(b['family_definition']['archive_matches']):reasons.append('archive_matches')
  if a['retention']['status']!=b['retention']['status']:reasons.append('retention')
  if sorted(a['retention']['post_ids'])!=sorted(b['retention']['post_ids']):reasons.append('retained_post_ids')
  row={'packet_id':key[0],'raw_id':key[1],'differences':reasons,**payload}
  if reasons:disagreements[key[0]]['raw'].append(row)
  else:agreed.append(row)
 for pid in sorted(expected):
  for field in ['distill_only_additions','recommended_violations','unresolved_recommended_fit']:
   a=views['J1']['pairs'][pid][field];b=views['J2']['pairs'][pid][field]
   if a!=b:disagreements[pid]['post'].append({'field':field,'J1':a,'J2':b})
 return {'phase':manifest['phase'],'case_id':manifest['case_id'],'status':'declared_differences_only','packet_count':len(expected),'raw_count':len(views['J1']['raw']),'disputed_pairs':len(disagreements),'pair_disagreements':[{'packet_id':pid,**d} for pid,d in sorted(disagreements.items())],'agreed_raw':agreed,'family_partitions':partitions,'limits':['This compares explicit categories and exact membership sets; it does not adjudicate causal equivalence.','Different reason or signature wording alone is not a disagreement or a novelty finding.','Post-field differences may be encoding differences; adjudication must inspect original text.','No condition labels or mapping files are read.','Unresolved semantic questions must remain uncertain under the frozen selection rule.']}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('phase');a.add_argument('case');q=a.parse_args()
 manifest=read(R/'blinded'/q.phase/q.case/'manifest.json')
 events=[json.loads(s) for s in (R/'receipts/review-events.jsonl').read_text().splitlines()]
 judgments={};sources=[]
 for jid in ['J1','J2']:
  path=R/'reviews'/f'{q.phase}-{q.case}-{jid}.json'
  locks=[e for e in events if e['event']=='join' and e['phase']==q.phase and e['case_id']==q.case and e['judge_id']==jid]
  assert len(locks)==1 and locks[0]['output_sha256']==sha(path),'Review must have exactly one terminal hash lock'
  judgments[jid]=read(path);sources.append({'judge_id':jid,'path':str(path),'sha256':sha(path),'agent_id':locks[0]['agent_id']})
 result=compare(manifest,judgments);result['locked_judgments']=sources
 out=R/'reports'/f'{q.phase}-{q.case}-disagreements.json';assert not out.exists(),'Difference packet already saved'
 out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'disputed_pairs':result['disputed_pairs'],'raw_count':result['raw_count'],'agreed_raw':len(result['agreed_raw']),'output':str(out)},indent=2))
