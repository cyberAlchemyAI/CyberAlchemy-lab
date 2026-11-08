"""Materialize an acyclic native selection after actual independent core review."""
import argparse,json,hashlib,os
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

def selected(path,expected=None):
    raw=path.read_bytes()
    if expected:need(sha(raw)==expected,'EXTERNAL_EXPECTED_BYTES')
    return {'kind':'execution','root_id':'repo','relative_path':str(path.relative_to(R)),
            'sha256':sha(raw),'size_bytes':len(raw)}

def write(name,value):
    raw=canonical(value)
    with (U/name).open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return selected(U/name)

core_binding=selected(U/'native-policy-core-0005.json','02b59c252e4bd4f74bd850db549c0180146a2d4b497b646ad19ddd4d3dad65be')
core=json.loads((R/core_binding['relative_path']).read_bytes())
review_binding=selected(U/'reviewer-native-core-0005-interpretation-review-0001.json',
    '392de98d5e99513cd5927d8223d363186b21b1d40fb519e5b201c97d2dc50055')
review=json.loads((R/review_binding['relative_path']).read_bytes())
need(review['policy_core_digest']==core_binding['sha256'] and review['outcome']=='PASS' and
     review['author_identity']=='delivery_review' and review['reviewer_identity']=='/root/evidence_review',
     'ACTUAL_INTERPRETATION_REVIEW')
policy_binding=write('native-evaluation-policy-0002.json',{**core,'interpretation_review_binding':review_binding})
cut=write('native-evaluation-selection-0002.json',{'schema_version':'lab-evidence-index-evaluation-cut/v1',
    'purpose':'bounded inert evaluation of complete native original policy','runtime_family_selected':False,
    'actual_native_evidence_count':0,'policy_core_binding':core_binding,'authority_effect':'none'})
inventory_binding=selected(S/'evidence_index/original-inventory-selection.json',
    '58ec71d1651f0eccb6de349195dcacb718fec352886eddfeb0e1f2b2d26199c4')
inventory_selection=json.loads((R/inventory_binding['relative_path']).read_bytes())
bindings=[inventory_binding,policy_binding,review_binding,cut,*core['mapping_bindings']]+[
    d['binding'] for d in inventory_selection['documents']]
bindings=list({canonical(b):b for b in bindings}.values())
context=write('native-evaluation-context-0002.json',{'schema_version':'lab-eligibility-context/v1',
    'selection_binding':cut,'subject_bindings':[],'evidence_bindings':[],'review_enrollments':[],
    'policy_review_binding':review_binding,'policy_reviewer_identity':'/root/evidence_review',
    'policy_author_identity':'delivery_review','public_retention_bindings':bindings,
    'privacy_class':'reviewed-public-selector','task_subject_bindings':[]})
bindings.append(context)
proposal=U.parent/'LC-U01-02/dispatch-proposal-0002.json'
need(sha(proposal.read_bytes())=='478e5ab1966aabe8c758121d51543b8366d8eb38558da54b9c3405fda2346864',
     'INDEPENDENT_ROOT_PIN')
pin=next(r for r in json.loads(proposal.read_bytes())['roots'] if r['root_id']=='repository')
reader=AnchoredReader([RootAnchor('repo',pin['path'],pin['identity'])],bindings)
result=evaluate(reader,inventory_binding,policy_binding,context)
need(all(t['status']=='INELIGIBLE' for t in result.projection['tasks'].values()),'NO_NATIVE_TASK_PROOF')
need(all(a['candidate_status']=='PENDING' for a in result.projection['acceptance'].values()),'NO_NATIVE_AC_PROOF')
projection=write('native-current-projection-0002.json',result.projection)
retention_root=U/'retained-native-evaluation-0002';retention_root.mkdir(mode=0o700)
retained=persist(result,RootAnchor('retention',str(retention_root),identity(retention_root.stat())),
                 reader=reader,expected_disclosure=context,expected_inventory=inventory_binding,expected_policy=policy_binding)
summary={'schema_version':'lab-native-evaluation-artifacts/v1','policy_binding':policy_binding,
    'context_binding':context,'selection_binding':cut,'projection_binding':projection,
    'inventory_binding':inventory_binding,'review_binding':review_binding,
    'retained_originals':len(result.originals),'retained_original_bytes':sum(len(raw) for _,raw in result.originals),
    'projection_bytes':projection['size_bytes'],'retention':retained,
    'original_task_acceptance':False,'authority_effect':'none'}
write('native-evaluation-artifacts-0002.json',summary)
print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS','checks':7,
                  'effect_state':'owned-inert','cleanup':'retained-owned'}))
