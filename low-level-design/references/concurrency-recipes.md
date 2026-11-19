# Concurrency recipes

These are the concurrency techniques from the course, in a form that does not depend on a language. Each recipe has a trigger, the steps, and the traps. Use a recipe only when its trigger is present.

For code, read the language file: `typescript.md` for TypeScript.

Threads and event loops have the same problem. With threads, two operations run at the same time. With an event loop, two operations interleave at each suspension point (`await`, a callback, an I/O call). The fixes are the same.

Lesson numbers refer to `interviewready-lld-transcripts`.

## First: find the race (103, 104)

Do this before you add any lock.

1. List each piece of shared mutable state.
2. For each operation, mark the suspension points between its read and its write.
3. Write down one bad interleaving for each pair of operations.
4. Decide which need each race breaks:
   - exclusivity: two writers must not overlap. Fix it with one owner or a lock.
   - ordering: B must see the effect of A. Fix it with a keyed executor.
5. Write a test that starts the bad interleaving on purpose.

## Keyed executor (063, 066, 073, 077, 103)

Trigger: operations on the same key must run in order. Operations on other keys can run in parallel. Example: a read after a write must see that write.

Steps:
1. Create N single-thread queues. N is fixed, for example the number of cores.
2. Send each task to queue `hash(key) % N`.
3. A queue runs its tasks one at a time, so tasks for one key keep their order.

Traps:
- Choose the narrowest key that still gives the guarantee. A wide key loses parallelism. A narrow key loses the guarantee. Example: `subscriber + topic` for reads, `topic` for writes.
- Never create one thread for each key or each user.
- A slow task blocks the other keys on its queue. Keep I/O out of the queue, or accept the cost.
- In a distributed system, one owner for each key gives the same result. Examples: a partition, an actor, a Durable Object.

## One owner or one lock for a composite (103)

Trigger: one operation updates two structures, such as a map by ID and a sorted index.

Steps:
1. Put both structures behind one object.
2. Give that object one lock, or one owner thread.
3. Change both structures in one critical section.

Traps:
- A concurrent map does not make the composite safe. The race is between the two structures.
- Lock only the paths that read and write together. Pure appends can stay outside the lock.
- Release the lock in `finally`.
- A global lock makes the code effectively single-threaded. Say so.

## Request collapsing (067)

Trigger: many concurrent misses for one key each start the same load.

Steps:
1. On a miss, look for an in-flight future for the key.
2. If one exists, return it.
3. If not, start the load, store its future in the map, and return it.
4. When the load completes, remove the future from the in-flight map.

Traps:
- Store the future before it completes. Otherwise two callers start two loads.
- In a cache with expiry, add the entry to the expiry index only after the load completes.
- A failed load must leave the map too, or every caller gets the same error forever.

## Immutable snapshot swap (047)

Trigger: readers must never see an aggregate that is half updated, such as a set of balances.

Steps:
1. Readers get a reference to the current immutable snapshot.
2. A writer copies the snapshot, applies all changes to the copy, and swaps the reference in one step.

Traps:
- Readers can see old data. Accept that, or do not use this recipe.
- With many writers, serialise the writers, or two swaps can lose an update.

## Timeouts and lock expiry (063, 103)

Trigger: any wait on something that can fail to complete. Any lock that an owner can fail to release.

Rules:
- Give every blocking wait a timeout.
- Give every distributed lock an expiry.
- Make the timeout error specific. Include what timed out and after how long.

## Never block the request path (062, 092, 093)

Trigger: a request handler calls a database or a remote service.

Rules:
- A function that does I/O returns a future.
- Run blocking I/O on its own pool. Use one pool for each concern: database, remote API, client.
- Do not block on a future inside a constructor. Pass the resolved value in.
- A hot-path decision, such as a rate limit check, stays local and returns a plain value.

## Retry, backoff and dead-letter queue (072, 076, 080)

Trigger: a transient failure, such as a timeout, a network error or a 5xx.

Steps:
1. Classify the error. Retry only errors that can recover.
2. Wait by the policy: periodic or exponential. Inject the sleep function.
3. Stop after the maximum attempts.
4. Send the failed item to a dead-letter queue with its error.

Traps:
- Invalid input fails the same way every time. Reject it at once.
- Never retry a payment or another user-initiated money action on its own. Tell the user.
- Retries need idempotent writes. Otherwise a retry duplicates the effect.

## Backpressure (097, 109)

Trigger: a producer sends faster than a consumer can process.

Rules:
- Lower the send rate to a consumer that fails. Raise it slowly when it recovers.
- Bound every increase. An unbounded `threshold++` never stops.
- Hold messages for a later pull when the consumer cannot take a push.

## Idempotent writes (072)

Trigger: a client or a queue can send the same write again.

Rules:
- Each write carries an ID. A duplicate ID is accepted and ignored.
- Events are immutable. A correction is a new event.
- If the client makes the ID, combine user, time and machine to make it unique.

## Persist before you acknowledge (109)

Trigger: a crash must not lose a write that the system accepted.

Steps:
1. Write to the durable store.
2. Update the in-memory state.
3. Return success.
4. On start, rebuild the memory from the store before you serve requests.

## Push or pull (107, 108, 109)

Trigger: readers need updates.

Rules:
- Use push for real-time needs. Fall back to pull only when push capacity runs out.
- Use the lightest transport for the direction. One-way server to client: server-sent events. Two-way: WebSockets. Fallback: long polling. Avoid short polling.
- With skewed fan-out, push to normal readers on write, and let readers pull heavy writers on read.
- The queue keeps each consumer's offset, not the consumer. Allow a manual reset for replay.
- For push delivery, require an acknowledgement. Retry, then dead-letter.

## Concurrency tests (102, 103)

- Test that a blocking call returns only after its event.
- Run many concurrent callers and check the invariants.
- Send inputs out of order on purpose.
- Make the test harness obey the client contract. Do not send an "end" before its "start".
- Control time with an injected clock.
