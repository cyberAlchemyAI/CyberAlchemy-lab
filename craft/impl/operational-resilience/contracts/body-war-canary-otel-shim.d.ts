declare module "@opentelemetry/api" {
  export interface Counter { add(value: number, attributes?: Record<string, string>): void }
  export interface Histogram { record(value: number, attributes?: Record<string, string>): void }
  export interface ObservableResult { observe(value: number, attributes?: Record<string, string>): void }
  export interface ObservableGauge {}
  export interface Meter {
    createCounter(name: string): Counter;
    createHistogram(name: string): Histogram;
    createObservableGauge(name: string, callback: (result: ObservableResult) => void): ObservableGauge;
  }
  export const metrics: { getMeter(name: string): Meter };
}
declare module "@opentelemetry/exporter-prometheus" {
  export class PrometheusExporter { constructor(options?: { port?: number; host?: string }) }
}
declare module "@opentelemetry/sdk-node" {
  export class NodeSDK { constructor(options?: { metricReader?: unknown }); start(): void; shutdown(): Promise<void> }
}
