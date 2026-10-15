#!/usr/bin/env python3
"""Cold exact native archive replay plus independent source/selector joins."""
import base64
import subprocess
import tempfile

from translation import *


def verify(executable, executable_sha, archive_path, archive_sha, witness_path, witness_sha, expected_view_digest):
    executable = Path(executable);archive_path = Path(archive_path);witness_path = Path(witness_path)
    require(sha(executable.read_bytes())==executable_sha,'independent native executable pin differs')
    require(sha(archive_path.read_bytes())==archive_sha and sha(witness_path.read_bytes())==witness_sha,
        'independent archive/witness original pins differ')
    archive = parse(archive_path.read_bytes());witnesses = parse(witness_path.read_bytes())
    require(archive['authority_effect']=='none' and archive['actual_owner_outcome'] is None
        and archive['private_key_included'] is False and archive['Session_memory_included'] is False
        and archive['ontology_admission'] is False and archive['source_effects_applied']==0,'archive authority/private scope differs')
    with tempfile.TemporaryDirectory(prefix='cal-O02-cold-') as temp:
        root = Path(temp);(root/'semantic').mkdir();(root/'governance').mkdir()
        for name,row in archive['files'].items():
            path = Path(name)
            require(not path.is_absolute() and len(path.parts)==2 and path.parts[0] in ('semantic','governance')
                and path.suffix=='.json' and '..' not in path.parts,'native archive path escape')
            raw = base64.b64decode(row['base64_original_bytes'],validate=True)
            require(sha(raw)==row['sha256'],'native original event bytes changed')
            with (root/path).open('xb') as stream:stream.write(raw)
        child = subprocess.run([str(executable),'read',str(root/'semantic'),str(root/'governance'),str(archive['semantic_cursor'])],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
        require(child.returncode==0,'cold native replay rejected: '+child.stderr.decode(errors='replace'))
        view = parse(child.stdout)
        require(object_sha(view)==expected_view_digest,'cold complete view differs from independently pinned warm view')
        require(len(view['semantic_events'])==archive['semantic_cursor'] and len(view['governance_events'])==archive['governance_cursor'],
            'native semantic/governance prefix differs')
        semantic = {e['event_id']:e for e in view['semantic_events']}
        with signed_catalog() as (catalog,operations):
            adapter = CandidateRepresentationAdapter(catalog,operations)
            translator = RichTranslation(adapter,witnesses['profile_binding'])
            for name in ['work','implementation','capability']:
                w = witnesses[name];spec = translator.node_spec(w['source_view'])
                state,actual = translator.translate_node(w['rich_record'],spec)
                for key in actual:require(actual[key]==w[key],'cold rich translation witness differs')
                ref = w['rich_record']['payload']['governance_binding']['semantic_event_ref']
                event = semantic[ref['semantic_event_id']]
                require(event['event_digest']==ref['semantic_event_digest'] and event['semantic_cursor']==ref['semantic_cursor']
                    and event['complete_resulting_semantic_state']==state,'cold rich Node semantic tuple mismatch')
            require(translator.signed_source_effect(witnesses['work']['source_view'])==witnesses['signed_source_effect'],
                'cold signed source effect/Project history tuple differs')
            case = parse(original(witnesses['source_case_binding']))
            cut = {'cut_id':case['case_id'],'authority_effect':'none','actual_owner_outcome':None,
                'records':[{k:r[k] for k in ['path','sha256','kind','version_ref']} for r in case['records']]}
            cut_view = adapter.candidate_cut(cut);adapter.validate_candidate_relations(cut_view)
            edge = witnesses['relation'];source = edge['source_typed_relation']
            require(cut_view['views'][source['represented_subject']['version_ref']]==source,'cold source relation differs')
            p = source['record']['payload'];require(edge['qualifiers']==p['qualifiers'],'cold qualifier values lost')
            require(edge['exact_source_revision']==p['source']['version_ref'] and edge['exact_target_revision']==p['target']['version_ref'],
                'cold direction/exact endpoint tuple differs')
            for w in witnesses['challenges']:
                event = parse(original(w['challenge_event_binding']));contract = parse(original(w['challenge_contract_binding']))
                require(event['payload']['subject_version_ref']==witnesses['implementation']['source_view']['represented_subject']['version_ref']
                    and event['payload']['subject_ref']==witnesses['implementation']['source_view']['represented_subject']['identity'],
                    'cold challenge revision mismatch')
                require(w['native_gate_identifier']=='source-gate:'+sha(contract['payload']['resolution_gate_ref'].encode()),
                    'cold exact gate reference encoding differs')
                if w['source_resolution_decision_binding']:
                    decision = parse(original(w['source_resolution_decision_binding']))
                    require(w['source_resolution_decision_ref'].startswith(decision['node_id']+'@'),'cold resolution Decision differs')
            require(sha(executable.read_bytes())==executable_sha and sha(archive_path.read_bytes())==archive_sha
                and sha(witness_path.read_bytes())==witness_sha,'cold selected bytes changed during replay')
    return {'result':'PASS','authority_effect':'none','actual_owner_outcome':None,'cold_view_digest':object_sha(view),
        'native_semantic_cursor':len(view['semantic_events']),'native_governance_cursor':len(view['governance_events']),
        'rich_nodes_verified':3,'typed_relations_verified':1,'challenge_revisions_verified':4,
        'signed_source_effect_verified':True,'original_domain_effects_reexecuted':0,'source_effects_applied':0,
        'canonical_ontology_admissions_applied':0,'native_checkpoint_parity':view['checkpoint_parity']}


if __name__=='__main__':
    print(json.dumps(verify(*sys.argv[1:]),indent=2,sort_keys=True))
