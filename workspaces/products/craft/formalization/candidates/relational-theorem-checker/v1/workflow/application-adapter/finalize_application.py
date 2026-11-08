#!/usr/bin/env python3
"""Audit candidate application boundary evidence without treating history as currency."""
from pathlib import Path
import adapter as c
s=c.s;HERE=Path(__file__).resolve().parent


def verify_semantic_tree(value):
    if isinstance(value,dict):
        if set(value)=={'path','sha256'}:c.v.safe_binding(value,limit=64*1024*1024)
        for child in value.values():verify_semantic_tree(child)
    elif isinstance(value,list):
        for child in value:verify_semantic_tree(child)


def main():
    s.require(s.task('R05')['status']=='not-started','R05 already accepted; do not overwrite')
    controls=s.read(HERE/'application-replay-controls.json')
    expected={'initialize','initialization-no-replace','full-review','actual-source-drift','epoch-drift',
        'semantic-baseline-drift','proposal-replay-substitution','bundle-replay-substitution','client-approval-flag',
        'client-human-authority-claim','review-outcome-byte-substitution','authority-path-as-state-rejected',
        'full-application-replay','old-review-after-application'}
    s.require(controls['result']=='pass' and {r['name'] for r in controls['cases']}==expected and len(controls['cases'])==14,'incomplete real application boundary controls')
    c.v.safe_binding(controls['validation_script']);c.current_adapter()
    paths={HERE/name for name in ['candidate-adapter','adapter.py','adapter-policy.json','README.md',
        'run_application.py','finalize_application.py','application-replay-controls.json','context-pack.json']}
    paths.update(p for p in (HERE/'cases').iterdir() if p.is_file())
    dependencies=set();by_name={}
    documents=[(p,s.read(p)) for p in (HERE/'runs').glob('*/adapter-outcome.json')]
    for row in controls['cases']:
        c.v.safe_binding(row['outcome']);c.v.safe_binding(row['stderr'])
        result=s.read(s.ROOT/row['outcome']['path']);by_name[row['name']]=result
        s.require(result['authority_effect']=='none' and result['human_authority_granted'] is False,'application output grants authority')
        if row['exit_code']==7:s.require(result['requires_fresh_review'] and result['status']=='fresh-check-required','drift allowed stale review reuse')
        matches=[p for p,value in documents if value==result];s.require(matches,'missing actual adapter execution artifact')
        paths.update(p for p in matches[-1].parent.iterdir() if p.is_file())
        if 'outcome' in result:
            outcome=result['outcome'];proposal=s.read(s.BASE/'workflow/evidence/instance-only-proposal.json')
            required=[x['id'] for x in c.g.generate(proposal)['obligations']]
            c.o.validate(outcome,required);s.require(c.o.exit_code(outcome)==0,'positive application semantic replay incomplete')
            verify_semantic_tree(outcome)
            for item in outcome['results']:
                for binding in item['evidence_refs']:
                    p=s.ROOT/binding['path'];verify_semantic_tree(s.read(p))
                    dependencies.update(q for q in p.parent.iterdir() if q.is_file())
    reviewed=by_name['full-review'];applied=by_name['full-application-replay']
    s.require(reviewed['fresh_replay_performed'] and applied['fresh_replay_performed'] and not applied['review_result_reused'],'missing full application rechecking')
    s.require(applied['status']=='applied-to-shadow' and applied['new_epoch']==1,'shadow application failed')
    before=s.read(s.ROOT/controls['before_shadow_snapshot']['path']);after=s.read(s.ROOT/controls['after_shadow_snapshot']['path'])
    s.require(len(after['snapshot']['graph']['assertions'])==len(before['snapshot']['graph']['assertions'])+1,'actual added assertion absent from applied candidate state')
    protected={row['path']:row['sha256'] for row in s.read(s.BASE/'replay/dependency-manifest.json')['dependencies'] if row['path'].startswith('authority/')}
    s.require(c.g.c.identity(protected)==controls['protected_source_identity'],'protected source inventory changed')
    for path,digest in protected.items():s.require(s.digest(s.ROOT/path)==digest,'authority source bytes changed')
    s.accept('R05',{str(p.relative_to(HERE)):p for p in sorted(paths)},
        ['Fourteen real boundary cases capture current source/state/epoch identities, refuse stale or substituted reviews and run all nine hard checks again at application. Review and application evidence directories are distinct; the shadow snapshot contains the actually checked added assertion.',
         'Shadow application changes only the explicit candidate snapshot. All outputs retain authority_effect none, human_authority_granted false and no reused review evidence; human assessment and admission remain separate.'],
        ['Actual simulation-source byte drift, epoch and semantic-baseline changes, proposal/bundle substitution and altered review bytes reject with a fresh-check requirement. Historical mutable-input bindings are observations; immutable before/after snapshots document what was tested.',
         'State paths are restricted to the candidate shadow directory, initialization refuses replacement, and a supplied authority path cannot become state. All captured authority source bytes remain identical. The cooperative lock and local-filesystem claim ceiling are explicit.'],
        sorted(dependencies))
    print('R05 accepted: fourteen actual review/application boundary cases')


if __name__=='__main__':main()
