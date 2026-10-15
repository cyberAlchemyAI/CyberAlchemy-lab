"""Prospective native generation receipts; original wave1 runtime stays frozen."""
from pathlib import Path
import json, sys, hashlib, datetime

R = Path(__file__).resolve().parents[1]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def jobs(): return {x['job_id']: x for x in read(R/'generation-schedule.v2.json')['jobs']}
def events(): return [json.loads(s) for s in (R/'receipts/events.jsonl').read_text().splitlines()]
def event(d):
    d = {'dispatch_id':'hammer-novelty-next-all-2026-10-08', 'time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'runtime_version':'generation-native-v2', **d}
    with (R/'receipts/events.jsonl').open('a') as f: f.write(json.dumps(d)+'\n')
    return d
def status():
    out = {k:'pending' for k in jobs()}
    for e in events():
        k = e.get('job_id')
        if k not in out: continue
        if e['event_kind']=='job_prepared': out[k]='ready'
        elif e['event_kind']=='native_spawn': out[k]='running'
        elif e['event_kind']=='native_terminal_join': out[k]='valid' if e['validation']['valid'] else 'invalid'
        elif e['event_kind']=='dependency_disposition': out[k]='skipped'
    return out
def required_freeze_paths():
    sources={
        'generation-schedule.v2.json','generation-review-schedule.v2.json',
        'receipts/generation-method-mapping.v2.json','generation-review-contract.v2.json',
        'criteria-generation.v2.json','prompts/generation-review-v2.txt',
        'tools/generation_runtime_v2.py','tools/generation_review_runtime_v2.py',
        'tools/blind_generation_v2.py','tools/generation_review_validation_v2.py',
        'cases/case-bank.json','archives/case-archives.json',
        'receipts/generation-archive-provenance.json','inputs/plan/portfolio.json',
        'receipts/gates/I01-readiness.json','receipts/gates/I09-fidelity-advance.json',
        'receipts/gates/generation-v2-prelaunch.json',
        'fixtures/generation-capacity-v2.json','reviews/generation-capacity-v2.json',
        'reports/generation-capacity-v2-parent-validation.json',
        'reports/generation-v2-independent-verification.json',
        'reports/generation-v2-repair-verification.json',
        'reports/generation-capacity-prospective-rebudget.json',
        'reports/generation-v2-repair-code-check.json','design/generation-v2-final-repair.json',
    }
    all_jobs=jobs(); outputs={j['output_ref'] for j in all_jobs.values()}
    for j in all_jobs.values():
        sources.add(j['prompt_ref'])
        sources.update(ref for ref in j['input_refs'] if ref not in outputs)
    for j in read(R/'generation-review-schedule.v2.json')['jobs']:sources.add(j['prompt_ref'])
    return sources
def frozen():
    p=R/'freeze-generation-v2.json'
    assert p.exists(), 'generation freeze not yet admitted'
    manifest=read(p);files=manifest.get('files')
    assert isinstance(files,list) and files, 'nonempty exact freeze required'
    assert all(isinstance(f,dict) and isinstance(f.get('path'),str) and isinstance(f.get('sha256'),str) for f in files),'typed freeze entries'
    paths=[f['path'] for f in files]
    assert len(paths)==len(set(paths)) and set(paths)==required_freeze_paths(),'exact required freeze source coverage'
    assert all(not Path(x).is_absolute() and '..' not in Path(x).parts and str(Path(x))==x for x in paths),'normalized freeze paths'
    for f in files: assert sha(R/f['path'])==f['sha256'], 'frozen source drift: '+f['path']
    gate=read(R/'receipts/gates/generation-v2-prelaunch.json')
    assert gate.get('status')=='pass','generation admission gate'
def prior_map(j):
    allj=jobs(); by_output={v['output_ref']:k for k,v in allj.items()}
    return {ref:by_output[ref] for ref in j['input_refs'] if ref in by_output}
def prepare(k):
    frozen(); j=jobs()[k]; st=status(); assert st[k]=='pending'
    bad=[x for x in j['depends_on'] if st[x] in ['invalid','skipped']]
    if bad:
        return event({'event_kind':'dependency_disposition','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'status':'skipped','cause':'invalid_or_skipped_dependency','dependency_ids':bad,'semantic_assessment':None})
    assert all(st[x]=='valid' for x in j['depends_on']), 'dependency not terminal-valid'
    for ref, producer in prior_map(j).items():
        if jobs()[producer]['role']=='incumbent-seed' and not read(R/ref)['openings']:
            return event({'event_kind':'dependency_disposition','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'status':'skipped','cause':'no_shared_incumbent','semantic_assessment':None})
    for gate in ['generation-v2-prelaunch', *j['requires_gates']]:
        p=R/'receipts/gates'/f'{gate}.json'; assert p.exists() and read(p).get('status')=='pass', 'gate: '+gate
    out=R/j['output_ref']; assert not out.exists(), 'first substantive save already exists'
    out.parent.mkdir(parents=True,exist_ok=True)
    inputs=[{'path':x,'sha256':sha(R/x)} for x in j['input_refs']]
    prompt=R/j['prompt_ref']; q=R/'prompts/generation-jobs'/f'{k}.txt';q.parent.mkdir(exist_ok=True);assert not q.exists()
    bound_role='D' if j['role']=='compression' else j['role']
    text=prompt.read_text()+ '\nExact job_id='+k+'; required role='+bound_role+'; exact case_id='+j['case_id']+'.\n'
    text+='Prior artifact/job map: '+json.dumps(prior_map(j))+'.\n'
    text+='Read only the instruction and assigned exact inputs: '+', '.join(str((R/x['path']).resolve()) for x in inputs)+'.\n'
    text+='Write only '+str(out.resolve())+'. Do not inspect schedule, archives, criteria, siblings, parent history, web or agents.\n'
    q.write_text(text)
    return event({'event_kind':'job_prepared','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'input_bindings':inputs,'prompt_ref':str(q.relative_to(R)),'prompt_sha256':sha(q),'output_ref':j['output_ref'],'schedule_sha256':sha(R/'generation-schedule.v2.json')})
def spawn(k, handle):
    j=jobs()[k];assert status()[k]=='ready'
    return event({'event_kind':'native_spawn','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'agent_handle':handle,'turn':1,'host_spawn_observed':True,'fresh_context':True})
def case_field_paths(value,prefix=''):
    paths=set()
    if isinstance(value,dict):
        for k,v in value.items():
            q=prefix+'.'+k if prefix else k;paths.add(q);paths.update(case_field_paths(v,q))
    elif isinstance(value,list):
        for i,v in enumerate(value):
            q=prefix+'['+str(i)+']';paths.add(q);paths.update(case_field_paths(v,q))
    return paths
def _validate(j):
    p=R/j['output_ref']; errors=[]
    if not p.exists(): return {'valid':False,'errors':['missing output']}
    try: d=read(p)
    except Exception as e: return {'valid':False,'errors':['invalid JSON '+str(e)],'output_sha256':sha(p)}
    def need(ok,msg):
        if not ok: errors.append(msg)
    need(d.get('case_id')==j['case_id'],'case ID');need(d.get('role')==('D' if j['role']=='compression' else j['role']),'role binding')
    op=d.get('openings'); lin=d.get('lineage');need(isinstance(op,list),'openings list');need(isinstance(lin,list),'lineage list')
    if not isinstance(op,list) or not isinstance(lin,list):return {'valid':False,'errors':errors,'output_sha256':sha(p)}
    need(len(op)<=j['maximum_current_openings'],'opening cap'); ids=[x.get('id') for x in op];need(all(isinstance(x,str) for x in ids) and len(ids)==len(set(ids)),'unique local IDs')
    pm=prior_map(j);prior={}
    case_paths=case_field_paths(read(R/next(x for x in j['input_refs'] if x.startswith('cases/'))))
    if j['role']=='compression':
        raw=read(R/j['input_refs'][-1]);prior={x['id']:x for x in raw['openings']};fields=['claim','discriminator','probe','uncertainty'];allowed_ids=['D'+str(n) for n in range(1,7)]
    else:
        for ref, producer in pm.items():
            prior.update({producer+':'+x['id']:x for x in read(R/ref)['openings']})
        fields=['claim','delta','prediction','probe'];allowed_ids=['R1','R2']
        need(isinstance(d.get('assessment'),str),'assessment string')
    need(set(ids)<=set(allowed_ids),'local ID namespace')
    if j['role']=='incumbent-seed':need(not ids or ids==['R1'],'one incumbent ID R1')
    for x in op:
        for f in fields:need(isinstance(x.get(f),str),'string field '+f)
        need(x.get('fit') in ['preserves','uncertain','conditional','violates'],'fit enum')
        if j['role']=='compression':
            ss=x.get('source_ids');need(isinstance(ss,list) and bool(ss) and len(ss)==len(set(ss)) and set(ss)<=set(prior),'D sources')
        else:
            need(x.get('kind') in ['mechanism','hypothesis','question'],'kind enum')
            need(isinstance(x.get('assumptions'),list) and all(isinstance(z,str) for z in x.get('assumptions',[])),'assumptions list')
            sr=x.get('source_refs');need(isinstance(sr,list) and all(isinstance(z,str) for z in sr),'source_refs list')
            if isinstance(sr,list):need(all(isinstance(z,str) and (z in prior or z in case_paths) for z in sr),'exact case field or qualified prior source reference')
    seen=[x.get('source_id') for x in lin];need(set(seen)==set(prior) and len(seen)==len(prior),'exact prior/current raw lineage coverage')
    allowed=['retained','merged','parked','rejected'] if j['role']=='compression' else ['retained','changed','merged','parked','rejected']
    for x in lin:
        di=x.get('disposition');tg=x.get('target_ids');need(di in allowed,'lineage disposition');need(isinstance(x.get('reason'),str),'lineage reason')
        if not isinstance(tg,list):need(False,'lineage targets list');continue
        need(len(tg)==len(set(tg)) and set(tg)<=set(ids),'valid targets')
        if di in ['parked','rejected']:need(not tg,'park/reject targets empty')
        if di in ['retained','changed']:need(bool(tg) if j['role']=='compression' else len(tg)==1,'retained/changed target cardinality')
        if di=='merged':need(bool(tg),'merged target required')
        if j['role']=='compression':
            for t in tg:
                if t in ids:need(x['source_id'] in next(o for o in op if o['id']==t).get('source_ids',[]),'reciprocal D source link')
    if j['role']=='compression':
        for opening in op:
            for source in opening.get('source_ids',[]):
                disposition=next((x for x in lin if x.get('source_id')==source),None)
                need(isinstance(disposition,dict) and disposition.get('disposition') in ['retained','merged'] and opening['id'] in disposition.get('target_ids',[]),'reciprocal source-to-target D link')
        need(isinstance(d.get('decision'),str),'decision string');pr=d.get('proposals',[]);need(isinstance(pr,list) and len(pr)<=2,'bounded D-only proposals')
        if isinstance(pr,list):
            need(len({x.get('id') for x in pr})==len(pr),'unique proposal IDs')
            for x in pr:
                need(x.get('id') in ['P1','P2'],'proposal ID')
                for f in ['claim','probe','uncertainty','source_gap']:need(isinstance(x.get(f),str),'proposal field '+f)
                need(x.get('fit') in ['preserves','uncertain','conditional','violates'],'proposal fit')
    if j['study_id']=='I03' and j['role']=='raw':
        arm=next(x['arm'] for x in read(R/'receipts/generation-method-mapping.v2.json')['mapping'] if x['job_id']==j['job_id'])
        if arm in ['critique','construct']:
            attacks=d.get('attacks');need(isinstance(attacks,list) and len(attacks)<=2,'attack cap/list')
            if isinstance(attacks,list):
                attack_ids=[x.get('attack_id') for x in attacks]
                need(len(attack_ids)==len(set(attack_ids)) and set(attack_ids)<=set(['A1','A2']),'unique A1/A2 attack IDs')
                for x in attacks:
                    need(isinstance(x.get('dependency'),str) and isinstance(x.get('source_refs'),list),'attack dependency/source refs')
                    refs=x.get('source_refs');need(isinstance(refs,list) and bool(refs) and len(refs)==len(set(refs)) and all(isinstance(z,str) and z in prior for z in refs),'assigned qualified incumbent attack sources')
                    targets=x.get('linked_opening_ids');need(isinstance(targets,list) and all(isinstance(t,str) for t in targets) and len(targets)==len(set(targets)) and set(targets)<=set(ids),'unique existing attack targets')
                    need(x.get('disposition') in ['replacement','removal','test','no_branch','critique'],'attack disposition')
                    if arm=='construct':need(x.get('disposition')!='critique' and (bool(targets) or x.get('disposition')=='no_branch'),'constructive coverage')
    if j['study_id']=='I08' and j['role']=='convergence':
        cs=d.get('contradictions');need(isinstance(cs,list),'contradiction list');need(d.get('contradiction_count')==len(cs or []),'contradiction count');pairs=[]
        if isinstance(cs,list):
            for x in cs:
                pair=x.get('pair',[]);need(len(pair)==2 and len(set(pair))==2 and all(z.removesuffix(':prediction') in prior and z.endswith(':prediction') for z in pair),'qualified contradiction pair');pairs.append(tuple(sorted(pair)));need(isinstance(x.get('evidence'),str),'contradiction evidence')
            need(len(pairs)==len(set(pairs)),'unique unordered contradiction pairs')
    return {'valid':not errors,'errors':errors,'output_sha256':sha(p),'saved_words':len(p.read_text().split()),'semantic_validity':'not asserted by structural validator'}
def validate(j):
    try:return _validate(j)
    except Exception as e:
        p=R/j['output_ref'];result={'valid':False,'errors':['malformed output shape: '+type(e).__name__+': '+str(e)],'semantic_validity':'not asserted by structural validator'}
        if p.exists():result.update(output_sha256=sha(p),saved_words=len(p.read_text().split()))
        return result
def join(k,handle):
    j=jobs()[k];assert status()[k]=='running';sp=[e for e in events() if e.get('job_id')==k and e['event_kind']=='native_spawn'][-1];assert sp['agent_handle']==handle
    pe=[e for e in events() if e.get('job_id')==k and e['event_kind']=='job_prepared'][-1]
    assert all(sha(R/x['path'])==x['sha256'] for x in pe['input_bindings']);assert sha(R/pe['prompt_ref'])==pe['prompt_sha256'];frozen()
    return event({'event_kind':'native_terminal_join','study_id':j['study_id'],'phase':j['phase'],'job_id':k,'agent_handle':handle,'terminal_observed':True,'terminal_witness':'parent_received_NATIVE_FINAL_ANSWER','validation':validate(j),'output_ref':j['output_ref']})
if __name__=='__main__':
    a=sys.argv[1:];cmd=a.pop(0)
    if cmd=='status':print(json.dumps(status(),indent=2))
    elif cmd=='prepare':print(json.dumps(prepare(a[0])))
    elif cmd=='spawn':print(json.dumps(spawn(*a)))
    elif cmd=='join':print(json.dumps(join(*a)))
    else:raise SystemExit('unknown command')
