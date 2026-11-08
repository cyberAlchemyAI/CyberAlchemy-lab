"""Supplied exact Representation Revision records;no actual revision,hashing or authority."""
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
 ds={'RevisionReference':['r0','r1','r2','rOutside'],'RepresentationReference':['a0','a1','a2','a3','a4','aOutside'],'RevisionIdentity':['revision0','revision1','revision2','revisionOutside'],'SemanticIdentity':['identity0','identity1','identityOutside'],'EpochReference':['epoch0','epoch1','epochOutside'],'MeaningReference':['meaning0','meaning1','meaningOutside'],'ByteStateReference':['state0','state1','state2','state3','state4','stateOutside'],'DigestReference':['digest0','digest1','digest2','digest3','digest4','digestOutside'],'SchemaReference':['schema0','schema1','schemaOutside'],'ArtifactTypeReference':['type0','type1','typeOutside'],'FieldLayoutReference':['layout0','layout1','layoutOutside'],'EncodingReference':['encoding0','encoding1','encodingOutside'],'DeltaReference':['delta0','delta1','delta2','deltaOutside'],'EquivalenceEvidenceReference':['equivalence0','equivalence1','equivalence2','equivalenceOutside'],'ValidationReference':['validation0','validation1','validation2','validationOutside'],'OwnerSelectionReference':['selection0','selection1','selection2','selectionOutside'],'OwnerReference':['owner0','owner1','ownerOutside'],'ScopeReference':['scope0','scope1','scopeOutside'],'RollbackReference':['rollback0','rollback1','rollback2','rollbackOutside'],'ExclusionsReference':['exclusions0','exclusions1','exclusionsOutside'],'OwnedModelReference':['owned0','owned1','ownedOutside'],'Token':['empty','reference','other']};cs={'EMPTY':'empty'}
 def tail(x):return 'Outside' if x.endswith('Outside') else x[-1]
 def before(x):return 'a'+{'0':'0','1':'0','2':'3','Outside':'Outside'}[tail(x)]
 def after(x):return 'a'+{'0':'1','1':'2','2':'4','Outside':'Outside'}[tail(x)]
 def semantic_tail(x):return 'Outside' if x.endswith('Outside') else '1' if x in ['r2','a3','a4','equivalence2','selection2'] else '0'
 maps={}
 for n,stem in [('revisionIdentity','revision'),('revisionDelta','delta'),('revisionEquivalenceEvidence','equivalence'),('revisionValidation','validation'),('revisionOwnerSelection','selection'),('revisionRollback','rollback')]:maps[n]=lambda x,stem=stem:stem+tail(x)
 maps.update(revisionBefore=before,revisionAfter=after,revisionPreDigest=lambda x:'digest'+tail(before(x)),revisionPostDigest=lambda x:'digest'+tail(after(x)))
 for n,stem in [('revisionSemanticIdentity','identity'),('revisionEpoch','epoch'),('revisionMeaning','meaning'),('revisionOwner','owner'),('revisionScope','scope')]:maps[n]=lambda x,stem=stem:stem+semantic_tail(x)
 for n,stem in [('representationIdentity','identity'),('representationEpoch','epoch'),('representationMeaning','meaning'),('representationScope','scope'),('representationExclusions','exclusions'),('representationOwnedModel','owned')]:maps[n]=lambda x,stem=stem:stem+semantic_tail(x)
 maps.update(representationState=lambda x:'state'+tail(x),representationDigest=lambda x:'digest'+tail(x),stateDigest=lambda x:'digest'+tail(x))
 for n,stem,changed in [('representationSchema','schema',['a1','a4']),('representationTypeContract','type',['a4']),('representationLayout','layout',['a4']),('representationEncoding','encoding',['a2'])]:maps[n]=lambda x,stem=stem,changed=changed:stem+('Outside' if x.endswith('Outside') else '1' if x in changed else '0')
 for n in ['deltaBefore','equivalenceBefore','validationBefore','rollbackBefore']:maps[n]=before
 for n in ['deltaAfter','equivalenceAfter','validationAfter','rollbackAfter']:maps[n]=after
 maps.update(equivalenceMeaning=lambda x:'meaning'+semantic_tail(x),validationRevision=lambda x:'r'+tail(x),selectionRevision=lambda x:'r'+tail(x),selectionEvidence=lambda x:'equivalence'+tail(x),selectionOwner=lambda x:'owner'+semantic_tail(x),selectionScope=lambda x:'scope'+semantic_tail(x),rollbackRevision=lambda x:'r'+tail(x))
 for sort,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert set(maps)==set(b.FUNCTIONS)
 funcs={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};preds={n:[] for n in b.SIGNATURE}
 for sort in b.SORTS:
  if sort not in ['RevisionReference','Token']:preds[sort+'Declared']=[[x] for x in ds[sort] if not x.endswith('Outside')]
 for n in ['RevisionApplicable','RevisionInScopeDeclared','RevisionClassifiedDeclared','RevisionImmutableDeclared']:preds[n]=[['r0'],['r1'],['r2']]
 preds.update(SchemaBindingChangedDeclared=[['r0'],['r2']],TypeContractChangedDeclared=[['r2']],FieldLayoutChangedDeclared=[['r2']],EncodingChangedDeclared=[['r1']],ExactPrePostDeclared=[['r0','a0','a1'],['r1','a0','a2'],['r2','a3','a4']],ExistingEpochDeclared=[['epoch0'],['epoch1']],RevisionActualAuthority=[['r2']])
 for n in ['RepresentationCanonicalDeclared','RepresentationImmutableDeclared']:preds[n]=[[x] for x in ['a0','a1','a2','a3','a4']]
 preds['RepresentationHistoricalDeclared']=[['a0'],['a3']];preds['RepresentationCandidatePostimageDeclared']=[['a1'],['a2'],['a4']]
 for n,stem in [('EquivalenceClaimRecordedDeclared','equivalence'),('ValidationRecordedDeclared','validation'),('OwnerSelectionRecordedDeclared','selection'),('RollbackRouteRecordedDeclared','rollback')]:preds[n]=[[stem+str(i)] for i in range(3)]
 m={'domains':ds,'constants':cs,'functions':funcs,'predicates':preds};refresh(m);return m
def controls():
 rows=[]
 def add(name,mutation=lambda m:None,T=True,I=True,error=None):
  m=base_model();mutation(m);rows.append({'case_id':name,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 def change(m,n,arg,value):setfn(m,n,arg,value);refresh(m)
 add('exact-representation-revisions')
 add('no-selected-revisions',lambda m:m['predicates'].update(RevisionApplicable=[],RevisionInScopeDeclared=[]),I=False)
 add('only-first-revision-selected',lambda m:m['predicates'].update(RevisionApplicable=[['r0']],RevisionInScopeDeclared=[['r0']]),I=False)
 add('duplicate-declared-revision-identity-not-forced-injective',lambda m:change(m,'revisionIdentity','r1','revision0'))
 add('independent-authority-not-supplied',lambda m:m['predicates'].update(RevisionActualAuthority=[]),I=False)
 add('all-actual-outcomes-independently-supplied',lambda m:[m['predicates'].update({'RevisionActual'+n:[['r0'],['r1'],['r2']]}) for n in b.ACTUAL],I=False)
 for n in b.ACTUAL:add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['RevisionActual'+n].append(['r0']))
 for n in b.EXCLUDED:add('selected-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['r0']),T=False,I=None);add('outside-excluded-'+n,lambda m,n=n:m['predicates'][n].append(['rOutside']))
 for n,arg in [('RevisionClassifiedDeclared','r0'),('RevisionImmutableDeclared','r0'),('ExistingEpochDeclared','epoch0'),('RepresentationCanonicalDeclared','a1'),('RepresentationImmutableDeclared','a0'),('RepresentationImmutableDeclared','a1'),('RepresentationHistoricalDeclared','a0'),('RepresentationCandidatePostimageDeclared','a1'),('EquivalenceClaimRecordedDeclared','equivalence0'),('ValidationRecordedDeclared','validation0'),('OwnerSelectionRecordedDeclared','selection0'),('RollbackRouteRecordedDeclared','rollback0')]:add('missing-posture-'+n+'-'+arg,lambda m,n=n,arg=arg:m['predicates'][n].remove([arg]),T=False,I=None)
 add('applicability-without-scope',lambda m:m['predicates']['RevisionInScopeDeclared'].remove(['r0']),T=False,I=None)
 add('scope-without-applicability',lambda m:m['predicates']['RevisionApplicable'].remove(['r0']),T=False,I=None)
 add('missing-exact-prepost',lambda m:m['predicates']['ExactPrePostDeclared'].remove(['r0','a0','a1']),T=False,I=None)
 add('hidden-conflicting-prepost',lambda m:m['predicates']['ExactPrePostDeclared'].append(['r0','a0','a2']),T=False,I=None)
 add('outside-prepost-unconstrained',lambda m:m['predicates']['ExactPrePostDeclared'].append(['rOutside','aOutside','a0']))
 for n,val in [('representationIdentity','identity1'),('representationEpoch','epoch1'),('representationMeaning','meaning1'),('representationScope','scope1'),('representationExclusions','exclusions1'),('representationOwnedModel','owned1')]:add('changed-semantic-component-'+n,lambda m,n=n,val=val:change(m,n,'a1',val),T=False,I=None)
 add('changed-meaning-with-same-label',lambda m:change(m,'representationMeaning','a1','meaning1'),T=False,I=None)
 add('unchanged-canonical-state',lambda m:change(m,'representationState','a1','state0'),T=False,I=None)
 add('unchanged-digest-label',lambda m:change(m,'revisionPostDigest','r0','digest0'),T=False,I=None)
 def collision(m):
  setfn(m,'stateDigest','state1','digest0');setfn(m,'representationDigest','a1','digest0');setfn(m,'revisionPostDigest','r0','digest0');refresh(m)
 add('different-states-with-equal-declared-digest',collision,T=False,I=None)
 add('different-digest-for-one-declared-state',lambda m:change(m,'stateDigest','state1','digest2'),T=False,I=None)
 add('missing-change-dimension',lambda m:m['predicates']['SchemaBindingChangedDeclared'].remove(['r0']),T=False,I=None)
 add('false-positive-change-dimension',lambda m:m['predicates']['EncodingChangedDeclared'].append(['r0']),T=False,I=None)
 def bytes_without_dimension(m):
  setfn(m,'representationSchema','a1','schema0');m['predicates']['SchemaBindingChangedDeclared'].remove(['r0']);refresh(m)
 add('changed-bytes-with-no-declared-dimension',bytes_without_dimension,T=False,I=None)
 def all_four(m):
  setfn(m,'representationEncoding','a4','encoding1');m['predicates']['EncodingChangedDeclared'].append(['r2']);refresh(m)
 add('all-four-change-dimensions-permitted',all_four)
 def only_encoding(m):
  setfn(m,'representationSchema','a1','schema0');setfn(m,'representationEncoding','a1','encoding1');m['predicates']['SchemaBindingChangedDeclared'].remove(['r0']);m['predicates']['EncodingChangedDeclared'].append(['r0']);refresh(m)
 add('schema-only-witness-not-source-wide-policy',only_encoding,I=False)
 for fields,carrier in b.GROUPS:
  arg={'RevisionReference':'r0','RepresentationReference':'a1','DeltaReference':'delta0','EquivalenceEvidenceReference':'equivalence0','ValidationReference':'validation0','OwnerSelectionReference':'selection0','RollbackReference':'rollback0'}[carrier]
  for n,sort in fields.items():
   add('missing-exact-binding-'+n,lambda m,n=n,arg=arg:m['predicates'].update({n+'BindingDeclared':[x for x in m['predicates'][n+'BindingDeclared'] if x[0]!=arg]}),T=False,I=None)
   alt=next(x for x in base_model()['domains'][sort] if x!=getfn(base_model(),n,arg));add('conflicting-exact-binding-'+n,lambda m,n=n,arg=arg,alt=alt:m['predicates'][n+'BindingDeclared'].append([arg,alt]),T=False,I=None)
   if sort!='RevisionReference':
    value=getfn(base_model(),n,arg);add('undeclared-selected-target-'+n,lambda m,sort=sort,value=value:m['predicates'][sort+'Declared'].remove([value]),T=False,I=None)
 for n,arg,val in [('deltaAfter','delta0','a2'),('equivalenceAfter','equivalence0','a2'),('equivalenceMeaning','equivalence0','meaning1'),('validationRevision','validation0','r1'),('validationAfter','validation0','a2'),('selectionRevision','selection0','r1'),('selectionEvidence','selection0','equivalence1'),('selectionOwner','selection0','owner1'),('selectionScope','selection0','scope1'),('rollbackAfter','rollback0','a2'),('rollbackRevision','rollback0','r1')]:add('support-endpoint-mismatch-'+n,lambda m,n=n,arg=arg,val=val:change(m,n,arg,val),T=False,I=None)
 for sort,n in b.HANDLES.items():
  value=next(x for x in base_model()['domains'][sort] if not x.endswith('Outside'));add('empty-selected-handle-'+sort,lambda m,n=n,value=value:setfn(m,n,value,'empty'),T=False,I=None)
 add('malformed-empty-domain',lambda m:m['domains'].update(RevisionReference=[]),error='empty-or-malformed-domain')
 add('malformed-missing-domain',lambda m:m['domains'].pop('MeaningReference'),error='model-signature-denominator-mismatch')
 add('malformed-missing-function',lambda m:m['functions'].pop('revisionBefore'),error='model-signature-denominator-mismatch')
 add('malformed-partial-function',lambda m:m['functions']['revisionBefore'].pop(),error='nontotal-function')
 add('malformed-function-range',lambda m:setfn(m,'revisionBefore','r0','foreign'),error='ill-sorted-function-result')
 add('malformed-function-argument',lambda m:m['functions']['revisionBefore'][0].update(args=['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-range',lambda m:m['predicates']['RevisionApplicable'].append(['foreign']),error='ill-sorted-model-tuple')
 add('malformed-predicate-arity',lambda m:m['predicates']['ExactPrePostDeclared'].append(['r0']),error='ill-sorted-model-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.projection-specification/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-RepresentationRevision-model-controls/v1-candidate','status':'PASS-for-exact-authored-RepresentationRevision-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Exact declared revision/endpoints,identity/epoch/meaning preservation,changed states/digests,immutable history,explicit evidence/validation/owner/rollback and lineage exclusions checked on supplied models;actual equivalence,hashes,storage,rollback,authority and whole proof remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
