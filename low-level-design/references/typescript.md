# TypeScript

Read this file when the repo is TypeScript. It maps the rules in `SKILL.md` to TypeScript, for Cloudflare Workers and Node. The generic forms are in `concurrency-recipes.md`, `smells.md` and `patterns.md`.

## Language mapping

| Course term | TypeScript form |
|---|---|
| Future | `Promise<T>` |
| Thread pool | The event loop, a queue consumer, or a Durable Object for each key |
| Interface | `type` for data shapes. `interface` for a contract that classes implement. |
| Abstract class | `abstract class`, only for shared state or shared steps |
| Enum | A union of string literals: `type OrderState = "open" \| "filled" \| "cancelled"` |
| Singleton | A module-scope `const`. Never a class with `getInstance()`. |
| Checked exception | A class that extends `Error`, or a result union for an expected failure |
| Dependency injection | Constructor parameters. No container unless the repo has one. |
| Strategy | A function type or a one-method `interface` |
| Builder | An options object with defaults. A builder class only for staged construction. |

## Types

- Use branded types where a mix-up of IDs is possible.

  ```ts
  export type UserId = string & { readonly __brand: "UserId" };
  export type TopicId = string & { readonly __brand: "TopicId" };
  export const userId = (raw: string) => raw as UserId;
  ```

- Use a discriminated union for a result that carries the reason.

  ```ts
  export type ApplyResult =
    | { kind: "applied"; deduction: number; cashback: number }
    | { kind: "rejected"; reason: "expired" | "min-order" | "used" };
  ```

- Use an exhaustive `switch` on a union. Let the compiler find a missing state.

  ```ts
  export function label(state: OrderState): string {
    switch (state) {
      case "open": return "Open";
      case "filled": return "Filled";
      case "cancelled": return "Cancelled";
      default: return assertNever(state);
    }
  }
  export function assertNever(value: never): never {
    throw new Error(`Unexpected value: ${String(value)}`);
  }
  ```

- Mark data `readonly` by default. Use `ReadonlyArray` and `ReadonlyMap` in public signatures.
- Do not use `any`. Use `unknown` at trust boundaries and parse it with a schema, for example `zod`.
- Do not use type assertions to make a hierarchy work. A cast is a design smell.
- Do not use optional fields to model states. Use a union of the states.

## Objects

- Use `private readonly` constructor parameters for dependencies.
- Use `#field` or `private` for state. Expose behaviour, not fields.
- Return copies or readonly views of internal collections.
- Wrap a nested `Map<K, Map<K2, V>>` in a class with named methods.

```ts
export class BalanceMap {
  readonly #balances = new Map<UserId, Map<UserId, number>>();

  add(from: UserId, to: UserId, amount: number): void {
    const row = this.#balances.get(from) ?? new Map<UserId, number>();
    row.set(to, (row.get(to) ?? 0) + amount);
    this.#balances.set(from, row);
  }

  owed(from: UserId, to: UserId): number {
    return this.#balances.get(from)?.get(to) ?? 0;
  }
}
```

## Rule engine

```ts
export type Rule<C> = (context: C) => boolean;

export function allPass<C>(rules: ReadonlyArray<Rule<C>>, context: C): boolean {
  return rules.every((rule) => rule(context));
}
```

To add a rule, add a function to the list. If order matters, use an ordered array of handlers that return `undefined` to pass to the next one.

## Errors

- Throw a specific `Error` subclass for a fault that the code cannot recover from.
- Return a result union for an expected failure that the caller must handle.
- Never `catch` and ignore. Never `throw` a string.

## Files

- One exported class or one concept for each file. Group by concern: `models/`, `services/`, `algorithms/`, `errors/`.
- Name files for the thing they export, in kebab-case: `rate-limiter.ts`.

## Tests

- Use the test runner of the repo. For Workers, use Vitest with `@cloudflare/vitest-pool-workers`.
- Inject `Clock` and `sleep`. Do not use fake timers when an injected clock works.
- Name the test file for the behaviour: `gameplay.test.ts`.

## Concurrency

On a single-threaded event loop the risk is interleaving across `await` points, not parallel threads. The fixes in `concurrency-recipes.md` are the same. These are the TypeScript forms.

### Keyed executor

Trigger: operations on the same key must run in order, and operations on other keys may run in parallel. Example: a read after a write must see the write.

```ts
export class KeyedExecutor {
  private readonly tails = new Map<string, Promise<unknown>>();

  run<T>(key: string, task: () => Promise<T>): Promise<T> {
    const previous = this.tails.get(key) ?? Promise.resolve();
    const next = previous.then(task, task);
    const tail = next.catch(() => undefined);
    this.tails.set(key, tail);
    tail.then(() => {
      if (this.tails.get(key) === tail) this.tails.delete(key);
    });
    return next;
  }
}
```

- Choose the narrowest key that still gives the guarantee. Use `subscriber:topic` for reads and `topic` for writes.
- On Cloudflare, a Durable Object for each key gives the same ordering across requests.

### Request collapsing

Trigger: many concurrent misses for one key cause one load each.

```ts
export class Collapser<V> {
  private readonly inFlight = new Map<string, Promise<V>>();

  get(key: string, load: (key: string) => Promise<V>): Promise<V> {
    const existing = this.inFlight.get(key);
    if (existing) return existing;
    const pending = load(key).finally(() => this.inFlight.delete(key));
    this.inFlight.set(key, pending);
    return pending;
  }
}
```

- Store the promise before it completes. Every caller gets the same promise.
- In a cache, add the entry to the expiry index only after the promise resolves.

### Immutable snapshot swap

Trigger: readers must never see an aggregate that is half updated.

```ts
type Balances = ReadonlyMap<string, number>;

export class BalanceStore {
  private snapshot: Balances = new Map();

  read(): Balances {
    return this.snapshot;
  }

  apply(changes: ReadonlyArray<readonly [string, number]>): void {
    const next = new Map(this.snapshot);
    for (const [user, delta] of changes) next.set(user, (next.get(user) ?? 0) + delta);
    this.snapshot = next;
  }
}
```

Readers can see old data, but the data is always consistent.

### Timeout on every wait

Trigger: any `await` on something that can fail to complete.

```ts
export function withTimeout<T>(work: Promise<T>, ms: number, label: string): Promise<T> {
  let timer: ReturnType<typeof setTimeout> | undefined;
  const timeout = new Promise<never>((_, reject) => {
    timer = setTimeout(() => reject(new TimeoutError(label, ms)), ms);
  });
  return Promise.race([work, timeout]).finally(() => clearTimeout(timer));
}

export class TimeoutError extends Error {
  constructor(readonly label: string, readonly ms: number) {
    super(`${label} timed out after ${ms}ms`);
  }
}
```

Prefer `AbortSignal.timeout(ms)` when the API accepts a signal, such as `fetch`.

### Retry with backoff and a dead-letter queue

Trigger: a transient failure, such as a network error or a 5xx. Never retry invalid input. Never retry a payment on its own.

```ts
export class RetryableError extends Error {}

export type RetryPolicy = {
  maxAttempts: number;
  delayMs: (attempt: number) => number;
};

export const exponential = (baseMs: number, maxAttempts: number): RetryPolicy => ({
  maxAttempts,
  delayMs: (attempt) => baseMs * 2 ** (attempt - 1),
});

export async function retry<T>(
  task: () => Promise<T>,
  policy: RetryPolicy,
  sleep: (ms: number) => Promise<void>,
  deadLetter: (error: unknown) => Promise<void>,
): Promise<T> {
  for (let attempt = 1; ; attempt++) {
    try {
      return await task();
    } catch (error) {
      if (!(error instanceof RetryableError) || attempt >= policy.maxAttempts) {
        await deadLetter(error);
        throw error;
      }
      await sleep(policy.delayMs(attempt));
    }
  }
}
```

- `sleep` is injected, so tests do not wait in real time.
- On Cloudflare Queues, use the built-in `retryDelay` and a dead-letter queue before you write this.

### Inject the clock

Trigger: any logic that reads the time.

```ts
export type Clock = { now: () => number };
export const systemClock: Clock = { now: () => Date.now() };

export class SlidingWindowLimiter {
  private readonly hits = new Map<string, number[]>();

  constructor(
    private readonly limit: number,
    private readonly windowMs: number,
    private readonly clock: Clock,
  ) {}

  shouldAccept(key: string): boolean {
    const now = this.clock.now();
    const recent = (this.hits.get(key) ?? []).filter((t) => now - t < this.windowMs);
    if (recent.length >= this.limit) {
      this.hits.set(key, recent);
      return false;
    }
    recent.push(now);
    this.hits.set(key, recent);
    return true;
  }
}
```

- `shouldAccept` returns a plain boolean. The hot path stays local and fast (090).
- The limiter removes expired timestamps on each check, so it needs no sweeper (098).

### Idempotent writes

Trigger: the client or a queue can retry a write.

```ts
export class EventLog<E extends { id: string }> {
  private readonly byId = new Map<string, E>();

  append(event: E): "stored" | "duplicate" {
    if (this.byId.has(event.id)) return "duplicate";
    this.byId.set(event.id, event);
    return "stored";
  }
}
```

Events are immutable. To correct an event, append a new one.
