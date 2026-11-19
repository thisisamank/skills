# Patterns and their triggers

Use a pattern only when its trigger is present. The column "Not when" lists the cases where the course rejected it.

| Pattern | Trigger | Not when |
|---|---|---|
| Strategy | One operation, several algorithms, chosen at runtime. Examples: AI difficulty, LRU or LFU, retry policy, buy or sell order. | There is only one algorithm. |
| Factory | Creation needs computation, defaults or many parameters. Callers and tests must not build the object. | A constructor with two arguments works. |
| Builder | Many optional fields. Constructors double with each new field. | One input and one output. Use a constructor. |
| Prototype (copy) | Code must change an independent copy and discard it. Examples: AI search, dry runs. | A shallow copy would leak shared mutable references. |
| Rule engine | Many independent conditions that change often. Each rule is `(context) => result`. The engine knows no rule. | The order of the rules matters. |
| Chain of responsibility | Steps run in a known order. The first step that matches wins. | The steps are independent. Use a rule list. |
| Observer / pub-sub | One event, many consumers that join and leave at runtime. The producer must not know them. | There is one fixed subscriber. |
| Command | An action as an object. Its parameters keep changing. The code that invokes, defines and runs it is separate. | A plain function call is stable. |
| State | A real state machine with sparse, clear transitions. | Any state can go to any other state. |
| Memento | History or undo is a requirement. | Memory is tight. Store moves and replay them. |
| Proxy (lazy) | The real object is expensive. Build it only on first use. Example: DB connections. | A constructor from the light form is simpler. |
| Flyweight | Many equal immutable objects. Share one instance for each value. | The objects are few, or the lookup costs as much as `new`. |
| Singleton | The object must exist once, and it is stateless or shared. | Never write it by hand. Use module scope or DI. |
| Object pool | Construction is expensive and the count is limited. Examples: connections, senders. | The objects are cheap. |
| Keyed executor | Per-key ordering with total parallelism. Use `hash(key) % N` single-thread queues. | There is no ordering requirement. |
| Request collapsing | Repeated concurrent misses for one key. | Misses are rare. |
| Immutable snapshot swap | Readers must never see a partial update of many fields. | There is a single atomic field. |
| Dead-letter queue | Retries ran out. Keep the item for later diagnosis. | The failure cannot recover. Reject it at once. |
| Push for most, pull for heavy | Fan-out is skewed. Push to normal readers on write. Celebrity writers are pulled on read. | Fan-out is uniform. |
| Blueprint plus expansion | A series repeats without end. Store the rule, expand it for the queried range. | The set is finite and small. |
| Content-addressed tree | History with small edits to large trees. Hash each node. A change rewrites the path to the root. | There is no history requirement. |
