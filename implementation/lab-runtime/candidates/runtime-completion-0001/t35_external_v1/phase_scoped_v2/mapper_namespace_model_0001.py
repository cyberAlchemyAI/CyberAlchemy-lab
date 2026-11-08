"""Pure Stage1 models. All identity/pidfd observations are untrusted synthetic data.

No socket, proc, process, filesystem or randomness adapter exists here. A successful
model result is not host evidence, peer authentication or namespace admission.
"""
import hashlib
import json


class Refusal(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise Refusal(code)


def closed(value, keys):
    require(type(value) is dict and set(value) == set(keys.split()), 'SHAPE')


def integer(value, low=0, high=(1 << 63) - 1):
    require(type(value) is int and low <= value <= high, 'INTEGER')


def digest(value):
    require(type(value) is str and len(value) == 64
            and all(c in '0123456789abcdef' for c in value), 'DIGEST')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def parse(raw):
    require(type(raw) is bytes and 0 < len(raw) <= 8192, 'FRAME_SIZE')
    try:
        value = json.loads(raw, object_pairs_hook=_pairs,
                           parse_constant=lambda _: require(False, 'NUMBER'))
        require(canonical(value) == raw, 'NONCANONICAL')
        return value
    except Refusal:
        raise
    except (ValueError, UnicodeError, RecursionError, TypeError, OverflowError):
        raise Refusal('FRAME_ENCODING') from None


def peer(value, measurement=False):
    require(type(value) is list and len(value) == 3, 'PEER')
    integer(value[0], 0 if measurement else 1, (1 << 31) - 1)
    integer(value[1], 0, (1 << 32) - 2)
    integer(value[2], 0, (1 << 32) - 2)


def ancillary(records, *, truncated=False, control_truncated=False):
    """Synthetic ancillary parser only; rights are reported, never closed here.

    The caller of a future real recvmsg adapter must collect/close ALL rights
    before this refusal. This function cannot distinguish explicit credentials.
    """
    require(type(truncated) is bool and type(control_truncated) is bool, 'FLAGS')
    require(not truncated and not control_truncated, 'TRUNCATED')
    require(type(records) is list and len(records) == 1, 'ANCILLARY')
    closed(records[0], 'kind tuple')
    require(records[0]['kind'] == 'SCM_CREDENTIALS', 'ANCILLARY')
    peer(records[0]['tuple'], measurement=True)
    return tuple(records[0]['tuple'])


def outbound_policy(method, ancillary_records):
    """Decision only. No sender callable is accepted or invoked."""
    require(type(method) is str and method == 'send', 'SEND_POLICY')
    require(type(ancillary_records) is list and not ancillary_records, 'SEND_POLICY')
    return 'ORDINARY_SEND_NO_ANCILLARY'


def send_result(size, result):
    integer(size, 1, 8192)
    if type(result) is str and result == 'EAGAIN_BEFORE_QUEUE':
        return 'RETRY_SAME_UNSENT_BYTES_WITHIN_ORIGINAL_DEADLINE'
    require(type(result) is int and result == size, 'SEND_UNKNOWN')
    return 'QUEUED'


class Exchange:
    """Closed transcript validator. Refusal permanently fences this model.

    Caller supplies the selected nonce/digest. It does not generate a nonce or
    prove selection provenance. Four frames bind exact prior canonical bytes.
    """
    schedule = (('controller', 'CHALLENGE'), ('payload', 'HELLO'),
                ('controller', 'OBSERVATION'), ('payload', 'RECEIPT'))

    def __init__(self, nonce, selection_sha256, *, identity_sha256,
                 namespaces_sha256, join_sha256):
        digest(nonce)
        digest(selection_sha256)
        for value in (identity_sha256, namespaces_sha256, join_sha256):
            digest(value)
        self.identity_sha256 = identity_sha256
        self.namespaces_sha256 = namespaces_sha256
        self.join_sha256 = join_sha256
        self.nonce = nonce
        self.selection = selection_sha256
        self.index = 0
        self.previous = None
        self.total = 0
        self.failed = False
        self.hello = None
        self.observation = None

    def accept(self, sender, raw):
        require(not self.failed, 'EXCHANGE_FENCED')
        try:
            require(self.index < 4, 'EXCHANGE_COMPLETE')
            f = parse(raw)
            closed(f, 'schema kind ordinal nonce selection_sha256 previous_sha256 body')
            require(f['schema'] == 'lab-mapper-namespace-probe/v1', 'SCHEMA')
            require(type(sender) is str and (sender, f['kind']) == self.schedule[self.index], 'ORDER')
            integer(f['ordinal'], 0, 3)
            require(f['ordinal'] == self.index, 'ORDER')
            digest(f['nonce']); digest(f['selection_sha256'])
            require((f['nonce'], f['selection_sha256']) == (self.nonce, self.selection), 'SELECTION')
            require(f['previous_sha256'] == self.previous, 'FRAME_CHAIN')
            if self.index == 0:
                closed(f['body'], '')
            elif self.index == 1:
                closed(f['body'], 'inner_pid parent_pid namespaces_sha256 identity_sha256 fd_census controller_tuple')
                integer(f['body']['inner_pid'], 1, (1 << 31) - 1)
                integer(f['body']['parent_pid'], 0, (1 << 31) - 1)
                require(f['body']['inner_pid'] == 1, 'INNER_PID')
                digest(f['body']['namespaces_sha256']); digest(f['body']['identity_sha256'])
                require(f['body']['namespaces_sha256'] == self.namespaces_sha256
                        and f['body']['identity_sha256'] == self.identity_sha256, 'HELLO_IDENTITY')
                require(f['body']['fd_census'] == [0, 1, 2, 3]
                        and all(type(x) is int for x in f['body']['fd_census']), 'FD_CENSUS')
                peer(f['body']['controller_tuple'], measurement=True)
            elif self.index == 2:
                closed(f['body'], 'hello_sha256 join_sha256 claim')
                digest(f['body']['join_sha256'])
                require(f['body']['join_sha256'] == self.join_sha256, 'JOIN_BINDING')
                require(f['body']['hello_sha256'] == self.hello, 'HELLO_BINDING')
                require(f['body']['claim'] == 'synthetic-identity-consistency-only', 'CLAIM')
            else:
                closed(f['body'], 'observation_sha256 controller_tuple')
                require(f['body']['observation_sha256'] == self.observation, 'OBSERVATION_BINDING')
                peer(f['body']['controller_tuple'], measurement=True)
                require(f['body']['controller_tuple'] == self.controller_tuple, 'CONTROLLER_DRIFT')
            require(self.total + len(raw) <= 49152, 'AGGREGATE')
            self.previous = sha(raw)
            if self.index == 1:
                self.hello = self.previous
                self.controller_tuple = list(f['body']['controller_tuple'])
            if self.index == 2:
                self.observation = self.previous
            self.index += 1
            self.total += len(raw)
            return self.previous
        except Refusal:
            self.failed = True
            raise

    def finish(self):
        if self.failed or self.index != 4:
            self.failed = True
            raise Refusal('INCOMPLETE_UNKNOWN')
        return {'claim': 'synthetic-transcript-only', 'sha256': self.previous,
                'frames': self.index, 'bytes': self.total, 'host_qualified': False}


def ns(value):
    require(type(value) is list and len(value) == 2, 'NAMESPACE')
    for x in value:
        integer(x, 1)


def id_map(value):
    """Already-parsed range rows, coordinates inner -> immediate outer.

    Raw proc parsing and multi-level composition are intentionally not provided.
    """
    require(type(value) is list and 0 < len(value) <= 64, 'MAP_SIZE')
    seen = [[], []]
    for row in value:
        require(type(row) is list and len(row) == 3, 'MAP_ROW')
        for x in row:
            integer(x, 0, (1 << 32) - 1)
        require(row[2] > 0, 'MAP_ROW')
        for axis in (0, 1):
            lo, hi = row[axis], row[axis] + row[2]
            require(hi <= (1 << 32) - 1, 'MAP_OVERFLOW')
            require(all(hi <= a or lo >= b for a, b in seen[axis]), 'MAP_OVERLAP')
            seen[axis].append((lo, hi))


def project(value, rows):
    integer(value, 0, (1 << 32) - 2)
    id_map(rows)
    matches = [b + value - a for a, b, n in rows if a <= value < a + n]
    require(len(matches) == 1, 'UNMAPPED_ID')
    return matches[0]


def snapshot(v):
    closed(v, 'observer_pidns observer_userns pid start ppid nspid uid gid namespaces caps no_new_privs uid_map gid_map map_outer_userns setgroups exe_sha256 exe_identity pidfd_live original_sha256 original_size')
    ns(v['observer_pidns']); ns(v['observer_userns']); ns(v['map_outer_userns'])
    integer(v['pid'], 1, (1 << 31) - 1); integer(v['start'], 1)
    integer(v['ppid'], 0, (1 << 31) - 1)
    require(type(v['nspid']) is list and 0 < len(v['nspid']) <= 32, 'NSPID')
    for x in v['nspid']: integer(x, 1, (1 << 31) - 1)
    require(v['nspid'][0] == v['pid'], 'NSPID')
    for name in ('uid', 'gid'):
        require(type(v[name]) is list and len(v[name]) == 4, 'IDS')
        for x in v[name]: integer(x, 0, (1 << 32) - 2)
    closed(v['namespaces'], 'pid pid_for_children user mount')
    for x in v['namespaces'].values(): ns(x)
    closed(v['caps'], 'inheritable permitted effective bounding ambient')
    for x in v['caps'].values():
        require(type(x) is str and len(x) == 16 and all(c in '0123456789abcdef' for c in x), 'CAPS')
    integer(v['no_new_privs'], 0, 1)
    id_map(v['uid_map']); id_map(v['gid_map'])
    require(type(v['setgroups']) is str and v['setgroups'] in ('allow', 'deny', 'unavailable'), 'SETGROUPS')
    digest(v['exe_sha256']); ns(v['exe_identity']); digest(v['original_sha256'])
    integer(v['original_size'], 1, 4 * 1024 * 1024)
    require(type(v['pidfd_live']) is bool and v['pidfd_live'], 'PIDFD')


def decide(selection, before, after, payload_claim, observed_tuple):
    """Synthetic model only; no booleans or JSON here mint genuine evidence.

    The model supports one explicitly labelled immediate user-map relation. A
    missing/multi-level relation is refused for a future selected adapter.
    """
    closed(selection, 'schema nonce selection_sha256 observer_pidns observer_userns wrapper_pid wrapper_start exe_sha256 exe_identity')
    require(selection['schema'] == 'lab-mapper-synthetic-identity-selection/v1', 'SELECTION_SCHEMA')
    digest(selection['nonce']); digest(selection['selection_sha256'])
    ns(selection['observer_pidns']); ns(selection['observer_userns'])
    integer(selection['wrapper_pid'], 1, (1 << 31) - 1); integer(selection['wrapper_start'], 1)
    digest(selection['exe_sha256']); ns(selection['exe_identity'])
    peer(observed_tuple)
    total = 0
    for chain in (before, after):
        require(type(chain) is list and 2 <= len(chain) <= 32, 'LINEAGE_SIZE')
        for item in chain:
            snapshot(item)
            require(item['observer_pidns'] == selection['observer_pidns']
                    and item['observer_userns'] == selection['observer_userns'], 'OBSERVER')
            total += item['original_size']
        require(len({x['pid'] for x in chain}) == len(chain), 'LINEAGE_CYCLE')
        require(total <= 4 * 1024 * 1024, 'EVIDENCE_BOUND')
        for child, parent in zip(chain, chain[1:]):
            require(child['ppid'] == parent['pid'], 'LINEAGE')
        require((chain[-1]['pid'], chain[-1]['start']) ==
                (selection['wrapper_pid'], selection['wrapper_start']), 'WRAPPER')
    stable = lambda chain: [{k: v for k, v in item.items()
                             if k not in ('original_sha256', 'original_size')}
                            for item in chain]
    require(stable(before) == stable(after), 'IDENTITY_DRIFT')
    p = before[0]
    require(observed_tuple == [p['pid'], p['uid'][0], p['gid'][0]], 'OBSERVED_TUPLE')
    require(p['nspid'][-1] == 1 and len(p['nspid']) >= 2, 'INNER_PID')
    require(p['namespaces']['pid'] != selection['observer_pidns'], 'PID_NAMESPACE')
    require((p['exe_sha256'], p['exe_identity']) ==
            (selection['exe_sha256'], selection['exe_identity']), 'EXECUTABLE')
    closed(payload_claim, 'nonce selection_sha256 inner_pid namespaces caps no_new_privs uid gid uid_map gid_map map_outer_userns setgroups')
    require((payload_claim['nonce'], payload_claim['selection_sha256']) ==
            (selection['nonce'], selection['selection_sha256']), 'CLAIM_SELECTION')
    integer(payload_claim['inner_pid'], 1, (1 << 31) - 1)
    require(payload_claim['inner_pid'] == 1, 'INNER_PID')
    for name in ('namespaces', 'caps', 'no_new_privs', 'uid_map', 'gid_map', 'map_outer_userns', 'setgroups'):
        require(canonical(payload_claim[name]) == canonical(p[name]), 'CLAIM_' + name.upper())
    require(p['map_outer_userns'] == selection['observer_userns'], 'MAP_COORDINATES')
    for name in ('uid', 'gid'):
        require(type(payload_claim[name]) is list and len(payload_claim[name]) == 4, 'CLAIM_IDS')
        require([project(x, p[name + '_map']) for x in payload_claim[name]] == p[name], 'CLAIM_IDS')
    return {'schema': 'lab-mapper-synthetic-identity-decision/v1',
            'claim': 'synthetic-identity-consistency-only', 'host_qualified': False,
            'joined_sha256': sha(canonical({'selection': selection, 'before': before,
                                            'after': after, 'claim': payload_claim,
                                            'observed_tuple': observed_tuple}))}
