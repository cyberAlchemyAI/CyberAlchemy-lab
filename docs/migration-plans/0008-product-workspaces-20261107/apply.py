#!/usr/bin/env python3
"""Apply the exact prepared Product workspace moves; never copy directory trees."""
from pathlib import Path
import os,json,hashlib,datetime,stat
ROOT=Path(__file__).resolve().parents[3]
HOME=Path(__file__).resolve().parent
PLAN=json.loads((HOME/'PLAN.json').read_text())
JPATH=HOME/'JOURNAL.json'
J=json.loads(JPATH.read_text())
def save():
 JPATH.write_text(json.dumps(J,indent=2,ensure_ascii=False)+'\n')
def need(ok,message):
 if not ok:raise RuntimeError(message)
def mapped(path):
 relative=Path(path).relative_to(ROOT).as_posix()
 for unit in PLAN['units']:
  source=unit['source']
  if relative==source or relative.startswith(source+'/'):
   relative=unit['destination']+relative[len(source):]
 return ROOT/relative
def links_in(source):
 found=[]
 for home,dirs,files in os.walk(source,followlinks=False):
  home=Path(home)
  for name in dirs+files:
   p=home/name
   if p.is_symlink():
    found.append({'relative':p.relative_to(source).as_posix(),'raw':os.readlink(p),'target':str(p.resolve(strict=False)),'valid_before':p.exists()})
  dirs[:]=[d for d in dirs if d not in {'.git','.venv','.local','dist','target','__pycache__'} and not (home/d).is_symlink()]
 return found
def apply_unit(unit):
 source=ROOT/unit['source'];destination=ROOT/unit['destination']
 if any(m['source']==unit['source'] for m in J['moves']):
  need(source.is_symlink() and source.resolve()==destination.resolve(),'Previously applied move drift: '+unit['source'])
  return
 need(source.is_dir() and not source.is_symlink(),'Expected physical source directory: '+unit['source'])
 need(not destination.exists() and not destination.is_symlink(),'Destination already exists: '+unit['destination'])
 need(source.resolve().is_relative_to(ROOT) and destination.resolve(strict=False).is_relative_to(ROOT),'Move escapes repository')
 destination.parent.mkdir(parents=True,exist_ok=True)
 need(source.stat().st_dev==destination.parent.stat().st_dev,'Cross-device move refused; no copy fallback')
 inode=source.stat().st_ino
 links=links_in(source)
 J['pending_move']={'source':unit['source'],'destination':unit['destination'],'inode':inode,'links':links}
 save()
 os.rename(source,destination)
 source.symlink_to(os.path.relpath(destination,source.parent),target_is_directory=True)
 need(destination.stat().st_ino==inode,'Directory inode changed unexpectedly')
 for row in links:
  p=destination/row['relative']
  target=Path(row['target'])
  if target.is_relative_to(ROOT):target=mapped(target)
  need(p.is_symlink(),'Symlink disappeared during move: '+str(p))
  if p.resolve(strict=False)!=target.resolve(strict=False):
   old=os.readlink(p);p.unlink();p.symlink_to(os.path.relpath(target,p.parent),target_is_directory=target.is_dir())
   J['link_rewrites'].append({'path':p.relative_to(ROOT).as_posix(),'before':old,'after':os.readlink(p),'target':str(target)})
  if row['valid_before']:need(p.exists(),'Previously valid link became dangling: '+str(p))
 J['moves'].append({'source':unit['source'],'destination':unit['destination'],'inode':inode,'compatibility_link':os.readlink(source),'method':'same-device-os.rename','link_count':len(links)})
 J.pop('pending_move',None);save()
 print('MOVED',unit['source'],'->',unit['destination'],'links',len(links),flush=True)
def main():
 need(str(ROOT)==PLAN['source_root'],'Wrong repository')
 need(J['state'] in ['prepared','applying'],'Journal requires reconciliation; inspect before continuing')
 J['state']='applying';save()
 for unit in PLAN['units']:apply_unit(unit)
 for item in PLAN['shared_roots']:
  need((ROOT/item['path']).stat().st_ino==item['inode'],'Shared root moved: '+item['path'])
 node=Path(PLAN['shared_node']['path'])
 need(node.stat().st_ino==PLAN['shared_node']['inode'] and hashlib.sha256(node.read_bytes()).hexdigest()==PLAN['shared_node']['sha256'],'Shared Node installation changed')
 J['state']='directories-migrated';J['runtime_copies']=0;save()
 print('Directory migration complete; shared roots and Node installation preserved.',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as error:
  J['state']='reconciliation-required';J['error']=str(error);save();raise
