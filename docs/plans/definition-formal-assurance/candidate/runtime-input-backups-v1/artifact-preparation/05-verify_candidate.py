"""Supplied typed Artifact record and canonical-origin declaration models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
def base_model():
 ds={s:[s.lower()+'A',s.lower()+'Outside'] for s in b.SORTS};ds.update(Artifact=['aDeclared','aAlt','aIntegrity','aActor','aIndependent','aNote','aOutside'],CanonicalKind=['kCanon','kAuthority','kAuthorityB','kOutside'],AuthorityKind=['akA','akB','akOutside'],ProducerReference=['pPrimary','pAlt','pOutside'],OriginStatementReference=['sDeclared','sAlt','sIntegrity','sActor','sIndependent','sNote','sOutside'],OriginAssurance=['hDeclared','hIntegrity','hActor','hOutside'],Digest=['dArtifact','dStatement','dDifferent','dOutside'],Token=['empty','reference'])
 constants={'EMPTY':'empty','DECLARED':'hDeclared','INTEGRITY_BOUND':'hIntegrity','ACTOR_ATTESTED':'hActor'};maps={};selected=ds['Artifact'][:-1];canonical=selected[:-1]
 for n,s in b.FIELDS.items():maps[n]=lambda a,s=s:ds[s][-1] if a=='aOutside' else ds[s][0]
 maps.update(artifactKind=lambda a:'kOutside' if a in ['aNote','aOutside'] else 'kCanon',artifactAuthorityKind=lambda a:'akOutside' if a=='aOutside' else 'akA',artifactDurability=lambda a:ds['Durability'][-1] if a=='aOutside' else ds['Durability'][0],kindAuthorityKind=lambda k:'akOutside' if k=='kOutside' else 'akB' if k=='kAuthorityB' else 'akA',kindDurability=lambda k:ds['Durability'][-1] if k=='kOutside' else ds['Durability'][0],authorityKindEmbedding=lambda k:'kOutside' if k=='akOutside' else 'kAuthorityB' if k=='akB' else 'kAuthority',artifactProducer=lambda a:'pOutside' if a=='aOutside' else 'pAlt' if a=='aAlt' else 'pPrimary',artifactProcess=lambda a:ds['ProcessReference'][-1] if a=='aOutside' else ds['ProcessReference'][0],artifactProcessVersion=lambda a:ds['ProcessVersionReference'][-1] if a=='aOutside' else ds['ProcessVersionReference'][0],artifactOrigin=lambda a:'s'+a[1:],artifactAssurance=lambda a:'hOutside' if a=='aOutside' else 'hIntegrity' if a=='aIntegrity' else 'hActor' if a=='aActor' else 'hDeclared',originProducer=lambda s:'pOutside' if s=='sOutside' else 'pAlt' if s=='sAlt' else 'pPrimary',originProcess=lambda s:ds['ProcessReference'][-1] if s=='sOutside' else ds['ProcessReference'][0],originProcessVersion=lambda s:ds['ProcessVersionReference'][-1] if s=='sOutside' else ds['ProcessVersionReference'][0],artifactStateDigest=lambda a:'dOutside' if a=='aOutside' else 'dArtifact',originStatementDigest=lambda s:'dOutside' if s=='sOutside' else 'dStatement',artifactIntegrityReceipt=lambda a:ds['IntegrityReceiptReference'][0],integrityArtifact=lambda i:'aIntegrity',integrityOrigin=lambda i:'sIntegrity',integrityArtifactDigest=lambda i:'dArtifact',integrityOriginDigest=lambda i:'dStatement',integrityVerifier=lambda i:ds['VerifierReference'][0],integrityMechanism=lambda i:ds['IntegrityMechanismReference'][0],artifactActor=lambda a:ds['ActorReference'][0],artifactIdentityPolicy=lambda a:ds['IdentityPolicyReference'][0],artifactSignature=lambda a:ds['ExternalSignatureReference'][0],signatureArtifact=lambda x:'aActor',signatureOrigin=lambda x:'sActor',signatureActor=lambda x:ds['ActorReference'][0],signaturePolicy=lambda x:ds['IdentityPolicyReference'][0])
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 for n in ['ArtifactApplicable','ArtifactInScopeDeclared','RecordFacetsExplicitDeclared']:predicates[n]=[[a] for a in selected]
 for n in ['CanonicalDeclared','OwnerOriginAdmittedDeclared','OriginStatementDeclared']:predicates[n]=[[a] for a in canonical]
 for s in b.SORTS:
  if s not in ['Artifact','Token']:predicates[s+'Declared']=[[x] for x in ds[s][:-1]]
 predicates['DigestDeclared']=[['dArtifact'],['dStatement'],['dDifferent']]
 predicates.update(CanonicalMachineRepresentationDeclared=[[ds['MachineRepresentationReference'][0]]],GeneratedProjectionDeclared=[[ds['MachineRepresentationReference'][0],ds['HumanProjectionReference'][0],ds['GeneratorReference'][0]]],CanonicalKindMemberDeclared=[['kCanon'],['kAuthority'],['kAuthorityB']],AuthorityKindMemberDeclared=[['akA'],['akB']],CurrentOwnerApprovedOriginsDeclared=[['kCanon']],ProducerEligibleDeclared=[['pPrimary'],['pAlt']],AllowedOriginDeclared=[['kCanon',p,ds['ProcessReference'][0],ds['ProcessVersionReference'][0]] for p in ['pPrimary','pAlt']],IntegritySupportDeclared=[[ds['IntegrityReceiptReference'][0]]],ActorAttestationDeclared=[[ds['ActorReference'][0],ds['ExternalSignatureReference'][0],ds['IdentityPolicyReference'][0]]],ArtifactActualAuthority=[['aIndependent'],['aNote']])
 return {'domains':ds,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-records-set-valued-origins-distinct-assurance-and-authority-independence',lambda m:None,I=True)
 for n in b.ACTUAL:
  def independent(m,n=n):
   if ['aIndependent'] not in m['predicates']['ArtifactActual'+n]:m['predicates']['ArtifactActual'+n].append(['aIndependent'])
  add('independently-supported-actual-'+n,independent,I=True)
 for n,s in b.FIELDS.items():
  add('missing-record-facet-declaration-'+n,lambda m,n=n,s=s:m['predicates'][s+'Declared'].remove([m['functions'][n][0]['value']]),T=False)
  add('empty-record-facet-handle-'+n,lambda m,n=n,s=s:setfn(m,b.HANDLES[s],m['functions'][n][0]['value'],'empty'),T=False)
 add('selected-empty-artifact-handle',lambda m:setfn(m,b.HANDLES['Artifact'],'aDeclared','empty'),T=False)
 add('outside-empty-artifact-handle',lambda m:setfn(m,b.HANDLES['Artifact'],'aOutside','empty'),I=True)
 add('canonical-machine-form-not-declared',lambda m:m['predicates']['CanonicalMachineRepresentationDeclared'].clear(),T=False)
 add('machine-human-generator-map-missing',lambda m:m['predicates']['GeneratedProjectionDeclared'].clear(),T=False)
 def mapped_human(m,add_map):
  value=m['domains']['HumanProjectionReference'][-1];setfn(m,'artifactHuman','aAlt',value);m['predicates']['HumanProjectionReferenceDeclared'].append([value])
  if add_map:m['predicates']['GeneratedProjectionDeclared'].append([m['domains']['MachineRepresentationReference'][0],value,m['domains']['GeneratorReference'][0]])
 add('changed-human-reference-without-exact-generation-map',lambda m:mapped_human(m,False),T=False)
 add('distinct-human-reference-with-explicit-generation-map',lambda m:mapped_human(m,True),I=True)
 add('record-facets-not-explicit',lambda m:m['predicates']['RecordFacetsExplicitDeclared'].remove(['aDeclared']),T=False)
 add('selected-scope-disagreement',lambda m:m['predicates']['ArtifactInScopeDeclared'].remove(['aDeclared']),T=False)
 add('owner-origin-admission-missing',lambda m:m['predicates']['OwnerOriginAdmittedDeclared'].remove(['aDeclared']),T=False)
 add('origin-statement-not-declared',lambda m:m['predicates']['OriginStatementDeclared'].remove(['aDeclared']),T=False)
 add('kind-not-enumerated',lambda m:m['predicates']['CanonicalKindMemberDeclared'].remove(['kCanon']),T=False)
 add('approved-origin-set-not-current',lambda m:m['predicates']['CurrentOwnerApprovedOriginsDeclared'].clear(),T=False)
 add('producer-not-eligible',lambda m:m['predicates']['ProducerEligibleDeclared'].remove(['pPrimary']),T=False)
 add('candidate-only-producer-cannot-qualify',lambda m:m['predicates']['ProducerCandidateOnlyDeclared'].append(['pPrimary']),T=False)
 add('exact-origin-not-allowed',lambda m:m['predicates']['AllowedOriginDeclared'].pop(0),T=False)
 for n,s in [('artifactProducer','ProducerReference'),('artifactProcess','ProcessReference'),('artifactProcessVersion','ProcessVersionReference'),('artifactOrigin','OriginStatementReference')]:add('unresolved-origin-reference-'+n,lambda m,n=n,s=s:setfn(m,n,'aDeclared',m['domains'][s][-1]),T=False)
 for n,s in [('originProducer','ProducerReference'),('originProcess','ProcessReference'),('originProcessVersion','ProcessVersionReference')]:add('changed-bound-origin-tuple-'+n,lambda m,n=n,s=s:setfn(m,n,'sDeclared',m['domains'][s][-1]),T=False)
 add('self-chosen-authority-kind',lambda m:setfn(m,'artifactAuthorityKind','aDeclared','akOutside'),T=False)
 add('self-chosen-durability',lambda m:setfn(m,'artifactDurability','aDeclared',m['domains']['Durability'][-1]),T=False)
 add('declared-authority-kind-not-in-canonical-image',lambda m:setfn(m,'authorityKindEmbedding','akA','kOutside'),T=False)
 add('declared-kind-embedding-must-preserve-distinct-members',lambda m:setfn(m,'authorityKindEmbedding','akB','kAuthority'),T=False)
 add('outside-kind-embedding-may-share-an-image',lambda m:setfn(m,'authorityKindEmbedding','akOutside','kAuthority'),I=True)
 add('unknown-assurance-tag',lambda m:setfn(m,'artifactAssurance','aDeclared','hOutside'),T=False)
 add('assurance-constants-collapsed',lambda m:m['constants'].update(INTEGRITY_BOUND='hDeclared'),T=False)
 add('unknown-assurance-declared',lambda m:m['predicates']['OriginAssuranceDeclared'].append(['hOutside']),T=False)
 add('recognized-assurance-not-declared',lambda m:m['predicates']['OriginAssuranceDeclared'].remove(['hDeclared']),T=False)
 add('canonical-shape-cannot-be-hidden',lambda m:m['predicates']['CanonicalDeclared'].remove(['aDeclared']),T=False)
 add('noncanonical-note-cannot-be-labeled-canonical',lambda m:m['predicates']['CanonicalDeclared'].append(['aNote']),T=False)
 add('outside-canonical-label-unconstrained',lambda m:m['predicates']['CanonicalDeclared'].append(['aOutside']),I=True)
 add('integrity-support-not-declared',lambda m:m['predicates']['IntegritySupportDeclared'].clear(),T=False)
 for n,val in [('integrityArtifact','aDeclared'),('integrityOrigin','sDeclared'),('integrityArtifactDigest','dDifferent'),('integrityOriginDigest','dDifferent')]:add('changed-integrity-binding-'+n,lambda m,n=n,val=val:setfn(m,n,m['domains']['IntegrityReceiptReference'][0],val),T=False)
 for n,s in [('integrityVerifier','VerifierReference'),('integrityMechanism','IntegrityMechanismReference')]:add('unresolved-integrity-support-'+n,lambda m,n=n,s=s:setfn(m,n,m['domains']['IntegrityReceiptReference'][0],m['domains'][s][-1]),T=False)
 add('actor-attestation-not-declared',lambda m:m['predicates']['ActorAttestationDeclared'].clear(),T=False)
 for n,val in [('signatureArtifact','aDeclared'),('signatureOrigin','sDeclared'),('signatureActor','actorreferenceOutside'),('signaturePolicy','identitypolicyreferenceOutside')]:add('changed-L2-binding-'+n,lambda m,n=n,val=val:setfn(m,n,m['domains']['ExternalSignatureReference'][0],val),T=False)
 for s in ['ProducerReference','ProcessReference','ProcessVersionReference','OriginStatementReference','IntegrityReceiptReference','VerifierReference','IntegrityMechanismReference','ActorReference','IdentityPolicyReference','ExternalSignatureReference','Digest']:
  add('missing-support-carrier-declaration-'+s,lambda m,s=s:m['predicates'][s+'Declared'].clear(),T=False)
 def noncanonical(m):
  m['predicates']['OwnerOriginAdmittedDeclared'].remove(['aDeclared']);m['predicates']['CanonicalDeclared'].remove(['aDeclared'])
 add('without-owner-origin-admission-record-can-remain-noncanonical',noncanonical,I=True)
 add('canonically-declared-reference-identity-reuse-does-not-imply-uniqueness',lambda m:setfn(m,'artifactIdentity','aAlt',m['functions']['artifactIdentity'][0]['value']),I=True)
 add('current-kind-with-more-than-one-allowed-origin',lambda m:None,I=True)
 add('ordinary-note-may-use-unspecified-origin-support',lambda m:setfn(m,'artifactAssurance','aNote','hOutside'),I=True)
 add('future-actor-support-is-not-actual-signature-success',lambda m:None,I=True)
 add('authority-kind-result-is-durability',lambda m:setfn(m,'artifactAuthorityKind','aDeclared',m['domains']['Durability'][0]),error='ill-sorted-function-result')
 add('missing-symbol',lambda m:m['predicates'].pop('ArtifactApplicable'),error='model-signature-denominator-mismatch')
 add('nontotal-function',lambda m:m['functions']['artifactOrigin'].pop(),error='nontotal-function')
 add('ill-sorted-constant',lambda m:m['constants'].update(DECLARED='aDeclared'),error='ill-sorted-constant')
 add('wrong-origin-relation-arity',lambda m:m['predicates'].update(AllowedOriginDeclared=[['kCanon','pPrimary']]),error='ill-sorted-model-tuple')
 add('duplicate-artifact-tuple',lambda m:m['predicates']['ArtifactApplicable'].append(['aDeclared']),error='duplicate-predicate-tuple')
 add('empty-actor-domain',lambda m:m['domains'].update(ActorReference=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['artifactOrigin'].append(copy.deepcopy(m['functions']['artifactOrigin'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.validation/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Artifact-model-controls/v1-candidate','status':'PASS-for-exact-authored-Artifact-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed record facets,exact declared origin tuples,kind-derived classification and separately supported assurance declarations checked on supplied models. Actual execution,truth,verification,authority,owner fidelity and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
