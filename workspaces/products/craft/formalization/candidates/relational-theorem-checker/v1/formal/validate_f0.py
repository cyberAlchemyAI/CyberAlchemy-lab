#!/usr/bin/env python3
"""Fresh Lean replay, exact statement checks, axiom policy and hostile controls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[5]
MODULES = [
    ('RelationalInput', 'core/RelationalInput.lean'),
    ('RelationalSemantics', 'core/RelationalSemantics.lean'),
    ('ReferenceChecker', 'reference-checker/l0/ReferenceChecker.lean'),
    ('CheckerSoundness', 'proofs/l0/CheckerSoundness.lean'),
    ('FixtureGraphs', 'reference-checker/l0/FixtureGraphs.lean'),
    ('FormalCheckerControls', 'reference-checker/l0/formal-checker-controls.lean'),
    ('InhabitedExample', 'proofs/l0/inhabited-example.lean'),
    ('StatementAudit', 'proofs/l0/StatementAudit.lean'),
]
ALLOW = {'propext', 'Classical.choice', 'Quot.sound'}
FORBIDDEN = r'\b(sorry|admit|axiom|native_decide|unsafe)\b|debug\.skipKernelTC|Lean\.ofReduceBool|implemented_by|extern'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def digest(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def axiom_report(output):
    result = {}
    for name, values in re.findall(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", output):
        result[name] = [x.strip() for x in values.split(',') if x.strip()]
    for name in re.findall(r"'([^']+)' does not depend on any axioms", output):
        result[name] = []
    return result

def policy_accepts(output):
    report = axiom_report(output)
    return bool(report) and all(set(v) <= ALLOW for v in report.values())

def source_policy(text):
    # Policy scans code, not explanatory comments.
    code = re.sub(r'/\-.*?\-/', '', text, flags=re.S)
    code = re.sub(r'--[^\n]*', '', code)
    return re.search(FORBIDDEN, code) is None

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', type=Path, default=BASE/'.toolcache/lean-4.33.1-linux/bin/lean')
    parser.add_argument('--write', action='store_true', help='Write the replay receipt and log after all checks pass')
    args = parser.parse_args()
    lean = args.lean.resolve()
    lock = json.loads((BASE/'toolchain-lock.json').read_text())
    version = subprocess.check_output([str(lean), '--version'], text=True).strip()
    require(version == lock['version_output'], 'Lean version/commit differs from D00 pin')
    require(digest(lean) == lock['lean_binary_sha256'], 'Lean executable differs from verified official release')
    require(digest(lean.parent.parent/'lib/lean/libleanshared.so') == lock['lean_shared_library_sha256'], 'Lean kernel/runtime library differs')
    slice_ = json.loads((BASE/'core/source-slice.json').read_text())
    # Check the independently reviewed declaration table against live bound records.
    semantics = (BASE/'core/RelationalSemantics.lean').read_text()
    table = semantics.split('def allowedPairs')[1].split('abbrev NodeValid')[0]
    def ctor(s):
        return ''.join(x.capitalize() if i else x for i, x in enumerate(s.split('-')))
    for kind, record in zip(['conformsTo','declaresEffectOn','materializesConsequence'], slice_['records']):
        path = ROOT/record['path']
        require(digest(path) == record['sha256'], 'captured relation source drift: '+record['path'])
        require(json.loads(path.read_text())['payload'] == record['payload'], 'source projection differs')
        branch = re.search(r'\| \.'+kind+r' => \[([^\]]*)\]', table)
        require(branch is not None, 'missing declared signature branch')
        actual = re.findall(r'\(\.([A-Za-z]+), \.([A-Za-z]+)\)', branch.group(1))
        expected = [(ctor(p['source_kind']),ctor(p['target_kind'])) for p in record['payload']['allowed_endpoint_pairs']]
        require(actual == expected, 'ordered-pair table differs from source: '+kind)
    require(len(re.findall(r'\| \.', table)) == 3, 'unexpected signature branch')
    for _, relative in MODULES:
        code = (BASE/relative).read_text()
        require(source_policy(code), 'forbidden proof bypass in '+relative)
        require(set(re.findall(r'^import ([A-Za-z0-9_.]+)$', code, re.M)) <= {n for n,_ in MODULES} | {'Init'}, 'unexpected proof dependency')
    catalog = json.loads((BASE/'reference-checker/l0/control-catalog.json').read_text())
    logs, builds, controls = [], [], []
    with tempfile.TemporaryDirectory(prefix='relational-f0-replay-') as temp:
        build = Path(temp)
        env = {**os.environ, 'LEAN_PATH': str(build)}
        def run(file, output=False):
            cmd = [str(lean)]
            if output:
                cmd += ['-o', str(file.with_suffix('.olean'))]
            cmd += [str(file)]
            p = subprocess.run(cmd, cwd=build, env=env, text=True, capture_output=True, timeout=120)
            text = p.stdout+p.stderr
            logs.append({'module':file.stem,'returncode':p.returncode,'output':text})
            return p.returncode, text
        for name, relative in MODULES:
            file = build/(name+'.lean')
            shutil.copyfile(BASE/relative, file)
            code, output = run(file, True)
            require(code == 0 and 'warning:' not in output, 'Lean replay failed: '+name+'\n'+output)
            builds.append({'module':name,'source_path':relative,'source_sha256':digest(BASE/relative),'olean_sha256':digest(file.with_suffix('.olean'))})
            print('PASS', name, flush=True)
        axioms = axiom_report(logs[-1]['output'])
        expected_names = {
            'Relational.Audit.audited_instance', 'Relational.Audit.audited_graph', 'Relational.Audit.audited_addition',
            'Relational.instance_check_iff', 'Relational.graph_check_iff', 'Relational.addition_preserves_admission_roots',
            'Relational.Witnesses.inhabited_valid_graph', 'Relational.Witnesses.inhabited_valid_addition',
            'Relational.Witnesses.conformance_without_admission', 'Relational.Witnesses.independent_admission_coexistence',
        } | {c['name'] for c in catalog['controls']}
        require(set(axioms) == expected_names, 'missing/unexpected audited declarations')
        require(policy_accepts(logs[-1]['output']), 'unapproved transitive axiom')
        def rejected(name, text, kernel_accepts=False):
            file = build/('Hostile'+str(len(controls))+'.lean')
            file.write_text(text)
            code, output = run(file)
            if kernel_accepts:
                require(code == 0 and not policy_accepts(output), 'assumed proof escaped policy: '+name)
                mechanism = 'transitive-axiom policy'
            else:
                require(code != 0, 'hostile control accepted: '+name)
                mechanism = 'Lean elaboration/kernel type checking'
            controls.append({'control':name,'result':'rejected','mechanism':mechanism,'compiler_returncode':code})
        prefix = 'import StatementAudit\nopen Relational Relational.Audit\n'
        rejected('weakened conclusion', prefix+'theorem weak : True := True.intro\nexample : RequiredGraphSoundness := weak\n')
        rejected('conclusion as assumption', prefix+'theorem circular (g : Graph) : Inv g → Inv g := id\nexample : RequiredGraphSoundness := circular\n')
        rejected('sorry proof', prefix+'theorem assumed : RequiredGraphSoundness := by sorry\n#print axioms assumed\n', True)
        rejected('custom axiom proof', prefix+'axiom invented : RequiredGraphSoundness\ntheorem assumed : RequiredGraphSoundness := invented\n#print axioms assumed\n', True)
        rejected('missing typed qualifier field', prefix+'def bad : Qualifiers := .conformance "scope" "v1"\n')
        rejected('extra typed qualifier field', prefix+'def bad : Qualifiers := .conformance "scope" "v1" "ref" "extra"\n')
        rejected('unknown kind', prefix+'def bad : RelationKind := .futureKind\n')
        rejected('accept-all checker cannot prove soundness', prefix+'def badCheck (_g : Graph) : Bool := true\nexample : ∀ g, badCheck g = true → Inv g := graph_check_sound\n')
        # This mutation is checked against the unchanged semantic conclusion.
        mutant = (BASE/'proofs/l0/CheckerSoundness.lean').read_text().replace('import ReferenceChecker', 'import RelationalSemantics\nnamespace Relational\ndef checkInstance (_g : Graph) (_e : Assertion) : Bool := true\ndef checkGraph (_g : Graph) : Bool := true\ndef checkAddition (_g : Graph) (_e : Assertion) : Bool := true\nend Relational')
        rejected('removed checker conditions', mutant)
        for name, specimen in [('native proof evaluation','example : 1 = 1 := by native_decide'),('skip kernel check','set_option debug.skipKernelTC true')]:
            require(not source_policy(specimen), 'forbidden proof bypass accepted')
            controls.append({'control':name,'result':'rejected','mechanism':'source policy'})
        # Proof imports are closed to the audited local DAG and Init. Traverse
        # Init's actual serialized module headers to record its transitive closure.
        library = lean.parent.parent/'lib/lean'
        output = subprocess.check_output([str(lean),'--run',str(BASE/'proofs/l0/DependencyAudit.lean'),str(library),'Init'],cwd=build,env=env,text=True,timeout=120)
        deps = set()
        for name in output.splitlines():
            path = library/(name.replace('.','/')+'.olean')
            require(path.is_file(), 'missing transitive import '+name)
            deps.add(path)
            for suffix in ('.private','.server'):
                extra = Path(str(path)+suffix)
                if extra.is_file():
                    deps.add(extra)
        imports = [{'path':str(p.relative_to(lean.parent.parent)), 'sha256':digest(p)} for p in sorted(deps)]
    source_paths = [BASE/rel for _, rel in MODULES]
    source_paths += sorted(p for p in (BASE/'specification/l0').glob('*') if p.name != 'task-acceptance.json')
    source_paths += [BASE/'core/context-pack.json', BASE/'core/semantic-definition-audit.md', BASE/'core/source-slice.json', BASE/'reference-checker/l0/context-pack.json', BASE/'reference-checker/l0/reference-checker-contract.md',BASE/'reference-checker/l0/control-catalog.json',BASE/'proofs/l0/context-pack.json',BASE/'proofs/l0/DependencyAudit.lean',BASE/'lean-toolchain',BASE/'toolchain-lock.json',BASE/'validate_f0.py']
    receipt = {
        'schema':'relational.statement-and-axiom-audit/v1','result':'pass','phase':'F0',
        'claim_ceiling':'General soundness/completeness for the explicit three-kind typed finite input invariant; no JSON, external evidence authentication, crypto, compiled-runtime equivalence or authority admission.',
        'toolchain':{**lock,'verified_version':version},'modules':builds,'standard_library_imports':imports,
        'statement_audit':'Separate required targets elaborate and accept the named general theorems; exact elaborated types in lean-replay.log.',
        'axiom_allowlist':sorted(ALLOW),'transitive_axioms':axioms,
        'fixture_controls':catalog,'hostile_controls':controls,
        'source_bindings':[{'path':str(p.relative_to(ROOT)), 'sha256':digest(p)} for p in sorted(set(source_paths))],
        'relation_sources':[{k:r[k] for k in ('path','sha256')} for r in slice_['records']],
        'trust_boundaries':['faithful source interpretation','JSON decoding deferred to P02','external assessment/authority authentication and sufficiency','crypto content identity binding','compiled evaluator/compiler and host execution','Lean kernel and pinned core library'],
        'review_mode':'Author self-review; no independent human or organizational admission',
    }
    if args.write:
        (BASE/'proofs/l0/statement-and-axiom-audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (BASE/'proofs/l0/lean-replay.log').write_text('\n'.join(f"{l['module']} [exit={l['returncode']}]\n{l['output']}" for l in logs))
    print(json.dumps({'result':'pass','modules':len(builds),'audited_declarations':len(axioms),'fixtures':catalog['counts'],'hostile_controls_rejected':len(controls),'import_files':len(imports)},indent=2))

if __name__ == '__main__':
    main()
