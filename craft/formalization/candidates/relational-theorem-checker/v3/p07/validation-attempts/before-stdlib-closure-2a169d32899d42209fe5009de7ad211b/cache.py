"""Expected cache metadata comes from accepted P02, never from the cache itself."""
from pathlib import Path
import hashlib
from ..p03.context import BASE,V2,C,check,read,binding,require

class CacheAnchor:
    def __init__(self,layout):
        require(layout in ['combined','staged'],'unknown cache layout policy')
        receipt=read(BASE/'p02/task-acceptance.json')
        require(receipt['result']=='accepted','P02 anchor not accepted')
        report_path=BASE/'p02/layout-equivalence-report.json'
        expected=next(r for r in receipt['artifacts'] if Path(r['path']).name==report_path.name)
        # check() resolves against the pinned repository root and checks bytes.
        require(check(expected)==report_path,'unexpected independent cache anchor report')
        self.expected=read(report_path)['inherited_dependency_binding']
        require(check(self.expected)==V2/'s13/build/dependencies.json','alternate cache metadata rejected')
        self.metadata=read(check(self.expected))
        self.references=[binding(BASE/'p02/task-acceptance.json'),expected,self.expected]
        for m in self.metadata['modules']:
            check(m['source']);check(m['olean']);self.references += [m['source'],m['olean']]
        formal=BASE.parent/'v1/formal';lock=read(formal/'toolchain-lock.json')
        self.references += [binding(formal/'toolchain-lock.json'),binding(formal/'.toolcache/lean-4.33.1-linux/bin/lean'),binding(formal/'.toolcache/lean-4.33.1-linux/lib/lean/libleanshared.so'),binding(BASE/'p01/catalog.json'),binding(BASE/'p02/proof_layout.py')]
        self.key=C.identity({'schema':'relational.dependency-cache-key/v3',
                             'source_and_compiled_closure':self.metadata['modules'],
                             'compiler':lock['lean_binary_sha256'],'kernel':lock['lean_shared_library_sha256'],
                             'catalog':C.identity(C.catalog()),'generator':binding(BASE/'p02/proof_layout.py'),
                             'layout':layout,'layout_policy':'exact-structured-sections-v3'})
        self.verify()

    def verify_metadata_bytes(self,raw):
        require(hashlib.sha256(raw).hexdigest()==self.expected['sha256'],'cache metadata differs from independently accepted anchor')
        return C.decode(raw)

    def verify(self):
        for ref in self.references:check(ref)
        self.verify_metadata_bytes(check(self.expected).read_bytes())
        return {'schema':'relational.cache-check/v3','cache_key':self.key,'anchor':self.expected,
                'checked':self.references,'fresh_qualification':False,'authority_effect':'none'}
