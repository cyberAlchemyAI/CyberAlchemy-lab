"""Supplied ordered-pair/version/qualifier/authority/local-scope models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):next(x for x in m['functions'][n] if x['args']==[arg])['value']=value
def getfn(m,n,arg):return next(x['value'] for x in m['functions'][n] if x['args']==[arg])
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
 triples=sorted({(getfn(m,'pairContract',r),getfn(m,'pairSourceKind',r),getfn(m,'pairTargetKind',r)) for [r] in m['predicates']['PairApplicable']})
 m['predicates']['ConnDeclared']=[list(x) for x in triples];m['predicates']['SourceIndexDeclared']=[list(x) for x in sorted({(c,s) for c,s,t in triples})];m['predicates']['TargetIndexDeclared']=[list(x) for x in sorted({(c,t) for c,s,t in triples})]
 m['predicates']['AvailableConnDeclared']=[list(x) for x in triples if [x[0]] in m['predicates']['ContractAdmittedDeclared'] and [x[0]] in m['predicates']['ContractEffectiveDeclared']]
 m['predicates']['PairAvailableDeclared']=[[r] for [r] in m['predicates']['PairApplicable'] if [getfn(m,'pairContract',r)] in m['predicates']['ContractAdmittedDeclared'] and [getfn(m,'pairContract',r)] in m['predicates']['ContractEffectiveDeclared']]
def base_model():
 ds={'ContractReference':['c0','c1','c2','cOutside'],'RelationKindReference':['rk0','rk1','rkOutside'],'QuestionReference':['q0','q1','qOutside'],'EndpointKindReference':['kA','kB','kC','kRegister','kOutside'],'EndpointContractReference':['epA','epB','epC','epOutside'],'PairReference':['r'+str(i) for i in range(6)]+['rOutside'],'DirectionReference':['directed','symmetric','dirOutside'],'QualifierSchemaReference':['qs0','qs1','qsOutside'],'ValueDomainReference':['values0','values1','valuesOutside'],'CrossConstraintReference':['cross0','cross1','crossOutside'],'AuthorityReference':['generic','specialized','authorityOutside'],'ContestabilityReference':['contest0','contest1','contestOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'EvidenceReference':['evidence0','evidence1','evidenceOutside'],'LifecycleEffectReference':['life0','life1','lifeOutside'],'ValidationEffectReference':['validation0','validation1','validationOutside'],'AuthorityEffectRuleReference':['effects0','effects1','effectsOutside'],'ProposalReference':['p0','p1','p2','p3','pOutside'],'ScopeReference':['global0','global1','local0','local1','scopeOutside'],'OntologyContractReference':['ontology0','ontology1','ontologyOutside'],'InstanceReference':['i0','i1','iOutside'],'ObjectReference':['objA','objB','objC','objOutside'],'QualifierValuesReference':['iv0','iv1','ivOutside'],'Token':['empty','ref','other']}
 maps={}
 def table(n,values):maps[n]=lambda x:values.get(x,ds[b.FUNCTIONS[n][1]][-1])
 table('contractKind',{'c0':'rk0','c1':'rk0','c2':'rk1'});table('contractQuestion',{'c0':'q0','c1':'q0','c2':'q1'});table('contractScope',{'c0':'global0','c1':'global0','c2':'global1'})
 table('endpointKind',{'epA':'kA','epB':'kB','epC':'kC'})
 contracts=['c0','c0','c1','c1','c1','c2'];sources=['kA','kB','kA','kB','kA','kA'];targets=['kB','kC','kB','kC','kC','kB']
 for n,values in [('pairContract',contracts),('pairSourceKind',sources),('pairTargetKind',targets),('pairSourceEndpoint',['ep'+x[-1] for x in sources]),('pairTargetEndpoint',['ep'+x[-1] for x in targets]),('pairDirection',['directed']*6),('pairSchema',['qs0']*5+['qs1']),('pairValues',['values0']*5+['values1']),('pairConstraints',['cross0']*5+['cross1']),('pairAuthority',['generic']*4+['specialized','generic']),('pairContestability',['contest0']*5+['contest1']),('pairOwner',['owner0']*5+['owner1']),('pairEvidence',['evidence0']*5+['evidence1']),('pairLifecycle',['life0']*5+['life1']),('pairValidation',['validation0']*5+['validation1']),('pairEffectRules',['effects0']*5+['effects1'])]:table(n,{'r'+str(i):z for i,z in enumerate(values)})
 for n,values in [('proposalSourceKind',['kA','kA','kA','kC']),('proposalTargetKind',['kC','kB','kB','kRegister']),('proposalDirection',['directed']*4),('proposalScope',['global0','global1','local0','local1']),('proposalOwner',['owner0','owner1','owner0','owner1']),('proposalEvidence',['evidence0','evidence1','evidence0','evidence1'])]:table(n,{'p'+str(i):z for i,z in enumerate(values)})
 table('proposalPredecessor',{'p0':'c0','p1':'c0'});table('proposalSuccessor',{'p0':'c1','p1':'c2'});table('proposalNewPair',{'p0':'r4','p1':'r5'});table('proposalOntology',{'p2':'ontology0','p3':'ontology1'})
 table('instanceContract',{'i0':'c0','i1':'c1'});table('instanceSource',{'i0':'objA','i1':'objA'});table('instanceTarget',{'i0':'objB','i1':'objC'});table('instanceDirection',{'i0':'directed','i1':'directed'});table('instanceQualifiers',{'i0':'iv0','i1':'iv1'});table('instancePair',{'i0':'r0'});table('objectKind',{'objA':'kA','objB':'kB','objC':'kC'})
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['ContractReference','PairReference','ProposalReference','InstanceReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['ContractApplicable','ContractInScopeDeclared','ContractGlobalDeclared','ContractFiniteDeclared','ContractClosedDeclared']:preds[n]=[['c0'],['c1'],['c2']]
 for n in ['ContractAdmittedDeclared','ContractEffectiveDeclared']:preds[n]=[['c0'],['c2']]
 for n in ['PairApplicable','PairInScopeDeclared','PairStructureDeclared','PairQualifierNoCollapseDeclared']:preds[n]=[['r'+str(i)] for i in range(6)]
 for n in ['PairTypedRelationCanonicalDeclared','PairTypedRelationWritableDeclared']:preds[n]=[['r'+str(i)] for i in [0,1,2,3,5]]
 for n in ['PairSpecializedCanonicalDeclared','PairSpecializedWritableDeclared','PairProjectsAsDeclared']:preds[n]=[['r4']]
 preds['PairSpecializedPresentDeclared']=[['r1'],['r3'],['r4']];preds['PairRepresentedByDeclared']=[['r1'],['r3']]
 preds['EndpointResolvedDeclared']=[['epA'],['epB'],['epC']];preds['EndpointAdmittedCarrierDeclared']=[['epA'],['epC']];preds['EndpointGovernedInternalDeclared']=[['epB']];preds['EndpointPermittedByContractDeclared']=[['c0','epB'],['c1','epB'],['c2','epB']]
 preds['SchemaClosedDeclared']=[['qs0'],['qs1']];preds['AuthorityTypedRelationDeclared']=[['generic']];preds['AuthoritySpecializedDeclared']=[['specialized']]
 preds['PairValueDomainBoundDeclared']=[['r'+str(i),maps['pairValues']('r'+str(i))] for i in range(6)];preds['PairCrossConstraintBoundDeclared']=[['r'+str(i),maps['pairConstraints']('r'+str(i))] for i in range(6)]
 preds['PairQuestionFitsDeclared']=[['r'+str(i),maps['contractQuestion'](contracts[i])] for i in range(6)]
 preds['ContestOwnerRouteDeclared']=[['contest0','owner0'],['contest1','owner1']]
 for n in ['RelationKind','Pair','Qualifiers','Endpoints','Instance']:preds['ContestCovers'+n+'Declared']=[['contest0'],['contest1']]
 for n in ['ProposalApplicable','ProposalInScopeDeclared']:preds[n]=[['p0'],['p1'],['p2'],['p3']]
 preds['ProposalGlobalDeclared']=[['p0'],['p1']];preds['ProposalLocalDeclared']=[['p2'],['p3']];preds['ProposalGlobalStructureDeclared']=[['p0'],['p1']];preds['ProposalReuseDeclared']=[['p0']];preds['ProposalDistinctDeclared']=[['p1']];preds['ProposalCandidateValidatedDeclared']=[['p0']]
 preds['ProposalAdmissionRecordedDeclared']=[['p1']];preds['ProposalGlobalAvailableDeclared']=[['p1']];preds['ProposalExactAdmissionDeclared']=[['p1','c2','r5']];preds['OntologyExactScopedDeclared']=[['ontology0','local0'],['ontology1','local1']]
 for n in ['InstanceApplicable','InstanceInScopeDeclared']:preds[n]=[['i0'],['i1']]
 preds['InstanceConformingDeclared']=[['i0']]
 for n in ['PairSchemaValidatedDeclared','PairValuesAcceptedDeclared','PairCrossConstraintsSatisfiedDeclared']:preds[n]=[['r0','iv0']]
 preds['KindRegisteredDeclared']=[['kRegister'],['kC']];preds['PairActualAuthority']=[['r1']]
 m={'domains':ds,'constants':{'EMPTY':'empty'},'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(n,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':n,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('closed-ordered-pairs-candidate-reuse-distinct-admitted-local-and-instance')
 add('no-selected-contracts-pairs-proposals-instances',lambda m:m['predicates'].update(ContractApplicable=[],ContractInScopeDeclared=[],PairApplicable=[],PairInScopeDeclared=[],ProposalApplicable=[],ProposalInScopeDeclared=[],InstanceApplicable=[],InstanceInScopeDeclared=[]),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(PairActualAuthority=[]),I=False)
 for prefix,names,selected,outside in [('Contract',b.CONTRACT_ACTUAL,['c0','c1','c2'],'cOutside'),('Pair',b.PAIR_ACTUAL,['r'+str(i) for i in range(6)],'rOutside'),('Proposal',b.PROPOSAL_ACTUAL,['p0','p1','p2','p3'],'pOutside'),('Instance',b.INSTANCE_ACTUAL,['i0','i1'],'iOutside')]:
  add('all-'+prefix+'-actual-outcomes-independent',lambda m,prefix=prefix,names=names,selected=selected:m['predicates'].update({prefix+'Actual'+n:[[x] for x in selected] for n in names}),I=None)
  for n in names:
   target=selected[0];add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,target=target:m['predicates'].update({prefix+'Actual'+n:[list(x) for x in sorted({tuple(x) for x in m['predicates'][prefix+'Actual'+n]}|{(target,)})]}),I=None)
 for names,target,outside in [(b.CONTRACT_EXCLUDED,'c0','cOutside'),(b.PAIR_EXCLUDED,'r0','rOutside'),(b.PROPOSAL_EXCLUDED,'p0','pOutside'),(b.INSTANCE_EXCLUDED,'i0','iOutside')]:
  for n in names:
   add('selected-excluded-'+n,lambda m,n=n,target=target:m['predicates'][n].append([target]),T=False,I=None)
   add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('register-additional-kind-without-connection',lambda m:m['predicates']['KindRegisteredDeclared'].append(['kA']))
 add('local-unused-global-bindings-absent',lambda m:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!='p2'] for n in b.GLOBAL_FIELDS}))
 add('nonconforming-unused-pair-binding-absent',lambda m:m['predicates'].update(instancePairBindingDeclared=[x for x in m['predicates']['instancePairBindingDeclared'] if x[0]!='i1']))
 add('unused-contract-handle-empty',lambda m:setfn(m,b.HANDLES['ContractReference'],'cOutside','empty'))
 add('unused-pair-handle-empty',lambda m:setfn(m,b.HANDLES['PairReference'],'rOutside','empty'))
 add('unused-ontology-handle-empty',lambda m:setfn(m,b.HANDLES['OntologyContractReference'],'ontologyOutside','empty'))
 add('admitted-contract-can-be-ineffective',lambda m:(m['predicates']['ContractEffectiveDeclared'].remove(['c2']),m['predicates']['ProposalGlobalAvailableDeclared'].remove(['p1']),refresh(m)),I=False)
 add('admitted-carrier-and-governed-internal-alternatives-inclusive',lambda m:m['predicates']['EndpointAdmittedCarrierDeclared'].append(['epB']))
 add('cartesian-cross-pair-not-authorized',lambda m:m['predicates']['ConnDeclared'].append(['c0','kA','kC']),T=False,I=None)
 add('reverse-pair-not-implicit',lambda m:m['predicates']['ConnDeclared'].append(['c0','kB','kA']),T=False,I=None)
 add('registration-not-a-pair',lambda m:m['predicates']['ConnDeclared'].append(['c0','kRegister','kA']),T=False,I=None)
 add('false-source-index',lambda m:m['predicates']['SourceIndexDeclared'].append(['c0','kRegister']),T=False,I=None)
 add('false-target-index',lambda m:m['predicates']['TargetIndexDeclared'].append(['c0','kRegister']),T=False,I=None)
 add('candidate-pair-not-available',lambda m:m['predicates']['PairAvailableDeclared'].append(['r4']),T=False,I=None)
 add('candidate-available-connection-not-admitted',lambda m:m['predicates']['AvailableConnDeclared'].append(['c1','kA','kC']),T=False,I=None)
 add('validated-proposal-without-admission-not-available',lambda m:m['predicates']['ProposalGlobalAvailableDeclared'].append(['p0']),T=False,I=None)
 add('local-proposal-cannot-be-global-available',lambda m:m['predicates']['ProposalGlobalAvailableDeclared'].append(['p2']),T=False,I=None)
 add('proposal-both-global-and-local',lambda m:m['predicates']['ProposalLocalDeclared'].append(['p0']),T=False,I=None)
 add('proposal-neither-global-nor-local',lambda m:m['predicates']['ProposalGlobalDeclared'].remove(['p0']),T=False,I=None)
 add('dual-canonical-authority',lambda m:m['predicates']['PairSpecializedCanonicalDeclared'].append(['r0']),T=False,I=None)
 add('second-writable-specialized-projection',lambda m:m['predicates']['PairSpecializedWritableDeclared'].append(['r1']),T=False,I=None)
 add('generic-canonical-projection-not-projects-as',lambda m:m['predicates']['PairProjectsAsDeclared'].append(['r1']),T=False,I=None)
 add('specialized-canonical-must-have-presence',lambda m:m['predicates']['PairSpecializedPresentDeclared'].remove(['r4']),T=False,I=None)
 add('wildcard-selected-endpoint',lambda m:m['predicates']['KindWildcardDeclared'].append(['kA']),T=False,I=None)
 add('catchall-selected-endpoint',lambda m:m['predicates']['KindCatchAllDeclared'].append(['kB']),T=False,I=None)
 add('same-kind-reuse-question-changed',lambda m:change(m,'contractQuestion','c1','q1'),T=False,I=None)
 add('distinct-kind-cannot-reuse-kind-identity',lambda m:change(m,'contractKind','c2','rk0'),T=False,I=None)
 add('reuse-new-pair-already-in-predecessor',lambda m:(change(m,'proposalTargetKind','p0','kB'),change(m,'proposalNewPair','p0','r2')),T=False,I=None)
 add('wrong-pair-endpoint-kind',lambda m:change(m,'pairSourceKind','r0','kC'),T=False,I=None)
 add('wrong-proposal-direction',lambda m:change(m,'proposalDirection','p0','symmetric'),T=False,I=None)
 add('wrong-local-ontology-scope',lambda m:m['predicates']['OntologyExactScopedDeclared'].remove(['ontology0','local0']),T=False,I=None)
 add('conforming-instance-wrong-direction',lambda m:change(m,'instanceDirection','i0','symmetric'),T=False,I=None)
 add('conforming-instance-wrong-target-kind',lambda m:change(m,'objectKind','objB','kC'),T=False,I=None)
 add('unadmitted-instance-cannot-conform',lambda m:m['predicates']['InstanceConformingDeclared'].append(['i1']),T=False,I=None)
 for n,arg in [('ContractGlobalDeclared','c0'),('ContractFiniteDeclared','c0'),('ContractClosedDeclared','c0'),('ContractAdmittedDeclared','c0'),('EndpointResolvedDeclared','epA'),('EndpointAdmittedCarrierDeclared','epA'),('EndpointGovernedInternalDeclared','epB'),('SchemaClosedDeclared','qs0'),('PairQualifierNoCollapseDeclared','r4'),('PairStructureDeclared','r0'),('ProposalGlobalStructureDeclared','p0')]:add('missing-selected-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,row in [('EndpointPermittedByContractDeclared',['c0','epB']),('PairValueDomainBoundDeclared',['r0','values0']),('PairCrossConstraintBoundDeclared',['r0','cross0']),('ContestOwnerRouteDeclared',['contest0','owner0']),('PairQuestionFitsDeclared',['r4','q0']),('ProposalExactAdmissionDeclared',['p1','c2','r5']),('PairSchemaValidatedDeclared',['r0','iv0']),('PairValuesAcceptedDeclared',['r0','iv0']),('PairCrossConstraintsSatisfiedDeclared',['r0','iv0'])]:add('missing-exact-relation-'+n,lambda m,n=n,row=row:m['predicates'][n].remove(row),T=False,I=None)
 for n in ['RelationKind','Pair','Qualifiers','Endpoints','Instance']:add('missing-contestability-'+n,lambda m,n=n:m['predicates']['ContestCovers'+n+'Declared'].remove(['contest0']),T=False,I=None)
 def rejected_question(m):
  setfn(m,'contractQuestion','c1','q1');m['predicates']['PairQuestionFitsDeclared']=[['r'+str(i),'q0' if i<2 else 'q1'] for i in range(6)];m['predicates']['ProposalReuseDeclared'].remove(['p0']);m['predicates']['ProposalRejectedDeclared'].append(['p0']);refresh(m)
 add('changed-question-can-remain-rejected',rejected_question,I=False)
 add('rejected-proposal-cannot-be-available',lambda m:(rejected_question(m),m['predicates']['ProposalGlobalAvailableDeclared'].append(['p0'])),T=False,I=None)
 add('reuse-successor-cannot-drop-old-pair',lambda m:(m['predicates']['PairApplicable'].remove(['r3']),m['predicates']['PairInScopeDeclared'].remove(['r3']),refresh(m)),T=False,I=None)
 add('reuse-successor-cannot-add-unproposed-pair',lambda m:(change(m,'pairContract','r5','c1'),change(m,'pairSourceKind','r5','kC'),change(m,'pairSourceEndpoint','r5','epC'),m['predicates']['PairQuestionFitsDeclared'].remove(['r5','q1']),m['predicates']['PairQuestionFitsDeclared'].append(['r5','q0'])),T=False,I=None)
 targets=[(b.CONTRACT_FIELDS,'c0'),(b.ENDPOINT_FIELDS,'epA'),(b.PAIR_FIELDS,'r0'),(b.PROPOSAL_FIELDS,'p0'),(b.GLOBAL_FIELDS,'p0'),(b.LOCAL_FIELDS,'p2'),(b.INSTANCE_FIELDS,'i0'),(b.INSTANCE_PAIR_FIELDS,'i0'),(b.OBJECT_FIELDS,'objA')]
 for fields,arg in targets:
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value);add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
 selected={sort:values[0] for sort,values in base_model()['domains'].items() if sort!='Token'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 for n,mutation,code in [('empty-domain',lambda m:m['domains'].update(PairReference=[]),'empty-or-malformed-domain'),('missing-domain',lambda m:m['domains'].pop('EndpointKindReference'),'model-signature-denominator-mismatch'),('missing-function',lambda m:m['functions'].pop('pairContract'),'model-signature-denominator-mismatch'),('partial-function',lambda m:m['functions']['pairContract'].pop(),'nontotal-function'),('function-range',lambda m:setfn(m,'pairContract','r0','foreign'),'ill-sorted-function-result'),('function-argument',lambda m:m['functions']['pairContract'][0].update(args=['foreign']),'ill-sorted-model-tuple'),('predicate-range',lambda m:m['predicates']['PairApplicable'].append(['foreign']),'ill-sorted-model-tuple'),('predicate-arity',lambda m:m['predicates']['ConnDeclared'].append(['c0','kA']),'ill-sorted-model-tuple')]:add('malformed-'+n,mutation,error=code)
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
    prior=json.loads((b.BASE/'definitions/cal.definition.constraint-cycle-safety-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-TypedConnectionExtension-model-controls/v1-candidate','status':'PASS-for-exact-authored-TypedConnectionExtension-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary closed ordered-pair/version/endpoint/qualifier/canonical-authority/global-local/instance declarations checked on supplied models;actual resolution,admission,validation,conformance,availability,authority,fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
