# Product Requirements Document (PRD)
## PulseQA – Web Application Quality Assurance & Intelligent Automation Platform
**Version:** 1.0  
**Date:** November 9, 2026  
**Author:** Abhishek Choudhari  
**Project Type:** Automation & Quality Assurance Developer Assessment  
**Technology Stack:** n8n, GitHub REST API, JavaScript, Discord Webhooks, Chrome Headless, Python  

---

## 1. Executive Summary
PulseQA is a quality assurance and workflow automation project designed to demonstrate how web applications can be tested, monitored, and supported through automated workflows.

The project combines three major capabilities:
1. **Web Application QA:** Investigate an existing AI-assisted web application, identify functional and usability issues, reproduce bugs, and document root causes and recommendations.
2. **Automated Data Integration:** Build an n8n workflow that retrieves public GitHub repository data, transforms and enriches the results, evaluates conditions, and distributes a formatted digest through Discord.
3. **Application Uptime Monitoring:** Create an automated monitoring workflow that periodically checks application availability, measures response times, and sends alerts when the application becomes unavailable.

---

## 2. Problem Statement
Modern applications, particularly those created using AI-assisted development tools ("vibe coding"), frequently contain functional bugs, inconsistent validation, incomplete error handling, and usability problems.

At the same time, development teams frequently perform repetitive activities such as collecting information from APIs, processing responses, monitoring application availability, and communicating important updates.

Without proper automation and monitoring:
- Application issues may remain undetected.
- API failures may interrupt business workflows silently.
- Important trend and operational information may be missed.
- Teams may spend unnecessary time performing repetitive tasks.
- Insufficient visibility leads to delayed incident recovery.

PulseQA addresses these problems through structured QA investigation and automated workflow execution.

---

## 3. Project Objectives
- Identify and document at least five reproducible issues in an existing web application.
- Perform functional testing of registration, authentication, content creation, editing, deletion, and logout.
- Build an n8n workflow integrating at least two API requests.
- Process and transform API responses using JavaScript.
- Implement conditional branching using IF nodes.
- Implement meaningful error handling and fallback behavior to prevent silent failure.
- Deliver automated notifications through Discord.
- Monitor application availability every five minutes with latency tracking and retry backoff.
- Produce reproducible documentation and exportable workflow configurations.

---

## 4. System Architecture

```
                          ┌────────────────────────────────────────────────────────┐
                          │         PulseQA Quality & Automation System            │
                          └────────────────────────────────────────────────────────┘
                                                       │
         ┌─────────────────────────────────────────────┼─────────────────────────────────────────────┐
         ▼                                             ▼                                             ▼
┌──────────────────────────────┐              ┌──────────────────────────────┐              ┌──────────────────────────────┐
│  Module A: Web App QA & RCA  │              │ Module B: GitHub Digest Flow │              │  Module C: Uptime Sentinel   │
│  - RealWorld Conduit App     │              │  - Hourly Schedule & Webhook │              │  - 5-Min Cron Health Check   │
│  - 6 Reproducible Bugs       │              │  - GitHub Search API         │              │  - Latency Tracking (ms)     │
│  - Deep-Dive ATO Analysis    │              │  - JavaScript Transformation │              │  - 5s Anti-Flap Retry Buffer │
│  - Multi-tier Remediation    │              │  - README Base64 Decoding    │              │  - Error Interception        │
│  - Formal PDF QA Report      │              │  - IF Star Threshold (10k)   │              │  - Diagnostic Outage Alerts  │
│                              │              │  - Discord Embeds & Fallback │              │  - Discord Webhook Channel   │
└──────────────────────────────┘              └──────────────────────────────┘              └──────────────────────────────┘
```

---

## 5. Deliverables & Acceptance Checklist

| Requirement ID | Deliverable File | Description | Status |
| :--- | :--- | :--- | :--- |
| **Task 1** | `Task1_QA_Report_Abhishek.pdf` | Comprehensive PDF report with 6 bugs and deep-dive RCA | **COMPLETED** |
| **Task 2 (Workflow)** | `Task2/Task2_Workflow_Abhishek.json` | Valid n8n v1.x importable JSON with error handling & Discord | **COMPLETED** |
| **Task 2 (Docs)** | `Task2/README.md` | Architectural rationale, APIs, code logic, error branches | **COMPLETED** |
| **Task 2 (Visuals)**| `screenshots/workflow.png`, `execution.png` | High-res workflow canvas and successful execution views | **COMPLETED** |
| **Bonus Task** | `Bonus/Bonus_UptimeMonitor_Abhishek.json` | 5-min uptime workflow with 5s retry buffer & latency check | **COMPLETED** |
| **Bonus (Docs)** | `Bonus/README.md` | Uptime Sentinel design, false-positive mitigation, diagnostics | **COMPLETED** |
| **Bonus (Visual)** | `screenshots/uptime-workflow.png` | High-res uptime monitor workflow canvas | **COMPLETED** |
| **Loom Walkthrough**| `Loom/demo-link.txt`, `VIDEO_WALKTHROUGH_SCRIPT.md` | Loom demo URL & word-for-word presentation script | **COMPLETED** |
| **Root Docs** | `README.md` | Complete repository documentation and execution instructions | **COMPLETED** |

