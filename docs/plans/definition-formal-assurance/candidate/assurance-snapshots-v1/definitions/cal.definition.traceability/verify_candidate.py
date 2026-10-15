"""Supplied typed Traceability case,question,path,link and terminal models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def base_model():
 domains={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};domains.update(Meaning=['meaning','meaningOutside'],TraceCase=['c0','c1','c2','cOutside'],DeclaredPath=['p0','p1','p2','pOutside'],Link=['l0','l1','l2','l3','l4','lOutside'],Position=['pos0','pos1','pos2','pos3','pos4','posOutside'],Terminal=['e0','e1','e2','eOutside'],AuthorityPosture=['postureA','postureB','postureOutside'],Token=['empty','reference','extra','meaning-id','meaning-kind','meaning-carrier','meaning-scope','source-d36'])
 constants=dict(zip(b.CONSTANTS,['empty','meaning-id','meaning-kind','meaning-carrier','meaning-scope','source-d36']));maps={}
 for n,k in zip(b.META,['MEANING_ID','MEANING_KIND','MEANING_CARRIER','MEANING_SCOPE','SOURCE_D36']):maps[n]=lambda m,k=k:'extra' if m=='meaningOutside' else constants[k]
 for n,s in b.CASE_FIELDS.items():maps[n]=lambda c,s=s:domains[s][-1] if c=='cOutside' else domains[s][0]
 maps['casePath']=lambda c:{'c0':'p0','c1':'p1','c2':'p2','cOutside':'pOutside'}[c]
 for n,s in b.LINK_FIELDS.items():maps[n]=lambda l,s=s:domains[s][-1] if l=='lOutside' else domains[s][0]
 maps['linkPath']=lambda l:{'l0':'p0','l1':'p0','l2':'p0','l3':'p1','l4':'p2','lOutside':'pOutside'}[l]
 maps['linkPosition']=lambda l:'posOutside' if l=='lOutside' else 'pos'+l[1:]
 maps['linkPosture']=lambda l:'postureOutside' if l=='lOutside' else 'postureB' if l=='l1' else 'postureA'
 for n,s in b.TERMINAL_FIELDS.items():maps[n]=lambda e,s=s:domains[s][-1] if e=='eOutside' else domains[s][0]
 maps['terminalPath']=lambda e:{'e0':'p0','e1':'p1','e2':'p2','eOutside':'pOutside'}[e]
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(domains[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['TraceabilityMeaning','ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:predicates[n]=[['meaning']]
 for n in ['TraceCaseApplicable','CaseInScopeDeclared','WorkQuestionBindingDeclared','RelevantChainDeclared','NoHiddenConversationContextRequiredDeclared']:predicates[n]=[['c0'],['c1'],['c2']]
 for n in ['PathApplicable','PathInScopeDeclared','TypedPathDeclared']:predicates[n]=[['p0'],['p1'],['p2']]
 for n in ['LinkApplicable','LinkInScopeDeclared','TargetPrecisionDeclared','RelationPrecisionDeclared','PosturePrecisionDeclared']:predicates[n]=[[x] for x in ['l0','l1','l2','l3','l4']]
 for n in ['TerminalApplicable','TerminalInScopeDeclared']:predicates[n]=[['e0'],['e1'],['e2']]
 predicates.update(WorkObjectDeclared=[['workobjectA']],ReviewQuestionDeclared=[['reviewquestionA']],ContextExplicitDeclared=[['contextA']],PositionDeclared=[[x] for x in ['pos0','pos1','pos2','pos3','pos4']],TargetReferenceDeclared=[['targetreferenceA']],RelationTypeDeclared=[['relationkindA']],AuthorityPostureDeclared=[['postureA'],['postureB']],AnswerReferenceDeclared=[['answerreferenceA']],TypedResidueDeclared=[['typedresidueA']],NamedGapNameDeclared=[['namedgapA']],AnswerTerminalDeclared=[['e0'],['e1']],ResidueTerminalDeclared=[['e1'],['e2']],GapTerminalDeclared=[['e2']],BrokenPathDeclared=[['p1'],['p2']],LinkBeforeDeclared=[['l0','l1'],['l0','l2'],['l1','l2']])
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-question-path-inclusive-answer-residue-gap-and-repeated-targets',lambda m:None,I=True)
 for n in b.ACTUAL:add('independent-actual-'+n,lambda m,n=n:m['predicates']['CaseActual'+n].append(['c1']),I=True)
 add('outside-case-empty-handle',lambda m:setfn(m,'traceCaseHandle','cOutside','empty'),I=True)
 add('outside-path-empty-handle',lambda m:setfn(m,'declaredPathHandle','pOutside','empty'),I=True)
 add('outside-link-empty-handle',lambda m:setfn(m,'linkHandle','lOutside','empty'),I=True)
 add('outside-terminal-empty-handle',lambda m:setfn(m,'terminalHandle','eOutside','empty'),I=True)
 add('outside-target-empty-handle',lambda m:setfn(m,'targetReferenceHandle','targetreferenceOutside','empty'),I=True)
 add('outside-terminal-may-have-no-tags',lambda m:setfn(m,'terminalAnswer','eOutside','answerreferenceOutside'),I=True)
 add('outside-self-order-allowed',lambda m:m['predicates']['LinkBeforeDeclared'].append(['lOutside','lOutside']),I=True)
 add('cross-path-order-cycle-does-not-impose-global-acyclicity',lambda m:m['predicates']['LinkBeforeDeclared'].extend([['l0','l3'],['l3','l0']]),I=True)
 add('answer-and-gap-and-residue-may-all-overlap',lambda m:m['predicates']['GapTerminalDeclared'].append(['e1']),I=True)
 add('selected-path-loses-its-only-terminal',lambda m:setfn(m,'terminalPath','e0','p1'),T=False)
 # Moving the only terminal off p0 must fail its declared path guard;extra terminal cardinality is otherwise unrestricted.
 add('partial-answer-can-be-absent-while-residue-remains',lambda m:m['predicates']['AnswerTerminalDeclared'].remove(['e1']),I=False)
 add('one-overlap-marker-can-be-absent-gap',lambda m:m['predicates']['GapTerminalDeclared'].remove(['e2']),I=False)
 add('one-overlap-marker-can-be-absent-residue',lambda m:m['predicates']['ResidueTerminalDeclared'].remove(['e2']),I=False)
 add('same-posture-on-repeated-targets-allowed',lambda m:setfn(m,'linkPosture','l1','postureA'),I=False)
 def different_target(m):m['predicates']['TargetReferenceDeclared'].append(['targetreferenceOutside']);setfn(m,'linkTarget','l2','targetreferenceOutside')
 add('selected-links-can-target-different-references',different_target,I=True)
 def extra_terminal(m):
  m['domains']['Terminal'].append('e3')
  for n,(sorts,result) in b.FUNCTIONS.items():
   if sorts==['Terminal']:m['functions'][n].append({'args':['e3'],'value':next(x['value'] for x in m['functions'][n] if x['args']==['e1'])})
  for n in ['TerminalApplicable','TerminalInScopeDeclared','AnswerTerminalDeclared','ResidueTerminalDeclared']:m['predicates'][n].append(['e3'])
 add('multiple-terminals-on-one-selected-path-allowed',extra_terminal,I=True)
 def sibling(m):m['predicates']['SiblingMeaningAssignmentDeclared'].append(['meaning','extra']);m['predicates']['ExplicitSiblingReferenceDeclared'].append(['meaning','extra'])
 add('explicit-sibling-reference-is-conditional',sibling,I=True)
 for n in ['ClassificationPreserved','SourceRelationsPreserved','NoSilentSiblingMerge']:add('missing-normalization-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 for n in b.META:add('wrong-normalized-component-'+n,lambda m,n=n:setfn(m,n,'meaning','extra'),T=False)
 for n in b.ROLES:add('meaning-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['meaning']),T=False)
 add('selected-case-in-scope-without-membership',lambda m:m['predicates']['TraceCaseApplicable'].remove(['c0']),T=False)
 for n in ['CaseInScopeDeclared','WorkQuestionBindingDeclared','RelevantChainDeclared','NoHiddenConversationContextRequiredDeclared']:add('missing-case-'+n,lambda m,n=n:m['predicates'][n].remove(['c0']),T=False)
 for n in ['WorkObjectDeclared','ReviewQuestionDeclared','ContextExplicitDeclared']:add('missing-case-component-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('case-binds-outside-meaning',lambda m:setfn(m,'caseMeaning','c0','meaningOutside'),T=False)
 add('case-binds-outside-path',lambda m:setfn(m,'casePath','c0','pOutside'),T=False)
 for n in ['PathInScopeDeclared','TypedPathDeclared']:add('missing-path-'+n,lambda m,n=n:m['predicates'][n].remove(['p0']),T=False)
 add('path-in-scope-without-membership',lambda m:m['predicates']['PathApplicable'].remove(['p0']),T=False)
 add('selected-path-without-any-link',lambda m:setfn(m,'linkPath','l3','p0'),T=False)
 for n in ['LinkInScopeDeclared','TargetPrecisionDeclared','RelationPrecisionDeclared','PosturePrecisionDeclared']:add('missing-link-'+n,lambda m,n=n:m['predicates'][n].remove(['l0']),T=False)
 add('link-in-scope-without-membership',lambda m:m['predicates']['LinkApplicable'].remove(['l0']),T=False)
 for n in ['PositionDeclared','TargetReferenceDeclared','RelationTypeDeclared','AuthorityPostureDeclared']:add('missing-link-component-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('link-binds-outside-path',lambda m:setfn(m,'linkPath','l0','pOutside'),T=False)
 add('duplicate-selected-positions',lambda m:setfn(m,'linkPosition','l1','pos0'),T=False)
 add('selected-self-order-forbidden',lambda m:m['predicates']['LinkBeforeDeclared'].append(['l0','l0']),T=False)
 add('selected-asymmetry-fails',lambda m:m['predicates']['LinkBeforeDeclared'].append(['l1','l0']),T=False)
 add('selected-transitivity-and-totality-fail',lambda m:m['predicates']['LinkBeforeDeclared'].remove(['l0','l2']),T=False)
 add('selected-totality-fails',lambda m:m['predicates']['LinkBeforeDeclared'].remove(['l0','l1']),T=False)
 add('terminal-in-scope-without-membership',lambda m:m['predicates']['TerminalApplicable'].remove(['e0']),T=False)
 add('missing-terminal-scope-declaration',lambda m:m['predicates']['TerminalInScopeDeclared'].remove(['e0']),T=False)
 add('terminal-binds-outside-path',lambda m:setfn(m,'terminalPath','e0','pOutside'),T=False)
 add('terminal-without-any-alternative',lambda m:m['predicates']['AnswerTerminalDeclared'].remove(['e0']),T=False)
 for n in ['AnswerReferenceDeclared','TypedResidueDeclared','NamedGapNameDeclared']:add('missing-terminal-component-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 def hidden_break(m):m['predicates']['ResidueTerminalDeclared'].remove(['e1'])
 add('broken-path-with-only-answer-and-no-marker',hidden_break,T=False)
 for s,arg in [('Meaning','meaning'),('TraceCase','c0'),('WorkObject','workobjectA'),('ReviewQuestion','reviewquestionA'),('DeclaredPath','p0'),('Link','l0'),('Position','pos0'),('TargetReference','targetreferenceA'),('RelationKind','relationkindA'),('AuthorityPosture','postureA'),('Context','contextA'),('Terminal','e0'),('AnswerReference','answerreferenceA'),('TypedResidue','typedresidueA'),('NamedGap','namedgapA')]:add('empty-selected-'+s+'-handle',lambda m,s=s,arg=arg:setfn(m,b.HANDLES[s],arg,'empty'),T=False)
 add('sibling-assignment-without-reference',lambda m:m['predicates']['SiblingMeaningAssignmentDeclared'].append(['meaning','extra']),T=False)
 def empty_sibling(m):m['predicates']['SiblingMeaningAssignmentDeclared'].append(['meaning','empty']);m['predicates']['ExplicitSiblingReferenceDeclared'].append(['meaning','empty'])
 add('sibling-assignment-empty-reference',empty_sibling,T=False)
 add('missing-symbol',lambda m:m['predicates'].pop('TraceCaseApplicable'),error='model-signature-denominator-mismatch')
 add('partial-total-function',lambda m:m['functions']['linkTarget'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(EMPTY='c0'),error='ill-sorted-constant')
 add('wrong-link-order-arity',lambda m:m['predicates'].update(LinkBeforeDeclared=[['l0']]),error='ill-sorted-model-tuple')
 add('duplicate-case-tuple',lambda m:m['predicates']['TraceCaseApplicable'].append(['c0']),error='duplicate-predicate-tuple')
 add('empty-Link-domain',lambda m:m['domains'].update(Link=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['linkTarget'].append(copy.deepcopy(m['functions']['linkTarget'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.source/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Traceability-model-controls/v1-candidate','status':'PASS-for-exact-authored-Traceability-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed normalized meaning,work/question/path links,local order and inclusive answer/residue/gap guards checked on supplied models. Actual navigation,resolution,answer adequacy,hidden-context independence,proof,completeness,approval,authority,owner acceptance and consumer maps remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
