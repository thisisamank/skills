---
name: mcp-marketplace-launch
description: Build an MCP server for a product and list it on the Claude and ChatGPT directories and other MCP registries. Use when the user wants an MCP server, OAuth for MCP clients, a reviewer account, or a marketplace listing.
disable-model-invocation: true
---

# MCP and marketplace launch

## Build
1. Plan first: which data and tools to expose, auth, hosting on Workers. Write SPEC requirements (`MCP-*`).
2. Serve `https://<domain>/mcp`. Add an OAuth provider so Claude and ChatGPT can connect. Respect the product's access rules (private by default).
3. Tool names, descriptions and parameter docs decide when ChatGPT picks a tool. Write them carefully.
4. A tool that creates something puts it in a new place (for example a new page) unless the caller gives one.

## Reviewer account
- Create `review@<domain>` on the top plan. Generate a password, save it in noenv, and set it on the Worker (see `noenv-secrets-to-workers`).
- Fill the account with sample data. Send its emails to `support@<domain>`.

## Pages the listings need
- Terms of service, privacy policy, and a "how to connect" help page for each platform.
- Test cases and a demo video shot list.

## Listings
- Claude directory, ChatGPT apps (business verification and a domain token), the MCP Registry (`server.json` with a `.well-known` proof), Smithery, Glama, mcp.so.
- Follow [chapter 8 of `saas-seo-playbook`](../saas-seo-playbook/docs/08-ai-app-directories.md). Add what you learn back to it.

## Hand back
- List only the steps that need the user. Number them. Say exactly where to click and what to type, in plain words.
