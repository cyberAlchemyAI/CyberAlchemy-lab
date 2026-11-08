import copy,json
import build_candidate as b
import verifier as v

def load(name):return json.loads((b.UNIT/name).read_bytes())
def getfn(m,name,arg):return next(row['value'] for row in m['functions'][name] if row['args']==[arg])
def setfn(m,name,arg,value):next(row for row in m['functions'][name] if row['args']==[arg])['value']=value
def refresh(m):
 for fields,carrier in b.GROUPS:
  for name in fields:m['predicates'][name+'BindingDeclared']=[[row['args'][0],row['value']] for row in m['functions'][name]]
 selected=[row[0] for row in m['predicates']['ContextApplicable']]
 m['predicates']['ContextProductLinkDeclared']=[[x,getfn(m,'contextProduct',x)] for x in selected]
 for kind in ['Project','Goal']:
  m['predicates']['Context'+kind+'LinkDeclared']=[[x,getfn(m,'context'+kind,x)] for x in selected if [x] in m['predicates']['ContextHas'+kind+'Declared']]
 m['predicates']['ContextBoundedContextLinkDeclared']=[[x,y] for x in selected for col,y in m['predicates']['BoundedContextCollectionContainsDeclared'] if col==getfn(m,'contextBoundedContexts',x)]
 m['predicates']['IndependentBoundaryOwnershipDeclared']=[[x,y,getfn(m,'boundedContextVersionOwner',y)] for x,y in m['predicates']['ContextBoundedContextLinkDeclared']]

def base_model():
 domains={sort:[sort+'0',sort+'1',sort+'Outside'] for sort in b.SORTS}
 domains.update(ContextReference=['ctx'+str(i) for i in range(8)]+['ctxOutside'],IdentityReference=['id'+str(i) for i in range(8)]+['idOutside'],ProductReference=['p0','p1','pOutside'],ProjectReference=['proj0','proj1','projOutside'],GoalReference=['goal0','goal1','goalOutside'],PurposeReference=['purpose0','purpose1','purposeOutside'],BoundedContextCollectionReference=['col0','col1','col2','col3','colOutside'],BoundedContextVersionReference=['bc0','bc1','bcOutside'],OwnerReference=['owner0','owner1','ownerOutside'],AnchorChangeReference=['aProduct','aProject','aGoal','aPurpose','aNonmaterial','aNoChange','aOutside'],SourceViewChangeReference=['view0','view1','viewOutside'],SourceViewReference=['sourceView0','sourceView1','sourceViewOutside'],Token=['empty','token'])
 m={'domains':domains,'constants':{'EMPTY':'empty'},'functions':{},'predicates':{name:[] for name in b.SIGNATURE}}
 for name,(args,result) in b.FUNCTIONS.items():
  m['functions'][name]=[{'args':[arg],'value':'token' if name in b.HANDLES.values() else domains[result][0]} for arg in domains[args[0]]]
 for sort in b.SORTS:
  if sort!='Token':m['predicates'][sort+'Declared']=[[x] for x in domains[sort]]
 contexts=domains['ContextReference'][:-1]
 for name in ['ContextApplicable','ContextInScopeDeclared','ContextDurableDeclared','ContextOwnerQualifiedDeclared','ContextPurposeStableDeclared']:m['predicates'][name]=[[x] for x in contexts]
 for i,x in enumerate(contexts):setfn(m,'contextIdentity',x,'id'+str(i))
 setfn(m,'contextIdentity','ctxOutside','idOutside')
 for x in ['ctx2','ctx4']:setfn(m,'contextProduct',x,'p1')
 for x in ['ctx2','ctx7']:setfn(m,'contextPurpose',x,'purpose1')
 for x in ['ctx1','ctx3','ctx5']:m['predicates']['ContextHasProjectDeclared'].append([x])
 setfn(m,'contextProject','ctx5','proj1')
 for x in ['ctx2','ctx3','ctx6']:m['predicates']['ContextHasGoalDeclared'].append([x])
 setfn(m,'contextGoal','ctx6','goal1')
 for x,col in [('ctx1','col1'),('ctx2','col2'),('ctx3','col3')]:setfn(m,'contextBoundedContexts',x,col)
 setfn(m,'contextOwner','ctx2','owner1');setfn(m,'boundedContextVersionOwner','bc1','owner1')
 m['predicates']['BoundedContextCollectionContainsDeclared']=[['col1','bc0'],['col2','bc0'],['col2','bc1'],['col3','bc0']]
 m['predicates']['ContextActualExecutionPermission']=[['ctx3']]
 changes=domains['AnchorChangeReference'][:-1]
 for name in ['AnchorChangeApplicable','AnchorChangeInScopeDeclared']:m['predicates'][name]=[[x] for x in changes]
 for x in changes:setfn(m,'changeOriginalContext',x,'ctx0');setfn(m,'changeSuccessorContext',x,'ctxOutside')
 for x,succ in [('aProduct','ctx4'),('aProject','ctx5'),('aGoal','ctx6'),('aPurpose','ctx7')]:
  m['predicates']['MaterialAnchorChangeDeclared'].append([x]);setfn(m,'changeSuccessorContext',x,succ)
  m['predicates']['SuccessorCoordinationIdentityDeclared'].append(['id0',getfn(m,'contextIdentity',succ)])
 for x in ['aProduct','aNonmaterial']:setfn(m,'changeDesiredProduct',x,'p1')
 setfn(m,'changeDesiredPurpose','aPurpose','purpose1')
 m['predicates']['ChangeDesiredHasProjectDeclared']=[['aProject']];setfn(m,'changeDesiredProject','aProject','proj1')
 m['predicates']['ChangeDesiredHasGoalDeclared']=[['aGoal']];setfn(m,'changeDesiredGoal','aGoal','goal1')
 for name in ['SourceViewChangeApplicable','SourceViewChangeInScopeDeclared']:m['predicates'][name]=[['view0'],['view1']]
 for view,ctx in [('view0','ctx0'),('view1','ctx1')]:
  setfn(m,'viewBeforeContext',view,ctx);setfn(m,'viewAfterContext',view,ctx);setfn(m,'viewBeforeSource',view,'sourceView0');setfn(m,'viewAfterSource',view,'sourceView1')
 refresh(m);return m

def controls():
 rows=[];baseline=base_model()
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  model=copy.deepcopy(baseline);mutation(model);rows.append({'case_id':name,'model':model,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,name,arg,value):setfn(m,name,arg,value);refresh(m)
 add('positive-fourteen-coordinates-optional-anchors-boundaries-material-changes-and-views')
 for prefix,outcomes,subject in [('Context',b.ACTUAL,'ctx0'),('AnchorChange',b.CHANGE_ACTUAL,'aProduct'),('SourceViewChange',b.VIEW_ACTUAL,'view0')]:
  for outcome in outcomes:add('independently-supported-'+prefix+outcome,lambda m,prefix=prefix,outcome=outcome,subject=subject:m['predicates'][prefix+'Actual'+outcome].append([subject]))
 for name in b.EXCLUDED:
  add('selected-excluded-'+name,lambda m,name=name:m['predicates'][name].append(['ctx0']),T=False,I=None)
  add('outside-excluded-'+name,lambda m,name=name:m['predicates'][name].append(['ctxOutside']))
 for name in ['ContextDurableDeclared','ContextOwnerQualifiedDeclared','ContextPurposeStableDeclared','ContextInScopeDeclared']:
  add('missing-'+name,lambda m,name=name:m['predicates'][name].remove(['ctx0']),T=False,I=None)
 add('second-Product-link',lambda m:m['predicates']['ContextProductLinkDeclared'].append(['ctx0','p1']),T=False,I=None)
 add('missing-Product-link',lambda m:m['predicates']['ContextProductLinkDeclared'].remove(['ctx0','p0']),T=False,I=None)
 for kind,ctx,other in [('Project','ctx1','proj1'),('Goal','ctx2','goal1')]:
  name='Context'+kind+'LinkDeclared';value=getfn(baseline,'context'+kind,ctx)
  add('second-'+kind+'-link',lambda m,name=name,ctx=ctx,other=other:m['predicates'][name].append([ctx,other]),T=False,I=None)
  add('missing-'+kind+'-link',lambda m,name=name,ctx=ctx,value=value:m['predicates'][name].remove([ctx,value]),T=False,I=None)
  add('absent-'+kind+'-unused-binding-may-be-empty',lambda m,kind=kind:m['predicates'].update({'context'+kind+'BindingDeclared':[x for x in m['predicates']['context'+kind+'BindingDeclared'] if x[0]!='ctx0']}))
  outside=baseline['domains'][kind+'Reference'][-1]
  add('unselected-'+kind+'-reference-may-be-undeclared',lambda m,kind=kind,outside=outside:(change(m,'context'+kind,'ctx0',outside),m['predicates'][kind+'ReferenceDeclared'].remove([outside])))
 add('missing-explicit-boundary-link',lambda m:m['predicates']['ContextBoundedContextLinkDeclared'].remove(['ctx1','bc0']),T=False,I=None)
 add('extra-boundary-link-outside-collection',lambda m:m['predicates']['ContextBoundedContextLinkDeclared'].append(['ctx1','bc1']),T=False,I=None)
 add('missing-independent-boundary-ownership',lambda m:m['predicates']['IndependentBoundaryOwnershipDeclared'].remove(['ctx1','bc0','owner0']),T=False,I=None)
 add('same-principal-can-own-independent-boundaries',lambda m:change(m,'boundedContextVersionOwner','bc1','owner0'))
 for name in ['aProduct','aProject','aGoal','aPurpose']:
  add('material-inplace-successor-'+name,lambda m,name=name:change(m,'changeSuccessorContext',name,'ctx0'),T=False,I=None)
  add('materiality-flag-removed-'+name,lambda m,name=name:m['predicates']['MaterialAnchorChangeDeclared'].remove([name]),I=False)
 add('material-change-missing-successor-identity',lambda m:m['predicates']['SuccessorCoordinationIdentityDeclared'].remove(['id0','id4']),T=False,I=None)
 add('material-change-wrong-desired-successor',lambda m:change(m,'changeSuccessorContext','aProduct','ctx5'),T=False,I=None)
 add('material-change-successor-collapses-identity',lambda m:change(m,'contextIdentity','ctx4','id0'),T=False,I=None)
 add('material-flag-without-anchor-delta',lambda m:m['predicates']['MaterialAnchorChangeDeclared'].append(['aNoChange']),T=False,I=None)
 for name in ['aNonmaterial','aNoChange']:
  add('no-materiality-unused-successor-binding-'+name,lambda m,name=name:m['predicates'].update(changeSuccessorContextBindingDeclared=[x for x in m['predicates']['changeSuccessorContextBindingDeclared'] if x[0]!=name]))
 add('source-view-change-mutates-coordination-identity',lambda m:change(m,'viewAfterContext','view0','ctx4'),T=False,I=None)
 add('source-view-same-before-after-reference-allowed',lambda m:change(m,'viewAfterSource','view0','sourceView0'))
 selected=[(b.FIELDS,'ctx0'),({'contextProject':'ProjectReference'},'ctx1'),({'contextGoal':'GoalReference'},'ctx2'),(b.BOUNDARY_FIELDS,'bc0'),(b.CHANGE_FIELDS,'aProduct'),({'changeDesiredProject':'ProjectReference'},'aProject'),({'changeDesiredGoal':'GoalReference'},'aGoal'),(b.SUCCESSOR_FIELDS,'aProduct'),(b.VIEW_FIELDS,'view0')]
 for fields,arg in selected:
  for name,sort in fields.items():
   value=getfn(baseline,name,arg);other=next(x for x in baseline['domains'][sort] if x!=value)
   add('missing-exact-binding-'+name,lambda m,name=name,arg=arg:m['predicates'].update({name+'BindingDeclared':[x for x in m['predicates'][name+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   add('conflicting-exact-binding-'+name,lambda m,name=name,arg=arg,other=other:m['predicates'][name+'BindingDeclared'].append([arg,other]),T=False,I=None)
   if sort not in b.MAP:add('undeclared-selected-target-'+name,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
   add('empty-selected-handle-'+name,lambda m,sort=sort,value=value:setfn(m,b.HANDLES[sort],value,'empty'),T=False,I=None)
 for sort,arg in [('ContextReference','ctx0'),('AnchorChangeReference','aProduct'),('SourceViewChangeReference','view0')]:
  add('empty-selected-root-handle-'+sort,lambda m,sort=sort,arg=arg:setfn(m,b.HANDLES[sort],arg,'empty'),T=False,I=None)
 for name,mutation,error in [('empty-domain',lambda m:m['domains'].update(ContextReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('OwnerReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('contextIdentity'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['contextOwner'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'contextOwner','ctx0','foreign'),'ill-sorted-function-result'),('predicate-arity',lambda m:m['predicates']['IndependentBoundaryOwnershipDeclared'].append(['ctx0','bc0']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['ContextApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('missing-constant',lambda m:m['constants'].pop('EMPTY'),'model-signature-denominator-mismatch')]:add('malformed-'+name,mutation,error=error)
 return rows
def qualify(model,ids):return {bucket:{ids[name]:value for name,value in model[bucket].items()} for bucket in ['domains','constants','functions','predicates']}

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
    prior=json.loads((b.BASE/'definitions/cal.definition.capability-realization-binding/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-CoordinationContext-model-controls/v1-candidate','status':'PASS-for-exact-authored-CoordinationContext-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary fourteen-coordinate frame, optional anchor cardinality, explicit independent boundary and identity guards checked on supplied models; actual outcomes, fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
