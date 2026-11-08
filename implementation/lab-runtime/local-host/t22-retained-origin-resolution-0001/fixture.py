"""Fresh current Reader resolves one exact retained native fixture candidate."""
import copy
from contextlib import contextmanager
from datetime import timedelta
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
_spec=importlib.util.spec_from_file_location('_retained_origin_exact_inputs',HERE/'inputs.py')
IN=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(IN)

@contextmanager
def example(view,schemas,*,api_namespace,origin_root=None):
    mod=lambda name:importlib.import_module(api_namespace+'.'+name)
    P,A,F,S,H,W,R,FH=(mod(n) for n in ('protocol','auth','fixtures','service','handlers','workspace','fixture_resolution_source','fixture_resolution_handler'))
    IN.need(P.ROOT==ROOT and hasattr(FH.FixtureResolution,'retained_original') and hasattr(FH.FixtureResolution,'verify_origin'),
            'selected actual maintained retained-origin resolver required')
    selected=view.custody_signed_sources;selected.guard();cut=H.cut(view)
    root_inputs=Path(origin_root) if origin_root is not None else ROOT.parent/'.cal-runtime/qualification/t22-origin71'
    original=IN.load(root_inputs)
    submission=json.loads(original['native-submission.json']);observation=json.loads(original['native-call-observation.json']);request=json.loads(original['native-request.json'])
    D=P.source.current_legacy_delivery();period=D.load(D.reader.HERE/'packages/0001/period.json')
    now=A.now();end=min(now+timedelta(minutes=30),A.instant(period['expires_at']))
    IN.need(A.instant(period['not_before'])<=now<end,'actual current coordinating Source period unavailable')
    with tempfile.TemporaryDirectory(prefix='cal-retained-origin-resolution-') as temporary:
        root=Path(temporary);root.chmod(0o700)
        principal='principal:retained-fixture-resolution-owner:'+uuid.uuid4().hex
        key,path,_=F.provision(root,source_name=P.source.CURRENT_LEGACY_NAME,principal=principal,materials={})
        policy=P.frame_parse(path.read_bytes());vault=Path(policy['workspace']['root'])
        capsule=R.build(submission=submission,observation=observation,candidate_raw=original['native-candidate.json'],request=request,
          now=A.now(),period_end=end.isoformat(),signing_key=key,fixture_principal_ref=principal)
        retained=IN.wrapper(capsule,original,copy.deepcopy(cut));raw=R.canon(retained);digest=R.sha(raw)
        manifest=P.frame_parse((vault/'workspace.json').read_bytes());W.atomic(vault/'objects'/(digest+'.json'),raw)
        route={'ref':'workspace-object:'+manifest['workspace_ref']+':'+digest,'sha256':digest}
        authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
        method=P.binding(str((P.HERE/'fixture_resolution_handler.py').relative_to(ROOT)),(P.HERE/'fixture_resolution_handler.py').read_bytes())
        policy.update(schema_version='lab-local-challenge-resolution-policy/v1-candidate',source_name=P.source.CURRENT_LEGACY_NAME,
          allowed_operations=list(P.RESOLUTION_SUPPORTED),expires_at=end.isoformat(),session_control=None,projection_control=None,
          purpose='durable-metadata-and-exact-challenge-resolution',scope_control=None,
          development_authorization_binding=P.binding(str(authority.relative_to(ROOT)),authority.read_bytes()),
          resolution_control={'routing_binding':route,'method_binding':method})
        policy_raw=P.compact(policy);path.write_bytes(policy_raw);path.chmod(0o600)
        channel=A.ReaderChannel(path,R.sha(policy_raw),schemas);host=None
        try:
            authenticated=channel.authenticate(F.proof(key,channel.challenge));key=None
            host=S.Service(view,channel,schemas)
            builder=FH.FixtureResolution(host,route,{'path':str((P.HERE/'source-manifest.json').relative_to(ROOT)),'sha256':R.sha((P.HERE/'source-manifest.json').read_bytes())})
            message={'schema_version':'lab-local-fixture-challenge-resolution/v1-candidate',
              'challenge':builder.header('challenge-event',original['native-candidate.json'],'challenge.candidate.1'),
              'resolution_decision':builder.header('decision'),'evidence_bindings':[route],
              'semantic_change_proposal_binding':None,'governance_change_proposal_binding':None,'unresolved_gaps':[],
              'source_cut':copy.deepcopy(cut),'authority_effect':'none'}
            IN.need(schemas.protocol_valid('urn:cyberalchemy-lab:protocol:challenge-resolution:v1-candidate',message),
                    'unchanged public resolution request schema differs')
            def call():
                value=F.call(channel.context,'lab.status',cut)
                value.update(operation='challenge.resolve',message=copy.deepcopy(message),deadline=end.isoformat(),
                  idempotency_key='retained-native-fixture-resolution:'+digest)
                return value
            yield host,call,{'root':vault,'fixture_root':root,'policy_path':path,'reader_key_path':root/'reader.pem',
              'routing_binding':route,'original_source_cut':copy.deepcopy(submission['source_cut']),'coordinating_source_cut':copy.deepcopy(cut),
              'original_source_posture':'historical-verified-native-origin','old_Work_or_Contract_Source_current':False,
              'authentication_reply':authenticated,'original_actual_inputs':copy.deepcopy(IN.PINS),'authority_effect':'none'}
        finally:
            if host is not None:host.close()
            else:channel.close()
            key=None
