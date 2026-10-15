#!/usr/bin/env python3
"""Exercise exact diffs against the current baseline and candidate changes."""
from copy import deepcopy
import json
from pathlib import Path
import classifier as c
s=c.s
BASE=Path(__file__).resolve().parent


def proposal(before,after,name):
    return {'schema':'relational.extension-proposal/v1','proposal_id':name,
            'baseline_identity':c.identity(before),'before':deepcopy(before),'after':deepcopy(after)}


def main():
    schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://cyberalchemy.local/schemas/relational-extension-proposal/v1',
            'type':'object','additionalProperties':False,'required':['schema','proposal_id','baseline_identity','before','after'],
            'properties':{'schema':{'const':'relational.extension-proposal/v1'},'proposal_id':{'type':'string','minLength':1},
                          'baseline_identity':{'type':'string','pattern':'^[0-9a-f]{64}$'},'before':{'$ref':'#/$defs/snapshot'},'after':{'$ref':'#/$defs/snapshot'}},
            '$defs':{'snapshot':{'type':'object','additionalProperties':False,'required':['registry','rules','graph'],
                                'properties':{'registry':{'type':'object'},'rules':{'type':'array','items':{'type':'object'}},'graph':{'type':'object'}}}}}
    s.write(BASE/'proposal-schema.json',schema)
    before=c.baseline();after=deepcopy(before)
    declaration={'id':'relation.trace-label-for','pairs':[{'source_kind':'capability-instance','target_kind':'contract'}],
        'fields':['trace_label'],'axis_id':'axis.static-trace-annotation',
        'unique_question':'Which exact contract does this capability instance carry a named trace annotation for?',
        'operational_effect':'Records a static nonempty annotation only; derives no executable effect, conformance or admission root.',
        'forbidden_inferences':['conformance','admission','authority'],
        'source_posture':{'lifecycle_state':'candidate','authority_effect':'none','claim_ceiling':'Named structural annotation profile only.'},
        'effective_state':'candidate-only'}
    source=BASE/'trace-label-declaration.json'
    s.write(source,{'schema':'relational.structural-declaration/v1-candidate','declaration':declaration,
                   'semantic_profile':'closed-required-string-ordered-pairs/v1',
                   'qualifier_interpretation':{'trace_label':'nonempty-string-annotation'},
                   'formal_predicate':'Registry.InstanceValid; no inference rule or external evidence meaning'})
    added={**declaration,'source':s.binding(source),'version':'sha256:'+s.digest(source)}
    after['registry']['kinds'].append(added);after['registry']['kind_count']+=1;after['registry']['ordered_pair_count']+=1
    fresh=proposal(before,after,'fixture:fresh-trace-label');s.write(BASE/'fresh-kind-proposal.json',fresh)
    classified=c.classify(fresh);s.require(classified['profile']=='fresh-kind-extension','fresh extension misclassified')
    controls=[{'name':'fresh kind','result':'pass','classification':classified}]
    changes=[('pair widening',lambda p:p['after']['registry']['kinds'][0]['pairs'].append({'source_kind':'agent-instance','target_kind':'contract'}),'unsupported-structural-or-semantic-change'),
             ('qualifier weakening',lambda p:p['after']['registry']['kinds'][0]['fields'].pop(),'unsupported-structural-or-semantic-change'),
             ('normative effect change',lambda p:p['after']['registry']['kinds'][0].update(operational_effect='Now grants unrestricted authority'),'unsupported-structural-or-semantic-change'),
             ('forbidden inference removed',lambda p:p['after']['registry']['kinds'][0]['forbidden_inferences'].pop(),'unsupported-structural-or-semantic-change'),
             ('unclassified field',lambda p:p['after']['registry']['kinds'][0].update(hidden_runtime_override=True),'unsupported-unclassified'),
             ('unknown registry field',lambda p:p['after']['registry'].update(new_semantics='unknown'),'unsupported-unclassified'),
             ('rule addition',lambda p:p['after']['rules'].append({'id':'rule:review-signal','version':'v1','head':{'predicate':'ReviewSignal','terms':[{'variable':'subject'}]},'body':[{'predicate':'Conforms','terms':[{'variable':'subject'}]}]}),'rule-only-extension'),
             ('data mutation',lambda p:p['after']['graph']['nodes'][0].update(content_identity='changed:fixture'),'instance-only')]
    for name,mutate,expected in changes:
        value=proposal(before,before,'fixture:'+name);mutate(value)
        value['after']['registry']['ordered_pair_count']=sum(len(k['pairs']) for k in value['after']['registry']['kinds'])
        result=c.classify(value);s.require(result['profile']==expected,'wrong computed change class: '+name)
        s.require(all(result[d]=='unchecked' for d in ['selected_data_compatibility','invariant_preservation','model_conservativity']),'diff inferred a proof verdict')
        if name=='rule addition':s.write(BASE/'rule-change-proposal.json',value)
        if name=='pair widening':s.write(BASE/'pair-widening-proposal.json',value)
        controls.append({'name':name,'result':'pass','classification':result})
    # Exact source/version changes are distinct even when shape remains equal.
    other=BASE/'rebound-source.json';original=s.read(s.ROOT/before['registry']['kinds'][0]['source']['path']);original['evidence_refs'].append('fixture:source-version-change');s.write(other,original)
    rebound=proposal(before,before,'fixture:source-rebind');row=rebound['after']['registry']['kinds'][0]
    row.update(source=s.binding(other),version='sha256:'+s.digest(other))
    result=c.classify(rebound);s.require({x['classification'] for x in result['changed_kind_fields']} >= {'exact-version-change','exact-source-identity-change'},'source identity change hidden')
    controls.append({'name':'exact source and version rebind','result':'pass','classification':result})
    wrong=deepcopy(fresh);wrong['baseline_identity']='0'*64
    try:c.classify(wrong)
    except ValueError:controls.append({'name':'wrong baseline identity','result':'rejected'})
    else:raise ValueError('wrong baseline accepted')
    s.write(BASE/'diff-controls.json',{'result':'pass','controls':controls,'control_count':len(controls),
        'fresh_kind_classification':classified,'authority_effect':'none',
        'claim_ceiling':'Computed changes and exact source identities only; compatibility and theorem obligations remain unchecked.'})
    s.accept('E01',{'proposal-schema.json':BASE/'proposal-schema.json','change-classifier':BASE/'classifier.py','diff-controls.json':BASE/'diff-controls.json',
                   **{name:BASE/name for name in ['trace-label-declaration.json','fresh-kind-proposal.json','rule-change-proposal.json','pair-widening-proposal.json','rebound-source.json']}},
        ['Recursive field diffs retain all changed values; relation pairs, qualifier fields, semantic prose, forbidden inferences, source posture, exact hashes/versions, rules and instance data are classified against the bound current baseline.',
         'All three compatibility dimensions start unchecked; source equality or an unchanged fixture creates no preservation or conservativity verdict.'],
        ['A widened ordered pair is classified as an old-kind semantic change and cannot enter the fresh-symbol profile.',
         'Unknown declaration or registry fields produce unsupported classification; an incorrect baseline identity rejects.'],
        [Path(__file__),s.BASE/'registry/normalized-registry.json',s.BASE/'references/resolver.py',s.BASE/'demonstrations/l0/input.json'])
    print(json.dumps({'task':'E01','result':'accepted','controls':len(controls)}))


if __name__=='__main__':main()
