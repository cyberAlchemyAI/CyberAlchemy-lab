"""Compare every inherited test-method AST to the API53 predecessor."""
import ast, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
API53=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v53-t16-challenge-source-0001'
API61=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v61-t16-abi423-bridge-0001'
INVENTORY=ROOT/'implementation/lab-runtime/local-host/t16-api49-provisional-regression-0001/INVENTORY-0001.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
cache={}

def node(root,identity):
    filename,method=identity.split(':',1)
    classname,name=method.rsplit('.',1)
    key=(str(root),filename)
    if key not in cache:cache[key]=ast.parse((root/filename).read_text())
    classes=[n for n in cache[key].body if isinstance(n,ast.ClassDef) and n.name==classname]
    if len(classes)!=1:raise ValueError('class not exact: '+identity)
    methods=[n for n in classes[0].body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name]
    if len(methods)!=1:raise ValueError('method not exact: '+identity)
    return ast.dump(methods[0],include_attributes=False)

def main():
    inventory=json.loads(INVENTORY.read_bytes())
    ids=[identity for rows in inventory['buckets'].values() for identity in rows]
    if len(ids)!=len(set(ids)) or len(ids)!=345:raise ValueError('inherited selection differs')
    changed=[identity for identity in ids if node(API53,identity)!=node(API61,identity)]
    files=sorted({identity.split(':',1)[0] for identity in ids})
    changed_files=[name for name in files if sha(API53/name)!=sha(API61/name)]
    result={'schema_version':'lab-T16-inherited-method-AST-comparison/v1-candidate',
            'predecessor_source_sha256':sha(API53/'source-manifest.json'),
            'successor_source_sha256':sha(API61/'source-manifest.json'),
            'inventory_sha256':sha(INVENTORY),'selected_method_count':345,
            'changed_method_asts':changed,'changed_whole_test_files':changed_files,
            'setup_and_helper_retarget_disclosure':{
                'test_challenge_api.py':'Two hard-coded current-family ID literals in setUpClass changed for the new signed family.',
                'test_preparation_corrected.py':'One hard-coded current-family ID literal in a helper changed for the new signed family.'},
            'result':'PASS-METHOD-ASTS-IDENTICAL' if not changed else 'FAIL-METHOD-AST-DRIFT',
            'whole_test_files_identical':not changed_files,
            'full_regression_passed':False,'authority_effect':'none'}
    target=Path(__file__).resolve().parent/'METHOD-AST-COMPARISON-0001.json'
    target.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'result':result['result'],'method_count':len(ids),
                      'changed_method_count':len(changed),'changed_whole_test_files':changed_files,
                      'receipt':str(target),'sha256':sha(target)},sort_keys=True))
    if changed:raise SystemExit(1)

if __name__=='__main__':main()
