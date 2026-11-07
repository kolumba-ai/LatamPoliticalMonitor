# Latam Political Monitor

Monitoring page for TikTok content by and about Morena politicians (Mexico), built on the
[Oriane](https://connect.oriane.xyz) search API. Videos are grouped into three categories
(Dirigentes de Partido, Presidentes Municipales, Candidatos Presidenciables), ranked by views,
and scored on two indices:

- **Índice de Presentación**: how each video portrays the politician (+1 / 0 / −1, shown as −100 to +100).
  Positive from the politician's own account = official communication; positive from other
  accounts = possible pro-Morena propaganda; negative = possible opposition propaganda.
- **Índice de Feedback**: stance of human commenters toward the politician,
  (for − against) ÷ human comments, −100 to +100. Likely bot comments are excluded from the
  score and counted separately.

The output is a single self-contained page, `morena_monitor.html`, with the data embedded.

## Files

| File | What it is |
|---|---|
| `fetch_morena.py` | Politician list and categories; fetches the last N days of TikTok videos from Oriane → `morena_data.json` |
| `fetch_comments.py` | Fetches Oriane's popular comments (max 15 per video) → `comments.json` |
| `perception.json` | Presentation labels per video–politician pair (`relevant=false` pairs are dropped) |
| `comment_labels.json` | Per-comment stance (`pos`/`neg`/`neu`) and bot label (`human`/`bot`/`unsure`) |
| `monitor_template.html` | Page template (HTML/CSS/JS) |
| `build_monitor.py` | Merges data and labels into the template → `morena_monitor.html` |
| `top10_mx_politicians_tiktok.csv` | Earlier one-off export: top 10 videos by Mexican politicians, Oct 30 – Nov 6, 2026 |

## Refreshing the data

```bash
export ORIANE_API_KEY=...        # never commit the key
python3 fetch_morena.py 30       # videos from the last 30 days
python3 fetch_comments.py        # popular comments for those videos
python3 build_monitor.py         # rebuild morena_monitor.html
```

New videos and comments have no labels until they are classified (presentation labels and
comment stance/bot labels were produced with AI models and reviewed by sampling). Unlabeled
videos show as neutral; unlabeled comments are not counted.

## Method notes and limits

- Coverage depends on which TikTok accounts Oriane has indexed; several politicians have no
  indexed account and appear only through mentions (caption, transcript, on-screen text or hashtags).
- Oriane returns at most 15 popular (most-liked) comments per video, not the full comment section.
- A comment is labeled a likely bot only with behavioral evidence (auto-generated handle, or the
  same generic text posted on 3+ videos); generic one-off comments are `unsure` and count as human.
- The politician classification reflects positions as of November 2026 and should be reviewed.
- `comments.json` and `comment_labels.json` contain TikTok users' public handles and comments;
  keep this repository private.
