"""Real Linux publication mechanics against the actual observer selector AST."""
import ast
import ctypes
import hashlib
import json
import os
from pathlib import Path
import select
import struct
import tempfile
import time
ROOT=Path(__file__).resolve().parents[4]
PATH=ROOT/'implementation/lab-runtime/local-host/t18-current-service-kill-0001/workflow_probe.py'
def need(ok,reason):
    if not ok:raise ValueError(reason)
def main():
    raw=PATH.read_bytes();tree=ast.parse(raw)
    assignments=[n for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='publication_mask' for t in n.targets)]
    need(len(assignments)==1,'actual publication predicate required')
    selector=compile(ast.Expression(assignments[0].value),str(PATH),'eval')
    mask_for=lambda stage:eval(selector,{}, {'stage':stage})
    with tempfile.TemporaryDirectory(prefix='cal-real-publication-events-') as folder:
        root=Path(folder);libc=ctypes.CDLL(None,use_errno=True);fd=libc.inotify_init1(os.O_CLOEXEC|os.O_NONBLOCK)
        need(fd>=0 and libc.inotify_add_watch(fd,os.fsencode(root),0x08|0x80|0x100)>=0,'actual inotify observer required')
        try:
            data=b'{"synthetic_publication_component":true}\n'
            direct=root/'direct.json'
            handle=os.open(direct,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
            with os.fdopen(handle,'wb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
            temporary=root/'completed.tmp';temporary.write_bytes(data)
            with temporary.open('rb') as stream:os.fsync(stream.fileno())
            linked=root/'result.json';os.link(temporary,linked)
            replacement=root/'head.tmp';replacement.write_bytes(data);os.replace(replacement,root/'HEAD.json')
            events=[];end=time.monotonic()+2
            while time.monotonic()<end:
                if not select.select([fd],[],[],.03)[0]:break
                block=os.read(fd,65536);position=0
                while position<len(block):
                    wd,mask,cookie,size=struct.unpack_from('iIII',block,position);position+=16
                    name=os.fsdecode(block[position:position+size].split(b'\0',1)[0]);position+=size
                    events.append({'name':name,'mask':mask})
            values={name:[e['mask'] for e in events if e['name']==name] for name in ('direct.json','result.json','HEAD.json')}
            need(any(m&0x100 for m in values['direct.json']) and any(m&0x08 for m in values['direct.json']),'actual direct-write create/close events absent')
            need(any(m&mask_for('claim') for m in values['direct.json']) and not (mask_for('claim')&0x100),'inner claim stops before complete write')
            need(any(m&mask_for('transaction') for m in values['direct.json']),'actual immutable transaction publication missed')
            need(values['result.json'] and all(not (m&(0x08|0x80)) for m in values['result.json'])
                 and any(m&mask_for('result') for m in values['result.json']),'actual fsynced hardlink result publication missed')
            need(any(m&mask_for('head') for m in values['HEAD.json']),'actual renamed HEAD publication missed')
            need(linked.read_bytes()==direct.read_bytes()==(root/'HEAD.json').read_bytes()==data,'publication original bytes differ')
            print(json.dumps({'result':'PASS-real-OS-publication-selector-component','workflow_probe_sha256':hashlib.sha256(raw).hexdigest(),
              'actual_events':values,'actual_inner_claim_and_tx_close_write':True,'actual_head_rename':True,'actual_outer_fsynced_hardlink_create':True,
              'old_close_or_move_filter_would_miss_result':True,'actual_Service_kill_or_power_loss_qualified':False,'authority_effect':'none'},sort_keys=True))
        finally:os.close(fd)
if __name__=='__main__':main()
