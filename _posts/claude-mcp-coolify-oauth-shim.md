---
title: "Prompt-Driven Deployments: Bridging Claude MCP with Coolify via an OAuth Shim"
slug: claude-mcp-coolify-oauth-shim
date: 2026-10-07
order: 2
category: DevOps / MCP
summary: "How I connected Claude MCP to self-hosted Coolify with a small Node/Express OAuth shim — Supabase sessions, rate limiting and consent."
description: Coolify's API uses a static bearer token; Claude's remote MCP connectors expect OAuth. Here's the small Node/Express shim I built to connect them — with Supabase-backed sessions, rate limiting, and a consent step.
---

At [SLTech](https://sltech.io/) we run client projects on a self-hosted **Coolify** instance. I wanted deployments to be something you could just ask for — "redeploy the staging app", "show me the last build logs" — from Claude, instead of clicking through a dashboard.

The Model Context Protocol (MCP) makes that possible: an MCP server exposes Coolify's operations as tools Claude can call. The catch was authentication.

## The mismatch

- **Coolify's API** authenticates with a **static bearer token**. One long-lived secret, full API access.
- **Claude's remote MCP connectors** expect the server to speak **OAuth** — the user is sent through an authorization flow, and Claude receives tokens it can refresh.

Handing the Coolify token to every client wasn't an option: there's no consent, no per-session revocation, and a leaked token means full access to the infrastructure. So I built a shim in the middle.

## The shim's job

A small **Node/Express** service that:

1. **Speaks OAuth to Claude** — the authorization and token endpoints Claude's connector expects.
2. **Shows a consent step** before issuing anything, so access is an explicit decision rather than a side effect of knowing a URL.
3. **Proxies MCP requests to Coolify**, attaching the static bearer token **server-side only**. The real token never leaves the shim.
4. **Stores sessions in Supabase**, so they survive redeploys.
5. **Rate-limits** requests per session.

```text
Claude ──OAuth──▶  Shim (Node/Express)  ──Bearer token──▶  Coolify API
                     │
                     └── sessions & tokens in Supabase
```

## Why Supabase for sessions

Keeping sessions in memory works right up until the shim itself is redeployed — which, on a tool whose whole purpose is deployments, happens a lot. Every redeploy would log everyone out and force them back through the OAuth flow.

Storing sessions and tokens in Supabase (Postgres) avoids that: the process is stateless, and a redeploy is invisible to connected clients. It also gives one place to look up and revoke a session.

```js
// Simplified: look up a session by its access token
const { data: session } = await supabase
  .from('mcp_sessions')
  .select('id, expires_at, revoked')
  .eq('access_token_hash', hash(accessToken))
  .single();

if (!session || session.revoked || isExpired(session)) {
  return res.status(401).json({ error: 'invalid_token' });
}
```

Storing tokens hashed means a database read alone doesn't hand anyone a usable credential.

## Guardrails

- **Consent flow protection.** The consent step is where a malicious link could try to trick someone into approving access, so it's protected against being completed by anything other than the user's own deliberate action.
- **Rate limiting.** An agent in a loop can fire a lot of requests. Per-session limits keep one runaway conversation from hammering the Coolify API.
- **Least exposure.** The Coolify token lives only in the shim's environment. Clients only ever hold shim-issued tokens that can be revoked individually.

## The payoff: deployments by prompt

With the shim and a custom MCP server in place, deployments across our client projects became **fully prompt-driven**. Redeploys, status checks, and log reads happen from a conversation, and the manual click-through steps are gone.

## Takeaways

1. **When two systems disagree on auth, put a small, boring service between them** rather than weakening either side.
2. **Never forward a master token to clients.** Issue your own revocable tokens and keep the real one server-side.
3. **Persist sessions outside the process** — especially for a service you'll redeploy often.
4. **Rate-limit anything an agent can call.**

Questions about MCP or Coolify setups? [Get in touch](/#contact).
