"""Create an exclusive rule successor for explicit Context Query exclusions."""
import ast
import hashlib
import json
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, NEW = BASE/'lesson-selection-rules-v1', BASE/'lesson-selection-rules-v2'


def main():
    manifest = json.loads((OLD/'source-manifest.json').read_bytes())
    assert manifest['source_sha256'] == '2e03a517674dcf2c74e1165f3cdd6eb1f5d589001c79b90a02e7c065b303c046'
    for row in manifest['files'] + manifest['input_bindings']:
        assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256']
    NEW.mkdir()
    for row in manifest['files']:
        p = ROOT/row['path']; (NEW/p.name).write_bytes(p.read_bytes())
    p = NEW/'rules.py'; text = p.read_text()
    text = text.replace('lesson-selection-rules-v1/rules.py', 'lesson-selection-rules-v2/rules.py')
    old = '    counterevidence_bindings: tuple[dict, ...]\n'
    assert text.count(old) == 1
    text = text.replace(old, old+'    query_excluded: bool = False\n')
    old = "            payload = body['payload']\n"
    assert text.count(old) == 1
    text = text.replace(old, old+"            require(type(fact.query_excluded) is bool, 'query exclusion fact unresolved')\n")
    old = "                if rule['project_ref'] != facts.project_ref or facts.project_ref not in payload['scope_refs']:\n"
    assert text.count(old) == 1
    text = text.replace(old, "                if fact.query_excluded:\n                    posture, reason = 'omitted', 'explicit-request-exclusion'\n                elif rule['project_ref'] != facts.project_ref or facts.project_ref not in payload['scope_refs']:\n")
    p.write_text(text)
    p = NEW/'test_rules.py'; p.write_text(p.read_text().replace('lesson-selection-rules-v1/rules.py','lesson-selection-rules-v2/rules.py'))
    def tests(p):
        return {n.name:ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(p.read_bytes()))
                if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
    assert tests(OLD/'test_rules.py') == tests(NEW/'test_rules.py') and len(tests(NEW/'test_rules.py')) == 56
    p = NEW/'checks.py'; text=p.read_text().replace('== 56','== 61').replace('56 complete','61 complete').replace("pattern='test_rules.py'", "pattern='test_*.py'")
    p.write_text(text)
    p = NEW/'README.md'; text=p.read_text().replace('56','61')
    p.write_text(text+'\nThis successor applies independently resolved explicit Context Query exclusions\nbefore eligible conflict pairs are formed. It retains all56 predecessor methods\nand the original W06 suite. Public source and Session qualification remain pending.\n')
    print(json.dumps({'result':'CONSTRUCTED-UNFROZEN', 'retained_methods':56, 'public_calls':0}),flush=True)


if __name__ == '__main__': main()
