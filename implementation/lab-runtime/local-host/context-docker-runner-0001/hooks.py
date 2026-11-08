"""Fixed fixture transport integration; actual Context entrypoint stays disabled."""
import os
from pathlib import Path
import threading
import time

import layout_bridge as B

GUARD_SHA = '1d320473ba057e508a1b52176c556cd2f368e3edfc4f8de4d7de076edf831538'
EFFECT_ENABLED = False


def client_endpoint(sock, peer, token, out, source, deadline, namespace_child):
    B.need(type(namespace_child) is bool, 'NAMESPACE_PROFILE')
    if not namespace_child:
        return B.Client(sock, peer, token, out, source, deadline)
    # Same fixed coordinate used by reviewed child0002: host parent lies outside
    # child PID namespace. This is not independent host identity or authority.
    B.need(os.getpid() == 1 and type(peer) is tuple and
           all(type(v) is int for v in peer) and peer == (0, os.getuid(), os.getgid()),
           'NAMESPACE_PARENT_COORDINATE')
    B.transport_selection((1, os.getuid(), os.getgid()), token, deadline)
    B.configure(sock)
    client = B.Client.__new__(B.Client)
    client.sock, client.peer, client.token = sock, peer, token
    client.out, client.source, client.deadline = Path(out), source, deadline
    client.seq, client.rows = 0, []
    client.state, client.released, client.closed, client.trace = 'OPEN', False, False, []
    return client


class Parent:
    def __init__(self, sock, peer, here, source, token, deadline):
        self.sock, self.peer = sock, peer
        self.here, self.source, self.token, self.deadline = Path(here), source, token, deadline
        B.transport_selection(peer, token, deadline)
        B.configure(sock)
        self.writer = self.mediator = self.thread = None
        self.joined = False
        self.state = 'NEW'

    def start(self):
        B.need(self.state == 'NEW', 'PARENT_ONCE')
        self.state = 'WAIT_READY'
        self.thread = threading.Thread(target=self._ready)
        self.thread.start()

    def _ready(self):
        transferred = False
        try:
            raw = B.receive(self.sock, self.peer, self.deadline)
            expected = {'schema': 'context-child-ready/v1', 'attempt': self.token,
                        'out': str(self.here / 'packages/0001'),
                        'original_guard_sha256': GUARD_SHA, 'output_absent': True}
            B.need(raw == B.encode(expected) and not os.path.lexists(self.here / 'packages'),
                   'ORIGINAL_READY_SCOPE')
            self.writer = B.Writer(self.here / 'packages', self.source, self.deadline)
            B.send(self.sock, B.encode({'schema': 'context-child-go/v1',
                                       'ready_sha256': B.sha(raw)}), self.deadline)
            self.mediator = B.Mediator(self.sock, self.peer, self.token, self.writer)
            self.mediator.start()
            transferred = True
            self.state = 'MEDIATING'
        except BaseException:
            self.state = 'UNKNOWN'
            if self.writer is not None:
                self.writer.abort()
        finally:
            if not transferred:
                try:
                    self.sock.close()
                except BaseException:
                    self.state = 'UNKNOWN'

    def join(self):
        B.need(self.thread is not None, 'PARENT_NOT_STARTED')
        self.thread.join(max(0, self.deadline - time.monotonic()))
        B.need(not self.thread.is_alive() and self.state == 'MEDIATING' and
               self.mediator is not None, 'PARENT_READY_UNKNOWN')
        B.need(self.mediator.join(max(0, self.deadline - time.monotonic())), 'PARENT_JOIN_UNKNOWN')
        self.joined = True


class Hooks:
    def __init__(self, sock, peer, here, original_private_root, source, token, deadline,
                 *, namespace_child=False):
        self.here = Path(here)
        self.private = Path(original_private_root)
        B.need(self.here.is_absolute() and self.private.is_absolute() and
               self.private != self.here and self.here not in self.private.parents and
               self.private not in self.here.parents,
               'PRIVATE_OUTSIDE_PUBLIC')
        self.client = client_endpoint(sock, peer, token, self.here / 'packages/0001',
                                      source, deadline, namespace_child)
        self.output = B.ProvisionalOutput()
        self.state = 'NEW'

    def _poison(self):
        self.state = 'UNKNOWN'
        try:
            self.client.close_once()
        except BaseException:
            pass

    def output_ready(self, out):
        try:
            B.need(self.state == 'NEW' and Path(out) == self.client.out and not os.path.lexists(out),
                   'READY_SCOPE')
            ready = {'schema': 'context-child-ready/v1', 'attempt': self.client.token,
                     'out': str(out), 'original_guard_sha256': GUARD_SHA, 'output_absent': True}
            B.send(self.client.sock, B.encode(ready), self.client.deadline)
            B.need(B.receive(self.client.sock, self.client.peer, self.client.deadline) ==
                   B.encode({'schema': 'context-child-go/v1', 'ready_sha256': B.sha(B.encode(ready))}),
                   'GO_BINDING')
            self.state = 'READY'
        except BaseException:
            self._poison()
            raise

    def emit(self, path, raw):
        try:
            B.need(self.state == 'READY', 'EMIT_STATE')
            self.client.emit(path, raw)
        except BaseException:
            self._poison()
            raise

    def release_private(self, root):
        try:
            # Original with/finally and its original absence assertion precede this.
            # The Writer's own empty fixture directory is a distinct transport marker.
            B.need(self.state == 'READY' and Path(root) == self.private and
                   not os.path.lexists(root), 'ORIGINAL_PRIVATE_NOT_RELEASED')
            self.client.release_private()
        except BaseException:
            self._poison()
            raise

    def provisional_print(self, text, *, flush=False):
        try:
            B.need(self.state == 'READY' and self.client.state == 'SUMMARY_PERMITTED' and
                   self.client.closed, 'SUMMARY_STATE')
            self.output.capture(text, flush=flush)
            self.state = 'PROVISIONAL'
        except BaseException:
            self._poison()
            raise

    def publish(self, parent):
        try:
            B.need(self.state == 'PROVISIONAL' and parent.joined and
                   parent.here == self.here and parent.writer.out == self.client.out,
                   'AGGREGATE_STATE')
            result = self.output.release(self.client, parent.mediator)
            self.state = 'PUBLISHED'
            return result
        except BaseException:
            self._poison()
            raise


def launch_context(*args, **kwargs):
    raise RuntimeError('ACTUAL_CONTEXT_EFFECT_DISABLED')
