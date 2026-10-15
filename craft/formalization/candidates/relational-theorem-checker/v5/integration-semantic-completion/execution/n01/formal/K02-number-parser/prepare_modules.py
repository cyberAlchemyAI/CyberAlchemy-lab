"""Local preparation only; these cached imports do not constitute fresh verification."""
from pathlib import Path
import os,shutil,subprocess,re
HERE=Path(__file__).resolve().parent
BASE=HERE.parents[5]
LEAN=BASE/'v1/formal/.toolcache/lean-4.33.1-linux/bin/lean'
BUILD=HERE/'preparation';BUILD.mkdir(exist_ok=True)
for stem,folder in [('ClosedJsonObject','K02-numeric'),('DecimalMeaning','K02-numeric'),('DecimalEpochCheck','K02-numeric'),('DecimalGrammar','K02-numeric'),('JsonElements','K02-binding-ast'),('BindingAstCombinators','K02-binding-ast')]:
    shutil.copy2(HERE.parent/folder/'compile'/f'{stem}.olean',BUILD/f'{stem}.olean')
for stem in ['NumberDigitScan','NumberTokenParser','NumberGrammarComplete','NumberEpochAst','NumberParserControls']:
    source=HERE/f'{stem}.lean'
    if not source.exists():continue
    attempts=[int(m.group(1)) for f in BUILD.glob(f'{stem}-attempt*.log') if (m:=re.search(r'attempt(\d+)\.log$',f.name))]
    attempt=max(attempts,default=0)+1
    result=subprocess.run([str(LEAN),'-o',str(BUILD/f'{stem}.olean'),str(source)],env=dict(os.environ,LEAN_PATH=str(BUILD)),capture_output=True,text=True,timeout=180)
    (BUILD/f'{stem}-attempt{attempt:02}.log').write_text(result.stdout+result.stderr)
    print(stem,attempt,result.returncode,flush=True)
    if result.returncode or 'warning:' in result.stdout:
        print(result.stdout+result.stderr,flush=True)
        raise SystemExit(1)
