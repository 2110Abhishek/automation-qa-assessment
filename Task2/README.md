# Task 2 — n8n API Integration Workflow
**Workflow Name:** `Task2_Workflow_Abhishek.json`  
**Author:** Abhishek Choudhari | Automation & QA Developer  
**System:** PulseQA Platform  
**Target Automation:** GitHub Intelligence Digest & Spotlight Dispatcher  

---

## 1. Architectural Overview & APIs Selected

| Component | Target Endpoint / Technology | Selection Rationale |
| :--- | :--- | :--- |
| **Primary Ingestion** | GitHub REST API v3:<br>`GET https://api.github.com/search/repositories` | Queries public software repositories globally sorted by `stargazers_count` with high availability, standardized pagination, and comprehensive repository metrics. |
| **Secondary Enrichment** | GitHub REST API v3:<br>`GET https://api.github.com/repos/{owner}/{repo}/readme` | Extracts official documentation metadata for the #1 ranked project, returning Base64-encoded raw markdown content for deep context extraction. |
| **Notification Channel** | Discord Webhook:<br>`POST https://discord.com/api/webhooks/...` | Delivers structured, color-coded Discord Embeds with medal icons, clickable hyperlinks, and formatted markdown blocks without requiring complex bot authentication. |
| **Orchestration Engine** | n8n Workflow Automation Engine | Provides visual DAG orchestration, node-level error branching, credential abstraction, and programmatic JavaScript execution. |

---

## 2. Triggering Architecture
1. **Schedule Trigger (`Schedule Trigger (Hourly)`):** Executes periodically every 1 hour to supply automated daily briefings.
2. **On-Demand Webhook (`Webhook Trigger (On-Demand)`):** Exposes an HTTP webhook endpoint (`/webhook/github-digest-trigger`) allowing developers and QA engineers to trigger immediate test executions using `curl` or Postman.

---

## 3. Data Transformation Logic (JavaScript Code Nodes)

### A. Repository Filtering & Top 5 Selection (`node-filter-top5`)
The initial API response returns a raw `items` collection containing up to 10 repositories. The JavaScript transformation node executes the following pipeline:
1. **Sanitization:** Filters out archived, disabled, or deprecated repositories (`!r.archived && !r.disabled`).
2. **Deterministic Sorting:** Enforces strict descending sort order by `stargazers_count` to guarantee rank accuracy.
3. **Data Normalization:** Extracts clean attributes (`rank`, `name`, `fullName`, `owner`, `stars`, `forks`, `language`, `url`, `description`, `updatedAt`).
4. **Target Isolation:** Automatically isolates the #1 ranked repository (`top5[0]`) and outputs `enrichOwner` and `enrichRepo` keys to drive the downstream secondary API request.

### B. Base64 README Decoding & Excerpt Synthesis (`node-decode-readme`)
GitHub's README endpoint delivers documentation encoded in Base64 with carriage returns. The processor:
1. Allocates a NodeJS `Buffer.from(content, 'base64')` to decode the UTF-8 text.
2. Applies regular expression filters to strip badge images (`![badge](...)`), markdown hyperlinks (`[title](url)` $\rightarrow$ `title`), headings (`#`), code fences (```...```), and HTML markup.
3. Truncates the cleaned text to a readable 220-character executive excerpt, appending an ellipsis (`...`) for seamless presentation in the notification digest.

---

## 4. Conditional Branching Strategy (IF Node)
The **Evaluate Star Threshold** IF node examines the #1 ranked project's star count against a configurable threshold:
- **Threshold Rule:** `{{ $json.topRepo.stars >= 10000 }}`
- **TRUE Branch (Spotlight Tier):** Formats an Emerald Green (`#2ECC71`) Discord Embed featuring fire icons (`🔥`), gold medals (`🥇`), and an expanded `🌟 #1 REPOSITORY SPOTLIGHT` section highlighting the decoded README documentation.
- **FALSE Branch (Standard Tier):** Formats a Sky Blue (`#3498DB`) standard summary embed suitable for regular traffic volumes.

---

## 5. Error Handling & Silent Failure Prevention
To satisfy the strict requirement that **the workflow must NOT crash silently**, PulseQA incorporates multi-tier error resilience:
1. **Continue On Fail Configuration:** Both HTTP Request nodes (`Fetch Popular Repositories` and `Fetch Top Repo README`) have `continueOnFail: true` enabled. Network timeouts, rate-limit 403s, or upstream 5xx errors do not terminate the execution DAG.
2. **Validation Gate (`Check GitHub API Status`):** An IF node immediately follows the initial fetch, verifying that `items` is an array and no `error` object exists.
3. **Dedicated Alert Fallback (`Format API Error Alert` $\rightarrow$ `Post Error Alert to Discord`):** If GitHub returns an error or empty payload, the execution routes to an emergency branch that constructs a Red (`#E74C3C`) warning embed specifying the endpoint, error details, and timestamp, instantly alerting the operations team on Discord.
4. **Enrichment Fallback:** If the #1 repository lacks a README (HTTP 404), the decoding node safely assigns a fallback string (`"No README documentation available"`) allowing the digest to complete successfully without interruption.

---

## 6. Credential & Secret Management
No API secrets, personal access tokens, or sensitive webhook URLs are hard-coded into the JSON definition. 
- The Discord Webhook URL is dynamically evaluated using n8n expressions:
  `={{ $env.DISCORD_WEBHOOK_URL || 'https://discord.com/api/webhooks/YOUR_WEBHOOK_URL' }}`
- In production, credentials should be configured within **n8n Settings > Credentials > Header Auth / Custom Webhook** and referenced securely across environments.

