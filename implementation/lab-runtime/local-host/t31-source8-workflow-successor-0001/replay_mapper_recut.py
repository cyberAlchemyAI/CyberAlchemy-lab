"""Read-only byte replay of the staged, unselected T31 Mapper recut."""
import ast
import hashlib
import os
from pathlib import Path
import stat

HERE = Path(__file__).absolute().parent
PRE = HERE / 'preimages/mapped-build.py'
POST = HERE.parent / 'source8-current-fixture/instances/legacy-local-ce4d53a6479188a5/mapped/build.py'
PRE_SHA = '3cb1807565bfa4fc5bb5527c9d35c82e2078af9a3a0a9f0ee049dc48b17cb6a4'
POST_SHA = 'cfd03a6214a38da40d453315184ab73e98beb60f0d91532471b5a7292aeee918'
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


def exact(path, digest):
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('selected Mapper code path is not absolute and closed')
    directory = os.open('/', os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:-1]:
            child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(path.name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        try:
            if not stat.S_ISREG(os.fstat(fd).st_mode):
                raise ValueError('selected Mapper code is not regular')
            with os.fdopen(fd, 'rb', closefd=False) as stream:
                raw = stream.read()
        finally:
            os.close(fd)
    except OSError as error:
        raise ValueError('selected Mapper code missing or linked') from error
    finally:
        os.close(directory)
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('selected Mapper code changed')
    return raw


def main():
    before = exact(PRE, PRE_SHA).decode('utf-8')
    if before.count(OLD) != 1:
        raise ValueError('Mapper recut anchor missing or ambiguous')
    after = before.replace(OLD, NEW)
    ast.parse(after)
    if after.encode('utf-8') != exact(POST, POST_SHA):
        raise ValueError('Mapper recut bytes differ')
    print('mapped/build.py', POST_SHA)


if __name__ == '__main__':
    main()
