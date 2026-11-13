---
name: noenv-secrets-to-workers
description: Move secrets between noenv, the shell and Cloudflare Workers without printing them. Use when setting, rotating, moving or removing a Worker secret or API key.
---

# Secrets: noenv to Workers

The noenv shell hook loads secrets when you `cd` into the repo. Use those variables. Do not read or print a value.

## Put a secret on a Worker
```sh
printf '%s' "$API_KEY" | npx wrangler secret put API_KEY
printf '%s' "$API_KEY" | npx wrangler secret put API_KEY -c ../other-worker/wrangler.jsonc
```
- If the key lives in another repo's noenv project, `cd` into that repo in the same command and pipe from there.

## New secret
1. Generate it (for example `openssl rand -base64 24`) into a variable.
2. Save it: `printf '%s' "$V" | noenv secret set NAME`.
3. Pipe the same variable to `wrangler secret put`.

## Rotate or switch provider
- Delete the old secret from production with `wrangler secret delete`.
- Keep the old value in local noenv unless the user asks to delete it.

## When a key fails
- Reload the shell (`cd` out and back in) before you blame the key.
- Test the key with one small API call. Report the status code, never the key.

## Do not
- Do not create `.env`, `.env.*` or `.dev.vars`.
- Do not share one product's webhook key with another product. Create a new webhook endpoint and ask the user for its key.
