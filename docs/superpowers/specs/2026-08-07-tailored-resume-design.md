# Tailored / ATS-Optimized Resume Generation — Design Spec

**Date:** 2026-08-07
**Author:** Shobhit Jain (bjshobhit)
**Status:** Approved

## Problem

Job Radar currently sends plain-text Telegram alerts for new backend jobs. To
increase shortlisting odds, each matching job should get a resume tailored to
that job's description (ATS-optimized), delivered as a PDF via Telegram.

This mirrors the reference repo `AK16-ak/qa-radar` (a QA fork of the same base
project), adapted to a backend / Java-Python-Kotlin profile.

## User Profile

- Backend Software Engineer, just crossed **2 years** experience.
- Stack: Java, Spring Boot, Python, SQL, distributed systems.
- Targets high pay; Delhi NCR preferred, open to remote/global.
- **Highly sensitive to Telegram alert spam** — always seed silently after
  changes (`python main.py --seed`).

## Locked Design Decisions

1. **Inject-all keyword optimization** — port the friend's aggressive approach:
   inject ALL JD keywords into the resume skills to maximize ATS keyword score.
   Accepted the keyword-stuffing/honesty tradeoff.
2. **Real resume** — user's actual resume
   (`Shobhit_Jain_Backend_Resume.pdf`) is converted to `resume/base.yaml`.
3. **PDF per job** — delivered via Telegram `sendDocument` with a caption
   carrying the ATS score, matched keywords, and gaps.
4. **10 resumes/run cap** — protects Actions runtime and avoids spam.
5. **weasyprint + apt libs** in GitHub Actions (pango/cairo/gdk-pixbuf);
   keep the friend's `template.html` structure.

## Backend Adaptations vs. qa-radar

- **`ats/keyword_extractor.py`** — rewrite `KEYWORD_BANK` from QA/SDET
  (selenium/testng/cypress) to backend: langs (java/python/kotlin/go/scala),
  Spring/Spring Boot/Micronaut/Vert.x/Dropwizard, Kafka/RabbitMQ/gRPC/REST/
  GraphQL, SQL/NoSQL/Redis/Cassandra/Elasticsearch/PostgreSQL/MongoDB/Neo4j,
  AWS/GCP/Docker/K8s/Terraform, microservices/distributed systems/system
  design/CI-CD.
- **`ats/optimizer.py`** — port inject-all logic; rewrite `_categorize_keyword()`
  categories and `_optimize_summary()` template for backend wording
  ("Backend Engineer … scalable distributed systems, microservices,
  high-throughput APIs").
- **`ats/jd_fetcher.py`** — improvement over friend: **prefer `job.description`
  if non-empty**, only fetch over network when empty. The `Job` model already
  carries a `description` field (from prior YOE work), and the extra sources
  `amazon`/`netflix` have JS-heavy pages that page-scraping handles poorly.
- **`ats/scorer.py`, `ats/pdf_generator.py`** — port essentially unchanged.
- **`main.py`** — add `process_with_resume(selected, cfg, token, chat, dry)`,
  branch on `cfg["resume"]["enabled"]`. **PRESERVE the existing
  delivery-success seen-marking** (mark seen only if send succeeded — safer
  than the friend's unconditional marking).
- **`notify.py`** — add `format_job_with_ats(...)` and
  `send_telegram_document(...)` (sendDocument, caption ≤ 1024 chars).
- **`config.yaml`** — add `resume:` block: `enabled: true`,
  `experience_years: 2`, `max_target_years: 6`, `max_resumes_per_run: 10`.
- **`requirements.txt`** — add `jinja2>=3.1`, `weasyprint>=60.0`.
- **`.github/workflows/scan.yml`** — add apt-get step for weasyprint system deps.
- PDFs saved to `state/resumes/`.

## Per-Job Flow

```
for each selected (job, priority):
    jd_text = job.description if non-empty else fetch_job_description(job)
    exp_ok, exp_info = experience_matches(jd_text, my_years=2, max_target=6)
    if exp_ok and resumes_generated < max_resumes_per_run:
        jd_keywords = extract_keywords(jd_text)
        optimized   = optimize_resume(base, jd_keywords, job.title)   # inject-all
        score       = calculate_ats_score(resume_kw, jd_keywords, ...)
        pdf_ok      = generate_pdf(optimized, state/resumes/<file>.pdf)
        caption     = format_job_with_ats(job, priority, exp_info, score)
        send document (or text if pdf failed); resumes_generated += 1
    else:
        send plain text alert noting why (too junior/senior, or cap reached)
```

Seen-marking stays delivery-success–gated in `main()`.

## Tests

- `keyword_extractor` — backend bank matches Java/Spring/Kafka; word-boundary
  for short tokens (go, sql) avoids false positives.
- `jd_parser` — `extract_experience` / `experience_matches` at 2y.
- `scorer` — weighting + empty-JD default.
- `optimizer` — inject-all adds missing JD keywords; summary carries job title;
  reordering puts relevant skills first.
- `jd_fetcher` — description-preferred path: returns `job.description` without
  a network call when present.

## Non-Goals

- No LLM rewriting of bullets (deterministic template only).
- No change to source collection or the title/keyword filters.
