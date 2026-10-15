"""Check concrete fixture bytes and joins; no general serializer/authenticity theorem."""
from pathlib import Path
import hashlib, importlib.util, json, re
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
def binding(path): return {'path':str(path.relative_to(ROOT)), 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def run():
    p=HERE/'generate_fixtures.py'; spec=importlib.util.spec_from_file_location('fixture_generator',p)
    generator=importlib.util.module_from_spec(spec); spec.loader.exec_module(generator)
    values=generator.expected(); code=(HERE/'SelectedProfileFixture.lean').read_text()
    assert code==generator.lean_source(values)
    records=[]
    for name,value in values.items():
        file=HERE/'fixtures'/(name+'.json'); data=file.read_bytes(); assert data==generator.raw(value)
        ident={'authority-positive':'authority','authority-missing-review':'missingReview'}.get(name,name)
        pattern=rf'^def {ident} : Envelope := ⟨(\[[^\n]*?\]),(\d+),bootstrap.ref,"([a-f0-9]{{64}})"⟩$'
        m=re.search(pattern,code,re.M); assert m
        assert bytes(json.loads(m[1]))==data and int(m[2])==len(data)
        assert m[3]==hashlib.sha256(data).hexdigest()
        records.append({'fixture':binding(file), 'byte_count':len(data), 'literal_bytes_identical':True})
    frame=json.loads((HERE.parent/'K02-catalog-snapshots/fixtures/metadata.json').read_text())['context']['frame']
    assert all(v['body']['frame']==frame for v in values.values())
    authority=values['authority-positive']['body']['target']
    declaration_ref=generator.ref(values['declaration']); selection_ref=generator.ref(values['selection'])
    assert values['selection']['body']['target']['declaration_ref']==declaration_ref
    assert authority['declaration_manifest']==[declaration_ref] and authority['selection_manifest']==[selection_ref]
    issued={json.dumps(v['source_ref'],sort_keys=True):v for v in authority['issuances']}
    for name in ['declaration','selection']:
        value=values[name]; issue=issued[json.dumps(generator.ref(value),sort_keys=True)]
        assert bytes(issue['source_bytes'])==(HERE/'fixtures'/(name+'.json')).read_bytes()
        assert issue['source_kind']==value['kind'] and issue['owner_review_ref']==value['owner_review_ref']
    assert all(v['scope']==frame['scope'] for v in authority['entitlements'])
    assert values['authority-missing-review']['body']['target']['reviews']==[]
    report={'task':'N01','unit':'K02-selected-relation','result':'concrete-fixture-byte-join-pass',
            'driver':binding(Path(__file__)), 'generator':binding(p),'fixture_module':binding(HERE/'SelectedProfileFixture.lean'),
            'prior_fixture_sources':[binding(HERE.parent/'K02-profile-evidence/fixtures'/(n+'.json')) for n in ['declaration','selection','authority-positive']],
            'relation_frame_fixture':binding(HERE.parent/'K02-catalog-snapshots/fixtures/metadata.json'),
            'records':records,'check_count':len(records),'all_frames_match_relation_world':True,
            'issuance_bytes_and_manifests_exact':True,'captured_context_is_synthetic':True,
            'fixture_serializer_proved':False,'real_authoritative_snapshot_provider':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'fixture-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: four concrete byte literals, exact source hashes/issuance joins, one frame; synthetic only.')
if __name__=='__main__': run()
