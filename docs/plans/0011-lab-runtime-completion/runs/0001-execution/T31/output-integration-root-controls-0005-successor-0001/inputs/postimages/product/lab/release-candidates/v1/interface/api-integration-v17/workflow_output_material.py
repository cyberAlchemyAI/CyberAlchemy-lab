"""Private late output slots, restricted to this actual invocation's owned files.

The independently selected resolver returns original paths/headers after the
producer returns. It grants no access through public messages or Vault.material.
"""
import ast,copy,hashlib,inspect,json,os,re,stat,sys,types
from pathlib import Path
from .protocol import ROOT,HERE
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
    def input_attached(self,links,root_fd):
        """Required input custody supplements all held attachment checks."""
        self.attached(links)
        expected=self.descriptor['output_custody']['identity'];inside=False
        for parent,name,held,identity in links:
            if parent==root_fd:inside=True
            selected=os.fstat(held);named=os.stat(name,dir_fd=parent,follow_symlinks=False)
            need((selected.st_dev,selected.st_ino)==(named.st_dev,named.st_ino)==identity,'selected private input attachment changed')
            if inside or held==root_fd:
                need(selected.st_uid==named.st_uid==os.getuid() and stat.S_IMODE(selected.st_mode)==stat.S_IMODE(named.st_mode)==0o700,'selected private input root/intermediate custody changed')
        s=os.fstat(root_fd)
        need([s.st_dev,s.st_ino,s.st_uid,stat.S_IMODE(s.st_mode)]==expected and expected[2:]==[os.getuid(),0o700],'selected private input root custody changed')

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
                fd=root
                for part in prefix.parts:
                    parent=fd;child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
                    held=os.fstat(child);selected=(held.st_dev,held.st_ino);named=os.stat(part,dir_fd=parent,follow_symlinks=False)
                    need((named.st_dev,named.st_ino)==selected,'selected output prefix detached while opening')
                    links.append((parent,part,child,selected));fd=child
                self.attached(links);walk(fd,prefix);self.attached(links)
            self.attached(links);return rows
        finally:
            for held in reversed(handles):os.close(held)
    def begin(self):
        need(self.before is None,'original output snapshot cannot be replaced');self.before=self.snapshot()
    def capture(self,row,*,input_identity=None):
        closed(row,('path','original_binding'));path=relative(row['path']);binding=row['original_binding'];closed(binding,('ref','sha256'))
        need(type(binding['ref'])is str and binding['ref'] and type(binding['sha256'])is str and re.fullmatch('[a-f0-9]{64}',binding['sha256']),'exact produced original binding required')
        need(self.before is not None and row['path'] not in self.before,'selected material was already present before this invocation')
        root,handles,links,roots=self.root_fd()
        def stamp(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
        try:
            need(any(path.is_relative_to(prefix) for prefix in roots),'private output is outside selected original output roots')
            parent=root
            for part in path.parts[:-1]:
                child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child);s=os.fstat(child)
                if input_identity is not None:need(s.st_uid==os.getuid() and stat.S_IMODE(s.st_mode)==0o700,'owned private input directory differs')
                links.append((parent,part,child,(s.st_dev,s.st_ino)));parent=child
            leaf_parent=parent;fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=leaf_parent);handles.append(fd);before=os.fstat(fd)
            need(stat.S_ISREG(before.st_mode) and before.st_uid==os.getuid() and before.st_size<=16*1024*1024,'bounded owned original produced file required')
            if input_identity is not None:need([before.st_dev,before.st_ino,before.st_uid,stat.S_IMODE(before.st_mode)]==input_identity and input_identity[2:]==[os.getuid(),0o600],'independently selected private input identity/mode differs')
            chunks=[];size=0
            while block:=os.read(fd,min(1024*1024,16*1024*1024-size+1)):
                size+=len(block);need(size<=before.st_size and size<=16*1024*1024,'original produced file grew');chunks.append(block)
            raw=b''.join(chunks);need(size==before.st_size and sha(raw)==binding['sha256'] and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'produced original changed/detached')
            self.attached(links)
            if input_identity is not None:self.input_attached(links,root)
            need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'produced original changed before return');return raw
        finally:
            for held in reversed(handles):os.close(held)
    def close(self,capsule,route_rows,carriers):
        need(self.materials is None and not capsule.pending,'only completed actual original result can close one output slot')
        self.guard();selected_resolver(self.resolver,self.descriptor,self.read_public,self.source_rows)
        actual=self.resolver(capsule.private_view());closed(actual,('schema_version','slots','action_receipts','authority_effect'))
        need(actual['schema_version']=='lab-private-produced-workflow-material/v2-candidate' and actual['authority_effect']=='none','closed private produced material required')
        need(type(actual['slots'])is dict and set(actual['slots'])=={r['output_slot_ref'] for r in route_rows.values()},'complete exact invocation output slots required')
        material={'slots':{},'action_receipts':[]};total=0
        for ref,row in route_rows.items():
            slot=[];seen=set()
            for value in actual['slots'][row['output_slot_ref']]:
                closed(value,('artifact','path','original_binding','scope_proof'));raw=self.capture({k:value[k] for k in ('path','original_binding')});h=value['artifact']
                need(h['byte_sha256']==value['original_binding']['sha256'] and contains_original(capsule.value,h),'output header/bytes absent from actual original result')
                carriers.output(h,raw,scope_ref=row['output_scope_ref'],transition_ref=ref,scope_proof=value['scope_proof'],invocation_lineage={'run_binding':capsule.run_binding,'work_ref':capsule.work_ref,'source_cut':capsule.source_cut,'principal_ref':capsule._authorization.packet['principal_ref']});need(h['version_ref'] not in seen,'duplicate actual output revision');seen.add(h['version_ref'])
                total+=len(raw);need(total<=64*1024*1024,'bounded completed output capsule required')
                slot.append({'artifact':copy.deepcopy(h),'path':value['path'],'original_binding':copy.deepcopy(value['original_binding']),'scope_proof':copy.deepcopy(value['scope_proof']),'raw':raw})
            from .workflow_output_registry import selected_transition
            need({r['artifact']['carrier_ref'] for r in slot}==set(selected_transition(ref)['output_carriers']),'complete original transition output categories required')
            material['slots'][row['output_slot_ref']]=slot
        need(type(actual['action_receipts'])is list and actual['action_receipts'],'actual original action receipt required')
        for row in actual['action_receipts']:
            raw=self.capture(row)
            observed=parse(raw)
            if type(observed)is dict:
                for key,expected in [('run_binding',capsule.run_binding),('work_ref',capsule.work_ref),('source_cut',capsule.source_cut)]:
                    if key in observed:need(observed[key]==expected,'actual producer receipt differs from expected capsule: '+key)
            need(contains_receipt(capsule.value,row['original_binding'],raw),'receipt absent from actual original producer result')
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


# A separate trusted bootstrap capability. Public Vault.material and public API
# messages never obtain a selector into this owned late-input custody.
class LateInvocation:
    __slots__=('owner','ref','selector','packet','seal','used','routes')
    def __init__(self,owner,ref,selector,packet):
        self.owner=owner;self.ref=ref;self.selector=copy.deepcopy(selector);self.packet=copy.deepcopy(packet)
        self.seal=sha(json.dumps(packet,sort_keys=True,separators=(',',':'),allow_nan=False).encode());self.used=False;self.routes=None
    def guard(self):
        need(sha(json.dumps(self.packet,sort_keys=True,separators=(',',':'),allow_nan=False).encode())==self.seal,'late invocation packet mutated')
        need(self.owner.read(self.selector)==self.owner.originals[self.seal],'selected late invocation detached/changed')
    def material(self,binding):
        self.guard();matches=[r for r in self.packet['materials']if r['binding']==binding]
        need(len(matches)==1,'material is not selected by this one actual invocation')
        return self.owner.read(matches[0]['selector'])


class LateInvocationInputs:
    """Exact owned inputs selected after their real predecessor exists.

    This capability is installed only by the selected private bootstrap. It
    grants no effect permission and constructs no Service, authority or lease.
    """
    def __init__(self,host,plan,*,guard,read_public,source_rows):
        self.host=host;self.plan=copy.deepcopy(plan);self.host_guard=guard;self.read_public=read_public;self.source_rows=frozenset(source_rows)
        self.descriptor=copy.deepcopy(plan['invocation_inputs']);self.claims={};self.originals={};self.active=None
        closed(self.descriptor,('schema_version','resolver_binding','resolver_entrypoint','assembler_binding','assembler_entrypoint','custody','phase_contracts'))
        need(self.descriptor['schema_version']=='lab-private-late-workflow-inputs/v1-candidate' and set(self.descriptor['phase_contracts'])==set(plan['transitions']),'complete all28 late input contracts required')
    def read(self,selector):
        closed(selector,('path','identity','sha256'));c=self.descriptor['custody'];path=relative(selector['path'])
        need(any(path.is_relative_to(relative(r))for r in c['output_roots']),'late input outside preselected custody prefix')
        # Reuse the complete held original-file reader, with explicit input
        # mode/identity and owned intermediate directories. No bytes are cached.
        reader=object.__new__(PrivateOutputMaterial);reader.host=self.host;reader.host_guard=self.host_guard
        reader.descriptor={'output_custody':copy.deepcopy(c)};reader.before={}
        return reader.capture({'path':selector['path'],'original_binding':{'ref':'late-input:'+selector['path'],'sha256':selector['sha256']}},input_identity=selector['identity'])
    def resolve(self,ref,selector):
        self.host_guard();need(ref in self.plan['transitions'],'unknown late invocation phase')
        row=self.plan['transitions'][ref];group=row['invocation_ref'];need(group not in self.claims,'late invocation resolution is one-shot; inspect/reconcile retained claim')
        need(_input_claim(self,group,'intent')is None,'durable invocation intent exists; inspect/reconcile, never redispatch')
        raw=self.read(selector);p=parse(raw)
        from jsonschema import Draft202012Validator
        Draft202012Validator(parse((HERE/'workflow-output-plan.schema.json').read_bytes())['$defs']['late_invocation']).validate(p)
        closed(p,('schema_version','invocation_ref','transition_refs','principal_ref','scope_ref','source_cut','run_binding','work_ref','producer_binding','producer_entrypoint','producer_control_binding','scope_contract_bindings','input_seal','object_lineage','run_material_binding','materials','authority_effect'))
        need(p['schema_version']=='lab-private-late-workflow-invocation/v1-candidate' and p['authority_effect']=='none','closed actual late input packet required')
        refs={r for r,d in self.plan['transitions'].items()if d['invocation_ref']==group}
        need(set(p['transition_refs'])==refs and len(p['transition_refs'])==len(refs) and p['invocation_ref']==group,'late input group/phase differs')
        need(p['principal_ref']==self.plan['principal_ref'] and p['scope_ref']==self.plan['scope_ref'] and p['source_cut']==self.plan['source_cut'],'late input principal/scope/cut differs')
        need(p['producer_binding']==row['producer_binding'] and p['producer_entrypoint']==row['producer_entrypoint'],'late callable differs from static selection')
        need(type(p['materials'])is list and p['materials'],'actual selected private inputs required')
        bindings=[]
        for material in p['materials']:
            closed(material,('binding','selector'));closed(material['binding'],('ref','sha256'));closed(material['selector'],('path','identity','sha256'))
            need(material['binding']['sha256']==material['selector']['sha256'],'late snapshot cannot reinterpret original bytes');bindings.append((material['binding']['ref'],material['binding']['sha256']))
        need(len(set(bindings))==len(bindings),'duplicate late original material')
        cap=LateInvocation(self,ref,selector,p);self.originals[cap.seal]=raw
        # Claims are retained before resolving any dependent private material.
        self.claims[group]=cap;self.active=cap
        try:
            for material in p['materials']:cap.material(material['binding'])
            run=parse(cap.material(p['run_material_binding']));need(p['run_material_binding']==p['run_binding'],'actual original run binding differs')
            need(self.host.schemas.protocol_valid('urn:cyberalchemy-lab:protocol:workflow-run:v1-candidate',run),'actual original WorkflowRun schema differs')
            need(run['work']['version_ref']==p['work_ref'] and run['source_cut']==p['source_cut'] and run['actor']['principal_ref']==p['principal_ref'] and run['authority_effect']=='none','actual run Work/cut/actor differs')
            expected=self.plan['transitions'][ref];phase=self.descriptor['phase_contracts'][ref]
            control=None if p['producer_control_binding']is None else parse(cap.material(p['producer_control_binding']))
            need((control is None)==(phase['producer_control_schema_version']is None)and(control is None or control['schema_version']==phase['producer_control_schema_version']),'late private control has missing/unselected phase schema')
            if phase['API_operation']is not None:need(control['operation']==phase['API_operation'],'late original operation differs')
            from .workflow_output_registry import selected_transition
            need(run['definition_binding']['sha256']==selected_transition(ref)['definition_binding']['sha256'],'late run original definition differs')
            cap.routes={r:dict(copy.deepcopy(self.plan['transitions'][r]),producer_control_binding=p['producer_control_binding'],scope_contract_binding=p['scope_contract_bindings'].get(r))for r in refs}
            need(set(p['scope_contract_bindings'])==refs,'complete late scope contract slots required')
            cap.guard();return cap
        except BaseException:
            # Unknown/invalid prepared state is retained. No automatic second
            # selection or producer retry can replace the same group claim.
            raise
    def material(self,binding):
        need(self.active is not None,'no actual selected private invocation material')
        return self.active.material(binding)
    def activate(self,cap):
        need(type(cap)is LateInvocation and cap.owner is self and self.claims.get(cap.packet['invocation_ref'])is cap,'foreign invocation capsule')
        cap.guard();self.active=cap


def private_material(host,binding):
    """Only the selected current invocation's sealed input set; no Vault widening."""
    reader=getattr(host,'workflow_invocation_inputs',None)
    need(type(reader)is LateInvocationInputs and reader.host is host,'trusted late private input capability unavailable')
    return reader.material(binding)


def _input_claim(reader,group,suffix,raw=None):
    """Fixed derived owned intent/observation leaves, never ambient discovery."""
    need(suffix in('intent','completed'),'closed technical claim leaf required');reader.host_guard()
    c=reader.descriptor['custody'];probe=object.__new__(PrivateOutputMaterial);probe.host_guard=reader.host_guard;probe.descriptor={'output_custody':copy.deepcopy(c)}
    root,handles,links,_=probe.root_fd();leaf=None
    try:
        parent=os.open('claims',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=root);handles.append(parent);st=os.fstat(parent)
        need(st.st_uid==os.getuid()and stat.S_IMODE(st.st_mode)==0o700,'preselected private claim directory differs');links.append((root,'claims',parent,(st.st_dev,st.st_ino)))
        name=sha(group.encode())+'.'+suffix+'.json';probe.attached(links)
        if raw is None:
            try:leaf=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
            except FileNotFoundError:probe.attached(links);return None
            before=os.fstat(leaf);need(stat.S_ISREG(before.st_mode)and before.st_uid==os.getuid()and stat.S_IMODE(before.st_mode)==0o600 and before.st_size<=1024*1024,'bounded owned technical claim required')
            chunks=[];size=0
            while block:=os.read(leaf,65536):size+=len(block);need(size<=before.st_size,'technical claim grew');chunks.append(block)
            content=b''.join(chunks);after=os.stat(name,dir_fd=parent,follow_symlinks=False)
            stamp=lambda s:(s.st_dev,s.st_ino,s.st_uid,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
            need(size==before.st_size and stamp(before)==stamp(os.fstat(leaf))==stamp(after),'technical claim detached/changed');probe.attached(links);return content
        leaf=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=parent);os.fchmod(leaf,0o600);before=os.fstat(leaf);offset=0
        while offset<len(raw):
            count=os.write(leaf,raw[offset:]);need(count>0,'technical claim write stalled');offset+=count
        os.fsync(leaf);after=os.stat(name,dir_fd=parent,follow_symlinks=False)
        need((before.st_dev,before.st_ino)==(after.st_dev,after.st_ino)and after.st_size==len(raw),'technical claim detached');probe.attached(links);os.fsync(parent)
        return raw
    finally:
        if leaf is not None:os.close(leaf)
        for fd in reversed(handles):os.close(fd)


def consume_inputs(reader,cap):
    cap.guard();need(type(cap)is LateInvocation and cap.owner is reader and not cap.used,'one-shot prepared invocation required')
    p=cap.packet;intent={'schema_version':'lab-private-workflow-invocation-intent/v1-candidate','invocation_ref':p['invocation_ref'],'selector':cap.selector,'packet_seal':cap.seal,'run_binding':p['run_binding'],'work_ref':p['work_ref'],'source_cut':p['source_cut'],'principal_ref':p['principal_ref'],'input_seal':p['input_seal'],'producer_binding':p['producer_binding'],'producer_entrypoint':p['producer_entrypoint'],'state':'reconciliation-required','redispatch_allowed':False,'authority_effect':'none'}
    _input_claim(reader,p['invocation_ref'],'intent',json.dumps(intent,sort_keys=True,separators=(',',':'),allow_nan=False).encode());cap.used=True


def completion_bytes(reader,cap,result):
    """Exact technical observation expected from this one held invocation."""
    cap.guard();need(type(cap)is LateInvocation and cap.owner is reader and cap.used,'consumed own invocation required')
    p=cap.packet;intent=_input_claim(reader,p['invocation_ref'],'intent')
    expected={'schema_version':'lab-private-workflow-invocation-intent/v1-candidate','invocation_ref':p['invocation_ref'],'selector':cap.selector,'packet_seal':cap.seal,'run_binding':p['run_binding'],'work_ref':p['work_ref'],'source_cut':p['source_cut'],'principal_ref':p['principal_ref'],'input_seal':p['input_seal'],'producer_binding':p['producer_binding'],'producer_entrypoint':p['producer_entrypoint'],'state':'reconciliation-required','redispatch_allowed':False,'authority_effect':'none'}
    need(intent is not None and intent==json.dumps(expected,sort_keys=True,separators=(',',':'),allow_nan=False).encode(),'exact durable initial invocation intent missing/changed')
    need(not result.pending and result.material.materials is not None and result.material.digest()==result.material.seal,'completed sealed actual material required')
    value={'schema_version':'lab-private-workflow-invocation-completed/v1-candidate','invocation_ref':p['invocation_ref'],'packet_seal':cap.seal,'intent_sha256':sha(intent),'result_seal':result.seal,'material_seal':result.material.seal,'state':'completed-sealed','producer_redispatched':False,'authority_effect':'none'}
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def verify_completed_inputs(reader,cap,result):
    """Read-only selection never creates or repairs completion state."""
    raw=completion_bytes(reader,cap,result)
    need(_input_claim(reader,cap.packet['invocation_ref'],'completed')==raw,'known output capture completion requires explicit retained reconciliation')
    return {'ref':'private-workflow-invocation:'+cap.packet['invocation_ref']+':completed','sha256':sha(raw)}


def complete_inputs(reader,cap,result):
    """Idempotent technical completion only; never dispatch or grant an effect."""
    raw=completion_bytes(reader,cap,result);group=cap.packet['invocation_ref'];existing=_input_claim(reader,group,'completed')
    if existing is None:_input_claim(reader,group,'completed',raw)
    else:need(existing==raw,'foreign/partial completion requires explicit retained reconciliation')
    return verify_completed_inputs(reader,cap,result)
