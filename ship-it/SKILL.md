---
name: ship-it
description: Commit, merge and deploy with micro commits, a single main branch and no AI attribution. Use when the user asks to commit, merge, deploy, ship, or bring production up to date.
disable-model-invocation: true
---

# Ship it

## Commit
1. Run the project checks first (typecheck, tests, or what AGENTS.md lists).
2. Make micro commits. Use Conventional Commits. One logical change per commit.
3. Put the requirement ID (for example `ENV-03`) in the message when the change implements one.
4. Do not add an AI sign-off or a `Co-Authored-By` trailer.
5. Commit on `main` unless the repo names another branch.
6. A request to commit everything includes changes that were already in the tree. Split them into separate micro commits.
7. Do not push unless the user asks.

## Merge
- Keep all work on `main`. A request to merge everything means all branches, also branches you did not create.
- Do not leave work on side branches at the end of a task.

## Deploy
1. Apply remote database migrations before the deploy that needs them.
2. Push new secrets to the Worker before the deploy with `noenv wrangler KEY…` (see `noenv-secrets-to-workers`). Run deploy commands that need secrets through `noenv exec --`.
3. Deploy every Worker that the change touches (API, web, admin). Name each one.
4. Check that production runs the current code. If a deploy looks rolled back, redeploy from the current tree.
5. Submit changed public pages to IndexNow if the repo supports it.
6. A deploy request is the approval. Do not ask again. "Commit and deploy" means commit first, then deploy.

## Report
- One short list: commits (short hashes), deployed Workers, and what is not done.
