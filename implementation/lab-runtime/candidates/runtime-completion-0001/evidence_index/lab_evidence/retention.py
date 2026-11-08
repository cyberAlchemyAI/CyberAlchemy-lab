"""No-replace retention of exact already-public originals in an owned directory."""
import os
from lab_contracts.codec import canonical, need, sha, parse
from lab_selectors.anchors import RootAnchor
from .common import binding, LIMIT, public_selector


def persist(evaluation, owned_root, *, reader, expected_disclosure,
            expected_inventory=None, expected_policy=None):
    # Recheck independently supplied disclosure even when a caller constructs
    # or mutates an Evaluation object directly. No in-memory boolean is a grant.
    binding(expected_disclosure)
    selection=public_selector(reader,expected_disclosure)
    approved={canonical(expected_disclosure)}
    for selected in selection['public_retention_bindings']:
        binding(selected);approved.add(canonical(selected))
    need(all(canonical(b) in approved for b,_ in evaluation.originals),'RETENTION_NOT_AUTHORIZED')
    need(len(evaluation.originals)<=8192 and
         sum(len(raw) for _,raw in evaluation.originals)<=64*1024*1024,'RETENTION_BOUND')
    # Never treat an in-memory Evaluation or its nested dictionaries as an
    # export grant. Recompute from independently selected original inputs.
    if selection['schema_version']=='lab-eligibility-context/v1':
        need(expected_inventory is not None and expected_policy is not None,'RETENTION_INPUT_SELECTIONS')
        from .eligibility import evaluate
        verified=evaluate(reader,expected_inventory,expected_policy,expected_disclosure)
    else:
        need(expected_inventory is None and expected_policy is None,'HISTORICAL_RETENTION_INPUTS')
        from .history import historical
        verified=historical(reader,expected_disclosure)
    need(canonical(evaluation.projection)==canonical(verified.projection),'RETENTION_PROJECTION_MISMATCH')
    given={canonical(b):raw for b,raw in evaluation.originals}
    actual={canonical(b):raw for b,raw in verified.originals}
    need(len(given)==len(evaluation.originals) and given==actual,'RETENTION_ORIGINAL_SET_MISMATCH')
    evaluation=verified
    projection_bytes=canonical(evaluation.projection)
    need(len(projection_bytes)<=LIMIT,'PROJECTION_BOUND')
    need(type(owned_root) is RootAnchor,'RETENTION_ROOT')
    handles,links=owned_root.open()
    created=[]
    try:
        fd=handles[-1]
        # Dedicated output root must be exclusively reserved and initially empty.
        need(not os.listdir(fd),'RETENTION_ROOT_NOT_EMPTY')
        originals={}
        for selected,raw in evaluation.originals:
            need(len(raw)==selected['size_bytes'] and sha(raw)==selected['sha256'],'RETENTION_BYTES')
            originals[sha(raw)]=raw
        rows=[{'binding':selected,'retained_file':selected['sha256']+'.original'}
              for selected,_ in evaluation.originals]
        files=[(digest+'.original',raw) for digest,raw in sorted(originals.items())]
        files.append(('projection.json',projection_bytes))
        files.append(('retention.json',canonical({'schema_version':'lab-evidence-retention/v1',
                    'originals':rows,'projection_sha256':sha(projection_bytes)})))
        for name,raw in files:
            child=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,
                          0o600,dir_fd=fd)
            created.append(name)
            try:
                view=memoryview(raw)
                while view:
                    count=os.write(child,view);need(count>0,'RETENTION_SHORT_WRITE');view=view[count:]
                os.fsync(child)
            finally:os.close(child)
        os.fsync(fd)
        # Reopen selected anchor before declaring success. A concurrent detach
        # cannot silently turn a retained receipt into a different root.
        check,unused=owned_root.open()
        for descriptor in reversed(check):os.close(descriptor)
        return {'files':created,'result':'PASS','effect_state':'owned-inert','cleanup':'retained-owned'}
    finally:
        # Any partial retention remains owned evidence, never rollback-deleted.
        for descriptor in reversed(handles):os.close(descriptor)
