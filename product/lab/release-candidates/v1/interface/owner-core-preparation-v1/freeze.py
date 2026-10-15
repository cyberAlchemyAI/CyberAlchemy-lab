"""Freeze owner original bytes, selected backend and scoped preparation source."""
import ast,importlib.metadata,json,platform
import prepare as C

def main():
    context=C.ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/context-R03-owner-core-preparation-0001.json';ctx=json.loads(context.read_bytes());assert ctx['strict_coverage']=='PASS' and not ctx['blockers'];rows={}
    def add(row):assert rows.get(row['path'],row)==row;rows[row['path']]=row
    for proof in [C.OWNER/'proof-0001.json',C.API/'source-manifest.json']:
        for r in json.loads(proof.read_bytes())['files']:add(r)
        add(C.bind(proof))
    add(C.bind(context))
    for r in ctx['source_bindings']:add(r)
    for path in C.HERE.glob('*.py'):ast.parse(path.read_bytes());add(C.bind(path))
    for r in rows.values():assert C.bind(C.ROOT/r['path'])==r,r['path']
    env={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')};assert env=={'python':'3.14.4','jsonschema':'4.23.0','cryptography':'46.0.5'}
    manifest={'schema_version':'lab-owner-core-preparation-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'environment':env,'context_binding':C.bind(context),'expected_tests':11,'expected_cores':42,'expected_scope_groups':21,'frozen_before_owned_effects':True,'authority_effect':'none','actual_owner_outcome':None,'task_complete':False}
    p=C.HERE/'source-manifest.json';p.open('xb').write(C.encoded(manifest));print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':C.bind(p)}))
if __name__=='__main__':main()
