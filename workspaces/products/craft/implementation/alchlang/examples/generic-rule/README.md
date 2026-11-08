# Generate and run a business Rule

This small project uses the installed Craft and AlchLang tools. It generates an
ESM module from a business condition, without a handwritten business callback
or formal claim. Use Linux x64 and Node 26.8.1 for the currently tested path.

Install both downloaded CLI archives into a new project, then copy this example:

```sh
mkdir my-rule
cd my-rule
npm init -y
npm install /absolute/path/domainspec-v2-cli-1.3.0.tgz /absolute/path/cyberalchemy-alchlang-0.7.0-candidate.0.tgz
cp -R node_modules/@cyberalchemy/alchlang/examples/generic-rule/. .
npx --no-install alchlang-generic generate --source business.alch --profile profile.json --rule ReviewDesk.IsVerified --out generated --accept-local-review my-rule
node exercise.mjs
```

Replace the two archive paths with the files you downloaded. Generation requires
a new output directory. Choose a new `--out` directory when regenerating and
run `node exercise.mjs <new-output-directory>` accordingly. The review label records your local
acceptance of the selected model; it does not authenticate a user or grant a
runtime permission.

`business.alch` declares a typed Request and the expression `request.verified`.
`profile.json` selects the supported Node ESM bounded-values capabilities and exact limits.
`contracts/bounds.json` declares the matching computation limits. The generated
`rule.mjs` accepts UTF-8 JSON bytes and returns a typed result. The exercise
checks true and false outcomes, shows that `flagged` does not change this Rule,
and rejects a string where a Boolean is required.

For Operations, Mappings, collection calculations, storage, protected Entries
and optional model exports, see the installed `docs/GENERIC-APPLICATIONS.md` in
both tool packages. Those capabilities require their own selected profiles.

## Open Questions

The complete cumulative application matrix and general runtime performance are
still under development. Local hosting, TDE, EVF and publication remain deferred.

## Optional formal model

The same `profile.json` supports the finite SMT-LIB exporter with the same
authored input and computation limits.

```sh
npx --no-install alchlang-generic formal-export --model smtlib2 --source business.alch --profile profile.json --rule ReviewDesk.IsVerified --out formal-smt --accept-local-review my-rule
```

Read `formal-smt/model.smt2` and `manifest.json`. Export produces formal text;
it does not run a solver, TDE or EVF. Generation with `profile.json` remains
available without formal claims or an export.
