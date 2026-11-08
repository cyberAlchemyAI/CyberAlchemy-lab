"""Private new operator grant attached to an independently live parent custody.

This selects no role or permission. Both original channels remain fresh, and
closing the attached operator releases none of the parent's resource custody.
"""
import copy,importlib,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent

def require(value,reason):
    if not value:raise ValueError(reason)

class SessionAttachment:
    def __init__(self,host,parent,expected):
        package=type(host).__module__.rsplit('.',1)[0]
        self.S=importlib.import_module(package+'.service')
        self.A=importlib.import_module(package+'.auth')
        self.G=importlib.import_module(package+'.guard')
        self.P=importlib.import_module(package+'.protocol')
        self.host=host;self.parent=parent;self.expected=copy.deepcopy(expected)
        require(type(host) is type(parent) is self.S.Service and host is not parent,
                'actual distinct selected operator Service instances required')
        require(type(host.channel) is type(parent.channel) is self.A.ReaderChannel
                and host.channel is not parent.channel, 'independent authenticated operator channels required')
        require(set(expected)=={'schema_version','parent_source_binding','session_ref','agent_instance_ref',
                               'assignment','session_state_binding','source_cut','principal_ref',
                               'parent_policy_sha256','operator_policy_sha256','parent_workspace_binding','operator_workspace_binding',
                               'selection_binding','applicability_binding','instruction_precedence_binding',
                               'authority_effect'}, 'closed private attachment selection required')
        require(expected['schema_version']=='lab-private-Source8-Session-attachment/v1-candidate'
                and expected['authority_effect']=='none', 'attachment is not permission or admission')
        self.sessions=parent.sessions
        self.runtime=importlib.import_module(type(self.sessions).__module__)
        require(type(self.sessions) is self.runtime.ContextSessions
                and Path(self.runtime.__file__).name in ('source8_context_sessions.py','fixture_context_sessions.py','current_context_sessions.py','current_legacy_context_sessions.py'),
                'actual selected Source8 parent custodian required')
        self.resource=self.sessions.live.get(expected['session_ref'])
        require(type(self.resource) is self.runtime.LiveReader, 'actual existing Source8 resource required')
        from jsonschema import Draft202012Validator,FormatChecker
        schema=self.P.source.parse((Path(__file__).parent/'session-attachment.schema.json').read_bytes())
        Draft202012Validator(schema,registry=host.schemas.registry,format_checker=FormatChecker()).validate(expected)
        self.closed=False;self.guard()

    def guard(self):
        require(not self.closed,'attached operator is closed')
        e=self.expected;parent=self.parent;host=self.host
        manifest=self.G.verify(e['parent_source_binding']['sha256'])
        for code in (Path(__file__).resolve(),Path(__file__).parent/'session-attachment.schema.json',Path(self.runtime.__file__).resolve()):
            require({'path':str(code.relative_to(self.P.ROOT)),'sha256':self.P.source.sha(code.read_bytes())} in manifest['files'],'attachment/runtime bytes are outside common host source')
        host.schemas.guard();host.vault.guard()
        path=Path(self.S.__file__).resolve().parent/'source-manifest.json'
        require(e['parent_source_binding']=={'path':str(path.relative_to(self.P.ROOT)),
                                           'sha256':self.P.source.sha(path.read_bytes())}, 'selected common host source differs')
        p=parent.channel.guard();c=host.channel.guard()
        assessment=(host.channel.policy['source_name']==self.P.source.CURRENT_LEGACY_NAME
                    and host.channel.policy['schema_version']=='lab-local-lesson-assessment-policy/v1-candidate')
        if assessment:
            require(p['principal_ref']==e['principal_ref']==self.runtime.D.records.PRINCIPAL
                    and c['principal_ref']!=p['principal_ref']
                    and p['role_assignment_bindings']==c['role_assignment_bindings']==[],
                    'independent assessor or original Session Principal differs')
        else:
            require(p['principal_ref']==c['principal_ref']==e['principal_ref']
                    and p['role_assignment_bindings']==c['role_assignment_bindings']==[],
                    'foreign Principal or inherited role refused')
        require(parent.channel.expected_sha==e['parent_policy_sha256']
                and host.channel.expected_sha==e['operator_policy_sha256'], 'independent grant binding differs')
        require(host.channel.policy['schema_version'] in ('lab-local-lesson-application-policy/v2-candidate',
                                                        'lab-local-lesson-assessment-policy/v1-candidate'),
                'attachment requires independently scoped application or assessment grant')
        require(host.handlers.view is parent.handlers.view and host.schemas is parent.schemas
                and host.vault.control_binding==e['operator_workspace_binding']
                and parent.vault.control_binding==e['parent_workspace_binding']
                and host.vault.root!=parent.vault.root
                and host.vault.manifest['principal_ref']==c['principal_ref']
                and parent.vault.manifest['principal_ref']==e['principal_ref']
                and host.vault.manifest['scope_refs']==parent.vault.manifest['scope_refs'],
                'actual shared source, Schemas or owned workspace differs')
        require(parent.sessions is self.sessions and not self.sessions.closed
                and self.sessions.channel is parent.channel
                and self.sessions.live.get(e['session_ref']) is self.resource
                and self.resource.source is self.sessions.source
                and self.resource.bridge is self.sessions.bridge
                and self.resource.bridge.channel is parent.channel, 'foreign, disposed or reconstructed custody refused')
        self.resource.guard();row=self.sessions.selected(e['session_ref'])
        require(row['posture']=='active' and row['source_cut']==e['source_cut']==self.sessions.source.source_cut
                and row['assignment']==e['assignment'] and row['session_state_binding']==e['session_state_binding']
                and row['agent_instance_ref']==e['agent_instance_ref']==self.resource.agent['node_id']
                and row['session_ref']==self.resource.session['node_id'], 'actual live Session preimage differs')
        selection=self.resource.lesson_selections.get(e['selection_binding']['sha256'])
        require(type(selection) is dict and selection['selection_binding']==e['selection_binding']
                and selection['source_cut']==e['source_cut'],'exact actual parent selection output is unavailable')
        for selected in (e['selection_binding'],e['applicability_binding'],e['instruction_precedence_binding']):
            parent.vault.object_read(selected)
        result=self.P.frame_parse(parent.vault.object_read(e['selection_binding']))
        require(result['instruction_precedence_binding']==e['instruction_precedence_binding']
                and any(item['applicability_check_binding']==e['applicability_binding'] for item in result['items']),
                'independently selected parent output bindings differ')
        return row

    def material_guard(self):
        require(not self.closed and self.resource is not None,
                'closed attachment material scope')
        resource=self.resource
        with resource._lifetime_lock:
            require(self.resource is resource and not resource.closed,
                    'disposed attachment material scope')
            return self._material_guard_locked()

    def _material_guard_locked(self):
        # Pure candidate scopes already hold the exact signed source graph and
        # run full original source checks at entry and exit. Borrow only those
        # immutable facts; private permission, revocation and UTC remain live.
        require(not self.closed and self.resource is not None,
                'closed attachment material scope')
        scope=self.runtime.D.FACT_SCOPE.scope_for_source(self.resource.source)
        if scope is None:
            return self.guard()
        e=self.expected;parent=self.parent;host=self.host
        require(not self.closed and scope.host is host.channel,
                'unselected or closed attachment material scope')
        scope.check()
        p=parent.channel.termination_guard();c=host.channel.termination_guard()
        assessment=(host.channel.policy['source_name']==self.P.source.CURRENT_LEGACY_NAME
                    and host.channel.policy['schema_version']=='lab-local-lesson-assessment-policy/v1-candidate')
        require(type(host) is type(parent) is self.S.Service and host is not parent
                and type(host.channel) is type(parent.channel) is self.A.ReaderChannel
                and host.channel is not parent.channel,'attachment material host or channel identity differs')
        if assessment:
            require(p['principal_ref']==e['principal_ref']==self.runtime.D.records.PRINCIPAL
                    and c['principal_ref']!=p['principal_ref']
                    and p['role_assignment_bindings']==c['role_assignment_bindings']==[],
                    'attachment material assessor identity differs')
        else:
            require(p['principal_ref']==c['principal_ref']==e['principal_ref']
                    and p['role_assignment_bindings']==c['role_assignment_bindings']==[],
                    'attachment material Principal or role differs')
        require(parent.channel.expected_sha==e['parent_policy_sha256']
                and host.channel.expected_sha==e['operator_policy_sha256'],
                'attachment material grant changed')
        require(host.channel.policy['schema_version'] in ('lab-local-lesson-application-policy/v2-candidate',
                                                        'lab-local-lesson-assessment-policy/v1-candidate'),
                'attachment material operator kind differs')
        from .workspace import validate_scope
        proot,pmanifest=validate_scope(parent.channel.policy);hroot,hmanifest=validate_scope(host.channel.policy)
        require(host.handlers.view is parent.handlers.view and host.handlers.view is self.resource.source.view
                and host.schemas is parent.schemas
                and host.vault.root==hroot and host.vault.manifest==hmanifest
                and parent.vault.root==proot and parent.vault.manifest==pmanifest
                and host.vault.control_binding==e['operator_workspace_binding']
                and parent.vault.control_binding==e['parent_workspace_binding']
                and host.vault.root!=parent.vault.root
                and host.vault.manifest['principal_ref']==c['principal_ref']
                and parent.vault.manifest['principal_ref']==e['principal_ref']
                and host.vault.manifest['scope_refs']==parent.vault.manifest['scope_refs'],
                'attachment material owned workspace or common source changed')
        require(parent.sessions is self.sessions and not self.sessions.closed
                and self.sessions.channel is parent.channel
                and self.sessions.live.get(e['session_ref']) is self.resource
                and self.resource.source is self.sessions.source
                and self.resource.bridge is self.sessions.bridge
                and self.resource.bridge.channel is parent.channel,
                'attachment material custody changed')
        self.resource.guard();row=self.sessions.selected(e['session_ref'])
        require(row['posture']=='active' and row['source_cut']==e['source_cut']==self.sessions.source.source_cut
                and row['assignment']==e['assignment'] and row['session_state_binding']==e['session_state_binding']
                and row['agent_instance_ref']==e['agent_instance_ref']==self.resource.agent['node_id']
                and row['session_ref']==self.resource.session['node_id'],
                'attachment material live Session preimage changed')
        proof=self.resource.lesson_selections.get(e['selection_binding']['sha256'])
        require(type(proof) is dict and proof['selection_binding']==e['selection_binding']
                and proof['source_cut']==e['source_cut'],
                'attachment material selection changed')
        return scope.check()

    def material(self,selected):
        require(selected in [self.expected[k] for k in ('selection_binding','applicability_binding','instruction_precedence_binding')],
                'unselected parent material refused')
        require(not self.closed and self.resource is not None,
                'closed attachment material scope')
        resource=self.resource
        with resource._lifetime_lock:
            require(self.resource is resource and not resource.closed,
                    'disposed attachment material scope')
            self.material_guard()
            raw=self.parent.vault.object_read(selected)
            self.material_guard()
            return raw

    def close(self):
        self.closed=True
        self.resource=None;self.sessions=None;self.parent=None
