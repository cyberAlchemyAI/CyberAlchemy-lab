export type Step = "render" | "upload";
export type Event =
  | { type: "START_EXPORT"; runId: string }
  | { type: "RETRY_STEP"; step: Step }
  | { type: "STEP_DONE"; runId: string; step: Step; attempt: number };

export interface Progress {
  readonly runId: string;
  readonly attempts: Readonly<Record<Step, number>>;
  readonly done: ReadonlySet<Step>;
}

export function reduceProgress(current: Progress, event: Event): Progress {
  switch (event.type) {
    case "START_EXPORT":
      return {
        runId: event.runId,
        attempts: { render: 1, upload: 1 },
        done: new Set(),
      };
    case "RETRY_STEP": {
      const done = new Set(current.done);
      done.delete(event.step);
      return {
        ...current,
        attempts: {
          ...current.attempts,
          [event.step]: current.attempts[event.step] + 1,
        },
        done,
      };
    }
    case "STEP_DONE":
      if (event.runId !== current.runId) return current;
      return { ...current, done: new Set([...current.done, event.step]) };
  }
}

export function stateFor(current: Progress): "running" | "complete" {
  return current.done.size === 2 ? "complete" : "running";
}

export interface Command {
  readonly runId: string;
  readonly step: Step;
  readonly attempt: number;
}

export function commandFor(current: Progress, step: Step): Command {
  return { runId: current.runId, step, attempt: current.attempts[step] };
}

export async function runWorker(
  command: Command,
  perform: (command: Command) => Promise<void>,
  report: (event: Event) => void,
): Promise<void> {
  await perform(command);
  report({ type: "STEP_DONE", ...command });
}
