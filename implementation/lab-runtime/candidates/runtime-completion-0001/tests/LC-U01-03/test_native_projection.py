"""Replay the selected real original policy; this supplies no native task evidence."""
import argparse,json,tempfile,shutil,os
from pathlib import Path
import sys
S=Path(__file__).absolute().parents[2];R=S.parents[3]
DEPS=R/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/deps'
sys.path[:0]=[str(S/'contracts'),str(S/'selectors'),str(S/'evidence_index'),str(DEPS)]
from lab_contracts.codec import canonical,sha,need
from lab_selectors.anchors import RootAnchor,AnchoredReader,identity
from lab_evidence.eligibility import evaluate
from lab_evidence.retention import persist

parser=argparse.ArgumentParser();parser.add_argument('--temp-root',required=True)
args=parser.parse_args();U=Path(args.temp_root)
need(U==R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-03','UNIT_ROOT')
# These literals select independently retained root and reviewed native inputs.
proposal=U.parent/'LC-U01-02/dispatch-proposal-0002.json'
need(not proposal.is_symlink() and sha(proposal.read_bytes())=='478e5ab1966aabe8c758121d51543b8366d8eb38558da54b9c3405fda2346864','ROOT_SELECTION')
pin=next(r for r in json.loads(proposal.read_bytes())['roots'] if r['root_id']=='repository')
root=RootAnchor('repo',pin['path'],pin['identity'])
def binding(name,digest,size):
    return {'kind':'execution','root_id':'repo','relative_path':str((U/name).relative_to(R)),
            'sha256':digest,'size_bytes':size}
summary_binding=binding('native-evaluation-artifacts-0002.json','4b98984179d0f8295665dcb5bcf24a26654bacf3b36c9417bfd4b2840e589f4e',12847)
reader=AnchoredReader([root],[summary_binding]);summary=json.loads(reader.read(summary_binding,max_bytes=65536))
context_binding=summary['context_binding'];reader=AnchoredReader([root],[context_binding])
context=json.loads(reader.read(context_binding,max_bytes=65536))
selected=[summary_binding,context_binding,summary['projection_binding'],*context['public_retention_bindings']]
reader=AnchoredReader([root],selected)
result=evaluate(reader,summary['inventory_binding'],summary['policy_binding'],context_binding)
need(canonical(result.projection)==reader.read(summary['projection_binding'],max_bytes=16*1024*1024),'NATIVE_EXACT_REPLAY')
need(len(result.projection['tasks'])==36 and all(t['status']=='INELIGIBLE' for t in result.projection['tasks'].values()),'NO_ORIGINAL_TASK_ACCEPTANCE')
need(len(result.projection['acceptance'])==13 and all(a['candidate_status']=='PENDING' for a in result.projection['acceptance'].values()),'NO_CANDIDATE_ACCEPTANCE')
need(len(result.originals)==summary['retained_originals'] and sum(len(raw) for _,raw in result.originals)==summary['retained_original_bytes'],'FULL_ORIGINAL_CAPTURE')
owned=Path(tempfile.mkdtemp(prefix='owned-index-native-',dir=U));anchor=RootAnchor('owned',str(owned),identity(owned.stat()))
try:
    persist(result,anchor,reader=reader,expected_disclosure=context_binding,
            expected_inventory=summary['inventory_binding'],expected_policy=summary['policy_binding'])
    bindings=[{'kind':'execution','root_id':'owned','relative_path':b['sha256']+'.original',
               'sha256':b['sha256'],'size_bytes':b['size_bytes']} for b,_ in result.originals]
    retained_reader=AnchoredReader([anchor],bindings)
    for b,(_,raw) in zip(bindings,result.originals):
        need(retained_reader.read(b,max_bytes=32*1024*1024)==raw,'EXACT_ORIGINAL_ROUNDTRIP')
finally:
    # Only this invocation's exclusively created fixture tree is removed.
    shutil.rmtree(owned)
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':5,
                  'effect_state':'owned-inert','cleanup':'clean'}))
