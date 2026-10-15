#!/usr/bin/env python3
"""Prospective fixture/plan compiler. No model calls and no scored results."""
import copy, hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parents[2]
ACA=BASE/'novelty/academic-extension/2026-10-10'
def save(rel,v):
    p=ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8') as f:
        f.write(v if isinstance(v,str) else json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def fact(i,t): return {'id':i,'text':t}
def mechanical(cid,demand=4,caps=None,hold=(3,6),end=10,available=None):
    caps=caps or [2,4,4,4,4,4]
    v={'case_id':cid,'domain':'J','evidence_kind':'stipulated finite model, not measured physics','demand':demand,'capacities':dict(zip(['pin','clip','sleeve','stem','head','loop'],caps)),'hold_ticks':list(range(hold[0],hold[1]+1)),'end_boundary':end,'available':available or ['H','M','S','P1','P2','C','V','L','Q'],'preferred_tool':'H','grammar':'Discrete fastening is a mutable benchmark convention; hard requirements are unchanged.','impact_preference':2,'unknowns':{'Q_theta':[0,4]},'facts':[
        fact('J01',f'Two initially aligned panels must retain at least {demand} units at ticks {hold[0]}–{hold[1]}, then separate with all installed retainers removed by boundary {end}. No damage/discard/substitution/outside resource.'),
        fact('J02','One operator; one action per integer tick, completes next boundary. Resources cannot occupy two places simultaneously. H initially intact; all other parts free.'),
        fact('J03','detach(H) frees M and S; assemble(H) requires both free. Neither creates retention. H requires M and S to remain assembled for tap.'),
        fact('J04',f'tap(P1/P2) requires intact H and free pin; each installed pin supplies {caps[0]} units. pull removes installed pin. Only pins add capacities; no pins with non-pin retainer.'),
        fact('J05',f'install(C) supplies {caps[1]} retention; remove(C) removes clip.'),
        fact('J06',f'install(V) then insert(S,V) with detached/free S supplies min({caps[2]},{caps[3]}) retention; withdraw(S,V) then remove(V) releases.'),
        fact('J07',f'place(M) after detach(H), then route(L), supplies min({caps[4]},{caps[5]}) retention. unroute(L) then lift(M) releases. Both are needed.'),
        fact('J08','install(Q) supplies theta in {0,4}; theta is initially unmeasured. measure(Q) returns exact theta in one tick, never itself creates retention. remove(Q) releases. No assumed theta.'),
        fact('J09','At most one non-pin retaining assembly installed; it cannot combine with pins. No unlisted operation, adhesive, welding, elastic extrapolation or sustained manual support.'),
        fact('J10','The conventional archive contains two-pin fastening and clip fastening. All supported properties are common to all arms; these known constructions are not locally original.'),
        fact('J11','The discrete-fastener grammar and impact budget b=2 are soft benchmark conventions/preferences, not mechanical laws. b may be set to 2,1,0 only in declared ladder cells.'),
        fact('J12',f'Available identities: {available or ["H","M","S","P1","P2","C","V","L","Q"]}. Capacity values above are complete; unknowns are not free variables.')],
        'actions':{'detach':'H','assemble':'H','tap':'P1 or P2','pull':'P1 or P2','install':'C or V or Q','remove':'C or V or Q','insert':'S,V','withdraw':'S,V','place':'M','lift':'M','route':'L','unroute':'L','measure':'Q','idle':None}}
    return v
def workflow(cid,n=4,end=12,update=None):
    sources=[f'E{i}' for i in range(1,n+1)]+['A','K','U']
    return {'case_id':cid,'domain':'W','evidence_kind':'stipulated reporting fixture; actual user utterances separately identified','n_claims':n,'sources':sources,'end_boundary':end,'update_boundary':update,'preferred_tool':'repeated independent source opening','facts':[
        fact('W01',f'Produce {n} distinct claim cards and compile by boundary {end}. Each card must cite its Ei plus A,K,U and preserve application, model outcome, comparison and claim ceiling separately.'),
        fact('W02','One operator/action per integer tick; actions complete next boundary. Sources immutable except the declared A update. read(source) caches exact token; write(i) requires its four current cached tokens and costs one tick; compile requires all valid cards and costs one tick.'),
        fact('W03','Cached tokens persist without a reread. Repeated opening costs an additional tick. No generated assertion replaces an actual source token; no unsupported human or field claim.'),
        fact('W04',f'Available sources are {sources}. No outside actors or sources. Current versions initially 1.'),
        fact('W05','Known ordinary repertoire already includes caching and an evidence table. Rediscovering caching is not original.'),
        fact('W06',('At boundary '+str(update)+' source A becomes version 2; invalidate cached old A. Later writes require current A; compile rejects every old-A card. Rewrite costs one tick.') if update is not None else 'No version updates in this fixture.'),
        fact('W07','Actual user utterances U01–U06 support useful novelty, academic grounding, coverage and reported comparisons. They supply no observed review time, adoption, learning or measured burden.'),
        fact('W08','An authored four-summary candidate omitting comparison/ceiling fields is deliberately invalid. Reframe only to the original complete claim contract; changing success criteria is forbidden.')],
        'tokens':{s:{'id':s,'version':1,'contents':({'application':'applied synthetic method','outcome':'finite-model output only','comparison':'matched old arm, possibly tied','ceiling':'no human, field or global originality claim'} if s.startswith('E') else {'role':{'A':'academic rationale, not method proof','K':'prior lineage already includes caching','U':'actual expressed preferences; unmeasured benefit'}[s]})} for s in sources},
        'actions':{'read':'source ID','write':'claim number as string','compile':None,'idle':None}}
def section(text,pattern):
    m=re.search(pattern,text,re.M);assert m,pattern
    rest=text[m.start():];n=re.search(r'^#{2,3} ',rest[m.end()-m.start():],re.M)
    return rest[:m.end()-m.start()+n.start()] if n else rest
def main():
    cases={'J0':mechanical('J0'),'W0':workflow('W0'),'T1':mechanical('T1',3,[2,2,3,3,3,3],available=['H','M','S','P1','P2','C','V','L']),'T2':mechanical('T2',4,[2,4,4,4,2,4],available=['H','M','S','P1','P2','C','V','L']),'TI':mechanical('TI',3,[2,3,4,4,2,3],hold=(4,6),available=['H','M','S','P1','P2','C','V','L']),'HR':mechanical('HR',hold=(4,7),end=11,available=['H','M','S','P1','P2','C','V','L']),'HN':mechanical('HN',5,[3,4,6,6,2,5],available=['H','M','S','P1','P2','C','V','L']),'HF':workflow('HF',3,11,4),'HX':mechanical('HX',available=['H','P1','P2']),'RJ':mechanical('RJ',5,[2,4,6,6,2,5],hold=(4,7),end=11,available=['H','M','S','P1','P2','C','V','L']),'RW':workflow('RW',3,12,3)}
    cases['HN']['surface']='Inspection gauge H has a detachable sensor housing M (ballast 2) and rigid handle S; V is a coupler. These are model identities; real gauge physics is not inferred.'
    cases['HX']['assigned_absent_dependency']='Do not use H or its parts; retained function unchanged. Only pins exist and tap requires H: source-supported no-opening.'
    for cid,v in cases.items():save('inputs/cases/'+cid+'.json',v)
    save('private/oracle.json',{'J0_Q_theta':4,'not_given_to_workers_or_selectors':True})
    prior_cases=json.loads((BASE/'novelty/runs/2026-10-10-composed-ten/inputs/cases.json').read_text())
    save('inputs/analogues.json',{'route_material':{'id':'AM','original_path':str(BASE/'novelty/runs/2026-10-10-composed-ten/inputs/cases.json'),'original_selector':'DEV','body':prior_cases['DEV']},'route_information':{'id':'AI','original_path':str(BASE/'novelty/runs/2026-10-10-composed-ten/inputs/cases.json'),'original_selector':'CONF','body':prior_cases['CONF']},'limit':'Two retrieved synthetic source cases, not independent empirical evidence. Source routes differ; root fixes common essentials.'})
    save('inputs/examples.json',{'id':'EX','feature_ids':['EX1','EX2'],'examples':[{'id':'EX1','feature':'impact plus two discrete pins','actions':[{'tick':0,'op':'tap','arg':'P1'},{'tick':1,'op':'tap','arg':'P2'},{'tick':7,'op':'pull','arg':'P1'},{'tick':8,'op':'pull','arg':'P2'}]},{'id':'EX2','feature':'clip, one installation and removal','actions':[{'tick':0,'op':'install','arg':'C'},{'tick':7,'op':'remove','arg':'C'}]}],'no_new_property_facts':True})
    pool=[]
    for k,acts in enumerate([[(0,'tap','P1'),(1,'tap','P2'),(7,'pull','P1'),(8,'pull','P2')],[(0,'install','C'),(7,'remove','C')],[(0,'detach','H'),(1,'install','V'),(2,'insert','S,V'),(7,'withdraw','S,V'),(8,'remove','V')],[(0,'detach','H'),(1,'place','M'),(2,'route','L'),(7,'unroute','L'),(8,'lift','M')],[(0,'tap','P1'),(7,'pull','P1')],[(0,'install','Q'),(7,'remove','Q')]],1):
        pool.append({'id':'K'+str(k),'mechanism':['pin','clip','stem-sleeve','ballast-loop','insufficient-pin','unknown-Q'][k-1],'actions':[{'tick':t,'op':o,'arg':a} for t,o,a in acts],'source_refs':['J01','J02','J03','J04','J05','J06','J07','J08','J09','J10']})
    save('inputs/fixed-pool.json',{'case_id':'J0','candidates':pool,'authorship':'Unscored preparation case author; fixed actual prescriptions, not human generation.','implementation_cap':2,'investigation_cap':1,'frontier_rule':'Among source-proven hard-feasible options, retain nondominated higher novelty/lower non-idle action burden; select lowest-burden known option plus highest-novelty distinct feasible option if nondominated, max 2. Unresolved Q is an investigation only; reject proven violations. Novelty against pins/clip and full specified lineage separately.'})
    newtext=(ACA/'STRATEGIES.md').read_text();roottext=(BASE/'STRATEGIES.md').read_text();ntext=(BASE/'novelty/STRATEGIES.md').read_text();core=json.loads((BASE/'novelty/runs/2026-10-10-composed-ten/inputs/methods.json').read_text())
    methods={}
    for i in range(1,21):
        cid=f'AC{i:02d}';s=section(newtext,r'^### '+cid+r'\.')
        # Illustrations and literature findings are reviewer-only, not case answers.
        s=re.sub(r'\*\*Illustration, not a tested result:\*\*.*?(?=\n\*\*)','',s,flags=re.S)
        methods[cid]={'id':cid,'source':str(ACA/'STRATEGIES.md'),'instructions':s.split('**Academic rationale:**')[0]}
    ns={i:section(ntext,r'^## N'+f'{i:02d}'+r' ') for i in [5,6,7,8,9]}
    rs={i:section(roottext,r'^### S'+f'{i:02d}'+r'\.') for i in [3,5,11,13,14]}
    # Only instructions prior to illustrative examples; exact catalog paths remain bound.
    for i,s in ns.items():methods[f'N:N{i:02d}']={'id':f'N:N{i:02d}','source':str(BASE/'novelty/STRATEGIES.md'),'instructions':s.split('**Hammer example:**')[0]}
    for i,s in rs.items():
        keep=[line for line in s.splitlines() if not line.startswith(('**Illustration','**Example','**Source','**Academic'))]
        methods[f'ROOT:S{i:02d}']={'id':f'ROOT:S{i:02d}','source':str(BASE/'STRATEGIES.md'),'instructions':'\n'.join(keep)}
    for cid in ['O','S01','S03','S05','R07']:
        mid='CORE:'+cid if cid.startswith('S') else ('RECIPE:'+cid if cid.startswith('R') else 'O')
        methods[mid]={'id':mid,'source':str(BASE/'novelty/runs/2026-10-10-composed-ten/inputs/methods.json'),'instructions':core[cid]['instructions']}
    methods['P:P08']={'id':'P:P08','source':str(BASE/'novelty/runs/2026-10-08-process-all/STRATEGIES.md'),'instructions':'Preserve productive disagreement between implementation-resource and downstream-service concerns, with explicit contrary dependencies/predictions, then construct a separating action before reconciliation.'}
    save('inputs/methods.json',methods)
    # A versioned compact method representation; not a claim to replace canonical cards.
    save('inputs/revision-card.v1.json',{'name':'R07 connection-retention compact experimental card','invariant':'Both named parent functions and every hard requirement remain unchanged.','operative_instruction':core['R07']['instructions'],'applicability':'Only when the assigned original and substitute connection and controls exist.','construction_obligation':'Supply a source-supported construction and separating comparison.','counterexample':'Changing or disabling a parent instead of its connection is inadmissible.','retention':'External JSON only; no weights or installed skill are changed.'})
    # Historical actual failed chain is feedback, not a newly staged failure.
    save('inputs/revision-feedback.json',{'source_path':str(BASE/'novelty/runs/2026-10-10-composed-ten/raw/CONF-R07-builder.json'),'raw':json.loads((BASE/'novelty/runs/2026-10-10-composed-ten/raw/CONF-R07-builder.json').read_text()),'audit_source':str(BASE/'novelty/runs/2026-10-10-composed-ten/reports/COMPLETION-AUDIT.v1.json'),'failure':'The original CONF-R07 substituted another connection; the assigned transfer was not applied. This documented earlier failure is fixed feedback for both revision conditions, not a new spontaneous practice failure.'})
    jobs=[]
    def add(jid,ac,arm,case,role,deps=(),method=None,extra=None,followup=None):
        j={'job_id':jid,'strategy_id':ac,'arm':arm,'case_id':case,'role':role,'dependencies':list(deps),'method_id':method or ac,'word_cap':1800 if role not in ['review','retained_card'] else 5500}
        if extra:j['instructions']=extra
        if followup:j['followup_of']=followup
        jobs.append(j);return jid
    def chain(ac,arm,case,method=None,extra=None,startdeps=()):
        pre=f'{ac}-{arm}-{case}'
        p=add(pre+'-proposal',ac,arm,case,'proposal',startdeps,method,extra)
        c=add(pre+'-critique',ac,arm,case,'critique',[p],method,extra)
        b=add(pre+'-builder',ac,arm,case,'builder',[c],method,extra)
        return [p,c,b]
    chain('ORD','O','J0','O');chain('ORD','O','W0','O')
    ordinary={'J0':'ORD-O-J0-builder','W0':'ORD-O-W0-builder'}
    gen={'AC01':('J0','N:N09'),'AC02':('J0','N:N07'),'AC03':('J0','N:N05'),'AC04':('J0','N:N08'),'AC05':('W0','N:N06'),'AC06':('W0','ROOT:S13'),'AC07':('J0','ROOT:S05'),'AC10':('J0','RECIPE:R07'),'AC13':('J0','CORE:S01'),'AC18':('W0','ROOT:S11')}
    for ac,(case,old) in gen.items():chain(ac,'T',case);chain(ac,'OLD',case,old)
    chain('AC03','GRAMMAR','J0','O','Use original discrete-fastener grammar only. Conduct broad search within it; do not silently relax it. Same three candidates and budget.')
    chain('AC05','FORMAT','W0','O','Use an additional verbal table/list with identical facts. Ordinary analysis, no forced graph round trip. Same total candidate and word allowance.')
    chain('AC06','FIXED','W0','O','Start with the given four-summary frame; actually replay the deliberately incomplete claim content, then repair within the same frame under original contract. Do not relabel requirements.')
    for arm,allocation in [('BREADTH','6 breadth/0 depth'),('DEPTH','0 breadth/6 depth')]:chain('AC07',arm,'J0','ROOT:S05','Exactly six search slots: '+allocation+'. Each slot a bounded record; final cap three candidates. T and OLD also have six slots; T=3/3, OLD uses its predeclared equal tournament.')
    chain('AC10','WHOLE','J0','O','Search whole-system replacement within fixed available resources and every unchanged hard constraint. No outside parts or replaced panels; if prohibited, give source-supported no-opening.')
    chain('AC13','T','HX');chain('AC13','OLD','HX','CORE:S01')
    for b in [2,1,0]:chain('AC11','B'+str(b),'J0','AC11',f'Impact soft preference b={b}; one ladder setting. Preserve all hard constraints; construct for this setting, anticipate adjacent setting, record hard-valid vs preference satisfaction separately.')
    chain('AC11','OLD','J0','N:N05','Binary impact deprivation b=0; do not remove any hard requirement. Same source facts and search allowance.')
    p=add('AC12-defense','AC12','shared','J0','proposal',method='CORE:S03',extra='Defend one incumbent candidate; do not generate the subsequent opening builder answer.')
    a=add('AC12-attack','AC12','shared','J0','shared_attack',[p],extra='Save one exact failed-dependency criticism, invariant and available variable separately. Do not include a new construction. The exact criticism will be reused unchanged.')
    for arm,method in [('CRITIQUE','O'),('OLD','CORE:S03'),('T','AC12')]:add('AC12-'+arm+'-builder','AC12',arm,'J0','builder',[a],method,'Use the assigned received attack variant. Same criticism bytes and common facts; one fresh construction or exact terminal boundary.')
    p=add('AC08-preparation','AC08','shared','J0','context_preparation',method='CORE:S05',extra='Prepare two incompatible accounts, source-bound prerequisites/tensions, then save a concise essential-fact summary. This role may receive one explicitly authorized continuation; no helpers.')
    x=add('AC08-CONT-resume','AC08','CONT','J0','resumption',[p],'CORE:S05',followup=p)
    y=add('AC08-FRESH-resume','AC08','FRESH','J0','resumption',[p],'CORE:S05')
    for arm,j in [('CONT',x),('FRESH',y)]:
        c=add('AC08-'+arm+'-critique','AC08',arm,'J0','critique',[j]);add('AC08-'+arm+'-builder','AC08',arm,'J0','builder',[c])
    for arm in ['AFTER','BEFORE','NONE']:
        p=add('AC09-'+arm+'-first','AC09',arm,'J0','example_first',method='ROOT:S03',extra='Generate/save first candidates now. Examples are supplied only in the BEFORE first-stage payload.')
        q=add('AC09-'+arm+'-second','AC09',arm,'J0','example_second',[p],extra='Preserve original candidates alongside revisions. AFTER now receives the examples for the first time; BEFORE sees same examples again; NONE sees none. Track exact EX feature provenance/copying.')
        c=add('AC09-'+arm+'-critique','AC09',arm,'J0','critique',[q]);add('AC09-'+arm+'-builder','AC09',arm,'J0','builder',[c])
    for arm in ['INDEPENDENT','IMMEDIATE']:
        a=add('AC14-'+arm+'-implementation','AC14',arm,'J0','concern',method='P:P08',extra='Implementation-resource concern only: propose constructions and resource costs; exclude service judgment; all common facts remain visible.')
        b=add('AC14-'+arm+'-service','AC14',arm,'J0','concern',([a] if arm=='IMMEDIATE' else []),'P:P08','Service-release/maintenance concern only; exclude construction optimization. IMMEDIATE may see first proposal; INDEPENDENT sees no other proposal.')
        c=add('AC14-'+arm+'-exchange','AC14',arm,'J0','exchange',[a,b],'AC14' if arm=='INDEPENDENT' else 'P:P08','Find an actual contradictory dependency/prediction, preserve initial provenance and disagreement; no synthetic consensus. Distill a construction opening or source-supported no-opening.')
        add('AC14-'+arm+'-builder','AC14',arm,'J0','builder',[c])
    for ac in ['AC15','AC19']:
        for arm,method in [('T',ac),('OLD','ROOT:S11' if ac=='AC15' else 'ROOT:S05'),('O','O')]:add(ac+'-'+arm+'-selection',ac,arm,'J0','selection',method=method,extra='Use frozen P-J0 only. No generation/rewrite/measurement result. Select at most two implementation candidates and one investigation; preserve all six ratings/reasons and displaced options. T AC15 obeys the frozen frontier rule; T AC19 separates reason types.')
    # Training and holdouts have distinct literal packets. Preparation authors never serve as learners.
    for arm,method in [('T','CORE:S01'),('ACTIVE','O')]:
        p=add('AC16-'+arm+'-practice1','AC16',arm,'T1','practice',method=method,extra='Practice the named procedure, with actual candidate actions. Include one deliberately wrong single-pin attempt as a labeled negative exercise, then a valid attempt. Do not treat the forced error as a spontaneous failure.')
        q=add('AC16-'+arm+'-practice2','AC16',arm,'T2','practice',[p],method,'Use actual first-practice replay feedback and the same named procedure; three bounded attempts including an honest failure boundary.')
        add('AC16-'+arm+'-card','AC16',arm,'T2','retained_card',[p,q],method,'Save a procedure-only method card: invariant, applicability, property extraction, mapping/construction obligation, refusal/counterexample. Omit case identities, timings, capacities, solved answers and holdout facts. External JSON is the only retained state; no weight change.')
    for h in ['HR','HN','HF','HX']:
        add('AC16-BASE-'+h,'AC16','BASE',h,'transfer',method='O',extra='Fresh baseline, no trained retained artifact. Outcome and honest applicability/refusal count separately.')
        for arm,dep,method in [('RETRIEVED','AC16-T-card','CORE:S01'),('ACTIVE','AC16-ACTIVE-card','O')]:add('AC16-'+arm+'-'+h,'AC16',arm,h,'transfer',[dep],method,'Retrieve only the supplied retained card, then construct on the unfamiliar/current case; flag procedural non-applicability rather than invent properties.')
        add('AC16-FIXED-'+h,'AC16','FIXED',h,'transfer',method='CORE:S01',extra='Fresh earlier fixed-method prompting control, no practice-derived card. Same task facts and work allowance.')
        add('AC16-NOCARD-'+h,'AC16','NOCARD',h,'transfer',['AC16-T-card'],'O','Fresh context after the teacher finished; no retained card or teacher history is supplied. Training has no hidden transmission. This tests external-scaffold removal, not human delayed retention.')
    for arm,dep,method in [('T','AC16-T-practice2','CORE:S01'),('ACTIVE','AC16-ACTIVE-practice2','O')]:add('AC16-IMMEDIATE-'+arm,'AC16','IMMEDIATE-'+arm,'TI','transfer',[dep],method,'Immediate scaffolded test: supplied practiced procedure and actual practice/feedback history. No retained teacher card yet required; not a delayed human test.')
    r=add('AC17-revision','AC17','revision','J0','revision',extra='Classify actual historical CONF-R07 failure; change exactly construction_obligation in the provided experimental card. Preserve all other fields byte-equivalent including invariant, counterexample and canonical operative instruction. Do not add prior solved schedules. Save old/new values and rationale; if no legitimate revision exists, preserve source-supported no-opening.')
    for h in ['RJ','RW']:
        for arm in ['FIXED','REVISED']:add('AC17-'+arm+'-'+h,'AC17',arm,h,'transfer',[r],'RECIPE:R07','Both receive identical historical failure feedback. FIXED gets unchanged compact card, REVISED gets one-field delta. Fresh heldout construction/test; external retained state only. The mechanical connection instruction may properly refuse a reporting task.')
    pre=[]
    for concern in ['implementation','service']:pre.append(add('AC20-PRE-'+concern,'AC20','PRE','J0','concern',method='ROOT:S03',extra='Pre-assistance candidate generation; no analog source bank is supplied. Preserve candidates and exact task-fact provenance.'))
    for arm in ['SHARED','DISTINCT','UNION']:
        routejobs=[]
        for idx in [0,1]:routejobs.append(add('AC20-'+arm+'-route'+str(idx),'AC20',arm,'J0','source_route',pre,'ROOT:S03','Read the exact supplied routed source pack. Save selector/source exposure and candidate mapping. Shared seed vs distinct routes vs equal-union information are different comparisons; never invent independent empirical sources.'))
        c=add('AC20-'+arm+'-exchange','AC20',arm,'J0','exchange',pre+routejobs,'AC20','Join actual routed proposals; map source→candidate mechanisms, coverage/overlap, reject lexical diversity, preserve feasible rare mechanisms and uncertainty.')
        add('AC20-'+arm+'-builder','AC20',arm,'J0','builder',[c])
    for idx in range(5):
        acs=[f'AC{i:02d}' for i in range(idx*4+1,idx*4+5)]
        deps=[j['job_id'] for j in jobs if j['strategy_id'] in acs]+[j['job_id'] for j in jobs if j['strategy_id']=='ORD']
        for reviewer in [1,2]:add(f'REVIEW-{idx+1}-{reviewer}','REVIEW','independent'+str(reviewer),'J0','review',deps,'O','Independently review exactly '+','.join(acs)+'. Never repair/regrade raw outputs; preserve unknowns and disagreement. Audit all operative clauses and every required matched comparison, full current upstream outputs, actual model replay and selective historical lineage. No world/human effect claims.')
        jobs[-1]['review_strategies']=acs;jobs[-2]['review_strategies']=acs
    save('preparation/PLAN.v1.json',jobs)
    save('preparation/HOLDOUT-PARTITIONS.v1.json',{'training':['T1','T2'],'immediate':['TI'],'AC16':['HR','HN','HF','HX'],'AC17':['RJ','RW'],'untouched_means':'Not exposed to practice teachers/card writers/reviser; preparation root access is declared. No feedback to learners before first saved outcomes.'})
    save('preparation/EXECUTION-COUNT.v1.json',{'scheduled_jobs':len(jobs),'scored_jobs':len(jobs),'preparation_actual_already':3,'preflight_reserved':1,'coordinator_reserved':1,'completion_auditors_reserved':2,'planned_native_total':len(jobs)+7,'ceiling':260,'replication':'Coverage pilot; one principal fixture per generator plus a negative AC13 case and heterogeneous heldouts. No population inference.'})
    print(json.dumps({'prepared_jobs':len(jobs),'planned_native_total':len(jobs)+7,'cases':list(cases)},indent=2))
if __name__=='__main__':main()
