"""Durable native originals with independently bound scope correspondence.

The private host selects this profile and its exact evidence index. Headers and
original bodies retain their native scopes; no Source admission is inferred.
"""
import base64
from dataclasses import dataclass
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT/'implementation/lab-runtime/local-host/t31-durable-output-0001/output_store.py'
BASE_SHA = 'e7c30f149ab0a9be6bfc7c6a4eb9e4bbc54da45fabd1831f8670c66fe54c35c1'
if hashlib.sha256(BASE.read_bytes()).hexdigest()!=BASE_SHA:
    raise ValueError('selected original durable output store differs')
_name = '_t31_scoped_original_output_store'
if _name not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_name,BASE)
    _module = importlib.util.module_from_spec(_spec);sys.modules[_name]=_module;_spec.loader.exec_module(_module)
S = sys.modules[_name]
need,sha = S.need,S.sha


def closed(value,fields,reason):
    need(type(value) is dict and set(value)==set(fields),reason)


def digest(value):
    need(type(value) is str and len(value)==64 and all(c in '0123456789abcdef' for c in value),
         'exact scope evidence digest required')


def binding(value):
    closed(value,('ref','sha256'),'closed original binding required')
    need(type(value['ref']) is str and bool(value['ref']),'nonempty original reference required')
    digest(value['sha256'])


def pointer(value,selector):
    need(type(selector) is str and selector.startswith('/'),'explicit native original selector required')
    for field in selector[1:].split('/'):
        key=field.replace('~1','/').replace('~0','~')
        if type(value) is list:
            need(key=='0' or (key.isascii() and key.isdecimal() and not key.startswith('0')),
                 'canonical native array selector required')
            value=value[int(key)]
        else:
            value=value[key]
    return value


@dataclass(frozen=True)
class ScopeSelection:
    index_path: str
    index_sha256: str

    @classmethod
    def from_host(cls,path,expected_sha256):
        path=Path(path).absolute();digest(expected_sha256)
        need(path.is_absolute() and '..' not in path.parts,'canonical private scope index required')
        need(sha(S.read_owned(path))==expected_sha256,'independently selected scope index differs')
        return cls(str(path),expected_sha256)


class PersistedScopes:
    def __init__(self,selection,journal):
        need(type(selection) is ScopeSelection,'private host-selected native scope profile required')
        self.selection=selection;self.journal=journal
        self.index,self.originals=self.capture()

    def capture(self):
        selected=self.selection;path=Path(selected.index_path)
        raw=S.read_owned(path);need(sha(raw)==selected.index_sha256,'private scope index bytes changed')
        index=S.O.parse(raw)
        closed(index,('schema_version','journal_config_sha256','scope_ref','run_ref','actor','work',
                      'source_cut','members','entries','authority_effect'),'closed native scope index required')
        need(index['schema_version']=='lab-owned-native-scope-index/v1'
             and index['authority_effect']=='none' and index['journal_config_sha256']==self.journal.config_sha256,
             'selected scope index or journal config differs')
        config=self.journal.config
        need(index['scope_ref']==config['scope_ref']==index['work']['scope_ref']
             and index['run_ref']==config['run_ref'] and index['actor']['principal_ref']==config['principal_ref'],
             'scope selection authority/Work/Run/Principal differs')
        need(type(index['members']) is list and type(index['entries']) is list and bool(index['entries']),
             'native correspondence original closure required')
        originals={};paths=set()
        for row in index['members']:
            closed(row,('ref','path','sha256'),'closed private native evidence member required')
            binding({'ref':row['ref'],'sha256':row['sha256']})
            relative=Path(row['path'])
            need(not relative.is_absolute() and relative.as_posix()==row['path'] and '..' not in relative.parts
                 and row['path']!='.' and '\\' not in row['path'] and '\0' not in row['path'],
                 'canonical private native evidence locator required')
            need(row['ref'] not in originals and row['path'] not in paths,'duplicate native evidence locator')
            paths.add(row['path']);body=S.read_owned(path.parent/relative)
            need(sha(body)==row['sha256'],'private native original bytes changed')
            originals[row['ref']]=(row['sha256'],body)
        used=set();keys=set()
        for row in index['entries']:
            closed(row,('transition_ref','artifact','contract_binding','proof_binding','lineage_binding',
                        'producer_receipt_binding','artifact_selector','proof_selector','lineage_selector'),
                   'closed native output correspondence required')
            key=(row['transition_ref'],row['artifact']['version_ref'])
            need(key not in keys,'ambiguous native output correspondence');keys.add(key)
            for name in ('contract_binding','proof_binding','lineage_binding','producer_receipt_binding'):
                b=row[name];binding(b);need(b['ref'] in originals and originals[b['ref']][0]==b['sha256'],
                                          'native evidence binding not independently selected');used.add(b['ref'])
            receipt=S.O.parse(originals[row['producer_receipt_binding']['ref']][1])
            proof=S.O.parse(originals[row['proof_binding']['ref']][1])
            lineage=S.O.parse(originals[row['lineage_binding']['ref']][1])
            need(pointer(receipt,row['artifact_selector'])==row['artifact']
                 and pointer(receipt,row['proof_selector'])==proof
                 and pointer(receipt,row['lineage_selector'])==lineage,
                 'native correspondence not present in selected actual producer receipt')
        need(used==set(originals),'extra or missing private scope evidence original')
        return index,originals

    def guard(self):
        index,originals=self.capture()
        need(index==self.index and originals==self.originals,'native scope evidence changed during use')

    def entry(self,artifact,transition=None):
        self.guard()
        rows=[row for row in self.index['entries'] if row['artifact']==artifact
              and (transition is None or row['transition_ref']==transition)]
        need(bool(rows),'exact native output lacks independently selected scope correspondence')
        # Same exact bytes may occur in multiple phases; all must carry the
        # same native scope. Each phase's producing Run binding remains distinct.
        return rows[0]

    def has_entry(self,artifact,transition=None):
        self.guard()
        return any(row['artifact']==artifact and (transition is None or row['transition_ref']==transition)
                   for row in self.index['entries'])

    def original(self,row,key):
        return S.O.parse(self.originals[row[key]['ref']][1])

    def validate(self,row,artifact,body_scope):
        contract=self.original(row,'contract_binding');proof=self.original(row,'proof_binding')
        lineage=self.original(row,'lineage_binding');index=self.index
        closed(contract,('schema_version','producer_binding','producer_entrypoint','review_sha256','source_binding',
                         'source_cut','principal_ref','work_ref','container_scope_ref','authority_scope_ref',
                         'permitted_body_scope_refs','authority_effect'),'closed persisted native scope contract required')
        closed(proof,('schema_version','artifact','container_scope_ref','body_scope_ref','authority_scope_ref',
                      'review_sha256','source_binding','source_cut','principal_ref','work_ref','producer_binding',
                      'producer_entrypoint','authority_effect'),'closed captured native scope proof required')
        closed(lineage,('run_binding','work_ref','source_cut','principal_ref'),'closed captured native invocation lineage required')
        schema_path=Path(__file__).with_name('scope-contract.schema.json')
        schema_raw=schema_path.read_bytes()
        need(sha(schema_raw)=='49cd0abd3dae7893c0f93fa7badddd5e14880f2ea906893a28706d559d0c7e72','selected owned native scope schema differs')
        S.O.Draft202012Validator(S.O.parse(schema_raw)).validate(contract)
        binding(lineage['run_binding']);binding(contract['source_binding']);digest(contract['review_sha256'])
        need(contract['schema_version']=='lab-private-owned-native-workflow-scope/v1-candidate'
             and proof['schema_version']=='lab-original-native-record-scope/v1-candidate'
             and contract['authority_effect']==proof['authority_effect']=='none',
             'native scope cannot provide admission or effect authority')
        need(proof['artifact']==artifact and artifact['scope_ref']==contract['container_scope_ref']
             and proof['body_scope_ref']==body_scope and body_scope in contract['permitted_body_scope_refs']
             and contract['authority_scope_ref']==index['scope_ref'],
             'native header/body/Project scope correspondence differs')
        for field in ('container_scope_ref','authority_scope_ref','review_sha256','source_binding','source_cut',
                      'principal_ref','work_ref','producer_binding','producer_entrypoint'):
            need(proof[field]==contract[field],'captured native scope field differs: '+field)
        need(contract['source_cut']==lineage['source_cut']==index['source_cut']
             and contract['principal_ref']==lineage['principal_ref']==index['actor']['principal_ref']
             and contract['work_ref']==lineage['work_ref']==index['work']['version_ref'],
             'native scope Source/Principal/Work invocation differs')
        producer=contract['producer_binding'];closed(producer,('path','sha256'),'closed native producer origin required')
        digest(producer['sha256']);origin=Path(producer['path'])
        if not origin.is_absolute():origin=ROOT/origin
        need(origin.is_relative_to(ROOT) and '..' not in origin.parts
             and not origin.is_symlink() and not any(p.is_symlink() for p in origin.parents)
             and sha(origin.read_bytes())==producer['sha256'],'selected actual native producer origin differs')
        need(type(contract['producer_entrypoint']) is str and bool(contract['producer_entrypoint']),
             'explicit native producer entrypoint required')
        self.guard()

    def permits(self,artifact,authority_scope):
        need(authority_scope==self.index['scope_ref'],'foreign native output authority scope')
        if artifact['scope_ref']==authority_scope and not self.has_entry(artifact):
            return True
        row=self.entry(artifact)
        proof=self.original(row,'proof_binding')
        self.validate(row,artifact,proof['body_scope_ref'])
        return True

    def validate_event(self,event):
        self.guard();index=self.index
        need(event['run_ref']==index['run_ref'] and event['source_cut']==index['source_cut']
             and event['actor']==index['actor'],'native scoped output actual event lineage differs')
        for artifact in event['output_artifact_refs']:
            if artifact['scope_ref']==index['scope_ref'] and not self.has_entry(artifact,event['transition_ref']):
                continue
            row=self.entry(artifact,event['transition_ref']);lineage=self.original(row,'lineage_binding')
            need(lineage['run_binding']==event['before_run_binding'],
                 'native producer receipt names another exact producing Run preimage')


class ScopedCarriers:
    def __init__(self,original,scope):
        self.original=original;self.scope=scope;self.rows=original.rows;self.schemas=original.schemas
        # Construct the exact original schema tables once. The contract still
        # reopens the independently selected scope evidence at every use.
        class BoundContract:
            def validate(_,transition,header,body_scope,passed_proof,passed_lineage):
                row=scope.entry(header,transition)
                need(passed_proof==scope.original(row,'proof_binding')
                     and passed_lineage==scope.original(row,'lineage_binding'),
                     'native scope contract invocation differs')
                scope.validate(row,header,body_scope)
        self.native=S.O.OriginalCarriers(S.CATALOG.read_bytes(),S.CATALOG_SHA,
            {r[k]:(ROOT/r[k]).read_bytes() for r in S.O.parse(S.CATALOG.read_bytes())['rows']
             for k in ('schema_path','artifact_path')},scope_contracts=BoundContract())

    def output(self,artifact,raw,*,scope_ref,transition_ref=None,scope_proof=None,invocation_lineage=None):
        need(scope_ref==self.scope.index['scope_ref'],'foreign workflow authority scope')
        if artifact['scope_ref']==scope_ref and scope_proof is None and not self.scope.has_entry(artifact,transition_ref):
            return self.original.output(artifact,raw,scope_ref=scope_ref,transition_ref=transition_ref)
        row=self.scope.entry(artifact,transition_ref)
        proof=self.scope.original(row,'proof_binding');lineage=self.scope.original(row,'lineage_binding')
        need(scope_proof is None or scope_proof==proof,'wire or caller replaced captured native scope proof')
        need(invocation_lineage is None or invocation_lineage==lineage,'native invocation lineage substituted')
        # Original schema/discriminator/identity/hash/privacy checks still run.
        # A small exact adapter supplies only the already bound native scope.
        body=S.O.parse(raw)
        body_scope=body.get('scope_ref',body.get('project_ref',body.get('payload',{}).get('project_ref')))
        self.scope.validate(row,artifact,body_scope)
        return self.native.output(artifact,raw,scope_ref=artifact['scope_ref'],transition_ref=row['transition_ref'],
                                  scope_proof=proof,invocation_lineage=lineage)


class ScopedOutputJournal(S.OutputJournal):
    @classmethod
    def initialize(cls,*args,**kwargs):
        raise ValueError('Initialize the original journal, persist its independently selected scope index, then open ScopedOutputJournal')

    def __init__(self,root,config_sha256,*,scope_selection):
        self.journal=S.J.Journal(root,config_sha256);self.root=self.journal.root
        folder=self.root/'outputs'
        need(not folder.is_symlink() and folder.is_dir() and folder.stat().st_uid==os.getuid()
             and stat.S_IMODE(folder.stat().st_mode)==0o700,'private native output folder required')
        self.scope=PersistedScopes(scope_selection,self.journal)
        self.carriers=ScopedCarriers(S.original_carriers(),self.scope)
        self.replay()

    def _stage(self,plan,originals):
        self.scope.validate_event(plan['event'])
        self._validate_run(plan['next_run'])
        return super()._stage(plan,originals)

    def apply(self,plan,*,originals,request_binding,host_guard,crash_at=None):
        def scoped_guard():
            host_guard()
            self.scope.validate_event(plan['event'])
            self._validate_run(plan['next_run'])
        return super().apply(plan,originals=originals,request_binding=request_binding,
                             host_guard=scoped_guard,crash_at=crash_at)

    def _validate_run(self,run):
        index=self.scope.index
        need(run['work']==index['work'] and run['actor']==index['actor']
             and run['source_cut']==index['source_cut'] and run['run_ref']==index['run_ref'],
             'native output actual producing Work/Actor/Source/Run differs')

    def replay(self):
        head,raw=super().replay()
        for number in range(1,head['sequence']+1):
            tx=S.O.parse(S.read_owned(self.root/'transactions'/f'{number:08d}.json'))
            self.scope.validate_event(tx['event'])
            self._validate_run(S.O.parse(base64.b64decode(tx['next_run_original_base64'],validate=True)))
        self.scope.guard()
        return head,raw

    def recover(self,key,fingerprint,*,host_guard):
        claim=S.O.parse(S.read_owned(self.root/'claims'/(self.journal.namespace(key)+'.json')))
        self.scope.validate_event(claim['plan']['event'])
        self._validate_run(claim['plan']['next_run'])
        def scoped_guard():
            host_guard()
            self.scope.validate_event(claim['plan']['event'])
            self._validate_run(claim['plan']['next_run'])
        return super().recover(key,fingerprint,host_guard=scoped_guard)
