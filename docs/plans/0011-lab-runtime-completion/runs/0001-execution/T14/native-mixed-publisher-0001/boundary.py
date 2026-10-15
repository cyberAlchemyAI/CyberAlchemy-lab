"""Current independently granted Source/cut/permission boundary, held to commit."""
from datetime import datetime,timezone
import copy,fcntl,os,stat,re
from .contracts import closed,need,compact,pin

class PublicationBoundary:
    def __init__(self,software,source_guard,cut_reader,permission_guard,owner_guard,control,*,independent_control_sha256,locks):
        fields=('schema_version','source_binding','profile_binding','source_cut','principal_ref','work_ref','native_store_ref','native_branch_ref','operation','permission_snapshot','expires_at','authority_effect')
        closed(control,fields);need(control['schema_version']=='lab-mixed-native-current-boundary/v1-candidate' and control['authority_effect']=='none','closed independent current boundary required')
        from .contracts import sha
        need(sha(compact(control))==independent_control_sha256,'independent boundary control changed')
        for field in ('source_binding','profile_binding'):
            closed(control[field],('ref','sha256'));pin(control[field]['sha256'])
        need(type(control['permission_snapshot'])is dict and bool(control['permission_snapshot']),'actual explicit permission snapshot required')
        need(type(locks)is tuple and locks,'independent existing source/permission lock descriptors required')
        self.software=software;self.source_guard=source_guard;self.cut_reader=cut_reader;self.permission_guard=permission_guard;self.owner_guard=owner_guard
        self.control=copy.deepcopy(control);self.seal=compact(control);self.locks=locks;self.held=False
        self.guard()
    def guard(self):
        need(compact(self.control)==self.seal,'independent current control mutated');self.software.guard()
        self.software.function(self.source_guard)()
        self.software.function(self.owner_guard)()
        need(self.software.function(self.cut_reader)()==self.control['source_cut'],'actual current Source cut differs')
        need(self.software.function(self.permission_guard)()==self.control['permission_snapshot'],'actual original permission selection differs')
        need(type(self.control['expires_at'])is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|\+00:00)',self.control['expires_at']),'actual UTC deadline syntax required')
        try:expiry=datetime.fromisoformat(self.control['expires_at'].replace('Z','+00:00'))
        except (ValueError,AttributeError):need(False,'actual UTC deadline required')
        need(expiry.tzinfo is not None and expiry.utcoffset().total_seconds()==0 and datetime.now(timezone.utc)<expiry,'original actual boundary expired')
        for fd,identity,mode in self.locks:
            info=os.fstat(fd)
            need(type(identity)is tuple and (info.st_dev,info.st_ino,info.st_uid,stat.S_IMODE(info.st_mode))==identity and stat.S_ISREG(info.st_mode) and info.st_uid==os.getuid() and stat.S_IMODE(info.st_mode)==0o600 and mode in (fcntl.LOCK_SH,fcntl.LOCK_EX),'actual selected source/permission lock differs')
    def hold(self):return HeldBoundary(self)
    def require_held(self):need(self.held,'current source/permission/owner publication boundary must remain held');self.guard()

class OwnerPublicationGuard:
    def __init__(self,ingress,review,response,selection,trust):
        self.ingress=ingress;self.review=copy.deepcopy(review);self.response=copy.deepcopy(response)
        self.selection=selection;self.trust=trust
        self.seal=compact({'review':self.review,'response':self.response})
    def check(self):
        need(self.seal==compact({'review':self.review,'response':self.response}),'actual owner guard inputs changed')
        return self.ingress.verify_for_publication(self.response,self.review,self.selection,self.trust)

class HeldBoundary:
    def __init__(self,boundary):self.boundary=boundary
    def __enter__(self):
        b=self.boundary;need(not b.held,'publication boundary already held')
        # These existing file descriptions remain coordinator-owned. Their
        # original owner releases them after the entire capability invocation.
        for fd,identity,mode in b.locks:fcntl.flock(fd,mode|fcntl.LOCK_NB)
        b.held=True
        try:b.guard();return b
        except BaseException:b.held=False;raise
    def __exit__(self,kind,value,traceback):
        b=self.boundary
        try:
            try:b.guard()
            except BaseException as secondary:
                if kind is None:raise
                b.exit_guard_failure={'exception_class':type(secondary).__name__,'primary_preserved':True}
        finally:b.held=False
        return False
