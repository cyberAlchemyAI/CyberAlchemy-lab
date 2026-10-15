"""Independent finite Constitution tuple, adoption, application, kind, mode and role controls."""
import copy,itertools,json
import build_candidate as b
import verifier as v
def load(n):return json.loads((b.UNIT/n).read_bytes())
def base_model():
 entities=['c1','c2','q1','q2','d1','d2','s1','s2','s3','r1','r2','p1'];fields=['F_'+n for n in b.FIELDS]+['EXTRA_FIELD'];kinds=b.KINDS+['OTHER_KIND'];modes=b.MODES+['OTHER_MODE'];domains={'Entity':entities,'Token':['EMPTY','value','version1','scope1'],'Field':fields,'SubjectKind':kinds,'ValidationMode':modes};constants={n:n for n in b.CONSTANTS};functions={n:[] for n in b.FUNCTIONS}
 for e,f in itertools.product(entities,fields):functions['fieldValue'].append({'args':[e,f],'value':'version1' if f=='F_version' else 'scope1' if f=='F_scope' else 'value'})
 for e in entities:
  functions['validationModeValue'].append({'args':[e],'value':'NONE_YET' if e=='r2' else 'DETERMINISTIC'});functions['actualSubjectKindValue'].append({'args':[e],'value':'TASK_OR_WORKFLOW' if e=='s2' else 'OTHER_KIND' if e=='s3' else 'ARTIFACT'})
 predicates={n:[] for n in b.SIGNATURE}
 for n in b.QUALIFIERS:predicates[n]=[['c1'],['c2']]+([] if n=='OwnerScopedAuthorityArtifact' else [['q1']])
 predicates.update(Constitution=[['c1'],['c2']],DeclaresField=[[e,'F_'+n] for e in ['c1','c2','q1'] for n in b.FIELDS],DeclaredSubjectKind=[['c1','ARTIFACT'],['c1','TASK_OR_WORKFLOW'],['c2','TASK_OR_WORKFLOW']],RawDeclaredComplete=[['q1']],Rule=[['r1'],['r2']],RuleOf=[['c1','r1'],['c1','r2'],['c2','r2']],DecisionRole=[['d1'],['d2']],OwnerAdoptsExact=[['d1','c1','version1','scope1'],['d2','c2','version1','scope1']],OwnerAuthorizedAdoption=[['d1','c1']],VersionExactOwnerAdoption=[['c1']],Promoted=[['c1']],InScope=[['c1','s1'],['c1','s2'],['c2','s2']],SelectorMatches=[['c1','s1'],['c2','s2']],Applies=[['c1','s1']],Candidate=[['c2']],Selected=[['c2']],ContextLoaded=[['c2']],DefinitionTermPromoted=[['c2']])
 return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}
def controls():
 rows=[]
 def add(id,change=lambda m:None,t=True,i=None,error=None):
  model=base_model();change(model);rows.append({'case_id':id,'model':model,'expected_T':t,'expected_I':i,'expected_error':error})
 def remove(m,n,row):m['predicates'][n].remove(row)
 def append(m,n,row):m['predicates'][n].append(row)
 def function(m,n,args,value):next(x for x in m['functions'][n] if x['args']==args).update(value=value)
 add('qualified-constitution-fields-adoption-application-none-yet-no-actual-effect',i=True)
 for n in b.OUTCOMES:add('independently-supplied-outcome-'+n,lambda m,n=n:append(m,n,['c1']))
 for n in ['Candidate','Selected','ContextLoaded']:add('applicable-constitution-can-also-be-'+n,lambda m,n=n:append(m,n,['c1']))
 for n in b.QUALIFIERS:add('Constitution-missing-genus-qualification-'+n,lambda m,n=n:remove(m,n,['c1']),False)
 add('qualified-genus-missing-Constitution-reverse-iff',lambda m:remove(m,'Constitution',['c1']),False)
 add('raw-declared-fields-mistaken-for-Constitution',lambda m:append(m,'Constitution',['q1']),False)
 for n in b.FIELDS:
  add('Constitution-missing-declared-field-'+n,lambda m,n=n:remove(m,'DeclaresField',['c1','F_'+n]),False)
  add('Constitution-empty-selected-field-'+n,lambda m,n=n:function(m,'fieldValue',['c1','F_'+n],'EMPTY'),False)
 for n in b.ROLES:add('Constitution-cannot-collapse-to-'+n,lambda m,n=n:append(m,n,['c1']),False)
 add('declared-subject-kind-outside-six-allowed-values',lambda m:append(m,'DeclaredSubjectKind',['c1','OTHER_KIND']),False)
 add('unrelated-entity-may-declare-another-kind',lambda m:append(m,'DeclaredSubjectKind',['q1','OTHER_KIND']))
 for mode in b.MODES:add('rule-mode-allowed-'+mode,lambda m,mode=mode:function(m,'validationModeValue',['r2'],mode))
 add('governed-rule-unknown-validation-mode',lambda m:function(m,'validationModeValue',['r2'],'OTHER_MODE'),False)
 add('unrelated-entity-unknown-mode-not-globally-forbidden',lambda m:function(m,'validationModeValue',['q2'],'OTHER_MODE'))
 add('RuleOf-target-without-Rule-qualification',lambda m:remove(m,'Rule',['r1']),False)
 add('raw-adoption-without-authorized-owner-not-qualified',lambda m:append(m,'VersionExactOwnerAdoption',['c2']),False)
 add('qualified-owner-record-without-adoption-marker-reverse-iff',lambda m:remove(m,'VersionExactOwnerAdoption',['c1']),False)
 add('selected-owner-Decision-role-missing',lambda m:remove(m,'DecisionRole',['d1']),False)
 add('selected-owner-authorization-missing',lambda m:remove(m,'OwnerAuthorizedAdoption',['d1','c1']),False)
 add('owner-adopts-another-version-does-not-transfer',lambda m:remove(m,'OwnerAdoptsExact',['d1','c1','version1','scope1']) or append(m,'OwnerAdoptsExact',['d1','c1','value','scope1']),False)
 add('owner-adopts-another-scope-does-not-transfer',lambda m:remove(m,'OwnerAdoptsExact',['d1','c1','version1','scope1']) or append(m,'OwnerAdoptsExact',['d1','c1','version1','value']),False)
 for n,row in [('Promoted',['c1']),('VersionExactOwnerAdoption',['c1']),('InScope',['c1','s1']),('SelectorMatches',['c1','s1'])]:add('Applies-missing-required-'+n,lambda m,n=n,row=row:remove(m,n,row),False)
 add('qualified-matching-context-missing-Applies-reverse-iff',lambda m:remove(m,'Applies',['c1','s1']),False)
 add('candidate-in-scope-match-without-promotion-adoption-cannot-Apply',lambda m:append(m,'Applies',['c2','s2']),False)
 def revoke(m):
  for n,row in [('OwnerAuthorizedAdoption',['d1','c1']),('VersionExactOwnerAdoption',['c1']),('Applies',['c1','s1'])]:remove(m,n,row)
 add('consistent-owner-adoption-revocation-no-application',revoke)
 add('consistent-unpromoted-constitution-no-application',lambda m:remove(m,'Promoted',['c1']) or remove(m,'Applies',['c1','s1']))
 def add_owner(m):
  append(m,'OwnerAuthorizedAdoption',['d2','c2']);append(m,'VersionExactOwnerAdoption',['c2'])
 add('qualified-candidate-adoption-still-needs-promotion',add_owner)
 add('adopted-promoted-second-constitution-applies-to-matching-subject',lambda m:add_owner(m) or append(m,'Promoted',['c2']) or append(m,'Applies',['c2','s2']))
 add('separate-binding-activation-does-not-make-Constitution-validator',lambda m:append(m,'ValidationBindingActive',['c1','r1']))
 add('separate-subject-effect-can-coexist-with-application',lambda m:append(m,'ActualSubjectEffect',['c1','s1']))
 def unmatched_kind(m):
  for n in ['InScope','SelectorMatches','Applies']:append(m,n,['c1','s3'])
 add('unreviewed-selector-kind-map-allows-undeclared-subject-kind',unmatched_kind)
 add('owner-route-field-not-connected-to-authenticated-owner-relation',lambda m:function(m,'fieldValue',['c1','F_owner_route'],'scope1'))
 add('extra-declared-field-not-excluded-by-fifteen-required-fields',lambda m:append(m,'DeclaresField',['c1','EXTRA_FIELD']))
 def alias_values(m):
  for x in m['functions']['fieldValue']:x['value']='value'
  for x in m['predicates']['OwnerAdoptsExact']:x[2:]=['value','value']
 add('all-field-Tokens-can-alias-with-consistent-adoption-labels',alias_values)
 def alias_kinds(m):
  for n in b.KINDS:m['constants'][n]='ARTIFACT'
  m['predicates']['DeclaredSubjectKind']=[['c1','ARTIFACT'],['c2','ARTIFACT']]
 add('six-kind-constant-names-not-proven-distinct-denotations',alias_kinds)
 def alias_modes(m):
  for n in b.MODES:m['constants'][n]='DETERMINISTIC'
  for x in m['functions']['validationModeValue']:x['value']='DETERMINISTIC'
 add('four-mode-constant-names-not-proven-distinct-denotations',alias_modes)
 add('nontotal-field-function',lambda m:m['functions']['fieldValue'].pop(),None,None,'nontotal-function')
 add('ill-sorted-field-function-result',lambda m:function(m,'fieldValue',['c1','F_scope'],'c1'),None,None,'ill-sorted-function-result')
 add('ill-sorted-field-constant',lambda m:m['constants'].update(F_scope='scope1'),None,None,'ill-sorted-constant')
 add('wrong-owner-adoption-arity',lambda m:append(m,'OwnerAdoptsExact',['d1','c1','version1']),None,None,'ill-sorted-model-tuple')
 add('duplicate-declared-field-tuple',lambda m:append(m,'DeclaresField',['c1','F_id']),None,None,'duplicate-predicate-tuple')
 add('empty-SubjectKind-domain',lambda m:m['domains'].update(SubjectKind=[]),None,None,'empty-or-malformed-domain')
 add('duplicate-function-tuple',lambda m:m['functions']['fieldValue'].append(copy.deepcopy(m['functions']['fieldValue'][0])),None,None,'duplicate-function-tuple')
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
        model=next(x['model'] for x in controls() if x['case_id']==q['countermodel_case_id']) if 'countermodel_case_id' in q else base_model()
        model=qualify(model,ids);e=v.Denotation(typed['declarations'],model)
        target=v.renamed(q['target'],ids);witness=v.renamed(q['witness_condition'],ids)
        b.ir.check_composed_formula(composed,target);b.ir.check_composed_formula(composed,witness)
        if q['selected_in_T'] is not False or evaluate(model)[:2]!=(True,True) or e.truth(target) is not False or e.truth(witness) is not True:raise ValueError('Target assumed or no valid countermodel: '+q['query_id'])
        queries.append({'query_id':q['query_id'],'target_false':True,'witness_condition_true':True,'model':model,'model_sha256':b.ir.digest(model),'mechanized_proof':False})
    prior=json.loads((b.BASE/'definitions/cal.definition.closed-authority-kind-invariant/delivery-manifest.json').read_bytes());b.unchanged(prior['files']+context['sources']+bindings);b.r.verify(snap,b.ROOT)
    b.external_current(context)
    comparison=load('comparison-selection.json');b.unchanged(comparison['selected_refs'])
    if comparison['comparison_assembled_into_primary_T'] is not False or comparison['source_precedence_reviewed'] is not False:raise ValueError('Inherited comparison silently adopted')
    if runtime!=v.f.current_bindings():raise ValueError('Runtime drift')
    report={'schema_version':'definition-assurance-Constitution-model-controls/v1-candidate','status':'PASS-for-exact-authored-Constitution-models','authority_effect':'none',
            'checker_bindings':bindings,'runtime_bindings':runtime,'input_refs':[b.ref(b.UNIT/n) for n in ['t.json','static-ir.json','correspondence.json','correspondence-check.json','query-policy.json','denominator.json']],
            'control_count':len(results),'results':results,'nonentailment_countermodels':queries,**counts,'source_fidelity':'pending','semantic_ready':False,'mechanized_proof':False,'whole_definition_translation':'pending',
            'source_files_current':201,'prior_candidate_files_preserved':len(prior['files']),
            'claim_ceiling':'Independent supplied Constitution genus,15-field declaration,qualified exact owner adoption and scoped application,6 declared kinds,4 rule modes and8-role boundaries. Real tuple/owner/version/scope/selector/kind/precedence/composition/validation/effect meaning remains unresolved.'}
    if write:b.put('model-controls.json',report)
    elif not b.r.same_json(report,load('model-controls.json')):raise ValueError('Fresh model controls differ')
    return report
def main():
    x=verify('--write' in b.sys.argv);print(json.dumps({'result':x['status'],'controls':x['control_count'],**{k:x[k] for k in load('denominator.json')},'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
