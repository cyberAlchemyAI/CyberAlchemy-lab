import {existsSync, linkSync, readFileSync, unlinkSync, writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {callLab, composeDefineContext, LAB_ROOT} from './context-adapter.mjs';
import {canonicalJson, digest} from './canonical.mjs';
import {runDefineCli as legacyCli} from './cli.mjs';
import {runDefineSession} from './session-runtime.mjs';
import {evaluateDefineLanguageQuality} from './language-quality.mjs';

export function saveCandidate(path, value) {
  const target = resolve(path), tmp = `${target}.${process.pid}.${Date.now()}.tmp`;
  writeFileSync(tmp, canonicalJson(value)+'\n', {flag: 'wx', mode: 0o600});
  try { linkSync(tmp, target); } finally { unlinkSync(tmp); }
  return target;
}
function options(argv) {
  const flags = {definition_refs: []}, rest = [];
  for (let i=0; i<argv.length; i++) {
    const key = argv[i];
    if (['--store','--subject','--definition-ref'].includes(key)) {
      const value = argv[++i]; if (!value || value.startsWith('--')) throw new Error(`Missing value: ${key}`);
      if (key === '--definition-ref') flags.definition_refs.push(value);
      else flags[key.slice(2)] = value;
    } else rest.push(key);
  }
  return {flags, rest};
}
export async function runLabDefine(argv, environment={}) {
  const out = environment.stdout ?? process.stdout, err = environment.stderr ?? process.stderr;
  try {
    const {flags, rest} = options(argv), repo = environment.repositoryRoot ?? LAB_ROOT;
    const command = rest[0];
    if (!rest.includes('--help') && !rest.includes('-h')) {
      const {inspectRuntime} = await import('./runtime-integrity.mjs'); inspectRuntime();
    }
    if (command === 'compile' && !rest.includes('--help')) {
      const inputIndex=rest.indexOf('--input');
      if(inputIndex>=0 && rest[inputIndex+1]) {
        const saved=JSON.parse(readFileSync(resolve(rest[inputIndex+1]),'utf8'));
        callLab('validate-result',{result:saved},repo);
        const binding=saved.lab_binding;
        if(!binding?.envelope) throw new Error('define.compile-requires-Lab-bound-result');
        const selected=saved.definition_pack;
        const current=composeDefineContext({...flags},repo);
        if(!current.ok)throw new Error(current.reason_codes.join('; '));
        const epoch=digest({snapshot:binding.source_snapshot_digest,head:binding.head});
        if(selected?.context_envelope_ref!==binding.envelope.context_epoch_id || selected?.source_epoch!==epoch || binding.envelope.source_epoch!==epoch || digest(binding.envelope)!==selected.context_envelope_digest)throw new Error('define.compile-context-binding-mismatch');
        if(current.source_epoch!==epoch || !Number.isFinite(Date.parse(binding.envelope.expires_at)) || Date.parse(binding.envelope.expires_at)<=Date.now())throw new Error('define.compile-stale-Lab-context');
      }
    }
    if (['context','ontology','inspect','review','doctor'].includes(command)) {
      let result;
      if (command === 'context' || command === 'doctor') {
        if(rest.length !== 1) throw new Error(`Unknown ${command} argument`);
        result = composeDefineContext({...flags, consumer: 'human:lab-define'}, repo);
        if (!result.ok) throw new Error(result.reason_codes.join('; '));
        if (command === 'doctor') {
          const {inspectRuntime} = await import('./runtime-integrity.mjs');
          result = {ok:true, runtime:inspectRuntime(), context:'current',
            inline_bytes:result.context_envelope.inline_bytes, source_epoch:result.source_epoch,
            model_transport:'isolated-codex-app-server', active_dependency_gaps:[],
            external_prerequisites:['Node >=26.8.1','Python with jsonschema and cryptography','built Lab Craft compiler','Codex login for live chat'],
            authority_effect:'none'};
        }
      } else if (command === 'review') {
        if (rest[1] !== '--proposal' || !rest[2] || rest.length !== 3) throw new Error('Usage: define review --store STORE --proposal PROPOSAL.json');
        if (!flags.store) throw new Error('Review requires --store with an explicitly provisioned Lab branch');
        result = callLab('review', {...flags, proposal:JSON.parse(readFileSync(resolve(rest[2]),'utf8'))}, repo);
      } else {
        const ref = rest[1] ?? flags.subject;
        if (command === 'inspect' && !ref) throw new Error('Usage: define inspect SUBJECT');
        if (rest.length > 2) throw new Error(`Unknown ${command} argument`);
        result = callLab(command, {...flags, ...(ref ? {subject:ref} : {})}, repo);
      }
      out.write(canonicalJson(result)+'\n');return 0;
    }
    if (command === 'run') {
      // Handle the script here to bind exact Lab references and language checks
      // before a proposed pack is emitted. Interactive run stays in the UI core.
      const index = rest.indexOf('--input');
      if (index >= 0) {
        const script = JSON.parse(readFileSync(resolve(rest[index+1]), 'utf8'));
        const values = {...flags};
        for (let i=1;i<rest.length;i++) {
          if (rest[i] === '--json') continue;
          if (!['--goal','--intent','--context','--consumer','--input','--output'].includes(rest[i]) || !rest[i+1] || rest[i+1].startsWith('--')) throw new Error(`Unknown or incomplete argument: ${rest[i]}`);
          values[rest[i].slice(2)] = rest[++i];
        }
        for (const response of script.responses ?? []) {
          const ref = response.action === 'reuse' ? response.payload?.definition_ref : response.action === 'specialize' ? response.payload?.base_definition_ref : null;
          if (ref) {
            const row = callLab('inspect', {...flags, subject:ref}, repo);
            if (row.category !== 'definition' || !['admitted-current','local-admitted-current'].includes(row.axes.status)) throw new Error('Reuse requires an exact current Lab Definition');
            values.definition_refs.push(row.version_ref);
            if(response.action==='reuse') response.payload.definition_ref=row.version_ref; else response.payload.base_definition_ref=row.version_ref;
          }
        }
        const ctx=composeDefineContext(values,repo); if(!ctx.ok)throw new Error(ctx.reason_codes.join('; '));
        let quality;
        if (script.language_scope || script.language_quality_evidence || script.language_quality_evaluation) {
          if (!script.language_scope || !script.language_quality_evidence) throw new Error('Language scope and evidence must both be supplied');
          const scope={language:script.language_scope,language_quality:script.language_quality_evidence};
          quality=evaluateDefineLanguageQuality(scope,[],{user_confirmed:script.user_confirmed === true});
          if(quality.status!=='pass')throw new Error(`Language quality ${quality.status}: ${quality.reason_codes.join('; ')}`);
        }
        const result=runDefineSession({...values,concepts:script.concepts,responses:script.responses,context_result:ctx,
          language_scope:script.language_scope,language_quality_evidence:script.language_quality_evidence,language_quality_evaluation:quality});
        if(!result.ok)throw new Error(result.reason_codes.join('; '));
        result.schema_version='cal.define-cli-result/v1';
        result.lab_binding={source_snapshot_digest:ctx.context_envelope.source_snapshot_digest,head:ctx.context_envelope.head,
          envelope:ctx.context_envelope,authority_effect:'none'};
        callLab('validate-result',{result},repo);
        if(values.output)saveCandidate(values.output,result);
        out.write(canonicalJson(result)+'\n');return result.validation.handoff_ready?0:4;
      }
    }
    const code = await legacyCli(rest,{...environment,repositoryRoot:repo,store:flags.store,subject:flags.subject,definition_refs:flags.definition_refs,transport_mode:'direct'});
    if (rest.includes('--help') || rest.includes('-h')) out.write('\nLab interfaces: context | ontology [SUBJECT] | inspect SUBJECT | doctor | review --store STORE --proposal FILE\nLab selectors: --store STORE --subject SUBJECT --definition-ref EXACT_REFERENCE\n');
    return code;
  } catch(error) {err.write(canonicalJson({ok:false,stage:'lab-define',reason_codes:[error.message],authority_effect:'none'})+'\n');return 3;}
}
