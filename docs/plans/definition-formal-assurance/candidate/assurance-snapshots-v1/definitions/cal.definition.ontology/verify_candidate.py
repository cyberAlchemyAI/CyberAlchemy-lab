"""Independent typed evidence tuple,branch/confidence/governance and shorthand controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['o1','o2','nb','ns','nr','e1','cb','cs','cr','s1','i1','d1','p1','p0','um','ua','uo','raw'];ontologies=['o1','o2'];values={'EMPTY':'empty','NORMALIZED_ID':'semantic.ontology','NORMALIZED_SCOPE':'scope.shared-authority','DEFINITION_CARRIER':'type.definition','D19_SOURCE':'CAV2-D19',**{n:n.lower() for n in ['CANDIDATE','REVIEWED','PROMOTED','DEMOTED','DEFERRED']}};tokens=list(values.values())+['node-type','edge-kind','ontology-scope','use','confidence-policy','next-gate','guidance','other']
 maps={'edgeSource':lambda x:'nb','edgeTarget':lambda x:'ns','sourceAnchor':lambda x:'s1','inventoryAnchor':lambda x:'i1','nodeType':lambda x:'node-type','edgeKind':lambda x:'edge-kind','ontologyScope':lambda x:'ontology-scope','intendedUse':lambda x:'use','confidencePolicy':lambda x:'confidence-policy','promotionState':lambda x:'candidate','nextGate':lambda x:'next-gate','useGuidance':lambda x:'guidance','normalizedIdentity':lambda x:'semantic.ontology','normalizedOwnerScope':lambda x:'scope.shared-authority','normalizedCarrier':lambda x:'type.definition','normalizedSource':lambda x:'CAV2-D19'}
 functions={n:[{'args':[x],'value':fn(x)} for x in entities] for n,fn in maps.items()};p={n:[] for n in b.SIGNATURE}
 for n in ['Ontology',*b.QUALIFIERS,'ChallengeDriftResidueRouteRecorded']:p[n]=[[x] for x in ontologies]
 for n in b.ACTIONABLE_FIELDS:p[n]=[['o1'],['o2']] if n=='ChallengeDriftResidueRouteRecorded' else [['o1']]
 p.update(HasNode=[['o1',n] for n in ['nb','ns','nr']],HasEdge=[['o1','e1']],OntologyNodeRole=[[n] for n in ['nb','ns','nr']],UsableContent=[[n] for n in ['nb','ns','nr']],OntologyEdgeRole=[['e1']],ContextRole=[[n] for n in ['cb','cs','cr']],ContextAssignment=[['o1','nb','cb'],['o1','ns','cs'],['o1','nr','cr'],['o1','e1','cr']],EvidenceLink=[['o1',n,'s1'] for n in ['nb','ns','nr','e1']],SourceEvidenceRole=[['s1']],InventoryEvidenceRole=[['i1']],LoadBearingClaim=[['nb']],EvidenceConfidenceRecorded=[['nb']],CommitmentConfidenceRecorded=[['nb']],ValidityRelevant=[['nb']],ValidityRecorded=[['nb']],ExpiryRecorded=[['nb']],BranchAware=[['o1']],BusinessClaim=[['nb']],SystemClaim=[['ns']],BridgeClaim=[['nr']],BusinessBranchRole=[['cb']],SystemBranchRole=[['cs']],BridgeBranchRole=[['cr']],Actionable=[['o1']],OnlyPointerList=[['raw']],CurrentOntology=[['o1']],OntologyDefinitionRole=[['d1']],CanonicalDefinitionInstance=[['d1']],AcceptedSourceRelationPreserved=[['d1']],OperationalPhrase=[['p1'],['p0']],ProjectionShorthandRole=[['p1'],['p0']],NoConcreteObligationRemaining=[['p0']],RetirePhraseRequired=[['p0']],HasObligation=[['p1',n] for n in ['um','ua','uo']],ObligationRole=[[n] for n in ['um','ua','uo']],MeaningObligation=[['um']],AuthorityPostureObligation=[['ua']],AgentOperationObligation=[['uo']],RoutesToOntologyMeaning=[['p1','um']],RoutesToAuthorityLifecycle=[['p1','ua']],ConcreteOperationalObligationNamed=[['p1','uo']])
 return {'domains':{'Entity':entities,'Token':tokens},'constants':values,'functions':functions,'predicates':p}
def setfn(m,n,x,value):next(row for row in m['functions'][n] if row['args']==[x])['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-ontology-tuple-branches-confidence-canonical-metadata-and-shorthand',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['o1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['o1']),T=False)
 add('reverse-genus-missing-Ontology',lambda m:m['predicates']['Ontology'].remove(['o1']),T=False)
 for n in ['normalizedIdentity','normalizedOwnerScope','normalizedCarrier','normalizedSource']:add('normalized-metadata-mismatch-'+n,lambda m,n=n:setfn(m,n,'d1','other'),T=False)
 add('canonical-Definition-role-missing',lambda m:m['predicates']['OntologyDefinitionRole'].clear(),T=False)
 add('canonical-source-relation-missing',lambda m:m['predicates']['AcceptedSourceRelationPreserved'].clear(),T=False)
 add('canonical-target-silently-merged',lambda m:m['predicates']['SilentlyMergedSibling'].append(['d1']),T=False)
 for n in ['ontologyScope','intendedUse','confidencePolicy','nextGate','useGuidance']:add('empty-ontology-token-'+n,lambda m,n=n:setfn(m,n,'o1','empty'),T=False)
 for n in ['OntologyNodeRole','UsableContent']:add('node-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['nb']),T=False)
 add('node-without-type-token',lambda m:setfn(m,'nodeType','nb','empty'),T=False)
 add('edge-without-role',lambda m:m['predicates']['OntologyEdgeRole'].clear(),T=False)
 add('edge-without-kind-token',lambda m:setfn(m,'edgeKind','e1','empty'),T=False)
 for n in ['edgeSource','edgeTarget']:add('edge-endpoint-outside-node-set-'+n,lambda m,n=n:setfn(m,n,'e1','raw'),T=False)
 add('self-edge-not-forbidden-by-source',lambda m:setfn(m,'edgeTarget','e1','nb'),I=True)
 add('duplicate-endpoint-signatures-not-global-cardinality-proof',lambda m:None,I=True)
 add('node-context-assignment-missing',lambda m:m['predicates']['ContextAssignment'].remove(['o1','nb','cb']),T=False)
 add('edge-context-assignment-missing',lambda m:m['predicates']['ContextAssignment'].remove(['o1','e1','cr']),T=False)
 add('untyped-context-assignment',lambda m:m['predicates']['ContextRole'].remove(['cb']),T=False)
 add('context-assignment-to-nonmember',lambda m:m['predicates']['ContextAssignment'].append(['o1','raw','cb']),T=False)
 for n in ['SourceEvidenceRole','InventoryEvidenceRole']:add('anchor-without-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('node-evidence-link-missing',lambda m:m['predicates']['EvidenceLink'].remove(['o1','nb','s1']),T=False)
 add('edge-evidence-link-missing',lambda m:m['predicates']['EvidenceLink'].remove(['o1','e1','s1']),T=False)
 add('evidence-link-to-nonmember',lambda m:m['predicates']['EvidenceLink'].append(['o1','raw','s1']),T=False)
 add('untyped-evidence-link',lambda m:m['predicates']['EvidenceLink'].append(['o1','nb','raw']),T=False)
 add('inventory-evidence-link-permitted',lambda m:(m['predicates']['EvidenceLink'].remove(['o1','nb','s1']),m['predicates']['EvidenceLink'].append(['o1','nb','i1'])),I=True)
 for n in ['EvidenceConfidenceRecorded','CommitmentConfidenceRecorded','ValidityRecorded','ExpiryRecorded']:add('required-confidence-or-relevance-record-missing-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('non-loadbearing-confidence-records-not-forced',lambda m:m['predicates']['LoadBearingClaim'].clear())
 add('nonrelevant-validity-records-not-forced',lambda m:m['predicates']['ValidityRelevant'].clear())
 for n in ['CANDIDATE','REVIEWED','PROMOTED','DEMOTED','DEFERRED']:add('explicit-source-promotion-token-'+n,lambda m,n=n:setfn(m,'promotionState','o1',m['constants'][n]),I=True)
 add('carrier-admitted-token-not-source-state-map',lambda m:setfn(m,'promotionState','o1','other'),T=False)
 add('missing-challenge-drift-residue-route',lambda m:m['predicates']['ChallengeDriftResidueRouteRecorded'].remove(['o1']),T=False)
 for n in ['Business','System','Bridge']:
  node={'Business':'nb','System':'ns','Bridge':'nr'}[n];ctx={'Business':'cb','System':'cs','Bridge':'cr'}[n];add('branch-aware-matching-branch-missing-'+n,lambda m,n=n,ctx=ctx:m['predicates'][n+'BranchRole'].remove([ctx]),T=False)
  other=next(x for x in ['Business','System','Bridge'] if x!=n);add('branch-aware-claim-collapse-'+n,lambda m,other=other,node=node:m['predicates'][other+'Claim'].append([node]),T=False)
 add('without-branch-aware-flag-overlapping-claims-not-constrained',lambda m:(m['predicates']['BranchAware'].clear(),m['predicates']['SystemClaim'].append(['nb'])))
 for n in b.ACTIONABLE_FIELDS:add('actionable-without-'+n,lambda m,n=n:m['predicates'][n].remove(['o1']),T=False)
 for n in b.SIBLINGS+['SelfPromotesDefinitions','SelfPromotesConstitutions','SelfPromotesRuntimeContracts','SelfPromotesPublicClaims','OwnsAuthorityTransitions']:add('forbidden-ontology-collapse-or-transition-'+n,lambda m,n=n:m['predicates'][n].append(['o1']),T=False)
 add('ontology-marked-only-pointer-list',lambda m:m['predicates']['OnlyPointerList'].append(['o1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['o1']),T=False)
 add('shorthand-without-projection-role',lambda m:m['predicates']['ProjectionShorthandRole'].remove(['p1']),T=False)
 for n in ['PrimitiveRole','PeerBranchRole','StandaloneSubtypeRole','AuthorityLifecycleAliasRole']:add('operational-shorthand-promoted-to-'+n,lambda m,n=n:m['predicates'][n].append(['p1']),T=False)
 add('shorthand-obligation-untyped',lambda m:m['predicates']['ObligationRole'].remove(['um']),T=False)
 for n in ['RoutesToOntologyMeaning','RoutesToAuthorityLifecycle','ConcreteOperationalObligationNamed']:add('operational-shorthand-route-missing-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('empty-operational-phrase-without-retirement-requirement',lambda m:m['predicates']['RetirePhraseRequired'].clear(),T=False)
 add('empty-ontology-permitted-by-T-with-explicit-I-witness',lambda m:None,I=True)
 add('normalized-Definition-record-not-ontology-object',lambda m:None,I=True)
 add('unclassified-obligation-category-unconstrained',lambda m:m['predicates']['MeaningObligation'].clear())
 add('multi-category-obligation-routes-must-all-hold',lambda m:(m['predicates']['AuthorityPostureObligation'].append(['um']),m['predicates']['RoutesToAuthorityLifecycle'].append(['p1','um'])),I=True)
 add('nontotal-edge-source',lambda m:m['functions']['edgeSource'].pop(),error='nontotal-function')
 add('ill-sorted-edge-source',lambda m:setfn(m,'edgeSource','e1','other'),error='ill-sorted-function-result')
 add('ill-sorted-empty-constant',lambda m:m['constants'].update(EMPTY='absent'),error='ill-sorted-constant')
 add('wrong-context-arity',lambda m:m['predicates'].update(ContextAssignment=[['o1','nb']]),error='ill-sorted-model-tuple')
 add('duplicate-membership-tuple',lambda m:m['predicates']['HasNode'].append(['o1','nb']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['edgeSource'].append(copy.deepcopy(m['functions']['edgeSource'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.model-instance-binding/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Ontology-model-controls/v1-candidate','status':'PASS-for-exact-authored-Ontology-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent typed ontology membership/endpoints,context/evidence links,confidence/governance/branch obligations,canonical Definition metadata and operational shorthand routing. Actual content/truth/provenance/confidence/source/authority/runtime maps pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
