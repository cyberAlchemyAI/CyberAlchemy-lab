"""Independent required-set and finite-witness checks, with explicit trust limits."""
import copy
from itertools import product
from math import prod
from pathlib import Path
from time import monotonic
import contracts as c
import resolver as r
import ir
import obligations as o
import bundles as b
from providers import finite as f

MAX_BYTES=32_000_000
MAX_STEPS=100_000
MAX_TUPLES=100_000
TIMEOUT=30


class VerificationFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


def exact(value,keys,code):
    if not isinstance(value,dict) or set(value)!=set(keys):raise VerificationFault(code)


class Denotation:
    """Separate structure validation and satisfaction; no provider evaluator calls."""
    def __init__(self,declarations,model,max_steps=MAX_STEPS,cancelled=None):
        c.bounded_tree(model)
        if type(max_steps) is not int or not 1<=max_steps<=MAX_STEPS:raise VerificationFault('invalid-verifier-step-budget')
        self.steps=0;self.max_steps=max_steps;self.cancelled=cancelled;self.deadline=monotonic()+TIMEOUT
        exact(model,['domains','constants','functions','predicates'],'incomplete-model')
        self.model=model;self.functions={};self.predicates={}
        if any(not isinstance(value,dict) for value in model.values()):raise VerificationFault('malformed-model-table')
        signature={};expected={key:set() for key in model}
        for row in declarations:
            identity=row['symbol_id'];kind=row['kind']
            if identity in signature:raise VerificationFault('duplicate-model-signature')
            signature[identity]=row;bucket={'sort':'domains','constant':'constants','total-function':'functions','predicate':'predicates','relation':'predicates'}.get(kind)
            if bucket is None:raise VerificationFault('unsupported-model-signature')
            expected[bucket].add(identity)
        if any(set(model[key])!=values for key,values in expected.items()):raise VerificationFault('model-signature-denominator-mismatch')
        for values in model['domains'].values():
            self.tick()
            if not isinstance(values,list) or not values or any(not isinstance(value,str) or not value for value in values) or len(set(values))!=len(values):raise VerificationFault('empty-or-malformed-domain')
        def tuple_value(values,sorts):
            if not isinstance(values,list) or len(values)!=len(sorts) or any(not isinstance(value,str) or value not in model['domains'][sort] for value,sort in zip(values,sorts)):raise VerificationFault('ill-sorted-model-tuple')
            return tuple(values)
        for identity,value in model['constants'].items():
            self.tick()
            if not isinstance(value,str) or value not in model['domains'][signature[identity]['result_sort']]:raise VerificationFault('ill-sorted-constant')
        for identity,rows in model['functions'].items():
            sorts=signature[identity]['argument_sorts'];count=prod(len(model['domains'][sort]) for sort in sorts)
            if count>MAX_TUPLES:raise VerificationFault('verifier-tuple-limit')
            if not isinstance(rows,list):raise VerificationFault('malformed-function-table')
            table={}
            for row in rows:
                self.tick();exact(row,['args','value'],'malformed-function-row');args=tuple_value(row['args'],sorts)
                if args in table:raise VerificationFault('duplicate-function-tuple')
                if not isinstance(row['value'],str) or row['value'] not in model['domains'][signature[identity]['result_sort']]:raise VerificationFault('ill-sorted-function-result')
                table[args]=row['value']
            # Independently enumerate the domain product, rather than trusting row count.
            for args in product(*(model['domains'][sort] for sort in sorts)):
                self.tick()
                if args not in table:raise VerificationFault('nontotal-function')
            self.functions[identity]=table
        for identity,rows in model['predicates'].items():
            if not isinstance(rows,list) or len(rows)>MAX_TUPLES:raise VerificationFault('malformed-or-oversized-extension')
            tuples=set()
            for row in rows:
                self.tick();values=tuple_value(row,signature[identity]['argument_sorts'])
                if values in tuples:raise VerificationFault('duplicate-predicate-tuple')
                tuples.add(values)
            self.predicates[identity]=tuples

    def tick(self):
        if self.cancelled is not None and self.cancelled():raise VerificationFault('cancelled')
        if monotonic()>=self.deadline:raise VerificationFault('verifier-timeout')
        if self.steps>=self.max_steps:raise VerificationFault('verifier-step-limit')
        self.steps+=1

    def term(self,node,environment):
        self.tick();op=node['op']
        if op=='var':return environment[node['name']]
        if op=='const':return self.model['constants'][node['name']]
        if op=='fn':return self.functions[node['name']][tuple(self.term(arg,environment) for arg in node['args'])]
        raise VerificationFault('unsupported-term')

    def truth(self,node,environment=None):
        self.tick();environment={} if environment is None else environment;op=node['op']
        if op=='pred':return tuple(self.term(arg,environment) for arg in node['args']) in self.predicates[node['name']]
        if op=='eq':return self.term(node['left'],environment)==self.term(node['right'],environment)
        if op=='not':return self.truth(node['arg'],environment) is False
        if op in {'and','or'}:
            # Explicit folds give the empty connective its mathematical identity.
            for arg in node['args']:
                value=self.truth(arg,environment)
                if op=='and' and value is False:return False
                if op=='or' and value is True:return True
            return op=='and'
        if op in {'implies','iff'}:
            left=self.truth(node['left'],environment);right=self.truth(node['right'],environment)
            return (left is False or right is True) if op=='implies' else left==right
        if op in {'forall','exists'}:
            for value in self.model['domains'][node['sort']]:
                next_environment=dict(environment);next_environment[node['var']]=value
                holds=self.truth(node['body'],next_environment)
                if op=='forall' and holds is False:return False
                if op=='exists' and holds is True:return True
            return op=='forall'
        raise VerificationFault('unsupported-formula')


def witness(subject,native,T,I,Q,cardinalities,mode,expected_bindings,selected_inputs=None,alignments=(),root=None,max_steps=MAX_STEPS,cancelled=None):
    """Check a supplied complete model; do not trust search counts or exhaustion."""
    c.bounded_tree(native)
    if subject.get('schema_version')=='definition-assurance-static-ir/v1-candidate':ir.verify_ir(subject)
    elif subject.get('schema_version')=='definition-assurance-composed-ir/v1-candidate':
        if selected_inputs is None:raise VerificationFault('missing-selected-composition')
        ir.verify_composed(subject,selected_inputs,alignments,root)
    else:raise VerificationFault('unsupported-witness-subject')
    declarations=subject['declarations'];sorts={row['symbol_id']:row['symbol_id'] for row in declarations if row['kind']=='sort'};symbols={row['symbol_id']:row for row in declarations if row['kind']!='sort'}
    if not isinstance(T,list) or not isinstance(I,list):raise VerificationFault('formula-lists-required')
    for value in [T,I,Q,cardinalities]:c.bounded_tree(value)
    T=[ir.formula(node,sorts,symbols) for node in T];I=[ir.formula(node,sorts,symbols) for node in I];Q=ir.formula(Q,sorts,symbols)
    if not isinstance(cardinalities,dict) or set(cardinalities)!=set(sorts) or any(type(value) is not int or not 1<=value<=3 for value in cardinalities.values()):raise VerificationFault('invalid-witness-cardinalities')
    status=native.get('status')
    if status not in {'witness-found','countermodel-found'}:raise VerificationFault('no-checkable-model-witness')
    if mode not in {'witness','countermodel','bounded-validity'} or native.get('mode')!=mode or (status=='witness-found')!=(mode=='witness'):raise VerificationFault('witness-mode-substitution')
    if native.get('schema_version')!='definition-assurance-finite-result/v1-candidate' or native.get('authority_effect')!='none' or native.get('semantic_ready') is not False or native.get('unbounded_conclusion') is not None or native.get('exhaustion_complete') is not False or native.get('evidence_strength')!='model-witness':raise VerificationFault('invalid-witness-claim-boundary')
    if native.get('policy_sha256')!=f.POLICY_SHA256:raise VerificationFault('native-policy-substitution')
    if not r.same_json(native.get('implementation_bindings'),expected_bindings):raise VerificationFault('provider-build-substitution')
    expected={'subject_ir_sha256':subject['ir_sha256'],'theory_sha256':ir.digest(T),'populations_sha256':ir.digest(I),'query_sha256':ir.digest(Q),'cardinalities_sha256':ir.digest(cardinalities),'composition_input_ir_sha256':[value['ir_sha256'] for value in selected_inputs] if selected_inputs is not None else None,'selected_alignment_refs_sha256':ir.digest(list(alignments))}
    actual=native.get('input_bindings')
    if not isinstance(actual,dict) or not set(expected).issubset(actual) or set(actual)-set(expected)-{'snapshot_sha256'} or any(not r.same_json(actual.get(key),value) for key,value in expected.items()):raise VerificationFault('witness-input-substitution')
    record=native.get('witness');exact(record,['model','model_sha256','query_truth','interpretation_rank_zero_based'],'malformed-witness')
    if type(record['interpretation_rank_zero_based']) is not int or record['interpretation_rank_zero_based']<0:raise VerificationFault('invalid-witness-rank')
    model=record['model']
    evaluator=Denotation(declarations,model,max_steps,cancelled)
    if ir.digest(model)!=record['model_sha256'] or any(len(model['domains'][key])!=value for key,value in cardinalities.items()):raise VerificationFault('witness-model-binding-mismatch')
    if not all(evaluator.truth(node) for node in T):raise VerificationFault('witness-fails-theory')
    if not all(evaluator.truth(node) for node in I):raise VerificationFault('witness-fails-population')
    truth=evaluator.truth(Q)
    if type(record['query_truth']) is not bool or truth!=record['query_truth'] or truth!=(status=='witness-found'):raise VerificationFault('witness-fails-query')
    return {'status':'checked-model-witness','query_truth':truth,'model_sha256':record['model_sha256'],'strength':'model-witness','steps':evaluator.steps,'mechanized_proof':False,'semantic_ready':False,'authority_effect':'none'}


def renamed(node,mapping):
    if isinstance(node,list):return [renamed(value,mapping) for value in node]
    if not isinstance(node,dict):return node
    result={key:renamed(value,mapping) for key,value in node.items()}
    if node.get('op') in {'const','fn','pred'}:result['name']=mapping[node['name']]
    if node.get('op') in {'forall','exists'}:result['sort']=mapping[node['sort']]
    return result


def signature_map(theory,subject,inputs,renaming,endpoints):
    """Explicit source-qualified nominal translation, including selected sort unions."""
    if not isinstance(renaming,list):raise VerificationFault('missing-nominal-renaming')
    originals=inputs if inputs is not None else [subject]
    origins={row['canonical_id']:row for item in originals for row in item['origins']}
    mapping={};selected={row['symbol_id']:row for row in subject['declarations']}
    for row in renaming:
        exact(row,['local_symbol_id','canonical_id','source'],'malformed-nominal-renaming');local=row['local_symbol_id'];canonical=row['canonical_id']
        if local in mapping or not any(r.same_json(row['source'],source) for source in theory['sources']):raise VerificationFault('nominal-source-or-identity-substitution')
        origin=origins.get(ir.qualified(row['source'],theory['scope'],local))
        aligned=subject.get('sort_alignment',{}).get(origin['canonical_id'],origin['canonical_id']) if origin else None
        if aligned!=canonical:raise VerificationFault('nominal-source-or-identity-substitution')
        mapping[local]=canonical
    if set(mapping)!={row['symbol_id'] for row in theory['declarations']} or set(mapping.values())!=set(selected) or len(set(mapping.values()))!=len(mapping):raise VerificationFault('nominal-signature-denominator-mismatch')
    for declaration in theory['declarations']:
        expected=copy.deepcopy(declaration);expected['symbol_id']=mapping[declaration['symbol_id']]
        for key in ['argument_sorts','result_sort']:
            if key in expected:expected[key]=[mapping[value] for value in expected[key]] if key=='argument_sorts' else mapping[expected[key]]
        observed=copy.deepcopy(selected[expected['symbol_id']]);expected.pop('scope',None);observed.pop('scope',None)
        if not r.same_json(expected,observed):raise VerificationFault('translated-signature-substitution')
    by_local={row['local_symbol_id']:row for row in renaming}
    for endpoint in endpoints.values():
        if not r.same_json(by_local[endpoint['predicate']]['source'],endpoint['source']):raise VerificationFault('nominal-endpoint-source-substitution')
    return mapping


def verify(root,bundle_ref,selection_ref,live_source_root=None,cancelled=None):
    """Externally selected byte references define inputs before submitted rows."""
    loaded={};size=0
    def load(ref):
        nonlocal size
        exact(ref,['path','sha256'],'malformed-selection-reference');raw=r.read_bytes(root,ref['path'])
        if r.digest(raw)!=ref['sha256']:raise VerificationFault('stale-independent-input',ref['path'])
        if ref['path'] in loaded and loaded[ref['path']]!=raw:raise VerificationFault('selection-read-race')
        if ref['path'] not in loaded:size+=len(raw)
        if size>MAX_BYTES:raise VerificationFault('verifier-input-byte-limit')
        loaded[ref['path']]=raw;return r.parse(raw,ref['path'])
    base={'authority_effect':'none','semantic_ready':False,'mechanized_proof':False,'owner_fidelity':'not-accepted','semantic_closure':'not-established'}
    try:
        root=r.resolve_root(root);selection=load(selection_ref)
        exact(selection,['schema_version','authority_effect','theory_ref','relation_requests_ref','populations_ref','endpoint_bindings_ref','snapshot_ref','assumption_set_ref','dependency_graph_ref','coupling_refs','finite_requests_ref','expected_contract','expected_provider_bindings_ref'],'malformed-independent-selection')
        if selection['schema_version']!='definition-assurance-verification-selection/v1-candidate' or selection['authority_effect']!='none':raise VerificationFault('invalid-selection-boundary')
        theory=load(selection['theory_ref']);requests=load(selection['relation_requests_ref']);populations=load(selection['populations_ref']);endpoints=load(selection['endpoint_bindings_ref'])
        for key in ['snapshot_ref','assumption_set_ref','dependency_graph_ref']:load(selection[key])
        for ref in selection['coupling_refs']:load(ref)
        expected=o.generate(theory,requests,populations,endpoints,root)
        # The selection of dependency bytes is independent. Semantic completeness remains a separate gate.
        expected_couplings=sorted([row['relation']['alignment']['map_ref'] for row in requests],key=lambda ref:ref['path'])
        if not r.same_json(sorted(selection['coupling_refs'],key=lambda ref:ref['path']),expected_couplings):raise VerificationFault('selected-coupling-denominator-mismatch')
        contract=b.checked_contract()
        if not r.same_json(selection['expected_contract'],contract):raise VerificationFault('unavailable-selected-contract-build')
        checked=b.inspect(root,bundle_ref,expected,live_source_root,selection['expected_contract'])
        bundle=r.parse(r.read_bytes(root,bundle_ref+'/envelope.json'),'envelope')
        for key in ['theory_ref','snapshot_ref','assumption_set_ref','dependency_graph_ref','coupling_refs']:
            if not r.same_json(bundle[key],selection[key]):raise VerificationFault('independent-artifact-substitution',key)
        assumptions=load(selection['assumption_set_ref']);exact(assumptions,['assumption_set_id','assumptions','authority_effect'],'malformed-assumption-context')
        if assumptions['assumption_set_id']!=theory['assumption_set_id'] or assumptions['authority_effect']!='none' or not isinstance(assumptions['assumptions'],list):raise VerificationFault('assumption-context-substitution')
        finite_requests=load(selection['finite_requests_ref']);provider_record=load(selection['expected_provider_bindings_ref']);exact(provider_record,['bindings'],'malformed-selected-provider-bindings')
        build_files=[Path(__file__),Path(o.__file__),o.RULES]
        build_hashes=[v.read_bytes() for v in build_files]
        current=f.current_bindings()
        if not r.same_json(provider_record['bindings'],current):raise VerificationFault('stale-selected-provider-build')
        obligations={row['obligation_id']:row for row in expected['logical_manifest']['obligations']}
        if not isinstance(finite_requests,dict) or set(finite_requests)-set(obligations):raise VerificationFault('unknown-selected-finite-query')
        for ref in finite_requests.values():
            request=load(ref)
            exact(request,['schema_version','subject_ref','selected_input_refs','alignment_refs','renaming','cardinalities','mode'],'malformed-finite-request')
            if request['schema_version']!='definition-assurance-verifier-finite-input/v1-candidate':raise VerificationFault('unsupported-finite-request')
            load(request['subject_ref'])
            if request['selected_input_refs'] is not None:
                for nested in request['selected_input_refs']:load(nested)
            for nested in request['alignment_refs']:load(nested)
        checked_rows=[];pending=[]
        for row in bundle['logical_results']:
            identity=row['obligation']['obligation_id'];native=row['native_result']
            if native is None:pending.append({'obligation_id':identity,'reason':'missing-native-evidence'});continue
            if row['provider_kind']!='finite-static' or native['data'].get('status') not in {'witness-found','countermodel-found'}:
                pending.append({'obligation_id':identity,'reason':'no-independent-checker-for-evidence-kind'});continue
            if identity not in finite_requests:raise VerificationFault('missing-independently-selected-finite-input',identity)
            input_ref=finite_requests[identity]
            if not r.same_json(input_ref,row['native_input_ref']):raise VerificationFault('native-input-selection-substitution',identity)
            request=load(input_ref)
            exact(request,['schema_version','subject_ref','selected_input_refs','alignment_refs','renaming','cardinalities','mode'],'malformed-finite-request')
            if request['schema_version']!='definition-assurance-verifier-finite-input/v1-candidate':raise VerificationFault('unsupported-finite-request')
            if not r.same_json(request['alignment_refs'],selection['coupling_refs']):raise VerificationFault('finite-alignment-substitution')
            subject=load(request['subject_ref']);inputs=[load(ref) for ref in request['selected_input_refs']] if request['selected_input_refs'] is not None else None
            # Regenerate subject from its input core(s) before interpreting a model.
            if inputs is None:ir.verify_ir(subject)
            else:ir.verify_composed(subject,inputs,request['alignment_refs'],root)
            originals=inputs if inputs is not None else [subject]
            if any(not any(r.same_json(item['source'],source) for source in theory['sources']) for item in originals):raise VerificationFault('finite-subject-source-substitution')
            mapping=signature_map(theory,subject,inputs,request['renaming'],endpoints)
            T=renamed(theory['statements']+assumptions['assumptions'],mapping)
            I=[] if identity=='query:consistency' else renamed([item['statement'] for key,item in obligations.items() if key.startswith('population:')],mapping)
            Q=renamed(obligations[identity]['statement'],mapping)
            if request['mode']=='witness' and obligations[identity]['minimum_strength']!='model-witness':raise VerificationFault('witness-cannot-establish-required-universal',identity)
            profile=load(row['profile_ref']);toolchain=load(row['toolchain_ref'])
            if not r.same_json(profile,r.parse(f.POLICY_PATH.read_bytes(),'profile')) or not r.same_json(toolchain,provider_record):raise VerificationFault('finite-profile-or-toolchain-substitution')
            if 'snapshot_sha256' in native['data'].get('input_bindings',{}) and native['data']['input_bindings']['snapshot_sha256']!=ir.digest(load(selection['snapshot_ref'])):raise VerificationFault('native-snapshot-substitution')
            result=witness(subject,native['data'],T,I,Q,request['cardinalities'],request['mode'],current,inputs,request['alignment_refs'],root,cancelled=cancelled)
            checked_rows.append({'obligation_id':identity,**result,'minimum_strength_met':result['query_truth'] is True and obligations[identity]['minimum_strength']=='model-witness'})
        # Every gate retains an explicit pending disposition, even if its producer reports support.
        gates=[{'gate_id':row['gate']['gate_id'],'status':'pending-independent-semantic-or-administrative-review','reported_status':row['reported_status']} for row in bundle['gate_results']]
        for path,raw in loaded.items():
            if r.read_bytes(root,path)!=raw:raise VerificationFault('independent-input-changed-during-verification',path)
        if any(path.read_bytes()!=raw for path,raw in zip(build_files,build_hashes)) or not r.same_json(contract,b.checked_contract()) or not r.same_json(current,f.current_bindings()):raise VerificationFault('checker-or-provider-build-changed-during-verification')
        b.inspect(root,bundle_ref,expected,live_source_root,selection['expected_contract'])
        return {**base,'status':'verified-candidate-accounting','required_set_sha256':expected['required_set_sha256'],'source_currentness':checked['source_currentness'],'checked_logical':checked_rows,'pending_logical':pending,'pending_gates':gates,'input_files_rehashed':len(loaded),'claim_ceiling':'Independent exact required-set, selected byte/currentness and supplied-model checks. Python checker trust remains; no generic soundness theorem, bounded exhaustion verification, semantic closure, owner fidelity or admission.'}
    except (VerificationFault,b.BundleFault,o.ObligationFault,o.p.PolicyFault,r.CaptureFault,ir.IRFault,c.InputError,f.ProviderFault) as error:
        return {**base,'status':'verification-rejected','diagnostics':[{'code':error.code,'path':error.path}],'claim_ceiling':'No readiness or logical claim accepted for rejected input.'}
    except (OSError,ValueError,TypeError,KeyError,IndexError,RecursionError,MemoryError) as error:
        return {**base,'status':'verification-unresolved','diagnostics':[{'code':type(error).__name__}],'claim_ceiling':'Execution or malformed-input failure; no logical absence conclusion.'}
