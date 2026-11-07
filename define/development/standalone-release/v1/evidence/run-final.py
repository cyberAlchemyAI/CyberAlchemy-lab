import hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
root=Path(__file__).resolve().parent
version,interpreter=sys.argv[1:3]
mode=sys.argv[3] if len(sys.argv)>3 else 'wheel'
name=version+('-sdist' if mode=='sdist' else '')
env=root/('final-'+name)
artifacts=root/'final-artifacts'
archive=next(artifacts.glob('*.tar.gz' if mode=='sdist' else '*.whl'))
tests=root/'final-source/cyberalchemy_define-0.3.0rc2/tests'
child_env={**os.environ,'DEFINE_DENY_REPO':'/home/vlad_/projects/CyberAlchemy-lab','PYTHONNOUSERSITE':'1'}
commands=[('venv',[interpreter,'-m','venv',str(env)]),
          ('install',[str(env/'bin/python'),'-m','pip','install',str(archive)]),
          ('pip-check',[str(env/'bin/python'),'-m','pip','check']),
          ('freeze',[str(env/'bin/python'),'-m','pip','freeze']),
          ('tests',[str(env/'bin/python'),'-I','-m','unittest','discover','-s',str(tests),'-v'])]
rows=[]
for step,command in commands:
 started=time.monotonic();p=subprocess.run(command,cwd=root,capture_output=True,timeout=300,env=child_env)
 (root/f'final-{name}-{step}.stdout').write_bytes(p.stdout);(root/f'final-{name}-{step}.stderr').write_bytes(p.stderr)
 row={'step':step,'exit_code':p.returncode,'seconds':round(time.monotonic()-started,3)}
 if step=='tests':
  match=re.search(r'Ran (\d+) tests',(p.stdout+p.stderr).decode());row['test_count']=int(match[1]) if match else None
 rows.append(row)
 if p.returncode:break
result={'python_selection':version,'interpreter':interpreter,'environment':str(env),'artifact':archive.name,'artifact_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'tests_from':'extracted-final-sdist','repository_denied_in_core_child':child_env['DEFINE_DENY_REPO'],'steps':rows,
        'outcome':'passed' if len(rows)==len(commands) and all(r['exit_code']==0 for r in rows) else 'failed'}
(root/f'final-{name}-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));raise SystemExit(0 if result['outcome']=='passed' else 1)
