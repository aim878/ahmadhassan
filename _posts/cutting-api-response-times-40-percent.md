---
title: Cutting API Response Times by 40% with Redis, Query Tuning, and Lazy Loading
slug: cutting-api-response-times-40-percent
date: 2026-10-07
order: 3
category: Performance
description: A practical breakdown of the caching strategies, query optimisation, and lazy loading I used at The Genius Group to reduce API response times by roughly 40% under production load.
---

At [The Genius Group](https://www.genius.co.uk/) I worked on products and marketing infrastructure that saw real, spiky traffic — campaign funnels, lead submission, live data. As usage grew, API latency crept up. Through a combination of **Redis caching, query tuning, and lazy loading**, we brought response times down by roughly **40%**.

None of these techniques is new. The value is in applying them in the right order and measuring as you go.

## 1. Measure first

Before changing anything, find out where the time actually goes. For each slow endpoint I looked at:

- **total response time** — at typical and peak load, not just the average;
- **time spent in the database** vs. in application code vs. waiting on third-party APIs;
- **how many queries** a single request triggers.

That last number is often the biggest surprise.

## 2. Fix the queries

Caching a slow query just hides it until the cache misses. So queries came first.

**Read the query plan.** `EXPLAIN ANALYZE` shows what the database is really doing:

```sql
EXPLAIN ANALYZE
SELECT id, status, created_at
FROM leads
WHERE campaign_id = $1
ORDER BY created_at DESC
LIMIT 50;
```

A sequential scan over a large table for a filter-and-sort like this is the classic sign of a missing index. A composite index matching the filter and sort order turns it into an index scan:

```sql
CREATE INDEX idx_leads_campaign_created
  ON leads (campaign_id, created_at DESC);
```

**Kill N+1 queries.** Loading a list, then querying related data once per row, scales linearly with the list. Fetching related rows in one query (a join, or a single `WHERE id = ANY($1)` lookup) collapses dozens of round trips into one.

**Select only what you use.** `SELECT *` on wide tables moves data nobody reads.

## 3. Cache what's read often and changes rarely

With queries in good shape, **Redis** took the remaining repeated work off the database. I used the cache-aside pattern:

```js
async function getCampaign(id) {
  const key = `campaign:${id}`;
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const campaign = await db.campaigns.findById(id);
  await redis.set(key, JSON.stringify(campaign), 'EX', 300);
  return campaign;
}
```

The rules that kept it correct:

- **Cache by access pattern, not by table.** Good candidates are read on almost every request and change rarely — configuration, campaign settings, reference data.
- **Always set a TTL.** Even with explicit invalidation, a TTL is the safety net against stale data living forever.
- **Invalidate on write.** When the source record changes, delete its key so the next read repopulates it.
- **Don't cache per-user, fast-changing data** unless you have a clear invalidation story.

## 4. Lazy-load the expensive parts

Some responses were slow because they did everything up front — computing or fetching data that most callers never used. Deferring that work helped on both sides:

- **API side:** return the core payload immediately; expose expensive, rarely-needed details through a separate endpoint or on request.
- **Frontend side:** load heavy components and below-the-fold data only when needed, so the page becomes usable sooner.

## 5. Make it stick

A one-off speed-up decays as features are added. To keep the gains:

- keep an eye on slow-query logs and endpoint latency after each release;
- treat a new N+1 or an unindexed filter as a bug in code review;
- keep the infrastructure efficient too — at TGG that included serving over **HTTP/2** with proper SSL configuration on our AWS servers.

## Summary

| Step | What it fixed |
|---|---|
| Measure | Found where time was really spent |
| Query tuning | Missing indexes, N+1 queries, over-fetching |
| Redis caching | Repeated reads of rarely-changing data |
| Lazy loading | Work done up front that most requests didn't need |

Together these brought response times down by about 40%. The order matters: **measure, fix queries, then cache, then defer.**

Working on a slow API? [Let's talk](/#contact).
