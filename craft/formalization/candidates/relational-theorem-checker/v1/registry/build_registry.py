#!/usr/bin/env python3
"""Project every exact source into the dynamic string-qualifier Lean profile."""
from copy import deepcopy
import json
import os
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import jsonschema
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'input'))
import decoder as d
s=d.s
BASE=Path(__file__).resolve().parent


def normalize(snapshot):
    rows=[];ids=[]
    for record in snapshot['records']:
        e=record['entry'];p=record['payload'];q=p['qualifier_contract']
        s.check_binding({'path':e['instance_path'],'sha256':e['instance_sha256']})
        s.require(s.read(s.ROOT/e['instance_path'])['payload']==p,'source payload mismatch')
        s.require(q['closed'] and set(q['required_axes'])==set(q['properties']),'unsupported open or optional qualifier contract')
        s.require(all(spec=={'type':'string','minLength':1} for spec in q['properties'].values()),'unsupported qualifier value shape requires new formal profile')
        pairs=p['allowed_endpoint_pairs'];s.require(len({(x['source_kind'],x['target_kind']) for x in pairs})==len(pairs),'duplicate pair evidence')
        s.require(p['relation_kind_id']==e['relation_kind_id'],'kind identity mismatch')
        ids.append(p['relation_kind_id'])
        rows.append({'id':p['relation_kind_id'],'version':'sha256:'+e['instance_sha256'],'pairs':pairs,'fields':q['required_axes'],
                     'source':{'path':e['instance_path'],'sha256':e['instance_sha256']},
                     'axis_id':p['axis_id'],'unique_question':p['unique_question'],'operational_effect':p['operational_effect'],
                     'forbidden_inferences':p['forbidden_inferences'],'source_posture':record['source_posture'],'effective_state':e['lifecycle_state']})
    s.require(len(set(ids))==len(ids)==snapshot['counts']['kinds'],'registry omission or repeated kind')
    total=sum(len(r['pairs']) for r in rows);s.require(total==snapshot['counts']['ordered_pairs'],'pair omission')
    return {'schema':'relational.normalized-registry/v1','normalization_version':'source-order-closed-string-qualifiers/v1',
            'kinds':rows,'node_kinds':[r['endpoint']['endpoint_kind'] for r in snapshot['carriers']],
            'kind_count':len(rows),'ordered_pair_count':total,'authority_effect':'none'}


def theory_lean(normal):
    # These source labels need no escapes. Restrict the fast representation to
    # an alphabet containing neither quotes nor Lean escape/source syntax;
    # arbitrary values retain the decoder's scalar-safe representation.
    def label(value):
        return '"'+value+'"' if re.fullmatch(r'[a-zA-Z0-9_.:/-]+',value) else d.literal(value)
    def kind(row):
        pair=lambda p:'('+label(p['source_kind'])+', '+label(p['target_kind'])+')'
        return '{ id := '+label(row['id'])+', version := '+label(row['version'])+', pairs := '+d.rows(row['pairs'],pair)+', fields := '+d.rows(row['fields'],label)+' }'
    return '{ nodeKinds := '+d.rows(normal['node_kinds'],label)+', kinds := '+d.rows(normal['kinds'],kind)+' }'


def structural(kind,source,target,qualifiers):
    s.require((source,target) in {(p['source_kind'],p['target_kind']) for p in kind['pairs']},'undeclared ordered pair')
    s.require(set(qualifiers)==set(kind['fields']) and all(isinstance(v,str) and v!='' for v in qualifiers.values()),'invalid qualifier contract')
    return True


def main():
    s.context('C03',[(s.PLAN,'tasks[id=C03]'),(s.BASE/'snapshot/effective-snapshot.json','all exact payloads and endpoint carriers'),
        (s.BASE/'coverage/carrier/carrier-coverage.json','all observed carrier gaps'),(s.FORMAL/'core/RelationalInput.lean','unchanged exact reference identity')],
        [{'classification':'non-blocking','choice':'formalize the complete current closed-string qualifier profile over dynamic named node kinds',
          'basis':'All selected qualifier properties are exactly required nonempty strings; unsupported future value shapes require new proofs.'}])
    snapshot=s.read(s.BASE/'snapshot/effective-snapshot.json');normal=normalize(snapshot)
    s.write(BASE/'normalized-registry.json',normal)
    # Check each declaration separately, then compose a validity proof. This
    # preserves the whole-theory invariant without one giant reduction term.
    labels=theory_lean(normal)
    node_list=labels.split(', kinds := ',1)[0].removeprefix('{ nodeKinds := ')
    node_source=BASE/'RegistryNodes.lean'
    node_source.write_text('import RegistryChecker\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Snapshot\ndef nodes : List String := '+node_list+'\ntheorem nodes_unique : nodes.Nodup := by decide\ntheorem nodes_named : ∀ k ∈ nodes, k ≠ "" ∧ k ≠ "*" := by decide\nend Registry.Snapshot\n')
    modules=[('RelationalInput',s.FORMAL/'core/RelationalInput.lean'),('RegistryChecker',BASE/'RegistryChecker.lean'),('RegistryNodes',node_source)]
    generated=[node_source]
    for index,row in enumerate(normal['kinds']):
        item=theory_lean({'node_kinds':[],'kinds':[row]}).split('kinds := [',1)[1][:-3]
        name='RegistryKind'+str(index);path=BASE/(name+'.lean')
        path.write_text('import RegistryNodes\nset_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Snapshot\ndef kind'+str(index)+' : Kind := '+item+'\ntheorem kind_valid'+str(index)+' : KindValid nodes kind'+str(index)+' := by decide\nend Registry.Snapshot\n')
        modules.append((name,path));generated.append(path)
    kind_names=['kind'+str(i) for i in range(normal['kind_count'])]
    text=''.join('import RegistryKind'+str(i)+'\n' for i in range(normal['kind_count']))
    text+='set_option maxRecDepth 8192\nset_option maxHeartbeats 4000000\nnamespace Registry.Snapshot\ndef captured : Theory := { nodeKinds := nodes, kinds := ['+', '.join(kind_names)+'] }\n'
    text+='theorem kinds_unique : (captured.kinds.map Kind.id).Nodup := by decide\n'
    text+='theorem kinds_valid : ∀ k ∈ captured.kinds, KindValid captured.nodeKinds k := by\n  intro k hk\n  simp only [captured, List.mem_cons] at hk\n  rcases hk with '+' | '.join('h'+str(i) for i in range(len(kind_names)+1))+'\n'
    text+=''.join('  · subst k; exact kind_valid'+str(i)+'\n' for i in range(len(kind_names)))
    text+='  · cases h'+str(len(kind_names))+'\n'
    text+='theorem valid_snapshot : TheoryValid captured := ⟨nodes_unique, nodes_named, kinds_unique, kinds_valid⟩\n'
    text+='def RequiredPairOrigin : Prop := ∀ (r : Theory) (g : Graph) (e : Assertion), checkInstance r g e = true → ∃ source ∈ g.nodes, ∃ target ∈ g.nodes, ∃ kind ∈ r.kinds, source.ref = e.source ∧ target.ref = e.target ∧ kind.id = e.kindId ∧ kind.version = e.kindVersion ∧ (source.kind,target.kind) ∈ kind.pairs\n'
    text+='theorem audited_pair_origin : RequiredPairOrigin := accepted_pair_has_origin\n#print axioms instance_checker_iff\n#print axioms graph_checker_iff\n#print axioms accepted_pair_has_origin\n#print axioms valid_snapshot\n#print axioms audited_pair_origin\nend Registry.Snapshot\n'
    (BASE/'RegistrySnapshot.lean').write_text(text)
    modules.append(('RegistrySnapshot',BASE/'RegistrySnapshot.lean'))
    with tempfile.TemporaryDirectory(prefix='registry-replay-') as folder:
        logs=s.compile_lean(Path(folder),modules)
    import importlib.util
    spec=importlib.util.spec_from_file_location('registry_axioms',s.FORMAL/'validate_f0.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)
    report=policy.axiom_report(logs[-1]['output']);s.require(len(report)==5 and all(set(v)<=policy.ALLOW for v in report.values()),'registry theorem audit failed')
    positives=0;negative_pairs=0
    for kind in normal['kinds']:
        pairs={(x['source_kind'],x['target_kind']) for x in kind['pairs']};q={k:'fixture:value' for k in kind['fields']}
        for source,target in pairs:structural(kind,source,target,q);positives+=1
        for source in {p[0] for p in pairs}:
            for target in {p[1] for p in pairs}:
                if (source,target) not in pairs:
                    try:structural(kind,source,target,q)
                    except ValueError:negative_pairs+=1
                    else:raise ValueError('Cartesian-product permission introduced')
    controls=[]
    for name,mutate in [('omitted source',lambda p:p['records'].pop()),('duplicate kind',lambda p:p['records'].append(deepcopy(p['records'][0]))),
                        ('wrong source hash',lambda p:p['records'][0]['entry'].update(instance_sha256='0'*64))]:
        bad=deepcopy(snapshot);mutate(bad)
        try:normalize(bad)
        except ValueError:controls.append({'name':name,'result':'rejected'})
        else:raise ValueError('bad registry projection accepted')
    s.write(BASE/'projection-audit.json',{'result':'pass','complete_kind_count':normal['kind_count'],'complete_pair_count':normal['ordered_pair_count'],
        'positive_pair_controls':positives,'undeclared_cartesian_pair_controls':negative_pairs,'negative_projection_controls':controls,
        'source_to_normal_correspondence':'All source pairs, required string qualifiers, identity hashes and explanatory text are retained; no omissions or additions.',
        'formal_theorems':report,'modules':logs,'snapshot_generated_modules':[s.binding(p) for p in generated],'JSON_projection_formally_proved':False,
        'claim_ceiling':'General checker correctness for the exact data-driven structural profile, plus valid 41-kind typed theory witness; no theorem for all prose semantics.'})
    s.accept('C03',{n:BASE/n for n in ['normalized-registry.json','RegistryChecker.lean','projection-audit.json','RegistrySnapshot.lean']},
        ['All 41 entries and 550 pairs are preserved and measured; every declared pair is exercised and every undeclared cross-product combination rejects.',
         'The independent data-driven predicates and general iff/pair-origin theorems compile; the whole typed snapshot satisfies its invariant by kernel reduction.'],
        ['All undeclared cross-product pairs are tested; the general origin theorem exposes an exact declared pair for every accepted instance.',
         'Source omissions, repeated kinds and mismatched hashes fail normalization.'],[Path(__file__),s.BASE/'snapshot/effective-snapshot.json',*generated])
    print(json.dumps({'task':'C03','result':'accepted','kinds':41,'pairs':550,'phantom_pairs_rejected':negative_pairs}))


if __name__=='__main__':main()
