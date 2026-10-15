"""Owned filesystem controls only; no native/API/permission fixture execution."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

HERE = Path(__file__).absolute().parent

def main():
    name = '_Root_T32_inert_'+uuid.uuid4().hex
    spec = importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)])
    pkg = importlib.util.module_from_spec(spec)
    sys.modules[name] = pkg
    spec.loader.exec_module(pkg)
    io = __import__(name+'.private_io',fromlist=['read'])
    store = __import__(name+'.selected_store',fromlist=['StoreFactory'])
    checks = []
    before = len(os.listdir('/proc/self/fd'))
    def refused(label,fn):
        try:
            fn()
        except (ValueError,OSError):
            checks.append(label)
            return
        raise AssertionError(label)
    with tempfile.TemporaryDirectory(prefix='cal-T32-inert-') as tmp:
        root = Path(tmp)
        root.chmod(0o700)
        value = b'{"original_inert_bytes":true}\n'
        leaf = root/'control.json'
        io.write(leaf,value)
        assert io.read(leaf) == value and leaf.stat().st_mode&0o777 == 0o600
        checks.append('exact original bounded bytes and exclusive600 output')
        refused('existing control never overwritten',lambda:io.write(leaf,b'foreign'))
        assert leaf.read_bytes() == value
        alias = root/'alias'
        alias.symlink_to(leaf)
        refused('symlink leaf is not a selected original',lambda:io.read(alias))
        parent = root/'parent'
        parent.mkdir(mode=0o700)
        try:
            with io.directory(parent):
                parent.rename(root/'retained-parent')
                parent.mkdir(mode=0o700)
        except ValueError:
            checks.append('held directory attachment refuses replacement and retains both directories')
        else:
            raise AssertionError('detached original directory accepted')
        assert (root/'retained-parent').is_dir() and not list(parent.iterdir())
        io.atomic(root/'HEAD.json',b'first')
        io.atomic(root/'HEAD.json',b'second')
        assert io.read(root/'HEAD.json') == b'second'
        checks.append('owned descriptor commit writes exact replacement bytes')
    refused('unbound public factory object cannot supply authority',lambda:store.StoreFactory(None,None,None,None,{}))
    assert len(os.listdir('/proc/self/fd')) == before
    checks.append('owned refusal and descriptor paths balanced')
    print(json.dumps({'result':'PASS-owned-inert-only','checks':checks,'FD_delta':0,
        'native_or_API_or_authorization_constructor_called':False,'native_recovery_qualified':False,'authority_effect':'none'},sort_keys=True))

if __name__ == '__main__':
    main()
