"""Frozen subject/header and actual full SQLite diagnostic; no qualification."""
import argparse,hashlib,importlib.util,json,os,sys,traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4];API=ROOT/'product/lab/release-candidates/v1/interface/api-v18'
PIN='07a14881e21fe3c0db88ff55e0b3b982de05959cbd68a931efa89a2c3368e445';PROFILE='fba4e67cada59ce70277ba2cfb09ece691193989bc20821ca4457eebcf5656ca'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def guard(pin):
 path=HERE/'custody-api-diagnostic-source-0002.json';assert sha(path.read_bytes())==pin
 for row in json.loads(path.read_bytes())['files']:
  p=ROOT/row['path'];assert not p.is_symlink() and sha(p.read_bytes())==row['sha256'],row['path']
def main():
 p=argparse.ArgumentParser();p.add_argument('--source-sha256',required=True);a=p.parse_args();guard(a.source_sha256)
 name='_cal_api18_projection_diagnostic';spec=importlib.util.spec_from_file_location(name,API/'__init__.py',submodule_search_locations=[str(API)]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
 def imported(s):return __import__(name+'.'+s,fromlist=['*'])
 G=imported('guard');G.verify(PIN);P=imported('protocol');M=imported('artifact_model');H=imported('handlers');Q=imported('projection');events=[]
 with P.source.replay_source('custody-participation') as view:
  for s in sorted(view.subjects.values(),key=lambda s:s['version_ref']):
   try:h=M.artifact_ref(view,s);events.append({'version_ref':s['version_ref'],'category':s['category'],'header':h,'result':'PASS'})
   except Exception:
    err=traceback.format_exc();events.append({'version_ref':s['version_ref'],'category':s['category'],'carrier_ref':s['carrier_ref'],'source':s['source'],'result':'FAIL','traceback':err});print(s['version_ref'],err,flush=True)
  try:
   generation=Q.Generation(view,H.cut(view),P.Schemas(PROFILE))
   try:result={'result':'PASS','subjects':len(generation.items),'relations':len(generation.relations),'gaps':len(generation.gaps)}
   finally:generation.close()
  except Exception:result={'result':'FAIL','traceback':traceback.format_exc()};print(result['traceback'],flush=True)
 G.verify(PIN);guard(a.source_sha256)
 report={'schema_version':'lab-source-projection-diagnostic/v1-candidate','events':events,'projection':result,'source_sha256':PIN,'profile_sha256':PROFILE,'owned_resources_closed':True,'full_suite_qualification':False,'authority_effect':'none','actual_owner_outcome':None}
 fd=os.open(HERE/'custody-api-diagnostic-result-0002.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2,sort_keys=True);f.write('\n')
 print(json.dumps({'result':'OBSERVED','subjects':len(events),'header_failures':[e['version_ref'] for e in events if e['result']=='FAIL'],'projection':result}),flush=True)
if __name__=='__main__':main()
