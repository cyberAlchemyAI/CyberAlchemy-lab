import type {ReconciledSourceSelection} from './materialize-reconciled-sources.mjs';

export type CrossGeneratorSourceSelection=Omit<ReconciledSourceSelection,'schema_version'>&{
  readonly schema_version:'domainspec.cross-generator-source-selection/v1-candidate';
};
export function materializeCrossGeneratorSources(selection:CrossGeneratorSourceSelection,read:(path:string)=>string):string;
