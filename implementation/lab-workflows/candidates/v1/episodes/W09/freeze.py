"""Freeze the prospective executable source closure before domain effects."""
from control import *
def freeze():
    s=selection();files={r['path']:r for r in s['source_files']}
    paths=list(HERE.glob('*.py'))+[HERE/'DESIGN.md',SELECTION_PATH]
    paths+=list(SELECTION_PATH.parent.rglob('*'))
    paths+=list((PACKAGE/'schemas').glob('*.json'))+list((PACKAGE/'design').glob('*.json'))
    paths+=list((PACKAGE/'authority').glob('*.py'))+list((PACKAGE/'learning').glob('*.py'))+list((PACKAGE/'tools').glob('*.py'))
    paths+=list((PACKAGE/'examples/engineering').glob('*.py'))+list((PACKAGE/'examples/research').glob('*.py'))
    paths+=list((PACKAGE/'tests').glob('*.py'))+list((PACKAGE/'receipts/action-boundaries').glob('*.py'))
    for p in paths:
        if p.is_file() and '__pycache__' not in p.parts:files[str(p.relative_to(ROOT))]=bind(p)
    for r in files.values():original(r)
    manifest={'schema_version':'lab-W09-source-selection/v1-candidate','task':'W09','authority_effect':'none','actual_owner_outcome':None,
        'selection_binding':bind(SELECTION_PATH),'files':list(sorted(files.values(),key=lambda r:r['path'])),
        'native_executable_binding':s['native_executable_binding'],'domain_execution_started':False,'canonical_effects_applied':0,
        'claim_ceiling':'Pre-effect executable/input provenance; not an admission or completion receipt.'}
    dest=HERE/'attempts/0001/source-manifest.json';emit(dest,manifest);print(encoded({'result':'PASS','source_manifest':bind(dest),'files':len(files)}).decode(),end='')
if __name__=='__main__':freeze()
