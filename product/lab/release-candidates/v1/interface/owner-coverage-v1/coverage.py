"""Compile independently selected requirements into distinct pending voices.

This kernel proves exact candidate routing closure. It never promotes a
proposed requirement policy, Principal or RoleAssignment into current authority.
The selected policy and its source resolver belong to the host boundary.
"""
from dataclasses import dataclass
import hashlib
import json

class CoverageFault(ValueError):
    pass

def need(condition, message):
    if not condition:
        raise CoverageFault(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')

def parse(raw):
    need(type(raw) is bytes and len(raw) <= 1048576, 'bounded original bytes required')
    def pairs(items):
        value = {}
        for key, item in items:
            need(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=lambda _: need(False, 'nonfinite JSON'))
        compact(value)
        return value
    except (ValueError, UnicodeError) as error:
        raise CoverageFault('invalid original JSON') from error

def fields(value, names, message):
    need(type(value) is dict and set(value) == set(names.split()), message)

def binding(value):
    fields(value, 'ref sha256', 'closed exact binding required')
    need(type(value['ref']) is str and bool(value['ref']), 'binding reference required')
    digest = value['sha256']
    need(type(digest) is str and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), 'binding digest differs')
    return value

@dataclass(frozen=True)
class SelectedBytes:
    ref: str
    original: bytes
    expected_sha256: str

    def read(self):
        selected = binding({'ref': self.ref, 'sha256': self.expected_sha256})
        need(type(self.original) is bytes and sha(self.original) == selected['sha256'], 'independently selected original bytes changed')
        return parse(self.original)

    def pin(self):
        self.read()
        return {'ref': self.ref, 'sha256': self.expected_sha256}

@dataclass(frozen=True)
class Member:
    scope_ref: str
    target_original: bytes
    core: SelectedBytes
    requested_effect: str

    def selector(self):
        target, core = parse(self.target_original), self.core.read()
        fields(core, 'decision_ref category operation version_ref target_digest', 'complete Decision core required')
        need(type(target) is dict, 'complete runtime target required')
        need(all(target.get(k) == core[k] for k in ('decision_ref', 'category', 'operation', 'version_ref')), 'Decision core and target differ')
        need(sha(compact(target)) == core['target_digest'], 'Decision core complete target digest differs')
        need(type(self.scope_ref) is str and bool(self.scope_ref), 'exact member scope required')
        need(type(self.requested_effect) is str and bool(self.requested_effect), 'exact requested effect required')
        return {'scope_ref': self.scope_ref, 'decision_ref': core['decision_ref'], 'category': core['category'],
                'operation': core['operation'], 'version_ref': core['version_ref'], 'carrier_ref': target['carrier_ref'],
                'core_binding': self.core.pin(), 'complete_target_sha256': sha(self.target_original),
                'requested_effect_sha256': sha(self.requested_effect.encode('utf-8'))}

class OwnerCoverage:
    def __init__(self, selected_policy, source_cut_binding, source_guard, basis_resolver):
        need(type(selected_policy) is SelectedBytes, 'independent host policy selection required')
        need(callable(source_guard) and callable(basis_resolver), 'independent source guards and basis resolver required')
        self.selected = selected_policy
        self.policy_pin = selected_policy.pin()
        self.source_cut = compact(binding(source_cut_binding))
        self.guard_source, self.resolve_basis = source_guard, basis_resolver
        self.policy_original = selected_policy.original
        self.guard()

    def guard(self):
        self.guard_source()
        need(self.selected.original == self.policy_original and self.selected.pin() == self.policy_pin, 'captured independent requirement policy replaced')
        policy = self.selected.read()
        fields(policy, 'schema_version policy_ref source_cut_binding purpose requirement_posture rules authority_effect actual_owner_outcome', 'closed independently selected requirement policy required')
        need(policy['schema_version'] == 'lab-exact-owner-requirements/v1-candidate'
             and policy['purpose'] == 'candidate-review-preparation'
             and policy['requirement_posture'] == 'proposed-exact-requirements'
             and policy['authority_effect'] == 'none' and policy['actual_owner_outcome'] is None,
             'candidate requirements cannot claim current governing authority')
        need(type(policy['policy_ref']) is str and bool(policy['policy_ref']), 'requirement policy identity required')
        need(compact(binding(policy['source_cut_binding'])) == self.source_cut, 'requirement policy source cut differs')
        need(type(policy['rules']) is list and 1 <= len(policy['rules']) <= 64, 'bounded complete requirement rules required')
        return policy

    def compile(self, members, routes):
        policy = self.guard()
        need(type(members) is tuple and 1 <= len(members) <= 64 and all(type(m) is Member for m in members), 'independently prepared immutable member sequence required')
        need(type(routes) is tuple and len(routes) == len(members), 'every independent Decision requires an owner route')
        routes = parse(compact(list(routes)))
        need(len(policy['rules']) == len(members), 'complete required-owner rule closure missing')
        required, seen_decisions, seen_versions, checked_basis = [], set(), set(), {}
        for index, (member, rule, route) in enumerate(zip(members, policy['rules'], routes, strict=True)):
            selector = member.selector()
            need(selector['decision_ref'] not in seen_decisions and selector['version_ref'] not in seen_versions, 'duplicate independent target or Decision')
            seen_decisions.add(selector['decision_ref'])
            seen_versions.add(selector['version_ref'])
            fields(rule, 'selector required_roles basis_bindings', 'closed exact target requirement rule required')
            need(rule['selector'] == selector, 'governing requirement target/scope/core/effect or order differs')
            roles = rule['required_roles']
            need(type(roles) is list and 1 <= len(roles) <= 20 and all(type(r) is str and r.startswith('role:') and len(r) > 5 for r in roles), 'nonempty independently required roles needed')
            need(len(set(roles)) == len(roles), 'required roles must stay distinct')
            bases = rule['basis_bindings']
            need(type(bases) is list and 1 <= len(bases) <= 8, 'explicit source basis required for each requirement')
            need(len({compact(binding(b)) for b in bases}) == len(bases), 'duplicate requirement basis')
            for basis in bases:
                token = compact(basis)
                if token not in checked_basis:
                    selected = self.resolve_basis(dict(basis))
                    need(type(selected) is SelectedBytes and selected.pin() == basis, 'independently resolved requirement basis differs')
                    checked_basis[token] = selected
                checked_basis[token].read()
            fields(route, 'decision_ref core_binding owner_voices', 'closed owner route required')
            need(route['decision_ref'] == selector['decision_ref'] and route['core_binding'] == selector['core_binding'], 'owner route Decision/core order differs')
            voices = route['owner_voices']
            need(type(voices) is list and len(voices) == len(roles), 'every independently required role needs exactly one pending voice')
            seen_roles = set()
            for voice_index, (role, voice) in enumerate(zip(roles, voices, strict=True)):
                fields(voice, 'role_ref principal_ref recognition_basis_binding', 'closed owner voice required')
                need(voice['role_ref'] == role and role not in seen_roles, 'missing, duplicated or collapsed independently required role')
                seen_roles.add(role)
                principal = voice['principal_ref']
                need(type(principal) is str and principal.startswith(('principal:', 'person:')), 'exact Principal reference required; aliases are not inferred')
                recognition = binding(voice['recognition_basis_binding'])
                selected = self.resolve_basis(dict(recognition))
                need(type(selected) is SelectedBytes and selected.pin() == recognition, 'owner recognition original basis differs')
                recognition_body = selected.read()
                # This adapter preserves an explicit legacy declaration only.
                # Scope prose is retained as evidence, never interpreted into
                # a permission or a complete governing requirement.
                need(recognition_body.get('artifact_type_ref') == 'cal.artifact-type.owner-registry/v1', 'supported independent recognition source required')
                matches = [row for row in recognition_body.get('role_assignments', [])
                           if row.get('role_id') == role.removeprefix('role:') and row.get('principal_id') == principal]
                need(len(matches) == 1 and matches[0].get('decision_separation') == 'required', 'exact legacy role/Principal declaration missing; no alias inferred')
                need(type(matches[0].get('scope')) is str and bool(matches[0]['scope']), 'independent legacy scope declaration required')
                required.append({'core_index': index, 'voice_index': voice_index, 'selector': selector,
                                 'owner_role_ref': role, 'owner_principal_ref': principal,
                                 'requirement_basis_bindings': bases, 'recognition_basis_binding': recognition,
                                 'legacy_assignment_id': matches[0]['assignment_id'], 'legacy_scope_prose': matches[0]['scope'],
                                 'selected_outcome': None, 'current_owner_authority_verified': False})
        need(self.guard() == policy, 'requirement policy changed during compilation')
        self.guard_source()
        # Equality with proposed requirements is deliberately different from
        # recognition of the repository's complete current governing role set.
        return {'schema_version': 'lab-owner-coverage-result/v1-candidate', 'posture': 'blocked',
                'policy_binding': self.selected.pin(), 'source_cut_binding': parse(self.source_cut),
                'candidate_rule_closure_verified': True, 'current_governing_coverage_verified': False,
                'current_owner_authority_verified': False, 'ordered_required_owner_responses': required,
                'gaps': [{'gap_ref': 'gap:current-governing-owner-coverage', 'description': 'Exact proposed requirements were compiled. Independently current governing requirements and owner authority remain unresolved.', 'affected_core_bindings': [m.core.pin() for m in members]}],
                'actual_owner_outcome': None, 'authority_effect': 'none'}
