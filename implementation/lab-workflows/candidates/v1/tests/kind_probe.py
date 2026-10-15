"""Reproduce exact kind rejection against replayed signed catalog contracts.

Both endpoint postimages are prospective and unadmitted. No transaction or grant.
"""
import copy
import importlib
from pathlib import Path
import sys
import tempfile

from integration_support import *


def probe(cases):
    sys.path.insert(0,str(ROOT/'implementation/lab-continuity/candidates/v1'))
    import continuity
    from lab_runtime.replay import ReplayPins,legacy_runtime
    archive=ROOT/'implementation/lab-work/candidates/v1/packages/0002/branch.snapshot'
    expected_sha='03850c8aa4cf7a994f3ce66c25cb68d4567c170ed38e40dc24e115a3e900f944'
    rows=[]
    with tempfile.TemporaryDirectory(prefix='cal-W07-kind-probe-') as temp:
        store=Path(temp)/'original-project'
        data=continuity.restore_archive(archive,expected_sha,store)
        name,_,stage=legacy_runtime(ROOT,ReplayPins(**parse(archive.read_bytes())['project_pins']))
        try:
            module=importlib.import_module(name+'.operations')
            for case in cases:
                original,closure=verify_records(case)
                for gap in closure['runtime_kind_join_gaps']:
                    record=original[gap['relation_ref']];target=gap['endpoint_ref']
                    projection=copy.deepcopy(data['projection'])
                    for endpoint in [record['payload']['source'],record['payload']['target']]:
                        ref=endpoint['version_ref']
                        if ref not in projection['subjects']:
                            source_row=next(r for r in case['records'] if r['version_ref']==ref)
                            projection['subjects'][ref]={'identity':contracts.ident(original[ref]),'version_ref':ref,
                                'kind':source_row['kind'],'effective_state':'candidate-unadmitted','record':original[ref]}
                    require(projection['subjects'][target]['kind']==gap['selected_carrier_semantic_kind'],'exact prospective target kind differs from audit')
                    require(any(c['semantic_kind']==gap['selected_carrier_semantic_kind'] for c in data['projection']['contracts'].values()),'signed catalog lacks selected carrier kind')
                    rejected=False;error=None
                    try:module.validate_relation(record,projection)
                    except Exception as exc:
                        rejected='endpoint identity/kind mismatch' in str(exc);error=str(exc)
                    require(rejected,'frozen runtime did not reproduce the exact diagnosed kind rejection')
                    rows.append({**gap,'observed_error':error,'expected_rejection_observed':True,
                        'prospective_target':next({'path':r['path'],'sha256':r['sha256']} for r in case['records'] if r['version_ref']==target),
                        'target_admission':'candidate-unadmitted; not an original signed Project instance',
                        'signed_source_posture':'independently replayed original catalog and relation contracts',
                        'candidate_endpoint_posture':'read-only unadmitted prospective subject overlay for both endpoints',
                        'transactions_applied':0,'actual_owner_outcome':None})
        finally:
            stage.cleanup()
            for key in list(sys.modules):
                if key==name or key.startswith(name+'.'):sys.modules.pop(key,None)
    require(len(rows)==2,'expected both current engineering and research kind mismatches')
    return {'result':'PASS','model_kind_closure':'FAIL','actual_rejections':rows,
        'signed_archive_sha256':expected_sha,'effects_dispatched':0,'actual_owner_outcome':None,
        'route':'O05 declared endpoint/carrier/schema reconciliation then fresh W07 completion proof'}
