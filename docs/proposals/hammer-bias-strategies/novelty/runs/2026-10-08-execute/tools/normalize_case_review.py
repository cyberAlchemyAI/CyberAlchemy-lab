#!/usr/bin/env python3
"""Copy locked independent judgments into the frozen selector's input schema.

No semantic resolution occurs here. This adapter currently requires consensus
empty post-only/unsafe-recommendation arrays; it refuses other cases explicitly.
"""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(x):return (x['packet_id'],x['raw_id'])
QUALIFICATION_FIELDS={'novelty','usefulness','fit','observability','retention','family_equivalence'}

def normalize(phase,case):
 sources=[]
 def locked(path,lock_path):
  lock=read(lock_path);assert lock['native_terminal_observed'] and lock['output_sha256']==sha(path)
  sources.append({'path':str(path.relative_to(R)),'sha256':sha(path),'native_handle':lock['agent_id']})
  return read(path)
 judgments={j:locked(R/'reviews'/f'{phase}-{case}-{j}.json',R/'receipts'/f'review-{phase}-{case}-{j}-lock.json') for j in ['J1','J2']}
 adjud=locked(R/'reviews'/f'{phase}-{case}-adjudication.json',R/'receipts'/f'adjudication-{phase}-{case}-lock.json')
 diff_path=R/'reports'/f'{phase}-{case}-disagreements.json';diff=read(diff_path)
 sources.append({'path':str(diff_path.relative_to(R)),'sha256':sha(diff_path)})
 for s in diff['locked_judgments']:assert s['sha256']==sha(Path(s['path']))
 assert adjud['case_id']==case
 views={};pair_views={}
 for jid,j in judgments.items():
  assert j['case_id']==case and j['judge_id']==jid
  families={f['id']:f for f in j['families']};assert len(families)==len(j['families'])
  pairs={p['packet_id']:p for p in j['pairs']};assert len(pairs)==len(j['pairs']);pair_views[jid]=pairs;views[jid]={}
  for pid,p in pairs.items():
   for field in ['distill_only_additions','recommended_violations','unresolved_recommended_fit']:
    assert p[field]==[],f'Explicit post-disposition adapter required: {pid}/{jid}/{field}'
   retained={x['raw_id']:x for x in p['retention']};assert len(retained)==len(p['retention'])
   assert {x['id'] for x in p['raw']}==set(retained)
   for x in p['raw']:
    k=(pid,x['id']);assert k not in views[jid];f=families[x['family']]
    views[jid][k]={**x,'novelty':f['novelty'],'kind':f['kind'],'retention':retained[x['id']]['status'],'post_ids':retained[x['id']]['post_ids']}
 expected=set(views['J1']);assert expected==set(views['J2'])
 manifest=read(R/'blinded'/phase/case/'manifest.json');packet_raw=set()
 for p in manifest['packets']:
  path=Path(p['file']);assert sha(path)==p['sha256'];packet=read(path)
  packet_raw.update((packet['packet_id'],x['id']) for lane in packet['raw'] for x in lane['openings'])
 assert packet_raw==expected
 assigned={key(x) for p in diff['pair_disagreements'] for x in p['raw']}
 decisions={key(x):x for x in adjud['resolutions']}
 assert len(decisions)==len(adjud['resolutions']) and set(decisions)==assigned
 canonical={f['canonical_family']:f for f in adjud['family_resolutions']}
 assert len(canonical)==len(adjud['family_resolutions'])
 membership={}
 for fid,f in canonical.items():
  assert f['equivalence'] in ['confirmed','uncertain'] and f['signature'] and f['reason']
  assert f['novelty'] in ['new','equivalent','parameter','uncertain']
  for member in f['members']:
   k=key(member);assert k not in membership;membership[k]=fid
  links=f['uncertain_equivalence_with'];assert len(links)==len(set(links))
  for other in links:assert other in canonical and other!=fid and fid in canonical[other]['uncertain_equivalence_with']
 assert set(membership)==expected
 for k,d in decisions.items():
  assert d['canonical_family']==membership[k]
  assert d['novelty'] in ['new','equivalent','parameter','uncertain']
  assert d['fit'] in ['preserves','uncertain','conditional','violates']
  assert d['retention'] in ['retained','lost','uncertain']
  assert type(d['usefulness']) is int and d['usefulness'] in [0,1,2]
  assert type(d['observability']) is int and d['observability'] in [0,1,2]
  for field in ['novelty','usefulness','fit','observability','retention','kind','support']:
   a,b=views['J1'][k][field],views['J2'][k][field]
   if a==b:assert d.get(field,a)==a,f'Agreed value changed: {k}/{field}'
  if sorted(views['J1'][k]['post_ids'])==sorted(views['J2'][k]['post_ids']):
   assert sorted(d.get('post_ids',views['J1'][k]['post_ids']))==sorted(views['J1'][k]['post_ids'])
 for u in adjud['unresolved']:
  assert isinstance(u,dict) and isinstance(u['fields'],list) and u['reason']
  assert set(u['fields'])<=QUALIFICATION_FIELDS|{'kind','support'}
  if 'raw_id' in u:assert key(u) in expected
  if 'canonical_family' in u:assert u['canonical_family'] in canonical
  if 'other_canonical_family' in u:assert u['other_canonical_family'] in canonical
 mapping_path=R/'reports'/f'{phase}-{case}-blind-mapping.json';mapping=read(mapping_path)
 assert {x['packet_id'] for x in mapping}==set(pair_views['J1'])==set(pair_views['J2'])
 units=[]
 for item in mapping:
  pid=item['packet_id'];raw=[];words=[]
  for k in sorted(x for x in expected if x[0]==pid):
   fid=membership[k];d=decisions.get(k,views['J1'][k]);unresolved=[]
   for u in adjud['unresolved']:
    applies=key(u)==k if 'raw_id' in u else fid in [u.get('canonical_family'),u.get('other_canonical_family')]
    if applies:unresolved.append(u)
   fields={f for u in unresolved for f in u['fields']}
   row={'raw_id':k[1],'family_id':fid,**{field:d[field] for field in ['novelty','usefulness','fit','observability','retention']},'support':d.get('support',views['J1'][k]['support']),'kind':d.get('kind',canonical[fid]['kind']),'judgment_resolved':not bool(fields & QUALIFICATION_FIELDS),'unresolved_judgments':unresolved,'intelligible':True,'post_ids':d.get('post_ids',views['J1'][k]['post_ids']),'judgment_source':'adjudication' if k in decisions else 'both_locked_judges','reason':d.get('reason','Locked reviewer consensus'),'packet_id':pid}
   raw.append(row)
  for output in item['source_outputs']:
   path=R/output['path'];assert sha(path)==output['sha256']
   receipt=read(R/'receipts'/f'{item["unit_id"]}-{output["role"]}.json');v=receipt['artifact_validation']
   assert v['valid'] and v['sha256']==sha(path);words.append(v.get('words'))
  units.append({'unit_id':item['unit_id'],'condition':item['condition'],'repetition':item['repetition'],'terminal_status':'completed','execution_valid':True,'assessment_complete':True,'output_words':sum(words) if all(w is not None for w in words) else None,'raw':raw,'post_only':[],'recommended_violations':[],'unresolved_recommended_fit':[],'anonymous_packet_id':pid})
 sources.append({'path':str(mapping_path.relative_to(R)),'sha256':sha(mapping_path)})
 families={fid:{'equivalence_status':f['equivalence'],'uncertain_equivalence_with':f['uncertain_equivalence_with'],'signature':f['signature'],'kind':f['kind'],'novelty':f['novelty'],'archive_matches':f['archive_matches'],'reason':f['reason']} for fid,f in canonical.items()}
 return {'phase':phase,'case_id':case,'status':'assessed_with_explicit_uncertainty','judgments_locked':True,'equivalence_review_locked':True,'families':families,'units':sorted(units,key=lambda u:u['unit_id']),'unresolved':adjud['unresolved'],'sources':sources,'adapter_sha256':sha(Path(__file__)),'validation':{'native_reviews_locked':3,'pairs':len(units),'raw_members':len(expected),'adjudicated_rows':len(decisions),'agreed_rows_carried':len(expected)-len(decisions),'canonical_families':len(families),'agreed_scalar_changes':0,'family_membership_coverage':'exactly_once','uncertain_links':'symmetric'},'claim_ceiling':'Mechanical normalization of locked model judgments; no new semantic judgment, global originality, statistical superiority or empirical benefit.'}

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('phase');a.add_argument('case');q=a.parse_args()
 result=normalize(q.phase,q.case);path=R/'reports'/f'{q.phase}-{q.case}-resolved.json';assert not path.exists(),'Normalized case already saved'
 path.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'output':str(path),'validation':result['validation'],'unresolved_entries':len(result['unresolved'])},indent=2))
