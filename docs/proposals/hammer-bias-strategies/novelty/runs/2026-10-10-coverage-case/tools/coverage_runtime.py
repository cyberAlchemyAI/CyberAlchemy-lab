"""One-case A/B adapter. Reuses immutable pure validators, never the184-job runner."""
import argparse, datetime, hashlib, importlib.util, itertools, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PURE = Path('/home/vlad_/projects/CyberAlchemy-lab/docs/proposals/hammer-bias-strategies/novelty/runs/2026-10-10-reference-explicit/tools/ten_runtime.py')
_binding=json.loads((ROOT/'SCOPE.json').read_text())['pure_validation_source']
if str(PURE)!=_binding['path'] or hashlib.sha256(PURE.read_bytes()).hexdigest()!=_binding['sha256']:
    raise ValueError('immutable pure-validation source binding mismatch')
spec = importlib.util.spec_from_file_location('immutable_ten_pure', PURE)
T = importlib.util.module_from_spec(spec)
spec.loader.exec_module(T)

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def save(path, value, raw=False):
    path = Path(path)
    data = value if raw else (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode()
    with path.open('xb') as f: f.write(data)
    return {'path':str(path),'sha256':sha(path)}
def require(ok, why):
    if not ok: raise ValueError(why)

def validate_case(value):
    T.obj(value, ('classification','independence_note','case'), 'single input')
    require(value['classification']=='synthetic_fresh_single_case_and_archive.v1', 'classification')
    require(value['independence_note'] in ('No prior candidates, strategy prompts or results were read','No prior candidates, strategy prompts or results were read.'), 'author independence')
    c=value['case']
    T.obj(c, ('case_id','phase','domain','valued_outcome','hard_constraints','observations','resources','preferred_dependency','causal_return_path_hypothesis','anomaly_id','parent_operations','available_observables','unknowns','ordinary_archive'), 'case')
    require((c['case_id'],c['phase'],c['domain'])==('NX','exploratory','workflow'), 'case identity')
    for key in ('valued_outcome','preferred_dependency','causal_return_path_hypothesis','anomaly_id'): T.string(c[key],key)
    tables={'hard_constraints':('C',3,6),'observations':('O',5,8),'resources':('R',5,8),'parent_operations':('P',2,2),'available_observables':('M',3,5),'unknowns':('U',2,4),'ordinary_archive':('A',3,3)}
    seen=[]
    for field,(prefix,lo,hi) in tables.items():
        T.array(c[field],field,lo,hi)
        ids=[]
        for row in c[field]:
            keys=('id','text','available') if field=='resources' else (('id','operation','relation','probe','limits') if field=='ordinary_archive' else ('id','text'))
            T.obj(row,keys,field)
            for key in keys:
                if key=='available': require(type(row[key]) is bool,'resource availability')
                else: T.string(row[key],field+'.'+key)
            ids.append(row['id']);seen.append(row['id'])
        T.unique(ids,field)
        require(set(ids)=={prefix+str(i) for i in range(1,len(ids)+1)},'contiguous fact IDs')
    T.unique(seen,'case row IDs')
    require(c['anomaly_id'] in {r['id'] for r in c['observations']},'anomaly observation')
    require(T.words(value)<=2500,'author cap')
    return True

def jobs():
    result=[{'job_id':'NX-'+r,'case_id':'NX','role':r,'condition':None,'dependencies':[]} for r in ('INV','ATT')]
    for condition in ('A','B'):
        previous=None
        for role in ('stage1','stage2','builder'):
            jid='NX-'+condition+'-'+role
            result.append({'job_id':jid,'case_id':'NX','role':role,'condition':condition,'dependencies':['NX-INV','NX-ATT']+([previous] if previous else []),'supplement_branch':'summary'})
            previous=jid
    for n in (1,2): result.append({'job_id':'NX-review'+str(n),'case_id':'NX','role':'review','condition':None,'dependencies':['NX-A-builder','NX-B-builder']})
    require(len(result)==10,'ten scored jobs')
    return result
def job(jid): return next(j for j in jobs() if j['job_id']==jid)
def output(jid): return ROOT/'outputs'/(jid+'.json')
def event(kind,jid): return ROOT/'events'/(kind+'--'+jid+'.json')
def case(): return T.packet(read(ROOT/'inputs/fresh-case-and-archive.v1.json')['case'])
def status(jid):
    for kind in ('joined','gated','started'):
        if event(kind,jid).exists(): return read(event(kind,jid))
    return {'disposition':'pending','valid':False,'terminal':False}
def valid_body(jid):
    s=status(jid)
    require(s['disposition']=='joined' and s['valid'],'valid source required')
    require(sha(output(jid))==s['output_sha256'],'source output drift')
    return read(output(jid))

def overhead_start(role,handle,prompt):
    require(role in read(ROOT/'BUDGET.json')['overhead_roles'],'undeclared overhead')
    require(prompt.is_file(),'literal overhead prompt')
    return save(event('overhead-started',role),{'kind':'started','role':role,'handle':handle,'observed_at':now(),'prompt':{'path':str(prompt),'sha256':sha(prompt)},'budget_sha256':sha(ROOT/'BUDGET.json'),'scored':False})
def overhead_join(role,handle,out,wit):
    start=read(event('overhead-started',role));require(start['handle']==handle,'overhead handle')
    T.witness(read(wit),handle)
    require(sha(start['prompt']['path'])==start['prompt']['sha256'],'overhead prompt drift')
    return save(event('overhead-joined',role),{'kind':'joined','role':role,'handle':handle,'observed_at':now(),'observation':'FINAL','output':{'path':str(out),'sha256':sha(out)} if out.exists() else None,'witness':{'path':str(wit),'sha256':sha(wit)},'scored':False})

def prepare():
    require(not (ROOT/'events/freeze.json').exists(),'already frozen')
    author=read(event('overhead-joined','PREP-case'))
    require(author['output']['path']==str(ROOT/'inputs/fresh-case-and-archive.v1.json'),'author output path')
    require(sha(author['output']['path'])==author['output']['sha256'],'author output drift')
    validate_case(read(ROOT/'inputs/fresh-case-and-archive.v1.json'))
    (ROOT/'prompts/base').mkdir(exist_ok=True)
    (ROOT/'prompts/actual').mkdir(exist_ok=True)
    prefix='Use python3 as the available interpreter for every operation. The scored output parent already exists. Build and check in memory before your only exclusive first save. Machine CONDITION_ID is separate from the human method name. For stage1, policy must equal the exact CONDITION_ID literal; also verify JOB_ID and CASE_ID. Never use method names such as S05 as the policy of condition B.\n'
    for j in jobs():
        ident='CONDITION_ID='+json.dumps(j['condition'])+'\n'
        save(ROOT/'prompts/base'/(j['job_id']+'.txt'),(prefix+ident+T.base_prompt(j)).encode(),True)
    return save(ROOT/'inputs/plan.json',{'classification':'single-case-ten-job-plan.v1','jobs':jobs(),'ordinary_archive':read(ROOT/'inputs/fresh-case-and-archive.v1.json')['case']['ordinary_archive'],'opaque_units':{'A':'U-8F4C','B':'U-2D9A'}})

def freeze():
    require((ROOT/'outputs').is_dir(),'actual scored output parent')
    pre=read(event('overhead-joined','PREP-prelaunch'))
    require(pre['output'] and read(pre['output']['path'])['verdict']=='pass','actual prelaunch pass required')
    require(sha(pre['output']['path'])==pre['output']['sha256'],'prelaunch output drift')
    source_paths=[ROOT/'SCOPE.json',ROOT/'BUDGET.json',ROOT/'inputs/fresh-case-and-archive.v1.json',ROOT/'inputs/plan.json',Path(__file__).resolve(),ROOT/'tools/preflight_checks.py',ROOT/'receipts/pre-freeze-independence-punctuation.v1.json',PURE,ROOT/'prompts/PREP-case.v1.txt',ROOT/'prompts/PREP-prelaunch.v1.txt',ROOT/'prompts/POST-completion-audit.v1.txt']
    source_paths+=list((ROOT/'prompts/base').glob('*.txt'))
    for role in ('PREP-case','PREP-prelaunch'):
        source_paths += [event('overhead-started',role),event('overhead-joined',role)]
        r=read(event('overhead-joined',role))
        source_paths += [Path(r['witness']['path']),Path(r['output']['path'])]
    return save(ROOT/'events/freeze.json',{'event':'frozen','observed_at':now(),'sources':{str(p):sha(p) for p in source_paths},'planned_scored':10,'planned_overhead':3,'claim_ceiling':'One fresh exploratory case; no recovery of prior invalid comparisons.'})
def integrity():
    for path,digest in read(ROOT/'events/freeze.json')['sources'].items(): require(sha(path)==digest,'frozen source drift: '+path)

def ready():
    integrity()
    pending=[]
    for j in jobs():
        if status(j['job_id'])['disposition']!='pending': continue
        deps=[status(d) for d in j['dependencies']]
        if j['role']!='review' and any(s['terminal'] and not s['valid'] for s in deps):
            save(event('gated',j['job_id']),{'job_id':j['job_id'],'disposition':'gated','terminal':True,'valid':False,'reason':'invalid predecessor','dependencies':j['dependencies'],'observed_at':now()})
        elif all(s['terminal'] for s in deps): pending.append(j['job_id'])
    return pending
def review_packet(j):
    plan=read(ROOT/'inputs/plan.json');units=[];cards=[];bindings={}
    for c in ('A','B'):
        jid='NX-'+c+'-builder';s=status(jid);require(s['terminal'],'all builders terminal')
        uid=plan['opaque_units'][c]
        units.append({'unit_id':uid,'status':'gated' if s['disposition']=='gated' else ('valid' if s['valid'] else 'invalid'),'reason':s.get('reason','validated native first save')})
        value=None
        if output(jid).exists():
            require(sha(output(jid))==s.get('output_sha256'),'review source drift')
            try: value=read(output(jid))
            except (ValueError,UnicodeDecodeError): pass
        for i,card in enumerate(T.raw_cards(value)):
            label=uid+'-C'+str(i+1).zfill(2)
            cards.append({'card_id':label,'unit_id':uid,'declared_card':T.blind_card(card,label),'structurally_valid_unit':s['valid'],'failure_reason':None if s['valid'] else s['reason']})
            bindings[label]={'condition':c,'job_id':jid,'index':i}
    return {'job_id':j['job_id'],'case_id':'NX','case':case(),'units':sorted(units,key=lambda x:x['unit_id']),'cards':sorted(cards,key=lambda x:x['card_id']),'archive':plan['ordinary_archive'],'rubric':T.RUBRIC},bindings
def projection(j):
    if j['role']=='review': return review_packet(j)[0]
    b={'case':case()}
    for d in j['dependencies']:
        value=valid_body(d)
        if d.endswith('-INV') or d.endswith('-ATT'): b[d.rsplit('-',1)[1]]=value
        elif j['role']=='builder': b['supplement']=value['summary']
        else: b['stage1']=value
    return b
def prompt(jid):
    integrity();j=job(jid)
    require(jid in ready(),'job not ready')
    require(not output(jid).exists(),'stale scored output')
    bodies=projection(j);base=(ROOT/'prompts/base'/(jid+'.txt')).read_bytes()
    literal=T.literal_prompt(j,base,output(jid),bodies)
    receipt=save(ROOT/'prompts/actual'/(jid+'.txt'),literal,True)
    return save(event('admitted',jid),{'job_id':jid,'literal':receipt,'declared_input_words':T.words(bodies),'literal_text_words':len(literal.decode().split()),'source_registry':T.source_registry(bodies['case']),'dependencies':{d:status(d).get('output_sha256') for d in j['dependencies']}})
def started(jid,handle):
    integrity();require(status(jid)['disposition']=='pending','not pending')
    r=read(event('admitted',jid));require(sha(r['literal']['path'])==r['literal']['sha256'],'admitted prompt drift')
    expected=T.literal_prompt(job(jid),(ROOT/'prompts/base'/(jid+'.txt')).read_bytes(),output(jid),projection(job(jid)))
    require(hashlib.sha256(expected).hexdigest()==r['literal']['sha256'],'literal differs from exact frozen projection')
    require(sum(status(j['job_id'])['disposition']=='started' for j in jobs())<2,'scored concurrency cap')
    recorded=[read(q)['handle'] for q in (ROOT/'events').glob('started--*.json')]+[read(q)['handle'] for q in (ROOT/'events').glob('overhead-started--*.json')]
    require(handle not in recorded,'fresh unique native handle required')
    require(all(status(d)['terminal'] and (job(jid)['role']=='review' or status(d)['valid']) for d in job(jid)['dependencies']),'predecessor gate')
    return save(event('started',jid),{'job_id':jid,'handle':handle,'disposition':'started','terminal':False,'valid':False,'prompt':r['literal'],'observed_at':now()})
def joined(jid,handle,wit):
    integrity();j=job(jid);s=status(jid)
    require(s['disposition']=='started' and s['handle']==handle,'actual start/handle required')
    T.witness(read(wit),handle);require(sha(s['prompt']['path'])==s['prompt']['sha256'],'spawned prompt drift')
    valid=False;reason='missing first-saved output';count=None;digest=None
    if output(jid).exists():
        digest=sha(output(jid))
        try:
            value=read(output(jid));count=T.words(value)
            bodies=projection(j)
            T.validate_output(j,value,case(),supplement_ids=[x['id'] for x in bodies.get('supplement',[])],review_packet=bodies if j['role']=='review' else None)
            valid=True;reason='validated native first save'
        except (ValueError,KeyError,TypeError,StopIteration,UnicodeDecodeError) as exc: reason=str(exc)
    return save(event('joined',jid),{'job_id':jid,'handle':handle,'disposition':'joined','terminal':True,'valid':valid,'reason':reason,'observation':'FINAL','witness_path':str(wit),'witness_sha256':sha(wit),'output_sha256':digest,'saved_words':count,'review_lock':j['role']=='review','observed_at':now()})

def report():
    integrity();ss={j['job_id']:status(j['job_id']) for j in jobs()}
    require(all(s['terminal'] for s in ss.values()),'all ten dispositions required')
    for jid,s in ss.items():
        if s['disposition']=='joined':
            require(sha(s['witness_path'])==s['witness_sha256'],'FINAL witness drift')
            require(sha(read(event('started',jid))['prompt']['path'])==read(event('started',jid))['prompt']['sha256'],'literal drift')
        if s.get('output_sha256'): require(sha(output(jid))==s['output_sha256'],'raw output drift')
    review_ids=['NX-review1','NX-review2'];review_valid=all(ss[j]['valid'] and ss[j].get('review_lock') for j in review_ids)
    packet,bindings=review_packet(job(review_ids[0]));qualified=[];uncertain=[];disagreements=[]
    if review_valid:
        reviews=[read(output(j)) for j in review_ids]
        rows=[{r['card_id']:r for r in v['cards']} for v in reviews]
        archives=[{(r['card_id'],r['archive_id']):r['relation'] for r in v['archive_pairs']} for v in reviews]
        for card in packet['cards']:
            cid=card['card_id'];declared=card['declared_card'];structural=card['structurally_valid_unit'] and isinstance(declared,dict)
            available=structural and all(next((r['available'] for r in case()['resources'] if r['id']==rid),False) for rid in declared['resources'])
            axes=[v[cid][axis] for v in rows for axis in T.RUBRIC['axes']]
            relations=[v[(cid,a['id'])] for v in archives for a in packet['archive']]
            if available and all(x is True for x in axes) and all(x=='distinct' for x in relations): qualified.append(cid)
            if available and not any(x is False for x in axes) and 'equivalent' not in relations: uncertain.append(cid)
            if any(rows[0][cid][axis]!=rows[1][cid][axis] for axis in T.RUBRIC['axes']) or any(archives[0][(cid,a['id'])]!=archives[1][(cid,a['id'])] for a in packet['archive']):disagreements.append(cid)
    fail=any(not s['valid'] for s in ss.values())
    overhead=[read(q) for q in (ROOT/'events').glob('overhead-started--*.json')]
    result={'classification':'one_case_exploratory_coverage_illustration','planned_scored':10,'actual_scored_starts':sum(s['disposition']=='joined' for s in ss.values()),'actual_scored_FINALs':sum(s['disposition']=='joined' for s in ss.values()),'gated':sum(s['disposition']=='gated' for s in ss.values()),'valid_outputs':sum(s['valid'] for s in ss.values()),'review_locks':sum(ss[j].get('review_lock',False) for j in review_ids),'valid_review_locks':sum(ss[j]['valid'] and ss[j].get('review_lock',False) for j in review_ids),'full_chains':{c:all(ss['NX-'+c+'-'+r]['valid'] for r in ('stage1','stage2','builder')) for c in ('A','B')},'hard_protocol_failure':fail,'comparative_superiority_claim':None,'qualified_cards':qualified if review_valid else None,'uncertainty_eligible_cards':uncertain if review_valid else None,'disagreements':disagreements,'private_card_bindings':bindings,'all_dispositions':ss,'declared_input_words_by_job':{jid:read(event('admitted',jid))['declared_input_words'] for jid,s in ss.items() if s['disposition']=='joined'},'literal_file_words_by_job':{jid:read(event('admitted',jid))['literal_text_words'] for jid,s in ss.items() if s['disposition']=='joined'},'saved_output_words':sum(s.get('saved_words') or 0 for s in ss.values()),'actual_overhead_starts_as_of_report':len(overhead),'tokens':None,'cost':None,'claim_limits':read(ROOT/'SCOPE.json')['claims'],'execution_goal_coverage':all(ss['NX-B-'+r]['valid'] for r in ('stage1','stage2','builder')) and review_valid,'audit_pending':True}
    return save(ROOT/'reports/report.json',result)

def main():
    p=argparse.ArgumentParser();p.add_argument('command');p.add_argument('args',nargs='*');a=p.parse_args();cmd=a.command;x=a.args
    if cmd=='prepare':r=prepare()
    elif cmd=='freeze':r=freeze()
    elif cmd=='ready':r=ready()
    elif cmd=='prompt':r=prompt(x[0])
    elif cmd=='started':r=started(x[0],x[1])
    elif cmd=='joined':r=joined(x[0],x[1],Path(x[2]))
    elif cmd=='report':r=report()
    elif cmd=='overhead-start':r=overhead_start(x[0],x[1],Path(x[2]))
    elif cmd=='overhead-join':r=overhead_join(x[0],x[1],Path(x[2]),Path(x[3]))
    elif cmd=='validate-case':r=validate_case(read(ROOT/'inputs/fresh-case-and-archive.v1.json'))
    else: raise ValueError('unknown command')
    print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
