"""C launcher component: actual private ELF execution, not final API proof."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('launcher_builder',HERE/'build.py')
B=importlib.util.module_from_spec(spec);spec.loader.exec_module(B)
INSTALL=Path.home()/'.local/share/cyberalchemy-lab/native-install/t22-0001'
STUB=b'''import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
NATIVE=ROOT.parent/'.cal-runtime/native'
sys.path.insert(0,str(NATIVE/'deps'))
sys.executable=str(ROOT/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python')
if sys.argv[1:2]==['--']: del sys.argv[1]
if sys.argv[1:2]!=['-c']: raise ValueError('component stub supports -c only')
code=sys.argv[2];sys.argv=['-c',*sys.argv[3:]]
exec(compile(code,'<component-probe>','exec'),{'__name__':'__main__'})
'''
PROBE='''import sys,json,subprocess,importlib.metadata
from pathlib import Path
import cryptography
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
Ed25519PrivateKey.generate().sign(b'actual-private-native-probe')
native=Path(sys._base_executable).parent.parent
mapped=[]
for line in Path('/proc/self/maps').read_text().splitlines():
 p=line.split()[-1]
 if p.startswith('/') and Path(p).is_file():
  with open(p,'rb') as f: elf=f.read(4)==b'\\x7fELF'
  if elf:
   if not Path(p).is_relative_to(native): raise ValueError('host ELF mapped')
   if p not in mapped:mapped.append(p)
depth=int(sys.argv[1]);row={'depth':depth,'launcher':sys.executable,'real_python':sys._base_executable,'proc_exe':str(Path('/proc/self/exe').resolve()),'maps':mapped,'isolated':sys.flags.isolated,'no_bytecode':sys.dont_write_bytecode,'no_site':sys.flags.no_site,'optimize':sys.flags.optimize,'jsonschema':importlib.metadata.version('jsonschema'),'crypto':cryptography.__version__}
if depth<2:
 child=subprocess.run([sys.executable,'-I','-B','-O','-c',sys.argv[2],str(depth+1),sys.argv[2]],capture_output=True,text=True,check=True)
 row['child']=json.loads(child.stdout)
print(json.dumps(row,sort_keys=True))
'''

class Launcher(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='cal-launcher-component-');cls.addClassCleanup(cls.temp.cleanup)
        cls.base=Path(cls.temp.name);cls.root=cls.base/'lab'
        cls.launcher=cls.root/'implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python'
        cls.launcher.parent.mkdir(parents=True)
        cls.bootstrap=cls.root/'implementation/lab-runtime/local-host/t25-integrated-runtime-0004/child_bootstrap.py'
        cls.bootstrap.parent.mkdir(parents=True);cls.bootstrap.write_bytes(STUB);cls.bootstrap.chmod(0o600)
        private=cls.base/'.cal-runtime';private.mkdir(mode=0o700);cls.native=private/'native'
        shutil.copytree(INSTALL,cls.native);cls.native.chmod(0o700)
        # Only the production installer receipt has fresh inode fields; C checks
        # its private file posture, while the real bootstrap checks its meaning.
        for directory,dirs,names in os.walk(cls.native):
            for name in dirs:(Path(directory)/name).chmod(0o700)
        B.build(cls.launcher,STUB)
    def invoke(self,*args,**kwargs):
        return subprocess.run([str(self.launcher),*args],capture_output=True,text=True,**kwargs)
    def test_actual_child_grandchild_private_ELF_and_dependency_proof(self):
        child=self.invoke('-B','-I','-S','-X','utf8','-u','-c',PROBE,'0',PROBE,check=True)
        row=json.loads(child.stdout)
        for depth in range(3):
            self.assertEqual(row['depth'],depth);self.assertEqual(row['jsonschema'],'4.23.0');self.assertEqual(row['crypto'],'46.0.5')
            self.assertTrue(row['isolated'] and row['no_bytecode'] and row['no_site']);self.assertTrue(row['maps'])
            self.assertEqual(row['proc_exe'],str(self.native/'lib/abi/ld-linux-x86-64.so.2'))
            self.assertEqual(row['real_python'],str(self.native/'bin/python'))
            self.assertEqual(row['launcher'],str(self.launcher));self.assertEqual(row['optimize'],0 if depth==0 else 1)
            if depth<2:row=row['child']
    def test_native_member_mutation_and_undeclared_file_refused_before_bootstrap(self):
        member=self.native/'lib/python3.14/abc.py';original=member.read_bytes()
        try:
            member.write_bytes(original+b'\n')
            refused=self.invoke('-c','print("MUST-NOT-RUN")');self.assertEqual(refused.returncode,126);self.assertFalse(refused.stdout)
        finally:member.write_bytes(original)
        probe=self.native/'owned-extra.py';probe.write_text('raise RuntimeError()');probe.chmod(0o600)
        try:
            refused=self.invoke('-c','print("MUST-NOT-RUN")');self.assertEqual(refused.returncode,126);self.assertFalse(refused.stdout)
        finally:probe.unlink()
    def test_bootstrap_mutation_and_unknown_flag_refused(self):
        try:
            self.bootstrap.write_bytes(STUB+b'\n')
            self.assertEqual(self.invoke('-c','print(1)').returncode,126)
        finally:self.bootstrap.write_bytes(STUB)
        self.assertEqual(self.invoke('-X','arbitrary-setting','-c','print(1)').returncode,126)
    def test_loader_and_python_environment_cannot_select_another_runtime(self):
        env={**os.environ,'LD_PRELOAD':'/owned-test-missing-host-library.so',
             'LD_LIBRARY_PATH':'/owned-test-host-libs','PYTHONHOME':'/owned-test-other-python',
             'PYTHONPATH':'/owned-test-other-modules'}
        child=self.invoke('-c','import sys; print(sys.flags.isolated, sys.flags.no_site, sys.dont_write_bytecode)',env=env,check=True)
        self.assertEqual(child.stdout.strip(),'1 1 True');self.assertFalse(child.stderr)
    def test_reproducible_static_binary_without_host_ELF_interpreter(self):
        target=self.base/'second-build';B.build(target,STUB)
        self.assertEqual(target.read_bytes(),self.launcher.read_bytes())
        headers=subprocess.run(['readelf','-l',str(target)],capture_output=True,text=True,check=True).stdout
        self.assertNotIn('INTERP',headers)

if __name__=='__main__':unittest.main()
