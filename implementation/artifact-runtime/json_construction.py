"""Bounded JSON encoding from explicit native construction values; no domain policy.

This is an encoder, not an expression evaluator: it has no calls, conditions,
filters, field discovery or business defaults. Construction choices are inputs.
"""
import re
from copy import deepcopy
from exact_io import Refusal, bound, decode, encode, pointer, require

MAX_SAFE = 2 ** 53 - 1

def uint(value):
    require(type(value) is int or isinstance(value, str) and re.fullmatch(r"0|[1-9][0-9]*", value), "invalid-uint")
    number = int(value)
    require(0 <= number <= MAX_SAFE, "inexact-json-number")
    return number

def variant(value):
    require(isinstance(value, dict) and set(value) == {"tag", "fields"}, "invalid-encoding-variant")
    require(isinstance(value["tag"], str) and isinstance(value["fields"], dict), "invalid-encoding-variant")
    return value["tag"], value["fields"]

def concat_parts(parts, documents=None):
    require(isinstance(parts, list) and len(parts) <= 100, "invalid-construction-concat")
    output = []
    for part in parts:
        kind, data = variant(part)
        if kind == "Text":
            require(set(data) == {"value"} and isinstance(data["value"], str), "invalid-construction-text")
            output.append(data["value"])
        elif kind == "DocumentText":
            require(set(data)=={'document','selector'} and documents is not None and data['document'] in documents,'invalid-construction-source-fragment')
            selected=pointer(documents[data['document']],data['selector']);require(isinstance(selected,str),'invalid-construction-text')
            output.append(selected)
        elif kind == "DocumentUInt":
            require(set(data)=={'document','selector','width'} and documents is not None and data['document'] in documents,'invalid-construction-source-fragment')
            width=uint(data['width']);require(width<=256,'construction-padding-bound')
            output.append(str(uint(pointer(documents[data['document']],data['selector']))).zfill(width))
        elif kind == "UInt":
            require(set(data) == {"value", "width"}, "invalid-construction-padding")
            width = uint(data["width"])
            require(width <= 256, "construction-padding-bound")
            output.append(str(uint(data["value"])).zfill(width))
        else:
            raise Refusal("invalid-construction-concat", "Only text and exact integer fragments may be encoded")
    result = "".join(output)
    require(len(result.encode("utf-8")) <= 16777216, "construction-output-bound")
    return result

def path_parts(path, documents=None):
    require(isinstance(path, list) and len(path) <= 64, "construction-depth")
    result = []
    for part in path:
        tag, fields = variant(part)
        if tag == "Field":
            require(set(fields) == {"name"} and isinstance(fields["name"], str), "invalid-construction-field")
            # Strict JSON encoding validates all Unicode, including names.
            encode(fields["name"])
            result.append(fields["name"])
        elif tag == "FieldParts":
            require(set(fields) == {"parts"}, "invalid-construction-field")
            result.append(concat_parts(fields["parts"], documents))
        elif tag == "Index":
            require(set(fields) == {"value"}, "invalid-construction-index")
            result.append(uint(fields["value"]))
        else:
            raise Refusal("invalid-construction-path", "Unknown JSON path component")
    return result

def read_sources(root, rows):
    require(isinstance(rows, list) and len(rows) <= 256, "construction-source-bound")
    documents = {}
    total = 0
    for row in rows:
        require(isinstance(row, dict) and set(row) == {"id", "binding"}, "invalid-construction-source")
        identity = row["id"]
        require(isinstance(identity, str) and identity and identity not in documents, "duplicate-construction-source")
        raw = bound(root, row["binding"])
        total += len(raw)
        require(total <= 67108864, "construction-source-budget")
        documents[identity] = decode(raw, source=True)
    return documents

def construct(batches, documents):
    require(isinstance(batches, list) and 0 < len(batches) <= 41, "construction-batch-bound")
    absent = object()
    output = absent
    targets = set()
    count = 0
    size = 0
    for batch in batches:
        require(isinstance(batch, list) and 0 < len(batch) <= 100, "construction-batch-bound")
        for step in batch:
            count += 1
            require(count <= 4096 and isinstance(step, dict) and set(step) == {"target", "value"}, "construction-step-bound")
            target = path_parts(step["target"], documents)
            key = tuple((type(item).__name__, item) for item in target)
            require(key not in targets, "construction-overwrite")
            tag, fields = variant(step["value"])
            if tag in ("Object", "Array", "Null"):
                require(set(fields) == {"marker"} and type(fields["marker"]) is bool, "invalid-construction-marker")
                value = {} if tag == "Object" else [] if tag == "Array" else None
            elif tag == "Text":
                require(set(fields) == {"value"} and isinstance(fields["value"], str), "invalid-construction-text")
                value = fields["value"]
            elif tag == "UInt":
                require(set(fields) == {"value"}, "invalid-construction-uint")
                value = uint(fields["value"])
            elif tag == "Bool":
                require(set(fields) == {"value"} and type(fields["value"]) is bool, "invalid-construction-bool")
                value = fields["value"]
            elif tag == "Copy":
                require(set(fields) == {"document", "selector"} and fields["document"] in documents, "construction-source-missing")
                value = pointer(documents[fields["document"]], fields["selector"])
            elif tag == "UIntText":
                require(set(fields) == {"document", "selector"} and fields["document"] in documents, "construction-source-missing")
                value = str(uint(pointer(documents[fields["document"]], fields["selector"])))
            elif tag == "Concat":
                require(set(fields) == {"parts"} and isinstance(fields["parts"], list) and len(fields["parts"]) <= 100, "invalid-construction-concat")
                value = concat_parts(fields["parts"], documents)
            else:
                raise Refusal("unsupported-construction-value", "Unknown JSON encoding value")
            size += len(encode(value)) + sum(len(str(part).encode("utf-8")) for part in target)
            require(size <= 16777216, "construction-output-bound")
            value = deepcopy(value)
            if not target:
                require(output is absent, "construction-overwrite")
                output = value
            else:
                require(output is not absent, "construction-parent-missing")
                parent = output
                for part in target[:-1]:
                    if type(part) is int:
                        require(isinstance(parent, list) and part < len(parent), "construction-parent-missing")
                    else:
                        require(isinstance(parent, dict) and part in parent, "construction-parent-missing")
                    parent = parent[part]
                last = target[-1]
                if type(last) is int:
                    require(isinstance(parent, list) and last == len(parent), "construction-sparse-or-overwrite")
                    parent.append(value)
                else:
                    require(isinstance(parent, dict) and last not in parent, "construction-overwrite")
                    parent[last] = value
            targets.add(key)
    require(output is not absent, "construction-empty")
    raw = encode(output)
    require(len(raw) <= 16777216, "construction-output-bound")
    return output, raw
