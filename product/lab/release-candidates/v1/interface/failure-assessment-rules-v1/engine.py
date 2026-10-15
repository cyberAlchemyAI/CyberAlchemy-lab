"""Exact failure references, independent evidence axes and declared thresholds.

This kernel authenticates no caller and creates no proposal or Incident. Its
host must supply the complete validated current/prospective selection and bind
the basis and threshold through current policy before dispatch.
"""
import copy
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RULE_ROOT = HERE.parent / 'classification-rules-v2'
RULE_SOURCE = '838255c60c56c37ecfb8af10edf4708c97efc9b2b42adb51df5e773cdbf934e1'
RULE_PROOF = 'f37815799df1b906c8ba8703c551862f66600cae8948e38c725899e5b65449b3'
FIELDS = ('scope_ref', 'identity_ref', 'version_ref', 'carrier_ref', 'byte_sha256')
AXES = ('occurrence', 'mode', 'cause', 'impact', 'containment', 'recovery', 'uncertainty')
EVIDENCE_KINDS = ('evidence-set', 'operational-observation', 'observation',
                  'measurement-result', 'finding', 'feedback-record')


class Refusal(ValueError):
    pass


def require(value, reason):
    if not value:
        raise Refusal(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    require(type(raw) is bytes, 'original bytes required')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'duplicate JSON member')
            result[key] = value
        return result
    def finite(token):
        value = float(token)
        require(math.isfinite(value), 'nonfinite JSON number')
        return value
    def invalid(token):
        raise Refusal('nonfinite JSON token')
    try:
        result = json.loads(raw, object_pairs_hook=unique, parse_float=finite,
                            parse_constant=invalid)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise Refusal('invalid original JSON') from error
    require(type(result) is dict, 'closed object required')
    return result


def check_binding(binding, raw):
    require(type(binding) is dict and set(binding) == {'ref', 'sha256'},
            'closed exact binding required')
    require(type(binding['ref']) is str and bool(binding['ref'])
            and type(raw) is bytes and binding['sha256'] == sha(raw),
            'binding original bytes differ')


@dataclass(frozen=True)
class Record:
    header: dict
    raw: bytes


class AssessmentRules:
    def __init__(self, source_sha256):
        self.pin = source_sha256
        self.verify_source()
        schemas = []
        for row in self.manifest['schemas']:
            schemas.append((self.manifest['schema_ids'][row['path']], parse((ROOT / row['path']).read_bytes())))
        registry = Registry().with_resources((identifier, Resource.from_contents(s, default_spec=DRAFT202012))
                                             for identifier, s in schemas)
        self.validators = {identifier: Draft202012Validator(s, registry=registry,
                            format_checker=FormatChecker()) for identifier, s in schemas}
        self.kind_schemas = self.manifest['kind_schemas']
        proof = parse((RULE_ROOT / 'receipts/proof-0001.json').read_bytes())
        require(sha((RULE_ROOT / 'source-manifest.json').read_bytes()) == RULE_SOURCE
                and sha((RULE_ROOT / 'receipts/proof-0001.json').read_bytes()) == RULE_PROOF
                and proof['result'] == 'PASS' and proof['actual_cases'] == 21
                and proof['actual_terminal_exit_code'] == 0,
                'qualified classification primitive differs')
        spec = importlib.util.spec_from_file_location('_cal_failure_classification_rules_v2', RULE_ROOT / 'engine.py')
        # dataclasses need the actual module entry during execution.
        import sys
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.classification = module

    def verify_source(self):
        raw = (HERE / 'source-manifest.json').read_bytes()
        require(type(self.pin) is str and len(self.pin) == 64 and sha(raw) == self.pin,
                'independently selected failure rule source differs')
        manifest = parse(raw)
        for row in manifest['files']:
            path = ROOT / row['path']
            require(not path.is_symlink() and not any(p.is_symlink() for p in path.parents),
                    'symbolic failure rule source refused')
            require(sha(path.read_bytes()) == row['sha256'], 'failure rule input changed')
        self.manifest = manifest

    def valid(self, identifier, value):
        require(identifier in self.validators and self.validators[identifier].is_valid(value),
                'selected original schema refused value')

    def record(self, record, scope):
        require(type(record) is Record and type(record.header) is dict
                and set(record.header) == set(FIELDS), 'closed five-axis record header required')
        header = record.header
        self.valid('urn:cyberalchemy-lab:failure-assessment:artifact-ref:v1-candidate', header)
        body = parse(record.raw)
        require(header['carrier_ref'] in self.kind_schemas, 'unselected record carrier')
        self.valid(self.kind_schemas[header['carrier_ref']], body)
        require(header['scope_ref'] == body['scope_ref'] == scope
                and header['identity_ref'] == body['node_id']
                and header['version_ref'].startswith(body['node_id'] + '@')
                and len(header['version_ref']) > len(body['node_id']) + 1
                and header['byte_sha256'] == sha(record.raw), 'record header or original bytes differ')
        return body

    def evaluate(self, records, request, candidate, *, basis_binding, basis_raw,
                 material_bytes, selected_threshold_binding=None):
        self.verify_source()
        self.valid('urn:cyberalchemy-lab:protocol:failure-assessment-request:v1-candidate', request)
        require(type(records) in (tuple, list) and type(material_bytes) is dict,
                'complete selected records and original material map required')
        scope = request['occurrence']['scope_ref']
        selected = {}
        for record in records:
            body = self.record(record, scope)
            require(record.header['version_ref'] not in selected, 'duplicate exact record revision')
            selected[record.header['version_ref']] = (record, body)

        def resolve(ref, kind=None):
            require(type(ref) is str and bool(ref), 'exact reference required')
            matches = [pair for version, pair in selected.items()
                       if version == ref or pair[1]['node_id'] == ref]
            require(len(matches) == 1, 'missing or ambiguous exact record reference')
            record, body = matches[0]
            require(kind is None or body['kind'] == kind, 'reference semantic kind differs')
            return record, body

        def exact(header, kind):
            record, body = resolve(header['version_ref'], kind)
            require(record.header == header, 'requested five-axis header differs')
            return record, body

        occurrence, ob = exact(request['occurrence'], 'failure-occurrence')
        assignment, ab = exact(request['mode_assignment'], 'classification-assignment')
        require(ab['payload']['subject_ref'] == ob['node_id']
                and ab['payload']['subject_version_ref'] == occurrence.header['version_ref']
                and ab['payload']['status'] in ('active', 'candidate-annotation'),
                'mode annotation selects another occurrence or inactive status')
        scheme, sb = resolve(ab['payload']['scheme_version_ref'], 'classification-scheme')
        value, vb = resolve(ab['payload']['value_ref'], 'classification-value')
        mode, mb = resolve(vb['payload']['definition_ref'], 'failure-mode')
        subject, subject_body = resolve(ob['payload']['subject_ref'])
        require(mb['payload']['subject_kind_ref'] in (subject_body['kind'], subject.header['carrier_ref']),
                'failure mode selects another subject kind')
        require(ob['payload']['expected_boundary_ref'] == mb['payload']['expected_boundary_ref'],
                'occurrence and mode expected boundary differ')
        assessment = self.record(candidate, scope)
        require(assessment['kind'] == 'failure-assessment'
                and assessment['lifecycle_state'] == 'candidate', 'candidate failure assessment required')
        check_binding(request['assessment_candidate_binding'], candidate.raw)
        payload = assessment['payload']
        require(resolve(payload['occurrence_ref'], 'failure-occurrence')[0] is occurrence
                and resolve(payload['mode_assignment_ref'], 'classification-assignment')[0] is assignment,
                'assessment applies to another occurrence or annotation')
        causes = [exact(ref, 'hypothesis')[0] for ref in request['cause_hypothesis_refs']]
        require(len(causes) == len({r.header['version_ref'] for r in causes}), 'duplicate exact cause hypothesis')
        selected_causes = [resolve(ref, 'hypothesis')[0] for ref in payload['cause_hypothesis_refs']]
        require({r.header['version_ref'] for r in selected_causes} == {r.header['version_ref'] for r in causes},
                'candidate cause hypothesis set differs')
        evidence = {}
        for binding in request['evidence_bindings']:
            require(binding['ref'] not in evidence, 'duplicate evidence binding identity')
            check_binding(binding, material_bytes.get(binding['ref']))
            evidence[binding['ref']] = binding

        def provenance(ref, visiting=()):
            if ref in evidence:
                return [copy.deepcopy(evidence[ref])]
            require(ref not in visiting, 'cyclic evidence without a selected original source')
            record, body = resolve(ref)
            require(body['kind'] in EVIDENCE_KINDS, 'evidence reference has another semantic kind')
            # A selected original record may itself be an evidence item.
            direct = [binding for binding in evidence.values() if binding['sha256'] == sha(record.raw)]
            if direct:
                return copy.deepcopy(direct)
            refs = list(body['evidence_refs'])
            if body['kind'] == 'evidence-set':
                refs += body['payload']['source_refs'] + body['payload']['item_refs']
            else:
                refs += body['payload'].get('evidence_refs', [])
            require(bool(refs), 'evidence record has no selected original-byte provenance')
            result = []
            for child in refs:
                result += provenance(child, visiting + (ref,))
            return result

        require(bool(ob['payload']['observed_manifestations']) and bool(ob['payload']['detection_evidence_refs']),
                'occurrence lacks observed manifestation or detection evidence')
        for ref in ob['payload']['detection_evidence_refs'] + assessment['evidence_refs']:
            provenance(ref)
        require(bool(assessment['evidence_refs']), 'assessment lacks explicit evidence')
        check_binding(basis_binding, basis_raw)
        basis = parse(basis_raw)
        self.valid('urn:cyberalchemy-lab:failure-assessment-basis:v1-candidate', basis)
        require(basis['scope_ref'] == scope and basis['source_cut'] == request['source_cut']
                and basis['assessment_binding'] == request['assessment_candidate_binding'],
                'independently selected axis basis differs')
        for axis in AXES:
            for binding in basis['axis_basis'][axis]:
                require(evidence.get(binding['ref']) == binding, 'axis evidence outside requested original basis')
        kernel = self.classification
        originals = [kernel.ExactRecord(r.header['version_ref'], r.raw, sha(r.raw)) for r in records]
        classification = kernel.evaluate(kernel.ExactRecords(originals, scope),
            subject_ref=occurrence.header['version_ref'], scheme_ref=scheme.header['version_ref'],
            value_ref=value.header['version_ref'], axis_ref=ab['payload']['axis_ref'], candidate=ab,
            basis_bindings=request['evidence_bindings'], material_bytes=material_bytes,
            existing_assignment_refs=[r.header['version_ref'] for r, b in selected.values()
                                      if b['kind'] == 'classification-assignment' and r is not assignment])
        threshold = {'result': 'not-requested', 'Incident_created': False}
        wanted = request['incident_threshold_binding']
        require(wanted == selected_threshold_binding, 'threshold is not independently selected')
        threshold_result = 'pass'
        if wanted is not None:
            check_binding(wanted, material_bytes.get(wanted['ref']))
            policy = parse(material_bytes[wanted['ref']])
            self.valid('urn:cyberalchemy-lab:failure-incident-threshold:v1-candidate', policy)
            require(policy['scope_ref'] == scope and policy['source_cut'] == request['source_cut'],
                    'threshold scope or exact source cut differs')
            cohort = []
            for header in policy['occurrences']:
                record, body = exact(header, 'failure-occurrence')
                require(record.header['version_ref'] not in cohort, 'duplicate threshold occurrence')
                require(bool(body['payload']['observed_manifestations'])
                        and bool(body['payload']['detection_evidence_refs']), 'threshold occurrence lacks evidence')
                for ref in body['payload']['detection_evidence_refs']:
                    provenance(ref)
                cohort.append(record.header['version_ref'])
            require(occurrence.header['version_ref'] in cohort, 'threshold applies to another cohort')
            if policy['rule'] != 'minimum-evidenced-occurrences':
                threshold_result = 'not-evaluable'
            else:
                threshold_result = 'pass' if len(cohort) >= policy['minimum_count'] else 'fail'
            threshold = {'result': threshold_result, 'rule': policy['rule'],
                         'selected_occurrence_refs': cohort, 'minimum_count': policy['minimum_count'],
                         'original_binding': copy.deepcopy(wanted), 'Incident_created': False,
                         'production_applicability_inferred': False}
        result = 'fail' if 'fail' in (classification['result'], threshold_result) else (
                 'not-evaluable' if 'not-evaluable' in (classification['result'], threshold_result) else 'pass')
        axes = {'occurrence': payload['occurrence_posture'], 'mode': payload['mode_posture'],
                'cause': copy.deepcopy(payload['cause_hypothesis_refs']), 'impact': payload['impact_posture'],
                'containment': payload['containment_posture'], 'recovery': payload['recovery_posture'],
                'uncertainty': copy.deepcopy(payload['uncertainty_refs'])}
        self.verify_source()
        return {'schema_version': 'lab-failure-assessment-rule-checks/v1-candidate',
                'result': result, 'assessment_header': copy.deepcopy(candidate.header),
                'source_cut': copy.deepcopy(request['source_cut']), 'axis_claims': axes,
                'axis_basis': copy.deepcopy(basis['axis_basis']), 'classification': classification,
                'incident_threshold': threshold, 'confirmed_cause_inferred': False,
                'recovery_or_control_effectiveness_inferred': False, 'whole_API_qualified': False,
                'current_Agent_qualified': False, 'authority_effect': 'none', 'actual_owner_outcome': None,
                'claim_ceiling': 'Exact carrier/reference/evidence consistency and declared threshold only. Axis postures remain authored claims. Current authenticated host, complete source cut, proposal cores, public dispatch, recovery, causality and effectiveness require separate evidence.'}
