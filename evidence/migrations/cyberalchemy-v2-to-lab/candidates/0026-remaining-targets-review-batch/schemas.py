from catalog import TYPES, LIFECYCLES, EVALUATIONS
TEXT={'type':'string','pattern':r'\S'}
BOOL={'type':'boolean'}
NUMBER={'type':'number'}
HASH={'type':'string','pattern':'^[0-9a-f]{64}$'}
def obj(p): return {'type':'object','additionalProperties':False,'required':sorted(p),'properties':p}
def array(item=TEXT,minimum=1,maximum=100): return {'type':'array','minItems':minimum,'maxItems':maximum,'items':item}
def strings(minimum=1): return {**array(TEXT,minimum),'uniqueItems':True}
def field(kind):
    if kind.startswith('id:'): return TEXT
    if kind.startswith('ids:'): return strings()
    if kind.startswith('ids0:'): return strings(0)
    return {'text':TEXT,'list':strings(),'list0':strings(0),'number':NUMBER,'nonnegative':{'type':'number','minimum':0},'nonnegative-int':{'type':'integer','minimum':0},'positive-int':{'type':'integer','minimum':1},'membership':{'enum':['active','ended']},'time':{'type':'string','format':'date-time'},'period':obj({'start':{'type':'string','format':'date-time'},'end':{'anyOf':[{'type':'string','format':'date-time'},{'type':'null'}]}})}[kind]
def record_schema(name):
    return {'$schema':'https://json-schema.org/draft/2020-12/schema',**obj({'node_id':TEXT,'kind':{'const':name},'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},'scope_ref':TEXT,'owner_ref':TEXT,**{k:field(v) for k,v in TYPES[name].items()}})}
def profile_shapes(name):
    scope={'scope_ref':TEXT}
    if name in LIFECYCLES:
        p={**scope,'states':strings(),'transitions':array({'type':'array','minItems':2,'maxItems':2,'items':TEXT}),'owner_route':TEXT,'gate_ref':TEXT}
        q={**scope,'from_state':TEXT,'to_state':TEXT,'owner_route':TEXT,'gate_ref':TEXT,'gate_passed':BOOL,'evidence_refs':strings(0)}
    elif name in EVALUATIONS:
        p={**scope,'required_checks':strings()}; q={**scope,'checks':{'type':'object','additionalProperties':BOOL}}
    else:
        p,q={
'repository-layout-policy':({'allowed_roots':strings()},{'paths':strings(0)}),
'source-selection-policy':({'allowed_sources':strings(),'allowed_postures':strings(),'max_sources':{'type':'integer','minimum':1}},{'sources':array(obj({'source_id':TEXT,'posture':TEXT}),0)}),
'authority-aware-navigation':({'visible_postures':strings()},{'nodes':array(obj({'node_id':TEXT,'posture':TEXT}),0)}),
'challenge':({'modes':strings(),'owner_route':TEXT},{'mode':TEXT,'evidence_refs':strings(0)}),
'retention':({'minimum_days':{'type':'integer','minimum':0}},{'recorded_at':field('time'),'as_of':field('time'),'legal_hold':BOOL,'permanently_reserved':BOOL}),
'semantic-consistency':({'identity_key':{'const':'definition_id+version'}},{'definitions':array(obj({'definition_id':TEXT,'version':TEXT,'sha256':HASH}),0)}),
'publication':({'artifact_sha256':HASH,'destination':TEXT,'actor_ref':TEXT,'operation':{'const':'publish'}},{'artifact_sha256':HASH,'destination':TEXT,'actor_ref':TEXT,'operation':TEXT,'decision_ref':{'type':'string'},'approved':BOOL}),
'cross-context-generalization':({'source_context':TEXT,'target_context':TEXT},{'source_context':TEXT,'target_context':TEXT,'assumptions_checked':BOOL,'counterevidence_reviewed':BOOL,'evidence_refs':strings(0)}),
'context-resolution':({'allowed_anchor_kinds':strings(),'minimum_anchors':{'type':'integer','minimum':0},'maximum_anchors':{'type':'integer','minimum':1},'maximum_budget':{'type':'integer','minimum':1}},{'anchors':array(obj({'id':TEXT,'kind':TEXT}),0),'requested_budget':{'type':'integer','minimum':1}}),
'recursion':({'maximum_depth':{'type':'integer','minimum':1}},{'depth':{'type':'integer','minimum':0},'ancestor_ids':array(TEXT,0),'current_id':TEXT,'remaining_budget':{'type':'integer'}})
        }[name]; p={**scope,**p}; q={**scope,**q}
    return obj(p),obj(q)
