"""Private late output slots, restricted to this actual invocation's owned files.

The independently selected resolver returns original paths/headers after the
producer returns. It grants no access through public messages or Vault.material.
"""
import ast,copy,hashlib,inspect,json,os,re,stat,sys,types
from pathlib import Path
from .protocol import ROOT
from .workflow_output_contracts import need,closed,parse,sha
from .workflow_output_validation import contains_original


def relative(value):
    need(type(value)is str and value and '\\' not in value and '\0' not in value,'canonical relative output origin required')
    p=Path(value);need(not p.is_absolute() and '..' not in p.parts and p.as_posix()==value and value!='.','canonical relative output origin required')
    return p

def selected_resolver(fn,row,read_public,source_rows):
    b=row['resolver_binding'];raw=read_public(b);need(sha(raw)==b['sha256'] and (b['path'],b['sha256']) in source_rows,'resolver absent/changed in selected Source')
    function=getattr(fn,'__func__',fn);path=ROOT/relative(b['path'])
    need(inspect.isfunction(function) and Path(function.__code__.co_filename)==path and function.__qualname__==row['resolver_entrypoint'],'actual selected private resolver origin differs')
    module=sys.modules.get(function.__module__);need(module is not None and function.__globals__ is module.__dict__ and Path(module.__file__)==path,'actual private resolver globals/module differs')
    parts=function.__qualname__.split('.');need('<locals>' not in parts,'private resolver needs a selected module/class entrypoint')
    registered=module
    for name in parts:registered=getattr(registered,name)
    need(getattr(registered,'__func__',registered)is function,'selected resolver function binding differs')
    if inspect.ismethod(fn):
        owner=module
        for name in parts[:-1]:owner=getattr(owner,name)
        need(type(fn.__self__)is owner or fn.__self__ is owner,'actual selected private resolver object required')
    def codes(code):
        yield code
        for child in code.co_consts:
            if isinstance(child,types.CodeType):yield from codes(child)
    actual=[code for code in codes(compile(raw,str(path),'exec',dont_inherit=True)) if code.co_qualname==function.__qualname__]
    need(len(actual)==1 and actual[0]==function.__code__,'private resolver executable code differs')


def contains_receipt(value,binding,raw):
    """An actual returned binding or exact returned JSON receipt, never a flag."""
    if type(value)is dict:
        if value.get('ref')==binding['ref'] and value.get('sha256')==binding['sha256']:return True
        if value==parse(raw):return True
        return any(contains_receipt(v,binding,raw) for v in value.values() if type(v)in (dict,list,tuple))
    if type(value)in (tuple,list):return any(contains_receipt(v,binding,raw) for v in value)
    return False


class PrivateOutputMaterial:
    def __init__(self,host,descriptor,*,resolver,read_public,host_guard,source_rows):
        self.host=host;self.descriptor=copy.deepcopy(descriptor);self.resolver=resolver;self.read_public=read_public;self.host_guard=host_guard;self.source_rows=frozenset(source_rows)
        self.before=None;self.materials=None;self.seal=None
        self.guard();selected_resolver(resolver,self.descriptor,read_public,self.source_rows)
    def guard(self):
        self.host_guard();c=self.descriptor['output_custody'];root=Path(c['root'])
        need(type(c['root'])is str and root.is_absolute() and c['root']==root.as_posix() and '..' not in root.parts and root.is_relative_to(Path('/tmp')) and not root.is_relative_to(ROOT),'selected owned output custody outside repository required')
        need(type(c['identity'])is list and len(c['identity'])==4 and c['identity'][2]==os.getuid() and c['identity'][3]==0o700,'exact owned output custody identity required')
        roots=[relative(x) for x in c['output_roots']];need(roots and len(roots)==len(set(roots)) and all(not a.is_relative_to(b) for a in roots for b in roots if a!=b),'closed nonoverlapping original output roots required')
        return root,roots
    def root_fd(self):
        root,roots=self.guard();handles=[];links=[]
        try:
            fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(fd)
            for part in root.parts[1:]:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);handles.append(child);st=os.fstat(child)
                links.append((fd,part,child,(st.st_dev,st.st_ino)));fd=child
            st=os.fstat(fd);need([st.st_dev,st.st_ino,st.st_uid,stat.S_IMODE(st.st_mode)]==self.descriptor['output_custody']['identity'],'selected output custody changed')
            return fd,handles,links,roots
        except BaseException:
            for held in reversed(handles):os.close(held)
            raise
    def attached(self,links):
        for parent,name,held,identity in links:
            s=os.stat(name,dir_fd=parent,follow_symlinks=False);h=os.fstat(held)
            need((s.st_dev,s.st_ino)==(h.st_dev,h.st_ino)==identity,'owned output custody/ancestor detached')
    def snapshot(self):
        root,handles,links,roots=self.root_fd();rows={}
        def walk(fd,prefix):
            need(len(prefix.parts)<=32,'bounded owned output depth required')
            for name in sorted(os.listdir(fd)):
                relative(name);s=os.stat(name,dir_fd=fd,follow_symlinks=False);path=(prefix/name).as_posix()
                if stat.S_ISDIR(s.st_mode):
                    child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd)
                    try:
                        held=os.fstat(child);need((held.st_dev,held.st_ino)==(s.st_dev,s.st_ino),'output subtree changed while opening');walk(child,prefix/name)
                        after=os.stat(name,dir_fd=fd,follow_symlinks=False);need((held.st_dev,held.st_ino)==(after.st_dev,after.st_ino),'output subtree detached')
                    finally:os.close(child)
                else:
                    need(stat.S_ISREG(s.st_mode) and s.st_uid==os.getuid(),'owned output metadata includes unsupported/symlink/nonowned file')
                    rows[path]=(s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
                    need(len(rows)<=10000,'bounded original output custody required')
        try:
            for prefix in roots:
                fd=root;opened=[]
                try:
                    for part in prefix.parts:
                        fd=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=fd);opened.append(fd)
                    walk(fd,prefix)
                finally:
                    for held in reversed(opened):os.close(held)
            self.attached(links);return rows
        finally:
            for held in reversed(handles):os.close(held)
    def begin(self):
        need(self.before is None,'original output snapshot cannot be replaced');self.before=self.snapshot()
    def capture(self,row):
        closed(row,('path','original_binding'));path=relative(row['path']);binding=row['original_binding'];closed(binding,('ref','sha256'))
        need(type(binding['ref'])is str and binding['ref'] and type(binding['sha256'])is str and re.fullmatch('[a-f0-9]{64}',binding['sha256']),'exact produced original binding required')
        need(self.before is not None and row['path'] not in self.before,'selected material was already present before this invocation')
        root,handles,links,roots=self.root_fd()
        def stamp(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        try:
            need(any(path.is_relative_to(prefix) for prefix in roots),'private output is outside selected original output roots')
            parent=root
            for part in path.parts[:-1]:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child);s=os.fstat(child);links.append((parent,part,child,(s.st_dev,s.st_ino)));parent=child
            leaf_parent=parent;fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=leaf_parent);handles.append(fd);before=os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_size<=16*1024*1024,'bounded owned original produced file required')
            chunks=[];size=0
            while block:=os.read(fd,min(1024*1024,16*1024*1024-size+1)):
                size+=len(block);need(size<=before.st_size and size<=16*1024*1024,'original produced file grew');chunks.append(block)
            raw=b''.join(chunks);need(size==before.st_size and sha(raw)==binding['sha256'] and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'produced original changed/detached')
            self.attached(links);need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'produced original changed before return');return raw
        finally:
            for held in reversed(handles):os.close(held)
    def close(self,capsule,route_rows,carriers):
        need(self.materials is None and not capsule.pending,'only completed actual original result can close one output slot')
        self.guard();selected_resolver(self.resolver,self.descriptor,self.read_public,self.source_rows)
        actual=self.resolver(capsule.private_view());closed(actual,('schema_version','slots','action_receipts','authority_effect'))
        need(actual['schema_version']=='lab-private-produced-workflow-material/v1-candidate' and actual['authority_effect']=='none','closed private produced material required')
        need(type(actual['slots'])is dict and set(actual['slots'])=={r['output_slot_ref'] for r in route_rows.values()},'complete exact invocation output slots required')
        material={'slots':{},'action_receipts':[]};total=0
        for ref,row in route_rows.items():
            slot=[];seen=set()
            for value in actual['slots'][row['output_slot_ref']]:
                closed(value,('artifact','path','original_binding'));raw=self.capture({k:value[k] for k in ('path','original_binding')});h=value['artifact']
                need(h['byte_sha256']==value['original_binding']['sha256'] and contains_original(capsule.value,h),'output header/bytes absent from actual original result')
                carriers.output(h,raw,scope_ref=row['output_scope_ref']);need(h['version_ref'] not in seen,'duplicate actual output revision');seen.add(h['version_ref'])
                total+=len(raw);need(total<=64*1024*1024,'bounded completed output capsule required')
                slot.append({'artifact':copy.deepcopy(h),'path':value['path'],'original_binding':copy.deepcopy(value['original_binding']),'raw':raw})
            from .workflow_output_registry import selected_transition
            need({r['artifact']['carrier_ref'] for r in slot}==set(selected_transition(ref)['output_carriers']),'complete original transition output categories required')
            material['slots'][row['output_slot_ref']]=slot
        need(type(actual['action_receipts'])is list and actual['action_receipts'],'actual original action receipt required')
        for row in actual['action_receipts']:
            raw=self.capture(row);need(contains_receipt(capsule.value,row['original_binding'],raw),'receipt absent from actual original producer result')
            material['action_receipts'].append({**copy.deepcopy(row),'raw':raw})
        self.guard();selected_resolver(self.resolver,self.descriptor,self.read_public,self.source_rows)
        self.materials=material;self.seal=self.digest();return self
    def digest(self):
        def safe(value):
            if type(value)is bytes:return {'original_bytes_sha256':sha(value)}
            if type(value)is dict:return {k:safe(v) for k,v in value.items()}
            if type(value)is list:return [safe(v) for v in value]
            return value
        return sha(json.dumps(safe(self.materials),sort_keys=True,separators=(',',':'),allow_nan=False).encode())
    def selected(self,slot):
        self.guard();need(self.materials is not None and self.digest()==self.seal,'sealed original output capsule missing/changed')
        for row in self.materials['slots'][slot]+self.materials['action_receipts']:
            need(self.capture({k:row[k] for k in ('path','original_binding')})==row['raw'],'sealed produced original no longer matches actual bytes')
        self.guard();return copy.deepcopy(self.materials['slots'][slot]),copy.deepcopy(self.materials['action_receipts'])
