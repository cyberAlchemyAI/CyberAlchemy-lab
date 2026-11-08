"""Select exact current API adoption original for two local product stages."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'implementation/lab-runtime/local-host/t31-retained-api-0001'))
import prepare_api_configs as A
import product_fixture_production as P


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def enc(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def prepare(terminal_path, output):
    selected = sys.modules.get('cal_installed_runtime_selection_v1')
    need(selected is not None and selected.root() == ROOT,
         'selected installed local product runtime required')
    selected.require_runtime_ready()
    selected.guard()
    source_sha = selected.binding('api.source')['sha256']
    profile_sha = selected.binding('api.profile')['sha256']
    reader = A.original_reader(ROOT)
    api_selection, observed = A.selected_case(
        reader, terminal_path, 'capability.adoption.prepare', source_sha, profile_sha)
    records = {h['version_ref']: (h, raw) for h, raw in observed['outputs']}
    run_ref = 'workflow-run:local-product-' + secrets.token_hex(12)
    reviewer = 'principal:local-fixture-product-reviewer-' + secrets.token_hex(12)
    controls = {'source_sha256': source_sha, 'profile_sha256': profile_sha,
                'source_cut': observed['original_source_cut'],
                'fixture_reviewer_ref': reviewer, 'fixture_run_ref': run_ref,
                'package_manifest_sha256': selected.current().package_pin,
                'adoption_observation_ref': observed['observation_binding']['ref']}
    production = P.produce(records=records, observations=[observed], controls=controls)
    receipt = production['receipt']
    need(receipt['actual_owner_outcome'] is None
         and receipt['human_pilot_performed'] is False
         and receipt['release_approved'] is False,
         'local fixture product boundary changed')
    definition = json.loads((ROOT / 'docs/proposals/0007-lab-integrated-schema-package/workflows/product-adoption-release.json').read_bytes())
    routes = {row['transition_ref']: row for row in definition['transitions']}
    ordered = ('transition:product-adoption-release:candidate-assessed',
               'transition:product-adoption-release:pilot-assessed')
    need(set(ordered) <= set(routes)
         and 'transition:product-adoption-release:release-reviewed' in routes,
         'exact original product workflow stage set required')
    inputs = {
        receipt['current_product']['carrier_ref']: receipt['current_product']['version_ref'],
        receipt['selected_fixture_capability']['carrier_ref']: receipt['selected_fixture_capability']['version_ref'],
        receipt['selected_implementation']['carrier_ref']: receipt['selected_implementation']['version_ref']}
    stages = []
    for ref in ordered:
        route = routes[ref]
        output_headers = receipt['outputs'][ref]
        need(set(inputs) >= set(route['input_carriers'])
             and {h['carrier_ref'] for h in output_headers} == set(route['output_carriers'])
             and len(output_headers) == len(route['output_carriers']),
             'current product input/output carrier closure differs')
        stages.append({'transition_ref': ref,
                       'input_refs': {carrier: inputs[carrier] for carrier in route['input_carriers']},
                       'output_refs': [h['version_ref'] for h in output_headers]})
        inputs.update({h['carrier_ref']: h['version_ref'] for h in output_headers})
    rel = str((HERE / 'product_fixture_production.py').relative_to(ROOT))
    binding = {'path': rel, 'sha256': sha((HERE / 'product_fixture_production.py').read_bytes())}
    config = {'schema_version': 'lab-actual-retained-workflow-run/v1',
              'kind': 'product-adoption-release', 'selections': [api_selection],
              'typed_productions': [{'module_binding': binding,
                                     'entrypoint': 'produce', 'controls': controls}],
              'stages': stages, 'final_state': routes[ordered[-1]]['to_state']}
    output = Path(output).absolute()
    need(not output.exists() and output.parent.is_dir()
         and not output.is_relative_to(ROOT)
         and not any(part.is_symlink() for part in output.parents),
         'fresh external private product selection required')
    raw = enc(config)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return {'config_path': str(output), 'config_sha256': sha(raw),
            'api_observation': observed['observation_binding'],
            'product_originals': receipt['outputs'],
            'fixture_reviewer_ref': reviewer, 'fixture_run_ref': run_ref,
            'actual_owner_outcome': None, 'human_pilot_performed': False,
            'release_approved': False, 'authority_effect': 'none'}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    for name in ('adoption-terminal', 'output'):
        ap.add_argument('--' + name, required=True)
    args = ap.parse_args()
    print(json.dumps(prepare(args.adoption_terminal, args.output), sort_keys=True))
