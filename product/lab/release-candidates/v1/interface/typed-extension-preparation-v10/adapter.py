"""Join original wire references to exact C14 proposal and evidence bytes.

This pure adapter is not a public handler or a source/owner authority resolver.
The host must independently resolve current relation and endpoint facts, verify
its authenticated Actor, source cut, policy, source closure and pending owner
review, then journal the exact candidate result. No registry is written here.
"""
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
KERNEL = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation'
PROOF = KERNEL / 'receipts/C14/0004.json'
KERNEL_INPUTS_SHA = '51bbea449e67bd7d5354d75e4bcdb1b5c3108555f7cccae953c0f826c9aaa564'
PROOF_SHA = '148722ed4cdfabd250e591590363daa120e6de03eaa11b58b3c215acd41cd1d2'
FIELDS = ('scope_ref', 'identity_ref', 'version_ref', 'carrier_ref', 'byte_sha256')


class WireFault(ValueError):
    pass


def require(value, message):
    if not value:
        raise WireFault(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate JSON key in exact material')
            value[key] = item
        return value
    def constant(value):
        raise WireFault('nonfinite JSON material')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)


def kernel():
    """Resolve the existing inspector from exact checked source, without copying it."""
    inputs_path = HERE / 'kernel-inputs.json'
    require(sha(inputs_path.read_bytes()) == KERNEL_INPUTS_SHA, 'independent full kernel input selection differs')
    for row in json.loads(inputs_path.read_bytes())['files']:
        path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink()
                and not any(parent.is_symlink() for parent in path.parents)
                and sha(path.read_bytes()) == row['sha256'], 'full selected kernel input changed')
    require(sha(PROOF.read_bytes()) == PROOF_SHA, 'independent C14 proof differs')
    proof = json.loads(PROOF.read_bytes())
    require(proof['result'] == 'PASS' and proof['tests'] == {'run': 29, 'errors': 0, 'failures': 0},
            'full original C14 primitive proof required')
    for row in proof['files'] + [proof['definition_binding']]:
        path = ROOT / row['path']
        require(path.is_file() and not path.is_symlink()
                and not any(parent.is_symlink() for parent in path.parents)
                and sha(path.read_bytes()) == row['sha256'], 'checked C14 source input changed')
    name = '_cal_typed_extension_wire_C14_v1'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, KERNEL / 'lab_runtime/__init__.py',
                                                    submodule_search_locations=[str(KERNEL / 'lab_runtime')])
        package = importlib.util.module_from_spec(spec)
        sys.modules[name] = package
        spec.loader.exec_module(package)
    module = importlib.import_module(name + '.extensions')
    require(Path(module.__file__).resolve() == KERNEL / 'lab_runtime/extensions.py',
            'unselected extension inspector')
    return module


def public_header(header):
    require(type(header) is dict and set(header) in
            (set(FIELDS), set(FIELDS) | {'candidate_contract_binding'}),
            'original five-axis artifact header required')
    return {field: copy.deepcopy(header[field]) for field in FIELDS}


def inspect_wire(request, *, proposal, proposal_raw, inspection,
                 independently_selected_actor, independently_selected_cut,
                 independently_selected_key, independently_selected_authority_ref,
                 independently_selected_successor_refs,
                 current_relations, endpoint_contracts, evidence_bytes,
                 material_reader, protocol_valid):
    """Validate every wire field before calling the complete original inspector.

    Actor, current relations, endpoint contracts, source cut and writable authority
    are host-selected inputs. Their authenticity is an integration obligation;
    this function never converts caller declarations into permission or admission.
    material_reader must verify the exact binding and preserve private boundaries.
    """
    require(protocol_valid('urn:cyberalchemy-lab:protocol:typed-extension-request:v1-candidate', request),
            'original typed extension request schema required')
    require(protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', proposal),
            'original ChangeProposal schema required')
    require(type(proposal_raw) is bytes and len(proposal_raw) <= 8 * 1024 * 1024
            and parse(proposal_raw) == proposal, 'proposal original bytes differ or exceed bound')
    def read(binding):
        require(type(binding) is dict and set(binding) == {'ref', 'sha256'},
                'closed exact material binding required')
        raw = material_reader(binding)
        require(type(raw) is bytes and len(raw) <= 8 * 1024 * 1024
                and sha(raw) == binding['sha256'], 'material byte binding or bound differs')
        return raw
    require(request['actor'] == proposal['actor'] == independently_selected_actor,
            'Actor differs from authenticated host selection')
    require(request['source_cut'] == proposal['base_cut'] == independently_selected_cut,
            'current source cut differs')
    require(proposal['idempotency_key'] == independently_selected_key,
            'proposal and outer durable key differ')
    require(request['canonical_writable_authority_ref'] == independently_selected_authority_ref,
            'canonical writable authority differs from independent selection')
    require(inspection['proposal_ref'] == proposal['proposal_ref'], 'inspection selects another proposal')
    relation_ref = request['relation_kind_candidate']
    require(relation_ref['scope_ref'] == proposal['scope_ref'], 'relation candidate scope differs')
    candidates = [target for target in proposal['targets']
                  if target['operation'] != 'withdraw'
                  and public_header(target['artifact']) == relation_ref]
    require(len(candidates) == 1, 'exact Relation Kind candidate target missing or duplicated')
    target = candidates[0]
    require(relation_ref['carrier_ref'] == 'cal.artifact-type.relation-kind/v2',
            'original Relation Kind/v2 carrier required')
    raw = read({'ref': target['content']['content_ref'],
                           'sha256': target['content']['byte_sha256']})
    require(sha(raw) == relation_ref['byte_sha256'] and len(raw) == target['content']['size_bytes'],
            'relation candidate byte identity or size differs')
    body = parse(raw)
    require(body['node_id'] == relation_ref['identity_ref'] == body['payload']['relation_kind_id']
            == inspection['relation_kind_ref'], 'relation body/header/inspection identity differs')
    require(inspection['successor_version_ref'] == relation_ref['version_ref'],
            'inspection successor revision differs')
    payload = body['payload']
    require(request['unique_semantic_question'] == payload['unique_question'] == inspection['unique_question']
            and request['axis_ref'] == payload['axis_id'] == inspection['axis_ref'],
            'wire/body/inspection question or orthogonal axis differs')
    predecessor = target['predecessor']
    require(inspection['predecessor_version_ref'] == (predecessor['version_ref'] if predecessor else None),
            'exact predecessor revision differs')
    old = current_relations.get(inspection['relation_kind_ref'])
    if old is None:
        require(request['prior_signature_binding'] is None and predecessor is None
                and target['operation'] == 'admit', 'distinct-kind predecessor or operation differs')
    else:
        require(predecessor is not None and target['operation'] == 'revise'
                and predecessor['version_ref'] == old['version_ref']
                and request['prior_signature_binding'] == old['signature_binding'],
                'effective predecessor/signature is not independently selected')
    require(request['noncollapse_report_binding'] == inspection['noncollapse_report_binding'],
            'noncollapse report selects another exact question/axis proposal')
    pair_bytes = [read(binding) for binding in request['pair_contract_bindings']]
    pairs = [parse(raw) for raw in pair_bytes]
    require(pairs == inspection['allowed_endpoint_pairs'], 'ordered exact pair contracts differ')
    require(payload['allowed_endpoint_pairs'] == [
        {'source_kind': pair['source_kind'], 'target_kind': pair['target_kind']} for pair in pairs],
        'Relation Kind pair set differs from ordered pair evidence')
    require(payload['source_kinds'] == inspection['source_kinds']
            and payload['target_kinds'] == inspection['target_kinds'],
            'directional kind projections differ')
    domains = []
    for pair in pairs:
        if pair['qualifier_schema_binding'] not in domains:
            domains.append(pair['qualifier_schema_binding'])
    require(domains == request['qualifier_domain_bindings'], 'complete qualifier domain order differs')
    canonical_refs = []
    for pair in pairs:
        if pair['canonical_authority'] == 'typed-relation':
            canonical_refs.append('cal.artifact-type.typed-relation/v3')
        elif pair['canonical_authority'] == 'specialized-carrier':
            projection = parse(read(pair['projection_binding']))
            canonical_refs.append(projection['specialized_carrier_ref'])
        else:
            raise WireFault('undeclared or dual canonical writable authority')
    require(all(ref == independently_selected_authority_ref and ref in endpoint_contracts
                for ref in canonical_refs), 'pair canonical authority differs from exact selected carrier')
    inspector = kernel()
    original_qualifiers = {'type': 'object', 'additionalProperties': False,
                          'properties': payload['qualifier_contract']['properties'],
                          'required': payload['qualifier_contract']['required_axes']}
    for domain in domains:
        schema = parse(read(domain))
        closure = inspector.check_closed_domain(schema)
        merged = copy.deepcopy(schema)
        merged.setdefault('allOf', []).append(original_qualifiers)
        require(inspector.check_closed_domain(merged)['allowed_values'] == closure['allowed_values'],
                'finite pair qualifier domain violates the exact candidate Relation Kind contract')
    successors = request['affected_carrier_successor_refs']
    require(successors == independently_selected_successor_refs,
            'complete affected carrier successor closure differs from independent selection')
    require(len({header['version_ref'] for header in successors}) == len(successors),
            'affected carrier successor list duplicates revisions')
    for header in successors:
        require(header['scope_ref'] == proposal['scope_ref']
                and header['carrier_ref'] == 'cal.artifact-type.artifact-type/v3'
                and len([t for t in proposal['targets'] if t['operation'] != 'withdraw'
                         and public_header(t['artifact']) == header]) == 1,
                'affected carrier successor is absent from the exact proposal closure')
    review_raw = read(request['semantic_owner_review_binding'])
    review = parse(review_raw)
    require(protocol_valid('urn:cyberalchemy-lab:protocol:proposal-review:v1-candidate', review),
            'exact pending semantic review preparation required')
    require(review['source_cut'] == independently_selected_cut
            and review['proposal_binding']['sha256'] == sha(proposal_raw)
            and review['stable_core_bindings'] == [t['decision_core_binding'] for t in proposal['targets']],
            'semantic review does not cover the exact proposal, cut and all ordered cores')
    require(review['authority_effect'] == 'none', 'review preparation cannot grant authority')
    checked = inspector.inspect_extension(inspection, current_relations=current_relations,
                                         endpoint_contracts=endpoint_contracts,
                                         evidence_bytes=evidence_bytes)
    require(checked['globally_available_pairs_added'] == checked['relation_instances_created'] == 0,
            'pure extension inspection produced an effect')
    checked['wire_binding_checks'] = {
        'candidate_header': copy.deepcopy(relation_ref), 'source_cut': copy.deepcopy(independently_selected_cut),
        'prior_signature_binding': copy.deepcopy(request['prior_signature_binding']),
        'pair_contract_bindings': copy.deepcopy(request['pair_contract_bindings']),
        'qualifier_domain_bindings': copy.deepcopy(domains),
        'affected_carrier_successor_refs': copy.deepcopy(successors),
        'semantic_owner_review_binding': copy.deepcopy(request['semantic_owner_review_binding']),
        'canonical_writable_authority_ref': independently_selected_authority_ref}
    checked['actual_owner_outcome'] = None
    checked['public_handler_qualified'] = False
    return copy.deepcopy(proposal), checked
