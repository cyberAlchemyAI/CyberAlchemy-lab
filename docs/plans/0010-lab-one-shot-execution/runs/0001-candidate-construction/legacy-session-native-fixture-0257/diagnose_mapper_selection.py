"""Read-only actual selected source identities; no mapping qualification."""
import fcntl,hashlib,importlib.util,json,os,sys
from pathlib import Path
OUT=Path(__file__).resolve().parent;RUN=OUT.parent;ROOT=RUN.parents[4];BASE=ROOT/'product/lab/release-candidates/v1/interface'
def boot(n,p):
 s=importlib.util.spec_from_file_location(n,p/'__init__.py',submodule_search_locations=[str(p)]);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m)
fd=os.open(RUN/'final-api-regression-0173-0190.execution.lock',os.O_RDONLY|os.O_NOFOLLOW);fcntl.flock(fd,fcntl.LOCK_SH)
try:
 boot('_legacy_mapper_diagnostic_guard',BASE/'api-integration-v14');G=__import__('_legacy_mapper_diagnostic_guard.guard',fromlist=['verify']);pin='aea84d1d97c2780e8fb172b6dd4d8807f2e89892a02f0fe0e5daab97b3f0c240';G.verify(pin)
 boot('_legacy_mapper_diagnostic',BASE/'legacy-session-fixture-mapped-v1-action-0148');B=__import__('_legacy_mapper_diagnostic.base',fromlist=['reader']);B.verify_source('b8829e2ce2ee5b01ca82a686e2d075b261d4d8e762dc96adf81ac22f0e52a294')
 with B.reader.open_signed(B.SOURCE_PIN,B.PACKAGE_PIN) as src:
  rows=[{'identity':s['identity'],'version_ref':s['version_ref'],'effective_state':s['effective_state'],'carrier_ref':s['carrier_ref']} for s in src.view.subjects.values() if 'legacy-session-fixture' in s['identity'] or s['carrier_ref']=='cal.artifact-type.typed-relation/v3']
  report={'qualification':False,'selected_records_prefix':B.records.PREFIX,'selected_records_module':str(Path(B.records.__file__).relative_to(ROOT)),'subjects':rows};src.guard()
 G.verify(pin)
 with (OUT/'mapper-selection-diagnostic.json').open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)
