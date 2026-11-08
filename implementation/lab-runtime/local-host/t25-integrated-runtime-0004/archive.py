"""Deterministic exact-member transport; extracted bytes confer no readiness."""
import argparse,gzip,hashlib,importlib.util,io,json,os,tarfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('_cal_archive_copy',HERE/'materialize.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

def file_sha(path):
 digest=hashlib.sha256()
 with Path(path).open('rb') as stream:
  while block:=stream.read(1024*1024):digest.update(block)
 return digest.hexdigest()

def entries(manifest):
 rows={'PACKAGE-MANIFEST.json':None}
 for row in manifest['members']:
  name='repository/'+str(M.relative(row['path']));M.need(name not in rows,'duplicate archive repository member');rows[name]=row
 for row in manifest['host_inputs']:
  path=Path(row['path']);M.need(path.is_absolute() and '..'not in path.parts,'unsafe host snapshot path');name='host-inputs/'+path.as_posix().lstrip('/');M.need(name not in rows,'duplicate host snapshot');rows[name]=row
 for name,row in manifest['native_payload']['members'].items():
  name='native-payload/'+str(M.relative(name));M.need(name not in rows,'duplicate native payload');rows[name]=row
 return rows

def write_archive(view,destination):
 view=Path(view);destination=Path(destination);raw=(view/'PACKAGE-MANIFEST.json').read_bytes();manifest=json.loads(raw);inputs=json.loads((view/'BUILD-INPUTS.json').read_bytes());M.need(M.sha(raw)==inputs['package_manifest_sha256'],'archive package selection differs');rows=entries(manifest)
 with destination.open('xb') as file,gzip.GzipFile(fileobj=file,mode='wb',filename='',mtime=0,compresslevel=6) as compressed,tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT) as archive:
  for name,row in rows.items():
   if name=='PACKAGE-MANIFEST.json':body=raw;mode=0o644
   else:
    if name.startswith('repository/'):source=inputs['repository_inputs'][name[len('repository/'):]]['input_path']
    elif name.startswith('host-inputs/'):source=inputs['host_inputs']['/'+name[len('host-inputs/'):]]['input_path']
    else:source=str(Path(inputs['native_payload_root'])/name[len('native-payload/'):])
    body=M.exact(source,row);mode=row['mode']
   info=tarfile.TarInfo(name);info.size=len(body);info.mode=mode;info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0;archive.addfile(info,io.BytesIO(body))
 with destination.open('rb') as f:os.fsync(f.fileno())
 return {'result':'PASS-exact-public-archive-written','package_manifest_sha256':M.sha(raw),'archive_sha256':file_sha(destination),'members':len(rows),'size_bytes':destination.stat().st_size,'installed_API_qualified':False,'authority_effect':'none'}

def extract_archive(path,destination,package_pin):
 destination=M.owned_directory(destination);M.need(not any(destination.iterdir()),'archive extraction requires fresh empty owned destination');seen=set();rows=None;manifest=None
 with tarfile.open(path,mode='r|gz') as archive:
  for item in archive:
   M.relative(item.name);M.need(item.isfile() and not item.issym() and not item.islnk() and item.name not in seen,'archive member must be unique regular file');M.need(0<=item.size<=128*1024*1024,'archive member exceeds bounded input');body=archive.extractfile(item).read(item.size+1);M.need(len(body)==item.size,'archive member length differs')
   if not seen:
    M.need(item.name=='PACKAGE-MANIFEST.json' and M.sha(body)==package_pin,'archive first member must be independently selected manifest');manifest=json.loads(body);rows=entries(manifest);M.need(item.mode==0o644,'archive manifest mode differs')
   else:
    M.need(item.name in rows and rows[item.name] is not None,'undeclared archive member');row=rows[item.name];M.need(len(body)==row['size_bytes'] and M.sha(body)==row['sha256'] and item.mode==row['mode'],'archive selected byte/mode differs')
   M.write_new(destination/M.relative(item.name),body,item.mode);seen.add(item.name)
 M.need(rows is not None and seen==set(rows),'archive closed member set incomplete')
 return {'result':'PASS-exact-public-archive-extracted','package_manifest_sha256':package_pin,'members':len(seen),'API_qualified':False,'authority_effect':'none'}
if __name__=='__main__':
 p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True);w=s.add_parser('write');w.add_argument('view',type=Path);w.add_argument('destination',type=Path);x=s.add_parser('extract');x.add_argument('archive',type=Path);x.add_argument('destination',type=Path);x.add_argument('package_sha256');a=p.parse_args();v=write_archive(a.view,a.destination) if a.action=='write' else extract_archive(a.archive,a.destination,a.package_sha256);print(json.dumps(v,sort_keys=True),flush=True)
