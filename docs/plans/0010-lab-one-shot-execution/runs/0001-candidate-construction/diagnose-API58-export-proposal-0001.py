"""Inspect the actual refused export proposal through unchanged change.validate."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-v58'
SOURCE='81385b39c851ddc257bfc898c150cf341bff923052fdd2ccaedcb8edc0d8b5dd'
PROFILE='5241a152708be5bc84f727ef404d749a14a0b532a6315b8d2d43adb78bfa69e3'
def bind(path):return {'path':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def main():
    name='_cal_API58_export_diagnostic';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)])
    package=importlib.util.module_from_spec(spec);sys.modules[name]=package;spec.loader.exec_module(package)
    guard=__import__(name+'.guard',fromlist=['verify']);guard.verify(SOURCE)
    P=__import__(name+'.protocol',fromlist=['Schemas'])
    F=__import__(name+'.package_export_fixture',fromlist=['example'])
    schemas=P.Schemas(PROFILE)
    with P.source.replay_source('custody-participation') as view:
        before=P.compact(view.data['projection'])
        with F.example(view,schemas) as (host,export,selected):
            call=F.MF.call(host.channel.context,'lab.status',export['expected_source_cut'])
            call.update(operation='change.validate',idempotency_key=F.KEY,
                message=P.frame_parse(host.vault.object_read(selected['proposal_binding'])))
            raw=P.compact(call);reply=host.call(raw)
            observed={'schema_version':'lab-export-proposal-diagnostic/v1-candidate','source_sha256':SOURCE,
                'profile_sha256':PROFILE,'request':call,'reply':reply,'public_export_attempted':False,
                'authority_effect':'none','actual_owner_outcome':None,'task_complete':False,'goal_complete':False}
            assert P.compact(view.data['projection'])==before
        assert not selected['root'].exists()
    guard.verify(SOURCE)
    path=RUN/'API58-export-proposal-diagnostic-0001.json'
    with path.open('x') as stream:json.dump(observed,stream,indent=2,sort_keys=True);stream.write('\n')
    print(json.dumps({'diagnostic_binding':bind(path),'kind':reply.get('kind'),
        'native_result':reply.get('message',{}).get('result'),
        'native_gaps':reply.get('message',{}).get('gaps'),'native_checks':reply.get('message',{}).get('checks'),
        'source_guarded_exit_completed':True,'owned_fixture_cleanup_completed':True,'public_export_attempted':False}),flush=True)
if __name__=='__main__':main()
