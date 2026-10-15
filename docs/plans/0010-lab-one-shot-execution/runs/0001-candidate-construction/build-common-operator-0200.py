"""Stage an explicitly unfrozen API13 successor; preserve the frozen API12."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-integration-v12'
NEW = BASE / 'api-integration-v13'
SOURCE = '5c7f5c69d5795f5a5c0cb8b67c52a47621f8eab746c6afd70d42f06177ddc6ae'
PROFILE = '2ae21af91f8366247cbd3ff77292d307519663fd020bac20cb410fd2d76db56a'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert not NEW.exists(), 'new exclusive successor directory required'
    assert sha(OLD / 'contract-profile.json') == PROFILE
    spec = importlib.util.spec_from_file_location('_cal_api13_parent_guard', OLD / 'guard.py')
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    guard.verify(SOURCE)
    shutil.copytree(OLD, NEW, ignore=shutil.ignore_patterns('receipts', '__pycache__'))
    # A staged directory must not claim the predecessor's signed source/profile.
    for name in ('source-manifest.json', 'contract-profile.json', 'SCHEMA-EXECUTION-DEPENDENCIES.json'):
        (NEW / name).unlink()
    path = NEW / 'protocol.py'
    text = path.read_text()
    lines = text.splitlines(keepends=True)
    tree = ast.parse(text)
    replacements = {
        'LESSON_ONTOLOGY_SUPPORTED': "LESSON_SUPPORTED=LEGACY_SUPPORTED+('lesson.select',)\n",
        'APPLICATION_SESSION_ONTOLOGY_SUPPORTED': "APPLICATION_SESSION_SUPPORTED=LEGACY_SUPPORTED+('lesson.apply',)\n",
    }
    selected = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in replacements:
                selected.append((node, replacements[name]))
    assert len(selected) == 2, 'exact two corrupted policy selectors required'
    for node, replacement in reversed(selected):
        lines[node.lineno - 1:node.end_lineno] = [replacement]
    result = ''.join(lines)
    # Keep only the final supported catalog assignment; earlier accidental
    # assignments were overwritten and granted no separate policy selection.
    parsed = ast.parse(result)
    duplicates = [n for n in parsed.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'SUPPORTED' for t in n.targets)]
    assert len(duplicates) == 3
    output = result.splitlines(keepends=True)
    for node in reversed(duplicates[:-1]):
        del output[node.lineno - 1:node.end_lineno]
    path.write_text(''.join(output))
    for file in NEW.glob('*.py'):
        ast.parse(file.read_text())
    guard.verify(SOURCE)
    print(json.dumps({'result': 'STAGED', 'api_directory': NEW.relative_to(ROOT).as_posix(),
                      'fixed_policy_selectors': list(replacements), 'source_frozen': False,
                      'runtime_qualified': False, 'goal_complete': False}), flush=True)

if __name__ == '__main__':
    main()
