"""Pinned additive selection of frozen API and qualified W02 mechanisms."""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
BASE=HERE.parent/'api-integration-v6'
BASE_SOURCE='7ab054776a5fa8fd310f60e126a29c98686d159f989fb3a721cb6dcd1f1f119f'
BASE_PROFILE='d832f9c20e487261d9987906408dfbd54c7f6cf624890f9144d750d7eb8a053f'
name='_cal_action_0148_base'
if name not in sys.modules:
 spec=importlib.util.spec_from_file_location(name,BASE/'__init__.py',submodule_search_locations=[str(BASE)])
 m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
P=__import__(name+'.protocol',fromlist=['*'])
G=__import__(name+'.guard',fromlist=['*'])
W02=ROOT/'implementation/lab-workflows/candidates/v1'
sys.path.insert(0,str(W02/'authority'))
from evaluator import HostAuthority,HostGrant,SelectedRecord,SessionLease,encoded,parse,byte_sha,require,timestamp,BoundaryFault
from dispatch import LocalDispatcher,LedgerPins,initialize,pins,public_evaluation
from counter import INPUT_CONTRACT,OUTPUT_CONTRACT,atomic,regular_json
from action import materialize_action
from datetime import datetime,timezone

def now():return datetime.now(timezone.utc).isoformat()
def iso(value):return datetime.fromtimestamp(value,timezone.utc).isoformat()
def binding(ref,raw):return {'ref':ref,'sha256':byte_sha(raw)}
def content(ref,raw):return {'content_ref':ref,'byte_sha256':byte_sha(raw),'size_bytes':len(raw),'media_type':'application/json'}
def guard(expected_source_sha256,*,history=False,integration_profile_binding=None):
 if history:G.verify(BASE_SOURCE)
 require(byte_sha((BASE/'source-manifest.json').read_bytes())==BASE_SOURCE,'original frozen API source manifest changed')
 import platform,importlib.metadata
 require(parse((BASE/'source-manifest.json').read_bytes())['environment']=={'python':platform.python_version(),'jsonschema':importlib.metadata.version('jsonschema'),'cryptography':importlib.metadata.version('cryptography')},'current independently selected Action environment differs')
 require(byte_sha((BASE/'contract-profile.json').read_bytes())==BASE_PROFILE,'original frozen API contract profile changed')
 manifest=HERE/'source-manifest.json'
 raw=manifest.read_bytes();require(byte_sha(raw)==expected_source_sha256,'independent Action source pin differs')
 value=parse(raw);G._verify_files(ROOT,value['files'])
 require(byte_sha((HERE/'contract-profile.json').read_bytes())==value['profile_sha256'],'Action profile drift')
 require(manifest.read_bytes()==raw,'Action manifest changed during current verification')
 selection_path=HERE/'EXECUTION-DEPENDENCIES.json';selected_raw=selection_path.read_bytes()
 require(byte_sha(selected_raw)==value['execution_selection_sha256'],'independent Action execution selector changed')
 selected=parse(selected_raw);G._verify_files(ROOT,selected['files'])
 allowed={str((ROOT/r['path']).resolve()) for r in selected['files']}
 extra={}
 if integration_profile_binding is not None:
  profile_path=ROOT/integration_profile_binding['ref']
  G._verify_files(ROOT,[{'path':integration_profile_binding['ref'],'sha256':integration_profile_binding['sha256']}])
  shared=parse(profile_path.read_bytes());extra={str((ROOT/r['path']).resolve()):r for r in shared['files']}

 for module in list(sys.modules.values()):
  file=getattr(module,'__file__',None)
  if not isinstance(file,str):continue
  path=Path(file)
  if path.is_absolute() and path.is_relative_to(ROOT) and path.suffix=='.py':
   archive=getattr(getattr(module,'__loader__',None),'archive',None)
   selected_archive=isinstance(archive,str) and str(Path(archive).resolve()) in allowed and str(path).startswith(archive+'/')
   resolved=str(path.resolve())
   selected_external=extra.get(str(Path(archive).resolve()) if isinstance(archive,str) else resolved)
   if resolved not in allowed and not selected_archive and selected_external is not None:
    G._verify_files(ROOT,[selected_external]);selected_archive=True
   require(resolved in allowed or selected_archive,'unselected repository execution import: '+str(path))
 require(selection_path.read_bytes()==selected_raw,'Action execution selector changed during current verification')
