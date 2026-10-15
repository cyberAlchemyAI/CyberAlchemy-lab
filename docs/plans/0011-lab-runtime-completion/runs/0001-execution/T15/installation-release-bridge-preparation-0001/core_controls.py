"""UNEXECUTED controls for Root after the active timed learning process ends.

Uses the actual original T08 VariedFixture and actual reviewed reader/graph.
No mock original callbacks, native engine, API constructors, lease or install.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE=Path(__file__).absolute().parent

def load_module(name,path,package=False):
    spec=importlib.util.spec_from_file_location(name,path,submodule_search_locations=[str(path.parent)] if package else None)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value);return value

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input-selection-sha256',required=True);parser.add_argument('--source-manifest-sha256',required=True);args=parser.parse_args()
    raw=(HERE/'input-selection.json').read_bytes();assert hashlib.sha256(raw).hexdigest()==args.input_selection_sha256
    selected=json.loads(raw)
    manifest_raw=(HERE/'source-manifest.json').read_bytes();assert hashlib.sha256(manifest_raw).hexdigest()==args.source_manifest_sha256
    manifest=json.loads(manifest_raw)
    def guard():
        for row in manifest['files']:
            path=ROOT/row['path'];assert not any(p.is_symlink() for p in (path,*path.parents))
            assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
    guard()
    own=load_module('_cal_unselected_completion_bridge',HERE/'__init__.py',True)
    bridge=__import__(own.__name__+'.protected_bridge',fromlist=['ProtectedHostBridge'])
    original_path=ROOT/'product/lab/release-candidates/v1/interface/release-proof-inputs-v2-completion-0001/test_inputs.py'
    original=load_module('_cal_original_T08_fixture_for_bridge',original_path)
    parent=HERE/'controls-owned-0001';parent.mkdir(mode=0o700)
    f=original.VariedFixture(parent)
    f.original('definition','authority/artifact-types/definition/v2/fixtures/valid/definition.json','cal.artifact-type.definition/v2','definition')
    f.original('owners','authority/owners/foundation-01/v1/owners.json','cal.artifact-type.owner-registry/v1')
    f.original('registered','authority/artifact-types/artifact-type/v3/artifact.json','cal.artifact-type.artifact-type/v3','artifact-type',True,'/registered_types/0')
    f.all_embedded_declarations();reader,anchor=f.finish()
    module_bindings=selected['module_bindings']
    schema_path=HERE/'typed-review-observation.schema.json'
    selection={'custody_anchor':reader.anchor.__dict__,'control_roots':reader.selector['roots'],'binding_routes':[],
               'semantic_selection':{'anchor':{**anchor.__dict__,'allowed_states':list(anchor.allowed_states)},'policy_file_id':'policy','declared_edges':f.edges,'root_refs':list(f.current)},
               'readiness_version':bridge.REVIEW_VERSION,'observation_schema_binding':{'path':str(schema_path.relative_to(ROOT)),'sha256':hashlib.sha256(schema_path.read_bytes()).hexdigest()},
               'historical_original_proof':{'status':'REFUSED','unavailable_binding':{'path':'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/accounting-0001/unavailable-original-inputs.json','sha256':'4408c5433d41119a92660f86f856d6847be24171ddb1dab368e22c63ee294e7a'},'unavailable_count':25}}
    value=bridge.ProtectedHostBridge(selection,original.P,original.G,module_bindings,ROOT)
    reopened=value.open_reader()
    with reopened.boundary():result=value.verify_semantics(reopened)
    assert result['nodes']==3 and result['declarations']==7 and result['admission_or_owner_authority'] is False
    checks=['actual original protected bootstrap and three original typed carriers/seven declarations']
    def refuses(label,fn):
        try:fn()
        except (ValueError,KeyError):checks.append(label);return
        raise AssertionError('unexpected acceptance: '+label)
    omitted=copy.deepcopy(selection);omitted['semantic_selection']=None
    empty=bridge.ProtectedHostBridge(omitted,original.P,original.G,module_bindings,ROOT)
    refuses('unselected production semantic policy refuses',lambda:empty.verify_semantics(empty.open_reader()))
    invalid=copy.deepcopy(selection);invalid['semantic_selection']['declared_edges']=[{'source':list(f.current)[0],'dependency':list(f.current)[0]}]
    bad=bridge.ProtectedHostBridge(invalid,original.P,original.G,module_bindings,ROOT)
    refuses('invented self-edge refuses against actual original graph',lambda:bad.verify_semantics(bad.open_reader()))
    changed=copy.deepcopy(selection);changed['historical_original_proof']['status']='PASS'
    refuses('historical missing proof cannot become PASS',lambda:bridge.ProtectedHostBridge(changed,original.P,original.G,module_bindings,ROOT))
    source=parent/'selector-control';old=parent/'selector-retained';source.rename(old);source.write_bytes(old.read_bytes());source.chmod(0o600)
    refuses('same selector bytes with substituted inode refuses',value.open_reader)
    # No artifact body, private key, grant or original selector is exported.
    guard()
    report={'result':'PASS-owned-technical-core-only','checks':checks,'original_typed_nodes':3,'original_declarations':7,'selected_manifest_sha256':args.source_manifest_sha256,
            'historical_full_proof':'REFUSED','original_unavailable_count':25,'private_keys_exported':False,
            'native_or_API_or_install_or_lease_calls':False,'whole_shared_bridge_qualified':False,'authority_effect':'none'}
    with (HERE/'core-controls-result-0001.json').open('x') as stream:stream.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True))
if __name__=='__main__':main()
