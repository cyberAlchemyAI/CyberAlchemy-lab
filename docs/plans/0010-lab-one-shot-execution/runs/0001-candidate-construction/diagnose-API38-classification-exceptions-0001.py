"""Trace exception locations from one actual public call, without exception values."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v38'
COMPOSITION=API.parent/'classification-preparation-v3'
SOURCE='7a7803987956c8935926b0ea608c3e114f92405e418adccbf72dfc5e2467ab7c'
PROFILE='ea982bcdcecc095b37d99b52fd545608fbe8740214af53391c865e61ea7b3f5b'


def bind(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input-sha256',required=True)
    args=parser.parse_args();inputs=RUN/'API38-classification-exception-inputs-0001.json'
    assert bind(inputs)['sha256']==args.input_sha256
    for row in json.loads(inputs.read_bytes())['files']:
        assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    name='_cal_API38_actual_exception_diagnostic_0001'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    guard=__import__(name+'.guard',fromlist=['verify']);guard.verify(SOURCE)
    assert bind(API/'contract-profile.json')['sha256']==PROFILE
    protocol=__import__(name+'.protocol',fromlist=['Schemas'])
    fixture=__import__(name+'.classification_fixture',fromlist=['example'])
    schemas=protocol.Schemas(PROFILE);observed=[];started=time.monotonic()
    watched=(str(API.parent)+'/',str(ROOT/'implementation/lab-runtime')+'/')
    def exceptions(frame,event,arg):
        if event=='exception':
            kind=arg[0]
            row={'source':str(Path(frame.f_code.co_filename).relative_to(ROOT)),
                 'function':frame.f_code.co_name,'line':frame.f_lineno,'exception_class':kind.__name__}
            if row not in observed:
                observed.append(row);print(json.dumps({'actual_exception_location':row}),flush=True)
        return exceptions
    def calls(frame,event,arg):
        if frame.f_code.co_filename.startswith(watched):
            frame.f_trace_lines=False;frame.f_trace_opcodes=False
            return exceptions
        return None
    print(json.dumps({'stage':'actual-schemas-ready'}),flush=True)
    with protocol.source.replay_source('custody-participation') as view:
        print(json.dumps({'stage':'actual-source-replayed'}),flush=True)
        with fixture.example(view,schemas) as (host,request,selected):
            owned_root=selected['root'];raw=protocol.compact(request)
            print(json.dumps({'stage':'actual-owned-host-ready'}),flush=True)
            assert sys.gettrace() is None
            sys.settrace(calls)
            try:reply=host.call(raw)
            finally:sys.settrace(None)
            public={k:reply[k] for k in ('schema_version','kind','code') if k in reply}
            if reply.get('kind')=='error':public['domain_error_code']=reply['message']['code']
            print(json.dumps({'stage':'actual-public-reply','public_fields':public}),flush=True)
    assert not owned_root.exists();guard.verify(SOURCE)
    value={'schema_version':'lab-classification-public-exception-diagnostic/v1-candidate',
        'result':'OBSERVED','source_binding':bind(API/'source-manifest.json'),
        'profile_binding':bind(API/'contract-profile.json'),'input_binding':bind(inputs),
        'actual_public_calls':1,'public_reply_fields':public,'exception_locations':observed,
        'request_sha256':hashlib.sha256(raw).hexdigest(),
        'reply_sha256':hashlib.sha256(protocol.compact(reply)).hexdigest(),
        'owned_workspace_removed':True,'private_values_or_memory_exported':False,
        'elapsed_seconds':time.monotonic()-started,'original_test_methods_invoked':0,
        'clock_replaced':False,'source_callbacks_replaced':False,'time_bounds_extended':False,
        'diagnostic_exception_tracing_enabled':True,'timing_qualification':False,
        'whole_API_qualified':False,'current_Agent_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
    with (RUN/'API38-classification-exception-diagnostic-0001.json').open('x') as stream:
        json.dump(value,stream,sort_keys=True,indent=2);stream.write('\n')
    print(json.dumps({'result':'OBSERVED','owned_workspace_removed':True,'public_fields':public}),flush=True)


if __name__=='__main__':main()
