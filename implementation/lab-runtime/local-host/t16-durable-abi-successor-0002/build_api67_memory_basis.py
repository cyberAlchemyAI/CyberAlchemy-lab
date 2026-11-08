"""Recheck prepared Session captured memory basis before any allocation."""
import ast,hashlib,json,os,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v66-t16-durable-open-0001'
NEW=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v67-t16-sealed-memory-open-0001'
SOURCE='511e301774026aa2e054eaa44007ee4be844565573bcd57d937076dfe3d975b4'
PROFILE='5342a47c1cff7109870651a582b0ed255cd0f60e45e30b4db62518b03954d109'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
enc=lambda x:(json.dumps(x,sort_keys=True,indent=2)+'\n').encode()
def binding(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p)}
def main():
 os.umask(0o077)
 if NEW.exists() or sha(OLD/'source-manifest.json')!=SOURCE or sha(OLD/'contract-profile.json')!=PROFILE:raise ValueError('selected predecessor differs or successor exists')
 source=json.loads((OLD/'source-manifest.json').read_bytes());profile=json.loads((OLD/'contract-profile.json').read_bytes());shutil.copytree(OLD,NEW,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 helper=NEW/'session_source_freshness.py'
 helper.write_text(helper.read_text()+'''
def captured_source_basis(selected):
    """Cheap integrity of private facts shared across trusted operations.

    This neither authenticates wire fields nor replaces physical freshness.
    Expected file digests remain independently selected by family manifests.
    """
    producer=selected.view.integrated_reader.adapter.source
    require(not selected.closed and not selected.view.handle.closed,
            'selected source or handle closed')
    require(selected.sources.current_guard==selected.guard,
            'selected source callback changed')
    require(selected.view.subjects==selected.view.data['projection']['subjects'],
            'captured projection subject views differ')
    common=selected.view.handle.common
    return {
        'config':common.digest(selected.view.data['config']),
        'baseline':common.digest(selected.view.data['baseline']),
        'projection':common.digest(selected.view.data['projection']),
        'cut':producer.cut(selected.view),
        'source_cut':selected.source_cut,'exact_sources_cut':selected.sources.source_cut,
        'scope':selected.sources.scope_ref,
        'records':producer.sha(selected.record_stamp(selected.records)),
        'exact_records':producer.sha(selected.record_stamp(selected.sources.records.values())),
        'schemas':producer.sha(selected.schema_stamp(selected.schemas)),
        'exact_schemas':producer.sha(selected.schema_stamp(selected.sources.schemas.values())),
        'validators':{k:producer.sha(producer.encoded(v.schema))
                      for k,v in selected.sources.validators.items()},
        'originals':{k:producer.sha(v) for k,v in selected.view.originals.items()},
    }
''')
 p=NEW/'current_legacy_context_sessions.py';s=p.read_text()
 s=s.replace('from .session_source_freshness import fresh_selected_source','from .session_source_freshness import fresh_selected_source,captured_source_basis')
 needle="                'family':family,'sid':sid"
 if s.count(needle)!=1:raise ValueError('prepared physical family selection differs')
 s=s.replace(needle,"                'family':family,'memory_basis':captured_source_basis(self.source),'sid':sid")
 needle="            fresh_selected_source(self.source,plan['family'])"
 if s.count(needle)!=1:raise ValueError('commit freshness seam differs')
 s=s.replace(needle,"            source.require(captured_source_basis(self.source)==plan['memory_basis'],\n                'captured source facts changed after Session preclaim')\n"+needle)
 ast.parse(s);p.write_text(s)
 for name in ('source_bridge.py','workflow_output_registry.py'):
  p=NEW/name;p.write_text(p.read_text().replace(OLD.name,NEW.name).replace('_cal_api66_t16_','_cal_api67_t16_'))
 for p in [*OLD.glob('test_*.py'),*OLD.glob('run_*checks.py')]:
  if sha(p)!=sha(NEW/p.name):raise ValueError('inherited test bytes changed')
 prefix=OLD.relative_to(ROOT).as_posix()+'/'
 def recut(row):return binding(NEW/row['path'][len(prefix):]) if row['path'].startswith(prefix) else row
 profile['files']=sorted([recut(r) for r in profile['files']],key=lambda r:r['path'])
 for k,v in list(profile.items()):
  if k!='files' and isinstance(v,dict) and set(v)=={'path','sha256'}:profile[k]=recut(v)
 (NEW/'contract-profile.json').write_bytes(enc(profile));source['files']=sorted([recut(r) for r in source['files']],key=lambda r:r['path']);source['profile_binding']=binding(NEW/'contract-profile.json');source['predecessor_source_manifest_binding']=binding(OLD/'source-manifest.json');(NEW/'source-manifest.json').write_bytes(enc(source))
 receipt={'schema_version':'lab-T16-memory-basis-open/v1-candidate','successor_package':NEW.relative_to(ROOT).as_posix(),'successor_manifest_sha256':sha(NEW/'source-manifest.json'),'successor_source_binding':binding(NEW/'source-manifest.json'),'successor_profile_binding':binding(NEW/'contract-profile.json'),'predecessor_source_binding':binding(OLD/'source-manifest.json'),'authority_effect':'none','t16_qualified':False}
 (NEW/'rebind-receipt.json').write_bytes(enc(receipt));print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
