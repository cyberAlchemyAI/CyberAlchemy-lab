"""Fresh exact W07 join plus signed Lesson/context replay; no effect redispatch."""
import os
from successor import *


def run(selection_sha,expected_path,expected_sha,native):
    require(selection_sha==SELECTION_SHA and byte_sha(SELECTION.read_bytes())==selection_sha,'independent cold selection pin differs')
    expected_path=Path(expected_path);require(expected_path.resolve().is_relative_to(PACKAGE/'receipts/integration/W07')
        and byte_sha(expected_path.read_bytes())==expected_sha,'independent warm join bytes differ')
    manifest_path=ROOT/'implementation/lab-continuity/candidates/v1/packages/0001/generator-manifest.json'
    manifest=parse(manifest_path.read_bytes());native=Path(native)
    require(native.is_file() and not native.is_symlink() and byte_sha(native.read_bytes())==manifest['native_executable_sha256'],
        'independent native executable differs')
    os.environ['W02_NATIVE_EXECUTABLE']=str(native)
    cases=original_cases();joined=validate_join(cases)
    require(joined==parse(expected_path.read_bytes()),'fresh exact workflow/coupling join differs from warm result')
    learning=next(c for c in cases if c['domain']=='learning');b=learning['episode_index']
    sys.path.insert(0,str(PACKAGE/'examples/learning-loop'))
    spec=importlib.util.spec_from_file_location('_W07_signed_lesson_cold',PACKAGE/'examples/learning-loop/run_episode.py')
    episode=importlib.util.module_from_spec(spec);sys.modules[spec.name]=episode;spec.loader.exec_module(episode)
    actual=episode.cold(ROOT/b['path'],b['sha256'],native)
    require(actual['result']=='PASS' and actual['signed_original_branch_replayed'] and actual['new_Agent_lesson_context']
        and actual['applications_reexecuted']==0 and actual['private_key_restored'] is False,'cold Lesson/session reconstruction differs')
    result={'schema_version':'lab-W07-signed-integration-cold/v1-candidate','result':'PASS','domain_cases_checked':4,
        'typed_connections_checked':joined['typed_connections_checked'],'remaining_runtime_gaps':0,'signed_coupling_archives_replayed':2,
        'warm_join_sha256':expected_sha,'selection_sha256':selection_sha,'native_executable_sha256':byte_sha(native.read_bytes()),
        'signed_lesson_cold_context':actual,'original_domain_effects_reexecuted':0,'keys_restored':False,'Session_memory_restored':False,
        'new_Agent_created_from_verified_state':True,'canonical_effects_applied':0,'global_merge_performed':False,'actual_owner_outcome':None,'authority_effect':'none'}
    print(encoded(result).decode(),end='');return result


if __name__=='__main__':
    require(len(sys.argv)==5,'usage: cold.py selection-sha warm-join-json warm-join-sha native-reader')
    run(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4])
