"""One unchanged-envelope surface over independently authenticated branches."""
from .protocol import compact,frame_parse,source

ACTION_OPERATIONS=('action.evaluate','action.dispatch','action.reconcile')
GOVERNANCE_OPERATIONS=('checkpoint.resolve','admission.apply','capability.adoption.prepare')

class IntegrationService:
    def __init__(self,base_service,*,action_service=None,governance_service=None):
        from .service import Service
        source.require(type(base_service) is Service,'actual selected base dispatcher required')
        self.base=base_service;self.actions=action_service;self.governance=governance_service
        self.schemas=base_service.schemas;self.profile_binding=self.schemas.profile_binding
        self.branches=[base_service]+[s for s in (action_service,governance_service) if s is not None]
        import sys
        from pathlib import Path
        members=source.parse(source.original(self.schemas.profile['integration_members_binding']))['members']
        for kind,service,classname in (('actions',action_service,'ActionService'),('governance',governance_service,'GovernanceService')):
            if service is None:continue
            selected=members[kind];folder=Path(__file__).resolve().parent.parent/selected['directory']
            module=sys.modules.get(type(service).__module__)
            source.require(module is not None and Path(module.__file__).resolve()==folder/'service.py'
                and type(service) is getattr(module,classname,None),'actual independently selected branch implementation required')
            source.require(source.sha((folder/'source-manifest.json').read_bytes())==selected['source_sha256']
                and source.sha((folder/'contract-profile.json').read_bytes())==selected['profile_sha256'],'independent branch source/profile pin differs')
        for service in self.branches:
            source.require(service.schemas is self.schemas,'all branches require the same independently selected schema object')
            selected=getattr(service,'profile_binding',self.schemas.profile_binding)
            source.require(selected==self.profile_binding,'branch public profile differs from common profile')
        self.callbacks={id(service):service.call for service in self.branches}
        self.closed=False

    def _branch_context(self,service):
        return getattr(service.channel,'context',None)

    def call(self,raw):
        source.require(not self.closed,'common dispatcher closed')
        for service in self.branches:
            source.require(service.call==self.callbacks[id(service)],'selected dispatcher callback changed')
        try:call=frame_parse(raw)
        except Exception:return self.base.call(raw)
        if not isinstance(call,dict):return self.base.call(raw)
        operation=call.get('operation')
        # A public context is an opaque locator, never authority. The selected
        # branch repeats its real nonce, principal, policy, source and clock
        # checks against original raw bytes before producing any effect.
        supplied_context=call.get('caller_context_ref')
        matches=[s for s in self.branches if isinstance(self._branch_context(s),dict)
                 and self._branch_context(s).get('context_ref')==supplied_context]
        source.require(len(matches)<=1,'ambiguous independent authenticated contexts')
        if matches:return matches[0].call(raw)
        if operation in ACTION_OPERATIONS and self.actions is not None:return self.actions.call(raw)
        if operation in GOVERNANCE_OPERATIONS and self.governance is not None:return self.governance.call(raw)
        if operation=='operation.inspect':
            lookup=call.get('message',{}).get('lookup',{})
            if lookup.get('operation') in ACTION_OPERATIONS and self.actions is not None:return self.actions.call(raw)
            if lookup.get('operation') in GOVERNANCE_OPERATIONS and self.governance is not None:return self.governance.call(raw)
        return self.base.call(raw)

    def close(self):
        if self.closed:return
        self.closed=True;errors=[]
        for service in reversed(self.branches):
            try:service.close()
            except BaseException as error:errors.append(error)
        if errors:raise errors[0]
