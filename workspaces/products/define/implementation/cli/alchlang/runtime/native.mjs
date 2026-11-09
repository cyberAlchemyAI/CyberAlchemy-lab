/** Resolve exact authored selectors through the original checked pure generator. */
import * as pack from '../pack-engine-build.mjs';
import * as construction from '../package-construction-build.mjs';
import * as graph from '../package-graph-build.mjs';
import * as cli from '../package-cli-build.mjs';
import * as materialization from '../materialization-build.mjs';
import * as capture from '../local-capture-build.mjs';
import * as stages from '../pack-stages-build.mjs';
import * as assembly from '../pack-assembly-build.mjs';
import * as references from '../pack-reference-protocol-build.mjs';
import * as facts from '../pack-facts-build.mjs';
import * as preparation from '../preparation-protocol-build.mjs';
import * as values from '../value-observations-build.mjs';
import * as readiness from '../pack-readiness-build.mjs';
import * as preparationCli from '../preparation-cli-build.mjs';
import * as confirmation from '../confirmation-observation-build.mjs';
import * as example from '../example-build.mjs';
import {evaluateArtifact} from '../../../../../../../implementation/artifact-runtime/pure-operation.mjs';
const catalogs=[pack,construction,graph,cli,materialization,capture,stages,assembly,references,facts,preparation,values,readiness,preparationCli,confirmation,example],cache=new Map();
let epoch;
function sourceEpoch(){return JSON.stringify(catalogs.map(catalog=>catalog.fingerprint()));}
export async function callNative(selector,args){
 const selected=sourceEpoch();if(epoch!==undefined&&epoch!==selected)throw Error('native-source-changed-during-execution');epoch??=selected;
 let entry=cache.get(selector);
 if(!entry){
  const matches=catalogs.flatMap(catalog=>catalog.selected.components.filter(row=>row.selector===selector).map(row=>({catalog,row})));
  if(matches.length!==1)throw Error('native-selector-not-unique: '+selector);
  const {catalog,row}=matches[0];entry={row,artifact:catalog.generate(row.name)};cache.set(selector,entry);
 }
 const result=await evaluateArtifact(entry.artifact.output,entry.artifact.member,args,{manifest_sha256:entry.artifact.manifest_sha256});
 if(sourceEpoch()!==selected)throw Error('native-source-changed-during-execution');
 if(!result.ok)throw Error('native-evaluation-refused: '+selector+': '+JSON.stringify(result.error));
 const value=JSON.parse(new TextDecoder().decode(result.wire));
 if(entry.row.kind==='operation'){
  if(value.tag!=='Returned')throw Error('native-operation-refused: '+selector+': '+value.fields.code);
  return value.fields.value;
 }
 return value;
}
export function assertNativeSourceCurrent(){if(epoch!==undefined&&sourceEpoch()!==epoch)throw Error('native-source-changed-during-execution');}
