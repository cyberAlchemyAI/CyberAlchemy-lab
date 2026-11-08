"""Finite structures and satisfaction for the independently specified static core."""
from math import prod
import contracts as c
import ir
import resolver as r

MAX_TUPLE_SPACE=100_000
MAX_STEPS=100_000


class ModelFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


class ResourceLimit(ModelFault):pass
class Cancelled(ModelFault):pass


def exact(value,keys,code):
    if not isinstance(value,dict) or set(value)!=set(keys):raise ModelFault(code)


def subject_declarations(subject,selected_inputs=None,selected_alignments=(),root=None):
    if not isinstance(subject,dict):raise ModelFault('malformed-typed-subject')
    if subject.get('schema_version')=='definition-assurance-static-ir/v1-candidate':ir.verify_ir(subject)
    elif subject.get('schema_version')=='definition-assurance-composed-ir/v1-candidate':
        if selected_inputs is None:raise ModelFault('missing-composition-inputs')
        ir.verify_composed(subject,selected_inputs,selected_alignments,root)
    else:raise ModelFault('unsupported-or-missing-typed-subject')
    return subject['declarations']


def validate_model(declarations,model):
    c.bounded_tree(model);exact(model,['domains','constants','functions','predicates'],'malformed-model-envelope')
    tables={key:model[key] for key in model}
    if any(not isinstance(table,dict) for table in tables.values()):raise ModelFault('malformed-model-table')
    expected={'domains':set(),'constants':set(),'functions':set(),'predicates':set()};signature={}
    for declaration in declarations:
        kind=declaration['kind'];identity=declaration['symbol_id'];signature[identity]=declaration
        bucket={'sort':'domains','constant':'constants','total-function':'functions','predicate':'predicates','relation':'predicates'}.get(kind)
        if bucket is None:raise ModelFault('unsupported-model-declaration')
        expected[bucket].add(identity)
    for key,names in expected.items():
        if set(tables[key])!=names:raise ModelFault('incomplete-or-extra-model-interpretation',key)
    domains={}
    for identity,values in model['domains'].items():
        if not isinstance(values,list) or not values or any(not isinstance(value,str) or not value for value in values) or len(set(values))!=len(values):raise ModelFault('empty-or-malformed-domain',identity)
        domains[identity]=tuple(values)
    def tuple_value(values,sorts,identity):
        if not isinstance(values,list) or len(values)!=len(sorts) or any(not isinstance(value,str) or value not in domains[sort] for value,sort in zip(values,sorts)):raise ModelFault('ill-sorted-model-tuple',identity)
        return tuple(values)
    constants={}
    for identity,value in model['constants'].items():
        if not isinstance(value,str) or value not in domains[signature[identity]['result_sort']]:raise ModelFault('ill-sorted-constant',identity)
        constants[identity]=value
    functions={}
    for identity,rows in model['functions'].items():
        declaration=signature[identity];sorts=declaration['argument_sorts'];count=prod(len(domains[sort]) for sort in sorts)
        if count>MAX_TUPLE_SPACE:raise ResourceLimit('function-tuple-space-limit',identity)
        if not isinstance(rows,list):raise ModelFault('malformed-function-table',identity)
        table={}
        for row in rows:
            exact(row,['args','value'],'malformed-function-row');args=tuple_value(row['args'],sorts,identity)
            if args in table:raise ModelFault('duplicate-function-tuple',identity)
            if not isinstance(row['value'],str) or row['value'] not in domains[declaration['result_sort']]:raise ModelFault('ill-sorted-function-result',identity)
            table[args]=row['value']
        if len(table)!=count:raise ModelFault('nontotal-function-interpretation',identity)
        functions[identity]=table
    predicates={}
    for identity,rows in model['predicates'].items():
        if not isinstance(rows,list):raise ModelFault('malformed-predicate-extension',identity)
        tuples=[tuple_value(row,signature[identity]['argument_sorts'],identity) for row in rows]
        if len(set(tuples))!=len(tuples):raise ModelFault('duplicate-predicate-tuple',identity)
        predicates[identity]=set(tuples)
    return {'domains':domains,'constants':constants,'functions':functions,'predicates':predicates}


class Evaluator:
    def __init__(self,structure,max_steps=MAX_STEPS,cancelled=None):
        if type(max_steps) is not int or max_steps<1:raise ModelFault('invalid-step-budget')
        self.structure=structure;self.max_steps=max_steps;self.steps=0;self.cancelled=cancelled

    def tick(self):
        if self.cancelled is not None and self.cancelled():raise Cancelled('cancelled')
        if self.steps>=self.max_steps:raise ResourceLimit('evaluation-step-limit')
        self.steps+=1

    def term(self,node,env):
        self.tick();op=node['op']
        if op=='var':return env[node['name']]
        if op=='const':return self.structure['constants'][node['name']]
        arguments=tuple(self.term(value,env) for value in node['args'])
        return self.structure['functions'][node['name']][arguments]

    def holds(self,node,env=None):
        self.tick();env={} if env is None else env;op=node['op']
        if op=='pred':return tuple(self.term(value,env) for value in node['args']) in self.structure['predicates'][node['name']]
        if op=='eq':return self.term(node['left'],env)==self.term(node['right'],env)
        if op=='not':return not self.holds(node['arg'],env)
        if op=='and':return all(self.holds(value,env) for value in node['args'])
        if op=='or':return any(self.holds(value,env) for value in node['args'])
        if op=='implies':return not self.holds(node['left'],env) or self.holds(node['right'],env)
        if op=='iff':return self.holds(node['left'],env)==self.holds(node['right'],env)
        values=(self.holds(node['body'],{**env,node['var']:value}) for value in self.structure['domains'][node['sort']])
        return all(values) if op=='forall' else any(values)


def prepare(subject,model,selected_inputs=None,selected_alignments=(),root=None,max_steps=MAX_STEPS,cancelled=None):
    declarations=subject_declarations(subject,selected_inputs,selected_alignments,root)
    structure=validate_model(declarations,model)
    sorts={row['symbol_id']:row['symbol_id'] for row in declarations if row['kind']=='sort'}
    symbols={row['symbol_id']:row for row in declarations if row['kind']!='sort'}
    evaluator=Evaluator(structure,max_steps,cancelled)
    def typed(node):
        c.bounded_tree(node)
        return ir.formula(node,sorts,symbols)
    return evaluator,typed


def evaluate(subject,model,node,**options):
    evaluator,typed=prepare(subject,model,**options);compiled=typed(node);truth=evaluator.holds(compiled)
    return {'status':'model-local-value','truth':truth,'steps':evaluator.steps,'model_sha256':ir.digest(model),'subject_ir_sha256':subject['ir_sha256'],'statement_sha256':ir.digest(compiled),'semantic_ready':False,'authority_effect':'none','claim_ceiling':'Truth in this exact complete finite structure; no source fidelity, unrestricted entailment or admission.'}


def assess(subject,model,theory,populations,targets,**options):
    for values in [theory,populations,targets]:
        if not isinstance(values,list):raise ModelFault('formula-list-required')
    evaluator,typed=prepare(subject,model,**options)
    T=[typed(value) for value in theory];I=[typed(value) for value in populations];Q=[typed(value) for value in targets]
    base={'semantic_ready':False,'authority_effect':'none','model_sha256':ir.digest(model),'subject_ir_sha256':subject['ir_sha256'],'theory_sha256':ir.digest(T),'population_sha256':ir.digest(I),'targets_sha256':ir.digest(Q)}
    if not all(evaluator.holds(value) for value in T):return {**base,'status':'model-theory-counterexample','theory_satisfied':False,'targets':[]}
    if not all(evaluator.holds(value) for value in I):return {**base,'status':'vacuous-required-population','theory_satisfied':True,'populations_satisfied':False,'targets':[]}
    values=[evaluator.holds(value) for value in Q]
    return {**base,'status':'model-local-supported' if all(values) else 'model-local-counterexample','theory_satisfied':True,'populations_satisfied':True,'targets':values,'steps':evaluator.steps,'claim_ceiling':'One complete model satisfying these selected premises/populations; target values are model-local, not all-model entailment.'}


def try_evaluate(subject,model,node,**options):
    try:return evaluate(subject,model,node,**options)
    except ir.Unsupported as error:status='unsupported';diagnostic={'code':error.code,'path':error.path}
    except Cancelled as error:status='cancelled';diagnostic={'code':error.code,'path':error.path}
    except ResourceLimit as error:status='resource-limit';diagnostic={'code':error.code,'path':error.path}
    except r.CaptureFault as error:status='unresolved-source-or-alignment';diagnostic={'code':error.code,'path':error.path}
    except (ModelFault,ir.IRFault,c.InputError) as error:status='malformed';diagnostic={'code':error.code,'path':error.path}
    return {'status':status,'diagnostics':[diagnostic],'semantic_ready':False,'authority_effect':'none','claim_ceiling':'No truth value or logical absence conclusion for this execution/model outcome.'}
