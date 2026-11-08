"""Versioned directional question with closed ordered pairs and pair-specific rules."""
import hashlib,json,sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parents[1]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A04')]
import contracts as c
import ir
import resolver as r
import correspondence as co
SCOPE='scope:candidate:relation-kind-contract-v1'
SORTS=['Contract','Question','EndpointKind','QualifierRule','QualifierValue','VersionLabel']
FUNCTIONS={'versionLabel':(['Contract'],'VersionLabel'),'axisQuestion':(['Contract'],'Question'),
           'pairRule':(['Contract','EndpointKind','EndpointKind'],'QualifierRule')}
REQUIRED=['RelationKind','Versioned','SemanticAxisContract','GovernedIdentityOrRecord','BoundedScope','ClosedFinitePairDeclaration']
ROLES=['RelationInstanceRole','SpecializedBindingRole','OntologyEdgeRole','WildcardEndpointFamilyRole','InferredCartesianProductRole']
OUTCOMES=['AuthorityEffect','AdmittedInstance','RuntimeSucceeded','IdentityEquivalent','ExternalEffect']
UNARY=REQUIRED+ROLES+OUTCOMES
SIGNATURE={n:['Contract'] for n in UNARY}
SIGNATURE.update(DirectionalQuestion=['Question'],ExactEndpointKind=['EndpointKind'],Asks=['Contract','Question'],
                 DeclaredPair=['Contract','EndpointKind','EndpointKind'],AllowedPair=['Contract','EndpointKind','EndpointKind'],
                 HasPairRule=['Contract','EndpointKind','EndpointKind','QualifierRule'],RuleAccepts=['QualifierRule','QualifierValue'],
                 QualifierAllowed=['Contract','EndpointKind','EndpointKind','QualifierValue'])
def var(n):return {'op':'var','name':n}
def pred(n,*args):return {'op':'pred','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def fn(n,*args):return {'op':'fn','name':n,'args':[var(x) if isinstance(x,str) else x for x in args]}
def both(*args):return {'op':'and','args':list(args)}
def neg(a):return {'op':'not','arg':a}
def implies(a,z):return {'op':'implies','left':a,'right':z}
def iff(a,z):return {'op':'iff','left':a,'right':z}
def eq(a,z):return {'op':'eq','left':a,'right':z}
def quant(op,sort,name,body):return {'op':op,'sort':sort,'var':name,'body':body}
def every(body):return quant('forall','Contract','k',body)
def witness(body):return quant('exists','Contract','k',body)
def pairs(body):return quant('forall','EndpointKind','s',quant('forall','EndpointKind','t',body))
CORE=every(implies(pred('RelationKind','k'),both(pred('Versioned','k'),pred('SemanticAxisContract','k'),
     pred('DirectionalQuestion',fn('axisQuestion','k')),pred('Asks','k',fn('axisQuestion','k')))))
QUESTION_UNIQUE=every(quant('forall','Question','q',implies(both(pred('RelationKind','k'),pred('Asks','k','q')),eq(var('q'),fn('axisQuestion','k')))))
PAIR_CLOSURE=both(every(implies(pred('RelationKind','k'),pred('ClosedFinitePairDeclaration','k'))),
 every(pairs(implies(pred('RelationKind','k'),iff(pred('AllowedPair','k','s','t'),pred('DeclaredPair','k','s','t'))))),
 every(pairs(implies(both(pred('RelationKind','k'),pred('DeclaredPair','k','s','t')),both(pred('ExactEndpointKind','s'),pred('ExactEndpointKind','t'))))))
PAIR_RULES=both(every(pairs(implies(both(pred('RelationKind','k'),pred('DeclaredPair','k','s','t')),
                                   pred('HasPairRule','k','s','t',fn('pairRule','k','s','t'))))),
 every(pairs(quant('forall','QualifierRule','r',implies(both(pred('RelationKind','k'),pred('HasPairRule','k','s','t','r')),
                  both(pred('DeclaredPair','k','s','t'),eq(var('r'),fn('pairRule','k','s','t'))))))),
 every(pairs(quant('forall','QualifierValue','v',implies(both(pred('RelationKind','k'),pred('QualifierAllowed','k','s','t','v')),
                  both(pred('AllowedPair','k','s','t'),pred('RuleAccepts',fn('pairRule','k','s','t'),'v')))))))
GENUS=every(implies(pred('RelationKind','k'),both(pred('GovernedIdentityOrRecord','k'),pred('BoundedScope','k'))))
def contrast(name):return every(implies(pred('RelationKind','k'),neg(pred(name,'k'))))
def ref(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def put(n,value):
    with (UNIT/n).open('x') as out:json.dump(value,out,indent=2,sort_keys=True);out.write('\n')
    return ref(UNIT/n)
def snapshot():return json.loads((BASE/'current-snapshot.json').read_bytes())
def unchanged(refs):
    for x in refs:
        if ref(ROOT/x['path'])!=x:raise ValueError('Changed selected input: '+x['path'])
def source_ref(snap,id):
    row=next(x for x in snap['current_entries'] if x['definition_id']==id)
    return {k:row[k] for k in ['definition_id','version_ref','path','sha256']}
def main():
    context=json.loads((UNIT/'context.json').read_bytes());unchanged(context['sources']);snap=snapshot();r.verify(snap,ROOT)
    source=source_ref(snap,'cal.definition.relation-kind');doc=co.source_document(snap,source);units=co.inventory(doc);texts=dict(co.string_leaves(doc))
    N='/voices/scientific_formal/normative_statement';F='/voices/scientific_formal/formal_expression';B='/voices/scientific_formal/boundary_conditions/0'
    bound={'/boundaries/0','/scope/exclusions/0','/voices/scientific_formal/boundary_conditions/1'}
    markers=['specialized binding','Ontology edge','wildcard endpoint family','nor inferred Cartesian product']
    clauses=[];links=[]
    for u in units:
        sel=u['selector'];text=texts[sel];offsets=[0]
        if sel in [N,B]:offsets += [text.index('through a finite'),text.index('and pair-specific')]
        if sel==N:offsets += [text.index('It is neither'),*[text.index(x) for x in markers]]
        elif sel in bound:offsets += [text.index(x) for x in markers]
        elif sel==F:offsets += [text.index('; ')+2]
        offsets.append(len(text))
        if offsets!=sorted(set(offsets)):raise ValueError('Unordered source span split')
        for start,end in zip(offsets,offsets[1:]):
            excerpt=text[start:end];formula=None;disposition='deferred';roles=['proof-obligation'];forms=['non-definitional']
            rationale='Actual finiteness, semantic question distinctness, exact endpoint carrier/qualifier contracts, source use/admission or effect bindings remain reviewed obligations; no theorem is assumed.'
            if sel in [N,B] and excerpt.startswith('A Relation Kind'):
                formula=both(CORE,QUESTION_UNIQUE);rationale='Versioned axis with exactly one selected directional question per Kind contract. No global injectivity across successor versions or semantic orthogonality from question strings.'
            elif sel in [N,B] and excerpt.startswith('through a finite'):
                formula=PAIR_CLOSURE;rationale='Allowed pairs equal this Kind declaration and use exact endpoint-kind statuses. ClosedFinitePairDeclaration is a primitive status, not an unbounded finiteness theorem. Summaries never generate a Cartesian product.'
            elif sel in [N,B] and excerpt.startswith('and pair-specific'):
                formula=PAIR_RULES;rationale='Each declared ordered pair has its selected rule; rule association is unique for that pair, and declared qualifier acceptance must satisfy that rule. Rules may be shared; no accepted qualifier or actual execution is invented.'
            elif sel in bound or sel==N and start>=text.index('It is neither'):
                index=0 if excerpt.startswith('It is neither') else next(i+1 for i,m in enumerate(markers) if excerpt.startswith(m))
                formula=contrast(ROLES[index]);rationale='Same-local-role contrast, without universal claims about external referenced objects or canonical type alignment.'
            elif sel==F and start==0:
                formula=GENUS;rationale='The explicit necessary governed-record and bounded-scope expression is not a complete membership biconditional.'
            elif sel.startswith('/voices/plain_language/') or sel.startswith('/voices/domain_context/') or sel.startswith('/voices/scientific_formal/notation/'):
                disposition='explanatory';roles=['explanation-example'];forms=['non-definitional'];rationale='Intuition, member-of example and notation retained without creating an actual Kind, instance, authority or accepted assumption.'
            if formula is not None:disposition='encoded';roles=['definition'];forms=['axiomatic-implicit']
            cid='RKI-'+str(len(clauses)+1).zfill(3)
            clauses.append({'clause_id':cid,'source_selector':sel,'excerpt_sha256':hashlib.sha256(excerpt.encode()).hexdigest(),'start_character':start,
                            'disposition':disposition,'forms':forms,'roles':roles,'formal_statement':formula,'rationale':rationale})
            links.append({'unit_id':u['unit_id'],'clause_id':cid,'end_character':end,'excerpt':excerpt})
    def clause(sel):return next(x['clause_id'] for x in clauses if x['source_selector']==sel)
    uses=[('cal.definition.governed-model',F,'Governed-record and bounded-scope predicates need reviewed common meanings.'),
          ('cal.definition.typed-relation',N,'Relation Kind contract and independently identified relation instance remain distinct; actual connection binding requires exact Kind version/pair/rules.'),
          ('cal.definition.artifact-type',N,'Exact endpoint kinds and carriers need artifact-type identity/version mapping rather than wildcard names.'),
          ('cal.definition.ontology-edge','/boundaries/0','A Kind is distinct from an ontology-local or global projected edge.'),
          ('cal.definition.authority',F,'A semantic question or allowed pair does not grant authority.'),
          ('cal.definition.definition','/voices/scientific_formal/testable_conditions/0','Every use must select this Definition or an admitted successor; source admission does not create a Kind instance.')]
    deps=[source_ref(snap,id) for id,_,_ in uses];dl=[{'clause_id':clause(sel),'dependency_ref':dep,'kind':'semantic-use','rationale':why} for (_,sel,why),dep in zip(uses,deps)]
    declarations=[{'kind':'sort','symbol_id':n,'scope':SCOPE,'domain_policy':'nonempty'} for n in SORTS]+[{'kind':'total-function','symbol_id':n,'scope':SCOPE,'argument_sorts':args,'result_sort':result,'definedness_policy':None} for n,(args,result) in FUNCTIONS.items()]+[{'kind':'predicate' if len(args)==1 else 'relation','symbol_id':n,'scope':SCOPE,'argument_sorts':args} for n,args in SIGNATURE.items()]
    populations=[]
    for n in UNARY:
        req=n in REQUIRED
        populations.append({'population_id':'POP-'+n,'carrier':'Contract','predicate_ref':n,'requirement':'required' if req else 'unresolved','statement':witness(both(pred('RelationKind','k'),pred(n,'k'))) if req else None,
                            'scope':SCOPE,'rationale':'One hypothetical Kind prevents vacuity.' if req else 'Actual role/authority/outcome populations require owner-reviewed existence or exemption; none is invented.','review_ref':None})
    for n in ['DirectionalQuestion','Asks','DeclaredPair','AllowedPair','HasPairRule','RuleAccepts','QualifierAllowed','ExactEndpointKind']:
        req=n in ['DirectionalQuestion','Asks'];body=pred('DirectionalQuestion',fn('axisQuestion','k')) if n=='DirectionalQuestion' else pred('Asks','k',fn('axisQuestion','k'))
        populations.append({'population_id':'POP-'+n,'carrier':'Contract','predicate_ref':None,'requirement':'required' if req else 'unresolved','statement':witness(both(pred('RelationKind','k'),body)) if req else None,
                            'scope':SCOPE,'rationale':'A question belongs to the same hypothetical Kind.' if req else 'Empty finite pair declarations/rule/value populations need explicit policy; no connection or accepted qualifier witness is required automatically.','review_ref':None})
    core={'interpretation_id':'interpretation:relation-kind-contract-v1','source':source,'scope':SCOPE,'declarations':declarations,'clauses':clauses,'depends_on':deps,'relations':[],
          'assumptions':[],'populations':populations,'logic_features':['first-order','equality'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:closed-ordered-kind-contract-candidate'}
    descriptions=[('RKI-QUESTION-001','Question identity per Kind is not semantic uniqueness/orthogonality or injectivity across Kind successors.'),('RKI-FINITE-002','Primitive closed-finite status and a bounded inspector do not prove unbounded finiteness; empty pair existence policy remains unresolved.'),('RKI-ENDPOINT-003','Exact ordered endpoint kinds require current carrier/version mapping; marginal source/target lists do not generate pair authority.'),('RKI-QUALIFIER-004','Pair-specific rule association permits shared rules but needs actual typed payload, value and cross-qualifier contracts; actual carrier defaults require embedding review.'),('RKI-ROLES-005','Kind, relation instance, specialized binding and ontology edge need common-carrier alignment; private contrast tags do not settle the canonical distinctions.'),('RKI-ADMISSION-006','Current CAL0065 Definition admission and selected Kind admission postimages differ from historical embedded candidate posture; none admits this interpretation or a connection instance.')]
    findings=[{'finding_id':id,'selectors':[N,F],'description':text,'status':'unresolved','owner_route':'role:definition-owner with Kind/carrier/qualifier/governance owners must review exact mappings and contracts.'} for id,text in descriptions]
    encoded=[x['clause_id'] for x in clauses if x['disposition']=='encoded']
    packet={'schema_version':'definition-assurance-correspondence/v1-candidate','authority_effect':'none','upstream_schema_sha256':r.digest((IMPL/'schemas/input-envelope.json').read_bytes()),'source_selection':'current',
            'inventory_policy':'all-nonempty-string-leaves-in-voices-boundaries-scope-and-claim-ceiling/v1','interpretation':core,'source_units':units,'correspondence':links,'dependency_links':dl,
            'dependency_closure':{'status':'unresolved','review_ref':None,'unresolved_notes':['Six authored uses require independent dependency completeness and carrier mapping review.','Finite/unique/closed declaration statuses do not supply missing proof, policy or live admission.']},'assumption_links':[],
            'source_precedence':{'normative_voice':'/voices/scientific_formal','conflicts':findings,'review_ref':None},
            'review_packet':{'instances':[{'case_id':'closed-membership-axis','scenario':'A Kind asks which governed container a member belongs to and explicitly permits capability->product and work->project, with rules bound to each pair.','expected_interpretation':'Exact declared pairs are allowed; cross-product capability->project is not inferred.','rationale':'One direction and closed pair enumeration are different from endpoint summaries.','related_clause_ids':encoded}],
                             'counterexamples':[{'case_id':'wildcard-cartesian-shortcut','scenario':'A consumer expands the marginal source/target sets to every combination and reuses a role from another pair.','expected_interpretation':'Undeclared pairs and wrong pair rules fail selected conditions.','rationale':'Meaning must not widen through wildcard or shared-list convenience.','related_clause_ids':encoded}],
                             'known_losses':['No semantic orthogonality or global uniqueness proof.','No unbounded finiteness theorem or owner-approved empty-pair population policy.','No reviewed source-carrier embedding or endpoint identity resolution.','No authority, lifecycle, connection admission or runtime effect from Kind meaning.'],'review_status':'pending','review_ref':None}}
    account=co.check(packet,snap,required_dependencies=[x['version_ref'] for x in deps],required_conflicts=[x['finding_id'] for x in findings])
    if not account.get('character_accounting_complete'):raise ValueError(json.dumps(account))
    typed=ir.compile_interpretation(core,snap);ir.verify_ir(typed)
    queries=[{'query_id':'Kind-not-'+n,'target':every(implies(pred('RelationKind','k'),pred(n,'k'))),'witness_condition':witness(both(pred('RelationKind','k'),neg(pred(n,'k')))),'selected_in_T':False} for n in OUTCOMES]
    queries.append({'query_id':'forward-pair-not-reverse','target':every(pairs(implies(both(pred('RelationKind','k'),pred('AllowedPair','k','s','t')),pred('AllowedPair','k','t','s')))),
                    'witness_condition':witness(quant('exists','EndpointKind','s',quant('exists','EndpointKind','t',both(pred('AllowedPair','k','s','t'),neg(pred('AllowedPair','k','t','s')))))),'selected_in_T':False})
    marginal=both(quant('exists','EndpointKind','a',pred('DeclaredPair','k','s','a')),quant('exists','EndpointKind','z',pred('DeclaredPair','k','z','t')))
    queries.append({'query_id':'marginal-lists-not-cartesian-authority','target':every(pairs(implies(both(pred('RelationKind','k'),marginal),pred('AllowedPair','k','s','t')))),
                    'witness_condition':witness(quant('exists','EndpointKind','s',quant('exists','EndpointKind','t',both(marginal,neg(pred('AllowedPair','k','s','t')))))),'selected_in_T':False})
    queries.append({'query_id':'question-not-injective-across-kind-versions','target':every(quant('forall','Contract','j',implies(both(pred('RelationKind','k'),pred('RelationKind','j'),eq(fn('axisQuestion','k'),fn('axisQuestion','j'))),eq(var('k'),var('j'))))),
                    'witness_condition':witness(quant('exists','Contract','j',both(pred('RelationKind','j'),eq(fn('axisQuestion','k'),fn('axisQuestion','j')),neg(eq(var('k'),var('j')))))),'selected_in_T':False,'model_case':'successor-same-question'})
    queries.append({'query_id':'allowed-pair-not-accepted-qualifier-inhabitant','target':every(pairs(implies(both(pred('RelationKind','k'),pred('AllowedPair','k','s','t')),quant('exists','QualifierValue','v',pred('QualifierAllowed','k','s','t','v'))))),
                    'witness_condition':witness(quant('exists','EndpointKind','s',quant('exists','EndpointKind','t',both(pred('AllowedPair','k','s','t'),neg(quant('exists','QualifierValue','v',pred('QualifierAllowed','k','s','t','v'))))))),'selected_in_T':False,'model_case':'no-accepted-qualifiers'})
    counts={'source_units':len(units),'mapped_clauses':len(clauses),**{n+'_clauses':sum(x['disposition']==n for x in clauses) for n in ['encoded','explanatory','deferred']},'declarations':len(declarations),'required_populations':sum(x['requirement']=='required' for x in populations),'unresolved_populations':sum(x['requirement']=='unresolved' for x in populations),'direct_semantic_uses':len(deps),'countermodel_queries':len(queries)}
    for name,value in [('t.json',{'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core}),('correspondence.json',packet),('static-ir.json',typed),('correspondence-check.json',account),('clause-analysis.json',{'authority_effect':'none','source':source,'clauses':clauses,'findings':findings,'whole_definition_translation':'pending'}),('query-policy.json',{'authority_effect':'none','queries':queries,'selected_in_T':False}),('denominator.json',counts)]:put(name,value)
    print(json.dumps({'result':'candidate-authored-and-typed',**counts,'semantic_ready':False},indent=2,sort_keys=True))
if __name__=='__main__':main()
