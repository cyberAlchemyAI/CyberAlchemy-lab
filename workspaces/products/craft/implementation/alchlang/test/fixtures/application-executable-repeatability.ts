import { loadDomainSpecCompiler } from "../../src/domainspec-cli.js";
import { prepareApplicationExecutable, compileApplicationExecutable } from "../../src/application-executable.js";
import { digest, json } from "../../src/domainspec-profile.js";
import { executableFixture } from "./application-executable-fixture.js";
import { realizationFixture } from "./application-realization-fixture.js";

const compiler = await loadDomainSpecCompiler();
const f = process.argv[3] === "realization" ? realizationFixture() : executableFixture();
const candidate = prepareApplicationExecutable(f.source, f.bindings, f.sources, f.interpretation, f.execution, compiler);
const result = compileApplicationExecutable(candidate, compiler.compileProject(process.argv[2]!).graph, compiler);
process.stdout.write(json({ candidate: digest(json(candidate)), join: digest(json(result.join)),
  trace: digest(json(result.trace)), artifacts: digest(json(result.view.artifacts)) }));
