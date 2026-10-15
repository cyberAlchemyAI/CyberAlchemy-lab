#!/usr/bin/env python3
"""Exercise real public CLI/CI paths, diagnostic failures and scoped evidence."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import tempfile
import time
import runtime as c
import ci
s=c.s; HERE=Path(__file__).resolve().parent


def main():
    cases=HERE/'cases';cases.mkdir(exist_ok=True)
    records=[]
    def save(name, value):
        p=cases/(name+'.json');s.write(p,value);return p
    def run(name, argv, code, ready=None, launcher='cli', trusted=None):
        print('CLI case starting:',name,flush=True)
        metrics=cases/(name+'-metrics.txt');started=time.monotonic()
        result=subprocess.run(['/usr/bin/time','-f','elapsed_seconds=%e\npeak_rss_kib=%M','-o',str(metrics),
            str(HERE/launcher),*map(str,argv)],text=True,capture_output=True,timeout=1800)
        outcome=c.d.decode(result.stdout)
        s.require(result.returncode==code,f'{name}: expected {code}, got {result.returncode}: {result.stdout[:2500]} {result.stderr[-2000:]}')
        s.require('Traceback' not in result.stderr,'raw traceback leaked: '+name)
        c.o.validate(outcome,trusted if trusted is not None else outcome['required_hard_obligation_ids'])
        if ready is not None:s.require(outcome['readiness']==ready,'wrong readiness: '+name)
        stdout=cases/(name+'-outcome.json');s.write(stdout,outcome)
        stderr=cases/(name+'-stderr.txt');stderr.write_text(result.stderr)
        measurements={}
        for line in metrics.read_text().splitlines():
            if '=' in line:
                key,value=line.split('=',1);measurements[key]=float(value)
        records.append({'name':name,'launcher':launcher,'argv':list(map(str,argv)),'exit_code':result.returncode,
            'execution':outcome['execution'],'currentness':outcome['currentness'],'readiness':outcome['readiness'],
            'obligation_count':len(outcome['required_hard_obligation_ids']),'wall_seconds':time.monotonic()-started,
            'process_measurements':measurements,'outcome':s.binding(stdout),'stderr':s.binding(stderr),'result':'pass'})
        print('CLI case passed:',name,result.returncode,flush=True);return outcome

    good=s.BASE/'input/example-addition.json'
    oid=s.digest(good)+':instance-validity'
    run('f0-instance',['check-instance',good],0,'not-applicable',trusted=[oid])
    invalid=deepcopy(s.read(good));invalid['graph']['assertions'][0]['qualifiers']['exact_version_ref']='wrong-version'
    bad=save('wrong-target-version',invalid)
    result=run('f0-semantic-failure',['check-instance',bad],1,'not-applicable',trusted=[s.digest(bad)+':instance-validity'])
    diag=next(x for x in result['diagnostics'] if x['code']=='wrong-target-version')
    s.require('relation.conforms-to' in diag['message'] and 'relation:conforms' in diag['location'] and diag['obligation_id'] and diag['next_action'],'diagnostic omitted offending relation, obligation or corrective action')
    run('unsupported-instance-meaning',['check-instance',good,'--profile','full-source-semantics/v1'],3,'not-applicable')
    malformed=cases/'duplicate.json';malformed.write_text('{"schema":1,"schema":2}')
    run('strict-json-failure',['check-instance',malformed],2,'not-applicable',trusted=[])
    run('missing-proposal-context',['check-proof',malformed],2,'not-applicable',trusted=[])
    with tempfile.TemporaryDirectory(prefix='cli-outside-') as folder:
        outside=Path(folder)/'input.json';outside.write_bytes(good.read_bytes())
        run('outside-workspace-input',['check-instance',outside],2,'not-applicable',trusted=[])

    proposal=s.BASE/'workflow/evidence/rule-only-extension-proposal.json'
    submitted=s.BASE/'workflow/proof-verifier/examples/derivation-submission.json'
    run('exact-proof',['check-proof',submitted,'--proposal',proposal],0,'not-applicable',trusted=[s.read(submitted)['obligation_id']])
    weak_source=cases/'weak.lean';weak_source.write_text('import DerivationSoundness\ntheorem submitted : True := True.intro\n')
    weak=save('weak-proof',c.v.make_submission(s.read(proposal),'derivation-soundness',weak_source,'submitted'))
    failed=run('actual-weak-proof',['check-proof',weak,'--proposal',proposal],1,'not-applicable',trusted=[s.read(weak)['obligation_id']])
    s.require(failed['results'][0]['verdict']=='violated' and 'does not disprove' in failed['diagnostics'][0]['next_action'],'proof rejection mislabeled theorem falsity')
    stale=deepcopy(s.read(submitted));stale['dependencies']['trusted_source_bindings'][0]['sha256']='0'*64
    stale_path=save('stale-proof',stale)
    run('proof-freshness-failure',['check-proof',stale_path,'--proposal',proposal],7,'not-applicable',trusted=[stale['obligation_id']])

    registry=save('registry-input',{'schema_version':'relational-checker.registry-instance-input/v1-candidate','graph':c.g.c.baseline()['graph']})
    run('registry-structure',['check-instance',registry,'--profile',c.STRUCTURE],0,'not-applicable',trusted=[s.digest(registry)+':instance-validity'])
    bad_registry=deepcopy(s.read(registry));bad_registry['graph']['assertions'][0]['kind_version']='v-wrong'
    bad_registry=save('bad-registry-input',bad_registry)
    run('registry-structure-failure',['check-instance',bad_registry,'--profile',c.STRUCTURE],1,'not-applicable',trusted=[s.digest(bad_registry)+':instance-validity'])

    unchanged=s.BASE/'workflow/evidence/unchanged-proposal.json';bundle=s.BASE/'workflow/evidence/unchanged-bundle.json'
    required=[x['id'] for x in c.g.generate(s.read(unchanged))['obligations']]
    passed=run('ci-extension',['check-extension',unchanged,'--bundle',bundle],0,'ready-for-review',launcher='ci-example',trusted=required)
    run('ci-single-check-not-review',['check-instance',good],4,'not-applicable',launcher='ci-example',trusted=[oid])
    fresh=s.BASE/'workflow/evidence/fresh-kind-extension-proposal.json';fresh_bundle=s.BASE/'workflow/evidence/fresh-kind-extension-bundle.json'
    run('replay-fresh-kind',['replay-evidence',fresh_bundle,'--proposal',fresh],0,'ready-for-review',trusted=[x['id'] for x in c.g.generate(s.read(fresh))['obligations']])
    invalid_proposal=deepcopy(s.read(unchanged));invalid_proposal['proposal_id']='proposal:cli-semantic-invalid'
    invalid_proposal['after']['graph']['assertions'][0]['qualifiers']['exact_version_ref']='wrong-version'
    invalid_path=save('invalid-extension',invalid_proposal)
    broken=run('extension-semantic-failure',['check-extension',invalid_path],1,'blocked',trusted=[x['id'] for x in c.g.generate(invalid_proposal)['obligations']])
    s.require(any(x['code']=='wrong-target-version' and x['obligation_id'] and 'relation.conforms-to' in x['message'] for x in broken['diagnostics']),'extension diagnostics omitted precise semantic cause')
    widened=s.BASE/'evolution/proposals/pair-widening-proposal.json'
    run('unsupported-extension',['check-extension',widened],3,'blocked',trusted=[x['id'] for x in c.g.generate(s.read(widened))['obligations']])
    stale_bundle=deepcopy(s.read(bundle));stale_bundle['dependencies']['bindings'][0]['sha256']='0'*64
    stale_bundle=save('stale-bundle',stale_bundle)
    run('replay-freshness-failure',['replay-evidence',stale_bundle,'--proposal',unchanged],7,'unresolved',trusted=required)
    run('ci-stale-failure',['check-extension',unchanged,'--bundle',stale_bundle],7,'unresolved',launcher='ci-example',trusted=required)
    missing_bundle=deepcopy(s.read(bundle));missing_bundle['obligations'].pop();missing=save('missing-obligation',missing_bundle)
    run('omitted-mandatory-check',['check-extension',unchanged,'--bundle',missing],2,'unresolved',trusted=required)
    s.require(not ci.review_ready(passed,required,1),'CI process failure passed semantic gate')
    altered=deepcopy(passed);altered['currentness']='stale'
    try:ci.review_ready(altered,required,0)
    except ValueError:pass
    except c.g.c.jsonschema.ValidationError:pass
    else:raise ValueError('inconsistent ready/stale outcome passed schema')
    s.write(HERE/'workflow-controls.json',{'schema':'relational.cli-controls/v1-candidate','result':'pass',
        'cases':records,'adapter_policy':s.binding(HERE/'cli-policy.json'),'validation_script':s.binding(Path(__file__)),
        'controls':['Zero exit from single checks cannot authorize CI review.', 'Process failure cannot pass an otherwise ready outcome.',
                    'Completed/current/schema-valid independently complete semantic evidence is required.',
                    'Actual weak proof, wrong relation version, unsupported meaning, stale bytes and omitted hard checks reject.'],
        'authority_effect':'none','review':'Codex author self-review; human pilot review remains pending'})
    print('R04 workflow controls passed:',len(records),'real CLI/CI cases',flush=True)


if __name__=='__main__':main()
