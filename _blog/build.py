#!/usr/bin/env python3
"""Build the blog from Markdown posts.

Usage (from the repo root):  python3 _blog/build.py

Reads _posts/*.md (front matter + Markdown) and writes:
  blog/index.html            list of all posts
  blog/<slug>/index.html     one page per post
  blog/rss.xml               feed (for Dev.to / Hashnode import)
  sitemap.xml                homepage + blog pages

Front matter keys: title, slug, date (YYYY-MM-DD), category, description.
Optional: order (tie-breaker for posts on the same date; lower shows first), updated.
Requires: pip install markdown
"""
import html
import math
import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://www.ahmadhassan.pro"
AUTHOR = "Ahmad Hassan"
OG_IMAGE = f"{SITE}/images/og-image.jpg"
esc = html.escape
TZ = timezone(timedelta(hours=5))  # Pakistan time; schema.org dates need a timezone


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing front matter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    for key in ("title", "slug", "date", "category", "description"):
        if not meta.get(key):
            raise SystemExit(f"{path.name}: front matter needs '{key}'")
    body = m.group(2)
    meta["html"] = markdown.markdown(body, extensions=["fenced_code", "tables", "sane_lists"])
    meta["minutes"] = max(1, math.ceil(len(re.findall(r"\w+", body)) / 220))
    meta["dt"] = datetime.strptime(meta["date"], "%Y-%m-%d").replace(hour=9, tzinfo=TZ)
    meta["iso"] = meta["dt"].isoformat()
    upd = meta.get("updated")
    meta["iso_updated"] = datetime.strptime(upd, "%Y-%m-%d").replace(hour=9, tzinfo=TZ).isoformat() if upd else meta["iso"]
    meta["pretty"] = meta["dt"].strftime("%b %-d, %Y")
    meta["url"] = f"{SITE}/blog/{meta['slug']}/"
    return meta


HEAD = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>try{{var t=localStorage.getItem('ah-theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="author" content="Ahmad Hassan">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{og}">
<link rel="alternate" type="application/rss+xml" title="Ahmad Hassan — Blog" href="/blog/rss.xml">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#05070f">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:ital,wght@0,300..900;1,300..900&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/blog/blog.css">
{jsonld}
</head>
<body>
<div class="orb"></div>
<header class="bnav">
  <div class="wrap bnav-in">
    <a href="/" class="brand"><div class="brand-badge">AH</div><div class="brand-name">Ahmad<em> Hassan</em></div></a>
    <nav class="bnav-links">
      <a href="/" class="hide-sm">Portfolio</a>
      <a href="/blog/" class="on">Blog</a>
      <a href="/#contact">Contact</a>
      <button class="icon-btn" id="themeBtn" aria-label="Toggle theme">
        <svg id="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>
        <svg id="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
      </button>
    </nav>
  </div>
</header>
"""

FOOT = """<a id="wa" href="https://wa.me/923039625229?text=Hi%20Ahmad%2C%20I%20found%20your%20portfolio%20and%20would%20like%20to%20discuss%20a%20project." target="_blank" rel="noopener" aria-label="Chat with Ahmad on WhatsApp">
  <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.66-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.09 1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35M12.05 21.79h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.82 9.82 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88m8.41-18.3A11.81 11.81 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.68 1.45h.01c6.55 0 11.89-5.34 11.89-11.89 0-3.18-1.24-6.16-3.48-8.41"/></svg>
  <span class="wa-tip">Chat on WhatsApp</span>
</a>
<footer class="bfoot">
  <div class="wrap">
    <span>© <span id="year">{year}</span> Ahmad Hassan</span>
    <span><a href="/">Portfolio</a> · <a href="/blog/rss.xml">RSS</a> · <a href="https://www.linkedin.com/in/aimhassan" target="_blank" rel="noopener">LinkedIn</a> · <a href="https://github.com/aim878" target="_blank" rel="noopener">GitHub</a></span>
  </div>
</footer>
<script>
document.getElementById('year').textContent = new Date().getFullYear();
document.getElementById('themeBtn').addEventListener('click', function () {
  var next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem('ah-theme', next); } catch (e) {}
});
</script>
</body>
</html>
"""


def jsonld(obj):
    import json
    return '<script type="application/ld+json">\n' + json.dumps(obj, indent=2, ensure_ascii=False) + "\n</script>"


PERSON = {"@type": "Person", "@id": f"{SITE}/#person", "name": AUTHOR, "url": f"{SITE}/"}


def page_head(title, desc, url, ogtype, ld):
    return HEAD.format(title=esc(title), desc=esc(desc), url=url, ogtype=ogtype, og=OG_IMAGE, jsonld=jsonld(ld))


def render_post(p, prev, nxt):
    crumbs = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{SITE}/blog/"},
            {"@type": "ListItem", "position": 3, "name": p["title"], "item": p["url"]},
        ],
    }
    post = {
        "@type": "BlogPosting",
        "headline": p["title"], "description": p["description"], "image": OG_IMAGE,
        "datePublished": p["iso"], "dateModified": p["iso_updated"],
        "author": PERSON, "publisher": PERSON,
        "mainEntityOfPage": p["url"], "articleSection": p["category"],
        "isPartOf": {"@id": f"{SITE}/#website"},
    }
    ld = {"@context": "https://schema.org", "@graph": [post, crumbs]}
    pn = ""
    if prev or nxt:
        pn = '<nav class="pn">'
        if prev:
            pn += f'<a href="/blog/{prev["slug"]}/"><small>← Newer</small><span>{esc(prev["title"])}</span></a>'
        if nxt:
            pn += f'<a class="next" href="/blog/{nxt["slug"]}/"><small>Older →</small><span>{esc(nxt["title"])}</span></a>'
        pn += "</nav>"
    body = f"""<main class="narrow">
  <header class="post-head">
    <a href="/blog/" class="back">← All articles</a><br>
    <span class="eyebrow">{esc(p['category'])}</span>
    <h1>{esc(p['title'])}</h1>
    <p class="lede">{esc(p['description'])}</p>
    <div class="byline">
      <img src="/images/ah.webp" alt="Ahmad Hassan" width="42" height="42">
      <div><div class="who">Ahmad Hassan</div><div class="when"><time datetime="{p['date']}">{p['pretty']}</time> · {p['minutes']} min read</div></div>
    </div>
  </header>
  <article class="prose">
{p['html']}
  </article>
  <aside class="cta">
    <div><h3>Building something similar?</h3><p>I'm a senior full-stack developer and team lead — happy to talk.</p></div>
    <a class="btn" href="/#contact">Get in touch →</a>
  </aside>
  {pn}
</main>
"""
    title = f"{p['title']} | Ahmad Hassan"
    return page_head(title, p["description"], p["url"], "article", ld) + body + FOOT.replace("{year}", str(datetime.now().year))


def render_index(posts):
    url = f"{SITE}/blog/"
    desc = "Articles by Ahmad Hassan on AI/RAG systems, deployment tooling, and full-stack performance engineering."
    ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Ahmad Hassan — Blog", "url": url,
          "author": PERSON,
          "blogPost": [{"@type": "BlogPosting", "headline": p["title"], "url": p["url"], "datePublished": p["iso"]} for p in posts]}
    cards = "\n".join(
        f"""    <a class="card" href="/blog/{p['slug']}/">
      <span class="cat">{esc(p['category'])}</span>
      <h2>{esc(p['title'])}</h2>
      <p>{esc(p['description'])}</p>
      <div class="meta"><span>{p['pretty']} · {p['minutes']} min</span><b>Read →</b></div>
    </a>""" for p in posts)
    body = f"""<main class="wrap">
  <section class="page-head">
    <span class="eyebrow">Writing</span>
    <h1>Blog &amp; Articles</h1>
    <p>Deep dives on the systems I build — retrieval pipelines, deployment tooling, and performance work.</p>
  </section>
  <div class="grid">
{cards}
  </div>
</main>
"""
    return page_head("Blog | Ahmad Hassan — Full-Stack Developer", desc, url, "website", ld) + body + FOOT.replace("{year}", str(datetime.now().year))


def render_rss(posts):
    items = "\n".join(f"""  <item>
    <title>{esc(p['title'])}</title>
    <link>{p['url']}</link>
    <guid isPermaLink="true">{p['url']}</guid>
    <pubDate>{format_datetime(p['dt'])}</pubDate>
    <category>{esc(p['category'])}</category>
    <description>{esc(p['description'])}</description>
    <content:encoded><![CDATA[{p['html']}]]></content:encoded>
  </item>""" for p in posts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Ahmad Hassan — Blog</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/blog/rss.xml" rel="self" type="application/rss+xml"/>
  <description>Articles on AI/RAG systems, deployment tooling, and full-stack performance.</description>
  <language>en</language>
{items}
</channel>
</rss>
"""


def render_sitemap(posts):
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [(f"{SITE}/", today, "monthly", "1.0"), (f"{SITE}/blog/", posts[0]["date"] if posts else today, "weekly", "0.8")]
    urls += [(p["url"], p.get("updated", p["date"]), "yearly", "0.7") for p in posts]
    rows = "\n".join(f"""  <url>
    <loc>{u}</loc>
    <lastmod>{d}</lastmod>
    <changefreq>{c}</changefreq>
    <priority>{pr}</priority>
  </url>""" for u, d, c, pr in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}\n</urlset>\n'


def main():
    posts = sorted((parse(f) for f in (ROOT / "_posts").glob("*.md")), key=lambda p: (p["date"], -int(p.get("order", 0))), reverse=True)
    out = ROOT / "blog"
    for i, p in enumerate(posts):
        prev = posts[i - 1] if i > 0 else None
        nxt = posts[i + 1] if i + 1 < len(posts) else None
        d = out / p["slug"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(render_post(p, prev, nxt), encoding="utf-8")
    (out / "index.html").write_text(render_index(posts), encoding="utf-8")
    (out / "rss.xml").write_text(render_rss(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(render_sitemap(posts), encoding="utf-8")
    print(f"Built {len(posts)} post(s): " + ", ".join(p["slug"] for p in posts))


if __name__ == "__main__":
    main()
