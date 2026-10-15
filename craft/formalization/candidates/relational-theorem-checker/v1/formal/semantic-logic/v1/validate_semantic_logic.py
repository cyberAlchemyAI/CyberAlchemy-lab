#!/usr/bin/env python3
"""Replay semantic laws independently of the checker, with statement and axiom audits."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
FORMAL = BASE.parents[1]
ROOT = FORMAL.parents[5]

spec = importlib.util.spec_from_file_location('f0_audit_helpers', FORMAL/'validate_f0.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
require, digest = helpers.require, helpers.digest

MODULES = [
    ('RelationalInput', FORMAL/'core/RelationalInput.lean'),
    ('RelationalSemantics', FORMAL/'core/RelationalSemantics.lean'),
    ('SemanticLogic', BASE/'SemanticLogic.lean'),
    ('SemanticWitnesses', BASE/'SemanticWitnesses.lean'),
    ('SemanticStatementAudit', BASE/'SemanticStatementAudit.lean'),
]
GENERAL = [
    'identity_functional_of_nodup_map', 'assessment_identity_functional',
    'conformance_has_bound_assessment', 'conformance_evidence_functional',
    'materialization_has_bound_receipt', 'materialization_receipt_functional',
    'admission_roots_do_not_change_instance_meaning', 'well_formed_admission_variation_preserves_inv',
]
WITNESSES = [
    'inhabited_semantic_model', 'conformance_without_root',
    'conformance_does_not_entail_admission_root', 'admission_independence_models',
    'no_automatic_scope_upgrade', 'same_bound_evidence_reuse_is_allowed',
    'separate_scope_assessment_is_allowed', 'unique_identity_premise_is_needed',
    'functionality_without_invariant_is_false',
]
AUDITED = ['audited_conformance', 'audited_receipt', 'audited_non_entailment', 'audited_root_variation']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean', type=Path, default=FORMAL/'.toolcache/lean-4.33.1-linux/bin/lean')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    lean = args.lean.resolve()
    lock = json.loads((FORMAL/'toolchain-lock.json').read_text())
    version = subprocess.check_output([str(lean),'--version'], text=True).strip()
    require(version == lock['version_output'], 'pinned toolchain version mismatch')
    require(digest(lean) == lock['lean_binary_sha256'], 'pinned binary mismatch')
    require(digest(lean.parent.parent/'lib/lean/libleanshared.so') == lock['lean_shared_library_sha256'], 'pinned kernel/runtime mismatch')
    parent_path = FORMAL/'proofs/l0/statement-and-axiom-audit.json'
    parent = json.loads(parent_path.read_text())
    require(parent['result'] == 'pass', 'missing accepted parent formalization')
    for binding in parent['source_bindings']+parent['relation_sources']:
        require(digest(ROOT/binding['path']) == binding['sha256'], 'parent definition/source drift: '+binding['path'])
    for binding in parent['standard_library_imports']:
        require(digest(lean.parent.parent/binding['path']) == binding['sha256'], 'core dependency drift: '+binding['path'])
    allowed_imports = {name for name,_ in MODULES} | {'Init'}
    for name,path in MODULES:
        text = path.read_text()
        require(helpers.source_policy(text), 'proof bypass in '+name)
        imports = set(re.findall(r'^import ([A-Za-z0-9_.]+)$',text,re.M))
        require(imports <= allowed_imports, 'unexpected import in '+name)
        require('checkGraph' not in text and 'checkInstance' not in text and 'CheckerSoundness' not in text, 'checker dependency in semantic proof')
    logs, builds, controls = [], [], []
    with tempfile.TemporaryDirectory(prefix='semantic-logic-replay-') as temp:
        build = Path(temp)
        env = {**os.environ,'LEAN_PATH':str(build)}
        def run(file, emit=False):
            cmd = [str(lean)] + (['-o',str(file.with_suffix('.olean'))] if emit else []) + [str(file)]
            result = subprocess.run(cmd,cwd=build,env=env,text=True,capture_output=True,timeout=120)
            text = result.stdout+result.stderr
            logs.append({'module':file.stem,'returncode':result.returncode,'output':text})
            return result.returncode,text
        for name,path in MODULES:
            file = build/(name+'.lean')
            shutil.copyfile(path,file)
            code,text = run(file,True)
            require(code == 0 and 'warning:' not in text, 'Lean replay failed: '+name+'\n'+text)
            builds.append({'module':name,'source_path':str(path.relative_to(ROOT)),'source_sha256':digest(path),'olean_sha256':digest(file.with_suffix('.olean'))})
            print('PASS',name,flush=True)
        axiom_report = helpers.axiom_report(logs[-1]['output'])
        expected = {'Relational.Logic.'+n for n in GENERAL} | {'Relational.Logic.Witnesses.'+n for n in WITNESSES} | {'Relational.Logic.Audit.'+n for n in AUDITED}
        require(set(axiom_report) == expected, 'semantic statement audit omitted or substituted a declaration')
        require(helpers.policy_accepts(logs[-1]['output']), 'unapproved transitive axiom')
        def reject(name,text,assumed=False):
            file = build/('Hostile'+str(len(controls))+'.lean');file.write_text(text)
            code,output = run(file)
            if assumed:
                require(code == 0 and not helpers.policy_accepts(output),'assumed semantic theorem escaped audit')
                mechanism = 'transitive-axiom policy'
            else:
                require(code != 0,'false/weakened semantic claim accepted: '+name)
                require('unknown module' not in output and 'Unknown identifier' not in output and 'unexpected token' not in output,
                        'negative control failed before checking its intended semantic claim: '+name)
                mechanism = 'Lean statement/type or kernel reduction check'
            controls.append({'name':name,'result':'rejected','mechanism':mechanism,'compiler_returncode':code})
        prefix = 'import SemanticStatementAudit\nopen Relational Relational.Logic Relational.Logic.Audit\n'
        reject('weakened semantic conclusion',prefix+'theorem weak : True := True.intro\nexample : RequiredConformanceFunctionality := weak\n')
        reject('conformance grants admission',prefix+'example : HasAdmissionRoot Witnesses.graph Witnesses.conforms.source := by decide\n')
        reject('scope upgrade under same evidence',prefix+'example : ConformsAt Witnesses.graph Witnesses.runtimeConforms "runtime" "v1" "evidence" := by decide\n')
        reject('ambiguous assessment identities are valid',prefix+'example : Inv Witnesses.ambiguousGraph := by decide\n')
        reject('assumed semantic theorem',prefix+'theorem assumed : RequiredConformanceFunctionality := by sorry\n#print axioms assumed\n',True)
        reject('custom semantic axiom',prefix+'axiom invented : RequiredReceiptFunctionality\ntheorem assumed : RequiredReceiptFunctionality := invented\n#print axioms assumed\n',True)
    paths = [p for _,p in MODULES]+[Path(__file__),BASE/'THEOREMS.md']
    receipt = {
        'schema':'relational.semantic-logic-audit/v1','result':'pass','status':'candidate derived semantic theorems',
        'toolchain':version,'parent_formalization':{'path':str(parent_path.relative_to(ROOT)),'sha256':digest(parent_path)},
        'proof_dependency_policy':'RelationalInput, RelationalSemantics and the three semantic modules only; no checker or checker-correctness theorem imported.',
        'modules':builds,'general_theorems':GENERAL,'semantic_witnesses_and_countermodels':WITNESSES,
        'exact_statement_assignments':AUDITED,'transitive_axioms':axiom_report,'axiom_allowlist':sorted(helpers.ALLOW),
        'negative_controls':controls,'verified_core_import_files':len(parent['standard_library_imports']),
        'source_bindings':[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in paths],
        'claim_ceiling':'Consequences and non-entailments of the accepted static input-relative semantics; no evidence authentication, real authority, transaction execution or inference-engine closure theorem.',
        'review_mode':'Codex author self-review; existing F0 acceptance and semantic definitions remain unchanged.',
    }
    if args.write:
        (BASE/'semantic-logic-audit.json').write_text(json.dumps(receipt,indent=2)+'\n')
        (BASE/'lean-replay.log').write_text('\n'.join(f"{x['module']} [exit={x['returncode']}]\n{x['output']}" for x in logs))
    print(json.dumps({'result':'pass','modules':len(builds),'general_theorems':len(GENERAL),'witnesses_and_countermodels':len(WITNESSES),'audited_declarations':len(axiom_report),'negative_controls_rejected':len(controls),'checker_dependencies':0},indent=2))

if __name__ == '__main__':
    main()
