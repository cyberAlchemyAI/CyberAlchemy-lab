#!/usr/bin/env python3
"""Fresh-process reconstruction of the C09 joined inspection fixture."""
import json,sys
from joined_inspection import *
from lab_runtime.replay import ReplayPins
from context import GeneratorPins
from native_reader import NativePins,NativeReadStore

body=load(sys.argv[1]);options=body['context_options'];options['generator_pins']=GeneratorPins(**options['generator_pins'])
project=VerifiedLegacyReadStore(body['project_path'],body['repository'],ROOT,ReplayPins(**body['project_pins']))
native=NativeReadStore(body['native_semantic'],body['native_governance'],body['native_request'],body['native_executable'],NativePins(**body['native_pins']))
result=inspect_successor(project,body['snapshot'],body['catalog_path'],bootstrap.CatalogPins(**body['catalog_pins']),bootstrap.RehearsalPolicy(**body['catalog_policy']),body['transition_path'],BranchPins(**body['transition_pins']),LocalPolicy(**body['transition_policy']),native,JoinPins(**body['join_pins']),context_options=options)
print(json.dumps({'result':'PASS','authority_effect':'none','catalog_digest':result['join_pins']['catalog_digest'],'project_state_digest':digest(result['project_state']),'memory_erased':result['session_closure']['short_memory_erased'],'candidate_postures':sorted(set([r['effective_state'] for r in result['candidate_catalog'].values()]+[r['effective_state'] for r in result['reconstructed_candidates'].values()]))}))
