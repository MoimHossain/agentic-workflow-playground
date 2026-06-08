# 🛡️ Demo 1 — Compliance Co-Pilot

> **Audience:** Regulated-industry stakeholders
> **Duration:** ~5 minutes live
> **What it shows:** an agentic workflow that turns written banking policies
> into automated PR review, enforcing GDPR / PSD2 / internal controls on every
> change.

---

## What it is

A GitHub Agentic Workflow (`.github/workflows/compliance-copilot.md`) that
fires on every pull request. The agent:

1. Reads the PR diff.
2. Loads every markdown file under `policies/` — those files are the **source
   of truth** for what "compliant" means.
3. Maps each changed line to policy clauses (e.g. `DATA-CLS-03`, `CRYPTO-01`,
   `AUDIT-01`).
4. Posts **one** PR review comment with a findings table, severity, and
   GitHub-native `suggestion` blocks the author can click-to-apply.
5. Labels the PR `compliance:ok` / `compliance:review-needed` /
   `compliance:blocked` (and `needs-dpo-review` if personal data is involved).

The agent itself has **read-only** permissions on the repository. All write
actions are routed through the `safe-outputs` block (`add-comment`,
`add-labels`) — this is the security model `gh-aw` enforces.

---

## How it works (architecture)

```
PR opened/updated
       │
       ▼
┌──────────────────────────────────────┐
│ compliance-copilot.md (agentic wf)   │
│  - permissions: read-all             │
│  - tools: github (default)           │
│  - safe-outputs: add-comment, labels │
└──────────────────────────────────────┘
       │ (compiled by `gh aw compile`)
       ▼
compliance-copilot.lock.yml  ← actual GH Actions YAML
       │
       ▼
Copilot LLM in the runner
       │ reads
       ▼
 - PR diff  (get_pull_request_files)
 - policies/*.md  (get_file_contents)
       │ emits via safe-output channel
       ▼
PR review comment + labels
```

**Why this is interesting for a bank:**

- Policies live in Markdown, in Git → reviewable, versioned, signed off.
- No proprietary rule engine, no separate policy DSL.
- Update a policy → next PR is reviewed against the new rule. Zero rollout.
- Read-only agent + safe-outputs = auditable, least-privilege.

---

## Demo script (live, ~5 min)

### 0. Prep (do once, before the meeting)

```powershell
# from repo root
gh aw compile compliance-copilot
git add .github/workflows/compliance-copilot.* policies/ payments/
git commit -m "Add compliance-copilot demo scaffold"
git push
```

Confirm the workflow shows up:

```powershell
gh workflow list | Select-String compliance
```

Also create the demo labels once (the agent will gracefully skip any that
don't exist, but they look nicer when they do):

```powershell
gh label create compliance:ok            --color 0E8A16 --description "Compliance Co-Pilot: clean"
gh label create compliance:review-needed --color FBCA04 --description "Compliance Co-Pilot: review"
gh label create compliance:blocked       --color B60205 --description "Compliance Co-Pilot: blocked"
gh label create needs-dpo-review         --color 5319E7 --description "Data Protection Officer review"
```

### 1. Open the policies live (30 s)

Open `policies/DATA-CLASSIFICATION.md` in the IDE. Read clause **DATA-CLS-03**
out loud:

> "Account numbers MUST be masked in any log sink."

Frame it: *"This Markdown file is the policy. There is no other rulebook."*

### 2. Make a deliberately bad change (1 min)

Create a feature branch and break the rules on purpose:

```powershell
git checkout -b demo/violations
```

Edit `payments/charge.py` and replace the `charge` function with this
deliberately-broken version (copy/paste during the demo for drama):

```python
import hashlib, logging, requests
logger = logging.getLogger(__name__)

API_KEY = "sk_live_51H8aZk_NEVER_COMMIT_ME"  # CRYPTO-02 violation

def charge(customer, amount_cents):
    # DATA-CLS-03 violation: raw IBAN in log
    logger.info("charging %s iban=%s amount=%d", customer.id, customer.iban, amount_cents)

    # CRYPTO-01 violation: MD5 for an "idempotency token"
    key = hashlib.md5(f"{customer.iban}{amount_cents}".encode()).hexdigest()

    # DATA-CLS-04 violation: TLS verification disabled
    requests.post("https://psp.example.com/charge",
                  json={"iban": customer.iban, "amount": amount_cents, "key": API_KEY},
                  verify=False)

    # AUDIT-01 violation: no audit.emit()
    return key
```

Commit, push, open a PR:

```powershell
git add payments/charge.py
git commit -m "feat(payments): faster charge path"
git push -u origin demo/violations
gh pr create --title "Faster charge path" --body "Streamlined version for perf." --fill
```

### 3. Watch the agent work (2 min)

```powershell
gh pr view --web
# or:
gh run watch
```

Within ~60–90 s the PR gets:

- a single comment titled **"🛡️ Compliance Co-Pilot review"** with verdict
  **❌ Blocking violations**
- a findings table calling out `DATA-CLS-03`, `CRYPTO-01`, `CRYPTO-02`,
  `DATA-CLS-04`, `AUDIT-01`
- click-to-apply suggestion blocks for the ones with a single-line fix
- labels: `compliance:blocked`, `needs-dpo-review`

### 4. Apply the agent's fix (1 min)

Click **"Commit suggestion"** on the IBAN-masking finding. Push. The workflow
re-runs and the verdict downgrades from ❌ to ⚠️ (or ✅ if you apply them all).

### 5. Punchline (30 s)

> "The policy file is the law. The agent is the auditor. Both live in Git,
> both are reviewable, both are versioned. Your DPO can review a pull request
> against `policies/` the same way your engineers review code."

---

## Q&A cheat-sheet

| Question | Answer |
|---|---|
| Can the agent write code on its own? | No — it has `read-all` perms. Every visible action (comment, label) goes through `safe-outputs`, which are allow-listed in the workflow file. |
| Where does the policy come from? | Plain Markdown in `policies/`. Git is the system of record. |
| Which model? | Default is GitHub Copilot inside the runner. Swappable via `engine:` in the front-matter (Claude, Codex, …). |
| Cost control? | `timeout-minutes`, `engine.model: small`, and the fact that read-only + safe-outputs make a runaway agent impossible. |
| Audit trail? | Every run is a GitHub Actions run with full logs; every comment is attributable to the workflow's GitHub App identity. |

---

## Troubleshooting

- **Workflow didn't run on the PR** — check `gh aw status`, then
  `gh aw compile compliance-copilot` and push the regenerated `.lock.yml`.
- **Agent says "no policy corpus available"** — confirm `policies/*.md` is on
  the PR's base branch (the agent reads from the repo, not the PR diff alone).
- **Labels missing from the comment** — run the `gh label create` block above.
