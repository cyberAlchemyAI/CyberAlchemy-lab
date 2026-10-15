"""Actual native schema and role preflight before freezing/signing the candidate."""
import importlib.util,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 name='_cal_fixture_source4_native_preflight_0208';s=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);b=__import__(name+'.build',fromlist=['*']);proof=b.schema_role_preflight();b.emit(HERE/'receipts/native-schema-role-preflight-0001.json',proof);print(json.dumps({'result':proof['result'],'targets':proof['actual_native_target_and_core_count'],'proof_binding':b.binding(HERE/'receipts/native-schema-role-preflight-0001.json')}),flush=True)
if __name__=='__main__':main()
