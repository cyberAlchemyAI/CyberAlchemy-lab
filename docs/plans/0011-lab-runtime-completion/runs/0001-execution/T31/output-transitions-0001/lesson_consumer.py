"""Actual W06 repaired-source consumption, not attribution-only application metadata.

This pure gate returns the exact already observed repaired builder bytes for the
existing W06 probe_child.py source argument. It does not apply another repair,
start a process, grant permission or establish causal/product improvement.
"""
from .output_contracts import need, parse, sha

def observed_research_builder_input(*, application_raw, manifest_raw, repaired_raw,
                                    expected_application_sha256, expected_manifest_sha256,
                                    lesson_ref, selected_source_head, session_ref):
    need(sha(application_raw) == expected_application_sha256 and sha(manifest_raw) == expected_manifest_sha256,
         'independent actual application originals differ')
    application = parse(application_raw); observed = parse(manifest_raw)
    payload = application['payload']
    need(application['kind'] == 'lesson-application' and application['authority_effect'] == 'none'
         and payload['application_posture'] == 'applied-in-controlled-later-case',
         'attribution-only application has no observed consuming path')
    need(payload['lesson_revision_ref'] == observed['lesson_ref'] == lesson_ref
         and payload['session_ref'] == observed['session_ref'] == session_ref
         and observed['source_head'] == selected_source_head, 'actual Lesson/session/source correspondence differs')
    need(observed['controlled'] is True and observed['returncode'] == 0
         and observed['original_source_unchanged'] is True and observed['inline_only_change'] is True
         and observed['actual_owner_outcome'] is None, 'original controlled source consumption was not observed')
    need(observed['result']['controlled'] is True and observed['result']['source_sha256'] == sha(repaired_raw),
         'actual executed research preparation source bytes differ')
    need(bool(observed['repaired_source_ref']) and bool(observed['stdout_ref']) and bool(observed['stderr_ref']),
         'actual source/process original evidence missing')
    return repaired_raw
