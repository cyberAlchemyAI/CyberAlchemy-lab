"""Public metadata and AST only. No installed payload/Source/native guard."""
import ast,hashlib,json,stat
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def parse(p):return json.loads(p.read_bytes())
def main():
    assert sha((P/'HANDOFF.json').read_bytes())=='b3a93307d61c14b793c54ebf9fcc5ff2c90db1b926bf43b121ca4b1e98cbd98f'
    assert sha((P/'source-manifest.json').read_bytes())=='e20a8410c6e27a070afd80faa557b464eff376a42ebfdbbd2dc4d8ca2b650270'
    mf=parse(P/'source-manifest.json');assert len(mf['files'])==16
    def physical():
        rows=[]
        for r in mf['files']:
            p=ROOT/r['path'];s=p.lstat();raw=p.read_bytes()
            assert stat.S_ISREG(s.st_mode)and not p.is_symlink()and sha(raw)==r['sha256']and len(raw)==r['size_bytes']
            rows.append({'path':r['path'],'sha256':sha(raw),'size_bytes':len(raw),'observed_mode':stat.S_IMODE(s.st_mode)})
        return rows
    before=physical()
    original=ROOT/'product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/control.py'
    a=ast.parse(original.read_bytes());b=ast.parse((P/'control.py').read_bytes())
    fun=lambda tree:{n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,ast.FunctionDef)}
    af=fun(a);bf=fun(b);assert len(af)==15 and af.keys()==bf.keys()and {n for n in af if af[n]!=bf[n]}=={'installed'}
    nonfun=lambda tree:[ast.dump(n,include_attributes=False)for n in tree.body if not isinstance(n,ast.FunctionDef)and not(isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ROOT'for t in n.targets))]
    assert nonfun(a)==nonfun(b)
    scope=parse(P/'full-proof-scope.json')
    base=parse(ROOT/scope['original_base_selection_binding']['path']);extension=parse(ROOT/scope['original_extension_selection_binding']['path'])
    assert sha((ROOT/scope['original_base_selection_binding']['path']).read_bytes())==scope['original_base_selection_binding']['sha256']
    assert sha((ROOT/scope['original_extension_selection_binding']['path']).read_bytes())==scope['original_extension_selection_binding']['sha256']
    expected={r['destination']:{'sha256':r['sha256'],'size_bytes':r['size_bytes'],'mode':0o755 if r['kind']in{'interpreter','native-executable'}else 0o644}for r in base['inputs']}
    expected.update(base['wheel_members']);expected['lib/abi/ld-linux-x86-64.so.2']['mode']=0o755
    assert len(expected)==1010 and len(base['inputs'])==720 and len(base['elf_graph'])==77
    for r in extension['added_inputs']:
        assert r['destination']not in expected
        expected[r['destination']]={k:r[k]for k in('sha256','size_bytes','mode')}
    assert expected==scope['expected_files']and len(expected)==scope['expected_files_count']==1011
    encoded=(json.dumps(expected,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    assert sha(encoded)==scope['expected_files_sha256']=='ce376a6d9b2c8b02653eb2f0cdfbb9f143be9ad4c5b1322007d9b79dc00c1952'
    assert scope['additional_exact_inventory_member']=='installation.json'and scope['historical_missing_inputs']==25
    adoption=parse(P/'ADOPTION.json');assert adoption['active']is False and adoption['actual_new_executor_selection_binding']is None
    after=physical();assert before==after
    return {'result':'PASS-scoped-static','authority_effect':'none','all16_entry_exit_rows':before,'all14_other_functions_AST_identical':True,'top_level_only_ROOT_changed':True,'full_expected1011_metadata_exact':True,'expected_files_sha256':sha(encoded),'original_base_inputs':720,'original_base_ELF_rows':77,'original_base_payloads':1010,'ontology_addition':1,'separate_receipt_inventory_member':'installation.json','actual1011_payloads_or_native_Source_ABI_guards_executed':False,'candidate_adoption_active':False}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
