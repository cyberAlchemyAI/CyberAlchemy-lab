"""Freeze actual new3600 dataset inputs; never edits the signed dataset."""
import hashlib, importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
FAMILY='implementation/lab-runtime/local-host/t03-long-local-fixture-0001/instances/legacy-local-5bd4f03a7076695c'
LANE='implementation/lab-runtime/local-host/t03-long-local-fixture-0001'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def bind(path):return {'path':str(path.relative_to(ROOT)),'sha256':sha(path.read_bytes())}
def main():
 out=HERE/'fresh-dataset-templates-0002';out.mkdir(mode=0o700)
 spec=importlib.util.spec_from_file_location('_fresh_metadata',HERE/'metadata_0008.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 templates=module.emit_templates(ROOT,out,family=FAMILY)
 index=json.loads((ROOT/FAMILY/'source/packages/0001/record-index.json').read_bytes())
 originals=[row['original_binding'] for row in index]
 assert len(originals)==26
 for row in originals:assert bind(ROOT/row['path'])==row
 fixture={}
 for kind in ('work','challenge-contract','operational-lesson'):
  selected=[r for r in index if r['kind']==kind];assert len(selected)==1
  fixture[kind]={**selected[0]['original_binding'],'version_ref':selected[0]['version_ref']}
 engine=ROOT/LANE/'engine-v3'
 paths={'engine.profile':engine/'runtime/profile.json','engine.manifest':engine/'engine-manifest.json','engine.loader':engine/'loader.py','engine.pins':engine/'pins.json'}
 suffixes={'source':'source/source-manifest.json','source_package':'source/packages/0001/manifest.json','reader_source':'reader/source-manifest.json','reader_package':'source/packages/0001/manifest.json','mapper_source':'mapped/source-manifest.json','mapper_package':'mapped/packages/0001/manifest.json','mapping':'mapped/packages/0001/mapping.json','context_source':'context/source-manifest.json','context_package':'context/packages/0001/manifest.json','delivery':'context/packages/0001/delivery.json','period':'source/packages/0001/period.json','record_index':'source/packages/0001/record-index.json','archive_handle':'source/packages/0001/archive-handle.json','context_native_role':'source/context-native-role.json'}
 paths.update({'family.'+slot:ROOT/FAMILY/value for slot,value in suffixes.items()})
 handle=json.loads(paths['family.archive_handle'].read_bytes());assert sha(Path(handle['path']).read_bytes())==handle['sha256']
 result={'schema_version':'lab-fresh-qualified-dataset-inputs/v1','dataset':{'family':Path(FAMILY).name,'store':'completion-'+Path(FAMILY).name,'scope':'project:cyberalchemy-v2-to-lab-migration','session_seconds':3600},'family':FAMILY,'bindings':{slot:bind(path) for slot,path in paths.items()},'fixture_records':fixture,'metadata_templates':templates,'template_root':str(out.relative_to(ROOT)),'original_source_artifacts':originals,'fixture_seed':handle,'Source_Reader_Mapper_Context_actual_PASS':True,'API_or_Session_qualified':False,'authority_effect':'none'}
 target=HERE/'FRESH-DATASET-ACTUAL-INPUTS-0001.json';assert not target.exists()
 target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');target.chmod(0o644)
 print(json.dumps({'result':'PASS-fresh-dataset-inputs-frozen','templates':len(templates),'binding':bind(target)},sort_keys=True))
if __name__=='__main__':main()
