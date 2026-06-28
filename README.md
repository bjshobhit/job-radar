# Job Radar

Get a Telegram alert within ~20 minutes of a relevant **backend** job going live —
from a hand-picked **watchlist** of companies (polled via their ATS: Greenhouse / Lever /
Ashby) **plus** broad **discovery** across free job APIs (Adzuna + Remotive). Runs free,
24/7, on GitHub Actions. No server, no cost.

## How it works

Every 20 minutes a GitHub Action runs `main.py`, which:
1. Fetches jobs from each watchlist company's ATS + the discovery APIs.
2. Filters by your keyword/location rules in `config.yaml`.
3. Drops anything already alerted (`state/seen.json`).
4. Sends new matches to your Telegram, then commits the updated seen-list.

## One-time setup

### 1. Create a Telegram bot
- Open Telegram, message **@BotFather**, send `/newbot`, follow prompts.
- Copy the **bot token** it gives you → this is `TELEGRAM_TOKEN`.
- Send any message to your new bot (so it can DM you).
- Open `https://api.telegram.org/bot<TELEGRAM_TOKEN>/getUpdates` in a browser and copy
  the `"chat":{"id":...}` number → this is `TELEGRAM_CHAT_ID`.

### 2. (Optional) Adzuna keys for broad discovery
- Sign up free at https://developer.adzuna.com → create an app.
- Copy **App ID** → `ADZUNA_APP_ID`, **App Key** → `ADZUNA_APP_KEY`.
- If you skip this, discovery still runs Remotive (remote jobs); only Adzuna is skipped.

### 3. Push to a PUBLIC GitHub repo
Public repos get **unlimited free Actions minutes**. The repo holds only code +
your company list — **never** secrets.

```bash
cd job-radar
git init && git add -A && git commit -m "init job-radar"
gh repo create job-radar --public --source=. --push    # or create on github.com and push
```

### 4. Add secrets
Repo → **Settings → Secrets and variables → Actions → New repository secret**. Add:
`TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`, and optionally `ADZUNA_APP_ID`, `ADZUNA_APP_KEY`.

### 5. Enable + test
- Repo → **Actions** tab → enable workflows.
- Open the **scan** workflow → **Run workflow** to trigger a manual run.
- You should get a Telegram message if any new matching jobs exist.

### 6. (Recommended) Seed first, to avoid a flood
The very first run would otherwise alert *every* currently-open matching job (hundreds).
Run the seed once to mark all current jobs as "already seen" — then you only ever get
**newly posted** jobs:

```bash
python main.py --seed     # locally, after pip install -r requirements.txt
git add state/seen.json && git commit -m "seed seen state" && git push
```

(Or just let the first scheduled run happen — alerts are split into Telegram-safe chunks
either way; seeding simply spares you the initial dump.)


## Customizing

Everything is in **`config.yaml`** — no code changes needed:
- `watchlist`: add companies under `greenhouse` / `lever` / `ashby`. Find a company's ATS
  by visiting its careers page and checking the URL (`boards.greenhouse.io/<slug>`,
  `jobs.lever.co/<slug>`, `jobs.ashbyhq.com/<slug>`).
- `include_keywords` / `exclude_keywords`: tune which titles match. Matching is
  case-insensitive and word-boundary aware (`java` does not match `javascript`).
- `priority_locations`: locations that get a ⭐ in alerts (NCR + remote by default).
- `strict_location: true`: only alert for priority locations.
- `discovery.enabled: false`: turn off broad discovery, keep only the watchlist.

## Run locally

```bash
pip install -r requirements.txt
python main.py --dry-run          # prints matches instead of sending Telegram
python main.py --seed             # mark all current jobs seen, no alerts (first-time)
python -m pytest -q               # run the test suite
```

> **Note on salary:** job postings almost never list salary, so the ≥18 LPA target can't
> be filtered directly. Filtering uses role/seniority keywords as a proxy; when a source
> exposes salary (Adzuna sometimes), it's shown in the alert.
