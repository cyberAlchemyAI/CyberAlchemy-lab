"""Typed selected-profile queries and bounded source-inspected explanations."""
from pathlib import Path
import copy
import hashlib
import json
import subprocess
import sys
from jsonschema import Draft202012Validator,ValidationError
from ..p03 import QualificationContext,inspect_saved
from ..p03.context import C,BASE,ROOT,check,require
HERE=Path(__file__).resolve().parent

def bound_read(ref):
    path=check(ref);raw=path.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==ref['sha256'],'bound payload changed during read')
    return C.decode(raw)

def schema(name):return json.loads((HERE/(name+'.schema.json')).read_text())
def value_text(v):return v['id']+'@'+v['version'] if v['kind']=='reference' else str(v['value'])
def atom_text(a):return a['predicate']['id']+'('+', '.join(value_text(v) for v in a['values'])+')'

def classify_query(normal,closure,complete,query):
    try:Draft202012Validator(schema('query')).validate(query)
    except ValidationError:return 'invalid-query','Malformed atom, predicate key or value.'
    declaration=next((p for p in normal['predicates'] if {k:p[k] for k in ['id','version','hash']}==query['predicate']),None)
    if declaration is None:return 'outside-profile','Exact predicate identity/version/digest is outside this profile.'
    if len(query['values'])!=len(declaration['sorts']) or [v['kind'] for v in query['values']]!=declaration['sorts']:
        return 'invalid-query','Predicate arity or ordered value sorts do not match.'
    if any(v not in normal['domain'] for v in query['values']):return 'outside-profile','A value is outside the declared finite domain.'
    if not complete:return 'incomplete','No checked complete closure is available.'
    if query in closure:return 'present','Present in the inspected complete selected closure.'
    return 'absent-in-complete-profile','Well-typed atom is absent from the inspected complete selected closure; it has no derivation from these fixed supplied facts in this positive profile.'

def certificate_trace(payload,query,limit):
    steps=payload['certificates'];positions={C.identity(s['conclusion']):i for i,s in enumerate(steps)}
    require(len(positions)==len(steps),'ambiguous duplicate certificate conclusions')
    root=positions.get(C.identity(query));require(root is not None,'missing query certificate')
    pending=[root];nodes={};omitted=set();supports=[]
    while pending:
        index=pending.pop()
        if index in nodes:continue
        if len(nodes)>=limit:omitted.add(index);continue
        require(type(index) is int and 0<=index<len(steps),'invalid certificate index')
        step=steps[index];atom=step['conclusion']
        node={'index':index,'atom':atom,'kind':step['kind'],'rule':None,'substitution':[],'premises':[],'leaf':None,'supports':[],'truth':None}
        if step['kind']=='base':
            selected=[s for s in payload['supports'] if s['atom']==atom]
            node.update(leaf='source-observation' if selected else 'independent-root' if atom['predicate']['id']=='CheckedRoot' else 'supplied-truth',supports=selected,truth='Source membership/endpoints/revision/scope are checked; accepted assessment truth is supplied.' if selected else 'Independent root or ordinary initial truth is supplied; this explanation does not authenticate its issuer.')
            for support in selected:
                if support not in supports:supports.append(support)
        else:
            require(step['kind']=='apply','unknown certificate step')
            instance=step['instance'];indices=step['indices']
            require(instance['head']==atom and len(indices)==len(instance['body']),'certificate conclusion/body mismatch')
            require(all(type(i) is int and 0<=i<index for i in indices),'forward/cyclic certificate premise')
            require([steps[i]['conclusion'] for i in indices]==instance['body'],'certificate premise/instance mismatch')
            rule=next((r for r in payload['normal_form']['rules'] if {k:r[k] for k in ['id','version','hash']}==instance['rule']),None)
            require(rule is not None and len(rule['variables'])==len(instance['substitution']),'unknown rule or substitution shape')
            node.update(rule=instance['rule'],substitution=[{'slot':i,'sort':rule['variables'][i]['sort'],'value':v} for i,v in enumerate(instance['substitution'])],premises=indices)
            pending.extend(reversed(indices))
        nodes[index]=node
    omitted-=set(nodes)
    return {'root':root,'nodes':list(nodes.values()),'truncated':bool(omitted),'omitted_indices':sorted(omitted)},supports

def finish(out,output_bytes):
    Draft202012Validator(schema('explanation')).validate(out)
    if len(json.dumps(out,ensure_ascii=False,allow_nan=False).encode())>output_bytes:
        return finish({'schema':'relational.explanation/v3','variant':'recursive','outcome':'incomplete','inspection':'incomplete','claim_scope':'Rendering envelope only; no absence or readiness claim.','truth_assumptions':[],'model_class':None,'trace':None,'supports':[],'source_support_count':0,'text':'Explanation exceeded its output-byte limit. No absence or application claim is emitted.','application_authorized':False,'authority_effect':'none'},output_bytes)
    return out

def describe(request,result,query=None,context=None,trace_nodes=256,output_bytes=32768):
    require(type(trace_nodes) is int and 1<=trace_nodes<=4096,'invalid trace node limit')
    require(type(output_bytes) is int and 1024<=output_bytes<=8388608,'invalid explanation output-byte limit')
    request=copy.deepcopy(request);result=copy.deepcopy(result)
    if result.get('schema')=='relational.mapped-stress-result/v2':
        require(query is None,'Mapped typed verdicts do not accept recursive atom queries.')
        worker=subprocess.run([sys.executable,str(HERE/'mapping_worker.py')],input=json.dumps({'request':request,'result':result}),capture_output=True,text=True,timeout=60)
        checked=C.decode(worker.stdout.encode());require(worker.returncode==0 and checked['ok'],checked.get('error','mapped inspection failed'))
        out=checked['value'];out.update(schema='relational.explanation/v3',inspection='recorded-current',application_authorized=False,authority_effect='none')
        if out['variant']=='inheritance':
            out['text']=f"Mapped propagation verdict: {out['verdict']}; condition verdict: {out['condition_status']}. {len(out['potential_norms'])} potential norms, {len(out['active_norms'])} active norms and {len(out['active_conflicts'])} active conflicts. Origins retain the exact binding, contract revision, subject and scope. Fulfillment is not established; admission is not derived. Supplied evaluations remain truth assumptions."
        else:out['text']='Exact mapped delegation verdict: '+out['verdict']+'. Agent, principal, delegation revision, action, scope and epoch are shown. Policy/gate truth is supplied; this direct profile provides no chain or whole-graph qualification.'
        return finish(out,output_bytes)
    C.validate('request',request);C.validate('result',result)
    require(result['request_identity']==C.identity(request),'explanation request mismatch')
    require(result['resource_report']['policy_identity']==C.identity(request['resource_policy']),'explanation resource-policy mismatch')
    context=context or QualificationContext(HERE/'inspection-runs',request['resource_policy'])
    out={'schema':'relational.explanation/v3','variant':'recursive','outcome':'incomplete','inspection':'incomplete','claim_scope':'Incomplete computation; no complete closure, absence or readiness claim.','truth_assumptions':[],'model_class':None,'trace':None,'supports':[],'source_support_count':0,'text':str(result.get('reason','No complete inspected result.'))[:160],'application_authorized':False,'authority_effect':'none'}
    if result['status']!='qualified-candidate':
        if query is not None:
            try:
                Draft202012Validator(schema('query')).validate(query)
            except ValidationError:
                out['outcome']='invalid-query';out['text']='Malformed query; no complete computation is available.'
            else:
                try:info=context.boundary(request['proposal'])
                except (ValueError,subprocess.TimeoutExpired):pass
                else:out['outcome'],out['text']=classify_query(info['normal_form'],[],False,query)
        return finish(out,output_bytes)
    inspect_saved(request,result,context)
    payload=bound_read(result['payload'])
    out.update(inspection='recorded-current',claim_scope=payload['closure_scope'],truth_assumptions=result['claims'][0]['truth_assumptions'],model_class=payload['model_class'],source_support_count=len(payload['supports']),outcome='summary',text='Inspected recorded evidence for the complete selected finite positive Horn closure. Every-old-model expansion is a separate theorem; saved inspection grants no fresh application replay.')
    if query is not None:
        out['outcome'],out['text']=classify_query(payload['normal_form'],payload['closure'],True,query)
        if out['outcome']=='present':
            out['trace'],out['supports']=certificate_trace(payload,query,trace_nodes)
            out['text']+=' Exact rule substitutions and source/supplied leaves are shown.'
            if out['trace']['truncated']:out['text']+=' Trace rendering was bounded; omitted premise indices are explicit. The inspected closure itself was complete.'
    context.assert_current()
    return finish(out,output_bytes)
