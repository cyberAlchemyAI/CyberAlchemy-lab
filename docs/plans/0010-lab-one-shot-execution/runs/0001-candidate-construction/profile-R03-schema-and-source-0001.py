"""Bounded passive CPU profiling of schema construction and owned source replay.

No frame locals, signing keys, Agent resources or Session RAM are inspected.
Original functions, source callbacks, permissions and clocks are unchanged.
"""
import argparse
import cProfile
import hashlib
import importlib.util
import json
from pathlib import Path
import pstats
import sys
import time

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v35'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--observer-source-sha256',required=True)
    parser.add_argument('--source-sha256',required=True)
    parser.add_argument('--profile-sha256',required=True)
    args=parser.parse_args()
    own=RUN/'schema-and-source-profile-inputs-0001.json'
    assert hashlib.sha256(own.read_bytes()).hexdigest()==args.observer_source_sha256
    for row in json.loads(own.read_bytes())['files']:
        assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256']
    spec=importlib.util.spec_from_file_location('_cal_profile_selected_guard',API/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    guard.verify(args.source_sha256)
    assert hashlib.sha256((API/'contract-profile.json').read_bytes()).hexdigest()==args.profile_sha256
    name='_cal_schema_source_profile_api35'
    spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    P=__import__(name+'.protocol',fromlist=['*'])
    phases=[]
    def measured(label,operation):
        profile=cProfile.Profile();started=time.perf_counter()
        profile.runcall(operation)
        elapsed=time.perf_counter()-started
        stats=pstats.Stats(profile)
        rows=[]
        for (path,line,function),(primitive,calls,own_time,cumulative,_) in stats.stats.items():
            rows.append({'source':path,'line':line,'function':function,'primitive_calls':primitive,
                         'total_calls':calls,'own_seconds':own_time,'cumulative_seconds':cumulative})
        phases.append({'phase':label,'elapsed_seconds':elapsed,
                       'top_cumulative_functions':sorted(rows,key=lambda row:row['cumulative_seconds'],reverse=True)[:40]})
        output=RUN/('schema-and-source-profile-'+label+'-0001.json')
        with output.open('x') as stream:
            json.dump({'result':'OBSERVED','phases':phases,'source_sha256':args.source_sha256,
                       'profile_sha256':args.profile_sha256,'scope':'passive profiler adds measurement overhead; no end-to-end latency claim',
                       'private_frame_values_inspected':False,'runtime_qualification':False,
                       'authority_effect':'none','actual_owner_outcome':None},stream,sort_keys=True,indent=2)
            stream.write('\n')
        print(json.dumps({'phase':label,'elapsed_seconds':elapsed,'report':str(output.relative_to(ROOT))}),flush=True)
    measured('schemas',lambda:P.Schemas(args.profile_sha256))
    def replay():
        with P.source.replay_source('custody-participation') as view:
            view.custody_signed_sources.guard()
    measured('source',replay)
    guard.verify(args.source_sha256)
    print(json.dumps({'result':'OBSERVED','phases':len(phases),'runtime_qualification':False}),flush=True)


if __name__=='__main__':main()
