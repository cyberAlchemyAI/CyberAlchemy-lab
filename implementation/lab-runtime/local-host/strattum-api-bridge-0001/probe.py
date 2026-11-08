"""Inspect installed Lab signed cuts through a fresh authenticated Reader fixture.

This is a source-discovery probe. It prints no credential or artifact body.
"""

import importlib.util
import json
import sys
import tempfile
from pathlib import Path


PICK = sys.modules.get('cal_installed_runtime_selection_v1')
if PICK is None:
    raise RuntimeError('Run with the installed selected-python launcher')
PICK.require_runtime_ready()
ROOT = PICK.root()
OPERATOR = ROOT / 'implementation/lab-runtime/local-host/t21-installed-operator-0001/command.py'
spec = importlib.util.spec_from_file_location('_strattum_installed_operator', OPERATOR)
operator = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = operator
spec.loader.exec_module(operator)


def main():
    m = operator.M
    protocol = operator.P
    m['guard'].verify(operator.SOURCE)
    schemas = protocol.Schemas(operator.PROFILE)
    with protocol.source.replay_source(protocol.source.CURRENT_LEGACY_NAME) as view:
        with tempfile.TemporaryDirectory(prefix='cal-strattum-api-probe-') as temporary:
            root = Path(temporary)
            materials, metadata, _ = m['example_fixture'].materials_for(view)
            key, policy, digest = m['metadata_fixture'].provision(root, materials, metadata, scoped=False)
            channel = m['auth'].ReaderChannel(policy, digest, schemas)
            host = None
            try:
                channel.authenticate(m['fixtures'].proof(key, channel.challenge))
                key = None
                host = m['service'].Service(view, channel, schemas)
                cuts = [m['handlers'].cut(item) for item in host.handlers.available_views]
                observations = []
                surface = m['integration_dispatch'].IntegrationService(host)
                for index, cut in enumerate(cuts):
                    request = m['fixtures'].call(
                        channel.context, 'artifact.query', cut,
                        carrier_refs=['cal.artifact-type.project-state/v2'],
                        identity_refs=[], relation_kind_refs=[], max_depth=0, limit=100,
                        page_cursor=None, query_basis='canonical',
                        freshness_requirement='current' if index == len(cuts)-1 else 'exact-historical',
                    )
                    reply = operator.invoke(surface, request, schemas)
                    row = {'sequence': cut['commit_sequence'], 'cut_sha256': cut['commit_sha256'],
                           'reply_kind': reply['kind'], 'code': reply['message'].get('code'),
                           'states': []}
                    if reply['kind'] == 'result':
                        row['states'] = reply['message']['results']
                    observations.append(row)
                print(json.dumps({'result': 'observed', 'api_source_sha256': operator.SOURCE,
                                  'profile_sha256': operator.PROFILE,
                                  'authenticated_principal': channel.context['principal_ref'],
                                  'cuts': observations, 'authority_effect': 'none'}, sort_keys=True))
            finally:
                key = None
                if host is not None:
                    host.close()
                channel.close()
    m['guard'].verify(operator.SOURCE)


if __name__ == '__main__':
    main()
