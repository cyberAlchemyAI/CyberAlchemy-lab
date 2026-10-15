"""Construct an independently selected typed-reference resolver successor."""
import ast,copy,json,shutil
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v74';API=BASE/'api-v75'
KIND='lab-local-reference-closed-review-policy/v1-candidate'
OLD_KIND='lab-local-challenge-review-policy/v1-candidate'
PURPOSE='durable-metadata-and-exact-reference-closed-review'
def replace(path,old,new):
    value=path.read_text();assert value.count(old)==1,(path,old);path.write_text(value.replace(old,new,1))
def main():
    assert not API.exists() and not (BASE/'lesson-host-composition-v25').exists()
    ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json')
    shutil.copytree(OLD,API,ignore=ignore)
    shutil.copytree(BASE/'lesson-host-composition-v24',BASE/'lesson-host-composition-v25',ignore=ignore)
    replace(BASE/'lesson-host-composition-v25/host.py','api-v74/service.py','api-v75/service.py')
    replace(API/'lesson_selection.py','lesson-host-composition-v24','lesson-host-composition-v25')
    shutil.copyfile(RUN/'API75-carrier_references.py',API/'carrier_references.py')
    shutil.copyfile(RUN/'API75-carrier-reference-check.schema.json',API/'carrier-reference-check.schema.json')
    path=API/'auth.py'
    replace(path,"        workflow=value['schema_version']=='"+OLD_KIND+"'",
        "        references=value['schema_version']=='"+KIND+"'\n        workflow=references or value['schema_version']=='"+OLD_KIND+"'")
    replace(path,"        if workflow:fields+=['composition_control']", "        if workflow:fields+=['composition_control']\n        if references:fields+=['reference_control']")
    replace(path,"'"+OLD_KIND+"')","'"+OLD_KIND+"','"+KIND+"')")
    replace(path,"        if workflow:\n            from .workflow_composition", "        if references:\n            from .carrier_references import validate_control as validate_references\n            validate_references(value)\n        if workflow:\n            from .workflow_composition")
    replace(path,"('durable-metadata-and-exact-challenge-review-composition' if workflow", "('"+PURPOSE+"' if references else 'durable-metadata-and-exact-challenge-review-composition' if workflow")
    path=API/'authentication.schema.json';schema=json.loads(path.read_bytes())
    branch=copy.deepcopy(next(b for b in schema['oneOf'] if b.get('properties',{}).get('schema_version',{}).get('const')==OLD_KIND))
    branch['properties']['schema_version']={'const':KIND};branch['properties']['purpose']={'const':PURPOSE}
    binding={'$ref':'urn:cyberalchemy-lab:protocol:common:v1-candidate#/$defs/binding'}
    carriers=['cal.artifact-type.evidence-set/v1','cal.artifact-type.challenge-event/v1','cal.artifact-type.user-decision-preference/v1']
    branch['properties']['reference_control']={'type':'object','additionalProperties':False,
        'properties':{'resolver_binding':binding,'routing_binding':binding,'supported_carriers':{'type':'array','const':carriers}},
        'required':['resolver_binding','routing_binding','supported_carriers']}
    branch['required'].append('reference_control');schema['oneOf'].append(branch)
    path.write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    for name in ('challenge_submission.py','generated_candidate.py'):
        replace(API/name,"'"+OLD_KIND+"')","'"+OLD_KIND+"','"+KIND+"')")
    path=API/'workflow_composition.py'
    replace(path,"KIND='"+OLD_KIND+"'", "KIND='"+OLD_KIND+"'\nREFERENCE_KIND='"+KIND+"'\nKINDS=(KIND,REFERENCE_KIND)")
    replace(path,"self.host.channel.policy['schema_version']==KIND", "self.host.channel.policy['schema_version'] in KINDS")
    replace(path,"policy['schema_version']!=KIND", "policy['schema_version'] not in KINDS")
    replace(path,'        return SelectedOutputs(self.vault,expected,objects,writer)',
        "        result=SelectedOutputs(self.vault,expected,objects,writer)\n        if policy['schema_version']==REFERENCE_KIND:\n            from .carrier_references import CarrierReferences\n            result.carrier_references=CarrierReferences(self.host,expected)\n        return result")
    path=API/'candidate.py'
    needle="                elif t['category'] not in ('typed-relation','artifact-type','relation-kind'):\n"
    replace(path,needle,"                elif getattr(vault,'carrier_references',None) is not None and t['carrier_ref'] in vault.carrier_references.control['supported_carriers']:\n                    resolved=vault.carrier_references.resolve(t,message,post)\n                    if resolved is None:\n                        check('remaining-domain-reference-'+source.sha(t['version_ref'].encode())[:12],'not-evaluable',{'carrier_ref':t['carrier_ref'],'reason':'Selected resolver does not support this exact scope/state.'},[proposal_binding])\n                        gaps.append(gap(t['version_ref'],'Carrier scope/state needs a separately selected typed resolver.','candidate-semantic-use'))\n                    else:\n                        schema=source.parse((HERE/'carrier-reference-check.schema.json').read_bytes())\n                        Draft202012Validator(schema,registry=self.schemas.registry,format_checker=self.schemas.checker).validate(resolved)\n                        check('selected-carrier-reference-'+source.sha(t['version_ref'].encode())[:12],'pass',resolved,resolved['input_bindings'])\n"+needle)
    replace(API/'service.py',"'workflow-composition.schema.json')", "'workflow-composition.schema.json','carrier_references.py','carrier-reference-check.schema.json')")
    path=API/'workflow_fixture.py';replace(path,'def example(view, schemas):','def example(view, schemas, *, resolve_references=False):')
    replace(path,'        raw = P.compact(policy); path.write_bytes(raw)',
        "        if resolve_references:\n            from .carrier_references import KIND,CARRIERS\n            policy.update(schema_version=KIND,purpose='"+PURPOSE+"',reference_control={\n                'resolver_binding':P.binding(str((Path(__file__).resolve().parent/'carrier_references.py').relative_to(P.ROOT)),(Path(__file__).resolve().parent/'carrier_references.py').read_bytes()),\n                'routing_binding':copy.deepcopy(policy['challenge_control']['routing_binding']),'supported_carriers':list(CARRIERS)})\n        raw = P.compact(policy); path.write_bytes(raw)")
    for path in API.rglob('*.py'):ast.parse(path.read_bytes())
    print(json.dumps({'result':'AUTHORED','version':75,'original_public_contracts':34,
        'authored_handlers':21,'missing_operations':13,'runtime_qualified':False,'authority_effect':'none'}))
if __name__=='__main__':main()
