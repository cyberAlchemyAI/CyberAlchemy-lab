"""Cached-import preparation only; full fresh verification is separate."""
from pathlib import Path
import shutil,subprocess,os,re
HERE=Path(__file__).resolve().parent
BUILD=HERE/'preparation';BUILD.mkdir(exist_ok=True)
BASE=HERE.parents[5];LEAN=BASE/'v1/formal/.toolcache/lean-4.33.1-linux/bin/lean'
for folder in ['K02-number-parser','K02-binding-ast','K02-owned-qualifiers']:
    for f in (HERE.parent/folder/'compile').glob('*.olean'):
        shutil.copy2(f,BUILD/f.name)
for stem in ['BindingFrame','BindingRecord','BindingRecordControls']:
    source=HERE/f'{stem}.lean'
    if not source.exists():continue
    attempts=[int(m.group(1)) for p in BUILD.glob(f'{stem}-attempt*.log') if (m:=re.search(r'attempt(\d+)\.log$',p.name))]
    attempt=max(attempts,default=0)+1
    result=subprocess.run([str(LEAN),'-o',str(BUILD/f'{stem}.olean'),str(source)],env=dict(os.environ,LEAN_PATH=str(BUILD)),capture_output=True,text=True,timeout=180)
    (BUILD/f'{stem}-attempt{attempt:02}.log').write_text(result.stdout+result.stderr)
    print(stem,attempt,result.returncode,flush=True)
    if result.returncode or 'warning:' in result.stdout:
        print(result.stdout+result.stderr,flush=True);raise SystemExit(1)
