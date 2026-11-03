---
title: "One Agent Builds, One Agent Tests: How I Used Claude Code Subagents to Build and QA an AI Proof of Concept"
slug: claude-code-subagents-builder-tester
date: 2026-11-04
category: AI / Developer Tools
summary: "How I used two Claude Code subagents, a builder and a tester, to build and QA an H5P + AI speaking demo in Moodle. Setup, prompts, bugs caught, lessons."
description: How I used two Claude Code subagents, a builder and a tester, to build and QA an H5P + AI speaking demo in Moodle. Setup, prompts, bugs caught, lessons.
---

Ask one AI agent to write code and then check its own work, and you'll usually get a confident "all done" back. It's like asking a student to grade their own exam.

I hit this while building a proof of concept for a client: AI speaking features added to existing H5P activities in Moodle. So I split the work in two. One Claude Code subagent builds. A second subagent tests, and it isn't allowed to fix anything. A task only counts as done when the tester passes it.

This article shows exactly how I set that up: the plan, the two agent files, the loop between them, and the real bugs the loop caught.

## The Project: AI Speaking Practice Inside Moodle

The client runs an English programme on Moodle, and their content is already built in H5P, the interactive content format Moodle supports out of the box. They wanted to see three things:

- Students answering existing activities by speaking instead of typing
- A spoken conversation with an AI tutor
- Scores still landing in the Moodle gradebook

The key constraint was "upgrade what exists, don't rebuild it." That shaped everything that followed.

The POC ended up with these parts:

- **Moodle 4.5 in Docker**, with a sample course, a test student and three ordinary "before" activities (Fill in the Blanks, Multiple Choice, Interactive Video)
- **H5P.VoiceLayer**, a custom H5P content type that wraps the existing Fill in the Blanks activity and adds a mic button to each blank using the browser's Web Speech API
- **H5P.AITutor**, a push-to-talk chat in which the tutor replies out loud
- **A small Node/Express AI service** that calls the Claude API with a fast, low-cost Haiku model, so the API key never reaches the browser

## Step 1: Start With a Plan That Has a "Done When" Column

Before creating any agents, I wrote a one-page plan as a Markdown file in the project. The most useful part turned out to be the timeline table, because every task has a "Done when" result:

| Task | Done when |
|---|---|
| Moodle in Docker + "before" activities | Moodle runs, activities open, mic prompt appears |
| Voice Layer | Speaking an answer fills the blank and scores it |
| AI Tutor | A 3-turn spoken conversation works |
| Pronunciation + points | Wrong words are flagged with a tip |
| xAPI + gradebook | A score appears for a test student |

That column became the tester's pass mark. Without it, "test this" is vague. With it, the tester has a yes-or-no question to answer.

The plan also lists what to cut if time runs short, risks to check early (for example, "does the mic even work inside Moodle's H5P iframe?"), and a checklist at the end.

## Step 2: Write a Workflow File

Next I added `workflow.md`, which describes how the two agents work together:

```text
Task from plan → Builder builds it → handoff note → Tester tests it
     ↑                                                   |
     └──────────── bug report (FAIL) ────────────────────┤
                                                         ↓ PASS
                                          Tick the checklist, next task
```

The rules are simple:

1. Pick the next task from the plan.
2. The builder builds it and writes a handoff note.
3. The tester tests it against the "Done when" column.
4. **PASS:** tick the checklist and move on.
5. **FAIL:** the tester writes a bug report, and the builder fixes only what's in it.
6. **Three failures on one task:** stop and decide whether to cut it.

The third-failure rule keeps the loop from running forever on something that isn't worth the time.

## Step 3: Create the Two Claude Code Subagents

Claude Code subagents are Markdown files in `.claude/agents/`. Each one has a short header (name, description, allowed tools) followed by its instructions. Claude Code reads the description to decide when to use the agent, and the tool list controls what the agent can actually do.

### The builder agent

```yaml
---
name: poc-builder
description: Builds one task of the H5P + AI POC ... and returns a
  handoff note for poc-tester. Use when a task from the plan needs to
  be created or a tester bug report needs fixing.
tools: Read, Write, Edit, Bash, Glob, Grep
---
```

Its main rules:

- Build only the task you were given, in the plan's order.
- Keep the API key in `.env`. Never put it in browser code, logs or commits, and provide a `.env.example` with placeholders only.
- Use a Haiku model with a short `max_tokens` and a strict tutor prompt.
- Handle failures with a clear message: denied mic, unsupported browser, AI errors.
- Never mark a task done. Only the tester can do that.

Every run ends with the same handoff note:

```text
Task:         <task name from the timeline>
What changed: <files added or edited>
How to run:   <commands, URLs, logins>
What to test: <the "Done when" result>
Known gaps:   <anything not finished or not working yet>
```

The "Known gaps" line matters more than it looks. It gives the builder a place to admit what's unfinished instead of glossing over it.

### The tester agent

```yaml
---
name: poc-tester
description: Tests one task of the H5P + AI POC against its "Done when"
  result, using the handoff note from poc-builder, and returns a PASS or
  FAIL report. Never fixes code.
tools: Read, Edit, Bash, Glob, Grep, <browser tools>
---
```

The tester gets browser tools (navigate, click, read the page, read console messages and network requests, run JavaScript) so it can use the app the way a person would. It does not get `Write`.

Its main rules:

- Follow the handoff note's "How to run" steps exactly as written.
- Check the console and network tab, and call the AI service directly with `curl`, including an error case.
- Check that no API key appears in page source or network responses.
- Never fix code. The only file it may edit is the plan, and only to tick a checklist item.
- Give a clear PASS or FAIL. No "mostly works".

Its report format:

```text
Task / Result / Browser / Steps / Expected / Actual /
Evidence / Needs manual check / Other issues
```

### Why the separation works

The builder wants to finish. The tester has no stake in the code, so it has nothing to defend. Because it can't patch problems quietly, every problem it finds shows up in a report where I can see it.

## Step 4: Run the Loop, One Task at a Time

Running a task is a single instruction to Claude Code:

> Use poc-builder to build task 1, then pass its handoff note to poc-tester.

The builder produced the Docker setup, the install scripts and the H5P packages. The tester logged in, opened every activity, checked the console, and either passed it or sent back a report.

### The QA problem: you can't speak to an automated browser

Speech is the core of this demo, and an automated browser has no voice. My workaround was to have the builder add small test hooks to each H5P library, for example `simulateTranscript(blankIndex, text)` and `simulateError(code)`. The tester calls these from the page to feed in a "heard" phrase, or an error such as permission denied, and then checks what the activity does.

The tester's report says plainly when speech was simulated, and anything that still needs a real human with a real microphone goes under "Needs manual check". That kept the results honest. A pass meant "the logic works with simulated speech", not "the mic definitely works in Chrome".

For the AI tutor, the service has a mock mode (`AI_MOCK=1`) that returns canned replies, so the chat flow could be tested end to end without spending API credit.

## What the Loop Caught

Some problems were found by the builder itself, and some only showed up in the tester's reports. Both are worth knowing.

**1. Escaped text on screen (builder found it, tester confirmed it).** Moodle's H5P stores text HTML-encoded, so messages showed `&quot;` instead of quote marks. The builder spotted this, decoded the strings, and listed the fix in its handoff note. The tester then checked every error message for leftover entities like `&quot;` and found none.

**2. Scores that never reached the gradebook (builder found it, tester confirmed it).** The Voice Layer listened for scoring events "bubbling up" from the wrapped activity, which is the usual pattern. But `H5P.newRunnable` replaces the wrapper's prototype, so the events never arrived and no grade was recorded. The builder changed the library to listen on the inner activity directly. The tester didn't stop at the page: it checked that the grade actually appeared in Moodle's gradebook.

**3. Small issues in the "Other issues" list (tester found them).** Each tester report ended with problems outside the task being tested. For example: the voice activity's intro still said "Type the missing word", there was no Retry button after a full score, every Check created a new attempt, and the Interactive Video grade was empty. None of these failed the task, but they're exactly the things a client notices in a demo.

**4. A billing problem, not a code problem.** When the real API key went in, the tutor returned errors. Because the AI service logs the error type and status instead of failing silently, the upstream message was clear: the account had no credit. That was a billing fix, not a debugging session.

Having the builder list its fixes in the handoff note mattered here. It told the tester exactly what to re-check.

## Lessons Learned

### Put guardrails in the agent files, not just in your head

Early on, while Docker was low on memory, Claude suggested a broad "stop every running container" command as a quick fix. My Docker Desktop runs several other client projects, so that would have been bad. I added a rule to both agent files: only touch this project's compose project (`h5m-poc`), never stop or prune anything else, and run compose only from the project folder.

If a rule matters, write it where the agent reads it every time it runs.

### Use a skill to check API details

For the Claude API call, I used Claude Code's built-in `claude-api` skill to confirm the right model ID and request settings for Haiku, instead of relying on memory. API details change, so checking takes a minute and saves a confusing 400 error later.

### Keep secrets out of the conversation

The test logins were generated into `.env`, which is git-ignored, and the agents point to that file instead of printing passwords. I added the real API key myself. The agents never handled it.

### Make "manual check" a normal result

Some things an agent can't verify, like a real microphone permission prompt. Giving the tester a standard place to say so beats a fake pass.

### Small, repeatable setup

Because the builder scripted the whole install, moving to another machine means copying the folder (without `.env`), creating `.env` from `.env.example`, and running:

```bash
docker compose up -d --build
```

Moodle, the course, the test student, both custom H5P libraries and all the activities install themselves on first start.

## How to Try This Pattern on Your Own Project

1. **Write a plan with a "Done when" column.** One line per task, in plain words.
2. **Add a workflow file** describing the loop, the handoff note and the bug report.
3. **Create two files in `.claude/agents/`:** a builder with write tools, and a tester without them.
4. **Give the tester real eyes:** browser tools, `curl`, logs.
5. **Add test hooks** for anything an automated tester can't do physically, such as speech, camera or hardware.
6. **Put your safety rules in both agent files:** secrets, shared infrastructure, scope.
7. **Run one task at a time and read the reports.** They're short, and they tell you what's actually true.

## Conclusion

Splitting the work between a builder subagent and a tester subagent didn't make the AI smarter. It made the process more honest. The builder has to hand over a note saying what changed and what's still missing. The tester has a clear pass mark and can't paper over problems. I review short reports instead of guessing.

For this POC, that pattern produced a working Moodle demo with voice-answered H5P activities, an AI tutor and gradebook scores. It also left a clear list of what still needs a human to check. If you're using Claude Code for anything bigger than a single file, try the builder and tester split on your next feature.

## FAQs

### What are Claude Code subagents?

They're specialised assistants defined as Markdown files in `.claude/agents/`. Each one has its own instructions and its own list of allowed tools, and Claude Code can hand tasks to them.

### Why not let one agent build and test?

An agent that checks its own work tends to confirm it. A separate tester that can't edit code reports problems instead of quietly patching them, so you see what really happened.

### How do you QA voice features with an AI agent?

Add test hooks to the code that simulate a speech result or an error, have the tester call them, and list real-microphone checks as manual steps.

### Do subagents need special setup?

No. Create the `.claude/agents/` folder in your project and add one Markdown file per agent. If a new agent doesn't show up, start a new Claude Code session so it's loaded.

### Is H5P required to add AI features to Moodle?

No. Moodle runs fine without H5P, and you could build the same features as a Moodle plugin. H5P made sense here because the client's existing content was already H5P.
