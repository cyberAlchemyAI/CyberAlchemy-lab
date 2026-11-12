from pathlib import Path
import json,tarfile,gzip,hashlib,io
R=Path(__file__).resolve().parents[3];P=Path(__file__).resolve().parent
mapping=json.loads((P/'MAPPING.json').read_text());rows=[]
archive=R/'evidence/definitions/full-v2-layout/define-packages.tar.gz';archive.parent.mkdir(parents=True,exist_ok=True)
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w') as t:
 for row in mapping['entries']:
  receipt=json.loads((R/row['work']/'DEFINE-RECEIPT.json').read_text());assert receipt['status']=='PASS'
  pack=(R/receipt['definition']['path']).parents[3]/'pack';assert pack.is_dir(),pack
  members=[]
  for f in sorted(pack.rglob('*')):
   if f.is_dir():continue
   assert f.is_file() and not f.is_symlink() and f.suffix=='.json',f
   relative=str(f.relative_to(pack));name=row['definition_id']+'/pack/'+relative;raw=f.read_bytes()
   info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o644;info.mtime=0;t.addfile(info,io.BytesIO(raw));members.append(relative)
  manifest=pack/'manifest.json';assert manifest.is_file(),pack
  rows.append({'definition_id':row['definition_id'],'archive_prefix':row['definition_id']+'/pack/','manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'members':len(members)})
raw=gzip.compress(buf.getvalue(),mtime=0);archive.write_bytes(raw)
out={'archive':{'path':str(archive.relative_to(R)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)},'packages':rows,'contains':'Verified portable Define package data only; no runtime code or private keys'}
(P/'PACKAGES.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'status':'PASS','packages':len(rows),'archive_bytes':len(raw)}))
