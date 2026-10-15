"""Consume actual W03/W04 materialization originals; no Tool dispatch or result fabrication."""
from .output_contracts import need, parse, sha, closed

SUPPORTED = {'transition:engineering:assessed':'engineering', 'transition:research:evaluated':'research'}

def verify_original_materialization(kind, review_raw, *, outputs, work_ref):
    review = parse(review_raw)
    need(review['authority_effect'] == 'none' and review['actual_owner_outcome'] is None
         and review['canonical_effects_applied'] == 0, 'producer review is not repository admission')
    if kind == 'engineering':
        need(review['work_effect']['from_version_ref'] == work_ref and review['work_effect']['applied'] is False,
             'original engineering Work outcome lineage differs')
        members = review['member_records']; hash_field = 'record_sha256'
    elif kind == 'research':
        need(review['process_completed'] is True, 'original research process did not complete')
        need(any(row['version_ref'] == work_ref for row in review['input_dependencies']),
             'original research Work dependency absent')
        members = review['selected_candidate_members']; hash_field = 'sha256'
    else: raise ValueError('original producer unsupported')
    for artifact in outputs:
        matching = [row for row in members if row['version_ref'] == artifact['version_ref']
            and row['identity_ref'] == artifact['identity_ref'] and row[hash_field] == artifact['byte_sha256']]
        need(len(matching) == 1, 'output is not an exact original materialized producer member')
    return review

class OriginalProducerOutputs:
    """A private bootstrap selection, never supplied by workflow.transition message data.

    The genuine Service/vault/source guard and separately authorized original
    producer must exist before this reader is installed. No constructor or
    producer is executed by the structural controls.
    """
    def __init__(self, host, *, selection_binding, carriers, producer_bindings):
        self.host = host; self.selection_binding = selection_binding
        self.carriers = carriers; self.producer_bindings = producer_bindings

    def select(self, message, plan):
        need(message['transition_ref'] in SUPPORTED, 'exact transition producer/consumer unresolved; retain original requirement')
        kind = SUPPORTED[message['transition_ref']]
        raw = self.host.vault.material(self.selection_binding)
        need(sha(raw) == self.selection_binding['sha256'], 'private independent output selection changed')
        selected = parse(raw)
        closed(selected, ('schema_version','transition_ref','run_binding','source_cut','work_ref',
            'producer_code_binding','producer_review_binding','outputs','authority_effect','actual_owner_outcome'))
        need(selected['schema_version'] == 'lab-independent-workflow-output-selection/v1-candidate'
             and selected['authority_effect'] == 'none' and selected['actual_owner_outcome'] is None,
             'private outputs cannot provide authority')
        need(selected['transition_ref'] == message['transition_ref'] and selected['run_binding'] == message['run_binding']
             and selected['source_cut'] == message['source_cut'], 'output run/transition/cut correspondence differs')
        need(selected['work_ref'] == plan['next_run']['work']['version_ref'], 'output producer names another exact Work')
        need(selected['producer_code_binding'] == self.producer_bindings[kind], 'unselected original output producer')
        code_raw = self.host.vault.material(selected['producer_code_binding'])
        need(sha(code_raw) == selected['producer_code_binding']['sha256'], 'selected original producer code differs')
        # All private control originals are bound by independently granted
        # action receipts, just as the inherited transition already requires.
        need(selected['producer_review_binding'] in message['action_receipt_bindings'],
             'producer review is outside independently selected action receipts')
        review_raw = self.host.vault.material(selected['producer_review_binding'])
        need(sha(review_raw) == selected['producer_review_binding']['sha256'], 'producer review original bytes differ')
        outputs = []; bodies = {}
        for row in selected['outputs']:
            closed(row, ('artifact','original_binding'))
            original = self.host.vault.material(row['original_binding'])
            need(sha(original) == row['original_binding']['sha256'] == row['artifact']['byte_sha256'],
                 'producer output original bytes differ')
            outputs.append(row['artifact']); bodies[row['artifact']['version_ref']] = original
        verify_original_materialization(kind, review_raw, outputs=outputs, work_ref=selected['work_ref'])
        return outputs, bodies, selected['work_ref']
