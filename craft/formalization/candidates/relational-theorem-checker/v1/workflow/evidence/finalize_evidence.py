#!/usr/bin/env python3
"""Audit completed R03 controls and record bounded candidate task acceptance."""
from pathlib import Path
import aggregate as a
import schema_contract as sc
b=a.b;s=b.s;HERE=Path(__file__).resolve().parent


def verify_binding_tree(value):
 if isinstance(value,dict):
  if set(value)=={'path','sha256'}:b.v.safe_binding(value,limit=64*1024*1024)
  for child in value.values():verify_binding_tree(child)
 elif isinstance(value,list):
  for child in value:verify_binding_tree(child)


def main():
 s.require(s.task('R03')['status']=='not-started','R03 acceptance already recorded; do not overwrite accepted evidence')
 controls=s.read(HERE/'evidence-controls.json')
 s.require(controls['result']=='pass' and len(controls['controls'])>=22,'complete semantic, source, carrier and output-integrity controls missing')
 s.check_binding(controls['validation_script'])
 expected={'unchanged','instance-only','fresh-kind-extension','fresh-kind-empty-pairs','rule-only-extension'}
 s.require(set(controls['positive_full_profiles'])==expected,'missing full positive change profile')
 sc.main()
 paths={HERE/name for name in ['bundle-verifier','aggregate-verifier','evidence-controls.json',
  'aggregate.py','bundle_contract.py','semantic_replay.py','schema_contract.py','finalize_evidence.py',
  'run_evidence.py','run_transport_controls.py','bundle-policy.json','README.md','context-pack.json',
  'evidence-bundle-schema.json','scoped-model-schema.json','bounded-search-schema.json',
  'transport-controls.json','source-boundary-controls.json','builtin-rule-bundle.json','typed-witness-bundle.json',
  'captured-countermodel-evidence.json','case-countermodel-evidence.json','empty-pairs-source.json']}
 for name in expected:
  proposal=s.read(HERE/(name+'-proposal.json'));bundle=s.read(HERE/(name+'-bundle.json'));outcome=s.read(HERE/(name+'-result.json'))
  s.check_binding(controls['positive_full_profiles'][name]);b.validate_transport(proposal,bundle)
  a.o.validate(outcome,[row['id'] for row in b.g.generate(proposal)['obligations']])
  s.require(outcome['readiness']=='ready-for-review' and a.o.exit_code(outcome)==0,'positive profile no longer ready: '+name)
  verify_binding_tree(outcome)
  for row in outcome['results']:
   evidence=s.read(s.ROOT/row['evidence_refs'][0]['path']);verify_binding_tree(evidence)
   s.require(evidence['verdict']=='satisfied' and evidence['execution']=='completed','missing actual verified evidence: '+name)
   paths.add(s.ROOT/row['evidence_refs'][0]['path'])
   # Each complete replay owns its generated sources and fresh module audit.
   paths.update(p for p in (s.ROOT/row['evidence_refs'][0]['path']).parent.iterdir() if p.is_file())
  paths.update(HERE/(name+'-'+suffix+'.json') for suffix in ['proposal','bundle','result'])
 transport=s.read(HERE/'transport-controls.json')
 s.require(transport['result']=='pass' and len(transport['controls'])==11,'closed transport controls missing')
 rules=s.read(HERE/'rule-only-extension-proposal.json')
 b.validate_transport(rules,s.read(HERE/'builtin-rule-bundle.json'))
 b.validate_transport(rules,s.read(HERE/'typed-witness-bundle.json'))
 verify_binding_tree(controls)
 paths.add(HERE/'invalid-data-result.json')
 paths.update(p for p in (HERE/'targeted-controls').iterdir() if p.is_file())
 paths.add(HERE/'targeted-weak-proof.lean');paths.add(HERE/'targeted-malformed.json')
 s.accept('R03',{str(p.relative_to(HERE)):p for p in sorted(paths)},
  ['Full original-byte source/artifact, profile, graph, rule, verifier/runtime and proof dependencies are independently rechecked before and after actual replay. Five complete cases across four computed profiles have current verified evidence, including a valid empty-denotation fresh-kind carrier; real weak proofs, invalid scoped models and substitutions reject.',
   'All 9 or 15 independently required hard obligations are replayed and aggregated. Selected data, invariant preservation and registry-plus-rule model conservativity stay distinct; proof-only bindings and unchecked provider search flags cannot establish readiness.'],
  ['Twenty-two semantic/workflow/source/carrier/output-integrity controls and eleven transport controls cover omission, digest/policy substitution, staleness, method/role mismatch, actual wrong theorems/models, unsafe sources, empty-pair carriers, overwritten generated evidence, unsupported changes and unknown search. Observed module timeouts remained unknown before unchanged theorem statements were successfully rerun under a bounded local registry budget.',
   'Exact independently generated inventory, hard/scope flags and current policy are compared; client readiness/satisfied flags, missing server rows and weaker policies cannot authorize readiness.'],
  [s.BASE/'workflow/contracts/outcomes.py',s.BASE/'workflow/proof-verifier/verifier.py',s.BASE/'evolution/obligations/generator.py'])
 state=s.read(HERE/'session-state.json')
 state.update(execution='completed',candidate_acceptance='accepted',actual_semantic_evidence_replay_complete=True,
  readiness_aggregation_complete=True,remaining=[],verified_controls={'semantic':len(controls['controls']),'transport':11},
  verification_note='Five complete current cases across four computed profiles replayed; candidate task acceptance is author self-review. Human normative/usefulness review remains R06/G4.',goal_complete=False)
 s.write(HERE/'session-state.json',state)
 print('R03 accepted: five complete cases, twenty-two semantic/source/carrier/output and eleven transport controls')


if __name__=='__main__':main()
