"""Streaming finite interpretations with explicit scope and completeness ceilings."""
from pathlib import Path
from time import monotonic
import contracts as c
import ir
import resolver as r
import semantics as s

IMPL=Path(__file__).resolve().parents[1]
ROOT=IMPL.parents[3]
POLICY_PATH=IMPL/'profiles/selection.json'
POLICY_SHA256='80bc2f323114efaf1cb058f01515b6522c19455d211899a8e651ebe545dd2d49'
MODES={'witness','countermodel','bounded-validity'}
MIN_OUTPUT_BYTES=2048


class ProviderFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


class StopSearch(ProviderFault):pass


def load_limits(overrides=None):
    raw=POLICY_PATH.read_bytes()
    if r.digest(raw)!=POLICY_SHA256:raise ProviderFault('stale-selected-policy')
    policy=r.parse(raw,str(POLICY_PATH));caps=policy['budgets'];limits={key:value for key,value in caps.items() if key!='execution_policy'}
    if overrides is not None:
        if not isinstance(overrides,dict) or set(overrides)-set(limits):raise ProviderFault('unknown-or-malformed-budget')
        for key,value in overrides.items():
            valid=(type(value) in (int,float) and value>0 and value<=caps[key]) if key=='timeout_seconds' else (type(value) is int and value>0 and value<=caps[key])
            if not valid:raise ProviderFault('invalid-or-loosened-budget',key)
            limits[key]=value
    if limits['max_output_bytes']<MIN_OUTPUT_BYTES:raise ProviderFault('output-budget-below-control-envelope')
    return limits


def current_bindings():
    # New provider implementation is bound directly; P01 remains its old epoch.
    raw=POLICY_PATH.read_bytes()
    if r.digest(raw)!=POLICY_SHA256:raise ProviderFault('stale-selected-policy')
    policy=r.parse(raw,str(POLICY_PATH));ref=policy['inventory_ref'];inventory_raw=r.read_bytes(ROOT,ref['path'])
    if r.digest(inventory_raw)!=ref['sha256']:raise ProviderFault('stale-selected-runtime-inventory')
    inventory=r.parse(inventory_raw,ref['path']);runtime=inventory['routes']['generic-finite']
    paths=[Path(__file__).resolve()]+[IMPL/name for name in ['contracts.py','resolver.py','ir.py','semantics.py','schemas/input-envelope.json','profiles/selection.json']]+[ROOT/ref['path']]
    result=[{'path':str(path.relative_to(ROOT)),'sha256':r.digest(path.read_bytes())} for path in paths]
    for binding in runtime['runtime_bindings']:
        path=Path(binding['path']);path=path if path.is_absolute() else ROOT/path
        if r.digest(path.read_bytes())!=binding['sha256']:raise ProviderFault('stale-bound-runtime',binding['path'])
        result.append(dict(binding))
    return result


class Control:
    def __init__(self,limits,cancelled,started):
        self.limits=limits;self.cancelled=cancelled;self.started=started;self.deadline=started+limits['timeout_seconds']
        self.counts={'visited':0,'theory_models':0,'admissible_models':0,'matching_query_models':0,'evaluation_steps':0}
    def poll(self):
        if self.cancelled is not None and self.cancelled():raise StopSearch('cancelled')
        if monotonic()>=self.deadline:raise StopSearch('timeout')
    def tick(self):
        self.poll()
        if self.counts['evaluation_steps']>=self.limits['max_evaluation_steps']:raise StopSearch('evaluation-step-limit')
        self.counts['evaluation_steps']+=1


class ControlledEvaluator(s.Evaluator):
    def __init__(self,structure,control):super().__init__(structure,control.limits['max_evaluation_steps']);self.control=control
    def tick(self):self.control.tick();super().tick()


def capped_power(base,exponent,cap):
    """Exact small radix or a known-larger sentinel, without a huge power."""
    result=1;factor=base;remaining=exponent;exact=True
    while remaining:
        if remaining&1:
            result*=factor
            if result>cap:return cap,False
            if not exact:return cap,False
        remaining>>=1
        if remaining:
            factor*=factor
            if factor>cap:factor=cap+1;exact=False
    return result,True


def tuple_count(argument_sorts,domains,cap):
    count=1
    for sort in argument_sorts:
        count*=len(domains[sort])
        if count>cap:raise StopSearch('symbol-tuple-space-limit')
    return count


def tuple_at(index,argument_sorts,domains):
    values=[]
    for sort in reversed(argument_sorts):
        members=domains[sort];index,offset=divmod(index,len(members));values.append(members[offset])
    return list(reversed(values))


def plan_space(declarations,cardinalities,control):
    c.bounded_tree(cardinalities)
    sorts={row['symbol_id'] for row in declarations if row['kind']=='sort'}
    if not isinstance(cardinalities,dict) or set(cardinalities)!=sorts:raise ProviderFault('exact-cardinality-denominator-required')
    if any(type(value) is not int or value<1 or value>control.limits['max_domain_cardinality'] for value in cardinalities.values()):raise ProviderFault('invalid-domain-cardinality')
    domains={sort:['a'+str(index) for index in range(cardinalities[sort])] for sort in sorted(sorts)}
    dimensions=[];factors=[];small_total=1;cap=control.limits['max_interpretations']+1
    for declaration in sorted(declarations,key=lambda row:row['symbol_id']):
        control.poll();kind=declaration['kind']
        if kind=='sort':continue
        if kind=='constant':base=len(domains[declaration['result_sort']]);exponent=1
        elif kind=='total-function':base=len(domains[declaration['result_sort']]);exponent=tuple_count(declaration['argument_sorts'],domains,control.limits['max_function_tuple_space'])
        elif kind in {'predicate','relation'}:base=2;exponent=tuple_count(declaration['argument_sorts'],domains,control.limits['max_function_tuple_space'])
        else:raise ir.Unsupported('unsupported-finite-declaration',kind)
        radix,exact=capped_power(base,exponent,cap)
        dimensions.append({'declaration':declaration,'base':base,'tuple_count':exponent,'radix':radix,'radix_exact':exact})
        factors.append({'symbol_id':declaration['symbol_id'],'kind':kind,'base':base,'exponent':exponent,'small_exact_choice_count':radix if exact else None})
        if small_total is not None:
            if not exact or small_total*radix>cap:small_total=None
            else:small_total*=radix
    return domains,dimensions,{'representation':'exact-product-of-powers','factors':factors,'small_exact_total':small_total,'large_space_rule':'Any capped radix exceeds the allowed visited prefix; capped enumeration cannot establish exhaustion.'}


class ModelSize:
    def __init__(self,model,control):self.control=control;self.size=len(ir.canonical(model))
    def add(self,value):
        self.control.poll();self.size+=len(ir.canonical(value))+2
        if self.size>self.control.limits['max_output_bytes']:raise StopSearch('model-representation-limit')


def build_model(domains,dimensions,digits,control):
    model={'domains':domains,'constants':{},'functions':{},'predicates':{}}
    size=ModelSize(model,control)
    # No precomputed tuple lists or cached predicate powersets.
    for dimension,digit in zip(dimensions,digits):
        declaration=dimension['declaration'];kind=declaration['kind'];identity=declaration['symbol_id'];size.add(identity)
        if kind=='constant':
            value=domains[declaration['result_sort']][digit];size.add(value);model['constants'][identity]=value
        elif kind=='total-function':
            rows=[];model['functions'][identity]=rows;values=domains[declaration['result_sort']]
            for index in range(dimension['tuple_count']):
                digit,offset=divmod(digit,len(values));row={'args':tuple_at(index,declaration['argument_sorts'],domains),'value':values[offset]}
                size.add(row);rows.append(row)
        else:
            rows=[];model['predicates'][identity]=rows
            while digit:
                bit=digit&-digit;index=bit.bit_length()-1;row=tuple_at(index,declaration['argument_sorts'],domains);size.add(row);rows.append(row);digit-=bit
    if len(ir.canonical(model))>control.limits['max_output_bytes']:raise StopSearch('model-representation-limit')
    return model


def advance(digits,dimensions):
    for index in range(len(digits)-1,-1,-1):
        digits[index]+=1
        if digits[index]<dimensions[index]['radix']:return True
        digits[index]=0
    return False


def search(subject,theory,populations,query,cardinalities,mode='witness',budgets=None,cancelled=None,selected_inputs=None,selected_alignments=(),alignment_root=None,snapshot=None,live_root=None):
    """One exact finite cardinality vector; existential or bounded queries only."""
    started=monotonic();control=None;space=None;inputs={};limits=None;implementation=None
    base={'schema_version':'definition-assurance-finite-result/v1-candidate','authority_effect':'none','semantic_ready':False,'mode':mode,'policy_sha256':POLICY_SHA256,'source_fidelity':'not-established-by-provider','source_currentness':'not-checked','unbounded_conclusion':None}
    def finish(status,complete=False,evidence='none',witness=None,diagnostics=()):
        value={**base,'status':status,'exhaustion_complete':complete,'evidence_strength':evidence,'witness':witness,'diagnostics':list(diagnostics),'input_bindings':inputs,'implementation_bindings':implementation,'limits':limits,'counts':control.counts if control else None,'space':space,'elapsed_seconds':max(0,monotonic()-started),'claim_ceiling':'Exact selected finite scope only. A checked witness is existential/model evidence; bounded exhaustion is not an unbounded theorem, inconsistency or absence claim.'}
        if limits and len(ir.canonical(value))>limits['max_output_bytes']:
            return {**base,'status':'resource-limit','exhaustion_complete':False,'evidence_strength':'none','witness':None,'diagnostics':[{'code':'result-representation-limit'}],'counts':control.counts if control else None,'input_bindings':inputs}
        return value
    try:
        limits=load_limits(budgets);control=Control(limits,cancelled,started);control.poll()
        if mode not in MODES:raise ProviderFault('unsupported-search-mode')
        if not isinstance(theory,list) or not isinstance(populations,list):raise ProviderFault('theory-and-population-lists-required')
        declarations=s.subject_declarations(subject,selected_inputs,selected_alignments,alignment_root)
        sorts={row['symbol_id']:row['symbol_id'] for row in declarations if row['kind']=='sort'};symbols={row['symbol_id']:row for row in declarations if row['kind']!='sort'}
        c.bounded_tree(theory);c.bounded_tree(populations);c.bounded_tree(query)
        T=[ir.formula(node,sorts,symbols) for node in theory];I=[ir.formula(node,sorts,symbols) for node in populations];Q=ir.formula(query,sorts,symbols)
        inputs={'subject_ir_sha256':subject['ir_sha256'],'theory_sha256':ir.digest(T),'populations_sha256':ir.digest(I),'query_sha256':ir.digest(Q),'cardinalities_sha256':ir.digest(cardinalities),'composition_input_ir_sha256':[value['ir_sha256'] for value in selected_inputs] if selected_inputs is not None else None,'selected_alignment_refs_sha256':ir.digest(list(selected_alignments))}
        if snapshot is not None:
            r.verify(snapshot,live_root)
            originals=selected_inputs if subject['schema_version']=='definition-assurance-composed-ir/v1-candidate' else [subject]
            for original in originals:ir.compile_interpretation(original['input_core'],snapshot)
            base['source_currentness']='verified-live' if live_root is not None else 'verified-against-captured-snapshot'
            inputs['snapshot_sha256']=ir.digest(snapshot)
        implementation=current_bindings()
        domains,dimensions,space=plan_space(declarations,cardinalities,control);space['domain_cardinalities']=dict(sorted(cardinalities.items()));space['atom_naming']='a0..a(n-1) within each exact sort; names do not align separate carriers';digits=[0]*len(dimensions)
        while True:
            control.poll()
            if control.counts['visited']>=limits['max_interpretations']:raise StopSearch('interpretation-limit')
            model=build_model(domains,dimensions,digits,control);structure=s.validate_model(declarations,model);evaluator=ControlledEvaluator(structure,control)
            control.counts['visited']+=1
            if all(evaluator.holds(node) for node in T):
                control.counts['theory_models']+=1
                if all(evaluator.holds(node) for node in I):
                    control.counts['admissible_models']+=1;truth=evaluator.holds(Q);match=truth if mode=='witness' else not truth
                    if match:control.counts['matching_query_models']+=1
                    if match:
                        control.poll()
                        if not r.same_json(implementation,current_bindings()):raise ProviderFault('provider-input-code-changed-during-search')
                        if r.digest(POLICY_PATH.read_bytes())!=POLICY_SHA256:raise ProviderFault('policy-changed-during-search')
                        witness={'model':model,'model_sha256':ir.digest(model),'query_truth':truth,'interpretation_rank_zero_based':control.counts['visited']-1}
                        return finish('witness-found' if mode=='witness' else 'countermodel-found',False,'model-witness',witness)
            if not advance(digits,dimensions):
                if any(not dimension['radix_exact'] for dimension in dimensions):raise StopSearch('incomplete-capped-space')
                if not r.same_json(implementation,current_bindings()):raise ProviderFault('provider-input-code-changed-during-search')
                if r.digest(POLICY_PATH.read_bytes())!=POLICY_SHA256:raise ProviderFault('policy-changed-during-search')
                if not control.counts['theory_models']:status='bounded-no-theory-model'
                elif not control.counts['admissible_models']:status='bounded-no-admissible-model'
                elif mode=='bounded-validity':status='bounded-supported'
                else:status='bounded-no-witness' if mode=='witness' else 'bounded-no-countermodel'
                return finish(status,True,'bounded-exhaustion')
    except ir.Unsupported as error:return finish('unsupported',diagnostics=[{'code':error.code,'path':error.path}])
    except StopSearch as error:return finish(error.code if error.code in {'timeout','cancelled'} else 'resource-limit',diagnostics=[{'code':error.code}])
    except (ProviderFault,s.ModelFault,ir.IRFault,c.InputError,r.CaptureFault) as error:return finish('unresolved-input-or-binding' if isinstance(error,r.CaptureFault) or error.code in {'stale-selected-policy','stale-selected-runtime-inventory','stale-bound-runtime','provider-input-code-changed-during-search','policy-changed-during-search'} else 'malformed',diagnostics=[{'code':error.code,'path':error.path}])
    except (OSError,ValueError,TypeError,KeyError,IndexError,MemoryError) as error:return finish('provider-error',diagnostics=[{'code':type(error).__name__}])


def replay(subject,result,theory,populations,query,cardinalities,selected_inputs=None,selected_alignments=(),alignment_root=None):
    """Checked witness replay only; independent evidence verification is E03."""
    witness=result.get('witness') if isinstance(result,dict) else None
    if not isinstance(witness,dict) or result.get('status') not in {'witness-found','countermodel-found'}:raise ProviderFault('no-replayable-witness')
    declarations=s.subject_declarations(subject,selected_inputs,selected_alignments,alignment_root)
    sorts={row['symbol_id']:row['symbol_id'] for row in declarations if row['kind']=='sort'};symbols={row['symbol_id']:row for row in declarations if row['kind']!='sort'}
    caps=load_limits()
    if not isinstance(cardinalities,dict) or set(cardinalities)!=set(sorts) or any(type(value) is not int or value<1 or value>caps['max_domain_cardinality'] for value in cardinalities.values()):raise ProviderFault('invalid-replay-cardinalities')
    c.bounded_tree(theory);c.bounded_tree(populations);c.bounded_tree(query)
    T=[ir.formula(node,sorts,symbols) for node in theory];I=[ir.formula(node,sorts,symbols) for node in populations];Q=ir.formula(query,sorts,symbols)
    bindings=result['input_bindings']
    for key,value in [('subject_ir_sha256',subject['ir_sha256']),('theory_sha256',ir.digest(T)),('populations_sha256',ir.digest(I)),('query_sha256',ir.digest(Q)),('cardinalities_sha256',ir.digest(cardinalities)),('composition_input_ir_sha256',[value['ir_sha256'] for value in selected_inputs] if selected_inputs is not None else None),('selected_alignment_refs_sha256',ir.digest(list(selected_alignments)))]:
        if bindings.get(key)!=value:raise ProviderFault('witness-replay-input-substitution',key)
    model=witness['model']
    if ir.digest(model)!=witness['model_sha256'] or set(model['domains'])!=set(cardinalities) or any(len(model['domains'][key])!=cardinalities[key] for key in cardinalities):raise ProviderFault('witness-model-binding-or-domain-mismatch')
    actual=s.assess(subject,model,T,I,[Q],selected_inputs=selected_inputs,selected_alignments=selected_alignments,root=alignment_root)
    truth=result['status']=='witness-found'
    if actual['status'] not in {'model-local-supported','model-local-counterexample'} or actual['targets']!=[truth] or type(witness['query_truth']) is not bool or witness['query_truth']!=truth:raise ProviderFault('witness-does-not-establish-selected-query')
    return {'result':'PASS','query_truth':truth,'model_sha256':witness['model_sha256'],'semantic_ready':False,'authority_effect':'none','claim_ceiling':'Checked model witness for independently selected exact replay inputs; no general provider correctness theorem or source fidelity.'}
