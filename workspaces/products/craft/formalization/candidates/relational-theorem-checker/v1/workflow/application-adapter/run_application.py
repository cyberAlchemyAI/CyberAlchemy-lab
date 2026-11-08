#!/usr/bin/env python3
"""Actual candidate review/application replay and reversible drift controls."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import tempfile
import time
import adapter as c
s=c.s;HERE=Path(__file__).resolve().parent


def main():
    cases=HERE/'cases';cases.mkdir(exist_ok=True)
    records=[]
    protected={row['path']:row['sha256'] for row in s.read(s.BASE/'replay/dependency-manifest.json')['dependencies']
               if row['path'].startswith('authority/')}
    def run(name,argv,code):
        print('Application case starting:',name,flush=True)
        metrics=cases/(name+'-metrics.txt');started=time.monotonic()
        result=subprocess.run(['/usr/bin/time','-f','elapsed_seconds=%e\npeak_rss_kib=%M','-o',str(metrics),
            str(HERE/'candidate-adapter'),*map(str,argv)],text=True,capture_output=True,timeout=1800)
        outcome=c.b.i.c.d.decode(result.stdout)
        s.require(result.returncode==code,f'{name}: expected {code}, got {result.returncode}: {result.stdout[:2500]} {result.stderr[-2000:]}')
        s.require(outcome['authority_effect']=='none' and outcome['human_authority_granted'] is False,'candidate result granted human authority')
        s.require('Traceback' not in result.stderr,'raw traceback exposed: '+name)
        if code==7:s.require(outcome['requires_fresh_review'] and not outcome['fresh_replay_performed'],'stale review did not require fresh checking')
        p=cases/(name+'-outcome.json');s.write(p,outcome)
        stderr=cases/(name+'-stderr.txt');stderr.write_text(result.stderr)
        measurements={}
        for line in metrics.read_text().splitlines():
            if '=' in line:
                key,value=line.split('=',1);measurements[key]=float(value)
        records.append({'name':name,'argv':list(map(str,argv)),'exit_code':code,'status':outcome['status'],
            'fresh_replay_performed':outcome['fresh_replay_performed'],'wall_seconds':time.monotonic()-started,
            'process_measurements':measurements,'outcome':s.binding(p),'stderr':s.binding(stderr),'result':'pass'})
        print('Application case passed:',name,code,flush=True);return outcome
    c.SHADOW.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='controlled-',dir=c.SHADOW) as folder:
        shadow=Path(folder);state=shadow/'state.json';probe=shadow/'input.txt'
        run('initialize',['init','--state',state],0)
        run('initialization-no-replace',['init','--state',state],2)
        probe.write_text('captured candidate source\n');value=s.read(state);value['source_inputs']=[s.binding(probe)];s.write(state,value)
        original=state.read_bytes();source_original=probe.read_bytes()
        before_snapshot=cases/'before-shadow-state.json';before_snapshot.write_bytes(original)
        proposal=s.BASE/'workflow/evidence/instance-only-proposal.json'
        bundle=s.BASE/'workflow/evidence/instance-only-bundle.json'
        result=run('full-review',['review',proposal,'--state',state,'--bundle',bundle],0)
        review=s.ROOT/result['review_record']['path'];saved_review=deepcopy(s.read(review))
        s.require(result['fresh_replay_performed'] and not result['review_result_reused'],'review evidence was not computed')
        app=['apply',review,'--proposal',proposal,'--state',state,'--bundle',bundle]
        probe.write_text('changed candidate source\n')
        run('actual-source-drift',app,7);s.require(state.read_bytes()==original,'source drift wrote application state')
        probe.write_bytes(source_original)
        drift=deepcopy(value);drift['epoch']+=1;s.write(state,drift)
        run('epoch-drift',app,7);state.write_bytes(original)
        drift=deepcopy(value);drift['snapshot']['graph']['nodes'][0]['content_identity']='candidate:changed-content'
        drift['baseline_identity']=c.g.c.identity(drift['snapshot']);s.write(state,drift)
        run('semantic-baseline-drift',app,7);state.write_bytes(original)
        substituted=['apply',review,'--proposal',s.BASE/'workflow/evidence/unchanged-proposal.json','--state',state,'--bundle',bundle]
        run('proposal-replay-substitution',substituted,7)
        other=cases/'substituted-bundle.json';bad=deepcopy(s.read(bundle));bad['policy_identity']='0'*64;s.write(other,bad)
        run('bundle-replay-substitution',['apply',review,'--proposal',proposal,'--state',state,'--bundle',other],7)
        forged=cases/'forged-review.json';bad=deepcopy(saved_review);bad['approved']=True;s.write(forged,bad)
        run('client-approval-flag',['apply',forged,'--proposal',proposal,'--state',state,'--bundle',bundle],2)
        bad=deepcopy(saved_review);bad['human_authority_granted']=True;s.write(forged,bad)
        run('client-human-authority-claim',['apply',forged,'--proposal',proposal,'--state',state,'--bundle',bundle],2)
        outcome_path=s.ROOT/saved_review['outcome']['path'];old_outcome=outcome_path.read_bytes()
        edited=s.read(outcome_path);edited['client_accepted']=True;s.write(outcome_path,edited)
        run('review-outcome-byte-substitution',app,7);outcome_path.write_bytes(old_outcome)
        live=s.ROOT/'authority/admissions/governance-transaction-surface/v1/registries/relation-kind-registry.json'
        run('authority-path-as-state-rejected',['apply',review,'--proposal',proposal,'--state',live,'--bundle',bundle],2)
        applied=run('full-application-replay',app,0)
        updated=s.read(state)
        s.require(applied['status']=='applied-to-shadow' and applied['fresh_replay_performed'] and not applied['review_result_reused'],'application reused review evidence')
        s.require(updated['epoch']==1 and updated['snapshot']==s.read(proposal)['after'],'actual shadow application did not contain checked candidate snapshot')
        old_paths={e['path'] for row in result['outcome']['results'] for e in row['evidence_refs']}
        new_paths={e['path'] for row in applied['outcome']['results'] for e in row['evidence_refs']}
        s.require(old_paths.isdisjoint(new_paths),'application evidence copied review receipt instead of fresh replay')
        after_snapshot=cases/'after-shadow-state.json';s.write(after_snapshot,updated)
        run('old-review-after-application',app,7)
        s.require(updated==s.read(state),'reused stale review modified applied state')
        # Save current generated review/application artifacts. Their captured mutable
        # state/probe bindings are historical observations, not claims of final currency.
        snapshot_files=[]
        for directory in [review.parent]:
            for p in directory.iterdir():
                if p.is_file():snapshot_files.append(s.binding(p))
        s.write(cases/'review-artifact-index.json',{'artifacts':snapshot_files,
            'mutable_inputs':'Historical observations; originals intentionally drifted and the temporary shadow was removed after testing.',
            'authority_effect':'none'})
    for path,digest in protected.items():s.require(s.digest(s.ROOT/path)==digest,'authority source bytes changed: '+path)
    s.write(HERE/'application-replay-controls.json',{'schema':'relational.application-controls/v1-candidate','result':'pass',
        'cases':records,'before_shadow_snapshot':s.binding(before_snapshot),'after_shadow_snapshot':s.binding(after_snapshot),
        'protected_authority_source_count':len(protected),'protected_source_identity':c.g.c.identity(protected),
        'validation_script':s.binding(Path(__file__)),'policy':s.binding(HERE/'adapter-policy.json'),
        'review_application_evidence_disjoint':True,'claim_ceiling':'Local candidate simulation with cooperative writer lock, full replay and explicit drift refusal; no authority or deployment.',
        'authority_effect':'none','human_authority_granted':False})
    print('R05 application controls passed:',len(records),'real boundary cases',flush=True)


if __name__=='__main__':main()
