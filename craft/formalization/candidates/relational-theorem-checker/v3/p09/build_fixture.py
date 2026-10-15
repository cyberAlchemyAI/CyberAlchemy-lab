"""Read-only legacy fixture construction for a bounded two-layout comparison."""
from pathlib import Path
import copy
import json
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
sys.path.insert(0,str(BASE.parent))
from v3.p03.context import C,V2,binding
sys.path.insert(0,str(V2/'s06'));import runtime as legacy
before=legacy.ext.c.fixture();after=legacy.ext.example(before)
request=C.decode((BASE/'p01/request-fixture.json').read_bytes())
request['proposal']=legacy.proposal(before,after,'P09-bounded-two-layout-cycle')
request['layout']='staged';C.validate('request',request)
(HERE/'layout-request.json').write_text(json.dumps(request,indent=2)+'\n')
(HERE/'fixture-origin.json').write_text(json.dumps({'schema':'relational.regression-fixture-origin/v3','request':binding(HERE/'layout-request.json'),
    'generator':binding(Path(__file__)),'legacy_constructor':binding(Path(legacy.ext.__file__)),'baseline_constructor':binding(Path(legacy.ext.c.__file__)),
    'source_profile':request['source_profile'],'scope':'Bounded representative of the same supported v2 profile; rich target/scope application coverage remains separately bound to P08.',
    'authority_effect':'none'},indent=2)+'\n')
print('Bounded two-layout fixture constructed:',len(before['inference']['predicates']),'to',len(after['inference']['predicates']),'predicates')
