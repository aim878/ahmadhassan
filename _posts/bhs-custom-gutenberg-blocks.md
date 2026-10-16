---
title: Building 70+ Custom Gutenberg Blocks for a NYC Real Estate Brokerage
slug: bhs-custom-gutenberg-blocks
date: 2026-10-16
category: WordPress / Real Estate
summary: "How I built 70+ custom Gutenberg blocks so Brown Harris Stevens' editors can build full marketing pages without code, and what kept it manageable."
description: At SLTech I built BHS Custom Blocks, a WordPress plugin with 70+ Gutenberg blocks for Brown Harris Stevens, one of New York's best-known residential brokerages. Here's how a block library that size stays easy for editors and easy to maintain.
---

A real estate brokerage publishes a lot of pages. New listings, agent profiles, neighbourhood guides, market reports, blog posts, campaign landing pages. And the people who need those pages are marketers and editors, not developers.

At [SLTech](https://sltech.io/) I built **BHS Custom Blocks**, a WordPress Gutenberg plugin for [Brown Harris Stevens](https://www.bhsusa.com/blog), one of New York City's best-known residential brokerages. It has more than 70 custom blocks. The goal was simple to say and harder to deliver: **editors should be able to build a full marketing page on their own, and it should still look like Brown Harris Stevens.**

This post covers how I think about a block library that size: what goes in it, what keeps it consistent, and what makes editors actually like using it.

## Why custom blocks, not a page builder

Page builders give editors a lot of freedom. That's the problem. With enough freedom, every page slowly drifts away from the brand: a slightly different blue, a new font size, a button that looks almost right.

Custom blocks flip that around. Each block is a finished piece of the design. The editor picks *what* goes on the page and fills in the content. The block decides *how* it looks.

For a luxury brand like BHS, that trade-off is worth it:

- **The brand stays consistent** on every page, no matter who built it.
- **Pages stay fast**, because each block only loads what it needs. There's no heavy builder framework on top.
- **Editors can't break the layout** by accident.
- **It's native WordPress.** Content stays in the standard editor, so there's nothing extra to learn or maintain.

## What 70+ blocks actually covers

Seventy sounds like a lot until you list what a brokerage website needs. The blocks fall into a few families:

| Family | Examples |
|---|---|
| **Agents** | Agent profiles, team listings, contact cards |
| **Property** | Listing cards, featured properties, property details |
| **Heroes** | Full-width hero banners, campaign headers |
| **Market data** | Market report sections, stats and highlights |
| **Communities** | Neighbourhood and community pages |
| **Editorial** | Article layouts, quotes, image and text sections |

Grouping them this way matters for editors too. In the block inserter, they look for "an agent block" or "a hero", not for block number 47.

## Keeping 70 blocks consistent

The hard part of a big block library isn't building block number 70. It's making sure block 70 still looks and behaves like block 1. A few rules make that possible.

**One set of design tokens.** Colours, font sizes, spacing and breakpoints should live in one place, shared by every block. If the brand blue changes, it should change once.

**Shared building pieces.** Most blocks are made of the same smaller parts: headings, buttons, image frames, cards. Build those once as shared React components for the editor and shared templates on the front end, and reuse them everywhere.

**The same controls everywhere.** If one block has its spacing setting in the sidebar, every block should. Editors learn the pattern once and it works across the whole library.

**Clear naming.** Every block gets a predictable name and lives in a clear category. Future developers will thank you, and so will editors searching the inserter.

## Static vs. dynamic blocks

Gutenberg blocks come in two kinds, and choosing the right one for each block saves a lot of pain later.

- **Static blocks** save their final HTML into the post. They're a good fit for content the editor fully controls, like an editorial section or a quote.
- **Dynamic blocks** are rendered by PHP on the server each time the page loads. They're the right choice for anything that changes on its own, like listings or agent details, because the page always shows the current data.

A useful rule: **if the content can change without an editor touching the page, make the block dynamic.** Otherwise you end up with pages showing a sold property or an agent who left months ago.

Dynamic blocks have one more benefit for a library this size: when you change a block's design, every page using it updates at once. With static blocks, old pages keep the old HTML until someone re-saves them.

## Designing for editors, not developers

A block is only useful if editors are comfortable using it. What helps:

- **The editor preview should match the live page.** If a block looks different in the editor than on the site, editors stop trusting it.
- **Give fewer options, with good defaults.** Every setting is a decision the editor has to make. Most blocks should look right the moment they're added.
- **Use patterns for common pages.** A ready-made layout for "new development launch" or "neighbourhood guide" lets editors start from a page that already works, then swap in their content.
- **Write labels in plain language.** "Background image", not "bg_media_id".

## What I'd tell anyone building a block library

1. **Design the system before the blocks.** Tokens and shared components first. Building blocks one by one without them is how you end up with 70 slightly different buttons.
2. **Default to dynamic for live data.** Listings and people change; pages shouldn't go stale.
3. **Fewer options make happier editors.** Constraints are a feature, not a limitation.
4. **Treat editors as your users.** Watch them build a page. The confusing parts show up in minutes.

A good block library feels boring in the best way. Editors open WordPress, build the page they need, and it looks right. That's the whole point.

Need a custom Gutenberg block library or a WordPress build for your team? [Get in touch](/#contact).
