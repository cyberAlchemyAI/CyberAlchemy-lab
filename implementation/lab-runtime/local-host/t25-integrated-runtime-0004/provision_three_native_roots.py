"""Provision only the real ABI layer of three owned future runtime stages.

This is not API installation qualification. Every root receives its own actual
directory identity and receipt while all1010 public payload bytes agree.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SUPPORT = ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001'
SELECTION = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
PIN = '2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
PAYLOAD = Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
DESTINATIONS = Path('/home/vlad_/.local/share/cyberalchemy-lab/portable-runtime-installations')
RESULT = HERE/'NATIVE-THREE-ROOTS-0001.json'


def run():
    os.umask(0o077)
    if RESULT.exists():
        raise ValueError('native layer result already exists')
    spec = importlib.util.spec_from_file_location('T25_actual_native_installer',HERE/'native_install.py')
    native = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(native)
    sys.path.insert(0,str(SUPPORT))
    import closure_hardened_0003 as dependencies
    selected,_ = dependencies.load_selection(SELECTION,PIN)
    members = dependencies.installed_files(selected)
    if len(dependencies.verify_installed(PAYLOAD,selected))!=1010:
        raise ValueError('original exact durable native closure differs')
    DESTINATIONS.mkdir(mode=0o700,parents=True,exist_ok=True)
    native.safe_root(DESTINATIONS)
    rows = []
    for label in ('0001-a','0001-b','0001-restore'):
        stage = DESTINATIONS/label
        stage.mkdir(mode=0o700)
        runtime = stage/'runtime'
        runtime.mkdir(mode=0o700)
        (runtime/'repository').mkdir(mode=0o700)
        private = runtime/'.cal-runtime'
        private.mkdir(mode=0o700)
        receipt = native.install(private,PAYLOAD,members,PIN)
        cold = native.cold_abi(private/'native')
        native.verify(private/'native',members,PIN)
        item = {'stage':str(stage),'repository_root':str(runtime/'repository'),
                'private_root':str(private),'native_receipt':receipt,'cold_ABI':cold,
                'status':'NATIVE-LAYER-PROVISIONED-API-NOT-INSTALLED','authority_effect':'none'}
        native.write_new(stage/'native-stage.json',native.encoded(item),0o600)
        rows.append(item)
        print(json.dumps({'stage':label,'result':'PASS-native-payload-and-cold-ABI','files':1010},sort_keys=True),flush=True)
    if len({tuple(row['native_receipt']['identity']) for row in rows})!=3:
        raise ValueError('native fresh-root identities unexpectedly coincide')
    value = {'schema_version':'lab-three-fresh-native-layers/v1','result':'PASS-native-layer-only',
             'native_selection_sha256':PIN,'payload_manifest_sha256':native.sha(native.encoded(members)),
             'roots':rows,'stable_native_payload_files':1010,'fresh_actual_root_identities':3,
             'full_API_installed':False,'full_API_cold_replayed':False,
             'child_grandchild_loader_maps_qualified':False,'t19_complete':False,'t25_complete':False,
             'authority_effect':'none'}
    native.write_new(RESULT,native.encoded(value),0o600)
    return value


if __name__=='__main__':
    run()
