"""Expected cache metadata comes from accepted P02, never from the cache itself."""
from pathlib import Path
import hashlib
from ..p03.context import BASE,ROOT,V2,C,check,read,binding,require
from ..p05.bindings import Resolver

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
        audit_receipt=read(BASE/'p05/task-acceptance.json');require(audit_receipt['result']=='accepted','P05 closure not accepted')
        audit=BASE/'p05/current-source-report.json'
        self.closure_expected=next(r for r in audit_receipt['artifacts'] if Path(r['path']).name==audit.name)
        require(check(self.closure_expected)==audit,'unexpected independent imported closure report')
        report=self.verify_closure_bytes(audit.read_bytes())
        require(report['result']=='pass' and not report['failures'],'imported source audit failed')
        unique={C.identity(r):r for r in report['verified_bindings'] if r['kind']=='toolchain'}
        self.imports=sorted(unique.values(),key=lambda r:(r['path'],r['sha256']))
        require(self.imports,'imported toolchain closure missing')
        self.resolver=Resolver()
        # Memoization only skips a repeat byte hash for the same inode/size/
        # mtime and expected digest. It never supplies an expected digest.
        for r in self.imports:self.resolver.check(r)
        self.references += [binding(BASE/'p05/task-acceptance.json'),self.closure_expected]
        self.import_references=[{'path':str(self.resolver.locate(r).relative_to(ROOT)),'sha256':r['sha256']} for r in self.imports]
        self.key=C.identity({'schema':'relational.dependency-cache-key/v3',
                             'source_and_compiled_closure':self.metadata['modules'],
                             'imported_toolchain_closure':self.imports,
                             'compiler':lock['lean_binary_sha256'],'kernel':lock['lean_shared_library_sha256'],
                             'catalog':C.identity(C.catalog()),'generator':binding(BASE/'p02/proof_layout.py'),
                             'layout':layout,'layout_policy':'exact-structured-sections-v3'})
        self.verify()

    def verify_closure_bytes(self,raw):
        require(hashlib.sha256(raw).hexdigest()==self.closure_expected['sha256'],'imported closure differs from independently accepted P05 report')
        return C.decode(raw)

    def verify_metadata_bytes(self,raw):
        require(hashlib.sha256(raw).hexdigest()==self.expected['sha256'],'cache metadata differs from independently accepted anchor')
        return C.decode(raw)

    def verify(self):
        for ref in self.references:check(ref)
        self.verify_metadata_bytes(check(self.expected).read_bytes())
        for ref in self.imports:self.resolver.check(ref)
        return {'schema':'relational.cache-check/v3','cache_key':self.key,'anchor':self.expected,
                'checked':self.references+self.import_references,'fresh_qualification':False,'authority_effect':'none'}
