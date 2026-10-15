"""Compute the unchanged record stamp with invocation-local immutable byte reuse.

Every distinct immutable byte object is hashed during this invocation. Mutable
buffers are always hashed again. Keeping the byte object alongside its identity
prevents identity reuse; nothing survives the invocation.
"""


def record_stamp(rows, encoded, digest, metrics=None):
    memo = {}
    counts = {'digest_calls': 0, 'hashed_bytes': 0, 'immutable_reuses': 0}

    def hashed(raw):
        if type(raw) is bytes:
            known = memo.get(id(raw))
            if known is not None and known[0] is raw:
                counts['immutable_reuses'] += 1
                return known[1]
        value = digest(raw)
        counts['digest_calls'] += 1
        counts['hashed_bytes'] += len(raw)
        if type(raw) is bytes:
            memo[id(raw)] = (raw, value)
        return value

    def witness(value):
        if value is None:
            return None
        return {'source_cut': value.source_cut, 'artifact_ref': value.artifact_ref,
                'enclosing_sha256': value.enclosing_sha256,
                'actual_enclosing_sha256': hashed(value.enclosing_original),
                'selector': value.selector, 'encoding': value.encoding}

    result = encoded([
        {'artifact': row.artifact, 'raw_sha256': hashed(row.original),
         'posture': row.posture, 'source_ref': row.source_ref,
         'witness': witness(row.revision_witness)} for row in rows
    ])
    if metrics is not None:
        metrics.update(counts)
    return result
