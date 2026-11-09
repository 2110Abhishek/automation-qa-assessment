# PulseQA — Technical Assessment Submission Summary
**Candidate:** Abhishek  
**Role Applied:** Automation & QA Developer  
**GitHub Repository:** Public Repository Link  
**Loom Walkthrough:** https://www.loom.com/share/pulseqa-automation-qa-abhishek  
**Target Application:** RealWorld Platform (Conduit)  

---

### 1. Task 1: Web App QA & Root-Cause Analysis
A systematic investigation of the RealWorld platform across registration, authentication, article publishing, inline editing, deletion, and boundary conditions surfaced **six critical-to-medium defects**:
- **Critical (ATO):** Submitting duplicate credentials to `POST /api/users` returns `201 Created` and mints an unauthenticated JWT session without verifying passwords.
- **Critical (Outage):** Documented production endpoints suffered unmonitored infrastructure abandonment (S3 `404 NoSuchBucket` on `demo.realworld.io`; Cloudflare `530 DNS Error 1016` on `api.realworld.io`).
- **High (Security):** Stored XSS vulnerability accepting raw `<script>` tags in article titles and markdown bodies without sanitization.
- **High (Validation):** Absence of password constraints (accepts 1-character passwords).
- **Medium (UX/SEO):** Article title updates regenerate slugs without HTTP 301 redirects, permanently breaking bookmarks and external links.
- **Medium (Session):** Tokens stored in unencrypted `localStorage` without server-side revocation on logout.

**Root-Cause Analysis (Issue #1):** Missing `UNIQUE` index constraints in the database schema combined with an unsafe ORM `findOrCreate()` controller pattern that signs session tokens for existing entities without password verification. Remediated via relational unique constraints, Zod schema validation middleware, and atomic existence checks returning HTTP 422.  
*Full report: [`Task1_QA_Report_Abhishek.pdf`](./Task1_QA_Report_Abhishek.pdf).*

---

### 2. Task 2: n8n API Integration Workflow
Built an automated intelligence briefing workflow in n8n ([`Task2/Task2_Workflow_Abhishek.json`](./Task2/Task2_Workflow_Abhishek.json)):
- **Primary Request:** Queries GitHub REST API for trending repositories worldwide.
- **Transformation:** JavaScript Code node filters archived projects, sorts descending by stars, normalizes attributes, and selects the top 5.
- **Secondary Enrichment:** Calls `GET /repos/{owner}/{repo}/readme`, decodes the Base64 buffer, strips markdown/HTML badges, and extracts a 220-character summary.
- **Conditional Branching (IF):** Repositories with $\ge 10,000$ stars route to a highlighted **Spotlight Tier** with an Emerald Green (`#2ECC71`) Discord Embed, medal rankings, and documentation excerpts.
- **Zero Silent Failures:** `continueOnFail: true` on all HTTP nodes paired with an IF validation gate routes API downtime or rate-limits to an emergency fallback alert branch on Discord.

---

### 3. Bonus Task: Continuous Uptime Sentinel
Built an automated synthetic monitoring workflow ([`Bonus/Bonus_UptimeMonitor_Abhishek.json`](./Bonus/Bonus_UptimeMonitor_Abhishek.json)):
- **5-Minute Heartbeat:** Pings target application API and tracks round-trip latency in milliseconds.
- **Anti-Flap Retry Buffer:** If the primary check fails, pauses 5 seconds and issues a confirmation probe. Transient packet drops log a self-healing notice; confirmed outages dispatch an immediate `@here` Discord alert with root-cause diagnostics (e.g. Cloudflare 530 vs S3 404 vs 500) and an emergency checklist.
