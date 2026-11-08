"""Read-only exact mapped-witness inspection in a dedicated interpreter."""
from pathlib import Path
import hashlib
import json
import sys
sys.dont_write_bytecode=True
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE.parents[0]))
from v3.p03.context import C,check,require
sys.path.insert(0,str(BASE.parent/'v2/s07'))
import stress_adapter as a
from jsonschema import Draft202012Validator

def inspect(request,result):
    Draft202012Validator(a.s.read(a.HERE/'interpretation.schema.json')).validate(request)
    edge=a.source_assertion(request);typed=a.map_input(request,edge)
    require(result['schema']=='relational.mapped-stress-result/v2','wrong mapped result schema')
    require(result['operation']==request['operation'] and result['status']==result['typed_result']['status'],'mapped operation/verdict mismatch')
    for field,value in [('request_identity',a.s.identity(request)),('source_identity',a.s.identity(request['baseline']['graph'])),('context_identity',a.s.identity(request['baseline']['context'])),('source_assertion',edge['id'])]:
        require(result[field]==value,'mapped identity mismatch '+field)
    deps=C.decode(check(result['dependencies']).read_bytes())['modules']
    require([m['source'] for m in deps]==[a.s.binding(p) for _,p in a.modules()],'mapped trusted source inventory mismatch')
    for m in deps:check(m['source']);check(m['olean'])
    require(len(result['kernel_evidence'])==1,'mapped witness module inventory')
    m=result['kernel_evidence'][0];source=check(m['source']);check(m['olean'])
    expected=a.witness_source(request,edge,typed,result['typed_result'])
    require(source.read_text()==expected and m['module']=='MappingWitness_'+a.s.identity(request)[:20],'displayed mapped values differ from concrete checked witness')
    truth=['supplied direct delegation/policy/gate truth','source endpoint kinds/registry selection tested boundary','source-bound typed interpretation truth','external condition evaluations are supplied, not arbitrary executable strings']
    require(result['truth_boundary']==truth and result['authority_effect']=='none','mapped truth/authority boundary changed')
    require(result['scope']=='one exact mapped source assertion, selected direct typed profile; no whole legacy graph qualification','mapped scope strengthened')
    out={'variant':request['operation'],'verdict':result['status'],'source_assertion':edge['id'],'claim_scope':result['scope'],'truth_assumptions':truth}
    if request['operation']=='inheritance':
        key=a.condition_key(request,typed['graph']['inheritances'][0]);status=a.condition_status(request['evaluations'],key)
        potential=result['typed_result'].get('facts',[])
        active=potential if result['status']=='yes' and status=='yes' else []
        conflicts=[[x,y] for x in active for y in active if x['norm']['mode']=='require' and y['norm']['mode']=='forbid' and x['norm']['action']==y['norm']['action']]
        values={'condition_key':key,'condition_status':status,'potential_norms':potential,'active_norms':active,'active_conflicts':conflicts,'fulfilled':'not-established','admission':'not-derived','potential_scope':'complete fixed mapped query' if result['status']=='yes' else 'unknown/incomplete mapped query','certificate_scope':'typed propagation witnesses retain origin; certificate alone does not establish complete-query/graph validity'}
        require(all(result[k]==v for k,v in values.items()),'mapped potential/active/conflict/fulfillment display changed')
        out.update(values)
    else:
        out['delegation']={'edge':typed['edge'],'action':typed['action'],'snapshot':typed['snapshot'],'redelegated':typed['redelegated']}
    # Raw typed-response certificates are not rendered: the concrete witness
    # binds the fields above, not every ancillary transport diagnostic.
    return out

if __name__=='__main__':
    try:
        wire=C.decode(sys.stdin.buffer.read());value=inspect(wire['request'],wire['result'])
        print(json.dumps({'ok':True,'value':value}))
    except Exception as e:
        print(json.dumps({'ok':False,'error':str(e).splitlines()[0]}));sys.exit(2)
