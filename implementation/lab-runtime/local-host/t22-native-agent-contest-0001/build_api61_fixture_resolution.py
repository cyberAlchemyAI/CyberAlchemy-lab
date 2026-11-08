"""Build an additive native fixture-resolution API cut without changing API60."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-integration-v60-t22-pinned-family-source-0001'
NEW=BASE/'api-integration-v61-t22-fixture-resolution-0001'
SOURCE='a38d44c85102b527ad681600b9b585914ac548659aba833b28915c59435fa47c'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rel(path):return path.relative_to(ROOT).as_posix()
def save(path,value):path.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
def main():
 if sha(OLD/'source-manifest.json')!=SOURCE or NEW.exists():raise ValueError('exact predecessor and disjoint output required')
 source=json.loads((OLD/'source-manifest.json').read_bytes());profile=json.loads((OLD/'contract-profile.json').read_bytes())
 prefix=rel(OLD)+'/'
 NEW.mkdir(mode=0o700)
 for row in source['files']:
  if row['path'].startswith(prefix):
   leaf=row['path'][len(prefix):];target=NEW/leaf;target.parent.mkdir(parents=True,exist_ok=True)
   if sha(ROOT/row['path'])!=row['sha256']:raise ValueError('predecessor file changed')
   shutil.copy2(ROOT/row['path'],target)
 for name in ['fixture_resolution_source.py','fixture_resolution_handler.py']:
  raw=(HERE/name).read_text().replace('ROOT = Path(__file__).resolve().parents[4]','from .source_bridge import ROOT')
  (NEW/name).write_text(raw)
 p=NEW/'challenge_resolution.py';text=p.read_text().replace("    version='v6'", "    if policy['source_name'].startswith('completion-legacy:') and policy['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate':\n        from .fixture_resolution_handler import FixtureResolution,RuleFailure\n        return FixtureResolution,RuleFailure\n    version='v6'");p.write_text(text)
 p=NEW/'auth.py';text=p.read_text()
 text=text.replace("        if resolution:fields+=['resolution_control']", "        current_legacy_resolution=resolution and value['source_name']==source.CURRENT_LEGACY_NAME\n        if resolution:fields+=['resolution_control']")
 text=text.replace("            method=HERE.parent/('challenge-resolution-v6' if reference_resolution else 'challenge-resolution-v3' if integrated else 'challenge-resolution-v1')/'preparation.py'", "            method=HERE/'fixture_resolution_handler.py' if current_legacy_resolution else HERE.parent/('challenge-resolution-v6' if reference_resolution else 'challenge-resolution-v3' if integrated else 'challenge-resolution-v1')/'preparation.py'")
 text=text.replace("        elif metadata:\n", """        elif current_legacy_resolution:
            d=selected_delivery
            source.require(check_source and d is not None and control is None
                and value['scope_control'] is None
                and value['purpose']=='durable-metadata-and-exact-challenge-resolution'
                and value['principal_ref'] not in (d.records.PRINCIPAL,'principal:R03-fresh-reader'),
                'independent fixture resolution principal and current source required')
            period=d.load(d.reader.HERE/'packages/0001/period.json')
            source.require(instant(period['not_before'])<=now()<instant(value['expires_at'])<=instant(period['expires_at']),
                'fixture resolution grant exceeds signed source period')
            authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
            source.require(value['development_authorization_binding']==binding(str(authority.relative_to(ROOT)),authority.read_bytes()),
                'fixture resolution technical authorization differs')
        elif metadata:
""")
 p.write_text(text)
 p=NEW/'service.py';text=p.read_text()
 text=text.replace("'agent_challenge_grant.py','protocol.py'", "'fixture_resolution_source.py','fixture_resolution_handler.py','agent_challenge_grant.py','protocol.py'")
 text=text.replace("        from .challenge_resolution import implementation\n        ChallengeResolution,_=implementation(self.channel.policy_guard())", """        from .challenge_resolution import implementation
        if self.channel.policy['source_name']==source.CURRENT_LEGACY_NAME and self.channel.policy['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate':
            from .fixture_resolution_handler import FixtureResolution
            selected=self.channel.policy_guard()['resolution_control']
            path=HERE/'source-manifest.json'
            try:
                builder=FixtureResolution(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
                builder.preflight(message,outer,key);return builder
            except Exception as error:
                raise ApplicationError('invalid-contract','Exact signed local fixture resolution source or scope refused.') from error
        ChallengeResolution,_=implementation(self.channel.policy_guard())""")
 old="binding(str((HERE.parent/('challenge-resolution-v6' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v3-candidate' else 'challenge-resolution-v3' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v2-candidate' else 'challenge-resolution-v1')/'preparation.py').relative_to(ROOT)),(HERE.parent/('challenge-resolution-v6' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v3-candidate' else 'challenge-resolution-v3' if self.channel.policy['schema_version']=='lab-local-integrated-challenge-resolution-policy/v2-candidate' else 'challenge-resolution-v1')/'preparation.py').read_bytes())"
 new="binding(str((HERE/'fixture_resolution_handler.py').relative_to(ROOT)),(HERE/'fixture_resolution_handler.py').read_bytes()) if self.channel.policy['source_name']==source.CURRENT_LEGACY_NAME and self.channel.policy['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate' else "+old
 # Parenthesize the special handler selection to preserve the outer operation ternary.
 if old not in text:raise ValueError('handler binding anchor differs')
 text=text.replace(old,'('+new+')');p.write_text(text)
 p=NEW/'authentication.schema.json';auth=json.loads(p.read_bytes())
 original=next(r for r in auth['oneOf'] if r.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-challenge-resolution-policy/v1-candidate')
 extra=copy.deepcopy(original);extra['properties']['source_name']={'const':'completion-legacy:legacy-local-d3537e8c3cb77a71'}
 auth['oneOf'].append(extra);save(p,auth)
 # An explicit additive local-fixture request variant leaves original requests intact.
 request=json.loads((ROOT/'docs/proposals/0007-lab-integrated-schema-package/schemas/challenge-resolution.schema.json').read_bytes())
 local=copy.deepcopy(request);local.pop('$id');local['properties']['schema_version']={'const':'lab-local-fixture-challenge-resolution/v1-candidate'}
 local['properties']['resolution_decision']['allOf'][1]['properties']['carrier_ref']['const']='cal.artifact-type.decision/v1'
 for row in local['properties'].values():
  pass
 def remap(value):
  if isinstance(value,dict):
   for k,v in value.items():
    if k=='$ref' and isinstance(v,str) and v.startswith('urn:cyberalchemy-lab:protocol:common:v1-candidate'):
     value[k]=v.replace('urn:cyberalchemy-lab:protocol:common:v1-candidate','urn:cyberalchemy-lab:source8-protocol:protocol:common:v1-candidate:revision-2')
    else:remap(v)
  elif isinstance(value,list):
   for v in value:remap(v)
 remap(local)
 original_ref={'$ref':'urn:cyberalchemy-lab:protocol:challenge-resolution:v1-candidate'}
 combined={'$id':'urn:cyberalchemy-lab:source8-protocol:protocol:challenge-resolution:v1-candidate:revision-2',
  '$schema':'https://json-schema.org/draft/2020-12/schema','anyOf':[original_ref,local]}
 save(NEW/'schemas/local-fixture-challenge-resolution.schema.json',combined)
 for p in NEW.glob('*.py'):compile(p.read_text(),str(p),'exec')
 def rebind(row):
  if row['path'].startswith(prefix):
   path=NEW/row['path'][len(prefix):];return {'path':rel(path),'sha256':sha(path)}
  return row
 profile['files']=[rebind(r) for r in profile['files']]
 additions=[NEW/'fixture_resolution_source.py',NEW/'fixture_resolution_handler.py',NEW/'schemas/local-fixture-challenge-resolution.schema.json']
 profile['files']+= [{'path':rel(p),'sha256':sha(p)} for p in additions]
 profile['files']=sorted(profile['files'],key=lambda r:r['path'])
 profile['integration_members_binding']={'path':rel(NEW/'integration-members.json'),'sha256':sha(NEW/'integration-members.json')}
 profile['claim_ceiling']='Additive local fixture Agent contest deferred-consequence preparation. Exact native submission lineage; no actual owner outcome, repository admission or activation.'
 save(NEW/'contract-profile.json',profile)
 source['files']=[rebind(r) for r in source['files']]
 source['files'] +=[{'path':rel(p),'sha256':sha(p)} for p in additions]
 source['files']=sorted(source['files'],key=lambda r:r['path'])
 source['profile_binding']={'path':rel(NEW/'contract-profile.json'),'sha256':sha(NEW/'contract-profile.json')}
 for r in source['files']:
  if r['path']==source['profile_binding']['path']:r['sha256']=source['profile_binding']['sha256']
 source['predecessor_source_manifest_binding']={'path':rel(OLD/'source-manifest.json'),'sha256':SOURCE}
 source['claim_ceiling']=profile['claim_ceiling'];save(NEW/'source-manifest.json',source)
 receipt={'schema_version':'lab-T22-local-fixture-resolution-source-rebind/v1',
  'successor_package':rel(NEW),'successor_manifest_sha256':sha(NEW/'source-manifest.json'),
  'successor_profile_sha256':sha(NEW/'contract-profile.json'),'authority_effect':'none'}
 save(NEW/'rebind-receipt.json',receipt);print(json.dumps(receipt,sort_keys=True))
if __name__=='__main__':main()
