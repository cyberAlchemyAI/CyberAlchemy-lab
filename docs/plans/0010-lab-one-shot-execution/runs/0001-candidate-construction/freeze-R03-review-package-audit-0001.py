"""Bind complete original twenty-case proof before independent owned audit."""
import ast,hashlib,importlib.metadata,json,platform
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];K=ROOT/'product/lab/release-candidates/v1/interface/review-package-v2'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def main():
 out=HERE/'review-package-audit-source-0001.json';assert not out.exists();m=json.loads((K/'source-manifest.json').read_bytes())
 assert bind(K/'source-manifest.json')['sha256']=='0c78b7951d9ac21a8cac03021bc7c5ed6df31c80ffa281e87fd7df5edd073d6a'
 report=json.loads((K/'receipts/checks.json').read_bytes());terminal=json.loads((HERE/'review-package-terminal-0002.json').read_bytes())
 assert report['result']=='PASS' and report['tests_run']==report['expected_tests']==len(report['cases'])==20 and all(c['result']=='PASS' for c in report['cases'])
 assert terminal['exit_code']==0 and terminal['checks_binding']==bind(K/'receipts/checks.json') and terminal['log_binding']==bind(K/'checks-0001.log') and terminal['source_binding']==bind(K/'source-manifest.json')
 rows={r['path']:r for r in m['files']}
 for p in [K/'source-manifest.json',K/'receipts/checks.json',K/'receipts/examples.json',K/'checks-0001.log',HERE/'review-package-terminal-0002.json',HERE/'context-R03-review-package-audit-0001.json',HERE/'audit-R03-review-package-0001.py',Path(__file__)]:
  if p.suffix=='.py':ast.parse(p.read_bytes())
  b=bind(p);assert rows.get(b['path'],b)==b;rows[b['path']]=b
 for r in rows.values():assert bind(ROOT/r['path'])==r
 env={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')};assert env==m['environment']
 out.open('x').write(json.dumps({'schema_version':'lab-review-kernel-audit-source/v1-candidate','files':sorted(rows.values(),key=lambda r:r['path']),'environment':env,'kernel_source_binding':bind(K/'source-manifest.json'),'full_twenty_case_terminal_binding':bind(HERE/'review-package-terminal-0002.json'),'frozen_before_owned_effects':True,'public_review_adapter_implemented':False,'actual_owner_outcome':None,'authority_effect':'none','task_complete':False},indent=2,sort_keys=True)+'\n')
 print(json.dumps({'result':'FROZEN','files':len(rows),'source_binding':bind(out)}),flush=True)
if __name__=='__main__':main()
