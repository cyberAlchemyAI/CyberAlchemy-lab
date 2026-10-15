"""Check source-accounting separately from logical typechecking or fidelity."""
import base64
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[7]
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1'
sys.path.insert(0,str(IMPL))
import contracts as c
import resolver as r

SCHEMA_PATH=IMPL/'schemas/interpretation.json'
MEANING_ROOTS=('voices','boundaries','scope','claim_ceiling')


def string_leaves(value,path=()):
    if isinstance(value,dict):
        for key,child in value.items():yield from string_leaves(child,(*path,key))
    elif isinstance(value,list):
        for index,child in enumerate(value):yield from string_leaves(child,(*path,index))
    elif isinstance(value,str) and value:yield c.pointer(path),value


def inventory(document):
    result=[]
    for root in MEANING_ROOTS:
        for selector,text in string_leaves(document.get(root), (root,)):
            facet=('normative' if selector.startswith('/voices/scientific_formal/') else 'explanatory' if selector.startswith('/voices/') else 'boundary' if selector.startswith('/boundaries/') else 'scope' if selector.startswith('/scope/') else 'claim-ceiling' if selector=='/claim_ceiling' else 'unresolved')
            result.append({'unit_id':'unit-'+r.digest((selector+'\x00'+text).encode()),'selector':selector,'text_sha256':r.digest(text.encode()),'length_characters':len(text),'source_facet':facet})
    return sorted(result,key=lambda row:row['selector'])


def source_document(snapshot,source):
    matches=[row for row in snapshot['current_entries'] if all(source[k]==row[k] for k in ('definition_id','version_ref','path','sha256'))]
    if len(matches)!=1:raise r.CaptureFault('unbound-current-interpretation-source')
    row=next(row for row in snapshot['captured_files'] if row['path']==source['path'])
    return r.parse(base64.b64decode(row['content_base64']),source['path'])


def schema():
    if c.Draft202012Validator is None:raise c.InputError('missing-jsonschema-runtime')
    value=json.loads(SCHEMA_PATH.read_text())
    stack=[value]
    while stack:
        node=stack.pop()
        if isinstance(node,dict):
            for key in ('$ref','$dynamicRef','$recursiveRef'):
                if key in node and (not isinstance(node[key],str) or not node[key].startswith('#/$defs/') or node[key][8:] not in value['$defs']):raise c.InputError('invalid-local-schema-reference')
            stack.extend(node.values())
        elif isinstance(node,list):stack.extend(node)
    c.Draft202012Validator.check_schema(value)
    return value


def check(packet,snapshot,required_dependencies=None,required_conflicts=()):
    """Required dependencies/findings come from the caller's separate review.

    This checker never issues semantic readiness, including for complete maps.
    Whole text leaves may contain multiple claims; explicit splits and review
    remain necessary. Character coverage establishes accounting only.
    """
    try:
        c.bounded_tree(packet);local=schema()
        errors=list(c.Draft202012Validator(local).iter_errors(packet))
        if errors:return {'status':'malformed','authority_effect':'none','semantic_ready':False,'diagnostics':[{'code':'schema-'+str(e.validator),'path':c.pointer(e.absolute_path)} for e in errors[:30]]}
        r.verify(snapshot)
        core=packet['interpretation'];base=c.validate({'schema_version':'definition-assurance-input/v1-candidate','kind':'interpretation','authority_effect':'none','payload':core},'interpretation')
        if base['status']!='structurally-valid':return {**base,'semantic_ready':False}
        document=source_document(snapshot,core['source']);expected=inventory(document);actual=packet['source_units']
        if len(actual)!=len(expected) or sorted(actual,key=lambda row:row['selector'])!=expected:raise r.CaptureFault('source-unit-denominator-mismatch')
        units={row['unit_id']:row for row in expected};texts=dict(string_leaves(document))
        clauses={row['clause_id']:row for row in core['clauses']};covered={key:[] for key in units};linked=set()
        for link in packet['correspondence']:
            if link['unit_id'] not in units or link['clause_id'] not in clauses:raise r.CaptureFault('unbound-clause-correspondence')
            if link['clause_id'] in linked:raise r.CaptureFault('duplicate-clause-correspondence',link['clause_id'])
            linked.add(link['clause_id']);clause=clauses[link['clause_id']];unit=units[link['unit_id']];start=clause['start_character'];end=link['end_character'];text=texts[unit['selector']]
            if not (0<=start<end<=len(text)) or clause['source_selector']!=unit['selector'] or text[start:end]!=link['excerpt'] or r.digest(link['excerpt'].encode())!=clause['excerpt_sha256']:raise r.CaptureFault('clause-excerpt-binding-mismatch',clause['clause_id'])
            covered[unit['unit_id']].append((start,end))
            if clause['disposition'] in {'explanatory','deferred','unresolved'} and clause['formal_statement'] is not None:raise r.CaptureFault('nonencoded-clause-has-formula',clause['clause_id'])
            if clause['disposition']=='explanatory' and set(clause['roles'])!={'explanation-example'}:raise r.CaptureFault('explanation-role-mismatch',clause['clause_id'])
        if linked!=set(clauses):raise r.CaptureFault('unmapped-formal-clause')
        complete=True
        for identity,ranges in covered.items():
            offset=0
            for start,end in sorted(ranges):
                if start<offset:raise r.CaptureFault('overlapping-source-clause-ranges',identity)
                if start!=offset:complete=False
                offset=end
            if offset!=units[identity]['length_characters']:complete=False
        current={row['version_ref']:row for row in snapshot['current_entries']}
        for dependency in core['depends_on']:
            if dependency['version_ref'] not in current or any(dependency[k]!=current[dependency['version_ref']][k] for k in ('definition_id','path','sha256')):raise r.CaptureFault('unbound-current-dependency',dependency['version_ref'])
        declared={dep['version_ref'] for dep in core['depends_on']};used=set()
        for link in packet['dependency_links']:
            if link['clause_id'] not in clauses:raise r.CaptureFault('unbound-dependency-clause')
            if link['kind']=='semantic-use':
                dependency=link['dependency_ref']
                if dependency not in core['depends_on']:raise r.CaptureFault('undeclared-semantic-dependency',dependency['version_ref'])
                used.add(dependency['version_ref'])
        if used!=declared:raise r.CaptureFault('unused-declared-dependency')
        if required_dependencies is not None and set(required_dependencies)!=declared:raise r.CaptureFault('required-dependency-denominator-mismatch')
        assumptions={row['assumption_id']:row for row in core['assumptions']};assumed={};seen_assumptions=set()
        for link in packet['assumption_links']:
            if link['clause_id'] not in clauses or link['assumption_id'] not in assumptions:raise r.CaptureFault('unbound-assumption-link')
            if link['clause_id'] in assumed or link['assumption_id'] in seen_assumptions:raise r.CaptureFault('duplicate-assumption-link')
            assumed[link['clause_id']]=assumptions[link['assumption_id']];seen_assumptions.add(link['assumption_id'])
        for identity,clause in clauses.items():
            selected={'selected-axiom','selected-premise','constraint'}&set(clause['roles'])
            if clause['disposition']=='externally-assumed' or selected&{'selected-axiom','selected-premise'}:
                assumption=assumed.get(identity)
                if not assumption or len(clause['roles'])!=1 or assumption['role'] not in selected or not assumption['selected'] or assumption['commitment']=='unresolved' or assumption['scope']!=core['scope'] or assumption['statement']!=clause['formal_statement']:raise r.CaptureFault('unselected-or-substituted-assumption',identity)
                if clause['disposition']!='externally-assumed':raise r.CaptureFault('assumption-disposition-mismatch',identity)
            elif identity in assumed:raise r.CaptureFault('nonassumption-clause-linked-as-assumption',identity)
        if {key for key,assumption in assumptions.items() if assumption['selected']}!=seen_assumptions:raise r.CaptureFault('unmapped-selected-assumption')
        cases=packet['review_packet']['instances']+packet['review_packet']['counterexamples']
        if len({case['case_id'] for case in cases})!=len(cases):raise r.CaptureFault('duplicate-review-case-id')
        conflicts=packet['source_precedence']['conflicts']
        if len({row['finding_id'] for row in conflicts})!=len(conflicts):raise r.CaptureFault('duplicate-source-conflict-id')
        for case in cases:
            if not set(case['related_clause_ids'])<=set(clauses):raise r.CaptureFault('unbound-review-case-clause')
        for conflict in packet['source_precedence']['conflicts']:
            if not set(conflict['selectors'])<=set(texts):raise r.CaptureFault('unbound-conflict-selector')
        if not set(required_conflicts)<={row['finding_id'] for row in packet['source_precedence']['conflicts']}:raise r.CaptureFault('required-source-conflict-omitted')
        unresolved=[row['clause_id'] for row in core['clauses'] if row['disposition'] in {'deferred','unresolved'} or 'unresolved' in row['roles'] or 'unresolved' in row['forms']]
        return {'status':'candidate-accounted' if complete and not unresolved else 'correspondence-pending','authority_effect':'none','semantic_ready':False,'character_accounting_complete':complete,'source_units':len(expected),'mapped_clauses':len(linked),'unresolved_clauses':unresolved,'dependency_denominator':'separately-compared' if required_dependencies is not None else 'requires-independent-review','source_fidelity':core['source_fidelity'],'logical_typing':'not-assessed','proof':'not-assessed','claim_ceiling':'Exact source units, spans, explicit roles and conservative premise/dependency accounting. No semantic preservation, logical typechecking, owner acceptance or theorem claim.'}
    except (r.CaptureFault,c.InputError) as error:return {'status':('unsupported-runtime' if error.code in {'missing-jsonschema-runtime','invalid-local-schema-reference'} else 'malformed') if isinstance(error,c.InputError) else 'correspondence-invalid','authority_effect':'none','semantic_ready':False,'diagnostics':[{'code':error.code,'path':error.path}]}
    except (ValueError,OSError,KeyError,TypeError,IndexError,c.SchemaError) as error:return {'status':'unresolved-runtime-or-shape','authority_effect':'none','semantic_ready':False,'diagnostics':[{'code':type(error).__name__}]}
