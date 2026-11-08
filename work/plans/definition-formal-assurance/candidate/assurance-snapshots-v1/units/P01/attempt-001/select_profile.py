"""Candidate routing policy: exact typed inputs first, capabilities second."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path.insert(0,str(IMPL))
import ir
import resolver as r
import contracts as c

MINIMUMS={'model-local-check':'model-local-value','consistency':'model-witness','joint-inhabitation':'model-witness','permitted-distinction':'model-witness','forbidden-implication-countermodel':'model-witness','bounded-property':'bounded-exhaustion','universal-property':'mechanized-theorem','conservativity':'mechanized-theorem'}
ROUTES={'model-local-check':'static-model-evaluator','consistency':'generic-finite','joint-inhabitation':'generic-finite','permitted-distinction':'generic-finite','forbidden-implication-countermodel':'generic-finite','bounded-property':'generic-finite','universal-property':'proof-kernel','conservativity':'proof-kernel'}
STATIC={'propositional','first-order','finite-cardinality','equality'}


class SelectionFault(ValueError):
    def __init__(self,code):self.code=code


def binding(path):
    path=Path(path).resolve()
    return {'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def validate_policy(policy):
    if not isinstance(policy,dict) or set(policy)!={'schema_version','authority_effect','logic','minimum_strengths','routes','budgets','install_policy','inventory_ref','claim_ceiling'}:raise SelectionFault('malformed-policy')
    if policy['schema_version']!='definition-assurance-provider-selection/v1-candidate' or policy['authority_effect']!='none':raise SelectionFault('wrong-policy-kind')
    if not r.same_json(policy['minimum_strengths'],MINIMUMS) or set(policy['logic']['supported_core'])!=STATIC:raise SelectionFault('changed-required-strength-or-logic')
    if set(policy['routes'])!={'static-model-evaluator','generic-finite','smt-projection','proof-kernel'}:raise SelectionFault('missing-or-extra-route')
    if policy['routes']['static-model-evaluator']['strengths']!=['model-local-value'] or policy['routes']['generic-finite']['strengths']!=['model-witness','bounded-exhaustion'] or policy['routes']['smt-projection']['strengths']!=['model-witness','solver-evidence'] or policy['routes']['proof-kernel']['strengths']!=['mechanized-theorem']:raise SelectionFault('invalid-route-strengths')
    for name,route in policy['routes'].items():
        if set(route)!={'logic_features','strengths','implementation_unit','required_runtime','claim_ceiling'} or set(route['logic_features'])!=STATIC:raise SelectionFault('invalid-route-contract')
        if not isinstance(route['implementation_unit'],str) or not isinstance(route['required_runtime'],str):raise SelectionFault('invalid-route-runtime')
    budgets=policy['budgets']
    if set(budgets)!={'timeout_seconds','max_interpretations','max_evaluation_steps','max_function_tuple_space','max_output_bytes','max_domain_cardinality','execution_policy'}:raise SelectionFault('invalid-budget-contract')
    for key in set(budgets)-{'execution_policy'}:
        if type(budgets[key]) is not int or budgets[key]<1:raise SelectionFault('invalid-positive-budget')
    if budgets['execution_policy']!='declared-for-later-adapters; not proof of current enforcement' or policy['install_policy']!='no-installs-in-P01; future isolated exact-runtime task required':raise SelectionFault('changed-execution-or-install-boundary')
    return policy


def load_policy(path=None):
    path=IMPL/'profiles/selection.json' if path is None else Path(path)
    return validate_policy(r.parse(path.read_bytes(),str(path)))


def verify_inventory(inventory,live=True):
    if not isinstance(inventory,dict) or inventory.get('schema_version')!='definition-assurance-tooling-assessment/v1-candidate' or inventory.get('authority_effect')!='none':raise SelectionFault('malformed-runtime-inventory')
    if set(inventory.get('routes',{}))!=set(ROUTES.values())|{'smt-projection'}:raise SelectionFault('incomplete-runtime-routes')
    for name,route in inventory['routes'].items():
        if set(route)!={'runtime_available','adapter_available','lowering_status','runtime_bindings','adapter_bindings','discovery_scope','diagnostics'}:raise SelectionFault('malformed-runtime-route')
        if type(route['runtime_available']) is not bool or type(route['adapter_available']) is not bool:raise SelectionFault('runtime-availability-must-be-boolean')
        if route['lowering_status'] not in {'implemented-static','pending-exact-lowering'}:raise SelectionFault('invalid-lowering-state')
        if route['runtime_available'] and not route['runtime_bindings']:raise SelectionFault('unbound-available-runtime')
        if route['adapter_available'] and not route['adapter_bindings']:raise SelectionFault('unbound-available-adapter')
        for row in route['runtime_bindings']+route['adapter_bindings']:
            if not isinstance(row,dict) or set(row)!={'path','sha256'} or not isinstance(row['path'],str) or not isinstance(row['sha256'],str) or len(row['sha256'])!=64:raise SelectionFault('malformed-runtime-binding')
            path=Path(row['path']);path=path if path.is_absolute() else ROOT/path
            if live:
                try:actual=hashlib.sha256(path.read_bytes()).hexdigest()
                except OSError:raise SelectionFault('missing-bound-runtime-or-adapter')
                if actual!=row['sha256']:raise SelectionFault('stale-runtime-or-adapter')
    return inventory


def select(core,request,policy,inventory,preferred_route=None,live=True):
    validate_policy(policy)
    c.bounded_tree(request)
    if not isinstance(request,dict) or set(request)!={'obligation_id','query_type','statement','minimum_strength','domain_scope'}:raise SelectionFault('malformed-selection-request')
    query=request['query_type']
    if not isinstance(query,str) or query not in MINIMUMS or not isinstance(request['obligation_id'],str) or not request['obligation_id']:raise SelectionFault('unsupported-obligation-kind')
    required=MINIMUMS[query]
    base={'authority_effect':'none','semantic_ready':False,'obligation_id':request['obligation_id'],'query_type':query,'required_strength':required,'policy_sha256':ir.digest(policy),'request_sha256':ir.digest(request),'source_fidelity':'not-established-by-routing'}
    # The exact interpretation, declaration kinds and AST must be supported.
    # A feature label alone never grants a route.
    try:
        subject=ir.compile_interpretation(core)
        sorts={row['symbol_id']:row['symbol_id'] for row in subject['declarations'] if row['kind']=='sort'}
        symbols={row['symbol_id']:row for row in subject['declarations'] if row['kind']!='sort'}
        statement=ir.formula(request['statement'],sorts,symbols)
    except ir.Unsupported as error:return {**base,'status':'unsupported-logic','diagnostics':[{'code':error.code,'path':error.path}],'selected_route':None}
    except (ir.IRFault,c.InputError) as error:return {**base,'status':'malformed-typed-input','diagnostics':[{'code':error.code,'path':error.path}],'selected_route':None}
    features={'propositional'}
    if any(row['kind'] in {'constant','total-function'} or row.get('argument_sorts') for row in subject['declarations']):features.add('first-order')
    pending=[statement,subject['clauses'],subject['assumptions'],subject['populations']]
    while pending:
        node=pending.pop()
        if isinstance(node,list):pending.extend(node)
        elif isinstance(node,dict):
            if node.get('op') in {'forall','exists'}:features.add('first-order')
            if node.get('op')=='eq':features.add('equality')
            pending.extend(node.values())
    base.update(input_ir_sha256=subject['ir_sha256'],statement_sha256=ir.digest(statement),derived_logic_features=sorted(features),declared_logic_features=core['logic_features'])
    if request['minimum_strength']!=required:return {**base,'status':'required-strength-mismatch','selected_route':None,'diagnostics':[{'code':'fixed-obligation-strength-cannot-be-weakened-or-substituted'}]}
    scope=request['domain_scope']
    if not isinstance(scope,dict) or set(scope)!={'kind','cardinalities'} or scope['kind'] not in {'finite-exact','general-static'}:raise SelectionFault('malformed-domain-scope')
    if scope['kind']=='finite-exact':
        if not isinstance(scope['cardinalities'],dict) or set(scope['cardinalities'])!=set(sorts) or any(type(size) is not int or size<1 or size>policy['budgets']['max_domain_cardinality'] for size in scope['cardinalities'].values()):raise SelectionFault('invalid-finite-domain-scope')
    elif scope['cardinalities'] is not None:raise SelectionFault('general-scope-has-finite-cardinalities')
    if query in {'model-local-check','bounded-property'} and scope['kind']!='finite-exact':return {**base,'status':'unsupported-domain-scope','selected_route':None,'diagnostics':[{'code':'exact-finite-scope-required'}]}
    name=ROUTES[query] if preferred_route is None else preferred_route
    if name not in policy['routes']:raise SelectionFault('unknown-route')
    route=policy['routes'][name]
    if required not in route['strengths']:return {**base,'status':'weaker-than-required-evidence','selected_route':None,'considered_route':name,'diagnostics':[{'code':'route-cannot-establish-required-proposition-strength'}]}
    inventory_ref=policy['inventory_ref']
    if not isinstance(inventory_ref,dict) or set(inventory_ref)!={'path','sha256'}:raise SelectionFault('malformed-inventory-binding')
    if inventory_ref['path']!='docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/tooling-assessment.json':raise SelectionFault('wrong-selected-inventory-path')
    if live:
        raw=(ROOT/inventory_ref['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=inventory_ref['sha256'] or not r.same_json(r.parse(raw,inventory_ref['path']),inventory):raise SelectionFault('inventory-selection-or-byte-binding-mismatch')
    verify_inventory(inventory,live)
    runtime=inventory['routes'][name]
    base.update(selected_route=name,inventory_sha256=ir.digest(inventory),domain_scope=scope,budgets=policy['budgets'],claim_ceiling=route['claim_ceiling'])
    if not runtime['runtime_available']:status='missing-runtime'
    elif not runtime['adapter_available']:status='pending-provider-implementation'
    elif runtime['lowering_status']!='implemented-static':status='pending-exact-lowering'
    else:status='ready-for-candidate-provider-execution'
    return {**base,'status':status,'diagnostics':runtime['diagnostics'],'runtime_bindings':runtime['runtime_bindings'],'adapter_bindings':runtime['adapter_bindings']}
