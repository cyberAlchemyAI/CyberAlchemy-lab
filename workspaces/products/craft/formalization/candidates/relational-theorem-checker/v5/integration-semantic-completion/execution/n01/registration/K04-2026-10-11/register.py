"""One-time candidate evidence registration; never supplies semantic acceptance."""
from pathlib import Path
import hashlib, json, shutil

HERE=Path(__file__).resolve().parent
N=HERE.parent.parent
EXEC=N.parent
ROOT=next(p for p in HERE.parents if (p/'authority/artifact-types').is_dir())
def binding(path):
    return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def read(path):return json.loads(path.read_text())
def save(path,data):path.write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':
    index_path=N/'formal-preparation-index.json'
    seq_path=N/'sequential-review.json'
    plan_path=EXEC/'plan.json'
    index,seq,plan=read(index_path),read(seq_path),read(plan_path)
    progress=next(task for task in plan['tasks'] if task['id']=='N01')['progress']
    assert index['total_distinct_new_candidate_theorems']==seq['candidate_fragment_theorems']==progress['candidate_fragment_theorems']==1984
    assert not index.get('pending_review_preparations')
    assert seq['current_unit']=='K04' and seq['accepted_meaning_count']==4
    assert index['inherited_discharges']==seq['new_inherited_discharges']==progress['inherited_discharges']==0
    request=read(N/'K04-assessment-request.json')
    assert request['actual_response'] is None
    snapshots=HERE/'snapshots'
    snapshots.mkdir(exist_ok=False)
    archived=[]
    for source in [seq_path,plan_path,N/'decision-gate.json',N/'K04-assessment-request.json']:
        target=snapshots/source.name
        shutil.copy2(source,target)
        original=binding(source)
        assert binding(target)['sha256']==original['sha256']
        archived.append({'original_path':original['path'],'original_sha256':original['sha256'],'snapshot':binding(target)})
    history_path=HERE/'historical-context.json'
    save(history_path,{'schema':'relational.historical-verification-context/v1','snapshots':archived,
        'interpretation':'Exact verification-time context only; current state is validated separately.',
        'actual_assessed_meanings_at_capture':4,'pending_unit_at_capture':'K04',
        'inherited_discharges_at_capture':0,'authority_effect':'none'})
    packages=[]
    for name,count,filenames in [
        ('K04-draft',43,['LessonUseCandidate.lean','LessonUseControls.lean']),
        ('K04-source-adapter',9,['LessonBodyProfiles.lean','LessonSourceAdapter.lean','LessonSourceControls.lean'])]:
        package_dir=N/'formal'/name
        proof=read(package_dir/'verification.json')
        assert proof['inherited_discharges']==0 and not proof['N01_accepted']
        assert len(proof['theorems'])==count
        package={'unit':name,'kind':'relation.applies-lesson','theorems':count,
            'preparation_status':'candidate-prepared-before-meaning-assessment',
            'verification':binding(package_dir/'verification.json'),
            'component_completion':binding(package_dir/'component-completion.json'),
            'model_review':binding(package_dir/'MODEL-REVIEW.md'),
            'local_sources':[binding(package_dir/filename) for filename in filenames],
            'historical_context':binding(history_path),
            'actual_owner_assessment_supplied':False,'inherited_discharges':0,
            'complete_source_refinement':False,'complete_full_theory_countermodels':False}
        if name.endswith('source-adapter'):
            package.update(control_index=binding(package_dir/'control-index.json'),
                generation_audit=binding(package_dir/'generation-audit.json'),
                source_policy_gaps=binding(package_dir/'source-policy-gap-map.json'))
        packages.append(package)
    before=index['total_distinct_new_candidate_theorems']
    index.update(pending_review_preparations=packages,pending_review_candidate_theorems=52,
        total_distinct_new_candidate_theorems=before+52,
        pending_review_audit_driver=binding(HERE/'audit_registered.py'))
    seq.update(candidate_fragment_theorems=before+52,pending_review_candidate_theorems=52)
    current=next(unit for unit in seq['units'] if unit['unit']=='K04')
    assert current['actual_assessment'] is None
    current['pending_preparations']=[{'unit':package['unit'],'verification':package['verification'],
        'component_completion':package['component_completion'],'theorems':package['theorems'],
        'historical_context':package['historical_context']} for package in packages]
    progress.update(candidate_fragment_theorems=before+52,pending_review_candidate_theorems=52,
        pending_review_preparations=packages,pending_review_audit_driver=binding(HERE/'audit_registered.py'))
    driver=N/'check_current_review.py'
    source=driver.read_text()
    marker="    for preparation in index.get('payload_provider_preparations', []):"
    assert source.count(marker)==1
    audit_block='''    if index.get('pending_review_preparations'):
        import importlib.util
        audit_path = ROOT / index['pending_review_audit_driver']['path']
        spec = importlib.util.spec_from_file_location('registered_pending_review_audit', audit_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        declarations.extend(module.audit(ROOT, index['pending_review_preparations'], seq, progress, check))
        assert index['pending_review_candidate_theorems'] == 52
'''
    source=source.replace(marker,audit_block+marker)
    compile(source,str(driver),'exec')
    save(index_path,index);save(seq_path,seq)
    changed={str(path.relative_to(ROOT)) for path in [index_path,seq_path]}
    for value in progress.values():
        if isinstance(value,dict) and value.get('path') in changed:
            value.update(binding(ROOT/value['path']))
    save(plan_path,plan)
    driver.write_text(source)
    text_path=EXEC/'PROGRESS.md'
    text=text_path.read_text()
    phrase='making 1984 distinct verified candidate declarations in total.'
    assert text.count(phrase)==1
    text=text.replace(phrase,'and K04 preparation adds 43 model/control declarations and nine source-adapter declarations, making 2036 distinct verified candidate declarations in total.')
    text+='''

K04 candidate preparation registered before owner assessment

Two separately verified K04 packages add 52 distinct declarations. The first
has 15 general theorems and 28 kernel-checked worked controls for the synthetic
use/non-use profile, exact qualifier joins, evidence and precedence requirements,
conflict/override retention and qualified relation recording. The source adapter
adds nine general declarations, complete fixed bodies covering 55 fields/six
record types, and 279 runtime controls per compile/replay phase. Runtime controls
are not counted as additional theorems.

The immutable verification reports retain their verification-time context. Exact
archived snapshots preserve that context; the current review audit validates
current execution state separately. Registration supplies no actual assessment.
Only K00-K03 meanings are accepted; K04 and D01-D08 remain pending. Actual owned
token, assessment, precedence and evidence providers, complete source semantics,
full-theory countermodels, independent checking and downstream integration remain.
All 263 inherited IDs remain open and all 90 original discharges retain scope.
'''
    text_path.write_text(text)
    save(HERE/'registration.json',{'schema':'relational.candidate-preparation-registration/v1',
        'result':'registered-candidate-preparation','before_theorems':1984,'added_theorems':52,
        'after_theorems':2036,'packages':packages,'historical_context':binding(history_path),
        'registration_driver':binding(Path(__file__)),'current_audit_driver':binding(driver),
        'formal_preparation_index':binding(index_path),'sequential_review':binding(seq_path),
        'execution_plan':binding(plan_path),'progress':binding(text_path),
        'actual_assessed_meanings':4,'current_unit':'K04','inherited_discharges':0,
        'N01_accepted':False,'goal_complete':False,'authority_effect':'none'})
    print('Registered 52 K04 candidate declarations; 2036 total; zero inherited discharges.')
