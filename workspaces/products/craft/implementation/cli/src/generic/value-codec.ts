/** Inert, source-derived storage representation. This module grants no read or codec execution.
 * Open Questions: docs/GENERIC-APPLICATIONS.md#open-questions. */
import {createHash} from 'node:crypto';
import {coreFreeze,coreSourceFail as fail} from '../commerce/commerce-core-syntax.js';
import {dataDigest} from '../profile-engine/contracts.js';
import {assertGenericRepositoryPlanOwner,type GenericRepositoryPlanOwner,type GenericKeyedApplicationHandle,type GenericServicePlanHandle} from './repository-plan.js';
import type {GenericRecordDefinitionV1} from './computation-data-v1.js';
import type {ValueTypeV1} from '../commerce/commerce-data-v1.js';
import type {GenericSqlResultColumnV1,GenericSqlMaterializationV1} from './query-data-v1.js';
import type {GenericTransactionApplicationHandle} from './repository-plan.js';
import type {GenericTransactionApplicationContractV1,GenericTransactionBoundsV1,GenericTransactionStorageDescriptorV1,GenericTransactionStorageTableV1,GenericTransactionSqlMaterializationV1,GenericTransactionSqlResultColumnV1,GenericCommandJournalDescriptorV1,GenericCommandSqlColumnV1,GenericTransactionMetadataMaterializationV1} from './transaction-data-v1.js';
import type {GenericExternalTransactionApplicationV1} from './external-read-data-v1.js';
import type {GenericExternalWriteTransactionApplicationV1} from './external-write-data-v1.js';
import type {GenericEventTransactionApplicationV1} from './event-data-v1.js';
const at={path:'generic-storage-layout',start:0,end:0},q=(s:string)=>'"'+s.replaceAll('"','""')+'"',hex=(s:string)=>Buffer.from(s,'utf8').toString('hex'),sha=(s:string)=>createHash('sha256').update(s).digest('hex');
export interface GenericStorageColumn {readonly name:string;readonly sql_name:string;readonly type:ValueTypeV1;readonly nullable:boolean}
export interface GenericStorageTable {readonly entity:string;readonly service:string;readonly physical_name:string;readonly columns:readonly GenericStorageColumn[];readonly keys:readonly (readonly string[])[];readonly record:GenericRecordDefinitionV1;readonly row_column:'_craft_row';readonly key_columns:readonly string[];readonly create_sql:string;readonly indexes:readonly string[];readonly insert_sql:string}
export interface GenericStorageDescriptor {readonly schema_version:'craft.generic-sqlite-storage/v1-candidate';readonly service:string;readonly value_bytes_max:number;readonly tables:readonly GenericStorageTable[];readonly materializations:readonly GenericSqlMaterializationV1[];readonly storage_projection_sha256:string;readonly authority_effect:'none'}
/** Produces SQL only from an original accepted application and actual service child. */
export function deriveGenericStorageDescriptor(plans:GenericRepositoryPlanOwner,application:GenericKeyedApplicationHandle,serviceHandle:GenericServicePlanHandle):GenericStorageDescriptor{
 assertGenericRepositoryPlanOwner(plans);plans.assertChild(serviceHandle,application);const app=plans.inspect(application).contract,service=plans.inspectService(serviceHandle),limit=Math.min(app.limits.max_value_bytes,524288);
 if(app.schema_version!=='craft.generic-keyed-application/v1-candidate'||app.admission_mode!=='keyed-query-entry')fail('UnsupportedCapability',at,'actual keyed application required');
 const tables:GenericStorageTable[]=app.values.records.filter(r=>r.role==='Entity'&&(r.name.startsWith(service.module+'.'))).map(record=>{
  const identity=record.entity;if(!identity?.identity.length)fail('InvalidContract',at,'Entity identity required');const keys=[identity.identity,...identity.unique];if(Object.keys(record.fields).length>64||keys.length>16||keys.some(k=>!k.length||k.length>16))fail('ResourceLimit',at,'bounded Entity storage layout exceeded');
  const physical_name='craft_'+hex(service.id)+'_'+hex(record.name),columns=Object.entries(record.fields).sort(([a],[b])=>a.localeCompare(b)).map(([name,type])=>({name,sql_name:'f_'+hex(name),type,nullable:type.kind==='optional'})),key_columns=keys.map((_,i)=>'_craft_key_'+i);
  const fields=columns.map(c=>{const n=q(c.sql_name);return n+' TEXT'+(c.nullable?'':' NOT NULL');}),hidden=[q('_craft_row')+' BLOB NOT NULL',...key_columns.map(k=>q(k)+' BLOB NOT NULL')],names=[...columns.map(c=>c.sql_name),'_craft_row',...key_columns];
  return {entity:record.name,service:service.id,physical_name,columns,keys,record,row_column:'_craft_row',key_columns,create_sql:'CREATE TABLE '+q(physical_name)+' ('+[...fields,...hidden,'PRIMARY KEY ('+q(key_columns[0]!)+')'].join(', ')+') STRICT;',indexes:key_columns.slice(1).map((k,i)=>'CREATE UNIQUE INDEX '+q(physical_name+'_unique_'+i)+' ON '+q(physical_name)+' ('+q(k)+');'),insert_sql:'INSERT INTO '+q(physical_name)+' ('+names.map(q).join(',')+') VALUES ('+names.map(()=>'?').join(',')+')'};
 });
 const materializations:GenericSqlMaterializationV1[]=app.queries.filter(x=>x.service===service.id).map(query=>{
  const table=tables.find(t=>t.entity===query.source.entity);if(!table)fail('InvalidContract',at,'Query Entity is not owned by its service');const selected=table.keys[query.key.index];if(!selected||dataDigest(selected)!==dataDigest(query.key.fields.map(f=>f.field)))fail('InvalidContract',at,'actual selected key differs from Entity');
  const base=[...table.columns.map(c=>({name:c.name,sql_name:c.sql_name,representation:'text' as const,nullable:c.nullable,role:'field' as const})),{name:'_craft_row',sql_name:'_craft_row',representation:'blob' as const,nullable:false,role:'canonical-row' as const},...table.key_columns.map(k=>({name:k,sql_name:k,representation:'blob' as const,nullable:false,role:'key' as const}))];
  if(base.length>81)fail('ResourceLimit',at,'physical storage cells exceeded');const columns:GenericSqlResultColumnV1[]=base.map((c,i)=>({...c,type_alias:'m_t_'+i,length_alias:'m_n_'+i,payload_alias:'p_'+i,max_bytes:limit}));
  const length=(c:GenericSqlResultColumnV1)=>'coalesce(octet_length('+q(c.sql_name)+'),0)',shape=columns.map(c=>'('+((c.nullable?'typeof('+q(c.sql_name)+")='null' OR ":''))+"typeof("+q(c.sql_name)+")='"+c.representation+"')").join(' AND '),dataLength=columns.filter(c=>c.role==='field').map(length).join('+')||'0',aggregate=columns.map(length).join('+'),bound=[...columns.map(c=>length(c)+'<='+limit),'('+dataLength+')<='+limit,'('+aggregate+')<='+((table.keys.length+2)*limit)].join(' AND '),guard='('+shape+') AND ('+bound+')';
  const sql='SELECT '+[...columns.flatMap(c=>['typeof('+q(c.sql_name)+') AS '+q(c.type_alias),length(c)+' AS '+q(c.length_alias),'CASE WHEN '+guard+' THEN '+q(c.sql_name)+' ELSE NULL END AS '+q(c.payload_alias)]),'CASE WHEN '+shape+' THEN 1 ELSE 0 END AS "m_shape"','CASE WHEN '+bound+' THEN 1 ELSE 0 END AS "m_bound"'].join(',')+' FROM '+q(table.physical_name)+' WHERE '+q(table.key_columns[query.key.index]!)+'=? LIMIT 2';
  if(Buffer.byteLength(sql,'utf8')>1048576)fail('ResourceLimit',at,'bounded SQL text exceeded');
  return {schema_version:'craft.generic-sql-materialization/v1-candidate',query:query.query,entity:table.entity,service:service.id,selected_key_index:query.key.index,sql,sql_sha256:sha(sql),columns,database_encoding:'UTF-8',rows_max:2,value_bytes_max:limit,data_bytes_max:limit,aggregate_bytes_max:(table.keys.length+2)*limit,shape_alias:'m_shape',bound_alias:'m_bound',guard:'whole-row-case-before-js-materialization/v1',length_measure:'octet_length-utf8/v1'};
 });
 // This source/schema projection is joined with the genuine selected native identity
 // by the repository owner before storage metadata is accepted. Provenance is excluded.
 const inspection=plans.inspect(application),compatibility={representation:'sqlite-keyed-canonical-values/v1-candidate',service:service.id,value_bytes_max:limit,tables,executable_semantics_sha256:inspection.executable_semantics_sha256,profile_sha256:inspection.derivation.profile_sha256};
 const result=coreFreeze({schema_version:'craft.generic-sqlite-storage/v1-candidate' as const,service:service.id,value_bytes_max:limit,tables,materializations,storage_projection_sha256:dataDigest(compatibility),authority_effect:'none' as const});plans.assertCurrent(application);return result;
}

// C08 is a separate layout. The old producer only gains an explicit keyed-mode guard.
const transactionJournalTable='_craft_generic_commands_v1' as const;
const transactionJournalCreate='CREATE TABLE "_craft_generic_commands_v1" (tuple_sha256 TEXT PRIMARY KEY, tuple BLOB NOT NULL, payload_sha256 TEXT NOT NULL, payload BLOB NOT NULL, result_sha256 TEXT NOT NULL, result BLOB NOT NULL, permission_trace BLOB NOT NULL, execution_fuel INTEGER NOT NULL, record_bytes INTEGER NOT NULL) STRICT;' as const;
const transactionJournalInsert='INSERT INTO "_craft_generic_commands_v1" (tuple_sha256,tuple,payload_sha256,payload,result_sha256,result,permission_trace,execution_fuel,record_bytes) VALUES (?,?,?,?,?,?,?,?,?)' as const;
const transactionMetadataCreate='CREATE TABLE "_craft_generic_metadata" (id INTEGER PRIMARY KEY CHECK(id=1), store_id TEXT NOT NULL, compatibility TEXT NOT NULL, revision_counter BLOB NOT NULL CHECK(typeof(revision_counter)=\'blob\' AND length(revision_counter)=8), command_count INTEGER NOT NULL CHECK(command_count>=0), command_bytes INTEGER NOT NULL CHECK(command_bytes>=0)) STRICT;' as const;

function transactionSql(text:string):string{
 if(Buffer.byteLength(text,'utf8')>1048576)fail('ResourceLimit',at,'bounded transaction SQL text exceeded');
 return text;
}

/** UTF8 is checked inside SQLite, without handing compatibility text to JS.
 * Recursion carries at most 1027 bytes: a 1024-byte working window and three
 * lookahead bytes for the last possible four-byte scalar. Windows advance only
 * at complete scalar boundaries. This avoids copying the whole TEXT for every
 * byte. The outer CASE bounds the scan before the CTE starts; malformed input
 * stops at its first invalid sequence. No raw compatibility TEXT reaches JS.
 */
function transactionUtf8SQL(value:string,limit:number):string{
 const blob='CAST('+value+' AS BLOB)',size='octet_length('+value+')';
 const byte=(n:number)=>'hex(substr(u.b,u.p+'+n+',1))';
 const between=(n:number,low:string,high:string)=>'('+byte(n)+" BETWEEN '"+low+"' AND '"+high+"')";
 const next=between(1,'80','BF'),third=between(2,'80','BF'),fourth=between(3,'80','BF');
 const width='CASE WHEN '+between(0,'00','7F')+' THEN 1 WHEN '+between(0,'C2','DF')+' AND '+next+' THEN 2 WHEN (('+byte(0)+"='E0' AND "+between(1,'A0','BF')+') OR ('+between(0,'E1','EC')+' AND '+next+') OR ('+byte(0)+"='ED' AND "+between(1,'80','9F')+') OR ('+between(0,'EE','EF')+' AND '+next+')) AND '+third+' THEN 3 WHEN (('+byte(0)+"='F0' AND "+between(1,'90','BF')+') OR ('+between(0,'F1','F3')+' AND '+next+') OR ('+byte(0)+"='F4' AND "+between(1,'80','8F')+')) AND '+third+' AND '+fourth+' THEN 4 ELSE 0 END';
 const advance='u.p+('+width+')',refill='('+advance+')>1024',start='u.s+('+advance+')-1';
 return '(CASE WHEN typeof('+value+")='text' AND "+size+'<='+limit+' THEN NOT EXISTS (WITH RECURSIVE u(s,p,b,n) AS (SELECT 1,1,substr('+blob+',1,1027),'+size+' UNION ALL SELECT CASE WHEN '+refill+' THEN '+start+' ELSE u.s END,CASE WHEN '+refill+' THEN 1 ELSE '+advance+' END,CASE WHEN '+refill+' THEN substr('+blob+','+start+',1027) ELSE u.b END,u.n FROM u WHERE u.s+u.p-1<=u.n AND ('+width+')>0) SELECT 1 FROM u WHERE u.s+u.p-1<=u.n AND ('+width+')=0) ELSE 0 END)';
}

function transactionMetadataSQL(bounds:GenericTransactionBoundsV1):GenericTransactionMetadataMaterializationV1{
 const n=(field:string)=>q(field),len=(field:string)=>'octet_length('+n(field)+')';
 const uuidPattern=[8,4,4,4,12].map(k=>'[0-9a-f]'.repeat(k)).join('-');
 const shape=["typeof(id)='integer'",'id=1',"typeof(store_id)='text'",len('store_id')+'=36',"store_id GLOB '"+uuidPattern+"'",transactionUtf8SQL(n('compatibility'),1048576),"typeof(revision_counter)='blob'",len('revision_counter')+'=8',"typeof(command_count)='integer'","typeof(command_bytes)='integer'",'command_count>=0','command_bytes>=0'].map(x=>'('+x+')').join(' AND ');
 const bound='command_count<='+bounds.max_command_records+' AND command_bytes<='+bounds.max_command_journal_bytes;
 const equal='('+len('compatibility')+'=octet_length(?1) AND compatibility COLLATE BINARY=?1 COLLATE BINARY)';
 const heldEqual='('+len('store_id')+'=octet_length(?2) AND store_id COLLATE BINARY=?2 COLLATE BINARY)';
 const make=(held:boolean)=>{
  const identity=equal+(held?' AND '+heldEqual:''),guard='c_shape=1 AND c_bound=1 AND c_identity=1';
  const payload=['revision_counter','command_count','command_bytes',...(held?[]:['store_id'])].map(c=>'CASE WHEN '+guard+' THEN '+n(c)+' ELSE NULL END AS '+q('m_'+c));
  // Materialization evaluates the expensive UTF8 predicate once per selected
  // row. LIMIT is inside the CTE so malformed extra rows cannot expand the scan.
  return transactionSql('WITH checked AS MATERIALIZED (SELECT revision_counter,command_count,command_bytes,store_id,CASE WHEN '+shape+' THEN 1 ELSE 0 END AS c_shape,CASE WHEN '+bound+' THEN 1 ELSE 0 END AS c_bound,CASE WHEN '+identity+' THEN 1 ELSE 0 END AS c_identity FROM "_craft_generic_metadata" LIMIT 2) SELECT '+[...payload,'c_shape AS m_shape','c_bound AS m_bound','CASE WHEN '+guard+' THEN 1 ELSE 0 END AS m_identity'].join(',')+' FROM checked');
 };
 const open_sql=make(false),held_sql=make(true),valid="typeof(record_bytes)='integer' AND record_bytes>=0 AND record_bytes<=16777216";
 const occupancy_sql=transactionSql('SELECT count(*) AS m_count,coalesce(sum(CASE WHEN '+valid+' THEN record_bytes ELSE 0 END),0) AS m_bytes,coalesce(max(CASE WHEN '+valid+' THEN 0 ELSE 1 END),0) AS m_malformed FROM (SELECT record_bytes FROM "_craft_generic_commands_v1" LIMIT 1025)');
 return {schema_version:'craft.generic-transaction-metadata-materialization/v1-candidate',table:'_craft_generic_metadata',open_sql,open_sql_sha256:sha(open_sql),held_sql,held_sql_sha256:sha(held_sql),occupancy_sql,occupancy_sql_sha256:sha(occupancy_sql),rows_max:2,store_id_bytes:36,compatibility_bytes_max:1048576,revision_bytes:8,command_records_max:bounds.max_command_records,command_bytes_max:bounds.max_command_journal_bytes,occupancy_rows_max:1025,guard:'metadata-identity-equality-and-whole-row-case-before-js/v1',snapshot:'same-original-sqlite-snapshot-as-occupancy/v1',compatibility_payload:'never-returned-to-js',held_store_id_payload:'never-returned-to-js'};
}

function transactionJournalSQL(app:GenericTransactionApplicationContractV1|GenericExternalTransactionApplicationV1|GenericExternalWriteTransactionApplicationV1|GenericEventTransactionApplicationV1):GenericCommandJournalDescriptorV1{
 const bounds=app.transaction_bounds,tupleMax=bounds.max_command_tuple_bytes,payloadMax=Math.min(app.limits.max_input_bytes,65536),resultMax=Math.min(app.limits.max_output_bytes,65536),traceMax=bounds.max_permission_trace_bytes;
 const specs:readonly [GenericCommandSqlColumnV1['name'],GenericCommandSqlColumnV1['representation'],number][]=[['tuple_sha256','text',64],['tuple','blob',tupleMax],['payload_sha256','text',64],['payload','blob',payloadMax],['result_sha256','text',64],['result','blob',resultMax],['permission_trace','blob',traceMax],['execution_fuel','integer',8],['record_bytes','integer',8]];
 const columns:GenericCommandSqlColumnV1[]=specs.map(([name,representation,max_bytes],i)=>({name,representation,max_bytes,type_alias:'j_t_'+i,length_alias:'j_n_'+i,payload_alias:'j_p_'+i}));
 const length=(c:GenericCommandSqlColumnV1)=>c.representation==='integer'?'(CASE WHEN typeof('+q(c.name)+")='integer' THEN 8 ELSE 0 END)":'coalesce(octet_length('+q(c.name)+'),0)';
 const shape=columns.map(c=>{
  const name=q(c.name),type="typeof("+name+")='"+c.representation+"'";
  if(c.representation==='integer')return '('+type+' AND '+name+'>=0 AND '+name+'<=9007199254740991)';
  if(c.representation==='text')return '('+type+' AND octet_length('+name+')=64 AND length('+name+')=64 AND '+name+" NOT GLOB '*[^0-9a-f]*')";
  return '('+type+')';
 }).join(' AND ');
 const recordBytes='(192+octet_length(tuple)+octet_length(payload)+octet_length(result)+octet_length(permission_trace)+16)';
 const bound=[...columns.map(c=>length(c)+'<='+c.max_bytes),...columns.filter(c=>c.representation==='blob').map(c=>length(c)+'>=1'),'record_bytes='+recordBytes,'record_bytes<='+bounds.max_command_journal_bytes].map(x=>'('+x+')').join(' AND '),guard='('+shape+') AND ('+bound+')';
 const sql=transactionSql('SELECT '+[...columns.flatMap(c=>['typeof('+q(c.name)+') AS '+q(c.type_alias),length(c)+' AS '+q(c.length_alias),'CASE WHEN '+guard+' THEN '+q(c.name)+' ELSE NULL END AS '+q(c.payload_alias)]),'CASE WHEN '+shape+' THEN 1 ELSE 0 END AS j_shape','CASE WHEN '+bound+' THEN 1 ELSE 0 END AS j_bound'].join(',')+' FROM '+q(transactionJournalTable)+' WHERE tuple_sha256 COLLATE BINARY=?1 COLLATE BINARY LIMIT 2');
 return {table:transactionJournalTable,create_sql:transactionJournalCreate,insert_sql:transactionJournalInsert,materialization:{schema_version:'craft.generic-command-journal-materialization/v1-candidate',table:transactionJournalTable,sql,sql_sha256:sha(sql),columns,rows_max:2,shape_alias:'j_shape',bound_alias:'j_bound',guard:'whole-command-case-before-js-materialization/v1',length_measure:'octet_length-utf8/v1',tuple_bytes_max:tupleMax,payload_bytes_max:payloadMax,result_bytes_max:resultMax,permission_trace_bytes_max:traceMax,record_accounting:'three-ascii-sha256-plus-four-blobs-plus-two-u64/v1'},mutation_policy:'original-owner-insert-and-read-only/v1',update_sql:null,delete_sql:null,pruning:false};
}

/** Inert SQL construction; only the public original-owner wrapper invokes this.
 * It is not exported and cannot grant an observation, mutation or transaction.
 */
function transactionStorageLayout(app:GenericTransactionApplicationContractV1|GenericExternalTransactionApplicationV1|GenericExternalWriteTransactionApplicationV1|GenericEventTransactionApplicationV1,service:{readonly id:string;readonly module:string},executable:string,profile:string):GenericTransactionStorageDescriptorV1{
 const limit=Math.min(app.limits.max_value_bytes,524288);
 const tables:GenericTransactionStorageTableV1[]=app.values.records.filter(r=>r.role==='Entity'&&r.name.startsWith(service.module+'.')).map(record=>{
  const identity=record.entity;if(!identity?.identity.length)fail('InvalidContract',at,'Entity identity required');
  const keys=[identity.identity,...identity.unique];if(Object.keys(record.fields).length>64||keys.length>16||keys.some(k=>!k.length||k.length>16))fail('ResourceLimit',at,'bounded Entity storage layout exceeded');
  const columns=Object.entries(record.fields).sort(([a],[b])=>Buffer.compare(Buffer.from(a),Buffer.from(b))).map(([name,type])=>({name,sql_name:'f_'+hex(name),type,nullable:type.kind==='optional'})),physical_name='craft_'+hex(service.id)+'_'+hex(record.name),key_columns=keys.map((_,i)=>'_craft_key_'+i),immutable=new Set(keys.flat());
  const fields=columns.map(c=>q(c.sql_name)+' TEXT'+(c.nullable?'':' NOT NULL')),hidden=[q('_craft_row')+' BLOB NOT NULL',...key_columns.map(k=>q(k)+' BLOB NOT NULL'),q('_craft_revision')+" BLOB NOT NULL CHECK(typeof(\"_craft_revision\")='blob' AND length(\"_craft_revision\")=8 AND \"_craft_revision\"!=X'0000000000000000')"],names=[...columns.map(c=>c.sql_name),'_craft_row',...key_columns,'_craft_revision'];
  const updateNames=[...columns.filter(c=>!immutable.has(c.name)).map(c=>c.sql_name),'_craft_row','_craft_revision'];
  return {entity:record.name,service:service.id,physical_name,columns,keys,record,row_column:'_craft_row',key_columns,revision_column:'_craft_revision',revision_encoding:'uint64-big-endian-nonzero/v1',create_sql:transactionSql('CREATE TABLE '+q(physical_name)+' ('+[...fields,...hidden,'PRIMARY KEY ('+q(key_columns[0]!)+')'].join(', ')+') STRICT;'),indexes:key_columns.slice(1).map((k,i)=>transactionSql('CREATE UNIQUE INDEX '+q(physical_name+'_unique_'+i)+' ON '+q(physical_name)+' ('+q(k)+');')),insert_sql:transactionSql('INSERT INTO '+q(physical_name)+' ('+names.map(q).join(',')+') VALUES ('+names.map(()=>'?').join(',')+')'),update_sql:transactionSql('UPDATE '+q(physical_name)+' SET '+updateNames.map(k=>q(k)+'=?').join(',')+' WHERE '+q(key_columns[0]!)+'=? AND "_craft_revision"=?')};
 });
 if(!tables.length||tables.length>256)fail('ResourceLimit',at,'bounded nonempty transaction Entity layout required');
 const materializations:GenericTransactionSqlMaterializationV1[]=app.queries.filter(x=>x.service===service.id).map(query=>{
  const table=tables.find(t=>t.entity===query.source.entity);if(!table)fail('InvalidContract',at,'Query Entity is not owned by its service');
  const selected=table.keys[query.key.index];if(!selected||dataDigest(selected)!==dataDigest(query.key.fields.map(f=>f.field)))fail('InvalidContract',at,'actual selected key differs from Entity');
  const base=[...table.columns.map(c=>({name:c.name,sql_name:c.sql_name,representation:'text' as const,nullable:c.nullable,role:'field' as const})),{name:'_craft_row',sql_name:'_craft_row',representation:'blob' as const,nullable:false,role:'canonical-row' as const},...table.key_columns.map(k=>({name:k,sql_name:k,representation:'blob' as const,nullable:false,role:'key' as const}))];
  if(base.length+1>82)fail('ResourceLimit',at,'physical transaction storage cells exceeded');
  const columns:GenericTransactionSqlResultColumnV1[]=[...base.map((c,i)=>({...c,type_alias:'m_t_'+i,length_alias:'m_n_'+i,payload_alias:'p_'+i,max_bytes:limit})),{name:'_craft_revision',sql_name:'_craft_revision',representation:'blob',nullable:false,role:'hidden-revision',type_alias:'m_t_'+base.length,length_alias:'m_n_'+base.length,payload_alias:'p_'+base.length,max_bytes:8}];
  const length=(c:GenericTransactionSqlResultColumnV1)=>'coalesce(octet_length('+q(c.sql_name)+'),0)';
  const shape=columns.map(c=>'('+((c.nullable?'typeof('+q(c.sql_name)+")='null' OR ":''))+"typeof("+q(c.sql_name)+")='"+c.representation+"')").concat(["octet_length(\"_craft_revision\")=8","\"_craft_revision\"!=X'0000000000000000'"]).map(x=>'('+x+')').join(' AND ');
  const dataLength=columns.filter(c=>c.role==='field').map(length).join('+')||'0',aggregate=columns.map(length).join('+'),aggregateLimit=(table.keys.length+2)*limit+8;
  const bound=[...columns.map(c=>length(c)+'<='+c.max_bytes),'('+dataLength+')<='+limit,'('+aggregate+')<='+aggregateLimit].join(' AND '),guard='('+shape+') AND ('+bound+')';
  const sql=transactionSql('SELECT '+[...columns.flatMap(c=>['typeof('+q(c.sql_name)+') AS '+q(c.type_alias),length(c)+' AS '+q(c.length_alias),'CASE WHEN '+guard+' THEN '+q(c.sql_name)+' ELSE NULL END AS '+q(c.payload_alias)]),'CASE WHEN '+shape+' THEN 1 ELSE 0 END AS m_shape','CASE WHEN '+bound+' THEN 1 ELSE 0 END AS m_bound'].join(',')+' FROM '+q(table.physical_name)+' WHERE '+q(table.key_columns[query.key.index]!)+'=? LIMIT 2');
  return {schema_version:'craft.generic-transaction-sql-materialization/v1-candidate',query:query.query,entity:table.entity,service:service.id,selected_key_index:query.key.index,sql,sql_sha256:sha(sql),columns,database_encoding:'UTF-8',rows_max:2,value_bytes_max:limit,data_bytes_max:limit,aggregate_bytes_max:aggregateLimit,shape_alias:'m_shape',bound_alias:'m_bound',guard:'whole-row-case-before-js-materialization/v1',length_measure:'octet_length-utf8/v1',revision_column:'_craft_revision',revision_encoding:'uint64-big-endian-nonzero/v1',revision_guard:'blob-exactly-eight-nonzero-before-js/v1'};
 });
 if(materializations.length>256)fail('ResourceLimit',at,'bounded transaction Query materializations exceeded');
 const journal=transactionJournalSQL(app),metadata={table:'_craft_generic_metadata' as const,create_sql:transactionMetadataCreate,revision_encoding:'uint64-big-endian-counter-zero-initial/v1' as const,revision_max_hex:'ffffffffffffffff' as const,materialization:transactionMetadataSQL(app.transaction_bounds)};
 const compatibility={representation:'sqlite-atomic-command-values/v1-candidate',service:service.id,application_namespace:app.application_namespace,value_bytes_max:limit,tables,materializations,journal,metadata,transaction_bounds:app.transaction_bounds,executable_semantics_sha256:executable,profile_sha256:profile};
 return coreFreeze({schema_version:'craft.generic-sqlite-atomic-storage/v1-candidate',service:service.id,value_bytes_max:limit,tables,materializations,journal,metadata,storage_projection_sha256:dataDigest(compatibility),authority_effect:'none'});
}

/** A genuine accepted transaction application and its service child are required.
 * No caller-supplied contract, descriptor or callback is accepted as authority.
 */
export function deriveGenericTransactionStorageDescriptor(plans:GenericRepositoryPlanOwner,application:GenericTransactionApplicationHandle,serviceHandle:GenericServicePlanHandle):GenericTransactionStorageDescriptorV1{
 assertGenericRepositoryPlanOwner(plans);plans.assertChild(serviceHandle,application);
 const inspection=plans.inspect(application),app=inspection.contract;
 if(!((app.schema_version==='craft.generic-transaction-application/v1-candidate'&&app.admission_mode==='atomic-state-entry')||(app.schema_version==='craft.generic-transaction-application/v2-candidate'&&app.admission_mode==='external-read-entry')))fail('UnsupportedCapability',at,'actual atomic transaction application required');
 const result=transactionStorageLayout(app,plans.inspectService(serviceHandle),inspection.executable_semantics_sha256,inspection.derivation.profile_sha256);
 plans.assertCurrent(application);return result;
}

/** Derive the existing atomic SQLite layout from an actual checked V3 source.
 * This is a storage projection; dispatch still requires the original owner. */
export function deriveGenericExternalWriteStorageDescriptor(plans:GenericRepositoryPlanOwner,application:GenericTransactionApplicationHandle,serviceHandle:GenericServicePlanHandle):GenericTransactionStorageDescriptorV1{
 assertGenericRepositoryPlanOwner(plans);plans.assertChild(serviceHandle,application);
 const inspection=plans.inspectSourceApplication(application),app=inspection.contract;
 if(app.schema_version!=='craft.generic-transaction-application/v3-candidate'||
    app.admission_mode!=='external-write-entry'||
    app.execution_policy!=='refused-until-original-durable-external-owner')
   fail('UnsupportedCapability',at,'actual checked V3 external-write source required');
 const result=transactionStorageLayout(app,plans.inspectService(serviceHandle),
  inspection.executable_semantics_sha256,inspection.derivation.profile_sha256);
 plans.assertCurrent(application);return result;
}

/** V4 adds profile-owned outbox/inbox tables to this same atomic layout. The
 * repository joins those tables to the one command transaction, not this inert
 * projection. Existing V1–V3 layouts remain byte-for-byte unchanged. */
export function deriveGenericEventStorageDescriptor(plans:GenericRepositoryPlanOwner,application:GenericTransactionApplicationHandle,serviceHandle:GenericServicePlanHandle):GenericTransactionStorageDescriptorV1{
 assertGenericRepositoryPlanOwner(plans);plans.assertChild(serviceHandle,application);
 const inspection=plans.inspectSourceApplication(application),app=inspection.contract as unknown as GenericEventTransactionApplicationV1;
 if(app.schema_version!=='craft.generic-transaction-application/v4-candidate'||
    app.admission_mode!=='event-handoff-entry'||app.execution_policy!=='original-durable-event-handoff'||
    !Array.isArray(app.event_bindings)||
    !Array.isArray(app.external_bindings)||!Array.isArray(app.write_bindings)||
    Boolean(app.write_bindings.length)!==Boolean(app.identity_limits))
   fail('UnsupportedCapability',at,'actual checked V4 event handoff source required');
 const service=plans.inspectService(serviceHandle);
 const finiteWorkflow=app.event_bindings.length===0&&plans.inspectWorkflows(application).some(workflow=>
   workflow.service===service.id&&workflow.source_capture_sha256===inspection.source_capture_sha256&&
   workflow.base_application_sha256===dataDigest(app)&&workflow.steps.length>0&&workflow.steps.every(step=>!!step.continuation_entry));
 if(!finiteWorkflow&&!app.event_bindings.some(binding=>binding.producer_service===service.id||binding.target_service===service.id))
   fail('UnsupportedCapability',at,'selected service has no original event handoff binding');
 const result=transactionStorageLayout(app,service,inspection.executable_semantics_sha256,inspection.derivation.profile_sha256);
 plans.assertCurrent(application);return result;
}
