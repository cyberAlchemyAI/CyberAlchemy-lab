"""A total, source-bound baseline inventory. Search leads never count as proof."""
import argparse
import base64
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path.insert(0,str(IMPL))
import resolver as r

DATA='docs/plans/definition-formal-assurance/candidate/assurance-snapshots-v1/'
PILOT='docs/plans/definition-formal-assurance/candidate/d0-d2-v1/'
EXCLUDED='craft/formalization/candidates/definition-assurance-v1/'


def pointer(tokens):return '/'+('/'.join(str(t).replace('~','~0').replace('/','~1') for t in tokens))


def leaves(value,tokens=()):
    if isinstance(value,dict):
        for key,child in value.items():yield from leaves(child,tokens+(key,))
    elif isinstance(value,list):
        for i,child in enumerate(value):yield from leaves(child,tokens+(i,))
    elif isinstance(value,str):yield pointer(tokens),value


def source_documents(snapshot):
    files={row['path']:base64.b64decode(row['content_base64']) for row in snapshot['captured_files']}
    return {row['version_ref']:r.parse(files[row['path']],row['path']) for row in snapshot['current_entries']+snapshot['historical_entries']}


def selected_value(document,selector):
    if not isinstance(selector,str) or not selector.startswith('/'):raise ValueError('invalid-selector')
    value=document
    for token in selector[1:].split('/'):
        token=token.replace('~1','/').replace('~0','~')
        value=value[int(token)] if isinstance(value,list) else value[token]
    return value


def annotation_bound(document,annotation):
    try:
        value=selected_value(document,annotation['selector']);excerpt=annotation['excerpt'];start=annotation['start_character']
        return (isinstance(value,str) and isinstance(excerpt,str) and type(start) is int and start>=0
                and value[start:start+len(excerpt)]==excerpt and r.digest(excerpt.encode())==annotation['excerpt_sha256'])
    except (ValueError,KeyError,TypeError,IndexError):return False


def origin_ids(document):
    # An imported ID is a lead into original vocabulary, never identity equality.
    return sorted({m.group(0) for ref in document.get('source_refs',[]) for _,value in leaves(ref)
                   for m in re.finditer(r'\bCAV2-D[0-9]+\b',value)})


def inventory(root,documents,entries,paths):
    ids={row['definition_id'] for row in entries}
    originals={identity:set() for identity in ids}
    for row in entries:originals[row['definition_id']].update(origin_ids(documents[row['version_ref']]))
    tokens=ids|{x for values in originals.values() for x in values}
    pattern=re.compile(r'(?<![A-Za-z0-9_.:-])('+ '|'.join(re.escape(x) for x in sorted(tokens,key=len,reverse=True))+r')(?![A-Za-z0-9_.:-])')
    records=[];direct={identity:[] for identity in ids};indirect={identity:[] for identity in ids}
    for path in sorted(set(paths)):
        record={'path':path,'sha256':None,'status':'unresolved','kind':'native-source' if path.endswith('.lean') else 'structured-artifact' if path.endswith('.json') else 'text-or-code'}
        try:
            raw=r.read_bytes(root,path);record['sha256']=r.digest(raw)
            if path.endswith('.json'):
                document=r.parse(raw,path);texts=list(leaves(document))
            else:texts=[('/text',raw.decode('utf-8'))]
            record['status']='inspected';seen=set()
            for selector,text in texts:
                matched={m.group(1) for m in pattern.finditer(text)}
                for identity in ids:
                    key=(identity,selector)
                    if key in seen:continue
                    evidence={'path':path,'sha256':record['sha256'],'selector':selector,'meaning':'Search lead only; no formal equivalence, source acceptance or proof inferred.'}
                    if identity in matched:direct[identity].append(evidence);seen.add(key)
                    elif matched&originals[identity]:
                        indirect[identity].append({**evidence,'matched_origin_ids':sorted(matched&originals[identity]),'meaning':'Declared source-origin vocabulary lead only; no identity merge or semantic preservation inferred.'});seen.add(key)
        except (r.CaptureFault,UnicodeError) as error:
            record['status']='uninspectable';record['error']=error.code if isinstance(error,r.CaptureFault) else 'non-utf8-artifact'
        records.append(record)
    return records,direct,indirect


def default_paths(root):
    paths=[]
    for file in (root/'craft/formalization').rglob('*'):
        if file.is_file() and '__pycache__' not in file.parts:
            path=file.relative_to(root).as_posix()
            if not path.startswith(EXCLUDED):paths.append(path)
    paths.extend(file.relative_to(root).as_posix() for file in (root/'craft/impl/cli/lean').glob('*.lean'))
    return sorted(set(paths))


def assess(snapshot,root,paths=None,expected_counts=None):
    root=r.resolve_root(root);r.verify(snapshot)
    if expected_counts and (snapshot['counts']['current_identities'],snapshot['counts']['admitted_versions'])!=expected_counts:
        raise r.CaptureFault('unexpected-source-denominator')
    currentness={'status':'current','checked_boundary':'assessment input'}
    try:r.verify(snapshot,root)
    except r.CaptureFault as error:currentness={'status':'unresolved','code':error.code,'path':error.path,'checked_boundary':'assessment input'}
    documents=source_documents(snapshot);all_entries=snapshot['current_entries']+snapshot['historical_entries']
    artifacts,direct,indirect=inventory(root,documents,all_entries,default_paths(root) if paths is None else paths)
    evidence_inputs=[];partial={};foundations={};annotations={};replay=None
    for path,kind in [(PILOT+'interpretation.json','pilot'),(DATA+'foundations/definition-kinds.json','foundation'),(DATA+'units/A03/existing-pilot-replay.json','replay')]:
        try:
            raw=r.read_bytes(root,path);doc=r.parse(raw,path);evidence_inputs.append({'path':path,'sha256':r.digest(raw),'status':'inspected'})
            if kind=='pilot':partial=doc.get('dependencies',{})
            elif kind=='foundation':
                foundations={item['definition_id']:item for item in doc.get('source_bindings',[])}
                for annotation in doc.get('source_clause_annotations',[]):annotations.setdefault(annotation['definition_id'],[]).append(annotation)
            else:
                # A report is recognized only as the local, exact prior replay report.
                # Its result never becomes whole-definition proof or owner acceptance.
                bound={item['path']:item['sha256'] for item in doc.get('bindings',[])}
                required={PILOT+f for f in ['evidence.json','checker.py','replay.py','verify_evidence.py','evidence.schema.json','interpretation.json']}
                if doc.get('result')=='PASS' and required==set(bound) and all(r.digest(r.read_bytes(root,p))==sha for p,sha in bound.items()):
                    replay={'status':'exact-prior-pilot-replay-report-bound','path':path,'sha256':r.digest(raw),'cases_checked':doc.get('cases_checked'),'witnesses_replayed':doc.get('witnesses_replayed'),'meaning':'Finite selected-clause evidence for the combined three-definition pilot. No whole-definition result or independent owner fidelity.'}
                else:replay={'status':'unresolved-report-bindings','path':path}
        except (r.CaptureFault,KeyError,TypeError,AttributeError) as error:
            evidence_inputs.append({'path':path,'status':'unresolved','code':getattr(error,'code','malformed-evidence-artifact')})
    queue=[];historical=[]
    for entry in all_entries:
        identity=entry['definition_id'];doc=documents[entry['version_ref']];voice=doc.get('voices',{}).get('scientific_formal',{})
        row={k:entry[k] for k in ['definition_id','version_ref','path','sha256','term','effective_state']}
        row.update(source_currentness=currentness,formal_voice={'present':isinstance(voice,dict),'normative_statement_present':isinstance(voice,dict) and isinstance(voice.get('normative_statement'),str),'formal_expression_present':isinstance(voice,dict) and isinstance(voice.get('formal_expression'),str),'meaning':'Source prose/expression; not an executable model or a proof result.'},origin_vocabulary_ids=origin_ids(doc),direct_identity_leads=direct[identity],indirect_origin_leads=indirect[identity],candidate_bindings=[],source_fidelity='owner-review-pending',whole_definition_assurance='not-established',verified_whole_definition_proofs=[],next_action='Author complete clause correspondence, explicit signature/dependencies/assumptions and obligation scope; then obtain attributable fidelity review and exact evidence.')
        pilot=partial.get(identity)
        if isinstance(pilot,dict):
            exact=(pilot.get('version_ref')==entry['version_ref'] and pilot.get('source_path')==entry['path'] and pilot.get('source_sha256')==entry['sha256'])
            try:
                for selector in pilot.get('selectors',[]):selected_value(doc,selector)
                exact=exact and bool(pilot.get('selectors'))
            except (ValueError,KeyError,TypeError,IndexError):exact=False
            row['candidate_bindings'].append({'kind':'partial-pilot-translation','status':'exact-source-bound' if exact else 'stale-or-unbound','selectors':pilot.get('selectors',[]),'fidelity_review':'owner-review-pending','coverage':'selected clauses only','replay':replay if exact else None})
        foundation=foundations.get(identity)
        if isinstance(foundation,dict):
            exact=all(foundation.get(k)==entry[k] for k in ['version_ref','path','sha256'])
            selected=annotations.get(identity,[])
            exact=exact and bool(selected) and all(a.get('source_ref')==entry['version_ref'] and annotation_bound(doc,a) for a in selected)
            row['candidate_bindings'].append({'kind':'foundation-clause-annotation','status':'exact-source-bound' if exact else 'stale-or-unbound','selectors':[a['selector'] for a in selected],'forms':sorted({f for a in selected for f in a.get('definitional_forms',[])}),'roles':sorted({role for a in selected for role in a.get('statement_roles',[])}),'coverage':'Selected source clause classification only; no complete semantic translation','fidelity_review':'not-owner-reviewed'})
        row['definition_form_status']='selected-clause-candidate' if any(x['kind']=='foundation-clause-annotation' and x['status']=='exact-source-bound' for x in row['candidate_bindings']) else 'unassigned'
        row['logic_profile_status']='requires-explicit-interpretation-selection'
        row['priority']=0 if row['definition_form_status']=='selected-clause-candidate' else 1
        (queue if entry['effective_state']=='admitted-current' else historical).append(row)
    queue.sort(key=lambda row:(row['priority'],row['definition_id']));historical.sort(key=lambda row:row['version_ref'])
    report={'schema_version':'definition-assurance-source-coverage/v1-candidate','authority_effect':'none','status':'assessed-baseline' if currentness['status']=='current' else 'source-currentness-unresolved','snapshot_binding':{'registry_sha256':snapshot['source_envelope']['payload']['registry_sha256'],'current_lookup_sha256':snapshot['source_envelope']['payload']['current_lookup_sha256']},'source_currentness':currentness,'counts':{'current_identities':len(queue),'admitted_versions':len(queue)+len(historical),'historical_versions':len(historical),'source_formal_expressions':sum(row['formal_voice']['formal_expression_present'] for row in queue),'source_bound_partial_pilot_translations':sum(any(x['kind']=='partial-pilot-translation' and x['status']=='exact-source-bound' for x in row['candidate_bindings']) for row in queue),'source_bound_foundation_annotations':sum(row['definition_form_status']=='selected-clause-candidate' for row in queue),'verified_whole_definition_proofs':0,'owner_reviewed_whole_definition_translations':0},'current_queue':queue,'historical_versions':historical,'inspected_artifacts':artifacts,'evidence_inputs':evidence_inputs,'inspection_scope':['craft/formalization excluding this assurance implementation and bytecode','craft/impl/cli/lean/*.lean','Exact previous pilot interpretation and local new replay report','Exact selected foundation annotations'],'excluded_inferences':['Textual identity occurrence is not a formal binding or proof','Imported source IDs do not identify Lab definitions by equality','Profile admission and JSON schema validation do not prove the admitted definitions','A model witness or finite result does not prove source fidelity or unrestricted consistency'],'unresolved_aspects':['Complete clause translations and owner fidelity for all 183 current identities','Exact checked theorem/obligation/provider joins for whole-definition assertions','Explicit classification and extension selection beyond eight selected foundational clauses','FID-HYP-001: inherited Premise/Hypothesis correspondence conflict','Complete shared theory, population, non-collapse and transition proofs'],'claim_ceiling':'Total exact-source baseline and bounded inspected-artifact leads. No silently omitted admitted version. No generic provider/source correspondence, new owner acceptance or whole-definition assurance.'}
    validate_coverage(snapshot,report)
    return report


def validate_coverage(snapshot,report):
    for key,rows_key in [('current_entries','current_queue'),('historical_entries','historical_versions')]:
        expected={row['version_ref']:row for row in snapshot[key]};rows=report[rows_key]
        if len(rows)!=len(expected) or {row['version_ref'] for row in rows}!=set(expected):raise r.CaptureFault('coverage-denominator-mismatch')
        for row in rows:
            if any(row[k]!=expected[row['version_ref']][k] for k in ['definition_id','version_ref','path','sha256','term','effective_state']):raise r.CaptureFault('coverage-source-binding-mismatch',row['version_ref'])
            if row['whole_definition_assurance']!='not-established' or row['verified_whole_definition_proofs'] or row['source_fidelity']!='owner-review-pending':raise r.CaptureFault('unjustified-coverage-claim',row['version_ref'])
    if (report['counts']['current_identities'],report['counts']['admitted_versions'],report['counts']['historical_versions'])!=(snapshot['counts']['current_identities'],snapshot['counts']['admitted_versions'],snapshot['counts']['historical_versions']):raise r.CaptureFault('coverage-denominator-mismatch')
    if report['counts']['verified_whole_definition_proofs'] or report['counts']['owner_reviewed_whole_definition_translations'] or report['authority_effect']!='none':raise r.CaptureFault('unjustified-coverage-claim')
    return {'result':'PASS','meaning':'Total source binding and conservative baseline claim checks only.'}


def publish_report(report,root,output):
    import os,uuid
    if not isinstance(output,str) or not output.startswith(DATA):raise r.CaptureFault('protected-output',str(output))
    parent,name=r.open_parent(r.resolve_root(root),output,create=True)
    temporary='.coverage-'+uuid.uuid4().hex+'.tmp'
    try:
        fd=os.open(temporary,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=parent)
        with os.fdopen(fd,'w') as stream:json.dump(report,stream,indent=2,sort_keys=True);stream.write('\n');stream.flush();os.fsync(stream.fileno())
        try:os.link(temporary,name,src_dir_fd=parent,dst_dir_fd=parent,follow_symlinks=False)
        except FileExistsError as error:raise r.CaptureFault('output-already-exists',output) from error
        os.fsync(parent)
    finally:
        try:os.unlink(temporary,dir_fd=parent)
        except FileNotFoundError:pass
        os.close(parent)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--repo',required=True);parser.add_argument('--snapshot',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    root=r.resolve_root(args.repo);snapshot=r.parse(r.read_bytes(root,args.snapshot),args.snapshot)
    report=assess(snapshot,root,expected_counts=(183,189))
    if report['source_currentness']['status']!='current':raise r.CaptureFault('source-currentness-unresolved')
    # Recheck every consumed artifact before create-only publication of this baseline.
    r.verify(snapshot,root)
    if default_paths(root)!=[row['path'] for row in report['inspected_artifacts']]:raise r.CaptureFault('artifact-inventory-drift')
    for row in report['inspected_artifacts']+report['evidence_inputs']:
        if row.get('sha256') and r.digest(r.read_bytes(root,row['path']))!=row['sha256']:raise r.CaptureFault('artifact-input-drift',row['path'])
    publish_report(report,root,args.output)
    print(json.dumps({'status':report['status'],'counts':report['counts'],'inspected_artifacts':len(report['inspected_artifacts']),'uninspectable_artifacts':sum(row['status']!='inspected' for row in report['inspected_artifacts']),'claim_ceiling':report['claim_ceiling']},indent=2))


if __name__=='__main__':
    try:main()
    except (r.CaptureFault,FileExistsError) as error:print(json.dumps({'status':'unresolved','code':getattr(error,'code','output-already-exists'),'path':getattr(error,'path','')}));raise SystemExit(2)
