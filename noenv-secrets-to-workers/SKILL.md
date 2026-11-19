---
name: noenv-secrets-to-workers
description: Load, save and move secrets with noenv - noenv exec for agent commands, noenv wrangler to push to Cloudflare Workers - without printing them. Use when a command needs secrets, or when setting, rotating, moving or removing a Worker secret or API key.
---

# Secrets: noenv to Workers

Needs noenv CLI 0.2.0 or newer (`npm install -g @thisisamank/noenv-cli`). Docs: https://noenv.thisisamank.in/guides. Do not read or print a secret value.

## Run commands that need secrets
Agent shells are fresh, so the `cd` hook does not run. Wrap each command:
```sh
noenv exec -- npm run dev
noenv exec -- npx wrangler deploy
```
- `noenv exec` picks the account and project from the current directory. It removes secrets from other repos and prints only the project name.
- Outside a noenv project, it runs the command without secrets.
- When the server is down, it uses the last encrypted copy and says so.

## Set up a repo
1. Run `noenv status`. It shows the account, the user and the project.
2. If the repo has no project, run `noenv init`. Commit the `.noenv` file it creates. It holds no values.
3. List the secrets the repo needs in `.noenv`. The shell then reports missing ones:
   ```toml
   version = 1
   [secrets]
   required = ["DATABASE_URL", "STRIPE_KEY"]
   ```
4. If the repo has `.env` files, run `noenv migrate`. It verifies every value before it deletes a file.
5. Add this line to the repo's AGENTS.md: "Run commands that need environment variables with `noenv exec -- <command>`. Do not create .env files."

## Push secrets to a Worker
```sh
noenv wrangler STRIPE_KEY API_KEY
```
- Name the keys. Without keys it opens an interactive list, which an agent cannot use.
- It sends the values to `wrangler secret bulk` on stdin. Nothing goes to screen or to a file.
- To push on every `secret set` and `secret rollback`, list the keys in `.noenv`:
  ```toml
  [wrangler]
  secrets = ["STRIPE_KEY", "API_KEY"]
  environment = "production"
  env = "staging"
  ```
  `environment` is the noenv environment to copy from. `env` goes to wrangler as `--env`. Both are optional.
- Dashboard changes do not push. Run `noenv wrangler` after them.
- For a Worker in another folder, pipe one key: `noenv exec -- sh -c 'printf "%s" "$API_KEY" | npx wrangler secret put API_KEY -c ../other-worker/wrangler.jsonc'`.

## New secret
1. Generate it into a variable (for example `V=$(openssl rand -base64 24)`).
2. Save it: `printf '%s' "$V" | noenv secret set NAME`.
3. Push it: `noenv wrangler NAME`, or let the `[wrangler]` list push it.

## Environments
- Select with `NOENV_ENVIRONMENT=staging`, or `environment = "staging"` in `.noenv`.
- `noenv migrate` and `noenv grant` use the current environment. Set it first.

## More than one team
- Each noenv deployment is one account. Add it once: `noenv account add acme https://noenv.acme.com github.com/acme`, then `noenv auth acme`.
- The CLI picks the account in this order: `NOENV_ACCOUNT`, the longest matching repo prefix, the default account, `NOENV_URL`.

## Rotate or switch provider
- Set the new value with `noenv secret set`. Old versions stay; `noenv secret history KEY` and `noenv secret rollback KEY VER` restore one.
- Delete the old secret from production with `wrangler secret delete`.
- After `noenv revoke`, rotate the important values. Revoke does not take back values a person already loaded.

## When a key fails
- Check `noenv status` and run the command again through `noenv exec`.
- Test the key with one small API call. Report the status code, never the key.

## Do not
- Do not create `.env`, `.env.*` or `.dev.vars`.
- Do not echo a value or pass it as a command argument.
- Do not share one product's webhook key with another product. Create a new webhook endpoint and ask the user for its key.
- If `noenv` is missing or no account is set up, stop and tell the user.
