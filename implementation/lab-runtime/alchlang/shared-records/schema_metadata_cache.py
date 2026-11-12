"""Bounded, process-local reuse of exact successful JSON-schema metadata checks."""
import json
from collections import OrderedDict

def install(validator_class, maximum=128):
    if "__lab_schema_metadata_cache__" in validator_class.__dict__:
        return validator_class.__dict__["__lab_schema_metadata_cache__"]
    if not isinstance(maximum, int) or isinstance(maximum, bool) or maximum < 1 or maximum > 128:
        raise ValueError("schema-metadata-cache-bound")
    original = validator_class.check_schema.__func__
    successful = OrderedDict()
    stats = {"hits": 0, "misses": 0, "bypassed": 0, "size": 0, "maximum": maximum}

    def is_json(value):
        if type(value) in (str, int, float, bool, type(None)):
            return True
        if type(value) is list:
            return all(is_json(v) for v in value)
        if type(value) is dict:
            return all(type(k) is str and is_json(v) for k, v in value.items())
        return False

    @classmethod
    def checked(cls, schema, *args, **kwargs):
        if args or kwargs or not is_json(schema):
            stats["bypassed"] += 1
            return original(cls, schema, *args, **kwargs)
        try:
            encoded = json.dumps(schema, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        except (ValueError, TypeError):
            stats["bypassed"] += 1
            return original(cls, schema)
        key = (cls, encoded)
        if key in successful:
            successful.move_to_end(key)
            stats["hits"] += 1
            return None
        stats["misses"] += 1
        result = original(cls, schema)
        successful[key] = True
        if len(successful) > maximum:
            successful.popitem(last=False)
        stats["size"] = len(successful)
        return result

    validator_class.check_schema = checked
    validator_class.__lab_schema_metadata_cache__ = stats
    return stats
