"""Meaningful path/preimage/atomic-copy controls in own inert files only."""
from pathlib import Path
import hashlib,json,os,stat,types
HERE=Path(__file__).absolute().parent
CODE=HERE/'adopt_reviewed_docs_v1.py'
module=types.ModuleType('_T21_owned_docs_adoption_controls');module.__file__=str(CODE)
exec(compile(CODE.read_bytes(),str(CODE),'exec',dont_inherit=True),module.__dict__)
FIXTURE=HERE/'owned-inert-controls';FIXTURE.mkdir(mode=0o700)
fd=os.open(FIXTURE,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW);checks=[];start=len(os.listdir('/proc/self/fd'))
def check(name,value):
 if not value:raise AssertionError(name)
 checks.append(name)
def refuses(name,fn):
 try:fn()
 except (ValueError,OSError):check(name,True)
 else:raise AssertionError(name)
try:
 for p in ['../website/x','website/a/../x','/website/x','product/lab/private','website//x']:
  refuses('target path refusal '+p,lambda p=p:module.target(p))
 inside=str(module.ROOT/'website/owned-control.txt');external='/opt/owned-inert-external/control.txt'
 check('absolute inside comparison only',module.captured_locator(inside)=='website/owned-control.txt')
 check('absolute external unchanged; no external body read',module.captured_locator(external)==external)
 refuses('absolute spelling alias refusal',lambda:module.captured_locator('/opt/inert/../control.txt'))
 raw=(json.dumps({'files':[{'path':inside,'sha256':'0'*64}]})+'\n').encode();module.exclusive_file(fd,'table.json',raw,0o600)
 b={'path':'table.json','sha256':module.sha(raw)};pkt={'runtime_overlap_bindings':{k:b for k in ['source','reader','mapped','context','original_api_source']}}
 refuses('absolute-inside captured overlap refuses before effect',lambda:module.overlap(fd,pkt,['website/owned-control.txt']))
 check('overlap produced no target',not (FIXTURE/'website/owned-control.txt').exists())
 module.exclusive_file(fd,'website/unchanged.txt',b'old\n',0o600);old,info=module.read_at(fd,'website/unchanged.txt')
 row={'target':'website/unchanged.txt','old_bytes':old,'old_stamp':module.stamp(info),'new_bytes':b'new\n','postimage_mode':0o600}
 module.exclusive_file(fd,'backup/unchanged.txt',old,0o600)
 module.install(fd,row,'inert-existing');actual,newinfo=module.read_at(fd,row['target'])
 check('existing atomic copy and mode preserved',actual==b'new\n' and stat.S_IMODE(newinfo.st_mode)==0o600)
 check('backup original bytes/mode preserved',(FIXTURE/'backup/unchanged.txt').read_bytes()==b'old\n' and stat.S_IMODE((FIXTURE/'backup/unchanged.txt').stat().st_mode)==0o600)
 old,info=module.read_at(fd,row['target']);row.update(old_bytes=old,old_stamp=module.stamp(info))
 (FIXTURE/row['target']).write_bytes(b'unrelated-change\n')
 refuses('current preimage conflict refuses before copy',lambda:module.install(fd,row,'inert-conflict'))
 check('unrelated inert change preserved',(FIXTURE/row['target']).read_bytes()==b'unrelated-change\n')
 newrow={'target':'website/new.txt','old_bytes':None,'old_stamp':None,'new_bytes':b'new-exclusive\n','postimage_mode':0o644}
 module.install(fd,newrow,'inert-new');refuses('exclusive occupied new leaf refuses',lambda:module.install(fd,newrow,'inert-new-again'))
 check('new bytes still exact',(FIXTURE/'website/new.txt').read_bytes()==b'new-exclusive\n')
 (FIXTURE/'website/link.txt').symlink_to('new.txt');refuses('symlink leaf refuses',lambda:module.read_at(fd,'website/link.txt'))
 (FIXTURE/'website/linkdir').symlink_to('.',target_is_directory=True);refuses('symlink directory refuses',lambda:module.read_at(fd,'website/linkdir/new.txt'))
 refuses('exclusive backup no overwrite',lambda:module.exclusive_file(fd,'backup/unchanged.txt',b'wrong',0o600))
 check('no temp files remain',not list(FIXTURE.rglob('*.tmp')))
 check('FD delta zero',len(os.listdir('/proc/self/fd'))==start)
finally:os.close(fd)
report={'schema_version':'lab-T21-owned-docs-adoption-controls/v1','authority_effect':'none','result':'PASS-owned-inert-path-conflict-and-copy-controls','code_sha256':hashlib.sha256(CODE.read_bytes()).hexdigest(),'check_count':len(checks),'checks':checks,'FD_delta':0,'actual_shared_apply':False,'native_or_private_body_or_callback_mutation':False,'fixture_root':str(FIXTURE)}
with (HERE/'OWNED-CONTROLS.json').open('x')as f:f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='checks'}))
