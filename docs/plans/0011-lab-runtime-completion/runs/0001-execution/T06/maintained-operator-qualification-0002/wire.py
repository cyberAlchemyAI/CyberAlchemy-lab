"""Private exact-byte T06 observations. No API, authentication or effect code."""
import base64,hashlib,json,os,re,select,stat,time
from pathlib import Path

def need(ok,why):
    if not ok:raise ValueError(why)
def compact(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def identity(st):return (st.st_dev,st.st_ino,st.st_uid,st.st_gid,st.st_mode)
def stamp(st):return (*identity(st),st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def sha(raw):return hashlib.sha256(raw).hexdigest()

class WireJournal:
    """One new exclusive0600 leaf, retained with every selected ancestor FD."""
    def __init__(self,root,selected,prefix,event):
        root=Path(root)
        need(root.is_absolute() and root.parent==Path('/tmp') and root.name.startswith('cal-T06-'),'owned T06 root required')
        need(type(selected)is list and len(selected)==4 and selected[2:]==[os.getuid(),0o700],'independent0700 root identity required')
        need(type(prefix)is str and re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,127}',prefix),'bounded flat wire prefix required')
        self.fds=[];self.links=[];self.fd=None;self.event=event;self.count=0;self.bytes=0
        self.previous=None;self.digest=hashlib.sha256();self.leaf=prefix+'.wire.jsonl'
        try:
            parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);self.fds.append(parent)
            for part in root.parts[1:]:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
                self.fds.append(child);self.links.append((parent,part,child,identity(os.fstat(child))));parent=child
            self.rootfd=parent;st=os.fstat(parent)
            need([st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]==selected,'selected private root differs')
            self.check()
            self.fd=os.open(self.leaf,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent)
            st=os.fstat(self.fd);self.file_identity=identity(st)
            need(stat.S_ISREG(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o600,'private wire leaf differs')
            self.check();os.fsync(parent)
        except BaseException:self.close();raise
    def check(self):
        for parent,name,child,selected in self.links:
            need(identity(os.stat(name,dir_fd=parent,follow_symlinks=False))==identity(os.fstat(child))==selected,'private wire ancestor detached')
        if self.fd is not None:
            before=os.fstat(self.fd);attached=os.stat(self.leaf,dir_fd=self.rootfd,follow_symlinks=False)
            need(identity(before)==identity(attached)==self.file_identity and stamp(before)==stamp(attached)
                 and before.st_size==self.bytes,'private wire leaf changed')
    def capture(self,raw,*,direction,phase,branch=None,call_id=None,operation=None,request_frame_sha256=None,complete=True,stage=None):
        need(type(raw)is bytes and 0<len(raw)<=1024*1024+1,'bounded actual wire bytes required')
        need(direction in {'inbound','outbound'} and type(phase)is str and re.fullmatch('[a-z-]{1,64}',phase),'closed wire direction/phase')
        need(branch in {None,'base','actions','governance'},'closed wire branch')
        need(complete is False or raw.endswith(b'\n'),'complete wire must retain transportLF')
        need(stage in {'received-before-parse','captured-before-send','partial-before-refusal'},'closed capture stage')
        for value in (call_id,operation):need(value is None or type(value)is str and len(value)<=256,'bounded wire correlation')
        need(request_frame_sha256 is None or type(request_frame_sha256)is str and re.fullmatch('[a-f0-9]{64}',request_frame_sha256),'exact request frame link')
        payload=raw[:-1] if complete else raw
        public={'sequence':self.count+1,'direction':direction,'phase':phase,'branch':branch,'call_id':call_id,
                'operation':operation,'request_frame_sha256':request_frame_sha256,'complete_LF_frame':complete,
                'capture_stage':stage,'frame_sha256':sha(raw),'frame_size_bytes':len(raw),
                'payload_sha256':sha(payload),'payload_size_bytes':len(payload),'previous_record_sha256':self.previous}
        record={'schema_version':'lab-T06-private-exact-wire/v1-candidate',**public,'frame_base64':base64.b64encode(raw).decode()}
        body=compact(record)+b'\n'
        need(self.count<256 and self.bytes+len(body)<=32*1024*1024,'bounded private wire journal exceeded')
        self.check();offset=0
        while offset<len(body):
            written=os.write(self.fd,body[offset:]);need(written>0,'private wire write stalled');offset+=written
        os.fsync(self.fd);self.bytes+=len(body);self.count+=1;self.digest.update(body);self.previous=sha(body)
        self.check()
        receipt={**public,'wire_journal_leaf':self.leaf,'record_sha256':self.previous,'authority_effect':'none'}
        self.event({'phase':'wire-captured','wire':receipt})
        return receipt
    def summary(self):
        self.check();return {'schema_version':'lab-T06-private-wire-summary/v1-candidate','leaf':self.leaf,
                            'sha256':self.digest.hexdigest(),'size_bytes':self.bytes,'records':self.count,
                            'last_record_sha256':self.previous,'raw_material_public_exported':False,'authority_effect':'none'}
    def close(self):
        if self.fd is not None:os.close(self.fd);self.fd=None
        for fd in reversed(self.fds):os.close(fd)
        self.fds=[]

class WireFrames:
    """Capture the exact framed bytes before strict parse; original Frames stays unchanged."""
    def __init__(self,stream,journal,parse):self.stream=stream;self.journal=journal;self.parse=parse;self.buffer=b''
    def receive(self,deadline,*,phase,branch=None,call_id=None,operation=None,request_frame_sha256=None):
        correlation={'direction':'inbound','phase':phase,'branch':branch,'call_id':call_id,'operation':operation,
                     'request_frame_sha256':request_frame_sha256}
        try:
            while b'\n' not in self.buffer:
                remaining=deadline-time.monotonic()
                need(remaining>0 and select.select([self.stream.fileno()],[],[],remaining)[0],'actual child observation deadline exceeded')
                raw=os.read(self.stream.fileno(),min(65536,1024*1024+1-len(self.buffer)))
                need(raw,'actual child ended before expected frame');self.buffer+=raw
                need(len(self.buffer)<=1024*1024+1,'bounded child frame exceeded')
                need(b'\n' in self.buffer or len(self.buffer)<=1024*1024,'unterminated child frame exceeded')
        except BaseException:
            if self.buffer:
                partial=self.buffer;self.buffer=b''
                self.journal.capture(partial,**correlation,complete=False,stage='partial-before-refusal')
            raise
        payload,self.buffer=self.buffer.split(b'\n',1);frame=payload+b'\n'
        self.last_receipt=self.journal.capture(frame,**correlation,complete=True,stage='received-before-parse')
        return self.parse(payload)

def send_raw(stream,raw,journal,event,*,phase,branch=None,call_id=None,operation=None):
    """Retain intended exact payload+LF first; claim sent only after full write/flush."""
    need(type(raw)is bytes and b'\n' not in raw and len(raw)<=1024*1024,'bounded LF-free payload required')
    frame=raw+b'\n'
    receipt=journal.capture(frame,direction='outbound',phase=phase,branch=branch,call_id=call_id,operation=operation,
                            complete=True,stage='captured-before-send')
    offset=0
    while offset<len(frame):
        count=stream.write(frame[offset:]);need(type(count)is int and count>0,'actual wire write stalled');offset+=count
    stream.flush()
    event({'phase':'wire-sent','wire':receipt})
    return receipt
