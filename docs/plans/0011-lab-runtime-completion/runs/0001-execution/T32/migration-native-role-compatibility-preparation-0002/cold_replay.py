"""Actual selected-loader cold replay; never invokes the historical path."""
import base64,os,re,tempfile
from pathlib import Path
from .execution_contract import ROOT,MigrationExecutionContract,need,parse,sha
from .private_io import directory,write
from .capture import capture_path

def read_native(archive,execution_contract):
    need(type(execution_contract)is MigrationExecutionContract,'selectedv2 private cold execution contract required')
    execution_contract.guard();executor=execution_contract.factory.executor
    # Retain the bounded cold store on success or refusal; disposal is a separate
    # explicit action, never inferred from a test outcome.
    root=Path(tempfile.mkdtemp(prefix='cal-O05-v2-cold-',dir=execution_contract.factory.selection['owned_parent']))
    need(not root.is_relative_to(ROOT),'cold native store outside repository required')
    with directory(root)as fd:
        for family in('semantic','governance'):os.mkdir(family,0o700,dir_fd=fd)
        os.fsync(fd)
    expected={}
    for name,b in archive['files'].items():
        need(re.fullmatch(r'(semantic|governance)/[0-9]{8}-ontology-(semantic|governance):O05:[1-9][0-9]*\.json',name)is not None
             and name.split('/')[0]==name.split('-ontology-')[1].split(':')[0], 'unselected native archive entry')
        need(set(b)=={'sha256','base64_original_bytes'},'closed native byte binding required')
        raw=base64.b64decode(b['base64_original_bytes'],validate=True);need(sha(raw)==b['sha256'],'native original event bytes differ')
        write(root/name,raw);expected[name]=sha(raw)
    def files():
        result={}
        with directory(root)as fd:
            need(set(os.listdir(fd))=={'semantic','governance'},'unknown cold-store root residue')
            for family in('semantic','governance'):
                with directory(root/family)as sub:
                    for name in os.listdir(sub):
                        relative=family+'/'+name;need(relative in expected,'unknown cold event file')
                        result[relative]=sha(capture_path(root/relative,maximum=32*1024*1024,required_uid=os.getuid()))
        return result
    before=files();need(before==expected,'cold event restoration incomplete');execution_contract.guard()
    child=executor.run_native('read',[str(root/'semantic'),str(root/'governance'),str(archive['semantic_cursor'])])
    write(root/'cold-stdout.json',child.stdout);write(root/'cold-stderr.txt',child.stderr)
    # files() checks only the event families after the two explicitly bound stream
    # leaves exist; direct family enumeration still refuses unknown event files.
    result={}
    for family in('semantic','governance'):
        with directory(root/family)as fd:
            for name in os.listdir(fd):
                relative=family+'/'+name;need(relative in expected,'unknown cold event file')
                result[relative]=sha(capture_path(root/relative,maximum=32*1024*1024,required_uid=os.getuid()))
    with directory(root)as fd:need(set(os.listdir(fd))=={'semantic','governance','cold-stdout.json','cold-stderr.txt'},'unknown cold root residue')
    need(before==result,'cold replay mutated original events');execution_contract.guard()
    need(child.returncode==0,'native cold replay rejected; owned exact streams retained')
    replay=parse(child.stdout)
    need(replay['result']==replay['checkpoint_parity']=='PASS'and replay['authority_effect']=='none','native replay parity incomplete')
    return replay
