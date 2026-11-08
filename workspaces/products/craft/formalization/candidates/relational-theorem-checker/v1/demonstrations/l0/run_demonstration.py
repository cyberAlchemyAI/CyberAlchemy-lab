#!/usr/bin/env python3
"""Produce and replay the exact three-kind relation addition demonstration."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'input'))
import decoder as d
s=d.s
BASE=Path(__file__).resolve().parent


def replay(receipt):
    for b in receipt['dependencies']:
        s.check_binding(b)
    for b in receipt['evaluation_artifacts']:
        s.check_binding(b)
    s.require(receipt['profile']==s.binding(s.FORMAL/'specification/l0/semantic-contract.md'), 'profile identity mismatch')
    raw=(s.ROOT/receipt['input']['path']).read_bytes()
    s.require(hashlib.sha256(raw).hexdigest()==receipt['input']['sha256']==receipt['raw_input_sha256'],'graph/input binding mismatch')
    normal=d.normalize(d.decode(raw))
    canonical=hashlib.sha256(json.dumps(normal,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
    s.require(canonical==receipt['result']['normal_form_sha256'],'normalization binding mismatch')
    s.require(receipt['result']['accepted_result'] and receipt['result']['proof_method']=='kernel-checked-instance-via-general-soundness','missing accepted evaluation proof')
    return True


def main():
    s.context('P06',[(s.PLAN,'tasks[id=P06]'),(d.BASE/'task-acceptance.json','accepted decoder mapping and controls'),
        (s.FORMAL/'proofs/l0/task-acceptance.json','general theorem and axiom closure'),
        (s.FORMAL/'specification/l0/semantic-contract.md','exact semantic profile'),
        (d.BASE/'example-addition.json','inhabited fixture graph and proposed materialization')],
        [{'classification':'non-blocking','choice':'kernel-check each accepted evaluation and preserve raw fixture bytes',
          'basis':'Runtime true alone is insufficient evidence for the specific graph invariant.'}])
    raw=(d.BASE/'example-addition.json').read_bytes();value=d.decode(raw);normal=d.normalize(value)
    (BASE/'input.json').write_bytes(raw);s.write(BASE/'normal-form.json',normal)
    artifacts=[]
    for node in value['graph']['nodes']:
        content=('fixture:'+node['node_id']).encode()
        s.require(hashlib.sha256(content).hexdigest()==node['source_ref']['sha256'] and len(content)==node['source_ref']['size_bytes'],'fixture content binding failed')
        target=BASE/'fixtures'/(node['source_ref']['sha256']+'.txt');target.parent.mkdir(exist_ok=True);target.write_bytes(content)
        artifacts.append(s.binding(target,artifact_id=node['source_ref']['artifact_id'],posture='synthetic fixture bytes; no real-world observation'))
    with tempfile.TemporaryDirectory(prefix='l0-demonstration-') as folder:
        build=Path(folder);modules=s.compile_lean(build,d.core_modules());result=d.check(normal,build)
        s.require(result['accepted_base'] and result['accepted_result'],'inhabited demonstration rejected')
        for name in ['InputQuery.lean','InputEvaluation.lean','InputEvaluation.olean']:
            (BASE/name).write_bytes((build/name).read_bytes())
        local_controls=[]
        spec=importlib.util.spec_from_file_location('demonstration_policy',s.FORMAL/'validate_f0.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
        for name,body,assumed in [
            ('weakened general proof','theorem weak : True := True.intro\nexample : ∀ g, checkGraph g = true → Inv g := weak\n',False),
            ('assumed general proof','theorem forged : ∀ g, checkGraph g = true → Inv g := by sorry\n#print axioms forged\n',True),
            ('custom graph axiom','axiom invented : ∀ g, checkGraph g = true → Inv g\ntheorem forged : ∀ g, checkGraph g = true → Inv g := invented\n#print axioms forged\n',True)]:
            path=build/'HostileProof.lean';path.write_text('import CheckerSoundness\nopen Relational\n'+body)
            run=subprocess.run([str(s.lean_path()),str(path)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},text=True,capture_output=True,timeout=60)
            output=run.stdout+run.stderr
            s.require((run.returncode==0 and not policy.policy_accepts(output)) if assumed else run.returncode!=0,'hostile proof accepted')
            local_controls.append({'name':name,'result':'rejected','mechanism':'transitive axiom policy' if assumed else 'independent required type'})
    dependencies=[s.binding(BASE.parent.parent/'baseline/baseline-manifest.json'),s.binding(d.BASE/'decoder.py'),
        s.binding(d.BASE/'normal-form-schema.json'),s.binding(s.FORMAL/'proofs/l0/statement-and-axiom-audit.json'),
        s.binding(s.FORMAL/'specification/l0/semantic-contract.md')]+[m['source'] for m in modules]+artifacts
    receipt={'schema':'relational.addition-demonstration/v1','authority_effect':'none',
        'input':s.binding(BASE/'input.json'),'raw_input_sha256':hashlib.sha256(raw).hexdigest(),
        'profile':s.binding(s.FORMAL/'specification/l0/semantic-contract.md'),
        'generic_theorem':'Relational.graph_check_sound','specific_theorem':'evaluated_model : Inv (applyAddition base addition)',
        'evaluation_artifacts':[s.binding(BASE/n) for n in ['InputQuery.lean','InputEvaluation.lean','InputEvaluation.olean']],
        'dependencies':dependencies,'result':result,'scope':'three-kind input-relative graph invariant',
        'trust_boundaries':result['runtime_trust']}
    s.require(replay(receipt),'receipt replay failed')
    for name,mutate in [('old receipt with changed graph hash',lambda r:r.update(raw_input_sha256='0'*64)),
                        ('old receipt with changed profile',lambda r:r['profile'].update(sha256='0'*64)),
                        ('missing accepted evaluation',lambda r:r['result'].update(accepted_result=False))]:
        bad=deepcopy(receipt);mutate(bad)
        try:replay(bad)
        except ValueError:local_controls.append({'name':name,'result':'rejected','mechanism':'exact replay bindings'})
        else:raise ValueError('stale or invalid receipt accepted')
    s.write(BASE/'demonstration-receipt.json',receipt)
    decoded=s.read(d.BASE/'decoding-controls.json')
    s.write(BASE/'hostile-control-report.json',{'result':'pass','decoder_control_receipt':s.binding(d.BASE/'decoding-controls.json'),
        'decoder_controls':decoded['controls'],'local_controls':local_controls,'positive_receipt_replay':True,
        'claim_ceiling':'Fixture and exact-binding replay; no increased generic theorem scope.'})
    s.accept('P06',{n:BASE/n for n in ['demonstration-receipt.json','hostile-control-report.json']},
        ['The exact saved input, normal form, fixture bytes, semantic profile, theorem dependencies and evaluation artifacts replay without drift.',
         'A six-node inhabited graph and materialization addition pass; pair, qualifier, reference, digest and weakened/assumed proof controls reject.',
         'The unchanged ReferenceChecker and general CheckerSoundness are compiled; the specific result is kernel checked against Inv.'],
        ['Graph/profile hash changes and missing accepted evaluation reject before receipt reuse.',
         'The result remains the input-relative three-kind theorem; fixtures and external evidence assumptions are explicitly labelled.'],
        [Path(__file__),BASE/'input.json',BASE/'normal-form.json',BASE/'InputEvaluation.lean',BASE/'InputEvaluation.olean',d.BASE/'decoding-controls.json'])
    print(json.dumps({'task':'P06','result':'accepted','assertions':result['assertion_count'],'hostile_controls':len(decoded['controls'])+len(local_controls)}))


if __name__=='__main__':main()
