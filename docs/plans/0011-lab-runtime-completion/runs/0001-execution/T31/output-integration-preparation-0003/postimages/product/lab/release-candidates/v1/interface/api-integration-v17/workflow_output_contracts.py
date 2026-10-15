"""Pure original-carrier output attachment; no producer, permission or admission."""
import copy, hashlib, json
from jsonschema import Draft202012Validator, FormatChecker

class OutputRefusal(ValueError): pass

def need(value, reason):
    if not value: raise OutputRefusal(reason)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def parse(raw):
    need(type(raw) is bytes and len(raw) <= 16 * 1024 * 1024, 'bounded original output bytes required')
    def pairs(rows):
        out = {}
        for key, value in rows:
            need(key not in out, 'duplicate original JSON key'); out[key] = value
        return out
    def invalid(_): raise OutputRefusal('nonfinite output JSON')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)

def closed(value, fields):
    need(type(value) is dict and set(value) == set(fields), 'closed independent output selection required')

def pointer(value, path):
    need(type(path) is str and path.startswith('/'), 'original discriminator pointer required')
    for token in path.split('/')[1:]: value = value[token.replace('~1', '/').replace('~0', '~')]
    return value

def privacy(value):
    if type(value) is dict:
        for key, child in value.items():
            need(key.lower() not in {'private_key', 'private_key_bytes', 'password', 'access_token',
                'refresh_token', 'session_memory', 'short_memory'}, 'private output body forbidden')
            privacy(child)
    elif type(value) is list:
        for child in value: privacy(child)
    elif type(value) is str: need('PRIVATE KEY-----' not in value, 'private signing material forbidden')

class OriginalCarriers:
    """Exact carrier identity, descriptor, schema and discriminator, never just a prefix."""
    def __init__(self, catalog_raw, expected_sha256, raw_documents, *, scope_contracts=None):
        need(sha(catalog_raw) == expected_sha256, 'independent output catalog differs')
        catalog = parse(catalog_raw)
        need(catalog['authority_effect'] == 'none' and catalog['actual_owner_outcome'] is None,
             'carrier metadata cannot provide authority')
        need(set(raw_documents) == {row[key] for row in catalog['rows'] for key in ('schema_path','artifact_path')},
             'original output document closure differs')
        self.rows = {}; self.schemas = {}; self.scope_contracts=scope_contracts
        for row in catalog['rows']:
            ref = row['artifact_type_ref']; need(ref not in self.rows, 'duplicate exact output carrier')
            schema_raw = raw_documents[row['schema_path']]; descriptor_raw = raw_documents[row['artifact_path']]
            need(sha(schema_raw) == row['schema_sha256'] and sha(descriptor_raw) == row['artifact_sha256'],
                 'original carrier descriptor or schema changed')
            descriptor = parse(descriptor_raw); schema = parse(schema_raw)
            need(descriptor['artifact_type_ref'] == ref and descriptor['schema_digest'] == row['schema_sha256'],
                 'carrier descriptor identity/schema digest differs')
            need(row['schema_selector'] is None, 'unsupported output fragment needs an explicit original adapter')
            Draft202012Validator.check_schema(schema)
            self.rows[ref] = copy.deepcopy(row); self.schemas[ref] = schema

    def output(self, artifact, raw, *, scope_ref, transition_ref=None, scope_proof=None):
        closed(artifact, ('scope_ref','identity_ref','version_ref','carrier_ref','byte_sha256'))
        ref = artifact['carrier_ref']; need(ref in self.rows, 'unselected exact output carrier')
        need(artifact['scope_ref'] == scope_ref and sha(raw) == artifact['byte_sha256'],
             'output original bytes or independent scope differs')
        body = parse(raw)
        if ref=='cal.artifact-type.agent-session/v1':
            # Original formal lifecycle body only; actual Session RAM is never an output.
            memory=body.get('payload',{}).get('session_memory')
            need(type(memory)is dict and set(memory)=={'selected_input_refs','working_record_refs','unresolved_questions','expires_with_session'} and memory['expires_with_session'] is True,'original Session lifecycle memory contract required')
            # These are original formal reference arrays, not actual resource.memory.
            # Validate their unchanged original schema; return only ArtifactRef headers.
            for name in ('selected_input_refs','working_record_refs','unresolved_questions'):privacy(memory[name])
            public=copy.deepcopy(body);del public['payload']['session_memory'];privacy(public)
        else:privacy(body)
        row = self.rows[ref]
        need(pointer(body, row['instance_discriminator']['path']) == row['instance_discriminator']['value'],
             'output body/carrier version differs')
        Draft202012Validator(self.schemas[ref], format_checker=FormatChecker()).validate(body)
        identity = body.get('node_id', body.get('goal_id', body.get('coordination_context_id', body.get('project_id',body.get('migration_manifest_id')))))
        need(identity == artifact['identity_ref'] and artifact['version_ref'].startswith(identity+'@'),
             'exact output identity/revision differs')
        if 'version' in body: need(artifact['version_ref'] == identity+'@'+body['version'], 'declared output revision differs')
        body_scope = body.get('scope_ref', body.get('project_ref', body.get('payload', {}).get('project_ref')))
        if ref=='cal.artifact-type.repository-migration-manifest/v1':
            need(body_scope is None and body['execution_authority'] is False,'original Migration manifest scope/authority contract differs')
            # Scope belongs to the independently bound actual producer/Work input
            # and ArtifactRef; no scope_ref is invented in the original body.
        elif scope_proof is not None:
            need(self.scope_contracts is not None and transition_ref is not None,'independently selected native-only scope contract required')
            self.scope_contracts.validate(transition_ref,artifact,body_scope,scope_proof)
        else:need(body_scope == scope_ref, 'original output body scope differs')
        need(body.get('authority_effect') == 'none', 'output cannot convey implicit authority')
        return body

def attach_outputs(kernel, plan, *, outputs, raw_by_ref, carriers, scope_ref, work_ref, transition_ref=None, scope_proofs=None):
    """Only existing event, receipt and outcome fields are used; no output fields on WorkflowRun."""
    need(plan['actual_apply_completed'] is False and plan['work_satisfaction_asserted'] is False,
         'planned coordination is not application or Work satisfaction')
    need(type(outputs) is list and len(outputs) == len({h['version_ref'] for h in outputs}),
         'unique original output revisions required')
    need({h['carrier_ref'] for h in outputs} == set(plan['allowed_output_carriers']),
         'complete original transition output carrier set required')
    need(set(raw_by_ref) == {h['version_ref'] for h in outputs}, 'output byte closure differs')
    result = copy.deepcopy(plan); outcomes = []
    for header in outputs:
        body = carriers.output(header, raw_by_ref[header['version_ref']], scope_ref=scope_ref,transition_ref=transition_ref,scope_proof=None if scope_proofs is None else scope_proofs[header['version_ref']])
        if header['carrier_ref'] == 'cal.artifact-type.work-outcome-assessment/v1':
            need(body['payload']['subject_ref'] == work_ref, 'outcome names another exact Work revision')
            outcomes.append(header)
    need(len(outcomes) <= 1, 'ambiguous observed Work outcome')
    result['event']['output_artifact_refs'] = copy.deepcopy(outputs)
    if outcomes: result['next_run']['outcome_assessment'] = copy.deepcopy(outcomes[0])
    event_sha = kernel.digest(result['event'])
    need(bool(result['next_run']['event_bindings']), 'original next event binding absent')
    result['next_run']['event_bindings'][-1] = {'ref':'workflow-event:'+event_sha, 'sha256':event_sha}
    result['next_run_structural_sha256'] = kernel.digest(result['next_run'])
    need(result['event']['completed_work_asserted'] is False and result['event']['canonical_admission_granted'] is False,
         'output-bearing transition cannot admit artifacts or assert completed Work')
    return result
