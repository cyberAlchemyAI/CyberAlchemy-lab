"""One fresh authenticated API46 Base lab.status call on the selected WSL cut."""

from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).resolve().parent
API = ROOT / 'product/lab/release-candidates/v1/interface/api-integration-v46-t31-workflow-current-0002'
SOURCE_SHA = 'caf4aa1f4dbfcc8a5eab336e15704487f3e1913b8d76bfbcfbd88b56204a0969'
PROFILE_SHA = 'a4a2afdf2853f135a473c19b8dd83dc4cd3b587bc00821a227a4790a365c7402'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    os.umask(0o077)
    spec = importlib.util.spec_from_file_location('_cal_t31_api46_live_status', API / '__init__.py',
                                                   submodule_search_locations=[str(API)])
    selected = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = selected
    spec.loader.exec_module(selected)
    prefix = spec.name + '.'
    P = __import__(prefix + 'protocol', fromlist=['Schemas'])
    A = __import__(prefix + 'auth', fromlist=['ReaderChannel'])
    S = __import__(prefix + 'service', fromlist=['Service'])
    H = __import__(prefix + 'handlers', fromlist=['cut'])
    F = __import__(prefix + 'example_fixture', fromlist=['materials_for'])
    G = __import__(prefix + 'guard', fromlist=['verify'])
    L = __import__(prefix + 'legacy_fixture_selection', fromlist=['PUBLIC_SOURCE_NAME'])
    C = __import__(prefix + 'projection_refresh', fromlist=['control'])
    G.verify(SOURCE_SHA)
    schemas = P.Schemas(PROFILE_SHA)
    result = {'schema_version': 'lab-T31-API46-authenticated-status/v1-candidate',
              'source_sha256': SOURCE_SHA, 'profile_sha256': PROFILE_SHA,
              'selection_sha256': sha((HERE / 'SELECTION-0001.json').read_bytes()),
              'authority_effect': 'none', 'whole_api_qualified': False,
              'workflow_transition_executed': False,
              'started_at_utc': datetime.now(timezone.utc).isoformat()}
    with P.source.replay_source(L.PUBLIC_SOURCE_NAME) as view:
        materials, metadata, _ = F.materials_for(view)
        with tempfile.TemporaryDirectory(prefix='cal-T31-api46-status-', dir='/tmp') as temporary:
            root = Path(temporary)
            root.chmod(0o700)
            key, policy, pin = F.provision(root, L.PUBLIC_SOURCE_NAME, materials, metadata,
                                           principal=L.EXPECTED_PRINCIPAL,
                                           projection_control=C.control(view))
            channel = A.ReaderChannel(policy, pin, schemas)
            authenticated = channel.authenticate(F.proof(key, channel.challenge))
            service = S.Service(view, channel, schemas)
            try:
                context = authenticated['context']
                if context['principal_ref'] != L.EXPECTED_PRINCIPAL:
                    raise ValueError('actual authenticated principal differs')
                call = F.call(context, 'lab.status', H.cut(view))
                reply = service.call(P.compact(call))
                if not (reply.get('kind') == 'result' and schemas.valid('api-reply', reply)):
                    raise ValueError('selected authenticated Base status refused')
                result.update(status='PASS', source_cut_sha256=sha(P.compact(H.cut(view))),
                              call_sha256=sha(P.compact(call)), reply_sha256=sha(P.compact(reply)),
                              operation='lab.status', reply_kind=reply['kind'],
                              principal_ref=context['principal_ref'])
            finally:
                service.close()
                channel.close()
                key = None
        if root.exists():
            raise ValueError('owned private status root remained')
        if hasattr(view, 'custody_signed_sources'):
            view.custody_signed_sources.guard()
    G.verify(SOURCE_SHA)
    result['private_root_removed'] = True
    result['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
    result['claim_ceiling'] = ('One authenticated current-cut API46 Base lab.status on this WSL host; '
                               'no workflow transition, portable package, owner decision, or release.')
    path = HERE / 'RUN-API46-STATUS-0001.json'
    with path.open('x') as stream:
        json.dump(result, stream, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'status': result['status'], 'receipt_sha256': sha(path.read_bytes())}, sort_keys=True))


if __name__ == '__main__':
    main()
