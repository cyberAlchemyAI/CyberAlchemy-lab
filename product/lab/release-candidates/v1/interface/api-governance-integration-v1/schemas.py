"""Exact public schema selection without unrelated historical receipt dependencies.

All original schema files and selected Source8 overlays are rehashed at each
boundary. This explicit additive execution selection changes no public schema,
resource mapping, signed source, clock, permission or imported validator.
"""
import importlib.util
from jsonschema import Draft202012Validator,FormatChecker
from referencing import Resource
from .dependencies import *
class GovernanceSchemas:
 def __init__(self):
  self.profile_binding=binding((BASE/'contract-profile.json').relative_to(ROOT).as_posix(),(BASE/'contract-profile.json').read_bytes())
  C.require(self.profile_binding['sha256']==BASE_PROFILE,'frozen original profile pin differs')
  self.profile=K.parse((BASE/'contract-profile.json').read_bytes());self.inputs=parse((BASE/'schema-inputs.json').read_bytes())
  self.rows=selection_rows();self.guard()
  path=ROOT/'docs/proposals/0007-lab-integrated-schema-package/resources.py';spec=importlib.util.spec_from_file_location('_governance0148_original_schema_resources',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);registry=m.build_registry()
  path=HERE.parent/'source8-protocol-v2/resources.py';spec=importlib.util.spec_from_file_location('_governance0148_source8_schema_resources',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  registry,self.uri_mapping=m.configure(registry,self.profile['protocol_resource_selection_binding'])
  self.schemas={}
  for file in sorted((ROOT/'docs/proposals/0008-lab-api-contracts/schemas').glob('*.schema.json')):
   v=K.parse(file.read_bytes());registry=registry.with_resource(v['$id'],Resource.from_contents(v));self.schemas[file.name.removesuffix('.schema.json')]=v
  for file in sorted((BASE/'schemas').glob('*.schema.json')):
   v=K.parse(file.read_bytes());registry=registry.with_resource(v['$id'],Resource.from_contents(v));self.schemas[file.name.removesuffix('.schema.json')]=v
  self.registry=registry.crawl();self.checker=FormatChecker();self.validators={n:Draft202012Validator(s,registry=self.registry,format_checker=self.checker) for n,s in self.schemas.items()}
  self.operations={r['operation']:r for r in parse((ROOT/'docs/proposals/0008-lab-api-contracts/api-contracts.json').read_bytes())['operations']}
 def guard(self):G._verify_files(ROOT,self.rows)
 def valid(self,name,value):return self.validators[name].is_valid(value)
 def protocol_valid(self,uri,value):
  root,mark,fragment=uri.partition('#');selected=self.uri_mapping.get(root,root)+(mark+fragment if mark else '')
  return Draft202012Validator({'$ref':selected},registry=self.registry,format_checker=self.checker).is_valid(value)
def selection_rows():
 raw=(HERE/'execution-dependency-selection.json').read_bytes();v=parse(raw)
 C.require(v['base_source_sha256']==BASE_SOURCE and v['base_profile_sha256']==BASE_PROFILE,'execution parent selection differs')
 return v['files']
