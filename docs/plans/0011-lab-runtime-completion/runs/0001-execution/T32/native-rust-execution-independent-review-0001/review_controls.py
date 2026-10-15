"""Independent frozen-byte/AST/inert peer; no execute module/guards imported."""
import ast,hashlib,json,os,runpy,stat,sys
from pathlib import Path
ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab');P=ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-rust-execution-preparation-0001'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def fds():
 rows={}
 for n in os.listdir('/proc/self/fd'):
  try:s=os.fstat(int(n));rows[n]=(s.st_dev,s.st_ino,s.st_mode)
  except OSError:continue
 return rows

def main():
 start=fds();assert sha((P/'HANDOFF.json').read_bytes())=='ae7bfd2f2a56c326dfc8ef679e5da30e3bf4248ccb8f9e267429c2e1a47c7f76'
 assert sha((P/'source-manifest.json').read_bytes())=='59cd71cb7a9f22945caf021d33e4394d131d8f4aa3c3b5098160c086e68597d3'
 mf=json.loads((P/'source-manifest.json').read_bytes());assert len(mf['files'])==153
 def physical():
  table=[]
  for r in mf['files']:
   path=Path(r['path']);path=path if path.is_absolute()else ROOT/path;s=path.lstat();raw=path.read_bytes()
   assert stat.S_ISREG(s.st_mode)and not path.is_symlink()and sha(raw)==r['sha256']and len(raw)==r['size_bytes']
   table.append({'path':r['path'],'sha256':sha(raw),'size_bytes':len(raw),'observed_mode':stat.S_IMODE(s.st_mode)})
  return table
 entry=physical();inputs=json.loads((P/'inputs.json').read_bytes());assert len(inputs['files'])==139
 original=json.loads((ROOT/inputs['references']['inputs110']['path']).read_bytes());assert len(original['files'])==110
 assert all(r in inputs['files']for r in original['files'])
 proposal=json.loads((ROOT/inputs['references']['proposal']['path']).read_bytes());assert len(proposal['commands'])==5
 setuprow=json.loads((P/'execution-selection-INACTIVE.json').read_bytes())['setup_binding'];assert setuprow['sha256']=='59864fe057e46bcdef485194770e25c771779992f30650a42d30ee40dc552b38'
 setup=json.loads(Path(setuprow['path']).read_bytes());assert sha(Path(setuprow['path']).read_bytes())==setuprow['sha256']
 dispatch=json.loads((P/'ROOT-DISPATCH-INACTIVE.json').read_bytes());assert dispatch['command_timeout_seconds']is None and dispatch['owned_root']==setup['root']
 assert json.loads((P/'execution-selection-INACTIVE.json').read_bytes())['root_dispatch_binding']is None
 code=ast.parse((P/'execute.py').read_bytes());run=next(n for n in code.body if isinstance(n,ast.FunctionDef)and n.name=='run');source=ast.unparse(run)
 assert source.index("sys.path.insert(0, str(INSTALL / 'deps'))")<source.index('guard.verify(SOURCE)')
 assert 'proposal[\'commands\']'in source and 'dict(command[\'environment\'])'in source
 assert "selected source compiler artifact missing"in source and "artifacts[0]['fresh'] is False"in source
 assert 'all25_historical_missing_inputs_remain_REFUSED'in source
 result=runpy.run_path(str(P/'pure_controls.py'),run_name='_T32_independent_inert')['main']();assert result['result']=='PASS'and result['check_count']==19
 exit=physical();assert entry==exit and fds()==start and 'ctypes'not in sys.modules
 return {'result':'PASS-scoped-inert-independent-review','all153_manifest_SHA_size_entry_exit':entry,'all139_inputs_include110_originals':True,'actual_setup_and_unactivated_dispatch_correspond':True,'independent_repeated_pure_controls':result,'FD_delta':0,'ctypes_imported':False,'actual_Cargo_native_Source_installed_or_setup_calls':0}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True))
