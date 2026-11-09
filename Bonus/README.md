# Bonus Task — Automated Uptime & Health Monitor
**Workflow Name:** `Bonus_UptimeMonitor_Abhishek.json`  
**Author:** Abhishek | Automation & QA Developer  
**System:** PulseQA Platform  
**Target Application:** RealWorld Platform API (`https://api.realworld.show/api/tags`)  

---

## 1. Executive Summary & Architecture
The PulseQA Uptime Sentinel is a continuous synthetic monitoring workflow designed to track web application availability, measure latency, and alert operations teams before users experience service degradation. 

Unlike naive ping scripts that alert on every transient network blip, this workflow implements **two-phase verification with retry backoff**, ensuring that alerts sent to Discord represent **genuine outages**, completely eliminating false-positive paging.

```
[Schedule (5 min)] ──┐
                     ├──► [Init Probe] ──► [HTTP Ping] ──► [Calc Latency] ──► [HTTP 200 OK?]
[Manual Webhook]   ──┘                                                              │
                                                        ┌───────────────────────────┴───────────────────────────┐
                                                        ▼ (TRUE)                                                ▼ (FALSE)
                                             [Log Healthy Metric]                                     [Wait 5s Retry Buffer]
                                                                                                                │
                                                                                                                ▼
                                                                                                      [HTTP Retry Ping (2nd)]
                                                                                                                │
                                                                                                                ▼
                                                                                                      [Outage Confirmed?]
                                                                                                                │
                                                        ┌───────────────────────────────────────────────────────┴───────────────────────────────────────────────────────┐
                                                        ▼ (TRUE - Confirmed Outage)                                                                                     ▼ (FALSE - Flap Recovered)
                                           [Format Critical Discord Alert]                                                                                 [Format Flap Recovery Notice]
                                                        │                                                                                                               │
                                                        ▼                                                                                                               ▼
                                           [Post Outage Alert to Discord]                                                                                  [Post Flap Notice to Discord]
```

---

## 2. Core Capabilities & Design Decisions

### A. Non-Blocking Status Code Interception
By default, n8n HTTP Request nodes throw an unhandled exception when receiving non-200 HTTP statuses (e.g., 404, 500, 503, 530). In the Uptime Sentinel, `continueOnFail: true` is enabled on both primary and retry HTTP request nodes. This converts HTTP failure responses into structured JSON payloads containing status codes, response headers, and error messages, allowing downstream logic to evaluate failures programmatically.

### B. High-Precision Latency Tracking
The probe captures a high-resolution millisecond timestamp (`Date.now()`) immediately before issuing the HTTP request and computes the delta (`latencyMs = Date.now() - probeStartTime`) upon response receipt. This tracks degradation and latency spikes before complete server failure.

### C. False-Positive Mitigation (5-Second Retry Buffer)
Transient packet loss, temporary DNS jitter, or upstream load-balancer restarts can cause a single health check to fail. When the primary check returns a non-200 code:
1. The execution branches into a `Wait` node pausing for 5 seconds.
2. A secondary HTTP Request issues a confirmation probe to the target URL.
3. If the retry succeeds (HTTP 200), the incident is classified as a **Transient Flap (Self-Healed)** and logged with a yellow warning notice.
4. If the retry also fails, the incident is classified as a **Confirmed Outage**, triggering a critical red alert.

### D. Automated Root-Cause Diagnostics
When a confirmed outage occurs, the alert formatter inspects the status code and injects actionable root-cause diagnostics directly into the Discord Embed:
- **HTTP 530 (Cloudflare Error 1016):** Highlights origin DNS resolution failures.
- **HTTP 404 (Not Found / NoSuchBucket):** Identifies missing endpoints or deleted S3 storage buckets.
- **HTTP 500 / 502 / 503:** Highlights server exceptions, container crashes, or upstream gateway timeouts.
- **Actionable Checklist:** Instructs on-call engineers on exact diagnostic steps to accelerate Mean Time to Resolution (MTTR).

---

## 3. Configuration & Credentials
- **Monitored URL:** Configured via expression `{{ $env.MONITORED_APP_URL || 'https://api.realworld.show/api/tags' }}`.
- **Notification Target:** Dispatches via `{{ $env.DISCORD_WEBHOOK_URL || '...' }}`.
- **Inspection Frequency:** Runs every 5 minutes automatically, or on demand via `GET /webhook/uptime-ping-trigger`.

