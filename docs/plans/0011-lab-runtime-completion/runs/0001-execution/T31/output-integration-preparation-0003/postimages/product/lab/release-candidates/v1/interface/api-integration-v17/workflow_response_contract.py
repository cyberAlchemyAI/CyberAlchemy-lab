"""Pure authenticated response-input proof; no producer/API effect or grant."""
import base64
from .workflow_output_contracts import need,closed,parse,sha
from .protocol import compact

def authenticate_response(response_raw,signature_raw,*,public_key,policy_binding,run_binding,work_ref,source_cut,eligible_invocation_ref):
    proof=parse(signature_raw)
    closed(proof,('schema_version','policy_binding','response_sha256','run_binding','work_ref','source_cut','eligible_invocation_ref','signature_base64'))
    need(proof['schema_version']=='lab-authenticated-challenge-response-input/v1-candidate' and proof['policy_binding']==policy_binding and proof['response_sha256']==sha(response_raw) and proof['run_binding']==run_binding and proof['work_ref']==work_ref and proof['source_cut']==source_cut and proof['eligible_invocation_ref']==eligible_invocation_ref,'actual response signature input lineage differs')
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    payload={k:v for k,v in proof.items() if k!='signature_base64'}
    Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key,validate=True)).verify(base64.b64decode(proof['signature_base64'],validate=True),compact(payload))
    return parse(response_raw),proof
