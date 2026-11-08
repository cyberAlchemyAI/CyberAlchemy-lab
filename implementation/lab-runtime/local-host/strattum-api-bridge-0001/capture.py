"""Capture two exact-cut authenticated Lab reads for the Strattum test.

Run through the installed selected-python launcher. Private credentials remain
in a disposable /tmp fixture; public call/reply evidence is retained in a
fresh owner-only output directory outside the installation.
"""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile

from probe import operator


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def write_new(path, value):
    raw = encoded(value) + b'\n'
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return sha(raw)


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def run(output):
    output = Path(output).absolute()
    need(not output.exists() and output.parent.is_dir() and not any(p.is_symlink() for p in output.parents),
         'fresh unlinked private output required')
    output.mkdir(mode=0o700)
    sync_dir(output.parent)
    write_new(output / 'AUDIT-INTENT.json', {'schema_version': 'lab-strattum-api-read-intent/v1',
                                           'purpose': 'two authenticated signed-cut Project State reads',
                                           'api_source_sha256': operator.SOURCE,
                                           'profile_sha256': operator.PROFILE, 'status': 'started',
                                           'authority_effect': 'none'})
    sync_dir(output)
    m = operator.M
    protocol = operator.P
    m['guard'].verify(operator.SOURCE)
    schemas = protocol.Schemas(operator.PROFILE)
    rows = []
    with protocol.source.replay_source(protocol.source.CURRENT_LEGACY_NAME) as view:
        with tempfile.TemporaryDirectory(prefix='cal-strattum-api-capture-') as temporary:
            root = Path(temporary)
            materials, metadata, _ = m['example_fixture'].materials_for(view)
            key, policy, policy_sha = m['metadata_fixture'].provision(root, materials, metadata, scoped=False)
            channel = m['auth'].ReaderChannel(policy, policy_sha, schemas)
            host = None
            try:
                policy_public = json.loads(policy.read_bytes())
                challenge_public = copy.deepcopy(channel.challenge)
                proof_raw = m['fixtures'].proof(key, channel.challenge)
                authentication = channel.authenticate(proof_raw)
                proof_public = json.loads(proof_raw)
                key = None
                host = m['service'].Service(view, channel, schemas)
                cuts = [m['handlers'].cut(item) for item in host.handlers.available_views]
                need(len(cuts) >= 3 and cuts[0] != cuts[-1], 'two distinct signed cuts required')
                surface = m['integration_dispatch'].IntegrationService(host)
                targets = ((cuts[0], 'project-state:cyberalchemy-v2-to-lab-migration:specialist-owner-bootstrap-0003'),
                           (cuts[-1], f"project-state:{cuts[-1]['store_ref']}:2"))
                for index, (cut, identity) in enumerate(targets):
                    query = m['fixtures'].call(
                        channel.context, 'artifact.query', cut,
                        carrier_refs=['cal.artifact-type.project-state/v2'], identity_refs=[identity],
                        relation_kind_refs=[], max_depth=0, limit=100, page_cursor=None,
                        query_basis='canonical',
                        freshness_requirement='current' if index else 'exact-historical',
                    )
                    query_reply = operator.invoke(surface, query, schemas)
                    need(query_reply['kind'] == 'result', 'exact-cut query refused')
                    query_result = query_reply['message']
                    need(query_result['source_cut'] == cut and query_result['requested_source_cut'] == cut
                         and query_result['query_basis'] == 'canonical'
                         and query_result['freshness'] == ('current' if index else 'historical')
                         and query_result['next_page_cursor'] is None
                         and len(query_result['results']) == 1
                         and query_result['results'][0]['identity_ref'] == identity,
                         'exact-cut query result is partial, ambiguous, or moved')
                    selected = query_result['results'][0]
                    inspect = m['fixtures'].call(channel.context, 'artifact.inspect', cut,
                                                 artifact=selected,
                                                 include=['body', 'provenance', 'evidence', 'gaps'])
                    inspect_reply = operator.invoke(surface, inspect, schemas)
                    need(inspect_reply['kind'] == 'result' and inspect_reply['message']['artifact'] == selected
                         and inspect_reply['message']['source_cut'] == cut
                         and inspect_reply['message']['envelope']['source_cut'] == cut
                         and inspect_reply['message']['envelope']['artifact'] == selected,
                         'exact selected Project State inspect refused or moved')
                    body = inspect_reply['message']['envelope']['decoded_artifact']['body']
                    need(body['kind'] == 'project-state' and body['payload']['project_ref'] == cut_scope
                         and body['node_id'] == selected['identity_ref'],
                         'inspected Project State body differs from the selected identity')
                    rows.append({'source_cut': cut, 'artifact': selected,
                                 'query_call': query, 'query_reply': query_reply,
                                 'inspect_call': inspect, 'inspect_reply': inspect_reply})
                bad = m['fixtures'].call(channel.context, 'artifact.query', cuts[-1],
                                         carrier_refs=['cal.artifact-type.project-state/v2'],
                                         identity_refs=[], relation_kind_refs=[], max_depth=0,
                                         limit=10, page_cursor=None, query_basis='canonical',
                                         freshness_requirement='current')
                bad['message']['scope_refs'] = ['scope:outside']
                denied = operator.invoke(surface, bad, schemas)
                need(denied['kind'] == 'error' and denied['message']['code'] == 'unauthorized',
                     'wrong-scope query was not refused')
                principal = channel.context['principal_ref']
            finally:
                key = None
                if host is not None:
                    host.close()
                channel.close()
    result = {'schema_version': 'lab-strattum-api-read-capture/v1',
              'api_source_sha256': operator.SOURCE, 'profile_sha256': operator.PROFILE,
              'authenticated_principal': principal, 'policy_sha256': policy_sha,
              'reader_authentication': {'policy': policy_public, 'challenge': challenge_public,
                                        'proof': proof_public, 'result': authentication},
              'reads': rows, 'denied_call': bad, 'denied_reply': denied,
              'lab_mutations_requested': 0, 'authority_effect': 'none'}
    digest = write_new(output / 'CAPTURE.json', result)
    need(sha((output / 'CAPTURE.json').read_bytes()) == digest, 'capture cold read differs')
    write_new(output / 'AUDIT-COMPLETED.json', {'schema_version': 'lab-strattum-api-read-receipt/v1',
                                               'capture_sha256': digest, 'principal_ref': principal,
                                               'policy_sha256': policy_sha,
                                               'cut_sha256s': [sha(encoded(row['source_cut'])) for row in rows],
                                               'query_sha256s': [sha(encoded(row['query_call'])) for row in rows],
                                               'reply_sha256s': [sha(encoded(row['query_reply'])) for row in rows],
                                               'denied_reply_sha256': sha(encoded(denied)),
                                               'status': 'complete', 'authority_effect': 'none'})
    sync_dir(output)
    m['guard'].verify(operator.SOURCE)
    return {'result': 'PASS', 'capture_directory': str(output), 'capture_sha256': digest,
            'authenticated_principal': principal, 'cut_sequences': [r['source_cut']['commit_sequence'] for r in rows],
            'state_refs': [r['artifact']['identity_ref'] for r in rows],
            'wrong_scope': denied['message']['code'], 'authority_effect': 'none'}


cut_scope = 'project:cyberalchemy-v2-to-lab-migration'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.output), sort_keys=True))
