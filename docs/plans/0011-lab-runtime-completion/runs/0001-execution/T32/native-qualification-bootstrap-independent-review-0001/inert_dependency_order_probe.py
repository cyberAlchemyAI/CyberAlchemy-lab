"""Metadata-only ordering probe; no API or native producer import."""
import importlib.metadata,json,os,sys
from pathlib import Path
I=Path('/home/vlad_/projects/CyberAlchemy-lab/product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004')
assert Path(sys.executable)==I/'bin/python' and sys.dont_write_bytecode and sys.flags.isolated and sys.flags.no_site
rows={}
for name in ('jsonschema','cryptography'):
    try:rows[name]={'before':importlib.metadata.version(name)}
    except importlib.metadata.PackageNotFoundError:rows[name]={'before':'PackageNotFoundError'}
sys.path.insert(0,str(I/'deps'))
for name in rows:rows[name]['after']=importlib.metadata.version(name)
assert all(row['before']=='PackageNotFoundError' and row['after'] for row in rows.values())
print(json.dumps({'pid':os.getpid(),'result':'CONFIRMED-selected-vendor-path-required-before-API-guard','packages':rows,'API_or_Source_or_native_imports':False,'full_installed_guard':False,'authority_effect':'none'},sort_keys=True))
