"""Build explicit static projection metadata; source fidelity remains pending."""
import json
import sys
from pathlib import Path
UNIT=Path(__file__).resolve().parent;ROOT=UNIT.parents[6];BASE=UNIT.parent.parent
IMPL=ROOT/'craft/formalization/candidates/definition-assurance-v1';sys.path[:0]=[str(IMPL),str(BASE/'units/A07')]
import ir
import obligations as o
import pilot_spec as p

SCOPE='scope:governance-record-projection-v2'
OWNERS={'Traceable':'provenance','Position':'authority','Right':'authority','Duty':'responsibility','BackedRight':'authority-claim'}


def put(name,value):
    path=UNIT/name
    with path.open('x') as stream:json.dump(value,stream,indent=2,sort_keys=True);stream.write('\n')
    return {'path':path.relative_to(ROOT).as_posix(),'sha256':p.r.digest(path.read_bytes())}


def main():
    spec_path=BASE/'pilot-v2/interpretation.json';spec=json.loads(spec_path.read_text());p.bind_sources(spec);sources={row['definition_id'].split('cal.definition.')[1]:row for row in spec['sources']};irs=[];input_refs=[];maps=[];map_refs=[]
    anchor=sources['provenance']
    for name,source in sources.items():
        document=json.loads((ROOT/source['path']).read_text());norm=document['voices']['scientific_formal']['normative_statement']
        core={'interpretation_id':'projection:'+source['definition_id'],'source':source,'scope':SCOPE,'declarations':[{'kind':'sort','symbol_id':'Record','scope':SCOPE,'domain_policy':'nonempty'}]+[{'kind':'predicate','symbol_id':key,'scope':SCOPE,'argument_sorts':['Record']} for key,owner in OWNERS.items() if owner==name],'clauses':[{'clause_id':'source-normative-pending','source_selector':'/voices/scientific_formal/normative_statement','excerpt_sha256':p.r.digest(norm.encode()),'start_character':0,'disposition':'deferred','forms':['operational'],'roles':['definition'] if name!='governance-axis-independence-invariant' else ['proof-obligation'],'formal_statement':None,'rationale':'Opaque unary projection of selected A07 record predicates. No whole-source lowering or full deontic/temporal interpretation is claimed.'}],'depends_on':[],'relations':[],'assumptions':[],'populations':[],'logic_features':['first-order'],'semantic_status':'candidate','source_fidelity':'pending','profile_ref':'profile:record-projection-v2'}
        value=ir.compile_interpretation(core);irs.append(value);input_refs.append(put(name+'-projection-ir.json',value))
        if name!='provenance':
            doc={'schema_version':'definition-assurance-carrier-alignment/v1-candidate','authority_effect':'none','mapping_kind':'identity-shared-carrier','carrier':'Record','scope':SCOPE,'left_source':anchor,'right_source':source,'reviewer_ref':'agent:Codex','review_basis':'Explicit same hypothetical object identity carrier for this candidate record projection only; predicate identity and owner source remain distinct.','equivalence_claim':'none'}
            ref=put(name+'-carrier.json',doc);maps.append(doc);map_refs.append(ref)
    composed=ir.compose(irs,map_refs,ROOT);subject_ref=put('composed-projection-ir.json',composed)
    ids={key:ir.qualified(sources[owner],SCOPE,key) for key,owner in OWNERS.items()};sort=composed['sort_alignment'][ir.qualified(anchor,SCOPE,'Record')];ids['Record']=sort
    bindings={name:{'source':sources[owner],'scope':SCOPE,'predicate':name,'carrier':'Record'} for name,owner in OWNERS.items()}
    populations=[{'population_id':'POP-'+name,'carrier':'Record','predicate_ref':name,'requirement':'required','statement':o.p.quant('exists','Record',o.p.pred(name)),'scope':SCOPE,'rationale':'Required hypothetical population in this selected record projection; not an assertion about real grants or duties.','review_ref':None} for name in OWNERS]
    requests=[]
    for name in ['Position','BackedRight']:
        owner=OWNERS[name];ref=next(ref for doc,ref in zip(maps,map_refs) if doc['right_source']==sources[owner]);relation={'relation_id':'TRACE-'+name,'left_definition':anchor,'right_definition':sources[owner],'relation_class':'overlap-distinct','direction':'forward','scope':SCOPE,'alignment':{'status':'reviewed','map_ref':ref},'required_statements':[],'minimum_strength':'model-witness'}
        requests.append({'relation':relation,'bindings':{'left':bindings['Traceable'],'right':bindings[name]},'proper':False,'distinction':'permitted','forbidden':[]})
    pred=o.p.pred;quant=o.p.quant
    union={'op':'iff','left':pred('Position'),'right':{'op':'or','args':[pred('Right'),pred('Duty')]}}
    backing={'op':'implies','left':pred('BackedRight'),'right':pred('Right')}
    theory={'theory_id':'T_RECORD_PROJECTION_V2','sources':spec['sources'],'declarations':[{'kind':'sort','symbol_id':'Record','scope':SCOPE,'domain_policy':'nonempty'}]+[{'kind':'predicate','symbol_id':name,'scope':SCOPE,'argument_sorts':['Record']} for name in OWNERS],'statements':[quant('forall','Record',union),quant('forall','Record',backing)],'assumption_set_id':'CTX_RECORDS_HYPOTHETICAL_V2','scope':SCOPE,'change_class':'initial','prior_theory_ref':None}
    required=o.generate(theory,requests,populations,bindings,ROOT)
    config={'schema_version':'definition-assurance-record-projection/v2-candidate','authority_effect':'none','semantic_ready':False,'source_spec_ref':{'path':spec_path.relative_to(ROOT).as_posix(),'sha256':p.r.digest(spec_path.read_bytes())},'subject_ref':subject_ref,'input_ir_refs':input_refs,'alignment_refs':map_refs,'theory_ref':put('projection-theory.json',theory),'relations_ref':put('projection-relations.json',requests),'populations_ref':put('projection-populations.json',populations),'endpoint_bindings_ref':put('projection-endpoints.json',bindings),'required_set_ref':put('projection-required-set.json',required),'symbol_mapping':ids,'sources':spec['sources'],'semantics_contract_ref':{'path':(BASE/'units/A07/SEMANTICS.md').relative_to(ROOT).as_posix(),'sha256':p.r.digest((BASE/'units/A07/SEMANTICS.md').read_bytes())},'claim_ceiling':'Source-qualified abstract unary projection of selected conditional record predicates only; no whole-definition, generic lowering correctness, deontic fulfillment or temporal theorem.'}
    put('projection.json',config);print(json.dumps({'result':'candidate-projection-produced','source_IRs':7,'carrier_maps':len(map_refs),'logical_queries':len(required['logical_manifest']['obligations']),'required_gates':len(required['administrative_and_semantic_gates']),'semantic_ready':False}))


if __name__=='__main__':main()
