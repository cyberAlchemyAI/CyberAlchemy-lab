#!/usr/bin/env python3
"""Audit real CLI controls, current evidence and exact R04 deliverables."""
from pathlib import Path
import runtime as c
s=c.s;HERE=Path(__file__).resolve().parent


def verify_bindings(value):
    if isinstance(value,dict):
        if set(value)=={'path','sha256'}:c.v.safe_binding(value,limit=64*1024*1024)
        for child in value.values():verify_bindings(child)
    elif isinstance(value,list):
        for child in value:verify_bindings(child)


def main():
    s.require(s.task('R04')['status']=='not-started','R04 already accepted; do not overwrite')
    controls=s.read(HERE/'workflow-controls.json')
    expected={'f0-instance','f0-semantic-failure','unsupported-instance-meaning','strict-json-failure',
        'missing-proposal-context','outside-workspace-input','exact-proof','actual-weak-proof','proof-freshness-failure',
        'registry-structure','registry-structure-failure','ci-extension','ci-single-check-not-review',
        'replay-fresh-kind','extension-semantic-failure','unsupported-extension','replay-freshness-failure',
        'ci-stale-failure','omitted-mandatory-check'}
    s.require(controls['result']=='pass' and {r['name'] for r in controls['cases']}==expected and len(controls['cases'])==len(expected),'missing real workflow controls')
    c.v.safe_binding(controls['validation_script'])
    current=c.current_adapter();paths={HERE/name for name in ['cli','ci-example','runtime.py','ci.py','cli-policy.json',
        'README.md','context-pack.json','run_cli.py','finalize_cli.py','workflow-controls.json']}
    paths.update(p for p in (HERE/'cases').iterdir() if p.is_file())
    dependencies=set()
    run_documents=[(p,s.read(p)) for p in (HERE/'runs').glob('*/outcome.json')]
    for record in controls['cases']:
        c.v.safe_binding(record['outcome']);c.v.safe_binding(record['stderr'])
        outcome=s.read(s.ROOT/record['outcome']['path'])
        args=c.parser().parse_args(record['argv']) if record['name']!='missing-proposal-context' else None
        if args and outcome['results']:
            if args.command in ['check-extension','replay-evidence']:
                proposal,_=c.read_input(args.input if args.command=='check-extension' else args.proposal)
                required=[x['id'] for x in c.g.generate(proposal)['obligations']]
            elif args.command=='check-proof':required=[s.read(args.input)['obligation_id']]
            else:required=[s.digest(args.input)+':instance-validity']
        elif args and args.command in ['check-extension','replay-evidence']:
            proposal,_=c.read_input(args.input if args.command=='check-extension' else args.proposal)
            required=[x['id'] for x in c.g.generate(proposal)['obligations']]
        else:required=[]
        c.o.validate(outcome,required)
        if record['name']=='ci-single-check-not-review':s.require(record['exit_code']==4 and c.o.exit_code(outcome)==0,'CI inferred extension readiness')
        else:s.require(c.o.exit_code(outcome)==record['exit_code'],'recorded failure exit inconsistent')
        matches=[p for p,value in run_documents if value==outcome]
        s.require(matches,'public outcome has no owned execution record: '+record['name'])
        run=matches[-1].parent;request=s.read(run/'request-bindings.json')
        if request['adapter'] is not None:s.require(request['adapter']==current,'case used a different CLI runtime/export closure')
        for bound in request['requests']:c.v.safe_binding(bound,limit=4*1024*1024)
        paths.update(p for p in run.iterdir() if p.is_file())
        verify_bindings(outcome)
        for row in outcome['results']:
            for bound in row['evidence_refs']:
                p=s.ROOT/bound['path'];evidence=s.read(p);verify_bindings(evidence)
                if not p.is_relative_to(HERE):dependencies.update(q for q in p.parent.iterdir() if q.is_file())
    s.accept('R04',{str(p.relative_to(HERE)):p for p in sorted(paths)},
        ['Nineteen real CLI/CI cases exercise all four commands, both instance profiles, valid extension/replay/proof evidence and actual semantic, proof, source-currentness and transport failures. Owned outcomes and exact required inventories were audited against the current accepted exports.',
         'Semantic diagnostics name the offending relation kind and assertion, exact failed obligation, input location and corrective action. Invalid inputs return one JSON outcome, and proof rejection is distinguished from mathematical refutation.'],
        ['CI runs the local checker and requires independently complete completed/current review readiness. Actual successful single-check execution returns CI code 4; process failure and inconsistent stale readiness cannot pass.',
         'Wrong relation versions, actual weak proofs, stale proofs/bundles, unsupported meanings/changes and omitted hard obligations all return nonzero exits and never readiness.'],
        sorted(dependencies))
    print('R04 accepted: nineteen real four-command CLI/CI cases')


if __name__=='__main__':main()
