"""Selected original W06 actual input consumer; Source8 attribution stays distinct."""
from pathlib import Path
from .workflow_output_contracts import need,sha
from .protocol import ROOT
import os,stat,sys,re

PATH='implementation/lab-workflows/candidates/v1/learning/application.py'
class W06Consumer:
    def __init__(self,host,*,module,module_binding,application,read_public,host_guard):
        raw=read_public(module_binding)
        need(module_binding['path']==PATH and sha(raw)==module_binding['sha256'] and Path(module.__file__)==ROOT/PATH,'independently selected original W06 module required')
        need(type(application)is module.LessonApplicationService and application.apply.__func__ is module.LessonApplicationService.apply,'actual original LessonApplicationService required')
        self.host=host;self.module=module;self.binding=module_binding;self.application=application;self.read_public=read_public;self.host_guard=host_guard;self.pending=False
    def verify_result(self,selection,lesson_ref,result,*,run_binding,work_ref,source_cut):
        """Observe the already returned original apply once; never dispatch it."""
        need(not self.pending,'W06 result verification is one-shot; retained uncertainty requires reconciliation')
        self.host_guard();need(sha(self.read_public(self.binding))==self.binding['sha256'],'original W06 consumer changed')
        factory=getattr(self,'factory',None);need(factory is not None and factory.host is self.host,'trusted W06 invocation factory required')
        cap=factory.inputs.active;cap.guard()
        need(cap.packet['run_binding']==run_binding and cap.packet['work_ref']==work_ref and cap.packet['source_cut']==source_cut
             and cap.ref==self.transition_ref,'actual selected W06 invocation lineage differs')
        need(type(result)is str and result==self.application.application_ref and self.application.application_ref is not None,'actual original W06 returned application differs')
        self.pending=True
        observed=self.application.observed
        need(type(observed)is dict and observed['controlled'] is True and observed['returncode']==0 and observed['original_source_unchanged'] is True and observed['inline_only_change'] is True and observed['lesson_ref']==lesson_ref and observed['selection_ref']==selection.original_ref and observed['session_ref']==selection.context.session_ref and observed['source_head']==selection.context.source_head,'actual W06 child/input/selection lineage missing')
        repaired=self.application.e.original(observed['repaired_source_ref'])
        need(observed['result']['controlled'] is True and observed['result']['source_sha256']==sha(repaired),'actual W06 child did not consume the exact repaired input')
        manifest=self.application.e.original(self.application.manifest_ref)
        need(self.module.parse(manifest)==observed and observed['stdout_ref'] and observed['stderr_ref'],'actual original child output/manifest bytes differ')
        stdout=self.application.e.original(observed['stdout_ref']);stderr=self.application.e.original(observed['stderr_ref'])
        need(type(stdout)is bytes and type(stderr)is bytes and self.module.parse(stdout)==observed['result'],'actual original child stdout/result bytes differ')
        self.host_guard();need(sha(self.read_public(self.binding))==self.binding['sha256'],'original W06 consumer changed after invocation')
        return {'schema_version':'lab-observed-W06-child-consumption/v1-candidate','application_ref':result,'lesson_ref':lesson_ref,'run_binding':run_binding,'work_ref':work_ref,'source_cut':source_cut,'manifest_sha256':sha(manifest),'repaired_source_sha256':sha(repaired),'stdout_sha256':sha(stdout),'stderr_sha256':sha(stderr),'session_ref':observed['session_ref'],'source_head':observed['source_head'],'actual_child_consumption_verified':True,'producer_redispatched':False,'general_benefit_established':False,'authority_effect':'none'}


def original_learning_outputs(sources,before,module_binding,read_public):
    path='implementation/lab-workflows/candidates/v1/learning/adapter.py'
    need(module_binding['path']==path and sha(read_public(module_binding))==module_binding['sha256'],'original learning adapter code differs')
    module=sys.modules.get(type(sources).__module__)
    need(module is not None and Path(module.__file__)==ROOT/path and type(sources)is module.CandidateSources,'actual original CandidateSources required')
    sources.check();rows=[]
    for ref in sorted(set(sources.records)-set(before)):
        need(sources.roles[ref]=='output','new input cannot masquerade as producer output')
        file,pin=sources.records[ref];value=sources.get(ref)
        # get performs original current-source/schema/authority checks. Capture
        # the exact new record through descriptors without a second pathname
        # body read, preserving no-follow ancestor and leaf attachment checks.
        raw=capture(file,pin)
        need(module.parse(raw)==value,'original learning output changed during capture')
        rows.append({'version_ref':ref,'identity_ref':value['node_id'],'sha256':pin,'original_record':value})
    sources.check();return rows

def capture(path,pin):
    expected_sha256=pin;maximum=16*1024*1024;required_uid=os.getuid()
    path=Path(path)
    need(path.is_absolute() and '..' not in path.parts and path.as_posix()==str(path),'canonical absolute captured origin required')
    need(expected_sha256 is None or type(expected_sha256)is str and re.fullmatch('[a-f0-9]{64}',expected_sha256),'independent exact capture SHA required')
    need(type(maximum)is int and 0<maximum<=32*1024*1024,'bounded capture required')
    handles=[];links=[]
    def directory_identity(s):return (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode)
    def stamp(s):return (*directory_identity(s),s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);handles.append(parent)
        for part in path.parts[1:-1]:
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);handles.append(child)
            selected=directory_identity(os.fstat(child))
            need(directory_identity(os.stat(part,dir_fd=parent,follow_symlinks=False))==selected,'capture ancestor detached while opening')
            links.append((parent,part,child,selected));parent=child
        leaf_parent=parent
        fd=os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=leaf_parent);handles.append(fd);before=os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size<=maximum,'bounded regular captured input required')
        need(required_uid is None or before.st_uid==required_uid,'captured input owner differs')
        parts=[];total=0
        while block:=os.read(fd,min(1024*1024,maximum-total+1)):
            total+=len(block);need(total<=before.st_size and total<=maximum,'captured input grew');parts.append(block)
        raw=b''.join(parts)
        need(total==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'captured file changed/detached')
        need(expected_sha256 is None or sha(raw)==expected_sha256,'independent captured input digest differs')
        for ancestor,name,held,selected in links:
            need(directory_identity(os.stat(name,dir_fd=ancestor,follow_symlinks=False))==directory_identity(os.fstat(held))==selected,'held capture ancestor detached')
        need(stamp(before)==stamp(os.fstat(fd))==stamp(os.stat(path.name,dir_fd=leaf_parent,follow_symlinks=False)),'capture leaf changed before return')
        return raw
    finally:
        for fd in reversed(handles):os.close(fd)
