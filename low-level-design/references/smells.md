# Smells and fixes

Use this list when you review code or before you finish a change. Each row is a smell from the course and the fix the course used. The numbers are lesson files in `interviewready-lld-transcripts`.

## Structure

| Smell | Fix | Source |
|---|---|---|
| One method of 90 lines that does many things | Split by responsibility. Extract the duplicated parts. | 002, 015 |
| All classes in one file | One class per file. Group files in folders by concern. | 005 |
| `main` or a controller holds the logic | Name a class for its role, such as `GameEngine`. The controller only calls the service. | 005, 106 |
| One engine creates, moves, checks state and suggests moves | Split into a game engine, a rule engine and an AI engine. | 009, 011 |
| Public mutable fields, such as `board.cells` | Private fields. Methods that validate every write. | 005, 014 |
| Code outside gets a child object and mutates it | The parent exposes `setX(...)` and validates. | 101 |
| Getter chains, such as `command.getDetails().getReceiver()` | Add `getReceiver()` on the outer object. | 042 |
| Nested map, such as `Map<User, Map<User, Amount>>` | Wrap it in a class, such as `BalanceMap`. | 050 |
| Three maps keyed by the same ID | One map of objects: `Map<TopicId, Topic>`. | 109 |
| Raw `Map` or `List` field that the code adds to and removes from | A dedicated class, such as `Watchlist`. | 106 |
| Deeply nested generic, such as `Map<Class, List<Rule<Board>>>` | A named class, such as `RuleSet`. | 024 |
| A class name that does not match its content | Rename it. `Balance` became `Amount`. | 050 |
| Catalog entity and booking entity in one class | Split them, for example `Service` and `Order`. | 114 |

## State and data

| Smell | Fix | Source |
|---|---|---|
| A boolean you can compute, such as `hasMoved` | Derive it from existing data. | 101 |
| Fields copied from one object into another | Derive them from the single source of truth. | 038 |
| Strings used as identity, such as a service title | IDs or typed objects. | 114 |
| Raw string IDs that the code can mix up | Wrapper types, such as `TopicId`. | 080 |
| Hard-coded `"X"` and `"O"` in logic | An enum. | 014 |
| Magic numbers, such as `2` or `(1,1)` | Named constants. | 025 |
| Cryptic names, such as `sRow`, `cc`, `dd` | Names that state intent. | 014, 112 |
| Whole objects stored in a cache | Store IDs. | 050 |
| Every instance of a repeating series stored | Store the rule. Expand it on read for the range. | 105 |
| A list of members in one DB column | A join table, one row for each member. | 105, 111 |
| Search inside a serialised JSON blob | Copy the queried fields into indexed columns. | 110 |
| An exploration function mutates live state | Work on a copy. | 013 |
| A shallow copy shares mutable references | Deep-copy the mutable parts. | 014 |

## Hierarchy

| Smell | Fix | Source |
|---|---|---|
| A base method added "in case" a subtype needs it | Put it on the concrete type. Split the interface. | 028 |
| A subclass cannot implement an inherited method | Split the interface: `Board` and `CellBoard`. | 024, 029 |
| A cast to make a hierarchy work | Composition or generics. | 041 |
| Subclasses with no clear difference, such as `TimedGame` | Composition with a config object. | 022 |
| Inheritance with no shared behaviour | An interface. | 106 |
| A wrapper class added for each new need | Extract the logic. Pass the right input in. | 018, 021 |
| `addCommentOnTweet` and `addCommentOnComment` | A shared type, such as `Commentable`. | 108 |

## Functions

| Smell | Fix | Source |
|---|---|---|
| A parameter the function does not use | Remove it. | 025 |
| A return value the caller already has | Return only the new information. | 025 |
| Two overloads that differ only in argument type | One function. Pass the value in. | 024 |
| Parameters already carried by another argument | Remove the duplicates. | 110 |
| A bare boolean when the caller needs the reason | A result object. | 110 |
| A public signature changed to fit internals | Private helpers. Keep the public signature. | 065 |
| A generic error type, such as `throws Exception` or `Error("failed")` | Specific error types. | 096 |
| Blocking on a future in a constructor | Pass the resolved value in. | 096 |
| A constructor with six parameters | A factory or a builder. | 035 |
| Constructors that double with each optional field | A builder. | 020 |
| A builder with one input and one output | A constructor. | 042 |
| Business decisions inside the service that performs the action | Move them to the caller, the builder or the factory. | 040 |
| A system clock read inside logic | Inject the clock. | 036, 076, 102 |

## Control flow

| Smell | Fix | Source |
|---|---|---|
| Loops nested three or more levels | Extract functions. Use iteration helpers. | 018, 032 |
| Four copy-pasted loops | One loop with named flags. | 112 |
| Conditions checked and acted on separately | Check them together. Decide once. | 023, 038 |
| A winner set twice, or a move made twice | One decision point. A guard for terminal states. | 037, 038 |
| An `if` for each rule inside one function | A rule list. | 019 |
| An unordered rule set where order matters | A chain or sequential code. | 023 |
| A cache that branches on the policy name | The policy in a comparator or a strategy. | 066 |
| Hard-coded calls from a publisher to each subscriber | A subscriber list behind an interface. | 106 |
| A timer that checks every item when the write path already knows | A hook in the write path. | 108 |
| `if` or `else` per coupon | Rule objects. Admin rules for the common shapes. | 110 |

## Performance and concurrency

| Smell | Fix | Source |
|---|---|---|
| A linear scan by ID | A map by ID. | 078, 102 |
| A hash map used for ordered extraction | A sorted map or a heap. | 102 |
| A linear scan of a sorted list | Binary search. | 108 |
| A comparator on the wrong key | Sort by the key the query needs. | 102 |
| A tree rebuilt with N joins | Find the real access pattern first. | 111 |
| A concurrent map treated as the whole fix | One lock or one owner for the composite. | 103 |
| Everything locked | Lock only the paths that read and mutate together. | 103 |
| A wait with no timeout | Add a timeout. | 103 |
| One thread per user or per key | A fixed pool, chosen by hash. | 074 |
| A request thread blocked on I/O | A separate pool for each concern. | 062, 093 |
| Readers see a half-updated aggregate | An immutable snapshot and a reference swap. | 047 |
| A stack trace printed when retries run out | A dead-letter queue. | 080 |
| Delivery state held in the consumer | The queue holds the offset. | 109 |
| All connections dropped to shed load | Evict the least recently used connection, or scale out. | 107 |
| A failed payment retried on its own | Tell the user. Let them submit again. | 106 |

## Tests

| Smell | Fix | Source |
|---|---|---|
| Tests depend on AI or random output | Hardcode the inputs. | 011, 014 |
| A test named after a class | Name it after the behaviour. | 010 |
| One test covers the factory and the logic | Test each unit separately. | 038 |
| The test changed to fit the code | Fix the code. | 014 |
| A real clock in tests | Pass timestamps in. | 036 |
| A concurrency test that breaks the client contract | Make the harness obey the contract. | 103 |
