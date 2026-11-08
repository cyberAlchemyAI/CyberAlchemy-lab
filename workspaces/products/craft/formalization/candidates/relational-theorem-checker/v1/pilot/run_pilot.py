#!/usr/bin/env python3
"""Representative candidate pilot with current predecessor evidence and fresh rule replay."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'workflow/cli'))
import runtime as c
from finalize_cli import verify_bindings
s=c.s


def main():
    s.require(s.task('R04')['status']=='accepted' and s.task('R05')['status']=='accepted','pilot prerequisites not accepted')
    cases=HERE/'cases';cases.mkdir(exist_ok=True)
    records=[]
    def run(name,argv,code):
        print('Pilot case starting:',name,flush=True)
        measurements=cases/(name+'-metrics.txt');started=time.monotonic()
        result=subprocess.run(['/usr/bin/time','-f','elapsed_seconds=%e\npeak_rss_kib=%M','-o',str(measurements),
            str(c.HERE/'cli'),*map(str,argv)],text=True,capture_output=True,timeout=1800)
        outcome=c.d.decode(result.stdout)
        s.require(result.returncode==code,f'{name}: expected {code}, got {result.returncode}: {result.stdout[:2000]} {result.stderr[-1500:]}')
        s.require('Traceback' not in result.stderr,'raw provider traceback exposed in pilot')
        proposal_path=argv[1] if argv[0]=='check-extension' else argv[argv.index('--proposal')+1]
        proposal=s.read(proposal_path);required=[x['id'] for x in c.g.generate(proposal)['obligations']]
        c.o.validate(outcome,required);verify_bindings(outcome)
        for row in outcome['results']:
            for binding in row['evidence_refs']:verify_bindings(s.read(s.ROOT/binding['path']))
        target=cases/(name+'-outcome.json');s.write(target,outcome)
        stderr=cases/(name+'-stderr.txt');stderr.write_text(result.stderr)
        observed={}
        for line in measurements.read_text().splitlines():
            if '=' in line:
                key,value=line.split('=',1);observed[key]=float(value)
        record={'name':name,'origin':'fresh R06 public CLI execution','argv':list(map(str,argv)),
            'exit_code':code,'outcome':s.binding(target),'stderr':s.binding(stderr),'wall_seconds':time.monotonic()-started,
            'process_measurements':observed,'before_graph':{'nodes':len(proposal['before']['graph']['nodes']),
                'assertions':len(proposal['before']['graph']['assertions'])},
            'after_graph':{'nodes':len(proposal['after']['graph']['nodes']),'assertions':len(proposal['after']['graph']['assertions'])},
            'obligation_count':len(required),'profile':outcome['profile_id'],'readiness':outcome['readiness'],'result':'pass'}
        records.append(record);print('Pilot case passed:',name,code,flush=True)
        return outcome

    # Preserve provenance: these are actual current prerequisite executions,
    # not claimed to be new measurements or independent human review.
    inherited=[]
    for task_id,path in [('R04',s.BASE/'workflow/cli/workflow-controls.json'),
                         ('R05',s.BASE/'workflow/application-adapter/application-replay-controls.json')]:
        controls=s.read(path);s.require(controls['result']=='pass','pilot prerequisite controls failed')
        for row in controls['cases']:
            c.v.safe_binding(row['outcome']);c.v.safe_binding(row['stderr'])
            inherited.append({**deepcopy(row),'origin':'accepted '+task_id+' execution; reused evidence, not a fresh measurement'})
    # Unsupported endpoint changes are included as negative coverage, not silently
    # promoted into a preservation profile that the existing theorem does not prove.
    widened=s.BASE/'evolution/proposals/pair-widening-proposal.json'
    run('endpoint-extension-unsupported',['check-extension',widened],3)
    rules=s.BASE/'workflow/evidence/rule-only-extension-proposal.json'
    bundle=s.BASE/'workflow/evidence/rule-only-extension-bundle.json'
    positive=run('complete-rule-change',['replay-evidence',bundle,'--proposal',rules],0)
    s.require(positive['readiness']=='ready-for-review' and len(positive['results'])==15,'full rule evidence incomplete')
    oldhead=deepcopy(s.read(rules));oldhead['proposal_id']='proposal:pilot-protected-old-head'
    oldhead['after']['rules'][0]['head']['predicate']='Admitted'
    bad=cases/'old-protected-head-proposal.json';s.write(bad,oldhead)
    run('protected-head-unsupported',['check-extension',bad],3)

    # A complete provider result without a checked witness stays unknown even
    # when every other required obligation passes the real public workflow.
    request=deepcopy(s.read(bundle));search=cases/'provider-search-result.json'
    s.write(search,{'schema':c.b.ROLE_SCHEMA['search-result'],'proposal_identity':c.g.c.identity(s.read(rules)),
        'provider_status':'completed','found':True,'accepted':True,'note':'Provider assertions only; no model witness.'})
    entry=next(x for x in request['obligations'] if x['name']=='independence-witnesses')
    entry.update(method='bounded-search',artifacts={'search-result':s.binding(search)})
    unresolved=cases/'unchecked-search-bundle.json';s.write(unresolved,request)
    unknown=run('search-without-checked-witness',['replay-evidence',unresolved,'--proposal',rules],4)
    s.require(unknown['readiness']=='unresolved' and any(r['evidence_method']=='bounded-search' and r['verdict']=='unknown' for r in unknown['results']),'unchecked provider flags became readiness')
    report={'schema':'relational.shadow-pilot/v1-candidate','machine_result':'pass','human_review':'pending',
        'fresh_cases':records,'accepted_predecessor_cases':inherited,
        'source_baseline':s.binding(s.BASE/'replay/dependency-manifest.json'),
        'rule_proposal':s.binding(rules),'validation_script':s.binding(Path(__file__)),
        'coverage':{'instance_addition':'R05 complete review and fresh application replay; actual added assertion in shadow state',
            'endpoint_extension':'Fresh negative; unsupported existing-pair widening does not inherit old-model guarantees',
            'kind_addition':'R04 fresh-kind complete public replay; R03 also checks empty-denotation new-kind carrier',
            'inference_rule_change':'Fresh complete 15-obligation replay with actual external proof and exact countermodel',
            'soundness_protected_boundaries':'Actual weak proof and invalid model controls in current R02/R03/R04; fresh old protected-head rejection',
            'workflow_failures':'Missing obligation, stale proof/bundle, source/epoch/baseline drift, client flags and complete unchecked-search scenario'},
        'measurement_scope':'Observed single runs on this host, some overlapping prerequisite validation. GNU time peak RSS is a process observation, not aggregate concurrent memory or a throughput guarantee.',
        'authority_effect':'none','human_authority_granted':False,
        'claim_ceiling':'Named captured candidate profiles only; business meaning, authentication, full inherited source semantics and deployment are not established by machine proof validity.'}
    s.write(HERE/'shadow-pilot-report.json',report)
    print('R06 machine pilot passed:',len(records),'fresh cases;',len(inherited),'current predecessor cases; human review pending',flush=True)


if __name__=='__main__':main()
