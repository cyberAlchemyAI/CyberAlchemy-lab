"""Read-only delivery/accounting check; does not infer theorem or source fidelity."""
import json
from pathlib import Path
import finalize as f

def main():
 manifest=json.loads((f.UNIT/'delivery-manifest.json').read_bytes());files=manifest['files']
 if len({row['path'] for row in files})!=len(files):raise ValueError('Duplicate delivery identity')
 for row in files:f.bound(row)
 receipt=json.loads((f.UNIT/'receipt.json').read_bytes())
 for row in receipt['inputs']+receipt['outputs']:f.bound(row)
 registry=f.checks.validate(f.checks.read());prior=f.checks.preserved(registry)
 report=json.loads((f.ROOT/receipt['validation']['actual_result_ref']['path']).read_bytes())
 if report['result']!='PASS' or len(report['control_results']['cases'])!=76 or receipt['goal_status']!='active' or receipt['semantic_ready'] is not False or receipt['authority_effect']!='none':raise ValueError('False completion or missing actual controls')
 print(json.dumps({'result':'PASS-for-sealed-E04-controls','candidate_files':len(files),'prior_candidate_files_preserved':prior,'executed_fixture_methods':76,'owner_fidelity':'pending','goal_status':'active','next_ready_unit':'I01.1'},indent=2,sort_keys=True))
if __name__=='__main__':main()
