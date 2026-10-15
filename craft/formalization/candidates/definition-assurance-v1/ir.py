"""Typed static canonical IR; structural typing is not semantic assurance."""
import copy
import hashlib
import json
import re
from pathlib import Path
import contracts as c
import resolver as r


class IRFault(ValueError):
    def __init__(self,code,path=''):self.code=code;self.path=path


class Unsupported(IRFault):pass


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def qualified(source,scope,local):return 'sym:'+digest([source['definition_id'],source['version_ref'],scope,local])


def shape(node,keys):
    if not isinstance(node,dict) or set(node)!=set(keys):raise IRFault('malformed-AST-shape')


def name(value):
    if not isinstance(value,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:-]*',value):raise IRFault('malformed-symbol-name')
    return value


def term(node,sorts,symbols,env):
    if not isinstance(node,dict) or not isinstance(node.get('op'),str):raise IRFault('malformed-term')
    op=node['op']
    if op=='var':
        shape(node,['op','name']);name(node['name'])
        if node['name'] not in env:raise IRFault('unbound-variable',str(node['name']))
        return copy.deepcopy(node),env[node['name']]
    if op=='const':
        shape(node,['op','name']);name(node['name']);symbol=symbols.get(node['name'])
        if symbol is None or symbol['kind']!='constant':raise IRFault('unknown-or-wrong-kind-constant',str(node['name']))
        return {'op':'const','name':symbol['symbol_id']},symbol['result_sort']
    if op=='fn':
        shape(node,['op','name','args']);name(node['name']);symbol=symbols.get(node['name'])
        if symbol is None or symbol['kind']!='total-function':raise IRFault('unknown-or-wrong-kind-function',str(node['name']))
        if not isinstance(node['args'],list) or len(node['args'])!=len(symbol['argument_sorts']):raise IRFault('function-arity')
        compiled=[term(value,sorts,symbols,env) for value in node['args']]
        if [sort for _,sort in compiled]!=symbol['argument_sorts']:raise IRFault('function-argument-sort')
        return {'op':'fn','name':symbol['symbol_id'],'args':[value for value,_ in compiled]},symbol['result_sort']
    raise Unsupported('unsupported-term-operator',op)


def formula(node,sorts,symbols,env=None):
    env={} if env is None else env
    if not isinstance(node,dict) or not isinstance(node.get('op'),str):raise IRFault('malformed-formula')
    op=node['op']
    if op=='pred':
        shape(node,['op','name','args']);name(node['name']);symbol=symbols.get(node['name'])
        if symbol is None or symbol['kind'] not in {'predicate','relation'}:raise IRFault('unknown-or-wrong-kind-predicate',str(node['name']))
        if not isinstance(node['args'],list) or len(node['args'])!=len(symbol['argument_sorts']):raise IRFault('predicate-arity')
        compiled=[term(value,sorts,symbols,env) for value in node['args']]
        if [sort for _,sort in compiled]!=symbol['argument_sorts']:raise IRFault('predicate-argument-sort')
        return {'op':'pred','name':symbol['symbol_id'],'args':[value for value,_ in compiled]}
    if op=='eq':
        shape(node,['op','left','right']);left,ls=term(node['left'],sorts,symbols,env);right,rs=term(node['right'],sorts,symbols,env)
        if ls!=rs:raise IRFault('unaligned-equality-sorts')
        return {'op':op,'left':left,'right':right}
    if op=='not':
        shape(node,['op','arg']);return {'op':op,'arg':formula(node['arg'],sorts,symbols,env)}
    if op in {'and','or'}:
        shape(node,['op','args'])
        if not isinstance(node['args'],list):raise IRFault('connective-arguments-not-list')
        return {'op':op,'args':[formula(value,sorts,symbols,env) for value in node['args']]}
    if op in {'implies','iff'}:
        shape(node,['op','left','right']);return {'op':op,'left':formula(node['left'],sorts,symbols,env),'right':formula(node['right'],sorts,symbols,env)}
    if op in {'forall','exists'}:
        shape(node,['op','var','sort','body'])
        if not isinstance(node['sort'],str) or node['sort'] not in sorts:raise IRFault('unbound-quantifier-sort-or-variable')
        name(node['var']);sort=sorts[node['sort']];return {'op':op,'var':node['var'],'sort':sort,'body':formula(node['body'],sorts,symbols,{**env,node['var']:sort})}
    raise Unsupported('unsupported-formula-operator',op)


def compile_interpretation(core,snapshot=None):
    result=c.validate({'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core},'interpretation')
    if result['status']!='structurally-valid':raise IRFault('malformed-interpretation')
    if set(core['logic_features'])-{'propositional','first-order','equality','finite-cardinality'}:raise Unsupported('unsupported-or-unresolved-logic-feature')
    if snapshot is not None:
        r.verify(snapshot)
        if not any(all(core['source'][key]==row[key] for key in ['definition_id','version_ref','path','sha256']) for row in snapshot['current_entries']):raise IRFault('unbound-current-source')
    declarations=core['declarations'];scope=core['scope'];source=core['source'];sorts={};symbols={};origins=[]
    for declaration in declarations:
        if declaration['scope']!=scope:raise IRFault('declaration-outside-selected-scope')
        local=declaration['symbol_id'];identity=qualified(source,scope,local)
        origins.append({'canonical_id':identity,'definition_id':source['definition_id'],'version_ref':source['version_ref'],'scope':scope,'local_symbol_id':local,'kind':declaration['kind']})
        if declaration['kind']=='sort':
            if declaration['domain_policy']!='nonempty':raise Unsupported('extension-required-domain-policy')
            sorts[local]=identity
    compiled=[]
    for declaration in declarations:
        row=copy.deepcopy(declaration);local=row['symbol_id'];row['symbol_id']=qualified(source,scope,local);kind=row['kind']
        if kind in {'partial-function','record','state','transition','trace'}:raise Unsupported('extension-required-declaration',kind)
        for field in ['result_sort','argument_sorts']:
            if field in row:
                names=[row[field]] if field=='result_sort' else row[field]
                if any(name not in sorts for name in names):raise IRFault('undeclared-signature-sort')
                row[field]=sorts[names[0]] if field=='result_sort' else [sorts[name] for name in names]
        if kind!='sort':symbols[local]=row
        compiled.append(row)
    clauses=[]
    for clause in sorted(core['clauses'],key=lambda row:row['clause_id']):
        row=copy.deepcopy(clause)
        if row['formal_statement'] is not None:row['formal_statement']=formula(row['formal_statement'],sorts,symbols)
        clauses.append(row)
    assumptions=[]
    for assumption in sorted(core['assumptions'],key=lambda row:row['assumption_id']):
        row=copy.deepcopy(assumption);row['statement']=formula(row['statement'],sorts,symbols);assumptions.append(row)
    populations=[]
    for population in sorted(core['populations'],key=lambda row:row['population_id']):
        row=copy.deepcopy(population)
        if row['carrier'] not in sorts:raise IRFault('undeclared-population-carrier')
        row['carrier']=sorts[row['carrier']]
        if row['predicate_ref'] is not None:
            symbol=symbols.get(row['predicate_ref'])
            if symbol is None or symbol['kind'] not in {'predicate','relation'}:raise IRFault('unknown-population-predicate')
            row['predicate_ref']=symbol['symbol_id']
        if row['statement'] is not None:row['statement']=formula(row['statement'],sorts,symbols)
        populations.append(row)
    body={'schema_version':'definition-assurance-static-ir/v1-candidate','authority_effect':'none','source':source,'interpretation_id':core['interpretation_id'],'scope':scope,'declarations':sorted(compiled,key=lambda row:row['symbol_id']),'origins':sorted(origins,key=lambda row:row['canonical_id']),'clauses':clauses,'assumptions':assumptions,'populations':populations,'depends_on':sorted(core['depends_on'],key=lambda row:row['version_ref']),'source_fidelity':core['source_fidelity'],'input_core':copy.deepcopy(core),'input_core_sha256':digest(core),'source_binding':'requires-independent-currentness-check','semantic_ready':False,'noncollapse':'not-assessed','claim_ceiling':'Closed static signature/formula typing and exact nominal identity; no model truth, population, source fidelity or non-collapse proof.'}
    return {**body,'ir_sha256':digest(body)}


def verify_ir(value):
    # Regenerate typed canonical declarations/statements from the bound input.
    # This checks static provenance/typing only; source-currentness is separate.
    c.bounded_tree(value)
    if not isinstance(value,dict) or 'input_core' not in value:raise IRFault('malformed-IR')
    expected=compile_interpretation(value['input_core'])
    if not r.same_json(value,expected):raise IRFault('stale-or-forged-IR')
    return True


def remap_formula(node,mapping):
    if isinstance(node,list):return [remap_formula(value,mapping) for value in node]
    if isinstance(node,dict):
        return {key:mapping.get(value,value) if key=='sort' and isinstance(value,str) else remap_formula(value,mapping) for key,value in node.items()}
    return node


def compose(interpretations,alignment_refs=(),root=None):
    if not interpretations:raise IRFault('empty-IR-composition')
    namespaces=set();declarations={};origins=[];parents={}
    for ir in interpretations:
        verify_ir(ir);namespace=(ir['source']['definition_id'],ir['source']['version_ref'],ir['scope'])
        if namespace in namespaces:raise IRFault('duplicate-interpretation-namespace')
        namespaces.add(namespace);origins.extend(ir['origins'])
        for declaration in ir['declarations']:
            identity=declaration['symbol_id']
            if identity in declarations:raise IRFault('canonical-symbol-collision')
            declarations[identity]=copy.deepcopy(declaration)
            if declaration['kind']=='sort':parents[identity]=identity
    def find(value):
        while parents[value]!=value:value=parents[value]
        return value
    alignment_bindings=[]
    for ref in alignment_refs:
        if root is None:raise IRFault('missing-alignment-root')
        shape(ref,['path','sha256']);raw=r.read_bytes(r.resolve_root(root),ref['path'])
        if r.digest(raw)!=ref['sha256']:raise IRFault('stale-carrier-alignment')
        doc=r.parse(raw,ref['path']);shape(doc,['schema_version','authority_effect','mapping_kind','carrier','scope','left_source','right_source','reviewer_ref','review_basis','equivalence_claim'])
        if doc['schema_version']!='definition-assurance-carrier-alignment/v1-candidate' or doc['authority_effect']!='none' or doc['equivalence_claim']!='none':raise IRFault('invalid-carrier-alignment')
        if doc['mapping_kind']!='identity-shared-carrier':raise Unsupported('unsupported-carrier-mapping')
        members=[]
        for source_key in ['left_source','right_source']:
            matches=[ir for ir in interpretations if r.same_json(ir['source'],doc[source_key]) and ir['scope']==doc['scope']]
            if len(matches)!=1:raise IRFault('alignment-source-scope-mismatch')
            match=matches[0];identity=qualified(match['source'],match['scope'],doc['carrier'])
            if identity not in parents:raise IRFault('alignment-not-a-declared-sort')
            members.append(identity)
        if any(not isinstance(doc[key],str) or not doc[key].strip() for key in ['reviewer_ref','review_basis']):raise IRFault('unattributed-carrier-alignment')
        parents[find(members[1])]=find(members[0]);alignment_bindings.append(copy.deepcopy(ref))
    groups={}
    for identity in parents:groups.setdefault(find(identity),[]).append(identity)
    mapping={}
    for members in groups.values():
        shared=members[0] if len(members)==1 else 'carrier:'+digest(sorted(members))
        for member in members:mapping[member]=shared
    result_declarations={}
    for identity,declaration in declarations.items():
        row=copy.deepcopy(declaration)
        if row['kind']=='sort':row['symbol_id']=mapping[identity];row['scope']='scope:explicit-shared' if row['symbol_id']!=identity else row['scope']
        if 'argument_sorts' in row:row['argument_sorts']=[mapping[value] for value in row['argument_sorts']]
        if 'result_sort' in row:row['result_sort']=mapping[row['result_sort']]
        if row['symbol_id'] in result_declarations and not r.same_json(row,result_declarations[row['symbol_id']]):raise IRFault('incompatible-shared-sort')
        result_declarations[row['symbol_id']]=row
    body={'schema_version':'definition-assurance-composed-ir/v1-candidate','authority_effect':'none','input_ir_sha256':sorted(ir['ir_sha256'] for ir in interpretations),'declarations':sorted(result_declarations.values(),key=lambda row:row['symbol_id']),'origins':sorted(origins,key=lambda row:row['canonical_id']),'sort_alignment':mapping,'alignment_bindings':sorted(alignment_bindings,key=lambda row:row['path']),'clauses':[{'namespace':digest([ir['source']['version_ref'],ir['scope']]),**remap_formula(clause,mapping)} for ir in sorted(interpretations,key=lambda row:row['ir_sha256']) for clause in ir['clauses']],'semantic_ready':False,'noncollapse':'not-assessed','claim_ceiling':'Exact nominal composition and selected carrier unions only; no population, equivalence, distinction, fidelity or theorem proof.'}
    return {**body,'ir_sha256':digest(body)}


def check_composed_formula(composed,node):
    if composed['ir_sha256']!=digest({key:value for key,value in composed.items() if key!='ir_sha256'}):raise IRFault('stale-composed-IR')
    c.bounded_tree(node)
    sorts={row['symbol_id']:row['symbol_id'] for row in composed['declarations'] if row['kind']=='sort'}
    symbols={row['symbol_id']:row for row in composed['declarations'] if row['kind']!='sort'}
    return formula(node,sorts,symbols)


def verify_composed(value,interpretations,selected_alignment_refs,root=None):
    """Compare against independently selected inputs and alignment records.

    A formula typechecks relative to a declared signature. This additional check
    is necessary when claiming that signature came from particular source IRs.
    """
    expected=compose(interpretations,selected_alignment_refs,root)
    if not r.same_json(value,expected):raise IRFault('composed-IR-input-or-alignment-substitution')
    return True
