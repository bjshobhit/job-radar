# India-or-Remote Location Filter + Company Expansion — Design Spec

**Date:** 2026-08-07
**Author:** Shobhit Jain (bjshobhit)
**Status:** Approved

## Problem

Two gaps in Job Radar today:

1. **Location is not filtered.** The tool is NCR-centric only in the sense of a
   `priority_locations` star; `strict_location: false` means jobs from *any*
   country pass. The user wants alerts ONLY for jobs that are **anywhere in
   India** OR **remote and India-eligible**. US-only / EMEA-only / other-country
   roles must be dropped.
2. **Too few companies.** The watchlist covers big/known names but misses many
   high-paying Indian startups and global seed/Series-A companies, and the four
   supported ATSes (greenhouse/lever/ashby/smartrecruiters) can't reach big-tech
   career sites (Google/Microsoft/Uber/Apple/Meta) that publish no-key JSON.

The user is **highly sensitive to Telegram alert spam** — after any change,
always seed silently (`python main.py --seed`) so future runs only alert on
genuinely new postings. Zero alerts must be sent during rollout.

## Locked Design Decisions

1. **Scope = India + India-eligible remote only.** Drop region-locked remote
   (US-only, EMEA-only, UK-only, Canada-only, LATAM-only, etc.).
2. **Unknown location is KEPT.** Blank / vague / bare-"Remote"-with-no-region
   jobs pass, tagged `📍 unverified` (user manually checks). Do not silently drop
   — losing a real India job is worse than an occasional false positive.
3. **Company growth = curated high-pay slugs + new big-tech ATS adapters.**
4. **Big-tech adapters:** Microsoft, Google, Uber use reliable public no-key
   JSON APIs (first class). Apple, Meta are **best-effort** — flaky/undocumented
   APIs, must auto-skip on failure (already handled by `safe_fetch` returning
   `[]` on any exception).
5. **All new companies flow through the SAME filters** — India-or-remote +
   title keyword include/exclude + YOE ceiling. No bypass.

## Part A — Location Filter

### New module `location.py`

`classify_location(job, cfg) -> str` returns one of five classes by scanning
`job.location` (and, as a weak fallback, `job.description`) case-insensitively:

| Class | Meaning | Action |
|---|---|---|
| `INDIA` | contains an India city/token (bengaluru, bangalore, mumbai, pune, hyderabad, chennai, gurugram, gurgaon, noida, delhi, ncr, kolkata, ahmedabad, jaipur, "india", etc.) | KEEP, ⭐ |
| `REMOTE_ELIGIBLE` | has a remote token AND (an India token OR a global token like "worldwide"/"anywhere"/"global") | KEEP, ⭐ |
| `REMOTE_REGION_LOCKED` | has a remote token but locked to a blocked region (us/usa/united states/eu/emea/uk/canada/latam/apac-excl-india…) with NO India/global token | **DROP** |
| `OTHER_COUNTRY` | non-remote and clearly another country (a blocked-region token present, no India token) | **DROP** |
| `UNKNOWN` | empty, vague, or bare "Remote" with no region signal | KEEP, tag `📍 unverified` |

Resolution order (first match wins): INDIA → REMOTE_ELIGIBLE →
REMOTE_REGION_LOCKED → OTHER_COUNTRY → UNKNOWN. India always wins over a blocked
region when both appear (e.g. "Remote - India/US" ⇒ REMOTE_ELIGIBLE, kept).

`location_ok(job, cfg) -> bool` = class not in {`REMOTE_REGION_LOCKED`,
`OTHER_COUNTRY`}. Helper `is_india_star(class)` = class in {`INDIA`,
`REMOTE_ELIGIBLE`} for the ⭐; `UNKNOWN` gets the `📍 unverified` tag instead.

### Config: new `location:` block

```yaml
location:
  mode: india_or_remote        # only supported mode today; explicit for clarity
  india_tokens: [india, bengaluru, bangalore, mumbai, pune, hyderabad,
                 chennai, gurugram, gurgaon, noida, delhi, ncr, kolkata,
                 ahmedabad, jaipur, indore, chandigarh, ...]
  remote_tokens: [remote, work from home, wfh, anywhere]
  global_tokens: [worldwide, global, anywhere]
  blocked_regions: [united states, usa, u.s., us-only, emea, europe, uk,
                    united kingdom, canada, latam, apac, singapore, dubai,
                    germany, ...]
```

- Retire `priority_locations` and `strict_location`. Their NCR/remote intent is
  folded into `india_tokens` + `remote_tokens`. `is_priority()` is replaced by
  the location class (⭐ for INDIA/REMOTE_ELIGIBLE).
- Lists are user-editable; no code change needed to tune scope.

### Wiring

- **`filters.py`**: `matches()` adds `if not location_ok(job, cfg): return False`
  after the keyword + YOE checks. Keep `is_priority` as a thin wrapper (or
  replace call sites) — see pipeline note.
- **`main.py` `select_new()`**: instead of `(j, is_priority(j, cfg))`, carry the
  location class so notify can distinguish ⭐ vs `📍 unverified`. Simplest
  backward-compatible change: keep the `(Job, bool)` tuple where
  `bool = is_india_star(class)`, and set `job` tagging for UNKNOWN via a small
  marker. **Decision:** carry the class label by returning
  `(job, star_bool)` AND letting `notify` recompute the `📍 unverified` tag from
  `classify_location` — avoids widening the tuple and touching the resume
  pipeline signature. `classify_location` is cheap/pure.
- **`notify.py`**: `format_job` / `format_job_with_ats` prepend `📍 unverified`
  when the job classifies as UNKNOWN (star already handled by the bool).

### Tests (`tests/test_location.py`)

- INDIA tokens (each major city) ⇒ INDIA, kept, star.
- "Remote - India" / "Remote (Worldwide)" ⇒ REMOTE_ELIGIBLE, kept, star.
- "Remote - US" / "San Francisco, CA" / "London, UK" ⇒ dropped.
- "Remote - India/US" ⇒ REMOTE_ELIGIBLE (India wins), kept.
- "" / "Remote" (bare) / "Multiple locations" ⇒ UNKNOWN, kept, unverified tag.
- `location_ok` returns False only for the two DROP classes.
- Update `tests/test_filters.py`: remove `strict_location`/`priority_locations`
  cases, add a `location_ok` integration case in `matches()`.

## Part B — Company Expansion

### B1. Big-tech ATS adapters (`sources/`)

Follow the `amazon.py`/`netflix.py` pattern: a pure `parse_X(data)` builder +
`fetch(...)` wrapping `parse_X(http_get_json(url, params))` in
`safe_fetch("name", lambda: ...)`. `Job.location` is set from each API's field
so the Part-A filter applies uniformly.

| Adapter | Endpoint (no key) | Tier |
|---|---|---|
| `microsoft.py` | `gcsservices.careers.microsoft.com/search/api/v1/search` (JSON) | first-class |
| `google.py` | `careers.google.com/api/v3/search/` (JSON) | first-class |
| `uber.py` | `uber.com/api/loadSearchJobsAsync` (POST JSON) | first-class |
| `apple.py` | jobs.apple.com search JSON | best-effort |
| `meta.py` | metacareers.com GraphQL/JSON | best-effort |

- Each supports an India/remote-biased query param where the API allows
  (narrows the flood; Part-A still filters regardless).
- Wire into `collect()` under `discovery` with per-source toggles + query lists,
  mirroring the existing `amazon`/`netflix` toggles.
- Apple/Meta failures are silent (`safe_fetch` ⇒ `[]`), so a broken endpoint
  never breaks a run.

### B2. Curated high-pay slugs (config watchlist)

Add ~40–60 slugs across greenhouse/lever/ashby. Candidates:

- **Indian:** razorpay, browserstack, hasura, chargebee, freshworks, sprinklr,
  spinny, upstox, angelone, delhivery, dream11, sharechat, urbancompany,
  zerodha, groyyo, mpl, physicswallah, jupiter, slice, m2p, plum, khatabook,
  cars24, licious, purplle, bharatpe, whatfix, gupshup, innovaccer …
- **Global (seed/A, high pay, India-friendly or remote):** plaid, rippling,
  deel, mercury, retool, sourcegraph, supabase, replit, huggingface, groq,
  glean, together, fal, cartesia, hadrius, sardine, warp, trunk, turing …

**Validate every slug before commit** — fetch each (greenhouse:
`boards-api.greenhouse.io/v1/boards/<slug>/jobs`, etc.). Dead slugs return 0
jobs (harmless) but are removed to keep config clean. Only verified slugs land.

### B3. Filtering guarantee

Every job from every new source passes through `matches()` (keyword + YOE +
`location_ok`), so the India-or-remote scope and title filters apply globally.
No new source gets special treatment.

## Rollout (spam-safe)

1. Implement + unit-test everything; full suite green (currently 68 tests pass).
2. `python main.py --dry-run` to eyeball classification + new-source output.
3. `python main.py --seed` — marks all current matches seen, **sends ZERO
   alerts**. Confirm log says seeded N, no Telegram calls.
4. Only then commit + push. Expect origin/main ahead (CI `chore: update seen
   state`); rebase with `state/seen.json` union on conflict (JSON list of
   16-hex-char id strings).

## Non-Goals

- No geocoding / external location API — token matching only (fast, no-key).
- No change to the resume pipeline logic or its signatures.
- No new ATS *engines* beyond the five direct big-tech adapters (still
  greenhouse/lever/ashby/smartrecruiters for the watchlist).
- `.DS_Store` stays untracked, never committed.
