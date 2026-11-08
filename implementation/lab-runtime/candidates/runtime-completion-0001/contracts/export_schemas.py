"""Print the finite closed schema bundle; caller exclusively stores the result."""
import json
from lab_contracts.schema_catalog import DEFS
from lab_contracts import dispatch_schema

if __name__ == '__main__':
    print(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema',
        '$id':'urn:lab-completion:closed-contracts:v1', '$defs':DEFS},indent=2,sort_keys=True))
