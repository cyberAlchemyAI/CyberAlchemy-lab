"""Owned development read consumers: RAM context, bounded durable metadata only.

This is a custody kernel, not an AgentAssignment authority resolver or API grant.
Cold metadata never recreates a consumer. The live process holds an exclusive
custody lock; failure to observe disposal is reported as indeterminate.
"""
from __future__ import annotations
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import threading
import uuid
from datetime import datetime, timezone
from local_context import ContextSession, regular
from lab_runtime.common import encoded, loads, require


def sha(raw): return hashlib.sha256(raw).hexdigest()
def stamp(): return datetime.now(timezone.utc).isoformat()
def binding(path): return {'ref': Path(path).name, 'sha256': sha(regular(path))}


def private_root(path):
    path = Path(path)
    require(path.is_absolute() and '..' not in path.parts and path == path.resolve(), 'canonical custody path required')
    require(path.is_dir() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents), 'regular custody root required')
    require(path.is_relative_to(Path('/tmp')) and path.stat().st_uid == os.getuid() and path.stat().st_mode & 0o777 == 0o700, 'owned private development custody root required')
    return path


def put(path, value):
    """Publish an immutable metadata revision without replacing another file."""
    raw = encoded(value)
    require(len(raw) <= 65536, 'custody metadata byte budget exceeded')
    tmp = path.parent / ('.pending-' + uuid.uuid4().hex)
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.link(tmp, path)
        directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        tmp.unlink(missing_ok=True)
    return binding(path)


class ReadCustodian:
    """Trusted local construction only; no public actor message supplies a grant."""
    def __init__(self, root, *, principal_ref, scope_ref, source_cut_binding, consumer_control_binding, source_guard, factory):
        self.root = private_root(root)
        require(re.fullmatch(r'principal:[A-Za-z0-9:._/-]{1,200}', principal_ref) is not None, 'exact development principal required')
        require(re.fullmatch(r'project:[A-Za-z0-9:._/@-]{1,200}', scope_ref) is not None, 'exact development scope required')
        require(set(source_cut_binding) == {'ref','sha256'} and re.fullmatch('[0-9a-f]{64}',source_cut_binding['sha256']), 'exact source cut binding required')
        require(set(consumer_control_binding) == {'ref','sha256'} and re.fullmatch('[0-9a-f]{64}',consumer_control_binding['sha256']), 'exact consumer control binding required')
        self.control = copy.deepcopy(consumer_control_binding); self.factory = factory
        self.principal = principal_ref; self.scope = scope_ref; self.cut = copy.deepcopy(source_cut_binding)
        self.guard = source_guard; self.live = {}; self.mutex = threading.RLock(); self.closed = False
        fd = os.open(self.root/'.custody-lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, 'r+b')
        try: fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BaseException: self.lock.close(); raise
        control = {'schema_version':'lab-read-custody-scope/v1-candidate','principal_ref':self.principal,
            'scope_ref':self.scope,'source_cut_binding':self.cut,'consumer_control_binding':self.control,'action_permission':'none',
            'assignment_authority':'unresolved','authority_effect':'none','actual_owner_outcome':None}
        try:
            if (self.root/'scope.json').exists():
                require(loads(regular(self.root/'scope.json')) == control, 'custody scope differs')
            else:
                require(set(p.name for p in self.root.iterdir()) == {'.custody-lock'}, 'new custody scope must be empty')
                put(self.root/'scope.json',control)
            self.scope_bytes = regular(self.root/'scope.json')
            self.history()
        except BaseException:
            self.lock.close(); raise

    def history(self):
        private_root(self.root)
        require(regular(self.root/'scope.json') == self.scope_bytes, 'custody scope changed')
        result = {}; allocations = {}; objects = {}
        for path in sorted(self.root.iterdir()):
            require(not path.is_symlink() and path.is_file() and path.stat().st_mode & 0o777 == 0o600, 'custody contains unsafe file')
            if path.name in ('.custody-lock','scope.json'): continue
            require(path.stat().st_size <= 65536, 'custody file byte budget exceeded')
            require(len(objects) < 512, 'custody event budget exceeded')
            raw = regular(path); row = loads(raw); objects[path.name] = row
            if path.name.startswith('allocation-'):
                require(set(row) == {'schema_version','key_digest','fingerprint','principal_ref','scope_ref','source_cut_binding','authority_effect'}, 'allocation metadata must be closed')
                require(row['schema_version']=='lab-read-allocation/v1-candidate' and row['authority_effect']=='none', 'allocation schema/authority differs')
                require(re.fullmatch('[0-9a-f]{64}',row['key_digest']) and re.fullmatch('[0-9a-f]{64}',row['fingerprint']), 'allocation digest invalid')
                require(path.name=='allocation-'+row['key_digest']+'.json', 'allocation locator differs')
                require(row['principal_ref']==self.principal and row['scope_ref']==self.scope and row['source_cut_binding']==self.cut, 'allocation scope differs')
                allocations[row['key_digest']] = (row,binding(path))
            else:
                match = re.fullmatch(r'event-([0-9a-f]{64})-([0-9]{4})\.json',path.name)
                require(match is not None, 'unexpected custody file')
                require(set(row)=={'schema_version','key_digest','sequence','previous_binding','session_ref','agent_instance_ref','principal_ref','scope_ref','source_cut_binding','posture','opened_at','ended_at','context_pack_digest','disposal_observed','authority_effect','assignment_authority','action_permission','short_memory_persisted','unresolved_action_refs'}, 'custody event metadata must be closed')
                require(row['schema_version']=='lab-read-custody-event/v1-candidate' and row['authority_effect']=='none' and row['assignment_authority']=='unresolved' and row['action_permission']=='none' and row['short_memory_persisted'] is False and row['unresolved_action_refs']==[], 'custody event authority/memory differs')
                require(row['principal_ref']==self.principal and row['scope_ref']==self.scope and row['source_cut_binding']==self.cut, 'custody event scope differs')
                require(match.group(1)==row['key_digest'] and int(match.group(2))==row['sequence'] and 0<=row['sequence']<10000, 'event locator differs')
                require(re.fullmatch(r'protocol:ephemeral-agent-session:[0-9a-f-]{36}',row['session_ref']) and re.fullmatch(r'protocol:ephemeral-agent-instance:[0-9a-f-]{36}',row['agent_instance_ref']), 'invalid ephemeral identity')
                require(re.fullmatch('[0-9a-f]{64}',row['context_pack_digest']), 'context digest invalid')
                require(row['posture'] in ['active','closed','expired','indeterminate'], 'unknown custody posture')
                require((row['posture']=='active' and row['disposal_observed'] is False and row['ended_at'] is None) or (row['posture']!='active' and row['disposal_observed'] is True and isinstance(row['ended_at'],str)), 'posture/disposal mismatch')
                datetime.fromisoformat(row['opened_at'])
                if row['ended_at'] is not None: datetime.fromisoformat(row['ended_at'])
                result.setdefault(row['key_digest'],[]).append((row,binding(path)))
        identities = set()
        for key, events in result.items():
            require(key in allocations, 'custody event allocation missing')
            previous = allocations[key][1]; first = events[0][0]
            require(first['session_ref'] not in identities, 'duplicate Session identity')
            identities.add(first['session_ref'])
            for index,(row,b) in enumerate(events):
                require(row['sequence']==index and row['previous_binding']==previous, 'custody history gap or byte drift')
                require(all(row[k]==first[k] for k in ['session_ref','agent_instance_ref','opened_at','context_pack_digest']), 'immutable custody identity differs')
                require(index==0 or events[index-1][0]['posture']=='active', 'terminated consumer cannot resume')
                previous=b
        return allocations,result

    def _owner(self, principal):
        require(not self.closed,'custodian closed')
        require(principal==self.principal,'consumer not found in this principal scope')

    def _lookup(self, session_ref):
        allocations,history=self.history()
        matches=[(key,rows[-1]) for key,rows in history.items() if rows[0][0]['session_ref']==session_ref]
        require(len(matches)==1,'consumer not found in this principal scope')
        return matches[0]

    def open(self, principal, key):
        with self.mutex:
            self._owner(principal)
            require(isinstance(key,str) and 1<=len(key.encode())<=256,'bounded custody key required')
            self.guard()
            key_digest=sha(key.encode())
            fingerprint=sha(encoded({'principal_ref':self.principal,'scope_ref':self.scope,'source_cut_binding':self.cut,'consumer_control_binding':self.control,'action_permission':'none'}))
            allocations,history=self.history()
            if key_digest in allocations:
                require(allocations[key_digest][0]['fingerprint']==fingerprint,'allocation control conflict')
                require(key_digest in history,'allocation is indeterminate; reconcile without redispatch')
                row,b=history[key_digest][-1]
                return self.inspect(principal,row['session_ref'])
            require(len(allocations)<128,'custody allocation budget exhausted')
            allocation={'schema_version':'lab-read-allocation/v1-candidate','key_digest':key_digest,'fingerprint':fingerprint,
                'principal_ref':self.principal,'scope_ref':self.scope,'source_cut_binding':self.cut,'authority_effect':'none'}
            prior=put(self.root/('allocation-'+key_digest+'.json'),allocation)
            consumer=None
            try:
                consumer=self.factory()
                require(isinstance(consumer,ContextSession),'actual pinned context consumer required')
                pack=consumer.context()
                require(pack['action_permission']=='none' and pack['short_memory_persisted'] is False,'read consumer authority/memory differs')
                require(not any(r.get('role')=='assignment_ref' for r in pack['resolved_references']),'unassigned read custody cannot claim assignment authority')
                self.guard()
                row={'schema_version':'lab-read-custody-event/v1-candidate','key_digest':key_digest,'sequence':0,'previous_binding':prior,
                    'session_ref':consumer.session_id,'agent_instance_ref':consumer.instance_id,'principal_ref':self.principal,'scope_ref':self.scope,'source_cut_binding':self.cut,
                    'posture':'active','opened_at':pack['generated_at'],'ended_at':None,'context_pack_digest':pack['pack_digest'],'disposal_observed':False,
                    'authority_effect':'none','assignment_authority':'unresolved','action_permission':'none','short_memory_persisted':False,'unresolved_action_refs':[]}
                put(self.root/('event-'+key_digest+'-0000.json'),row)
                self.live[consumer.session_id]=consumer
                return self.inspect(principal,consumer.session_id)
            except BaseException:
                if consumer is not None: consumer.close()
                raise

    def inspect(self, principal, session_ref):
        with self.mutex:
            self._owner(principal);key,(row,b)=self._lookup(session_ref)
            consumer=self.live.get(session_ref)
            if row['posture']=='active' and consumer is not None:
                try:
                    self.guard(); consumer.context()
                except BaseException:
                    expired=consumer.core.clock()>=consumer.core.deadline
                    self._dispose(key,row,b,consumer,'expired' if expired else 'indeterminate')
                    key,(row,b)=self._lookup(session_ref)
            view=copy.deepcopy(row)
            if row['posture']=='active' and consumer is None:
                view['posture']='indeterminate'
            view.pop('previous_binding');view.pop('key_digest');view.pop('sequence')
            view['metadata_binding']=b;view['short_memory_in_response']=False
            view['durable_continuity_source']='project-state-via-context-and-ontology-views'
            view['claim_ceiling']='Unassigned development read consumer only. Custody is not AgentAssignment permission; lost live process does not prove disposal.'
            return view

    def note(self, principal, session_ref, text):
        with self.mutex:
            metadata=self.inspect(principal,session_ref)
            require(metadata['posture']=='active','no current live read consumer')
            return self.live[session_ref].note(text)

    def _dispose(self,key,row,b,consumer,posture):
        # Do not read Project State or demand freshness before disposing RAM.
        consumer.close()
        require(consumer.closed and consumer.core.closed and consumer.core._memory==[] and consumer.core._pack is None and consumer._pack is None,'actual disposal not observed')
        self.live.pop(row['session_ref'],None)
        next_row={**row,'sequence':row['sequence']+1,'previous_binding':b,'posture':posture,'ended_at':stamp(),'disposal_observed':True}
        return put(self.root/('event-'+key+'-'+str(next_row['sequence']).zfill(4)+'.json'),next_row)

    def close_consumer(self, principal, session_ref, expected_binding):
        with self.mutex:
            self._owner(principal);key,(row,b)=self._lookup(session_ref)
            require(b==expected_binding,'exact custody metadata binding differs')
            if row['posture']!='active': return self.inspect(principal,session_ref)
            consumer=self.live.get(session_ref)
            require(consumer is not None,'lost live process is indeterminate; disposal cannot be asserted')
            self._dispose(key,row,b,consumer,'closed')
            return self.inspect(principal,session_ref)

    def close(self):
        with self.mutex:
            if self.closed:return
            errors=[]
            # Even corrupt durable metadata must not keep owned live RAM alive.
            for session_ref,consumer in list(self.live.items()):
                try:
                    key,(row,b)=self._lookup(session_ref)
                    self._dispose(key,row,b,consumer,'closed')
                except BaseException as error:
                    consumer.close();self.live.pop(session_ref,None);errors.append(error)
            self.closed=True;self.lock.close()
            if errors:raise errors[0]
