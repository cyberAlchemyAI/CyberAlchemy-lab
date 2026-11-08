"""Explicit owned semantic fixtures plus read-only exact public origin bindings."""
import bootstrap
from bootstrap import R,S,E,checked
import copy,json,os,time
from pathlib import Path
from lab_contracts.codec import canonical,sha
from lab_selectors.anchors import AnchoredReader,RootAnchor,identity
from dependency_graph.reader import RoleReader,ReaderSelection,FixturePermission,ROLE_KINDS
from environment.composite import CompositeSelection,ORIGINAL_DESCRIPTOR_SHA,ORIGINAL_SCHEMA_SHA
from environment.origins import OriginSelection
from environment.requirements import PRIOR_PATH,ORIGINAL_BINDINGS
from semantic_fixture import VariedFixture

BASE=R/'product/lab/release-candidates/v1/interface/composite-environment-v1-completion-0001'
DEPENDENCY=R/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/revision-0002/dependency-selection-0002.json'
DEPENDENCY_SHA='2345d4d3a59c6ff87aa8e42f5c84b6fd92a188797d64ba38298710cc64113835'
PUBLIC_INPUTS={}

class CompositeFixture(VariedFixture):
    def __init__(self,root):
        super().__init__(root);self.external={};self.legacy=[];self.origin_members=[]
        self.original('definition','authority/artifact-types/definition/v2/fixtures/valid/definition.json','cal.artifact-type.definition/v2','definition')
        self.original('owners','authority/owners/foundation-01/v1/owners.json','cal.artifact-type.owner-registry/v1')
        self.original('registered','authority/artifact-types/artifact-type/v3/artifact.json','cal.artifact-type.artifact-type/v3','artifact-type',True,'/registered_types/0')
        self.all_embedded_declarations()
        descriptor=checked(BASE/'supported-composite-environment.json',ORIGINAL_DESCRIPTOR_SHA)
        self.add('descriptor','environment-contract',descriptor);self.descriptor=json.loads(descriptor)
        self.original_descriptor=self.external_file('original-descriptor',BASE/'supported-composite-environment.json',ORIGINAL_DESCRIPTOR_SHA,'environment-contract')
        self.schema=self.external_file('composite-schema',BASE/'environment.schema.json',ORIGINAL_SCHEMA_SHA,'governed-schema')
        d=self.descriptor
        metadata=[(d['original_composite_binding'],'environment-contract'),(d['historical_classification_binding'],'environment-contract'),
            (d['retained_full_proof']['source_binding'],'source-manifest'),(d['retained_full_proof']['profile_binding'],'contract-profile'),
            (d['execution_dependencies']['selection_binding'],'execution-selection'),
            ({'path':PRIOR_PATH,'sha256':ORIGINAL_BINDINGS[PRIOR_PATH]},'execution-selection')]
        metadata += [(r,'host-dependency') for r in d['module_bindings']]
        for i,(row,role) in enumerate(metadata):
            name='metadata-'+str(i);b=self.external_file(name,R/row['path'],row['sha256'],role)
            self.legacy.append({'path':row['path'],'file_id':name,'binding':b,'role':role})
        self.requirements=json.loads(checked(DEPENDENCY,DEPENDENCY_SHA))
        members={r['destination']:r for r in self.requirements['inputs']};members.update(self.requirements['wheel_members'])
        installed=Path(d['execution_dependencies']['installed_root'])
        for i,(destination,row) in enumerate(members.items()):
            name='runtime-'+str(i);b={'kind':'execution','root_id':'repository',
                'relative_path':str((installed/destination).relative_to(R)),'sha256':row['sha256'],'size_bytes':row['size_bytes']}
            self.external[name]={'file_id':name,'binding':b,'kind':'host-dependency','logical_path':'owned-public-origin/'+name}
            self.origin_members.append({'destination':destination,'file_id':name,'binding':b})
            PUBLIC_INPUTS[b['relative_path']]=b

    def external_file(self,name,path,digest,role):
        raw=checked(path,digest)
        b={'kind':ROLE_KINDS[role][0],'root_id':'repository','relative_path':str(path.relative_to(R)),
            'sha256':digest,'size_bytes':len(raw)}
        self.external[name]={'file_id':name,'binding':b,'kind':role,'logical_path':'owned-public-origin/'+name}
        PUBLIC_INPUTS[b['relative_path']]=b
        return b

    def reader(self):
        rows=[{'file_id':name,'binding':self.binding(name),'logical_path':'technical:owned/'+name,'kind':self.kinds[name]}
              for name in sorted(self.payloads)]+list(self.external.values())
        policy={'schema_version':'lab-original-role-selection/v1','source_binding':self.source,'profile_binding':self.profile,
            'source_cut':self.cut,'files':rows,'table_descriptors':[],'authority_effect':'none'}
        raw=canonical(policy);(self.root/'_role-control').write_bytes(raw)
        policy_binding={'kind':'execution','root_id':'fixture','relative_path':'_role-control','sha256':sha(raw),'size_bytes':len(raw)}
        grant={'schema_version':'lab-fixture-reader-permission/v1','posture':'owned-fixture','subject':'owned-composite-fixture',
            'source_binding':self.source,'profile_binding':self.profile,'source_cut':self.cut,
            'allowed_bindings':[r['binding'] for r in rows if r['binding']['kind']=='protected-input'],
            'not_before_ns':0,'expires_ns':time.time_ns()+180_000_000_000,'authority_effect':'none'}
        raw=canonical(grant);(self.root/'_grant-control').write_bytes(raw)
        gb={'kind':'evidence','root_id':'fixture','relative_path':'_grant-control','sha256':sha(raw),'size_bytes':len(raw)}
        root=RootAnchor('fixture',str(self.root),identity(os.stat(self.root)))
        class Provider:
            def read(self,b,*,max_bytes):
                selected={**b,'kind':'public-package'}
                return AnchoredReader([root],[selected]).read(selected,max_bytes)
        held=AnchoredReader([root,RootAnchor('repository',str(R),identity(os.stat(R)))],
            [r['binding'] for r in rows]+[policy_binding,gb],protected_provider=Provider())
        return RoleReader(held,ReaderSelection(policy_binding,self.source,self.profile,self.cut,[]),posture='owned-fixture',
            permission=FixturePermission(held,gb,'owned-composite-fixture'))

    def selections(self):
        reader,anchor=self.finish()
        selection=CompositeSelection('descriptor',self.binding('descriptor'),'composite-schema',self.schema,
            'original-descriptor',self.original_descriptor,self.source,self.profile,self.cut,copy.deepcopy(self.legacy))
        origins=OriginSelection(self.source,self.profile,self.cut,copy.deepcopy(self.origin_members))
        semantic={'policy_file_id':'policy','declared_edges':self.edges,'root_refs':list(self.current),'anchor':anchor,
            'policy_schema_raw':checked(S/'dependency_graph/semantic-policy.schema.json','6c21294529c01bc86014aa400f230d718e9ddc69e45f1e937e00cbd44ae7db8e')}
        return reader,selection,origins,semantic

    def change_descriptor(self,mutate):
        value=copy.deepcopy(self.descriptor);mutate(value)
        self.add('descriptor','environment-contract',(json.dumps(value,sort_keys=True,indent=2)+'\n').encode())
