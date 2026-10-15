"""Project finite certificates and freshly replay the pure Lean checker."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'profile'))
import frontend as f
s=f.s;d=f.d
BASE=Path(__file__).resolve().parent
MODULES=['InferenceCore','DerivationSoundness']


def policy():
    spec=importlib.util.spec_from_file_location('inference_axiom_policy',s.FORMAL/'validate_f0.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def key_lean(key):
    return '{ id := '+d.literal(key['id'])+', version := '+d.literal(key['version'])+', hash := '+d.literal(key['hash'])+' }'


def value_lean(value):
    if value['kind']=='reference':return '(.reference '+d.literal(value['id'])+' '+d.literal(value['version'])+')'
    if value['kind']=='epoch':return '(.epoch '+str(value['value'])+')'
    return '(.'+value['kind']+' '+d.literal(value['value'])+')'


def atom_lean(atom):
    return '{ predicate := '+key_lean(atom['predicate'])+', values := '+d.rows(atom['values'],value_lean)+' }'


def pattern_lean(pattern):
    def term(t):return '(.slot '+str(t['slot'])+')' if 'slot' in t else '(.constant '+value_lean(t['constant'])+')'
    return '{ predicate := '+key_lean(pattern['predicate'])+', terms := '+d.rows(pattern['terms'],term)+' }'


def rule_lean(rule):
    return '{ key := '+key_lean(rule)+', variables := '+d.rows(rule['variables'],lambda v:'.'+v['sort'])+\
           ', head := '+pattern_lean(rule['head'])+', body := '+d.rows(rule['body'],pattern_lean)+' }'


def theory_lean(normal):
    roles={'ordinary':'ordinary','protected':'protectedConclusion','checked-root':'checkedRoot','root-carrier':'rootCarrier'}
    def pred(p):return '{ key := '+key_lean(p)+', sorts := '+d.rows(p['sorts'],lambda x:'.'+x)+', role := .'+roles[p['role']]+' }'
    return '{ domain := '+d.rows(normal['domain'],value_lean)+', predicates := '+d.rows(normal['predicates'],pred)+\
        ', rules := '+d.rows(normal['rules'],rule_lean)+', roots := '+d.rows(normal['roots'],lambda r:d.rows(r['values'],value_lean))+\
        ', epoch := '+str(normal['snapshot_epoch'])+' }'


def instance_lean(ground):
    return '{ rule := '+key_lean(ground['rule'])+', substitution := '+d.rows(ground['substitution'],value_lean)+\
        ', head := '+atom_lean(ground['head'])+', body := '+d.rows(ground['body'],atom_lean)+' }'


def step_lean(step):
    if step['kind']=='base':return '(.base '+atom_lean(step['conclusion'])+')'
    return '(.apply '+instance_lean(step['instance'])+' '+d.rows(step['indices'],str)+')'


def captured_atom(normal,raw):
    f.fields(raw,['predicate','version','terms'],'certificate ground atom')
    sig=next((p for p in normal['predicates'] if p['id']==raw['predicate'] and p['version']==raw['version']),None)
    s.require(sig is not None,'undeclared or wrong-version certificate predicate')
    s.require(isinstance(raw['terms'],list),'certificate atom terms must be a list')
    return {'predicate':{k:sig[k] for k in ['id','version','hash']},'values':[f.value(v) for v in raw['terms']]}


def normalize_certificate(normal,certificate):
    f.fields(certificate,['schema','normal_form_identity','query','steps'],'derivation certificate')
    s.require(certificate['schema']=='relational.derivation-certificate/v1','unknown certificate version')
    s.require(certificate['normal_form_identity']==normal['normal_form_identity'],'certificate belongs to another theory/fact/root snapshot')
    s.require(isinstance(certificate['steps'],list),'certificate steps must be a list')
    query=captured_atom(normal,certificate['query']);steps=[];positions={}
    for raw in certificate['steps']:
        s.require(isinstance(raw,dict) and raw.get('kind') in ['base','apply'],'unknown certificate step')
        f.fields(raw,['id','kind','conclusion'] if raw['kind']=='base' else ['id','kind','conclusion','rule','substitution','premises'],'certificate step')
        name=f.text(raw['id'],'step identity');s.require(name not in positions,'duplicate certificate step ID')
        conclusion=captured_atom(normal,raw['conclusion'])
        if raw['kind']=='base':step={'kind':'base','conclusion':conclusion}
        else:
            f.fields(raw['rule'],['id','version','hash'],'exact rule reference')
            for coordinate in ['id','version','hash']:f.text(raw['rule'][coordinate],'rule '+coordinate)
            rule=next((r for r in normal['rules'] if r['id']==raw['rule']['id'] and r['version']==raw['rule']['version']),None)
            s.require(rule is not None,'unknown captured rule identity/version')
            s.require(isinstance(raw['substitution'],dict) and set(raw['substitution'])=={v['name'] for v in rule['variables']},'substitution must bind every declared variable exactly once')
            substitution=[f.value(raw['substitution'][v['name']]) for v in rule['variables']]
            s.require(isinstance(raw['premises'],list) and all(isinstance(p,str) and p in positions for p in raw['premises']),'premises must cite earlier certificate steps; missing, forward or cyclic references rejected')
            indices=[positions[p] for p in raw['premises']]
            ground={'rule':deepcopy(raw['rule']),'substitution':substitution,'head':conclusion,
                    'body':[steps[i]['conclusion'] for i in indices]}
            step={'kind':'apply','conclusion':conclusion,'instance':ground,'indices':indices}
        positions[name]=len(steps);steps.append(step)
    return {'query':query,'steps':steps}


def instantiated(pattern,values):
    return {'predicate':pattern['predicate'],'values':[values[t['slot']] if 'slot' in t else t['constant'] for t in pattern['terms']]}


def projected_result(normal,certificate):
    """A companion prediction only; Lean checks the exact result independently."""
    def atom_valid(atom):
        sig=next((p for p in normal['predicates'] if {k:p[k] for k in ['id','version','hash']}==atom['predicate']),None)
        return sig is not None and [v['kind'] for v in atom['values']]==sig['sorts'] and all(v in normal['domain'] for v in atom['values'])
    if not atom_valid(certificate['query']):return False
    previous=[]
    for step in certificate['steps']:
        if step['kind']=='base':valid=step['conclusion'] in normal['facts']
        else:
            ground=step['instance'];rule=next((r for r in normal['rules'] if {k:r[k] for k in ['id','version','hash']}==ground['rule']),None)
            values=ground['substitution']
            valid=rule is not None and [v['kind'] for v in values]==[v['sort'] for v in rule['variables']] and all(v in normal['domain'] for v in values)
            if valid:valid=instantiated(rule['head'],values)==ground['head'] and [instantiated(p,values) for p in rule['body']]==ground['body']
            if valid:valid=all(0<=i<len(previous) for i in step['indices']) and [previous[i] for i in step['indices']]==ground['body']
        if not valid:return False
        previous.append(step['conclusion'])
    return certificate['query'] in previous


def fixture_source(normal):
    return 'import DerivationSoundness\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Inference.Captured\n'+\
        'def theory : Theory := '+theory_lean(normal)+'\n'+\
        'def facts : List Atom := '+d.rows(normal['facts'],atom_lean)+'\n'+\
        'theorem theory_valid : TheoryValid theory := by decide\n'+\
        'theorem initial_valid : InitialValid theory facts := by decide\n'+\
        '#print axioms theory_valid\n#print axioms initial_valid\nend Inference.Captured\n'


def compile_generated(build,name,source):
    path=build/(name+'.lean');path.write_text(source)
    run=subprocess.run([str(s.lean_path()),'-o',str(path.with_suffix('.olean')),str(path)],
        cwd=build,env={**os.environ,'LEAN_PATH':str(build)},capture_output=True,text=True,timeout=60)
    output=run.stdout+run.stderr;s.require(run.returncode==0 and 'warning:' not in output,'inference kernel replay failed: '+name+'\n'+output)
    audit=policy();s.require(audit.policy_accepts(output),'inference replay contains unapproved axiom')
    return {'module':name,'generated_source_sha256':s.digest(path),'olean_sha256':s.digest(path.with_suffix('.olean')),
            'output':output,'axioms':audit.axiom_report(output)}


def prepare(normal,build):
    audit=policy()
    for name in MODULES:
        source=(BASE/(name+'.lean')).read_text()
        s.require(audit.source_policy(source),'forbidden proof bypass in '+name)
        import re
        s.require(set(re.findall(r'^import ([A-Za-z0-9_.]+)$',source,re.M))<=set(MODULES)|{'Init'},'unapproved inference dependency')
    logs=s.compile_lean(build,[(name,BASE/(name+'.lean')) for name in MODULES])
    logs.append(compile_generated(build,'InferenceFixture',fixture_source(normal)))
    return logs


def query_source(certificate,expected):
    source='import InferenceFixture\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nopen Inference Inference.Captured\n'
    source+='def certificate : List Step := '+d.rows(certificate['steps'],step_lean)+'\n'
    source+='def query : Atom := '+atom_lean(certificate['query'])+'\n'
    source+='theorem checked_result : checkDerivation theory facts certificate query = '+('true' if expected else 'false')+' := by decide\n#print axioms checked_result\n'
    if expected:source+='theorem checked_derivation : Derivable theory facts query := derivation_certificate_sound theory facts certificate query checked_result\n#print axioms checked_derivation\n'
    return source


def check(request,certificate,build=None):
    normal=f.normalize(request);projected=normalize_certificate(normal,certificate);expected=projected_result(normal,projected)
    if build is None:
        with tempfile.TemporaryDirectory(prefix='inference-certificate-') as folder:
            build=Path(folder);prepare(normal,build)
            return check(request,certificate,build)
    s.require((build/'InferenceFixture.lean').read_text()==fixture_source(normal),'private build contains another theory/fact snapshot')
    result=compile_generated(build,'DerivationQuery',query_source(projected,expected))
    # Recheck independent evidence after execution; timestamps never repair drift.
    s.require(f.normalize(request)==normal,'inference dependencies changed during replay')
    return {'status':'checked-derivable' if expected else 'rejected-certificate','accepted':expected,
            'normal_form_identity':normal['normal_form_identity'],'certificate_identity':f.identity(certificate),
            'source_sha256':result['generated_source_sha256'],'olean_sha256':result['olean_sha256'],'axioms':result['axioms'],
            'closure_complete':False,'protected_policy_review':normal['protected_policy_status'],
            'authority_effect':'none','scope':'Exact finite captured theory/facts. Positive derivation soundness; no closure completeness or admission authority claimed.'}


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('request',type=Path);parser.add_argument('certificate',type=Path)
    args=parser.parse_args()
    try:result=check(d.decode(args.request.read_bytes()),d.decode(args.certificate.read_bytes()))
    except (ValueError,UnicodeError) as error:result={'status':'invalid-input','diagnostic':str(error),'accepted':False,'authority_effect':'none'}
    except (subprocess.TimeoutExpired,OSError) as error:result={'status':'execution-failed','diagnostic':str(error),'accepted':False,'authority_effect':'none'}
    print(json.dumps(result,ensure_ascii=False));return 0 if result['accepted'] else 1


if __name__=='__main__':raise SystemExit(main())
