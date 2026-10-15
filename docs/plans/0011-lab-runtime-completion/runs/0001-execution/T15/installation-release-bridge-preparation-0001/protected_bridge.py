"""Trusted host bridge to the original reviewed protected reader and typed graph."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import stat
from .native_launch import closed, module_origin, need

ANCHOR_FIELDS = ('principal_ref', 'public_key_b64', 'source_binding', 'profile_binding', 'source_cut', 'operation',
                 'selector_binding', 'grant_binding', 'selector_locator', 'grant_locator')
GRAPH_FIELDS = ('policy_binding', 'eligibility_binding', 'source_binding', 'profile_binding', 'source_cut', 'allowed_states')
REVIEW_VERSION = 'lab-release-typed-review-closure/v3-candidate'
REVIEW_FIELDS = ('schema_version', 'member_bindings', 'protected_selector_binding', 'semantic_policy_binding',
                'eligibility_binding', 'semantic_member_headers', 'semantic_roots', 'semantic_edges',
                'open_gaps', 'typed_semantic_graph_acyclic', 'current_protected_proof_verified',
                'original_full_proof_status', 'owner_review_preconditions_resolved', 'final_release_decision_required')

@contextmanager
def control_root(root):
    closed(root, ('id', 'path', 'device', 'inode', 'uid', 'mode'))
    path = Path(root['path']); need(path.is_absolute() and '..' not in path.parts and path.as_posix() == root['path'], 'canonical custody root required')
    need(root['uid'] == os.geteuid() and root['mode'] == 0o700, 'independently selected private control ownership required')
    fds = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    try:
        for part in path.parts[1:]: fds.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        value = os.fstat(fds[-1])
        need((value.st_dev, value.st_ino, value.st_uid, stat.S_IMODE(value.st_mode)) == (root['device'], root['inode'], root['uid'], root['mode']), 'custody root identity differs')
        yield fds[-1]
        for index, part in enumerate(path.parts[1:]):
            value = os.stat(part, dir_fd=fds[index], follow_symlinks=False); opened = os.fstat(fds[index+1])
            need((value.st_dev, value.st_ino, value.st_mode) == (opened.st_dev, opened.st_ino, opened.st_mode), 'custody ancestor detached')
    finally:
        for fd in reversed(fds): os.close(fd)

def control_bytes(root, locator, binding):
    closed(locator, ('root_id', 'path', 'size', 'device', 'inode', 'uid', 'mode')); closed(binding, ('ref', 'sha256'))
    relative = Path(locator['path'])
    need(locator['root_id'] == root['id'] and not relative.is_absolute() and relative.as_posix() == locator['path']
         and relative.parts and '..' not in relative.parts and locator['mode'] == 0o600 and locator['uid'] == os.geteuid()
         and type(locator['size']) is int and 0 <= locator['size'] <= 64*1024*1024, 'closed private custody locator required')
    with control_root(root) as parent:
        fds = []
        try:
            current = parent
            for part in relative.parts[:-1]:
                fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current); fds.append(fd); current = fd
                value = os.fstat(fd); need(value.st_uid == os.geteuid() and not stat.S_IMODE(value.st_mode) & 0o022, 'custody intermediate directory differs')
            fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=current); fds.append(fd)
            before = os.fstat(fd)
            identity = lambda s: (s.st_dev, s.st_ino, s.st_uid, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
            need(stat.S_ISREG(before.st_mode) and (before.st_dev, before.st_ino, before.st_uid, stat.S_IMODE(before.st_mode), before.st_size)
                 == (locator['device'], locator['inode'], locator['uid'], locator['mode'], locator['size']), 'custody control file identity differs')
            chunks = []; length = 0
            while True:
                raw = os.read(fd, 1024*1024)
                if not raw: break
                chunks.append(raw); length += len(raw); need(length <= locator['size'], 'custody control grew')
            raw = b''.join(chunks)
            need(identity(before) == identity(os.fstat(fd)) == identity(os.stat(relative.name, dir_fd=current, follow_symlinks=False))
                 and len(raw) == locator['size'] and hashlib.sha256(raw).hexdigest() == binding['sha256'], 'custody control bytes/attachment differ')
            return raw
        finally:
            for fd in reversed(fds): os.close(fd)

class ProtectedHostBridge:
    def __init__(self, selection, protected_module, graph_module, module_bindings, repository):
        closed(selection, ('custody_anchor', 'control_roots', 'binding_routes', 'semantic_selection', 'readiness_version', 'observation_schema_binding', 'historical_original_proof'))
        module_origin(protected_module, module_bindings['protected_inputs'], repository)
        module_origin(graph_module, module_bindings['semantic_graph'], repository)
        need(graph_module.ProtectedReader is protected_module.ProtectedReader, 'typed graph must consume the actual accepted reader type')
        self.value = selection; self.protected = protected_module; self.graph = graph_module; self.root = Path(repository)
        need(selection['readiness_version'] == REVIEW_VERSION, 'explicit successor readiness observation version required')
        self._seal = protected_module.canonical(selection)
        closed(selection['custody_anchor'], ANCHOR_FIELDS)
        self.anchor = protected_module.CustodyAnchor(**selection['custody_anchor'])
        historical = selection['historical_original_proof']
        closed(historical, ('status', 'unavailable_binding', 'unavailable_count'))
        need(historical == {'status': 'REFUSED', 'unavailable_binding': {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json', 'sha256': '4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'}, 'unavailable_count': 25}, 'original historical refusal cannot be promoted or pruned')
        self.reader = None

    def bind(self, builder):
        host = builder.host; anchor = self.anchor
        need(anchor.principal_ref == host.channel.context['principal_ref'] and anchor.source_cut == builder.plan['source_cut']
             and anchor.profile_binding == host.schemas.profile_binding and anchor.operation == builder.operation, 'trusted host principal/profile/cut/operation differs')
        expected_source = host.schemas.profile_path.parent / 'source-manifest.json'
        need(anchor.source_binding['ref'] == str(expected_source.relative_to(self.root)),
             'independent current API source origin differs')
        self.builder = builder

    def open_reader(self):
        need(self.protected.canonical(self.value) == self._seal, 'protected host control mutated')
        roots = {r['id']: r for r in self.value['control_roots']}
        need(len(roots) == len(self.value['control_roots']), 'duplicate custody bootstrap root')
        a = self.anchor
        selector = control_bytes(roots[a.selector_locator['root_id']], a.selector_locator, a.selector_binding)
        grant = control_bytes(roots[a.grant_locator['root_id']], a.grant_locator, a.grant_binding)
        reader = self.protected.ProtectedReader(selector, grant, a)
        need(all(reader.roots[k] == v for k, v in roots.items()), 'custody bootstrap roots differ from selected original reader roots')
        return reader

    @contextmanager
    def boundary(self, *, semantics=True):
        self.builder.guard()
        reader = self.open_reader()
        with reader.boundary():
            if semantics: self.verify_semantics(reader)
            try: yield reader
            finally: self.builder.guard()

    def verify_semantics(self, reader):
        selected = self.value['semantic_selection']
        need(selected is not None, 'production per-record semantic/proof/current-context dispositions remain unselected')
        closed(selected, ('anchor', 'policy_file_id', 'declared_edges', 'root_refs'))
        closed(selected['anchor'], GRAPH_FIELDS)
        value = dict(selected['anchor']); value['allowed_states'] = tuple(value['allowed_states'])
        return self.graph.verify_graph(reader, selected['policy_file_id'], selected['declared_edges'], selected['root_refs'], self.graph.GraphAnchor(**value))

    def read_selected(self, selected):
        closed(selected, ('ref', 'sha256'))
        rows = [r for r in self.value['binding_routes'] if r['binding'] == selected]
        if not rows: return None
        need(len(rows) == 1, 'duplicate protected route')
        row = rows[0]; closed(row, ('binding', 'file_id', 'kind'))
        reader = self.open_reader(); entry = reader.files.get(row['file_id'])
        need(entry is not None and entry['logical_path'] == selected['ref'] and entry['sha256'] == selected['sha256'] and entry['kind'] == row['kind'], 'protected route does not select exact typed input')
        with reader.boundary(): return reader.read(row['file_id'], row['kind'])

    def review_graph(self, observed, roots):
        # v2 remains a byte-binding digest graph. This new v3 contract separately
        # verifies complete protected proof and actual schema-declared semantics.
        closed(observed, REVIEW_FIELDS)
        schema_binding=self.value['observation_schema_binding'];closed(schema_binding,('path','sha256'))
        path=self.root/schema_binding['path']
        need(path.is_absolute() and path.is_relative_to(self.root) and '..' not in path.parts and not any(p.is_symlink() for p in (path,*path.parents)), 'observation schema origin alias')
        raw=path.read_bytes();need(hashlib.sha256(raw).hexdigest()==schema_binding['sha256'],'independent observation schema bytes differ')
        self.graph.Draft202012Validator(self.protected.parse(raw)).validate(observed)
        need(observed['schema_version'] == REVIEW_VERSION and observed['open_gaps'] == []
             and observed['typed_semantic_graph_acyclic'] is True and observed['current_protected_proof_verified'] is True
             and observed['original_full_proof_status'] == 'REFUSED'
             and observed['owner_review_preconditions_resolved'] is True and observed['final_release_decision_required'] is True,
             'closed technical review observations or original refusal differ')
        selected = self.value['semantic_selection']
        need(selected is not None, 'production per-record semantic/proof/current-context dispositions remain unselected')
        anchor = selected['anchor']
        need(observed['protected_selector_binding'] == self.anchor.selector_binding
             and observed['semantic_policy_binding'] == anchor['policy_binding'] and observed['eligibility_binding'] == anchor['eligibility_binding']
             and observed['semantic_roots'] == selected['root_refs'] and observed['semantic_edges'] == selected['declared_edges'],
             'independently selected semantic/proof observations differ')
        requested = {(b['ref'], b['sha256']) for b in roots}
        members = {(b['ref'], b['sha256']) for b in observed['member_bindings']}
        need(len(members) == len(observed['member_bindings']) and members <= requested, 'duplicate or unselected release members')
        with self.boundary(semantics=False) as reader:
            proof = reader.verify(); semantic = self.verify_semantics(reader)
            policy = self.protected.parse(reader.read(selected['policy_file_id'], 'semantic-policy'))
            eligibility = self.protected.parse(reader.read(policy['eligibility_file_id'], 'history-proof'))
            node_versions = {n['file_id']: n['version_ref'] for n in policy['nodes']}
            route_map = {}
            for route in self.value['binding_routes']:
                closed(route, ('binding', 'file_id', 'kind')); b = route['binding']; closed(b, ('ref', 'sha256'))
                key = (b['ref'], b['sha256']); need(key not in route_map, 'duplicate typed member route'); route_map[key] = route
            headers = []
            for key in sorted(requested):
                need(key in route_map, 'release member lacks independently selected binding-kind route')
                route = route_map[key]; row = reader.files[route['file_id']]
                need((row['logical_path'], row['sha256']) == key and row['kind'] == route['kind'], 'release member proof/semantic route differs')
                reader.read(route['file_id'], route['kind'])
                if route['kind'] == 'governed-record':
                    need(route['file_id'] in node_versions, 'governed member has no actual typed semantic node')
                    version = node_versions[route['file_id']]; subject = eligibility['subjects'][version]
                    headers.append({'binding': {'ref': key[0], 'sha256': key[1]}, 'version_ref': version,
                                    'identity': subject['identity'], 'category': subject['category']})
            need(observed['semantic_member_headers'] == headers, 'semantic member headers were not derived from exact original policy/eligibility bytes')
            return {'protected_proof': proof, 'typed_semantic_graph': semantic, 'original_full_proof_status': 'REFUSED',
                    'historical_unavailable_count': 25, 'authority_effect': 'none', 'whole_release_qualified': False}
