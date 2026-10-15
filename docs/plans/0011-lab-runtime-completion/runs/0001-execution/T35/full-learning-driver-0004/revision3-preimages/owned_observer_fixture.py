"""Inert observer qualification functions. No Lab objects or runtime effects."""
import fcntl,time

def leaf(size=1500):
    value=0
    for i in range(size):value=(value+i*i)%100003
    return value

def nested():return leaf()+leaf()

def caught():
    try:raise ValueError('PRIVATE-EXCEPTION-SENTINEL')
    except ValueError:return leaf(10)

def primary():raise RuntimeError('PRIVATE-PRIMARY-SENTINEL')

def generator():
    yield leaf(25)
    yield leaf(25)

def locks(fd):
    fcntl.flock(fd,fcntl.LOCK_EX)
    time.sleep(.003)
    fcntl.flock(fd,fcntl.LOCK_UN)

def ambiguous_locks(a,b):
    fcntl.flock(a,fcntl.LOCK_EX)
    fcntl.flock(b,fcntl.LOCK_EX)
    fcntl.flock(a,fcntl.LOCK_UN)
    fcntl.flock(b,fcntl.LOCK_UN)

def threaded(barrier):
    barrier.wait()
    for i in range(8):nested()

def workload():
    for i in range(250):nested()

def inline():
    bad='PRIVATE-INLINE-SENTINEL'
    leaf(25)
    application=leaf(25)
    return application
