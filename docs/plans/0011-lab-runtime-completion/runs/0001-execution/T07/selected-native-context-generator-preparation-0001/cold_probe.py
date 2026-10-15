"""Explicit fresh C08/v2 route; consumes selected adapter rather than old class."""
import argparse,json
from pathlib import Path
from . import context_selected as C
from . import selected_runtime as SR
from lab_runtime.replay import ReplayPins
from lab_runtime.store import VerifiedLegacyReadStore

def main(argv=None):
    parser=argparse.ArgumentParser();parser.add_argument('--input-selection',required=True);parser.add_argument('--input-selection-sha256',required=True)
    args=parser.parse_args(argv)
    selected=json.loads(SR.exact({'path':args.input_selection,'sha256':args.input_selection_sha256}))
    SR.closed(selected,('schema_version','authority_effect','generator_manifest_binding','input_root','input_locator','input_binding'))
    SR.need(selected['schema_version']=='lab-selected-native-context-cold-selection/v1-candidate' and selected['authority_effect']=='none','closed independently selected cold input required')
    manifest_binding=selected['generator_manifest_binding'];SR.exact(manifest_binding)
    pins=C.SelectedGeneratorPins(manifest_binding['sha256'],C.IMPLEMENTATION_VERSION)
    manifest_path=SR.ROOT/manifest_binding['path'];manifest=C.verify_generator(manifest_path,pins)
    runtime=SR.SelectedRuntime(manifest);runtime.guard()
    raw=runtime.custody_module.control_bytes(selected['input_root'],selected['input_locator'],selected['input_binding'])
    body=C.loads(raw)
    SR.closed(body,('schema_version','authority_effect','store_path','repository','store_pins','semantic_directory','governance_directory',
                   'native_request','native_executable','native_pins','source_snapshot','options'))
    SR.need(body['schema_version']=='lab-selected-native-context-cold-input/v1-candidate' and body['authority_effect']=='none','unknown cold input version or authority')
    SR.need(type(body['options'])is dict and not {'selected_runtime','generator_pins','generator_manifest','clock','wall_clock'}&set(body['options']),
            'cold reconstruction cannot inject runtime, manifest or clocks')
    store=VerifiedLegacyReadStore(body['store_path'],body['repository'],C.ROOT,ReplayPins(**body['store_pins']))
    native=runtime.store(body['semantic_directory'],body['governance_directory'],body['native_request'],body['native_executable'],body['native_pins'])
    session=None
    try:
        session=C.SelectedContextSession(store,body['source_snapshot'],native,generator_manifest=manifest_path,
                  generator_pins=pins,selected_runtime=runtime,**body['options'])
        pack=session.context()
        result={'result':'PASS-selected-native-cold-reconstruction','authority_effect':'none','native_projection_digest':C.digest(pack['native_ontology']),
                'generator_provenance':pack['generator_provenance'],'project_state_digest':C.digest(pack['project_state']),
                'candidate_kinds':sorted(pack['candidate_artifacts']),'session_memory_entries':len(session.core._memory),
                'action_permission':pack['action_permission'],'actual_owner_outcome':None,'whole_runtime_qualified':False}
    finally:
        if session is not None:session.close()
        runtime.guard();C.verify_generator(manifest_path,pins)
    print(json.dumps(result,sort_keys=True));return 0
