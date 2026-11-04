#!/usr/bin/env python3
"""Builds Evan's site into the _site/ folder.

You never need to run this yourself: GitHub runs it every time a file changes.
To preview on a computer anyway:  python3 build.py   then open _site/index.html
It uses only Python's built-in tools, so nothing needs to be installed.
"""
import datetime
import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"

# ---------- reading Markdown files ----------

def read_md(path):
    """Split a Markdown file into its settings block (between --- lines) and its text."""
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)  # notes to yourself never show
    meta = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].strip().splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip().lower()] = value.strip().strip('"')
            text = text[end + 4:]
    return meta, text.strip("\n")


def esc(value):
    return html.escape(value, quote=True)


def fix_url(url, prefix):
    if re.match(r"^(https?:|mailto:|#|/)", url):
        return url
    return prefix + url


PLACEHOLDER = re.compile(r"\[((?:ADD|WRITE HERE)[^\]]*)\](?!\()")


def inline(text, prefix=""):
    s = html.escape(text, quote=False)

    def image(m):
        return f'<img src="{esc(fix_url(m[2], prefix))}" alt="{esc(m[1])}" loading="lazy">'

    def link(m):
        label, url = m[1], m[2]
        cls = ' class="ph"' if label.startswith(("ADD", "WRITE HERE")) else ""
        ext = ' target="_blank" rel="noopener"' if url.startswith("http") else ""
        return f'<a href="{esc(fix_url(url, prefix))}"{cls}{ext}>{label}</a>'

    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", image, s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    s = PLACEHOLDER.sub(r'<mark class="ph">\1</mark>', s)
    s = re.sub(r"(?<![\w>])WRITE HERE(?![\w<])", '<mark class="ph">WRITE HERE</mark>', s)
    return s


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"


def paragraph(lines, prefix):
    first = lines[0]
    m = re.fullmatch(r"!\[([^\]]*)\]\(([^)\s]+)\)", first)
    if m:  # a picture on its own line, with an optional caption line under it
        caption = " ".join(lines[1:]).strip()
        if caption.startswith("*") and caption.endswith("*") and not caption.startswith("**"):
            caption = caption[1:-1]
        src = esc(fix_url(m[2], prefix))
        img = f'<img src="{src}" alt="{esc(m[1])}" loading="lazy">'
        source = re.search(r"\]\(([^)\s]+)\)", caption)
        if source:
            img = f'<a href="{esc(fix_url(source[1], prefix))}" target="_blank" rel="noopener">{img}</a>'
        cap = f"<figcaption>{inline(caption, prefix)}</figcaption>" if caption else ""
        return f"<figure>{img}{cap}</figure>"
    return f"<p>{inline(' '.join(lines), prefix)}</p>"


def markdown(text, prefix=""):
    out, para, items, quote = [], [], [], []
    kind = None

    def flush():
        nonlocal para, items, quote, kind
        if para:
            out.append(paragraph(para, prefix))
            para = []
        if items:
            lis = "".join(f"<li>{inline(i, prefix)}</li>" for i in items)
            out.append(f"<{kind}>{lis}</{kind}>")
            items, kind = [], None
        if quote:
            out.append(f"<blockquote>{markdown(chr(10).join(quote), prefix)}</blockquote>")
            quote = []

    for raw in text.split("\n"):
        s = raw.strip()
        if not s:
            flush()
            continue
        m = re.match(r"(#{1,4})\s+(.*)", s)
        if m:
            flush()
            level = max(2, len(m[1]))  # the page title is the only top heading
            out.append(f'<h{level} id="{slugify(m[2])}">{inline(m[2], prefix)}</h{level}>')
            continue
        bullet = re.match(r"[-+*]\s+(.*)", s)
        number = re.match(r"\d+[.)]\s+(.*)", s)
        if bullet or number:
            want = "ul" if bullet else "ol"
            if para or quote or (kind and kind != want):
                flush()
            kind = want
            items.append((bullet or number)[1])
            continue
        if s.startswith(">"):
            if not quote:
                flush()
            quote.append(s[1:].lstrip())
            continue
        if items and raw[:1] in (" ", "\t"):
            items[-1] += " " + s
            continue
        if items or quote:
            flush()
        para.append(s)
    flush()
    return "\n".join(out)


def nice_date(value):
    try:
        d = datetime.date.fromisoformat(value)
    except ValueError:
        return value, datetime.date.min
    return f"{d:%B} {d.day}, {d.year}", d

# ---------- page frame ----------

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' rx='16' fill='%2317181c'/%3E"
    "%3Ctext x='32' y='41' font-family='Arial,sans-serif' font-size='26' font-weight='700' "
    "fill='white' text-anchor='middle'%3EEN%3C/text%3E%3C/svg%3E"
)


def page(title, body, active, prefix, description, name, image=None):
    def nav(label, href, key):
        current = ' aria-current="page"' if key == active else ""
        return f'<a href="{prefix}{href}"{current}>{label}</a>'

    og_image = f'<meta property="og:image" content="{esc(image)}">' if image and image.startswith("http") else ""
    year = datetime.date.today().year
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
{og_image}
<link rel="icon" href="{FAVICON}">
<link rel="stylesheet" href="{prefix}style.css">
</head>
<body>
<header class="top">
  <div class="top-in">
    <a class="brand" href="{prefix}index.html"><i aria-hidden="true">EN</i><span>{esc(name)}</span></a>
    <nav class="views" aria-label="Main menu">
      {nav("Home", "index.html", "home")}
      {nav("Resume", "index.html#resume", "resume")}
      {nav("Blog", "blog.html", "blog")}
    </nav>
  </div>
</header>
<main>
{body}
</main>
<footer class="foot">© {year} {esc(name)}</footer>
</body>
</html>
"""

# ---------- building ----------

def load_posts():
    posts = []
    for path in sorted((ROOT / "posts").glob("*.md")):
        meta, text = read_md(path)
        label, sort_key = nice_date(meta.get("date", ""))
        posts.append({
            "slug": slugify(path.stem),
            "title": meta.get("title", path.stem),
            "summary": meta.get("summary", ""),
            "date": label,
            "iso": meta.get("date", ""),
            "sort": sort_key,
            "text": text,
        })
    posts.sort(key=lambda p: p["sort"], reverse=True)
    return posts


def post_list(posts, prefix, heading_level=2):
    h = f"h{heading_level}"
    cards = []
    for p in posts:
        cards.append(f"""<a class="card post-card" href="{prefix}posts/{p['slug']}.html">
  <time datetime="{esc(p['iso'])}">{esc(p['date'])}</time>
  <{h}>{inline(p['title'])}</{h}>
  <p>{inline(p['summary'])}</p>
  <span class="more">Read post <span aria-hidden="true">→</span></span>
</a>""")
    return "\n".join(cards)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copy(ROOT / "style.css", OUT / "style.css")
    shutil.copytree(ROOT / "images", OUT / "images")
    (OUT / ".nojekyll").write_text("")

    meta, text = read_md(ROOT / "home.md")
    name = meta.get("name", "Your name")
    headline = meta.get("headline", "")
    photo = meta.get("photo", "images/headshot.jpg")
    linkedin = meta.get("linkedin", "")
    tags = [t.strip() for t in meta.get("tags", "").split("|") if t.strip()]
    posts = load_posts()

    # the text before the first "## " heading is the bio; each "## " section is a resume card
    parts = re.split(r"^##\s+", text, flags=re.M)
    bio, sections = parts[0], parts[1:]

    chips = "".join(f"<li>{inline(t)}</li>" for t in tags)
    li_cls = "pbtn main" + (" ph-btn" if "ADD" in linkedin else "")
    hero = f"""<section class="card hero">
  <img class="photo" src="{esc(photo)}" alt="Headshot of {esc(name)}" width="160" height="160">
  <div class="hero-text">
    <h1>{esc(name)}</h1>
    <p class="headline">{inline(headline)}</p>
    {f'<ul class="chips">{chips}</ul>' if chips else ''}
  </div>
  <div class="bio">{markdown(bio)}</div>
  <div class="actions">
    <a class="{li_cls}" href="{esc(linkedin)}" target="_blank" rel="noopener">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.75h4v11H3zM9.5 9.75h3.8v1.5h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1v5.45h-4v-4.83c0-1.15-.02-2.64-1.6-2.64-1.61 0-1.85 1.25-1.85 2.55v4.92h-4z"/></svg>
      LinkedIn
    </a>
    <a class="pbtn" href="blog.html">Read my blog</a>
  </div>
</section>"""

    cards = []
    for sec in sections:
        title, _, rest = sec.partition("\n")
        cards.append(f'<section class="card resume-card"><h2>{inline(title.strip())}</h2>{markdown(rest)}</section>')
    resume = f'<h2 class="sect" id="resume">Resume</h2>\n' + "\n".join(cards) if cards else ""

    latest = ""
    if posts:
        links = "".join(
            f'<li><a href="posts/{p["slug"]}.html">{inline(p["title"])}</a><time datetime="{esc(p["iso"])}">{esc(p["date"])}</time></li>'
            for p in posts[:3]
        )
        latest = f"""<h2 class="sect">From the blog</h2>
<section class="card latest"><ul>{links}</ul><a class="more" href="blog.html">All posts <span aria-hidden="true">→</span></a></section>"""

    description = re.sub(r"<[^>]+>", "", inline(headline))
    (OUT / "index.html").write_text(
        page(f"{name}", "\n".join([hero, resume, latest]), "home", "", description, name, photo),
        encoding="utf-8",
    )

    blog_body = f"""<section class="page-head">
  <h1>Blog</h1>
  <p>Writing on accounting, analytics and consulting.</p>
</section>
{post_list(posts, "")}"""
    (OUT / "blog.html").write_text(
        page(f"Blog · {name}", blog_body, "blog", "", f"Blog posts by {name}", name), encoding="utf-8"
    )

    (OUT / "posts").mkdir()
    for p in posts:
        body = f"""<article class="card article">
  <a class="back" href="../blog.html"><span aria-hidden="true">←</span> All posts</a>
  <h1>{inline(p['title'], '../')}</h1>
  <p class="meta">By {esc(name)} · <time datetime="{esc(p['iso'])}">{esc(p['date'])}</time></p>
  {markdown(p['text'], '../')}
</article>"""
        desc = re.sub(r"<[^>]+>", "", inline(p["summary"])) or p["title"]
        (OUT / "posts" / f"{p['slug']}.html").write_text(
            page(f"{p['title']} · {name}", body, "blog", "../", desc, name), encoding="utf-8"
        )

    print(f"Built {len(posts)} posts into {OUT}")


if __name__ == "__main__":
    build()
