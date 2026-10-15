"""Read-only v2 normalization/inspection inside a dedicated interpreter.

Legacy imports are confined to this process. No v3 function is patched, no old
task runner/qualification/application is invoked, and no old evidence is written.
"""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode=True
V2=Path(__file__).resolve().parents[2]/'v2'
sys.path.insert(0,str(V2/'s06'))
import runtime as r


def inspect(proposal,result=None):
    classified=r.ext.classify(proposal['before'],proposal['after'])
    r.s.require(proposal['baseline_identity']==r.s.identity(proposal['before']),'baseline substitution')
    predicted=r.projection.predict(proposal['before'])
    r.s.require(not predicted['unhandled_kinds'],'unselected source meanings need a distinct stress profile')
    old=r.normal_with_observations(proposal['before'],predicted)
    new=r.normal_with_observations(proposal['after'],predicted)
    if result is not None:
        r.validate_receipt(proposal,result)
        r.s.require(result['before_normal_form']==old and result['normal_form']==new,'saved normal form/proposal mismatch')
        r.s.require(result['observations']==predicted['facts'] and result['supports']==predicted['supports'],'saved observation/support mismatch')
    return {'change_class':classified['change_class'],'before_normal_form':old,'normal_form':new,
        'observations':predicted['facts'],'supports':predicted['supports'],
        'projection_source':r.projection.witness_source(predicted),
        'runtime_sources':[r.s.binding(p) for _,p in r.module_list()],
        'bounds':r.resource.preflight(proposal['after']),
        'source_profile_identity':r.s.identity(r.ext.c.profile()),
        'authority_effect':'none'}


if __name__=='__main__':
    envelope=json.loads(sys.stdin.buffer.read())
    try:
        value=inspect(envelope['proposal'],envelope.get('result'))
        print(json.dumps({'ok':True,'value':value}))
    except Exception as e:
        print(json.dumps({'ok':False,'error':str(e).splitlines()[0],'error_type':type(e).__name__}))
        sys.exit(2)
