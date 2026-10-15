"""Fresh exact mapped witness, bounded by the unchanged supervisor policy."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.p03.context import BASE,V2,C,check,read,binding,require,write
from v3.p06.worker_context import WorkerContext,ToolExhausted,ResourceExhausted
from v3.p07.cache import CacheAnchor
from v3.p04.mapping_worker import a,inspect
from jsonschema import Draft202012Validator

def qualify(job,raw):
    wire=C.decode(raw);require(set(wire)=={'request','resource_policy'},'mapped envelope fields')
    request=wire['request'];policy=wire['resource_policy']
    ctx=WorkerContext(job,policy);cache=CacheAnchor('staged')
    ctx.trusted += cache.references
    report=read(check(cache.closure_expected))
    expected={r['path']:r for r in report['verified_bindings'] if r['kind']=='repo'}
    dep_path=V2/'s07/build/dependencies.json'
    dep_ref=expected[binding(dep_path)['path']]
    check(dep_ref);deps=read(dep_path)['modules']
    require([m['source'] for m in deps]==[binding(p) for _,p in a.modules()],'exact mapped import inventory')
    build=job/'mapped-build';build.mkdir()
    copied=[]
    for m in deps:
        for key in ['source','olean']:
            ref=m[key];require(expected.get(ref['path'],{}).get('sha256')==ref['sha256'],'mapped dependency lacks independent P05 anchor')
            check(ref);ctx.trusted.append(ref)
        dst=build/(m['module']+'.olean');shutil.copyfile(check(m['olean']),dst)
        require(binding(dst)['sha256']==m['olean']['sha256'],'mapped cache copy differs')
        copied.append({**m,'olean':binding(dst)})
    write(build/'dependencies.json',{'modules':copied,'anchor':dep_ref,'imported_toolchain_anchor':cache.closure_expected})
    Draft202012Validator(read(a.HERE/'interpretation.schema.json')).validate(request)
    edge=a.source_assertion(request);typed=a.map_input(request,edge)
    ctx.assert_current();cache.verify()
    query=build/('TypedQuery_'+C.identity(request)[:20]+'.lean');query.write_text(a.typed.query_source(typed))
    evaluation=ctx.run_tool([str(ctx.lean),'--run',str(query)],cwd=build,env=ctx.environment(build))
    require(evaluation.returncode==0,'typed mapped evaluation failed')
    response=C.decode(evaluation.stdout.encode())
    source=build/('MappingWitness_'+C.identity(request)[:20]+'.lean');source.write_text(a.witness_source(request,edge,typed,response))
    logs=ctx.compile_default(build,[(source.stem,source)])
    # Recompile the exact concrete witness in an empty environment using the
    # same pinned kernel. This is fresh replay, not an independent checker.
    replay=ctx.run_tool(['/usr/bin/env','-i','LEAN_PATH='+str(build),str(ctx.lean),str(source)],cwd=build)
    require(replay.returncode==0 and 'sorryAx' not in replay.stdout+replay.stderr and 'warning:' not in replay.stdout+replay.stderr,'mapped same-kernel replay failed')
    out={'schema':'relational.mapped-stress-result/v2','operation':request['operation'],'status':response['status'],
         'source_assertion':edge['id'],'request_identity':C.identity(request),'source_identity':C.identity(request['baseline']['graph']),
         'context_identity':C.identity(request['baseline']['context']),'typed_result':response,'kernel_evidence':logs,
         'dependencies':binding(build/'dependencies.json'),'truth_boundary':['supplied direct delegation/policy/gate truth','source endpoint kinds/registry selection tested boundary','source-bound typed interpretation truth','external condition evaluations are supplied, not arbitrary executable strings'],
         'scope':'one exact mapped source assertion, selected direct typed profile; no whole legacy graph qualification','human_review':'pending','authority_effect':'none'}
    if request['operation']=='inheritance':
        key=a.condition_key(request,typed['graph']['inheritances'][0]);status=a.condition_status(request['evaluations'],key)
        potential=response.get('facts',[]);active=potential if response['status']=='yes' and status=='yes' else []
        conflicts=[[x,y] for x in active for y in active if x['norm']['mode']=='require' and y['norm']['mode']=='forbid' and x['norm']['action']==y['norm']['action']]
        out.update(condition_status=status,condition_key=key,potential_norms=potential,active_norms=active,active_conflicts=conflicts,
                   potential_scope='complete fixed mapped query' if response['status']=='yes' else 'unknown/incomplete mapped query',
                   fulfilled='not-established',admission='not-derived',certificate_scope='typed propagation witnesses retain origin; certificate alone does not establish complete-query/graph validity')
    inspected=inspect(request,out);ctx.assert_current();cache.verify()
    write(job/'mapped-request.json',request);write(job/'mapped-result.json',out)
    packet={'schema':'relational.unissued-mapped-check/v3','state':'unissued','request_bytes_sha256':hashlib.sha256(raw).hexdigest(),
            'policy_identity':C.identity(policy),'request_identity':C.identity(request),'request':binding(job/'mapped-request.json'),
            'result':binding(job/'mapped-result.json'),'inspection':inspected,'replay':'fresh-same-pinned-kernel',
            'dependencies':binding(build/'dependencies.json'),'authority_effect':'none','application_authorized':False}
    return packet

if __name__=='__main__':
    job=Path(os.environ['RELATIONAL_SUPERVISOR_JOB']).resolve();os.umask(0o077)
    try:packet=qualify(job,(job/'request.raw').read_bytes())
    except Exception as e:
        packet={'schema':'relational.mapped-worker-refusal/v3','state':'unissued','status':'unknown-resource' if isinstance(e,(ResourceExhausted,a.resource.Exhausted)) else 'invalid',
                'reason':str(e).splitlines()[0][:500],'authority_effect':'none','application_authorized':False}
    with (job/'candidate.json').open('x') as f:json.dump(packet,f,allow_nan=False)
