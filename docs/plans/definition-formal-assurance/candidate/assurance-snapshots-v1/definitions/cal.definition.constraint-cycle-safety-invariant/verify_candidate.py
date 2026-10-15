"""Supplied Constraint Cycle Safety watch/exception models; no solver or edge effects."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def getfn(m,n,*args):return next(x['value'] for x in m['functions'][n] if x['args']==list(args))
def refresh(m):
 for fields,carrier in b.GROUPS:
  for n in fields:m['predicates'][n+'BindingDeclared']=[[x['args'][0],x['value']] for x in m['functions'][n]]
def base_model():
 ds={'InvariantInstanceReference':['i0','i1','iOutside'],'NormalizedIdentityReference':['normalizedID','otherID','identityOutside'],'ScopeReference':['sharedScope','scope0','scope1','scopeOutside'],'ArtifactTypeReference':['invariantType','residueType','otherType','typeOutside'],'SourceReference':['sourceD28','otherSource','sourceOutside'],'SourceRelationReference':['sr0','sr1','srOutside'],'ProposalReference':['p'+str(i) for i in range(8)]+['pOutside'],'ProposalKindReference':['relationKind','edgeKind','movementKind','kindOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'ExceptionReference':['x1','x2','x3','xOutside'],'EvidenceReference':['e1','e2','e3','eOutside'],'ConstraintSemanticsReference':['s1','s2','s3','sOutside'],'ReviewReference':['r1','r2','r3','rOutside'],'WitnessReference':['w1','w2','w3','wOutside'],'ResidueReference':['z1','z2','z3','zOutside'],'ValidatorReference':['v1','v3','vOutside'],'ReviewerReference':['a2','a3','aOutside'],'Token':['empty','ref','other']}
 maps={}
 def table(n,d):maps[n]=lambda x:d.get(x,ds[b.FUNCTIONS[n][1]][-1])
 for n,value in [('instanceIdentity','normalizedID'),('instanceScope','sharedScope'),('instanceType','invariantType')]:table(n,{i:value for i in ['i0','i1']})
 table('instanceSourceRelation',{'i0':'sr0','i1':'sr1'})
 table('sourceRelationIdentity',{'sr0':'normalizedID','sr1':'normalizedID'});table('sourceRelationTarget',{'sr0':'sourceD28','sr1':'sourceD28'})
 owners={'p'+str(i):'owner0' if i%2 else 'owner1' for i in range(8)};scopes={'p'+str(i):'scope0' if i%2 else 'scope1' for i in range(8)}
 table('proposalOwner',owners);table('proposalScope',scopes);table('proposalKind',{'p'+str(i):['edgeKind','relationKind','movementKind'][i%3] for i in range(8)});table('proposalException',{'p1':'x1','p2':'x2','p3':'x3'})
 for n,prefix in [('exceptionEvidence','e'),('exceptionSemantics','s'),('exceptionReview','r'),('exceptionWitness','w'),('exceptionResidue','z')]:table(n,{'x'+str(i):prefix+str(i) for i in [1,2,3]})
 table('exceptionProposal',{'x'+str(i):'p'+str(i) for i in [1,2,3]});table('exceptionOwner',{'x'+str(i):owners['p'+str(i)] for i in [1,2,3]});table('exceptionScope',{'x'+str(i):scopes['p'+str(i)] for i in [1,2,3]})
 table('reviewProposal',{'r'+str(i):'p'+str(i) for i in [1,2,3]});table('reviewScope',{'r'+str(i):scopes['p'+str(i)] for i in [1,2,3]});table('reviewWitness',{'r'+str(i):'w'+str(i) for i in [1,2,3]})
 table('witnessValidator',{'w1':'v1','w3':'v3'});table('witnessReviewer',{'w2':'a2','w3':'a3'});table('residueType',{'z'+str(i):'residueType' for i in [1,2,3]})
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'ref'
 assert set(maps)==set(b.FUNCTIONS)
 functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[z] for z in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['InvariantInstanceReference','ProposalReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['InstanceApplicable','InstanceInScopeDeclared','InstanceGovernedDeclared','InstanceSourceDigestsCurrentDeclared','InstanceDefinitionSchemaValidDeclared','InstanceProjectionExactDeclared']:preds[n]=[['i0'],['i1']]
 preds['SourceRelationAcceptedDeclared']=[['sr0'],['sr1']];preds['InstanceActualAuthority']=[['i1']]
 for n in ['ProposalApplicable','ProposalInScopeDeclared','ProposalGovernedDeclared']:preds[n]=[['p'+str(i)] for i in range(8)]
 preds['ProposalRelationDeclared']=[['p1'],['p4'],['p7']];preds['ProposalEdgeTypeDeclared']=[['p0'],['p3'],['p6']];preds['ProposalOntologyMovementDeclared']=[['p2'],['p5']]
 for n,vals in [('ValueConstraining',[0,1,2,3,4,7]),('CyclePermission',[0,1,2,3,5,7]),('ExplicitAcyclicity',[7]),('EffectiveCyclePermitted',[0,1,2,3,5]),('WatchTriggered',[0,1,2,3]),('GovernanceStopped',[0,1,2,3]),('PromotionBlocked',[0,1,2,3]),('ReviewRequired',[0,1,2,3]),('ReviewCompleted',[1,2,3]),('ExceptionPresent',[1,2,3]),('InfluenceApproved',[1,3,7]),('PromotionApproved',[2,5])]:preds['Proposal'+n+'Declared']=[['p'+str(i)] for i in vals]
 for axis,vals in [('Value',[0,7]),('Label',[1]),('AuthorityState',[2]),('SchemaField',[3]),('ValidationOutcome',[4])]:preds['ProposalConstrains'+axis+'Declared']=[['p'+str(i)] for i in vals]
 preds['ProposalActualAuthority']=[['p5']]
 for n in ['ExceptionRecordedDeclared','ExceptionExplicitOwnerDecisionDeclared']:preds[n]=[['x1'],['x2'],['x3']]
 for n in ['SourceEvidencePresentDeclared']:preds[n]=[['e1'],['e2'],['e3']]
 preds['ConstraintSemanticsNamedDeclared']=[['s1'],['s2'],['s3']]
 for n in ['ReviewRecordedDeclared','ReviewValidatorOrReviewerCatchNamedDeclared']:preds[n]=[['r1'],['r2'],['r3']]
 preds['ReviewSatisfiabilityDeclared']=[['r1'],['r3']];preds['ReviewObstructionDeclared']=[['r2'],['r3']]
 preds['WitnessRecordedDeclared']=[['w1'],['w2'],['w3']];preds['WitnessValidatorDeclared']=[['w1'],['w3']];preds['WitnessReviewerDeclared']=[['w2'],['w3']]
 preds['ResidueTypedDeclared']=[['z1'],['z2'],['z3']];preds['OwnerAcceptsRemainingResidueDeclared']=[[owners['p'+str(i)],'z'+str(i)] for i in [1,2,3]]
 m={'domains':ds,'constants':{'EMPTY':'empty','NORMALIZED_ID':'normalizedID','SHARED_SCOPE':'sharedScope','INVARIANT_TYPE':'invariantType','SOURCE_D28':'sourceD28'},'functions':functions,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(n,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':n,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-watch-stop-pending-and-reviewed-exception-alternatives')
 add('no-selected-invariants-proposals',lambda m:m['predicates'].update(InstanceApplicable=[],InstanceInScopeDeclared=[],ProposalApplicable=[],ProposalInScopeDeclared=[]),I=False)
 add('invariants-without-proposals',lambda m:m['predicates'].update(ProposalApplicable=[],ProposalInScopeDeclared=[]),I=False)
 add('no-independent-authority',lambda m:m['predicates'].update(InstanceActualAuthority=[]),I=False)
 for prefix,names,selected,outside in [('Instance',b.INSTANCE_ACTUAL,['i0','i1'],'iOutside'),('Proposal',b.PROPOSAL_ACTUAL,['p'+str(i) for i in range(8)],'pOutside'),('Exception',b.EXCEPTION_ACTUAL,['x1','x2','x3'],'xOutside')]:
  add('all-'+prefix+'-actual-outcomes-independent',lambda m,prefix=prefix,names=names,selected=selected:m['predicates'].update({prefix+'Actual'+n:[[x] for x in selected] for n in names}),I=None)
  for n in names:
   target=selected[0];add('independently-supported-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,target=target:m['predicates'].update({prefix+'Actual'+n:[list(x) for x in sorted({tuple(x) for x in m['predicates'][prefix+'Actual'+n]}|{(target,)})]}),I=None)
   add('outside-'+prefix+'-Actual'+n,lambda m,prefix=prefix,n=n,outside=outside:m['predicates'][prefix+'Actual'+n].append([outside]))
 for names,target,outside in [(b.INSTANCE_EXCLUDED,'i0','iOutside'),(b.PROPOSAL_EXCLUDED,'p0','pOutside'),(b.EXCEPTION_EXCLUDED,'x1','xOutside')]:
  for n in names:
   add('selected-excluded-'+n,lambda m,n=n,target=target:m['predicates'][n].append([target]),T=False,I=None)
   add('outside-excluded-'+n,lambda m,n=n,outside=outside:m['predicates'][n].append([outside]))
 add('pending-risk-unused-exception-handle-empty',lambda m:setfn(m,b.HANDLES['ExceptionReference'],'xOutside','empty'))
 add('pending-risk-unused-exception-binding-absent',lambda m:m['predicates'].update(proposalExceptionBindingDeclared=[x for x in m['predicates']['proposalExceptionBindingDeclared'] if x[0]!='p0']))
 add('reviewer-only-unused-validator-binding-absent',lambda m:m['predicates'].update(witnessValidatorBindingDeclared=[x for x in m['predicates']['witnessValidatorBindingDeclared'] if x[0]!='w2']))
 add('validator-only-unused-reviewer-binding-absent',lambda m:m['predicates'].update(witnessReviewerBindingDeclared=[x for x in m['predicates']['witnessReviewerBindingDeclared'] if x[0]!='w1']))
 add('unused-validator-handle-empty',lambda m:setfn(m,b.HANDLES['ValidatorReference'],'vOutside','empty'))
 add('unused-reviewer-handle-empty',lambda m:setfn(m,b.HANDLES['ReviewerReference'],'aOutside','empty'))
 add('inclusive-relation-edge-and-movement-kinds',lambda m:(m['predicates']['ProposalRelationDeclared'].append(['p0']),m['predicates']['ProposalOntologyMovementDeclared'].append(['p0'])))
 add('multiple-value-axes-allowed',lambda m:m['predicates']['ProposalConstrainsLabelDeclared'].append(['p0']))
 add('harmless-cyclic-nonvalue-influence-allowed',lambda m:m['predicates']['ProposalInfluenceApprovedDeclared'].append(['p5']))
 add('harmless-acyclic-value-promotion-allowed',lambda m:m['predicates']['ProposalPromotionApprovedDeclared'].append(['p4']))
 add('extra-owner-residue-acceptance-relation-allowed',lambda m:m['predicates']['OwnerAcceptsRemainingResidueDeclared'].append(['owner1','z1']))
 for n,arg in [('InstanceInScopeDeclared','i0'),('InstanceGovernedDeclared','i0'),('InstanceSourceDigestsCurrentDeclared','i0'),('InstanceDefinitionSchemaValidDeclared','i0'),('InstanceProjectionExactDeclared','i0'),('SourceRelationAcceptedDeclared','sr0'),('ProposalInScopeDeclared','p0'),('ProposalGovernedDeclared','p0'),('ProposalGovernanceStoppedDeclared','p0'),('ProposalPromotionBlockedDeclared','p0'),('ProposalReviewRequiredDeclared','p0'),('ProposalReviewCompletedDeclared','p1'),('ExceptionRecordedDeclared','x1'),('ExceptionExplicitOwnerDecisionDeclared','x1'),('SourceEvidencePresentDeclared','e1'),('ConstraintSemanticsNamedDeclared','s1'),('ReviewRecordedDeclared','r1'),('ReviewValidatorOrReviewerCatchNamedDeclared','r1'),('WitnessRecordedDeclared','w1'),('ResidueTypedDeclared','z1')]:add('missing-selected-'+n,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 for n,arg,val in [('instanceIdentity','i0','otherID'),('instanceScope','i0','scope0'),('instanceType','i0','otherType'),('sourceRelationIdentity','sr0','otherID'),('sourceRelationTarget','sr0','otherSource'),('exceptionProposal','x1','p2'),('exceptionOwner','x1','owner1'),('exceptionScope','x1','scope1'),('reviewProposal','r1','p2'),('reviewScope','r1','scope1'),('reviewWitness','r1','w2')]:add('wrong-exact-coordinate-'+n,lambda m,n=n,arg=arg,val=val:change(m,n,arg,val),T=False,I=None)
 add('no-declared-proposal-kind',lambda m:m['predicates']['ProposalEdgeTypeDeclared'].remove(['p0']),T=False,I=None)
 add('value-flag-without-value-axis',lambda m:m['predicates']['ProposalConstrainsValueDeclared'].remove(['p0']),T=False,I=None)
 add('value-axis-without-value-flag',lambda m:m['predicates']['ProposalConstrainsLabelDeclared'].append(['p5']),T=False,I=None)
 add('effective-cycle-with-explicit-acyclicity',lambda m:m['predicates']['ProposalEffectiveCyclePermittedDeclared'].append(['p7']),T=False,I=None)
 add('cycle-permission-without-effective-cycle',lambda m:m['predicates']['ProposalEffectiveCyclePermittedDeclared'].remove(['p0']),T=False,I=None)
 add('watch-without-both-properties',lambda m:m['predicates']['ProposalWatchTriggeredDeclared'].append(['p5']),T=False,I=None)
 add('both-properties-without-watch',lambda m:m['predicates']['ProposalWatchTriggeredDeclared'].remove(['p0']),T=False,I=None)
 add('risk-influence-without-exception',lambda m:m['predicates']['ProposalInfluenceApprovedDeclared'].append(['p0']),T=False,I=None)
 add('risk-promotion-without-exception',lambda m:m['predicates']['ProposalPromotionApprovedDeclared'].append(['p0']),T=False,I=None)
 add('neither-satisfiability-nor-obstruction-review',lambda m:m['predicates']['ReviewSatisfiabilityDeclared'].remove(['r1']),T=False,I=None)
 add('neither-validator-nor-reviewer-witness',lambda m:m['predicates']['WitnessValidatorDeclared'].remove(['w1']),T=False,I=None)
 add('missing-exact-owner-residue-acceptance',lambda m:m['predicates']['OwnerAcceptsRemainingResidueDeclared'].remove(['owner0','z1']),T=False,I=None)
 targets=[(b.INSTANCE_FIELDS,'i0'),(b.RELATION_FIELDS,'sr0'),(b.PROPOSAL_FIELDS,'p0'),(b.OPTIONAL_EXCEPTION_FIELDS,'p1'),(b.EXCEPTION_FIELDS,'x1'),(b.REVIEW_FIELDS,'r1'),(b.VALIDATOR_FIELDS,'w1'),(b.REVIEWER_FIELDS,'w2'),(b.RESIDUE_FIELDS,'z1')]
 for fields,arg in targets:
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   value=getfn(base_model(),n,arg);alt=next(x for x in base_model()['domains'][sort] if x!=value)
   add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   declared=b.member(sort);add('undeclared-selected-target-'+n,lambda m,declared=declared,value=value:m['predicates'][declared].remove([value]),T=False,I=None)
 selected={'InvariantInstanceReference':'i0','NormalizedIdentityReference':'normalizedID','ScopeReference':'sharedScope','ArtifactTypeReference':'invariantType','SourceReference':'sourceD28','SourceRelationReference':'sr0','ProposalReference':'p0','ProposalKindReference':'edgeKind','OwnerReference':'owner1','ExceptionReference':'x1','EvidenceReference':'e1','ConstraintSemanticsReference':'s1','ReviewReference':'r1','WitnessReference':'w1','ResidueReference':'z1','ValidatorReference':'v1','ReviewerReference':'a2'}
 for sort,n in b.HANDLES.items():add('empty-selected-handle-'+sort,lambda m,n=n,value=selected[sort]:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(ProposalReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('ExceptionReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('proposalOwner'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['proposalOwner'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'proposalOwner','p0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['proposalOwner'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['ProposalApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['OwnerAcceptsRemainingResidueDeclared'].append(['owner0']),error='ill-sorted-model-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.principal-reference/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ConstraintCycleSafety-model-controls/v1-candidate','status':'PASS-for-exact-authored-ConstraintCycleSafety-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Necessary typed watch,stop and exact recorded exception checked on supplied models;actual safety,obstruction,review adequacy,owner acceptance,authority,fidelity and whole proof pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
