"""Fixed Stage2 helpers. Import has no proc/socket/filesystem effects."""
import array
import base64
import binascii
import hashlib
import json
import os
import select
import socket
import stat
import time


class Refusal(Exception):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode()


def closed(value, fields):
    need(type(value) is dict and set(value) == set(fields.split()), 'SCHEMA')


def number(value, low=0, high=(1 << 63)-1):
    need(type(value) is int and low <= value <= high, 'NUMBER')


def hex64(value):
    need(type(value) is str and len(value)==64 and all(x in '0123456789abcdef' for x in value), 'DIGEST')


def decode(raw, maximum=8192):
    need(type(raw) is bytes and 0 < len(raw) <= maximum, 'BYTES_BOUND')
    def pairs(rows):
        out={}
        for k,v in rows:
            need(k not in out, 'DUPLICATE_KEY');out[k]=v
        return out
    try:
        value=json.loads(raw, object_pairs_hook=pairs,
                         parse_constant=lambda _: need(False,'NONFINITE'))
        need(encode(value)==raw,'NONCANONICAL')
        return value
    except Refusal:raise
    except (ValueError,TypeError,UnicodeError,RecursionError,OverflowError):
        raise Refusal('JSON') from None


def identity(st):
    return [st.st_dev,st.st_ino,st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode)]


def read_regular(path, maximum, *, proc_link=False):
    flags=os.O_RDONLY|os.O_CLOEXEC|os.O_NONBLOCK
    if not proc_link:flags|=os.O_NOFOLLOW
    fd=os.open(path,flags)
    try:
        a=os.fstat(fd);need(stat.S_ISREG(a.st_mode),'REGULAR_FILE')
        out=bytearray()
        while True:
            chunk=os.read(fd,min(65536,maximum+1-len(out)))
            if not chunk:break
            out.extend(chunk);need(len(out)<=maximum,'FILE_BOUND')
        b=os.fstat(fd)
        need((identity(a),a.st_size,a.st_mtime_ns,a.st_ctime_ns)==
             (identity(b),b.st_size,b.st_mtime_ns,b.st_ctime_ns),'FILE_DRIFT')
        return bytes(out),identity(a)
    finally:os.close(fd)


def check_binding(row):
    closed(row,'path sha256 size_bytes');hex64(row['sha256']);number(row['size_bytes'],0,64*1024*1024)
    need(type(row['path']) is str and row['path'].startswith('/'),'BINDING_PATH')
    raw,ident=read_regular(row['path'],row['size_bytes'])
    need(len(raw)==row['size_bytes'] and sha(raw)==row['sha256'],'BINDING_DRIFT')
    return raw,ident


def parse_stat(raw):
    need(type(raw) is bytes and len(raw)<=4096,'STAT_BOUND')
    try:
        end=raw.rindex(b')');start=raw.index(b'(')
        pid=int(raw[:start].strip());f=raw[end+2:].split()
        need(len(f)>=20,'STAT_FIELDS')
        values={'pid':pid,'ppid':int(f[1]),'pgrp':int(f[2]),'session':int(f[3]),'start':int(f[19])}
        for k,v in values.items():number(v,1 if k in ('pid','start') else 0)
        need(f[0] in (b'R',b'S',b'D',b'Z',b'T',b't',b'X',b'I',b'P'),'STAT_STATE')
        values['state']=f[0].decode();return values
    except Refusal:raise
    except (ValueError,IndexError,UnicodeError):raise Refusal('STAT_PARSE') from None


def parse_status(raw):
    need(type(raw) is bytes and len(raw)<=65536,'STATUS_BOUND')
    wanted={'PPid','NSpid','Uid','Gid','CapInh','CapPrm','CapEff','CapBnd','CapAmb','NoNewPrivs'}
    out={}
    try:
        for line in raw.decode('ascii').splitlines():
            key,sep,value=line.partition(':')
            if key not in wanted:continue
            need(sep and key not in out,'STATUS_DUPLICATE')
            parts=value.split()
            if key.startswith('Cap'):
                need(len(parts)==1 and len(parts[0])==16 and all(c in '0123456789abcdef' for c in parts[0]),'CAPS')
                out[key]=parts[0]
            else:
                need(all(p.isdecimal() for p in parts),'STATUS_INTEGER')
                vals=[int(p) for p in parts]
                if key in ('Uid','Gid'):need(len(vals)==4,'IDS')
                elif key=='NSpid':need(1<=len(vals)<=32,'NSPID')
                else:need(len(vals)==1,'STATUS_SCALAR')
                for n in vals:number(n,0,(1<<32)-2)
                out[key]=vals
        need(set(out)==wanted and out['NoNewPrivs'][0] in (0,1),'STATUS_REQUIRED')
        return out
    except Refusal:raise
    except (UnicodeError,ValueError):raise Refusal('STATUS_PARSE') from None


def parse_map(raw):
    need(type(raw) is bytes and 0<len(raw)<=4096,'MAP_BOUND')
    rows=[];ranges=[[],[]]
    try:
        lines=raw.decode('ascii').splitlines();need(1<=len(lines)<=64,'MAP_COUNT')
        for line in lines:
            words=line.split();need(len(words)==3 and all(w.isdecimal() for w in words),'MAP_ROW')
            row=[int(w) for w in words];need(row[2]>0,'MAP_LENGTH')
            for axis in (0,1):
                lo,hi=row[axis],row[axis]+row[2]
                need(0<=lo<hi<=(1<<32)-1,'MAP_OVERFLOW')
                need(all(hi<=a or lo>=b for a,b in ranges[axis]),'MAP_OVERLAP')
                ranges[axis].append((lo,hi))
            rows.append(row)
        return rows
    except Refusal:raise
    except (ValueError,UnicodeError):raise Refusal('MAP_PARSE') from None


def namespace(pid,name):
    path=f'/proc/{pid}/ns/{name}'
    target=os.readlink(path);need(len(target.encode())<=256,'NS_LINK_BOUND')
    st=os.stat(path)
    return [st.st_dev,st.st_ino]


def proc_observation(pid, originals, label, *, with_exe=True):
    """Read bounded proc originals. Caller owns pidfd/currentness, not this JSON."""
    number(pid,1,(1<<31)-1)
    base=f'/proc/{pid}'
    def capture(name,limit):
        raw,_=read_regular(base+'/'+name,limit)
        key=label+'/'+name
        need(key not in originals,'ORIGINAL_REUSE')
        need(sum(len(x) for x in originals.values())+len(raw)<=4*1024*1024,'ORIGINAL_TOTAL')
        originals[key]=raw
        return raw
    first=parse_stat(capture('stat',4096));status=parse_status(capture('status',65536))
    um=parse_map(capture('uid_map',4096));gm=parse_map(capture('gid_map',4096))
    try:sg=capture('setgroups',64).decode('ascii').strip();need(sg in ('allow','deny'),'SETGROUPS')
    except FileNotFoundError:sg='unavailable'
    nss={n:namespace(pid,n) for n in ('pid','pid_for_children','user','mnt')}
    exe_sha=None;exe_id=None
    if with_exe:
        raw,exe_id=read_regular(base+'/exe',16*1024*1024,proc_link=True);exe_sha=sha(raw)
    post,_=read_regular(base+'/stat',4096)
    need(sum(len(x) for x in originals.values())+len(post)<=4*1024*1024,'ORIGINAL_TOTAL')
    originals[label+'/stat-post']=post
    last=parse_stat(post)
    need(first['pid']==pid and first['start']==last['start'] and first['ppid']==last['ppid'],'PROC_DRIFT')
    need(status['PPid'][0]==first['ppid'] and status['NSpid'][0]==pid,'PROC_JOIN')
    return dict(pid=pid,start=first['start'],ppid=first['ppid'],nspid=status['NSpid'],
                uid=status['Uid'],gid=status['Gid'],namespaces=nss,
                caps={k:status[k] for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')},
                no_new_privs=status['NoNewPrivs'][0],uid_map=um,gid_map=gm,setgroups=sg,
                exe_sha256=exe_sha,exe_identity=exe_id)


def ancestry(pid,wrapper,originals,label):
    rows=[];seen=set()
    for i in range(32):
        need(pid not in seen,'ANCESTRY_CYCLE');seen.add(pid)
        row=proc_observation(pid,originals,f'{label}/{i}',with_exe=(i==0));rows.append(row)
        if pid==wrapper['pid']:
            need(row['start']==wrapper['start'],'WRAPPER_START');return rows
        pid=row['ppid'];need(pid>0,'WRAPPER_NOT_ANCESTOR')
    raise Refusal('ANCESTRY_BOUND')


def stable(row):
    return row  # Only selected stable parsed fields; raw status is retained separately.


def join(controller,before,after,claim,cred,exe_sha,exe_id):
    """Actual acquisition adapter supplies these observations; pure checks here."""
    need(before==after and before,'REPEATED_IDENTITY')
    p=before[0]
    need(cred==[p['pid'],p['uid'][0],p['gid'][0]],'CREDENTIAL_JOIN')
    need(p['nspid'][-1]==1 and len(p['nspid'])>=2,'INNER_PID')
    for name in ('pid','user','mnt'):
        need(p['namespaces'][name]!=controller['namespaces'][name],'UNSHARE_REQUIRED')
    need(p['exe_sha256']==exe_sha and p['exe_identity']==exe_id,'EXECUTABLE_JOIN')
    closed(claim,'pid start ppid nspid uid gid namespaces caps no_new_privs uid_map gid_map setgroups exe_sha256 exe_identity')
    number(claim['start'],1)
    need(claim['start']==p['start'],'CHILD_START')
    need(type(claim['pid']) is int and claim['pid']==1 and type(claim['ppid']) is int and claim['ppid']==0
         and encode(claim['nspid'])==b'[1]','CHILD_PID')
    need(type(claim['exe_identity']) is list and len(claim['exe_identity'])==5,'CHILD_EXE_SHAPE')
    for x in claim['exe_identity']:number(x)
    for name in ('namespaces','caps','no_new_privs','uid_map','gid_map','setgroups','exe_sha256'):
        need(encode(claim[name])==encode(p[name]),'CHILD_'+name.upper())
    need([claim['exe_identity'][i] for i in (0,1,4)]==[p['exe_identity'][i] for i in (0,1,4)],'CHILD_EXECUTABLE_INODE')
    # The selected first probe supports precisely one child user namespace whose
    # direct parent is the controller user namespace; NS_GET_PARENT is captured
    # separately by the controller, not guessed from a uid_map row.
    for field in ('uid','gid'):
        values=[]
        need(type(claim[field]) is list and len(claim[field])==4,'CHILD_IDS')
        for x in claim[field]:
            number(x,0,(1<<32)-2)
            found=[b+x-a for a,b,n in p[field+'_map'] if a<=x<a+n]
            need(len(found)==1,'UNMAPPED_ID');values.append(found[0])
        need(values==p[field],'MAPPED_IDS')
    return sha(encode({'controller':controller,'before':before,'after':after,'claim':claim,'credentials':cred}))


def send_packet(sock,raw):
    need(type(raw) is bytes and 0<len(raw)<=8192,'SEND_BOUND')
    count=sock.send(raw,socket.MSG_NOSIGNAL)
    need(count==len(raw),'SHORT_SEND_UNKNOWN')


def recv_packet(sock, *, allow_eof=False):
    raw,anc,flags,_=sock.recvmsg(8192,socket.CMSG_SPACE(12)+socket.CMSG_SPACE(253*4),socket.MSG_CMSG_CLOEXEC)
    if allow_eof and raw==b'' and not anc and flags==0:return None,None
    tuples=[];bad=False;close_failed=False
    for level,kind,data in anc:
        if level==socket.SOL_SOCKET and kind==socket.SCM_RIGHTS:
            rights=array.array('i');rights.frombytes(data[:len(data)//rights.itemsize*rights.itemsize]);bad=True
            for fd in rights:
                try:os.close(fd)
                except BaseException:close_failed=True
        elif level==socket.SOL_SOCKET and kind==socket.SCM_CREDENTIALS and len(data)==12:
            ints=array.array('i');ints.frombytes(data)
            tuples.append([ints[0],ints[1] & 0xffffffff,ints[2] & 0xffffffff])
        else:bad=True
    need(not close_failed,'RIGHTS_CLOSE_UNKNOWN')
    need(not bad and not flags & (socket.MSG_TRUNC|socket.MSG_CTRUNC) and len(tuples)==1,'ANCILLARY')
    t=tuples[0];number(t[0],0,(1<<31)-1);number(t[1],0,(1<<32)-2);number(t[2],0,(1<<32)-2)
    need(raw,'PEER_EOF');return raw,t


KINDS=('CHALLENGE','HELLO','OBSERVATION','RECEIPT')


def frame(index,nonce,selection,previous,body):
    return encode(dict(schema='lab-mapper-namespace-probe/v3',kind=KINDS[index],ordinal=index,
                       nonce=nonce,selection_sha256=selection,previous_sha256=previous,body=body))


def validate_frame(raw,index,nonce,selection,previous):
    v=decode(raw);closed(v,'schema kind ordinal nonce selection_sha256 previous_sha256 body')
    number(v['ordinal'],0,3);hex64(v['nonce']);hex64(v['selection_sha256'])
    need(v['schema']=='lab-mapper-namespace-probe/v3' and v['kind']==KINDS[index]
         and v['ordinal']==index and v['nonce']==nonce and v['selection_sha256']==selection
         and v['previous_sha256']==previous,'FRAME_CHAIN')
    need(type(v['body']) is dict,'BODY');return v['body']


def census():
    rows=[]
    with os.scandir('/proc/self/fd') as entries:
        for entry in entries:
            need(len(rows)<64,'FD_BOUND')
            try:fd=int(entry.name);st=os.fstat(fd)
            except FileNotFoundError:continue
            except OSError as e:
                if e.errno==9:continue
                raise
            rows.append([fd,stat.S_IFMT(st.st_mode)])
    # scandir itself was present during iteration and has now closed.
    rows=[row for row in rows if row[0] in (0,1,2,3) or _still_open(row[0])]
    need(sorted(x[0] for x in rows)==[0,1,2,3],'FD_CENSUS')
    return sorted(rows)


def _still_open(fd):
    try:os.fstat(fd);return True
    except OSError as e:
        if e.errno==9:return False
        raise


CHILD_FILES = {'stat':4096,'stat-post':4096,'status':65536,
               'uid_map':4096,'gid_map':4096,'setgroups':64}


def pack_child_originals(originals,phase,claim):
    need(phase in ('self-before','self-after'),'CHILD_PHASE')
    files={}
    for name in CHILD_FILES:
        key=phase+'/'+name
        if key not in originals:
            need(name=='setgroups' and claim['setgroups']=='unavailable','CHILD_ORIGINAL_MISSING')
            continue
        raw=originals[key]
        need(type(raw) is bytes and 0<len(raw)<=CHILD_FILES[name],'CHILD_ORIGINAL_BOUND')
        files[name]={'base64':base64.b64encode(raw).decode('ascii'),
                     'sha256':sha(raw),'size_bytes':len(raw)}
    return {'schema':'mapper-child-proc-originals/v1','phase':phase,
            'observer_pidns':claim['namespaces']['pid'],
            'observer_userns':claim['namespaces']['user'],
            'subject_pid':claim['pid'],'subject_start':claim['start'],'files':files}


def verify_child_originals(value,phase,claim):
    closed(value,'schema phase observer_pidns observer_userns subject_pid subject_start files')
    need(value['schema']=='mapper-child-proc-originals/v1' and value['phase']==phase,'CHILD_ORIGINAL_SCHEMA')
    number(value['subject_pid'],1);number(value['subject_start'],1)
    need(value['subject_pid']==claim['pid'] and value['subject_start']==claim['start'],'CHILD_ORIGINAL_SUBJECT')
    for field,nsname in (('observer_pidns','pid'),('observer_userns','user')):
        need(encode(value[field])==encode(claim['namespaces'][nsname]),'CHILD_ORIGINAL_COORDINATES')
    files=value['files'];expected=set(CHILD_FILES)
    if claim['setgroups']=='unavailable':expected.remove('setgroups')
    need(type(files) is dict and set(files)==expected,'CHILD_ORIGINAL_FILES')
    decoded={}
    for name,row in files.items():
        closed(row,'base64 sha256 size_bytes');hex64(row['sha256']);number(row['size_bytes'],1,CHILD_FILES[name])
        need(type(row['base64']) is str and len(row['base64'])<=((CHILD_FILES[name]+2)//3)*4,'CHILD_ORIGINAL_ENCODING')
        try:raw=base64.b64decode(row['base64'],validate=True)
        except (ValueError,binascii.Error):raise Refusal('CHILD_ORIGINAL_ENCODING') from None
        need(base64.b64encode(raw).decode('ascii')==row['base64'] and len(raw)==row['size_bytes']
             and sha(raw)==row['sha256'],'CHILD_ORIGINAL_BINDING')
        decoded[name]=raw
    need(sum(map(len,decoded.values()))<=16384,'CHILD_ORIGINAL_TOTAL')
    first=parse_stat(decoded['stat']);last=parse_stat(decoded['stat-post']);status=parse_status(decoded['status'])
    for st in (first,last):
        need(st['pid']==claim['pid'] and st['start']==claim['start'] and st['ppid']==claim['ppid'],'CHILD_RAW_STAT_JOIN')
    need(status['NSpid']==claim['nspid'] and status['PPid']==[claim['ppid']] and
         status['Uid']==claim['uid'] and status['Gid']==claim['gid'] and
         status['NoNewPrivs']==[claim['no_new_privs']],'CHILD_RAW_STATUS_JOIN')
    need({k:status[k] for k in ('CapInh','CapPrm','CapEff','CapBnd','CapAmb')}==claim['caps'],'CHILD_RAW_CAPS_JOIN')
    need(parse_map(decoded['uid_map'])==claim['uid_map'] and parse_map(decoded['gid_map'])==claim['gid_map'],'CHILD_RAW_MAP_JOIN')
    if 'setgroups' in decoded:
        need(decoded['setgroups'] in (b'allow\n',b'deny\n') and decoded['setgroups'].strip().decode()==claim['setgroups'],'CHILD_RAW_SETGROUPS_JOIN')
    return decoded


def inverse_id(outer,rows,overflow):
    number(outer,0,(1<<32)-2);number(overflow,0,(1<<32)-2)
    # Reuse the exact bounded raw parser so both inner and outer overlap refuse.
    raw=('\n'.join(' '.join(str(x) for x in row) for row in rows)+'\n').encode()
    checked=parse_map(raw)
    matches=[a+outer-b for a,b,n in checked if b<=outer<b+n]
    need(len(matches)<=1,'CONTROLLER_MAP_AMBIGUOUS')
    return matches[0] if matches else overflow


def expected_controller_tuple(controller,child,overflow):
    closed(overflow,'uid gid');number(overflow['uid'],0,(1<<32)-2);number(overflow['gid'],0,(1<<32)-2)
    return [0,inverse_id(controller['uid'][0],child['uid_map'],overflow['uid']),
              inverse_id(controller['gid'][0],child['gid_map'],overflow['gid'])]


def validate_controller_tuple(observed,controller,child,overflow):
    need(type(observed) is list and len(observed)==3,'CONTROLLER_TUPLE')
    for x in observed:number(x,0,(1<<32)-2)
    need(observed==expected_controller_tuple(controller,child,overflow),'CONTROLLER_COORDINATE_JOIN')


def host_join_summary(controller,before,after,claim,creds,exe_sha,exe_id,parent_userns,overflow,controller_tuple,hello_sha):
    hex64(hello_sha)
    need(parent_userns==controller['namespaces']['user'],'USER_PARENT')
    validate_controller_tuple(controller_tuple,controller,before[0],overflow)
    joined=join(controller,before,after,claim,creds,exe_sha,exe_id)
    return {'schema':'mapper-host-join-summary/v1','controller':controller,
            'before':before,'after':after,'payload_claim':claim,'observed_credentials':creds,
            'exe_sha256':exe_sha,'exe_identity':exe_id,'parent_userns':parent_userns,
            'overflow_ids':overflow,'controller_tuple':controller_tuple,
            'hello_sha256':hello_sha,'identity_join_sha256':joined}


def verify_host_join_summary(summary,claim,challenge,controller_tuple,hello_sha,overflow):
    closed(summary,'schema controller before after payload_claim observed_credentials exe_sha256 exe_identity parent_userns overflow_ids controller_tuple hello_sha256 identity_join_sha256')
    need(summary['schema']=='mapper-host-join-summary/v1','HOST_SUMMARY_SCHEMA')
    need(encode(summary['payload_claim'])==encode(claim) and summary['hello_sha256']==hello_sha,'HOST_SUMMARY_PAYLOAD')
    ctrl=summary['controller']
    need(ctrl['pid']==challenge['controller_pid'] and ctrl['start']==challenge['controller_start']
         and encode(ctrl['namespaces'])==encode(challenge['controller_namespaces']),'HOST_SUMMARY_CONTROLLER')
    need(summary['controller_tuple']==controller_tuple and summary['overflow_ids']==overflow,'HOST_SUMMARY_MAPPING')
    rebuilt=host_join_summary(ctrl,summary['before'],summary['after'],claim,
                             summary['observed_credentials'],summary['exe_sha256'],summary['exe_identity'],
                             summary['parent_userns'],overflow,controller_tuple,hello_sha)
    need(encode(rebuilt)==encode(summary),'HOST_SUMMARY_DRIFT')
    return sha(encode(summary))


def validate_child_readback(expected,actual):
    need(type(actual) is dict and set(actual)==set(expected),'CHILD_READBACK_FILES')
    for name,raw in expected.items():
        need(type(actual[name]) is bytes and actual[name]==raw,'CHILD_READBACK_DRIFT')
    return {name:{'sha256':sha(raw),'size_bytes':len(raw)} for name,raw in actual.items()}
