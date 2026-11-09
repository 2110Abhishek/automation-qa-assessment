# PulseQA — Technical Interview Defense & Cheat Sheet
**Role:** Automation & QA Developer  
**Candidate:** Abhishek  
**Assessment Target:** RealWorld Web Application QA & n8n Workflow Orchestration  

---

## 🎯 1. Overview & Strategy for the 45-Minute Technical Call

The interviewers will evaluate three primary competencies:
1. **Critical Thinking in QA:** Can you prioritize high-risk vulnerabilities (security, data integrity, availability) over trivial visual bugs?
2. **System Architecture in n8n:** Do you understand DAG workflow design, memory data flow (`$json`), transformations, and resilience?
3. **Communication with Stakeholders:** Can you explain technical defects in clear business terms to product managers while providing concrete code fixes to software engineers?

---

## 💡 2. Top Likely Interview Questions & Model Answers

### Q1: "Why did you choose the RealWorld Conduit app, and what was your QA testing methodology?"
> **Model Answer:**
> *"I selected the RealWorld Conduit platform because it mirrors modern production architectures: a single-page application (SPA) communicating with a stateless REST API backend.*
>
> *Rather than just clicking around the UI, I adopted an **API-first, risk-weighted testing strategy**:*
> 1. *I first probed infrastructure availability via `curl` and discovered that the officially documented endpoints (`demo.realworld.io` and `api.realworld.io`) suffered an unmonitored production outage (S3 `404 NoSuchBucket` and Cloudflare `530 DNS Error 1016`).*
> 2. *I then tested core stateful user journeys (Sign-up $\rightarrow$ Login $\rightarrow$ Article Create $\rightarrow$ Edit $\rightarrow$ Delete $\rightarrow$ Logout).*
> 3. *Finally, I targeted edge cases and security boundaries: duplicate registration idempotency, single-character password boundaries, stored script tags in markdown, and slug mutation routing.*
>
> *This surfaced 6 distinct defects spanning infrastructure, access control, and data integrity."*

---

### Q2: "Can you explain your Root-Cause Analysis on Issue #1 (Duplicate Registration)?"
> **Model Answer:**
> *"Yes. When submitting an already registered email to `POST /api/users`, the API returned `HTTP 201 Created` and minted a valid JWT session for the existing user without verifying their password. This is a critical Account Takeover (ATO) vector.*
>
> *The root cause was twofold:*
> 1. *The database migration failed to define a `UNIQUE` index constraint on `users.email` and `users.username`.*
> 2. *The AI-generated controller used an unsafe ORM shorthand like `findOrCreate()` or `upsert()` without a preceding password verification check. When a collision occurred, it simply retrieved the existing record and signed a token.*
>
> *I proposed a 3-tier remediation:*
> - *Database tier: Add unique constraints (`ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);`).*
> - *Middleware tier: Add a Zod/Joi schema validation layer.*
> - *Controller tier: Implement an atomic existence check returning standard RealWorld `422 Unprocessable Entity` payloads before any hashing or persistence."*

---

### Q3: "In Task 2, why did you use the GitHub Search API and README API?"
> **Model Answer:**
> *"GitHub does not expose an official `/trending` REST endpoint. Web-scraping trending HTML is fragile because DOM class names change without notice.*
>
> *Using `GET /search/repositories?q=stars:>5000&sort=stars&order=desc` gives us reliable, versioned JSON with exact star counts, fork counts, and licensing metadata.*
>
> *For enrichment, I queried `GET /repos/{owner}/{repo}/readme` because it tested a real-world multi-step transformation: the endpoint returns Base64-encoded raw markdown. In my Code node, I allocated a Node.js `Buffer` to decode it, stripped markdown badges, links, and HTML tags with regex, and generated a clean 220-character summary for our morning brief."*

---

### Q4: "Why did you set the star threshold at 10,000 in the IF node?"
> **Model Answer:**
> *"In the open-source community, 10,000 stars represents a standard industry benchmark separating established ecosystem frameworks (like React, Vue, or popular utility libraries) from emerging tools.*
>
> *Setting the threshold at 10,000 creates a meaningful distinction between our **Spotlight Tier** (highlighted in Emerald Green with full README excerpts and ranking medals) and the **Standard Tier** (sky blue summary). In n8n, this threshold is an editable expression parameter, allowing operations teams to tune it easily."*

---

### Q5: "How do you ensure your n8n workflows never fail silently?"
> **Model Answer:**
> *"By default, unhandled 4xx or 5xx HTTP responses terminate workflow execution without notice. To prevent silent crashes:*
> 1. *I enabled `continueOnFail: true` on all HTTP Request nodes so failure payloads are captured as data.*
> 2. *I placed an **IF Status Verification Node** directly after the fetch to check for non-200 responses, rate-limits, or empty payloads.*
> 3. *If an error occurs, execution branches to a dedicated **Format API Error Alert** node that dispatches a high-priority red warning embed to Discord, detailing the failed endpoint, HTTP status code, and timestamp.*
> 4. *In production, I also configure n8n's global **Error Workflow** (`Error Trigger` node) to catch any unexpected execution exceptions."*

---

### Q6: "Why did you build the Uptime Sentinel (Bonus) with a 5-second wait buffer?"
> **Model Answer:**
> *"The biggest flaw of naive uptime monitors is **false-positive paging** caused by momentary packet loss, DNS jitter, or upstream load-balancer cycling.*
>
> *In the PulseQA Uptime Sentinel, when the primary ping detects a non-200 status code:*
> 1. *It does not immediately send a critical alert.*
> 2. *It enters a 5-second `Wait` buffer and fires a secondary confirmation probe.*
> 3. *If the second probe returns HTTP 200, it classifies the event as a **Self-Healed Transient Flap** and logs a minor notice.*
> 4. *Only if both probes fail consecutively does it confirm an outage and dispatch a critical `@here` incident alert with automated root-cause diagnostics (distinguishing Cloudflare 530 DNS failures from S3 404s or 500 server crashes)."*

---

### Q7: "How do you handle credentials and secrets in n8n?"
> **Model Answer:**
> *"No secrets or webhook tokens are ever committed in plaintext to workflow JSON files. We use two best practices:*
> 1. *In development and containerized environments, we reference environment variables using n8n expressions: `{{ $env.DISCORD_WEBHOOK_URL }}`.*
> 2. *In production, we store secrets in n8n's encrypted **Credentials Store** (AES-256 encrypted in the PostgreSQL/SQLite backend) and bind them via node credential references."*

