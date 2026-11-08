"""Typed Relation identity, ordered endpoints and declared metadata remain separate."""
import hashlib
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import resolver as r
import ir
import correspondence as co

SCOPE='scope:candidate:typed-relation-instance-v1'
FIELDS={'sourceEndpoint':'EndpointInstance','targetEndpoint':'EndpointInstance','kindVersion':'RelationKindVersion',
        'qualifierRecord':'QualifierRecord','ownerLabel':'OwnerLabel','evidenceRecord':'EvidenceRecord',
        'lifecycleLabel':'LifecycleLabel','contestabilityContract':'ContestabilityContract','scopeLabel':'Scope'}
SORTS=['RelationInstance',*dict.fromkeys(FIELDS.values())]
METADATA=['HasQualifiers','HasOwner','HasEvidence','HasLifecycle','HasContestability']
OUTCOMES=['AuthorityEffect','AdmittedInstance','RuntimeSucceeded','IdentityEquivalent','PublicationReleased']
APPEARANCES=['SchemaFieldsPresent','SharedPath','OntologyProjection','CandidateValidated']
UNARY=['TypedRelation','IndependentlyIdentified','GlobalConnection','GovernedIdentityOrRecord','BoundedScope',*METADATA,
       'MergesEndpointIdentities',*APPEARANCES,*OUTCOMES]
SIGNATURE={n:['RelationInstance'] for n in UNARY}
SIGNATURE.update(ExactInstance=['EndpointInstance'],AdmittedKindVersion=['RelationKindVersion'],
                 AllowedOrderedPair=['RelationKindVersion','EndpointInstance','EndpointInstance'])
def var(n):return {'op':'var','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n):return {'op':'fn','name':n,'args':[var('x')]}
def both(*args):return {'op':'and','args':list(args)}
def neg(arg):return {'op':'not','arg':arg}
def implies(left,right):return {'op':'implies','left':left,'right':right}
def eq(left,right):return {'op':'eq','left':left,'right':right}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(body):return quant('forall','RelationInstance','x',body)
def witness(body):return quant('exists','RelationInstance','x',body)
CORE=every(implies(pred('TypedRelation','x'),both(pred('IndependentlyIdentified','x'),pred('GlobalConnection','x'),
      pred('ExactInstance',fn('sourceEndpoint')),pred('ExactInstance',fn('targetEndpoint')),
      pred('AdmittedKindVersion',fn('kindVersion')),
      pred('AllowedOrderedPair',fn('kindVersion'),fn('sourceEndpoint'),fn('targetEndpoint')),
      *[pred(n,'x') for n in METADATA])))
GENUS=every(implies(pred('TypedRelation','x'),both(pred('GovernedIdentityOrRecord','x'),pred('BoundedScope','x'))))
NO_MERGE=every(implies(pred('TypedRelation','x'),neg(pred('MergesEndpointIdentities','x'))))
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(name,value):
    with (UNIT/name).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
    return ref(UNIT/name)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
    for x in refs:
        if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input: '+x['path'])
def source_ref(snap,identity):
    row=next(x for x in snap['current_entries'] if x['definition_id']==identity)
    return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}
def main():
    context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);snap=snapshot();r.verify(snap,ROOT)
    source=source_ref(snap,'cal.definition.typed-relation');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc))
    clauses=[];links=[];N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression'
    B='/voices/scientific_formal/boundary_conditions/0';boundaries={'/boundaries/0','/voices/scientific_formal/boundary_conditions/1','/scope/exclusions/0'}
    for unit in units:
        selector=unit['selector'];text=texts[selector];spans=[(0,len(text))]
        if selector==N:
            cut=text.index('It neither');split=text.index('nor becomes');spans=[(0,cut),(cut,split),(split,len(text))]
        if selector==F:
            cut=text.index('; ')+2;spans=[(0,cut),(cut,len(text))]
        if selector in boundaries:
            split=text.index('nor becomes');spans=[(0,split),(split,len(text))]
        formula=None
        for start,end in spans:
            excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional']
            rationale='Exact source meaning, use/admission, actual metadata contracts, lifecycle, effect or counterpart alignment requires reviewed bindings; no target premise is fabricated.'
            if selector==B or selector==N and start==0:
                formula=CORE;disposition='encoded';roles=['definition'];forms=['genus-differentia','axiomatic-implicit']
                rationale='Necessary local instance conditions: independent identity, exact ordered endpoints, selected admitted-kind status/allowed pair and declared metadata. Status predicates and total fields do not authenticate a live Kind, owner, evidence or contract.'
            elif selector==F and start==0:
                formula=GENUS;disposition='encoded';roles=['definition'];forms=['axiomatic-implicit']
                rationale='Source explicit necessary governed-identity-or-record and bounded-scope conditions; no converse or whole source closure is selected.'
            elif selector in boundaries and start==0 or selector==N and excerpt.startswith('It neither'):
                formula=NO_MERGE;disposition='encoded';roles=['definition'];forms=['axiomatic-implicit']
                rationale='No endpoint-identity-merging status for a Typed Relation. The following nonentailment span is separately deferred and tested as a target outside T; no blanket negation of attributes is inferred.'
            elif selector.startswith('/voices/plain_language/') or selector.startswith('/voices/domain_context/') or selector.startswith('/voices/scientific_formal/notation/'):
                disposition='explanatory';roles=['explanation-example'];forms=['non-definitional'];rationale='Intuition, example and notation retained without creating TR-204, its endpoints, kind admission or authority.'
            cid='TRL-'+str(len(clauses)+1).zfill(3)
            clauses.append({'clause_id':cid,'source_selector':selector,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),
                            'start_character':start,'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':rationale})
            links.append({'unit_id':unit['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
    def clause(selector):return next(x['clause_id'] for x in clauses if x['source_selector']==selector)
    uses=[('cal.definition.relation-kind',N,'An exact admitted Kind version and ordered allowed-pair contract require the Relation Kind counterpart.'),
          ('cal.definition.governed-model',F,'Governed identity/record and bounded scope need a reviewed counterpart meaning, not nominal predicate equality.'),
          ('cal.definition.evidence',N,'Evidence metadata and its actual validity/support are separate from connection identity.'),
          ('cal.definition.contestability-policy',N,'Contestability contract applicability, route and challenge behavior require explicit counterpart semantics.'),
          ('cal.definition.authority',F,'Meaning and candidate relation status do not establish an authority effect.'),
          ('cal.definition.definition','/voices/scientific_formal/testable_conditions/0','Every use requires the exact Definition or admitted successor; version reference alone does not admit an instance.')]
    deps=[source_ref(snap,x[0]) for x in uses]
    dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
    declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]
    declarations += [{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':['RelationInstance'],'result_sort':s,'definedness_policy':None} for n,s in FIELDS.items()]
    declarations += [{'kind':'predicate' if len(s)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':s} for n,s in SIGNATURE.items()]
    populations=[]
    required={'TypedRelation','IndependentlyIdentified','GlobalConnection','GovernedIdentityOrRecord','BoundedScope',*METADATA}
    for n in UNARY:
        req=n in required
        populations.append({'population_id':'POP-'+n,'carrier':'RelationInstance','predicate_ref':n,'requirement':'required' if req else 'unresolved',
                            'statement':witness(both(pred('TypedRelation','x'),pred(n,'x'))) if req else None,'scope':SCOPE,
                            'rationale':'One hypothetical typed relation prevents vacuous candidate requirements.' if req else 'Actual appearance, admission/effect or merge-status existence/exemption needs owner review; none is invented.','review_ref':None})
    for n in ['ExactInstance','AdmittedKindVersion','AllowedOrderedPair']:
        target=pred('ExactInstance',fn('sourceEndpoint')) if n=='ExactInstance' else pred('AdmittedKindVersion',fn('kindVersion')) if n=='AdmittedKindVersion' else pred('AllowedOrderedPair',fn('kindVersion'),fn('sourceEndpoint'),fn('targetEndpoint'))
        populations.append({'population_id':'POP-'+n,'carrier':'RelationInstance','predicate_ref':None,'requirement':'required','statement':witness(both(pred('TypedRelation','x'),target)),
                            'scope':SCOPE,'rationale':'Endpoint, selected kind and ordered pair witnesses belong to the same hypothetical typed relation; no actual Kind admission decision is claimed.','review_ref':None})
    core={'interpretation_id':'interpretation:typed-relation-instance-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,
          'depends_on':deps,'relations':[],'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],
          'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:typed-relation-necessary-conditions-candidate'}
    finding_texts=[('TRL-CARRIER-001','Independent relation identity, exact endpoint identities and carrier shape need actual Kind/Artifact Type/instance mapping. A self-loop does not merge identities; multiple identified relations may share a pair.'),
                   ('TRL-KIND-002','AdmittedKindVersion and AllowedOrderedPair are selected primitive statuses, not authenticated admission, a resolved live registry or proof of every pair/qualifier contract.'),
                   ('TRL-METADATA-003','Total fields and presence predicates do not establish evidence support, owner authorization, lifecycle transitions or operational contestability.'),
                   ('TRL-BOUNDARY-004','Nonentailment from schema/path/projection/validation and nonmerging do not ban an independently admitted relation with those same attributes.'),
                   ('TRL-GENUS-005','The explicit governed-record/bounded-scope expression is weaker than the normative instance requirements; common vocabulary and completeness converse are unreviewed.'),
                   ('TRL-ADMISSION-006','Current CAL0065 source admission and embedded historical candidate posture are distinct; use/instance admission, successor selection and external effects require separate decisions.')]
    findings=[{'finding_id':fid,'selectors':[N,F],'description':desc,'status':'unresolved','owner_route':'role:definition-owner and selected relation/kind/evidence/governance owners must review exact contracts and mappings.'} for fid,desc in finding_texts]
    encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
    packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),
            'source_selection':'current','inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,
            'dependency_links':dl,'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Six authored semantic uses require independent denominator review.','Actual kind, pair, qualifiers, owners, lifecycle, contestability and endpoint carrier alignment are unresolved.']},
            'assumption_links':[],'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},
            'review_packet':{'instances':[{'case_id':'TR-204-hypothetical','scenario':'A separately identified relation connects an exact capability to an exact product under a member-of Kind version and product-capability qualifier.','expected_interpretation':'Necessary local statuses and metadata may hold without authority or runtime success.','rationale':'Source example is hypothetical rather than an actual admitted instance.','related_clause_ids':encoded}],
                             'counterexamples':[{'case_id':'same-schema-field-without-kind','scenario':'A row names endpoints but lacks the selected admitted Kind version and allowed ordered pair.','expected_interpretation':'Schema fields alone do not entail TypedRelation.','rationale':'Meaning is distinct from carrier shape or candidate validation.','related_clause_ids':encoded}],
                             'known_losses':['No actual relation/endpoint carrier or live Kind registry selected.','No owner/evidence/lifecycle/contestability execution or authority proof.','Necessary conditions are not a complete membership biconditional.','No semantics inferred for unaligned counterpart predicates.'],'review_status':'pending','review_ref':None}}
    report=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
    if not report['character_accounting_complete']:raise ValueError(json.dumps(report))
    typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
    queries=[]
    for a,z in [('TypedRelation',n) for n in OUTCOMES]+[(n,'TypedRelation') for n in APPEARANCES]:
        queries.append({'query_id':a+'-does-not-entail-'+z,'target':every(implies(pred(a,'x'),pred(z,'x'))),
                        'witness_condition':witness(both(pred(a,'x'),neg(pred(z,'x')))),'selected_in_T':False})
    queries.append({'query_id':'self-loop-is-not-endpoint-identity-merging','target':every(implies(pred('TypedRelation','x'),neg(eq(fn('sourceEndpoint'),fn('targetEndpoint'))))),
                    'witness_condition':witness(both(pred('TypedRelation','x'),eq(fn('sourceEndpoint'),fn('targetEndpoint')))),'selected_in_T':False,'model_case':'self-loop'})
    for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',report),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('clause-analysis.json',{'authority_effect':'none','source':source,'source_units':len(units),'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'})]:put(name,value)
    counts={'source_units':len(units),'mapped_clauses':len(clauses),'encoded_clauses':len(encoded),'explanatory_clauses':sum(x['disposition']=='explanatory' for x in clauses),'deferred_clauses':sum(x['disposition']=='deferred' for x in clauses),'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
    put('denominator.json',counts);print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False,'whole_translation':'pending'},indent=2,sort_keys=True))
if __name__=='__main__':main()
