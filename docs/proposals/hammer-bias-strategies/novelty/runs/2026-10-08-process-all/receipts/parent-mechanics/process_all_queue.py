import sys,json,importlib.util
from pathlib import Path
p=Path('/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-08-process-all')
def mod(n):
 s=importlib.util.spec_from_file_location(n,p/'tools'/f'{n}.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
assert mod('integrity').verify()['valid']
m=mod('runtime')
args=sys.argv[1:]
while args and args[0] in ('join','spawn'):
 action,j,a=args[:3];args=args[3:];e=getattr(m,action)(j,a,True) if action=='join' else m.spawn(j,a)
 print(json.dumps({k:e[k] for k in ('event','job_id','validation','known_words') if k in e}))
while True:
 st=m.status()['jobs'];skip=[j['job_id'] for j in m.schedule()[0].values() if j['stage']!='preflight' and st[j['job_id']]['status']=='unprepared' and any(st[d]['status'] in ('failed','skipped') for d in j['depends_on'])]
 if not skip:break
 for j in skip:m.skip(j)
st=m.status()['jobs'];ready=[k for k,v in st.items() if v['status']=='ready']
for j in m.schedule()[0].values():
 if len(ready)>=3:break
 if j['stage']!='preflight' and st[j['job_id']]['status']=='unprepared' and all(st[d]['status']=='valid' for d in j['depends_on']):m.prepare(j['job_id']);ready.append(j['job_id'])
st=m.status()['jobs'];sc=[st[j['job_id']]['status'] for j in m.schedule()[0].values() if j['stage']!='preflight']
print(json.dumps({'ready':ready,'running':[j for j,v in st.items() if v['status']=='running'],'scored_counts':{k:sc.count(k) for k in sorted(set(sc))}}))
