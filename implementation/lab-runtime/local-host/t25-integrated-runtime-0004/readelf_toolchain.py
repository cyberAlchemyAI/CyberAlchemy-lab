"""Capture the real ELF inspection tool's complete runtime namespace closure.

Canonical files become ordinary exact host snapshots. Alias names are an
explicit Docker namespace construction recipe; no WSL namespace is modified.
"""
import hashlib,json,re,stat,subprocess
from pathlib import Path
TOOL=Path('/usr/bin/x86_64-linux-gnu-readelf')
LIBRARIES=(Path('/usr/lib/x86_64-linux-gnu'),Path('/lib/x86_64-linux-gnu'))

def need(value,reason):
 if not value:raise ValueError(reason)
def capture(path):
 path=Path(path).resolve(strict=True);info=path.lstat();need(stat.S_ISREG(info.st_mode),'ELF tool dependency must be a canonical regular file');raw=path.read_bytes();need(raw.startswith(b'\x7fELF'),'ELF tool dependency is not ELF')
 return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'size_bytes':len(raw),'mode':stat.S_IMODE(info.st_mode)}
def inspect(path):
 command=[str(TOOL),'-lWd',str(path)];child=subprocess.run(command,capture_output=True,check=False,timeout=15,env={'PATH':'/usr/bin:/bin','LC_ALL':'C','PYTHONDONTWRITEBYTECODE':'1'})
 need(child.returncode==0,'actual readelf dependency inspection failed');text=child.stdout.decode('utf-8')
 needed=re.findall(r'\(NEEDED\).*?Shared library: \[([^\]]+)\]',text)
 for name in needed:need(re.fullmatch(r'[A-Za-z0-9_.+\-]+',name) is not None and name not in ('.','..'),'closed DT_NEEDED soname required')
 interp=re.findall(r'Requesting program interpreter: ([^\]]+)',text);need(len(interp)<=1,'ambiguous PT_INTERP')
 return needed,interp

def selection():
 queue=[TOOL.resolve(strict=True)];files={};aliases={};graphs={}
 while queue:
  path=queue.pop();name=str(path)
  if name in files:continue
  row=capture(path);files[name]=row;needed,interp=inspect(path);graphs[name]={'needed':needed,'interpreter':interp[0] if interp else None}
  for library in needed:
   choices=[directory/library for directory in LIBRARIES if (directory/library).is_file()];need(choices,'real ELF tool dependency unavailable: '+library)
   original=choices[0];target=original.resolve(strict=True);need(target.parent==LIBRARIES[0],'ELF tool library outside selected canonical system directory');queue.append(target)
   alias=str(LIBRARIES[0]/library)
   if alias!=str(target):
    need(alias not in aliases or aliases[alias]==str(target),'conflicting tool namespace alias');aliases[alias]=str(target)
  for alias in interp:
   value=Path(alias);need(value.is_absolute() and value.as_posix()==alias and '..'not in value.parts,'closed PT_INTERP path required');target=value.resolve(strict=True);need(target.parent==LIBRARIES[0],'ELF interpreter outside selected canonical system directory');queue.append(target)
   if alias!=str(target):aliases[alias]=str(target)
 rows=[]
 for alias,target in sorted(aliases.items()):
  need(target in files,'alias target outside complete canonical ELF tool closure');rows.append({'path':alias,'source_path':target,**{k:files[target][k] for k in ('sha256','size_bytes','mode')}})
 return {'schema_version':'lab-public-ELF-inspection-runtime/v1','tool':str(TOOL.resolve(strict=True)),'host_inputs':[files[name] for name in sorted(files)],'tool_namespace_aliases':rows,'ELF_graph':graphs,'actual_tool_inspection_completed':True,'native_payload_changed':False,'authority_effect':'none'}
if __name__=='__main__':print(json.dumps(selection(),sort_keys=True,indent=2))
