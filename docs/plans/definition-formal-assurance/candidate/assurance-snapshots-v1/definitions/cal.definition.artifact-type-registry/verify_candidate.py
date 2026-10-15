"""Supplied Registry entry,binding,overlay and discriminator models."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def setfn(m,n,arg,value):
 args=arg if isinstance(arg,list) else [arg];next(x for x in m['functions'][n] if x['args']==args)['value']=value
NAMES=['Current','Historical','Candidate','Second','Authority','Outside']
def base_model():
 ds={'RegistryReference':['rMain','rAuthority','rOutside'],'EntryReference':['e'+n for n in NAMES],'ArtifactTypeReference':['t'+n for n in NAMES],'ArtifactTypeKey':['key'+n for n in NAMES],'ArtifactContractReference':['a'+n for n in NAMES],'SchemaDocumentReference':['sShared','sWhole','sOutside'],'SchemaSelector':['kShared','kWhole','kOutside'],'ContentDigest':['dArtifact'+n for n in NAMES[:-1]]+['dSchemaShared','dSchemaWhole','dOutside'],'DiscriminatorPath':['pathShared','pathSecond','pathAuthority','pathZero','pathOutside'],'DiscriminatorValue':['valShared','valSecond','valAuthority','valZero','valOutside'],'DefinitionSetReference':['setPopulated','setEmpty','setOutside'],'DefinitionReference':['defDefinition','defArtifactType','defOutside'],'OwnerDecisionReference':['dec'+n for n in NAMES],'OverlayReference':['o'+n for n in NAMES],'LifecycleState':['state'+n for n in b.STATE_NAMES]+['stateOutside'],'Token':['empty','reference','differentReference']}
 constants={'EMPTY':'empty',**{n:'state'+n for n in b.STATE_NAMES}}
 def suffix(e):return e[1:]
 maps={'entryType':lambda e:'t'+suffix(e),'typeKey':lambda t:'key'+t[1:],'entryArtifact':lambda e:'a'+suffix(e),'entryArtifactDigest':lambda e:'dOutside' if e=='eOutside' else 'dArtifact'+suffix(e),'entrySchema':lambda e:'sShared' if e in ['eCurrent','eHistorical'] else 'sOutside' if e=='eOutside' else 'sWhole','entrySchemaDigest':lambda e:'dSchemaShared' if e in ['eCurrent','eHistorical'] else 'dOutside' if e=='eOutside' else 'dSchemaWhole','entrySchemaSelector':lambda e:'kShared' if e in ['eCurrent','eHistorical'] else 'kOutside' if e=='eOutside' else 'kWhole','entryDiscriminatorPath':lambda e:'pathShared' if e in ['eCurrent','eHistorical','eCandidate'] else 'path'+suffix(e),'entryDiscriminatorValue':lambda e:'valShared' if e in ['eCurrent','eHistorical','eCandidate'] else 'val'+suffix(e),'entryDefinitions':lambda e:'setEmpty' if e=='eCandidate' else 'setOutside' if e=='eOutside' else 'setPopulated','entryDecision':lambda e:'dec'+suffix(e),'entryOverlay':lambda e:'o'+suffix(e),'entryState':lambda e:'stateADMITTED_HISTORICAL' if e=='eHistorical' else 'stateCANDIDATE' if e in ['eCandidate','eOutside'] else 'stateADMITTED_CURRENT'}
 for s,n in b.HANDLES.items():maps[n]=lambda x:'reference'
 assert maps.keys()==b.FUNCTIONS.keys();functions={n:[{'args':list(args),'value':maps[n](*args)} for args in itertools.product(*(ds[s] for s in sorts))] for n,(sorts,result) in b.FUNCTIONS.items()};predicates={n:[] for n in b.SIGNATURE}
 predicates['RegistryApplicable']=[['rMain'],['rAuthority']];predicates['RegistryInScopeDeclared']=copy.deepcopy(predicates['RegistryApplicable']);predicates['CanonicalReferenceIndexDeclared']=copy.deepcopy(predicates['RegistryApplicable'])
 for s in b.SORTS:
  if s not in ['RegistryReference','Token']:predicates[s+'Declared']=[[x] for x in ds[s][:-1]]
 members=[['rMain','e'+n] for n in NAMES[:4]]+[['rAuthority','eAuthority']];entries=ds['EntryReference'][:-1]
 predicates.update(RegistryMemberDeclared=members,RegistryEntryDeclared=[[r,e,maps['entryType'](e)] for r,e in members],ArtifactBindingDeclared=[[e,maps['entryArtifact'](e),maps['entryArtifactDigest'](e)] for e in entries],SchemaBindingDeclared=[[e,maps['entrySchema'](e),maps['entrySchemaDigest'](e),maps['entrySchemaSelector'](e)] for e in entries],DiscriminatorBindingDeclared=[[e,maps['entryDiscriminatorPath'](e),maps['entryDiscriminatorValue'](e)] for e in entries],DefinitionSetBindingDeclared=[[e,maps['entryDefinitions'](e)] for e in entries],DefinitionSetMemberDeclared=[['setPopulated',d] for d in ds['DefinitionReference'][:-1]],EntryDefinitionMemberDeclared=[[e,d] for e in entries if e!='eCandidate' for d in ds['DefinitionReference'][:-1]],LifecycleOverlayDeclared=[[e,maps['entryOverlay'](e),maps['entryDecision'](e),maps['entryState'](e)] for e in entries],EntryReferenceOnlyDeclared=[[e] for e in entries],CandidateEntryDeclared=[['rMain','eCandidate']],AdmittedEntryDeclared=[[r,e] for r,e in members if e!='eCandidate'],CurrentEntryDeclared=[[r,e] for r,e in members if e not in ['eCandidate','eHistorical']],HistoricalVisibleDeclared=[['rMain','eHistorical']],CurrentDecisionOverlayDeclared=[[r,e,maps['entryOverlay'](e)] for r,e in members if e not in ['eCandidate','eHistorical']],SuccessorOverlayDeclared=[['rMain','eHistorical','eCurrent']],AdmittedCurrentDiscriminatorResultDeclared=[[r,maps['entryDiscriminatorPath'](e),maps['entryDiscriminatorValue'](e),maps['entryType'](e)] for r,e in members if e not in ['eCandidate','eHistorical']],SharedSchemaSelectorDeclared=[['kShared']],WholeSchemaSelectorDeclared=[['kWhole']],RegistryActualAuthority=[['rAuthority']])
 return {'domains':ds,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,mutate,T=True,I=None,error=None):
  m=base_model();mutate(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('exact-bindings-three-postures-shared-selector-zero-results-and-independent-authority',lambda m:None,I=True)
 for n in b.ACTUAL:
  if n!='Authority':add('independently-supported-actual-'+n,lambda m,n=n:m['predicates']['RegistryActual'+n].append(['rAuthority']),I=True)
 add('selected-registry-empty-handle',lambda m:setfn(m,b.HANDLES['RegistryReference'],'rMain','empty'),T=False)
 add('outside-registry-empty-handle',lambda m:setfn(m,b.HANDLES['RegistryReference'],'rOutside','empty'),I=True)
 add('selected-registry-scope-disagreement',lambda m:m['predicates']['RegistryInScopeDeclared'].remove(['rMain']),T=False)
 add('canonical-reference-index-marker-absent',lambda m:m['predicates']['CanonicalReferenceIndexDeclared'].remove(['rMain']),T=False)
 add('entry-not-declared',lambda m:m['predicates']['EntryReferenceDeclared'].remove(['eCurrent']),T=False)
 add('entry-empty-handle',lambda m:setfn(m,b.HANDLES['EntryReference'],'eCurrent','empty'),T=False)
 for n,s in b.FACETS.items():
  value=next(x['value'] for x in base_model()['functions'][n] if x['args']==['eCurrent'])
  add('facet-not-declared-'+n,lambda m,s=s,value=value:m['predicates'][s+'Declared'].remove([value]),T=False)
  add('facet-empty-handle-'+n,lambda m,s=s,value=value:setfn(m,b.HANDLES[s],value,'empty'),T=False)
 add('type-key-not-declared',lambda m:m['predicates']['ArtifactTypeKeyDeclared'].remove(['keyCurrent']),T=False)
 add('type-key-empty-handle',lambda m:setfn(m,b.HANDLES['ArtifactTypeKey'],'keyCurrent','empty'),T=False)
 for n in b.STATE_NAMES:add('recognized-state-not-declared-'+n,lambda m,n=n:m['predicates']['LifecycleStateDeclared'].remove(['state'+n]),T=False)
 for n in b.STATE_NAMES[1:]:add('state-constant-collapsed-'+n,lambda m,n=n:m['constants'].update({n:'stateCANDIDATE'}),T=False)
 add('unsupported-fourth-state-declared',lambda m:m['predicates']['LifecycleStateDeclared'].append(['stateOutside']),T=False)
 for name in ['RegistryEntryDeclared','ArtifactBindingDeclared','SchemaBindingDeclared','DiscriminatorBindingDeclared','DefinitionSetBindingDeclared','LifecycleOverlayDeclared']:
  row=next(x for x in base_model()['predicates'][name] if ('eCurrent' in x))
  add('missing-exact-'+name,lambda m,name=name,row=row:m['predicates'][name].remove(row),T=False)
 extra={'RegistryEntryDeclared':['rMain','eCurrent','tHistorical'],'ArtifactBindingDeclared':['eCurrent','aHistorical','dArtifactCurrent'],'SchemaBindingDeclared':['eCurrent','sShared','dSchemaShared','kWhole'],'DiscriminatorBindingDeclared':['eCurrent','pathSecond','valShared'],'DefinitionSetBindingDeclared':['eCurrent','setEmpty'],'LifecycleOverlayDeclared':['eCurrent','oHistorical','decCurrent','stateADMITTED_CURRENT']}
 for name,row in extra.items():add('multiple-conflicting-'+name,lambda m,name=name,row=row:m['predicates'][name].append(row),T=False)
 add('missing-exact-entry-Definition-member',lambda m:m['predicates']['EntryDefinitionMemberDeclared'].remove(['eCurrent','defDefinition']),T=False)
 add('extra-entry-Definition-member',lambda m:m['predicates']['EntryDefinitionMemberDeclared'].append(['eCandidate','defDefinition']),T=False)
 add('Definition-member-reference-not-declared',lambda m:m['predicates']['DefinitionReferenceDeclared'].remove(['defDefinition']),T=False)
 add('Definition-member-empty-handle',lambda m:setfn(m,b.HANDLES['DefinitionReference'],'defDefinition','empty'),T=False)
 def coherent_digest(m):
  setfn(m,'entryArtifactDigest','eCurrent','dArtifactHistorical');next(x for x in m['predicates']['ArtifactBindingDeclared'] if x[0]=='eCurrent')[2]='dArtifactHistorical'
 add('changed-digest-with-coherent-declaration-does-not-verify-bytes',coherent_digest,I=True)
 add('changed-digest-without-corresponding-declaration',lambda m:setfn(m,'entryArtifactDigest','eCurrent','dArtifactHistorical'),T=False)
 def fill_empty(m):
  setfn(m,'entryDefinitions','eCandidate','setPopulated');next(x for x in m['predicates']['DefinitionSetBindingDeclared'] if x[0]=='eCandidate')[1]='setPopulated';m['predicates']['EntryDefinitionMemberDeclared'] += [['eCandidate','defDefinition'],['eCandidate','defArtifactType']]
 add('all-selected-Definition-sets-nonempty-loses-empty-witness',fill_empty,I=False)
 add('shared-selector-marker-loss-is-population-loss',lambda m:m['predicates']['SharedSchemaSelectorDeclared'].clear(),I=False)
 add('whole-selector-marker-loss-is-population-loss',lambda m:m['predicates']['WholeSchemaSelectorDeclared'].clear(),I=False)
 add('candidate-entry-claims-admission',lambda m:m['predicates']['AdmittedEntryDeclared'].append(['rMain','eCandidate']),T=False)
 add('historical-entry-claims-currentness',lambda m:m['predicates']['CurrentEntryDeclared'].append(['rMain','eHistorical']),T=False)
 add('current-entry-claims-candidate',lambda m:m['predicates']['CandidateEntryDeclared'].append(['rMain','eCurrent']),T=False)
 add('current-decision-overlay-missing',lambda m:m['predicates']['CurrentDecisionOverlayDeclared'].remove(['rMain','eCurrent','oCurrent']),T=False)
 add('two-current-decision-overlays',lambda m:m['predicates']['CurrentDecisionOverlayDeclared'].append(['rMain','eCurrent','oHistorical']),T=False)
 add('candidate-entry-gets-current-overlay',lambda m:m['predicates']['CurrentDecisionOverlayDeclared'].append(['rMain','eCandidate','oCandidate']),T=False)
 add('historical-visibility-missing',lambda m:m['predicates']['HistoricalVisibleDeclared'].clear(),T=False)
 add('successor-points-to-candidate',lambda m:m['predicates']['SuccessorOverlayDeclared'].append(['rMain','eHistorical','eCandidate']),T=False)
 add('successor-old-is-current',lambda m:m['predicates']['SuccessorOverlayDeclared'].append(['rMain','eCurrent','eSecond']),T=False)
 add('outside-successor-declaration-unconstrained',lambda m:m['predicates']['SuccessorOverlayDeclared'].append(['rOutside','eCandidate','eSecond']),I=True)
 add('reference-only-marker-missing',lambda m:m['predicates']['EntryReferenceOnlyDeclared'].remove(['eCurrent']),T=False)
 add('selected-entry-declares-duplicate-canonical-carrier',lambda m:m['predicates']['CanonicalCarrierDuplicateDeclared'].append(['eCurrent']),T=False)
 add('registry-declares-that-it-defines-entry-type',lambda m:m['predicates']['RegistryDefinesTypeDeclared'].append(['rMain','tCurrent']),T=False)
 add('registry-declares-that-it-admits-entry-type',lambda m:m['predicates']['RegistryAdmitsTypeDeclared'].append(['rMain','tCurrent']),T=False)
 add('outside-entry-duplicate-marker-unconstrained',lambda m:m['predicates']['CanonicalCarrierDuplicateDeclared'].append(['eOutside']),I=True)
 def same_type(m):
  setfn(m,'entryType','eSecond','tCurrent');next(x for x in m['predicates']['RegistryEntryDeclared'] if x[1]=='eSecond')[2]='tCurrent';next(x for x in m['predicates']['AdmittedCurrentDiscriminatorResultDeclared'] if x[1]=='pathSecond')[3]='tCurrent'
 add('two-selected-entries-for-one-exact-type-version',same_type,T=False)
 def conflicting_current(m):
  setfn(m,'entryDiscriminatorPath','eSecond','pathShared');setfn(m,'entryDiscriminatorValue','eSecond','valShared');next(x for x in m['predicates']['DiscriminatorBindingDeclared'] if x[0]=='eSecond')[1:]=['pathShared','valShared'];next(x for x in m['predicates']['AdmittedCurrentDiscriminatorResultDeclared'] if x[3]=='tSecond')[1:3]=['pathShared','valShared']
 add('two-distinct-current-types-for-one-discriminator',conflicting_current,T=False)
 add('missing-current-discriminator-result',lambda m:m['predicates']['AdmittedCurrentDiscriminatorResultDeclared'].remove(['rMain','pathShared','valShared','tCurrent']),T=False)
 add('candidate-inserted-as-current-result',lambda m:m['predicates']['AdmittedCurrentDiscriminatorResultDeclared'].append(['rMain','pathShared','valShared','tCandidate']),T=False)
 add('historical-inserted-as-current-result',lambda m:m['predicates']['AdmittedCurrentDiscriminatorResultDeclared'].append(['rMain','pathShared','valShared','tHistorical']),T=False)
 add('zero-match-given-fabricated-current-result',lambda m:m['predicates']['AdmittedCurrentDiscriminatorResultDeclared'].append(['rMain','pathZero','valZero','tCurrent']),T=False)
 add('outside-registry-extra-discriminator-result',lambda m:m['predicates']['AdmittedCurrentDiscriminatorResultDeclared'].append(['rOutside','pathZero','valZero','tOutside']),I=True)
 add('type-key-injectivity-not-invented',lambda m:setfn(m,'typeKey','tHistorical','keyCurrent'),I=True)
 add('outside-schema-selector-handle-can-be-empty',lambda m:setfn(m,b.HANDLES['SchemaSelector'],'kOutside','empty'),I=True)
 add('reference-handle-change-does-not-determine-lifecycle',lambda m:setfn(m,b.HANDLES['ArtifactContractReference'],'aCurrent','differentReference'),I=True)
 add('schema-selector-result-is-owner-decision',lambda m:setfn(m,'entrySchemaSelector','eCurrent','decCurrent'),error='ill-sorted-function-result')
 add('missing-symbol',lambda m:m['predicates'].pop('RegistryMemberDeclared'),error='model-signature-denominator-mismatch')
 add('nontotal-entry-selector',lambda m:m['functions']['entrySchemaSelector'].pop(),error='nontotal-function')
 add('ill-sorted-state-constant',lambda m:m['constants'].update(CANDIDATE='aCurrent'),error='ill-sorted-constant')
 add('wrong-schema-binding-arity',lambda m:m['predicates'].update(SchemaBindingDeclared=[['eCurrent','sShared','dSchemaShared']]),error='ill-sorted-model-tuple')
 add('duplicate-membership-tuple',lambda m:m['predicates']['RegistryMemberDeclared'].append(['rMain','eCurrent']),error='duplicate-predicate-tuple')
 add('empty-selector-domain',lambda m:m['domains'].update(SchemaSelector=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['entrySchemaSelector'].append(copy.deepcopy(m['functions']['entrySchemaSelector'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.artifact-surface-classification/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ArtifactTypeRegistry-model-controls/v1-candidate','status':'PASS-for-exact-authored-ArtifactTypeRegistry-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Typed exact Registry entry bindings,reference-only declarations,decision overlays,historical visibility and at-most-one current discriminator results checked on supplied models. Actual bytes,selector validity,decision authority,admission,resolution,owner fidelity and consumer alignment remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
