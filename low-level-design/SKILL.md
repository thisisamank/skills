---
name: low-level-design
description: How an agent should writes code - order of work, object modelling, APIs, data structures, concurrency, extensibility and tests. Use when writing, designing or refactoring non-trivial code, modelling a new domain, adding a feature to existing classes, or choosing a design pattern.
---

# Low level design

These rules come from the 97 lessons of the InterviewReady Low Level Design course. They do not depend on a language. Apply them in the language of the repo.

The rules work with `ponytail`, not against it. Simple and correct first. Structure only where it pays.

## References
Read a reference only when its trigger applies.

| File | Read it when |
|---|---|
| `references/typescript.md` | The repo is TypeScript. It maps every rule to TypeScript and has the code for the concurrency recipes. |
| `references/patterns.md` | Before you add a design pattern. Each pattern has its trigger and the cases where it is wrong. |
| `references/smells.md` | Before you finish a change, and during a review. Each smell has its fix. |
| `references/concurrency-recipes.md` | Shared state, ordering, retries, timeouts, push or pull. |
| `references/worked-designs-projects.md` | The task is like a game engine with changing features, a payment tracker, a cache, an event bus or a rate limiter. |
| `references/worked-designs-live.md` | The task is like chess, a logger, an orchestrator, a calendar, a trading app, live scores, a social feed, a message queue, a coupon engine, a schema or version store, or a booking system. |

## Order of work
1. Write the requirements as a numbered list. Mark each one core or extra. Build only the core ones.
2. Say what is out of scope: auth, payments, notifications, analytics, metadata. State that they exist, then skip them.
3. Walk the real flow end to end: the user acts, the system responds, the result comes back. Get the services and methods from this flow.
4. Write the API contracts before the bodies: name, inputs, return value, errors, blocking or async.
5. Model the nouns and their behaviours. Then add only the fields that those behaviours need.
6. Code the hardest part first: the algorithm, the concurrency, the eviction. Stub plain CRUD with an in-memory map.
7. Make it work, even if it is ugly. Run it.
8. Write tests. Then refactor with the tests green. Refactor only where the payoff is larger than the effort.
9. Add retries, validation and polish last. Say what you deferred.

For a product that engineers use (a queue, a cache, a rate limiter), start from the API surface. Skip the user stories.

## Objects
- Give each class one reason to change. Split engines by role. For example, one class makes moves, one class applies rules, one class suggests moves.
- Put a behaviour on the object that owns its data. Example: `player.flip()`, not code outside that rebuilds the player.
- Keep fields private. Every mutation goes through one method that validates it. A parent mutates its children. It never gives a child out for other code to mutate.
- Derive state when you can. Do not store a flag that you can compute, such as `hasMoved` or a cell colour.
- Use one source of truth. Do not copy fields from one object into another and keep them in sync.
- A collection field with its own behaviour becomes a class. Examples: `Watchlist`, `Timeline`, `BalanceMap`.
- A nested map like `Map<K, Map<K2, V>>` means a class is missing. Wrap it, and give its behaviour a home.
- Several maps with the same key become one map of objects: `Map<TopicId, Topic>`.
- Wrap primitive IDs in types (`TopicId`, `UserId`) where a mix-up is possible.
- Use an enum for a status or a type with more than two values. Use a boolean only for a true yes/no.
- Name things for what they are. Rename a class when its name is wrong. Use no abbreviations and no magic numbers.
- Put each class in its own file. Group the files into folders by concern: models, services, algorithms, exceptions.

## Inheritance and composition
- Use inheritance only when "X is a Y" is true and every subtype supports every inherited method.
- Put a method on the base type only if all subtypes need it. If you are not sure, put it on the concrete type.
- If a subtype cannot implement a method, split the interface. Do not throw "not supported".
- Prefer composition for configuration and for behaviour that changes. Use `Game` with a `GameConfig`, not `TimedGame` and `LeisureGame`.
- If you cannot say what a subclass adds, delete it.
- An abstract class holds shared state and shared steps. An interface holds only a contract.
- Casts to make a hierarchy work are a smell. Use composition or generics.
- Accept the most general type you can. Return the most specific type you can.

## Functions and APIs
- Keep public signatures stable. Put internal needs in private helpers. Do not change a public signature to fit them.
- Do not take a parameter that the function does not use. Do not return something the caller already has.
- Pass the whole object when the callee needs more than its ID. Store IDs, not whole objects, in caches and persisted structures.
- Return a result object, not a bare boolean, when the caller needs the reason. Example: what applied, the amount, the failure reason.
- A function that does I/O returns a future or `Promise`. A hot-path check, such as a rate limit decision, returns a plain value.
- Throw specific errors. Never throw or declare a generic `Exception`.
- Make writes idempotent by ID. A duplicate ID is accepted and ignored.
- Treat events as immutable. Send a correction as a new event.
- Inject the clock and other non-deterministic inputs. Do not read the system time inside logic.
- Do not block on a future in a constructor. Pass the resolved value in.

## Control flow
- Do not nest loops three or more levels deep. Extract a function, use iteration helpers, or reuse an existing class.
- Keep `if` nesting shallow. Check related conditions together, in one place, and decide once. Split checks caused the double move and double winner bugs.
- Add guards for terminal states. Example: after a win, ignore further moves.
- Extract duplicated blocks. Pass the part that changes as a function. Revert the extraction if the result is harder to read.
- Readable beats short. A shorter method that is harder to read is worse.
- Keep a growing list of independent rules as data: a list of `(context) => result` functions. To add a rule, add to the list. If order matters, use an ordered chain or plain sequential code.

## Simulation and copies
- Code that explores or simulates (an AI search, a dry run, a preview) works on a copy. It never mutates live state.
- Prefer a copy to undo. Undo breaks concurrency and has cascading effects.
- Check that the copy is deep enough. Shared mutable references leak changes.

## Data structures
- Write the needed complexity for each operation first. Then pick the structures.
- A map by ID gives an O(1) lookup. A sorted map or a heap gives "earliest" or "next". A sorted structure gives the "since T" seek in O(log n).
- When no single structure serves every operation, keep two or more that hold the same object reference.
- Sort by the right key. Break comparator ties on purpose, for example LFU ties by LRU.
- Put a policy, such as LRU or LFU, in the comparator or a strategy. Do not branch on the policy name.
- When a key is overwritten, remove its stale index entries.
- Store a series that repeats as a rule with exceptions. Expand it only for the queried range.
- In a schema, choose what to store from the requirements, and how to store it from the queries. Use a join table for many-to-many. Never store a list in one column.
- Copy fields you query out of opaque blobs into indexed columns.

## Concurrency
- Before you add a lock, list the shared mutable state and the interleavings that break it.
- Separate the two needs. Locks give exclusivity. Routing to the same thread gives ordering.
- For per-key ordering, use a keyed executor: N single-thread queues, chosen by `hash(key) % N`. Pick the narrowest key that still gives the guarantee.
- Never create one thread per user or per key.
- Never block a request thread on I/O. Give each concern its own pool: DB, remote API, client.
- A concurrent map does not make a composite of two structures safe. Use one lock or one owner for the two structures.
- Lock only the paths that read and mutate together. Release in `finally`. Say so when a global lock makes the code effectively single-threaded.
- Give every wait a timeout. Give every lock an expiry or a guaranteed release.
- For aggregates that readers must not see half-updated, build a new immutable snapshot and swap the reference.
- Collapse concurrent misses for one key: store the in-flight future in the map and return it to every caller.
- Prefer push (complete a future) to spin or poll loops.
- Persist before you acknowledge. After a crash, rebuild memory from the store before you serve.

## Failure handling
- Retry only errors that can recover. Invalid input fails the same way every time.
- Make the retry policy pluggable: max attempts, wait, exponential backoff. When retries run out, send the item to a dead-letter queue. Do not only print the stack trace.
- Add backpressure. Slow down sends to a consumer that fails.
- Do not retry a failed payment or other user-initiated money action. Tell the user and let them submit again.

## Tests
- Test behaviour, not algorithms that change. Hardcode the inputs. Do not depend on AI or random output.
- Name tests by behaviour (`GameplayTest`), not by class.
- Test one unit at a time. Test the factory and the game logic separately.
- Start with the worked example from the spec. Then add edge values and units (seconds against milliseconds).
- For concurrent code, test that blocking calls block, run many threads, and send inputs out of order. The test harness must obey the client contract.
- When a test fails, fix the code, not the test.
- Debug nulls in three passes: missing or empty values, then which code updates each structure, then concurrency.

## Do not
- Do not add a pattern because it exists. Use it only when its trigger in `references/patterns.md` is present.
- Do not add base-class methods "in case" of a future subtype.
- Do not write a singleton by hand. Use module scope or the DI container.
- Do not use Observer for one fixed subscriber. Call it directly.
- Do not build admin-editable or config-driven rules for rare cases. Keep rare cases in code.
- Do not use WebSockets for one-way updates. Use server-sent events.
- Do not build a full ACL system when a user-to-object access level mapping works.
- Do not add special-case config, such as "3 users on Sunday". Put it in the key.
- Do not optimise for perfection where a greedy approach is good enough. Say what the approach cannot do.
- Do not write deep domain rules that are not the point. Stub them and confirm scope.

For a review or restructure, use `code-structure-pass`. These rules are the standard it applies to logic and object design.
