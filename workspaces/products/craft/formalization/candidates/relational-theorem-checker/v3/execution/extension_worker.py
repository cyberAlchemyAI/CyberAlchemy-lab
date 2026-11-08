"""Raw input through checked extension witness, in the owned P06 worker group."""
from pathlib import Path
import hashlib
import json
import os
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from v3.execution.extension_runtime import load_extension,schema_validate
from v3.p03.context import BASE,C,binding,check,require,write,UnsupportedProfile
from v3.p06.worker_context import WorkerContext,ResourceExhausted
from v3.p07.cache import CacheAnchor

def qualify(extension,job):
    descriptor=C.decode((job/'supervision.json').read_bytes());policy=descriptor['policy']
    raw=(job/'request.raw').read_bytes();request=C.decode(raw)
    ctx=WorkerContext(job,policy);anchor=CacheAnchor('staged');ctx.trusted+=anchor.references;anchor.verify()
    mod=load_extension(extension)
    if hasattr(mod,'prevalidate'):mod.prevalidate(request)
    schema_validate(mod.SCHEMA,request)
    prepared=mod.normalize(request,ctx)
    build=job/'proof';build.mkdir()
    request_ref=write(job/'request.json',request)
    source_modules=mod.modules();require(len(source_modules)<=16,'extension module ceiling')
    for name,path in source_modules:
        ref=binding(path);ctx.trusted.append(ref)
        if path.parent!=BASE/extension.lower():
            receipt=C.decode((path.parent/'task-acceptance.json').read_bytes())
            require(ref in receipt['artifacts']+receipt['inputs'],'cross-extension module is not accepted/bound')
    logs=ctx.compile_default(build,source_modules)
    name=extension+'Witness_'+C.identity(request)[:20];source=build/(name+'.lean');source.write_text(mod.render(prepared))
    logs+=ctx.compile_default(build,[(name,source)])
    # A second actual compile without inherited environment, by the same kernel.
    replay=ctx.run_tool(['/usr/bin/env','-i','LEAN_PATH='+str(build),str(ctx.lean),str(source)],cwd=build)
    require(replay.returncode==0 and 'warning:' not in replay.stdout+replay.stderr and 'sorryAx' not in replay.stdout+replay.stderr,'extension same-kernel replay rejected')
    value=mod.result(prepared);schema_validate(mod.SCHEMA,value,True)
    ctx.assert_current();anchor.verify()
    return {'state':'unissued','extension':extension,'status':'checked','input_sha256':hashlib.sha256(raw).hexdigest(),
        'request_identity':C.identity(request),'request':request_ref,'value':value,'kernel':logs,'witness':binding(source),
        'imports':anchor.references+anchor.import_references+[binding(p) for _,p in source_modules]+prepared.get('source_bindings',[]),
        'scope':mod.SCOPE,'authority_effect':'none','application_authorized':False}

if __name__=='__main__':
    job=Path(os.environ['RELATIONAL_SUPERVISOR_JOB']).resolve();extension=sys.argv[1];os.umask(0o077)
    try:packet=qualify(extension,job)
    except Exception as e:packet={'state':'unissued','extension':extension,'status':'unknown-resource' if isinstance(e,ResourceExhausted) else 'unsupported' if isinstance(e,UnsupportedProfile) else 'invalid',
        'reason':str(e).splitlines()[0][:800],'authority_effect':'none','application_authorized':False}
    write(job/'candidate.json',packet)
