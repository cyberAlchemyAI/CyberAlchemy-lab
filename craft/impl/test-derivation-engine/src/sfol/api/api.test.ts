import { describe, expect, it } from "vitest";

import { digestSfolValue } from "../cases/index.js";
import { closeTestClosure, SFOL_TDE_API_VERSION, SFOL_TDE_OPTIONAL_EVF_API_VERSION, verifyContentAddressedReceipt } from "./index.js";

describe("stable SFOL TDE API", () => {
  it("verifies a content-addressed receipt and rejects drift", () => {
    const unsigned = { schema_version: "example/v1", result: "pass" };
    const receipt = { ...unsigned, receipt_digest: digestSfolValue(unsigned) };
    expect(verifyContentAddressedReceipt(receipt)).toMatchObject({ ok: true });
    expect(verifyContentAddressedReceipt({ ...receipt, result: "fail" })).toMatchObject({ ok: false, diagnostics: [{ code: "SFOL_RECEIPT_INVALID" }] });
  });

  it("closes only over content-valid passing proof and detection receipts", () => {
    const proofUnsigned = { schema_version: "proof/v1", status: "pass" };
    const matrixUnsigned = { schema_version: "domainspec-sfol-detection-matrix/v1" as const, profile_version: "domainspec-sfol-negative-control/v1" as const, fault_model_set_digest: "a".repeat(64), control_set_digest: "b".repeat(64), observation_set_digest: "c".repeat(64), required_count: 0, detected_count: 0, surviving_count: 0, indeterminate_count: 0, invalid_control_count: 0, unsupported_count: 0, result: "pass" as const, rows: [] };
    const result = closeTestClosure({
      api_version: SFOL_TDE_API_VERSION,
      proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) },
      detection_matrix: { ...matrixUnsigned, receipt_digest: digestSfolValue(matrixUnsigned) },
    });
    expect(result).toMatchObject({ ok: true, value: { status: "pass" } });
    expect(closeTestClosure({ api_version: SFOL_TDE_API_VERSION, proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) } } as unknown as Parameters<typeof closeTestClosure>[0])).toMatchObject({ ok: false, diagnostics: [{ subject: "detection_matrix" }] });
    expect(closeTestClosure({ api_version: SFOL_TDE_API_VERSION, proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) }, detection_matrix: { ...matrixUnsigned, result: "fail", receipt_digest: digestSfolValue({ ...matrixUnsigned, result: "fail" }) } })).toMatchObject({ ok: false });
  });

  it("allows v2 closure without EVF and records that EVF was not requested", () => {
    const proofUnsigned = { schema_version: "proof/v1", status: "pass" };
    const result = closeTestClosure({
      api_version: SFOL_TDE_OPTIONAL_EVF_API_VERSION,
      proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) },
    });
    expect(result).toMatchObject({ ok: true, value: { schema_version: "domainspec-sfol-test-closure-receipt/v2", status: "pass", evf_status: "not_requested", detection_matrix_digest: null } });
  });

  it("keeps optional EVF fail-closed when a detection matrix is supplied", () => {
    const proofUnsigned = { schema_version: "proof/v1", status: "pass" };
    const matrixUnsigned = { schema_version: "domainspec-sfol-detection-matrix/v1" as const, profile_version: "domainspec-sfol-negative-control/v1" as const, fault_model_set_digest: "a".repeat(64), control_set_digest: "b".repeat(64), observation_set_digest: "c".repeat(64), required_count: 0, detected_count: 0, surviving_count: 0, indeterminate_count: 0, invalid_control_count: 0, unsupported_count: 0, result: "pass" as const, rows: [] };
    expect(closeTestClosure({ api_version: SFOL_TDE_OPTIONAL_EVF_API_VERSION, proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) }, detection_matrix: { ...matrixUnsigned, receipt_digest: digestSfolValue(matrixUnsigned) } })).toMatchObject({ ok: true, value: { evf_status: "passed" } });
    expect(closeTestClosure({ api_version: SFOL_TDE_OPTIONAL_EVF_API_VERSION, proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) }, detection_matrix: { ...matrixUnsigned, receipt_digest: "d".repeat(64) } })).toMatchObject({ ok: false });
    expect(closeTestClosure({ api_version: SFOL_TDE_OPTIONAL_EVF_API_VERSION, proof_receipt: { ...proofUnsigned, receipt_digest: digestSfolValue(proofUnsigned) }, detection_matrix: { ...matrixUnsigned, result: "fail", receipt_digest: digestSfolValue({ ...matrixUnsigned, result: "fail" }) } })).toMatchObject({ ok: false });
  });
});
