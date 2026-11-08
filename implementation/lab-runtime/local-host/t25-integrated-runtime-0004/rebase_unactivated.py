"""Advance an unactivated owned package stage without recopying stable bytes.

This cannot alter an installed or constructing runtime. Both manifests and
all changed bytes are retained and checked; fresh bootstrap verifies closure.
"""
import argparse,hashlib,importlib.util,json,os,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_package_copy',HERE/'materialize.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
def atomic(path,raw,mode):
 fd,name=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as out:out.write(raw);out.flush();os.fsync(out.fileno())
  os.chmod(name,mode);os.replace(name,path)
 finally:Path(name).unlink(missing_ok=True)
def rebase(root,view):
 root=M.owned_directory(root);private=root.parent/'.cal-runtime';view=Path(view)
 M.need(not (private/'installation.json').exists() and not (private/'construction-selection.json').exists(),'activated or constructing package cannot be rebased')
 old_raw=(root/'.cal-package-manifest.json').read_bytes();old=json.loads(old_raw);new_raw=(view/'PACKAGE-MANIFEST.json').read_bytes();new=json.loads(new_raw);inputs=json.loads((view/'BUILD-INPUTS.json').read_bytes())
 M.need(inputs['package_manifest_sha256']==M.sha(new_raw),'new assembly manifest binding differs')
 old_rows={r['path']:r for r in old['members']};new_rows={r['path']:r for r in new['members']}
 M.need(old_rows.keys()<=new_rows.keys() and old['dataset']==new['dataset'] and old['native_payload']==new['native_payload'] and old['binding_paths']==new['binding_paths'] and old['generated_metadata_paths']==new['generated_metadata_paths'],'stage rebase may only advance public code/template bytes')
 changed=[]
 for name,row in sorted(new_rows.items()):
  if old_rows.get(name)==row:continue
  path=root/M.relative(name)
  if name in old_rows:M.exact(path,old_rows[name])
  else:M.need(not path.exists(),'new stage target already exists')
  raw=M.exact(inputs['repository_inputs'][name]['input_path'],row)
  M.owned_directory(path.parent);atomic(path,raw,row['mode']);changed.append(name)
 M.write_new(private/('unactivated-package-'+M.sha(old_raw)+'.json'),old_raw,0o600)
 atomic(root/'.cal-package-manifest.json',new_raw,0o644)
 return {'result':'PASS-unactivated-stage-rebase','previous_package_sha256':M.sha(old_raw),'package_manifest_sha256':M.sha(new_raw),'changed_members':changed,'API_qualified':False,'authority_effect':'none'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('view',type=Path);a=p.parse_args();print(json.dumps(rebase(a.root,a.view),sort_keys=True),flush=True)
