"""Ephemeral context consumer; every governed claim resolves to a pinned revision."""
from __future__ import annotations
import copy
from datetime import datetime,timezone
import importlib
import sys
import time
import uuid
from .common import RuntimeFault,byte_digest,digest,load,require,under
from .replay import legacy_runtime
from .sources import freshness,verify_snapshot
from .store import VerifiedLegacyReadStore


def reference(subjects, ref, expected_kind=None):
    """Stable identity may resolve only one effective revision; no label aliases."""
    require(isinstance(ref,str) and ref,'context reference must be a nonempty string')
    exact=subjects.get(ref)
    matches=[exact] if exact else [e for e in subjects.values() if e['identity']==ref and e['effective_state'] in ['admitted-current','local-admitted-current']]
    if len(matches)!=1:
        return {'reference':ref,'reference_class':'unresolved','reason':'Unknown or ambiguous exact subject revision','governed_claim':False}
    entry=matches[0]
    if expected_kind is not None and entry['kind']!=expected_kind:
        return {'reference':ref,'reference_class':'unresolved','reason':'Resolved kind does not meet requested role: '+expected_kind,'governed_claim':False}
    return {'reference':ref,'reference_class':'governed-subject','identity_ref':entry['identity'],'version_ref':entry['version_ref'],'kind':entry['kind'],'effective_state':entry['effective_state'],'source_binding':copy.deepcopy(entry['source']),'governed_claim':True,'authority_effect':'none'}


class Session:
    def __init__(self, store, source_snapshot, *, expected_profile_sha256,
                 expected_snapshot_digest, subject_ref, references=None,
                 ttl=900, clock=time.monotonic, wall_clock=time.time,
                 depth=2, max_nodes=60, max_edges=100):
        require(isinstance(store,VerifiedLegacyReadStore),'trusted read-only verified store adapter required')
        require(type(ttl) is int and 1<=ttl<=86400,'session TTL must be 1..86400 seconds')
        require(type(depth) is int and 0<=depth<=4 and type(max_nodes) is int and 1<=max_nodes<=100 and type(max_edges) is int and 1<=max_edges<=200,'context graph limits exceeded')
        verify_snapshot(source_snapshot,expected_profile_sha256=expected_profile_sha256)
        require(source_snapshot['snapshot_digest']==expected_snapshot_digest,'independent context source snapshot pin mismatch')
        self.store=store;self.snapshot=copy.deepcopy(source_snapshot);self.clock=clock
        self.started=clock();self.deadline=self.started+ttl;self.closed=False;self._memory=[];self._pack=None
        self.session_id='protocol:ephemeral-agent-session:'+str(uuid.uuid4())
        self.instance_id='protocol:ephemeral-agent-instance:'+str(uuid.uuid4())
        try:
            self._check_executable()
            require(freshness(store.repository,self.snapshot)['status']=='current','source snapshot stale before session preparation')
            data=store.replay(require_current=True)
            require(data['baseline']['materials']==self.snapshot['materials'],'context source selection differs from store baseline')
            self.head=data['head']['transaction_digest'];self.config_digest=digest(data['config']);self.state_digest=digest(data['projection']['state'])
            subjects=data['projection']['subjects']
            root=reference(subjects,subject_ref)
            require(root['governed_claim'],'selected context root unresolved: '+subject_ref)
            diagnostics=[];resolved=[root]
            expected_roles={'assignment_ref':'agent-assignment','principal_ref':'principal','profile_ref':'agent-profile','implementation_ref':'implementation','delegation_ref':'delegation'}
            for role,ref in (references or {}).items():
                require(role in expected_roles,'unknown context reference role')
                item=reference(subjects,ref,expected_roles[role]);item['role']=role
                (resolved if item['governed_claim'] else diagnostics).append(item)
            name,adapter,stage=legacy_runtime(store.executable_repo,store.pins)
            try:
                graph=importlib.import_module(name+'.graph').query(data,root['version_ref'],depth=depth,max_nodes=max_nodes,max_edges=max_edges)
            finally:
                stage.cleanup()
                for key in list(sys.modules):
                    if key==name or key.startswith(name+'.'):sys.modules.pop(key,None)
            # Existing source-backed graph is a disposable repository representation.
            # Project history cursors do not become ontology-native event cursors.
            generated=datetime.fromtimestamp(wall_clock(),timezone.utc).isoformat()
            schema_state=reference(subjects,data['projection']['state']['node_id'],'project-state')
            if schema_state['governed_claim']:resolved.append(schema_state)
            else:diagnostics.append(schema_state)
            histories={kind:{'identity_ref':record['node_id'],'cursor':len(record['payload']['events']),'record_digest':digest(record)} for kind,record in data['projection']['histories'].items()}
            for history in histories.values():
                item=reference(subjects,history['identity_ref'])
                (resolved if item['governed_claim'] else diagnostics).append(item)
            protocol_refs=[{'reference':self.session_id,'reference_class':'protocol-session-handle','governed_claim':False},{'reference':self.instance_id,'reference_class':'protocol-ephemeral-instance-handle','governed_claim':False}]
            if not any(r.get('role')=='assignment_ref' for r in resolved):diagnostics.append({'reference':'assignment_ref','reference_class':'unresolved','reason':'No exact governed assignment supplied; this read consumer grants no action permission.','governed_claim':False})
            diagnostics.append({'reference':'ontology-native-cut','reference_class':'unresolved','reason':'No verified ontology semantic/governance event cut supplied. Repository graph is a protocol projection; Project histories are not substituted.','governed_claim':False})
            diagnostics.append({'reference':'generator-implementation-realization','reference_class':'unresolved','reason':'Candidate package provenance is exact; no admitted Implementation revision is claimed to realize this new package.','governed_claim':False})
            material_closure={r['source_binding']['path']:self.snapshot['materials'].get(r['source_binding']['path']) for r in resolved if r['source_binding'].get('path') in self.snapshot['materials']}
            control=self.snapshot['controls']['executable_manifest'] if 'executable_manifest' in self.snapshot['controls'] else None
            generator={'reference_class':'protocol-generator-package','package_profile_sha256':expected_profile_sha256,'source_snapshot_digest':expected_snapshot_digest,'executable_manifest_binding':copy.deepcopy(control),'governed_implementation_revision':None,'implementation_realization':'unresolved','legacy_helper_executable_binding':{'path':store.pins.manifest_path,'sha256':store.pins.manifest_sha256,'selected_runtime':store.pins.runtime_version},'authority_effect':'none'}
            self._pack={'schema_version':'lab-session-context-read-model/v1-candidate','session_id':self.session_id,'instance_id':self.instance_id,'generated_at':generated,'ttl_seconds':ttl,'head':self.head,'source_profile_sha256':expected_profile_sha256,'source_snapshot_digest':expected_snapshot_digest,'selected_source_cut':self.snapshot['expected_cut'],'project_state':copy.deepcopy(data['projection']['state']),'project_history_bindings':histories,'context_view':{'reference_class':'protocol-context-selection','governed_carrier_ref':None,'selected_governed_references':resolved,'material_closure':material_closure,'source_digest':digest(material_closure),'authority_effect':'none','replay_source':False},'ontology_view':{'reference_class':'protocol-repository-graph-view','governed_carrier_ref':None,'canonical_ontology_cut_ref':None,'ontology_semantic_cursor':None,'ontology_governance_cursor':None,'projection_digest':digest(graph),'graph':graph,'authority_effect':'none','replay_source':False},'generator_provenance':generator,'reference_diagnostics':diagnostics,'protocol_references':protocol_refs,'session_memory_owner':self.session_id,'durable_memory_owner':'Exact Project State and source-backed Context/Ontology Views','short_memory_persisted':False,'action_permission':'none','authority_effect':'none','claim_ceiling':'Bounded derived read context only; no domain artifact admission, genuine ontology-native cut, generator realization, actor permission or persistence from this session.'}
            self._pack['pack_digest']=digest(self._pack)
        except BaseException:
            self.close();raise

    def _check_executable(self):
        for ref in self.snapshot['executable_materials']:
            file=under(self.store.executable_repo,ref['path'])
            require(not file.is_symlink() and byte_digest(file.read_bytes())==ref['sha256'],'session executable bytes changed')

    def context(self):
        require(not self.closed,'session is closed')
        try:
            self._check_executable()
            require(self.clock()<self.deadline,'session context expired')
            require(freshness(self.store.repository,self.snapshot)['status']=='current','session source changed; prepare a new context')
            data=self.store.replay(require_current=True)
            require(data['head']['transaction_digest']==self.head and digest(data['config'])==self.config_digest and digest(data['projection']['state'])==self.state_digest,'session head/configuration/state changed')
            return copy.deepcopy(self._pack)
        except BaseException:
            self.close();raise

    def note(self,text):
        self.context()
        require(isinstance(text,str) and 0<len(text.encode())<=10000,'session note must fit 10000 UTF-8 bytes')
        require(len(self._memory)<100 and sum(len(s.encode()) for s in self._memory)+len(text.encode())<=1048576,'short memory budget exceeded')
        self._memory.append(text)
        return {'session_id':self.session_id,'memory_entries':len(self._memory),'persisted':False}

    def close(self):
        self._memory.clear();self._pack=None;self.snapshot=None;self.closed=True
        return {'session_id':self.session_id,'instance_id':self.instance_id,'termination_state':'closed','short_memory_erased':True,'durable_effect':'none'}
