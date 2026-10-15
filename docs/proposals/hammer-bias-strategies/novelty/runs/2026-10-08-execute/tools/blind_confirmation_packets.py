#!/usr/bin/env python3
"""Create reversible anonymous packets without changing substantive content."""
import argparse,hashlib,json,random
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(f):return json.loads((R/f).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=argparse.ArgumentParser();a.add_argument('phase',choices=['confirmation']);a.add_argument('case');q=a.parse_args()
schedule=read('confirmation-schedule.json');rows=[u for u in schedule['units'] if u['phase']==q.phase and u['case_id']==q.case]
assert rows,'No scheduled units'
phase_number={'discovery':0,'bundle':1,'confirmation':2}[q.phase]
case_number=int(q.case[1:])+ (10 if q.case.startswith('H') else 0)
rng=random.Random(schedule['blind_seed']+100*phase_number+case_number);rng.shuffle(rows)
base=R/'blinded'/q.phase/q.case;base.mkdir(parents=True,exist_ok=True)
assert not (base/'manifest.json').exists(),'Packets already frozen'
mapping=[];packets=[]
for i,u in enumerate(rows,1):
 pid=f'{q.case}-P{i:03d}';raw=[];src=[];failure=[]
 for role in u['roles']:
  f=R/'outputs'/u['unit_id']/f'{role}.json';receipt=R/'receipts'/f'{u["unit_id"]}-{role}.json'
  if not f.exists():failure.append({'role':role,'error':'missing output'});continue
  if not receipt.exists() or not json.loads(receipt.read_text())['artifact_validation']['valid']:failure.append({'role':role,'error':'not validated/joined'});continue
  src.append({'role':role,'path':str(f.relative_to(R)),'sha256':sha(f)})
  d=json.loads(f.read_text())
  if role=='D':post=d
  else:raw.append(d)
 packet={'packet_id':pid,'case_id':q.case,'raw':raw,'post_distill':post if not failure else None,'execution_failures':failure}
 f=base/f'{pid}.json';f.write_text(json.dumps(packet,indent=2,ensure_ascii=False)+'\n');packets.append({'packet_id':pid,'file':str(f),'sha256':sha(f)})
 mapping.append({'packet_id':pid,'unit_id':u['unit_id'],'case_id':u['case_id'],'condition':u['condition'],'repetition':u['repetition'],'source_outputs':src})
manifest={'phase':q.phase,'case_id':q.case,'packet_count':len(packets),'case_path':str(R/'cases'/f'{q.case}.json'),'archive_path':str(R/'archives'/f'{q.case}.json'),'packets':packets}
(base/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'reports'/f'{q.phase}-{q.case}-blind-mapping.json').write_text(json.dumps(mapping,indent=2)+'\n')
for j in [1,2]:
 order=packets.copy();random.Random(schedule['blind_seed']+100*phase_number+case_number+1000*j).shuffle(order)
 out=R/'reviews'/f'{q.phase}-{q.case}-J{j}.json'
 task=(R/'prompts/judge.txt').read_text()+f'\nCase: {manifest["case_path"]}\nArchive: {manifest["archive_path"]}\nJudge_id: J{j}\nPacket order (read each; preserve independence):\n'+json.dumps(order,indent=2)+f'\nExact output file: {out}\nDo not read conditionmapping files or peerreviews. No extra file writes.\n'
 f=R/'prompts/jobs'/f'judge-{q.phase}-{q.case}-J{j}.txt';f.write_text(task)
print(json.dumps({'packet_count':len(packets),'manifest':str(base/'manifest.json'),'judge_prompts':[str(R/'prompts/jobs'/f'judge-{q.phase}-{q.case}-J{j}.txt') for j in [1,2]]},indent=2))
