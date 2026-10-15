"""Unrun pure inert wire controls; no API, key, lease, native or operator launch."""
import base64,hashlib,io,json,os,tempfile,time
from pathlib import Path

def check(H):
    W=H.wire_component();results=[];fd0=len(os.listdir('/proc/self/fd'))
    def passed(label):results.append({'control':label,'result':'PASS'})
    def refuses(label,fn):
        try:fn()
        except (ValueError,OSError):passed(label);return
        raise AssertionError(label)
    def root_identity(root):
        root.chmod(0o700);s=root.stat();return [s.st_dev,s.st_ino,s.st_uid,0o700]
    def receive(journal,raw,phase='dispatch-result',**kw):
        rd,wr=os.pipe()
        try:
            os.write(wr,raw);os.close(wr);wr=None
            with os.fdopen(rd,'rb') as stream:
                rd=None;F=W.WireFrames(stream,journal,H.parse)
                return F.receive(time.monotonic()+1,phase=phase,**kw)
        finally:
            if rd is not None:os.close(rd)
            if wr is not None:os.close(wr)
    with tempfile.TemporaryDirectory(prefix='cal-T06-wire-controls-') as tmp:
        root=Path(tmp);selected=root_identity(root);events=[];J=W.WireJournal(tmp,selected,'fresh',events.append)
        try:
            raw=b' \t{"inert": true} \r\n'
            assert receive(J,raw)=={'inert':True};passed('inbound exact whitespace CR and LF captured before parse')
            sink=io.BytesIO();request=b' \t{"call_id": "inert:call"} \r'
            sent=W.send_raw(sink,request,J,events.append,phase='dispatch',branch='base',call_id='inert:call',operation='operation.inspect')
            assert sink.getvalue()==request+b'\n';passed('outbound captured and written identical bytes including LF')
            reply=b'{ "inert" : true }\r\n'
            assert receive(J,reply,branch='base',call_id='inert:call',operation='operation.inspect',request_frame_sha256=sent['frame_sha256'])=={'inert':True}
            refuses('malformed inbound bytes retained before strict parse refusal',lambda:receive(J,b'\t{malformed}\r\n'))
            refuses('partial EOF retained without fabricating complete frame',lambda:receive(J,b' inert-incomplete'))
            summary=J.summary();content=(root/'fresh.wire.jsonl').read_bytes();rows=[json.loads(x) for x in content.splitlines()]
            assert len(rows)==5 and summary['records']==5 and summary['sha256']==hashlib.sha256(content).hexdigest()
            assert base64.b64decode(rows[0]['frame_base64'],validate=True)==raw
            assert base64.b64decode(rows[1]['frame_base64'],validate=True)==request+b'\n'
            assert base64.b64decode(rows[2]['frame_base64'],validate=True)==reply
            assert rows[2]['request_frame_sha256']==rows[1]['frame_sha256'] and rows[2]['call_id']==rows[1]['call_id']
            assert rows[0]['payload_sha256']!=rows[2]['payload_sha256'];passed('response digest distinguishes semantically equal whitespace variants')
            assert base64.b64decode(rows[3]['frame_base64'],validate=True)==b'\t{malformed}\r\n'
            assert base64.b64decode(rows[4]['frame_base64'],validate=True)==b' inert-incomplete' and rows[4]['complete_LF_frame']is False
            previous=None
            for sequence,(line,row) in enumerate(zip(content.splitlines(keepends=True),rows),1):
                assert row['sequence']==sequence and row['previous_record_sha256']==previous
                frame=base64.b64decode(row['frame_base64'],validate=True)
                assert hashlib.sha256(frame).hexdigest()==row['frame_sha256']
                previous=hashlib.sha256(line).hexdigest()
            assert summary['last_record_sha256']==previous;passed('private original record chain and request response correlation independently checked')
            assert (root/'fresh.wire.jsonl').stat().st_mode&0o777==0o600
            assert 'frame_base64' not in json.dumps(events) and any(e['phase']=='wire-sent' for e in events)
            passed('public events disclose digests only and distinguish captured from sent')
            refuses('existing private wire leaf never replaced',lambda:W.WireJournal(tmp,selected,'fresh',events.append))
            assert (root/'fresh.wire.jsonl').read_bytes()==content
        finally:J.close()
    with tempfile.TemporaryDirectory(prefix='cal-T06-wire-parent-') as tmp:
        parent=Path(tmp);root=parent/'cal-T06-root'
        # Wire custody contract deliberately requires the independently selected direct /tmp root.
        root.mkdir(mode=0o700)
        refuses('unselected nested private root refuses',lambda:W.WireJournal(root,root_identity(root),'fresh',lambda _:None))
    with tempfile.TemporaryDirectory(prefix='cal-T06-wire-attachment-') as tmp:
        root=Path(tmp);selected=root_identity(root);J=W.WireJournal(root,selected,'fresh',lambda _:None)
        retained=root.with_name(root.name+'-retained')
        try:
            root.rename(retained);root.mkdir(mode=0o700)
            refuses('late private root replacement refuses',lambda:J.capture(b'{}\n',direction='inbound',phase='startup',stage='received-before-parse'))
            assert not list(root.iterdir())
        finally:
            J.close();root.rmdir();retained.rename(root)
    assert len(os.listdir('/proc/self/fd'))==fd0;passed('all wire capture refusal and private descriptor paths balanced')
    return results
