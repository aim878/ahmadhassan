---
title: Building a Production RAG Chatbot with OpenAI, Chroma, and Claude
slug: production-rag-chatbot
date: 2026-10-07
order: 1
category: AI / RAG Systems
summary: "How I built REConnect's production RAG chatbot with OpenAI embeddings, Chroma Cloud and Claude — chunking, agentic tools, and guardrails."
description: How I built a knowledge-base chatbot for REConnect — from chunking source docs and retrieval with Chroma Cloud to agentic tools, rolling summaries, and thumbs-down retry logic.
---

Most chatbot demos stop at "embed some documents, retrieve a few chunks, ask the model." That gets you a demo. Getting to something you can put on a real product's website — where users ask about pricing, coverage, and their own account — takes a lot more.

This post walks through the chatbot I built for **[REConnect](https://reconnectapp.com/)**, a real estate data platform, at [SLTech](https://sltech.io/). It started as a straightforward retrieval-augmented generation (RAG) widget and grew into an agent that can look things up, adapt its tone, and guide people through sign-up.

## The stack

| Layer | Choice |
|---|---|
| Embeddings | OpenAI embeddings |
| Vector store | Chroma Cloud |
| Answer model | Claude Haiku 4.5 |
| Backend | Node.js |
| Frontend | Site chat widget |

I picked a small, fast model for answering on purpose. In a support widget, latency is part of the experience — and when retrieval does its job, the model mostly needs to read and summarise well, not reason for a long time.

## Step 1: Chunk the source documents

The knowledge base is the product's own content: **pricing, MLS coverage, and FAQs**. Each type of document has a natural shape, and chunking along that shape matters more than any clever splitting algorithm:

- **FAQs** — one question and its answer per chunk. Never split an answer from its question.
- **Pricing** — one plan per chunk, with the plan name repeated in the chunk text so it still makes sense on its own.
- **MLS coverage** — grouped by region/provider so a question like "do you cover X?" lands on a chunk that actually names X.

Every chunk carries metadata (source, section, last updated) so I can filter, debug, and re-index one source without touching the rest.

```js
// Simplified: index one document's chunks into Chroma
const embeddings = await openai.embeddings.create({
  model: EMBEDDING_MODEL,
  input: chunks.map(c => c.text),
});

await collection.upsert({
  ids: chunks.map(c => c.id),
  documents: chunks.map(c => c.text),
  embeddings: embeddings.data.map(e => e.embedding),
  metadatas: chunks.map(c => ({ source: c.source, section: c.section })),
});
```

## Step 2: Retrieve, then let the model answer

For each user message, the backend embeds the query, pulls the **10 most relevant chunks** from Chroma, and passes them to Claude with a system prompt that keeps it grounded:

- answer only from the provided context and the user's data;
- say so plainly when the answer isn't there, and offer a next step (contact support, see pricing) instead of guessing.

Ten chunks is a deliberate trade-off. Too few and multi-part questions ("how much is the pro plan and does it cover my MLS?") miss half the answer. Too many and you pay for tokens the model has to wade through. Because the chunks are small and well-shaped, ten fits comfortably.

## Step 3: From answering to acting

A pure RAG bot can only quote documents. Users kept asking things the documents couldn't answer — "is my listing live?", "which plan am I on?" — so I gave the bot tools:

- **MLS provider lookups** — check coverage against live data rather than a static page.
- **Account, plan, and listing data** for logged-in users — the bot can answer about *their* account, scoped strictly to the authenticated user.
- **Guided sign-up flows** — the bot can walk someone through creating an account, with **explicit confirmation steps** before anything is submitted.

The confirmation step is the important part. A model deciding to take an action is fine; a model taking it without the user seeing exactly what will happen is not.

## Step 4: Make it feel right for each user

**Role-aware tone.** An agent, a broker, and a first-time visitor need different answers to the same question. The bot adjusts its tone and level of detail based on who's asking.

**Rolling conversation summaries.** Long chats are where costs and confusion creep in. Instead of resending the whole transcript, older turns are periodically folded into a running summary, and only recent turns are sent verbatim. The model keeps the thread of the conversation without the context growing forever.

## Step 5: Production guardrails

The unglamorous part is what makes it shippable:

- **Rate limiting** per user/session, so one client (or bot) can't run up the bill or degrade the widget for everyone else.
- **Thumbs-down retry.** When a user marks an answer as unhelpful, the bot retries with that feedback in context instead of just logging it. It's a cheap way to recover a conversation in the moment — and the logged thumbs-downs show exactly where the knowledge base has gaps.

## What I'd tell anyone building one

1. **Chunking is the product.** Most "the bot gave a wrong answer" bugs were retrieval bugs, and most retrieval bugs were chunking bugs.
2. **Small model, good context** beats big model, bad context — for latency and for cost.
3. **Tools need confirmations**, and user-data tools need strict scoping to the signed-in user.
4. **Feedback buttons should do something** in the moment, not just feed a dashboard.

If you're building something similar, I'm happy to compare notes — [get in touch](/#contact).
