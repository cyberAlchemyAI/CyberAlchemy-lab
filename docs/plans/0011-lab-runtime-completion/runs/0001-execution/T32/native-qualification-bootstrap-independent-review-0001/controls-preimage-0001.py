"""Owned inert controls only; never call launcher.main or a Lab constructor."""
import ast, hashlib, json, os, sys, tempfile, types
from pathlib import Path

HERE=Path(__file__).absolute().parent
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
I=ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
assert Path(sys.executable)==I/'bin/python' and sys.dont_write_bytecode and sys.flags.isolated and sys.flags.no_site
raw=(HERE/'launch_qualify.py').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='1be0ac60161c863e44ef9ad6a3711fd3ab671d8f7ae00a06da947491ac386568'
m=types.ModuleType('_owned_inert_launch_capture');m.__file__=str(HERE/'launch_qualify.py')
exec(compile(raw,m.__file__,'exec'),m.__dict__)
checks=[];start=len(os.listdir('/proc/self/fd'))
def check(label,fn,refused=False):
    try:fn()
    except (ValueError,OSError):
        assert refused,label
    else:assert not refused,label
    checks.append(label)
with tempfile.TemporaryDirectory(prefix='cal-T32-launch-inert-')as t:
    root=Path(t);p=root/'leaf.py';p.write_bytes(b'inert owned bytes\n');pin=hashlib.sha256(p.read_bytes()).hexdigest()
    check('same-byte capture',lambda: m.capture(p,pin)==p.read_bytes())
    check('wrong independent digest refused',lambda:m.capture(p,'0'*64),True)
    q=root/'alias.py';q.symlink_to(p)
    check('leaf symlink refused',lambda:m.capture(q,pin),True)
    d=root/'directory';d.mkdir();(d/'leaf').write_bytes(b'x');a=root/'parent-alias';a.symlink_to(d,target_is_directory=True)
    check('parent symlink refused',lambda:m.capture(a/'leaf',hashlib.sha256(b'x').hexdigest()),True)
    empty=root/'empty';empty.touch()
    check('empty code refused',lambda:m.capture(empty,hashlib.sha256(b'').hexdigest()),True)
    large=root/'large';large.write_bytes(b'x'*(1024*1024+1))
    check('oversize code refused',lambda:m.capture(large,'0'*64),True)
tree=ast.parse(raw);main=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='main')
text=ast.unparse(main)
assert text.index('sys.path.insert')<text.index('exec(compile')<text.index('return module.main()')
checks.append('selected dependency insertion precedes unchanged runner execution')
original=m.capture(m.RUNNER,m.RUNNER_SHA);rt=ast.parse(original)
run=next(n for n in rt.body if isinstance(n,ast.FunctionDef)and n.name=='run');runtext=ast.unparse(run)
assert runtext.index('guard.verify(SOURCE)')<runtext.index("sys.path.insert(0, str(INSTALL / 'deps'))")
checks.append('original bare-launch ordering defect retained without callback edit')
assert len(os.listdir('/proc/self/fd'))==start
print(json.dumps({'result':'PASS-inert-launcher-controls','checks':checks,'FD_delta':0,'pid':os.getpid(),'API_Source_native_installer_or_lease_called':False,'authority_effect':'none'},sort_keys=True))
