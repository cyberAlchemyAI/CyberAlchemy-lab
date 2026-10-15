"""Passive independent final-selector/inventory audit; no runtime imports."""
import ast
import hashlib
import json
import os
import stat
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN = 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/'
API = 'product/lab/release-candidates/v1/interface/api-integration-v17/'
OWN = RUN + 'T03/margin-software-manifest-preparation-0001/'
MODULES = ('service','workspace','auth','protocol','guard','session_attachment','current_context_sessions',
    'handlers','lesson_assessment','application_journal','observed_margin','margin_capture','margin_kernel','margin_seal')

def main():
    checks = []; selected = {}; entry = {}; bodies = {}; fd_start = len(os.listdir('/proc/self/fd'))
    def check(name, value):
        assert value, name
        checks.append(name)
    def capture(name, pin):
        absolute = ROOT / name; held = [os.open('/', os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)]
        try:
            for part in absolute.parts[1:-1]:
                held.append(os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=held[-1]))
            held.append(os.open(absolute.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=held[-1]))
            before = os.fstat(held[-1]); assert stat.S_ISREG(before.st_mode)
            chunks = []
            while raw := os.read(held[-1], 1024 * 1024): chunks.append(raw)
            raw = b''.join(chunks); after = os.fstat(held[-1])
            stamp = lambda s: (s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
            assert stamp(before) == stamp(after) and hashlib.sha256(raw).hexdigest() == pin
            for index, part in enumerate(absolute.parts[1:]):
                a = os.stat(part, dir_fd=held[index], follow_symlinks=False); b = os.fstat(held[index+1])
                assert (a.st_dev,a.st_ino,a.st_mode,a.st_uid,a.st_gid) == (b.st_dev,b.st_ino,b.st_mode,b.st_uid,b.st_gid)
            return raw, {'path':name,'sha256':pin,'size_bytes':len(raw),'mode':stat.S_IMODE(before.st_mode),
                'device':before.st_dev,'inode':before.st_ino}
        finally:
            for fd in reversed(held): os.close(fd)
    def select(binding):
        name, pin = binding['path'], binding['sha256']
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        if name in selected: assert selected[name] == pin; return bodies[name]
        raw, record = capture(name,pin); selected[name]=pin; entry[name]=record; bodies[name]=raw
        return raw
    def load(binding): return json.loads(select(binding))
    def ref(name,pin): return {'path':RUN+name,'sha256':pin}
    app_ref=ref('T02/selector-merge-0005/application-receipt.json','71877e214513ea86b1d963d5e48c2fb49577172ec37a1ececef19688948308f0')
    merge_ref=ref('T00/selector-merge-review-0005.json','b95f2e2f7660a247f45bef04499f28be35116c0f73837c218e7f1e870e73b146')
    input_ref=ref('T03/margin-software-manifest-preparation-0001/input-selection-0002.json','3d2ba1070c4e2e2093ffa3ca0677c43050ea45d229799392330c4a71cbc78620')
    software_ref=ref('T03/margin-software-manifest-preparation-0001/software-0002.json','5bdd8adba0ffd73ea2ab5121e6a52ce232c86bf398b1ed25c233b7f3bd3e9081')
    app=load(app_ref); merge=load(merge_ref); inputs=load(input_ref); software_raw=select(software_ref); software=json.loads(software_raw)
    old=load(ref('T03/margin-software-manifest-preparation-0001/input-selection.json','450ab74861b41caabde1b505b595c7b78c7197f93ed54ff0ba837c23763a1c7e'))
    check('exact16 inventory closed schema and no authority', set(software)=={'schema_version','authority_effect','files'} and software['authority_effect']=='none' and software['schema_version']=='lab-T03-observed-margin-software/v1-candidate')
    check('exact14 independently selected module names', set(inputs['module_bindings'])==set(MODULES))
    rows=[]
    for name in MODULES:
        row=inputs['module_bindings'][name]; check('true module origin:'+name,row['path']==API+name+'.py');select(row);rows.append(row)
    for key,path in [('policy_schema_binding',API+'observed-margin-policy.schema.json'),('assessment_method_binding','product/lab/release-candidates/v1/interface/lesson-assessment-v2-action-0148/preparation.py')]:
        row=inputs[key];check('true selected method/schema:'+key,row['path']==path);select(row);rows.append(row)
    check('exact16 ordered inventory from independent bindings', software['files']==sorted(rows,key=lambda r:r['path']) and len({r['path'] for r in rows})==16)
    check('exact deterministic inventory bytes',software_raw==(json.dumps(software,sort_keys=True,indent=2)+'\n').encode())
    changes=[name for name in MODULES if inputs['module_bindings'][name]!=old['module_bindings'][name]]
    check('oldselection only currentContext module changes',changes==['current_context_sessions'])
    check('old schema/assessment bindings unchanged', all(inputs[k]==old[k] for k in ['policy_schema_binding','assessment_method_binding']))
    check('final input bound same exact Root merge review',inputs['merge_review_binding']==merge_ref)
    check('Root merge tied exact application',merge['selector_application_binding']==app_ref)
    check('Root merge tied exact currentContext inventory',merge['postselector_current_context_binding']==inputs['module_bindings']['current_context_sessions'])
    for key in ['actual_family_selection_binding','runtime_selection_binding','independent_reviews']:
        check('Rootmerge/application binding correspondence:'+key,merge[key]==app[key])
    family=load(app['actual_family_selection_binding']); descriptor=load(app['runtime_selection_binding']); overlay=load(app['overlay_binding'])
    check('descriptor/overlay exact family bindings',descriptor['actual_family_selection_binding']==app['actual_family_selection_binding'] and overlay['descriptor_binding']==app['runtime_selection_binding'])
    check('all9 family native metadata bindings',len(family['family_bindings'])==9 and all(descriptor[k]==v for k,v in family['family_bindings'].items()))
    for row in family['family_bindings'].values():select(row)
    for row in app['independent_reviews']:
        review=load(row);check('independent prior peer PASS and no findings:'+row['path'],review['result'].startswith('PASS') and not review.get('findings'))
    check('exact5 selector targets before and after',len(app['rows'])==len(overlay['rows'])==5 and app['changed_files']==4 and app['unchanged_files']==1)
    before=load({'path':RUN+'T02/selector-merge-0005/before-selection.json','sha256':hashlib.sha256((ROOT/(RUN+'T02/selector-merge-0005/before-selection.json')).read_bytes()).hexdigest()})
    check('retained before table equals selected overlay',before['rows']==overlay['rows'])
    selector_modes=[]
    for applied, staged in zip(app['rows'],overlay['rows']):
        target=applied['target']; pre=select(applied['preimage']); post=select(staged['postimage']); actual=select(applied['actual']); snapshot=select(staged['snapshot'])
        check('selector exact target/hash links:'+target,target==staged['original']['path']==applied['actual']['path'] and applied['preimage']['sha256']==staged['original']['sha256'])
        check('selector exact reviewed before/after bytes:'+target,pre==snapshot and actual==post and applied['changed']==(pre!=post))
        mode_before=entry[applied['preimage']['path']]['mode'];mode_actual=entry[target]['mode']
        check('selector original mode retained:'+target,mode_before==mode_actual and applied['mode_preserved'] is True)
        selector_modes.append({'target':target,'preimage_mode':mode_before,'actual_mode':mode_actual,'changed':applied['changed']})
    margin=load(merge['prior_margin_merge_binding']); marginapp=load(margin['application_receipt']); marginselection=load(marginapp['overlay_selection'])
    check('Root prior margin receipt exact independently selected 8 targets',len(marginapp['actual_target_bindings'])==len(marginselection['targets'])==8)
    margin_modes=[]
    for actualrow, staged in zip(marginapp['actual_target_bindings'],marginselection['targets']):
        actual=select(actualrow);post=select(staged['staged_binding']);component=select(staged['component_postimage_binding'])
        check('all8 unchanged margin applied bytes:'+actualrow['path'],actual==post==component and actualrow['path']==staged['target'])
        prior=staged['prior_binding']
        if prior:
            select(prior);check('prior margin original mode retained:'+actualrow['path'],entry[prior['path']]['mode']==entry[actualrow['path']]['mode'])
        margin_modes.append({'path':actualrow['path'],'actual_mode':entry[actualrow['path']]['mode'],'prior_mode':entry[prior['path']]['mode'] if prior else None})
    writer=select({'path':OWN+'build.py','sha256':'d9e1cf1afe2df1094101f80447cc918f9f14c6bdfb7eb28b817f7e178ec335eb'})
    def literal(raw,name):
        node=next(n for n in ast.parse(raw).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets))
        return ast.literal_eval(node.value)
    check('writer exact14 module contract',literal(writer,'MODULES')==MODULES)
    check('runtime margin exact14 module contract',literal(bodies[API+'observed_margin.py'],'MODULES')==MODULES)
    check('writer does not import original Lab/runtime APIs',all(not (isinstance(n,ast.ImportFrom) and n.level) for n in ast.walk(ast.parse(writer))))
    oldsource=select({'path':API+'source-manifest.json','sha256':'e41772f7478253fa2ede056afaa08461a962cc2e1063e541f5f2921f7ebe1195'})
    oldprofile=select({'path':API+'contract-profile.json','sha256':'5c62fe3a14da4499e3a1b08be62b759b322b68e959cc4914e2e0225f94f4a714'})
    prebase=RUN+'T02/composite-merge-preparation-0004/preimage/'
    check('old API source/profile bytes preserved',oldsource==select({'path':prebase+'source-manifest.json','sha256':hashlib.sha256(oldsource).hexdigest()}) and oldprofile==select({'path':prebase+'contract-profile.json','sha256':hashlib.sha256(oldprofile).hexdigest()}))
    oldpins={r['path']:r['sha256'] for r in json.loads(oldsource)['files']}; mismatches=[]
    for row in app['rows']:
        name=row['target']
        if name in oldpins and oldpins[name]!=selected[name]:mismatches.append(name)
    check('historical API manifest currently ineligible after actual selectors',len(mismatches)>=4 and merge['current_API_capture_invalid_until_successor_freeze'] is True)
    exit_rows={name:capture(name,pin)[1] for name,pin in selected.items()}
    check('all passive held byte/physical entry exit identities unchanged',entry==exit_rows)
    check('FD delta zero',len(os.listdir('/proc/self/fd'))==fd_start)
    report={'schema_version':'lab-T03-independent-selector-software-review-controls/v1','result':'PASS','checks':checks,'check_count':len(checks),'entry':list(entry.values()),'exit':list(exit_rows.values()),'FD_delta':0,'software_binding':software_ref,'input_binding':input_ref,'Root_merge_binding':merge_ref,'application_binding':app_ref,'selector_modes':selector_modes,'margin_modes':margin_modes,'old_manifest_selector_mismatches':mismatches,'runtime_or_native_or_current_guard_imports':False,'authority_effect':'none','task_complete':False}
    with (ROOT/(OWN+'independent-review-controls-0002.json')).open('x') as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'entry','exit','checks','selector_modes','margin_modes'}}))

if __name__=='__main__':main()
