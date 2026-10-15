"""Keep original checks; avoid verifying the same producer twice per policy call."""
import ast
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v54', BASE / 'api-v55'


def main():
    assert not API.exists()
    shutil.copytree(OLD, API, ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json'))
    for old_name, new_name in [('lesson-host-composition-v4', 'lesson-host-composition-v5'),
                               ('api54-package-checks-v1', 'api55-package-checks-v1'),
                               ('api54-session-checks-v1', 'api55-session-checks-v1')]:
        target = BASE / new_name
        assert not target.exists()
        shutil.copytree(BASE / old_name, target, ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json'))
        for path in target.rglob('*.py'):
            text = path.read_text().replace('api-v54', 'api-v55').replace('_API54', '_API55')
            path.write_text(text)
    path = API / 'lesson_selection.py'
    path.write_text(path.read_text().replace('lesson-host-composition-v4', 'lesson-host-composition-v5'))
    path = API / 'auth.py'
    text = path.read_text()
    before = '''        borrowed=FACT_SCOPE.policy_scope(self)
        if borrowed is not None:
            source.require(value['source_name']=='custody-participation' and borrowed.host is self,'borrowed source selection differs')
            borrowed.check()
        elif check_source:source.source_selection(value['source_name'])
'''
    after = '''        borrowed=FACT_SCOPE.policy_scope(self)
        # Invocation-local producer selection only: no source bytes, digest,
        # policy, permission or clock are cached between calls. The original
        # preflight and reader selection still execute in this invocation.
        selected_delivery=None
        if borrowed is not None:
            source.require(value['source_name']=='custody-participation' and borrowed.host is self,'borrowed source selection differs')
            borrowed.check()
        elif check_source:
            if value['source_name']=='custody-participation':
                selected_delivery=source.custody_delivery()
                selected_delivery.reader.selection(selected_delivery.SOURCE_PIN,selected_delivery.SOURCE_PACKAGE,value['source_name'])
            else:source.source_selection(value['source_name'])
'''
    assert before in text
    text = text.replace(before, after)
    before = 'd=borrowed.producer if borrowed is not None else source.custody_delivery()'
    after = 'd=borrowed.producer if borrowed is not None else selected_delivery'
    assert text.count(before) == 2
    text = text.replace(before, after)
    ast.parse(text)
    path.write_text(text)
    print('API55 authored with invocation-local original producer selection; all original source callbacks retained.', flush=True)


if __name__ == '__main__':
    main()
