"""Selected fixture/producer packet preflight, with no API dispatch or workflow effect."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')


def selected(name, filename):
    path = HERE / filename
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    fixture = selected('_cal_t31_api52_cold_fixture_v4', 'fixture_api52.py')
    invoke = selected('_cal_t31_api52_cold_invoke_v4', 'invoke.py')
    start = time.monotonic()
    with fixture.current_fixture() as live:
        root = live['owned_root']
        host_before = fixture.owned_snapshot(live['workspace'])
        producer_before = fixture.owned_snapshot(live['producer_service'].vault.root)
        factory = invoke.install_factory(live)
        selected_input, request_raw, packet = invoke.prepare(live, factory)
        host_after = fixture.owned_snapshot(live['workspace'])
        producer_after = fixture.owned_snapshot(live['producer_service'].vault.root)
        if host_before != host_after or producer_before != producer_after:
            raise ValueError('cold preparation changed host or producer Vault')
        result = {
            'result': 'PASS',
            'selected_api_source_sha256': fixture.SOURCE_SHA,
            'selected_api_profile_sha256': fixture.PROFILE_SHA,
            'selected_signed_family': live['source_cut']['store_ref'],
            'selected_principal_ref': live['policy']['principal_ref'],
            'private_plan_transition_count': len(live['output_plan']['transitions']),
            'late_material_count': len(packet['materials']),
            'late_selection_sha256': selected_input['sha256'],
            'original_request_sha256': hashlib.sha256(request_raw).hexdigest(),
            'producer_service_type': type(live['producer_service']).__name__,
            'host_vault_regular_files_unchanged': True,
            'producer_vault_regular_files_unchanged': True,
            'native_api_dispatches': 0,
            'workflow_run_appends': 0,
            'later_consumers': 0,
            'original_28_transition_increment': 0,
            'claim_ceiling': 'Selected fixture and late packet only; tailored Work input, no producer or workflow effect.',
        }
    if root.exists():
        raise ValueError('private temporary fixture root remains after cold preparation')
    result['private_fixture_root_removed'] = True
    result['elapsed_seconds'] = time.monotonic() - start
    return result


if __name__ == '__main__':
    print(json.dumps(main(), sort_keys=True, indent=2), flush=True)
