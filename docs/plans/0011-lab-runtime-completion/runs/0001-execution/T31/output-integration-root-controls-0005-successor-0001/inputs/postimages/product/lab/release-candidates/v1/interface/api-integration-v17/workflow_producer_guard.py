"""Original producer boundary, separate from workflow-only coordination guard."""
from .protocol import HERE,ROOT,source,Schemas
from .handlers import cut
from .workflow_output_contracts import need,closed

def guard_original_producer(service,coordinator,policy_binding,source_binding,*,operation=None):
    from .service import Service
    from .auth import ReaderChannel
    need(type(service)is Service and type(service.channel)is ReaderChannel and type(service.schemas)is Schemas and service.schemas.profile_binding==coordinator.schemas.profile_binding,'exact original producer Service/ReaderChannel required')
    closed(policy_binding,('ref','sha256'));closed(source_binding,('path','sha256'))
    need(source_binding['path']==str((HERE/'source-manifest.json').relative_to(ROOT)),'exact original producer API Source origin required')
    from .guard import verify
    verify(source_binding['sha256'])
    context=service.channel.guard();policy=service.channel.policy_guard()
    need(policy_binding=={'ref':str(service.channel.path),'sha256':service.channel.expected_sha},'independently selected actual producer policy differs')
    need(context['principal_ref']==coordinator.channel.guard()['principal_ref'] and cut(service.handlers.view)==cut(coordinator.handlers.view),'actual producer principal/source cut differs')
    need(policy['scope_refs']==[service.handlers.view.data['config']['scope_ref']] and policy['scope_refs']==coordinator.channel.policy_guard()['scope_refs'],'actual original producer scope differs')
    if operation is not None:need(operation in policy['allowed_operations'],'original producer policy denies this existing API operation')
    service.schemas.guard();service.vault.guard()
    need(all(source.sha((HERE/name).read_bytes())==pin for name,pin in service.code_files.items()),'original producer API code changed')
    # The original current() retains its selected reader/signed source and full
    # original freshness checks for this actual branch; no integrated-family
    # predicate or workflow grant is substituted for its producer policy.
    need(service.handlers.current(),'original producer selected source is stale')
    if service.session_attachment is not None:service.session_attachment.guard()
    return context,policy
