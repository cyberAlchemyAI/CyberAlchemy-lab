"""Fresh scoped read of an immutable completed owned application journal.

The independent assessment grant selects this input store. No channel, grant,
Session memory, current Artifact admission or writer is reconstructed.
"""
import importlib,copy,fcntl,os
from pathlib import Path
from contextlib import contextmanager
from jsonschema import Draft202012Validator

class ApplicationJournal:
    def __init__(self,host):
        self.host=host;package=type(host).__module__.rsplit('.',1)[0]
        self.P=importlib.import_module(package+'.protocol')
        self.W=importlib.import_module(package+'.workspace')
        self.selected=copy.deepcopy(host.channel.policy['source8_control']['application_journal_scope'])
        self.P.source.require(type(self.selected) is dict,'independent application journal scope absent')
        self.root=Path(self.selected['root']);self.guard()

    def guard(self):
        p=self.P;policy=self.host.channel.policy_guard();self.host.channel.guard();self.host.schemas.guard()
        p.source.require(policy['source8_control']['application_journal_scope']==self.selected,
                         'current independent journal read scope changed')
        root=self.root
        p.source.require(root.is_absolute() and root.is_relative_to(Path('/tmp')) and root.resolve()==root
                         and not root.is_relative_to(p.ROOT) and not root.is_symlink()
                         and not any(q.is_symlink() for q in root.parents),'unsafe application input store')
        self.W.safe(root,0o700)
        for name in ('inputs','objects','journal'):self.W.safe(root/name,0o700)
        raw=self.W.read_private(root/'workspace.json');m=p.source.parse(raw)
        p.source.require(p.source.sha(raw)==self.selected['manifest_sha256']
                         and self.selected['workspace_binding']=={'ref':'workspace:'+m['workspace_ref'],'sha256':p.source.sha(raw)}
                         and m['principal_ref']==policy['principal_ref'] and m['scope_refs']==policy['scope_refs'],
                         'original application workspace manifest or scope differs')
        schema=p.source.parse((Path(self.W.__file__).parent/'workspace.schema.json').read_bytes())
        Draft202012Validator(schema).validate(m)
        refs=set();paths=set()
        for row in m['materials']:
            path=Path(row['path'])
            p.source.require(row['ref'] not in refs and row['path'] not in paths and not path.is_absolute()
                             and path.parts[0]=='inputs' and '..' not in path.parts and path.as_posix()==row['path'],
                             'unsafe duplicate application input')
            refs.add(row['ref']);paths.add(row['path'])
            original=self.W.read_private(root/path)
            p.source.require(p.source.sha(original)==row['sha256'],'original application material changed')
            self.W.privacy(p.source.parse(original))
        p.source.require(set(q.relative_to(root).as_posix() for q in (root/'inputs').iterdir())==paths,
                         'closed application input set differs')
        self.manifest=m;self.inputs={row['ref']:row for row in m['materials']}
        return True

    def object_read(self,b):
        p=self.P;p.source.require(set(b)=={'ref','sha256'} and b['ref']=='workspace-object:'+self.manifest['workspace_ref']+':'+b['sha256'],
                                 'foreign application object namespace')
        raw=self.W.read_private(self.root/'objects'/(b['sha256']+'.json'))
        p.source.require(p.source.sha(raw)==b['sha256'],'original application object changed')
        self.W.privacy(p.source.parse(raw));return raw

    def material(self,b):
        row=self.inputs.get(b['ref']);self.P.source.require(row is not None and row['sha256']==b['sha256'],
                                                         'application content is outside selected original input')
        raw=self.W.read_private(self.root/row['path']);self.P.source.require(self.P.source.sha(raw)==b['sha256'],'application input changed')
        return raw

    @contextmanager
    def lock(self):
        self.guard();fd=os.open(self.root/'.lock',os.O_RDONLY|os.O_NOFOLLOW)
        try:
            self.W.safe(self.root/'.lock',0o600);fcntl.flock(fd,fcntl.LOCK_SH);self.guard();yield
        finally:fcntl.flock(fd,fcntl.LOCK_UN);os.close(fd)

    def state(self,namespace):
        p=self.P;p.source.require(len(namespace)==64 and all(c in '0123456789abcdef' for c in namespace),'closed journal namespace required')
        allocation=p.source.parse(self.W.read_private(self.root/'journal'/(namespace+'.allocated.json')))
        raw=self.W.read_private(self.root/'journal'/(namespace+'.claim.json'));claim=p.source.parse(raw)
        p.source.require(allocation=={**claim,'claim_sha256':p.source.sha(raw)} and claim['namespace']==namespace,
                         'original allocation/claim closure differs')
        wire=self.object_read(claim['original_call_material_binding'])
        p.source.require(p.source.sha(wire)==claim['original_call_binding']['sha256']
                         and p.source.parse(wire)['operation']==claim['operation'],'original application call binding differs')
        result_path=self.root/'journal'/(namespace+'.result.json')
        if not result_path.exists():return claim,None
        result=p.source.parse(self.W.read_private(result_path))
        p.source.require(set(result)=={'claim_sha256','domain_binding','posture','evidence_bindings'}
                         and result['claim_sha256']==p.source.sha(raw) and result['posture'] in ('completed','failed'),
                         'original application result/claim closure differs')
        self.object_read(result['domain_binding'])
        for b in result['evidence_bindings']:self.object_read(b)
        return claim,result
