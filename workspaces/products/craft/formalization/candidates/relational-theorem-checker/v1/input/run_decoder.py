#!/usr/bin/env python3
"""Validate source-to-F0 decoding, hostile transports and semantic evaluations."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import tempfile
import decoder as d
s=d.s
BASE=Path(__file__).resolve().parent


def exercise(build):
    fixture=s.read(BASE/'example-addition.json')
    controls=[]
    def reject(name,mutate,structural=True):
        item=deepcopy(fixture);mutate(item)
        try:normal=d.normalize(item)
        except ValueError as error:
            s.require(structural, 'semantic control unexpectedly failed decoding: '+name)
            controls.append({'name':name,'result':'rejected','method':'strict schema/reference projection','diagnostic':str(error)})
            return
        s.require(not structural, 'invalid decoding accepted: '+name)
        result=d.check(normal,build)
        s.require(not result['accepted_result'], 'invalid semantic graph accepted: '+name)
        controls.append({'name':name,'result':'rejected','method':result['proof_method'],'evaluation_source_sha256':result['evaluation_source_sha256']})
    reject('unknown relation kind',lambda q:q['addition'].update(relation_kind_id='relation.future'))
    reject('extra qualifier',lambda q:q['addition']['qualifiers'].update(extra='no'))
    reject('missing qualifier',lambda q:q['addition']['qualifiers'].pop('output_digest'))
    reject('duplicate node identity/version',lambda q:q['graph']['nodes'].append(deepcopy(q['graph']['nodes'][0])))
    reject('unresolved endpoint',lambda q:q['addition']['target'].update(node_id='missing'))
    reject('phantom conformance pair',lambda q:q['graph']['assertions'][0].update(target=q['graph']['nodes'][4]))
    reject('reversed materialization pair',lambda q:q['addition'].update(source=q['addition']['target'],target=q['addition']['source']))
    reject('changed definition identity',lambda q:q['addition']['definition_ref'].update(artifact_id='other'))
    reject('changed definition digest',lambda q:q['addition']['definition_ref'].update(sha256='0'*64))
    reject('unknown F0 node kind',lambda q:q['graph']['nodes'][0].update(kind='principal'))
    reject('duplicate evidence identity',lambda q:q['assessments'].append(deepcopy(q['assessments'][0])))
    reject('unresolved assessment endpoint',lambda q:q['assessments'][0]['target'].update(version='v9'))
    reject('extra sidecar property',lambda q:q.update(extra=True))
    reject('wrong target version',lambda q:q['addition']['qualifiers'].update(output_digest=q['addition']['qualifiers']['output_digest']) or q['graph']['assertions'][0]['qualifiers'].update(exact_version_ref='v2'),False)
    reject('digest mismatch',lambda q:q['addition']['qualifiers'].update(output_digest='wrong'),False)
    reject('missing conformance assessment',lambda q:q['assessments'].pop(0),False)
    reject('unaccepted application receipt',lambda q:q['assessments'][1].update(accepted=False),False)
    reject('scope upgrade with same evidence',lambda q:q['graph']['assertions'][0]['qualifiers'].update(conformance_scope='runtime'),False)
    reject('duplicate addition identity',lambda q:q['addition'].update(assertion_id=q['graph']['assertions'][0]['assertion_id']),False)
    # The whole old graph is checked again, even if the proposed assertion is valid.
    reject('invalid base survives otherwise valid addition',lambda q:q['graph']['assertions'][1]['qualifiers'].update(exact_target_version_ref='v9'),False)
    for name,raw in [('duplicate JSON members',b'{"x":1,"x":2}'),('nonfinite JSON',b'{"x":NaN}'),
                     ('invalid UTF8',b'\xff'),('isolated surrogate',b'"\\ud800"')]:
        try:d.decode(raw)
        except (ValueError,UnicodeError):controls.append({'name':name,'result':'rejected','method':'strict raw transport'})
        else:raise ValueError('malformed transport accepted: '+name)
    normal=d.normalize(fixture)
    # Raw scalar preservation includes control chars and syntax-like strings.
    scalar=deepcopy(fixture);scalar['addition']['assertion_id']='ação 漢字\n"; axiom bypass : False --'
    preserved=d.normalize(d.decode(json.dumps(scalar).encode()))
    s.require(preserved['addition']['id']==scalar['addition']['assertion_id'],'string projection changed input')
    s.require(d.check(preserved,build)['accepted_result'],'scalar-safe encoder failed')
    controls.append({'name':'Unicode/control/syntax scalar preservation','result':'preserved','method':'scalar encoding and kernel evaluation'})
    result=d.check(normal,build)
    s.require(result['accepted_base'] and result['accepted_result'] and result['assertion_count']==3,'inhabited addition failed')
    return normal,result,controls


def main():
    s.context('P02',[(s.PLAN,'tasks[id=P02]'),(BASE.parent/'baseline/task-acceptance.json','accepted current baseline'),
        (s.FORMAL/'core/RelationalInput.lean','all formal input structures'),(s.FORMAL/'core/RelationalSemantics.lean','independent validity clauses'),
        (d.INTERFACES/'schemas/l0-graph.schema.json','companion structural graph'),(d.INTERFACES/'schemas/l0-assertion.schema.json','exact three-kind qualifier branches'),
        (d.INTERFACES/'contracts/L0.md','normalization and checking boundaries')],
        [{'classification':'non-blocking','choice':'retain the existing companion carrier and add explicit assessment/root sidecars',
          'basis':'The old graph carrier lacks the assessment and admission-root inventories required by the proved model.'},
         {'classification':'non-blocking','choice':'preserve exact version qualifier strings without token rewriting',
          'basis':'F0 compares the supplied version string with the endpoint version. Compound token formats need a separately reviewed adapter.'}])
    with tempfile.TemporaryDirectory(prefix='decoder-audit-') as folder:
        build=Path(folder);logs=s.compile_lean(build,d.core_modules());normal,result,controls=exercise(build)
    fields={
        'schema_version':'transport discriminator; retained in raw-input binding',
        'graph.graph_id':'normal-form metadata; retained in normalization receipt, outside Lean Graph',
        'graph.nodes[*].node_id':'Node.ref.id','graph.nodes[*].version':'Node.ref.version',
        'graph.nodes[*].kind':'Node.kind closed constructor; unknown F0 kinds rejected',
        'graph.nodes[*].source_ref.sha256':'Node.contentIdentity; opaque string equality in the formal model',
        'graph.nodes[*].source_ref.artifact_id/size_bytes/media_type':'transport metadata retained in raw bytes; not authenticated by F0',
        'graph.assertions[*].schema_version':'companion carrier discriminator',
        'graph.assertions[*].assertion_id':'Assertion.id','graph.assertions[*].relation_kind_id':'Assertion.kind',
        'graph.assertions[*].relation_kind_version/definition_ref':'checked against exact selected kind source hash and byte size',
        'graph.assertions[*].source/target':'Assertion.source/target exact identity/version; complete raw endpoint metadata must equal inventory',
        'qualifiers.conformance_scope/exact_version_ref/conformance_evidence_refs':'Qualifiers.conformance(scope,version,evidence), strings preserved exactly',
        'qualifiers.effect_kind/exact_target_version_ref':'Qualifiers.effect(effectKind,version), strings preserved exactly',
        'qualifiers.application_receipt_ref/consequence_role/output_digest':'Qualifiers.materialization(receipt,role,digest), strings preserved exactly',
        'assessments[*].ref/mode/subject/target/scope/role/output_digest/accepted':'Assessment.ref/mode/subject/target/scope/role/outputDigest/accepted, one-to-one',
        'admission_roots[*].subject/decision/authority_evidence':'AdmissionRoot.subject/decision/authorityEvidence, supplied data only',
        'addition':'same assertion mapping; checkGraph(applyAddition) fully recomputes all invariants'}
    s.write(BASE/'schema-api-alignment.json',{'result':'pass','supported_operations':['normalizeGraph','checkAddition'],
        'input_discriminator':'relational-checker.execution-input/v1','companion_carrier':'unchanged candidate l0-graph + sidecars',
        'frozen_typed_relation_v2_unchanged':True,'field_mapping':fields,
        'old_example_version_policy':'Compound exact-version tokens are not silently converted; a literal mismatch yields rejection.',
        'identity_policy':'Exact (id,version) uniqueness, matching the formal model; distinct versions of one ID remain representable.',
        'unsupported_operations':'Other authored API operations remain their later plan tasks.',
        'trust_boundaries':['UTF8/JSON parsing','source-to-formal projection','SHA256 implementation','Lean compiler/runtime','supplied evidence truth'],
        'general_decoder_equivalence_proved':False,'individual_evaluations_kernel_checked':True,
        'modules':logs,'normal_form_sha256':result['normal_form_sha256']})
    s.write(BASE/'decoding-controls.json',{'result':'pass','controls':controls,'positive':result,
        'normal_form_preservation':normal,'claim_ceiling':'Deterministic projection tested against unchanged typed semantics; no raw-decoder equivalence or external evidence authentication theorem.'})
    s.accept('P02',{'schema-api-alignment.json':BASE/'schema-api-alignment.json','decoder':BASE/'decoder.py',
        'normal-form-schema.json':BASE/'normal-form-schema.json','decoding-controls.json':BASE/'decoding-controls.json'},
        ['Every supported carrier, sidecar and qualifier field has an explicit mapping; immutable Typed Relation/v2 remains unchanged.',
         'Strict parser, exact definitions and endpoint inventories are checked; scalars and qualifier strings are preserved and all evaluated outcomes are kernel replayed.'],
        ['Twenty-four malformed or semantic cases reject, including kinds, qualifiers, identities, references, pairs and digest mismatch.',
         'Compound version tokens are never reinterpreted silently; raw parsing, hashing and compiler/evidence trust remain explicit.'],
        [Path(__file__),BASE/'L0Runtime.lean',BASE/'example-addition.json',BASE.parent/'baseline/baseline-manifest.json',
         s.FORMAL/'proofs/l0/statement-and-axiom-audit.json'])
    print(json.dumps({'task':'P02','result':'accepted','controls':len(controls),'proof_method':result['proof_method']}))


if __name__=='__main__':main()
