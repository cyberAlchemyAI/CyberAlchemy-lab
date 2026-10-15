"""Qualification adapter sharing the actual API7 schema registry under one profile."""
import copy,importlib.util,sys
from .dependencies import *
API7=HERE.parent/'api-integration-v7'
def native_package():
 name='_cal_action_0148_actual_api7'
 if name not in sys.modules:
  spec=importlib.util.spec_from_file_location(name,API7/'__init__.py',submodule_search_locations=[str(API7)]);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 return __import__(name+'.protocol',fromlist=['Schemas'])

class IntegratedSchemas:
 """Preserve actual original validators; independently guard both selected profiles.

 This is a qualification adapter for the actual API7 schema object, not a final
 34-operation implementation claim. The final host can pass its own full shared
 Schemas object directly to ActionService instead.
 """
 def __init__(self,native_profile_sha256,integration_profile_binding):
  self.native=native_package().Schemas(native_profile_sha256)
  self.profile_binding=copy.deepcopy(integration_profile_binding)
  G._verify_files(ROOT,[{'path':integration_profile_binding['ref'],'sha256':integration_profile_binding['sha256']}])
  self.profile=parse((ROOT/integration_profile_binding['ref']).read_bytes())
  require(self.profile['native_schema_profile_binding']==self.native.profile_binding,'shared qualification profile does not select actual API7 schemas')
  require(self.profile['implemented_operations']==list(self.native.profile['implemented_operations'])+['action.evaluate','action.dispatch','action.reconcile'],'shared qualification operation scope differs')
  self.guard()
 def guard(self):
  self.native.guard()
  G._verify_files(ROOT,[{'path':self.profile_binding['ref'],'sha256':self.profile_binding['sha256']}])
  require(parse((ROOT/self.profile_binding['ref']).read_bytes())==self.profile,'captured shared original profile changed')
 def __getattr__(self,name):return getattr(self.native,name)
