from pathlib import Path
import json,hashlib,random,sys
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text())
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
phase=sys.argv[1];rs=read(R/'review-schedule.json')['jobs'];mapping=read(R/'receipts/I09-method-mapping.json')['mapping']
for shard in [1,2]:
 j=next(x for x in rs if x['phase']==phase and x['shard']==shard);source_cases={};units=[];bindings=[];maprows=[]
 for m in mapping:
  if m['case_id'] not in j['case_ids']:continue
  case_path=R/'fixtures'/f"{m['case_id']}.json";post_path=R/m['output_ref'];assert post_path.exists(),'missing exact post source'
  source_cases[m['case_id']]=read(case_path)
  uid='U'+hashlib.sha256(('blinded-next-v1:'+m['job_id']).encode()).hexdigest()[:10]
  units.append({'unit_id':uid,'case_id':m['case_id'],'post':read(post_path)})
  bindings.extend([{'path':str(case_path.relative_to(R)),'sha256':h(case_path)},{'path':str(post_path.relative_to(R)),'sha256':h(post_path)}])
  maprows.append({'unit_id':uid,**m})
 random.Random('next-v1-'+phase+str(shard)).shuffle(units)
 packet={'phase':phase,'shard':shard,'source_cases':source_cases,'units':units,'rubric':{'retention':read(R/'criteria.json')['scales']['retention'],'fit':read(R/'criteria.json')['scales']['fit'],'protected_fields':'Every raw relation, full discriminator/probe including all rival/directional/challenge/defeat/capacity conditions, uncertainty and source-declared fit. See exact review instruction.','claim_ceiling':'Supplied synthetic/model sources; no physical/human effect. Inherited source conflicts separate from compression additions.'},'method_blinding':'Administrative labels withheld; semantic recognizability remains possible.'}
 out=R/'fixtures'/f'blinded-{phase}-{shard}.json';assert not out.exists(),'first packet already saved';out.write_text(json.dumps(packet,indent=2)+'\n')
 mp=R/'receipts'/f'blinded-{phase}-{shard}-mapping.json';mp.write_text(json.dumps({'mapping':maprows,'source_bindings':bindings,'packet_sha256':h(out)},indent=2)+'\n')
 print(json.dumps({'phase':phase,'shard':shard,'case_packets':len(source_cases),'units':len(units),'raw_review_rows':sum(len(source_cases[u['case_id']]['raw_candidates']) for u in units),'packet_words':len(out.read_text().split()),'sha256':h(out)}))
