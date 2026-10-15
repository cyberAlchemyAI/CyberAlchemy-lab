"""Independent read-only public-byte/AST review; no candidate imports/effects."""
import ast,base64,collections,hashlib,json,stat
from pathlib import Path

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
RUN=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
P=RUN/'T32/migration-native-role-compatibility-preparation-0001'
V=RUN/'T32/native-lifecycle-recovery-adoption-0003'
ORIGINAL=ROOT/'implementation/lab-ontology/candidates/v1/migration/adapters'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding(path):
    raw=path.read_bytes()
    return {'path':str(path.relative_to(ROOT))if path.is_relative_to(ROOT)else str(path),'sha256':sha(raw),'size_bytes':len(raw)}
def methods(path,cls):
    tree=ast.parse(path.read_bytes());node=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name==cls)
    return {n.name:n for n in node.body if isinstance(n,ast.FunctionDef)}
def functions(path):return {n.name:n for n in ast.parse(path.read_bytes()).body if isinstance(n,ast.FunctionDef)}
def shape(n):return ast.dump(n,include_attributes=False)

def review():
    mfraw=(P/'source-manifest.json').read_bytes();assert sha(mfraw)=='f144f27effe46be3ff49f8e0462fc7e6ed0b23fa2c0f9d819d54c8021980899c'
    assert sha((P/'HANDOFF.json').read_bytes())=='e7fff3b03964e52b931c642492d8ae2c022947ae199a33258a54a9055861c845'
    mf=json.loads(mfraw);assert len(mf['files'])==220
    rows={}
    for row in mf['files']:
        path=Path(row['path']);path=path if path.is_absolute()else ROOT/path
        s=path.lstat();assert stat.S_ISREG(s.st_mode)and not path.is_symlink()
        raw=path.read_bytes();assert sha(raw)==row['sha256']
        if 'size_bytes'in row:assert len(raw)==row['size_bytes']
        if 'mode'in row:assert stat.S_IMODE(s.st_mode)==row['mode']
        assert str(path)not in rows;rows[str(path)]={'sha256':sha(raw),'observed_size_bytes':len(raw)}
    parent=json.loads((V/'source-manifest.json').read_bytes());assert len(parent['files'])==130
    for row in parent['files']:
        path=Path(row['path']);path=path if path.is_absolute()else ROOT/path
        assert rows[str(path)]['sha256']==row['sha256']
    original=methods(V/'postimages/migration.py','SourceTranslation');new=methods(P/'migration.py','SourceTranslation')
    assert len(original)==len(new)==10 and set(original)==set(new)
    same=[name for name in original if shape(original[name])==shape(new[name])]
    assert set(same)==set(original)-{'__init__','guard'}
    tests=methods(ORIGINAL/'test_import.py','ImportGuards');newtests=methods(P/'import_guards.py','ImportGuards')
    assert len([k for k in tests if k.startswith('test_')])==48
    assert all(shape(node)==shape(newtests[name])for name,node in tests.items()if name!='setUpClass')
    oldf=functions(V/'postimages/migration.py');newf=functions(P/'migration.py')
    for name in ('record_bytes','pointer','schema','semantic_draft','governance_draft'):assert shape(oldf[name])==shape(newf[name])
    oldscope=json.loads((ORIGINAL/'build-scope.json').read_bytes())
    assert sha((ORIGINAL/'build-scope.json').read_bytes())=='9f42e28db872ad237c0859d99614758e13c9016168c3c93704bb83fd3573b3ad'
    assert oldscope['native_executable']['sha256']=='480d421a438f712db930bb287d2ee1d5e4a0933e1336816defa28d6c284de9c3'
    assert "pin = translator.scope['native_executable']"in(V/'postimages/migration.py').read_text()
    # Evaluate only the actual final output isolation predicate extracted from
    # guard(), over path values. No module/contract/factory or directory exists.
    guard=methods(P/'execution_contract.py','MigrationExecutionContract')['guard']
    node=next(n for n in guard.body if isinstance(n,ast.Expr)and isinstance(n.value,ast.Call)
        and len(n.value.args)>1 and isinstance(n.value.args[1],ast.Constant)
        and n.value.args[1].value=='explicit distinct successor output root required')
    expr=ast.Expression(body=node.value.args[0]);ast.fix_missing_locations(expr)
    nested=Path(oldscope['output_root'])/'independent-owned-predicate-only-never-created'
    result=eval(compile(expr,str(P/'execution_contract.py'),'eval'),{'Path':Path,'output':nested,'s':{'output_root':str(nested)},'old':oldscope})
    assert result is True
    original_loader=functions(ORIGINAL/'check.py')['load_package']
    assert '.rglob('in ast.unparse(original_loader)
    archive_path=ROOT/'implementation/lab-ontology/candidates/v1/migration/candidate/0001/native.snapshot'
    archive=json.loads(archive_path.read_bytes());assert len(archive['files'])==176 and archive['semantic_cursor']==archive['governance_cursor']==88
    expected={};families={k:[]for k in ('semantic','governance')}
    for family in families:
        for i in range(1,89):
            name=f'{family}/{i:08d}-ontology-{family}:O05:{i}.json';entry=archive['files'][name]
            raw=base64.b64decode(entry['base64_original_bytes'],validate=True);assert sha(raw)==entry['sha256']
            event=json.loads(raw);assert event['event_family']==family and event[family+'_cursor']==i
            expected[name]=sha(raw);families[family].append(event)
    assert set(expected)==set(archive['files'])
    for sem,gov in zip(families['semantic'],families['governance']):
        assert gov['semantic_ref']=={'semantic_event_id':sem['event_id'],'semantic_event_digest':sem['event_digest'],'semantic_cursor':sem['semantic_cursor']}
    selection=json.loads((ROOT/oldscope['selection_binding']['path']).read_bytes());assert len(selection['items'])==140
    dispositions=collections.Counter(x['disposition']for x in selection['items']);assert dispositions['block']==9
    inputs=json.loads((P/'input-selection.json').read_bytes());assert len(inputs['inputs'])==90
    executor_binding={'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/ontology-installation-root-0001/execution-selection.json','sha256':'3b0c97b2b31363f6d344af10e2dde3281dbffb042a6746e67f0b9fe1795a3bf4'}
    eraw=(ROOT/executor_binding['path']).read_bytes();assert sha(eraw)==executor_binding['sha256'];execution=json.loads(eraw)
    assert execution['ontology_role']['sha256']=='57416d01d3479238f9e76a967c0275f1af04466efeb130fc0125bcb94e3a3399'
    assert execution['base_dependency_selection_binding']['sha256']=='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
    abi=execution['added_elf_graph']['bin/lab-ontology-native'];assert abi=={'needed':['ld-linux-x86-64.so.2','libc.so.6','libgcc_s.so.1'],'interpreter':'ld-linux-x86-64.so.2'}
    # Full package/candidate imports, actual guards, streams/native execution,
    # source-body reconstruction and original 48 tests are expressly not run.
    return {'result':'REVISION-REQUIRED-output-root-isolation','authority_effect':'none','all220_public_SHA_and_declared_size_mode_checks':'PASS',
        'all130_parent_path_SHA_rows_retained':True,'translator10_methods_retained':True,'translator8_identical_algorithms':same,
        'all48_original_hostile_test_ASTs_and_support_except_explicit_bootstrap_identical':True,'five_pure_draft_helpers_identical':True,
        'historical480_scope_and_strict_v3_preserved':True,'native574_selector_and_ABI_contract':execution['ontology_role'],
        'actual176_historical_event_byte_SHA_and_semantic_governance_tuple_checks':'PASS-metadata-only-not-native-sealing',
        'old_archive_binding':binding(archive_path),'source_items':140,'blocked_source_revisions':9,'dispositions':dict(dispositions),
        'non_effect_counterexample':{'actual_guard_expression':ast.unparse(node.value.args[0]),'path_value':str(nested),'accepted_by_actual_selected_predicate':result,
            'directory_or_candidate_effect_created':False,'consequence':'This accepted destination lies under the frozen original package. Publisher can create it, and original recursive load_package includes its new files, breaking original exact membership.'},
        'no_candidate_import_or_native_API_Source_installed_guard_installation_or_lease_execution':True,'new220_carrier_runtime_validation_or_176_native_compatibility_established':False,
        'input_files':rows}

if __name__=='__main__':print(json.dumps(review(),sort_keys=True))
