"""Prepare stable portable API code; host manifests are generated at install.

No source/profile qualification is claimed until the trusted bootstrap has
selected and verified a complete per-install Source/Context and ABI binding.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = ROOT/'product/lab/release-candidates/v1/interface/api-integration-v73-t15-learning-selector-0001'
NEW = BASE.parent/'api-integration-v74-portable-inputs-0001'
LOGICAL = NEW
T03 = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T03/local-lifecycle-actual-clock-0001'
POST = T03/'cross-host-application-postimages-0001'
SOURCE = '5127caa2d6a829303f12af398912eeb98bb2b52580af40614e4925080224f4e7'
sha = lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(value, reason):
    if not value:
        raise ValueError(reason)


def once(text,before,after):
    need(text.count(before)==1,'portable merge seam differs: '+before[:90])
    return text.replace(before,after,1)


def assignment(text,name,expression):
    nodes = [node for node in ast.parse(text).body if isinstance(node,ast.Assign)
             and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)
             and node.targets[0].id==name]
    need(len(nodes)==1,'portable input assignment differs: '+name)
    node = nodes[0]
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:node.lineno-1])+name+' = '+expression+'\n'+''.join(lines[node.end_lineno:])


def configured_import(text):
    nodes = ast.parse(text).body
    position = 0
    for node in nodes:
        if ((isinstance(node,ast.Expr) and isinstance(node.value,ast.Constant) and isinstance(node.value.value,str))
            or (isinstance(node,ast.ImportFrom) and node.module=='__future__')):
            position = node.end_lineno
        else:
            break
    lines = text.splitlines(keepends=True)
    return ''.join(lines[:position])+'from . import runtime_selection as PORTABLE\n'+''.join(lines[position:])


def methods(folder):
    result = {}
    for path in [*folder.glob('test_*.py'),*folder.glob('run_*checks.py')]:
        for cls in ast.parse(path.read_text()).body:
            if isinstance(cls,ast.ClassDef):
                for node in cls.body:
                    if isinstance(node,ast.FunctionDef) and node.name.startswith('test_'):
                        result[path.name+':'+cls.name+'.'+node.name] = ast.dump(node,include_attributes=False)
    return result


def main():
    os.umask(0o077)
    need(not NEW.exists() and sha(BASE/'source-manifest.json')==SOURCE,'portable code stage exists or predecessor differs')
    for row in json.loads((BASE/'source-manifest.json').read_bytes())['files']:
        need(sha(ROOT/row['path'])==row['sha256'],'selected code constructor input changed: '+row['path'])
    original = methods(BASE)
    need(len(original)==345,'original inherited inventory differs')
    shutil.copytree(BASE,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc','receipts'))
    for name in ('source-manifest.json','contract-profile.json','rebind-receipt.json'):
        (NEW/name).unlink()
    post_pins = {'auth.py':'f0c34322074fcb1cd6e3c7fc139359571987a50c73c1712c7970e5836df669de',
                 'current_legacy_context_sessions.py':'9614ac28994bdb8c61c2ffd90bc2655522a0bb53d27a7a6d5bf8c53e111b3834',
                 'session_attachment.py':'8882e621a69a406de91a156883f7f04a1a0a922aad5c57ae1be687b241693330',
                 'observed_margin.py':'43224208abc27b24c02ace861ec1c1fbac6baf5a84bb310f18e06c1c026d0472'}
    for name,pin in post_pins.items():
        need(sha(POST/name)==pin,'reviewed cross-host callback postimage changed')
        shutil.copyfile(POST/name,NEW/name)
    shutil.copyfile(HERE/'api_runtime_selection.py',NEW/'runtime_selection.py')
    for path in NEW.glob('*.py'):
        if not (path.name.startswith('test_') or path.name.startswith('run_')):
            path.write_text(path.read_text().replace('lesson-application-v7-t03-derived-effect-0001',
                                                   'lesson-application-v8-t03-scope-custody-0001'))
    path = NEW/'guard.py'
    text = configured_import(path.read_text())
    text = once(text,"ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')",'ROOT = PORTABLE.ROOT')
    text = once(text,'    path = HERE / \'source-manifest.json\'',
        "    PORTABLE.guard()\n    expected = PORTABLE.binding('api.source')\n    if expected != {'path':str((HERE/'source-manifest.json').relative_to(ROOT)),'sha256':pin}:\n        raise ValueError('API source differs from trusted private installation selection')\n    path = HERE / 'source-manifest.json'")
    needle='    actual_helpers = set()'
    component_paths = ('implementation/lab-runtime/local-host/t25-integrated-runtime-0004/installed_selection.py',
        'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/native_install.py',
        'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/child_bootstrap.py',
        'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python')
    text = once(text,needle,'    helper_paths |= set('+repr(tuple(sorted(component_paths)))+')\n'+needle)
    path.write_text(text)
    path = NEW/'source_bridge.py'
    text = configured_import(path.read_text())
    text = once(text,'ROOT=legacy.ROOT',"ROOT=PORTABLE.ROOT\nrequire_root = legacy.require\nrequire_root(legacy.ROOT==ROOT,'portable legacy reader root differs from installed code')")
    fields = {
        'CURRENT_LEGACY_NAME':"PORTABLE.value('identity.source_name')",
        'CURRENT_SOURCE8_NAME':"'completion-current-participation:'+PORTABLE.value('identity.family')",
        'CURRENT_LEGACY_STORE':"PORTABLE.value('identity.store')",
        'CURRENT_SOURCE8_STORE':"PORTABLE.value('identity.store')",
        'CURRENT_LEGACY_CONTEXT':"str(Path(PORTABLE.binding('family.context_source')['path']).parent)",
        'CURRENT_SOURCE8_CONTEXT':"str(Path(PORTABLE.binding('family.context_source')['path']).parent)",
        'CURRENT_LEGACY_READER':"str(Path(PORTABLE.binding('family.reader_source')['path']).parent)",
        'CURRENT_SOURCE8_READER':"str(Path(PORTABLE.binding('family.reader_source')['path']).parent)",
        'CURRENT_LEGACY_SOURCE':"str(Path(PORTABLE.binding('family.source')['path']).parent)",
        'CURRENT_SOURCE8_SOURCE':"str(Path(PORTABLE.binding('family.source')['path']).parent)",
        'CURRENT_LEGACY_DELIVERY_PIN':"PORTABLE.binding('family.context_source')['sha256']",
        'CURRENT_SOURCE8_DELIVERY_PIN':"PORTABLE.binding('family.context_source')['sha256']"}
    for name,expression in fields.items():
        text = assignment(text,name,expression)
    old_profile="ROOT/'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/engine-v3/runtime/profile.json'"
    need(text.count(old_profile)==2,'portable current engine-profile paths differ')
    text = text.replace(old_profile,"ROOT/PORTABLE.binding('engine.profile')['path']")
    text = text.replace('_cal_api73_','_cal_api74_')
    path.write_text(text)
    for name in ('current_legacy_context_sessions.py','current_context_sessions.py'):
        path = NEW/name
        text = configured_import(path.read_text())
        text = assignment(text,'DELIVERY_PIN',"PORTABLE.binding('family.context_source')['sha256']")
        text = assignment(text,'MAPPING_PIN',"PORTABLE.binding('family.mapper_package')['sha256']")
        path.write_text(text)
    path = NEW/'native_dispositions.py'
    text = configured_import(path.read_text())
    for name,slot in [('SOURCE_PACKAGE','family.source_package'),('MAPPED_PACKAGE','family.mapper_package'),('MAPPING','family.mapping')]:
        text = assignment(text,name,"ROOT / PORTABLE.binding('"+slot+"')['path']")
        text = assignment(text,name+'_SHA',"PORTABLE.binding('"+slot+"')['sha256']")
    logical = "ROOT / 'implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d/context'"
    need(text.count(logical)==2,'portable disposition current-family paths differ')
    text = text.replace(logical,"ROOT / source.CURRENT_LEGACY_CONTEXT")
    path.write_text(text)
    path = NEW/'legacy_fixture_selection.py'
    text = configured_import(path.read_text())
    for name,expression in {
        'PUBLIC_SOURCE_NAME':"PORTABLE.value('identity.source_name')",
        'EXPECTED_NOT_BEFORE':"PORTABLE.value('period.not_before')",
        'EXPECTED_EXPIRES_AT':"PORTABLE.value('period.expires_at')",
        'EXPECTED_READER_ROOT':"str(PORTABLE.ROOT/Path(PORTABLE.binding('family.reader_source')['path']).parent)",
        'EXPECTED_ENTRYPOINT':"str(Path(PORTABLE.binding('family.reader_source')['path']).parent/'reader.py')+'#SelectedReader.open_signed'",
        'EXPECTED_READER_SHA':"PORTABLE.member_pin('family.reader_source',str(Path(PORTABLE.binding('family.reader_source')['path']).parent/'reader.py'))"}.items():
        text = assignment(text,name,expression)
    text = text.replace('from . import runtime_selection as PORTABLE\n','from . import runtime_selection as PORTABLE\nfrom pathlib import Path\n',1)
    path.write_text(text)
    path = NEW/'agent_challenge_grant.py'
    text = configured_import(path.read_text())
    text = assignment(text,'ROOT','PORTABLE.ROOT')
    text = assignment(text,'FAMILY',"str(Path(PORTABLE.binding('family.source')['path']).parent.parent)")
    slots = {'SOURCE_SHA':'family.source','PACKAGE_SHA':'family.source_package','INDEX_SHA':'family.record_index',
             'COLD_SHA':'family.cold','PERIOD_SHA':'family.period','MAPPING_SHA':'family.mapping','DELIVERY_SHA':'family.delivery'}
    for name,slot in slots.items():
        text = assignment(text,name,"PORTABLE.binding('"+slot+"')['sha256']")
    # Work/Contract body pins and schema pins belong to the immutable selected
    # artifact dataset. Per-host role metadata must never rewrite those hashes.
    start="json.loads(selected('implementation/lab-runtime/local-host/t15-integrated-fixture-0001/reports/legacy-local-4636eca980a5d94d-cold-attempt0002.json', COLD_SHA))['observation']"
    text = once(text,start,"json.loads(selected(PORTABLE.binding('family.cold')['path'], COLD_SHA))['observation']")
    path.write_text(text)
    path = NEW/'machine_auth_scope.py'
    text = configured_import(path.read_text())
    tree = ast.parse(text)
    original_runtime = next(node for node in tree.body if isinstance(node,ast.Assign) and any(isinstance(n,ast.Name) and n.id=='RUNTIMES' for n in node.targets))
    value = ast.literal_eval(original_runtime.value)
    lines = []
    for key,row in value.items():
        expression = "(str(PORTABLE.ROOT/Path(PORTABLE.binding('family.context_source')['path']).parent),PORTABLE.binding('family.context_source')['sha256'])" if key in ('current_context_sessions.py','current_legacy_context_sessions.py') else repr(row)
        lines.append(repr(key)+':'+expression)
    text = assignment(text,'RUNTIMES','{'+','.join(lines)+'}')
    path.write_text(text)
    path = NEW/'observed_margin.py'
    text = configured_import(path.read_text())
    text = text.replace('executable=Path(sys.executable).resolve(strict=True)','executable=PORTABLE.actual_python().resolve(strict=True)')
    text = once(text,"installation=Path(config['dependency_installation']);need(Path(sys.executable)==installation/'bin/python')",
        "installation=Path(config['dependency_installation']);need(PORTABLE.actual_python()==installation/'bin/python')")
    path.write_text(text)
    for path in NEW.rglob('*.py'):
        ast.parse(path.read_text())
    need(methods(NEW)==original,'an inherited test method AST changed')
    rows = [{'path':str((LOGICAL/path.relative_to(NEW)).relative_to(ROOT)),'sha256':sha(path)} for path in NEW.rglob('*') if path.is_file()]
    report = {'schema_version':'lab-portable-api-code-stage/v1','status':'CODE-PREPARED-UNSELECTED',
              'predecessor_source_sha256':SOURCE,'code_directory':str(LOGICAL.relative_to(ROOT)),
              'files':sorted(rows,key=lambda row:row['path']),'inherited_methods':345,'changed_method_asts':0,
              'generated_api_source_profile_required':True,'installed_bootstrap_required':True,
              'runtime_qualified':False,'authority_effect':'none'}
    if NEW==LOGICAL:
        (HERE/'API74-CODE-PREPARATION-0002.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    else:
        original_report = json.loads((HERE/'API74-CODE-PREPARATION-0002.json').read_bytes())
        need(report['files']==original_report['files'],'deterministic code rebuild bytes differ')
        receipt = {'schema_version':'lab-portable-code-deterministic-rebuild/v1','result':'PASS-code-only',
                   'constructor_sha256':sha(Path(__file__)),'predecessor_source_sha256':SOURCE,
                   'canonical_output_directory':str(LOGICAL.relative_to(ROOT)),
                   'rebuilt_files':len(rows),'byte_identical_code_and_static_data':True,
                   'api_source_profile_rebuilt':False,'authority_effect':'none'}
        with (HERE/'API74-CODE-REBUILD-0002.json').open('x') as stream:
            stream.write(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'files':len(rows),'methods':345},sort_keys=True))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rebuild-destination',type=Path)
    args = parser.parse_args()
    if args.rebuild_destination is not None:
        need(args.rebuild_destination.is_absolute() and not args.rebuild_destination.exists()
             and not args.rebuild_destination.resolve().is_relative_to(ROOT),
             'rebuild requires disjoint fresh owned destination')
        NEW = args.rebuild_destination
    main()
