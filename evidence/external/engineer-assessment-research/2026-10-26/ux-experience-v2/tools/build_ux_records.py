"""Generate six candidate carriers and source-bound UX instance records."""
from pathlib import Path
import hashlib, json
from build_integration_records import ROOT, LAB, carrier, write, sha

SOURCE=ROOT/'design/source.json'; OUT=ROOT/'design/records'
ALTERNATIVES={
 'brand-identity':[('cal.artifact-type.product/v1','Product identity is not the audience-facing promise, voice and claim guardrails.'),('cal.artifact-type.policy/v2','An issued policy has authority effects; this is candidate expression guidance.')],
 'design-system':[('cal.artifact-type.schema/v1','Schema constrains representation; it does not own tokens and interaction conventions.'),('cal.artifact-type.implementation/v1','Implementation records realized behavior; this is a pre-implementation contract.')],
 'experience-flow':[('cal.artifact-type.experiment-design/v1','A study design tests a hypothesis; a flow specifies user actions and visible states.'),('cal.artifact-type.implementation/v1','No realized interface is claimed.')],
 'interface-screen':[('cal.artifact-type.schema/v1','A data schema cannot carry copy, visible states, actions and accessibility behavior.'),('cal.artifact-type.implementation/v1','A screen spec precedes an implemented screen.')],
 'ui-component':[('cal.artifact-type.schema/v1','A schema cannot carry keyboard, focus, error and contextual component behavior.'),('cal.artifact-type.implementation/v1','This is a candidate reusable design contract, not a deployed component.')],
 'analytics-event-spec':[('cal.artifact-type.operational-observation/v1','An operational observation is an occurrence; this specifies a future event allowlist.'),('cal.artifact-type.schema/v1','A schema alone omits purpose, emitter, deduplication, retention and metric consumers.')]
}

def field_schema(v):
    if isinstance(v,str):return {'type':'string','minLength':1}
    if isinstance(v,list):return {'type':'array','items':{'type':'string','minLength':1}}
    raise TypeError(v)

def main():
    src=json.loads(SOURCE.read_text()); assert src['authority_effect']=='none'
    allrefs=[]; counts={}; source_hash=sha(SOURCE.read_bytes())
    for family,rows in src['families'].items():
        assert rows and family in ALTERNATIVES
        definition='ea.'+family
        sample=rows[0]
        assert all(set(r)==set(sample) for r in rows),family
        rowprops={k:field_schema(v) for k,v in sample.items()}
        row_schema={'type':'object','additionalProperties':False,'required':list(sample),'properties':rowprops}
        prefix={'schema_version':{'const':f'ea.{family}/v1-candidate'},
                'artifact_type_ref':{'const':f'ea.artifact-type.{family}/v1-candidate'},
                'record_id':{'type':'string','minLength':1},'version':{'const':'0.1.0-candidate.1'},
                'status':{'const':'candidate-unadmitted'},'authority_effect':{'const':'none'},
                'source_ref':{'const':'design/source.json'},
                'source_sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'},
                'source_index':{'type':'integer','minimum':0},
                'source_excerpt_sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'},
                'owner_ref':{'type':'string','minLength':1},
                'challenge_route':{'type':'string','minLength':1},
                'source_row':row_schema,
                'claim_ceiling':{'type':'string','minLength':1}}
        base=ROOT/'model/carriers'/family/'v1'
        write(base/'schema.json',{'$schema':'https://json-schema.org/draft/2020-12/schema',
             'type':'object','additionalProperties':False,'required':list(prefix),'properties':prefix})
        carrier(family,definition,f'Preserve one versioned {family} contract with exact source row, owner and review route.',ALTERNATIVES[family])
        counts[family]=len(rows)
        for i,row in enumerate(rows):
            rec={'schema_version':f'ea.{family}/v1-candidate','artifact_type_ref':f'ea.artifact-type.{family}/v1-candidate',
                 'record_id':row['id'],'version':'0.1.0-candidate.1','status':'candidate-unadmitted','authority_effect':'none',
                 'source_ref':'design/source.json','source_sha256':source_hash,'source_index':i,
                 'source_excerpt_sha256':hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),
                 'owner_ref':'role:ea-product-design-owner-unassigned',
                 'challenge_route':'role:ea-independent-ux-reviewer-unassigned',
                 'source_row':row,
                 'claim_ceiling':'Candidate design contract only; no type admission, browser validation, participant comprehension evidence, active telemetry or release.'}
            path=OUT/row['id']/'record.json';write(path,rec)
            (path.parent/'RECORD.md').write_text(f'# {row["title"]}\n\nCandidate {family} record from [source.json](../../source.json). See [record.json](record.json) for exact content and source digest.\n',encoding='utf-8')
            allrefs.append(str(path.relative_to(ROOT)))
    write(ROOT/'design/index.json',{'schema_version':'ea.ux-record-index/v1','status':'candidate-unadmitted',
        'authority_effect':'none','source_ref':'design/source.json','source_sha256':source_hash,
        'count':len(allrefs),'counts':counts,'record_refs':allrefs,
        'type_request_refs':[f'model/carriers/{f}/v1/request.json' for f in counts]})
    print('Built',len(allrefs),'candidate UX records and',len(counts),'Artifact Type Requests')

if __name__=='__main__':main()
