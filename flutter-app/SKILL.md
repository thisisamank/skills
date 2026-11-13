---
name: flutter-app
description: Build and evolve a Flutter mobile app with a layered package structure, Riverpod state, a generated API client, a design-system package, an HTML-first design loop, and device testing. Use when creating, restructuring, designing or testing a Flutter app, or when adding a screen or feature to one.
---

# Flutter app

## 1. Structure
Use a Dart pub workspace: one root `pubspec.yaml`, one lockfile, one `dart pub get`. Every package sets `resolution: workspace`.

```
app/lib/     app/ screens/<flow>/ widgets/ models/ notifier/ di/ repositories/ utils/
packages/    api/            generated API client and a thin wrapper
             core/           shared non-UI code: results, errors, formatters, logging
             design_system/  tokens/ theme/ responsive/ components/
```
- Add a package only when two or more parts of the workspace use the code.
- Dependencies flow one way: `app → packages`. A package never imports `app/`. `design_system` imports no other package.
- Group screens by flow, not in one flat folder.
- Pin the Flutter SDK version (for example with fvm). Write the version in AGENTS.md.

## 2. Architecture
- **Dependency injection:** one container (for example `get_it`). Register services in `di/` and await setup in `main()` before `runApp`. Create infrastructure only in `di/`.
- **State:** Riverpod with code generation. Use `ref` for state, not to find services.
  - Async state is `AsyncValue`. Mutations go through `AsyncValue.guard`. Do not hide errors in a bare `try/catch`.
  - Notifiers hold state and orchestration. They do not build widgets, format display text, or call the network directly.
  - Use `setState` only for small local UI state. Never copy provider state into a `State` field.
- **No implicit state machines.** Do not model state with several booleans, nullable fields or status strings that combine into hidden states (for example `isLoading`, `hasError`, `data == null`). Model each state as a `freezed` union or a sealed class with named states. Put every transition in the notifier. Handle every state in the UI with an exhaustive `switch`.
  - When you review a screen or notifier, list its states and transitions first. Fix any flag combination that can produce an impossible state.
- **Models:** immutable, generated with `freezed`. Use unions only for real unions.
- **Navigation:** one router (for example `go_router`).
- **Repositories** turn transport objects into domain models and decide what to cache. Notifiers get domain models only.

## 3. API contract
- The backend schema is the only source of truth. Export it as an OpenAPI file.
- Generate the Dart client from that file into `packages/api`. Commit the generated code. Never edit it by hand.
- Run every generation step in order (client generator, `build_runner`, formatter) and write the steps in AGENTS.md.
- Generated types stay inside `packages/api`.
- A route change regenerates the OpenAPI file and the client in the same commit. Delete orphaned models.
- If the formatter changes files that your change did not touch, revert them.
- Build a screen only against an endpoint that exists and passes its tests.
- Refresh tokens in one place, inside the API client.
- If a third-party identity provider gives a token, exchange it once for the app's own session, then discard it.

## 4. Local data
- Secure storage for session tokens only. A local database only for data the app must keep offline. Simple key-value storage for UI flags.
- Cache sensitive personal data on the device only when the product needs it.
- Logout and account deletion clear all local storage and sign out of every identity provider.

## 5. Design system
- All colours, type, spacing, radii and motion come from `design_system` tokens. No hardcoded values in `app/`.
- Shared components carry a short app prefix.
- Use one icon pack across the app. Show the user a few options before you choose.
- Keep illustrations as one consistent set.
- Keep the widget tree stable around text fields. If a decoration appears only on focus, the field rebuilds and loses input. Always pass the decoration and change only its values.

## 6. Design loop: HTML first, then Flutter
1. Prototype the screen or flow in one local HTML file. Start from the user's reference images when they give some.
2. Show several versions on one page, labelled A, B, C. The user picks one for each screen.
3. Iterate until the user approves. Keep every state of a flow in the design file, in the order a user meets it.
4. Build it in Flutter pixel to pixel, with every behaviour and animation. Plan for performance with large data sets.
5. When the code and the design file disagree, check which one is current. Update the other.

## 7. Mobile UX
- Give each screen one main job. More screens are better than one crowded screen.
- Give each screen one primary action. Secondary actions look secondary.
- A button that has no next action after a tap becomes plain text.
- The top bar colour fills the status bar area.
- Haptics confirm an action with a single tick. Do not use them as a reward.
- Keep the app text simple.
- Keep an existing design that the user says is correct.

## 8. Testing
Use three layers. Each layer does one job.

| Layer | Tool | Job |
|---|---|---|
| Smoke | Maestro | 5 to 10 critical user journeys on a real build |
| Depth | Patrol or `integration_test` | Edge cases, error states and native dialogs, with the backend faked |
| Design | Golden or screenshot tests | Match each screen to the approved design |

### Every change set
- Run `flutter analyze`, the formatter on changed files, and `flutter test`. Keep the existing tests green.

### When to write tests
- While a flow's design still changes, keep new tests few.
- When a flow is stable, add its Maestro flow, its depth tests and its goldens.

### Smoke layer: Maestro
- Cover only critical journeys: sign-in, onboarding, the core action, payment if any, logout and account deletion.
- Give every interactive widget a stable `Semantics` identifier. Maestro reads the accessibility tree, and Flutter widgets without semantics are invisible to it.
- Select elements by identifier, not by visible text, so copy changes do not break flows.
- Wait for elements, not for fixed times.
- Run against a non-production environment with a seeded test account. Reset its data before each run.
- Do not let a flow complete actions that notify or affect real users.

### Depth layer: Patrol or `integration_test`
- Find widgets by `Key`.
- Fake the backend through provider overrides. Cover every state of each union (loading, empty, error, success).
- Use Patrol for native parts: permission dialogs, notifications, camera, contacts, location.

### Design layer: goldens
- Add a golden for each approved screen and each important state.
- Update goldens only when the design changes on purpose.

### Devices
- Use the emulator or simulator only when the user asks:
  - Android emulator: install with `adb`, drive with `adb shell input tap`, and read screenshots from `adb exec-out screencap -p`. Take a new screenshot before each tap.
  - iOS simulator: run it on each device size the user names.
- During a manual device pass, compare each screen with the approved design. Move on at about 95% match. Fix what the pass finds in one commit.

## 9. Observability and release
- Put crash reporting and product analytics behind one wrapper. Remove an old SDK completely when you replace it.
- When the app icon changes, update it on Android and iOS.
- Follow the repo's branch rules. Do not promote to release branches unless the user asks.

## 10. Questions
- When information is missing, ask multiple-choice questions in small rounds, with the trade-off in each option.
