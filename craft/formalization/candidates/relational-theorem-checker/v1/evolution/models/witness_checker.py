"""Check supplied nonempty models and explicit countermodels in a private build."""
from copy import deepcopy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'obligations'))
import generator as g
s=g.s;d=g.c.r.d
sys.path.insert(0,str(s.BASE/'registry'))
import build_registry as registry_projection
BASE=Path(__file__).resolve().parent


def kind_lean(row):
    return registry_projection.theory_lean({'node_kinds':[],'kinds':[row]}).split('kinds := [',1)[1][:-3]


def graph_lean(graph):
    def node(n):return '{ ref := '+d.refs(n['ref'])+', kind := '+d.literal(n['kind'])+', contentIdentity := '+d.literal(n['content_identity'])+' }'
    def edge(e):return '{ id := '+d.literal(e['id'])+', kindId := '+d.literal(e['kind'])+', kindVersion := '+d.literal(e['kind_version'])+', source := '+d.refs(e['source'])+', target := '+d.refs(e['target'])+', qualifiers := '+d.rows(list(e['qualifiers'].items()),lambda q:'('+d.literal(q[0])+', '+d.literal(q[1])+')')+' }'
    return '{ nodes := '+d.rows(graph['nodes'],node)+', assertions := '+d.rows(graph['assertions'],edge)+' }'


def fixture_source(proposal):
    classification=g.c.classify(proposal);g.source_projection(proposal)
    s.require(classification['profile']=='fresh-kind-extension','unsupported model profile')
    added=proposal['after']['registry']['kinds'][len(proposal['before']['registry']['kinds']):]
    text='import RegistrySnapshot\nimport ConservativeExpansion\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Models.Captured\n'
    text+='def added : List Kind := '+d.rows(added,kind_lean)+'\n'
    text+='def expanded : Theory := expandedTheory Snapshot.captured added\n'
    text+='theorem added_valid : ∀ d ∈ added, KindValid Snapshot.captured.nodeKinds d := by decide\n'
    text+='theorem expanded_valid : TheoryValid expanded := by\n  refine ⟨Snapshot.valid_snapshot.1, Snapshot.valid_snapshot.2.1, by decide, ?_⟩\n  intro d hd\n  change d ∈ Snapshot.captured.kinds ++ added at hd\n  rcases List.mem_append.mp hd with old | fresh\n  · exact Snapshot.valid_snapshot.2.2.2 d old\n  · exact added_valid d fresh\n'
    text+='def selected : Graph := '+graph_lean(proposal['before']['graph'])+'\n'
    text+='theorem selected_valid : Inv Snapshot.captured selected := by\n  exact ⟨Snapshot.valid_snapshot, by decide, by decide, by decide, by decide⟩\n'
    text+='theorem actual_every_base_model_expands : ∀ model, Inv Snapshot.captured model → ∃ expansion, Inv expanded expansion ∧ oldReduct Snapshot.captured expansion = model := expands_every_base_model Snapshot.captured added expanded_valid\n'
    text+='#print axioms expanded_valid\n#print axioms selected_valid\n#print axioms actual_every_base_model_expands\nend Registry.Models.Captured\n'
    return text


def prepare(proposal,build):
    for row in s.read(s.BASE/'registry/projection-audit.json')['modules']:s.check_binding(row['source'])
    fixture=build/'ConservativeFixture.lean';fixture.write_text(fixture_source(proposal))
    modules=[(row['module'],s.ROOT/row['source']['path']) for row in s.read(s.BASE/'registry/projection-audit.json')['modules']]
    logs=s.compile_lean(build,modules+[('ConservativeExpansion',BASE/'ConservativeExpansion.lean')])
    run=subprocess.run([str(s.lean_path()),'-o',str(fixture.with_suffix('.olean')),str(fixture)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},text=True,capture_output=True,timeout=60)
    output=run.stdout+run.stderr
    s.require(run.returncode==0 and 'warning:' not in output,'captured conservative theory failed: '+output)
    logs.append({'module':'ConservativeFixture','generated_source_sha256':s.digest(fixture),
                 'proposal_identity':g.c.identity(proposal),'olean_sha256':s.digest(fixture.with_suffix('.olean')),'output':output})
    return logs


def check_witness(proposal,request,build=None):
    s.require(isinstance(request,dict) and set(request)=={'proposal_identity','graph','claim'},'unknown or missing witness fields')
    s.require(request['proposal_identity']==g.c.identity(proposal),'witness from another proposal')
    s.require(proposal['after']['registry']['node_kinds'] and proposal['after']['registry']['kinds'],'empty theory cannot pass readiness')
    g.c.structural_registry(proposal['after']['registry']);g.source_projection(proposal)
    graph=request['graph'];s.require(graph['nodes'] and graph['assertions'],'empty witness cannot pass readiness')
    resolved=g.c.r.resolve(graph,proposal['after']['registry'])
    s.require(not resolved['errors'],'invalid typed witness: '+json.dumps(resolved['errors']))
    claim=request['claim'];s.require(isinstance(claim,dict) and claim.get('kind') in {'model-existence','non-entailment'},'unsupported model claim')
    if claim['kind']=='model-existence':s.require(set(claim)=={'kind'},'unknown model constraints require another profile')
    else:
        s.require(set(claim)=={'kind','premise_kind','conclusion_kind'},'unknown countermodel formula')
        known={row['id'] for row in proposal['after']['registry']['kinds']}
        s.require(claim['premise_kind'] in known and claim['conclusion_kind'] in known,'unknown predicate meaning')
    if build is None:
        with tempfile.TemporaryDirectory(prefix='model-witness-') as folder:
            return check_witness(proposal,request,Path(folder)) if prepare(proposal,Path(folder)) else None
    s.require((build/'ConservativeFixture.lean').read_text()==fixture_source(proposal),'private build has another theory')
    source='import ConservativeFixture\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nopen Registry Registry.Models Registry.Models.Captured\ndef submitted : Graph := '+graph_lean(graph)+'\n'
    source+='theorem checked_model : InhabitedUse expanded submitted := by\n  exact ⟨⟨expanded_valid, by decide, by decide, by decide, by decide⟩, by decide, by decide⟩\n#print axioms checked_model\n'
    if claim['kind']=='non-entailment':
        premise=d.literal(claim['premise_kind']);conclusion=d.literal(claim['conclusion_kind'])
        source+='theorem checked_countermodel : HasKind submitted '+premise+' ∧ ¬ HasKind submitted '+conclusion+' := by decide\n'
        source+='theorem checked_non_entailment : ¬ (∀ model, InhabitedUse expanded model → HasKind model '+premise+' → HasKind model '+conclusion+') := by\n  intro implication\n  exact checked_countermodel.2 (implication submitted checked_model checked_countermodel.1)\n#print axioms checked_countermodel\n#print axioms checked_non_entailment\n'
    path=build/'WitnessCheck.lean';path.write_text(source)
    run=subprocess.run([str(s.lean_path()),'-o',str(path.with_suffix('.olean')),str(path)],cwd=build,env={**os.environ,'LEAN_PATH':str(build)},text=True,capture_output=True,timeout=60)
    output=run.stdout+run.stderr
    s.require(run.returncode==0 and 'warning:' not in output,'witness kernel check failed: '+output)
    spec=importlib.util.spec_from_file_location('witness_axioms',s.FORMAL/'validate_f0.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    s.require(policy.policy_accepts(output),'model proof contains an unapproved axiom')
    return {'status':'checked-model' if claim['kind']=='model-existence' else 'checked-non-entailment',
            'evidence_kind':'finite-model-witness','request_identity':g.c.identity(request),'proposal_identity':g.c.identity(proposal),
            'scope':'Inhabited Registry structural graph; HasKind means assertion presence, with every Inv requirement checked.',
            'axioms':policy.axiom_report(output),'source_sha256':s.digest(path),'olean_sha256':s.digest(path.with_suffix('.olean')),
            'authority_effect':'none','full_source_semantics_proved':False}


def unsuccessful_search():
    return {'status':'unknown','evidence_kind':'bounded-search-without-witness',
            'non_entailment_proved':False,'model_existence_proved':False}
