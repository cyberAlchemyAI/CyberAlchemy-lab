"""Read-only reconstruction and selected-manifest check of final T31 Mapper code."""
import ast
import hashlib
import json
import os
from pathlib import Path
import stat

HERE = Path(__file__).absolute().parent
ROOT = HERE.parents[3]
FAMILY = ROOT / 'implementation/lab-runtime/local-host/source8-current-fixture/instances/legacy-local-ce4d53a6479188a5'
PRE = HERE / 'preimages/mapped-build.py'
POST = FAMILY / 'mapped/build.py'
MANIFEST = FAMILY / 'mapped/source-manifest.json'
PRE_SHA = '3cb1807565bfa4fc5bb5527c9d35c82e2078af9a3a0a9f0ee049dc48b17cb6a4'
POST_SHA = '57b33bd2ff63a873b389bb51392f9766f302951dcecefa497e5130fadcb7b49a'
MANIFEST_SHA = 'fa05a8638d49ba8f27df4b6ffdf2dae00868ff4d7ac3946d2785f5bbfe771b02'
OLD = """        selected_relation_refs={row['version_ref'] for row in declared if row['carrier_ref']=='cal.artifact-type.typed-relation/v3'}
        require(len(selected_relation_refs)==10,'exact ten independently declared relation versions required')
"""
NEW = """        original_relation_names=('reference-principal','work-project','assignment-project','goal-project',
            'context-project','assignment-intent','goal-intent','profile-capability',
            'implementation-product-capability','context-goal')
        selected_relation_refs={'typed-relation:'+records.PREFIX+':'+name+'@'+records.VERSION
            for name in original_relation_names}
        declared_relation_refs={row['version_ref'] for row in declared
            if row['carrier_ref']=='cal.artifact-type.typed-relation/v3'}
        workflow_ref='typed-relation:'+records.PREFIX+':workflow-decision-resolution@'+records.VERSION
        require(len(selected_relation_refs)==10 and declared_relation_refs==selected_relation_refs|{workflow_ref},
            'exact ten Context relations and one retained workflow relation required')
"""
PINS = {
    "SOURCE_PIN='f3cbec21c32dce3938460a1203e6e3f3575608f463aa3f3fffae9f9338a798f2'":
        "SOURCE_PIN='0dc869f614e4d1f4be29c4b85f60dd5abd8f25b9fe84e1dc779932aee90c50d4'",
    "PACKAGE_PIN='8e7b675666308e0e73fb23962b310ea3a89baa48ad6bf2c9cf1c5c9ce9e96964'":
        "PACKAGE_PIN='7006fd4fac3327b76f4ffcc03d93ffb070bb25288ca7bab7e7e5b20470baf22c'",
}


def read_regular(path):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('selected path not absolute and closed')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                            dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError('selected Mapper file not regular')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                return stream.read()
        finally:
            os.close(fd)
    except OSError as error:
        raise ValueError('selected Mapper path missing or linked') from error
    finally:
        os.close(directory)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def reconstruct():
    raw = read_regular(PRE)
    if sha(raw) != PRE_SHA:
        raise ValueError('Mapper preimage changed')
    text = raw.decode('utf-8')
    if text.count(OLD) != 1:
        raise ValueError('Mapper relation recut anchor missing or ambiguous')
    text = text.replace(OLD, NEW)
    for old, new in PINS.items():
        if text.count(old) != 1:
            raise ValueError('Mapper native pin anchor missing or ambiguous')
        text = text.replace(old, new)
    ast.parse(text)
    output = text.encode('utf-8')
    if sha(output) != POST_SHA:
        raise ValueError('Mapper final reconstruction changed')
    return output


def verify():
    expected = reconstruct()
    actual = read_regular(POST)
    if actual != expected:
        raise ValueError('Mapper selected final bytes differ')
    manifest_raw = read_regular(MANIFEST)
    if sha(manifest_raw) != MANIFEST_SHA:
        raise ValueError('Mapper selected manifest changed')
    manifest = json.loads(manifest_raw)
    rows = [row for row in manifest['files'] if row['path'] == POST.relative_to(ROOT).as_posix()]
    if rows != [{'path': POST.relative_to(ROOT).as_posix(), 'sha256': POST_SHA}]:
        raise ValueError('Mapper final code absent from selected manifest')
    return {'final_code_sha256': POST_SHA, 'manifest_sha256': MANIFEST_SHA}


if __name__ == '__main__':
    print(json.dumps(verify(), sort_keys=True))
