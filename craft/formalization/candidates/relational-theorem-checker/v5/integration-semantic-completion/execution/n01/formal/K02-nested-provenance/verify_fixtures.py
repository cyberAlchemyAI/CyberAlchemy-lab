"""Concrete full nested-source/fixture join audit; no serializer/authenticity theorem."""
from pathlib import Path
import hashlib,importlib.util,json,re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[9]
def binding(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
    p=HERE/'generate_fixtures.py';s=importlib.util.spec_from_file_location('generator',p);g=importlib.util.module_from_spec(s);s.loader.exec_module(g)
    values,source=g.expected();code=(HERE/'NestedFixture.lean').read_text();assert code==g.lean_source(values,source)
    rows=[]
    for name,value in values.items():
        file=HERE/'fixtures'/(name+'.json');data=file.read_bytes();assert data==g.raw(value)
        ident={'authority-positive':'authority'}.get(name,name)
        literal=re.search(r'^def '+ident+r' : Envelope := ⟨\((".*")\)\.toUTF8\.toList,(\d+),(?:bootstrap.ref|declarationRef),"([a-f0-9]{64})"⟩$',code,re.M)
        assert literal and json.loads(literal[1]).encode('utf-8')==data
        assert int(literal[2])==len(data) and literal[3]==g.hash_bytes(data)
        rows.append({'fixture':binding(file),'byte_count':len(data),'literal_bytes_identical':True})
    source_file=HERE/'fixtures/source.json';assert source_file.read_bytes()==source
    literal=re.search(r'^def source : Envelope := ⟨\((".*")\)\.toUTF8\.toList,(\d+),declarationRef,"([a-f0-9]{64})"⟩$',code,re.M)
    assert literal and json.loads(literal[1]).encode('utf-8')==source
    assert int(literal[2])==len(source) and literal[3]==g.hash_bytes(source)
    rows.append({'fixture':binding(source_file),'byte_count':len(source),'literal_bytes_identical':True})
    artifacts=g.artifacts(values); assert len(artifacts)==20
    nested=[]
    for index,a in enumerate(artifacts):
        data=bytes(a['content']);assert g.hash_bytes(data)==a['ref']['digest'];parsed=json.loads(data)
        if index<2:assert parsed==a['body'] and parsed['kind']==a['sourceKind']
        elif index<16:assert parsed==a['body']
        else:
            assert set(parsed)=={'schema_version','binding_revision_key','kind','body','owner_review_ref'}
            assert parsed['binding_revision_key']==a['ref']['key'] and parsed['kind']==a['sourceKind']
            assert parsed['body']==a['body'] and parsed['owner_review_ref']==a['ownerReview']
            assert parsed['body']['frame']==values['metadata']['context']['frame']
        nested.append({'index':index,'ref':a['ref'],'byte_count':len(data),'document_body_digest_match':True})
    # Generated code is reconstructed exactly above; check every UTF8 content term independently too.
    literals=re.findall(r'⟨\(("(?:[^"\\]|\\.)*")\)\.toUTF8\.toList,(\d+),(?:bootstrap.ref|declarationRef),"([a-f0-9]{64})"⟩',code)
    assert len(literals)==27
    for text,count,digest in literals:
        data=json.loads(text).encode('utf-8');assert len(data)==int(count) and g.hash_bytes(data)==digest
    declaration_ref=g.ref(values['declaration']);selection_ref=g.ref(values['selection'])
    authority=values['authority-positive']['body']['target'];frame=values['metadata']['context']['frame']
    assert authority['declaration_manifest']==[declaration_ref] and authority['selection_manifest']==[selection_ref]
    assert all(values[n]['body']['frame']==frame for n in ['declaration','selection','authority-positive'])
    assert values['selection']['body']['target']['declaration_ref']==declaration_ref
    for issue in authority['issuances']:
        name=next(n for n in ['declaration','selection'] if g.ref(values[n])==issue['source_ref'])
        assert bytes(issue['source_bytes'])==g.raw(values[name])
    report={'task':'N01','unit':'K02-nested-provenance','result':'concrete-nested-fixture-join-pass',
            'driver':binding(Path(__file__)),'generator':binding(p),'fixture_module':binding(HERE/'NestedFixture.lean'),
            'prior_fixture_sources':[binding(HERE.parent/'K02-catalog-snapshots/fixtures'/(n+'.json')) for n in ['metadata','payload','owned']]+
                [binding(HERE.parent/'K02-profile-evidence/fixtures'/(n+'.json')) for n in ['declaration','selection','authority-positive']],
            'records':rows,'fixture_count':7,'content_literal_count':27,'nested_occurrence_count':20,'nested_checks':nested,
            'all_frames_match_relation_world':True,'issuance_bytes_and_manifests_exact':True,
            'complete_original_primary_body_retained':True,'nested_full_body_digest_alignment':True,
            'captured_context_is_synthetic':True,'fixture_serializer_proved':False,'real_authoritative_snapshot_provider':False,'inherited_discharges':0,'authority_effect':'none'}
    (HERE/'fixture-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS: seven source fixtures, 27 literal contents, 20 complete nested occurrences and exact profile/frame joins.')
if __name__=='__main__':run()
