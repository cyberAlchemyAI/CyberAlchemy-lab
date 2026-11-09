"""Build project-scoped candidate Definition/v1 records from local canonical meanings.

The source catalog remains the task-local normative source. These generated carrier
records are review inputs and do not register or admit Lab definitions.
"""
from pathlib import Path
import hashlib, importlib.util, json, os

ROOT=Path(__file__).resolve().parents[1]
LAB=Path(os.environ.get('CYBERALCHEMY_LAB_ROOT',str(ROOT.parent/'CyberAlchemy-lab')))
TYPE=LAB/'authority/artifact-types/definition/v1'
SOURCE=ROOT/'model/definitions.json'
OUT=ROOT/'model/definition-records'
PRIORITY_IDS={
 'ea.role-profile','ea.target-outcome','ea.construct','ea.case-family','ea.case-version',
 'ea.assessment-session','ea.candidate-response','ea.transcript','ea.rubric','ea.scoring-run',
 'ea.score-report','ea.feedback-metric','ea.product-success-metric','ea.validation-study',
 'ea.claim-tier','ea.consent-record','ea.cohort','ea.decision-policy','ea.criterion-rating',
 'ea.independent-criterion','ea.response-mode','ea.rater','ea.scoring-specification',
 'ea.measurement-uncertainty','ea.calibration-set','ea.validation-holdout','ea.estimand',
 'ea.case-exposure','ea.decision-threshold','ea.analytical-reasoning','ea.creative-reasoning',
 'ea.ingenuity','ea.technical-design-judgment','ea.cooperation-judgment',
 'ea.communication-judgment','ea.high-performing-engineer',
}
CONSUMER_SECTIONS={
 'research-measurement':set(PRIORITY_IDS),
 'case-lifecycle':{'ea.case-generator','ea.item-bank','ea.case-evaluation','ea.scorer-evaluation',
                    'ea.generation-brief','ea.generation-run','ea.case-candidate','ea.mechanism-fingerprint',
                    'ea.similarity-assessment','ea.case-trial','ea.case-review','ea.case-disposition',
                    'ea.case-rule','ea.case-use-case','ea.case-operation','ea.case-workflow'},
 'application-and-custody':{'ea.challenge','ea.invitation','ea.study-protocol','ea.purpose-choice',
                            'ea.assessment-attempt','ea.assignment-manifest','ea.session-assignment',
                            'ea.administration-policy','ea.session-event','ea.media-object','ea.asr-run',
                            'ea.transcript-correction','ea.evidence-span','ea.adjudication','ea.research-export',
                            'ea.rights-request','ea.retention-schedule','ea.audit-event','ea.participant',
                            'ea.identity-vault','ea.notice-version','ea.outbox-job','ea.access-permission',
                            'ea.access-policy','ea.access-decision','ea.exception-grant',
                            'ea.recovery-rule','ea.recovery-decision','ea.upload-attempt',
                            'ea.integration-option-review','ea.integration-verification-contract',
                            'ea.technology-component','ea.integration-binding'},
}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 path.write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')

def build():
 definitions=json.loads(SOURCE.read_text(encoding='utf-8'))['definitions']
 ids=[x['id'] for x in definitions]
 assert len(ids)==len(set(ids))==85
 assert set.union(*CONSUMER_SECTIONS.values())==set(ids)
 assert all(sum(x in g for g in CONSUMER_SECTIONS.values())==1 for x in ids)
 spec=importlib.util.spec_from_file_location('ea_definition_generator',TYPE/'generator.py')
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 source_sha=digest(SOURCE);schema_sha=digest(TYPE/'schema.json');generator_sha=digest(TYPE/'generator.py')
 index=[]
 for i,d in enumerate(definitions):
  did=d['id'];slug=did.removeprefix('ea.');dir=OUT/slug
  group=next(name for name,members in CONSUMER_SECTIONS.items() if did in members)
  priority=did in PRIORITY_IDS
  formal=d.get('formal_expression')
  notation=[{'symbol':key,'meaning':value} for key,value in d.get('notation',{}).items()]
  scope=d['scope'];boundaries=d['boundaries']
  plain=d.get('intuition') or ('In this project, '+d['term']+' refers to the bounded subject described in the scientific voice; its scope and exclusions still control.')
  record={
   'schema_version':'cyberalchemy-lab-definition/v1','definition_id':did,'version':'0.1.0-candidate.1',
   'term':d['term'],'aliases':[],
   'classification':{'artifact_type_ref':'cal.artifact-type.definition/v1','semantic_kind':'definition',
                     'authority_kind':'semantic-authority','lifecycle_posture_ref':'candidate:ea-project-definition-review/v1'},
   'semantic_owner_ref':'role:ea-definitions-owner-unassigned',
   'scope':{'authority_scope_ref':'scope:ea-project-candidate','applicability':scope,
            'exclusions':['Any other product or Lab-wide meaning without separate owner review and admission.']},
   'voices':{
    'scientific_formal':{'normative_statement':d['statement'],'formal_expression':formal,
                         'notation':notation,'boundary_conditions':boundaries,'testable_conditions':[]},
    'plain_language':{'normative':False,'explanation':plain},
    'domain_context':{'normative':False,'workspace_ref':str(ROOT),
                      'explanation':'Candidate '+d['term']+' meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.',
                      'examples':[]}},
   'boundaries':boundaries,
   'source_refs':[{'source_ref':'model/definitions.json','selector':'/definitions/'+str(i),
                   'content_sha256':source_sha,'admission_posture':'candidate-unadmitted','source_admission_ref':None}],
   'primary_consumer_refs':['model/DEFINITIONS.md','model/ontology.json']+
       (['research/full-protocol.md'] if group=='research-measurement' else
        ['software/QUESTION-LIFECYCLE.md'] if group=='case-lifecycle' else ['software/DEFINITION-COVERAGE.md']),
   'index_entry':{'index_ref':'model/definition-records/index.json','entry_id':did},
   'drift_route':{'owner_ref':'role:ea-definitions-owner-unassigned',
                  'audit_ref':'tools/validate_definition_records.py',
                  'challenge_ref':'role:ea-independent-reviewer-unassigned'},
   'source_direction':{'canonical':'definition.json','human_projection':'DEFINITION.md',
                       'projection_policy':'generated-only','generator_ref':'cal.generator.definition-markdown/v1',
                       'generator_sha256':generator_sha},
   'schema_ref':'cal.schema.definition/v1','schema_digest':schema_sha,
   'evidence_refs':[],'residue_refs':[],'typed_relations':[],
   'claim_ceiling':'Generated project-scoped candidate Definition record only. Shape and projection checks grant no Lab admission, semantic truth, implementation, collection or employment-use authority.'}
  write(dir/'definition.json',record)
  (dir/'DEFINITION.md').write_text(module.render(record),encoding='utf-8')
  index.append({'definition_id':did,'term':d['term'],'version':record['version'],
                'group':group,'review_route':'lab-reuse-semantic-review' if priority else 'project-local-semantic-review',
                'record_ref':str((dir/'definition.json').relative_to(ROOT)),
                'projection_ref':str((dir/'DEFINITION.md').relative_to(ROOT)),
                'source_selector':'/definitions/'+str(i),'status':'candidate-unadmitted','authority_effect':'none'})
 write(OUT/'index.json',{'schema_version':'ea.definition-record-index/v1','status':'candidate-unadmitted',
                         'authority_effect':'none','source_ref':'model/definitions.json',
                         'source_sha256':source_sha,'artifact_type_ref':'cal.artifact-type.definition/v1',
                         'review_rule':'Lab-reuse is a semantic review queue, not admission or a claim of cross-project applicability.',
                         'count':len(index),'records':index})
 print(f'Built {len(index)} candidate Definition/v1 records ({len(PRIORITY_IDS)} Lab-reuse review, {len(index)-len(PRIORITY_IDS)} project-local review)')
if __name__=='__main__':build()
