"""Per-install control metadata over one immutable signed4636 dataset.

Stable code and original Artifact/event/history bytes are package inputs. Only
explicit metadata targets can change. This stage makes no cold/Context PASS;
construction child and fresh-process qualification remain mandatory.
"""
import copy,hashlib,json,os,stat,tempfile
from pathlib import Path
OLD_FAMILY='implementation/lab-runtime/local-host/t15-integrated-fixture-0001/instances/legacy-local-4636eca980a5d94d'
OLD_LANE='implementation/lab-runtime/local-host/t15-integrated-fixture-0001'
SOURCE_ARTIFACT_PREFIX=OLD_FAMILY+'/source/packages/0001/artifacts/'
NATIVE_LOGICAL='product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004/bin/lab-context-native-reader'
NATIVE_SHA='fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c'
PORTABLE_ROLE_LOADER='implementation/lab-runtime/local-host/t25-portable-family-0001/portable-payload-origin-0005/role_loader.py'
PORTABLE_ROLE_CONTROL='implementation/lab-runtime/local-host/t25-portable-family-0001/portable-role-origin-0003/control.py'
PORTABLE_INSTALLED_PAYLOAD='implementation/lab-runtime/local-host/t25-portable-family-0001/installed_payload_0001.py'
CONTROL_TARGETS=(
 'source/source-manifest.json','source/context-native-role.json','source/packages/0001/archive-handle.json','source/packages/0001/manifest.json',
 'reader/source-manifest.json','mapped/source-manifest.json','mapped/packages/0001/manifest.json','mapped/packages/0001/mapping.json',
 'context/source-manifest.json','context/implementation-binding.json')

def need(value,reason):
 if not value:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def parse(raw):
 def pairs(rows):
  out={}
  for k,v in rows:need(k not in out,'duplicate metadata key');out[k]=v
  return out
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite metadata'))
def relative(value):
 p=Path(value);need(type(value)is str and p.as_posix()==value and not p.is_absolute() and '..'not in p.parts and '\\'not in value and value!='.','closed metadata relative path required');return p
def identity(path):
 p=Path(path);s=p.lstat();need(stat.S_ISDIR(s.st_mode),'regular owned directory required');return[s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]
def native_executable_bindings(native):
 file_binding={'path':str(Path(native)/'bin/lab-context-native-reader'),'sha256':NATIVE_SHA}
 # Source capture's exact two-field locator is distinct from the selected
 # native role's mode-bearing execution contract. Neither is widened.
 return file_binding,{**file_binding,'required_mode':0o755}
def capture(path,digest=None,*,mode=None):
 p=Path(path);need(p.is_absolute() and '..'not in p.parts,'metadata capture path unsafe');handles=[];links=[]
 stamp=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
 try:
  parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);handles.append(parent)
  for part in p.parts[1:-1]:
   child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent);value=os.fstat(child);handles.append(child);links.append((parent,part,child,value.st_dev,value.st_ino));parent=child
  fd=os.open(p.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=parent);handles.append(fd);before=os.fstat(fd)
  need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_size<=64*1024*1024,'bounded owned metadata file required')
  need(mode is None or stat.S_IMODE(before.st_mode)==mode,'metadata file mode differs');chunks=[];size=0
  while chunk:=os.read(fd,1024*1024):
   size+=len(chunk);need(size<=before.st_size,'metadata capture grew');chunks.append(chunk)
  raw=b''.join(chunks)
  need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(p.name,dir_fd=parent,follow_symlinks=False)) and len(raw)==before.st_size,'metadata changed during capture')
  for ancestor,name,held,device,inode in links:
   a=os.stat(name,dir_fd=ancestor,follow_symlinks=False);h=os.fstat(held);need(stat.S_ISDIR(a.st_mode) and(a.st_dev,a.st_ino)==(h.st_dev,h.st_ino)==(device,inode),'metadata ancestor attachment changed')
  need(digest is None or sha(raw)==digest,'metadata independent digest differs');return raw
 finally:
  for fd in reversed(handles):os.close(fd)

def template_targets(repository):
 root=Path(repository);base=root/OLD_FAMILY
 result=[OLD_FAMILY+'/'+name for name in CONTROL_TARGETS]
 # All derived Context package outputs are explicitly replaceable host-bound
 # metadata, including newly generated view identities. OriginalSource26 are
 # outside this set and must remain exact. Signed native events stay stable.
 result.extend(p.relative_to(root).as_posix() for p in sorted((base/'context/packages/0001').rglob('*')) if p.is_file())
 return sorted(set(result))

def emit_templates(repository,destination):
 root=Path(repository).resolve();out=Path(destination).resolve();need(root!=out,'template output must be distinct')
 result={}
 for name in template_targets(root):
  raw=capture(root/name);target=out/'.cal-metadata-templates'/name;target.parent.mkdir(parents=True,exist_ok=True)
  need(not target.exists(),'refuse replace selected metadata template');target.write_bytes(raw);target.chmod(0o644)
  result[name]={'path':str(target.relative_to(out)),'sha256':sha(raw)}
 return result

class Constructor:
 def __init__(self,root,package_sha):
  self.root=Path(root).resolve();self.private=self.root.parent/'.cal-runtime'
  self.package=parse(capture(self.root/'.cal-package-manifest.json',package_sha))
  need(self.package['schema_version']=='lab-stable-runtime-package/v1' and self.package['authority_effect']=='none','exact stable package required')
  self.allowed=set(self.package['generated_metadata_paths']);self.stable={r['path']:r for r in self.package['members']};self.templates={}
  need(not any(name.startswith(SOURCE_ARTIFACT_PREFIX) for name in self.allowed),'original signed Artifact bodies cannot be generated metadata')
  for target,binding in self.package['metadata_templates'].items():
   relative(target);relative(binding['path']);need(target in self.allowed and self.stable.get(binding['path'],{}).get('sha256')==binding['sha256'],'template outside independently packaged members')
   self.templates[target]=capture(self.root/binding['path'],binding['sha256'])
  need(set(self.templates)==self.allowed,'closed complete metadata templates required')
  need(identity(self.private)[2:]==[os.getuid(),0o700],'private install directory custody differs')
 def binding(self,name):
  relative(name);return {'path':name,'sha256':sha(capture(self.root/name))}
 def emit(self,name,raw):
  need(name in self.allowed,'write outside generated metadata set');p=self.root/relative(name);p.parent.mkdir(parents=True,exist_ok=True)
  fd,temp=tempfile.mkstemp(prefix='.'+p.name+'.',dir=p.parent)
  try:
   with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
   os.chmod(temp,0o644);os.replace(temp,p);d=os.open(p.parent,os.O_RDONLY|os.O_DIRECTORY)
   try:os.fsync(d)
   finally:os.close(d)
  finally:Path(temp).unlink(missing_ok=True)
 def _fresh_bindings(self,value):
  if isinstance(value,list):return[self._fresh_bindings(x) for x in value]
  if not isinstance(value,dict):return value
  result={k:self._fresh_bindings(v) for k,v in value.items()}
  key='path' if isinstance(result.get('path'),str) else 'ref' if isinstance(result.get('ref'),str) else None
  if key is not None and isinstance(result.get('sha256'),str):
   path=Path(result[key])
   if not path.is_absolute() and '..'not in path.parts:
    logical=path.as_posix()
    if logical in self.allowed:result['sha256']=sha(capture(self.root/relative(logical)))
    elif logical in self.stable:
     # Stable postimages come only from the independently pinned public
     # package, never a newly read file chosen by this mutable metadata.
     # Materialization checks these exact bytes; trusted bootstrap verifies
     # the full physical closure again before construction/runtime imports.
     result['sha256']=self.stable[logical]['sha256']
    elif key=='path' or (self.root/path).is_file():raise ValueError('selected metadata file binding is undeclared: '+str(path))
   elif path.is_absolute() and path==self.private/'native/bin/lab-context-native-reader':result['sha256']=sha(capture(path,mode=0o755))
  return result
 def initial(self):
  native=self.private/'native';archive=self.private/'fixture-archives/branch.snapshot'
  ni=identity(native);need(ni[2:]==[os.getuid(),0o700],'fresh native identity/custody differs')
  native_receipt=parse(capture(native/'installation.json',mode=0o600));need(native_receipt['schema']=='cal-clean-installed-native-runtime/v1' and native_receipt['identity']==ni and native_receipt['file_count']==1010,'fresh native receipt body differs')
  original_handle=parse(self.templates[OLD_FAMILY+'/source/packages/0001/archive-handle.json']);capture(archive,original_handle['sha256'],mode=0o600)
  role=parse(self.templates[OLD_FAMILY+'/source/context-native-role.json']);need(role['dependency_selection_binding']['sha256']==native_receipt['selection_sha256'],'fresh native selection differs from fixed dataset ABI')
  role['installation']={'path':str(native),'identity':ni};role['installation_receipt_binding']={'path':str(native/'installation.json'),'sha256':sha(capture(native/'installation.json',mode=0o600))}
  need(all(name in self.stable for name in (PORTABLE_ROLE_CONTROL,PORTABLE_ROLE_LOADER,PORTABLE_INSTALLED_PAYLOAD)),'independently packaged portable role helpers required')
  role['module_bindings']['control']={'path':PORTABLE_ROLE_CONTROL,'sha256':self.stable[PORTABLE_ROLE_CONTROL]['sha256']}
  role['module_bindings']['installed_payload']={'path':PORTABLE_INSTALLED_PAYLOAD,'sha256':self.stable[PORTABLE_INSTALLED_PAYLOAD]['sha256']}
  role=self._fresh_bindings(role)
  values={name:parse(raw) for name,raw in self.templates.items()}
  values[OLD_FAMILY+'/source/context-native-role.json']=role
  source_manifest=values[OLD_FAMILY+'/source/source-manifest.json']
  for name in (PORTABLE_ROLE_LOADER,PORTABLE_ROLE_CONTROL,PORTABLE_INSTALLED_PAYLOAD):
   need(not any(row['path']==name for row in source_manifest['files']),'portable Source helper already present in historical template')
   source_manifest['files'].append({'path':name,'sha256':self.stable[name]['sha256']})
  values[OLD_FAMILY+'/source/packages/0001/archive-handle.json']={**original_handle,'path':str(archive)}
  executable,executable_role=native_executable_bindings(native);capture(native/'bin/lab-context-native-reader',NATIVE_SHA,mode=0o755)
  for name in (OLD_FAMILY+'/mapped/source-manifest.json',OLD_FAMILY+'/context/source-manifest.json'):
   body=values[name];body['files']=[executable if r['path']==NATIVE_LOGICAL else r for r in body['files']]
   body['external_dependency_bindings']=[r for r in body['files'] if Path(r['path']).is_absolute()]
   if 'native_executable_binding'in body:body['native_executable_binding']=executable_role
  for name,raw in self.templates.items():self.emit(name,raw)
  # Manifest dependencies form an acyclic family closure. Each pass updates
  # only explicit byte bindings. No arbitrary scalar digest or signed record
  # body is rewritten. All generated Context bodies remain provisional until
  # the native Context constructor replaces them in its private child process.
  for iteration in range(16):
   changed=False
   for name in sorted(values):
    body=self._fresh_bindings(values[name])
    if name==OLD_FAMILY+'/mapped/packages/0001/mapping.json':
     closure=body.get('source_closure',{})
     basis=closure.get('candidate_selection_basis',{})
     for key,logical in (
       ('manifest_sha256',OLD_FAMILY+'/source/packages/0001/manifest.json'),
       ('source_manifest_sha256',OLD_FAMILY+'/source/source-manifest.json'),
       ('adapter_source_sha256',OLD_FAMILY+'/reader/source-manifest.json')):
      if key in basis:basis[key]=sha(capture(self.root/logical))
    if name==OLD_FAMILY+'/context/packages/0001/delivery-provenance.json':
     body['mapped_package_sha256']=sha(capture(self.root/OLD_FAMILY/'mapped/packages/0001/manifest.json'))
    raw=encoded(body)
    if capture(self.root/name)!=raw:self.emit(name,raw);changed=True
    values[name]=body
   if not changed:break
  else:raise ValueError('metadata byte-binding dependency did not converge')
  period=parse(capture(self.root/OLD_FAMILY/'source/packages/0001/period.json'))
  return {'bindings':self.export_bindings(),'values':{'identity.family':self.package['dataset']['family'],'identity.store':self.package['dataset']['store'],'identity.scope':self.package['dataset']['scope'],'identity.source_name':'completion-legacy:legacy-local-4636eca980a5d94d','native.root':str(native),'native.identity':ni,'native.receipt':role['installation_receipt_binding'],'native.dependency_selection':role['dependency_selection_binding'],'archive.path':str(archive),'archive.sha256':original_handle['sha256'],'period.not_before':period['not_before'],'period.expires_at':period['expires_at']},'phase':'construct-context','cold_or_Context_qualified':False}
 def export_bindings(self,*,ready=False):
  unresolved={'api.source','api.profile','family.context_package','family.delivery','family.cold'}
  return {slot:None if not ready and slot in unresolved else self.binding(path)
          for slot,path in self.package['binding_paths'].items()}
 def finalize(self):
  """Refresh actual generated outputs; never restore provisional templates.

  The construction child must already have exited. This does not mint a ready
  receipt or claim qualification; the installer seals that independently.
  """
  source_members={name:row['sha256'] for name,row in self.stable.items()
                  if name.startswith(SOURCE_ARTIFACT_PREFIX)}
  need(len(source_members)==26,'exact26 original Source Artifact bodies required')
  for name,digest in source_members.items():capture(self.root/name,digest)
  values={name:parse(capture(self.root/relative(name))) for name in self.allowed}
  cold_name=self.package['binding_paths']['family.cold']
  cold=values[cold_name]
  need(cold.get('observation',{}).get('result')=='PASS-native-cold'
       and cold['observation'].get('independent_cold_replays')==2,
       'actual two-replay native cold observation required before finalize')
  # The API source/profile closure excludes rebind-receipt itself. Reject a
  # cycle rather than iterating arbitrary mutually attesting hash claims.
  source_name=self.package['binding_paths']['api.source']
  profile_name=self.package['binding_paths']['api.profile']
  receipt_names=[name for name in values if name.endswith('/rebind-receipt.json')]
  need(len(receipt_names)==1,'exact per-install API rebind receipt required')
  receipt_name=receipt_names[0]
  for name in (source_name,profile_name):
   def reject_receipt(value):
    if isinstance(value,list):
     for row in value:reject_receipt(row)
    elif isinstance(value,dict):
     need(value.get('path')!=receipt_name and value.get('ref')!=receipt_name,'API receipt cannot occur in its own source/profile closure')
     for row in value.values():reject_receipt(row)
   reject_receipt(values[name])
  for iteration in range(16):
   changed=False
   for name in sorted(values):
    body=self._fresh_bindings(values[name])
    if name==OLD_FAMILY+'/context/packages/0001/delivery-provenance.json':
     body['mapped_package_sha256']=sha(capture(self.root/OLD_FAMILY/'mapped/packages/0001/manifest.json'))
    if name==receipt_name:body['successor_manifest_sha256']=sha(capture(self.root/source_name))
    raw=encoded(body)
    if capture(self.root/name)!=raw:self.emit(name,raw);changed=True
    values[name]=body
   if not changed:break
  else:raise ValueError('final metadata byte-binding dependency did not converge')
  for name,digest in source_members.items():capture(self.root/name,digest)
  need(values[receipt_name]['successor_manifest_sha256']==sha(capture(self.root/source_name)),
       'final API rebind receipt manifest differs')
  return {'bindings':self.export_bindings(ready=True),'phase':'metadata-finalized-unqualified',
          'ready_receipt_emitted':False,'actual_fresh_process_qualification':False,
          'original_Source_Artifact_bodies_unchanged':26}
