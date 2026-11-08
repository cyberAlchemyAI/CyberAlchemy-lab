import { PlayerStatsRepository } from "../../domain/player-stats/player-stats.repository";
import { PlayerRepository } from "../../domain/player/player.repository";
import { getDealSplit } from "../../domain/deal/deal.service";
import {
  computeSettlement,
  decideSettlementSideEffects,
} from "../../domain/settlement/settlement.service";
import {
  FinancialWriteContext,
  FinancialWriteUnitOfWork,
} from "../../domain/shared/financial-write-unit-of-work";
import type { SettlementEventHandler } from "../../domain/settlement/settlement.events";
import { TransactionRepository } from "../../domain/transaction/transaction.repository";
import { SettlementResult } from "./settlement.dto";
import {
  businessAvgSettlementValue,
  businessMakeupRecovered,
  businessPayoutAmount,
  businessPreviewBeforeSettlement,
  businessSettlementsExecuted,
  calculationDrift,
  createCounter,
  createGauge,
  createHistogram,
  eventEmit,
  exposureAmount,
  idempotencyDedup,
  idempotencyViolation,
  operationDuration,
  operationInvocation,
  postconditionCheck,
  reconciliationMismatch,
  ruleViolation,
  transactionDuplicate,
  workflowDuration,
  workflowFailed,
  workflowInvocation,
  workflowStepDuration,
} from "../../infrastructure/telemetry/instruments";
import { markSettlementInvocation } from "./settlement-kpi-runtime";

const FEATURE = "financial-settlement";
const OPERATION = "GenerateSettlement";
const WORKFLOW = "SettlementWorkflow";
const CAPABILITY = "GenerateSettlement";

const settlementCycleInvocations = createCounter("settlement.cycle.invocations", {
  unit: "{invocation}",
  description: "Settlement cycle invocation count (O16)",
});

const settlementCyclePayoutAmount = createCounter(
  "settlement.cycle.payout_amount",
  {
    unit: "{currency_minor}",
    description: "Settlement cycle payout amount in minor currency units (O16)",
  },
);

const settlementCycleMakeupApplied = createCounter(
  "settlement.cycle.makeup_applied",
  {
    unit: "{currency_minor}",
    description:
      "Settlement cycle makeup amount applied in minor currency units (O16)",
  },
);

const settlementCycleAvgValue = createGauge("settlement.cycle.avg_value", {
  unit: "{currency_minor}",
  description: "Settlement cycle value distribution (O16)",
});

const settlementCycleErrorRate = createGauge("settlement.cycle.error_rate", {
  unit: "1",
  description: "Settlement cycle error rate samples (0 or 1) (O16)",
});

const settlementRecalculationDrift = createGauge(
  "settlement.recalculation.drift",
  {
    unit: "{currency_minor}",
    description: "Settlement recalculation drift amount (O16)",
  },
);

type WorkflowStep =
  | "validate_request"
  | "load_dependencies"
  | "compute_policy"
  | "persist_side_effects";

const toCurrencyMinor = (value: number): number => Math.round(value * 100);

export const generateSettlementUseCase =
  (
    playerStatsRepo: PlayerStatsRepository,
    playerRepo: PlayerRepository,
    transactionRepo: TransactionRepository,
    unitOfWork?: FinancialWriteUnitOfWork,
    onEvent?: SettlementEventHandler,
  ) =>
  async (
    playerId: string,
    startDate: string,
    endDate: string,
  ): Promise<SettlementResult> => {
    const startedAt = performance.now();
    let operationResult: "success" | "error" = "error";
    let failedAtStep: WorkflowStep = "validate_request";
    let stepStartedAt = startedAt;

    const closeStep = (step: WorkflowStep) => {
      const now = performance.now();
      workflowStepDuration.record((now - stepStartedAt) / 1000, {
        feature: FEATURE,
        workflow: WORKFLOW,
        step_name: step,
      });
      stepStartedAt = now;
    };

    const execute = async (
      context: FinancialWriteContext,
    ): Promise<SettlementResult> => {
      if (!playerId || !startDate || !endDate) {
        ruleViolation.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R2",
        });
        throw new Error("playerId, startDate, and endDate are required");
      }

      const parsedStart = new Date(startDate);
      const parsedEnd = new Date(endDate);
      if (
        Number.isNaN(parsedStart.getTime()) ||
        Number.isNaN(parsedEnd.getTime()) ||
        parsedStart > parsedEnd
      ) {
        ruleViolation.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R3",
        });
        throw new Error("Invalid settlement period");
      }

      closeStep("validate_request");
      failedAtStep = "load_dependencies";

      const player = await context.playerRepo.findById(playerId);
      if (!player) {
        throw new Error("Player not found");
      }

      const { entries } = await playerStatsRepo.findByPlayerId(playerId);
      const records = entries.map((s) => ({
        date: s.statDate,
        profit: s.profit,
        rakeback: s.rakeback,
      }));
      const previousMakeup = player.makeup;

      closeStep("load_dependencies");
      failedAtStep = "compute_policy";

      const settlement = computeSettlement({
        records,
        currentLimit: player.currentLimit,
        previousMakeup,
        periodStart: startDate,
        periodEnd: endDate,
        policy: player.makeupPolicy ?? undefined,
      });

      const recomputed = computeSettlement({
        records,
        currentLimit: player.currentLimit,
        previousMakeup,
        periodStart: startDate,
        periodEnd: endDate,
        policy: player.makeupPolicy ?? undefined,
      });

      const c1Drift = Math.abs(recomputed.totalProfit - settlement.totalProfit);
      const c2Drift = Math.abs(
        recomputed.totalRakeback - settlement.totalRakeback,
      );
      const c4Drift = Math.abs(recomputed.newMakeup - settlement.newMakeup);
      const dealShare = getDealSplit(player.currentLimit).player;
      const expectedPlayerProfitShare = Math.round(
        (Math.max(0, settlement.totalProfit) - settlement.appliedFromProfit) *
          dealShare,
      );
      const c3Drift = Math.abs(
        expectedPlayerProfitShare - settlement.playerProfitShare,
      );

      calculationDrift.record(c1Drift, {
        feature: FEATURE,
        operation: OPERATION,
        calculation_id: "C1",
      });
      calculationDrift.record(c2Drift, {
        feature: FEATURE,
        operation: OPERATION,
        calculation_id: "C2",
      });
      calculationDrift.record(c3Drift, {
        feature: FEATURE,
        operation: OPERATION,
        calculation_id: "C3",
      });
      calculationDrift.record(c4Drift, {
        feature: FEATURE,
        operation: OPERATION,
        calculation_id: "C4",
      });

      settlementRecalculationDrift.record(
        Math.max(c1Drift, c2Drift, c4Drift),
        {
          feature: FEATURE,
          calculation_id: "settlement_recalculation",
        },
      );

      const totalAppliedMakeup =
        settlement.appliedFromProfit + settlement.appliedFromRakeback;
      const existingTransactions = await context.transactionRepo.findByPlayerId(
        player.id,
      );

      const existingMakeupEvents = existingTransactions.filter(
        (item) => item.type === "MAKEUP_APPLIED" && item.date === endDate,
      ).length;
      const existingPayoutEvents = existingTransactions.filter(
        (item) => item.type === "PAYOUT" && item.date === endDate,
      ).length;

      const makeupDuplicateExposure = existingTransactions
        .filter((item) => item.type === "MAKEUP_APPLIED" && item.date === endDate)
        .slice(1)
        .reduce((sum, item) => sum + item.amount, 0);
      const payoutDuplicateExposure = existingTransactions
        .filter((item) => item.type === "PAYOUT" && item.date === endDate)
        .slice(1)
        .reduce((sum, item) => sum + item.amount, 0);
      const duplicateExposure = makeupDuplicateExposure + payoutDuplicateExposure;

      if (duplicateExposure > 0) {
        exposureAmount.record(duplicateExposure, {
          feature: FEATURE,
          operation: OPERATION,
        });
      }

      if (existingMakeupEvents > 1) {
        const duplicates = existingMakeupEvents - 1;
        transactionDuplicate.add(duplicates, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R4",
          transaction_type: "MAKEUP_APPLIED",
        });
        idempotencyViolation.add(duplicates, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R4",
        });
        ruleViolation.add(duplicates, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R4",
        });
      }

      if (existingPayoutEvents > 1) {
        const duplicates = existingPayoutEvents - 1;
        transactionDuplicate.add(duplicates, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R5",
          transaction_type: "PAYOUT",
        });
        idempotencyViolation.add(duplicates, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R5",
        });
        ruleViolation.add(duplicates, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R5",
        });
      }

      closeStep("compute_policy");
      failedAtStep = "persist_side_effects";

      const sideEffects = decideSettlementSideEffects({
        existingTransactions,
        periodEnd: endDate,
        totalAppliedMakeup,
        totalPayout: settlement.totalPayout,
      });

      if (totalAppliedMakeup > 0 && !sideEffects.shouldCreateMakeupAppliedEvent) {
        idempotencyDedup.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R4",
        });
      }

      if (settlement.totalPayout > 0 && !sideEffects.shouldCreatePayoutEvent) {
        idempotencyDedup.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R5",
        });
      }

      if (sideEffects.shouldCreateMakeupAppliedEvent) {
        let created = true;

        if (context.transactionRepo.createSettlementEventIfAbsent) {
          created = await context.transactionRepo.createSettlementEventIfAbsent({
            playerId: player.id,
            type: "MAKEUP_APPLIED",
            amount: totalAppliedMakeup,
            date: endDate,
          });

          if (!created) {
            idempotencyDedup.add(1, {
              feature: FEATURE,
              operation: OPERATION,
              rule_id: "R4",
            });
          }
        } else {
          await context.transactionRepo.create({
            playerId: player.id,
            type: "MAKEUP_APPLIED",
            amount: totalAppliedMakeup,
            date: endDate,
          });
        }

        postconditionCheck.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          postcondition_id: "makeup_tx_created",
          result: created ? "satisfied" : "deduped",
        });
      }

      if (settlement.newMakeup !== previousMakeup) {
        await context.playerRepo.update(player.id, {
          makeup: settlement.newMakeup,
        });

        postconditionCheck.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          postcondition_id: "makeup_updated",
          result: "satisfied",
        });
      }

      reconciliationMismatch.record(
        Math.abs(recomputed.newMakeup - settlement.newMakeup),
        {
          feature: FEATURE,
          entity: "Player",
        },
      );

      if (sideEffects.shouldCreatePayoutEvent) {
        let created = true;

        if (context.transactionRepo.createSettlementEventIfAbsent) {
          created = await context.transactionRepo.createSettlementEventIfAbsent({
            playerId: player.id,
            type: "PAYOUT",
            amount: settlement.totalPayout,
            date: endDate,
          });

          if (!created) {
            idempotencyDedup.add(1, {
              feature: FEATURE,
              operation: OPERATION,
              rule_id: "R5",
            });
          }
        } else {
          await context.transactionRepo.create({
            playerId: player.id,
            type: "PAYOUT",
            amount: settlement.totalPayout,
            date: endDate,
          });
        }

        postconditionCheck.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          postcondition_id: "payout_tx_created",
          result: created ? "satisfied" : "deduped",
        });

        if (created && onEvent) {
          await onEvent({
            type: "PayoutCreated",
            playerId: player.id,
            date: endDate,
            amount: settlement.totalPayout,
            occurredAt: new Date(),
          });

          eventEmit.add(1, {
            feature: FEATURE,
            event_type: "PayoutCreated",
          });
        }
      }

      const result: SettlementResult = {
        playerId,
        periodStart: startDate,
        periodEnd: endDate,
        totalProfit: settlement.totalProfit,
        totalRakeback: settlement.totalRakeback,
        netProfit: settlement.netProfit,
        previousMakeup,
        newMakeup: settlement.newMakeup,
        playerProfitShare: settlement.playerProfitShare,
        playerRakebackShare: settlement.playerRakebackShare,
        totalPayout: settlement.totalPayout,
      };

      if (onEvent) {
        await onEvent({
          type: "SettlementGenerated",
          playerId,
          periodStart: startDate,
          periodEnd: endDate,
          totalProfit: settlement.totalProfit,
          totalRakeback: settlement.totalRakeback,
          previousMakeup,
          newMakeup: settlement.newMakeup,
          totalPayout: settlement.totalPayout,
          occurredAt: new Date(),
        });

        eventEmit.add(1, {
          feature: FEATURE,
          event_type: "SettlementGenerated",
        });
      }

      postconditionCheck.add(1, {
        feature: FEATURE,
        operation: OPERATION,
        postcondition_id: "result_returned",
        result: "satisfied",
      });

      closeStep("persist_side_effects");

      return result;
    };

    try {
      const result = unitOfWork
        ? await unitOfWork.runInTransaction((context) => execute(context))
        : await execute({ playerRepo, transactionRepo });

      operationResult = "success";

      settlementCycleInvocations.add(1, {
        feature: FEATURE,
      });
      settlementCyclePayoutAmount.add(
        toCurrencyMinor(Math.max(result.totalPayout, 0)),
        {
          feature: FEATURE,
        },
      );
      settlementCycleMakeupApplied.add(
        toCurrencyMinor(Math.max(result.previousMakeup - result.newMakeup, 0)),
        {
          feature: FEATURE,
        },
      );
      settlementCycleAvgValue.record(toCurrencyMinor(result.totalPayout), {
        feature: FEATURE,
      });

      businessSettlementsExecuted.add(1, {
        feature: FEATURE,
        capability: CAPABILITY,
      });
      businessPayoutAmount.add(toCurrencyMinor(Math.max(result.totalPayout, 0)), {
        feature: FEATURE,
        capability: CAPABILITY,
      });
      businessMakeupRecovered.add(
        toCurrencyMinor(Math.max(result.previousMakeup - result.newMakeup, 0)),
        {
          feature: FEATURE,
          capability: CAPABILITY,
        },
      );
      businessAvgSettlementValue.record(toCurrencyMinor(result.totalPayout), {
        feature: FEATURE,
        capability: CAPABILITY,
      });

      const previewBeforeSettlementRatio = markSettlementInvocation();
      businessPreviewBeforeSettlement.record(previewBeforeSettlementRatio, {
        feature: FEATURE,
        capability: "GetSettlementPreview",
      });

      settlementCycleErrorRate.record(0, {
        feature: FEATURE,
      });

      return result;
    } catch (error) {
      closeStep(failedAtStep);

      const typedError = error as {
        code?: string;
        message?: string;
      };

      if (typedError.message === "Player not found") {
        ruleViolation.add(1, {
          feature: FEATURE,
          operation: OPERATION,
          rule_id: "R1",
        });
      }

      settlementCycleErrorRate.record(1, {
        feature: FEATURE,
      });

      workflowFailed.add(1, {
        feature: FEATURE,
        workflow: WORKFLOW,
        failed_at_step: failedAtStep,
      });

      postconditionCheck.add(1, {
        feature: FEATURE,
        operation: OPERATION,
        postcondition_id: "result_returned",
        result: "violated",
      });

      throw error;
    } finally {
      const durationSec = (performance.now() - startedAt) / 1000;

      operationInvocation.add(1, {
        feature: FEATURE,
        operation: OPERATION,
        result: operationResult,
      });

      operationDuration.record(durationSec, {
        feature: FEATURE,
        operation: OPERATION,
      });

      workflowInvocation.add(1, {
        feature: FEATURE,
        workflow: WORKFLOW,
        result: operationResult === "success" ? "completed" : "failed",
      });

      workflowDuration.record(durationSec, {
        feature: FEATURE,
        workflow: WORKFLOW,
      });
    }
  };
