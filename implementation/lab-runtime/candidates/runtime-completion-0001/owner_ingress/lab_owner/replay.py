"""Isolated persistent fixture replay custody; reservations never roll back.

An actual deployment needs independently selected non-worker-writable global
custody and current G07 enrollment. This fixture store cannot supply that fact.
"""
import os
from lab_selectors.anchors import RootAnchor
from .contracts import *
from .verifier import verify_fixture


def reserve_fixture(reader,expected_enrollment,expected_selection,*,now):
    result=verify_fixture(reader,expected_enrollment,expected_selection,now=now)
    trust=parse(reader.read(expected_enrollment,max_bytes=LIMIT),max_bytes=LIMIT);enrollment(trust)
    r=trust['replay_root'];root=RootAnchor(r['root_id'],r['path'],r['identity'])
    handles,links=root.open();created=[]
    try:
        directory=handles[-1]
        reservations=[]
        for row in result['owner_results']:
            # Target, operation, principal and caller path never salt host event
            # identity. A consumed event cannot move to a different operation.
            reservations.append(('host-event',row['host_event']))
            p=row['presentation_event']
            reservations.append(('host-event',{k:p[k] for k in ['host_issuer','mechanism_ref','event_id']}))
            reservations.append(('presentation-nonce',{k:p[k] for k in ['host_issuer','mechanism_ref','nonce']}))
        for kind,event in reservations:
            name=sha(canonical({'kind':kind,'event':event}))+'.reservation.json'
            record={'schema_version':'lab-owner-fixture-replay-reservation/v2','usage':'technical-fixture','authority_effect':'none',
                    'state':'reserved-no-effect','event':event,'event_kind':kind,'operation_id':result['operation_id'],
                    'review_binding':result['review_binding'],'selection_binding':expected_selection,'enrollment_binding':expected_enrollment,
                    'owner_results':result['owner_results'],'original_bindings':result['original_bindings']}
            data=canonical(record);need(len(data)<=LIMIT,'RESERVATION_BOUND')
            try:fd=os.open(name,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory)
            except FileExistsError:raise Refusal('HOST_EVENT_ALREADY_RESERVED') from None
            created.append(name)
            try:
                view=memoryview(data)
                while view:
                    n=os.write(fd,view);need(n>0,'REPLAY_SHORT_WRITE');view=view[n:]
                os.fsync(fd)
            finally:os.close(fd)
            os.fsync(directory)
        # Reopen after durable writes; detach/replacement is not success.
        check,checklinks=root.open()
        try:need(os.fstat(check[-1]).st_ino==os.fstat(directory).st_ino,'REPLAY_ROOT_CHANGED')
        finally:
            for fd in reversed(check):os.close(fd)
        return {**result,'reservation_files':created,'replay_state':'reserved-no-effect'}
    finally:
        for fd in reversed(handles):os.close(fd)
