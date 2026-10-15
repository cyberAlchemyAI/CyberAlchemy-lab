"""Capture the declared successor executable; parent bytes stay immutable."""
from loader import *


def freeze():
    require(not MANIFEST.exists(),'candidate executable already captured')
    parent_binding=bind(HERE.parent/'coupling/engine-manifest.json');parent=parse(original(parent_binding))
    delta=[]
    for row in parent['files']:
        original(row);path=ENGINE/Path(row['path']).relative_to('product/lab/release-candidates/v1/interface/coupling/engine')
        if sha(path.read_bytes())!=row['sha256']:delta.append({'parent_binding':row,'candidate_binding':bind(path)})
    manifest={'schema_version':'lab-R03-correction-engine-manifest/v1-candidate','authority_effect':'none','actual_owner_outcome':None,
        'engine_id':'lab-operator-reference-correction/v1-candidate','parent_binding':parent_binding,
        'files':[bind(p) for p in sorted(ENGINE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts],
        'changed_files':delta,'profile_binding':bind(ENGINE/'profile.json'),'mapping_binding':parent['mapping_binding'],
        'correction_profile_binding':bind(ENGINE/'write-profile.json')}
    with MANIFEST.open('xb') as stream:stream.write(encoded(manifest))
    pins=selected_pins();verify_engine(pins)
    with (HERE/'pins.json').open('xb') as stream:stream.write(encoded(pins.__dict__))
    print(json.dumps({'result':'PASS','parent_files_changed':0,'candidate_parent_deltas':len(delta),'files':len(manifest['files']),'pins':pins.__dict__},sort_keys=True))


if __name__=='__main__':freeze()
