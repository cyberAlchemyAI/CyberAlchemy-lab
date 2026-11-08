"""Pure original-result/header matching, no invocation or authority."""
import hashlib
def sha(raw):return hashlib.sha256(raw).hexdigest()

def contains_original(value,header):
    """Actual original result must contain the exact produced byte digest.

    Original Work materializers expose record_sha256/sha256, API replies expose
    exact bound objects/headers, and private body returns are compared as bytes.
    No metadata flag can turn an uncalled producer into an invocation result.
    """
    if type(value)is bytes:return False # bytes alone cannot invent an ArtifactRef version
    if type(value)is dict:
        hashes=[value.get(k) for k in ('byte_sha256','record_sha256','sha256')]
        if header['byte_sha256'] in hashes:
            identities=[value.get(k) for k in ('identity_ref','node_id','migration_manifest_id') if value.get(k) is not None]
            versions=[value.get(k) for k in ('version_ref',) if value.get(k) is not None]
            # No guessed identity/version from a body hash or partial binding.
            if header['identity_ref'] in identities and header['version_ref'] in versions:return True
        return any(contains_original(v,header) for v in value.values())
    if type(value)in (list,tuple):return any(contains_original(v,header) for v in value)
    return False

