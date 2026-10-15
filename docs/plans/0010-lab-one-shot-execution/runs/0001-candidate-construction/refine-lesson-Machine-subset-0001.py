"""Keep the legacy seven-read constant and add only an explicit lesson subset."""
import hashlib
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'


def main():
    path=BASE/'api-v51/machine_transport.py'
    selected=json.loads((RUN/'API51-construction-static-0001.json').read_bytes())
    row=next(r for r in selected['files'] if r['path']==path.relative_to(ROOT).as_posix())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
    text=path.read_text()
    old="                   'context.get', 'session.inspect', 'operation.inspect', 'lesson.select')"
    assert text.count(old)==1
    text=text.replace(old,"                   'context.get', 'session.inspect', 'operation.inspect')\nLESSON_READ_OPERATIONS = READ_OPERATIONS + ('lesson.select',)")
    old="        policy['allowed_operations'] = [operation for operation in READ_OPERATIONS\n                                        if operation in policy['allowed_operations']]"
    assert text.count(old)==1
    text=text.replace(old,"        reads = LESSON_READ_OPERATIONS if policy['schema_version']=='lab-local-lesson-read-policy/v1-candidate' else READ_OPERATIONS\n        policy['allowed_operations'] = [operation for operation in reads\n                                        if operation in policy['allowed_operations']]")
    path.write_text(text)
    print(json.dumps({'result':'REFINED-UNFROZEN','legacy_reads':7,'explicit_lesson_reads':8,'public_calls':0}),flush=True)


if __name__=='__main__':main()
