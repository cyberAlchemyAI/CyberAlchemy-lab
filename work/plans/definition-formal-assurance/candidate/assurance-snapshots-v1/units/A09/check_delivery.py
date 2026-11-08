"""Verify sealed candidate/prior bytes and current binding after fresh replay."""
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;sys.path.insert(0,str(UNIT));import replay as a
import run_replay as h


def main():
    manifests={}
    for path in [a.BASE/'units/A08/delivery-manifest.json',UNIT/'delivery-manifest.json']:
        rows=json.loads(path.read_bytes())['files']
        if len({row['path'] for row in rows})!=len(rows):raise ValueError('Duplicate delivery identity')
        for row in rows:a.load_ref(row,{},False)
        manifests[path.relative_to(a.ROOT).as_posix()]=len(rows)
    receipt=json.loads((UNIT/'receipt.json').read_bytes())
    for row in receipt['inputs']+receipt['outputs']:a.load_ref(row,{},False)
    if receipt['unit_id']!='A09.1' or receipt['authority_effect']!='none' or receipt['goal_status']!='active' or receipt['test_count']!=36:raise ValueError('False unit/authority/completion boundary')
    evidence=json.loads((a.BASE/'pilot-v2/evidence.json').read_bytes());prepared=a.prepare();a.verify_bindings(prepared)
    if evidence['semantic_ready'] is not False or evidence['unbounded_conclusion'] is not None or evidence['whole_definition_proofs']!=0 or evidence['owner_review']!='pending-A10':raise ValueError('False owner/proof/readiness claim')
    if evidence['required_set_sha256']!=prepared['required']['required_set_sha256'] or {row['obligation_id'] for row in evidence['logical_results']}!=set(prepared['Q']) or len(evidence['logical_results'])!=11 or len(evidence['administrative_and_semantic_gates'])!=11:raise ValueError('Evidence obligation/gate denominator differs')
    coverage=a.load_ref(evidence['finite_coverage']['coverage_ref'],{});rows=[a.load_ref(ref,{}) for ref in evidence['finite_coverage']['range_refs']]
    if not a.r.same_json(a.merge(rows,prepared=prepared),coverage):raise ValueError('Sealed coverage differs from declared exact range union')
    positive=next(row for row in evidence['native_controls'] if row['case_id']=='positive');checked=a.verify_native(a.load_ref(positive['native_ref'],{}),positive['request'],prepared)
    stored=a.load_ref(positive['check_ref'],{})
    if not a.r.same_json(checked,stored) or any(row['strength']!='model-witness' for row in stored['queries']):raise ValueError('Sealed positive evidence no longer replays')
    fresh=a.load_ref(evidence['fresh_verification_ref'],{})
    if fresh['status']!='PASS' or fresh['fresh_range_replay'] is not True or fresh['range_configurations']!=9210 or fresh['range_runs']!=77:raise ValueError('Actual full fresh replay result missing')
    print(json.dumps({'status':'PASS','authority_effect':'none','delivery_manifests':manifests,'source_binding':a.types.bind_sources(prepared['spec'],a.ROOT),'tests':36,'independently_replayed_finite_baseline':8640,'freshly_replayed_baseline_and_stress':9210,'independently_checked_existential_witnesses':11,'pending_administrative_semantic_gates':11,'source_fidelity':'pending','semantic_dependency_closure':'unresolved','owner_accepted_whole_definition_translations':0,'whole_definition_proofs':0,'verification_scope':'Exact sealed bytes/prior-file preservation, current source/runtime and retained fresh-all-range evidence plus positive witness recheck; no new whole-source or owner-admission claim.','goal_status':'active','next_unit':'A10.1'},indent=2,sort_keys=True))


if __name__=='__main__':main()
