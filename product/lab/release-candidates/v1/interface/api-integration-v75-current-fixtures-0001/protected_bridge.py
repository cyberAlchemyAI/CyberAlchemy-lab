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

# Held selected builtin primitives; no exception property/iterator/message dispatch.
_ERROR_STORE = BaseException.__dict__['__dict__'].__get__
_ERROR_STORE_SET = BaseException.__dict__['__dict__'].__set__
_ERROR_TB = BaseException.__dict__['__traceback__'].__get__
_ERROR_WITH_TB = BaseException.with_traceback
_ERROR_NAME = type.__dict__['__name__'].__get__
_ERROR_TYPE = type
_ERROR_ID = id
_ERROR_ITEMS = dict.items
_ERROR_MISSING = object()
_ERROR_FAMILIES = ('cleanup_errors','outer_cleanup_errors','initiating_cleanup_errors',
                   'independent_cleanup_errors','owned_construction_cleanup_errors')
_ERROR_LIMITS = (32, 8, 8, 64)  # rows, depth, entries/family, characters/label

def _error_field(data, name, default=None):
    # Keys themselves need not be safe objects: never hash or compare them.
    for key, value in _ERROR_ITEMS(data):
        if _ERROR_TYPE(key) is str and key == name:return value
    return default

def error_details(error):
    """Finite class/phase-only projection; raw primary/families stay held.

    Limits/reference/unclassified markers are explicit. Never present a bounded
    or unclassified projection as complete, nor relax the original32MiB cap.
    """
    data = _ERROR_STORE(error, BaseException)
    limits = {'rows':_ERROR_LIMITS[0],'depth':_ERROR_LIMITS[1],
              'family_entries':_ERROR_LIMITS[2],'label_characters':_ERROR_LIMITS[3]}
    reasons = {}; memo = {}; pending = []; rows = [0]
    def label(value, target, field):
        if _ERROR_TYPE(value) is not str:
            reasons['unclassified-label'] = True;return 'Unknown'
        if len(value)>limits['label_characters']:
            reasons['label-limit'] = True
            target[field+'_limit'] = {'original_characters':len(value),'limit':limits['label_characters']}
            return value[:limits['label_characters']]
        return value
    result = {};result['exception_class'] = label(_ERROR_NAME(_ERROR_TYPE(error),type),result,'exception_class')
    def family(values, depth):
        if _ERROR_TYPE(values) is not list and _ERROR_TYPE(values) is not tuple:
            reasons['unclassified-family'] = True
            return [{'exception_class':'UnclassifiedStructuredCause'}]
        number = _ERROR_ID(values)
        if number in memo:return [{'exception_class':'StructuredErrorReference','reference':memo[number]}]
        memo[number] = len(memo)+1; out = []
        for index,row in enumerate(values):
            reason = ('depth' if depth>limits['depth'] else
                      'rows' if rows[0]>=limits['rows'] else
                      'family_entries' if index>=limits['family_entries'] else None)
            if reason is not None:
                reasons[reason+'-limit'] = True
                out.append({'exception_class':'StructuredErrorLimit','limit':reason,
                            'omitted_direct_entries':len(values)-index,'untraversed_descendants':True})
                break
            if _ERROR_TYPE(row) is not dict:
                reasons['unclassified-row'] = True
                out.append({'exception_class':'UnclassifiedStructuredCause'});rows[0]+=1;continue
            number = _ERROR_ID(row)
            if number in memo:
                out.append({'exception_class':'StructuredErrorReference','reference':memo[number]});continue
            memo[number] = len(memo)+1;target={'node_reference':memo[number]};out.append(target)
            rows[0]+=1;pending.append((row,target,depth))
        return out
    for name in _ERROR_FAMILIES:
        values = _error_field(data,name,_ERROR_MISSING)
        if values is not _ERROR_MISSING:result[name] = family(values,1)
    unknown = _error_field(data,'_source8_unclassified_storage_keys',0)
    if _ERROR_TYPE(unknown) is not int or unknown<0:unknown = 0
    unknown += sum(1 for key,value in _ERROR_ITEMS(data) if _ERROR_TYPE(key) is not str)
    if unknown>0:
        reasons['unclassified-storage-key'] = True
        result['unclassified_storage_keys'] = min(unknown,10**12)
        if unknown>10**12:reasons['storage-count-limit'] = True
    while pending:
        row,target,depth = pending.pop()
        target['exception_class'] = label(_error_field(row,'exception_class',_error_field(row,'class','Unknown')),target,'exception_class')
        value = _error_field(row,'phase',_ERROR_MISSING)
        if value is not _ERROR_MISSING:target['phase'] = label(value,target,'phase')
        # Preserve the finite selected marker vocabulary across nested collectors.
        for name in ('reference','node_reference','omitted_direct_entries','unclassified_storage_keys'):
            value = _error_field(row,name,_ERROR_MISSING)
            if _ERROR_TYPE(value) is int and 0<=value<10**12:target[name] = value
        for name in ('untraversed_descendants',):
            value = _error_field(row,name,_ERROR_MISSING)
            if _ERROR_TYPE(value) is bool:target[name] = value
        value = _error_field(row,'limit',_ERROR_MISSING)
        if value is not _ERROR_MISSING:target['limit'] = label(value,target,'limit')
        prior = _error_field(row,'diagnostic_projection',_ERROR_MISSING)
        if _ERROR_TYPE(prior) is dict and _error_field(prior,'complete',True) is False:
            reasons['prior-incomplete-projection'] = True
            target['diagnostic_projection'] = {'complete':False,'prior_projection_limited_or_unclassified':True}
        if target['exception_class'] in ('StructuredErrorLimit','UnclassifiedStructuredCause'):
            reasons['prior-limit-or-unclassified-marker'] = True
        for name in _ERROR_FAMILIES:
            values = _error_field(row,name,_ERROR_MISSING)
            if values is not _ERROR_MISSING:target[name] = family(values,depth+1)
    result['diagnostic_projection'] = {'complete':not reasons,'limits':limits,
        'projected_rows':rows[0],'limitation_reasons':sorted(reasons)}
    return result

def _append_error(primary, late):
    data = _ERROR_STORE(primary,BaseException)
    # Updating the original dict can invoke a colliding custom key __eq__ even
    # through dict.__setitem__. Replace through the held BaseException storage
    # descriptor, using only exact str keys. Hold the original malformed dict so
    # its data remain available and no key destructor runs during retention.
    safe = {};unclassified = 0
    for key,value in _ERROR_ITEMS(data):
        if _ERROR_TYPE(key) is str:safe[key] = value
        else:unclassified += 1
    old = _error_field(safe,'outer_cleanup_errors',[])
    values = [*old] if (_ERROR_TYPE(old) is list or _ERROR_TYPE(old) is tuple) else [{'exception_class':'UnclassifiedStructuredCause'}]
    values.extend(late)
    safe['outer_cleanup_errors'] = values
    if unclassified:
        safe['_source8_held_unclassified_storage'] = data
        safe['_source8_unclassified_storage_keys'] = unclassified
    # Also retain unsupported old family values when all keys were safe: their
    # last reference must not be released while annotating the primary.
    safe['_source8_held_previous_storage'] = data
    _ERROR_STORE_SET(primary,safe)

def verify_control_links(links):
    """Check every selected relative parent/name/held-FD attachment before return."""
    for ancestor_parent,name,held,selected in links:
        attached=os.stat(name,dir_fd=ancestor_parent,follow_symlinks=False);opened=os.fstat(held)
        actual=lambda value:(value.st_dev,value.st_ino,value.st_uid,value.st_gid,value.st_mode)
        need(actual(attached)==actual(opened)==selected,'custody intermediate directory detached before return')

@contextmanager
def control_root(root):
    closed(root, ('id', 'path', 'device', 'inode', 'uid', 'mode'))
    path = Path(root['path']); need(path.is_absolute() and '..' not in path.parts and path.as_posix() == root['path'], 'canonical custody root required')
    need(root['uid'] == os.geteuid() and root['mode'] == 0o700, 'independently selected private control ownership required')
    fds = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
    primary = None; traceback = None; errors = []; close_owned = os.close
    error_fields = BaseException.__dict__['__dict__'].__get__
    traceback_of = BaseException.__dict__['__traceback__'].__get__
    def detail(error):
        return error_details(error)
    try:
        for part in path.parts[1:]: fds.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fds[-1]))
        value = os.fstat(fds[-1])
        need((value.st_dev, value.st_ino, value.st_uid, stat.S_IMODE(value.st_mode)) == (root['device'], root['inode'], root['uid'], root['mode']), 'custody root identity differs')
        yield fds[-1]
        for index, part in enumerate(path.parts[1:]):
            value = os.stat(part, dir_fd=fds[index], follow_symlinks=False); opened = os.fstat(fds[index+1])
            need((value.st_dev, value.st_ino, value.st_mode) == (opened.st_dev, opened.st_ino, opened.st_mode), 'custody ancestor detached')
    except BaseException as error:
        primary = error; traceback = traceback_of(error, BaseException)
    finally:
        while fds:
            fd = fds.pop()
            try: close_owned(fd)
            except BaseException as error: errors.append({'phase':'owned-control-root-close', **detail(error)})
    if primary is not None:
        if errors:
            _append_error(primary, errors)
        raise _ERROR_WITH_TB(primary, traceback)
    if errors:
        failure = ValueError('independent owned control root closes failed')
        error_fields(failure, BaseException)['cleanup_errors'] = errors
        raise failure

def control_bytes(root, locator, binding):
    closed(locator, ('root_id', 'path', 'size', 'device', 'inode', 'uid', 'mode')); closed(binding, ('ref', 'sha256'))
    relative = Path(locator['path'])
    need(locator['root_id'] == root['id'] and not relative.is_absolute() and relative.as_posix() == locator['path']
         and relative.parts and '..' not in relative.parts and locator['mode'] == 0o600 and locator['uid'] == os.geteuid()
         and type(locator['size']) is int and 0 <= locator['size'] <= 64*1024*1024, 'closed private custody locator required')
    primary = None; traceback = None; errors = []; value = None; close_owned = os.close
    error_fields = BaseException.__dict__['__dict__'].__get__
    traceback_of = BaseException.__dict__['__traceback__'].__get__
    def detail(error):
        return error_details(error)
    try:
        with control_root(root) as parent:
            fds = []; links = []
            try:
                current = parent
                for part in relative.parts[:-1]:
                    ancestor_parent = current
                    fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=ancestor_parent); fds.append(fd); current = fd
                    value = os.fstat(fd); need(value.st_uid == os.geteuid() and not stat.S_IMODE(value.st_mode) & 0o022, 'custody intermediate directory differs')
                    selected = (value.st_dev,value.st_ino,value.st_uid,value.st_gid,value.st_mode)
                    attached = os.stat(part,dir_fd=ancestor_parent,follow_symlinks=False)
                    need((attached.st_dev,attached.st_ino,attached.st_uid,attached.st_gid,attached.st_mode)==selected,'custody intermediate detached while opening')
                    links.append((ancestor_parent,part,fd,selected))
                fd = os.open(relative.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=current); fds.append(fd)
                before = os.fstat(fd)
                identity = lambda s: (s.st_dev, s.st_ino, s.st_uid, s.st_mode, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
                need(stat.S_ISREG(before.st_mode) and (before.st_dev, before.st_ino, before.st_uid, stat.S_IMODE(before.st_mode), before.st_size)
                     == (locator['device'], locator['inode'], locator['uid'], locator['mode'], locator['size']), 'custody control file identity differs')
                chunks = []; length = 0
                while True:
                    raw = os.read(fd, min(1024*1024,locator['size']-length+1))
                    if not raw: break
                    length += len(raw); need(length <= locator['size'], 'custody control grew');chunks.append(raw)
                raw = b''.join(chunks)
                need(identity(before) == identity(os.fstat(fd)) == identity(os.stat(relative.name, dir_fd=current, follow_symlinks=False))
                     and len(raw) == locator['size'] and hashlib.sha256(raw).hexdigest() == binding['sha256'], 'custody control bytes/attachment differ')
                verify_control_links(links)
                need(identity(before)==identity(os.fstat(fd))==identity(os.stat(relative.name,dir_fd=current,follow_symlinks=False)),
                     'custody leaf changed at final attachment boundary')
                value = raw
            except BaseException as error:
                primary = error; traceback = traceback_of(error, BaseException)
            finally:
                while fds:
                    fd = fds.pop()
                    try: close_owned(fd)
                    except BaseException as error: errors.append({'phase':'owned-control-file-or-intermediate-close', **detail(error)})
    except BaseException as error:
        if primary is None: primary = error; traceback = traceback_of(error, BaseException)
        else: errors.append({'phase':'independent-owned-control-root-exit', **detail(error)})
    if primary is not None:
        if errors:
            _append_error(primary, errors)
        raise _ERROR_WITH_TB(primary, traceback)
    if errors:
        failure = ValueError('independent owned control file closes failed')
        error_fields(failure, BaseException)['cleanup_errors'] = errors
        raise failure
    return value

class ProtectedHostBridge:
    def __init__(self, selection, protected_module, graph_module, module_bindings, repository, *, private_content_module):
        closed(selection, ('custody_anchor', 'control_roots', 'binding_routes', 'semantic_selection', 'readiness_version', 'observation_schema_binding', 'historical_original_proof', 'historical_content'))
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
        closed(selection['historical_content'], ('scope_binding', 'scope_file_id'))
        closed(selection['historical_content']['scope_binding'], ('ref', 'sha256'))
        need(type(selection['historical_content']['scope_file_id']) is str and selection['historical_content']['scope_file_id'],
             'one independently selected private content scope required')
        module_origin(private_content_module, module_bindings['private_content'], repository)
        self.content_module = private_content_module
        self.content_binding = dict(module_bindings['private_content'])
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
    def verified_boundary(self, *, semantics=True):
        """One lexical proof; host exit covers pre-yield failures as well."""
        primary = None; traceback = None; errors = []; resource = None; entered = False
        resource_exit = None; host_guard = self.builder.guard
        error_dict = BaseException.__dict__['__dict__'].__get__
        error_traceback = BaseException.__dict__['__traceback__'].__get__
        def detail(error):
            return error_details(error)
        try:
            host_guard()
            reader = self.open_reader()
            resource = reader.boundary(); resource_exit = type(resource).__exit__
            type(resource).__enter__(resource); entered = True
            content = self.verify_historical_content(reader)
            if semantics: self.verify_semantics(reader)
            yield reader, content
        except BaseException as error:
            primary = error; traceback = error_traceback(error, BaseException)
        finally:
            if entered:
                try:
                    # The genuine reader never suppresses; passing no primary
                    # prevents duplicate wrapping of the already retained body
                    # failure while still running its complete fresh exit.
                    result = resource_exit(resource, None, None, None)
                    need(not result, 'original reader boundary cannot suppress errors')
                except BaseException as error:
                    errors.append({'phase':'independent-original-reader-exit', **detail(error)})
            try: host_guard()
            except BaseException as error:
                errors.append({'phase':'independent-current-host-exit', **detail(error)})
        if primary is not None:
            if errors:
                _append_error(primary, errors)
            raise _ERROR_WITH_TB(primary, traceback)
        if errors:
            failure = ValueError('independent selected host boundary exits failed')
            error_dict(failure, BaseException)['cleanup_errors'] = errors
            raise failure

    @contextmanager
    def boundary(self, *, semantics=True):
        with self.verified_boundary(semantics=semantics) as (reader, content):
            yield reader

    def verify_historical_content(self, reader):
        module_origin(self.content_module, self.content_binding, self.root)
        selected = self.value['historical_content']
        closed(selected, ('scope_binding', 'scope_file_id'))
        binding = selected['scope_binding']; closed(binding, ('ref', 'sha256'))
        row = reader.files[selected['scope_file_id']]
        need(row['logical_path'] == binding['ref'] and row['sha256'] == binding['sha256']
             and row['kind'] == 'history-proof', 'exact independent typed private scope route differs')
        raw = reader.read(selected['scope_file_id'], 'history-proof')
        need(hashlib.sha256(raw).hexdigest() == binding['sha256'], 'selected private scope bytes differ')
        port = self.content_module.PrivateHistoricalContent(raw, binding, reader, self.protected, self.graph, self.root)
        need(port.value['scope_file_id'] == selected['scope_file_id']
             and port.value['semantic_selection'] == self.value['semantic_selection'],
             'private content scope and independently selected host semantic policy differ')
        result = port.verify_content()
        module_origin(self.content_module, self.content_binding, self.root)
        return result

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
        with self.verified_boundary(semantics=False) as (reader, content):
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
            return {'protected_proof': proof, 'typed_semantic_graph': semantic, 'historical_content': content, 'original_full_proof_status': 'REFUSED',
                    'historical_unavailable_count': 25, 'authority_effect': 'none', 'whole_release_qualified': False}
