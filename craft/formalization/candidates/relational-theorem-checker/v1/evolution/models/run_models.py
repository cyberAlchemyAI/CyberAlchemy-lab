#!/usr/bin/env python3
"""Check inhabited models, a semantic countermodel, and constructive expansion."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import witness_checker as w
s=w.s
BASE=Path(__file__).resolve().parent


def main():
    proposal=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json')
    (BASE/'ConservativeFixture.lean').write_text(w.fixture_source(proposal))
    graph=deepcopy(proposal['before']['graph']);kind=proposal['after']['registry']['kinds'][-1]
    trace={'id':'fixture:trace-edge','kind':kind['id'],'kind_version':kind['version'],
           'source':deepcopy(graph['nodes'][0]['ref']),'target':deepcopy(graph['nodes'][1]['ref']),
           'qualifiers':{'trace_label':'fixture:bounded-static-annotation'}}
    mixed=deepcopy(graph);mixed['assertions'].append(trace)
    isolated=deepcopy(graph);isolated['assertions']=[trace]
    requests=[{'proposal_identity':w.g.c.identity(proposal),'graph':current,'claim':{'kind':'model-existence'}} for current in [graph,mixed]]
    requests.append({'proposal_identity':w.g.c.identity(proposal),'graph':isolated,
                     'claim':{'kind':'non-entailment','premise_kind':kind['id'],'conclusion_kind':'relation.conforms-to'}})
    s.write(BASE/'witnesses.json',{'profile':'captured-structural-annotation-extension/v1','requests':requests})
    controls=[];results=[]
    with tempfile.TemporaryDirectory(prefix='model-profile-replay-') as folder:
        build=Path(folder);modules=w.prepare(proposal,build)
        for index,request in enumerate(requests):
            result=w.check_witness(proposal,request,build);results.append(result)
            (BASE/('Witness'+str(index)+'.lean')).write_bytes((build/'WitnessCheck.lean').read_bytes())
        cases=[('empty witness',lambda q:q['graph'].update(nodes=[],assertions=[],assessments=[],admission_roots=[])),
               ('premise absent',lambda q:q['graph'].update(assertions=[deepcopy(graph['assertions'][1])])),
               ('conclusion present',lambda q:q['graph'].update(assertions=deepcopy(mixed['assertions']))),
               ('wrong witness proposal',lambda q:q.update(proposal_identity='0'*64)),
               ('unsupported extra model axiom',lambda q:q['claim'].update(axioms=['False']))]
        for name,mutate in cases:
            request=deepcopy(requests[-1]);mutate(request)
            try:w.check_witness(proposal,request,build)
            except ValueError as error:
                text=str(error)
                s.require(not any(x in text for x in ['unknown module','Unknown identifier','unexpected token']),'control failed before checking its intended requirement')
                controls.append({'name':name,'result':'rejected','reason':text[:500]})
            else:raise ValueError('invalid model/countermodel accepted: '+name)
        inconsistent=deepcopy(proposal)
        inconsistent['after']['registry']['kinds'][-1]['id']=inconsistent['after']['registry']['kinds'][0]['id']
        inconsistent_request=deepcopy(requests[0]);inconsistent_request['proposal_identity']=w.g.c.identity(inconsistent)
        try:w.check_witness(inconsistent,inconsistent_request,build)
        except ValueError:controls.append({'name':'inconsistent duplicate-kind theory','result':'rejected'})
        else:raise ValueError('inconsistent theory accepted')
        empty=deepcopy(proposal)
        empty['after']['registry'].update(kinds=[],node_kinds=[],kind_count=0,ordered_pair_count=0)
        empty_request=deepcopy(requests[0]);empty_request['proposal_identity']=w.g.c.identity(empty)
        try:w.check_witness(empty,empty_request,build)
        except ValueError:controls.append({'name':'empty proposed theory','result':'rejected'})
        else:raise ValueError('empty theory accepted')
    unknown=w.unsuccessful_search()
    s.require(unknown['status']=='unknown' and not unknown['non_entailment_proved'],'failed search becomes theorem')
    controls.append({'name':'bounded search without witness','result':'unknown','outcome':unknown})
    spec=importlib.util.spec_from_file_location('conservativity_axioms',s.FORMAL/'validate_f0.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    report={**policy.axiom_report(modules[-2]['output']),**policy.axiom_report(modules[-1]['output'])}
    s.require(len(report)==8 and all(set(v)<=policy.ALLOW for v in report.values()),'conservativity theorem audit failed')
    s.write(BASE/'model-audit.json',{'result':'pass','proposal_identity':w.g.c.identity(proposal),'formal_theorems':report,
        'conservativity_theorem':'Registry.Models.audited_conservativity : RequiredConservativity',
        'captured_conservativity_theorem':'Registry.Models.Captured.actual_every_base_model_expands',
        'construction':'For every valid base graph choose the same graph, assigning no assertions to fresh kinds; the old reduct is identical.',
        'witnesses':results,'controls':controls,'modules':modules,'authority_effect':'none',
        'claim_ceiling':'Constructive conservativity for the exact append-only declaration theory; inhabited finite witnesses and scoped HasKind non-entailment. No arbitrary new constraints, mandatory occurrences or full prose semantics.'})
    outputs={'model-witness-checker':BASE/'witness_checker.py','witnesses':BASE/'witnesses.json',
             **{name:BASE/name for name in ['ConservativeExpansion.lean','ConservativeFixture.lean','model-audit.json','Witness0.lean','Witness1.lean','Witness2.lean']}}
    s.accept('E04',outputs,
        ['Checked nonempty old and extended graphs satisfy every typed Registry invariant; a separate countermodel has the new annotation premise and no conformance assertion, with exact model and non-entailment proofs.',
         'The audited RequiredConservativity theorem quantifies over every base model and constructs an expansion with unchanged old reduct; the captured proposed theory independently satisfies its assumptions.'],
        ['Empty witnesses/theories, duplicate-kind inconsistency, unsupported extra axioms, missing premises and true conclusions cannot pass witness verification.',
         'A non-entailment result requires an inhabited checked model and explicit premise/negated conclusion; unsuccessful bounded search remains unknown.'],
        [Path(__file__),s.BASE/'evolution/proposals/fresh-kind-proposal.json',s.BASE/'evolution/obligations/generator.py',s.BASE/'registry/build_registry.py',s.BASE/'registry/RegistryChecker.lean'])
    print(json.dumps({'task':'E04','result':'accepted','audited_theorems':len(report),'witnesses':len(results),'controls':len(controls)}))


if __name__=='__main__':main()
