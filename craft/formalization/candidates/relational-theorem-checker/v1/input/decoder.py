#!/usr/bin/env python3
"""Deterministic strict JSON projection into the unchanged F0 Lean model."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import jsonschema
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'execution'))
import support as s

BASE = Path(__file__).resolve().parent
INTERFACES = BASE.parent / 'interfaces'
KINDS = {'relation.conforms-to':'conformsTo','relation.declares-effect-on':'declaresEffectOn',
         'relation.materializes-consequence':'materializesConsequence'}
NODE_KINDS = ['admission-transaction','agent-capability','agent-profile','artifact-type','capability-instance',
    'capability-realization-binding','challenge-event','classification-assignment','communication-preference',
    'context','context-profile','contract','decision','definition','delegation','effect','failure-assessment',
    'failure-control-binding','failure-mode','failure-occurrence','generated-output','governed-model',
    'improvement-target','incident','intent-resolution','operational-lesson','product-capability',
    'project-governance-event-history','project-semantic-event-history','project-state','relation-kind']


def object_pairs(pairs):
    result = {}
    for key,value in pairs:
        s.require(key not in result, 'duplicate JSON member')
        result[key] = value
    return result


def decode(raw):
    if isinstance(raw, bytes):
        text = raw.decode('utf-8', errors='strict')
    else:
        text = raw
    def bad_constant(_):raise ValueError('non-finite JSON number')
    value = json.loads(text, object_pairs_hook=object_pairs, parse_constant=bad_constant)
    def unicode_valid(item):
        if isinstance(item,str):item.encode('utf-8',errors='strict')
        elif isinstance(item,list):
            for v in item:unicode_valid(v)
        elif isinstance(item,dict):
            for k,v in item.items():unicode_valid(k);unicode_valid(v)
    unicode_valid(value)
    return value


def validators():
    schemas = [s.read(p) for p in (INTERFACES/'schemas').glob('*.schema.json')]
    own = s.read(BASE/'normal-form-schema.json')
    schemas.append(own)
    registry = Registry().with_resources((schema['$id'],Resource.from_contents(schema,default_specification=DRAFT202012)) for schema in schemas)
    return {schema['$id'].split('/')[-1]:jsonschema.Draft202012Validator(schema,registry=registry) for schema in schemas}


def unique(rows, key, label):
    values = [key(row) for row in rows]
    s.require(len(values) == len(set(values)), 'duplicate ' + label)


def ref(node):
    return {'id':node['node_id'], 'version':node['version']}


def key(r):return r['id'],r['version']


def normalize(value):
    # Both the old companion carrier and the new sidecar envelope are validated.
    v = validators()
    s.require(isinstance(value,dict) and set(value) in [
        {'schema_version','graph','assessments','admission_roots'},
        {'schema_version','graph','assessments','admission_roots','addition'}], 'unknown or missing input field')
    s.require(value['schema_version']=='relational-checker.execution-input/v1', 'unknown input schema')
    raw_graph=value['graph']
    errors=list(v['l0-graph.schema.json'].iter_errors(raw_graph))
    s.require(not errors, 'invalid three-kind companion graph shape')
    if 'addition' in value:
        s.require(not list(v['l0-assertion.schema.json'].iter_errors(value['addition'])), 'invalid addition shape')
    unique(raw_graph['nodes'],lambda n:(n['node_id'],n['version']),'node identity/version')
    unique(raw_graph['assertions'],lambda a:a['assertion_id'],'assertion identity')
    nodes={key(ref(n)):n for n in raw_graph['nodes']}
    baseline=s.read(BASE.parent/'baseline/baseline-manifest.json')
    definitions={r['entry']['relation_kind_id']:r['entry'] for r in baseline['records']}
    projected_nodes=[]
    for n in raw_graph['nodes']:
        s.require(n['kind'] in NODE_KINDS, 'node kind outside F0 typed profile')
        projected_nodes.append({'ref':ref(n),'kind':n['kind'],'content_identity':n['source_ref']['sha256']})
    def assertion(a):
        expected=definitions[a['relation_kind_id']]
        s.require(a['relation_kind_version']=='sha256:'+expected['instance_sha256'], 'wrong relation definition version')
        s.require(a['definition_ref']['sha256']==expected['instance_sha256'] and
                  a['definition_ref']['artifact_id']==a['relation_kind_id'] and
                  a['definition_ref']['size_bytes']==(s.ROOT/expected['instance_path']).stat().st_size,
                  'wrong relation definition binding')
        for side in ['source','target']:
            r=ref(a[side]);s.require(key(r) in nodes, 'unresolved exact endpoint')
            s.require(a[side]==nodes[key(r)], 'endpoint kind/version/content differs from inventory')
        return {'id':a['assertion_id'],'kind':a['relation_kind_id'],'source':ref(a['source']),
                'target':ref(a['target']),'qualifiers':a['qualifiers']}
    g={'graph_id':raw_graph['graph_id'],'nodes':projected_nodes,
       'assertions':[assertion(a) for a in raw_graph['assertions']],
       'assessments':value['assessments'],'admission_roots':value['admission_roots']}
    normal={'schema_version':'relational-checker.normal-form/v1','graph':g}
    if 'addition' in value:normal['addition']=assertion(value['addition'])
    s.require(not list(v['normal-form-schema.json'].iter_errors(normal)), 'invalid evidence/root sidecar shape')
    unique(g['assessments'],lambda a:a['ref'],'assessment identity')
    for a in g['assessments']:
        for k in ['subject','target']:s.require(key(a[k]) in nodes, 'unresolved assessment endpoint')
    for a in g['admission_roots']:
        for k in ['subject','decision']:s.require(key(a[k]) in nodes, 'unresolved supplied root endpoint')
    return normal


def literal(text):
    # Scalar encoding preserves arbitrary valid Unicode and control characters;
    # input text can never terminate a source-code string or inject Lean syntax.
    return '(String.ofList ['+', '.join('(Char.ofNat '+str(ord(c))+')' for c in text)+'])'


def camel(text):return ''.join(w.capitalize() if i else w for i,w in enumerate(text.split('-')))
def refs(r):return '{ id := '+literal(r['id'])+', version := '+literal(r['version'])+' }'
def rows(values,fn):return '['+', '.join(fn(v) for v in values)+']'


def assertion_lean(a):
    q=a['qualifiers']
    if a['kind']=='relation.conforms-to':
        qualifier='.conformance '+literal(q['conformance_scope'])+' '+literal(q['exact_version_ref'])+' '+literal(q['conformance_evidence_refs'])
    elif a['kind']=='relation.declares-effect-on':
        qualifier='.effect '+literal(q['effect_kind'])+' '+literal(q['exact_target_version_ref'])
    else:qualifier='.materialization '+literal(q['application_receipt_ref'])+' '+literal(q['consequence_role'])+' '+literal(q['output_digest'])
    return '{ id := '+literal(a['id'])+', kind := .'+KINDS[a['kind']]+', source := '+refs(a['source'])+', target := '+refs(a['target'])+', qualifiers := '+qualifier+' }'


def graph_lean(g):
    def node(n):return '{ ref := '+refs(n['ref'])+', kind := .'+camel(n['kind'])+', contentIdentity := '+literal(n['content_identity'])+' }'
    def assessment(a):return '{ ref := '+literal(a['ref'])+', mode := .'+camel(a['mode'])+', subject := '+refs(a['subject'])+', target := '+refs(a['target'])+', scope := '+literal(a['scope'])+', role := '+literal(a['role'])+', outputDigest := '+literal(a['output_digest'])+', accepted := '+str(a['accepted']).lower()+' }'
    def root(a):return '{ subject := '+refs(a['subject'])+', decision := '+refs(a['decision'])+', authorityEvidence := '+literal(a['authority_evidence'])+' }'
    return '{ nodes := '+rows(g['nodes'],node)+', assessments := '+rows(g['assessments'],assessment)+', assertions := '+rows(g['assertions'],assertion_lean)+', admissionRoots := '+rows(g['admission_roots'],root)+' }'


def core_modules():
    return [('RelationalInput',s.FORMAL/'core/RelationalInput.lean'),('RelationalSemantics',s.FORMAL/'core/RelationalSemantics.lean'),
        ('ReferenceChecker',s.FORMAL/'reference-checker/l0/ReferenceChecker.lean'),('CheckerSoundness',s.FORMAL/'proofs/l0/CheckerSoundness.lean'),
        ('L0Runtime',BASE/'L0Runtime.lean')]


def check(normal, build=None):
    if build is None:
        with tempfile.TemporaryDirectory(prefix='relational-input-') as folder:
            build=Path(folder);s.compile_lean(build,core_modules());return check(normal,build)
    graph=graph_lean(normal['graph'])
    target='applyAddition base addition' if 'addition' in normal else 'base'
    declarations='def base : Graph := '+graph+'\n'
    if 'addition' in normal:declarations+='def addition : Assertion := '+assertion_lean(normal['addition'])+'\n'
    lean=s.lean_path();env={**os.environ,'LEAN_PATH':str(build)}
    program='import L0Runtime\nopen Relational\n'+declarations+'def main : IO Unit := IO.println ((Runtime.result base ('+target+')).compress)\n'
    query=build/'InputQuery.lean';query.write_text(program)
    run=subprocess.run([str(lean),'--run',str(query)],cwd=build,env=env,text=True,capture_output=True,timeout=60)
    s.require(run.returncode==0,'input runtime failed: '+run.stdout+run.stderr)
    result=decode(run.stdout)
    # Specific evaluation is independently checked by reduction in the kernel.
    proof='import CheckerSoundness\nopen Relational\n'+declarations
    if result['accepted_result']:
        proof+='theorem evaluated_model : Inv ('+target+') := graph_check_sound _ (by decide)\n#print axioms evaluated_model\n'
        method='kernel-checked-instance-via-general-soundness'
    else:
        proof+='theorem evaluated_rejection : checkGraph ('+target+') = false := by decide\n#print axioms evaluated_rejection\n'
        method='kernel-checked-rejection'
    proof_file=build/'InputEvaluation.lean';proof_file.write_text(proof)
    run=subprocess.run([str(lean),'-o',str(proof_file.with_suffix('.olean')),str(proof_file)],cwd=build,env=env,text=True,capture_output=True,timeout=60)
    s.require(run.returncode==0 and 'warning:' not in run.stdout+run.stderr,'kernel evaluation failed: '+run.stdout+run.stderr)
    spec_path=s.FORMAL/'validate_f0.py'
    import importlib.util
    spec=importlib.util.spec_from_file_location('l0_input_axioms',spec_path);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    s.require(helper.policy_accepts(run.stdout+run.stderr),'unapproved evaluation axiom')
    result.update(proof_method=method,normal_form_sha256=hashlib.sha256(json.dumps(normal,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest(),
                  query_sha256=s.digest(query),evaluation_source_sha256=s.digest(proof_file),
                  evaluation_olean_sha256=s.digest(proof_file.with_suffix('.olean')),axiom_report=helper.axiom_report(run.stdout+run.stderr),
                  authority_effect='none',runtime_trust=['JSON projection','hash function','compiler and host execution','supplied assessment truth'])
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('request',type=Path);args=parser.parse_args()
    try:
        raw=args.request.read_bytes();normal=normalize(decode(raw));result=check(normal)
        result['raw_input_sha256']=hashlib.sha256(raw).hexdigest();print(json.dumps(result,indent=2));return 0 if result['accepted_result'] else 1
    except (ValueError,UnicodeError,jsonschema.ValidationError) as error:
        print(json.dumps({'status':'invalid','diagnostic':str(error),'authority_effect':'none'}));return 2
    except subprocess.TimeoutExpired:
        print(json.dumps({'status':'unknown','diagnostic':'kernel or runtime budget exhausted','authority_effect':'none'}));return 3


if __name__=='__main__':sys.exit(main())
