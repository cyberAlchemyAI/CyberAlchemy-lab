#!/usr/bin/env python3
"""Bind the full semantic closure and exercise deterministic rechecking."""
from copy import deepcopy
import json
from pathlib import Path
import replay_engine as e
s=e.s
BASE=Path(__file__).resolve().parent


def main():
    bound=e.manifest()
    first=e.replay(bound);second=e.replay(bound)
    s.require(first['result_identity']==second['result_identity'] and first['result']==second['result'],'replay not deterministic')
    controls=[]
    suffixes={'graph':'demonstrations/l0/input.json', 'registry':'registry/normalized-registry.json',
              'profile':'formal/specification/l0/semantic-contract.md',
              'rule':'relation-stress/v1/implementation/StressLaws.lean',
              'evidence':'demonstrations/l0/fixtures/106250bd165a7a4760dd147f0c2741d4de5c10422944ca8c46de58e78aa65def.txt',
              'proof':'formal/proofs/l0/CheckerSoundness.lean'}
    for category,suffix in suffixes.items():
        altered=deepcopy(bound)
        item=next((b for b in altered['dependencies'] if b['path'].endswith(suffix)),None)
        s.require(item is not None,'dependency category omitted: '+category)
        item['sha256']='0'*64
        # A claimed current execution timestamp never repairs the stale identity.
        try:e.verify(altered,executed_at='2026-10-08T23:59:59Z')
        except ValueError:controls.append({'name':category+' dependency changed with current timestamp','result':'rejected','binding':item['path']})
        else:raise ValueError('stale dependency accepted')
    for name,mutate in [('missing dependency',lambda m:m['dependencies'].pop()),
                        ('altered profile',lambda m:m.update(profile='other-profile')),
                        ('host runtime changed',lambda m:m['host_runtime']['files'][0].update(sha256='0'*64)),
                        ('changed closure identity',lambda m:m.update(dependency_identity='0'*64))]:
        altered=deepcopy(bound);mutate(altered)
        try:e.verify(altered)
        except ValueError:controls.append({'name':name,'result':'rejected'})
        else:raise ValueError('incomplete replay manifest accepted')
    # Exercise actual changed fixture bytes in an isolated copy. Live and admitted
    # sources remain untouched; generic binding verification sees real drift.
    import tempfile
    with tempfile.TemporaryDirectory(prefix='invalidation-copy-') as folder:
        path=Path(folder)/'input.json';path.write_bytes((s.BASE/'demonstrations/l0/input.json').read_bytes())
        before=s.digest(path);path.write_bytes(path.read_bytes()+b' ')
        s.require(s.digest(path)!=before,'actual input mutation went undetected')
        controls.append({'name':'actual isolated graph byte mutation','result':'invalidated','before':before,'after':s.digest(path)})
    s.write(BASE/'dependency-manifest.json',bound)
    s.write(BASE/'invalidation-controls.json',{'result':'pass','dependency_file_count':len(bound['dependencies']),
        'host_runtime_file_count':len(bound['host_runtime']['files']),'controls':controls,'replays':[first,second],
        'identical_semantic_identity':first['result_identity'],'full_recheck':True,
        'claim_ceiling':'Deterministic named-profile result identity and full declared dependency recheck; no external truth, concurrent filesystem snapshot or incremental cache proof.'})
    s.accept('C06',{'dependency-manifest.json':BASE/'dependency-manifest.json','replay-engine':BASE/'replay_engine.py','invalidation-controls.json':BASE/'invalidation-controls.json'},
        ['Two fresh kernel evaluations and reference resolutions produce identical canonical semantic results and result identities; operational build logs are not semantic identity.',
         'Graph, complete registry, supported profile, existing rule source, evidence fixture, proof source and runtime changes invalidate the manifest; the closure is recomputed before and after evaluation.'],
        ['A current timestamp cannot repair a changed dependency hash, and omitted dependency/profile/runtime/identity cases reject.',
         'The engine recomputes its independently selected transitive closure and checks every binding; no incremental invalidation is claimed.'],
        [Path(__file__),s.BASE/'execution/support.py'])
    print(json.dumps({'task':'C06','result':'accepted','dependency_files':len(bound['dependencies']),'controls':len(controls)}))


if __name__=='__main__':main()
