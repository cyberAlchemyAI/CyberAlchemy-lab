"""Independent exact View binding,material/annotation and normative temporal boundary controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['v1','v2','v3','d1','d2','r1','r2','c1','e1','e2','m1','x1','s1','u1','raw','event1'];views=['v1','v2','v3'];fields=b.FIELDS+['extra'];tokens=['empty','spec','viewID','proj1','proj2','proj3','sel','reason','lineage','limitation','expiry','refresh','other','*']
 domains={'Entity':entities,'Field':fields,'Token':tokens}
 def fv(e,f):return {'v1':'proj1','v2':'proj2','v3':'proj3'}.get(e,'spec') if f=='projection_digest' else 'spec'
 functions={'fieldValue':[{'args':[e,f],'value':fv(e,f)} for e,f in itertools.product(entities,fields)]}
 maps={'normalizedIdValue':lambda e:'viewID','viewRequest':lambda e:'r2' if e=='v2' else 'r1','viewContext':lambda e:'c1','viewEpoch':lambda e:'e2' if e=='v2' else 'e1','requestContext':lambda e:'c1','viewDigest':lambda e:{'v1':'proj1','v2':'proj2','v3':'proj3'}.get(e,'spec'),'materialSource':lambda e:'s1','materialSelector':lambda e:'sel','materialDigest':lambda e:'spec','exclusionReason':lambda e:'reason'}
 functions.update({n:[{'args':[e],'value':fn(e)} for e in entities] for n,fn in maps.items()})
 p={n:[] for n in b.SIGNATURE};p.update(ContextView=[[e] for e in views],NormalizedDefinitionTarget=[['d1'],['d2']],ContextResolutionScope=[['d1'],['d2']],DefinitionCarrier=[['d1'],['d2']],CanonicalDefinitionInstance=[['d1']],PreservesExactD66Relation=[['d1']],RequestRole=[['r1'],['r2']],ContextRole=[['c1']],SourceEpochRole=[['e1'],['e2']],SourceRole=[['s1']],ConsumerRole=[['u1']],IncludedRecordRole=[['m1']],ExcludedRecordRole=[['x1']],DigestBoundMaterial=[['m1']],IncludedMaterial=[['v1','m1']],ExcludedMaterial=[['v1','x1']],MaterialAtEpoch=[['m1','e1']],DeclaresField=[[e,f] for e,f in itertools.product(views+['raw'],b.FIELDS)],Lineage=[[e,'lineage'] for e in views],Limitation=[[e,'limitation'] for e in views],Expiry=[['v1','expiry'],['v3','expiry']],Refresh=[['v2','refresh']],LineageToken=[['lineage']],LimitationToken=[['limitation']],ExpiryToken=[['expiry']],RefreshToken=[['refresh']],ImmutableProjectionRequired=[[e] for e in views],CurrentView=[['v1']],StaleView=[['v2']],ConsumerUse=[['v2','u1']],ReResolutionRequired=[['v2','u1']],ChangedResolutionBindings=[['v1','event1']],NewViewRequired=[['v1','event1']],PriorViewRetentionRequired=[['v1','event1']],RawDeclaredComplete=[['raw']])
 for n in b.QUALIFIERS:p[n]=[[e] for e in views]
 return {'domains':domains,'constants':{'EMPTY':'empty','NORMALIZED_VIEW_ID':'viewID',**{'F_'+n:n for n in b.FIELDS}},'functions':functions,'predicates':p}
def setfn(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args)['value']=value
def controls():
 rows=[]
 def add(id,change,T=True,I=None,error=None):
  m=base_model();change(m);rows.append({'case_id':id,'model':m,'expected_T':T,'expected_I':I,'expected_error':error})
 add('typed-View-exact-bindings-material-annotations-and-temporal-boundaries',lambda m:None,I=True)
 for n in b.OUTCOMES:add('independent-outcome-'+n,lambda m,n=n:m['predicates'][n].append(['v1']))
 for n in b.QUALIFIERS:add('missing-genus-'+n,lambda m,n=n:m['predicates'][n].remove(['v1']),T=False)
 add('reverse-genus-iff-missing',lambda m:m['predicates']['ContextView'].remove(['v1']),T=False)
 for n in b.FIELDS:add('missing-field-'+n,lambda m,n=n:m['predicates']['DeclaresField'].remove(['v1',n]),T=False)
 for n in ['ContextResolutionScope','DefinitionCarrier']:add('normalized-definition-missing-'+n,lambda m,n=n:m['predicates'][n].remove(['d1']),T=False)
 add('normalized-definition-wrong-identity',lambda m:setfn(m,'normalizedIdValue',['d1'],'other'),T=False)
 add('canonical-definition-without-target',lambda m:m['predicates']['NormalizedDefinitionTarget'].remove(['d1']),T=False)
 add('canonical-definition-without-D66-relation',lambda m:m['predicates']['PreservesExactD66Relation'].clear(),T=False)
 add('canonical-definition-silent-sibling-merge',lambda m:m['predicates']['SilentSiblingIdentityMerge'].append(['d1']),T=False)
 for n,e in [('RequestRole','r1'),('ContextRole','c1'),('SourceEpochRole','e1')]:add('untyped-binding-'+n,lambda m,n=n,e=e:m['predicates'][n].remove([e]),T=False)
 add('request-Context-mismatch',lambda m:setfn(m,'requestContext',['r1'],'e1'),T=False)
 add('empty-projection-digest',lambda m:(setfn(m,'viewDigest',['v1'],'empty'),setfn(m,'fieldValue',['v1','projection_digest'],'empty')),T=False)
 add('projection-field-digest-mismatch',lambda m:setfn(m,'fieldValue',['v1','projection_digest'],'other'),T=False)
 for n,e in [('IncludedRecordRole','m1'),('SourceRole','s1'),('DigestBoundMaterial','m1')]:add('included-untyped-'+n,lambda m,n=n,e=e:m['predicates'][n].remove([e]),T=False)
 add('included-missing-epoch-binding',lambda m:m['predicates']['MaterialAtEpoch'].clear(),T=False)
 for n in ['materialSelector','materialDigest']:add('included-empty-'+n,lambda m,n=n:setfn(m,n,['m1'],'empty'),T=False)
 add('excluded-untyped-record',lambda m:m['predicates']['ExcludedRecordRole'].clear(),T=False)
 add('excluded-empty-reason',lambda m:setfn(m,'exclusionReason',['x1'],'empty'),T=False)
 add('included-and-excluded-same-record',lambda m:(m['predicates']['ExcludedMaterial'].append(['v1','m1']),m['predicates']['ExcludedRecordRole'].append(['m1'])),T=False)
 for n,role,tok in [('Lineage','LineageToken','lineage'),('Limitation','LimitationToken','limitation'),('Expiry','ExpiryToken','expiry'),('Refresh','RefreshToken','refresh')]:
  if n in ['Lineage','Limitation']:add('annotation-absent-'+n,lambda m,n=n,tok=tok:m['predicates'][n].remove(['v1',tok]),T=False)
  add('annotation-untyped-'+n,lambda m,role=role:m['predicates'][role].clear(),T=False)
  entity='v2' if n=='Refresh' else 'v1'
  add('annotation-empty-'+n,lambda m,n=n,role=role,tok=tok,entity=entity:(m['predicates'][n].remove([entity,tok]),m['predicates'][n].append([entity,'empty']),m['predicates'][role].append(['empty'])),T=False)
 add('neither-expiry-nor-refresh',lambda m:m['predicates']['Expiry'].remove(['v1','expiry']),T=False)
 add('no-immutable-requirement',lambda m:m['predicates']['ImmutableProjectionRequired'].remove(['v1']),T=False)
 for n in ['NewViewRequired','PriorViewRetentionRequired']:add('changed-binding-without-'+n,lambda m,n=n:m['predicates'][n].clear(),T=False)
 add('stale-use-untyped-consumer',lambda m:m['predicates']['ConsumerRole'].clear(),T=False)
 add('stale-use-without-reresolution-requirement',lambda m:m['predicates']['ReResolutionRequired'].clear(),T=False)
 add('silent-stale-reuse',lambda m:m['predicates']['SilentStaleReuse'].append(['v2','u1']),T=False)
 for n in b.INFER_FLAGS:add('forbidden-inference-'+n,lambda m,n=n:m['predicates'][n].append(['v1']),T=False)
 for n in [*b.ROLES,'SiblingMeaningImportedWithoutExplicitReference']:add('forbidden-sibling-collapse-'+n,lambda m,n=n:m['predicates'][n].append(['v1']),T=False)
 add('same-source-in-distinct-included-excluded-records',lambda m:None,I=True)
 add('empty-material-View-permitted',lambda m:None,I=True)
 add('both-expiry-and-refresh-permitted',lambda m:m['predicates']['Refresh'].append(['v1','refresh']),I=True)
 add('literal-glob-selector-not-parsed',lambda m:setfn(m,'materialSelector',['m1'],'*'),I=True)
 add('opaque-projection-digest-not-hash-authentication',lambda m:(setfn(m,'viewDigest',['v1'],'other'),setfn(m,'fieldValue',['v1','projection_digest'],'other')),I=True)
 add('one-material-record-marked-at-two-epochs',lambda m:(m['predicates']['MaterialAtEpoch'].append(['m1','e2']),m['predicates']['IncludedMaterial'].append(['v2','m1'])),I=True)
 add('nonstale-silent-reuse-unconstrained',lambda m:m['predicates']['SilentStaleReuse'].append(['v1','u1']),I=True)
 add('noncanonical-target-sibling-marker-unconstrained',lambda m:m['predicates']['SilentSiblingIdentityMerge'].append(['d2']),I=True)
 add('extra-field-declaration-permitted',lambda m:m['predicates']['DeclaresField'].append(['v1','extra']),I=True)
 add('field-name-constants-may-alias',lambda m:m['constants'].update(F_request_ref='context_ref'),I=True)
 add('nontotal-view-function',lambda m:m['functions']['viewRequest'].pop(),error='nontotal-function')
 add('ill-sorted-view-function',lambda m:setfn(m,'viewRequest',['v1'],'spec'),error='ill-sorted-function-result')
 add('ill-sorted-field-constant',lambda m:m['constants'].update(F_request_ref='absent'),error='ill-sorted-constant')
 add('wrong-material-arity',lambda m:m['predicates'].update(IncludedMaterial=[['v1']]),error='ill-sorted-model-tuple')
 add('duplicate-material-tuple',lambda m:m['predicates']['IncludedMaterial'].append(['v1','m1']),error='duplicate-predicate-tuple')
 add('empty-entity-domain',lambda m:m['domains'].update(Entity=[]),error='empty-or-malformed-domain')
 add('duplicate-view-function-tuple',lambda m:m['functions']['viewRequest'].append(copy.deepcopy(m['functions']['viewRequest'][0])),error='duplicate-function-tuple')
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
    prior=json.loads((b.BASE/'definitions/cal.definition.context-request/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-ContextView-model-controls/v1-candidate','status':'PASS-for-exact-authored-ContextView-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent exact View bindings,material and annotation markers and normative immutability/stale-use requirements. Actual digests,resolution and clock/currentness remain pending.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
