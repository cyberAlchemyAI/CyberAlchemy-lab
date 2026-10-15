#!/usr/bin/env python3
"""Local pure admission/evidence adapter. Model execution is ONLY native collaboration."""
import argparse, copy, datetime, hashlib, json, os, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parents[2]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(v):return (json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n').encode()
def save(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(v if isinstance(v,bytes) else encoded(v));f.flush();os.fsync(f.fileno())
def require(b,m):
    if not b:raise ValueError(m)
def words(v):return len(json.dumps(v,ensure_ascii=False).split())
def replay(case,candidate,oracle=4):
    """State-at-boundary finite replay; no field or physical observation."""
    actions=candidate.get('actions',[]);errors=[];trace=[];unknown=False;impact=0
    seen=set()
    for a in actions:
        if not isinstance(a,dict) or set(a)!={'tick','op','arg'}:errors.append('Action must have exactly tick,op,arg');continue
        t=a['tick']
        if type(t) is not int or t<0 or t>=case['end_boundary']:errors.append('Action tick outside available range');continue
        if t in seen:errors.append('More than one operator action at tick '+str(t))
        seen.add(t)
    if errors:return {'status':'infeasible','errors':errors,'action_count':len(actions),'trace':trace,'evidence':'pure stipulated-model replay'}
    by={a['tick']:a for a in actions}
    if case['domain']=='J':
        s={'intact':True,'pins':set(),'C':False,'V':False,'stem':False,'M':False,'L':False,'Q':False,'measured':False}
        cap=case['capacities'];available=set(case['available']);hold_results=[]
        def retention():
            nonlocal unknown
            if s['pins']:return len(s['pins'])*cap['pin']
            if s['C']:return cap['clip']
            if s['stem']:return min(cap['sleeve'],cap['stem'])
            if s['M'] and s['L']:return min(cap['head'],cap['loop'])
            if s['Q']:
                if not s['measured']:unknown=True
                return oracle
            return 0
        def any_retainer():return bool(s['pins'] or s['C'] or s['V'] or s['M'] or s['L'] or s['Q'])
        for t in range(case['end_boundary']):
            r=retention()
            if t in case['hold_ticks']:
                hold_results.append({'tick':t,'retention':('unmeasured' if s['Q'] and not s['measured'] else r),'demand':case['demand']})
                if r<case['demand']:errors.append('Retention below demand at tick '+str(t))
            a=by.get(t)
            if a is None:continue
            o,x=a['op'],a['arg'];bad=None
            if o not in case['actions']:bad='Unlisted operation '+str(o)
            elif case.get('assigned_absent_dependency') and (x=='H' or o in ['tap','detach','assemble','insert','place']):bad='Assigned missing dependency H cannot be restored'
            elif o=='detach':
                if x!='H' or not s['intact'] or not {'H','M','S'}<=available:bad='detach precondition'
                else:s['intact']=False
            elif o=='assemble':
                if x!='H' or s['intact'] or s['stem'] or s['M'] or not {'H','M','S'}<=available:bad='assemble precondition'
                else:s['intact']=True
            elif o=='tap':
                if x not in ['P1','P2'] or x not in available or x in s['pins'] or not s['intact'] or any([s['C'],s['V'],s['M'],s['L'],s['Q']]):bad='tap precondition'
                else:s['pins'].add(x);impact+=1
            elif o=='pull':
                if x not in s['pins']:bad='pull precondition'
                else:s['pins'].remove(x)
            elif o=='install':
                if x not in ['C','V','Q'] or x not in available or any_retainer():bad='install precondition or occupied assembly'
                else:s[x]=True
            elif o=='remove':
                if x not in ['C','V','Q'] or not s.get(x) or (x=='V' and s['stem']):bad='remove precondition'
                else:s[x]=False
            elif o=='insert':
                if x!='S,V' or 'S' not in available or s['intact'] or not s['V'] or s['stem']:bad='insert precondition'
                else:s['stem']=True
            elif o=='withdraw':
                if x!='S,V' or not s['stem']:bad='withdraw precondition'
                else:s['stem']=False
            elif o=='place':
                if x!='M' or 'M' not in available or s['intact'] or any_retainer():bad='place precondition'
                else:s['M']=True
            elif o=='route':
                if x!='L' or 'L' not in available or s['L'] or s['pins'] or s['C'] or s['V'] or s['Q']:bad='route precondition'
                else:s['L']=True
            elif o=='unroute':
                if x!='L' or not s['L']:bad='unroute precondition'
                else:s['L']=False
            elif o=='lift':
                if x!='M' or not s['M'] or s['L']:bad='lift precondition'
                else:s['M']=False
            elif o=='measure':
                if x!='Q' or 'Q' not in available:bad='measure precondition'
                else:s['measured']=True
            elif o=='idle' and x is not None:bad='idle arg must be null'
            if bad:errors.append(f'tick {t}: {bad}')
            trace.append({'start':t,'complete_boundary':t+1,'op':o,'arg':x,'error':bad})
        if any_retainer() or s['stem']:errors.append('Installed retainer remains at final boundary')
        return {'status':'infeasible' if errors else ('unknown' if unknown else 'feasible'),'errors':errors,'action_count':sum(a['op']!='idle' for a in actions),'impact_actions':impact,'soft_preference_satisfied':impact<=case.get('impact_preference',2),'hold_results':hold_results,'trace':trace,'measurement':oracle if s['measured'] else None,'evidence':'pure stipulated-model replay, oracle only returned after an assigned measurement'}
    cache={};cards={};compiled=False;version=1;required={'application','outcome','comparison','ceiling'}
    fields=set(candidate.get('claim_fields',[]))
    for t in range(case['end_boundary']):
        if t==case.get('update_boundary'):version=2;cache.pop('A',None);trace.append({'boundary':t,'event':'A version 2; old cache invalidated'})
        a=by.get(t)
        if not a:continue
        o,x=a['op'],a['arg'];bad=None
        if o=='read':
            if x not in case['sources']:bad='Unknown source'
            else:cache[x]=version if x=='A' else 1
        elif o=='write':
            ids={f'E{x}','A','K','U'}
            if not isinstance(x,str) or not x.isdigit() or not 1<=int(x)<=case['n_claims']:bad='Unknown claim'
            elif not ids<=set(cache) or cache['A']!=version:bad='Missing/current cited tokens'
            elif fields!=required:bad='Missing contract fields: '+','.join(sorted(required-fields))
            else:cards[x]=version
        elif o=='compile':
            if x is not None or set(cards)!={str(i) for i in range(1,case['n_claims']+1)} or any(v!=version for v in cards.values()):bad='Compile requires every current valid card'
            else:compiled=True
        elif o!='idle' or x is not None:bad='Unlisted operation/argument'
        if bad:errors.append(f'tick {t}: {bad}')
        trace.append({'start':t,'complete_boundary':t+1,'op':o,'arg':x,'error':bad})
    if not compiled:errors.append('No valid compiled report by deadline')
    return {'status':'infeasible' if errors else 'feasible','errors':errors,'action_count':sum(a['op']!='idle' for a in actions),'read_count':sum(a['op']=='read' for a in actions),'write_count':sum(a['op']=='write' for a in actions),'compiled':compiled,'trace':trace,'evidence':'pure stipulated-reporting model; no human benefit measured'}

SCHEMA={'job_id':'exact string','strategy_id':'exact string','arm':'exact string','case_id':'exact string','operation_trace':[{'step':1,'action':'what actually done','source_refs':['exact allowed fact IDs'],'input_job_refs':['exact direct dependency job IDs'],'result':'finding; mark modeled vs observed'}],'candidates':[{'id':'unique local ID','mechanism':'causal operation','actions':[{'tick':0,'op':'exact primitive','arg':'exact argument or null'}],'claim_fields':['application','outcome','comparison','ceiling'],'source_refs':['exact allowed fact IDs'],'prediction':'measured/modeled/conditional clearly','defeat':'specific condition','burden':'operator and displaced work','lineage':'initial/received/changed provenance'}],'attack':{'failure':'specific criticism or honest no supported attack','invariant':'unchanged required function','permitted_variable':'available opening or none','source_refs':['allowed fact IDs']},'handoff':{'summary':'source-bound construction contract with exact operations, constraints, uncertainty/refusal','residue':'inconvenient detail, not supplied to fresh builder unless summary explicitly includes it'},'budget_used':{'search_slots':6,'allocation':'declared before search','candidate_count':0,'limits':'word caps are not equal compute'},'limits':['claim ceilings'],'selection':{'ratings':[],'implementation':[],'investigation':[],'displaced':[]},'method_card':{},'revision':{} }
REVIEW_SCHEMA={'job_id':'exact string','strategy_id':'REVIEW','arm':'exact string','case_id':'J0','strategy_reviews':[{'strategy_id':'ACxx','application':'applied|explicit_no_opening|not_applied|unknown','operative_clauses':[{'clause':'exact operative requirement','fulfilled':True,'evidence_jobs':['literal raw job IDs'],'reason':'specific evidence'}],'source_support':True,'handoff_fidelity':True,'resource_fit':True,'comparisons':[{'arm_pair':['T','OLD'],'available':True,'result':'specific construction/selection/transfer distinction or tie; no score fabrication','qualified_addition':False,'upstream_overlap':'exact earlier current/archived role or unknown','usefulness':'finite-case result','burden':'actual non-idle actions/other costs','evidence_jobs':['exact IDs']}],'historical_lineage':'conceptual precedents and selective raw inspection; coverage limit','learning_or_human_limit':'exact ceiling','reason':'summary'}],'disagreements_preserved':True}

class Runtime:
    def __init__(self,root=ROOT):self.root=Path(root)
    def p(self,s):return self.root/s
    def plan(self):return read(self.p('preparation/PLAN.v1.json'))
    def job(self,jid):return next(j for j in self.plan() if j['job_id']==jid)
    def state(self,jid):
        for suffix in ['failed','finished','gated','spawned','admitted']:
            p=self.p('receipts/jobs/'+jid+'.'+suffix+'.json')
            if p.exists():return {'disposition':suffix,**read(p)}
        return {'disposition':'pending','terminal':False,'valid':False}
    def invocations(self):
        return [read(p) for p in self.p('receipts/invocations').glob('*.json')] if self.p('receipts/invocations').exists() else []
    def budget(self):
        actual=self.invocations();pending=sum(self.state(j['job_id'])['disposition'] in ['pending','admitted'] for j in self.plan())
        audits=max(0,2-sum(v['purpose']=='completion_audit' and v['outcome']=='actual_spawn_observed' for v in actual))
        coordinator=0 if any(v['purpose']=='coordinator' and v['outcome']=='actual_spawn_observed' for v in actual) else 1
        return {'actual_native_calls':len(actual),'remaining_scheduled_calls':pending,'required_auditors_reserved':audits,'coordinator_remaining':coordinator,'ceiling':260,'prospective_total':len(actual)+pending+audits+coordinator}
    def reserve_overhead(self,iid,purpose):
        require(purpose in ['coordinator','completion_audit','unplanned'],'Reserved overhead purpose')
        b=self.budget();extra=0 if (purpose=='coordinator' and b['coordinator_remaining']) or (purpose=='completion_audit' and b['required_auditors_reserved']) else 1
        require(b['prospective_total']+extra<=260,'Overhead pre-call budget exceeded')
        save(self.p('receipts/reservations/overhead-'+iid+'.json'),{'invocation_id':iid,'purpose':purpose,'status':'pre_call_reserved_only','utc_reserved':now(),'budget_before_call':b,'actual_call_not_yet_observed':True})
        return {'overhead_reserved':iid,'purpose':purpose,'budget':b}
    def record_overhead(self,iid,handle,purpose,evidence,outcome='spawn'):
        require(purpose in ['preparation','preflight','coordinator','completion_audit','unplanned'],'Overhead purpose')
        require(outcome in ['spawn','error'] and bool(evidence) and (bool(handle) or outcome=='error'),'Actual observed overhead success/error evidence required')
        if purpose in ['coordinator','completion_audit']:require(self.p('receipts/reservations/overhead-'+iid+'.json').exists(),'Overhead requires pre-call reservation')
        save(self.p('receipts/invocations/'+iid+'.json'),{'invocation_id':iid,'purpose':purpose,'outcome':'actual_spawn_observed' if outcome=='spawn' else 'actual_tool_error_observed','handle':handle,'evidence':evidence,'utc_recorded':now(),'not_pre_call_reservation':True})
        return {'recorded_actual_invocation':iid,'budget':self.budget()}
    def effective_case(self,j):
        c=read(self.p('inputs/cases/'+j['case_id']+'.json'))
        if j['strategy_id']=='AC11':
            if j['arm'].startswith('B'):c['impact_preference']=int(j['arm'][1:])
            elif j['arm']=='OLD':c['impact_preference']=0
        return c
    def body(self,jid):
        s=self.state(jid);require(s['terminal'] and s['valid'],'Invalid dependency '+jid);return read(self.p('raw/'+jid+'.json'))
    def integrity(self):
        v=read(self.p('preparation/FREEZE.v1.json'))
        for name,digest in v['sources'].items():require(sha(name)==digest,'Frozen source drift '+name)
        return True
    def ready(self):
        out={'ready':[],'gateable':[]}
        for j in self.plan():
            if self.state(j['job_id'])['disposition']!='pending':continue
            ss=[self.state(d) for d in j['dependencies']]
            if all(s['terminal'] for s in ss):out['ready' if j['role']=='review' or all(s['valid'] for s in ss) else 'gateable'].append(j['job_id'])
        return out
    def prepare(self):
        plan=self.plan();require(len(plan)+7<=260,'Prospective call budget exceeded')
        ids=[j['job_id'] for j in plan];require(len(ids)==len(set(ids)),'Duplicate job')
        for j in plan:
            require(set(j['dependencies'])<=set(ids),'Unknown dependency')
            require(j['job_id'] not in j['dependencies'],'Self dependency')
        save(self.p('preparation/SCHEMAS.v1.json'),{'role':SCHEMA,'review':REVIEW_SCHEMA})
        w=read(self.p('inputs/cases/W0.json'));a=[{'tick':i,'op':'read','arg':s} for i,s in enumerate(w['sources'])]+[{'tick':7+i,'op':'write','arg':str(i+1)} for i in range(4)]+[{'tick':11,'op':'compile','arg':None}]
        seed={'id':'seed-incomplete','mechanism':'four summaries with omitted evidence dimensions','actions':a,'claim_fields':['application','outcome']}
        save(self.p('inputs/frame-failure.json'),{'candidate':seed,'replay':replay(w,seed),'status':'actual executed pure model failure, authored negative exercise common to AC06 conditions'})
        pool=read(self.p('inputs/fixed-pool.json'));j=read(self.p('inputs/cases/J0.json'));save(self.p('preparation/CORE-VERIFICATION.v1.json'),{'candidate':pool['candidates'][0],'replay':replay(j,pool['candidates'][0]),'verified_core':'Known two-pin panel join in finite J0, not physical verification; stable panel requirements preserved.'})
        return {'prepared':True,'planned_jobs':len(plan),'model_calls':0}
    def freeze(self):
        require(read(self.p('preparation/PREFLIGHT.v1.json'))['status']=='pass','Preflight does not pass')
        require(read(self.p('receipts/preflight.final.json'))['observation']=='actual_FINAL','Actual preflight terminal witness absent')
        names=list(self.p('inputs').rglob('*'))+list(self.p('private').rglob('*'))+list(self.p('tools').glob('*.py'))+list(self.p('preparation').glob('*'))+[self.p('CONTRACT.md')]
        # Existing historical corpus is bound without exposing it to generation.
        names+=list(BASE.rglob('*.json'))+list(BASE.rglob('*.md'))
        names=[p.resolve() for p in names if p.is_file() and (self.root.resolve() not in p.parents or (str(p).startswith(str(self.p('inputs').resolve())) or str(p).startswith(str(self.p('private').resolve())) or str(p).startswith(str(self.p('tools').resolve())) or str(p).startswith(str(self.p('preparation').resolve())) or p.name=='CONTRACT.md'))]
        # Main report will be extended after execution; bind snapshot, not mutable publication.
        names=[p for p in names if p!=BASE/'RESEARCH-REPORT.md']
        names=list(dict.fromkeys(names));sources={str(p):sha(p) for p in names if self.root.resolve() in p.parents}
        historical={str(p):sha(p) for p in names if self.root.resolve() not in p.parents}
        save(self.p('preparation/FREEZE.v1.json'),{'sources':sources,'historical_sources':historical,'utc':now(),'planned_jobs':len(self.plan()),'actual_native_execution':'Not established by this source freeze','root_publication_exception':str(BASE/'RESEARCH-REPORT.md'),'historical_raw_immutable':True})
        return {'frozen':True,'sources':len(sources),'historical_sources':len(historical)}
    def payload(self,j):
        role=j['role'];case=self.effective_case(j)
        v={'job':j,'schema':REVIEW_SCHEMA if role=='review' else SCHEMA,'case':case,'method':read(self.p('inputs/methods.json'))[j['method_id']],'allowed_source_refs':[f['id'] for f in case['facts']]+['U01','U02','U03','U04','U05','U06','AM','AI','EX1','EX2','FB01'],'allowed_input_job_refs':j['dependencies'],'candidate_cap':3,'word_cap':j['word_cap']}
        if role=='review':
            v['methods']={k:m for k,m in read(self.p('inputs/methods.json')).items() if k in j['review_strategies']}
            v['fidelity_requirements']=self.p('preparation/FIDELITY-COMPLETION-REQUIREMENTS.v1.md').read_text()
            v['prior_map']=self.p('preparation/PRIOR-COMPARATOR-MAP.v1.md').read_text()
            v['actual_chains']={d:{'state':self.state(d),'raw':read(self.p('raw/'+d+'.json')) if self.p('raw/'+d+'.json').exists() else None,'replay':read(self.p('replays/'+d+'.json')) if self.p('replays/'+d+'.json').exists() else None} for d in j['dependencies']}
            for d,record in v['actual_chains'].items():
                side=self.p('raw/'+d+'.arrangements.json')
                if side.exists():record['arrangement_sidecar']={'bytes_as_utf8':side.read_text(),'sha256':sha(side),'ordering_observation':record['state'].get('arrangement_ordering_observation')}
            v['historical_paths_for_selective_read']=[str(BASE/'novelty/runs/2026-10-10-composed-ten/raw/CONF-S04-stage1.json'),str(BASE/'novelty/runs/2026-10-10-composed-ten/raw/CONF-R04-builder.json'),str(BASE/'novelty/runs/2026-10-08-process-all/RESULTS.md'),str(BASE/'novelty/runs/2026-10-08-next-all/reports/ALL13-AUDITED-RESULTS.md')]
            return v
        if case['domain']=='W':v['actual_beneficiary']=read(self.p('inputs/beneficiary-evidence.json'))
        if j['strategy_id'] not in ['AC09','AC16','AC17','AC20'] and role not in ['retained_card','revision']:v['common_analog_source_bank']=read(self.p('inputs/analogues.json'))
        deps={d:self.body(d) for d in j['dependencies']}
        if role=='builder':
            if j['strategy_id']=='AC12':
                attack=next(iter(deps.values()))['attack'];v['received_criticism']=attack['failure'];v['criticism_sha256']=hashlib.sha256(attack['failure'].encode()).hexdigest()
                if j['arm']!='CRITIQUE':v['received_opening']={k:attack[k] for k in ['invariant','permitted_variable','source_refs']}
            else:v['received_handoffs']={d:body['handoff']['summary'] for d,body in deps.items()}
        elif role=='resumption':v['essential_summary']=next(iter(deps.values()))['handoff']['summary'];v['context_manifest']={'continued':j['arm']=='CONT','fresh_fork':j['arm']=='FRESH','common_literal_essentials_equal':True,'intentional_removed_history':'Fresh omits original preparation role conversation/raw search; continued keeps actual same-agent history.'}
        elif role=='transfer':
            if j['strategy_id']=='AC16':
                if j['arm'] in ['RETRIEVED','ACTIVE']:v['retrieved_card']=next(iter(deps.values()))['method_card']
                elif j['arm'].startswith('IMMEDIATE'):v['practice_history']=deps;v['practice_feedback']={d:read(self.p('replays/'+d+'.json')) for d in deps}
                elif j['arm']=='NOCARD':v['external_state']='No teacher state transmitted; fresh artifact-free role. Completion prerequisite only.'
            elif j['strategy_id']=='AC17':
                original=read(self.p('inputs/revision-card.v1.json'));v['retrieved_card']=original if j['arm']=='FIXED' else self.body('AC17-revision')['method_card'];v['matched_failure_feedback']=read(self.p('inputs/revision-feedback.json'))
        else:
            v['received_roles']=deps
            v['received_replays']={d:read(self.p('replays/'+d+'.json')) for d in deps if self.p('replays/'+d+'.json').exists()}
            sides={d:{'bytes_as_utf8':self.p('raw/'+d+'.arrangements.json').read_text(),'sha256':sha(self.p('raw/'+d+'.arrangements.json')),'ordering_observation':self.state(d).get('arrangement_ordering_observation')} for d in deps if self.p('raw/'+d+'.arrangements.json').exists()}
            if sides:v['received_arrangement_sidecars']=sides
        if j['strategy_id']=='AC06':v['actual_common_frame_failure']=read(self.p('inputs/frame-failure.json'))
        if j['strategy_id']=='AC10':v['verified_core']=read(self.p('preparation/CORE-VERIFICATION.v1.json'))
        if j['strategy_id']=='AC07':v['fixed_search_budget']={'slots':6,'T':'3 breadth then 3 depth','OLD':'3 families then 3 comparison/development slots','BREADTH':'6 breadth/0 depth','DEPTH':'0 breadth/6 depth','selection_before_outcomes':True}
        if j['strategy_id']=='AC09' and (j['arm']=='BEFORE' or (j['arm']=='AFTER' and role!='example_first')):v['examples']=read(self.p('inputs/examples.json'))
        if role=='selection':v['fixed_pool']=read(self.p('inputs/fixed-pool.json'));v['fixed_pool_sha256']=sha(self.p('inputs/fixed-pool.json'))
        if role=='revision':v['old_card']=read(self.p('inputs/revision-card.v1.json'));v['actual_feedback']=read(self.p('inputs/revision-feedback.json'))
        if role=='source_route':
            bank=read(self.p('inputs/analogues.json'));idx=int(j['job_id'][-1]);keys=['route_material'] if j['arm']=='SHARED' else ([['route_material','route_information'][idx]] if j['arm']=='DISTINCT' else ['route_material','route_information'])
            v['routed_sources']={k:bank[k] for k in keys};v['source_exposure_manifest']={'selectors':keys,'distinct_empirical_datasets':False,'unique_bodies':len(keys),'literal_bytes':len(encoded(v['routed_sources']))}
        allowed=[f['id'] for f in case['facts']]
        if 'actual_beneficiary' in v:allowed+=['U01','U02','U03','U04','U05','U06']
        if 'common_analog_source_bank' in v:allowed+=['AM','AI']
        if 'routed_sources' in v:allowed+=[s['id'] for s in v['routed_sources'].values()]
        if 'examples' in v:allowed+=['EX1','EX2']
        if 'actual_feedback' in v or 'matched_failure_feedback' in v:allowed+=['FB01']
        # Dependency provenance is delivered data, not permission to browse hidden source packs.
        forwarded={}
        def cited_ids(x):
            out=set()
            if isinstance(x,dict):
                for k,y in x.items():
                    if k=='source_refs' and isinstance(y,list):out.update(a for a in y if isinstance(a,str))
                    else:out.update(cited_ids(y))
            elif isinstance(x,list):
                for y in x:out.update(cited_ids(y))
            return out
        for d,body in deps.items():
            if role=='builder':
                summary=body['handoff']['summary'];ids={x for x in ['AM','AI','EX1','EX2','U01','U02','U03','U04','U05','U06','FB01'] if re.search(r'\b'+x+r'\b',summary)}
            elif role=='transfer' and j['strategy_id']=='AC16' and j['arm']=='NOCARD':ids=set()
            elif 'received_roles' in v or 'practice_history' in v:ids=cited_ids(body)
            else:ids=set()
            if ids:
                allowed+=sorted(ids);forwarded[d]={'source_ids':sorted(ids),'scope':'Literal received role data or selected summary only; original source bytes are not thereby supplied.'}
        v['forwarded_source_provenance']=forwarded
        v['allowed_source_refs']=list(dict.fromkeys(allowed))
        return v
    def literal(self,j,v):
        out=self.p('raw/'+j['job_id']+'.json')
        common='One bounded actual native role. Read only this literal packet and assigned allowed historical files when review. No web, memory, helper agents, prior output browsing, goal updates, extra model calls or retries. Save create-exclusive (Python open x or xb); never overwrite. Treat case rules as synthetic axioms. Source refs must be literal allowed IDs; input_job_refs must be literal direct dependencies. All schema keys required, irrelevant selection/method_card/revision use empty defaults. At most 3 candidate constructions, fresh builder at most 1; actions exactly tick/op/arg. No outside operations. Show causal differences, burden, uncertainty and unchanged required function. Terminal FINAL must identify actual saved path and exclusive save; a planned file is not output. '
        roles={'proposal':'Actually execute the assigned method using explicitly recorded concern passes; preserve both concerns and exact hypothesis. For AC01 properties first; AC02 map both analogues; AC03 old/new one-rule grammar then excluded-operation search; AC04 create-exclusive sidecar raw/'+j['job_id']+'.arrangements.json before any function interpretation, then interpret, swap local assembly/interpretation concerns once and record rejected arrangement; AC05 round trip all source facts; AC06 use actual common modeled failure and justified frame delta; AC07 exactly six budget slots; AC10 fixed verified core and exactly one changed connection; AC13 typed necessity and admissible countermodel; AC18 cite actual U utterances and forecast burden separately. If unsupported/no opening, preserve exact boundary. These are local concern passes, not independent agents.',
        'critique':'Fresh independent attack and Distill pass. Apply the assigned method to actual received proposal; inspect exact changed operation, hard requirements, primitive-resource support and model replay; retain mismatch, invariant, available variable, uncertainty and refusal in selected SUMMARY. AC04 reconstruct/swap once if not already recorded; preserve arrangement sidecar provenance. Do not erase source-bound no-opening or invent another problem. Do not claim you run canonical skill executors.',
        'builder':'Fresh builder gets common facts, assigned method and selected handoff only (AC12 variant explicitly controlled). Actually construct a primitive-action candidate plus separating probe/defeat, or carry source-bound method-specific refusal. Preserve every relevant operation, invariant, uncertainty and applicable card requirement. Recovering received/upstream idea is not new generation.',
        'shared_attack':'Independently attack the actual incumbent, save exact criticism separate from invariant/permitted variable. No subsequent solution; same criticism is reused literally.',
        'context_preparation':'Actually prepare incompatible accounts and source-bound tensions, save essential-fact summary. A later authorized continuation may be sent to this same native agent; do not launch helpers or more turns yourself.',
        'resumption':'Actually resume search under the declared context condition. Record new vs prepared mechanisms and cue exposure. Continued is an actual followup to the same preparation agent; fresh is fork_turns none. No human incubation claim.',
        'example_first':'Generate bounded candidates under current exposure only; no other stages/files. Preserve source-feature provenance. EX is present only if BEFORE; AFTER/NONE have task facts only.',
        'example_second':'Actually revise from saved first candidates and current examples if present; preserve both independent originals and new/changed variants in trace. Record EX feature copying versus supported transfer and candidate loss.',
        'concern':'Generate by the exact assigned concern/exclusions. No fabricated other investigator or source history. INDEPENDENT and AC20 PRE do not see another proposal; IMMEDIATE service does. Preserve actual precursor candidates.',
        'exchange':'Inspect actual joined proposal pool; identify contrary dependency/prediction and actual unresolved tension, or supported no-opening. Distill construction contract and full initial source lineage; do not credit an already proposed mechanism as exchange addition.',
        'selection':'Actually rate/reject/select from fixed pool only. All six candidate IDs need ratings/reasons; no new actions/candidates or simulated oracle result. T AC15 applies frozen frontier; T AC19 separates infeasible/missing evidence/burden/mismatch/unfamiliarity. Preserve correct rejections and at most one bounded next-test recommendation.',
        'practice':'Actually perform practice using assigned method and action candidates; distinguish forced negative exercise from organic failures. Root will replay after this save. Received earlier replay is actual model feedback. No heldout access.',
        'retained_card':'Create reusable procedure-only external method_card from actual two practice outputs/replays. No task identities/capacities/timings/solved answers/holdout references. Keep invariant, conditions, operation, applicability/refusal and counterexample. Ordinary active practice retains ordinary procedure. External file retrieval is not model weight learning.',
        'transfer':'Actually apply only supplied current task facts, assigned method and declared retrieved state/history. One action construction or exact supported refusal, separating check, source/property mapping and scaffold ledger. Do not invent mechanical affordances in workflow tasks. Fresh no-card outputs have no teacher state.',
        'revision':'Classify source-bound historical failure and revise exactly construction_obligation in immutable old_card. All other fields byte-equivalent. Save entire revised method_card plus revision old/new values and evidence. No solved case answer, no holdout browsing. If no legitimate change possible, explicitly carry no-opening and unchanged card.',
        'source_route':'Actually inspect supplied routed bytes/selectors; map source relation to common target facts and keep mismatch. Preserve pre-assistance candidates; record actual source→candidate graph and feasible mechanism differences. Same synthetic authorship and source-union differences limit independence/efficacy claims.',
        'review':'Independent semantic review of all listed cards, actual stages, controls and replays. Judge application separately from feasible outcome, matched final addition, full-current-upstream novelty, selection and learning. Check exact clauses, ordering, actual independent/fresh boundaries, retained cards, fixed pool, beneficiary provenance, source-route bytes, resource/cost fairness. Read allowed historical paths if useful and cite what was actually inspected; inventory enumeration is not exhaustive semantic inspection. A useful substitute that omits assigned clause is not-applied. Missing comparator invalid/gated stays unknown, never zero. Preserve raw disagreements and historical grades.'}
        # Controls receive their own older clause, never the new intervention's checklist.
        roles['proposal']='Actually execute the assigned method using explicitly recorded local concern passes; preserve changed operation, hard constraints, source support, resources and exact failure/no-opening boundary. These are local passes, not independent agents. Do not add another method merely because it exists elsewhere.'
        if j['strategy_id']=='AC04' and j['arm']=='T':roles['proposal']+=' Save create-exclusive '+str(self.p('raw/'+j['job_id']+'.arrangements.json'))+' with bounded valid arrangements before assigning any target role; then interpret, swap local assembly/interpretation concerns once, reject one interpretation and reconstruct a survivor. Sidecar must precede interpretation save. Combined normalized JSON words in main output plus sidecar must fit the same 1800 word cap; keep sidecar at most 400 words.'
        if not (j['strategy_id']=='AC04' and j['arm']=='T'):roles['critique']=roles['critique'].replace('AC04 reconstruct/swap once if not already recorded; preserve arrangement sidecar provenance. ','')
        return common+roles[j['role']]+' Additional exact condition instructions: '+j.get('instructions','')+'\nSave JSON at '+str(out)+'\nMAXIMUM '+str(j['word_cap'])+' normalized JSON words. Candidate action effects are replayed by root. No self-grading as final result.\nPAYLOAD_JSON\n'+json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n'
    def start(self,jid):
        self.integrity();require(jid in self.ready()['ready'],'Job not ready')
        require(self.budget()['prospective_total']<=260,'Actual invocation ledger plus admitted remaining work/audit reserve exceeds ceiling')
        require(sum(self.state(j['job_id'])['disposition'] in ['admitted','spawned'] for j in self.plan())<2,'Two child-worker ceiling under root+coordinator')
        j=self.job(jid);v=self.payload(j);prompt=self.literal(j,v)
        save(self.p('prompts/'+jid+'.payload.json'),v);save(self.p('prompts/'+jid+'.txt'),prompt.encode())
        save(self.p('receipts/jobs/'+jid+'.admitted.json'),{'job_id':jid,'utc':now(),'terminal':False,'valid':False,'prompt_sha256':sha(self.p('prompts/'+jid+'.txt')),'payload_sha256':sha(self.p('prompts/'+jid+'.payload.json'))})
        save(self.p('receipts/reservations/score-'+jid+'.json'),{'invocation_id':'score-'+jid,'job_id':jid,'utc_reserved':now(),'status':'pre_call_reserved_only','purpose':'scheduled_job','budget_before_call':self.budget()})
        follow=j.get('followup_of')
        return {'job_id':jid,'task_name':'acw_'+str([r['job_id'] for r in self.plan()].index(jid)),'message':'Read '+str(self.p('prompts/'+jid+'.txt'))+' and perform exactly that one bounded native role. Save assigned JSON exclusively and return actual FINAL. No helpers or extra turns.','call_type':'followup' if follow else 'spawn','target':self.state(follow).get('handle') if follow else None}
    def spawned(self,jid,handle):
        j=self.job(jid);require(self.state(jid)['disposition']=='admitted','Not admitted')
        if j.get('followup_of'):require(handle==self.state(j['followup_of'])['handle'],'Continuation not same actual agent')
        else:require(handle not in [self.state(r['job_id']).get('handle') for r in self.plan()],'Fresh agent handle reused')
        save(self.p('receipts/invocations/score-'+jid+'.json'),{'invocation_id':'score-'+jid,'job_id':jid,'purpose':'scheduled_job','outcome':'actual_followup_observed' if j.get('followup_of') else 'actual_spawn_observed','handle':handle,'utc_recorded':now(),'actual_tool_observation':'Coordinator directly observed collaboration tool return, then supplied exact handle.'})
        save(self.p('receipts/jobs/'+jid+'.spawned.json'),{'job_id':jid,'utc':now(),'handle':handle,'call_type':'followup' if j.get('followup_of') else 'spawn','actual_native_invocation':True,'terminal':False,'valid':False})
        return {'registered':jid,'handle':handle}
    def failed(self,jid,witness):
        require(self.state(jid)['disposition']=='admitted','Failed start must follow pre-call admission')
        require(witness.get('observation')=='actual_TOOL_ERROR' and bool(witness.get('text')),'Actual tool error witness required')
        save(self.p('receipts/invocations/score-'+jid+'.json'),{'invocation_id':'score-'+jid,'job_id':jid,'purpose':'scheduled_job','outcome':'actual_tool_error_observed','witness':witness,'utc_recorded':now()})
        save(self.p('receipts/jobs/'+jid+'.failed.json'),{'job_id':jid,'terminal':True,'valid':False,'actual_native_invocation':True,'error':witness['text'],'utc':now(),'no_agent_FINAL_claimed':True})
        return {'failed_actual_attempt':jid,'budget':self.budget()}
    def validate(self,j,v):
        schema=REVIEW_SCHEMA if j['role']=='review' else SCHEMA
        require(isinstance(v,dict) and set(v)==set(schema),'Exact role JSON keys required')
        for k in ['job_id','strategy_id','arm','case_id']:require(v[k]==j[k],'Identity mismatch '+k)
        require(words(v)<=j['word_cap'],'Output word cap')
        if j['role']=='review':
            require({r['strategy_id'] for r in v['strategy_reviews']}==set(j['review_strategies']) and len(v['strategy_reviews'])==len(j['review_strategies']),'Complete assigned review rows')
            for r in v['strategy_reviews']:
                require(set(r)==set(REVIEW_SCHEMA['strategy_reviews'][0]),'Exact review row keys')
                require(r['application'] in ['applied','explicit_no_opening','not_applied','unknown'],'Invalid application disposition')
                for k in ['source_support','handoff_fidelity','resource_fit']:require(r[k] is None or type(r[k]) is bool,'Review tri-state '+k)
                for c in r['operative_clauses']:
                    require(c['fulfilled'] is None or type(c['fulfilled']) is bool,'Clause tri-state')
                    require(set(c['evidence_jobs'])<=set(j['dependencies']),'Review clause evidence membership')
                for c in r['comparisons']:
                    require(c['available'] is None or type(c['available']) is bool,'Comparison availability tri-state')
                    require(c['qualified_addition'] is None or type(c['qualified_addition']) is bool,'Addition tri-state')
                    require(set(c['evidence_jobs'])<=set(j['dependencies']),'Review comparison evidence membership')
            return
        require(isinstance(v['operation_trace'],list) and bool(v['operation_trace']),'Actual trace absent')
        require(isinstance(v['candidates'],list) and len(v['candidates'])<= (1 if j['role'] in ['builder','transfer'] else 3),'Candidate cap')
        require(len({c['id'] for c in v['candidates']})==len(v['candidates']),'Duplicate candidate ID')
        allowed=set(read(self.p('prompts/'+j['job_id']+'.payload.json'))['allowed_source_refs']);deps=set(j['dependencies'])
        def visit(x):
            if isinstance(x,dict):
                for k,y in x.items():
                    if k=='source_refs':require(isinstance(y,list) and all(isinstance(a,str) and a in allowed for a in y),'Literal fact reference grammar/membership')
                    if k=='input_job_refs':require(isinstance(y,list) and all(a in deps for a in y),'Direct dependency references only')
                    visit(y)
            elif isinstance(x,list):
                for y in x:visit(y)
        visit(v)
        require(isinstance(v['handoff'],dict) and isinstance(v['handoff'].get('summary'),str) and bool(v['handoff']['summary'].strip()),'Selected summary absent')
        require(set(v['attack'])=={'failure','invariant','permitted_variable','source_refs'},'Attack contract keys')
        for c in v['candidates']:
            require(set(c)==set(SCHEMA['candidates'][0]),'Exact candidate keys')
            require(isinstance(c['actions'],list),'Candidate actions absent')
            for a in c['actions']:require(isinstance(a,dict) and set(a)=={'tick','op','arg'} and type(a['tick']) is int,'Primitive action syntax')
        if j['strategy_id']=='AC04' and j['arm']=='T' and j['role']=='proposal':
            side=self.p('raw/'+j['job_id']+'.arrangements.json');require(side.exists(),'Pre-interpretation arrangement sidecar missing')
            require(words(read(side))<=400 and words(v)+words(read(side))<=j['word_cap'],'Combined arrangement/output word cap')
            require(side.stat().st_mtime_ns<=self.p('raw/'+j['job_id']+'.json').stat().st_mtime_ns,'Arrangement save occurred after interpretation output')
        if j['role']=='selection':
            sel=v['selection'];require(len(sel['ratings'])==6,'All fixed candidates require ratings')
            require(len(sel['implementation'])<=2 and len(sel['investigation'])<=1,'Selection caps')
        if j['role']=='revision':
            old=read(self.p('inputs/revision-card.v1.json'));new=v['method_card'];require(set(new)==set(old),'Revision card keys')
            require([k for k in old if old[k]!=new[k]] in [[],['construction_obligation']],'More than one permitted method field changed')
    def finish(self,jid,witness):
        self.integrity();j=self.job(jid);s=self.state(jid);require(s['disposition']=='spawned','Not actually registered spawned')
        require(witness.get('observation')=='actual_FINAL' and witness.get('handle')==s['handle'] and isinstance(witness.get('text'),str) and bool(witness['text']),'Actual native FINAL witness required')
        save(self.p('receipts/jobs/'+jid+'.native-final.json'),{**witness,'utc_observed':now(),'limit':'Coordinator observed actual collaboration message; no independent platform attestation.'})
        p=self.p('raw/'+jid+'.json');valid=False;error=None;digest=None;v=None;side_digest=None;side_order=None
        if p.exists():
            data=p.read_bytes();digest=hashlib.sha256(data).hexdigest();save(self.p('locks/'+jid+'.first-bytes'),data)
            try:v=json.loads(data);self.validate(j,v);valid=True
            except Exception as e:error=str(e)
        else:error='Native FINAL without assigned saved output'
        side=self.p('raw/'+jid+'.arrangements.json')
        if side.exists():
            side_data=side.read_bytes();side_digest=hashlib.sha256(side_data).hexdigest();save(self.p('locks/'+jid+'.arrangements.first-bytes'),side_data)
            side_order={'sidecar_mtime_ns':side.stat().st_mtime_ns,'main_mtime_ns':p.stat().st_mtime_ns if p.exists() else None,'observed_before_main_save':p.exists() and side.stat().st_mtime_ns<=p.stat().st_mtime_ns,'limit':'Filesystem write-order observation, not attestation of internal thought timing.'}
        if v is not None and isinstance(v,dict):
            case=self.effective_case(j)
            replays=[];candidates=v.get('candidates',[])
            if not isinstance(candidates,list):
                replays.append({'candidate_id':None,'replay':{'status':'invalid_candidates','errors':['Candidate list malformed; first native output remains invalid.']}});candidates=[]
            for c in candidates:
                try:
                    require(isinstance(c,dict),'Candidate is not an object');replays.append({'candidate_id':c.get('id'),'replay':replay(case,c)})
                except Exception as e:replays.append({'candidate_id':c.get('id') if isinstance(c,dict) else None,'replay':{'status':'invalid_actions','errors':[str(e)]}})
            save(self.p('replays/'+jid+'.json'),{'job_id':jid,'raw_sha256':digest,'candidate_replays':replays,'not_native_or_world_execution':True})
            if j['strategy_id']=='AC11':
                ladder=[]
                for b in [2,1,0]:
                    cc=copy.deepcopy(case);cc['impact_preference']=b
                    adjacent=[]
                    for c in candidates:
                        if isinstance(c,dict):
                            try:adjacent.append({'candidate_id':c.get('id'),'replay':replay(cc,c)})
                            except Exception as e:adjacent.append({'candidate_id':c.get('id'),'replay':{'status':'invalid_actions','errors':[str(e)]}})
                    ladder.append({'setting':b,'candidate_replays':adjacent})
                save(self.p('replays/'+jid+'.ladder.json'),{'job_id':jid,'actual_adjacent_setting_replays':ladder,'single_variable':'soft impact preference only; all hard facts fixed'})
        save(self.p('receipts/jobs/'+jid+'.finished.json'),{'job_id':jid,'utc':now(),'handle':s['handle'],'terminal':True,'valid':valid,'first_observed_sha256':digest,'arrangement_sidecar_sha256':side_digest,'arrangement_ordering_observation':side_order,'error':error,'actual_native_invocation':True})
        return {'finished':jid,'valid':valid,'error':error}
    def gate(self,jid):
        require(jid in self.ready()['gateable'],'Cannot gate ready/pending dependencies')
        save(self.p('receipts/jobs/'+jid+'.gated.json'),{'job_id':jid,'utc':now(),'terminal':True,'valid':False,'actual_native_invocation':False,'error':'Invalid dependency; not a zero outcome','dependencies':{d:self.state(d) for d in self.job(jid)['dependencies']}})
        return {'gated':jid}
    def status(self):
        rows={j['job_id']:self.state(j['job_id']) for j in self.plan()};counts={k:sum(s['disposition']==k for s in rows.values()) for k in ['pending','admitted','spawned','finished','failed','gated']}
        actual=self.invocations()
        return {'counts':counts,'valid_finished':sum(s['disposition']=='finished' and s['valid'] for s in rows.values()),'invalid_finished':[k for k,s in rows.items() if s['disposition']=='finished' and not s['valid']],'live':[k for k,s in rows.items() if s['disposition'] in ['admitted','spawned']],'actual_scored_native_invocations':sum(v['purpose']=='scheduled_job' for v in actual),'total_native_with_prep_coordinator':len(actual),'budget':self.budget(),'ready':self.ready(),'terminal':all(s['terminal'] for s in rows.values())}
    def verify(self):
        self.integrity();errors=[];handles={}
        for name,digest in read(self.p('preparation/FREEZE.v1.json'))['historical_sources'].items():
            if sha(name)!=digest:errors.append('Historical source drift '+name)
        for j in self.plan():
            jid=j['job_id'];s=self.state(jid)
            if not s['terminal']:errors.append('Nonterminal '+jid);continue
            if s['disposition']=='gated':continue
            if s['disposition']=='failed':
                if read(self.p('receipts/invocations/score-'+jid+'.json'))['outcome']!='actual_tool_error_observed':errors.append('Failed attempt missing actual invocation '+jid)
                continue
            p=self.p('raw/'+jid+'.json')
            if s.get('first_observed_sha256') and sha(p)!=s['first_observed_sha256']:errors.append('First-save drift '+jid)
            if s.get('first_observed_sha256') and sha(self.p('locks/'+jid+'.first-bytes'))!=s['first_observed_sha256']:errors.append('Lock drift '+jid)
            if s.get('arrangement_sidecar_sha256'):
                if sha(self.p('raw/'+jid+'.arrangements.json'))!=s['arrangement_sidecar_sha256']:errors.append('Arrangement sidecar drift '+jid)
                if sha(self.p('locks/'+jid+'.arrangements.first-bytes'))!=s['arrangement_sidecar_sha256']:errors.append('Arrangement lock drift '+jid)
            adm=read(self.p('receipts/jobs/'+jid+'.admitted.json'))
            for field,path in [('prompt_sha256','prompts/'+jid+'.txt'),('payload_sha256','prompts/'+jid+'.payload.json')]:
                if adm[field]!=sha(self.p(path)):errors.append('Admitted prompt drift '+jid)
            witness=read(self.p('receipts/jobs/'+jid+'.native-final.json'))
            if witness['observation']!='actual_FINAL' or witness['handle']!=s['handle']:errors.append('Native witness mismatch '+jid)
            handles.setdefault(s['handle'],[]).append(jid)
            inv=read(self.p('receipts/invocations/score-'+jid+'.json'))
            if inv.get('handle')!=s['handle']:errors.append('Invocation ledger handle mismatch '+jid)
        for handle,jids in handles.items():
            if len(jids)>1 and set(jids)!={'AC08-preparation','AC08-CONT-resume'}:errors.append('Unplanned handle reuse '+handle)
        return {'status':'pass' if not errors else 'fail','errors':errors,'status_detail':self.status(),'native_observation_limit':'First-save integrity and coordinator witness, not independently attested hidden access or compute.'}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','freeze','ready','status','verify','start','spawned','finish','failed','gate','record-overhead','reserve-overhead']);ap.add_argument('--job');ap.add_argument('--handle');ap.add_argument('--witness-file');ap.add_argument('--invocation-id');ap.add_argument('--purpose');ap.add_argument('--evidence');ap.add_argument('--outcome',choices=['spawn','error'],default='spawn');args=ap.parse_args();r=Runtime()
    if args.command in ['prepare','freeze','ready','status','verify']:v=getattr(r,args.command)()
    elif args.command=='start':v=r.start(args.job)
    elif args.command=='spawned':v=r.spawned(args.job,args.handle)
    elif args.command=='finish':v=r.finish(args.job,read(args.witness_file))
    elif args.command=='failed':v=r.failed(args.job,read(args.witness_file))
    elif args.command=='record-overhead':v=r.record_overhead(args.invocation_id,args.handle,args.purpose,args.evidence,args.outcome)
    elif args.command=='reserve-overhead':v=r.reserve_overhead(args.invocation_id,args.purpose)
    else:v=r.gate(args.job)
    print(json.dumps(v,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
