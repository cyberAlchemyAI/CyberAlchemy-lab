import hashlib,json,pathlib,stat,datetime,os
L=pathlib.Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host');C=L/'context-signed-scope-portable-bundle-0001';R=L/'context-signed-scope-portable-bundle-independent-review-0001'
B=pathlib.Path('/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-signed-scope-portable-bundle-0001')
def need(ok):
 if not ok:raise RuntimeError('AUDIT_MISMATCH')
def pin(p):
 b=p.read_bytes();s=p.stat();return {'path':str(p),'sha256':hashlib.sha256(b).hexdigest(),'size':len(b),'mode':oct(stat.S_IMODE(s.st_mode)),'uid':s.st_uid}
f=json.loads((C/'freeze.json').read_bytes());need(pin(C/'freeze.json')['sha256']=='47f593a19daaa0f3c74735b1d478650c7281100a4f5c243a88a9348c3bcacad3')
pins=[pin(C/'freeze.json')]
for name,h in f['members'].items():
 q=pin(C/name);need(q['sha256']==h);pins.append(q)
m=json.loads((B/'manifest.json').read_bytes());need(pin(B/'manifest.json')['sha256']==f['selected_bundle_manifest_sha256'])
need({p.name for p in B.iterdir()}=={'manifest.json','blobs'})
expected={m['loader_source']['sha256']}|{v['sha256'] for v in m['code'].values()}|{v['sha256'] for v in m['metadata'].values()}
need(len(expected)==105 and {p.name for p in (B/'blobs').iterdir()}==expected)
for dirname in [B,B/'blobs']:need(stat.S_IMODE(dirname.stat().st_mode)==0o700 and dirname.stat().st_uid==os.getuid())
for p in [B/'manifest.json',*sorted((B/'blobs').iterdir())]:
 q=pin(p);need(q['mode']=='0o600' and q['uid']==os.getuid());pins.append(q)
 if p.parent.name=='blobs':need(q['sha256']==p.name)
for role in ['code','metadata']:
 for path,row in m[role].items():
  need(not pathlib.Path(path).is_absolute() and '..' not in pathlib.Path(path).parts and pathlib.Path(path).name!='branch.snapshot')
  q=pin(B/'blobs'/row['sha256']);need(q['size']==row['size'])
probes=[]
for stem in ['docker-environment-probe','docker-probe','docker-probe-0002','docker-probe-0003']:
 ob=json.loads((C/(stem+'-observation.json')).read_bytes())
 for stream in ['stdout','stderr']:
  q=pin(C/(stem+'.'+stream));need(q['sha256']==ob[stream+'_sha256']);need(q['size']==ob[stream+'_size'])
 need(type(ob['os_exit']) is int)
 probes.append({'name':stem,'reported_os_exit':ob['os_exit'],'reported_name_absent_before':ob.get('name_absent_before'),'reported_name_absent_after':ob.get('name_absent_after'),'argv':ob['argv']})
for rel in ['context-successor-checked-reader-loader-0001/freeze.json','context-successor-checked-reader-loader-0001/checked_loader.py','context-successor-checked-reader-loader-independent-review-0001/review.json','context-successor-signed-scope-docker-plan-0001/freeze.json','context-successor-signed-scope-docker-plan-independent-review-0001/review.json']:pins.append(pin(L/rel))
pins.append(pin(pathlib.Path('/usr/bin/python3.14')))
report={'schema':'independent-portable-bundle-audit/v1','timestamp_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pins':pins,'code_rows':len(m['code']),'metadata_rows':len(m['metadata']),'source_rows':len(m['source_manifest']['files']),'reader_rows':len(m['reader_rows']),'blobs':len(expected),'exact_current_bundle_modes_and_inventory':True,'no_archive_body_read':True,'new_docker_effect':False,'probe_evidence':probes,'probe_limit':'OS exit/name absence are retained author observations. Raw stdout/stderr hashes verified; raw absence stderr and its command/exit not retained in this candidate. No fresh Docker observation.'}
(R/'audit.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['pins','probe_evidence']},sort_keys=True))
