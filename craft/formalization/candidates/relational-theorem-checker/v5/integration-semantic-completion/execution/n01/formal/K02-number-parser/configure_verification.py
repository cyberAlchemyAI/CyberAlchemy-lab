"""Configure the fresh isolated candidate verifier from the existing local harness."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
source=(HERE.parent/'K02-numeric/verify_candidate.py').read_text()
source=source.replace('K02 exact decimal components','K02 exact number token parser')
start=source.index('    dependencies = ');end=source.index('    sources = dependencies + new_sources',start)
source=source[:start]+'''    dependencies = [HERE.parent / "K02-json/ClosedJsonObject.lean",
                    HERE.parent / "K02-json/JsonElements.lean",
                    HERE.parent / "K02-binding-ast/BindingAstCombinators.lean",
                    HERE.parent / "K02-numeric/DecimalMeaning.lean",
                    HERE.parent / "K02-numeric/DecimalEpochCheck.lean",
                    HERE.parent / "K02-numeric/DecimalGrammar.lean"]
    new_sources = [HERE / name for name in ["NumberDigitScan.lean", "NumberTokenParser.lean",
                   "NumberGrammarComplete.lean", "NumberEpochAst.lean", "NumberParserControls.lean"]]
'''+source[end:]
source=source.replace('"unit": "K02-numeric"','"unit": "K02-number-parser"')
start=source.index('              "claim_scope": ');end=source.index('              "source_capture": ',start)
source=source[:start]+'''              "claim_scope": "Complete exact JSON-number token grammar parsing, retained-character reconstruction, representation completeness/uniqueness and exact nonnegative integer epoch AST decoding without caller witness or floats. Full frame/body/record/schema, byte/source/authentic/resource and independent closure remain open.",
'''+source[end:]
source=source.replace('"numeric_AST_witness_check_proved": True','"numeric_AST_decoder_proved": True')
source=source.replace('"raw_number_token_parser_proved": False','"raw_number_token_parser_proved": True')
source=source.replace('"token_representation_completeness_proved": False','"token_representation_completeness_proved": True')
source=source.replace('"token_representation_uniqueness_proved": False','"token_representation_uniqueness_proved": True')
source=source.replace('              "numeric_grammar_soundness_proved": True,','              "numeric_grammar_soundness_proved": True,\n              "number_token_parser_proved": True,\n              "complete_JSON_number_grammar_proved": True,')
(HERE/'verify_candidate.py').write_text(source)
audit=(HERE.parent/'K02-numeric/audit_imports.py').read_text().replace('K02 exact decimal components','K02 exact number token parser').replace('"unit": "K02-numeric"','"unit": "K02-number-parser"')
(HERE/'audit_imports.py').write_text(audit)
