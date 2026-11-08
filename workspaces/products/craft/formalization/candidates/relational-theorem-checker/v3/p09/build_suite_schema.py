"""Evidence classification for finite regression, without implied freshness."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
text={'type':'string','minLength':1};ref=obj({'path':text,'sha256':{'type':'string','pattern':'^[0-9a-f]{64}$'}})
case=obj({'name':text,'entry_point':text,'evidence_kind':{'enum':['fresh-kernel','saved-inspection','decoder','boundary','contract','inherited-control','abstract-theorem','unqualified-io']},
          'input':ref,'output':ref,'expected':text,'observed':text,'result':{'const':'pass'},'claim_scope':text,'authority_effect':{'const':'none'}})
suite=obj({'schema':{'const':'relational.qualification-suite/v3'},'result':{'const':'pass'},'cases':{'type':'array','items':case},
           'catalog':ref,'required_ids':{'type':'array','items':text},'source_receipts':{'type':'array','items':ref},
           'finite_regression_only':{'const':True},'authority_effect':{'const':'none'}})
(HERE/'qualification-suite.schema.json').write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:qualification-suite',**suite},indent=2)+'\n')
natural={'type':'integer','minimum':0}
audit=obj({'layout':{'enum':['combined','staged']},'evidence':ref,'required_statement':{'const':'Successor.Runtime.Catalog.RequiredGeneralBundle'},
           'statement_mode':text,'transitive_axioms':{'type':'array','uniqueItems':True,'items':{'enum':['propext','Classical.choice','Quot.sound']}}})
report=obj({'result':{'const':'pass'},'suite':ref,
    'controls':{'type':'array','items':obj({'name':text,'result':{'const':'pass'},'evidence_kind':case['properties']['evidence_kind']})},
    'catalog_audits':{'type':'array','minItems':2,'maxItems':2,'items':audit},
    'selected_successful_fresh_horn_qualifications':natural,'successful_layout_horn_qualifications':{'const':12},
    'selected_successful_applications':{'const':4},'new_fresh_mapped_qualifications':{'const':1},'inherited_unique_controls':{'const':342},
    'new_control_cases':natural,'actual_rich_combined_status':{'enum':['qualified-candidate','unknown-resource']},
    'retained_staged_deadline_refusal':ref,'saved_or_schema_validation_does_not_issue_live_event':{'const':True},
    'measured_profile_only':{'const':True},'author_review':text,'authority_effect':{'const':'none'}})
(HERE/'regression-report.schema.json').write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:relational:v3:regression-report',**report},indent=2)+'\n')
