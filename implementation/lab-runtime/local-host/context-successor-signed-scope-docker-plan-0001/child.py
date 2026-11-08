"""Non-executable child placeholder for the signed-scope Docker projection."""
import json
import sys

EFFECT_ENABLED=False

def main(argv):
    if argv==['--self-check']:
        return {'schema':'context-signed-scope-child-placeholder/v1',
                'effect':'NOT_RUN','private_source':'UNOPENED',
                'checked_closure':'PORTABLE_BUNDLE_UNIMPLEMENTED'}
    raise RuntimeError('EFFECT_DISABLED_NO_SIGNED_READER_OR_PRIVATE_OPEN')

if __name__=='__main__':
    print(json.dumps(main(sys.argv[1:]),sort_keys=True))
