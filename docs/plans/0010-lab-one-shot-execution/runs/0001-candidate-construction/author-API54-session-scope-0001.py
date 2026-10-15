"""Author an exclusive successor; preserve all frozen source and test methods."""
import ast
from pathlib import Path
import shutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v53', BASE / 'api-v54'


def main():
    assert not API.exists()
    shutil.copytree(OLD, API, ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json'))
    lesson = BASE / 'lesson-host-composition-v4'
    checks = BASE / 'api54-package-checks-v1'
    assert not lesson.exists() and not checks.exists()
    shutil.copytree(BASE / 'lesson-host-composition-v3', lesson,
                    ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json'))
    shutil.copytree(BASE / 'api53-package-checks-v1', checks,
                    ignore=shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json'))
    for path, before, after in [(lesson / 'host.py', 'api-v53/service.py', 'api-v54/service.py'),
                                (checks / 'checks.py', "'api-v53'", "'api-v54'"),
                                (API / 'lesson_selection.py', 'lesson-host-composition-v3', 'lesson-host-composition-v4')]:
        text = path.read_text()
        assert before in text
        path.write_text(text.replace(before, after))
    path = API / 'custody_context_sessions.py'
    text = path.read_text()
    before = '''    def open_plan(self,message,outer):
        source.require(outer==message['source_cut'],'Session outer cut differs')
        EL.no_private_memory(message)
        with BOUNDARIES.read_scope(self.source,EL,self.bridge,producer=D,
                                     package_checks=[(D.verify_source,DELIVERY_PIN)]) as snapshot:
            authority=EL.SessionEligibility(snapshot,self.bridge.permission,self.bridge.permission_guard)
            plan=authority.open_plan(message,self.bridge.actor(),self.delivery)
        source.require([r['version_ref'] for r in message['capabilities']]==[R.CAPABILITY+'@'+R.VERSION],'source-reader Session requires its exact selected Agent Capability')
        return plan
'''
    after = '''    def _open_plan(self,message,outer,snapshot,delivery_reader):
        source.require(outer==message['source_cut'],'Session outer cut differs')
        EL.no_private_memory(message)
        source.require(BOUNDARIES.scope_for_source(self.source).snapshot is snapshot,'opening requires its exact current sealed source copy')
        authority=EL.SessionEligibility(snapshot,self.bridge.permission,self.bridge.permission_guard)
        plan=authority.open_plan(message,self.bridge.actor(),delivery_reader)
        source.require([r['version_ref'] for r in message['capabilities']]==[R.CAPABILITY+'@'+R.VERSION],'source-reader Session requires its exact selected Agent Capability')
        return plan
    def open_plan(self,message,outer):
        with BOUNDARIES.read_scope(self.source,EL,self.bridge,producer=D,
                                     package_checks=[(D.verify_source,DELIVERY_PIN)]) as snapshot:
            return self._open_plan(message,outer,snapshot,self.delivery)
'''
    assert before in text
    text = text.replace(before, after)
    before = "    def connections(self,agent,session,classification,proof,request):\n"
    after = "    def connections(self,agent,session,classification,proof,request,*,facts=None):\n        if facts is None:facts=self.source.sources\n        else:source.require(BOUNDARIES.scope_for_source(self.source).snapshot is facts,'connection metadata requires the selected sealed source copy')\n"
    assert before in text
    text = text.replace(before, after)
    text = text.replace("refs[R.PROFILE]=self.source.sources.resolve(R.PROFILE+'@'+R.VERSION)[0].artifact",
                        "refs[R.PROFILE]=facts.resolve(R.PROFILE+'@'+R.VERSION)[0].artifact")
    start = text.index('            # Repeat the entire real preflight after the durable API key claim.')
    end = text.index('            resource=LiveReader', start)
    body = text[start:end]
    body = body.replace('            # Repeat the entire real preflight after the durable API key claim.\n            plan=self.open_plan(message,outer);proof=self.delivery(message[\'context_delivery_binding\'])\n',
        '''            # Revalidate after the claim. Capture the exact delivery that the
            # original eligibility calculation consumed in this pure scope.
            captured=[]
            def delivered(wanted):
                proof=self.delivery(wanted);captured.append(proof);return proof
            plan=self._open_plan(message,outer,snapshot,delivered)
            source.require(len(captured)==1,'opening must consume one exact original delivery')
            proof=captured[0]
''')
    body = body.replace('self.connections(agent,session,classification,proof,request)',
                        'self.connections(agent,session,classification,proof,request,facts=snapshot)')
    text = text[:start] + '''            # Pure metadata only: no live resource, RAM note or durable write.
            with BOUNDARIES.read_scope(self.source,EL,self.bridge,producer=D,
                                         package_checks=[(D.verify_source,DELIVERY_PIN)]) as snapshot:
''' + ''.join('    ' + line if line.strip() else line for line in body.splitlines(keepends=True)) + text[end:]
    text = text.replace('            resource=LiveReader',
        '''            # Scope exit has re-read every original source and current policy.
            # Original permission/clock guards and durable writers run outside it.
            D.FACT_SCOPE.require_outside_scope()
            resource=LiveReader''', 1)
    ast.parse(text)
    path.write_text(text)
    path = API / 'service.py'
    text = path.read_text()
    before = '        self.channel.guard();return result\n    def close(self):'
    after = '''        self.channel.guard()
        if effective<=now():raise ApplicationError('indeterminate','Deadline expired during final verification; inspect the exact recorded operation outcome.')
        return result
    def close(self):'''
    assert before in text
    path.write_text(text.replace(before, after))
    print('API54 Session scope authored; frozen predecessors and inherited methods preserved.', flush=True)


if __name__ == '__main__':
    main()
