"""Run a retained Playwright CLI collector and save its structured result."""
from pathlib import Path
import argparse,json,os,subprocess
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'output/playwright/impeccable-implementation-20261014'
CLI='/mnt/c/Users/vlad_/.codex/skills/playwright/scripts/playwright_cli.sh'
def cli(args):
 env=dict(os.environ,LD_LIBRARY_PATH='/home/vlad_/.cache/ms-playwright/user-libs/usr/lib/x86_64-linux-gnu',PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS='1')
 r=subprocess.run([CLI,'-s=impeccable-implementation','--json',*args],cwd=ROOT,env=env,capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stderr[-3000:]+r.stdout[-1000:])
 data=json.loads(r.stdout)['result']
 while isinstance(data,str):
  try:data=json.loads(data)
  except ValueError:break
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('script');p.add_argument('output');a=p.parse_args()
 d=cli(['run-code','--filename',str(Path(a.script).resolve())]);(OUT/a.output).write_text(json.dumps(d,indent=2)+'\n')
 print(json.dumps({'saved':a.output,'summary':d.get('summary') if isinstance(d,dict) else None}))
