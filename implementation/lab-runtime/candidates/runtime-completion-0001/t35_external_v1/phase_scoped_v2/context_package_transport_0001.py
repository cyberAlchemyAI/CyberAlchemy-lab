"""Scratch-only seqpacket Context stand-in, not a generated builder bridge.

The kernel-credential frame primitives are reused without their spawn API.
NATIVE_READ remains an explicitly synthetic selected digest observation.
"""
from __future__ import annotations

import base64
import binascii
import copy

from . import context_ipc_model_0001 as model
from . import mapper_package_transport_0001 as wire
from . import context_package_writer_0001 as writer

VERSION = 'lab-context-scratch-transport/v1-inert'
PACKETS_MAX = 4096
CHUNK_MAX = 32768
Refusal = writer.Refusal
need = writer.need


class ScratchSession:
    """One connection, one fixed package. No reconnect or retry on uncertainty."""

    def __init__(self, context, source_binding, protocol):
        need(type(protocol) is model.ProtocolModel and protocol.step == 0 and
             not protocol.failed and not protocol.finished and
             protocol.package_path == str(context/'packages/0001') and
             protocol.private_root_path == str(context.parent.parent.parent).replace('context-writer-', 'context-private-', 1), 'protocol_selection')
        self.context = context
        self.source_binding = copy.deepcopy(source_binding)
        self.protocol = copy.deepcopy(protocol)
        self.writer = None
        self.upload = None
        self.ordinal = self.total_uploaded = 0
        self.unknown = self.closed = False

    def poison(self):
        self.unknown = True
        self.protocol.failed = self.protocol.retain_attempt = True
        if self.protocol.first_failure is None:
            self.protocol.first_failure = 'SCRATCH_UNKNOWN'
        if self.writer is not None: self.writer.unknown = True

    def _available(self):
        need(not self.closed and not self.unknown and not self.protocol.finished, 'session_unavailable')

    def _expected(self):
        return model.schedule()[self.protocol.step]

    def _action(self, payload):
        model.closed(payload, ('verb','payload'))
        verb, value = payload['verb'], payload['payload']
        expected, leaf = self._expected()
        need(verb == expected, 'action_order')
        if verb != 'EMIT': need(self.upload is None, 'unexpected_upload')
        observation = 'MODEL_ONLY'
        if verb == 'PREPARE':
            model.closed(value, ())
            self.writer = writer.PackageWriter(self.context, self.source_binding)
            value = self.writer.prepare_receipt()
            observation = 'SCRATCH_DIRECTORY_SYNCED'
        elif verb == 'PRIVATE_ROOT':
            model.closed(value, ())
            value = self.writer.create_private()
            observation = 'SCRATCH_PRIVATE_DIRECTORY_SYNCED'
        elif verb == 'EMIT':
            model.closed(value, ('leaf',))
            need(self.upload is not None and value['leaf'] == leaf == self.upload['leaf'], 'upload_selection')
            data = bytes(self.upload['data'])
            need(len(data) == self.upload['size_bytes'] and model.sha(data) == self.upload['sha256'], 'upload_incomplete_or_changed')
            value = {'leaf':leaf,'sha256':model.sha(data),'size_bytes':len(data)}
            if leaf == 'authentication-proof.json':
                value['proof'] = model.codec.decode(data)
        elif verb == 'RELEASE_PRIVATE':
            model.closed(value, ())
            value = self.writer.release_private()
            observation = 'SCRATCH_PRIVATE_REMOVAL_SYNCED'
        elif verb == 'FINISH':
            model.closed(value, ())
            value = {'manifest_rows':self.writer.manifest_rows(),'package_closed':True}
        # Clone before model acceptance: a file/ACK failure never commits a
        # model-only success as a reusable live session.
        candidate = copy.deepcopy(self.protocol)
        raw_model = model.message(candidate, verb, value)
        candidate.receive(raw_model, peer=candidate.peer)
        if verb == 'PROVISION':
            self.writer.provision(model.encoded(value['policy']))
            observation = 'SCRATCH_PUBLIC_POLICY_SYNCED'
        elif verb == 'EMIT':
            self.writer.emit(leaf, data)
            self.upload = None
            observation = 'SCRATCH_FILE_SYNCED'
        elif verb == 'FINISH':
            self.writer.finish()
            observation = 'SCRATCH_PACKAGE_VERIFIED'
        self.protocol = candidate
        return {'observation':observation,'model_request_sha256':model.sha(raw_model),'model_step':candidate.step}

    def receive(self, raw):
        self._available()
        try:
            frame = model.codec.decode(raw)
            model.closed(frame, ('schema_version','attempt_id','selection_sha256','ordinal','verb','payload'))
            need(frame['schema_version'] == VERSION and frame['attempt_id'] == self.protocol.attempt_id and frame['selection_sha256'] == self.protocol.selection_sha256, 'transport_selection')
            need(model.integer(frame['ordinal']) and frame['ordinal'] == self.ordinal < PACKETS_MAX, 'transport_ordinal')
            verb, payload = frame['verb'], frame['payload']
            if verb == 'BLOB_BEGIN':
                model.closed(payload, ('leaf','sha256','size_bytes'))
                expected, leaf = self._expected()
                need(expected == 'EMIT' and payload['leaf'] == leaf and self.upload is None and model.hexhash(payload['sha256']) and model.integer(payload['size_bytes'],1,model.LEAF_MAX) and self.total_uploaded + payload['size_bytes'] <= model.PACKAGE_MAX, 'blob_selection_or_bound')
                if leaf == 'request.json': need(payload['size_bytes'] <= model.REQUEST_MAX, 'request_bound')
                if leaf.startswith('artifacts/'):
                    need(self.writer.artifact_total+payload['size_bytes'] <= model.ARTIFACT_TOTAL_MAX, 'artifact_bound')
                self.upload = dict(payload, data=bytearray())
                self.total_uploaded += payload['size_bytes']
                response = {'observation':'BUFFER_ONLY'}
            elif verb == 'BLOB_CHUNK':
                model.closed(payload, ('offset','bytes_base64'))
                need(self.upload is not None and model.integer(payload['offset']) and payload['offset'] == len(self.upload['data']) and type(payload['bytes_base64']) is str, 'chunk_order')
                try: data = base64.b64decode(payload['bytes_base64'], validate=True)
                except (ValueError, TypeError, binascii.Error): raise Refusal('chunk_encoding') from None
                need(0 < len(data) <= CHUNK_MAX and len(self.upload['data'])+len(data) <= self.upload['size_bytes'] and base64.b64encode(data).decode() == payload['bytes_base64'], 'chunk_bound')
                self.upload['data'].extend(data)
                response = {'observation':'BUFFER_ONLY'}
            elif verb == 'ACTION':
                response = self._action(payload)
            else:
                raise Refusal('transport_verb')
            response.update(schema_version=VERSION, ordinal=self.ordinal,
                            request_sha256=model.sha(raw), effect_ready=False)
            self.ordinal += 1
            return response
        except BaseException:
            self.poison()
            raise

    def close(self):
        if self.closed: return
        if not self.protocol.finished: self.poison()
        self.closed = True
        if self.writer is not None:
            self.writer.close()
            if self.writer.unknown: self.poison()
        self.upload = None


class Server:
    def __init__(self, endpoint, peer, session):
        need(type(session) is ScratchSession and peer == session.protocol.peer, 'server_selection')
        self.endpoint, self.peer, self.session = endpoint, peer, session
        self.closed = False

    def receive_one(self):
        need(not self.closed, 'server_closed')
        try:
            raw = wire.recv_frame(self.endpoint, self.peer)
            response = self.session.receive(raw)
            wire.send_frame(self.endpoint, model.codec.encode(response))
            return response
        except BaseException:
            self.session.poison()
            self.close()
            raise

    def close(self):
        if not self.closed:
            self.closed = True
            try:
                self.session.close()
            finally:
                try: self.endpoint.close()
                except OSError:
                    self.session.poison()
                    raise


def frame(session, verb, payload, *, ordinal=None):
    return model.codec.encode({'schema_version':VERSION,'attempt_id':session.protocol.attempt_id,
        'selection_sha256':session.protocol.selection_sha256,'ordinal':session.ordinal if ordinal is None else ordinal,
        'verb':verb,'payload':payload})
