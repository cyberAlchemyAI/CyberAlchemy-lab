"""Create an immutable successor for discoverable pending validation evidence."""
from pathlib import Path
import ast
import shutil

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[4]
BASE = ROOT / 'product/lab/release-candidates/v1/interface'
OLD, API = BASE / 'api-v56', BASE / 'api-v57'
COMPOSITION = BASE / 'classification-preparation-v9'
CHECK = BASE / 'api57-classification-checks-v1'


def replace(path, before, after):
    text = path.read_text()
    assert text.count(before) == 1, (path, before)
    path.write_text(text.replace(before, after, 1))


def main():
    for target in (API, COMPOSITION, CHECK, BASE / 'lesson-host-composition-v7'):
        assert not target.exists(), target
    ignore = shutil.ignore_patterns('receipts', '__pycache__', 'source-manifest.json', 'contract-profile.json')
    shutil.copytree(OLD, API, ignore=ignore)
    shutil.copytree(BASE / 'classification-preparation-v8', COMPOSITION, ignore=ignore)
    shutil.copytree(BASE / 'lesson-host-composition-v6', BASE / 'lesson-host-composition-v7', ignore=ignore)
    replace(BASE / 'lesson-host-composition-v7/host.py', 'api-v56/service.py', 'api-v57/service.py')
    replace(API / 'lesson_selection.py', 'lesson-host-composition-v6', 'lesson-host-composition-v7')
    path = API / 'classification_preparation.py'
    path.write_text(path.read_text().replace('classification-preparation-v8', 'classification-preparation-v9')
                    .replace('classification_preparation_v8', 'classification_preparation_v9')
                    + '\nPendingValidationRefusal = selected.PendingValidationRefusal\n')
    replace(COMPOSITION / 'preparation.py',
        '''    pass


class ClassificationPreparation:''',
        '''    def __init__(self, message, evidence):
        super().__init__(message)
        self.evidence = copy.deepcopy(evidence)


class ClassificationPreparation:''')
    replace(COMPOSITION / 'preparation.py',
        "raise PendingValidationRefusal('classification prospective schema/core closure failed; retained native verification report, operation remains pending')",
        "raise PendingValidationRefusal('classification prospective schema/core closure failed; retained native verification report, operation remains pending', details['evidence'])")
    replace(API / 'service.py', 'from .classification_preparation import ClassificationPreparation, RuleFailure',
        'from .classification_preparation import ClassificationPreparation, RuleFailure, PendingValidationRefusal')
    replace(API / 'service.py',
        "                    except RuleFailure as error:\n",
        '''                    except PendingValidationRefusal as error:
                        from .guarded_candidate import selection
                        with selection(self):
                            self.channel.guard();self.schemas.guard()
                            source.require(self.handlers.current(),'classification source changed before recording pending native evidence')
                            for item in error.evidence:self.vault.object_read(item)
                        self.vault.record_pending_evidence(namespace,error.evidence)
                        raise ApplicationError('indeterminate','Native validation refused incomplete stable cores. Retained verification evidence is available through operation.inspect; reconciliation is required.')
                    except RuleFailure as error:
''')
    replace(API / 'workspace.py', '    def lookup(self,lookup,context):\n',
        '''    def record_pending_evidence(self,ns,evidence):
        # Evidence is an observation, never a completion or permission to retry.
        source.require(type(evidence) is list and 0<len(evidence)<=128,'bounded pending verification evidence required')
        with self.lock():
            claim,result=self.state(ns)
            source.require(claim is not None and result is None
                and claim['principal_ref']==self.channel.context['principal_ref'], 'pending operation owner or state differs')
            for item in evidence:
                source.require(type(item) is dict and set(item)=={'ref','sha256'},'closed pending evidence binding required')
                self.object_read(item)
            claimraw=read_private(self.root/'journal'/(ns+'.claim.json'))
            row={'schema_version':'lab-private-pending-evidence/v1-candidate',
                 'claim_sha256':source.sha(claimraw),'evidence_bindings':evidence,'authority_effect':'none'}
            atomic(self.root/'journal'/(ns+'.pending-evidence.json'),source.encoded(row))
    def pending_evidence(self,ns):
        with self.lock():
            claim,result=self.state(ns)
            source.require(claim is not None and result is None
                and claim['principal_ref']==self.channel.context['principal_ref'],'pending operation owner or state differs')
            path=self.root/'journal'/(ns+'.pending-evidence.json')
            if not path.exists():return []
            row=source.parse(read_private(path))
            claimraw=read_private(self.root/'journal'/(ns+'.claim.json'))
            source.require(type(row) is dict and set(row)=={'schema_version','claim_sha256','evidence_bindings','authority_effect'}
                and row['schema_version']=='lab-private-pending-evidence/v1-candidate'
                and row['claim_sha256']==source.sha(claimraw) and row['authority_effect']=='none'
                and type(row['evidence_bindings']) is list and 0<len(row['evidence_bindings'])<=128,'pending evidence claim binding differs')
            for item in row['evidence_bindings']:
                source.require(type(item) is dict and set(item)=={'ref','sha256'},'closed pending evidence binding required')
                self.object_read(item)
            return row['evidence_bindings']
    def lookup(self,lookup,context):
''')
    replace(API / 'candidate.py', "        uncertain=result is None\n        domain=None",
        "        uncertain=result is None\n        pending_evidence=self.vault.pending_evidence(claim['namespace']) if uncertain else []\n        domain=None")
    replace(API / 'candidate.py', "result['evidence_bindings'] if result else [claim['original_call_binding']]",
        "result['evidence_bindings'] if result else [claim['original_call_binding'],*pending_evidence]")
    shutil.copytree(BASE / 'api56-classification-checks-v1', CHECK, ignore=ignore)
    path=CHECK / 'test_classification_api.py'
    with path.open('a') as stream:
        stream.write('''
    def test_17_pending_native_evidence_is_inspectable_and_tamper_refused(self):
        host, request, _ = self.example(mode='bad-core')
        first=self.invoke(host,request)
        self.assertEqual(first['message']['code'],'indeterminate',first)
        before=self.journal(host)
        self.assertEqual(list((host.vault.root/'journal').glob('*.result.json')),[])
        inspect=copy.deepcopy(request)
        inspect['call_id']='call:pending:inspect:'+uuid.uuid4().hex
        inspect['operation']='operation.inspect';inspect['idempotency_key']=None
        inspect['message']={'schema_version':'lab-operation-inspect-request/v1-candidate',
            'lookup':{'operation':'classification.prepare','idempotency_key':request['idempotency_key']}}
        reply=self.invoke(host,inspect)
        self.assertEqual(reply['kind'],'result',reply)
        result=reply['message']
        self.assertEqual(result['posture'],'indeterminate')
        self.assertIsNone(result['result_binding'])
        self.assertTrue(result['reconciliation_required'])
        self.assertFalse(result['retry_allowed'])
        reports=[]
        for binding in result['effect_evidence_bindings'][1:]:
            body=P.frame_parse(host.vault.object_read(binding))
            if body.get('schema_version')=='lab-validation-report/v1-candidate':reports.append(body)
        self.assertEqual(len(reports),1)
        self.assertEqual(reports[0]['result'],'fail')
        self.assertEqual(self.journal(host),before)
        retry=copy.deepcopy(request);retry['call_id']='call:pending:retry:'+uuid.uuid4().hex
        self.assertEqual(self.invoke(host,retry)['message']['code'],'recovery-required')
        self.assertEqual(self.journal(host),before)
        pending=next((host.vault.root/'journal').glob('*.pending-evidence.json'))
        original=pending.read_bytes()
        altered=P.frame_parse(original);altered['claim_sha256']='0'*64
        pending.write_bytes(P.compact(altered))
        inspect['call_id']='call:pending:tamper:'+uuid.uuid4().hex
        try:
            refused=self.invoke(host,inspect)
            self.assertEqual(refused['kind'],'error',refused)
            self.assertEqual(refused['message']['code'],'integrity-failed')
            self.assertEqual(refused['message']['evidence_bindings'],[])
        finally:pending.write_bytes(original)
        self.assertEqual(self.journal(host),before)
        self.assertEqual(self.rules(host),[])
        self.assert_live(host,request)
''')
    path=CHECK / 'checks.py'
    text=path.read_text().replace('api-v56','api-v57').replace('API56','API57')
    text=text.replace("choices=['focused', 'full']", "choices=['focused', 'full', 'pending']")
    text=text.replace("    if args.suite == 'focused':", "    if args.suite == 'pending':\n        suite=unittest.TestSuite([module.ClassificationAPI('test_17_pending_native_evidence_is_inspectable_and_tamper_refused')])\n        expected=1\n    elif args.suite == 'focused':")
    text=text.replace('expected = 16','expected = 17')
    path.write_text(text)
    for folder in (API,COMPOSITION,CHECK,BASE/'lesson-host-composition-v7'):
        for path in folder.rglob('*.py'):ast.parse(path.read_bytes())
    print('Authored API57 pending native evidence observation; original operation result/retry semantics and inherited test methods retained.',flush=True)


if __name__ == '__main__':main()
