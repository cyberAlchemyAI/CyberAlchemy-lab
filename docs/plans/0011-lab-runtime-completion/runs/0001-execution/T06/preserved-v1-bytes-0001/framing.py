"""Serialized bounded LF framing, absolute deadlines and no input reencoding."""
import os,select,time
from control import sha
class FrameError(ValueError):
    def __init__(self,code,raw=b''):self.code=code;self.byte_sha256=sha(raw) if raw else None
class Reader:
    def __init__(self,stream,*,max_frames,max_wire_bytes):
        self.stream=stream;self.max_frames=max_frames;self.max_wire_bytes=max_wire_bytes;self.frames=0;self.wire_bytes=0;self.buffer=b'';self.eof=False
    def receive(self,limit,deadline=None):
        if self.frames>=self.max_frames:raise FrameError('transport-budget-exhausted')
        while True:
            if b'\n' in self.buffer:
                raw,self.buffer=self.buffer.split(b'\n',1)
                if len(raw)>limit:raise FrameError('input-too-large',raw[:limit+1])
                self.frames+=1;return raw
            if len(self.buffer)>limit:raise FrameError('input-too-large',self.buffer[:limit+1])
            if self.eof:
                if self.buffer:raise FrameError('partial-frame',self.buffer)
                return None
            try:fd=self.stream.fileno()
            except (AttributeError,OSError):
                chunk=self.stream.read(min(4096,limit+1-len(self.buffer)))
            else:
                if deadline is not None:
                    remaining=deadline-time.monotonic()
                    if remaining<=0 or not select.select([fd],[],[],remaining)[0]:raise FrameError('startup-deadline-exceeded')
                chunk=os.read(fd,min(4096,limit+1-len(self.buffer)))
            self.wire_bytes+=len(chunk)
            if self.wire_bytes>self.max_wire_bytes:raise FrameError('transport-budget-exhausted')
            if not chunk:self.eof=True
            else:self.buffer+=chunk
def write(stream,value,max_bytes):
    from control import compact,need
    raw=compact(value);need(len(raw)<=max_bytes,'output frame budget exceeded');stream.write(raw+b'\n');stream.flush()
def dispatch(service,reader,output,limit,response_limit):
    # Single loop and one synchronous callback: channel call-ID/nonce/budget
    # consumption is never concurrent. Remove only framing LF, preserve CR,
    # whitespace, member order and exact original received JSON bytes.
    while True:
        raw=reader.receive(limit)
        if raw is None:return 0
        response=service.call(raw);write(output,response,response_limit)
