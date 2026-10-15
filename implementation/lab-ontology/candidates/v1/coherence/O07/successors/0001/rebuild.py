"""Cold original-source construction; explicit same-byte native locator relocation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from base import *
from successor import guard_successor

def run(pin,output,selection_pin):
 guard_successor(selection_pin)
 ctx=source_guard(pin);output=Path(output);require(not output.exists() and output.resolve().is_relative_to(HERE/'proof'),'empty candidate rebuild destination required')
 migration=ONTOLOGY/'migration/adapters';sys.path.insert(0,str(migration));build=module('build',migration/'build.py');check=module('_O07_original_check',migration/'check.py')
 historical=load(migration/'build-scope.json')['native_executable'];current=ctx['execution_locator_binding']
 require(current['sha256']==historical['sha256'],'native relocation would change executable semantics');bound(current,external=True)
 original_store=build.NativeCandidateStore;owned=[]
 class RelocatedStore(original_store):
  def __init__(self,translator,path,digest):
   require({'path':path,'sha256':digest}==historical,'unselected historical native locator')
   super().__init__(translator,current['path'],digest);owned.append(self.root)
 build.NativeCandidateStore=RelocatedStore
 expected=check.load_package(ORIGINAL)
 try:rebuilt=build.build()
 finally:build.NativeCandidateStore=original_store
 require(set(rebuilt)==set(expected) and len(rebuilt)==225 and all(raw==rebuilt[name] for name,raw in expected.items()),'fresh original-byte rebuild differs')
 require(owned and all(not p.exists() for p in owned),'owned rebuilt ontology store remains')
 with build.signed_catalog() as (catalog,operations):
  translator=build.SourceTranslation(catalog,operations)
  validated=check.validate_payload(rebuilt,translator,load(ONTOLOGY/'receipts/O05/0001.json')['manifest_binding']['sha256'],native=False)
  archive=parse(rebuilt['native.snapshot']);replay=check.read_native(archive,current)
  require(replay['checkpoint_parity']=='PASS' and len(replay['semantic_events'])==len(replay['governance_events'])==88,'cold original event replay incomplete')
  for family,cursor_key in [('semantic','semantic_cursor'),('governance','governance_cursor')]:
   original_events=[parse(base64.b64decode(archive['files'][f'{family}/{i:08d}-ontology-{family}:O05:{i}.json']['base64_original_bytes'],validate=True)) for i in range(1,89)]
   require(replay[family+'_events']==original_events,'cold native event bytes/tuples differ')
 output.mkdir(parents=True,exist_ok=False);rows=[]
 for name,raw in sorted(rebuilt.items()):
  target=output/'package'/name;require(target.resolve().is_relative_to(output),'rebuild path escaped candidate output');target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as stream:stream.write(raw)
  rows.append(binding(target))
 source_guard(pin);guard_successor(selection_pin)
 result={'schema_version':'lab-O07-cold-rebuild/v1-candidate','result':'PASS','source_manifest_binding':binding(HERE/'manifest.json'),'files_compared':225,
  'same_original_bytes':True,'source_construction':validated,'native_checkpoint_parity':replay['checkpoint_parity'],'semantic_cursor':88,'governance_cursor':88,
  'execution_locator_relocation':{'historical_binding':historical,'current_same_byte_binding':current,'original_scope_changed':False},'candidate_output_files':rows,
  'source_recovery_material':'original canonical-format event bytes only; no checkpoint/cache/Session state restored','owned_native_stores_removed':True,
  'private_fixture_keys_removed_by_source_catalog_context':True,'source_execution':False,'source_bodies_copied':0,'canonical_effects_applied':0,
  'authority_effect':'none','actual_owner_outcome':None,'admitted_operation':False}
 emit(output/'result.json',result);print(json.dumps({'result':'PASS','result_binding':binding(output/'result.json'),'files_compared':225}))

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--manifest-sha256',required=True);p.add_argument('--output',required=True);p.add_argument('--selection-sha256',required=True);a=p.parse_args();run(a.manifest_sha256,a.output,a.selection_sha256)
