"""Original JSON values, preserving bytes separately from signed-control codecs."""
import math
from lab_contracts.codec import Refusal, need
from lab_selectors.anchors import legacy_json

MAX_BYTES = 64 * 1024 * 1024

def parse_original(raw, *, max_bytes=MAX_BYTES):
    need(type(max_bytes) is int and 0 < max_bytes <= MAX_BYTES, 'ORIGINAL_LIMIT')
    need(type(raw) is bytes and len(raw) <= max_bytes, 'ORIGINAL_BYTES')
    try:
        value = legacy_json(raw)
        pending = [(value, 0)]
        while pending:
            item, depth = pending.pop()
            need(depth <= 64, 'ORIGINAL_DEPTH')
            if type(item) is float:
                need(math.isfinite(item), 'ORIGINAL_NONFINITE')
            elif type(item) is str:
                need(not any(0xD800 <= ord(c) <= 0xDFFF for c in item), 'ORIGINAL_UNICODE')
            elif type(item) is dict:
                pending.extend((child, depth + 1) for pair in item.items() for child in pair)
            elif type(item) is list:
                pending.extend((child, depth + 1) for child in item)
            else:
                need(item is None or type(item) in (int, bool), 'ORIGINAL_TYPE')
        return value
    except Exception:
        raise Refusal('ORIGINAL_JSON_REFUSED') from None
