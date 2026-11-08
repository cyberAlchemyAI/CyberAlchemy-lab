"""Public-source, installed-interpreter replay of the Action import guard."""
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import uuid

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
INTERFACE=ROOT/'product/lab/release-candidates/v1/interface'
API=INTERFACE/'api-integration-v38-current-t06-0001'
ACTION=INTERFACE/'api-action-integration-v5-current-t06-0001'
GOV=INTERFACE/'api-governance-integration-v5-current-t12-0001'
sys.path[:0]=[str(INTERFACE),str(ROOT/'implementation/lab-runtime/local-host/t06-jsonschema-419-overlay-0001/overlay'),
               str(ROOT/'implementation/lab-runtime/local-host/t06-current-composite-successor-0001/working/installation-0001/deps')]

def package(path):
    name='_cal_composite_'+path.name.replace('-','_')+'_'+uuid.uuid4().hex
    spec=importlib.util.spec_from_file_location(name,path/'__init__.py',submodule_search_locations=[str(path)])
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return name

def main():
    started=time.monotonic()
    api=package(API);action=package(ACTION);gov=package(GOV)
    importlib.import_module(api+'.guard')
    importlib.import_module(api+'.protocol')
    importlib.import_module(action+'.runtime')
    importlib.import_module(action+'.service')
    importlib.import_module(gov+'.host')
    importlib.import_module(gov+'.service')
    source=importlib.import_module(api+'.source_bridge')
    # The replay source name is selected by the private policy but never printed.
    control=Path('/tmp/cal-T06-api38-control-0002')
    private_root=Path((control/'root.txt').read_text().strip())
    record=json.loads((private_root/'private-branch-selection.json').read_bytes())
    policy=json.loads(Path(record['branches']['base']['policy']['path']).read_bytes())
    view=source.replay_source(policy['source_name'])
    try:
        view.__enter__()
        importlib.import_module(api+'.service')
        importlib.import_module(api+'.integration_dispatch')
        D=importlib.import_module(action+'.dependencies')
        profile={'ref':'product/lab/release-candidates/v1/interface/api-integration-v38-current-t06-0001/contract-profile.json',
                 'sha256':'32e43cbdaf65a81ccd29033d7351f1685e28ca54c640d595e894322749f82869'}
        D.guard('c530150e5cca87f2f3e84d897f423b16562de0fecdf3d17b39e8c6b421d07013',
                integration_profile_binding=profile)
        print(json.dumps({'status':'PASS','elapsed_seconds':round(time.monotonic()-started,3)}))
    except Exception as error:
        print(json.dumps({'status':'REFUSED','exception_class':type(error).__name__,
                          'reason':str(error)[:240],'elapsed_seconds':round(time.monotonic()-started,3)}))
        return 1
    finally:
        view.__exit__(None,None,None)
    return 0

if __name__=='__main__':raise SystemExit(main())
