"""Build the static program directory and stable, standalone episode pages."""

import json
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
ORIGIN = "https://zhanghaoquan631.github.io/tianxi-podcasts/"
PROGRAMS = json.loads((ROOT / "data" / "episodes.json").read_text(encoding="utf-8"))


def page(program, prefix):
    slug = program["id"]
    title = escape(program["title"])
    canonical = ORIGIN + slug + "/"
    description = escape(program["introduction"], quote=True)
    audio = f"{prefix}media/{slug}.mp3"
    links = []
    for entry in PROGRAMS:
        current = ' aria-current="page"' if entry["id"] == slug else ""
        links.append(
            f'<li><a href="{prefix}{entry["id"]}/"{current}>'
            f'<span>{escape(entry["title"])}</span>'
            f'<small>{escape(entry["duration"])}</small></a></li>'
        )

    transcript = "\n".join(
        f'<li data-time="{int(row["at"])}"><button type="button" class="time js-only" '
        f'aria-label="跳到 {escape(row["time"])}">{escape(row["time"])}</button>'
        f'<noscript><span class="time">{escape(row["time"])}</span></noscript>'
        f'<p>{escape(row["text"])}</p></li>'
        for row in program["transcript"]
    )
    sections = "\n".join(
        f'<h3>{escape(section["title"])}</h3>'
        + "".join(f'<p>{escape(paragraph)}</p>' for paragraph in section["paragraphs"])
        for section in program["sections"]
    )
    references = []
    for reference in program["references"]:
        if urlsplit(reference["href"]).scheme != "https":
            raise ValueError(f"Unsupported reference protocol in {slug}")
        references.append(
            f'<li><a href="{escape(reference["href"], quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">{escape(reference["label"])}</a></li>'
        )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{description}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title} · 播客资料室">
  <meta property="og:url" content="{canonical}">
  <meta property="og:description" content="{description}">
  <link rel="canonical" href="{canonical}">
  <link rel="stylesheet" href="{prefix}assets/programs.css">
  <script defer src="{prefix}assets/player.js"></script>
  <title>{title} · 播客资料室</title>
</head>
<body>
  <a class="skip" href="#episode">跳到本集</a>
  <header class="masthead">
    <div class="masthead-inner"><a href="{prefix}">播客资料室</a><span>天禧 AI 原声</span></div>
  </header>
  <div class="layout">
    <nav class="catalog" aria-labelledby="catalog-heading">
      <h2 id="catalog-heading">全部节目</h2>
      <ul>{"".join(links)}</ul>
    </nav>
    <main id="episode">
      <header class="episode-header">
        <h1>{title}</h1>
        <div class="episode-actions">
          <span>天禧 AI 原声 · {escape(program["duration"])}</span>
          <button class="share js-only" type="button" id="share">复制本集链接</button>
        </div>
        <div class="share-fallback" id="share-fallback" hidden>
          <label for="share-url">本集链接</label>
          <input id="share-url" readonly value="{canonical}">
        </div>
        <p id="share-status" class="status" role="status"></p>
      </header>
      <section class="player" aria-label="节目播放">
        <audio controls preload="metadata" aria-label="{title}">
          <source src="{audio}" type="audio/mpeg">
          <a href="{audio}">打开原声</a>
        </audio>
        <div class="player-footer">
          <p id="audio-status" role="status"></p>
          <a href="#references">节目与核对资料</a>
        </div>
      </section>
      <section class="transcript" id="transcript" aria-labelledby="transcript-heading">
        <header class="section-header">
          <h2 id="transcript-heading">逐字稿</h2>
          <label class="follow js-only"><input type="checkbox" id="follow" checked> 自动跟随</label>
        </header>
        <p class="caption">节目由天禧 AI 生成，原书 v1.4 标为虚构。逐字稿为自动转写，人名、引述和时码以原声为准。</p>
        <ol aria-label="带时间点的逐字稿">{transcript}</ol>
      </section>
      <section class="reading" aria-labelledby="reading-heading">
        <h2 id="reading-heading">文字解读</h2>
        <p>{description}</p>
        {sections}
      </section>
      <section class="references" id="references" aria-labelledby="references-heading">
        <h2 id="references-heading">节目与核对资料</h2>
        <ul>
          <li><a href="{audio}">原节目 · 天禧 AI 原声（MP3）</a></li>
          <li><a href="#transcript">逐字稿 · 原声自动转写</a></li>
          {"".join(references)}
        </ul>
      </section>
    </main>
  </div>
</body>
</html>
"""


for episode in PROGRAMS:
    directory = DOCS / episode["id"]
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "index.html").write_text(page(episode, "../"), encoding="utf-8")

(DOCS / "index.html").write_text(page(PROGRAMS[0], "./"), encoding="utf-8")
