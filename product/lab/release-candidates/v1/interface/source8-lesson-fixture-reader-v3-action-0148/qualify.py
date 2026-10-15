"""Exercise the exact reader class with native signed cold evidence."""
import argparse,base64,hashlib,importlib.util,json,sys
from datetime import datetime,timezone
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--reader-sha256',required=True);p.add_argument('--source-sha256',required=True);p.add_argument('--package-sha256',required=True);a=p.parse_args();name='_cal_fixture_reader_native_qualified_0208';spec=importlib.util.spec_from_file_location(name,HERE/'__init__.py',submodule_search_locations=[str(HERE)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);R=__import__(name+'.reader',fromlist=['*']);B=__import__(name+'.base',fromlist=['*']);started=datetime.now(timezone.utc).isoformat();reader=R.FixtureReader(a.reader_sha256,a.source_sha256,a.package_sha256);checks=[]
 try:R.FixtureReader('0'*64,a.source_sha256,a.package_sha256)
 except ValueError:checks.append('independently-pinned-reader-mismatch-refused-before-cold-open')
 else:raise AssertionError('wrong reader source pin accepted')
 with reader.open_signed(a.source_sha256,a.package_sha256) as source:
  assert type(source) is reader.adapter.SignedSources and source is source.view.custody_signed_sources;source.guard();subjects=source.view.subjects;fresh=B.load(B.HERE/'packages/0001/record-index.json');assert len(fresh)==23
  for row in fresh:
   s=subjects[row['version_ref']];assert s['effective_state']=='local-admitted-current';raw,locator,encoding,enclosing=reader.adapter.model.record_bytes(source.view,s);assert raw==B.original(row['original_binding']) and B.sha(raw)==row['original_byte_sha256']
  refs={row['version_ref'] for row in fresh};assert reader.records.PRINCIPAL+'@'+reader.records.VERSION in refs;assert reader.records.ASSIGNMENT+'@'+reader.records.VERSION in refs;assert 'operational-lesson:R03-source8-runtime-lesson-fixture-0208@'+reader.records.VERSION in refs
  checks+=['actual-local-SignedSources-exact-type-and-origin','all-23-fresh-original-bodies-and-current-header-parity','distinct-Principal-Assignment-and-runtime-scoped-Lesson-resolve'];cut=source.source_cut;source.guard()
 assert source.closed;reader.guard();checks.append('SignedSources-closed-and-reader-full-exit-guards')
 report={'schema_version':'lab-controlled-fixture-reader-proof/v1-candidate','result':'PASS','started_at':started,'ended_at':datetime.now(timezone.utc).isoformat(),'checks':checks,'reader_binding':B.binding(HERE/'source-manifest.json'),'source_binding':B.binding(B.HERE/'source-manifest.json'),'package_binding':B.binding(B.HERE/'packages/0001/manifest.json'),'source_cut':cut,'fixture_only':True,'native_cold_cleanup':'C.open_source finalizer removes owned root on context exit; standalone source proof independently verifies root absence','original_Source8_keys_bytes_periods_unchanged':True,'original_Lesson_applicability_inferred':False,'public_API_or_Session_qualified':False,'authority_effect':'none','actual_owner_outcome':None};path=HERE/'receipts/native-reader-proof-0001.json';path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
 with path.open('x') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'PASS-fixture-reader','report_binding':B.binding(path)}),flush=True)
if __name__=='__main__':main()
