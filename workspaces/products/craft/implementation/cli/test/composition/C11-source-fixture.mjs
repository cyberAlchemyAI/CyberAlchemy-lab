import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,cpSync,unlinkSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import os from 'node:os';
import path from 'node:path';
import {createCoreCommerceSourceOwner} from '../../src/commerce/commerce-core-source-owner.ts';
import {createGenericSemanticOwner} from '../../src/generic/semantic-reconstruction.ts';
import {createGenericSourceReviewOwner} from '../../src/generic/source-review-owner.ts';
import {createGenericRepositoryPlanOwner} from '../../src/generic/repository-plan.ts';
import {captureExternalProfile,generateExternalBusinessSources} from '../../src/generic/external-read-profile.ts';
import {createExternalApiComposition} from '../../src/generic/external-read-source.ts';
import {reconstructCoreCommerceSources} from '../../src/commerce/commerce-core-reconstruction.ts';
const repo=fileURLToPath(new URL('../../../../../../../',import.meta.url));
const fixtureBase=path.join(repo,'implementation/craft-alchlang-generic-applications-2026-10-18-r5/evidence/C10/first-happy-installed-context-005/first-happy/probe-attempt-001/consumer/tmp/craft-atomic-expanded-vQDQS7');


export function build(domain,sharedMapping=false,selectedBounds={}){
const root=path.join(mkdtempSync(path.join(os.tmpdir(),'craft-c11-v3-plan-')),'model');
cpSync(fixtureBase,root,{recursive:true});
 if(domain!=='ReviewDesk'){
  for(const rel of ['business.alch','application.alch','contracts/external-profile.json','contracts/selected-profile.json','contracts/http-profile.json','contracts/external-generation.json']){
   const p=path.join(root,rel),v=readFileSync(p,'utf8');writeFileSync(p,v.replaceAll('ReviewDesk',domain).replaceAll('review-desk',domain.toLowerCase()+'-desk').replaceAll('reviewdesk',domain.toLowerCase()));
  }
 }
if(Object.keys(selectedBounds).length)for(const rel of ['contracts/transactions.json','contracts/selected-profile.json']){
 const file=path.join(root,rel),value=JSON.parse(readFileSync(file,'utf8'));
 const bounds=rel.endsWith('selected-profile.json')?value.transaction_bounds:value;
 for(const [key,limit] of Object.entries(selectedBounds))bounds[key]=limit;
 writeFileSync(file,JSON.stringify(value,null,2)+'\n');
}
mkdirSync(path.join(root,'native'));
let business=readFileSync(path.join(root,'business.alch'),'utf8');
business+=`

value-object ProviderCurrency:
  carrier String
  utf8-bytes 3..3
  unicode-scalars 3..3
  pattern "^USD$"

value-object ProviderStatus:
  carrier String
  utf8-bytes 7..20
  unicode-scalars 7..20

value-object ProviderReference:
  carrier String
  utf8-bytes 1..128
  unicode-scalars 1..128

value-object ProviderAttemptKey:
  carrier String
  utf8-bytes 68..68
  unicode-scalars 68..68
  pattern "^c11-[0-9a-f]{64}$"

value-object ProviderRequest:
  orderId UInt64
  amountMinor UInt64
  currency ProviderCurrency

value-object ProviderResult:
  attemptKey ProviderAttemptKey
  orderId UInt64
  amountMinor UInt64
  currency ProviderCurrency
  status ProviderStatus
  providerReference optional<ProviderReference>

rule SameProviderRequest:
  input left ProviderRequest
  input right ProviderRequest
  expression left.orderId == right.orderId and left.amountMinor == right.amountMinor and left.currency == right.currency

mapping ToProviderRequest:
  input request ProviderRequest
  target ProviderRequest
  total true
  expression request

mapping ToInspectRequest:
  input request ProviderRequest
  target ProviderRequest
  total true
  expression request

mapping BuildProviderRequest:
  input request Request
  target ProviderRequest
  total true
  field orderId <- request.requestId
  field amountMinor <- SelectTotal(request)
  field currency <- request.providerCurrency

rule ValidProviderResponse:
  input request ProviderRequest
  input response ProviderResult
  expression request.orderId == response.orderId and request.amountMinor == response.amountMinor and request.currency == response.currency

mapping FromProviderResult:
  input response ProviderResult
  target ProviderResult
  total true
  expression response

rule MatchesProviderResult:
  input request ProviderRequest
  input response ProviderResult
  expression request.orderId == response.orderId and request.amountMinor == response.amountMinor and request.currency == response.currency

rule UnresolvedProviderResult:
  input response ProviderResult
  expression response.status != "Captured" and response.status != "DefinitivelyDeclined"

interface Provider:
  kind external
  exposes Capture, Inspect
  protocol DemoPay-v1
  request ProviderRequest
  result ProviderResult
  binding native/provider.json

operation Capture:
  input orderId UInt64
  input amountMinor UInt64
  input currency ProviderCurrency
  output ProviderResult
  native-protocol ReviewDesk.Provider.Capture
  intent immutable ToProviderRequest(request=ProviderRequest(orderId=orderId,amountMinor=amountMinor,currency=currency))
  same-key same-request returns current original-attempt status; never another effect
  same-key different-request fails ProviderRequestConflict without mutation
  may-return Captured, DefinitivelyDeclined, Unknown
  on-malformed-request fails ProviderInputRejected
  on-invalid-response fails ProviderProtocolRejected
  on-transport-failure fails ProviderTransportUnknown

query Inspect:
  input orderId UInt64
  input amountMinor UInt64
  input currency ProviderCurrency
  output ProviderResult
  native-protocol ReviewDesk.Provider.Inspect
  compare original request using ReviewDesk.SameProviderRequest
  on-existing returns current original-attempt status
  on-missing returns UnknownKey with exact supplied identity and no reference
  on-conflict fails ProviderRequestConflict
  effects none
`;
const invariantBefore='  invariant startsAt < endsAt and endsAt <= 1440\n\nrule ApprovalSlotAvailable:';
assert.ok(business.includes(invariantBefore),'fixture-only invariant target required');
business=business.replace(invariantBefore,'\nrule ApprovalSlotAvailable:'); // fixture-only: codec admits invariant-free root input
assert.ok(business.includes('  requestId UInt64\n  state ApprovalState'),'fixture-only Request currency target required');
business=business.replace('  requestId UInt64\n  state ApprovalState','  requestId UInt64\n  providerCurrency ProviderCurrency\n  state ApprovalState');
assert.ok(business.includes('  field requestId <- request.requestId\n  field state <- decision.proposal.state'),'fixture-only Request mapping target required');
business=business.replace('  field requestId <- request.requestId\n  field state <- decision.proposal.state','  field requestId <- request.requestId\n  field providerCurrency <- request.providerCurrency\n  field state <- decision.proposal.state');
business=business.replace('  transaction CommitApproval:\n',`  call receipt Capture(orderId=stored.value.requestId,amountMinor=SelectTotal(stored.value),currency=stored.value.providerCurrency)
    on-transport-error fail provider-unknown
    on-invalid-response fail provider-invalid
    on-error fail provider-error
  on not MatchesProviderResult(BuildProviderRequest(stored.value),receipt) reject provider-mismatch
  on UnresolvedProviderResult(receipt) fail provider-unknown
  on receipt.status == "DefinitivelyDeclined" reject provider-declined
  transaction CommitApproval:
`);
if(domain!=='ReviewDesk')business=business.replaceAll('ReviewDesk',domain);
writeFileSync(path.join(root,'business.alch'),business);
writeFileSync(path.join(root,'native/provider.json'),JSON.stringify({protocol:'DemoPay-v1'}));
writeFileSync(path.join(root,'contracts/external-write-bindings.json'),JSON.stringify({schema_version:'craft.generic-external-write-selection/v1-candidate',identity_limits:{schema_version:'craft.generic-causal-identity-limits/v1-candidate',max_child_depth:8,max_local_call_frames:8,max_site_occurrences:64,max_total_occurrences:128,max_tuple_bytes:4096,wrapper_depth:4},bindings:[{id:'capture',interface_ref:'ReviewDesk.Provider',write_operation_ref:'ReviewDesk.Capture',inspect_query_ref:'ReviewDesk.Inspect',native_family_ref:'ReviewDesk.Provider',protocol_id:'DemoPay-v1',request_mapping_ref:'ReviewDesk.ToProviderRequest',inspect_request_mapping_ref:'ReviewDesk.ToInspectRequest',response_validation_rule_ref:'ReviewDesk.ValidProviderResponse',response_mapping_ref:'ReviewDesk.FromProviderResult',matches_rule_ref:'ReviewDesk.MatchesProviderResult',unresolved_rule_ref:'ReviewDesk.UnresolvedProviderResult'}]}));
if(domain!=='ReviewDesk'){const p=path.join(root,'contracts/external-write-bindings.json');writeFileSync(p,readFileSync(p,'utf8').replaceAll('ReviewDesk',domain));}
if(sharedMapping){
 const p=path.join(root,'contracts/external-write-bindings.json');
 const selected=JSON.parse(readFileSync(p,'utf8'));
 selected.bindings[0].inspect_request_mapping_ref=selected.bindings[0].request_mapping_ref;
 writeFileSync(p,JSON.stringify(selected));
}
const appPath=path.join(root,'application.alch'),originalApp=readFileSync(appPath,'utf8');
const oldGenerated=originalApp.match(/generated\/external-[a-f0-9]{64}\.alch/)?.[0];assert.ok(oldGenerated);
const baseApp=originalApp.split('\n').filter(line=>!line.includes('source generated/external-')&&!line.includes('external-bindings contracts/external-profile.json')&&!line.includes('external-config contracts/external-config.json')).join('\n');
const initialSources=[{path:'business.alch',text:business},{path:'application.alch',text:baseApp},{path:'generated/auth-context.alch',text:readFileSync(path.join(root,'generated/auth-context.alch'),'utf8')}];
const external=captureExternalProfile(path.join(root,'contracts/external-profile.json'),root);
const regenerated=generateExternalBusinessSources(external,reconstructCoreCommerceSources(initialSources,'external-write-entry'),[{path:'business.alch',text:business}],initialSources);
assert.equal(regenerated.files.length,1);
unlinkSync(path.join(root,oldGenerated));
for(const f of regenerated.files)writeFileSync(path.join(root,f.path),f.text);
writeFileSync(appPath,originalApp.replace(oldGenerated,regenerated.files[0].path));
const compositionText=JSON.stringify(createExternalApiComposition(regenerated.bindings),null,2)+'\n';
writeFileSync(path.join(root,'contracts/external-composition.json'),compositionText);
const generationPath=path.join(root,'contracts/external-generation.json'),generation=JSON.parse(readFileSync(generationPath,'utf8'));
const sha=text=>createHash('sha256').update(text).digest('hex');
generation.bindings=regenerated.bindings;generation.calls=regenerated.calls;
generation.files=generation.files.filter(f=>f.path!==oldGenerated&&f.path!=='contracts/external-composition.json');
for(const f of [...regenerated.files,{path:'contracts/external-composition.json',text:compositionText}])generation.files.push({path:f.path,sha256:sha(f.text),bytes:Buffer.byteLength(f.text)});
writeFileSync(generationPath,JSON.stringify(generation,null,2)+'\n');
const v3Profile={schema_version:'craft.generic-v3-injected-http-key-profile/v1-candidate',id:'v3-injected-key',application_profile:'contracts/selected-profile.json',realization:'injected-request-response/v1-candidate',route:{id:domain+'.CommitHttp',service:domain+'Service',entry:domain+'.CommitRequestApprovalEntry',method:'POST',path:'/commit'},metadata:{carrier:'header',name:'x-craft-command-key',encoding:'base64url-utf8',target:'GenericCommandMetadataV1.client_key'},body:{carrier:'request-body',media_type:'application/json; charset=utf-8',schema_version:'craft.original-v3-entry-input/v1-candidate',target:'selected-route-entry'},limits:{max_request_bytes:65536,max_header_bytes:8192,body_timeout_ms:5000}};
writeFileSync(path.join(root,'contracts/http-profile.json'),JSON.stringify(v3Profile,null,2)+'\n');
const sources=createCoreCommerceSourceOwner('external-write-entry'),source=sources.prepare(root,'application.alch');
const semantics=createGenericSemanticOwner(sources,'external-write-entry'),semantic=semantics.check(source),inspection=semantics.inspect(semantic);
assert.equal(inspection.admission_mode,'external-write-entry');
const reviews=createGenericSourceReviewOwner(semantics),review=reviews.prepare(semantic,'C11-source007');
const decision=reviews.recordDecision(review,{decision_id:'C11-source007',owner:'C11-source007',outcome:'accepted',reviewed_digest:reviews.inspect(review).review_sha256},path.join(root,'decision.json'));
const plans=createGenericRepositoryPlanOwner(sources,source,semantics,semantic,reviews,reviews.requireAccepted(review,decision));
const application=plans.check(inspection.transaction_contract);
assert.equal(plans.inspectSourceApplication(application).contract.admission_mode,'external-write-entry');
return {root,sources,source,plans,application};
}



