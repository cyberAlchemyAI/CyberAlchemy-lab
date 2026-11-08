"""Hash every selected public transport byte and inventory named privacy classes.

This detects actual PEM blocks and records sensitive-field/path candidates
without printing their values. Synthetic test data needs an exact disposition;
absence of these finite patterns is not a claim about every possible secret.
"""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import tarfile
import zipfile

LIMIT=128*1024*1024
PEM=re.compile(rb'(?m)^-----BEGIN ((?:RSA |EC |DSA |OPENSSH |ENCRYPTED )?PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----\r?\n[\s\S]{1,1048576}?^-----END \1-----')
PRIVATE_PATH=re.compile(r'(?:^|/)(?:\.cal-runtime|\.ssh|id_rsa|id_ed25519)(?:/|$)|(?:^|/)reader\.pem$')
REVIEW_PATH=re.compile(r'(?:^|/)[^/]*(?:private[_-]?key|credential|password|secret)[^/]*|\.(?:pem|key|p12|pfx|sqlite|db)$',re.I)
CREDENTIAL=re.compile(rb'\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{35})\b|(?mi:^[ \t]*(?:export[ \t]+)?(?:password|client[_-]?secret|api[_-]?key|access[_-]?token|refresh[_-]?token)[ \t]*=[ \t]*[^\r\n]+)')
SENSITIVE={'privatekey','privatekeypem','privatecredentials','password','secret','secretkey','clientsecret','apikey','accesstoken','refreshtoken','bearertoken','credential','credentials','authtoken','signingkey','keymaterial','sessionmemory','workingnotes','privatenote'}

def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while block:=stream.read(1024*1024):h.update(block)
    return h.hexdigest()
def relative(name):
    p=PurePosixPath(name)
    need(type(name)is str and name and not p.is_absolute() and p.as_posix()==name and '..'not in p.parts and '\\'not in name,'closed relative member required')
    return name
def pairs(rows):
    result={}
    for key,value in rows:
        need(key not in result,'duplicate JSON key');result[key]=value
    return result
def parse(raw):return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'nonfinite JSON'))
def selected(path,pin):
    path=Path(path)
    need(path.is_absolute() and not any(p.is_symlink() for p in (path,*path.parents)),'absolute unlinked scan input required')
    a=path.stat();need(stat.S_ISREG(a.st_mode) and a.st_size<=LIMIT,'bounded regular scan input required')
    raw=path.read_bytes();b=path.stat()
    stamp=lambda s:(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    need(stamp(a)==stamp(b) and sha(raw)==pin,'selected scan input changed');return raw
def entries(manifest):
    rows={'PACKAGE-MANIFEST.json':None}
    for row in manifest['members']:
        name='repository/'+relative(row['path']);need(name not in rows,'duplicate repository member');rows[name]=row
    for row in manifest['host_inputs']:
        path=PurePosixPath(row['path']);need(path.is_absolute() and '..'not in path.parts,'closed host snapshot locator required')
        name='host-inputs/'+relative(str(path).lstrip('/'));need(name not in rows,'duplicate snapshot member');rows[name]=row
    for name,row in manifest['native_payload']['members'].items():
        name='native-payload/'+relative(name);need(name not in rows,'duplicate native member');rows[name]=row
    return rows

class Scanner:
    def __init__(self):self.findings=[];self.finding_keys=set();self.expanded=0;self.nested_objects=0;self.seen_nested=set()
    def finding(self,kind,location,raw,pointer=None):
        key=(kind,location,sha(raw),pointer)
        if key not in self.finding_keys:
            self.finding_keys.add(key);self.findings.append({'kind':kind,'location':location,'content_sha256':key[2],**({'json_pointer':pointer} if pointer is not None else {})})
    def value(self,value,location,raw,pointer='',depth=0,nesting=0):
        need(depth<=128,'bounded JSON structure required')
        if isinstance(value,dict):
            for key,item in value.items():
                token=re.sub('[^a-z0-9]','',str(key).lower());at=pointer+'/'+str(key).replace('~','~0').replace('/','~1')
                empty=item is None or item is False or item=='' or item==[] or item=={}
                if token in SENSITIVE and not empty:self.finding('sensitive-json-field',location,raw,at)
                if isinstance(item,str) and ('base64'in token or token in {'b64','bytesb64'}):
                    try:decoded=base64.b64decode(item,validate=True)
                    except (ValueError,TypeError):pass
                    else:
                        if decoded:self.blob(location+'#'+at,decoded,level=nesting+1)
                self.value(item,location,raw,at,depth+1,nesting)
        elif isinstance(value,list):
            for n,item in enumerate(value):self.value(item,location,raw,pointer+'/'+str(n),depth+1,nesting)
    def blob(self,location,raw,level=0):
        need(len(raw)<=LIMIT and level<=8,'bounded nested scan object required')
        self.expanded+=len(raw);need(self.expanded<=2*1024*1024*1024,'bounded nested member expansion required')
        if PRIVATE_PATH.search(location):self.finding('runtime-private-path',location,raw)
        elif REVIEW_PATH.search(location):self.finding('sensitive-path-name',location,raw)
        if PEM.search(raw):self.finding('private-PEM-block',location,raw)
        if CREDENTIAL.search(raw):self.finding('credential-pattern',location,raw)
        marker=(sha(raw),location.split('#',1)[0])
        if level and marker in self.seen_nested:return
        if level:self.seen_nested.add(marker);self.nested_objects+=1
        stripped=raw.lstrip()
        if stripped.startswith((b'{',b'[')):
            try:value=parse(raw)
            except (ValueError,UnicodeError,RecursionError):pass
            else:self.value(value,location,raw,nesting=level)
        if raw.startswith(b'PK\x03\x04'):
            with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                names=set()
                for member in archive.infolist():
                    name=relative(member.filename.rstrip('/') if member.is_dir() else member.filename);need(name not in names,'duplicate nested ZIP member');names.add(name)
                    need(member.file_size<=LIMIT and (member.external_attr>>16)&0o170000 not in (0o120000,),'bounded regular nested ZIP member required')
                    if member.is_dir():continue
                    self.blob(location+'!'+name,archive.read(member),level+1)

def run(archive_path,archive_pin,package_pin,late_selection=None,dispositions=None):
    scanner_pin=sha(Path(__file__).read_bytes())
    archive_path=Path(archive_path).absolute();need(not any(p.is_symlink() for p in (archive_path,*archive_path.parents)),'unlinked archive required')
    need(file_sha(archive_path)==archive_pin,'independently selected archive differs')
    scanner=Scanner();inventory=[];seen=set();expected=None
    with tarfile.open(archive_path,mode='r|gz') as archive:
        for member in archive:
            name=relative(member.name);need(member.isfile() and not member.issym() and not member.islnk() and name not in seen and 0<=member.size<=LIMIT,'unique bounded regular archive member required')
            raw=archive.extractfile(member).read(member.size+1);need(len(raw)==member.size,'archive member length differs')
            if not seen:
                need(name=='PACKAGE-MANIFEST.json' and sha(raw)==package_pin and member.mode==0o644,'exact first package manifest required');expected=entries(parse(raw))
            else:
                need(name in expected and expected[name] is not None,'undeclared archive member');row=expected[name]
                need(sha(raw)==row['sha256'] and len(raw)==row['size_bytes'] and member.mode==row['mode'],'selected archive byte or mode differs')
            scanner.expanded=0;scanner.seen_nested=set();scanner.blob(name,raw)
            inventory.append({'path':name,'sha256':sha(raw),'size_bytes':len(raw),'mode':member.mode});seen.add(name)
    need(expected is not None and seen==set(expected) and file_sha(archive_path)==archive_pin,'whole selected archive changed or incomplete')
    late=[]
    if late_selection:
        selection_path=Path(late_selection).absolute();selection=parse(selection_path.read_bytes())
        need(selection['schema_version']=='lab-explicit-public-late-artifact-selection/v1' and selection['archive_sha256']==archive_pin,'late artifact selection differs')
        for row in selection['files']:
            need(set(row)=={'path','sha256'},'closed late artifact binding required');raw=selected(row['path'],row['sha256']);scanner.expanded=0;scanner.seen_nested=set();scanner.blob(row['path'],raw);late.append(dict(row))
    accepted={}
    if dispositions:
        d=parse(Path(dispositions).read_bytes());need(d['archive_sha256']==archive_pin and d['package_manifest_sha256']==package_pin,'exact archive privacy dispositions required')
        for row in d['findings']:
            key=(row['kind'],row['location'],row['content_sha256'],row.get('json_pointer'))
            need(key not in accepted and row['classification'] in ('public-source-or-schema','public-synthetic-test-fixture','public-dependency','public-documentation') and row['reason'],'explicit unique disposition required');accepted[key]=row
    unresolved=[]
    for row in scanner.findings:
        key=(row['kind'],row['location'],row['content_sha256'],row.get('json_pointer'))
        if row['kind'] in ('private-PEM-block','runtime-private-path') or key not in accepted:unresolved.append(row)
    need(sha(Path(__file__).read_bytes())==scanner_pin,'scanner code changed during observation')
    return {'schema_version':'lab-whole-final-artifact-named-privacy-scan/v1','result':'PASS-selected-named-classes' if not unresolved else 'REVIEW-REQUIRED',
        'archive_sha256':archive_pin,'package_manifest_sha256':package_pin,'archive_member_count':len(inventory),'archive_bytes_scanned':sum(r['size_bytes'] for r in inventory),'inventory_sha256':sha(encoded(inventory)),
        'members':inventory,'nested_objects_scanned':scanner.nested_objects,'late_artifacts':late,'candidate_findings':scanner.findings,'unresolved_findings':unresolved,
        'private_PEM_blocks':sum(r['kind']=='private-PEM-block' for r in scanner.findings),'runtime_private_paths':sum(r['kind']=='runtime-private-path' for r in scanner.findings),
        'scanner_sha256':scanner_pin,'later_private_RAM_sentinel_scanned':False,'protected_Source8_scanned':False,'authority_effect':'none',
        'claim_ceiling':'Every selected public transport byte and explicitly selected late artifact scanned for named path, PEM and JSON classes, including ZIP and explicit base64 payloads. Actual Machine RAM/wire/Vault erasure requires its separate live witness; unrecognized secret encodings are outside this finite pattern scan.'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('archive','archive-sha256','package-sha256','output'):p.add_argument('--'+n,required=True)
    p.add_argument('--late-selection');p.add_argument('--dispositions');a=p.parse_args();result=run(a.archive,a.archive_sha256,a.package_sha256,a.late_selection,a.dispositions)
    raw=(json.dumps(result,sort_keys=True,indent=2)+'\n').encode();fd=os.open(a.output,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
    print(json.dumps({k:result[k] for k in ('result','archive_member_count','archive_bytes_scanned','private_PEM_blocks','runtime_private_paths')},sort_keys=True),flush=True)
