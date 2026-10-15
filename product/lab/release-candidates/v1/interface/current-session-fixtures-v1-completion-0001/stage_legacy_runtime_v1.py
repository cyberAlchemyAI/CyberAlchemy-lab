"""Emit independently declared fresh legacy selectors after actual construction."""
import argparse,ast,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[5]
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def main(instance):
 F=HERE/'instances'/instance
 if not F.is_dir() or F.parent!=HERE/'instances' or not instance.startswith('legacy-'):raise ValueError('closed separate legacy instance required')
 paths={k:F/v for k,v in {'source':'source/source-manifest.json','source_package':'source/packages/0001/manifest.json','reader':'reader/source-manifest.json','mapper':'mapped/source-manifest.json','mapper_package':'mapped/packages/0001/manifest.json','context':'context/source-manifest.json','context_package':'context/packages/0001/manifest.json','implementation':'context/implementation-binding.json','period':'source/packages/0001/period.json'}.items()}
 if not all(p.is_file() for p in paths.values()):raise ValueError('complete actual source/reader/mapper/Context required')
 declaration=json.loads((F/'source/episode-contract.json').read_bytes());selection=json.loads((F/'construction-selection.json').read_bytes());record_index=json.loads((F/'source/packages/0001/record-index.json').read_bytes())
 relation_versions=[r['version_ref'] for r in record_index if r['carrier_ref'].startswith('cal.artifact-type.typed-relation/')]
 refs={'EXPECTED_NOT_BEFORE':declaration['not_before'],'EXPECTED_EXPIRES_AT':declaration['expires_at'],'EXPECTED_PRINCIPAL':declaration['principal_ref'],'EXPECTED_RELATION_PREFIX':'typed-relation:'+selection['prefix']+':','EXPECTED_RELATION_VERSIONS':relation_versions,'EXPECTED_PRODUCT_VERSION':'product:cyberalchemy-lab@current-episode-0004.candidate.1','EXPECTED_READER_ROOT':(F/'reader').relative_to(ROOT).as_posix(),'EXPECTED_ENTRYPOINT':(F/'reader/reader.py').relative_to(ROOT).as_posix()+'#SelectedReader.open_signed','EXPECTED_READER_SHA':hashlib.sha256((F/'reader/reader.py').read_bytes()).hexdigest(),'PUBLIC_SOURCE_NAME':selection['public_source_name']}
 descriptor={'schema_version':'lab-T02-fresh-legacy-runtime-integration-selection/v1-candidate','instance':instance,'bindings':{k:bind(p) for k,p in paths.items()},'independently_declared_fixture_expectations':refs,'original5_period_chain_preserved':True,'previous_distinct_legacy_period_binding':selection['original_legacy_period_binding'],'source5_or_oldlegacy_renewed':False,'root_required_changes':['source_bridge exact new public source enum/producer/reader and original ABI nickname retained','authentication and schema enum exact new source name; fresh independent host grants and nonce/currentness checks','legacy_context_sessions selects exact new Context/reader/mapper with independently captured pins, original class and method guards retained','legacy_fixture_selection independently copied constants and exact source/period/reader expectations; original5 chain assertions retained','guarded_reads/guarded_candidate and termination source selection explicitly include the new actual producer and native cut','final shared profile/source freeze remains root owned; two entire Session classes and wrong-class negatives still require actual execution'],'actual_whole_classes_executed':False,'shared_API_qualified':False,'authority_effect':'none','actual_owner_outcome':None}
 write(F/'runtime/runtime-selection.json',descriptor);print(json.dumps({'result':'STAGED-UNQUALIFIED-current-legacy-runtime-selection','binding':bind(F/'runtime/runtime-selection.json')}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--instance',required=True);a=p.parse_args();main(a.instance)
