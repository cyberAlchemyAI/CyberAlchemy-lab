"""Exact typed proposal preparation inside the original authenticated dispatcher.

No owner decision, semantic verdict, relation registration or live transaction
is produced. Optional scope hypotheses remain explicitly unprovisioned.
"""
import copy
import hashlib
import importlib
import importlib.util
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from .selection import require, schema_paths, target_metadata

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
HELPER = HERE.parent / 'typed-extension-preparation-v11'
HELPER_SOURCE = '56a9db7a496302d1811d55df2c217dadef01af9ee6b60889e7771e8b103f8674'
HELPER_PROOF = 'ac2400fc8882c1fd70e528792b3935314e18c9c66174dc9bb13ee78814e31612'
CATALOG_PROFILE = 'bb8ab4538a524031924d8fa5c3352c2f9bc1cd66893c39222615160d0c9fd302'
CATALOG_REVIEW = 'aa9041fe1f8d1a5988f727a752081a62f1ecdcff26a93ace4d615f01776f414c'
REPRESENTATIONS = '435a78f4b974d0f5ad1679940c779be256cad349ee18d98c0d1b3ae99a3b0cfc'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def binding(path):
    return {'ref': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}


def helpers():
    source, proof = HELPER / 'source-manifest.json', HELPER / 'receipts/proof-0001.json'
    require(sha(source.read_bytes()) == HELPER_SOURCE and sha(proof.read_bytes()) == HELPER_PROOF,
            'independently selected typed helper source or complete proof differs')
    import json
    selected, checked = json.loads(source.read_bytes()), json.loads(proof.read_bytes())
    require(checked['result'] == 'PASS' and checked['actual_cases'] == 144
            and checked['actual_terminal_exit_code'] == 0,
            'complete actual typed helper proof required')
    for row in selected['files']:
        path = ROOT / row['path']
        require(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink()
                and not any(parent.is_symlink() for parent in path.parents)
                and sha(path.read_bytes()) == row['sha256'], 'typed helper input changed')
    name = '_cal_public_typed_host_helpers_v11'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, HELPER / '__init__.py',
                                                    submodule_search_locations=[str(HELPER)])
        package = importlib.util.module_from_spec(spec)
        sys.modules[name] = package
        spec.loader.exec_module(package)
    modules = [importlib.import_module(name + '.' + suffix) for suffix in
               ('adapter', 'source_selection', 'prospective', 'postimage')]
    require(all(Path(module.__file__).resolve() == HELPER / (suffix + '.py')
                for module, suffix in zip(modules, ('adapter', 'source_selection', 'prospective', 'postimage'))),
            'unselected typed helper module')
    return modules


class TypedPreparation:
    def __init__(self, host, routing_binding, host_source_binding):
        module = sys.modules.get(type(host).__module__)
        require(module is not None and getattr(module, 'Service', None) is type(host),
                'actual selected Service instance required')
        service_path = Path(module.__file__).resolve()
        require(service_path.parent.parent == HERE.parent and service_path.name == 'service.py',
                'foreign Service source refused')
        host_manifest = service_path.parent / 'source-manifest.json'
        require(host_source_binding == {'path': host_manifest.relative_to(ROOT).as_posix(),
                                       'sha256': sha(host_manifest.read_bytes())},
                'exact independent host source selection required')
        self.package = type(host).__module__.rsplit('.', 1)[0]
        self.guard_module = importlib.import_module(self.package + '.guard')
        selected = self.guard_module.verify(host_source_binding['sha256'])
        for path in (HERE / 'preparation.py', HERE / 'selection.py', HERE / 'routing.schema.json'):
            require({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path.read_bytes())}
                    in selected['files'], 'typed composition source is outside the selected host closure')
        auth = importlib.import_module(self.package + '.auth')
        require(type(host.channel) is auth.ReaderChannel,
                'typed operator composition requires the actual selected authenticated ReaderChannel')
        self.host, self.vault, self.schemas = host, host.vault, host.schemas
        self.P = importlib.import_module(self.package + '.protocol')
        self.H = importlib.import_module(self.package + '.handlers')
        self.host_source_binding = copy.deepcopy(host_source_binding)
        self.A, self.S, self.R, self.T = helpers()
        self.routing_binding = copy.deepcopy(routing_binding)
        require(host.channel.policy_guard().get('typed_control', {}).get('routing_binding') == routing_binding,
                'typed routing is not independently selected by the current signed policy')
        self.raw = self.vault.object_read(routing_binding)
        self.routing = self.P.frame_parse(self.raw)
        schema = self.P.frame_parse((HERE / 'routing.schema.json').read_bytes())
        require(Draft202012Validator(schema, registry=self.schemas.registry,
                                     format_checker=FormatChecker()).is_valid(self.routing),
                'closed typed routing contract required')
        require(self.routing['helper_source_binding'] == {'ref': str((HELPER / 'source-manifest.json').relative_to(ROOT)), 'sha256': HELPER_SOURCE}
                and self.routing['helper_proof_binding'] == {'ref': str((HELPER / 'receipts/proof-0001.json').relative_to(ROOT)), 'sha256': HELPER_PROOF},
                'routing selects another typed helper or proof')
        require(self.routing['representation_profile_binding'] == binding(service_path.parent / 'catalog-representations.json')
                and self.routing['representation_profile_binding']['sha256'] == REPRESENTATIONS,
                'independently selected public representation profile differs')

    def read(self, selected):
        require(type(selected) is dict and set(selected) == {'ref', 'sha256'},
                'closed exact typed material binding required')
        if selected['ref'].startswith('workspace-object:'):
            raw = self.vault.object_read(selected)
        else:
            raw = self.vault.material(selected)
        require(sha(raw) == selected['sha256'], 'exact typed material bytes differ')
        return raw

    def preflight(self, message, outer, key):
        self.guard_module.verify(self.host_source_binding['sha256'])
        self.schemas.guard()
        helpers()
        context, policy = self.host.channel.guard(), self.host.channel.policy_guard()
        require('typed.extension.prepare' in policy['allowed_operations']
                and context['limits']['max_actions'] >= 1,
                'typed preparation lacks independently selected operation or action permission')
        actor = {field: context[field] for field in
                 ('principal_ref', 'agent_instance_ref', 'assignment_ref', 'session_ref')}
        actor['role_assignment_refs'] = context['role_assignment_bindings']
        require(message['actor'] == actor, 'typed Actor differs from actual authenticated transport')
        require(message['source_cut'] == outer == self.routing['source_cut'] == self.H.cut(self.host.handlers.view),
                'typed routing and request must select the actual current source cut')
        require(policy.get('typed_control', {}).get('routing_binding') == self.routing_binding
                and self.vault.object_read(self.routing_binding) == self.raw,
                'independently selected typed routing bytes changed')
        proposal_raw = self.read(self.routing['proposal_binding'])
        proposal = self.P.frame_parse(proposal_raw)
        require(self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:typed-extension-request:v1-candidate', message)
                and self.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:change-proposal:v1-candidate', proposal),
                'original typed request and ChangeProposal contracts required')
        require(proposal['actor'] == actor and proposal['base_cut'] == outer
                and proposal['idempotency_key'] == key and proposal['scope_ref'] == self.routing['scope_ref'],
                'original proposal Actor, current cut, outer key or scope differs')
        require(message['canonical_writable_authority_ref'] == self.routing['canonical_writable_authority_ref'],
                'typed authority differs from independently selected routing')
        self.host.candidates.preflight(proposal, outer)
        target_metadata(proposal, self.vault.manifest)
        schema_paths(self.routing, proposal)
        return proposal_raw, proposal, actor

    def catalog(self):
        inspector = self.A.kernel()
        profiles = importlib.import_module(inspector.__package__ + '.profiles')
        sources = importlib.import_module(inspector.__package__ + '.sources')
        path = self.A.KERNEL / 'profiles/selections.json'
        rows = self.A.parse(path.read_bytes())['selections']
        matches = [row for row in rows if row['name'] == 'd75']
        require(len(matches) == 1, 'independent catalog profile selection is ambiguous')
        row = matches[0]
        require(row['profile_sha256'] == CATALOG_PROFILE and row['review_sha256'] == CATALOG_REVIEW
                and self.routing['catalog_profile_binding'] == {'ref': row['profile_path'], 'sha256': CATALOG_PROFILE}
                and self.routing['catalog_review_binding'] == {'ref': row['review_path'], 'sha256': CATALOG_REVIEW},
                'catalog profile or review differs from the original kernel selection')
        selected = profiles.select(ROOT, **{k: v for k, v in row.items()
                                           if k not in ('name', 'source_materials', 'source_bytes')})
        snapshot = sources.capture(selected)
        return snapshot, sources

    def prepare(self, message, request, outer, key):
        guarded = importlib.import_module(self.package + '.guarded_candidate')
        with guarded.calculation(self.host) as writer:
            proposal_raw, proposal, actor = self.preflight(message, outer, key)
            inspection = self.P.frame_parse(self.read(self.routing['inspection_binding']))
            snapshot, sources = self.catalog()
            catalog = self.S.select_bound_catalog(snapshot, expected_profile_sha256=CATALOG_PROFILE,
                expected_snapshot_digest=self.routing['catalog_snapshot_digest'], evidence_bytes={})
            evidence = {}
            # Only closed original binding fields select bytes. Every read is
            # checked against the independently provisioned Vault inventory.
            def collect(value):
                if type(value) is dict:
                    if set(value) == {'ref', 'sha256'}:
                        if value['ref'] in catalog['materials']:
                            raw = catalog['materials'][value['ref']]
                            require(sha(raw) == value['sha256'], 'captured canonical evidence binding differs')
                        else:
                            raw = self.read(value)
                        require(value['ref'] not in evidence or evidence[value['ref']] == raw,
                                'candidate binding shadows another exact material')
                        evidence[value['ref']] = raw
                    else:
                        for item in value.values():
                            collect(item)
                elif type(value) is list:
                    for item in value:
                        collect(item)
            # Prior signature bytes come from the complete captured catalog,
            # not an arbitrary caller-selected repository file.
            request_evidence = copy.deepcopy(message)
            request_evidence.pop('prior_signature_binding', None)
            collect(request_evidence)
            collect(inspection)
            for ref, raw in evidence.items():
                require(ref not in catalog['materials'] or catalog['materials'][ref] == raw,
                        'candidate evidence cannot shadow independently captured canonical bytes')
                catalog['materials'][ref] = raw
            def material(selected):
                if selected['ref'] in catalog['materials']:
                    raw = catalog['materials'][selected['ref']]
                    require(sha(raw) == selected['sha256'], 'exact captured catalog material differs')
                    return raw
                return self.read(selected)
            paths = schema_paths(self.routing, proposal)
            prospective, pending = self.R.resolve_prospective_carriers(catalog, inspection, proposal,
                read_material=material, independently_selected_schema_paths=paths)
            impact = self.S.assess_carrier_impacts(prospective, inspection)
            successors = self.S.resolve_impacted_successors(impact, proposal, material)
            original_proposal, wire = self.A.inspect_wire(message, proposal=proposal, proposal_raw=proposal_raw,
                inspection=inspection, independently_selected_actor=actor, independently_selected_cut=outer,
                independently_selected_key=key,
                independently_selected_authority_ref=self.routing['canonical_writable_authority_ref'],
                independently_selected_successor_refs=successors, current_relations=catalog['relations'],
                endpoint_contracts=prospective['endpoints'], evidence_bytes=prospective['materials'],
                material_reader=material, protocol_valid=self.schemas.protocol_valid)
            view = self.host.handlers.selected_view
            C, projection, config = view.handle.common, view.data['projection'], view.data['config']
            baseline = self.P.source.parse(view.originals['baseline.json'])
            config_sealed = self.P.source.parse(view.originals['config.json'])
            expected = self.P.source.parse(self.P.source.original(view.selected['expected_replay_binding']))
            C.verify_seal(config_sealed)
            original_config = {k: v for k, v in config_sealed.items() if k != 'digest'}
            require(view.data['baseline'] == baseline and config == original_config
                    and sha(view.originals['config.json']) == expected['config_sha256']
                    and baseline['snapshot_digest'] == expected['baseline_snapshot_digest'],
                    'actual sealed original runtime baseline or configuration differs')
            scope_binding = self.routing['scope_preparation_profile_binding']
            scope_raw = None if scope_binding is None else self.read(scope_binding)
            postimage = self.T.prepare_exact_postimage(catalog, inspection, impact, original_proposal,
                projection=projection, config=config, head=view.data['head']['transaction_digest'],
                expected_projection_digest=expected['projection_sha256'],
                expected_config_digest=C.digest(original_config), expected_head=expected['expected_head'],
                read_material=material, independently_selected_schema_paths=paths,
                independently_selected_catalog_snapshot=snapshot, independently_selected_runtime_baseline=baseline,
                expected_runtime_baseline_digest=C.digest(baseline), expected_catalog_profile_sha256=CATALOG_PROFILE,
                independently_selected_representation_profile_bytes=(Path(sys.modules[type(self.host).__module__].__file__).parent / 'catalog-representations.json').read_bytes(),
                expected_representation_profile_sha256=REPRESENTATIONS,
                read_source_material=lambda b: self.P.source.original({'path': b['ref'], 'sha256': b['sha256']}),
                independently_selected_scope_preparation_profile_bytes=scope_raw,
                expected_scope_preparation_profile_sha256=None if scope_binding is None else scope_binding['sha256'])
            require(sources.freshness(ROOT, snapshot)['status'] == 'current', 'captured typed catalog changed')
            self.preflight(message, outer, key)
            require(self.host.handlers.current(), 'typed current source changed during preparation')
            checked = {'schema_version': 'lab-typed-host-preparation-checks/v1-candidate',
                       'result': 'PASS', 'source_cut': copy.deepcopy(outer),
                       'request_binding': copy.deepcopy(request), 'routing_binding': self.routing_binding,
                       'proposal_binding': self.routing['proposal_binding'], 'wire': wire,
                       'carrier_impact': impact, 'prospective': pending, 'postimage': postimage,
                       'genuine_semantic_owner_verdict_provided': False,
                       'operational_preparation_ready': False, 'runtime_admission_authorized': False,
                       'actual_owner_outcome': None, 'authority_effect': 'none'}
            evidence_binding = writer.object(self.P.source.encoded(checked))
        return original_proposal, [evidence_binding]
