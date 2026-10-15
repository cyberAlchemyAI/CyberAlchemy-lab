#!/usr/bin/env python3
"""Verify complete generated obligations and immutable carrier projection."""
from copy import deepcopy
import json
from pathlib import Path
import jsonschema
import generator as g
s=g.s
BASE=Path(__file__).resolve().parent


def evidence_skeleton(required):
    return {'proposal_identity':required['proposal_identity'],'policy_identity':required['policy_identity'],
            'obligations':deepcopy(required['obligations'])}


def main():
    fresh=s.read(s.BASE/'evolution/proposals/fresh-kind-proposal.json')
    rules=s.read(s.BASE/'evolution/proposals/rule-change-proposal.json')
    required=g.generate(fresh);rule_required=g.generate(rules)
    s.require({o['name'] for o in required['obligations']}==set(g.NON_RULE),'non-rule obligation omission')
    s.require({o['name'] for o in rule_required['obligations']}==set(g.NON_RULE+g.RULE),'rule obligation omission')
    g.validate_submission(fresh,evidence_skeleton(required));g.source_projection(fresh)
    controls=[]
    for name,mutate in [('omitted hard obligation',lambda x:x['obligations'].pop()),
                        ('duplicated hard obligation',lambda x:x['obligations'].append(deepcopy(x['obligations'][0]))),
                        ('weakened policy',lambda x:x.update(policy_identity='0'*64)),
                        ('weakened hard flag',lambda x:x['obligations'][0].update(hard=False)),
                        ('wrong proposal identity',lambda x:x.update(proposal_identity='0'*64))]:
        submission=evidence_skeleton(required);mutate(submission)
        try:g.validate_submission(fresh,submission)
        except ValueError:controls.append({'name':name,'result':'rejected'})
        else:raise ValueError('obligation policy bypassed')
    missing_rule=evidence_skeleton(rule_required);missing_rule['obligations']=[o for o in missing_rule['obligations'] if o['scope']!='L3']
    try:g.validate_submission(rules,missing_rule)
    except ValueError:controls.append({'name':'misclassified rule change drops L3 obligations','result':'rejected'})
    else:raise ValueError('rule obligation bypassed')
    unknown=deepcopy(fresh);unknown['after']['registry']['kinds'][-1]['unknown_logic']=True
    unsupported=g.generate(unknown)
    s.require(not unsupported['supported'] and any(o['name']=='unsupported-change-meaning' for o in unsupported['obligations']),'unknown extension readied')
    controls.append({'name':'unknown extension profile','result':'unsupported'})
    mismatched=deepcopy(fresh);mismatched['after']['registry']['kinds'][-1]['fields']=['unproved_reference_ref']
    try:g.source_projection(mismatched)
    except ValueError:controls.append({'name':'new normative source projection mismatch','result':'rejected'})
    else:raise ValueError('new source semantics silently reinterpreted')
    projected=g.carrier(fresh);jsonschema.Draft202012Validator.check_schema(projected)
    import sys
    sys.path.insert(0,str(s.BASE/'coverage/carrier'));from check_coverage import table
    rows=table(projected)
    s.require(len(rows)==42 and sum(len(v['pairs']) for v in rows.values())==551,'extension carrier omits declarations')
    for row in fresh['after']['registry']['kinds']:
        s.require(rows[row['id']]['pairs']==row['pairs'],'carrier ordered-pair widening')
    instance=s.read(s.ROOT/'authority/admissions/governance-transaction-surface/v1/instances/typed-relations/materializes-generated-output.json')
    row=fresh['after']['registry']['kinds'][-1]
    instance['schema_version']='relational-checker.extension-carrier/v1-candidate'
    instance['payload'].update(relation_kind_ref=row['id'],qualifiers={'trace_label':'fixture:label'})
    instance['payload']['source']['kind']='capability-instance';instance['payload']['target']['kind']='contract'
    s.require(not list(jsonschema.Draft202012Validator(projected).iter_errors(instance)),'new declared carrier input rejected')
    instance['payload']['target']['kind']='principal'
    s.require(list(jsonschema.Draft202012Validator(projected).iter_errors(instance)),'new undeclared pair accepted')
    controls.append({'name':'extension carrier preserves all ordered declarations','result':'pass','kinds':42,'pairs':551})
    s.write(BASE/'obligation-policy.json',g.policy())
    s.write(BASE/'required-fresh-obligations.json',required);s.write(BASE/'required-rule-obligations.json',rule_required)
    s.write(BASE/'candidate-extension-carrier.json',projected)
    s.write(BASE/'coverage-controls.json',{'result':'pass','controls':controls,
        'fresh_obligation_count':len(required['obligations']),'rule_obligation_count':len(rule_required['obligations']),
        'source_projection':g.source_projection(fresh),'authority_effect':'none'})
    outputs={name:BASE/name for name in ['obligation-policy.json','coverage-controls.json','required-fresh-obligations.json','required-rule-obligations.json','candidate-extension-carrier.json']}
    outputs['obligation-generator']=BASE/'generator.py'
    s.accept('E02',outputs,
        ['Computed supported profiles generate all nine non-rule obligations; a rule change adds six mandatory L3 obligations. The fresh candidate has exact source/profile correspondence and a 42-kind, 551-pair carrier.',
         'Submission validation recomputes classification and the policy identity and requires the exact obligation ID/name/hard/scope set; evidence can only fill the generated entries.'],
        ['Omitted/duplicated obligations, weakened policy/hard flags, wrong proposal identity and a misclassified rule change reject.',
         'Unknown fields create an explicit unsupported hard obligation; an added reference meaning unsupported by the declared annotation profile rejects source projection.'],
        [Path(__file__),s.BASE/'evolution/proposals/classifier.py',s.BASE/'evolution/proposals/fresh-kind-proposal.json',s.BASE/'evolution/proposals/rule-change-proposal.json',s.BASE/'coverage/carrier/check_coverage.py'])
    print(json.dumps({'task':'E02','result':'accepted','non_rule_obligations':len(required['obligations']),'rule_obligations':len(rule_required['obligations'])}))


if __name__=='__main__':main()
