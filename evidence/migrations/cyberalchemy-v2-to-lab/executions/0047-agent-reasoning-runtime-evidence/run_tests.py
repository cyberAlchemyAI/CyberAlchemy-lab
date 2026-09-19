import hashlib,json,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];SOURCE=ROOT.parent/'cyberAlchemy-v2';PACKAGES=SOURCE/'implementation/agent-reasoning-engine/packages'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():return [{'path':str(p.relative_to(SOURCE)),'sha256':sha(p)} for p in sorted(PACKAGES.rglob('*')) if p.is_file() and not any(x in p.parts for x in ['node_modules','__pycache__','.git'])]
tests=['codex-app-server-wrapper/test/wrapper.test.mjs','codex-app-server-wrapper/test/continuation-frontier.test.mjs','evolution-runtime/test/evolution-runtime.test.mjs','evolution-runtime/test/operations.test.mjs']
before=inputs();command=['node','--test','--test-reporter=tap',*[str(PACKAGES/t) for t in tests]]
result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
assert before==inputs(),'Source inputs changed during tests'
(HERE/'tested-inputs.json').write_text(json.dumps(before,indent=2,sort_keys=True)+'\n')
(HERE/'runtime-tests.tap').write_text(result.stdout+result.stderr)
(HERE/'test-run.json').write_text(json.dumps({'exit_code':result.returncode,'command':command,'node_version':subprocess.check_output(['node','--version'],text=True).strip(),'inputs_unchanged':True,'authority_effect':'none','scope':'local fixture tests; no whole-engine or live-service conformance'},indent=2,sort_keys=True)+'\n')
print(result.stdout[-400:]);raise SystemExit(result.returncode)
