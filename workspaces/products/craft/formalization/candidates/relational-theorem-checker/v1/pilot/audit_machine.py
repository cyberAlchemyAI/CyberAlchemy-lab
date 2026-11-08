#!/usr/bin/env python3
"""Audit actual pilot inventories, scoped evidence and negative outcomes."""
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'workflow/cli'))
import runtime as c
from finalize_cli import verify_bindings
s=c.s


def main():
    report=s.read(HERE/'shadow-pilot-report.json')
    s.require(report['machine_result']=='pass','machine pilot did not pass')
    c.v.safe_binding(report['validation_script'])
    expected={'endpoint-extension-unsupported':3,'complete-rule-change':0,
              'protected-head-unsupported':3,'search-without-checked-witness':4}
    s.require(len(report['fresh_cases'])==4 and {r['name'] for r in report['fresh_cases']}==set(expected),'missing fresh pilot scenario')
    evidence=set();audited=[]
    for row in report['fresh_cases']:
        s.require(row['exit_code']==expected[row['name']],'incorrect observed pilot exit')
        c.v.safe_binding(row['outcome']);c.v.safe_binding(row['stderr'])
        outcome=s.read(s.ROOT/row['outcome']['path'])
        args=c.parser().parse_args(row['argv'])
        proposal,_=c.read_input(args.input if args.command=='check-extension' else args.proposal)
        required=[x['id'] for x in c.g.generate(proposal)['obligations']]
        c.o.validate(outcome,required);s.require(c.o.exit_code(outcome)==expected[row['name']],'pilot exit differs from semantic outcome')
        verify_bindings(outcome)
        for item in outcome['results']:
            for bound in item['evidence_refs']:
                path=s.ROOT/bound['path'];verify_bindings(s.read(path))
                evidence.update(p for p in path.parent.iterdir() if p.is_file())
        if row['name']=='complete-rule-change':
            s.require(len(outcome['results'])==15 and all(r['verdict']=='satisfied' for r in outcome['results']) and outcome['readiness']=='ready-for-review','rule pilot is incomplete')
        if row['name']=='search-without-checked-witness':
            pending=[r for r in outcome['results'] if r['verdict']!='satisfied']
            s.require(len(pending)==1 and pending[0]['obligation_id'].endswith(':independence-witnesses') and
                pending[0]['evidence_method']=='bounded-search' and pending[0]['verdict']=='unknown','search case hid another unresolved obligation')
            s.require(outcome['readiness']=='unresolved' and outcome['execution']=='completed' and outcome['currentness']=='current','unchecked search misreported failure or currency')
        audited.append({'name':row['name'],'exit_code':row['exit_code'],'required_obligations':len(required),
            'satisfied':sum(r['verdict']=='satisfied' for r in outcome['results']),
            'outcome':row['outcome'],'result':'pass'})
    s.require(len(report['accepted_predecessor_cases'])==33,'predecessor pilot coverage missing')
    for row in report['accepted_predecessor_cases']:
        c.v.safe_binding(row['outcome']);c.v.safe_binding(row['stderr'])
    # Current accepted receipts bind these prior executions; candidate state
    # bindings inside adapter reports are explicitly historical observations.
    for tid in ['R04','R05']:
        receipt=s.read(s.ROOT/s.task(tid)['validation']['acceptance_ref']['path'])
        for item in receipt['artifacts']+receipt['dependency_bindings']:
            c.v.safe_binding({'path':item['path'],'sha256':item['sha256']},limit=64*1024*1024)
    s.write(HERE/'machine-validation-audit.json',{'schema':'relational.pilot-machine-audit/v1-candidate','result':'pass',
        'fresh_cases':audited,'predecessor_cases':33,'generated_evidence_dependencies':[s.binding(p) for p in sorted(evidence)],
        'validation_script':s.binding(Path(__file__)),'human_review':'pending','authority_effect':'none'})
    print('Pilot machine audit passed: 15 satisfied rule obligations; 14 satisfied plus exact unknown witness in search case')


if __name__=='__main__':main()
