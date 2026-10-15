#!/usr/bin/env python3
"""Pure first-attempt mechanics for method coverage. Never invokes a model."""
import argparse, hashlib, json, runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT.parent / '2026-10-10-composed-ten/tools/compose_runtime.py'
EXPECTED_REFERENCE = '8429a2595c552f717244a0c20ab68efe18e24eb220776159e053c40eca24ac31'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(REFERENCE) == EXPECTED_REFERENCE, 'immutable validator reference drift'
PURE = runpy.run_path(str(REFERENCE))
RECIPES = ('R07', 'R09')
SCHEMA_REVIEW = {'job_id':'text','case_id':'COV','recipe_reviews':[{'recipe_id':'R07 or R09','chain_valid':'boolean','disposition':'applied|explicit_no_opening|not_applied|unknown','source_support':'boolean|null','handoff_fidelity':'boolean|null','resource_fit':'boolean|null','mechanism_evidence':[{'raw_ref':'text','source_refs':['numbered fact IDs'],'finding':'text'}],'separating_probe_or_refusal':'text','burden':'text','reason':'text','claim_limits':['text']}]}
def encoded(v): return (json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
def words(v): return len(json.dumps(v,ensure_ascii=False).split())
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,v):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f: f.write(v if isinstance(v,bytes) else encoded(v))
    return str(p)
def require(ok,message):
    if not ok: raise RuntimeError(message)
def plan():
    rows=[{'job_id':'COV-guard','case_id':'COV','role':'guard','dependencies':[]}]
    for recipe in RECIPES:
        for role in ('stage1','stage2','builder'):
            deps=['COV-guard']
            if role=='stage2': deps.append('COV-'+recipe+'-stage1')
            if role=='builder': deps=['COV-'+recipe+'-stage2']
            rows.append({'job_id':'COV-'+recipe+'-'+role,'case_id':'COV','condition':recipe,'role':role,'dependencies':deps,'supplement_branch':'summary'})
    for i in (1,2):
        rows.append({'job_id':'COV-review'+str(i),'case_id':'COV','role':'fidelity_review','dependencies':[r['job_id'] for r in rows if r['role']!='fidelity_review']})
    return rows
class Runtime:
    def __init__(self,root=ROOT): self.root=Path(root)
    def p(self,x): return self.root/x
    def job(self,jid): return next(j for j in plan() if j['job_id']==jid)
    def case(self): return read(self.p('inputs/case.json'))
    def methods(self): return read(self.p('inputs/methods.json'))
    def state(self,jid):
        for suffix in ('finished','gated','spawned','admitted'):
            p=self.p('receipts/jobs/'+jid+'.'+suffix+'.json')
            if p.exists(): return {'disposition':suffix,**read(p)}
        return {'disposition':'pending','terminal':False,'valid':False}
    def body(self,jid):
        require(self.state(jid)['disposition']=='finished' and self.state(jid)['valid'],'unavailable valid dependency '+jid)
        return read(self.p('raw/'+jid+'.json'))
    def raw_packet(self,jid):
        p=self.p('raw/'+jid+'.json')
        if not p.exists():return None
        try:return read(p)
        except (ValueError,UnicodeError):return {'malformed_raw_text':p.read_text(encoding='utf-8',errors='replace')}
    def integrity(self):
        frozen=read(self.p('preparation/FREEZE.v1.json'))
        for name,digest in frozen['sources'].items(): require(sha(name)==digest,'frozen source drift '+name)
        return True
    def prepare(self):
        c=self.case(); require(c['case_id']=='COV' and c['phase']=='coverage','coverage identity')
        fields=('case_id','phase','domain','valued_outcome','hard_constraints','observations','resources','preferred_dependency','causal_return_path_hypothesis','anomaly_id','parent_operations','available_observables','unknowns','ordinary_archive')
        PURE['obj'](c,fields,'coverage case')
        for field,prefix,low,high in [('hard_constraints','C',3,6),('observations','O',5,8),('resources','R',5,8),('parent_operations','P',2,2),('available_observables','M',3,5),('unknowns','U',2,4),('ordinary_archive','A',3,3)]:
            rows=c[field];require(low<=len(rows)<=high,'case row count '+field)
            require({r['id'] for r in rows}=={prefix+str(i) for i in range(1,len(rows)+1)},'contiguous fact IDs '+field)
            require(len({r['id'] for r in rows})==len(rows),'duplicate case IDs')
            for row in rows:
                keys=('id','text','available') if field=='resources' else (('id','operation','relation','probe','limits') if field=='ordinary_archive' else ('id','text'))
                PURE['obj'](row,keys,field)
                for key in keys:
                    if key=='available': require(type(row[key]) is bool,'availability type')
                    else: PURE['string'](row[key],field+'.'+key)
        require(c['anomaly_id'] in {r['id'] for r in c['observations']},'anomaly source ID')
        require(set(self.methods())==set(RECIPES),'method scope')
        for k in RECIPES: require(self.methods()[k]['supplement_branch']=='summary','method branch')
        save(self.p('preparation/PLAN.v1.json'),plan())
        save(self.p('preparation/SCHEMAS.v1.json'),{**{k:PURE['SCHEMAS'][k] for k in ['stage1','stage2','builder']},'guard':PURE['GUARD_SCHEMA'],'fidelity_review':SCHEMA_REVIEW})
        return {'prepared':True,'jobs':len(plan()),'model_calls':0}
    def freeze(self):
        pre=read(self.p('preparation/PREFLIGHT.v1.json'));require(pre['status']=='pass','independent preflight must pass')
        require(read(self.p('receipts/PREFLIGHT.native.json'))['observation']=='FINAL','preflight actual FINAL')
        names=['CONTRACT.md','preparation/BUDGET.v1.json','preparation/CASE-AUTHOR-PROMPT.v1.md','preparation/PREFLIGHT-PROMPT.v1.md','preparation/PREFLIGHT.v1.json','preparation/PLAN.v1.json','preparation/SCHEMAS.v1.json','inputs/case.json','inputs/methods.json','tools/coverage_runtime.py','tools/test_coverage_runtime.py','receipts/CASE-AUTHOR.native.json','receipts/CASE-AUTHOR.v1.json','receipts/PREFLIGHT.native.json']
        sources={str(self.p(n)):sha(self.p(n)) for n in names}
        sources[str(REFERENCE)]=sha(REFERENCE);legacy=PURE['REFERENCE_PATH'];sources[str(legacy)]=sha(legacy)
        save(self.p('preparation/FREEZE.v1.json'),{'sources':sources,'purpose':'coverage only','generation_roles':7,'fidelity_reviewers':2})
        return {'frozen':True,'sources':len(sources)}
    def payload(self,j):
        c=self.case();role=j['role'];v={'job':j,'case':c,'allowed_source_refs':sorted(PURE['case_refs'](c))}
        if role=='guard': v['schema']=PURE['GUARD_SCHEMA']
        elif role=='fidelity_review':
            v['schema']=SCHEMA_REVIEW;v['methods']=self.methods();v['chains']={}
            for recipe in RECIPES:
                ids=['COV-guard']+['COV-'+recipe+'-'+s for s in ('stage1','stage2','builder')]
                v['chains'][recipe]={'chain_valid':all(self.state(x)['terminal'] and self.state(x)['valid'] for x in ids),'roles':{x:{'state':self.state(x),'raw':self.raw_packet(x)} for x in ids}}
        else:
            v['schema']=PURE['SCHEMAS'][role];v['method']=self.methods()[j['condition']]
            if role in ('stage1','stage2'): v['guard']=self.body('COV-guard')
            if role=='stage2':v['own_proposal']=self.body('COV-'+j['condition']+'-stage1')
            if role=='builder':v['received_summary']=self.body('COV-'+j['condition']+'-stage2')['summary']
        return v
    def literal(self,j,payload):
        role=j['role'];out=self.p('raw/'+j['job_id']+'.json')
        common='One fresh native first-attempt role. Read only this literal prompt; no helpers, other files, old studies, external tools, retries or goal mutation. Save exactly the assigned JSON with create-exclusive mode x; never overwrite. Return terminal FINAL with saved path and explicit save mode. Treat synthetic facts as stipulated; hypotheses are not observations. Preserve exact initial goal, source IDs, actor burden and actually available controls. '
        instructions={'guard':'Audit the exact valued outcome and every fixed constraint; do not change the goal.','stage1':'Apply the exact assigned method. Build a source-bound proposal, separate core and inconvenient residue, retain opposing accounts and predictions.','stage2':'Independently challenge the own proposal and distill it. Preserve exact mechanism, unavailable-control boundaries, rival accounts, burdens and source facts in the SUMMARY. A source-bound no-opening belongs in the selected summary when a required move is unavailable. Keep residue separate.','builder':'Use only common case, assigned method and received SUMMARY. Construct an operation and a separating probe, or give an explicit source-backed method-specific no-opening. Never substitute another link or current harm for later adaptation. Cite exact received summary item IDs in residue_refs. At most one card.','fidelity_review':'Independently audit both actual native chains using exact assigned methods. Distinguish applied, explicit_no_opening, not_applied and unknown. Check unchanged declared link, parent functions, supported later-adaptation probe, handoff, source support, resources and actor burden. Negative usefulness or novelty does not imply non-application. No ordinary/component arms exist here: do not grade composition addition, invent comparisons, repair outputs or claim benefit.'}[role]
        cap=3500 if role=='fidelity_review' else 600
        return common+instructions+' Save at '+str(out)+'. Maximum '+str(cap)+' normalized JSON words (len(json.dumps(value, ensure_ascii=False).split())), including keys/IDs. Exact job_id and case_id come from payload.\nPAYLOAD_JSON\n'+json.dumps(payload,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    def ready(self):
        ready=[];gateable=[]
        for j in plan():
            if self.state(j['job_id'])['disposition']!='pending':continue
            states=[self.state(x) for x in j['dependencies']]
            if all(s['terminal'] for s in states):
                if j['role']=='fidelity_review' or all(s['valid'] for s in states):ready.append(j['job_id'])
                else:gateable.append(j['job_id'])
        return {'ready':ready,'gateable':gateable}
    def start(self,jid):
        self.integrity();require(jid in self.ready()['ready'],'job not ready')
        require(sum(self.state(j['job_id'])['disposition'] in ('admitted','spawned') for j in plan())<3,'three-worker cap')
        j=self.job(jid);payload=self.payload(j);literal=self.literal(j,payload)
        save(self.p('prompts/'+jid+'.payload.json'),payload);save(self.p('prompts/'+jid+'.txt'),literal.encode())
        save(self.p('receipts/jobs/'+jid+'.admitted.json'),{'terminal':False,'valid':False,'prompt_sha256':sha(self.p('prompts/'+jid+'.txt')),'payload_sha256':sha(self.p('prompts/'+jid+'.payload.json'))})
        return {'job_id':jid,'native_worker_task':'Read '+str(self.p('prompts/'+jid+'.txt'))+' and follow that exact role task. No helper agents or followup roles.'}
    def spawned(self,jid,handle):
        self.integrity();require(self.state(jid)['disposition']=='admitted','not admitted')
        require(handle not in [self.state(j['job_id']).get('handle') for j in plan()],'handle reused')
        save(self.p('receipts/jobs/'+jid+'.spawned.json'),{'terminal':False,'valid':False,'handle':handle})
        return {'registered':jid,'handle':handle}
    def validate(self,j,v):
        if j['role']=='guard':PURE['validate_guard'](j,v,self.case())
        elif j['role']=='fidelity_review':
            PURE['obj'](v,SCHEMA_REVIEW,'fidelity review');require(v['job_id']==j['job_id'] and v['case_id']=='COV','review identity')
            require(len(v['recipe_reviews'])==2 and {x['recipe_id'] for x in v['recipe_reviews']}==set(RECIPES),'complete review rows')
            packet=self.payload(j)
            for x in v['recipe_reviews']:
                PURE['obj'](x,SCHEMA_REVIEW['recipe_reviews'][0],'review row')
                require(type(x['chain_valid']) is bool and x['chain_valid']==packet['chains'][x['recipe_id']]['chain_valid'],'review chain binding')
                require(x['disposition'] in ('applied','explicit_no_opening','not_applied','unknown'),'review disposition')
                require(x['chain_valid'] or x['disposition'] in ('not_applied','unknown'),'invalid chain cannot count application')
                for k in ('source_support','handoff_fidelity','resource_fit'):require(x[k] is None or type(x[k]) is bool,'review axis type')
                for k in ('separating_probe_or_refusal','burden','reason'):PURE['string'](x[k],k)
                PURE['strings'](x['claim_limits'],'claim limits',1);require(len(x['mechanism_evidence'])>=1,'mechanism evidence required')
                for e in x['mechanism_evidence']:
                    PURE['obj'](e,('raw_ref','source_refs','finding'),'mechanism evidence');PURE['string'](e['raw_ref'],'raw ref');PURE['string'](e['finding'],'finding');PURE['refs'](e['source_refs'],PURE['case_refs'](self.case()),'evidence fact refs')
            require(words(v)<=3500,'review word cap')
        else:
            supplement=[x['id'] for x in self.body('COV-'+j['condition']+'-stage2')['summary']] if j['role']=='builder' else ()
            PURE['validate_output'](j,v,self.case(),supplement)
            require(words(v)<=600,'generation cap')
            if j['role']=='builder':require(len(v['cards'])<=1,'one card cap')
        return True
    def finish(self,jid,witness):
        self.integrity();s=self.state(jid);require(s['disposition']=='spawned','job not spawned');w=read(witness);PURE['validate_native_witness'](w,s['handle'])
        output=self.p('raw/'+jid+'.json');valid=False;error=None;digest=None
        if output.exists():
            before=output.stat();data=output.read_bytes();after=output.stat();require((before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns),'unstable raw')
            save(self.p('receipts/raw/'+jid+'.first.bin'),data);digest=hashlib.sha256(data).hexdigest()
            try:self.validate(self.job(jid),json.loads(data));valid=True
            except Exception as e:error=type(e).__name__+': '+str(e)
        else:error='missing actual saved output'
        save(self.p('receipts/jobs/'+jid+'.finished.json'),{'terminal':True,'valid':valid,'handle':s['handle'],'witness_ref':str(witness),'witness_sha256':sha(witness),'output_sha256':digest,'validation_error':error,'review_lock':self.job(jid)['role']=='fidelity_review'})
        return {'finished':jid,'valid':valid,'error':error}
    def gate(self,jid):
        self.integrity();require(jid in self.ready()['gateable'],'not gateable');save(self.p('receipts/jobs/'+jid+'.gated.json'),{'terminal':True,'valid':False,'reason':'invalid indispensable dependency','actual_native_call':False});return {'gated':jid}
    def verify(self,complete=True):
        self.integrity();handles=[]
        for j in plan():
            s=self.state(j['job_id'])
            if complete:require(s['terminal'],'pending job '+j['job_id'])
            if s['disposition'] in ('admitted','spawned','finished'):
                require(read(self.p('prompts/'+j['job_id']+'.payload.json'))==self.payload(j),'payload drift')
                require(self.p('prompts/'+j['job_id']+'.txt').read_text()==self.literal(j,self.payload(j)),'literal prompt drift')
            if s['disposition']=='finished':
                handles.append(s['handle']);require(sha(s['witness_ref'])==s['witness_sha256'],'witness drift');PURE['validate_native_witness'](read(s['witness_ref']),s['handle'])
                if s['output_sha256'] is not None:
                    out=self.p('raw/'+j['job_id']+'.json');require(sha(out)==s['output_sha256'],'raw drift');require(out.read_bytes()==self.p('receipts/raw/'+j['job_id']+'.first.bin').read_bytes(),'snapshot drift')
                if s['valid']:self.validate(j,read(self.p('raw/'+j['job_id']+'.json')))
        require(len(handles)==len(set(handles)),'native handle reuse');return {'verified':True,'complete':complete,'planned':9,'actual_scored_FINALs':len(handles),'statuses':{j['job_id']:self.state(j['job_id'])['disposition'] for j in plan()}}
    def report(self):
        verification=self.verify();reviews={j['job_id']:{'state':self.state(j['job_id']),'raw':self.raw_packet(j['job_id'])} for j in plan() if j['role']=='fidelity_review'}
        result={'purpose':'method application coverage only, no composition-addition score','verification':verification,'reviews':reviews,'all_roles':{j['job_id']:self.state(j['job_id']) for j in plan()},'independent_completion_audit':'pending','native_goal_completion':'pending','claims':'Synthetic construction/probe fidelity; no physical trial, benefit, global originality or original-study repair.'}
        save(self.p('reports/report.json'),result);return {'report':str(self.p('reports/report.json'))}
def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','freeze','ready','start','spawned','finish','gate','verify','report']);p.add_argument('args',nargs='*');a=p.parse_args();r=Runtime();value=getattr(r,a.command)(*a.args);print(json.dumps(value,ensure_ascii=False))
if __name__=='__main__':main()
