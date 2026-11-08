/** Portable public boundary shape. The owning Core validates/registers the input.
 * No declaration imports private source-checkout paths. Open questions: BA04/BA18 qualification. */
export interface BusinessApplicationInput {
 readonly snapshot:Readonly<{project:Readonly<{application_intents:readonly Readonly<{id:string;application_id:string;operation_ref:string;mapping_ref:string;mapping_arguments:Readonly<Record<string,Readonly<{root:'body'|'request'|'value';path:readonly string[]}>>>;access:Readonly<{kind:'public'}>}>[]}>}>;
 readonly applications:readonly {
  readonly model:Readonly<{id:string;source:string;semantics:string}>;
  readonly source:string;readonly source_sha256:string;readonly semantics_sha256:string;
  readonly semantics:Readonly<{
   owner:string;declarations:Readonly<Record<string,any>>;
   claim_meanings:Readonly<Record<string,Readonly<{claim_id:string;version:string;supersedes:string|null;business_meaning:Readonly<Record<string,any>>;owner_acceptance:Readonly<Record<string,any>>;definitions:readonly Readonly<Record<string,any>>[];definition_refs:readonly string[]}>>>;
   rule_meanings:Readonly<Record<string,Readonly<{sorts:Readonly<Record<string,string>>;constants:Readonly<Record<string,string>>;predicates:Readonly<Record<string,string>>}>>>;
   operation_behaviors:Readonly<Record<string,any>>;value_invariant_bindings:Readonly<Record<string,any>>;required_guarantees:readonly string[];
  }>;
 }[];
 readonly runtime:Readonly<{data:Readonly<{application_runtime:Readonly<{formal_profile_asset:string;identity_algorithm_asset:string}>}>;assets:Readonly<Record<string,Readonly<{text?:string}>>>}>;
}
