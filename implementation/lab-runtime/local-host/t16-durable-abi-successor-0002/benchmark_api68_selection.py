"""Time selected source selection without native replay or a Session."""
import sys,time,importlib.util,importlib,json
from pathlib import Path
sys.dont_write_bytecode=True
INSTALL=Path('/home/vlad_/.local/share/cyberalchemy-lab/native-install/t22-0001');sys.path.insert(0,str(INSTALL/'deps'))
ROOT=Path(__file__).resolve().parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v68-t16-live-source-freshness-0001';NAME='_t16_api68_selection_benchmark'
spec=importlib.util.spec_from_file_location(NAME,API/'__init__.py',submodule_search_locations=[str(API)]);package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
B=importlib.import_module(NAME+'.source_bridge');t=time.monotonic();D=B.current_legacy_delivery();load=time.monotonic()-t
values=[]
for _ in range(3):
 t=time.monotonic();D.reader.selection(D.SOURCE_PIN,D.SOURCE_PACKAGE,'custody-participation');values.append(time.monotonic()-t)
print(json.dumps({'load_seconds':load,'selection_seconds':values,'source_replay':False,'Session':False,'authority_effect':'none'},sort_keys=True))
