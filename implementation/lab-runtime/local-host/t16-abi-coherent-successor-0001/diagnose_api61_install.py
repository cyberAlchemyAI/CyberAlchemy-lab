"""Read-only preflight diagnosis of API61 installation integrity refusal."""
import importlib,importlib.util,json,sys,traceback
from pathlib import Path
from datetime import datetime

ROOT=Path(__file__).resolve().parents[4]
INSTALL=Path('/tmp/cal-T03-native-install-20261023/0001')
sys.path.insert(0,str(INSTALL/'deps'))
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v61-t16-abi423-bridge-0001'
NAME='_cal_t16_api61_install_diagnosis'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)])
package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
g=importlib.import_module(NAME+'.guard');g.verify('84435a57c990a1d85504cf844a257e6dc3607c81519d368c828449ac8106ffc4')
p=importlib.import_module(NAME+'.protocol');source=p.source
f=importlib.import_module(NAME+'.installation_release_fixture')
h=importlib.import_module(NAME+'.installation_release')
cut=importlib.import_module(NAME+'.handlers').cut
schemas=p.Schemas('843ee830613211f6c36c6c822ef32b08e71b5799166485ed24b99d09f053e12c')
try:
    with source.replay_source('custody-participation') as view:
        with f.example(view,schemas) as (host,call,plan):
            handler=h.InstallationRelease(host,'installation.execute',datetime.fromisoformat(call['deadline']))
            request={'ref':'request:isolated-diagnostic','sha256':source.sha(p.compact(call))}
            domain,evidence=handler.prepare(call['message'],request,cut(view),call['idempotency_key'])
            print(json.dumps({'result':'PASS-DIRECT-PREPARE','posture':domain['posture'],
                              'evidence_count':len(evidence),'authority_effect':'none'}))
except BaseException:
    traceback.print_exc()
    raise
