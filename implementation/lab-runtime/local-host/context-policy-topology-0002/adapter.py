"""Pure policy-path/retention/proof contract. No key, policy, socket or Docker effects."""
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath

LOCAL = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
HOST_ROOT = '/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-jit-private-attempt-0001'
CHILD_ROOT = '/context-policy'
CHILD_SOURCE = '/workspace'
HOST_SOURCE = '/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/context-attempt/root'
EFFECT_ENABLED = False
PINS = {
 'context-jit-provision-0001/projected-control.py':'ebd63979ce378070e6d5647c240234548a9fb38d141b6ed0d57885925f66c7e1',
 'context-policy-0002/held_policy.py':'0565b4a1a559404cf773198bf52e62f444b656084157557319ff0c3b44253a6f',
 'context-jit-provision-0001/projected-build.py':'30149a0388f3eb32fb30dd5b07bc11a8309ed7ab3fafa56ef8b5d714d39f93f0',
 'context-original-bridge-0001/hooks.py':'8cf65dafc2b200ea695b3692b0a3dae5ef2ccca19915b409d01a041fdc0ce9d4',
 'context-successor-mount-reconcile-0001/mount_vector.py':'ed04a32ce0d904f5d3f1303f99feb60b02b4ed59fb75b4944d8cc1b58006f95f',
 'context-successor-stage-jit-release-plan-0002/release_plan.py':'1e403bdee4eb38da88ca8463e607ba923965117d48dc3419b60f6a000cc9c090',
}
class Refused(ValueError): pass

def need(ok, code):
    if not ok: raise Refused(code)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def compact(value):
    return json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=False, allow_nan=False).encode()

def original(name):
    need(name in PINS,'UNSELECTED_ORIGINAL')
    raw=(LOCAL/name).read_bytes()
    need(digest(raw)==PINS[name],'ORIGINAL_DRIFT')
    return raw

def replace_exact(raw, changes):
    result=raw
    for old,new in changes:
        need(result.count(old)==1 and new not in result,'EXACT_SPAN')
        result=result.replace(old,new,1)
    inverse=result
    for old,new in reversed(changes):
        need(inverse.count(new)==1,'INVERSE_SPAN')
        inverse=inverse.replace(new,old,1)
    need(inverse==raw,'INVERSE')
    ast.parse(result)
    return result

def project_policy_guard(view):
    need(type(view) is str and view in ('host','child'),'VIEW')
    root=HOST_ROOT if view=='host' else CHILD_ROOT
    source=HOST_SOURCE if view=='host' else CHILD_SOURCE
    raw=original('context-policy-0002/held_policy.py')
    # Other nofollow/identity/UID/mode/link/readback/close checks remain byte-identical.
    return replace_exact(raw,[(b"_PolicyPurePath('/tmp') in base.parents",
        ("base == _PolicyPurePath("+repr(root)+") and\n                  source == _PolicyPurePath("+repr(source)+")").encode())])

def project_control():
    raw=original('context-jit-provision-0001/projected-control.py')
    return replace_exact(raw, [(b"_PolicyPurePath('/tmp') in base.parents",
        ("base == _PolicyPurePath("+repr(CHILD_ROOT)+") and\n                  source == _PolicyPurePath("+repr(CHILD_SOURCE)+")").encode())])

def project_build():
    raw=original('context-jit-provision-0001/projected-build.py')
    changes=[
      (b"JIT_PRIVATE_ROOT = Path('/tmp/cal-context-jit-private-20261020-0001')",b"JIT_PRIVATE_ROOT = Path('/context-policy')"),
      (b'_jit_private_root() as tmp:',b'_ctx_retained_policy_scope() as tmp:'),
      (b'key, policy_pin = provision(policy_path, source)',b'policy_pin = _ctx_selected_policy_pin(policy_path, source)'),
      (b"proof_raw = wire({'challenge': channel.challenge, 'signature': base64.b64encode(key.sign(wire(channel.challenge))).decode()})",b'proof_raw = _ctx_parent_proof(channel.challenge)'),
      (b'            key = None',b'            _ctx_drop_proof_handle()'),
      (b"require(not root.exists(), 'private host permission root remains')",b'_ctx_policy_retained(root)\n    _ctx_release_transport_scratch(root)'),
      (b"'owned_host_policy_and_transport_key_removed': True",b"'owned_host_policy_and_transport_key_removed': False, 'private_policy_retained_pending_external_verification': True, 'parent_key_custody': 'EXTERNAL_PENDING_POSTCLOSE_OBSERVATION'"),
    ]
    result=replace_exact(raw,changes)
    need(result.count(b"def _t35_effect_refused():")==1,'GUARD_PRESERVED')
    return result

def project_release_hook():
    raw=original('context-original-bridge-0001/hooks.py')
    # Compatibility bytes only. The concrete retained-policy guard must be wired
    # by a reviewed runner; this symbol is intentionally not an authority callback.
    return replace_exact(raw,[(b'not os.path.lexists(root), \'ORIGINAL_PRIVATE_NOT_RELEASED\'',
        b"_ctx_policy_retained_exact(root), 'PRIVATE_POLICY_RETENTION_NOT_VERIFIED'")])

def topology():
    return {'schema':'context-policy-topology/v1-inert','effect_enabled':False,
        'host_private_root':HOST_ROOT,'child_policy_root':CHILD_ROOT,
        'policy_leaf':'permission.json','directory_mode':'0700','leaf_mode':'0600',
        'source_child':CHILD_SOURCE,'source_host':HOST_SOURCE,
        'additional_bind':{'source':HOST_ROOT,'target':CHILD_ROOT,'read_only':True},
        'required_private_inventory':['permission.json'],
        'private_key':'PARENT_MEMORY_ONLY_NEVER_MOUNTED',
        'transport':'SEPARATELY_SELECTED_ONE_USE_PROOF_SEQPACKET_ON_CONTROL',
        'previous_five_bind_probe':'INSUFFICIENT_FOR_SIXTH_POLICY_BIND',
        'output':'PARENT_HELD_WRITER_CHILD_RO',
        'policy_paths':'HOST_AND_CHILD_EXACT_SEPARATE_VIEWS',
        'execution':'REFUSED'}

def validate_mount_observation(raw):
    # Pure fixture observation; never attests the actual kernel.
    need(type(raw) is bytes and 0<len(raw)<=65536,'MOUNT_FRAME')
    try: rows=json.loads(raw)
    except (ValueError,UnicodeError): raise Refused('MOUNT_JSON') from None
    targets={'/workspace','/control','/runner','/cache-disabled','/attempt/input/lab-context-native-reader',CHILD_ROOT}
    need(type(rows) is list and len(rows)==6,'SIX_BINDS')
    need(all(type(r) is dict and set(r)=={'target','read_only','source'} and type(r['target']) is str and
             type(r['source']) is str and r['read_only'] is True for r in rows),'MOUNT_ROWS')
    need({r['target'] for r in rows}==targets,'EXACT_TARGETS')
    policy=next(r for r in rows if r['target']==CHILD_ROOT)
    need(policy['source']==HOST_ROOT,'POLICY_MOUNT_SOURCE')
    need(all(not r['target'].startswith('/workspace/') for r in rows),'NO_NESTED_WORKSPACE')
    return 'SYNTHETIC_TOPOLOGY_ONLY'

class RetentionModel:
    """Selected observation model only; performs no cleanup or key operations."""
    def __init__(self):
        self.state='OPEN'; self.unknown=False
    def closed_channel(self, *, channel_closed, local_proof_handle_dropped, policy_attached):
        need(self.state=='OPEN','ORDER')
        if not (channel_closed is True and local_proof_handle_dropped is True and policy_attached is True):
            self.unknown=True;self.state='UNKNOWN';raise Refused('CLOSE_OR_RETENTION_UNKNOWN')
        self.state='RETAINED'
    def release_transport_scratch(self, ordinal, *, scratch_empty, policy_attached):
        # The first attempted release is terminal on failure. Retrying after an
        # uncertain Writer or policy observation would violate the one-shot cut.
        if self.state!='RETAINED' or type(ordinal) is not int or ordinal!=38:
            self.unknown=True;self.state='UNKNOWN';raise Refused('RELEASE38_ORDER')
        if scratch_empty is not True or policy_attached is not True:
            self.unknown=True;self.state='UNKNOWN';raise Refused('SCRATCH_NOT_JIT')
        self.state='SCRATCH_RELEASED'
    def result(self):
        need(self.state=='SCRATCH_RELEASED','RESULT39_ORDER')
        return {'owned_host_policy_and_transport_key_removed':False,
                'private_policy_retained_pending_external_verification':True,
                'parent_key_custody':'EXTERNAL_PENDING_POSTCLOSE_OBSERVATION'}
    def external_gate(self, *, os_exit, container_absent, final_closed, output_verified, independent_review, parent_key_dropped):
        need(self.state=='SCRATCH_RELEASED','EXTERNAL_ORDER')
        if not (type(os_exit) is int and os_exit==0 and container_absent is True and final_closed is True and
                output_verified is True and independent_review is True and parent_key_dropped is True):
            self.unknown=True;self.state='UNKNOWN';raise Refused('KEEP_PRIVATE_UNKNOWN_NO_RETRY')
        self.state='CLEANUP_ELIGIBLE_MODEL_ONLY'
    def cleanup_effect(self): raise Refused('EFFECT_DISABLED_NO_PRIVATE_CLEANUP')

class ProofModel:
    """Pure two-phase consumption model. No signer/key/network; inputs synthetic."""
    def __init__(self, *, policy_sha, expires_at, attempt, peer):
        need(type(policy_sha) is str and len(policy_sha)==64 and all(c in '0123456789abcdef' for c in policy_sha),'POLICY_SHA')
        need(type(expires_at) is str and type(attempt) is str and 1<=len(attempt)<=128,'SELECTION')
        need(type(peer) is tuple and len(peer)==3 and all(type(v) is int and v>=0 for v in peer) and peer[0]>0,'PEER')
        self.policy=policy_sha;self.expiry=expires_at;self.attempt=attempt;self.peer=peer
        self.state='UNUSED';self.challenge=None;self.request_digest=None
    def consume(self, raw, *, peer, current):
        need(self.state=='UNUSED','PROOF_ALREADY_CONSUMED')
        # Receipt of the first request consumes the opportunity even if its
        # frame, peer, currentness, or challenge is invalid.
        self.state='UNKNOWN_CONSUMED'
        need(type(raw) is bytes and 0<len(raw)<=8192 and type(peer) is tuple and
             len(peer)==3 and all(type(v) is int for v in peer) and peer==self.peer and current is True,'CURRENT_PEER_BOUNDS')
        def pairs(items):
            d={}
            for k,v in items:need(k not in d,'DUPLICATE');d[k]=v
            return d
        try:r=json.loads(raw,object_pairs_hook=pairs)
        except (ValueError,UnicodeError,RecursionError):raise Refused('REQUEST_JSON') from None
        need(type(r) is dict and set(r)=={'schema','attempt','challenge'},'REQUEST_FIELDS')
        need(r['schema']=='context-parent-proof-request/v1' and r['attempt']==self.attempt,'REQUEST_SCOPE')
        c=r['challenge']
        fields={'schema_version','host_instance_ref','connection_ref','nonce','policy_sha256','expires_at','authority_effect'}
        need(type(c) is dict and set(c)==fields and all(type(v) is str for v in c.values()),'ORIGINAL_CHALLENGE_FIELDS')
        need(c['schema_version']=='lab-context-host-challenge/v1-candidate' and c['policy_sha256']==self.policy and
             c['expires_at']==self.expiry and c['authority_effect']=='none' and
             c['host_instance_ref'].startswith('host:R03-context:') and
             c['connection_ref'].startswith('connection:R03-context:') and
             len(c['host_instance_ref'])<=256 and len(c['connection_ref'])<=256 and len(c['nonce'])==64 and
             all(x in '0123456789abcdef' for x in c['nonce']),'ORIGINAL_CHALLENGE_JOIN')
        need(compact(r)==raw,'CANONICAL_REQUEST')
        self.challenge=compact(c);self.request_digest=digest(raw);self.state='CONSUMED_PENDING_DURABILITY'
        return {'request_sha256':self.request_digest,'challenge_sha256':digest(self.challenge),
                'bytes_to_sign':self.challenge,'claim':'SYNTHETIC_NO_SIGNATURE'}
    def durable(self, *, retained_request_sha, fsync_observed, current):
        need(self.state=='CONSUMED_PENDING_DURABILITY','DURABILITY_ORDER')
        if not (retained_request_sha==self.request_digest and fsync_observed is True and current is True):
            self.state='UNKNOWN_CONSUMED';raise Refused('NO_SIGN_DURABILITY_UNKNOWN')
        self.state='SIGN_ELIGIBLE_MODEL_ONLY'
    def sign(self):raise Refused('EFFECT_DISABLED_NO_KEY_OR_SIGNATURE')
    def restart(self):raise Refused('EXISTING_ATTEMPT_CONSUMED_NO_RESTART')

def provision_or_launch(*args,**kwargs):raise Refused('EFFECT_DISABLED_NO_POLICY_KEY_AUTH_DOCKER')
