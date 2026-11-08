/** Small independent characterization fixtures; no replacement evaluator.
 * Open Questions: docs/POLICY-ENFORCEMENT.md#open-questions. */
export const crmEligibilityGuards=[
 ['not request.sourceCurrent','source-stale','SourceStale'],
 ['not request.releaseAllowed','disclosure-denied','DisclosureDenied'],
 ['not CandidateCurrent(request)','candidate-stale','CandidateStale'],
 ['request.attempt == Unknown','reconciliation-required','ReconciliationRequired'],
 ['request.attempt == Confirmed','already-confirmed','AlreadyConfirmed'],
 ['request.attempt == Cancelled','cancelled','Cancelled'],
 ['request.duplicate','duplicate-contact','DuplicateContact'],
 ['not request.identityVerified','identity-unverified','IdentityUnverified'],
 ['not request.contactAllowed','preference-denied','PreferenceDenied'],
 ['request.expectedPreferenceVersion != request.currentPreferenceVersion','preference-changed','PreferenceChanged'],
 ['not EvidenceGrounded(request)','unsupported-enrichment','UnsupportedEnrichment'],
 ['not ApprovalCurrent(request)','approval-stale','ApprovalStale'],
] as const;
export const crmInlineGuardBlock=crmEligibilityGuards.map(([condition,code])=>'  on '+condition+' reject '+code).join('\n');
export const crmEligibilityDeclarations=`enum ContactUpdateRejection:
${crmEligibilityGuards.map(([,code,name])=>'  value '+name+' wire '+JSON.stringify(code)).join('\n')}

enum ContactUpdateAdmission:
  variant Allow
  variant Reject reason ContactUpdateRejection

calculation AllowUpdate:
  pure
  result ContactUpdateAdmission
  expression ContactUpdateAdmission.Allow()

calculation RejectUpdate:
  pure
  input reason ContactUpdateRejection
  result ContactUpdateAdmission
  expression ContactUpdateAdmission.Reject(reason=reason)

policy ContactUpdateEligibility:
  input request ReviewRequest
  result ContactUpdateAdmission
  ordered-cases:
${crmEligibilityGuards.map(([condition,,name])=>'    '+name[0]!.toLowerCase()+name.slice(1)+' when '+condition+' -> RejectUpdate(reason=ContactUpdateRejection.'+name+')').join('\n')}
    otherwise -> AllowUpdate()

`;
/** Insert into the authored module, preserving every original declaration. */
export function extractCrmEligibility(source:string):string {
 if(source.includes('  enforce ContactUpdateEligibility(request=request)'))return source;
 if(!source.includes(crmInlineGuardBlock))throw Error('Original CRM ordered guard list changed; inspect before extraction');
 const operation='operation PrepareContactUpdate:';
 if(!source.includes(operation))throw Error('Original CRM Operation missing');
 return source.replace(operation,crmEligibilityDeclarations+operation).replace(crmInlineGuardBlock,'  enforce ContactUpdateEligibility(request=request)');
}
/** Preserve a comparable inline Operation after the actual CRM is migrated. */
export function inlineCrmEligibility(source:string):string {
 return source.replace('  enforce ContactUpdateEligibility(request=request)',crmInlineGuardBlock);
}

export const secondDomainLibrary=`module ResearchAdmission version 1
enum Cause:
  value ApprovalMissing wire "approval-needed"
  value CalculationRejected wire "calculation-rejected"
enum Verdict:
  variant Allow
  variant Reject reason Cause
`;
export const secondDomain=`module ResearchDesk version 1
use ResearchAdmission.Cause
use ResearchAdmission.Verdict

rule PositiveRatio:
  input divisor UInt64
  expression 10 / divisor == 5

calculation Permit:
  pure
  result Verdict
  expression Verdict.Allow()

calculation Deny:
  pure
  input reason Cause
  result Verdict
  expression Verdict.Reject(reason=reason)

policy PublicationEligibility:
  input approved Bool
  input divisor UInt64
  result Verdict
  ordered-cases:
    noApproval when not approved -> Deny(reason=Cause.ApprovalMissing)
    invalidRatio when not PositiveRatio(divisor=divisor) -> Deny(reason=Cause.CalculationRejected)
    otherwise -> Permit()

operation Publish:
  input approved Bool
  input divisor UInt64
  output Bool
  enforce PublicationEligibility(approved=approved,divisor=divisor)
  return approved
`;
export const secondDomainInline=secondDomain.replace('  enforce PublicationEligibility(approved=approved,divisor=divisor)',
 '  on not approved reject approval-needed\n  on not PositiveRatio(divisor=divisor) reject calculation-rejected');
