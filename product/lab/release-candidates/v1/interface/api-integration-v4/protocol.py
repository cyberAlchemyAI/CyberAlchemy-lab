"""Exact offline API resources and bounded UTF-8 wire/message encodings."""
import importlib.util
import json
import math
from pathlib import Path
import sys
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Resource

HERE=Path(__file__).resolve().parent
from . import source_bridge as source
ROOT=source.ROOT
INPUTS=HERE/'schema-inputs.json'
INPUTS_SHA='46ba45049ce2efc4772e6eb4c79c3f13f302eb37f2d6da48badd0d462aaac26c'
API=ROOT/'docs/proposals/0008-lab-api-contracts'
SCHEMAS=ROOT/'docs/proposals/0007-lab-integrated-schema-package'
METADATA_SUPPORTED=('lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query', 'change.prepare', 'change.validate', 'operation.inspect', 'projection.refresh')
LEGACY_SUPPORTED=('lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query', 'change.prepare', 'change.validate', 'operation.inspect', 'context.get', 'session.open', 'session.close', 'session.inspect', 'projection.refresh')
EXPORT_SUPPORTED=METADATA_SUPPORTED+('files.materialize',)
REVIEW_SUPPORTED=METADATA_SUPPORTED+('proposal.review',)
CLASSIFICATION_SUPPORTED=METADATA_SUPPORTED+('classification.prepare',)
FAILURE_SUPPORTED=METADATA_SUPPORTED+('failure.assess',)
TYPED_SUPPORTED=METADATA_SUPPORTED+('typed.extension.prepare',)
LESSON_ONTOLOGY_SUPPORTED=METADATA_SUPPORTED+('ontology.project',)
SUPPORTED=LEGACY_SUPPORTED+('lesson.select',)
PACKAGE_SUPPORTED=METADATA_SUPPORTED+('package.import',)
PACKAGE_EXPORT_SUPPORTED=METADATA_SUPPORTED+('package.export',)
CHALLENGE_SUPPORTED=METADATA_SUPPORTED+('challenge.submit',)
ASSESSMENT_SUPPORTED=METADATA_SUPPORTED+('lesson.assess',)
RESOLUTION_SUPPORTED=METADATA_SUPPORTED+('challenge.resolve',)
APPLICATION_SUPPORTED=METADATA_SUPPORTED+('lesson.apply',)
APPLICATION_SESSION_ONTOLOGY_SUPPORTED=METADATA_SUPPORTED+('ontology.project',)
SUPPORTED=LEGACY_SUPPORTED+('lesson.apply',)
WORKFLOW_SUPPORTED=CHALLENGE_SUPPORTED+('proposal.review',)
WORKFLOW_TRANSITION_SUPPORTED=METADATA_SUPPORTED+('workflow.transition',)
ONTOLOGY_SUPPORTED=METADATA_SUPPORTED+('ontology.project',)
SUPPORTED=LEGACY_SUPPORTED+('challenge.submit','files.materialize','proposal.review','classification.prepare','failure.assess','typed.extension.prepare','lesson.select','package.import','package.export','lesson.assess','lesson.apply','challenge.resolve','workflow.transition','ontology.project')


def compact(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')


def binding(ref,raw):return {'ref':ref,'sha256':source.sha(raw)}


def frame_parse(raw):
    if type(raw) is not bytes or len(raw)>1024*1024:raise ValueError('input budget')
    text=raw.decode('utf-8',errors='strict');depth=0;string=False;escaped=False
    for char in text:
        if string:
            if escaped:escaped=False
            elif char=='\\':escaped=True
            elif char=='"':string=False
        elif char=='"':string=True
        elif char in '{[':
            depth+=1
            if depth>32:raise ValueError('nesting budget')
        elif char in '}]':depth-=1
    value=source.parse(raw)
    def bounded(v):
        if isinstance(v,str):
            if any(ord(c)==0 or 0xD800<=ord(c)<=0xDFFF for c in v):raise ValueError('unsupported Unicode')
        elif type(v) is int:
            if abs(v)>2**63-1:raise ValueError('unsupported integer')
        elif type(v) is float:
            if not math.isfinite(v):raise ValueError('nonfinite numeric value')
        elif isinstance(v,dict):
            if len(v)>1000:raise ValueError('object budget')
            for k,x in v.items():bounded(k);bounded(x)
        elif isinstance(v,list):
            if len(v)>1000:raise ValueError('array budget')
            for x in v:bounded(x)
    bounded(value)
    return value


def message_bytes(raw):
    """Exact received top-level message value span, excluding separator spaces."""
    text=raw.decode('utf-8');decoder=json.JSONDecoder();pos=0
    def ws(p):
        while p<len(text) and text[p].isspace():p+=1
        return p
    pos=ws(pos)
    if text[pos]!='{':raise ValueError('object required')
    pos+=1
    while True:
        pos=ws(pos)
        if text[pos]=='}':break
        key,end=decoder.raw_decode(text,pos);pos=ws(end)
        if text[pos]!=':':raise ValueError('separator required')
        pos=ws(pos+1);start=pos;_,pos=decoder.raw_decode(text,pos)
        if key=='message':return text[start:pos].encode('utf-8')
        pos=ws(pos)
        if text[pos]==',':pos+=1
        elif text[pos]=='}':break
        else:raise ValueError('separator required')
    raise ValueError('message missing')


class Schemas:
    def __init__(self,expected_profile_sha256=None):
        source.require(source.sha(INPUTS.read_bytes())==INPUTS_SHA,'independent API schema closure differs')
        self.inputs=source.parse(INPUTS.read_bytes())
        self.profile_path=HERE/'contract-profile.json'
        raw=self.profile_path.read_bytes();self.profile_sha=source.sha(raw)
        source.require(expected_profile_sha256 is None or self.profile_sha==expected_profile_sha256,'independently selected protocol profile differs')
        self.profile=source.parse(raw)
        source.require(self.profile['schema_version']=='lab-operator-contract-profile/v4-candidate'
            and self.profile['implemented_operations']==list(SUPPORTED),'unexpected protocol profile')
        self.profile_binding=binding(str(self.profile_path.relative_to(ROOT)),raw)
        self.local_schema_path=HERE/'authentication.schema.json'
        self.local_schema_sha=source.sha(self.local_schema_path.read_bytes())
        self.guard()
        spec=importlib.util.spec_from_file_location('_R03_exact_protocol_resources',SCHEMAS/'resources.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        registry=module.build_registry()
        selected=self.profile['protocol_resource_selection_binding']
        resource_path=HERE.parent/'source8-protocol-v2/resources.py'
        spec=importlib.util.spec_from_file_location('_cal_source8_protocol_resources_v1',resource_path)
        resource_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(resource_module)
        registry,self.uri_mapping=resource_module.configure(registry,selected)
        self.protocol_resource_selection_binding=selected
        self.schemas={}
        for file in sorted((API/'schemas').glob('*.schema.json')):
            value=source.parse(file.read_bytes());registry=registry.with_resource(value['$id'],Resource.from_contents(value))
            self.schemas[file.name.removesuffix('.schema.json')]=value
        value=source.parse(self.local_schema_path.read_bytes())
        registry=registry.with_resource(value['$id'],Resource.from_contents(value))
        self.schemas['reader-authentication']=value
        for file in sorted((HERE/'schemas').glob('*.schema.json')):
            value=source.parse(file.read_bytes());registry=registry.with_resource(value['$id'],Resource.from_contents(value))
            self.schemas[file.name.removesuffix('.schema.json')]=value
        self.registry=registry.crawl();self.checker=FormatChecker()
        self.operations={r['operation']:r for r in source.parse((API/'api-contracts.json').read_bytes())['operations']}
        self.validators={name:Draft202012Validator(s,registry=self.registry,format_checker=self.checker) for name,s in self.schemas.items()}
    def guard(self):
        # The same complete input/profile rows are read and hashed afresh.
        # Directory descriptors are reused only inside this guard invocation;
        # no source bytes, permissions or digest results survive the boundary.
        from .guard import _verify_files
        rows={}
        for row in [*self.inputs['files'],*self.profile['files'],
                    self.profile['original_operation_catalog_binding'],self.profile['original_schema_inputs_binding']]:
            previous=rows.get(row['path'])
            source.require(previous is None or previous==row,'conflicting exact schema source bindings')
            rows[row['path']]=row
        _verify_files(ROOT,[rows[key] for key in sorted(rows)])
        source.require(source.sha(self.local_schema_path.read_bytes())==self.local_schema_sha,'captured authentication schema changed')
        source.require(source.sha(self.profile_path.read_bytes())==self.profile_sha,'captured protocol profile changed')
        if hasattr(self,'uri_mapping'):
            selected=source.parse(source.original(self.protocol_resource_selection_binding))
            source.require(self.uri_mapping==selected['uri_mapping'],'captured protocol resource selection changed')
    def valid(self,name,value):return self.validators[name].is_valid(value)
    def protocol_valid(self,uri,value):
        root,mark,fragment=uri.partition('#')
        selected=self.uri_mapping.get(root,root)+(mark+fragment if mark else '')
        return Draft202012Validator({'$ref':selected},registry=self.registry,format_checker=self.checker).is_valid(value)
