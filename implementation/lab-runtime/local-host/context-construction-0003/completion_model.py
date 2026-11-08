"""Pure ordering model. Caller assertions are not authenticated writer evidence."""
from dataclasses import dataclass


def hex256(value):
    return type(value) is str and len(value) == 64 and all(c in '0123456789abcdef' for c in value)


@dataclass(frozen=True)
class Selection:
    attempt: str
    peer: str
    manifest_sha256: str
    manifest_request_sha256: str
    manifest_response_sha256: str
    selected_leaf_sha256: str
    finish_request_sha256: str
    finish_response_sha256: str
    model_request_sha256: str
    inventory_sha256: str
    close_receipt_sha256: str
    finish_ack_schema: str

    def __post_init__(self):
        if not (type(self.attempt) is str and self.attempt and type(self.peer) is str and self.peer and
                type(self.finish_ack_schema) is str and self.finish_ack_schema and
                all(hex256(getattr(self, name)) for name in self.__dataclass_fields__
                    if name.endswith('_sha256'))):
            raise ValueError('exact completion selection required')


@dataclass(frozen=True)
class State:
    step: str
    selected: Selection
    finish_send_count: int = 0


def begin(selected: Selection) -> State:
    if type(selected) is not Selection:
        raise ValueError('exact completion selection required')
    return State('await_manifest_ack', selected)


def _base(fields, selected, expected):
    return (type(fields) is dict and set(fields) == expected and
            fields['attempt'] == selected.attempt and fields['peer'] == selected.peer)


def _true(fields, *keys):
    return all(type(fields[key]) is bool and fields[key] is True for key in keys)


def next_state(state: State, event: str, fields: dict) -> State:
    """Exactly one FINISH send is required; all invalid transitions are sticky UNKNOWN."""
    if type(state) is not State:
        raise ValueError('exact completion state required')
    if state.step == 'UNKNOWN':
        return state
    s = state.selected
    base = {'attempt', 'peer'}
    if state.step == 'await_manifest_ack' and event == 'MANIFEST_EMIT_ACK':
        keys = base | {'ordinal', 'manifest_sha256', 'request_sha256', 'response_sha256',
                       'selected_leaf_sha256', 'prior_39_durable', 'release_private_ack',
                       'private_root_absent', 'build_result_durable', 'manifest_durable',
                       'manifest_readback_fsync'}
        if (_base(fields, s, keys) and type(fields['ordinal']) is int and fields['ordinal'] == 40 and
                fields['manifest_sha256'] == s.manifest_sha256 and
                fields['request_sha256'] == s.manifest_request_sha256 and
                fields['response_sha256'] == s.manifest_response_sha256 and
                fields['selected_leaf_sha256'] == s.selected_leaf_sha256 and
                _true(fields, 'prior_39_durable', 'release_private_ack', 'private_root_absent',
                      'build_result_durable', 'manifest_durable', 'manifest_readback_fsync')):
            return State('await_finish_send', s)
    elif state.step == 'await_finish_send' and event == 'FINISH_SENT':
        keys = base | {'ordinal', 'action_payload', 'request_sha256', 'send_count',
                       'transport_send_observed'}
        if (_base(fields, s, keys) and type(fields['ordinal']) is int and fields['ordinal'] == 41 and
                type(fields['action_payload']) is dict and fields['action_payload'] == {} and
                fields['request_sha256'] == s.finish_request_sha256 and
                type(fields['send_count']) is int and fields['send_count'] == 1 and
                _true(fields, 'transport_send_observed')):
            return State('await_finish_ack', s, 1)
    elif state.step == 'await_finish_ack' and event == 'FINISH_ACK':
        keys = base | {'ordinal', 'request_sha256', 'response_sha256', 'model_request_sha256',
                       'inventory_sha256', 'schema_version', 'effect', 'original_profile_valid',
                       'forty_leaves_valid', 'thirty_nine_rows_valid', 'writer_readback',
                       'writer_closed', 'private_root_absent', 'completion_observed'}
        if (_base(fields, s, keys) and state.finish_send_count == 1 and
                type(fields['ordinal']) is int and fields['ordinal'] == 41 and
                fields['request_sha256'] == s.finish_request_sha256 and
                fields['response_sha256'] == s.finish_response_sha256 and
                fields['model_request_sha256'] == s.model_request_sha256 and
                fields['inventory_sha256'] == s.inventory_sha256 and
                fields['schema_version'] == s.finish_ack_schema and fields['effect'] == 'none' and
                _true(fields, 'original_profile_valid', 'forty_leaves_valid',
                      'thirty_nine_rows_valid', 'writer_readback', 'writer_closed',
                      'private_root_absent', 'completion_observed')):
            return State('await_client_close', s, 1)
    elif state.step == 'await_client_close' and event == 'CLIENT_CLOSED':
        keys = base | {'close_count', 'checked', 'close_receipt_sha256'}
        if (_base(fields, s, keys) and state.finish_send_count == 1 and
                type(fields['close_count']) is int and fields['close_count'] == 1 and
                _true(fields, 'checked') and fields['close_receipt_sha256'] == s.close_receipt_sha256):
            return State('summary_permitted', s, 1)
    return State('UNKNOWN', s, state.finish_send_count)
