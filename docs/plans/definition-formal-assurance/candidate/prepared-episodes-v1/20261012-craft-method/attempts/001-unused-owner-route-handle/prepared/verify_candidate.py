"""Supplied Craft eleven-tuple,stage/view/residue/recomposition/closure models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def getfn(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={sort:[sort[0].lower()+sort[1:]+'0',sort[0].lower()+sort[1:]+'1',sort[0].lower()+sort[1:]+'Outside'] for sort in b.SORTS}
 ds.update(CraftReference=['m0','m1','mOutside'],MethodReference=['generic0','generic1','genericOutside'],ScopeReference=['scope0','scope1','scopeOutside'],StageReference=['s0','s1','s2','sOutside'],SubjectReference=['sub0','sub1','sub2','subOutside'],IdentityReference=['id0','id1','id2','idOutside'],TypeReference=['type0','type1','type2','prereqType','residueType','typeOutside'],SourceReference=['source0','source1','sourceOutside'],EvidenceReference=['e0','e1','e2','e3','e4','eOutside'],ViewReference=['v0','v1','vOutside'],CanonicalInputReference=['in0','in1','inOutside'],DigestReference=['inputDigest0','inputDigest1','renderDigest0','renderDigest1','digestOutside'],ResidueReference=['r0','r1','r2','rOutside'],OwnerRouteReference=['route0','route1','routeOutside'],RecompositionReference=['x0','x1','xOutside'],ClosureReference=['c0','c1','cOutside'],OwnerReference=['owner0','owner1','ownerOutside'],DecisionReference=['decision0','decision1','decisionOutside'],Token=['empty','ref','other'])
 maps={}
 def table(n,values):maps[n]=lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 for n,sort in b.CRAFT_FIELDS.items():table(n,{'m0':ds[sort][0],'m1':ds[sort][1]})
 table('craftGenericMethod',{'m0':'generic0','m1':'generic0'})
 for n,sort in b.SCOPE_FIELDS.items():table(n,{'scope0':ds[sort][0],'scope1':ds[sort][1]})
 for n,values in [('stageMethod',['m0','m1','m1']),('stageSubject',['sub0','sub1','sub2']),('stageCanonicalSource',['source0','source1','source1']),('stagePredecessorEvidence',['e0','e1','e2']),('stageResultEvidence',['e1','e2','e3']),('stageConstruction',[ds['ConstructionReference'][0],ds['ConstructionReference'][1],ds['ConstructionReference'][1]])]:table(n,{'s'+str(i):z for i,z in enumerate(values)})
 table('subjectIdentity',{'sub'+str(i):'id'+str(i) for i in range(3)});table('subjectType',{'sub'+str(i):'type'+str(i) for i in range(3)});table('stageParent',{'s1':'s0','s2':'s1'});table('stagePrerequisiteResidue',{'s1':'r0'})
 table('viewMethod',{'v0':'m0','v1':'m1'});table('viewInput',{'v0':'in0','v1':'in1'});table('viewFirstDigest',{'v0':'renderDigest0','v1':'renderDigest1'});table('viewSecondDigest',{'v0':'renderDigest0','v1':'renderDigest1'});table('inputSource',{'in0':'source0','in1':'source1'});table('inputDigest',{'in0':'inputDigest0','in1':'inputDigest1'})
 table('residueMethod',{'r0':'m1','r1':'m0','r2':'m1'});table('residueType',{'r0':'prereqType','r1':'residueType','r2':'residueType'});table('residueOwnerRoute',{'r0':'route1','r2':'route1'})
 for n,values in [('recompositionChild',['s1','s2']),('recompositionParent',['s0','s1']),('recompositionEvidence',['e2','e3']),('recompositionResidue',['r0','r2'])]:table(n,{'x'+str(i):z for i,z in enumerate(values)})
 table('continuationOwner',{ds['OwnerContinuationReference'][0]:'owner0',ds['OwnerContinuationReference'][1]:'owner1'})
 table('closureMethod',{'c0':'m0','c1':'m1'});table('closureOwner',{'c0':'owner0','c1':'owner1'});table('closureContinuation',{'c0':ds['OwnerContinuationReference'][0],'c1':ds['OwnerContinuationReference'][1]});table('closureDecision',{'c0':'decision0'});table('closureEvidence',{'c0':'e4'})
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in [x[1] for x in b.PRIMARY]+['Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in b.FLAGS['Craft']:preds[n]=[['m0'],['m1']]
 for n in ['StageApplicable','StageInScopeDeclared','StageTypedIdentityPreservedDeclared','StageCanonicalAuthorityPreservedDeclared']:preds[n]=[['s0'],['s1'],['s2']]
 preds['StageRootDeclared']=[['s0']];preds['StageChildDeclared']=[['s1'],['s2']];preds['StageImplementationBearingDeclared']=[['s0'],['s1']];preds['StageFollowsCAV2D65Declared']=[['s0']]
 for n in b.FLAGS['View']:preds[n]=[['v0'],['v1']]
 for n in ['ResidueApplicable','ResidueInScopeDeclared','ResidueTypedDeclared']:preds[n]=[['r0'],['r1'],['r2']]
 preds['ResidueOpenDeclared']=[['r0'],['r2']];preds['ResiduePrerequisiteDeclared']=[['r0']]
 for n in b.FLAGS['Recompose']:preds[n]=[['x0'],['x1']]
 for n in ['ClosureApplicable','ClosureInScopeDeclared','ClosureOwnerControlsDeclared']:preds[n]=[['c0'],['c1']]
 preds['ClosureClosedDeclared']=[['c0']];preds['ScopeBoundedDeclared']=[['scope0'],['scope1']];preds['ScopeWithinDeclared']=[['scope1','scope0'],['scope1','scope1']]
 preds['IdentityTypeBindingDeclared']=[['id'+str(i),'type'+str(i)] for i in range(3)];preds['SourceCanonicalAuthoritativeDeclared']=[['source0'],['source1']];preds['EvidenceResolvedDeclared']=[['e'+str(i)] for i in range(5)]
 preds['ParentEvidenceBindingDeclared']=[['s0','e1'],['s1','e2']];preds['InputMachineCanonicalDeclared']=[['in0'],['in1']];preds['RecomposeResiduePropagatedDeclared']=[['x0','r0'],['x1','r2']];preds['ClosureDecisionOwnerMethodDeclared']=[['decision0','owner0','m0']];preds['CraftActualAuthority']=[['m1']]
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(n,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':n,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-eleven-tuple-recursive-stage-view-residue-owner-closure')
 add('no-selected-method-stages-views-residues-recomposition-closure',lambda m:m['predicates'].update({prefix+suffix:[] for prefix,sort,e,a in b.PRIMARY for suffix in ['Applicable','InScopeDeclared']}),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(CraftActualAuthority=[]),I=False)
 add('method-without-closure-records',lambda m:m['predicates'].update(ClosureApplicable=[],ClosureInScopeDeclared=[]),I=False)
 for (prefix,sort,excluded,names),target in zip(b.PRIMARY,['m0','s0','v0','r0','x0','c0']):
  for n in names:add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,target=target:m['predicates'].update({prefix+'Actual'+n:[list(x) for x in sorted({tuple(x) for x in m['predicates'][prefix+'Actual'+n]}|{(target,)})]}),I=None)
  for n in excluded:
   add('selected-excluded-'+n,lambda m,n=n,target=target:m['predicates'][n].append([target]),T=False,I=None)
   outside=base_model()['domains'][sort][-1];add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('root-unused-parent-binding-absent',lambda m:m['predicates'].update(stageParentBindingDeclared=[x for x in m['predicates']['stageParentBindingDeclared'] if x[0]!='s0']))
 add('nonimplementation-unused-prerequisite-binding-absent',lambda m:m['predicates'].update(stagePrerequisiteResidueBindingDeclared=[x for x in m['predicates']['stagePrerequisiteResidueBindingDeclared'] if x[0]!='s2']))
 add('following-C65-unused-prerequisite-binding-absent',lambda m:m['predicates'].update(stagePrerequisiteResidueBindingDeclared=[x for x in m['predicates']['stagePrerequisiteResidueBindingDeclared'] if x[0]!='s0']))
 add('closed-residue-unused-owner-route-binding-absent',lambda m:m['predicates'].update(residueOwnerRouteBindingDeclared=[x for x in m['predicates']['residueOwnerRouteBindingDeclared'] if x[0]!='r1']))
 add('pending-closure-unused-decision-evidence-bindings-absent',lambda m:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!='c1'] for n in b.CLOSED_FIELDS}))
 for sort in ['StageReference','ResidueReference','OwnerRouteReference','DecisionReference']:add('unused-'+sort+'-handle-empty',lambda m,sort=sort:setfn(m,b.HANDLES[sort],m['domains'][sort][-1],'empty'))
 add('input-and-output-digest-nominations-remain-distinct',lambda m:None)
 add('extra-parent-evidence-binding-supported',lambda m:m['predicates']['ParentEvidenceBindingDeclared'].append(['s0','e2']))
 add('extra-scope-within-relation-supported',lambda m:m['predicates']['ScopeWithinDeclared'].append(['scope0','scope1']))
 add('owner-closure-decision-for-additional-method',lambda m:m['predicates']['ClosureDecisionOwnerMethodDeclared'].append(['decision0','owner0','m1']))
 add('missing-root-bounded-scope',lambda m:m['predicates']['ScopeBoundedDeclared'].remove(['scope0']),T=False,I=None)
 for n,arg in [(n,'m0') for n in b.FLAGS['Craft'] if n not in ['CraftApplicable']]+[('StageTypedIdentityPreservedDeclared','s0'),('StageCanonicalAuthorityPreservedDeclared','s0'),('SourceCanonicalAuthoritativeDeclared','source0'),('EvidenceResolvedDeclared','e0'),('InputMachineCanonicalDeclared','in0'),('ViewDerivedDeclared','v0'),('ViewUsesMachineCanonicalInputDeclared','v0'),('ResidueTypedDeclared','r0'),('ResiduePrerequisiteDeclared','r0'),('RecomposeRecordedDeclared','x0'),('ClosureOwnerControlsDeclared','c0')]:add('missing-selected-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,row in [('IdentityTypeBindingDeclared',['id0','type0']),('ParentEvidenceBindingDeclared',['s0','e1']),('RecomposeResiduePropagatedDeclared',['x0','r0']),('ScopeWithinDeclared',['scope1','scope0']),('ClosureDecisionOwnerMethodDeclared',['decision0','owner0','m0'])]:add('missing-exact-relation-'+n,lambda m,n=n,row=row:m['predicates'][n].remove(row),T=False,I=None)
 for n,arg,value in [('stageConstruction','s1',base_model()['domains']['ConstructionReference'][0]),('stageParent','s1','s1'),('stagePrerequisiteResidue','s1','r1'),('viewSecondDigest','v0','renderDigest1'),('recompositionParent','x0','s2'),('recompositionEvidence','x0','e1'),('recompositionResidue','x0','r1'),('closureOwner','c0','owner1'),('closureContinuation','c0',base_model()['domains']['OwnerContinuationReference'][1]),('closureEvidence','c0','eOutside')]:add('wrong-exact-coordinate-'+n,lambda m,n=n,arg=arg,value=value:change(m,n,arg,value),T=False,I=None)
 add('stage-both-root-and-child',lambda m:m['predicates']['StageRootDeclared'].append(['s1']),T=False,I=None)
 add('stage-neither-root-nor-child',lambda m:m['predicates']['StageRootDeclared'].remove(['s0']),T=False,I=None)
 add('implementation-prerequisite-residue-not-typed',lambda m:m['predicates']['ResidueTypedDeclared'].remove(['r0']),T=False,I=None)
 add('pending-closure-cannot-fabricate-closed-decision',lambda m:m['predicates']['ClosureClosedDeclared'].append(['c1']),T=False,I=None)
 targets=[(b.CRAFT_FIELDS,'m0'),(b.SCOPE_FIELDS,'scope0'),(b.STAGE_FIELDS,'s0'),(b.SUBJECT_FIELDS,'sub0'),(b.PARENT_FIELDS,'s1'),(b.PREREQ_FIELDS,'s1'),(b.VIEW_FIELDS,'v0'),(b.INPUT_FIELDS,'in0'),(b.RESIDUE_FIELDS,'r0'),(b.OPEN_FIELDS,'r0'),(b.RECOMPOSE_FIELDS,'x0'),(b.CONTINUATION_FIELDS,base_model()['domains']['OwnerContinuationReference'][0]),(b.CLOSURE_FIELDS,'c0'),(b.CLOSED_FIELDS,'c0')]
 for fields,arg in targets:
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value);add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][b.member(sort)].remove([value]),T=False,I=None)
 selected={sort:values[0] for sort,values in base_model()['domains'].items() if sort!='Token'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 for n,mutate,code in [('empty-domain',lambda m:m['domains'].update(StageReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('CraftReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('craftScope'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['craftScope'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'craftScope','m0','foreign'),'ill-sorted-function-result'),('function-argument',lambda m:m['functions']['craftScope'][0].update(args=['foreign']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['CraftApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('predicate-arity',lambda m:m['predicates']['ClosureDecisionOwnerMethodDeclared'].append(['decision0']),'ill-sorted-model-tuple')]:add('malformed-'+n,mutate,error=code)
 return rows
def qualify(model,ids):return {bucket:{ids[n]:value for n,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}

def verify(write=False):
    context=load('context.json');b.unchanged(context['sources']);b.external_current(context);snap=b.snapshot();b.r.verify(snap,b.ROOT)
    runtime=v.f.current_bindings();bindings=[b.ref(p) for p in [b.UNIT/'build_candidate.py',b.UNIT/'verify_candidate.py',b.IMPL/'verifier.py',b.IMPL/'ir.py',b.IMPL/'contracts.py',b.BASE/'units/A04/correspondence.py']]
    core=load('t.json')['payload'];typed=load('static-ir.json');packet=load('correspondence.json');counts=load('denominator.json')
    if not b.r.same_json(typed,b.ir.compile_interpretation(core,snap)) or not b.r.same_json(packet['interpretation'],core):raise ValueError('Substituted interpretation/IR')
    account=b.co.check(packet,snap,required_dependencies=[x['version_ref'] for x in core['depends_on']],required_conflicts=[x['finding_id'] for x in packet['source_precedence']['conflicts']])
    if not account['character_accounting_complete'] or not b.r.same_json(account,load('correspondence-check.json')):raise ValueError('Incomplete source account')
    if core['assumptions'] or packet['assumption_links'] or core['source_fidelity']!='pending':raise ValueError('Assumed target or owner fidelity')
    T=[x for x in typed['clauses'] if x['disposition']=='encoded'];I=[x for x in typed['populations'] if x['requirement']=='required']
    if len(T)!=counts['encoded_clauses'] or len(I)!=counts['required_populations']:raise ValueError('Changed theory/population denominator')
    ids={x['symbol_id']:b.ir.qualified(core['source'],core['scope'],x['symbol_id']) for x in core['declarations']}
    def evaluate(model):
        e=v.Denotation(typed['declarations'],model)
        tc=[{'clause_id':x['clause_id'],'truth':e.truth(x['formal_statement'])} for x in T]
        pc=[{'population_id':x['population_id'],'truth':e.truth(x['statement'])} for x in I]
        return all(x['truth'] for x in tc),all(x['truth'] for x in pc),tc,pc
    results=[]
    for case in controls():
        model=qualify(case['model'],ids)
        try:
            t,i,tc,pc=evaluate(model)
            if case['expected_error'] is not None or t!=case['expected_T'] or (case['expected_I'] is not None and i!=case['expected_I']):raise ValueError('Wrong authored control: '+case['case_id']+' '+str((t,i)))
            result={'case_id':case['case_id'],'status':'independently-evaluated-authored-model','model':model,'model_sha256':b.ir.digest(model),
                    'primary_theory_satisfied':t,'required_population_satisfied':i,'primary_clause_results':tc,'population_results':pc}
        except v.VerificationFault as error:
            if error.code!=case['expected_error']:raise
            result={'case_id':case['case_id'],'status':'rejected-model-structure','code':error.code,'model':model,'model_sha256':b.ir.digest(model)}
        results.append(result)
    queries=[];composed=b.ir.compose([typed])
    for q in load('query-policy.json')['queries']:
        model=base_model()
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.typed-connection-extension-rule/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-CraftMethod-model-controls/v1-candidate','status':'PASS-for-exact-authored-CraftMethod-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary Craft eleven-tuple/typed-stage/source/view/residue/recomposition/owner-closure declarations checked on supplied models;actual construction,conformance,determinism,owner authority,closure,fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
