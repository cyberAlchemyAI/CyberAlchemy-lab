"""Fresh source/native original-byte reconstruction; no effects or keys restored."""
import subprocess
from mapping import *


def verify(executable, executable_sha, witness_path, witness_sha):
    executable=Path(executable);witness_path=Path(witness_path)
    require(not executable.is_symlink() and sha(executable.read_bytes())==executable_sha,
        'independent native executable pin differs')
    require(sha(witness_path.read_bytes())==witness_sha, 'independent source/native witness pin differs')
    witness=parse(witness_path.read_bytes())
    require(witness['authority_effect']=='none' and witness['actual_owner_outcome'] is None, 'witness claims owner authority')
    source_archive=parse(original(witness['source_archive_binding']))
    native_archive=parse(original(witness['native_archive_binding']))
    require(native_archive['authority_effect']=='none' and native_archive['actual_owner_outcome'] is None
        and native_archive['private_key_included'] is False and native_archive['Session_memory_included'] is False
        and native_archive['ontology_admission'] is False and native_archive['source_effects_applied']==0
        and native_archive['semantic_cursor']==1 and native_archive['governance_cursor']==3
        and native_archive['native_executable_sha256']==executable_sha, 'native archive authority/custody differs')
    with tempfile.TemporaryDirectory(prefix='cal-O02-cold-source-native-') as temp:
        root=Path(temp);cuts={}
        try:
            for operation in ('admit','withdraw'):
                cuts[operation]=restore_cut(source_archive,operation,root/operation,
                    ReplayPins(**witness['source_pins'][operation]))
                require(object_sha(cuts[operation].data['projection'])==witness['source_projection_digests'][operation],
                    'cold source cut differs from independently pinned warm projection')
            semantic=root/'semantic';semantic.mkdir();governance=root/'governance';governance.mkdir()
            require(set(native_archive['files'])=={'semantic/00000001-ontology-semantic:O02:1.json',
                'governance/00000001-ontology-governance:O02:1.json',
                'governance/00000002-ontology-governance:O02:2.json',
                'governance/00000003-ontology-governance:O02:3.json'}, 'source mapping native archive closure differs')
            for name,row in native_archive['files'].items():
                raw=base64.b64decode(row['base64_original_bytes'],validate=True)
                require(sha(raw)==row['sha256'], 'cold original native bytes differ')
                with (root/name).open('xb') as stream:stream.write(raw)
            child=subprocess.run([str(executable),'read',str(semantic),str(governance),'1'],
                stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
            require(child.returncode==0, 'cold full native replay rejected: '+child.stderr.decode(errors='replace'))
            view=parse(child.stdout)
            require(object_sha(view)==witness['complete_native_view_digest'] and view['checkpoint_parity']=='PASS',
                'cold complete native view or checkpoint differs')
            require(witness['semantic_original_byte_digests']=={k:v['sha256'] for k,v in native_archive['files'].items() if k.startswith('semantic/')},
                'cold semantic originals differ from pre-withdrawal bytes')
            with signed_catalog() as (catalog,operations):
                translator=RichTranslation(CandidateRepresentationAdapter(catalog,operations),witness['profile_binding'])
                rich=witness['rich_node'];spec=translator.node_spec(rich['source_view'])
                state,translated=translator.translate_node(rich['rich_record'],spec)
                for key,value in translated.items():require(value==rich[key], 'cold rich translation witness differs')
                event=view['semantic_events'][0];ref={
                    'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],'semantic_cursor':event['semantic_cursor']}
                require(event['complete_resulting_semantic_state']==state and state['lifecycle']=='active', 'cold source-backed native state differs')
                require(rich['rich_record']['payload']['governance_binding']['semantic_event_ref']==ref,
                    'cold original rich Node governance tuple differs')
                previous=view['governance_events'][0]['complete_resulting_governance_state']
                effects={}
                for index,operation in enumerate(('admit','withdraw'),start=1):
                    effect=joined_effect(spec,cuts[operation]);mapping=witness['source_effects'][index-1]
                    require(mapping['effect']==effect and mapping['native_semantic_ref']==ref, 'cold signed source effect/native tuple differs')
                    current=view['governance_events'][index]
                    expected=governance_state(previous,effect)
                    require(current['semantic_ref']==ref and current['complete_resulting_governance_state']==expected
                        and current['event_id']==mapping['native_governance_event_id']
                        and current['event_digest']==mapping['native_governance_event_digest'], 'cold exact governance transformation differs')
                    previous=expected;effects[operation]=effect
                require(effects['admit']['source_eligible'] is True and effects['withdraw']['source_eligible'] is False,
                    'cold withdrawal eligibility differs')
                require(cuts['withdraw'].data['transactions'][2]['previous_digest']==effects['admit']['source_head'],
                    'cold withdrawal signed predecessor differs')
                require(witness['selected_catalog_posture']=='candidate-unadmitted'
                    and rich['source_view']['source_admission']=='candidate-unadmitted', 'selected catalog was relabeled as fixture admission')
            original(witness['original_C12_source_archive_binding'])
            require(sha(executable.read_bytes())==executable_sha and sha(witness_path.read_bytes())==witness_sha,
                'cold executable/witness changed during replay')
        finally:
            for cut in cuts.values():cut.closed=True
    require(not root.exists(), 'cold owned root retained')
    return {'result':'PASS','authority_effect':'none','actual_owner_outcome':None,
        'signed_source_cuts_verified':2,'actual_source_withdrawal_verified':True,'source_signatures_replayed':2,
        'native_semantic_cursor':1,'native_governance_cursor':3,'representation_lifecycle':'active',
        'current_source_eligible':False,'original_semantic_bytes_unchanged':True,
        'complete_native_view_digest':object_sha(view),'checkpoint_parity':'PASS',
        'source_project_histories':{k:v['project_histories'] for k,v in effects.items()},
        'effects_reexecuted':0,'private_keys_restored':0,'Session_memory_restored':0,
        'canonical_ontology_admissions_applied':0,'repository_admissions_applied':0,'owned_root_removed':True}


if __name__=='__main__':print(json.dumps(verify(*sys.argv[1:]),sort_keys=True))
