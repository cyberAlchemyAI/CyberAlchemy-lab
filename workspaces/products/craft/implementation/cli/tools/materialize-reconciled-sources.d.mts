export interface ReconciledSourceSelection {
  readonly schema_version:'domainspec.reconciled-source-selection/v1-candidate';
  readonly authority_effect:'none';
  readonly sources:readonly Readonly<{id:string;path:string;sha256:string}>[];
}
export function materializeReconciledSources(selection:ReconciledSourceSelection,read:(path:string)=>string):string;
