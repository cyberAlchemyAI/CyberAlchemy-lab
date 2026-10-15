from pathlib import Path
import json, hashlib, datetime, sys, re
B=Path(__file__).resolve().parent
now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(n):return json.loads((B/n).read_text())
def save(n,x): (B/n).write_text(json.dumps(x,indent=2)+'\n')
def exclusive(p,t):p.parent.mkdir(parents=True,exist_ok=True);p.open('x').write(t)
def textout(job):return (B/'jobs'/job/'output.md').read_text()
def supplement(job,branch):
    body=textout(job)
    m=re.search(r'(?m)^## '+branch+r'\s*\n(.*?)(?=^## (?:MAIN|RESIDUE)\s*$|\Z)',body,re.S|re.M)
    if not m: raise RuntimeError('missing branch in '+job)
    return m.group(1).strip()
def render(job):
    s=next(x for x in load('SCHEDULE.json') if x['job']==job); c=s['case']; p=load('PROMPTS.json'); case=(B/'cases'/(c+'.json')).read_text()
    path=B/'jobs'/job; path.mkdir(parents=True,exist_ok=True)
    out=path/'output.md'
    key=s['stage']
    if key=='converger':key='converger_'+s['policy']
    if key=='distill' and s['condition'] in 'OG':key='distill_relay'
    body=p['global']+'\n'+p['templates'][key]+f'\n\nSAVE ONLY: {out}\n\nCOMMON CASE\n'+case
    dependencies=[]
    if s['role']=='converger':
        for dep in s['depends']:
            raw=textout(dep);body+='\n\nSHARED CONCERN '+dep.rsplit('_',1)[1]+'\n'+raw;dependencies.append({'job':dep,'sha256':sha(B/'jobs'/dep/'output.md')})
    elif s['role']=='distill':
        dep=s['depends'][0];body+='\n\nOWN CONVERGER\n'+textout(dep);dependencies.append({'job':dep,'sha256':sha(B/'jobs'/dep/'output.md')})
    elif s['role']=='builder':
        dep=s['depends'][0];sup=supplement(dep,s['branch']);exclusive(path/'supplement.md',sup+'\n');body+='\n\nFROZEN SUPPLEMENT\n'+sup
        dependencies.append({'job':dep,'sha256':sha(B/'jobs'/dep/'output.md'),'assigned_branch':s['branch'],'supplement_sha256':sha(path/'supplement.md'),'supplement_words':len(sup.split())})
    elif s['role']=='assessor':
        body+='\n\nORDINARY AND UPSTREAM COMMON CONCERN ARCHIVE\n'
        for dep in [c+'_inversion',c+'_attack']:
            body+=textout(dep)+'\n';dependencies.append({'job':dep,'sha256':sha(B/'jobs'/dep/'output.md')})
        mapping=load('FREEZE.json')['blind_order_map'][c]
        for label,condition in mapping.items():
            dep=c+'_'+condition+'_builder';sup=(B/'jobs'/dep/'supplement.md').read_text()
            body+='\n\nANONYMOUS OUTPUT '+label+'\n'+textout(dep)+'\n\nITS SUPPLIED SUPPLEMENT\n'+sup
            dependencies.append({'job':dep,'sha256':sha(B/'jobs'/dep/'output.md'),'blind_label':label,'supplement_sha256':sha(B/'jobs'/dep/'supplement.md')})
    exclusive(path/'payload.md',body)
    task=f'Read ONLY this frozen role payload: {path}/payload.md . Its SHA-256 is {sha(path/"payload.md")}. Perform its role now. Use no other files or prior case context. Save exactly one substantive output.md exclusively in that job directory using file mode x. Return the same substantive body in FINAL so the coordinator can join the actual native role. Do not spawn helpers. Do not overwrite. The human authorized this native experiment.'
    exclusive(path/'spawn-message.txt',task)
    save(str(Path('jobs')/job/'INPUT-RECEIPT.json'),{'job':job,'rendered_at':now(),'case_sha256':sha(B/'cases'/(c+'.json')),'payload_sha256':sha(path/'payload.md'),'spawn_message_sha256':sha(path/'spawn-message.txt'),'dependencies':dependencies,'exposure':'exact payload only, fork_turns=none; no administrative labels in assessor payload'})
    return {'job':job,'task':task,'payload_sha256':sha(path/'payload.md')}
def spawned(job,agent):
    n=load('NATIVE-INVOCATIONS.json');n['invocations'].append({'job':job,'agent_id':agent,'spawn_status':'success','spawn_observed_at':now(),'fork_turns':'none','join_status':'pending','close_status':'pending','first_attempt':True,'role':next(x['role'] for x in load('SCHEDULE.json') if x['job']==job),'payload_sha256':sha(B/'jobs'/job/'payload.md')});save('NATIVE-INVOCATIONS.json',n)
    pr=load('PROGRESS.json');pr.update(current_stage=job,status='running',updated_at=now());save('PROGRESS.json',pr)
def joined(job):
    s=next(x for x in load('SCHEDULE.json') if x['job']==job);f=B/'jobs'/job/'output.md';body=f.read_text() if f.exists() else '';words=len(body.split());caps=load('PROMPTS.json')['caps'];cap=caps['concern'] if s['role']=='concern' else caps['distill_total'] if s['role']=='distill' else caps[s['role']]
    errors=[]
    if not body.strip() or len(body.split())<20:errors.append('missing_or_non_substantive_body')
    if words>cap:errors.append('primary_word_cap_exceeded')
    if s['role']=='distill':
        for branch in ['MAIN','RESIDUE']:
            try:
                if len(supplement(job,branch).split())>300:errors.append(branch+'_supplement_cap_exceeded')
            except Exception:errors.append('missing_'+branch)
    n=load('NATIVE-INVOCATIONS.json');item=next(x for x in n['invocations'] if x['job']==job);item.update(join_status='FINAL_observed',close_status='terminal',final_observed_at=now(),first_primary_sha256=sha(f) if f.exists() else None,actual_primary_words=words,validation='invalid' if errors else 'substantive_shape_pass',errors=errors,observer_status='coordinator observed native FINAL notification; exact message is in native conversation event stream',blockers=errors,handoff_note='Frozen first primary; no repair/regrade performed',capability_ref='experiment-harness/native-research-adaptation',dispatch_id='novelty-successor-pilot-20261011');save('NATIVE-INVOCATIONS.json',n)
    exclusive(B/'jobs'/job/'FIRST-SAVE.json',json.dumps(item,indent=2)+'\n')
    pr=load('PROGRESS.json');pr['pending'].remove(job);pr['joined']+=1;pr['current_stage']='joined '+job;pr['updated_at']=now();pr['invalid']+=([job] if errors else []);save('PROGRESS.json',pr)
    return {'joined':pr['joined'],'job':job,'words':words,'sha256':item['first_primary_sha256'],'errors':errors,'next':pr['pending'][0] if pr['pending'] else None}
if __name__=='__main__':
    action=sys.argv[1]
    if action=='render':result=render(sys.argv[2])
    elif action=='spawned':spawned(sys.argv[2],sys.argv[3]);result={'spawn_saved':sys.argv[2]}
    elif action=='joined':result=joined(sys.argv[2])
    elif action=='next':result={'next':load('PROGRESS.json')['pending'][0] if load('PROGRESS.json')['pending'] else None}
    else:raise ValueError(action)
    print(json.dumps(result))
