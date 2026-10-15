"""Explicit original lifecycle adoption of selected native generation commits.

Only a trusted bootstrap supplies executable and permission capabilities.
Original event/translation algorithms are inherited at their original origins.
No close path deletes a store, pending intent, generation, or foreign residue.
"""
import base64
import copy
from dataclasses import asdict
import inspect
import json
import os
from pathlib import Path
import stat
import sys
import time
import uuid
from .private_io import canonical, directory, read, require, sha, sync, write

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
VERSION = 'lab-selected-native-lifecycle-store/v1-candidate'

def binding(value):
    require(type(value) is dict and set(value) == {'path', 'sha256'}, 'closed original code binding required')
    path = Path(value['path'])
    require(not path.is_absolute() and '..' not in path.parts and path.as_posix() == value['path'], 'true selected code origin required')
    require(sha(read(ROOT/path)) == value['sha256'], 'selected original code changed')
    return ROOT/path

def module_origin(module, selected):
    path = binding(selected)
    require(sys.modules.get(module.__name__) is module and Path(module.__file__) == path, 'actual selected module origin differs')

def capability_origin(value, selected):
    require(type(selected) is dict and set(selected) == {'code_binding', 'class_name'}, 'closed bootstrap capability selection required')
    path = binding(selected['code_binding'])
    cls = type(value)
    require(cls.__name__ == selected['class_name'] and Path(inspect.getsourcefile(cls)) == path,
            'bootstrap capability class/origin differs')

def rich_metadata_after_append(translator, semantic, governance, witness, base_specs):
    """Derive delayed original map_node metadata before any native effect."""
    require(type(witness) is dict and type(base_specs) is dict, 'exact original append metadata required')
    result = copy.deepcopy(base_specs)
    if 'source_view' not in witness and 'rich_record' not in witness:
        return result
    require('source_view' in witness and 'rich_record' in witness
            and len(semantic) == len(governance) == 1, 'exact original node mapping witness required')
    spec = translator.node_spec(witness['source_view'])
    event = semantic[0]
    require(spec['node_id'] not in base_specs
            and event['subject_identity']['subject_id'] == spec['node_id']
            and event['subject_identity']['subject_kind'] == 'node', 'original node metadata/semantic subject differs')
    reference = {'semantic_event_id':event['event_id'],'semantic_event_digest':event['event_digest'],
                 'semantic_cursor':event['semantic_cursor']}
    record = translator.rich_record(spec,reference,[governance[0]['event_id']])
    require(record == witness['rich_record'], 'original rich record differs from exact sealed request')
    state,_ = translator.translate_node(record,spec)
    require(state == event['complete_resulting_semantic_state'], 'rich metadata differs from original native state')
    result[spec['node_id']] = copy.deepcopy(spec)
    return result

class StoreFactory:
    """Private bootstrap capability; a public call cannot supply this factory."""
    def __init__(self, original, generation, executor, boundary, selection):
        fields = {'schema_version','authority_effect','original_store_binding','generation_module_binding',
                  'executor_class_binding','boundary_class_binding','owned_parent','owned_parent_identity','retention_policy'}
        require(type(selection) is dict and set(selection) == fields and selection['schema_version'] == VERSION
                and selection['authority_effect'] == 'none' and selection['retention_policy'] == 'preserve-all-until-explicit-disposition',
                'closed explicit private native store selection required')
        self.selection = copy.deepcopy(selection)
        self._seal = canonical(selection)
        self.original = original
        self.generation = generation
        self.executor = executor
        self.boundary = boundary
        self.guard()

    def guard(self):
        require(canonical(self.selection) == self._seal, 'private native store selection mutated')
        module_origin(self.original, self.selection['original_store_binding'])
        module_origin(self.generation, self.selection['generation_module_binding'])
        capability_origin(self.executor, self.selection['executor_class_binding'])
        capability_origin(self.boundary, self.selection['boundary_class_binding'])
        self.boundary.guard()
        self.executor.guard()
        parent = Path(self.selection['owned_parent'])
        require(parent.is_absolute() and '..' not in parent.parts and not parent.is_relative_to(ROOT), 'selected durable owned native parent outside repository required')
        selected = self.selection['owned_parent_identity']
        with directory(parent) as fd:
            info = os.fstat(fd)
            require([info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode)] == selected
                    and info.st_uid == os.getuid() and stat.S_IMODE(info.st_mode) == 0o700,
                    'independent owned native parent identity differs')

    def create(self, translator, executable, executable_sha256):
        self.guard()
        require(Path(executable) == Path(self.executor.executable_path)
                and executable_sha256 == self.executor.executable_sha256, 'selected original ontology executable differs')
        parent = Path(self.selection['owned_parent'])
        name = 'native-lifecycle-'+uuid.uuid4().hex
        with directory(parent) as fd:
            os.mkdir(name,0o700,dir_fd=fd)
            os.fsync(fd)
        factory = self
        original = self.original
        generation = self.generation

        class SelectedCandidateStore(original.NativeCandidateStore):
            def __init__(self):
                self.translator = translator
                self.executable = Path(executable)
                self.executable_sha256 = executable_sha256
                self.root = parent/name
                info = self.root.lstat()
                self.root_identity = [info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode)]
                self.closed = False
                self.expires = time.monotonic()+900
                self.semantic_events = []
                self.governance_events = []
                self.expected_files = {}
                self.specs = {}
                self.witnesses = []
                self.sources = {}
                self.pending_operation = None
                self.commit_receipts = []
                self.store_root = self.root/'native'
                self.store_root.mkdir(mode=0o700)
                selected = self.store_root.stat()
                self.committed = generation.GenerationStore(self.store_root,(selected.st_dev,selected.st_ino),
                    self.executable,self.executable_sha256,executor=factory.executor,boundary=factory.boundary)
                self.committed.bootstrap()
                sync(self.root)
                self.guard()

            def guard(self, *, pending_ok=False):
                factory.guard()
                require(self.pending_operation is None or pending_ok is True, 'native attempt is pending; inspect/reconcile before another write')
                info = self.root.lstat()
                require([info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode)] == self.root_identity,
                        'owned lifecycle root changed')
                original.NativeCandidateStore.guard(self)
                self.committed.guard()

            @property
            def semantic(self):
                return self.committed.head()[2]/'semantic'

            @property
            def governance(self):
                return self.committed.head()[2]/'governance'

            def files(self):
                return copy.deepcopy(self.committed.head()[0]['files'])

            def call(self, mode, args, value=None):
                self.guard()
                require(mode == 'seal' and args == [] and value is not None, 'direct native writes/reads cannot bypass the selected generation boundary')
                request = self.root/('seal-'+uuid.uuid4().hex+'.json')
                raw = original.canonical(value)
                write(request,raw)
                child = factory.executor.run_native('seal',[str(request)])
                require(child.returncode == 0, 'selected original native sealing refused')
                factory.guard()
                require(read(request) == raw, 'selected sealing request changed')
                return original.parse(child.stdout)

            def append(self, semantic, governance, witness):
                self.guard()
                request = {'semantic':copy.deepcopy(semantic),'governance':copy.deepcopy(governance)}
                rich_state = {'base_specs':copy.deepcopy(self.specs),
                    'next_specs':rich_metadata_after_append(self.translator,semantic,governance,witness,self.specs)}
                token = uuid.uuid4().hex
                request_path = self.root/('append-'+token+'.json')
                raw = original.canonical(request)
                write(request_path,raw)
                pending_path,pins = self.committed.prepare(request_path,sha(raw))
                intent = {'schema_version':'lab-native-lifecycle-recovery-control/v2-candidate','authority_effect':'none',
                    'pending_path':str(pending_path),'pending_pins':asdict(pins),'request_binding':{'path':str(request_path),'sha256':sha(raw)},
                    'witness':copy.deepcopy(witness),'base_semantic_events':copy.deepcopy(self.semantic_events),
                    'base_governance_events':copy.deepcopy(self.governance_events),'source_bindings':copy.deepcopy(self.sources),
                    'rich_state':copy.deepcopy(rich_state),
                    'automatic_retry':False,'retention_policy':'preserve-all-until-explicit-disposition'}
                intent_path = self.root/('recovery-control-'+token+'.json')
                intent_raw = canonical(intent)
                write(intent_path,intent_raw)
                self.pending_operation = {'control_path':str(intent_path),'control_sha256':sha(intent_raw),
                    'pending_path':pending_path,'pins':pins,'request':request,'witness':copy.deepcopy(witness),
                    'rich_state':copy.deepcopy(rich_state)}
                # Any exception keeps this exact capsule and every staged byte.
                result = self.committed.run(pending_path,pins)
                return self._adopt(result)

            def _adopt(self, result):
                pending = self.pending_operation
                require(pending is not None and result['committed'] is True, 'actual original native commit evidence required')
                control_raw = read(pending['control_path'])
                require(sha(control_raw) == pending['control_sha256'], 'durable rich recovery capsule changed')
                control = json.loads(control_raw)
                require(type(control) is dict and set(control) == {'schema_version','authority_effect','pending_path','pending_pins',
                    'request_binding','witness','base_semantic_events','base_governance_events','source_bindings','rich_state',
                    'automatic_retry','retention_policy'}
                    and control['schema_version'] == 'lab-native-lifecycle-recovery-control/v2-candidate'
                    and control['authority_effect'] == 'none' and control['automatic_retry'] is False
                    and control['retention_policy'] == 'preserve-all-until-explicit-disposition'
                    and control['pending_path'] == str(pending['pending_path'])
                    and control['pending_pins'] == asdict(pending['pins'])
                    and control['witness'] == pending['witness'] and control['source_bindings'] == self.sources
                    and control['base_semantic_events'] == self.semantic_events
                    and control['base_governance_events'] == self.governance_events,
                    'exact closed original adoption capsule differs')
                request_binding = control['request_binding']
                require(type(request_binding) is dict and set(request_binding) == {'path','sha256'}, 'closed recovery request binding required')
                request_raw = read(request_binding['path'])
                require(request_binding['sha256'] == pending['pins'].request_sha256
                    and sha(request_raw) == request_binding['sha256']
                    and original.parse(request_raw) == pending['request'], 'exact original recovery request differs')
                rich_state = control['rich_state']
                require(type(rich_state) is dict and set(rich_state) == {'base_specs','next_specs'}
                    and rich_state == pending['rich_state'] and rich_state['base_specs'] == self.specs,
                    'original rich metadata base changed before adoption')
                require(rich_metadata_after_append(self.translator,pending['request']['semantic'],pending['request']['governance'],
                    pending['witness'],self.specs) == rich_state['next_specs'], 'original rich metadata derivation changed')
                observed = self.committed.read_committed()
                native = observed['native_cut']
                semantic = self.semantic_events+pending['request']['semantic']
                governance = self.governance_events+pending['request']['governance']
                require(observed['result'] == 'PASS' and native['semantic_events'] == semantic and native['governance_events'] == governance,
                        'cold replay differs from exact original selected events')
                receipt = {'result':'PASS','commit_point':'fsynced-HEAD-replacement',
                    'recovery_control_binding':{'path':pending['control_path'],'sha256':pending['control_sha256']},
                    'native_request_sha256':pending['pins'].request_sha256,'original_event_files':copy.deepcopy(observed['files']),
                    'authority_effect':'none','source_admission_applied':False}
                prior = (self.semantic_events,self.governance_events,self.expected_files,self.specs)
                self.semantic_events = copy.deepcopy(semantic)
                self.governance_events = copy.deepcopy(governance)
                self.expected_files = copy.deepcopy(observed['files'])
                self.specs = copy.deepcopy(rich_state['next_specs'])
                try:
                    self.guard(pending_ok=True)
                except BaseException:
                    # Restore only the unaccepted in-memory view. The native
                    # commit and durable recovery capsule remain untouched.
                    self.semantic_events,self.governance_events,self.expected_files,self.specs = prior
                    raise
                self.witnesses.append(copy.deepcopy(pending['witness']))
                self.commit_receipts.append(receipt)
                self.pending_operation = None
                return copy.deepcopy(native)

            def reconcile_pending(self, independent_control):
                factory.guard()
                pending = self.pending_operation
                require(not self.closed and time.monotonic() < self.expires and pending is not None,
                        'live original store and exact pending control required; no lease transfer')
                require(independent_control == {'path':pending['control_path'],'sha256':pending['control_sha256']}
                        and sha(read(independent_control['path'])) == independent_control['sha256'],
                        'independent selected recovery control differs')
                for selected in self.sources.values():
                    original.original(selected)
                result = self.committed.run(pending['pending_path'],pending['pins'],recover=True)
                return self._adopt(result)

            def read(self):
                self.guard()
                require(self.semantic_events, 'empty ontology has no cut')
                result = self.committed.read_committed()
                require(result['result'] == 'PASS', 'selected original cold native replay required')
                require(result['native_cut']['semantic_events'] == self.semantic_events
                        and result['native_cut']['governance_events'] == self.governance_events,
                        'original native cursor/event selection differs')
                self.guard()
                return copy.deepcopy(result['native_cut'])

            def export(self):
                self.guard()
                head,head_raw,current = self.committed.head()
                files = {}
                for relative,pin in sorted(head['files'].items()):
                    raw = read(current/relative)
                    require(sha(raw) == pin, 'original committed export bytes differ')
                    files[relative] = {'sha256':pin,'base64_original_bytes':base64.b64encode(raw).decode()}
                require(read(self.store_root/'HEAD.json') == head_raw, 'native export head changed')
                self.guard()
                return {'schema_version':'lab-O02-public-native-archive/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
                    'files':files,'native_executable_sha256':self.executable_sha256,'semantic_cursor':len(self.semantic_events),
                    'governance_cursor':len(self.governance_events),'private_key_included':False,'Session_memory_included':False,
                    'ontology_admission':False,'source_effects_applied':0}

            def snapshot_original_outcome(self):
                """Private exact native bytes for the selected outer publisher.

                Typed Artifact construction and Project/Core/State/history
                commit are the outer publisher's separate responsibilities.
                """
                self.guard()
                head,head_raw,current = self.committed.head()
                cold = self.committed.read_committed()
                require(cold['result'] == 'PASS' and cold['files'] == head['files'], 'complete original native replay required')
                members = {}
                for relative,pin in sorted(head['files'].items()):
                    raw = read(current/relative)
                    require(sha(raw) == pin, 'original native member changed')
                    members[relative] = {'raw':raw,'sha256':pin}
                require(read(self.store_root/'HEAD.json') == head_raw, 'native outcome head changed')
                self.guard()
                return {'schema_version':'lab-selected-native-original-outcome/v1-candidate',
                    'head_binding':{'path':str(self.store_root/'HEAD.json'),'sha256':sha(head_raw)},
                    'head_raw':head_raw,'generation':head['generation'],'event_files':members,
                    'projection_raw':cold['native_stdout_bytes'],'projection_sha256':cold['native_stdout_sha256'],
                    'semantic_events':copy.deepcopy(self.semantic_events),'governance_events':copy.deepcopy(self.governance_events),
                    'causal_witnesses':copy.deepcopy(self.witnesses),'commit_receipts':copy.deepcopy(self.commit_receipts),
                    'typed_Artifacts_constructed':False,'Project_history_committed':False,'authority_effect':'none'}

            def close(self):
                self.closed = True
                # No stale-lock guess, temporary cleanup, unlink or rmtree.
                # Independent cold inspection/recovery uses a new bootstrap.

        return SelectedCandidateStore()

    def recover_detached(self, *, store_root, store_identity, control_binding):
        """Fresh authorization inspects/recovers exact known native bytes only.

        This does not revive an expired Session or infer rich lifecycle state.
        Metadata/source adoption is a separate publisher reconciliation step.
        """
        self.guard()
        store_root = Path(store_root)
        require(store_root.is_absolute() and '..' not in store_root.parts and store_root.name == 'native'
                and store_root.parent.parent == Path(self.selection['owned_parent'])
                and store_root.parent.name.startswith('native-lifecycle-'), 'detached native root outside selected custody')
        require(type(control_binding) is dict and set(control_binding) == {'path','sha256'}
                and Path(control_binding['path']).parent == store_root.parent,
                'independent selected private recovery origin required')
        control_raw = read(control_binding['path'])
        control = json.loads(control_raw)
        require(sha(control_raw) == control_binding['sha256'], 'independent cold recovery bytes changed')
        require(type(control) is dict and set(control) == {'schema_version','authority_effect','pending_path','pending_pins',
                    'request_binding','witness','base_semantic_events','base_governance_events','source_bindings','rich_state',
                    'automatic_retry','retention_policy'}
                and control['schema_version'] == 'lab-native-lifecycle-recovery-control/v2-candidate'
                and control['authority_effect'] == 'none' and control['automatic_retry'] is False
                and control['retention_policy'] == 'preserve-all-until-explicit-disposition'
                and Path(control['pending_path']).parent == store_root,
                'closed original recovery protocol required')
        request = control['request_binding']
        require(type(request) is dict and set(request) == {'path','sha256'}
                and Path(request['path']).parent == store_root.parent
                and sha(read(request['path'])) == request['sha256'], 'original cold recovery request changed')
        for selected in control['source_bindings'].values():
            self.original.original(selected)
        store = self.generation.GenerationStore(store_root,store_identity,self.executor.executable_path,
            self.executor.executable_sha256,executor=self.executor,boundary=self.boundary)
        pins = self.generation.PendingPins(**control['pending_pins'])
        result = store.run(control['pending_path'],pins,recover=True)
        cold = store.read_committed()
        self.guard()
        return {'native_commit':result,'cold_native':cold,'recovery_control_binding':copy.deepcopy(control_binding),
            'lifecycle_metadata_adopted':False,'old_Session_revived':False,'automatic_retry':False,'authority_effect':'none'}

    def cold_snapshot_original_outcome(self, *, store_root, store_identity, expected_head_binding,
            expected_generation, expected_event_files, expected_projection_sha256):
        """Replay the independently selected immutable generation, never HEAD.

        expected_head_binding selects the outer publisher's retained exact head
        bytes. The current mutable inner HEAD is deliberately not consulted.
        """
        self.guard()
        store_root = Path(store_root)
        require(store_root.is_absolute() and '..' not in store_root.parts and store_root.name == 'native'
                and store_root.parent.parent == Path(self.selection['owned_parent']),
                'immutable native generation outside selected custody')
        require(type(expected_head_binding) is dict and set(expected_head_binding) == {'path','sha256'},
                'independent retained original head binding required')
        head_raw = read(expected_head_binding['path'])
        require(sha(head_raw) == expected_head_binding['sha256'], 'retained original head bytes differ')
        head = json.loads(head_raw)
        require(type(head) is dict and set(head) == {'generation','files','request_sha256','authority_effect'}
                and head['authority_effect'] == 'none' and head['generation'] == expected_generation
                and head['files'] == expected_event_files, 'independent immutable native head selection differs')
        require(type(expected_generation) is str and expected_generation.startswith('operation-')
                and len(expected_generation) == 42 and all(c in '0123456789abcdef' for c in expected_generation[10:]),
                'closed immutable native operation generation required')
        require(type(expected_event_files) is dict and expected_event_files, 'complete immutable event closure required')
        store = self.generation.GenerationStore(store_root,store_identity,self.executor.executable_path,
            self.executor.executable_sha256,executor=self.executor,boundary=self.boundary)
        generation_path = store_root/'generations'/expected_generation
        require(store.tree(generation_path,expected=expected_event_files) == expected_event_files, 'selected immutable native event files differ')
        members = {}
        for relative,pin in sorted(expected_event_files.items()):
            raw = read(generation_path/relative)
            require(sha(raw) == pin, 'selected immutable original event bytes differ')
            members[relative] = {'raw':raw,'sha256':pin}
        cursor = sum(name.startswith('semantic/') for name in expected_event_files)
        child = self.executor.run_native('read',[str(generation_path/'semantic'),str(generation_path/'governance'),str(cursor)])
        require(child.returncode == 0 and sha(child.stdout) == expected_projection_sha256,
                'actual immutable cold native replay differs')
        projection = json.loads(child.stdout)
        require(store.tree(generation_path,expected=expected_event_files) == expected_event_files
                and read(expected_head_binding['path']) == head_raw, 'immutable native snapshot changed during replay')
        self.guard()
        return {'schema_version':'lab-selected-native-immutable-snapshot/v1-candidate',
            'head_binding':copy.deepcopy(expected_head_binding),'head_raw':head_raw,'generation':expected_generation,
            'event_files':members,'projection_raw':child.stdout,'projection_sha256':sha(child.stdout),
            'semantic_events':projection['semantic_events'],'governance_events':projection['governance_events'],
            'mutable_inner_HEAD_followed':False,'write_or_retry_performed':False,'authority_effect':'none'}
