"""Select the unchanged twelve export cases plus two actual lookup probes."""
import ast
import hashlib
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api58-export-checks-v2';NEW=BASE/'api59-export-checks-v1';API=BASE/'api-v59'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def tests(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not NEW.exists();NEW.mkdir()
    shutil.copyfile(OLD/'fixture.py',NEW/'fixture.py')
    text=(OLD/'tests.py').read_text()
    extra='''    def test_13_unknown_operation_inspection_preserves_empty_workspace(self):
        host,_,selected=self.example();before=self.files(selected)
        self.assertFalse((host.vault.root/'.lock').exists())
        request=F.MF.call(host.channel.context,'operation.inspect',selected['plan']['source_cut'],
            lookup={'operation':'package.export','idempotency_key':F.KEY})
        reply=self.invoke(host,request)
        self.assertEqual(reply['kind'],'error',reply)
        self.assertEqual(reply['message']['code'],'not-found')
        self.assertEqual(self.files(selected),before)
        self.assertFalse((host.vault.root/'.lock').exists())
    def test_14_missing_journal_lock_is_not_recreated_on_retry(self):
        host,request,selected=self.example();self.published(host,request,selected)
        (host.vault.root/'.lock').unlink();before=self.files(selected)
        request['call_id']='call:package-export:missing-lock:'+uuid.uuid4().hex
        reply=self.invoke(host,request)
        self.assertEqual(reply['kind'],'error',reply)
        self.assertEqual(reply['message']['code'],'integrity-failed')
        self.assertEqual(self.files(selected),before)
        self.assertFalse((host.vault.root/'.lock').exists())

'''
    needle="if __name__=='__main__':unittest.main()";assert text.count(needle)==1
    (NEW/'tests.py').write_text(text.replace(needle,extra+needle))
    assert all(tests(NEW/'tests.py')[n]==v for n,v in tests(OLD/'tests.py').items())
    runner=(OLD/'checks.py').read_text().replace("api-v58","api-v59").replace("_cal_API58_package_export_","_cal_API59_package_export_")
    runner=runner.replace("names=['test_01_controlled_native_candidate_export_with_original_source_proofs',\n            'test_02_admitted_source_root_preserves_independent_original_basis',\n            'test_03_exact_retry_reads_one_generation_without_redispatch']",
        "names=['test_05_caller_cannot_replace_selected_privacy_review',\n            'test_06_caller_cannot_omit_dependency_closure',\n            'test_13_unknown_operation_inspection_preserves_empty_workspace',\n            'test_14_missing_journal_lock_is_not_recreated_on_retry']")
    runner=runner.replace('expected=3','expected=4').replace('expected=12','expected=14')
    runner=runner.replace("'original_inherited_methods_retained':293","'original_inherited_methods_retained':305,'original_export_methods_unchanged':12")
    (NEW/'checks.py').write_text(runner)
    rows=[bind(NEW/n) for n in ('fixture.py','tests.py','checks.py')]
    rows.extend(bind(p) for p in (API/'source-manifest.json',API/'contract-profile.json',OLD/'source-manifest.json',OLD/'tests.py',Path(__file__).resolve()))
    with (NEW/'source-manifest.json').open('x') as f:json.dump({'schema_version':'lab-selected-qualification-source/v1-candidate',
        'files':rows,'original_export_method_count':12,'original_export_methods_unchanged':True,
        'added_lookup_cases':2,'authority_effect':'none','actual_runtime_qualified':False},f,indent=2,sort_keys=True);f.write('\n')
    print(json.dumps({'result':'AUTHORED-QUALIFICATION','check_source_binding':bind(NEW/'source-manifest.json'),
        'focused_cases':4,'full_cases':14,'unchanged_original_export_methods':12}),flush=True)
if __name__=='__main__':main()
