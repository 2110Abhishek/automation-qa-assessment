# PulseQA — Loom Video Walkthrough & Presentation Script
**Candidate:** Abhishek  
**Target Role:** Automation & QA Developer  
**Project:** PulseQA – Web Application Quality & Automation Monitor  
**Duration:** ~4–5 minutes  

---

## ⏱️ Video Timeline & Visual Cue Guide

| Timecode | Presentation Section | Screen to Show |
| :--- | :--- | :--- |
| **0:00 – 0:35** | **Executive Introduction** | GitHub Repo root (`README.md`) & Project Architecture Diagram |
| **0:35 – 1:50** | **Task 1: QA Investigation & Root Cause** | `Task1_QA_Report_Abhishek.pdf` (Bug Table + Code Snippet) |
| **1:50 – 3:15** | **Task 2: n8n API Integration Workflow** | n8n Canvas (`workflow.png`) & Execution View (`execution.png`) |
| **3:15 – 4:15** | **Bonus Task: Automated Uptime Monitor** | Uptime Canvas (`uptime-workflow.png`) & Discord Alert Mock |
| **4:15 – 4:45** | **Conclusion & Decision Defense** | Repo structure & Loom sign-off |

---

## 🎙️ Spoken Script

### 1. Introduction (0:00 – 0:35)
> *"Hi everyone, my name is Abhishek, and this is my technical walkthrough for the Automation & QA Developer assessment. Today, I'm presenting **PulseQA**, a comprehensive quality assurance and intelligent automation platform designed to keep AI-built web applications running smoothly, monitor their health, and orchestrate automated intelligence digests.*
>
> *I’ll walk you through three core deliverables: first, my QA and security investigation of the RealWorld web application with an in-depth Root Cause Analysis; second, my multi-step n8n API integration workflow with error handling and Discord dispatch; and third, the bonus continuous uptime monitoring workflow with retry logic."*

---

### 2. Task 1: Web App QA & Root Cause Analysis (0:35 – 1:50)
> *(Scroll to Section 3 of `Task1_QA_Report_Abhishek.pdf`)*
>
> *"For Task 1, I investigated the RealWorld Conduit platform across all primary user journeys: registration, authentication, article creation, editing, deletion, and boundary testing.*
>
> *I identified six reproducible defects across infrastructure, security, and data integrity:*
> 1. *First, the official documented endpoints (`demo.realworld.io` and `api.realworld.io`) suffered an unmonitored production outage—specifically, an AWS S3 `404 NoSuchBucket` error and a Cloudflare `530 DNS Error 1016`.*
> 2. *Second, a high-severity stored Cross-Site Scripting (XSS) vulnerability, where the backend accepts unescaped raw HTML and JavaScript tags in article titles and markdown bodies.*
> 3. *Third, zero password validation, allowing accounts with single-character passwords.*
> 4. *Fourth, SEO and bookmark link rot, where editing an article title mutates its slug without setting up an HTTP 301 redirect or alias.*
> 5. *Fifth, insecure JWT storage in `localStorage` without server-side revocation on logout.*
>
> *(Scroll to Section 4 of PDF)*
>
> *For my deep-dive Root-Cause Analysis, I focused on **Issue #1: Silent Duplicate Registration and Unauthenticated Token Minting**. When submitting duplicate credentials to `POST /api/users`, the API unexpectedly returns `HTTP 201 Created` and mints a valid JWT token instead of throwing a `422 Unprocessable Entity`.*
>
> *The root cause is twofold: the database schema lacked a `UNIQUE` constraint index on the email column, and the controller utilized an unsafe `findOrCreate()` ORM call without checking password validity before issuing a session. In the report, I’ve provided the remediation code: adding relational database constraints, implementing a Zod validation middleware schema, and refactoring the controller to use an atomic pre-existence check."*

---

### 3. Task 2: n8n API Integration Workflow (1:50 – 3:15)
> *(Switch screen to `Task2/screenshots/workflow.png` or live n8n canvas)*
>
> *"Moving to Task 2: we built an automated morning intelligence brief in n8n. Let me walk you through the node execution pipeline:*
>
> 1. *It triggers on an hourly schedule or via an on-demand webhook for developer testing.*
> 2. *The primary HTTP Request queries the GitHub REST API for trending repositories globally, sorted by stars.*
> 3. *Crucially, we enabled **'Continue On Fail'** on all HTTP nodes. Directly after the fetch, an IF node verifies whether `items` exists. If GitHub is rate-limited or down, execution routes to a dedicated fallback branch that posts an incident alert to Discord, ensuring the workflow **never crashes silently**.*
> 4. *In the happy path, a custom JavaScript code node filters out archived repositories, sorts them strictly by stars, selects the top 5, and isolates the #1 ranked project.*
> 5. *We then call a secondary GitHub endpoint to fetch the README documentation of the top repository. A second code node decodes the Base64 buffer, cleans markdown images and badges, and extracts a crisp 220-character executive preview.*
> 6. *Next, an IF node checks our interest threshold: if the top repository has 10,000 or more stars, it routes to our **Spotlight Tier**, formatting an Emerald Green Discord Embed with medal emojis, formatted star counts, and the enriched README preview.*
> 7. *Finally, it dispatches the payload to a Discord webhook, referencing secrets safely through n8n expressions rather than hardcoding tokens."*
>
> *(Briefly switch to `Task2/screenshots/execution.png`)*
> *"Here you can see the successful execution: all nodes green, executing in under 500 milliseconds, with the delivered Discord briefing."*

---

### 4. Bonus Task: Continuous Uptime Sentinel (3:15 – 4:15)
> *(Switch screen to `Bonus/screenshots/uptime-workflow.png`)*
>
> *"For the Bonus Task, I built the **PulseQA Uptime Sentinel**. It checks the health of our web application every 5 minutes.*
>
> *The critical engineering decision here was **false-positive mitigation**:*
> - *A naive monitor pages an engineer the moment a single packet drops. In our workflow, when the primary ping detects a non-200 code or timeout, it does NOT alert immediately.*
> - *Instead, it enters a 5-second wait buffer and sends a second confirmation probe.*
> - *If the second probe recovers with HTTP 200, it logs a self-healing notice.*
> - *If both probes fail, it confirms an active outage, formats a diagnostic alert detailing whether it's a Cloudflare 530, an S3 404, or an internal 500, and pings the operations channel on Discord with an immediate action checklist.*
> - *It also measures round-trip latency in milliseconds for every check to track performance degradation."*

---

### 5. Conclusion & Defending Decisions (4:15 – 4:45)
> *(Switch back to GitHub repository root)*
>
> *"To summarize: every deliverable requested in the assessment is packaged cleanly in this repository: the PDF QA report, valid importable workflow JSONs, documentation, and screenshots.*
>
> *I chose the GitHub Search and README endpoints because they provide rich real-world data and test multi-step base64 transformations; I chose Discord webhooks because they support structured, color-coded embeds; and I designed both workflows around strict resilience—zero silent failures and zero false-positive alerts.*
>
> *Thank you for reviewing my assessment, and I look forward to discussing my technical reasoning in the follow-up interview!"*

