"""Build coherent synthetic controls; this generator supplies no authenticity proof."""
from pathlib import Path
import copy, hashlib, json
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[9]
def read(path): return json.loads(path.read_text())
def binding(path): return {'path': str(path.relative_to(ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
def raw(value): return json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode()
def ref(value): return {'key': value['binding_revision_key'], 'digest': hashlib.sha256(raw(value)).hexdigest()}
def lean_ref(value):
    k = value['key']
    return '⟨⟨' + ','.join(json.dumps(k[x]) for x in ['owner','artifact','revision']) + '⟩,' + json.dumps(value['digest']) + '⟩'
def expected():
    prior = HERE.parent / 'K02-profile-evidence/fixtures'
    frame = read(HERE.parent / 'K02-catalog-snapshots/fixtures/metadata.json')['context']['frame']
    declaration, selection, authority = [read(prior / (n + '.json')) for n in ['declaration','selection','authority-positive']]
    old_decl = {'key': declaration['binding_revision_key'], 'digest': hashlib.sha256((prior/'declaration.json').read_bytes()).hexdigest()}
    old_sel = {'key': selection['binding_revision_key'], 'digest': hashlib.sha256((prior/'selection.json').read_bytes()).hexdigest()}
    declaration['body']['frame'] = frame
    selection['body']['frame'] = frame
    new_decl = ref(declaration)
    selection['body']['target']['declaration_ref'] = new_decl
    new_sel = ref(selection)
    authority['body']['frame'] = frame
    target = authority['body']['target']
    target['declaration_manifest'] = [new_decl]
    target['selection_manifest'] = [new_sel]
    for issue in target['issuances']:
        if issue['source_ref'] == old_decl: issue.update(source_ref=new_decl, source_bytes=list(raw(declaration)))
        elif issue['source_ref'] == old_sel: issue.update(source_ref=new_sel, source_bytes=list(raw(selection)))
        else: raise AssertionError('unexpected original issuance')
    for review in target['reviews']:
        if review['source_ref'] == old_decl: review['source_ref'] = new_decl
        elif review['source_ref'] == old_sel: review['source_ref'] = new_sel
        else: raise AssertionError('unexpected original review')
    for grant in target['entitlements']: grant['scope'] = frame['scope']
    missing = copy.deepcopy(authority)
    missing['body']['target']['reviews'] = []
    return {'declaration': declaration,'selection': selection,'authority-positive': authority,'authority-missing-review': missing}
def lean_source(values):
    lines = ['import SelectedRelationPipeline','import CatalogRuntimeControls','import AuthorityControls',
             'set_option autoImplicit false','set_option maxRecDepth 65536','set_option maxHeartbeats 10000000','namespace RelationalSuccessor.CandidateSelectedRelation.GeneratedFixture',
             'open CandidateBindingCapture (Envelope)','open CandidateProfileEvidence.Controls (bootstrap root)']
    for name, value in values.items():
        ident = {'authority-positive':'authority','authority-missing-review':'missingReview'}.get(name,name)
        data = raw(value)
        lines += [f'def {ident}Ref : RevisionRef := {lean_ref(ref(value))}',
                  f'def {ident} : Envelope := ⟨{list(data)},{len(data)},bootstrap.ref,{json.dumps(ref(value)["digest"])}⟩']
    lines += ['end RelationalSuccessor.CandidateSelectedRelation.GeneratedFixture']
    return '\n'.join(lines) + '\n'
def run():
    fixtures = HERE / 'fixtures'; fixtures.mkdir(exist_ok=True)
    values = expected()
    for name, value in values.items(): (fixtures / (name+'.json')).write_bytes(raw(value))
    (HERE/'SelectedProfileFixture.lean').write_text(lean_source(values))
    print('Generated four coherent synthetic source fixtures and exact byte literals.')
if __name__ == '__main__': run()
