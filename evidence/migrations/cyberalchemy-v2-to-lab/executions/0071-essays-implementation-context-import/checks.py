"""Run local checks with captured output. Open questions: README.md."""
import subprocess,json,os
from pathlib import Path
R=Path.cwd();H=Path(__file__).resolve().parent;W=R/'.local/essays-implementation-package-0071/cyberAlchemy-v2/essays/development/agent-runtime/implementation';launcher=str(R.parent/'cyberAlchemy-v2/tools/toolchain/run')
commands={'rust-version':['rustc','--version'],'fmt':['cargo','fmt','--check'],'clippy':['cargo','clippy','--locked','--offline','--all-targets','--','-D','warnings'],'test':['cargo','test','--locked','--offline'],'browser-syntax':['node','--check','browser/playwright-runner.mjs'],'desktop-check':['cargo','check','--locked','--offline','--manifest-path','desktop/src-tauri/Cargo.toml']}
for name,args in commands.items():
 out=H/'checks'/f'{name}.json';out.parent.mkdir(exist_ok=True)
 if out.exists():continue
 print('START',name,flush=True)
 try:
  c=subprocess.run([launcher,*args],cwd=W,capture_output=True,text=True,timeout=240,env={**os.environ,'RUSTUP_AUTO_INSTALL':'0','PYTHONDONTWRITEBYTECODE':'1'});d={'command':args,'exit_code':c.returncode,'stdout':c.stdout,'stderr':c.stderr}
 except subprocess.TimeoutExpired as e:d={'command':args,'exit_code':None,'status':'TIMEOUT','stdout':(e.stdout or b'').decode(),'stderr':(e.stderr or b'').decode()}
 out.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print('DONE',name,d['exit_code'],d['stderr'][-450:],flush=True)
