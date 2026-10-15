"""Bind classification v8 and independently qualify the closed axis fixture."""
import ast
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v55', BASE / 'api-v56'
CHECK = BASE / 'api56-classification-checks-v1'


def main():
    assert not API.exists() and not CHECK.exists()
    shutil.copytree(OLD, API, ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json'))
    lesson = BASE / 'lesson-host-composition-v6'
    assert not lesson.exists()
    shutil.copytree(BASE / 'lesson-host-composition-v5', lesson,
                    ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json'))
    path = lesson / 'host.py'
    path.write_text(path.read_text().replace('api-v55/service.py', 'api-v56/service.py'))
    path = API / 'lesson_selection.py'
    path.write_text(path.read_text().replace('lesson-host-composition-v5', 'lesson-host-composition-v6'))
    path = API / 'classification_preparation.py'
    path.write_text(path.read_text().replace('classification-preparation-v7', 'classification-preparation-v8')
                    .replace('classification_preparation_v7', 'classification_preparation_v8'))
    CHECK.mkdir()
    (CHECK / '__init__.py').write_text('"""Separately bound original classification qualification successor."""\n')
    original = (API / 'test_classification_api.py').read_text()
    before = '''    def test_09_independent_axis_is_preserved(self):
        host, request, _ = self.example(mode='independent-axis')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'result', reply)
        checked = self.rules(host)[0]
        self.assertEqual(checked['result'], 'pass')
        self.assertEqual(len(checked['complete_postimage_assignment_refs']), 1)
        self.assertEqual(checked['axis_ref'], request['message']['axis_ref'])
        self.assertEqual(len(reply['message']['targets']), 5)
        self.assert_live(host, request)
'''
    after = '''    def test_09_independent_axis_is_preserved(self):
        host, request, selected = self.example(mode='independent-axis')
        reply = self.invoke(host, request)
        self.assertEqual(reply['kind'], 'result', reply)
        checked = self.rules(host)[0]
        self.assertEqual(checked['result'], 'pass')
        self.assertEqual(len(checked['complete_postimage_assignment_refs']), 1)
        self.assertEqual(checked['axis_ref'], request['message']['axis_ref'])
        self.assertEqual(reply['message'], selected['proposal'])
        self.assertEqual(len(reply['message']['targets']), 9)
        from collections import Counter
        counts=Counter(t['artifact']['carrier_ref'] for t in reply['message']['targets'])
        self.assertEqual(counts, {'cal.artifact-type.classification-scheme/v1':1,
            'cal.artifact-type.classification-value/v1':2,
            'cal.artifact-type.classification-assignment/v1':2,
            'cal.artifact-type.typed-relation/v3':4})
        relations=[t for t in reply['message']['targets']
                   if t['artifact']['carrier_ref']=='cal.artifact-type.typed-relation/v3']
        connections=reply['message']['connection_proposals']
        self.assertEqual(len(connections),4)
        from .artifact_model import signature
        for target,connection in zip(relations,connections,strict=True):
            content=target['content']
            raw=host.vault.material({'ref':content['content_ref'],'sha256':content['byte_sha256']})
            body=P.frame_parse(raw);payload=body['payload']
            contract,binding=signature(host.handlers.view,payload['relation_kind_ref'])
            self.assertEqual(connection['relation_kind_ref'],payload['relation_kind_ref'])
            self.assertEqual(connection['signature_sha256'],binding['sha256'])
            self.assertEqual(connection['axis_ref'],contract['payload']['axis_id'])
            self.assertIn({'source_kind':payload['source']['kind'],
                           'target_kind':payload['target']['kind']},
                          contract['payload']['allowed_endpoint_pairs'])
            self.assertEqual(connection['qualifiers'],payload['qualifiers'])
            for end in ['source','target']:
                self.assertEqual(connection[end]['semantic_kind'],payload[end]['kind'])
                self.assertEqual(connection[end]['artifact']['identity_ref'],payload[end]['ref'])
                self.assertEqual(connection[end]['artifact']['version_ref'],payload[end]['version_ref'])
        self.assert_live(host, request)
'''
    assert before in original
    revised = original.replace(before, after, 1)
    ast.parse(revised)
    with (CHECK / 'test_classification_api.py').open('x') as stream:
        stream.write(revised)
    print('API56 selects classification v8; original test file unchanged; one separate method successor adds exact nine-target/four-relation checks.', flush=True)


if __name__ == '__main__':
    main()
