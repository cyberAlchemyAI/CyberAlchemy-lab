#!/usr/bin/env python3
"""Validate reference resolution against kernel-checked F0 decisions."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import resolver as r
s=r.s
BASE=Path(__file__).resolve().parent


def main():
    registry=s.read(s.BASE/'registry/normalized-registry.json')
    raw=(s.BASE/'input/example-addition.json').read_bytes()
    graph=r.from_decoder(raw)
    s.require(r.resolve(graph,registry)['status']=='supported','positive reference fixture rejected')
    cases=[('valid',lambda g:None,True),
        ('wrong target version',lambda g:g['assertions'][0]['qualifiers'].update(exact_version_ref='other-version'),False),
        ('nonempty absent evidence',lambda g:g['assertions'][0]['qualifiers'].update(conformance_evidence_refs='missing:assessment'),False),
        ('wrong evidence type',lambda g:g['assessments'][0].update(mode='application-receipt',role='role',output_digest='digest'),False),
        ('wrong scope',lambda g:g['assessments'][0].update(scope='other-scope'),False),
        ('unaccepted evidence',lambda g:g['assessments'][0].update(accepted=False),False),
        ('wrong evidence endpoint version',lambda g:g['assessments'][0]['target'].update(version='other-version'),False),
        ('wrong effect target version',lambda g:g['assertions'][1]['qualifiers'].update(exact_target_version_ref='other-version'),False),
        ('wrong receipt role',lambda g:g['assessments'][1].update(role='other-role'),False),
        ('wrong receipt digest',lambda g:g['assessments'][1].update(output_digest='other-digest'),False),
        ('wrong target content identity',lambda g:g['nodes'][4].update(content_identity='other-identity'),False),
        ('nonempty absent receipt',lambda g:g['assertions'][2]['qualifiers'].update(application_receipt_ref='missing:receipt'),False),
        ('duplicate evidence token',lambda g:g['assessments'].append(deepcopy(g['assessments'][0])),False),
        ('reversed ordered pair',lambda g:g['assertions'][0].update(source=deepcopy(g['assertions'][0]['target']),target=deepcopy(g['assertions'][0]['source'])),False),
        ('wrong root decision type',lambda g:g['admission_roots'].append({'subject':g['nodes'][0]['ref'],'decision':g['nodes'][1]['ref'],'authority_evidence':'fixture:root'}),False)]
    controls=[]
    with tempfile.TemporaryDirectory(prefix='reference-controls-') as folder:
        build=Path(folder);modules=s.compile_lean(build,r.d.core_modules())
        for name,mutate,expected in cases:
            fixture=deepcopy(graph);mutate(fixture)
            result=r.resolve(fixture,registry)
            projected=deepcopy(fixture)
            for edge in projected['assertions']:edge.pop('kind_version')
            kernel=r.d.check({'schema_version':'relational-checker.normal-form/v1','graph':projected},build)
            accepted=result['status']=='supported'
            s.require(accepted==expected==kernel['accepted_result'],'reference projection differs from kernel: '+name)
            controls.append({'name':name,'expected_acceptance':expected,'result':'pass','resolver':result,'kernel':kernel})
    for name,mutate in [('wrong definition version',lambda g:g['assertions'][0].update(kind_version='sha256:'+'0'*64)),
                        ('missing endpoint',lambda g:g['nodes'].pop(1))]:
        fixture=deepcopy(graph);mutate(fixture);result=r.resolve(fixture,registry)
        s.require(result['status']=='invalid','invalid binding accepted')
        controls.append({'name':name,'result':'pass','resolver':result})
    for kind in registry['kinds']:
        if kind['id'] in r.SUPPORTED:continue
        pair=kind['pairs'][0]
        fixture={'nodes':[{'ref':{'id':'s','version':'v1'},'kind':pair['source_kind'],'content_identity':'source:fixture'},
                          {'ref':{'id':'t','version':'v1'},'kind':pair['target_kind'],'content_identity':'target:fixture'}],
                 'assertions':[{'id':'e','kind':kind['id'],'kind_version':kind['version'],
                                'source':{'id':'s','version':'v1'},'target':{'id':'t','version':'v1'},
                                'qualifiers':{axis:'fixture:nonempty' for axis in kind['fields']}}],
                 'assessments':[],'admission_roots':[]}
        result=r.resolve(fixture,registry)
        s.require(result['status']=='unsupported' and not result['derived_admission_roots'],'unresolved semantics classified valid')
        controls.append({'name':'unsupported '+kind['id'],'result':'pass','resolver':result})
    s.write(BASE/'reference-policy.json',r.policy(registry))
    s.write(BASE/'reference-controls.json',{'result':'pass','control_count':len(controls),
        'kernel_differential_control_count':len(cases),'controls':controls,'modules':modules,
        'all_qualifier_axes_accounted':sum(len(row['fields']) for row in registry['kinds']),
        'projection_formally_proved':False,
        'claim_ceiling':'Typed three-kind reference resolution aligned against kernel controls; every other current kind returns unsupported. Assessment and authority truth are supplied.'})
    s.accept('C04',{'reference-resolver':BASE/'resolver.py','reference-policy.json':BASE/'reference-policy.json','reference-controls.json':BASE/'reference-controls.json'},
        ['Exact target versions, assessment modes, exact subject/target references, accepted posture, scopes, receipt roles and output identities are checked; 15 fixtures agree with kernel decisions.',
         'All qualifier axes of all 41 records are listed; the other 38 kinds have explicit unresolved typed semantic obligations, including separate stress-profile adapter boundaries.'],
        ['Nonempty wrong-type/version/scope/role references and absent evidence reject in meaningful differential controls.',
         'No assertion derives an admission root; all 38 unresolved kinds return unsupported, and assessment truth remains an explicit external assumption.'],
        [Path(__file__),s.BASE/'input/decoder.py',s.BASE/'registry/normalized-registry.json',s.FORMAL/'core/RelationalSemantics.lean'])
    print(json.dumps({'task':'C04','result':'accepted','controls':len(controls)}))


if __name__=='__main__':main()
