"""Cached preparation only; fresh verification and matching imports remain separate."""
from pathlib import Path
import shutil,os,re,subprocess
HERE=Path(__file__).resolve().parent;BUILD=HERE/'preparation';BUILD.mkdir(exist_ok=True)
LEAN=HERE.parents[5]/'v1/formal/.toolcache/lean-4.33.1-linux/bin/lean'
for p in (HERE.parent/'K02-json-parser/compile').glob('*.olean'):shutil.copy2(p,BUILD/p.name)
for stem in ['GrammarReconstruction','RecursiveSoundness','DocumentSoundness','SoundnessControls']:
    source=HERE/f'{stem}.lean'
    if not source.exists():continue
    attempts=[int(m.group(1)) for p in BUILD.glob(f'{stem}-attempt*.log') if (m:=re.search(r'attempt(\d+)\.log$',p.name))]
    attempt=max(attempts,default=0)+1
    result=subprocess.run([str(LEAN),'-o',str(BUILD/f'{stem}.olean'),str(source)],env=dict(os.environ,LEAN_PATH=str(BUILD)),capture_output=True,text=True,timeout=180)
    log=BUILD/f'{stem}-attempt{attempt:02}.log';log.write_text(result.stdout+result.stderr);print(stem,attempt,result.returncode,flush=True)
    if result.returncode or 'warning:' in result.stdout:print(result.stdout+result.stderr,flush=True);raise SystemExit(1)
