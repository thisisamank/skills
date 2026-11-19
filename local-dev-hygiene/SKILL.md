---
name: local-dev-hygiene
description: Keep local Workers dev servers healthy - orphan ports, local D1 traps, the user's running server, and device installs. Use when a dev server fails to start, a port is in use, or before running local D1 commands.
---

# Local dev hygiene

## Ports
- "Address already in use" means an orphan from an earlier run, often a vite child. Kill it by PID: `lsof -ti :PORT | xargs kill`.
- A dev script that starts child servers must stop them on exit. Fix the script (`trap`, process-group kill) so the error does not return.

## Local D1
- Do not run `wrangler d1 execute --local` while the dev server runs. It can kill the Worker. Use the local explorer API (`/cdn-cgi/local/explorer/api/d1/database/<id>/raw`) or stop dev first.
- "no such table" in dev means local migrations did not run. Apply them with the repo's `--persist-to` path.

- A dev server that needs secrets runs as `noenv exec -- npm run dev`. Agent shells do not load them on `cd`.

## The user's dev server
- If the user's dev server already runs, make your change visible in it. Restart only what is needed. Do not start a second one.

## Devices
- If a phone is connected, a request to run on the device means a release build installed with adb or Flutter.
