"""Construct one private signed fixture successor from API60 actual evidence."""
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import fixture_resolution_source as S

HERE=Path(__file__).resolve().parent
PRIVATE=Path.home()/'.local/share/cyberalchemy-lab'

def selected_inputs():
    submission=json.loads((HERE/'LIVE-NATIVE-AGENT-CHALLENGE-API60-0001.json').read_bytes())
    observation=json.loads((HERE/'NATIVE-AGENT-CHALLENGE-CALL-API60-0001.json').read_bytes())
    matches=[]
    for path in (PRIVATE/'t22-native-agent-diagnostics').glob('*/call-observation.json'):
        value=json.loads(path.read_bytes())
        if value.get('reply_sha256')==submission['challenge_response_sha256']: matches.append(path.parent)
    if len(matches)!=1: raise ValueError('one exact private native observation required')
    base=matches[0]
    return submission,observation,(base/'candidate.json').read_bytes(),json.loads((base/'request.json').read_bytes())

def run():
    sub,obs,candidate,request=selected_inputs()
    source=S.build(submission=sub,observation=obs,candidate_raw=candidate,request=request,
                   now=datetime.now(timezone.utc),period_end='2026-10-24T17:54:44.262511+00:00')
    output=PRIVATE/'t22-fixture-resolution-source-20261024'
    output.mkdir(mode=0o700,exist_ok=False)
    source_file=output/'source.json'
    fd=os.open(source_file,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:
        stream.write(S.canon(source));stream.flush();os.fsync(stream.fileno())
    receipt={'schema_version':'lab-T22-fixture-resolution-source-construction/v1',
        'result':'PASS-signed-local-fixture-source','source_sha256':S.sha(source_file.read_bytes()),
        'selected_public_hex':source['issuer_public_hex'],'source_cut':sub['source_cut'],
        'native_submission_sha256':S.sha(S.canon(sub)), 'original_candidate_sha256':S.sha(candidate),
        'members':list(source['members']),'selected_fixture_outcome':'defer','source_admitted':False,
        'challenge_resolved_through_native_API':False,'actual_owner_outcome':None,'authority_effect':'none',
        'private_source_locator_sha256':S.sha(str(source_file).encode()),
        'producer_sha256':S.sha(Path(S.__file__).read_bytes())}
    path=HERE/'FIXTURE-RESOLUTION-SOURCE-20261024-0001.json'
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as stream:
        stream.write(json.dumps(receipt,sort_keys=True,indent=2).encode()+b'\n')
    return {k:receipt[k] for k in ['result','source_sha256','members','selected_fixture_outcome','source_admitted','challenge_resolved_through_native_API']}

if __name__=='__main__':print(json.dumps(run(),sort_keys=True))
