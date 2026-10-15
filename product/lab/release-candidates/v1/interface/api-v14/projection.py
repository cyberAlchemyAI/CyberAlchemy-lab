"""Disposable complete SQLite generations, independently checked against replay."""
import base64
import os
from pathlib import Path
import sqlite3
import tempfile
import uuid
from .artifact_model import artifact_ref,carrier,connections,references,representations
from .protocol import *

DDL=ROOT/'docs/proposals/0006-lab-artifact-storage/schemas/sqlite-read-model.sql'
DDL_SHA='586a421d5007c45772c177018d073a85a387f8fd9096e79cedec58579b5e0ee1'
DATA_TABLES=('stream_watermark','content_cache','artifact_revision','artifact_head','typed_relation_projection',
    'contract_binding_projection','reference_resolution','authority_fact_projection','ontology_representation_link','projection_gap')
LEGACY_IDENTITY={
    'cal.artifact-type.artifact-type/v1':'artifact_type_id','cal.artifact-type.artifact-type/v2':'artifact_type_id',
    'cal.artifact-type.definition/v1':'definition_id',
    **{ref:'record_id' for ref in ('cal.artifact-type.definition-registry/v1','cal.artifact-type.drift-audit/v1',
        'cal.artifact-type.evaluation-profile/v1','cal.artifact-type.foundation-manifest/v1','cal.artifact-type.lifecycle-profile/v1',
        'cal.artifact-type.owner-registry/v1','cal.artifact-type.source-admission/v1')}}


def row_digest(db):
    def value(v):return {'base64':base64.b64encode(v).decode()} if isinstance(v,bytes) else v
    rows={}
    for table in DATA_TABLES:
        entries=[[value(v) for v in row] for row in db.execute('SELECT * FROM '+table)]
        rows[table]=sorted(entries,key=lambda row:compact(row))
    return source.sha(compact(rows))


class Generation:
    def __init__(self,view,cut,schemas):
        source.original({'path':str(DDL.relative_to(ROOT)),'sha256':DDL_SHA})
        source.require(sqlite3.sqlite_version_info>=(3,37,0),'SQLite STRICT compatibility unavailable')
        self.temp=tempfile.TemporaryDirectory(prefix='cal-R03-query-generation-');self.path=Path(self.temp.name)/'read-model.sqlite'
        self.db=None
        try:
            descriptor=os.open(self.path,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);os.close(descriptor)
            self.db=sqlite3.connect(self.path);self.db.executescript(DDL.read_text())
            self.ref='generation:R03-query:'+uuid.uuid4().hex;self.cut=cut
            self.items=references(view);self.relations,self.gaps=connections(view,schemas)
            self.projector_sha=source.sha((HERE/'projection.py').read_bytes())
            catalog=view.data['projection']['contracts'];self.catalog_sha=source.sha(compact(catalog));scope=view.data['config']['scope_ref']
            db=self.db
            with db:
                db.execute('INSERT INTO projection_generation VALUES(?,?,?,?,?,?,?,?,?)',
                    (self.ref,source.sha(compact(cut)),source.PINS.profile_sha256,self.projector_sha,self.catalog_sha,'0'*64,'building',0,'none'))
                for stream in cut['streams']:
                    db.execute('INSERT INTO stream_watermark VALUES(?,?,?,?)',(self.ref,stream['stream_ref'],stream['cursor'],stream['head_sha256']))
                for subject in sorted(view.subjects.values(),key=lambda s:s['version_ref']):
                    header=artifact_ref(view,subject);facets=source.facets(subject);binding=subject['source']
                    package=('store:'+binding['store_id']) if 'store_id' in binding else 'repository:'+view.data['baseline']['snapshot_digest']
                    declared=representations.row(view,subject)
                    entry=declared['source_locator'] if declared else binding['path']+('#'+binding['selector'] if binding.get('selector') else '')
                    db.execute('INSERT INTO artifact_revision VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                        (self.ref,scope,subject['version_ref'],header['identity_ref'],header['carrier_ref'],subject['category'],subject['kind'],
                        header['byte_sha256'],view.handle.common.digest(representations.body(view,subject)),'inherited-json-structural-sha256',package,entry,
                        facets['admission'],facets['domain'],facets['implementation'],facets['runtime_observation'],facets['outcome']))
                    # Exact bytes cache is optional. Populate only available originals;
                    # stale whole-file bytes cannot be reconstructed from parsed bodies.
                    from .artifact_model import record_bytes
                    try:raw,_,_,_=record_bytes(view,subject)
                    except Exception:raw=None
                    if raw is not None:
                        db.execute('INSERT OR IGNORE INTO content_cache VALUES(?,?,?,?)',(header['byte_sha256'],'application/json',len(raw),raw))
                candidates={}
                for subject in view.subjects.values():
                    if subject['effective_state'] in ('admitted-current','local-admitted-current'):
                        candidates.setdefault(artifact_ref(view,subject)['identity_ref'],[]).append(subject['version_ref'])
                for identity,versions in sorted(candidates.items()):
                    if len(versions)==1:
                        db.execute('INSERT INTO artifact_head VALUES(?,?,?,?)',(self.ref,scope,identity,versions[0]))
                    else:self.gaps.append({'subject_ref':identity,'reason':'Multiple independently captured eligible current revisions; no unique artifact head selected from admission posture.'})
                for row in self.relations:
                    c=row['connection'];a=c['source']['artifact'];b=c['target']['artifact'];qualifiers=compact(c['qualifiers'])
                    db.execute('INSERT INTO typed_relation_projection VALUES(?,?,?,?,?,?,?,?,?,?)',(self.ref,scope,row['version_ref'],row['kind_version_ref'],
                        a['scope_ref'],a['version_ref'],b['scope_ref'],b['version_ref'],source.sha(qualifiers),qualifiers))
                for ref,contract in sorted(catalog.items()):
                    source.require(ref in view.subjects,'catalog descriptor revision absent from source inventory')
                    d=contract['instance_discriminator']
                    field=contract['artifact'].get('instance_contract',{}).get('identity_field') or LEGACY_IDENTITY.get(ref)
                    source.require(field is not None,'exact declared contract identity selector missing')
                    db.execute('INSERT INTO contract_binding_projection VALUES(?,?,?,?,?,?,?,?)',(self.ref,scope,ref,contract['schema_sha256'],
                        contract.get('schema_selector'),'/'+field,d['path'],d['value']))
                for i,g in enumerate(self.gaps):
                    db.execute('INSERT INTO projection_gap VALUES(?,?,?,?,?,?,?)',(self.ref,'gap:R03-query:'+str(i),scope,g['subject_ref'],
                        'unclosed-typed-connection','R03/S02/R08','use-needing-connection-closure'))
                # Verify complete population against independently replayed source
                # metadata before making this private generation ready/selected.
                actual=[{'scope_ref':scope,'identity_ref':identity,'version_ref':version,'carrier_ref':c,'byte_sha256':digest}
                    for version,identity,c,digest in db.execute('SELECT version_ref,identity_ref,carrier_ref,byte_sha256 FROM artifact_revision ORDER BY version_ref')]
                source.require(actual==self.items,'complete generation differs from original canonical revisions')
                source.require(db.execute('SELECT count(*) FROM typed_relation_projection').fetchone()[0]==len(self.relations)
                    and db.execute('SELECT count(*) FROM contract_binding_projection').fetchone()[0]==len(catalog),'generation relation/contract population incomplete')
                source.require(db.execute('PRAGMA integrity_check').fetchall()==[('ok',)]
                    and db.execute('PRAGMA foreign_key_check').fetchall()==[],'generation failed integrity before ready selection')
                source.require(all(source.sha(raw)==digest and len(raw)==size for digest,size,raw in db.execute('SELECT byte_sha256,size_bytes,content FROM content_cache')),
                    'generation exact-byte cache differs before ready selection')
                self.expected_rows=row_digest(db)
                db.execute('UPDATE projection_generation SET derived_rows_sha256=?,posture=? WHERE generation_ref=?',(self.expected_rows,'ready',self.ref))
                db.execute('INSERT INTO active_generation VALUES(?,?)',('artifact-read-model',self.ref))
            self.metadata=tuple(db.execute('SELECT * FROM projection_generation').fetchone())
            self.expected_file_sha=source.sha(self.path.read_bytes())
            self.binding={'ref':self.ref,'sha256':source.sha(compact({'metadata':list(self.metadata),'file_sha256':self.expected_file_sha,'cut':cut}))}
            self.verify()
            db.execute('PRAGMA query_only=ON')
        except Exception:self.close();raise
    def verify(self):
        source.require(self.db is not None and not self.path.is_symlink() and self.path.is_file(),'projection unavailable')
        source.require(source.sha((HERE/'projection.py').read_bytes())==self.projector_sha,'projector changed')
        source.original({'path':str(DDL.relative_to(ROOT)),'sha256':DDL_SHA})
        source.require(source.sha(self.path.read_bytes())==self.expected_file_sha,'independently captured projection file changed')
        source.require(self.db.execute('PRAGMA integrity_check').fetchall()==[('ok',)]
            and self.db.execute('PRAGMA foreign_key_check').fetchall()==[],'SQLite integrity/foreign keys differ')
        source.require(tuple(self.db.execute('SELECT * FROM projection_generation').fetchone())==self.metadata
            and self.db.execute('SELECT * FROM active_generation').fetchall()==[('artifact-read-model',self.ref)]
            and row_digest(self.db)==self.expected_rows,'generation/rows/pointer differ from independently captured expected state')
        source.require(self.metadata[1]==source.sha(compact(self.cut)) and self.metadata[6:] == ('ready',0,'none'),'generation cut/posture differs')
    def query(self,message):
        self.verify();scope=message['scope_refs'][0]
        # Parameterized SQL discovers seeds and exact typed endpoints. Client values
        # never become SQL identifiers, clauses, paths or expressions.
        placeholders=','.join('?' for _ in message['carrier_refs'])
        params=[self.ref,scope,*message['carrier_refs']]
        statement='SELECT version_ref,identity_ref,carrier_ref,byte_sha256 FROM artifact_revision WHERE generation_ref=? AND scope_key=? AND carrier_ref IN ('+placeholders+')'
        identities=message['identity_refs']
        if identities:
            marks=','.join('?' for _ in identities);statement+=' AND (identity_ref IN ('+marks+') OR version_ref IN ('+marks+'))';params.extend(identities);params.extend(identities)
        seeds=self.db.execute(statement,params).fetchall()
        versions={r[0] for r in seeds};frontier=set(versions);seen_relations={}
        by_relation={r['version_ref']:r for r in self.relations}
        kinds=set(message['relation_kind_refs'])
        for _ in range(message['max_depth']):
            following=set()
            for version in sorted(frontier):
                edges=self.db.execute('SELECT relation_version_ref,source_version_ref,target_version_ref FROM typed_relation_projection WHERE generation_ref=? AND (source_version_ref=? OR target_version_ref=?)',(self.ref,version,version)).fetchall()
                for ref,a,b in edges:
                    row=by_relation[ref]
                    if kinds and row['connection']['relation_kind_ref'] not in kinds:continue
                    seen_relations[ref]=row;following.update(v for v in (a,b) if v not in versions)
            versions.update(following);frontier=following
            if not frontier:break
        items=[]
        for version in sorted(versions):
            identity,c,digest=self.db.execute('SELECT identity_ref,carrier_ref,byte_sha256 FROM artifact_revision WHERE generation_ref=? AND scope_key=? AND version_ref=?',(self.ref,scope,version)).fetchone()
            items.append({'scope_ref':scope,'identity_ref':identity,'version_ref':version,'carrier_ref':c,'byte_sha256':digest})
        return items,[seen_relations[v] for v in sorted(seen_relations)]
    def close(self):
        if self.db is not None:self.db.close();self.db=None
        self.temp.cleanup()
