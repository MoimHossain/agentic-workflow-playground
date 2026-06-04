# 🕰️ Demo 2 — Incident Time-Machine

> **Audience:** ING / SRE / platform-engineering stakeholders
> **Duration:** ~4 minutes live
> **What it shows:** an agentic workflow that turns an alert into a draft RCA
> issue + a draft revert PR in under two minutes — chaining observability,
> reasoning, and remediation in a single GitHub-native workflow.

---

## What it is

A GitHub Agentic Workflow (`.github/workflows/incident-time-machine.md`) that
fires on:

- `workflow_dispatch` — a human pastes the alert and clicks Run, or
- `repository_dispatch` (`event_type: incident`) — an alerting system
  (PagerDuty, Grafana, Splunk) posts the alert via the GitHub API.

The agent then:

1. Lists merged PRs and commits in the last *N* hours.
2. Reads the diffs of the top 5 most suspicious changes.
3. Correlates them with the alert text (service path, keywords, timing).
4. Picks a single most-likely culprit with an explicit confidence level.
5. Opens an **RCA issue** with a Mermaid timeline, suspect table, and rollback
   command.
6. Opens a **draft revert PR** linked to the issue (only if confidence ≥ medium).

---

## How it works (architecture)

```
 Alert  ──repository_dispatch──▶  ┌─────────────────────────────┐
 (human or PagerDuty)             │ incident-time-machine.md    │
                                  │  - permissions: read-all    │
                                  │  - safe-outputs:            │
                                  │      create-issue           │
                                  │      create-pull-request    │
                                  └─────────────────────────────┘
                                              │
                                              ▼
                                  ┌─────────────────────────────┐
                                  │ Agent reasoning loop:        │
                                  │  • list_pull_requests        │
                                  │  • list_commits              │
                                  │  • get_pull_request_files    │
                                  │  • search_issues             │
                                  └─────────────────────────────┘
                                              │
                            ┌─────────────────┴─────────────────┐
                            ▼                                   ▼
                  RCA issue (with Mermaid          Draft revert PR (linked
                   timeline + suspects)             back to the RCA issue)
```

**Why this is interesting for a bank / SRE org:**

- Pager → PR in ~90 s, with a written paper trail your CISO will accept.
- Always a **draft** revert — humans stay in the loop.
- The same workflow works for prod (`repository_dispatch` from PagerDuty) and
  for game-days (`workflow_dispatch` from a browser).
- No infra: just GitHub Actions + Copilot.

---

## Demo script (live, ~4 min)

### 0. Prep (do once, before the meeting)

```powershell
gh aw compile incident-time-machine
git add .github/workflows/incident-time-machine.*
git commit -m "Add incident-time-machine demo scaffold"
git push
```

Create the demo labels:

```powershell
gh label create incident  --color B60205 --description "Production incident"
gh label create rca       --color 5319E7 --description "Root-cause analysis"
gh label create revert    --color FBCA04 --description "Auto-generated revert PR"
gh label create automated --color C5DEF5 --description "Created by an agent"
```

### 1. Plant the "bad" change (1 min, *before* the demo starts)

Open a regular PR that looks innocuous and merge it to `main`. This becomes
the agent's culprit. Example:

```powershell
git checkout main; git pull
git checkout -b chore/retry-bump
"# bumped retry budget from 3 to 30 (this is the planted culprit)" |
  Add-Content payments/charge.py
git commit -am "perf(payments): bump retry budget to 30"
gh pr create --fill --title "perf(payments): bump retry budget to 30"
gh pr merge --squash --auto
```

Also merge **one** unrelated PR (a docs change) so the agent has to *choose*
between candidates and can't just pick the only PR in the window.

### 2. Fire the alert (30 s, live)

Two ways to do this — pick one based on audience.

**Option A — humans-in-the-loop, from the GitHub UI:**

1. Go to **Actions → Incident Time-Machine → Run workflow**.
2. Paste this alert text:

   ```
   payment-api 5xx error rate >5% sustained 3m at 14:02 UTC; p99 latency 4.8s
   ```

3. Service: `payments`
4. Lookback hours: `48`
5. Click **Run workflow**.

**Option B — simulate the PagerDuty integration from the CLI:**

```powershell
gh api repos/:owner/:repo/dispatches `
  -f event_type=incident `
  -f client_payload[alert]="payment-api 5xx error rate >5% at 14:02 UTC" `
  -f client_payload[service]="payments" `
  -f client_payload[lookback_hours]="48"
```

### 3. Watch the agent work (2 min)

```powershell
gh run watch
```

Within ~60–120 s you'll see:

- A new **issue** titled `[INCIDENT] payment-api 5xx error rate spike` with:
  - the alert quoted verbatim
  - hypothesis: PR #<N> "perf(payments): bump retry budget to 30" — confidence
    **high**
  - a Mermaid `timeline` diagram of the last 48 h
  - a suspects table ranked by suspicion
- A **draft pull request** titled `[revert] perf(payments): bump retry budget`
  that:
  - links back to the incident issue
  - is marked **draft** so it can't be merged accidentally
  - includes the literal `git revert` command in the body

### 4. The reveal (30 s)

> "From a one-line alert to a written RCA hypothesis and a draft remediation
> PR — in the time it takes the on-call to find their laptop. The on-call's
> job becomes *judging* the agent's draft, not assembling it from scratch."

---

## Variations you can show if there's time

- **No-culprit path:** dispatch with an alert for a service that has had no
  recent changes (`service: marketing-site`). The agent should refuse to open
  a revert PR and instead write a "no automated revert proposed" section.
- **Game-day:** plant 3 plausible culprits and watch the agent rank them.
- **PagerDuty wiring:** show the 6-line PagerDuty webhook → GitHub
  `repository_dispatch` mapping. (Optional slide — not required to run live.)

---

## Q&A cheat-sheet

| Question | Answer |
|---|---|
| Could it auto-merge the revert? | Technically yes (`draft: false` + auto-merge). We deliberately keep it `draft: true` because reverts in a regulated org need human sign-off. |
| What if the agent picks the wrong commit? | The PR is a draft — humans close it. The RCA issue still has the full suspect list for re-triage. |
| Can it look at logs / metrics, not just Git? | Yes — add an MCP server for your observability backend (Grafana, Splunk, Azure Monitor) under `tools:` and the agent will use it. |
| Cost? | One run per incident. With `engine.model: small` it costs cents. |
| Audit trail? | Full GitHub Actions run log + the issue + the PR are all permanent artifacts. |

---

## Troubleshooting

- **Workflow doesn't appear under "Run workflow"** — `gh aw compile
  incident-time-machine` then push the regenerated `.lock.yml` to `main`
  (workflow_dispatch only appears for workflows that live on the default
  branch).
- **Agent posts `noop`** — the lookback window had no merged PRs. Lower the
  lookback, or merge a throwaway PR to give it something to chew on.
- **Revert PR not created** — the agent's confidence was below `medium`. That
  is the intended guardrail; check the RCA issue for the explanation.
