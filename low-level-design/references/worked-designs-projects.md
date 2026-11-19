# Worked designs: course projects

These are the five projects of the course, built step by step. Read the section for a problem that is like your task. Copy the reasoning, not the class names. Signatures do not depend on a language. File numbers refer to `interviewready-lld-transcripts`.

The transcripts are auto-captions. Some names are a best reading.

## Tic-Tac-Toe Game Engine (files 002-042)
**Core requirements:**
1. Start a game and get a board.
2. Make a move on the board.
3. Report the game result: over or not, and the winner or draw.
4. Let an AI suggest a move. The target is any turn-based board game. Tic-tac-toe (3x3) is the concrete case.
5. Add later: report forks, time limits per game and per move, several AI levels, move history with undo, and email/SMS on a win or a return after 10 days.

**Out of scope:** Other games (chess, Go, hexagonal boards) only drive the abstractions. No UI, server, persistence or real email/SMS delivery.

**Objects:**
- `Board` - abstract class, then interface. Methods: `move`, `copy`. Owns no cells.
- `CellBoard` - sub-interface of `Board` with `getSymbol(i, j)`.
- `TicTacToeBoard` - 3x3 array of string of cells, a `History`, and its own `RuleSet`. Has `Symbol` enum (X, O).
- `Cell` - immutable row and column. Shared through a static pre-built `getCell`.
- `Player` - symbol and user. Has `flip()` and time used.
- `User` - id, last active time.
- `Move` - player and cell.
- `GameState` - isOver and winner.
- `GameInfo` and `GameInfoBuilder` - state plus fork player and fork cell.
- `GameEngine` - `start` and `move`.
- `RuleEngine` - `getState`, `getInfo`. Holds rule sets.
- `Rule` and `RuleSet` - a board-to-`GameState` function; a typed list of rules.
- `AIEngine` - `suggestMove`.
- `Placement` chain - `OffensivePlacement`, `DefensivePlacement`, `ForkPlacement`, `CenterPlacement`, `CornerPlacement`. All are singletons.
- `Strategy`, `StrategyFactory`, `BasicStrategy`, `SmartStrategy`, `OptimalStrategy`.
- `History` - list of boards (memento). `BoardProxy` - string form of a board.
- `Game` - board, `GameConfig`, players, last move time, winner. `GameCreator` (factory).
- `EmailService`, `SMSService`, `EmailCommand`, `SMSCommand`, `NotificationDetails`.
- `Event`, `EventBus`, `Subscriber`.

**API:**
- `start(gameType) -> Board`
- `move(board, move) -> Board`
- `getState(board) -> GameState`
- `getInfo(board) -> GameInfo`
- `suggestMove(board, player) -> Move`
- `Board.copy() -> Board`
- `History.getBoardAtMove(index) -> Board`, `History.undo() -> Board`
- `Game.move(move, timestampMillis) -> void`
- `GameCreator.createGame(maxTimePerMove?, maxTimePerPlayer?) -> Game`
- `Strategy.getOptimalMove(board, player) -> Cell`
- `Placement.place(board, player) -> Cell or none`, `Placement.next()`
- `EventBus.publish(event) -> void`, `EventBus.subscribe(eventType, subscriber) -> void`

**Hard part:**
- Win detection. Row, column and diagonal checks were copy-pasted in one 90-line `getState`. The course unified them with a traversal function `(i, j) -> cell` for the inner loop. It then moved each check into a `Rule`. `getState` runs the rules in a list and returns the first that ends the game. A rule set needs no order.
- AI exploration. The smart move plays a winning cell, else blocks the opponent's winning cell, else the first empty cell. A first version played moves on the live board and corrupted it. The fix is to copy the board (prototype), play on the copy, and discard it. Cells are immutable strings, so a shallow array copy is safe.
- Fork detection. A fork is a cell where the player moves, the opponent is forced to block, and the player still wins. It reuses `DefensivePlacement` and `OffensivePlacement` on board copies. The first version had 4-5 nested loops. It is cut to 3 over empty cells. The course still flags it as a code smell.
- Optimal move order. Win, block, fork, block opponent fork, center, corner, any. The order matters, so the course uses a chain of responsibility. Each placement names the next one.
- Timers. `Game.move` takes a timestamp from the caller. It adds the elapsed time to the player. The player loses if the per-game limit or the per-move limit is passed. Both limits sit in one condition. A win check follows each move.
- History. `History` stores one board copy per move. Jumping back to move k removes the later boards. Removing from a list shifts indexes, so the loop removes the last element. Memory is cut by storing a `BoardProxy` string.

**Decisions and trade-offs:**
- Chose board copy over undo for AI exploration. Undo breaks under concurrency and is hard for chess. The cost is more objects.
- Chose a two-argument function over iterator for traversal. An iterator holds one position. A streak check needs row and column.
- Chose a `GameConfig` field in `Game` over `TimeGame` and `LeisureGame` subclasses. All games have a config. Composition removes the subclasses.
- Chose plain if/else in `Game.move` over a rule engine for timing. Timing rules depend on order. A rule set has no order.
- Chose `CellBoard` over `getSymbol` on `Board` or generics. A hexagonal or 3D board cannot implement `getSymbol`. That breaks Liskov substitution. The generic rule set was removed after this.
- Chose strategy plus factory over the state pattern. State transitions were an N-by-N mesh that depended on board and player. A clear graph did not exist.
- Chose composition (`NotificationDetails`) over a base command class. A base builder returns the base type. `SMSService` needs `SMSCommand`. A typecast is unsafe.
- Chose a plain factory for `Game`, a builder for `GameInfo`. Builder fits many optional fields. Factory fits hidden creation logic.

**Evolution:**
1. Write all code in one file with no design. It works but duplicates a lot.
2. Split classes into files and packages (game, state, board types). Hide `cells` behind `getCell`.
3. Single responsibility: `GameEngine`, `AIEngine`, `RuleEngine`. `Move` carries its player.
4. Add unit tests.
5. AI needs lookahead. Mutating state hurts. Add `copy` (prototype).
6. DRY: merge row and column checks, then diagonals, using a two-argument function. Iterator compared and rejected.
7. Open-closed: fork request. Add `GameInfo`, then move win checks into a `Rule` list.
8. Builder for `GameInfo` to stop constructor growth.
9. Timers. Add `Game`, `GameConfig`, `User`. Use composition over inheritance.
10. Extract `RuleSet`. Generics conflict with Liskov. Then add `CellBoard` (interface segregation, dependency inversion).
11. Optimal AI. Chain of responsibility with singletons.
12. Undo and history: memento.
13. Memory: `BoardProxy`, shared `Cell` (flyweight). Replace X/O strings with an enum.
14. State pattern tried and dropped. `GameCreator` factory. Strategy plus `StrategyFactory`.
15. Notifications: command pattern, builder, composition, then `EventBus` (publish-subscribe).

**Tests:**
- `GameplayTest` with a shared setup step. Cases: row, column, diagonal and reverse-diagonal wins, a nine-move game, and a computer win.
- The first tests relied on the AI choice and broke when the board rejected a move on an occupied cell. The fix hardcodes both players' moves, so the AI is out of the tests.
- `GameTest` for timed games. It passes explicit timestamps, not the system clock. Setup: 11 s per player, 5 s per move, or 3 s per move.
- Bugs found: moves allowed after a winner, seconds vs milliseconds, and the board copy result not assigned. Two others: the win check missing after a move, and a wrong `GameConfig` set by the factory.
- Anti-pattern noted: one test covered the factory and the game. Test the factory alone.
- Suggested but not done: board-building helpers, and edge cases with 1-3 ms left.

## Splitwise-like Payment Tracker (files 043-053)
**Core requirements:**
1. Add an expense.
2. Edit an expense.
3. Settle an expense. Keep the old record. Set a `settled` flag. Do not count settled expenses in balances.
4. Group expenses. A group holds many expenses. Add, edit and settle work for them.
5. Simplified settlement. Remove transitive debts (A owes B 10, B owes C 20 gives A pays C 10, B pays C 10). The user can still choose the plain way.
6. Every expense must sum to zero. Validate this on add.

**Out of scope:** Comments, the activity log, and simple CRUD (`getUser`, `getGroup`, `getExpense`). The user service is not coded.

**Objects:**
- `Expense` - id, `BalanceMap`, metadata (title, description, image URL, timestamp), `settled` flag, group ID.
- `BalanceMap` - wrapper over a user ID to `Amount` map. It replaces nested maps.
- `Amount` - value plus currency (USD only). Immutable. `add` returns a new `Amount`.
- `User` - user ID, image URL, bio.
- `Group` - id, title, description, image URL, list of user ID strings (not `User` objects, to keep the cache small).
- `GroupExpenses` - group ID plus list of expenses. Kept apart from `Group`.
- `PaymentGraph` - map of user to `BalanceMap`: how much each user pays each other user.
- `GroupService` - checks group membership, sums group balances, returns the graph.
- `ExpenseService` - holds group ID to expense list (stands in for the database). Builds the graph.

**API:**
- `GroupService.getGroupPaymentGraph(groupId, userId) -> PaymentGraph`
- `GroupService.getBalances(groupId, userId) -> BalanceMap`
- `ExpenseService.getGroupExpenses(groupId) -> list of Expense`
- `ExpenseService.getPaymentGraph(balances) -> PaymentGraph`
- `ExpenseService.addExpense(expense) -> void` (no-op if group ID is null)
- Designed, not coded: `editExpense(expenseId, ...)`, `settleExpense(expenseId)`, `getGroupBalances(groupId)`.
- Cached: `getGroupExpenses`, `getGroupPaymentGraph`.

**Hard part:** Turn net balances per user into a payment graph with few transactions.
- Sum all expense balances per user: `get-or-default(user, 0).add(amount)`.
- Put positive balances in one max-heap and negative balances in another (priority queue; negate the comparator for descending order).
- While both heaps are non-empty: poll the top of each. Transfer the minimum of the two absolute values. Record the edge: receiver maps to payer with the amount.
- Push the node with a remainder back into its heap. If both are equal, both leave.
- Each step removes at least one node. Result: O(n log n) time, at most n-1 edges.
- The method is greedy, not optimal. The course shows a case where the greedy result has 6 transactions and 5 are possible. A second case gives 8 against 7, even with equal-pair cancel.
- The exact minimum is a subset-sum / knapsack problem. The course skips it for interviews.

**Decisions and trade-offs:**
- Chose the ER-diagram (state-first) approach over behaviour-first because LLD must stay close to code.
- Chose a separate `GroupExpenses` object over an expense list in `Group` because a group exists without its expenses and the list would bloat it. Kept a group ID in `Expense` as a deliberate denormalisation.
- Chose a `settled` flag over deleting or changing records because the old record stays and settle is an edit.
- Chose greedy two-heap matching over optimal minimisation because it is simple, fast and enough for an interview.
- Chose immutable objects (build a new map, swap the reference) over read/write locks because readers get stale but consistent data (eventual consistency).
- Chose to cache only `getGroupExpenses` and `getGroupPaymentGraph` because many users read them. The cache is not implemented.
- Chose to code `getGroupPaymentGraph` first over models first because it covers both algorithms. The needed behaviour then defines the state.
- Chose `Amount` and `BalanceMap` over a nested `map of user to map of user to balance`, and user ID strings over `User` objects in `Group` and `BalanceMap`.

**Tests:** Unit tests with in-memory services and assert statements.
- Group balances: group 123, three expenses. A +10, B +20, C -30. A -50, B +10, C +40. A +90, C -90. Expected totals: A 50, B 30, C -80. The author found a bug (`add(Amount)` did not add) by printing step by step, then fixed it.
- Payment graph: six users A-F, expenses added with a new `addExpense` method (added so tests reuse setup). Expected edges: A gets 90 from E, D gets 70 from B, F gets 40 from C, D gets 10 from E. Edge order is not checked.
- Only happy paths. The course notes that edge cases could follow.

## Cache (files 059-067)
**Core requirements:**
1. Read your own writes: a client sees its own write in later reads.
2. Multiple write policies: write-through and write-back.
3. Expiry time per entry.
4. Multiple replacement algorithms: LRU and LFU (LFU breaks ties with LRU).
5. Asynchronous results: `get` and `set` return futures, so reader threads stay free.
6. Request collapsing: many requests for one key cause one database call.
7. Hot loading: prefetch a given list of keys at startup.
8. Event logging: log each load and each evict (to a log or a message queue).

**Out of scope:** Distributed consistency across caches. The course assumes horizontal partitioning, so all requests for one key reach one cache. A short interview covers only the core problems. The `DataSource` is a dummy.

**Objects:**
- `Cache` - public `get` and `set`. Owns the map, the two sorted structures and the thread array.
- `DataSource` - `load(key)` and `persist(key, value)`. Both return future. The course stubs it.
- `Record<VALUE>` - the value, `loadTime` and `AccessDetails`.
- `AccessDetails` - `accessTimestamp` and `accessCount`. Kept separate from `loadTime`.
- Persistence algorithm enum - `WRITE_THROUGH`, `WRITE_BACK`.
- Eviction algorithm enum - `LRU`, `LFU`. It only picks the comparator.
- `records` - a concurrent hash map from key to Record. Later it holds a future of Record.
- `expiryQueue` - a sorted map from load time to a list of keys, ordered by load time.
- `priorityQueue` - sorted map from `AccessDetails` to a list of keys. The comparator depends on LRU or LFU.
- `executors` - an array of single-thread queues.

**API:**
- `get(key) -> Future<Value>`
- `set(key, value) -> Future<void>`
- `Cache(persistenceAlgorithm, evictionAlgorithm, dataSource, expirySeconds, hotLoadKeys)` - the constructor parameters, as built across the code videos.
- Internal: `getInAssignedThread`, `setInAssignedThread`, `addToCache(key, valueFuture)`.

**Hard part:**
- Read-your-writes. Send every operation on one key to one single-thread queue. Pick it with `hash(key) % threadCount`. A thread runs its tasks in order, so a read after a write sees the write. Without the key-to-thread link, two cores could run the read first and return the old value. Both data locality and sequential execution are needed. Locks are the other option. The course names them but does not build them.
- Async. A blocked reader thread cannot read other sockets. Head-of-line blocking follows: slow remote calls block fast local ones. A future returns at once and fills later. It also allows chaining and composition. A plain blocking future does not.
- Fast eviction. LRU needs the last access time. LFU needs the access count. Expiry needs the load time. One sorted map cannot serve all three. Use two sorted structures:
  - `expiryQueue` by load time. Expiry does not depend on how often the entry is read.
  - `priorityQueue` by `AccessDetails`. LRU compares timestamps. LFU compares counts, then timestamps.
  - Both are concurrent sorted maps. Operations cost O(log N).
  - The value lists are copy-on-write lists, created with put-if-absent.
- Cleanup. On access or overwrite, remove the old entry from both structures. Otherwise stale timestamps pile up. Update both structures on every `addToCache`.
- Overflow, at `addToCache` when size reaches the threshold (500 in the example):
  1. Lazy expiry: take the first `expiryQueue` entry. Check that it is really expired. Remove its keys from the map and the priority queue.
  2. If still full, take the first `priorityQueue` entry. Evict one key. Remove it from the map, `expiryQueue` and `priorityQueue`.
  - `get` also checks expiry on read. If expired, it reloads from the `DataSource`.
- Write policy. Write-through: persist first, then add to the map. Write-back: add to the map, then start an async persist and do not wait. The course accepts the data-loss risk.
- Hot loading. For each key, call `dataSource.load`, then `addToCache`.
- Request collapsing. Store a future in the map, not a value. The first request for a key starts the load and stores the future. Later requests get the same future. `addToCache` takes the value future. It puts the future in the map at once. It builds the `Record` in a map step on the future. Eviction only finds completed entries, because the expiry queue is filled after completion. So a blocking wait is safe there.
- Events. `addToCache` logs a load. Overflow eviction logs an evict.

**Decisions and trade-offs:**
- Chose write-through as the personal default over write-back because it is simpler and consistent. Write-back is faster but can lose data on power loss.
- Chose "read your own writes" over full consistency because it covers most ordering needs. It needs no cross-cache notification.
- Chose key-hashed single-thread queues over locks because the ordering is then implicit. No lock expiry or dead-owner problem.
- Chose two sorted structures over one sorted map because LRU, LFU and expiry use three different sort keys.
- Chose a concurrent sorted map over a plain sorted map because the cache must be concurrent. It still gives O(log N).
- Chose a composable future over a plain blocking future because it allows callbacks and composition.
- Chose keys in the priority queue over full records because the code only needs keys to remove.
- Chose to keep `get` and `set` signatures and split internals (`addToCache`) over changing the public API.
- Chose lazy expiry (only on overflow, plus a check on read) over a background sweeper because it is simpler. The cost is stale entries that stay until the cache is full.

**Tests:** The testing video is not in files 059-067. File 067 ends with "head to testing", and the course says a machine-coding round expects tests and working code. It names no test cases. Note that the course expects bugs in the code and plans to fix them there.

## Event Bus (files 071-083)
**Core requirements:**
1. Many publishers and many subscribers use one bus.
2. Events have an ID, a type or name, and free-form attributes.
3. Publishers post events to topics. One event can belong to many topics.
4. Subscribers subscribe per topic. Each subscription is push or pull. Both are configurable.
5. Idempotency: the bus accepts an event with a known ID, acknowledges it, and does not process it again.
6. Retry on failure. Max attempts and algorithm (exponential backoff or fixed interval) are configurable.
7. After max retries, send the event to a dead letter queue for later diagnosis.
8. Events are immutable. No update. No delete. Reads only.
9. Pull from an event ID or from a timestamp.
10. Ordering: writes are ordered per topic. Reads are ordered per subscriber per topic.

**Out of scope:** Distributed deployment of the bus, clock sync and vector clocks, persistence, real network delivery to the subscriber IP.

**Objects:**
- `EventBus` - owns the topic log, subscriptions, indexes, executors, retry algorithm, dead letter queue, and timer.
- `Event` - ID, name, attributes, timestamp. Immutable.
- `EventID`, `Topic`, `SubscriberID` - wrapper classes over String. The compiler catches mixed-up keys.
- `Entity` - ID, service name, IP address. A publisher and a subscriber are the same kind of thing.
- `Subscription` - subscription ID, subscriber ID, topic, type (pull or push), precondition, handler.
- `SubscriptionType` - PULL or PUSH.
- `Precondition` - function from event to boolean. It filters events before delivery.
- `KeyedExecutor` - array of single-thread queues. Routes a task by key hash.
- `RetryAlgorithm` - abstract class with `retry`.
- `ExponentialBackoff`, `PeriodicRetry` - subclasses of `RetryAlgorithm`.
- `Timer` - wraps the system clock. Tests replace it.
- `RetryableException`, `RetryLimitExceeded`, `EventNotFoundException`.
- `FailureEvent` - event, failure time, exception.
- Dead letter queue - an `EventBus` instance.

**API:**
```
publish(topic, event) -> void
subscribe(topic, subscription) -> void
poll(topic, subscriberID) -> Event
getEvent(topic, eventID) -> Event
getEventsBetween(topic, t1, t2) -> list of Event
setIndexFromTimestamp(topic, subscriberID, timestamp) -> void
setIndexFromEvent(topic, subscriberID, eventID) -> void
push(subscriber, event) -> void
KeyedExecutor.submit(key, task) -> Future<void>
KeyedExecutor.get(key, supplier) -> Future<T>
RetryAlgorithm.retry(task, param) -> result
```

**Hard part:**
- Ordering versus concurrency. One thread per key gives total order but is slow. One thread per user does not scale to millions of users.
- Solution: causal ordering on a fixed pool. Only tasks that depend on each other share a thread.
- `KeyedExecutor` holds T single-thread queues. A task goes to index `hash(key) % T`. T comes from a properties file (the demo uses 10). Tasks on one thread run in order.
- Reader pool: key is `hash(subscriberID, topic) % RT`. One subscriber on one topic is ordered. Other subscribers and other topics run in parallel.
- Writer pool: key is `hash(topic) % WT`. This orders all publishers on a topic. It is a stronger guarantee than the read side.
- Hashing by topic alone on reads would serialize all subscribers of a topic. Hashing by subscriber alone would serialize all topics of one subscriber. Both are needless.
- Different keys can share a thread. This costs some concurrency but saves threads and memory.
- Data structures per topic:
  - Topic log: `concurrent map from Topic to list of Event`. Append-only.
  - Subscriber index: `topic -> subscriberID -> index`. Poll reads and increments it in O(1). Clients do not need to store subscription IDs.
  - Event index: `topic -> eventID -> index`. Map lookup in O(1). It replaced a linear scan in `getEvent`.
  - Timestamp index: `topic -> sorted map from long to EventID`. the sorted map's next-higher-entry lookup finds the next event in O(log n) even if the timestamp does not exist. A hash map fails here.
- Complexity: poll O(1). Publish O(log n) from the sorted map. Range read O(log n) seek plus a sequential scan. Set index from timestamp O(log n). Set index from event O(1).
- Retry: `retry(task, param)` applies the task and catches `RetryableException`. At the max attempts it throws `RetryLimitExceeded`. A non-retryable exception propagates at once. Exponential backoff sleeps `1000 * 2^(attempt-1)` ms, so 1, 2, 4 seconds. `PeriodicRetry` sleeps a fixed `timeToMillis`. Max attempts and wait come from the constructor.
- Push path: `addEventToBus` updates the log and the timestamp index. It then finds push subscriptions on the topic and runs `retry` with `subscription.handler`. If `RetryLimitExceeded` is thrown, the bus publishes a `FailureEvent` to the dead letter queue.

**Decisions and trade-offs:**
- Chose a fixed thread pool with hash routing over a thread per user because millions of users cost too many threads and too much mapping memory. The price is some lost concurrency.
- Chose causal ordering over global ordering because only dependent tasks need order. Independent topics and subscribers run in parallel.
- Chose strong order per topic on writes and weaker order per subscriber and topic on reads. Hashing writes by publisher and topic would loosen the guarantee.
- Chose logical indexes over timestamps for ordering because clocks drift across machines. Synchronized clocks and vector clocks are heavier than this problem needs.
- Chose one `Subscription` object in a topic-to-subscriptions map over separate push and pull maps because the two maps were identical. The object holds the type and a precondition filter.
- Chose a concurrent sorted map over a hash map for timestamps because seek needs a sorted lookup for a missing key.
- Chose an abstract `RetryAlgorithm` and an injected `Timer` over hard-coded sleeps. The user decides what is retryable, and tests control time.
- Chose wrapper types and composite objects over raw String maps because they make intent clear, catch errors at compile time, and allow separate unit tests. The course notes this may be overkill.

**Tests:**
- Setup: `EventBus` with `PeriodicRetry` (5 attempts, 1 second), no dead letter queue, and a `Timer`.
- Test 1, default behavior: publish event 1 to topic 1 before any subscriber exists. Subscribe with a PULL subscription and a precondition that is always true. `poll` returns null. Publish event 2. `poll` returns a non-null event with ID 2.
- The first run threw a null-pointer error. The fix used three phases:
  1. Remove nulls. Use get-or-default with an empty concurrent hash map. Use put-if-absent for new topic maps. A sorted map cannot hold null, so a placeholder event ID stands in.
  2. Fix interactions. `subscribe` now sets the subscriber index. The course lists each data structure and checks where it is set. The remaining gap: the index must point at a real position in the log, not the timestamp lookup result. This was left for phase 3.
  3. Fix concurrency issues. The transcript ends before this phase.

## Rate Limiter (files 088-098)
**Core requirements:**
1. Accept or reject each request by time and count (for example 100 per second).
2. Split the system into a thin client library and a simple server.
3. The client decides accept or reject. It must be fast and must not call the server per request.
4. The server stores the config per service and the aggregated counts. A central data store syncs many server instances.
5. A service registers config: service, key, time unit, amount. A key is generic, for example `userId_sunday`.
6. The caller supplies callbacks: `onAccept` and `onReject`. Rejection does nothing by default.
7. The caller can plug in an algorithm. The default is sliding window.
8. Back pressure: a failed request lowers the threshold.
9. The client sends aggregated counts to the server on a heartbeat (every 3, 5 or 10 seconds). The client pulls global state in the same call.

**Out of scope:** caching, exception handling, scaling servers, degrading features, HTTP/gRPC wiring, config file parsing, retry policy. Token bucket and leaky bucket are only named.

**Objects:**
- `RateLimiterClient` - holds service name, the algorithm, `onAccept`, `onReject`, a fixed thread pool, and a `RateLimiterServer` handle.
- `Algorithm` (abstract) - `shouldAccept`, `backPressure`, `forwardPressure`.
- `SlidingWindow` - extends `Algorithm`. Owns a list of timestamps, a threshold and a time unit.
- `RateLimiterServer` (client side) - sends `readServiceConfig`, `readKey` and `updateKey` requests. The transport is `null` in the demo.
- `ReadConfigRequest` - service name and request ID.
- `RateLimitedTimeUnit` - own enum: second, minute, hour, day. It blocks nanoseconds so serialization is safe.
- `ServiceConfiguration` - service, limit (int), time unit, key. Service and key stay separate so you can list all keys of a service.
- `Request` (abstract) - service name and ID. `UpdateRequest` extends it with count, timestamp (long) and key.
- `Response` (abstract) - ID. `UpdateResponse` extends it.
- `RateLimiter` controller - `updateKeyMetrics`, `getKey`.
- `ServiceConfig` controller - `updateServiceConfig`.
- `ApiGateway` - entry point. Owns a fixed pool of 10 threads. Converts JSON to objects.
- `RateLimiterDao`, `ServiceConfigDao` - own the SQL for their tables.
- `DbConnector` - runs SQL. Also has a typed read: `read(sql, resultType) -> list of results`.
- Packages: models, request, response, controller, dao, db, api (gateway), algorithm.

**API:**
```
// client
RateLimiterClient(serviceName, onAccept?, onReject?)   // callbacks: (resource) -> Future<void>
setAlgorithm(algorithm or null)   // null selects SlidingWindow
shouldAccept(resource) -> boolean
getServiceConfiguration() -> Future<ServiceConfiguration>
readKey(key) -> Future<map of string to Limit>   // Limit = {amount, timeUnit}
updateKey(key, amount, timestamp) -> Future<void>

// algorithm
shouldAccept(resource, timestamp) -> boolean
backPressure(resource, timestamp)
forwardPressure(resource, timestamp)

// server
ApiGateway.updateKey(json) -> void   // writes to the socket
ApiGateway.updateServiceConfig(json) -> void
RateLimiter.updateKeyMetrics(updateRequest) -> Future<UpdateResponse>
ServiceConfig.updateServiceConfig(serviceConfiguration) -> Future<void>
```

**Hard part:** The client must decide in memory. The server owns shared state.
- Sliding window is a list of `long` timestamps. They stay sorted because each one is appended.
- On `shouldAccept`, remove every timestamp not newer than `now - timeUnitMillis`. The lecturer uses a bulk remove or a filter. This is O(n).
- Optimization left as an exercise: stop at the first fresh timestamp. This is O(expired).
- Accept if `threshold >= timestamps.size()`. Else reject. On accept, append the timestamp.
- Back pressure runs on reject. It does `threshold--`.
- Forward pressure `threshold++` is wrong. Each accept raises the limit, so the window grows without bound. The lecturer leaves it empty.
- Options for forward pressure: `+0.5` per accept, or `+0.1` (one per 10 accepts).
- Smarter back pressure: if the failed request is under 100 ms old, do `threshold--`. Else subtract 0.1.
- The lecturer keeps the plain version for simplicity.
- The threshold comes from `ServiceConfig.amount` and `RateLimitedTimeUnit`.
- Threads: a request-reading thread must never block on IO.
  - `ApiGateway` runs each call on its own 10-thread pool.
  - Each `Dao` or `DbConnector` should own its pool.
  - Controllers use `map stepAsync(fn, executor)` on a future.
  - The client has its own fixed thread pool (10 in the demo; 1 or 2 is more realistic) for `readKey` and `updateKey`.
  - `onAccept` and `onReject` do not run on the client pool. The caller owns their thread.
- Config is a future but the constructor needs a value. Two fixes:
  - Call a blocking wait on the future in the constructor. It blocks and throws checked exceptions.
  - Pass `ServiceConfiguration` in from outside. This is dependency inversion.
- Sync: each client sends aggregated counts to the server. The server writes to the data store. Instances pull the store to get the global total. If a heartbeat fails, keep the last known state.

**Decisions and trade-offs:**
- Chose client-side decisions over server-side decisions because every check must be fast. The server then stays simple.
- Chose a generic `key` string over custom rule fields because `userId_sunday` covers special cases. This avoids over-engineering.
- Chose to keep the algorithm out of server storage because clients choose their own. Mixed algorithms across clients of one service are the caller's problem.
- Chose `boolean` over `Future<boolean>` for `shouldAccept` because a rate limiter must not make network calls per check.
- Chose `Future` returns for `readKey` and `updateKey` over blocking calls because the signature then shows IO. Timeouts go inside the future.
- Chose callbacks as `Future<void>` functions over plain functions because logging or a dead letter queue can be async. The caller owns their thread.
- Chose a one-way heartbeat (client to server) over two-way because it is simpler. On a missed ping, the client keeps its last state.
- Chose a separate API gateway pool, DAO layer and packages over one class because it isolates threads and concerns. The lecturer says to describe this in an interview but not to build all of it in 45 minutes.
- Chose own `RateLimitedTimeUnit` enum over a built-in time-unit type because nanoseconds could break serialization.
- Chose to share state between `onReject` and the algorithm (fail count) over a separate back pressure class. This is simple but coupled.

**Tests:** The transcripts show no unit tests. The only check is that the code compiles without obvious errors. The lecturer notes that the HTTP/gRPC calls return `null` and are not wired. The lecturer suggests the stale-entry loop and stream variants as exercises.

