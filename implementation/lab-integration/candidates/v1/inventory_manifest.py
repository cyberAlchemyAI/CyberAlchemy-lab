"""Immutable source and regression inventory for C09 verification."""
import hashlib,json
from pathlib import Path

PACKAGE=Path(__file__).resolve().parent;ROOT=PACKAGE.parents[3]
RUNTIME=ROOT/'implementation/lab-runtime/candidates/repeatable-operation'
BOOTSTRAP=ROOT/'implementation/lab-bootstrap/candidates/v1'
CONTEXT=ROOT/'implementation/lab-context/candidates/v1'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def read(path):
    path=Path(path)
    if not path.is_file() or path.is_symlink():raise ValueError('manifest input missing or symlink: '+str(path))
    return path.read_bytes()
def load(path):return json.loads(read(path))


def groups():
    return [
        {'id':'profiles','module':'test_profiles','classes':['Profiles'],'test_directory':(RUNTIME/'tests').relative_to(ROOT).as_posix(),'budget_seconds':180},
        {'id':'extensions','module':'test_extensions','classes':['ExtensionTests'],'additional':[{'module':'test_bound_extensions','classes':['BoundExtensionTests']}],'test_directory':(RUNTIME/'tests').relative_to(ROOT).as_posix(),'budget_seconds':180},
        {'id':'replay','module':'test_replay','classes':['ReplayTests'],'test_directory':(RUNTIME/'tests').relative_to(ROOT).as_posix(),'budget_seconds':240},
        {'id':'transition','module':'test_transition','classes':['TransitionTests'],'test_directory':(RUNTIME/'tests').relative_to(ROOT).as_posix(),'budget_seconds':600},
        {'id':'promotion','module':'test_promotion','classes':['PromotionTests'],'test_directory':(RUNTIME/'tests').relative_to(ROOT).as_posix(),'budget_seconds':900},
        {'id':'bootstrap','module':'test_bootstrap','classes':['BootstrapTests'],'test_directory':(BOOTSTRAP/'tests').relative_to(ROOT).as_posix(),'budget_seconds':600},
        {'id':'context','module':'test_context','classes':['ContextTests','SessionTests'],'test_directory':(CONTEXT/'tests').relative_to(ROOT).as_posix(),'budget_seconds':600,'serialize_source_mutation':True},
        {'id':'joined-inspection','module':'test_join','classes':['JoinTests'],'test_directory':(PACKAGE/'tests').relative_to(ROOT).as_posix(),'budget_seconds':600,'context_consumer':True},
        {'id':'publication-invalidation','module':'test_publication_join','classes':['PublicationJoinTests'],'test_directory':(PACKAGE/'tests').relative_to(ROOT).as_posix(),'budget_seconds':300,'context_consumer':True},
        {'id':'manifest','module':'test_manifest','classes':['ManifestTests'],'test_directory':(PACKAGE/'tests').relative_to(ROOT).as_posix(),'budget_seconds':180},
        {'id':'frozen-v2-regression','module':'test_runtime','classes':['RuntimeTests'],'test_directory':'implementation/lab-runtime/v2/tests','budget_seconds':2400,'case_workers':6,'scope':'Exact preserved v2 compatibility mechanics; its historical protocol views do not establish C08 native/carrier claims.'},
    ]


def selected_files():
    paths=set()
    for folder in [RUNTIME/'lab_runtime',RUNTIME/'tests',RUNTIME/'schemas',RUNTIME/'design',RUNTIME/'profiles']:
        paths.update(p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.update(p for p in RUNTIME.glob('*.py'))
    for folder in [ROOT/'implementation/lab-runtime/v1',ROOT/'implementation/lab-runtime/v2']:
        paths.update(p for p in folder.rglob('*') if p.is_file() and not ({'__pycache__','receipts'} & set(p.parts)))
    for folder in [BOOTSTRAP,CONTEXT]:
        paths.update(p for p in folder.glob('*.py'))
        paths.update((folder/'tests').glob('*.py'));paths.add(folder/'README.md')
        paths.update(p for p in (folder/'packages/0004').rglob('*') if p.is_file())
    paths.update(p for p in (CONTEXT/'native').rglob('*') if p.is_file() and 'target' not in p.parts)
    native=ROOT/'ontology-lifecycle/runtime'
    paths.update([native/'src/lib.rs',native/'Cargo.toml',native/'Cargo.lock'])
    paths.update(p for p in PACKAGE.glob('*.py'));paths.update((PACKAGE/'tests').glob('*.py'));paths.add(PACKAGE/'README.md')
    run=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'
    paths.update([run/'context-C09.json',run/'CONTEXT-C09.md',run/'authorization.json'])
    compatibility=ROOT/'docs/proposals/0007-lab-integrated-schema-package/schema-dependencies.json';paths.add(compatibility)
    # Exact authoring sources used by C04 and inherited validation remain bound.
    selections=load(RUNTIME/'profiles/selections.json')
    for selected in selections['selections']:
        profile=load(ROOT/selected['profile_path'])
        policy=load(ROOT/selected['policy_path'])
        manifest_path=profile['content_manifest']['path']
        if manifest_path:
            paths.add(ROOT/manifest_path)
            for row in load(ROOT/manifest_path)['materials']:paths.add(ROOT/row['path'])
    return sorted(paths)


def validate_manifest(path,expected_sha256):
    raw=read(path)
    if sha(raw)!=expected_sha256:raise ValueError('independent candidate manifest pin mismatch')
    m=json.loads(raw)
    if set(m)!={'schema_version','authority_effect','files','groups','native_executable_sha256','candidate_scope','actual_owner_outcome','frozen_source_policy'}:raise ValueError('candidate manifest must be closed')
    if m['schema_version']!='lab-successor-integration-manifest/v1-candidate' or m['authority_effect']!='none' or m['actual_owner_outcome'] is not None:raise ValueError('candidate manifest cannot claim owner authority')
    if m['groups']!=groups():raise ValueError('regression group inventory changed')
    expected={p.relative_to(ROOT).as_posix() for p in selected_files()}
    names=[r['path'] for r in m['files']]
    if len(names)!=len(set(names)) or set(names)!=expected:raise ValueError('candidate file closure changed')
    for row in m['files']:
        if set(row)!={'path','sha256'} or row['sha256']!=sha(read(ROOT/row['path'])):raise ValueError('candidate bytes changed: '+row['path'])
    return m
