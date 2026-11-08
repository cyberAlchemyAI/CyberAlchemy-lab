"""Prepare additive resolver postimages only from an actual successful API71 call.

The common successor package remains owned by the integration agent. This
program writes a disjoint delta and never mutates API71 or a shared API cut.
"""
import ast,copy,hashlib,json,os,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
API=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v71-t15-integrated-closure-0001'
SOURCE='c05e64221236ce7e3be16d9560014f0d98e37ad36c82e842ca9934a54a85cbab'
PROFILE='f70913d3c3fbc1189646dcb4cad3dce379a9ca8ad0fdfa5ba4c96e263356611e'
OUT=HERE/'integrated-resolver-delta-0001'
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canon(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def parse(p):return json.loads(p.read_bytes())
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p.read_bytes())}
def write(p,raw):
    p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as s:s.write(raw);s.flush();os.fsync(s.fileno())
def replace(text,a,b):need(a in text,'closed integration anchor absent');return text.replace(a,b)
def main():
    need(not OUT.exists() and sha((API/'source-manifest.json').read_bytes())==SOURCE
         and sha((API/'contract-profile.json').read_bytes())==PROFILE,'exact immutable predecessor required')
    receipt=HERE/'LIVE-NATIVE-AGENT-COLD-API71-0001.json';observed=HERE/'NATIVE-AGENT-COLD-CALL-API71-0002.json'
    submission=parse(receipt);observation=parse(observed)
    need(submission['result']=='PASS' and submission['challenge_submitted'] is True
         and submission['challenge_resolved'] is False and submission['owner_decision'] is None
         and submission['session_closed'] is True and observation['reply_kind']=='result'
         and submission['api_source_binding']['sha256']==observation['api_source_sha256']==SOURCE,
         'actual successful closed native API71 origin required')
    found=[]
    for directory in (Path.home()/'.local/share/cyberalchemy-lab/t22-native-agent-diagnostics').iterdir():
        p=directory/'call-observation.json'
        if directory.is_dir() and not directory.is_symlink() and p.is_file() and sha(p.read_bytes())==sha(canon(observation)):found.append(directory)
    need(len(found)==1,'exact privately retained actual observation required')
    directory=found[0];request=parse(directory/'request.json');candidate=(directory/'candidate.json').read_bytes()
    need(sha(candidate)==submission['fresh_process_cold_journal']['candidate_sha256']
         and request['source_cut']==submission['source_cut']==observation['source_cut'],
         'actual candidate/request/cold journal correspondence differs')
    pins={'native_API_source':SOURCE,'native_submission':sha(canon(submission)),'native_observation':sha(canon(observation)),
          'original_request':sha(canon(request)),'original_candidate':sha(candidate),'original_source_cut':sha(canon(submission['source_cut']))}
    replacements={
      'a38d44c85102b527ad681600b9b585914ac548659aba833b28915c59435fa47c':pins['native_API_source'],
      '2f358e462cace64bf08f0899d0087826087e71f7fbe924f47be0858d3570073b':pins['native_submission'],
      'dede7abdfb0af369761b1bcb8febeab098b9a1e6aa86f2a064e8eb7bd4bcccfe':pins['native_observation'],
      'e087b1ab75226957a7422934a06cc0cfeaaf44898b0f2d95aa1b779496272901':pins['original_request'],
      '4a1a12597dd15b838bf28db0dfaf8ff48a42048f314859883473e2c53b69ab34':pins['original_candidate'],
      'be6891b44f1d31c35db9151829688323e9d7572a8e9bf4917a51e884b77d7475':pins['original_source_cut'],
      'api-integration-v60-t22-pinned-family-source-0001':API.name,
      'ROOT = Path(__file__).resolve().parents[4]':'from .source_bridge import ROOT'}
    for kind in ('source','handler'):
        text=(HERE/('fixture_resolution_'+kind+'_v3.py')).read_text()
        for a,b in replacements.items():text=text.replace(a,b)
        ast.parse(text);write(OUT/('fixture_resolution_'+kind+'.py'),text.encode())
    text=(API/'challenge_resolution.py').read_text().replace('HERE=Path(__file__).resolve().parent','from . import source_bridge as source\nHERE=Path(__file__).resolve().parent')
    text=replace(text,"    version='v6'","    if policy['source_name']==source.CURRENT_LEGACY_NAME and policy['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate':\n        from .fixture_resolution_handler import FixtureResolution,RuleFailure\n        return FixtureResolution,RuleFailure\n    version='v6'")
    write(OUT/'challenge_resolution.py',text.encode())
    text=(API/'auth.py').read_text()
    text=replace(text,"        if resolution:fields+=['resolution_control']","        current_legacy_resolution=resolution and value['source_name']==source.CURRENT_LEGACY_NAME\n        if resolution:fields+=['resolution_control']")
    text=replace(text,"            method=HERE.parent/('challenge-resolution-v6' if reference_resolution else 'challenge-resolution-v3' if integrated else 'challenge-resolution-v1')/'preparation.py'","            method=HERE/'fixture_resolution_handler.py' if current_legacy_resolution else HERE.parent/('challenge-resolution-v6' if reference_resolution else 'challenge-resolution-v3' if integrated else 'challenge-resolution-v1')/'preparation.py'")
    branch="""        elif current_legacy_resolution:
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
"""
    text=replace(text,'        elif metadata:\n',branch);write(OUT/'auth.py',text.encode())
    text=(API/'service.py').read_text()
    text=replace(text,"('agent_challenge_grant.py'","('fixture_resolution_source.py','fixture_resolution_handler.py','agent_challenge_grant.py'")
    anchor='        from .challenge_resolution import implementation\n        ChallengeResolution,_=implementation(self.channel.policy_guard())'
    block="""        from .challenge_resolution import implementation
        if self.channel.policy['source_name']==source.CURRENT_LEGACY_NAME and self.channel.policy['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate':
            from .fixture_resolution_handler import FixtureResolution
            selected=self.channel.policy_guard()['resolution_control'];path=HERE/'source-manifest.json'
            try:
                builder=FixtureResolution(self,selected['routing_binding'],{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})
                builder.preflight(message,outer,key);return builder
            except Exception as error:
                raise ApplicationError('invalid-contract','Exact signed local fixture resolution source or scope refused.') from error
        ChallengeResolution,_=implementation(self.channel.policy_guard())"""
    text=replace(text,anchor,block)
    pattern=r"binding\(str\(\(HERE\.parent/\('challenge-resolution-v6'.*?read_bytes\(\)\)"
    matches=list(re.finditer(pattern,text));need(len(matches)==1,'exact existing resolution method binding required')
    old=matches[0].group();new="(binding(str((HERE/'fixture_resolution_handler.py').relative_to(ROOT)),(HERE/'fixture_resolution_handler.py').read_bytes()) if self.channel.policy['source_name']==source.CURRENT_LEGACY_NAME and self.channel.policy['schema_version']=='lab-local-challenge-resolution-policy/v1-candidate' else "+old+")"
    text=text.replace(old,new);write(OUT/'service.py',text.encode())
    auth=parse(API/'authentication.schema.json');original=next(r for r in auth['oneOf'] if r.get('properties',{}).get('schema_version',{}).get('const')=='lab-local-challenge-resolution-policy/v1-candidate')
    extra=copy.deepcopy(original);extra['properties']['source_name']={'const':'completion-legacy:legacy-local-4636eca980a5d94d'};auth['oneOf'].append(extra)
    write(OUT/'authentication.schema.json',(json.dumps(auth,sort_keys=True,indent=2)+'\n').encode())
    old=ROOT/'product/lab/release-candidates/v1/interface/api-integration-v64-t22-fixture-resolution-0001/schemas/local-fixture-challenge-resolution.schema.json'
    write(OUT/'schemas/local-fixture-challenge-resolution.schema.json',old.read_bytes())
    for p in OUT.glob('*.py'):ast.parse(p.read_bytes())
    result={'schema_version':'lab-actual-native-integrated-resolver-delta/v1-candidate','predecessor_source_binding':bind(API/'source-manifest.json'),
      'predecessor_profile_binding':bind(API/'contract-profile.json'),'native_submission_receipt':bind(receipt),'native_observation_receipt':bind(observed),
      'origin_pins':pins,'postimages':[bind(p) for p in sorted(OUT.rglob('*')) if p.is_file()],
      'required_integration':'Common successor owner rebinds all postimage profile/source/code files and union schema, retains T03/T16 margin/basis deltas and original strict routes. Do not publish these as an independently qualified API package.',
      'fixture_outcome_only':'defer','actual_owner_outcome':None,'authority_effect':'none'}
    write(OUT/'DELTA-PINS.json',(json.dumps(result,sort_keys=True,indent=2)+'\n').encode());print(json.dumps({'result':'PASS-postimages-only','binding':bind(OUT/'DELTA-PINS.json')},sort_keys=True),flush=True)
if __name__=='__main__':main()
