"""Resume a known failed unactivated copy; no arbitrary destination overwrite."""
import argparse,hashlib,importlib.util,json,os,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_resume_materialize',HERE/'materialize.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def atomic(path,raw,mode):
 fd,name=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
  os.chmod(name,mode);os.replace(name,path)
 finally:Path(name).unlink(missing_ok=True)
def resume(old_view,new_view,root):
 old_view=Path(old_view);new_view=Path(new_view);root=M.owned_directory(root);private=root.parent/'.cal-runtime'
 M.need(not (private/'installation.json').exists() and not (private/'construction-selection.json').exists() and not (root/'.cal-package-manifest.json').exists(),'only an incomplete unactivated materialization may resume')
 old=json.loads((old_view/'PACKAGE-MANIFEST.json').read_bytes());raw=(new_view/'PACKAGE-MANIFEST.json').read_bytes();new=json.loads(raw);inputs=json.loads((new_view/'BUILD-INPUTS.json').read_bytes());M.need(M.sha(raw)==inputs['package_manifest_sha256'],'new assembly manifest binding differs')
 M.need(old['dataset']==new['dataset'] and old['native_payload']==new['native_payload'] and old['binding_paths']==new['binding_paths'],'failed copy may not retarget dataset/native/binding meaning')
 before={r['path']:r for r in old['members']};after={r['path']:r for r in new['members']};M.need(before.keys()<=after.keys(),'resume may not silently remove old selected members')
 for directory,subdirs,names in os.walk(root,followlinks=False):
  for name in subdirs+names:M.need(not (Path(directory)/name).is_symlink(),'linked incomplete repository cannot resume')
  for name in names:M.need(str((Path(directory)/name).relative_to(root)) in after,'unselected file in incomplete repository')
 skipped=copied=advanced=0
 for name,row in sorted(after.items()):
  target=root/M.relative(name)
  if target.exists():
   try:M.exact(target,row)
   except ValueError:
    M.need(name in before,'existing resume target outside previous selection');M.exact(target,before[name]);body=M.exact(inputs['repository_inputs'][name]['input_path'],row);atomic(target,body,row['mode']);advanced+=1
   else:skipped+=1
  else:
   body=M.exact(inputs['repository_inputs'][name]['input_path'],row);M.write_new(target,body,row['mode']);copied+=1
  if (skipped+copied+advanced)%5000==0:print(json.dumps({'checked_members':skipped+copied+advanced,'copied':copied,'advanced':advanced}),flush=True)
 M.write_new(root/'.cal-package-manifest.json',raw,0o644)
 return {'result':'PASS-resumed-public-repository-materialization','package_manifest_sha256':M.sha(raw),'checked_existing_members':skipped,'copied_members':copied,'explicit_advanced_members':advanced,'API_qualified':False,'authority_effect':'none'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('old_view',type=Path);p.add_argument('new_view',type=Path);p.add_argument('repository',type=Path);a=p.parse_args();print(json.dumps(resume(a.old_view,a.new_view,a.repository),sort_keys=True),flush=True)
