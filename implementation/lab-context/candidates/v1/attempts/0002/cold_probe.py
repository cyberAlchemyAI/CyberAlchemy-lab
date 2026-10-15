#!/usr/bin/env python3
"""Fresh-process read-only reconstruction for isolated C08 evidence."""
import json
import sys
from context import *
from lab_runtime.replay import ReplayPins
from lab_runtime.store import VerifiedLegacyReadStore
from native_reader import NativePins

body=load(sys.argv[1])
store=VerifiedLegacyReadStore(body['store_path'],body['repository'],ROOT,ReplayPins(**body['store_pins']))
native=NativeReadStore(body['semantic_directory'],body['governance_directory'],body['native_request'],body['native_executable'],NativePins(**body['native_pins']))
with_session=None
try:
    with_session=ContextSession(store,body['source_snapshot'],native,generator_manifest=body['generator_manifest'],generator_pins=GeneratorPins(**body['generator_pins']),**body['options'])
    pack=with_session.context()
    print(json.dumps({'result':'PASS','authority_effect':'none','native_projection_digest':digest(pack['native_ontology']), 'generator_provenance':pack['generator_provenance'],'project_state_digest':digest(pack['project_state']),'candidate_kinds':sorted(pack['candidate_artifacts']),'session_memory_entries':len(with_session.core._memory),'action_permission':pack['action_permission']}))
finally:
    if with_session is not None:with_session.close()
