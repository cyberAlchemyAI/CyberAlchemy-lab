"""Time exact byte guards without a Session or source replay."""
import sys,time,importlib.util,importlib,json
from pathlib import Path
sys.dont_write_bytecode=True
INSTALL=Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001')
sys.path.insert(0,str(INSTALL/'deps'))
ROOT=Path(__file__).resolve().parents[4]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v68-t16-live-source-freshness-0001'
NAME='_t16_api68_schema_benchmark'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)]);package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
P=importlib.import_module(NAME+'.protocol');G=importlib.import_module(NAME+'.guard')
t=time.monotonic();schemas=P.Schemas('ba389526fa3e9e1c9d840632d3b1c038fcc4a648c4e0ed1767b85fe2cf7c0355');constructed=time.monotonic()-t
rows=[]
for _ in range(3):
 t=time.monotonic();schemas.guard();rows.append(time.monotonic()-t)
print(json.dumps({'construct_seconds':constructed,'schema_guard_seconds':rows,'authority_effect':'none','source_replay':False,'Session':False},sort_keys=True))
