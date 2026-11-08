"""Finite worked-example interpreter, not the production IR/provider.

Models have exact nonempty named domains, fixed total functions/constants and
either fixed or exhaustively enumerated predicate extensions. Every reported
witness is a complete interpretation of this declared signature. Exhausted
absence is explicitly bounded. Source prose fidelity is outside this module.
"""
from itertools import product


class Malformed(ValueError):
    pass


class Unsupported(ValueError):
    pass


def variable(name): return {"op":"var", "name":name}
def constant(name): return {"op":"const", "name":name}
def function(name,*args): return {"op":"fn", "name":name, "args":list(args)}
def predicate(name,*args): return {"op":"pred", "name":name, "args":list(args)}
def conjunction(*args): return {"op":"and", "args":list(args)}
def disjunction(*args): return {"op":"or", "args":list(args)}
def negate(arg): return {"op":"not", "arg":arg}
def implication(left,right): return {"op":"implies", "left":left,"right":right}
def equivalence(left,right): return {"op":"iff", "left":left,"right":right}
def equality(left,right): return {"op":"eq", "left":left,"right":right}
def forall(name,sort,body): return {"op":"forall", "var":name,"sort":sort,"body":body}
def exists(name,sort,body): return {"op":"exists", "var":name,"sort":sort,"body":body}


def shape(node,keys):
    if not isinstance(node,dict) or set(node)!=set(keys):
        raise Malformed("Unknown/missing AST fields")


def validate_signature(signature):
    if set(signature)!={"domains","constants","functions","predicates","fixed_predicates"}:
        raise Malformed("Unknown/missing signature fields")
    domains=signature["domains"]
    for name,values in domains.items():
        if not name or not values or len(values)!=len(set(values)):
            raise Malformed("Core sort domains must be nonempty and unique")
    symbols=list(signature["constants"])+list(signature["functions"])+list(signature["predicates"])
    if len(symbols)!=len(set(symbols)):
        raise Malformed("Ambiguous symbol identity")
    for name,(sort,value) in signature["constants"].items():
        if sort not in domains or value not in domains[sort]:
            raise Malformed("Invalid constant interpretation")
    for name,(arguments,result,table) in signature["functions"].items():
        if any(sort not in domains for sort in [*arguments,result]):
            raise Malformed("Unbound function sort")
        tuples=set(product(*(domains[s] for s in arguments)))
        if set(table)!=tuples or any(v not in domains[result] for v in table.values()):
            raise Malformed("Function interpretation must be total and typed")
    for name,arguments in signature["predicates"].items():
        if any(sort not in domains for sort in arguments):
            raise Malformed("Unbound predicate sort")
    for name,extension in signature["fixed_predicates"].items():
        if name not in signature["predicates"]:
            raise Malformed("Unknown fixed predicate")
        allowed=set(product(*(domains[s] for s in signature["predicates"][name])))
        if not set(extension)<=allowed:
            raise Malformed("Ill-typed predicate interpretation")


def term_sort(node,signature,env):
    op=node.get("op") if isinstance(node,dict) else None
    if op in {"var","const"}:
        shape(node,{"op","name"})
        table=env if op=="var" else signature["constants"]
        if node["name"] not in table:raise Malformed("Unbound term")
        return table[node["name"]] if op=="var" else table[node["name"]][0]
    if op=="fn":
        shape(node,{"op","name","args"})
        if node["name"] not in signature["functions"]:raise Malformed("Unknown function")
        arguments,result,_=signature["functions"][node["name"]]
        if len(node["args"])!=len(arguments):raise Malformed("Function arity")
        if [term_sort(a,signature,env) for a in node["args"]]!=arguments:raise Malformed("Function argument type")
        return result
    if not isinstance(op,str):raise Malformed("Missing/invalid term operator")
    raise Unsupported("Term outside the selected static core")


def validate_formula(node,signature,env=None):
    env={} if env is None else env
    op=node.get("op") if isinstance(node,dict) else None
    if op=="pred":
        shape(node,{"op","name","args"})
        if node["name"] not in signature["predicates"]:raise Malformed("Unknown predicate")
        arguments=signature["predicates"][node["name"]]
        if len(arguments)!=len(node["args"]):raise Malformed("Predicate arity")
        if [term_sort(a,signature,env) for a in node["args"]]!=arguments:raise Malformed("Predicate argument type")
    elif op=="eq":
        shape(node,{"op","left","right"})
        if term_sort(node["left"],signature,env)!=term_sort(node["right"],signature,env):raise Malformed("Unaligned equality")
    elif op=="not":
        shape(node,{"op","arg"});validate_formula(node["arg"],signature,env)
    elif op in {"and","or"}:
        shape(node,{"op","args"})
        if not isinstance(node["args"],list):raise Malformed("Connective arguments")
        for arg in node["args"]:validate_formula(arg,signature,env)
    elif op in {"implies","iff"}:
        shape(node,{"op","left","right"})
        validate_formula(node["left"],signature,env);validate_formula(node["right"],signature,env)
    elif op in {"forall","exists"}:
        shape(node,{"op","var","sort","body"})
        if node["sort"] not in signature["domains"]:raise Malformed("Unbound quantifier sort")
        nested=dict(env);nested[node["var"]]=node["sort"]
        validate_formula(node["body"],signature,nested)
    else:
        if not isinstance(op,str):raise Malformed("Missing/invalid formula operator")
        raise Unsupported("Formula outside the selected static core")


def interpret_term(node,signature,env):
    if node["op"]=="var":return env[node["name"]]
    if node["op"]=="const":return signature["constants"][node["name"]][1]
    args=tuple(interpret_term(a,signature,env) for a in node["args"])
    return signature["functions"][node["name"]][2][args]


def satisfies(node,signature,interpretation,env=None):
    env={} if env is None else env
    op=node["op"]
    if op=="pred":return tuple(interpret_term(a,signature,env) for a in node["args"]) in interpretation[node["name"]]
    if op=="eq":return interpret_term(node["left"],signature,env)==interpret_term(node["right"],signature,env)
    if op=="not":return not satisfies(node["arg"],signature,interpretation,env)
    if op=="and":return all(satisfies(a,signature,interpretation,env) for a in node["args"])
    if op=="or":return any(satisfies(a,signature,interpretation,env) for a in node["args"])
    if op=="implies":return not satisfies(node["left"],signature,interpretation,env) or satisfies(node["right"],signature,interpretation,env)
    if op=="iff":return satisfies(node["left"],signature,interpretation,env)==satisfies(node["right"],signature,interpretation,env)
    domain=signature["domains"][node["sort"]]
    outcomes=(satisfies(node["body"],signature,interpretation,{**env,node["var"]:value}) for value in domain)
    return all(outcomes) if op=="forall" else any(outcomes)


def models(signature):
    slots=[]
    for name,arguments in signature["predicates"].items():
        if name not in signature["fixed_predicates"]:
            slots.extend((name,args) for args in product(*(signature["domains"][s] for s in arguments)))
    for bits in product((False,True),repeat=len(slots)):
        interpretation={name:set(extension) for name,extension in signature["fixed_predicates"].items()}
        for name in signature["predicates"]:interpretation.setdefault(name,set())
        for (name,args),bit in zip(slots,bits):
            if bit:interpretation[name].add(args)
        yield interpretation


def serialize_model(interpretation):
    return {name:[list(row) for row in sorted(extension)] for name,extension in interpretation.items()}


def search(signature,formulas,model_limit=None,cancelled=None):
    validate_signature(signature)
    for formula in formulas:validate_formula(formula,signature)
    examined=0
    for interpretation in models(signature):
        if cancelled and cancelled():return {"outcome":"cancelled","examined":examined,"exhausted":False}
        if model_limit is not None and examined>=model_limit:return {"outcome":"resource-limit","examined":examined,"exhausted":False}
        examined+=1
        if all(satisfies(f,signature,interpretation) for f in formulas):
            return {"outcome":"finite-sat","examined":examined,"exhausted":False,"model":serialize_model(interpretation),"meaning":"A complete model of these exact formulas under the declared finite profile."}
    return {"outcome":"bounded-unsat","examined":examined,"exhausted":True,"meaning":"No model in this exact finite profile; no unbounded absence claim."}


def assemble(clauses,target_id=None):
    """Role control for worked cases, not a generic theorem/premise checker."""
    assumptions=[]
    for clause in clauses:
        if clause["id"]==target_id and clause["selected"]:raise Malformed("Target cannot be its own selected premise")
        role=clause["role"]
        if role in {"selected-axiom","selected-premise","constraint"} and clause["selected"]:
            assumptions.append(clause["formula"])
        elif role=="definition" and clause["selected"]:
            assumptions.append(clause["formula"])
        elif role in {"hypothesis","proof-obligation","explanation-example"} and clause["selected"]:
            raise Malformed("Investigation/target/explanation cannot be silently assumed")
    return assumptions


def bounded_entailment(signature,theory,target,populations=()):
    consistency=search(signature,theory)
    if consistency['outcome']!='finite-sat':
        return {"outcome":"inconsistent-or-unresolved-premises","consistency":consistency}
    inhabited=search(signature,[*theory,*populations])
    if inhabited['outcome']!='finite-sat':
        return {"outcome":"vacuous-or-unresolved-populations","inhabitation":inhabited}
    counter=search(signature,[*theory,*populations,negate(target)])
    return {"outcome":"counterexample" if counter['outcome']=='finite-sat' else "bounded-valid", "counterexample_search":counter,
            "meaning":"Exact finite-profile entailment control; not a general unbounded theorem."}


def least_reachable(initial,edges):
    reached=set(initial)
    while True:
        successor=reached|{target for source,target in edges if source in reached}
        if successor==reached:return reached
        reached=successor
