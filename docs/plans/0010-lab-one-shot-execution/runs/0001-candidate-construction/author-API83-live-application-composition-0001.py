"""Repair application authentication and future identity binding in a successor."""
import ast
import copy
import json
import shutil
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD = BASE / 'api-v82'
API = BASE / 'api-v83'
KIND = 'lab-local-lesson-application-policy/v2-candidate'


def replace(path, before, after):
    text = path.read_text()
    assert text.count(before) == 1, (path, before)
    path.write_text(text.replace(before, after, 1))


def main():
    assert not API.exists() and not (BASE / 'lesson-application-v2').exists()
    assert not (BASE / 'lesson-host-composition-v33').exists()
    ignore = shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json')
    shutil.copytree(OLD, API, ignore=ignore)
    shutil.copytree(BASE / 'lesson-application-v1', BASE / 'lesson-application-v2', ignore=ignore)
    shutil.copytree(BASE / 'lesson-host-composition-v32', BASE / 'lesson-host-composition-v33', ignore=ignore)
    replace(BASE / 'lesson-host-composition-v33/host.py', 'api-v82/service.py', 'api-v83/service.py')
    replace(API / 'lesson_selection.py', 'lesson-host-composition-v32', 'lesson-host-composition-v33')
    replace(API / 'lesson_application.py', 'lesson-application-v1', 'lesson-application-v2')
    replace(BASE / 'lesson-application-v2/preparation.py',
            "KIND = 'lab-local-lesson-application-policy/v1-candidate'", "KIND = '" + KIND + "'")
    replace(BASE / 'lesson-application-v2/preparation.py',
            "        resource, session = self.live(message['session_ref'])",
            "        require(message['session_ref'] == policy['application_control']['runtime_identities']['session_ref'], 'application must use the independently selected one-use Session identity')\n        resource, session = self.live(message['session_ref'])")
    replace(API / 'protocol.py', "APPLICATION_SUPPORTED=METADATA_SUPPORTED+('lesson.apply',)",
            "APPLICATION_SUPPORTED=METADATA_SUPPORTED+('lesson.apply',)\nAPPLICATION_SESSION_SUPPORTED=LEGACY_SUPPORTED+('lesson.apply',)")
    auth = API / 'auth.py'
    replace(auth, "        application=value['schema_version']=='lab-local-lesson-application-policy/v1-candidate'",
            "        application_session=value['schema_version']=='" + KIND + "'\n        application=application_session or value['schema_version']=='lab-local-lesson-application-policy/v1-candidate'")
    replace(auth, 'metadata=application or assessment', 'metadata=(application and not application_session) or assessment')
    replace(auth, "        if application:fields+=['application_control']",
            "        if application:fields+=['application_control']\n        if application_session:fields+=['purpose','development_authorization_binding']")
    replace(auth, "'lab-local-lesson-application-policy/v1-candidate')",
            "'lab-local-lesson-application-policy/v1-candidate','" + KIND + "')")
    replace(auth, 'list(APPLICATION_SUPPORTED if application else',
            'list(APPLICATION_SESSION_SUPPORTED if application_session else APPLICATION_SUPPORTED if application else')
    replace(auth, "            method=HERE.parent/'lesson-application-v1/preparation.py'",
            "            method=HERE.parent/('lesson-application-v2' if application_session else 'lesson-application-v1')/'preparation.py'")
    replace(auth, "        if failure:\n            from .workspace import read_private",
            "        if application_session:\n            authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'\n            source.require(value['source_name']=='custody-participation' and value['session_control'] is not None\n                and value['purpose']=='current-participation-and-exact-lesson-application'\n                and value['development_authorization_binding']==binding(str(authority.relative_to(ROOT)),authority.read_bytes()),\n                'application requires original participation plus exact development authorization')\n        if failure:\n            from .workspace import read_private")
    path = API / 'authentication.schema.json'
    schema = json.loads(path.read_bytes())
    old_branch = next(b for b in schema['oneOf'] if b.get('properties', {}).get('schema_version', {}).get('const') == 'lab-local-lesson-application-policy/v1-candidate')
    parent_branch = next(b for b in schema['oneOf'] if b.get('properties', {}).get('schema_version', {}).get('const') == 'lab-local-candidate-policy/v4-candidate')
    branch = copy.deepcopy(old_branch)
    branch['properties']['schema_version'] = {'const': KIND}
    branch['properties']['purpose'] = {'const': 'current-participation-and-exact-lesson-application'}
    branch['properties']['allowed_operations']['const'] = [
        'lab.status','catalog.get','artifact.inspect','artifact.query','change.prepare','change.validate',
        'operation.inspect','context.get','session.open','session.close','session.inspect','projection.refresh','lesson.apply']
    branch['properties']['source_name'] = {'const': 'custody-participation'}
    branch['properties']['session_control'] = copy.deepcopy(next(item for item in parent_branch['properties']['session_control']['anyOf'] if item.get('type') == 'object'))
    branch['properties'].pop('scope_control')
    branch['required'].remove('scope_control')
    control = branch['properties']['application_control']
    control['properties']['runtime_identities'] = {
        'type': 'object', 'additionalProperties': False,
        'required': ['session_ref', 'agent_instance_ref'],
        'properties': {
            'session_ref': {'type': 'string', 'pattern': '^agent-session:R03-live:[a-f0-9]{32}$'},
            'agent_instance_ref': {'type': 'string', 'pattern': '^agent-instance:R03-live:[a-f0-9]{32}$'}}}
    control['required'].append('runtime_identities')
    schema['oneOf'].append(branch)
    path.write_text(json.dumps(schema, indent=2, sort_keys=True) + '\n')
    path = API / 'custody_context_sessions.py'
    replace(path, '    def open(self,message,request,outer,raw,plan):',
            "    def allocate_runtime_identities(self):\n        policy=self.channel.policy_guard()\n        if policy['schema_version']!='" + KIND + "':\n            return 'agent-session:R03-live:'+uuid.uuid4().hex,'agent-instance:R03-live:'+uuid.uuid4().hex\n        selected=policy['application_control']['runtime_identities']\n        sid,aid=selected['session_ref'],selected['agent_instance_ref']\n        # Durable identity metadata prevents reuse; it cannot restore RAM.\n        rows=self.history()\n        source.require(sid not in rows and all(events[0][0]['agent_instance_ref']!=aid for events in rows.values())\n            and sid not in self.live,'application Session identity already used; new private policy identities required')\n        source.require(re.fullmatch('agent-session:R03-live:[a-f0-9]{32}',sid)\n            and re.fullmatch('agent-instance:R03-live:[a-f0-9]{32}',aid),'closed private runtime identities required')\n        return sid,aid\n    def reserve_runtime_identities(self,sid,aid,request):\n        D.FACT_SCOPE.require_outside_scope()\n        policy=self.channel.policy_guard()\n        if policy['schema_version']!='" + KIND + "':return\n        source.require(policy['application_control']['runtime_identities']=={'session_ref':sid,'agent_instance_ref':aid},'private runtime identity selection differs')\n        paths=[self.directory/('runtime-identity-'+ref.replace(':','_')+'.json') for ref in (sid,aid)]\n        source.require(all(not path.exists() for path in paths),'runtime identity previously reserved; pending operations require inspection')\n        raw=source.encoded({'schema_version':'lab-private-runtime-identity-reservation/v1-candidate','session_ref':sid,'agent_instance_ref':aid,'opening_request_binding':request,'authority_effect':'none','memory_persistence_allowed':False})\n        for path in paths:atomic(path,raw)\n        self.channel.guard()\n    def open(self,message,request,outer,raw,plan):")
    replace(path, "                identity=uuid.uuid4().hex;sid='agent-session:R03-live:'+identity;aid='agent-instance:R03-live:'+uuid.uuid4().hex",
            '                sid,aid=self.allocate_runtime_identities()')
    replace(path, '            resource=LiveReader(self.source,self.bridge,plan,proof,agent,session,classification)',
            '            self.reserve_runtime_identities(sid,aid,request)\n            resource=LiveReader(self.source,self.bridge,plan,proof,agent,session,classification)')
    # The original declaration and all inherited assertions remain unchanged.
    for path in API.rglob('*.py'):
        ast.parse(path.read_text())
    print(json.dumps({'result': 'AUTHORED', 'authored_handlers': 23, 'remaining_handlers': 11,
                      'runtime_qualified': False, 'authority_effect': 'none'}), flush=True)


if __name__ == '__main__':
    main()
