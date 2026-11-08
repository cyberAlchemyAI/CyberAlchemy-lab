"""Freshly check supplied models against exact typed Horn and root semantics."""
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'closure'))
import closure_checker as c
f=c.f;s=c.s;d=c.d
BASE=Path(__file__).resolve().parent


def normalize_witness(normal,witness):
    f.fields(witness,['schema','normal_form_identity','model','claim'],'semantic model witness')
    s.require(witness['schema']=='relational.inference-model/v1','unknown model witness version')
    s.require(witness['normal_form_identity']==normal['normal_form_identity'],'model from another captured theory/fact/root context')
    s.require(isinstance(witness['model'],list),'model must supply actual atom inventory')
    model=[c.c.captured_atom(normal,a) for a in witness['model']]
    claim=witness['claim'];s.require(isinstance(claim,dict) and claim.get('kind') in ['model-existence','non-entailment'],'unsupported model claim')
    f.fields(claim,['kind'] if claim['kind']=='model-existence' else ['kind','premise','conclusion'],'model claim')
    result={'model':model,'kind':claim['kind']}
    if claim['kind']=='non-entailment':
        result.update(premise=c.c.captured_atom(normal,claim['premise']),conclusion=c.c.captured_atom(normal,claim['conclusion']))
    return result


def projected_result(normal,witness):
    model=witness['model'];predicates={f.identity({k:p[k] for k in ['id','version','hash']}):p for p in normal['predicates']}
    def valid(atom):
        p=predicates.get(f.identity(atom['predicate']))
        return p is not None and [v['kind'] for v in atom['values']]==p['sorts'] and all(v in normal['domain'] for v in atom['values'])
    if len({f.identity(a) for a in model})!=len(model) or not all(valid(a) for a in model):return False
    if any(predicates[f.identity(a['predicate'])]['role']!='ordinary' and a['values'] not in [r['values'] for r in normal['roots']] for a in model):return False
    if not all(a in model for a in normal['facts']):return False
    instances,reason=c.enumerate_instances(normal,limit=None);s.require(reason is None,'model grounding incomplete')
    if any(all(a in model for a in i['body']) and i['head'] not in model for i in instances):return False
    return witness['kind']=='model-existence' or (valid(witness['premise']) and valid(witness['conclusion']) and witness['premise'] in model and witness['conclusion'] not in model)


def prepare(normal,build):
    logs=c.prepare(normal,build);audit=c.c.policy();source=(BASE/'ModelSemantics.lean').read_text()
    s.require(audit.source_policy(source),'forbidden model proof bypass')
    import re
    s.require(set(re.findall(r'^import ([A-Za-z0-9_.]+)$',source,re.M))=={'ClosureAdequacy'},'unknown model proof import')
    return logs+s.compile_lean(build,[('ModelSemantics',BASE/'ModelSemantics.lean')])


def query_source(witness,accepted):
    source='import InferenceFixture\nimport ModelSemantics\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nopen Inference Inference.Captured\n'
    source+='def witnessModel : List Atom := '+d.rows(witness['model'],c.c.atom_lean)+'\n'
    if witness['kind']=='model-existence':expression='checkModel theory facts witnessModel'
    else:
        source+='def premise : Atom := '+c.c.atom_lean(witness['premise'])+'\ndef conclusion : Atom := '+c.c.atom_lean(witness['conclusion'])+'\n'
        expression='checkCountermodel theory facts witnessModel premise conclusion'
    source+='theorem checked_result : '+expression+' = '+('true' if accepted else 'false')+' := by decide\n#print axioms checked_result\n'
    if accepted:
        if witness['kind']=='model-existence':
            source+='theorem checked_model : Closed theory facts witnessModel := checked_model_is_closed checked_result\n#print axioms checked_model\n'
        else:
            source+='theorem checked_non_entailment : ¬ (∀ model : List Atom, Closed theory facts model → premise ∈ model → conclusion ∈ model) := checked_countermodel_non_entailment checked_result\n#print axioms checked_non_entailment\n'
    return source


def check(request,witness,build=None):
    normal=f.normalize(request);projected=normalize_witness(normal,witness);accepted=projected_result(normal,projected)
    if build is None:
        with tempfile.TemporaryDirectory(prefix='inference-model-') as folder:
            build=Path(folder);prepare(normal,build);return check(request,witness,build)
    s.require((build/'InferenceFixture.lean').read_text()==c.c.fixture_source(normal),'model build contains another context')
    result=c.c.compile_generated(build,'ModelQuery',query_source(projected,accepted))
    s.require(f.normalize(request)==normal,'model dependency drift during replay')
    return {'status':('checked-model' if projected['kind']=='model-existence' else 'checked-semantic-non-entailment') if accepted else 'rejected-model',
        'accepted':accepted,'non_entailment_proved':accepted and projected['kind']=='non-entailment',
        'normal_form_identity':normal['normal_form_identity'],'witness_identity':f.identity(witness),
        'source_sha256':result['generated_source_sha256'],'olean_sha256':result['olean_sha256'],'axioms':result['axioms'],
        'authority_effect':'none','scope':'Exact ground implication over all closed models of the captured finite Horn theory/facts; no universal noninterference claim.',
        'truth_boundary':'Typed supplied model and independent root truth assumptions; parser, hashing and projection are explicit.'}


def unsuccessful_search():
    return {'status':'unknown','method':'bounded-search-without-witness','non_entailment_proved':False,
            'non_derivability_proved':False,'authority_effect':'none'}


def main():
    import argparse,json,subprocess
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('request',type=Path);parser.add_argument('witness',type=Path);args=parser.parse_args()
    try:result=check(d.decode(args.request.read_bytes()),d.decode(args.witness.read_bytes()))
    except (ValueError,UnicodeError) as error:result={'status':'invalid-input','diagnostic':str(error),'accepted':False,'authority_effect':'none'}
    except (subprocess.TimeoutExpired,OSError) as error:result={'status':'execution-failed','diagnostic':str(error),'accepted':False,'authority_effect':'none'}
    print(json.dumps(result,ensure_ascii=False));return 0 if result['accepted'] else 1


if __name__=='__main__':raise SystemExit(main())
