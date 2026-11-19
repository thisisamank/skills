# Worked designs: live classes and mock interviews

These are the live design classes and the mock interviews of the course. Read the section for a problem that is like your task. Copy the reasoning, not the class names. Signatures do not depend on a language. File numbers refer to `interviewready-lld-transcripts`.

The transcripts are auto-captions. Some names are a best reading. Files 107, 111 and 115 have no formal API, so their signatures are derived.

## Chess (file 101)

**Core requirements:**
1. Build an app that can play chess.
2. Model the pieces: Pawn, Rook, Knight, Bishop, Queen, King.
3. Every piece can move, capture, and check the enemy king.
4. Every piece returns all its possible moves.
5. Reject any move that leaves the own king in check.
6. Reject a capture of a piece of the same color.
7. Support special moves: pawn decimal move, en passant, promotion, king castling.

**Out of scope:** Scale, networking, high-level design. Castling logic and full check detection (the speaker says an interviewer will not ask for them). Engine optimizations.

**Objects:**
- `Piece` - abstract class. Holds color, current position, and a pointer to its board. Holds the shared move logic.
- `Pawn`, `Rook`, `Knight`, `Bishop`, `Queen`, `King` - subclasses. Each defines its own `isValid` rule.
- `Board` - owns a map of `Position` to `Piece`. Makes moves and exposes cell access.
- `Position` - a row and column pair.
- `Color` - enum: WHITE, BLACK.

**API:**
- `Piece.move(start, destination)`
- `Piece.getAllPossibleMoves() -> list<Position>`
- `Piece.isValid(current, destination) -> boolean` (abstract)
- `Piece.getColor() -> Color`
- `Board.makeMove(piece, destination)`
- `Board.getPiece(position) -> Piece or null`
- `Board.setPiece(row, col, piece)`
- `isKingInCheck(color) -> boolean`

**Hard part:** The shared move template. `move` first calls `isValid`. Then it handles legality for all pieces in one place.
- Return false if the own king is already in check and the move does not fix it.
- Copy the board into a temporary board. Apply the move there.
- Run `isKingInCheck(color)` on the temporary board. If true, the move is illegal.
- Look up the destination in the board map. If a piece exists with the other color, mark a capture and remove it. If it has the same color, return false.
- If the move checks the enemy king, notify the opponent.
- Subclasses only implement the rule that differs per piece (for example, pawn, two squares from the start rank).
- The speaker leaves `isKingInCheck` as a stub. He says it checks whether any enemy piece can capture the king.
- Pawn decimal move needs no "has moved" flag. The current position shows if the pawn is on its start rank. A pawn cannot return to it.
- Bishop color needs no extra logic. The start square and the diagonal rule keep it on its color.
- The board holds a map from position to piece. The speaker also discusses an 8x8 cell matrix.

**Decisions and trade-offs:**
- Chose a whiteboard design before code over opening the editor, because a wrong inheritance choice costs a rewrite.
- Chose inheritance (`Rook` is a `Piece`) over composition (`Pawn` has a `Piece`), because a piece is the thing that moves, captures, and checks.
- Chose an abstract class over an for `Piece`, because capture and check logic is common and can live in the base class.
- Chose to extract common behavior (capture, check test, same-color guard) into the base class and keep only `isValid` per subclass.
- Chose a temporary-board simulation for king safety over per-piece check rules, because one check covers all pieces.
- Chose a position-to-piece map over a stored "moved" flag for the pawn, because the position already gives the state.
- Chose `Board` as the only writer to cells over exposing cells (`board.setPiece(row, col, piece)` over `getCell(...).set`), because the board can then add validation. The speaker also suggests a singleton board.

## Logger (file 102-103)

**Core requirements:**
1. Implement a `LogClient` with `start(processId)`, `end(processId)`, and `poll()`.
2. `start` and `end` are events. The logger records the time (`System.currentTimeMillis`).
3. `poll()` prints the earliest-started process, but only after it has ended. Format: `process <id> started at <t1> and ended at <t2>`.
4. Output order follows start time, not end time. A later-started process that ended first waits.
5. `poll()` blocks until that process ends.
6. All three methods run in O(log n) or better.
7. Callers can call all methods concurrently. The client calls `start` before `end` for the same ID.
8. Make the code testable.

**Out of scope:** An `end` that arrives before its `start`. The speaker assumes the client orders them. He names a second option: buffer the early `end` until `start` arrives.

**Objects:**
- `Process` - final `id`, final `startTime`, mutable `endTime` (initial -1).
- `LogClientImpl` - holds the data structures, the lock, the futures, and the task scheduler.
- `thread-safe hash map` (string to Process) - id to process. Gives O(1) lookup for `end`.
- `thread-safe sorted map` (start time to Process) - ordered by start time. Gives the earliest process for `poll`.
- `list of future` (snapshot-on-write) - waiting pollers.
- `lock` - guards `poll` and `end`.
- `list of single-thread queues` - 10 single-thread executors.
- `Timer` - injected time source. A mock replaces it in tests.

**API:**
- `start(processId)`
- `end(processId)`
- `poll() -> string` (blocking; `get` with a 3-second timeout)

**Hard part:** No single structure gives fast `start`, `end`, and `poll`.
- Linked list: `end` is O(n).
- Hash map: `poll` cannot find the minimum.
- Heap: `end` cannot find the id.
- Tree map keyed by id: wrong order.
- Solution: a composite. The hash map gives O(1) `end`. The ordered map keyed by start time gives the earliest process. Both hold the same `Process` object. `end` sets `endTime` on the map entry, and the ordered map sees it through the shared reference. It needs no second update.
- Complexity: `start` O(log n), `end` O(1), `poll` O(log n). A heap plus a map also works.
- `poll`: if the first entry has an end time, remove it from both structures and print. Otherwise create a `future`, add it to the list, and wait.
- `end`: if the ended process is the first entry, remove the first future and complete it.
- Concurrency has two problems. Exclusivity: a lock around `poll` and `end`. Ordering: `start` and `end` of one ID must run in order.
- Ordering fix: hash the process id, take it modulo 10, and run the call on that single-thread executor. Same ID means same thread, so `start` runs before `end`.
- Only `start` runs in parallel. Locking every method would make the logger single-threaded.
- A concurrent hash map alone does not help. Two structures change together, and the pair is not atomic.

**Decisions and trade-offs:**
- Chose hash map plus ordered map over one structure, because no single structure meets O(log n) for all three methods.
- Chose to share the `Process` reference over updating the ordered map in `end`, because it keeps `end` at O(1).
- Chose futures (push) over spinning or a class-wide mutex in `poll`, because pollers wait without a busy loop and many can block at once.
- Chose a lock on `poll` and `end` only over a lock on all methods, because `start` stays parallel. `poll` blocking inside the lock causes head-of-line blocking. Returning the future would avoid that, but the API must block.
- Chose a hash-to-thread task scheduler over locks for ordering, because same-thread execution is sequential.
- Chose `thread-safe sorted map` over `sorted map`, because it is thread safe and has O(log n) expected time.
- Chose an injected timer over `System.currentTimeMillis`, because tests then control time.
- Chose a 3-second `get` timeout over an unbounded wait, because every API needs a timeout.
- Tests: a blocking test (polls block until the first process ends) and a concurrency test (about 1000 tasks, random commands, client order guaranteed, output checked in order).

## Orchestration Service (file 104)

**Core requirements:**
1. Accept a client request and return a response.
2. Call several downstream services (service 1, 2, 3). Services depend on each other.
3. Validate the request first. Reject an invalid request with an exception or a notification.
4. Decode the request into a list of parameters.
5. Map the parameters to the services to call.
6. Call the services in dependency order. Return the final service response.

**Out of scope:** Database storage (an in-memory map replaces it). Concurrency code and locks (the instructor calls this machine-coding scope).

**Objects:**
- `OrchestrationSystem` - owns the validation engine (composition), decode service, algo service, and calling service. Holds a list of validators.
- `ValidationEngine` - checks that the user is valid, and that the parameters are valid (for example, funds or stock in the account).
- `Request` - holds a description, a URL, a list of parameters, and headers. The parameter type stays open (map or object).
- `Response` - holds one integer cost. Generalize later.
- `DecodeService` (interface) - turns a request into a list of parameters.
- `AlgoService` (interface) - turns a parameter list into the order of service calls.
- `CallingService` (interface) - runs the services in order and returns the response.
- `Service` (interface) - one downstream service. Each service has an implementation class.
- Dependency map - parameter to service list. Stored in the calling service and passed to the decoder.

**API:**
```ts
DecodeService { decode(request) -> list<string> }
AlgoService { getOrder(params) -> list<Service> }
CallingService { getResponse(request) -> Response }
```

**Hard part:** Dependency ordering. Service B can wait for service A. A response from one service can feed the next. The solution is a topological sort. Treat services as graph nodes and dependencies as edges. Example: if A needs B and C, and C needs B, the order is B, C, A. `AlgoService.getOrder` hides the algorithm. Callers see only the ordered list. Another algorithm can replace it. The flow is: client call, validate, decode, get order, call services in order, return the response. The instructor names one concurrency risk. One call updates the dependency map while another call reads it. For example, a service scales out or is removed (remove S5, add S6). Fix: take a write lock during the update. In a distributed setup, keep one global store and lock it. A lock hurts performance, but only updates need it. The instructor also names thread-safe maps as a framework option. Complexity is not stated in the transcript.

**Decisions and trade-offs:**
- Chose composition for the validation engine over aggregation because the engine cannot exist without the system.
- Chose interfaces for the services over concrete classes. One reason: many implementations of one method (email and SMS notify). Another reason: new versions of the calling service.
- Chose topological sort for ordering over a fixed call list because services depend on each other.
- Chose to keep the dependency map in the calling service over the decoder because other services can reuse it.
- Chose a write lock on map updates over no locking because a read during an update returns stale or partial data. The lock slows other callers.
- Chose generic service names over a real domain. Real examples named: calling platform (billing, routing, legality checks), Amazon order (inventory, pin code), brokerage order (valid user, then funds).

## Calendar Event Scheduling (file 105)

**Core requirements:**
1. Create an event: start time, end time, description, metadata, invited users.
2. Create recurring events (daily, weekly, monthly, third Saturday, and so on). A recurring event can have no end.
3. Update an event. For a recurring event, update this event, this and following events, or all events.
4. Get all events of a user in a date range. Include events that overlap the range.
5. Invite users to an event. RSVP is an update.

**Out of scope:** Notifications (a separate email or SMS service). Public and private events and sharing (permissions; Zanzibar paper mentioned). Notes (a link to a Google doc). Plans and SSO. Meet link (plain metadata).

**Objects:**
- `BookingService` - the only service. Exposes the three APIs.
- `Event` - id, start time, end time, metadata. Stored in the event table.
- `Participant` (table) - user id, event id, and relation data (join time, RSVP state).
- `Blueprint` - the template of a recurring event: start, optional end, recurrence rule, details, id.
- Recurrence rule - a cron-like expression. Allow only a subset: day, weekday, monthly.

**API:**
```ts
createEvent(userId, eventId?, start, end, metadata, users, recurrence?)
getEvents(userId, start, end) -> list<Event>
updateEvent(userId, eventId, changes, scope: "this" or "thisAndFollowing" or "all")
```

**Hard part:** Recurring events. Do not store each instance. A recurrence can be infinite, and one update would touch hundreds of rows, locks, and notifications. Store one blueprint and generate instances at read time.

- Schema: event table (id, start, end, data). Index on start time. Participant table (user_id, event_id, relation state).
- Read query: join participant `p` with event on `p.event_id = event.id`, filter `p.user_id` and the start and end range.
- Update "this and following": set the end time of the old blueprint. Create a new blueprint from the change date to infinity. Send one notification for the whole series.
- Update "just this event": end the original blueprint before the date. Create a one-event blueprint for that date, with the update. Clone the original from the day after to infinity. Result: three blueprints.
- Read for a range: find the first occurrence inside the range without stepping one by one. Example: weekly event, query is one year ahead. Linear stepping takes about 52 steps. Use exponential jumping (7, 14, 28, 56 ...) to overshoot or hit the range. Then use binary search. Then generate events forward and backward in the range. Complexity is not stated.

**Decisions and trade-offs:**
- Chose a server-generated event id over a client id for no-collision simplicity. A client id gives idempotent retries but can collide across clients. Compromise: client id combined with user id and timestamp, as in Snowflake (machine id plus time).
- Chose a participant join table over a participants column in the event table or an events column in the user table. Reasons: the relation is many-to-many, access goes both ways, the relation holds data (join time, state), and a big column bloats rows and causes lock contention.
- Chose a blueprint plus generation over storing every instance because recurrence can be infinite. Also because an update would fan out to hundreds of rows and notifications.
- Chose splitting blueprints on update over editing one blueprint because past events must stay unchanged.
- Chose the Prototype pattern (clone) for new blueprints. A Builder fits partial updates.
- Chose exponential jump plus binary search over linear stepping for efficiency.
- Chose a cron subset over free cron expressions to limit the rule space.

## Stock Trading App like Zerodha (file 106)

**Core requirements:**
1. A user views stock prices and a watchlist.
2. A user searches for stocks.
3. A user places buy and sell orders. Order types: Market and Limit.
4. A user has one portfolio of held stocks.
5. The system validates the user and the funds or stock position before an order.
6. The system executes the order and updates the portfolio.
7. The system sends a notification when an order succeeds or fails.
8. The system manages users, a wallet and stock data (add stock, update price).

**Out of scope:** KYC, payments as a core flow, recommendations and analytics, mutual-fund metadata, sector diversification, GTT order types, order history tracking, the stock exchange integration, controllers and database.

**Objects:**
- `Stock` - price, description, company name, metadata, stock type enum.
- `User` - email, password, one `Portfolio` (composition), watchlists, active orders, wallet money.
- `Watchlist` - separate entity holding a set of stocks. Stocks can be added and removed.
- `ActiveOrders` - separate entity holding the open orders of a user.
- `Order` - stock, user object, quantity, price, `isBuyOrder` flag, `OrderType` enum (MARKET, LIMIT), `OrderState` enum (in progress, successful, failed).
- `Portfolio` - user id, `map of Stock to PortfolioStock`, money invested, current money.
- `PortfolioStock` - quantity and average price for one stock.
- `Notification` - description. Type and action buttons are optional metadata.
- `UserService` - list of users, create user, wallet add and withdraw.
- `StockService` - map of stock id to `Stock`, get and update price, add stock, search.
- `OrderService` - place, cancel and read order state.
- `ValidationEngine` - checks the user and the funds or stock position.
- `NotificationService` - interface. `SmsNotificationService` and `EmailNotificationService` implement it.

**API:**
```ts
UserService { createUser(user); addMoney(user, amount); withdrawMoney(user, amount) }
StockService { getStockPrice(stockId) -> number; updateStockPrice(stockId, price); addStock(stock) }
OrderService { placeOrder(user, stock, quantity, price, isBuy); cancelOrder(order); getOrderState(order) -> OrderState }
NotificationService { sendNotification(description, user) }
```
Public REST APIs: place buy order, place sell order, login, get user details, get portfolio, get stock info, get watchlist. Do not expose order execution.

**Hard part:**
- Order flow in `placeOrder`: create the order, call `ValidationEngine`, then branch.
  - On failure, call `NotificationService` with the reason.
  - On success, call execute. Execute deducts funds (buy) or checks and removes stock (sell), calls the exchange, updates the portfolio, then sends a success notification.
- Buy and sell share method names but run different logic. Buy checks funds, removes funds, updates the portfolio. Sell checks the stock position, removes stock, updates the wallet. Model this as a Strategy chosen at runtime.
- `PortfolioStock` keeps a weighted average price. Example: 2 at 100 and 2 at 150 gives 4 at 125.
- `Portfolio` uses a map. A buy updates one entry in O(1). A list needs an O(n) scan.
- `StockService` uses a map from stock id to `Stock` for O(1) lookup.
- Money invested changes only when an order executes. Current money is derived from live prices.
- A Market order executes at once at the current stock price. A Limit order waits until the price meets the limit. The session did not build limit-order matching.

**Decisions and trade-offs:**
- Chose composition between `User` and `Portfolio` over aggregation because a portfolio cannot exist without its user.
- Chose separate entities for watchlist, active orders and portfolio stock over raw lists and maps in `User` because they are complex objects that change often.
- Chose an `OrderType` enum over a Boolean because more types (GTT) can come. Kept `isBuyOrder` as a Boolean because only two sides exist.
- Chose to pass a full `User` and `Stock` object over ids because the stock carries the current price and the code has no database.
- Chose Strategy for buy and sell over one branching method because the logic differs but the method is the same.
- Chose no Observer for `NotificationService` because the order has one fixed subscriber. Use Observer when `OrderService` publishes to many services (notification, invoice) that change at runtime. Observer also replaces polling.
- Chose no automatic retry on a failed order because Zerodha does not retry. The user places a new order.
- Chose interfaces for services over abstract classes because there is no shared code and interfaces allow a versioned second implementation (for example, an `OrderService` v2 with validation). Use an abstract class when subclasses share code.
- Use request and response DTOs for `placeOrder` when the parameter list grows.
- Prices reach the client as a unidirectional server stream. The client sends subscribe and unsubscribe events when the watchlist changes.

## Live Score Updates, Polling and WebSockets (file 107)

Note: this session is a system-design discussion, not a class-level LLD. It has no class diagram. The fields below come from the talk.

**Core requirements:**
1. Show live scores for matches (the example is a cricket score app). One ball event must reach all interested users in real time.
2. Users can also request the current score.
3. Store per match: match id, team or country id, match type, start time.
4. Store per ball a comment: comment id and ball id (for example 19.1).
5. An admin UI lets an operator record an event (four, six, goal) in seconds. The score and an initial placeholder comment appear at once.
6. The admin can edit the comment later (about 30 seconds to 2 minutes). The edit must also be sent as a notification.
7. The broadcast goes to users who have the match open. Other users pull.

**Out of scope:** Profile service, session service, gateway, player and team rosters, and the admin typing speed (named as a separate hard problem).

**Objects:**
- `Match` - match id, team ids, match type, start time.
- `Comment` - comment id, ball id, score data, text. Starts from a template. An admin edits it.
- `AdminUI` - fast input for events and comment edits.
- `NotificationServer` - holds client connections and pushes updates. A single monolith is assumed first.
- `ConnectionManager` - decides which connections stay open. Uses LRU eviction.

**API:**
The transcript gives no signatures. It names these operations:
- `getScore(matchId)` - pull request.
- `subscribe(matchId)` - open a long-lived connection (SSE or long poll).
- `publishEvent(matchId, event)` - admin action. The server broadcasts it.
- `editComment(commentId, text)` - admin action. The server broadcasts it.

**Hard part:** Deliver one event to many clients with a limited number of open connections.
- Short polling: the client asks at fixed intervals. It is simple, but it wastes requests and adds latency. The server may throttle it.
- Long polling: the server holds the request until an event exists. The client sends a new request right after each response. It sends fewer messages than short polling. The client must reconnect when the server drops the connection. The client can also retry after a timeout (for example 5 minutes).
- WebSockets: peer-to-peer and two-way. The client needs only server-to-client data, so this is too heavy.
- Server-sent events (SSE): one HTTP request. The server then sends events over a long-lived connection. It is lighter than a WebSocket and simpler to keep alive.
- Connection limit: when a server is full, evict with LRU. Keep connections of active users. Drop the least recently active.
- Thrashing: if all users are active and the limit is too low, the server creates and deletes connections without useful work. Scale out.
- Capacity: one machine can hold hundreds of thousands to about a million connections. A TCP connection does not need its own file descriptor. Heap memory is the practical limit.
- Sharding: shard subscribers by match or by country (consistent hashing was proposed).
- Fallback: if push reaches its limit, the next step is pull.

**Decisions and trade-offs:**
- Chose long polling over short polling because it sends fewer messages and gives faster updates.
- Chose SSE over WebSockets because only server-to-client data is needed and SSE is lighter, runs on HTTP, and is easier to keep alive.
- Chose push for active users and pull for the rest because the business needs push to as many users as possible. Pull is a forced fallback.
- Chose LRU eviction over dropping all connections because a mass drop causes a thundering herd, memory spikes, and poor user experience.
- Chose scale-out over more eviction because thrashing wastes work. The cost is more servers.
- Rejected polling-only for all users, although slow networks (for example in India) favor it. Active tabs get push. Others poll.
- Keep connection metadata separate from the connection gateways, so a deploy does not break all connections (a thundering-herd chapter is referenced).

## Twitter with Trending (file 108)

**Core requirements:**
1. A profile creates tweets.
2. Users react to tweets and comments.
3. Users comment on tweets and on comments (threads).
4. Users follow profiles.
5. Each profile has a timeline of tweets from followed profiles.
6. A shared trending list exists. A tweet joins it when it passes a like threshold (for example 1000).
7. The system sends notifications (publisher-subscriber, may change) and supports search. These were listed but not designed.
8. Interview focus chosen by participants: timeline, follow, trending.

**Out of scope:** Retweet, polls, follow requests and private profiles, media types, password handling, search, notifications, tweet length validation (to be added outside `Tweet`).

**Objects:**
- `Profile` - name, tweets, followings, followers, `isCelebrity` flag, `lastSeen` time, timeline. "Profile" replaces "user" because one person can own many profiles.
- `Tweet` - extends `Reactable` and `Commentable`. Holds description and `createdAt`.
- `Comment` - extends both. Holds description, `createdAt`, and the author profile.
- `Reaction` - author profile and an optional type enum (like, thumbs up).
- `Timeline` - list of tweets.
- `Reactable` - abstract class. Holds the reactions list, `getReactions()`.
- `Commentable` - abstract class. Holds the comments list, `addComment()`, `getComments()`.
- `ProfileService` - owns the list of profiles. Creates and deletes them.
- `TweetService` - creates tweets and sets `createdAt`.
- `CommentService` - adds a comment to any `Commentable`.
- `ReactionService` - adds and removes reactions on any `Reactable`. Calls the trending service.
- `TimelineService` - builds timelines with push and pull.
- `TrendingService` - keeps the shared trending list.

**API:**
```ts
ProfileService.createProfile(username, password) -> Profile
ProfileService.deleteProfile(profile)
TweetService.createTweet(description, profile) -> Tweet
CommentService.comment(target, profile, description) -> Comment
ReactionService.addReaction(target, profile)
ReactionService.removeReaction(target, profile)
TimelineService.addToTimelines(tweet, followers)
TimelineService.pullCelebTweets(celebFollowings, lastSeen) -> list<Tweet>
```

**Hard part:** Build timelines for accounts with very different follower counts.
- Normal profiles (limited followers): push. On a new tweet, the service adds it to each follower timeline. The service can run this in parallel.
- Celebrities: pushing to millions of timelines would crash the system. Use pull instead.
- Pull runs only when the user opens the app. The service splits followings into a celebrity list and a normal list.
- The service uses `lastSeen` on `Profile` to select only new celebrity tweets.
- A celebrity tweet list is sorted by time because tweets are appended. Binary search finds the first tweet after `lastSeen`. Cost is O(log n) per celebrity, not a full scan of up to millions of tweets.
- Trending: `ReactionService` counts likes after each add (`getReactions().length`). When the count passes the threshold, it calls `TrendingService`. The list is shared by all users. A tweet that stays on top stays on top for everyone.
- Other trending criteria can use the same hook in their own services. The alternative is a cron job that scans all tweets.

**Decisions and trade-offs:**
- Chose abstract classes `Reactable` and `Commentable` over duplicate fields and methods because `Tweet` and `Comment` share the same data and logic. A new type (for example Reels) needs no new service methods. An cannot hold the shared list or default methods.
- Chose one `comment(Commentable, ...)` method over separate tweet and comment methods because the code was duplicated.
- Chose a hybrid push and pull timeline over push only because celebrity tweets would overload the system.
- Chose binary search on a time-sorted list over a linear scan because lists can be very large.
- Chose to trigger trending from `ReactionService` over a polling job because it reacts at once and avoids a full scan. The cost is a coupling between the two services.
- Chose `Timeline` and `Tweet` as separate classes over inline lists because lists need add and remove logic.
- Said the shared abstract class is not a factory pattern. It only removes duplication.

## Pub/Sub Message Queue (file 109)

**Core requirements:**
1. A publisher adds a message to a topic.
2. A subscriber pulls the next message from a topic.
3. A subscriber registers as a push subscriber for a topic. The queue pushes each new message to it.
4. The queue stores the pull position (offset) for each pull subscriber. The subscriber does not store it.
5. Pull subscribers need no registration. A new subscriber starts at index 0.

**Out of scope:** Batch push, batch poll, flush or delete, retry with dead letter queue, back pressure, encryption, database persistence, delivery guarantees. The transcript discusses these but does not code them.

**Objects:**
- `MessageQueue` - owns `map of topicId to Topic`. Exposes the public API. Routes messages to push subscribers.
- `Topic` - owns the messages list, the pull offsets and the push subscribers for one topic.
- `Message` - the event payload.
- `Subscriber` - a consumer, such as an analytics service.

**API:**
```ts
class MessageQueue {
  addToQueue(topicId, message)
  register(topicId, subscriber)
  poll(topicId, subscriber) -> Message
}
class Topic {
  addMessage(message)
  initialize(subscriber)
  getPushSubscribers() -> list<Subscriber>
  getNext(subscriber) -> Message
}
```
`register` means push only. `poll` is for pull.

**Hard part:** Three maps keyed by topic are hard to manage. The maps are the message list, the subscriber offsets and the push subscriber list. The design merges them into one `Topic` object. A single `map of topicId to Topic` finds the topic in O(1).

`Topic` fields, all private:
- `list of Message messages`
- `map of Subscriber to int pullOffsets`
- `list of Subscriber pushSubscribers`

`getNext(subscriber)`:
1. Read `offset = pullOffsets.getOrDefault(subscriber, 0)`.
2. Store `offset + 1` back.
3. Return `messages.get(offset)`.

Each call is O(1). Do not remove the message on poll. Other subscribers still need it.

`addToQueue` flow:
1. Get the topic by id.
2. Call `topic.addMessage`.
3. Get `topic.getPushSubscribers()`.
4. Send the message to each push subscriber.

Push stays inside `addToQueue`. It is not a public API. `MessageQueue` does the broadcast, not `Topic`. `Topic` does not own routing.

Only pull subscribers need offsets. A push subscriber gets the message at once and has no index. The transcript considers renaming the map to `pullOffsets`.

Persistence, as discussed but not coded: write to the database synchronously in `addToQueue`. Return success only after the database accepts the write. On a failed write, return a service-unavailable error so the client retries. After a crash, reload the topics, offsets and registrations from the database before serving requests.

**Decisions and trade-offs:**
- Chose a `Topic` class over three parallel maps because it encapsulates the data and removes nested `get` and `put` chains.
- Chose private fields with `addMessage` and `getNext` methods over direct field access. Validation or a data structure change then stays inside `Topic`.
- Chose `getNext` returning a message over `getOffset` returning an index. The caller does not need the offset. Delete or add logic stays in one place.
- Chose the queue to store offsets over the subscriber storing them. A restarted subscriber does not lose its position. The cost is no replay by the subscriber. An admin can reset the offset manually.
- Chose no registration for pull subscribers because they ask when they want data. Only push subscribers register.
- Chose to allow both push and pull per topic. Pull needs memory for lagging subscribers. Push needs fast broadcast and more bandwidth. Both together cost both.
- Deferred retry with exponential back-off, then a dead letter queue, and back pressure. Back pressure applies to push only. The queue lowers the send rate after failures.

## Coupon Rule Engine for Food Delivery (file 110)

**Core requirements:**
1. On checkout, show all coupons the user can apply. Also show near-miss coupons, such as "spend 30 more".
2. Check if a coupon is valid for the user, cart and restaurant.
3. Support coupon clubbing. Decide if a proposed coupon can combine with applied coupons.
4. Return a deducted amount, a cashback amount, or both.
5. Let admins add flexible rules from a dashboard. Do not change code per coupon.
6. Rule inputs: valid from, valid till, recurring daily time window, payment method, minimum order value, user, restaurant.
7. Coupon scope is user, restaurant or platform wide.

**Out of scope:** Coupons written by developers in code ("system coupons"), such as a Black Friday coupon for electronics only. OR rules. Tax on the deduction. Coupon creation UI. Validation of admin rules (raised, not solved).

**Objects:**
- `Coupon` - code, validity dates, `userId` (nullable), `restaurantId` (nullable), `platformWide` flag, payment method, linked rules.
- `Rule` - one condition as a function object. Input is a request, output is a boolean.
- `CouponRequest` - holds the coupon, cart and user.
- `Cart` - items, order value, user. It identifies the restaurant.
- `RuleEngine` - runs all rules of a coupon. It does not know what the rules are.
- `CouponResponse` - applied coupon set, total deducted amount, total cashback.

**API:**
```ts
apply(coupon, cart, appliedCoupons) -> CouponResponse
getList(cart) -> list<Coupon>
```
`CouponResponse` holds `set of Coupon`, `deductedAmount: decimal` and `cashback: decimal`. Pass `cart`, not user and restaurant. The cart carries both. The admin dashboard creates coupons outside this API.

**Hard part:** Two problems exist. These are rule storage and execution, and listing candidate coupons fast.

Rule engine:
- Model each rule as a function from `CouponRequest` to boolean. A rule is an object, so it serializes.
- Store rules per coupon id in the database, as JSON or text. Load them at apply time and parse them into function objects.
- The engine takes all rules of the coupon and requires every rule to return true (AND).
- Without a function type, parse the text. This is like writing a small compiler.
- The author showed a tic-tac-toe game. Each win check (row, column, diagonal, draw) is a rule in a `RuleEngine`. A new win condition needs a new rule only.
- Coupon rules include minimum order value, user match, `validFrom`, `validTill`, payment method and time window.

Clubbing: the proposed coupon is always kept. If it clubs with the applied set, keep both. If not, drop the applied coupons and keep the proposed one. The transcript says coupons need tags for clubbing. It does not define the tag design.

`getList`: rules are JSON, so a query cannot search them. Store scope as plain columns on the coupon.
1. Filter by validity dates. Index on `validFrom` and `validTill`. Cache the valid coupons.
2. Query by `userId` (indexed).
3. Query by `restaurantId` (indexed).
4. Query platform wide coupons (`platformWide = true`).
5. Run the rule engine on each candidate.

User and restaurant sets are small. Platform sets can reach hundreds or thousands. Show only about 10. Rank paid placement first, then rotate platform coupons at random. Add payment method metadata to prefilter platform coupons. Prefetch user and restaurant coupons while the user fills the cart.

Usage limits (use once): the rule engine would need a database call, so it is hard. Check the orders table, or keep a platform-to-user used mapping, with a cache.

**Decisions and trade-offs:**
- Chose a rule engine with an admin dashboard over manual coupon creation, a config file, or developer if-else code. Config files are tedious to change. Developer code does not scale. The cost is less flexibility than code. Only the known rule types are possible.
- Chose rules as function objects over hard-coded checks. A new rule needs no engine change.
- Chose scope columns outside the rules over searching rule JSON. Complex objects are not easy to index or query.
- Chose AND-only combination over OR for now. OR is more complex.
- Chose a single API with a cart and a proposed coupon over many calls. The UI sends fewer objects. The cart implies user and restaurant.
- Chose to keep system coupons in code over putting them on the dashboard. They are rare, specific and too flexible to model.
- Chose usage-count checks outside the rule engine over a rule. The engine would need database access, and a "used by user" record fits better in the orders table.
- Chose to remove old coupons on a clash over rejecting the new one. This matches Zomato. The author notes the user experience is poor.

## Database Schema Design and Git Storage (file 111)

**Core requirements:**
1. Store users, organizations, teams, and repositories (public or private).
2. Store authorization: who can read, write, or admin which organization, repository, or file.
3. Store files, directories, branches, commits, and file diffs, so any commit can be restored or reverted.
4. Store pull requests with state, reviewers, and review comments.
5. Find the content of a branch from its root node, with few queries.

**Out of scope:** Real Git internals such as pack files and garbage collection; the diff algorithm; the interviewer defers efficient tree reads and commit-graph traversal to a later class.

**Objects:**
- `User` - id, email, two-factor data. Keep login statistics in a separate table.
- `Organization` - name; members stored in a separate membership table.
- `OrgMember` - one row per (org, user, type), where type is admin or member.
- `AccessEntry` - (user or user set, object, relation); relation is editor, viewer, or commenter.
- `Token` - signed credential that carries identity and a time-limited admin right.
- `Project` - repository; has a public or private flag.
- `Ref` - (project, branch name, root node hash).
- `ObjectStore` - hash to storage location (S3 URL) for every file version.
- `Tree` - directory version; lists its children.
- `Blob` - file version; has no children.
- `Commit`, `Diff` - stored as objects, like Git.
- `PullRequest`, `Reviewer`, `ReviewComment`.

**API:** The transcript gives no signatures. The method: list the product features, turn each feature into an API, list the objects each API needs, and map the objects to tables. Do not design from the database side.

**Hard part:**
- Content addressing. Hash the file content (SHA-1 in Git). The hash is the file id. `ObjectStore` maps hash to location. Lookup by hash is fast. File bytes live in S3, not in the database. If the interviewer allows only an RDBMS, store the bytes in the database.
- A change makes a new hash. Git stores a whole new copy of the file locally. Git compresses only when it sends data over the network (pack files).
- Directory version. A directory hash depends on its children hashes. Change file B and its parent A becomes A'. Unchanged children C and D stay the same and are reused. This is a persistent data structure. Each change creates new nodes on the path from the file to the root.
- Branch lookup. A `Ref` row stores the root hash per branch. Read the root, read its children, repeat. Two tables hold the whole tree: the object table and the ref table.
- Known flaw. A full tree read costs one query per level, or one join per level. Seven levels mean seven queries. This is too slow for a review. The answer: most reads do not need the full repository. Only `git clone` needs it. Other reads need a few files, a commit, or a diff between two commits.
- Commit history is a graph, not a line, because of branches and merges.
- Access check. Store one row per (user, object, relation). Index by user or by object, based on the main query.

**Decisions and trade-offs:**
- Chose a product-first schema over a database-first schema because it is easier to imagine as a user.
- Chose one row per member with a type column over one row holding all admins because it follows normalization, supports an index on member, and does not leak other members. Cost: listing all members of both types needs more rows or a join.
- Chose a layout driven by access pattern over a fixed layout because speed depends on the queries. If you always read all members, keep them together or cache them.
- Chose a simple user-to-object access list over Zanzibar-style rules because GitHub does not need generic rules. Keep the (user, object, relation) idea.
- Chose a signed token over a database token lookup for temporary rights because the server verifies the signature with its public key and needs no mapping.
- Chose S3 plus a hash table over blobs in the database because it reads fast and scales.
- Chose to rewrite parent directories on each change because reads are far more common than writes.
- Stop at second normal form (2NF). Most teams skip third. NoSQL teams often skip normalization.

## Tic-Tac-Toe (file 112)

**Core requirements:**
1. Model an N x N board and two players who take turns.
2. Make a move and detect the winner or a draw.
3. Keep the design extensible for optional features, chosen after clarifying questions.
4. Follow-up: `makeMove` and `getWinner` must run in O(1).

**Out of scope:** Timed play (chess clock), tournaments, AI, ELO rating. Spectators and statistics appear only as optional features. The transcript lists them and does not design them in detail.

**Objects:**
- `Board` - an N x N integer matrix (empty, player one, player two). Holds the status (player one won, player two won, in progress, draw) and the current player flag.
- `Move` - the player and the cell (row, column).
- `User` - id and statistics (wins, losses, rating). The statistics object is open.
- `Game` - id, two user ids, and the list of moves.

**API:**
```ts
Board.init()
Board.getWinner()
Board.getStatus()
Board.makeMove(move)
move(player, row, col) -> -1, 0 or 1
```
The return value of `move`: 0 means no winner, +1 means player one won, -1 means player two won.

**Hard part:** Winner detection.

- Approach 1, O(N) per move: only the mover can win, and the winning line must contain the new cell. Check the cell's row, column, diagonal (only if row equals column), and reverse diagonal (only if row equals N-1-column). At most 4N cells. Player one writes +1, player two writes -1.
- Code-clarity step: merge the four checks into one loop from 0 to N with four booleans (row, column, diagonal, reverse diagonal). Remove the `break` statements.
- Approach 2, O(1) per move: keep running scores. Use a row array, a column array, one diagonal counter, and one reverse-diagonal counter. Add the player value (+1 or -1) on each move. Update the diagonal counters only if the cell lies on them. After the update, check whether the absolute value of any affected counter equals N. If yes, the mover wins. Only a full line of one player reaches magnitude N.
- Undo: remove the last move and set the square to empty. For games where reversal is hard, replay all moves from the start. The move list also supports a downloadable game record.

**Decisions and trade-offs:**
- Chose the board as the first class over small classes because the whole system interacts with it. Small classes first lead to over-detail.
- Chose an integer per cell over a `Square` object because tic-tac-toe is simple. Chess would need a square object (piece, attack zone).
- Chose +1/-1 encoding over symbols because magnitude N detects a win with one comparison.
- Chose the player input 0 or 1 and the result -1, 0, +1 over a 0/1 result because a 0/1 result cannot signal "no winner yet".
- Chose a single merged loop over four separate loops. It repeats less code, at a small efficiency cost.
- Chose a list of moves in `Game` over board-only state because it supports undo, replay, and export.

**Interviewer feedback:** The video is a monologue, not a scored mock interview. It states what interviewers value.
- Rewarded: clarifying questions on features and listing features before choosing a subset (time is short). Code quality and clarity. Defined function contracts as a precursor to API design. Extensible class diagram. Using the key observation that only the mover can win. Talking to the interviewer while coding.
- Penalised: unclear names such as `cc` or `dd`. Chasing a fast algorithm at the cost of clarity. Detailing small classes while ignoring the main one.

## Zomato Order Status and Delivery Assignment (file 113)

**Core requirements:**
1. Get the status of an order by order id. Callers: customer, system, delivery executive. Statuses: accepted, being cooked, picked up, completed.
2. Assign a delivery executive to an order by order id.
3. Prefer an executive who is not busy. Prefer a short time to reach the restaurant.
4. If no executive accepts, fail the request.

**Out of scope:** Ratings and support calls. Computing travel time (an API returns time from locations). Optimization that batches orders or sends an executive early. Testing.

**Objects:**
- `Order` - key order details. Has a pointer to the status log. Linked to user, restaurant, payment, and delivery executive.
- `Restaurant` - fulfils the order. Has a location.
- `DeliveryExecutive` - an employee. Has a location and a busy state.
- `User` - the customer who placed the order.
- `Payment` - linked to the order.
- Delivery process log - a list of entries (timestamp, message). Records every state change.
- `Observer` (interface) - `updateOrderStatus`. Implementations: SMS service, notifier service. A payment service can join later (for example, only on cancel).
- Subject (order status) - `addObserver`, `removeObserver`, `notifyObservers`.

**API:**
```ts
getStatus(orderId) -> OrderStatus
assignDeliveryExecutive(orderId)
Observer.updateOrderStatus(orderId, status)
```
Assume a library call: given a restaurant id, return the top 10 nearby executives sorted by time to reach.

**Hard part:** Assignment flow and notification fan-out.

- Assignment: get the location of the restaurant by id. Call the library for the sorted top 10 executives. Offer the order to one executive at a time. Wait up to about two minutes for acceptance. If declined or timed out, offer to the next. When one accepts, save the assignment on the order in the database. If none accepts, fail the request.
- Sequential offers keep the system simple and avoid races where several executives accept.
- Status change: write an entry to the log. Call `notifyObservers`. Each observer takes its own action.
- Parallel orders: send notifications for many orders at once. Reuse the notification resource through a pool.
- Assignment can run in the background while the restaurant cooks. The key path is payment and recording the order.

**Decisions and trade-offs:**
- Chose assigning one executive at a time over broadcasting to all nearby executives. Reason: executives are employees. Uber-style broadcast fits third parties that may decline.
- Chose to start assignment after order creation and not block the order. Reason: assignment is less time-critical than payment and order recording. This allows a streaming or event design.
- Chose a separate status log with a pointer from the order over putting all history in the order.
- Chose the Observer pattern over direct calls. A new listener implements the and registers. No other code changes.
- Chose a sequential assignment loop over parallel offers for simplicity. Concurrency issues stay out of scope.
- Interviewer's preferred answer for contention: an object pool (like a connection pool) over semaphores. Creating objects is expensive, so reuse a limited set.

**Interviewer feedback:**
- Rewarded: product decisions (assign instead of broadcast; assign without rushing, so the system has time to optimize). Use of the Observer pattern, which simplified the design. Keeping the design extensible. Treating the log as a list with timestamp and message.
- Penalised: the code was not fleshed out (time was short; testing was not expected in 45 minutes). The candidate thought of semaphores and concurrency. The interviewer wanted the resource pool pattern.
- Overall rating: "strong hire", or between hire and strong hire.

## Service Booking like Urban Company, mock interview (file 114)

**Core requirements:**
1. Create a service. Only internal staff use this API.
2. Create an order for a service. An order has an order id and a user id.
3. Get my previous services: all past orders of a user, before the current time.
4. Services belong to a hierarchy of groups (for example housework, carpentry, furniture, chairs). The user can browse by group or search by title and description.
5. A service can have add-ons and metadata (for example haircut style).

**Out of scope:** Child services, combo discounts at the service level (the interviewer prefers a coupon at payment), update and delete APIs, multiple companies per order, matching by location and availability (only mentioned).

**Objects:**
- `Service` - id, title, description, image url, price, expected minutes, list of groups, add-ons, metadata. Immutable.
- `Group` - id, title, description, image url, parent groups. Groups form a tree, up to N levels. Immutable.
- `AddOn` - proper object for a paid extra (for example curtain cleaning for 50 rupees).
- `Order` - order id, service id, user id, company id (null while requested), scheduled time, created time, status enum (requested, scheduled, ongoing, completed, cancelled), payment id.
- `Payment` - id, user id, amount, method enum, reason (service or subscription), status enum (succeeded, failed, refunded), optional discount.
- `ServiceManager` - microservice with create service and create group. Internal only.
- `OrderService` - separate microservice that stores orders.

**API:**
```ts
createService(title, description, groupIds, price, expectedMinutes, addOns, imageUrl, metadata) -> ServiceResponse
createGroup(title, description, imageUrl, parentGroupIds) -> GroupResponse
createOrder(serviceId, userId, companyId, scheduledAt, paymentId) -> OrderResponse
getMyPreviousOrders(userId) -> list<Order>
```

**Hard part:**
- Service hierarchy: each leaf `Service` stores all its parent groups. Each `Group` has a parent. The UI shows child groups on each click. This is a tree, not a graph.
- Group count is small (100 to 500) and fixed. Treat `Service` and `Group` as immutable objects in an object pool. Load them from the database, which is the source of truth.
- A client sends only the service id, user, time and company. The server maps the id to the service. A client cannot send a wrong title.
- Write path for create service: write to the database first, then to the cache. The cache then holds all services. Other services read the cache, not the database.
- Read path for previous orders: index orders on user id, optionally on status. Select by user id and time before now. Show failed orders too.
- A title change needs a cache refresh or a service restart. This is the weak point of the design.

**Decisions and trade-offs:**
- Chose a group tree with parents stored on each service over one flat type field because the UI browses level by level and the depth can grow.
- Chose a separate `Group` entity over a string category because groups carry a description and an image.
- Chose immutable pooled objects over per-request objects because services never change at runtime.
- Chose database write then cache write over async write because the cache must never hold a service the database lacks.
- Chose a separate order microservice over one service because order volume and read patterns differ from the service catalog.
- Chose to keep metadata over removing it because a barber needs the chosen haircut style. The candidate admitted it is a generic tag.
- Chose a nullable company id over a separate requested-order type because the status enum already marks the stage.

**Interviewer feedback:**
- Rewarded: structured class fields including payment. Rewarded: grouping services, which helps both backend and UI search. Rewarded: caching and immutable object pool. Rewarded: asking questions and clarifying scope.
- Penalised: weak structure between classes. The interviewer expected a class hierarchy (base service, cleaning, salon, power) with shared fields.
- Penalised: a Factory pattern for service creation was expected and not used. Strategy (behavior per city, such as Chennai carpentry only) and Decorator (add-ons) were also valid answers. The candidate said no shared creation logic was visible.
- Penalised: service titles and descriptions as plain strings. The interviewer wanted class objects with an id that maps to a title, so that type-wide actions (discounts, city rules) work and a title change does not touch many places. An enum is too rigid.
- The candidate drifted into payment, which the interviewer did not ask for.
- Real LLD interviews last 1.5 to 2 hours and include code and tests.

## IRCTC Train Booking, mock interview (file 115)

**Core requirements:**
1. Search trains between a source and a destination for a date or time range.
2. View the schedule and route of one train for a date or date range.
3. Book one or more seats for a source-to-destination journey, with no decimal booking under parallel requests.
4. Give an atomic result: if a booking fails or is cancelled mid-flow, charge nothing.
5. Cancel a booking.
6. Booking window: three months ahead.

**Out of scope:** Notifications and ticket download; seat choice on a map (seats are assigned randomly); seat change mid-journey; multiple bookings to cover one route; Tatkal; coaches and pricing; hotels, catering, passenger and luggage trains.

**Objects:**
- `TrainService` - owns train data; back-end users add trains and routes.
- `Train` - train id, seat count, seat names. Seat layout is fixed.
- `Schedule` - one row per hop: train id, source, destination, estimated departure, estimated arrival, optional actual times for audit.
- `Route` - (train id, stop, date); lists the stops a train serves on a date.
- `SeatInventory` - (train id, date, segment, seats left); one counter per hop.
- `Ticket` - train, user, source, destination, seat number (set later).

**API:**
- `searchTrains(source, destination, startTime, endTime) -> list<Train>`
- `getSchedule(trainId, fromTimestamp, toTimestamp) -> list<Schedule>`
- `bookSeats(trainId, userId, source, destination, count) -> Ticket`
- `cancelTicket(ticketId)`

**Hard part:**
- Scale. Estimate: 13,000 trains per day, about 50 stops each, so about 650,000 rows. A row is about 150 bytes, so about 100 MB. Use an in-memory database backed by SQL.
- Search. Store each hop as a row. Index estimated departure. Do a binary search on departure after the start time. Filter on arrival before the end time, source, and destination. SQL uses one index per query, so the other columns are filters. To check that a train serves A and D, read its `Route` rows. A train serves the pair if both stops exist in order. A BFS or graph over hops was considered and judged slow. A graph database was suggested by an audience member and left open.
- Schedule query. Select by the departure index for the range, then filter by train id. This handles multi-day trains.
- Booking. Keep one seat counter per hop. A booking from A to C locks and decrements the hops A-B and B-C. Do not lock the destination row, because the seat frees at C. Start with all counters at the seat count. A hop counter at zero rejects the booking.
- Pessimistic lock. Take an exclusive row lock on the hops, check counters, decrement, release. A second booking on overlapping rows waits.
- Optimistic lock. Read the version of the counters, try to decrement, and fail if the version changed.
- Cancel. Increment the same hop counters under an exclusive lock.
- Seat numbers. Assign them at random about two days before departure.

**Decisions and trade-offs:**
- Chose SQL over NoSQL because the data is small, writes are rare, queries are range queries, and SQL indexes are cheaper and easy to explain.
- Chose pessimistic locking over optimistic because it is easier to reason about. Optimistic fits very high contention but wastes work on retries. The candidate was unsure about Tatkal load.
- Chose a free cancel window of seven days over free cancel at any time. In the last 12 hours, send the seat number, give no refund, and mark the ticket cancelled without restoring counters.
- Chose a `Route` table over building a graph per request because it removes in-memory graph work.
- Chose to skip seat-level assignment at booking time. Known flaw (raised in the interview): a per-hop counter can show free seats while no single seat is free for the whole trip. The design works only if seat change is allowed or seat identity is tracked.
- Chose to lock fewer rows (exclude the destination hop) over locking every row in the range because it removes needless contention.

**Interviewer feedback:**
- Rewarded: close estimates; covering search, booking, and cancel; early focus on concurrency; leeway that let the design form.
- Penalised: no scope statement (IRCTC is more than train booking); estimates came late, after the data part; the candidate did not ask the interviewer for real numbers; no mention of Tatkal or coaches and prices; too much detail early; the candidate explained his own solution and did not involve the interviewer. The interviewer called it poor communication.
