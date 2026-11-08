"""Real fd3/SCM_CREDENTIALS tests with an inert stand-in and /tmp scratch."""
import os
from pathlib import Path
import tempfile
import unittest

from t35_external_v1.phase_scoped_v2 import mapper_package_ipc_model_0004 as grammar
from t35_external_v1.phase_scoped_v2 import mapper_package_standin_0001 as standin
from t35_external_v1.phase_scoped_v2 import mapper_package_transport_0001 as transport
from t35_external_v1.phase_scoped_v2 import mapper_package_writer_0001 as writer
from t35_external_v1.phase_scoped_v2 import mapper_package_plan_0002 as plan


def live_fds():
    result = set()
    for value in os.listdir('/proc/self/fd'):
        fd = int(value)
        try:
            os.fstat(fd)
        except OSError:
            continue
        result.add(fd)
    return result


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(
            prefix='lc-u02-05-mapper-writer-', dir='/tmp')
        self.addCleanup(self.tmp.cleanup)
        self.scratch = Path(self.tmp.name)
        self.mapped = self.scratch / 'output/legacy-fixture-source/mapped'
        self.mapped.mkdir(parents=True, mode=0o700)
        for path in (self.scratch, self.scratch / 'output',
                     self.mapped.parent, self.mapped):
            path.chmod(0o700)

    def server(self, scenario, *, writer_object=None, peer_override=None):
        parent, child = transport.socket_pair()
        try:
            pid = transport.spawn_standin(child, scenario)
        finally:
            child.close()
        peer = (pid, transport.process_start(pid), os.geteuid(), os.getegid())
        selected = peer_override(peer) if peer_override else peer
        protocol = grammar.ProtocolModel(attempt_id=standin.ATTEMPT,
                                         selection_sha256=standin.SELECTION,
                                         begin_pins=standin.PINS, peer=selected)
        return transport.ModelServer(parent, selected, protocol,
                                     writer_object), pid

    def test_genuine_bidirectional_credentials_fd3_and_durable_first_leaf(self):
        binding = {'path': plan.FAMILY + '/mapped/source-manifest.json',
                   'sha256': 'a' * 64}
        with writer.PackageWriter(self.mapped, binding) as owned:
            server, pid = self.server('normal', writer_object=owned)
            try:
                self.assertEqual(os.getpgid(pid), pid)
                observations = [server.receive_one() for _ in range(13)]
                self.assertTrue(all(item['peer_pid'] == pid for item in observations))
                self.assertEqual(observations[-1]['observation'], 'DURABLE_FILE')
                self.assertEqual(server.emits, 1)
                self.assertEqual(server.protocol.step, 4)
                self.assertEqual(transport.reap_standin(pid), 0)
                leaf = self.mapped / 'packages/0001/semantic/00000001.json'
                self.assertEqual(leaf.read_bytes(), b'{"synthetic":"event"}\n')
                with self.assertRaises(transport.TransportRefusal):
                    server.receive_one()
                self.assertTrue(server.failed)
                self.assertTrue(owned.unknown)
            finally:
                server.close()

    def test_replay_and_disconnect_poison_channel(self):
        server, pid = self.server('replay')
        try:
            self.assertEqual(server.receive_one()['ordinal'], 0)
            with self.assertRaises(grammar.Refusal):
                server.receive_one()
            self.assertTrue(server.failed)
            self.assertTrue(server.protocol.failed)
            with self.assertRaises(transport.TransportRefusal):
                server.receive_one()
            transport.reap_standin(pid)
        finally:
            server.close()

        server, pid = self.server('disconnect')
        try:
            with self.assertRaises(transport.TransportRefusal):
                server.receive_one()
            self.assertTrue(server.failed)
            self.assertEqual(server.protocol.first_failure, 'DISCONNECTED')
            transport.reap_standin(pid)
        finally:
            server.close()

    def test_rights_and_truncation_refuse_without_leaking_received_fd(self):
        for scenario, code in (('rights', 'SCM_RIGHTS'),
                               ('trunc', 'MSG_TRUNC'),
                               ('ctrunc', 'MSG_CTRUNC')):
            with self.subTest(scenario=scenario):
                server, pid = self.server(scenario)
                before = live_fds()
                channel_fd = server.endpoint.fileno()
                try:
                    with self.assertRaisesRegex(transport.TransportRefusal, code):
                        server.receive_one()
                    self.assertTrue(server.failed)
                    self.assertEqual(live_fds(), before - {channel_fd})
                    transport.reap_standin(pid)
                finally:
                    server.close()

    def test_wrong_kernel_peer_identity_refuses(self):
        server, pid = self.server('replay',
                                  peer_override=lambda p: (p[0], p[1] + 1,
                                                           p[2], p[3]))
        try:
            with self.assertRaisesRegex(transport.TransportRefusal,
                                        'PEER_IDENTITY'):
                server.receive_one()
            self.assertTrue(server.failed)
            transport.reap_standin(pid)
        finally:
            server.close()

    def test_inheritable_host_fd_refuses_before_launch(self):
        parent, child = transport.socket_pair()
        extra = os.open(self.scratch / 'extra', os.O_RDWR | os.O_CREAT | os.O_EXCL,
                        0o600)
        os.set_inheritable(extra, True)
        try:
            with self.assertRaisesRegex(transport.TransportRefusal,
                                        'INHERITABLE_FD'):
                transport.spawn_standin(child, 'normal')
        finally:
            os.close(extra)
            parent.close()
            child.close()


if __name__ == '__main__':
    unittest.main()
