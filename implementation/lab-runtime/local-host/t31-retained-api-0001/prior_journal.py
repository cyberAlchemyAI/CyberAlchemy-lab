"""Copy exact retained journal originals into a fresh owned live /tmp root.

The archive is read-only evidence. The actual journal implementation still
enforces its original live-root rule and cold-replays the copied real chain.
"""
import base64
import json
import os
from pathlib import Path
import stat
import retained as R

def enc(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def capture(root):
    root=Path(root);R.need(root.is_absolute() and root.as_posix()==str(root) and '..'not in root.parts
        and not root.is_symlink() and root.is_dir() and not any(p.is_symlink()for p in root.parents),'exact original journal directory required')
    directories=[];files={};total=0
    for path in [root,*sorted(root.rglob('*'))]:
        R.need(not path.is_symlink(),'linked prior journal member refused')
        st=path.stat(follow_symlinks=False)
        if stat.S_ISDIR(st.st_mode):
            R.need(st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o700,'owned private prior journal directory required')
            if path!=root:directories.append(path.relative_to(root).as_posix())
        else:
            name=path.relative_to(root).as_posix();R.relative(name);raw=R.read(path);files[name]=raw;total+=len(raw)
            R.need(total<=64*1024*1024,'bounded complete original journal required')
    index={'directories':directories,'files':[{'path':name,'sha256':R.sha(raw),'size_bytes':len(raw)}for name,raw in sorted(files.items())]}
    return index,files

def verify(root,expected):
    R.need(type(expected)is dict and set(expected)=={'journal_config_sha256','head','run_sha256','inventory_sha256'},'closed independently selected prior journal required')
    index,files=capture(root)
    R.need(R.sha(enc(index))==expected['inventory_sha256'] and R.sha(files['config.json'])==expected['journal_config_sha256']
           and json.loads(files['HEAD.json'])==expected['head'],'prior actual journal inventory/config/HEAD differs')
    head=expected['head'];sequence=head['sequence']
    raw=files['genesis.json'] if sequence==0 else base64.b64decode(json.loads(files['transactions/'+str(sequence).zfill(8)+'.json'])['next_run_original_base64'],validate=True)
    R.need(R.sha(raw)==expected['run_sha256']==head['run_sha256'],'prior actual journal run original differs')
    return index,files,raw

def copy_selected(source,target,expected,store_type):
    target=Path(target);R.need(target.is_absolute() and target.is_relative_to(Path('/tmp')) and not target.exists()
        and target.parent.is_dir() and not any(p.is_symlink()for p in target.parents),'fresh owned /tmp journal target required')
    index,files,raw=verify(source,expected);target.mkdir(mode=0o700)
    for name in index['directories']:(target/R.relative(name)).mkdir(mode=0o700)
    for name,original in files.items():
        fd=os.open(target/R.relative(name),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb')as stream:stream.write(original);stream.flush();os.fsync(stream.fileno())
    after,originals,again=verify(source,expected);copied,copied_originals=capture(target)
    R.need(after==copied==index and originals==copied_originals==files and again==raw,'prior journal original changed during independent copy')
    store=store_type(target,expected['journal_config_sha256']);R.need(store.replay()==(expected['head'],raw),'actual cold replay differs from retained prior journal')
    # Cold replay and consume traverse actual output originals, not headers.
    for sequence in range(1,expected['head']['sequence']+1):store.consume(sequence)
    R.need(capture(source)==(index,files) and capture(target)==(index,files),'cold prior replay changed original inventory')
    return store
