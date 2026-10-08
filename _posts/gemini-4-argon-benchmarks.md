---
title: "Gemini 4 Argon's Benchmark Table, Read by Someone Who Ships AI Features"
slug: gemini-4-argon-benchmarks
date: 2026-10-08
category: AI / Models
summary: "Gemini 4 Argon tops 14 of 19 rows in Google's benchmark table. What the numbers say, what they don't, and how I'd pick a model for real work."
description: Google's launch table puts Gemini 4 Argon ahead of GPT-6 Astra, Claude Fable 5.1 and Claude Opus 5.5 on most benchmarks. Here's how I read it as someone who builds production AI features, and why the rows where it loses are the interesting ones.
---

Every model launch comes with a table like this one, and every table like this one is built to make a point. Google DeepMind's table for Gemini 4 Argon makes its point clearly: a column of blue cells, top to bottom.

I don't train models. I build things on top of them: chatbots, agents, internal tools that real users touch. So when I read a benchmark table, I'm not asking "which model is smartest?" I'm asking "which model should I put behind this feature, and what will break?"

Here's the full table, as Google published it:

| Area | Benchmark | Gemini 4 Argon | GPT-6 Astra | Claude Fable 5.1 | Claude Opus 5.5 |
|---|---|---|---|---|---|
| Knowledge work | Vals Index | **68.9%** | 63.1% | 65.8% | 67.0% |
| | AutomationBench (score) | **51.3%** | 41.4% | 31.4% | 42.5% |
| | Vals Finance Agent v2 | **65.4%** | 53.5% | 58.9% | 58.6% |
| | Harvey's Legal Agent Benchmark | **19.6%** | 5.4% | 6.7% | 3.8% |
| Agentic coding | DeepSWE v1.1 | **77.9%** | 74.1% | 67.4% | 74.2% |
| | FrontierSWE v2 | 55.0% | **65.5%** | 56.3% | 62.3% |
| | Vibe Code Bench | **91.9%** | 89.6% | 90.3% | 90.3% |
| | Terminal-bench 4.0 | 57.4% | 58.2% | 57.9% | **66.4%** |
| ML engineering | PostTrainBench | 45.3% | 44.3% | 40.2% | **49.3%** |
| Science and math | Terminal-Bench Science 0.1 | 57.6% | **68.1%** | 52.6% | 63.3% |
| | LABBench 2 | **88.8%** | 85.4% | 68.6% | 73.1% |
| | RiemannBench | **76.0%** | 72.0% | 65.6% | 69.6% |
| Long context | GraphWalks, up to 128k (BFS F1) | **99.7%** | 98.7% | 91.4% | 90.6% |
| | GraphWalks, 256k to 1M (BFS F1) | **84.2%** | 71.8% | 65.0% | 66.8% |
| Computer use | Agent's Last Exam (pass rate) | **39.5%** | 34.2% | — | 38.2% |
| | OSWorld-2.0 (offline subset, partial score) | 69.2% | **72.6%** | — | — |
| Multimodal | Chartography | **71.6%** | 71.0% | 46.2% | 66.3% |
| | LVBench | **91.7%** | 87.5% | 79.7% | 83.7% |
| Cybersecurity | CWE-bench v1 | **68.0%** | **68.0%** | 58.0% | 67.0% |

*Source: Google DeepMind's Gemini 4 Argon launch materials. Methodology at deepmind.google/models/evals-methodology/gemini-4-argon. Bold marks the best score in each row.*

## Start with who made the table

These are Google's numbers, picked and run by Google, for a Google launch. That doesn't make them wrong. It does mean the benchmark list was chosen by the team with the most reason to look good on it, and the competitor scores were measured under Google's setup, not each vendor's own.

So I treat a table like this as a strong hint, not a verdict. The independent leaderboards and, more importantly, your own tests come later.

## Where Argon clearly pulls ahead

Gemini 4 Argon has the top score, or a share of it, in 14 of the 19 rows. Some of those wins are a point or two. A few are not, and those are the ones I'd pay attention to.

**Very long context.** At up to 128k tokens, every model in the table does fine, with all four between 90% and 99.7%. Between 256k and 1M tokens, Argon scores 84.2% and the next best is 71.8%. That's the biggest practical gap in the whole table. If your product needs to reason over a full codebase, a long contract or months of support tickets in one go, this row matters more than any coding benchmark.

**Agents doing office work.** AutomationBench (51.3% vs 42.5% for the next model) and Vals Finance Agent v2 (65.4% vs 58.9%) are both about multi-step tasks in business settings. Harvey's legal benchmark is the most striking on paper: 19.6% against single digits for everyone else. But read the absolute number too. Even the winner fails most of those tasks. "Best" and "ready to run unsupervised" are different things.

**Charts and video.** On LVBench and Chartography Argon leads, though GPT-6 Astra is close on charts (71.0% vs 71.6%).

## The rows where it doesn't win are more useful

If you only look at the blue cells, you'd conclude Argon is the best choice for everything. The grey cells tell a more practical story.

**Coding is close, and it depends on the kind of coding.** On Vibe Code Bench, all four models land between 89.6% and 91.9%. That's close to a tie, and any of them will handle typical "build me this feature" work. The differences show up in the harder, more specific tests:

- **Claude Opus 5.5** leads Terminal-bench 4.0 by a wide margin: 66.4%, against 57.4% to 58.2% for the others. That benchmark is about working in a real terminal over many steps: running commands, reading output, fixing what broke.
- **GPT-6 Astra** leads FrontierSWE v2 with 65.5%, ten points above Argon's 55.0%.
- **Argon** leads DeepSWE v1.1 with 77.9%.

Three coding benchmarks, three different winners. To me that's the most honest signal in the table. "Best at coding" isn't one thing anymore.

**Science tasks done in the terminal** go to GPT-6 Astra (68.1%), and **ML engineering** goes to Opus 5.5 (49.3%). In both cases Argon trails.

**Computer use is thin data.** Fable 5.1 has no scores here, and Opus 5.5 has none on OSWorld. GPT-6 Astra leads OSWorld-2.0, but on an "offline subset" with "partial score", which is a narrower test than the name suggests. I wouldn't pick a model for computer-use agents from these two rows.

## How I'd actually use this

When I built the RAG chatbot for REConnect, I used Claude Haiku 4.5, which isn't in this table at all. It was the right call, because the job was answering from well-chunked context quickly and cheaply, not solving the hardest benchmark in the world. Most production AI features look like that. The model only needs to be good enough at a narrow job, and fast and affordable at scale.

So here's how I'd turn a table like this into decisions:

1. **Match the benchmark to your workload.** If your agent lives in a terminal, Terminal-bench tells you more than the overall win count. If you process huge documents in one pass, the 1M-token row is the one to read.
2. **Run your own evals before switching.** Take 50 to 100 real examples from your product, with known good answers, and run each candidate on them. That will tell you more than any launch chart.
3. **Don't build for one model.** Put a thin layer between your app and the model API, so swapping models is a config change, not a rewrite. With launches this frequent, the "best" model changes every few months.
4. **Route by task if you can.** Nothing stops you from using one model for long-document analysis and another for coding agents. The table practically argues for it.
5. **Keep an eye on what the table leaves out.** There's nothing here about price, speed or rate limits. For a live chat widget, those decide more than a two-point benchmark gap.

## So, is Gemini 4 Argon the best model?

On Google's chosen benchmarks, mostly yes. It wins most rows, and in long context and business-agent tasks it wins by real margins. If those match your workload, it should be first on your list to test.

But the table also shows that the top models are now close on everyday coding, and that each one has areas it's clearly best at. That's good news for anyone building products. It means you can pick by fit, cost and speed, instead of feeling locked into whichever lab has the latest launch.

If you're choosing a model for a product feature and want a second opinion, [get in touch](/#contact). I'm happy to help set up a proper evaluation on your own data.
