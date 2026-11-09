# Task 1 — Web Application QA & Debug Report
**Project:** PulseQA – Web Application Quality & Automation Monitor  
**Target Application:** RealWorld (Conduit) Application Platform  
**Testing Environment:** Angular/React SPA Frontend (`demo.realworld.show` / `demo.realworld.io`) & REST API (`api.realworld.show/api` / `api.realworld.io/api`)  
**Assessment Candidate:** Abhishek Choudhari  
**Date:** November 9, 2026  
**Document Status:** Complete / Final  

---

## 1. Executive Summary
During a systematic quality assurance and security investigation of the AI-assisted ("vibe-coded") RealWorld (Conduit) web platform, the QA team evaluated all core user workflows: account registration, authentication, content authoring, inline editing, article deletion, logout, input validation, and boundary conditions. 

The evaluation revealed six critical-to-medium severity defects spanning infrastructure availability, data integrity, access control, and cross-site scripting vulnerabilities. Most notably, the official production endpoints documented across the codebase suffered catastrophic infrastructure abandonment (`404 NoSuchBucket` and `530 Cloudflare DNS`), while the active backend exposes severe idempotency flaws allowing duplicate user registrations to silently mint session tokens. This report documents the reproducible steps, expected versus actual behaviors, suspected root causes, and provides an in-depth root-cause analysis (RCA) with concrete remediation code.

---

## 2. Testing Scope & User Flow Matrix

| User Flow | Test Focus | Method / Tool | Status |
| :--- | :--- | :--- | :--- |
| **Sign-Up** | Form validation, duplicate emails, password length, token generation | Automated Python Test Harness, cURL | **FAIL** (Issues #1, #4) |
| **Authentication** | Valid credentials, bad password, token persistence | Chrome DevTools, Network tab, cURL | **PASS / WARNING** (Issue #6) |
| **Content Creation** | Markdown parsing, title slugification, XSS tag filtering | Automated Test Harness, DOM Inspector | **FAIL** (Issue #3) |
| **Content Edit** | Field mutation, slug stability, slug redirect | REST API PUT calls, Browser navigation | **FAIL** (Issue #5) |
| **Content Deletion**| Cascading deletion, authorization boundaries | REST API DELETE, Unauthorized checks | **PASS** |
| **Logout & Session**| LocalStorage clearing, server-side token revocation | LocalStorage Inspector, JWT Replay | **FAIL** (Issue #6) |
| **Infrastructure** | DNS resolution, S3 bucket routing, error page rendering | cURL, OpenSSL, DNS lookup | **FAIL** (Issue #2) |

---

## 3. Bug Findings Table

| # | Title / Summary | Steps to Reproduce | Expected vs Actual | Severity | Suspected Cause |
|---|---|---|---|---|---|
| **1** | **Silent Duplicate Registration & Unauthenticated Token Generation** | 1. Send `POST /api/users` with email `user@example.com`, username `user1`, password `Password123!`.<br>2. Receive `201 Created`.<br>3. Send the exact same `POST /api/users` request again with identical email and username. | **Expected:** `422 Unprocessable Entity` with `{"errors": {"email": ["has already been taken"]}}`.<br><br>**Actual:** Returns `201 Created` and issues a brand-new authentication token without verifying password. | **Critical** | Missing unique index constraint on `users.email` and `users.username` in database schema, combined with an unsafe `findOrCreate` or `upsert` in the registration controller that lacks uniqueness validation. |
| **2** | **Production Outage of Documented Endpoints (`demo.realworld.io` & `api.realworld.io`)** | 1. Navigate to `https://demo.realworld.io` in a browser.<br>2. Query `https://api.realworld.io/api/tags` via GET request. | **Expected:** `demo.realworld.io` serves the SPA frontend with HTTP 200; `api.realworld.io` returns JSON tags with HTTP 200.<br><br>**Actual:** `demo.realworld.io` returns `HTTP 404 NoSuchBucket` (AWS S3); `api.realworld.io` returns `HTTP 530 Error 1016` (Cloudflare DNS origin failure). | **Critical** | Decommissioned infrastructure without DNS cleanup. S3 bucket was deleted while Route53 records remained active. Cloudflare CNAME points to an inactive origin server. Lack of automated uptime monitoring. |
| **3** | **Stored Cross-Site Scripting (XSS) via Unsanitized Article Inputs** | 1. Authenticate with valid JWT token.<br>2. Send `POST /api/articles` with payload: `{"article": {"title": "<script>alert('XSS')</script>", "body": "<img src=x onerror=alert('XSS')>", "tagList": ["<script>"]}}`.<br>3. Inspect API response and render in frontend reader. | **Expected:** API rejects raw HTML tags or sanitizes them using DOMPurify / sanitize-html before storage.<br><br>**Actual:** Server stores raw scripts verbatim and returns them in `GET /api/articles/{slug}`. Frontends using unescaped HTML (`v-html` / `[innerHTML]`) execute malicious scripts. | **High** | Absence of input sanitization middleware on the API gateway and markdown parser pipeline failing to strip raw HTML elements before injection into the DOM. |
| **4** | **Absence of Password Complexity or Minimum Length Enforcement** | 1. Send `POST /api/users` with payload `{"user": {"username": "weak_usr", "email": "weak@example.com", "password": "1"}}`.<br>2. Observe server response. | **Expected:** `422 Unprocessable Entity` rejecting passwords under 8 characters: `{"errors": {"password": ["is too short (minimum 8 characters)"]}}`.<br><br>**Actual:** Returns `201 Created`. Account created with a single-character password (`"1"`). | **High** | Missing schema validation rules in the request validation layer (e.g. Joi/Zod schema specifies `string().required()` instead of `string().min(8).regex(...)`). |
| **5** | **Broken Links (HTTP 404) on Article Title Updates due to Slug Mutation** | 1. Create article with title `"System Design Guide"` (slug: `system-design-guide-123`).<br>2. Edit article title to `"System Design Guide 2026"` (new slug: `system-design-guide-2026`).<br>3. Query previous URL `/api/articles/system-design-guide-123`. | **Expected:** HTTP 301 redirect to new slug, or system resolves previous slug alias.<br><br>**Actual:** Server returns `HTTP 404 Not Found: {"errors": {"article": ["not found"]}}`. External links and bookmarks break permanently. | **Medium** | The database uses `slug` as the primary lookup key rather than an immutable UUID/ID. Updating `title` regenerates the slug and overwrites the column without maintaining a slug alias history table. |
| **6** | **Insecure JWT Storage in `localStorage` & Lack of Server-Side Revocation** | 1. Log in and copy token from `localStorage.getItem('jwtToken')`.<br>2. Click "Logout" in UI.<br>3. Send `GET /api/user` with header `Authorization: Token <copied_token>`. | **Expected:** Token is stored in `HttpOnly, Secure, SameSite=Strict` cookie, and server revokes token session on logout.<br><br>**Actual:** Token remains stored in client-accessible `localStorage` (vulnerable to XSS theft) and continues to authenticate successfully on the backend indefinitely after logout. | **Medium** | Stateless JWT implementation without an active session blocklist (e.g. Redis cache), token rotation, or server-side logout endpoint. "Logout" is merely client-side cache clearing. |

---

## 4. Deep-Dive Root-Cause Analysis (RCA)

### Selected Issue: Issue #1 — Silent Duplicate User Registration & Unauthenticated Token Generation

#### 1. What is Happening?
When a client submits a registration request (`POST /api/users`) containing an email address and username that already exist in the database, the API does not reject the request with an HTTP 422 Unprocessable Entity validation error. Instead, the application returns `HTTP 201 Created` alongside a newly generated authentication token, effectively signing the requester into the existing user account without verifying the account's existing password.

#### 2. Why is it Happening? (Root Cause)
The vulnerability originates from two compounding architecture flaws in the AI-generated backend service:
1. **Missing Schema-Level Constraints:** The database migration failed to define a `UNIQUE` index on the `users.email` and `users.username` columns, allowing relational tables to either duplicate records or rely entirely on application-level checks.
2. **Improper ORM Query Pattern:** In the registration controller, the AI-generated code utilized an unsafe `findOrCreate()` or `upsert()` ORM method instead of an explicit sequential check (`findOne` $\rightarrow$ abort if present $\rightarrow$ `create`). Because `findOrCreate()` locates the existing user record without validating the provided password, it passes the retrieved entity to the JWT signing utility, minting a valid authorization token for the existing account. This constitutes a severe Account Takeover (ATO) risk.

#### 3. How to Fix It? (Remediation Plan)
To permanently remediate this defect, the engineering team must implement a multi-layered fix across the database, validation middleware, and controller logic:

1. **Database Migration:** Apply unique constraints to ensure database integrity at the persistence layer:
   ```sql
   ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);
   ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username);
   ```

2. **Validation Middleware (Zod / Joi Schema):** Validate input types, string lengths, and email format before reaching the controller:
   ```typescript
   export const RegisterSchema = z.object({
     user: z.object({
       username: z.string().min(3).max(30).regex(/^[a-zA-Z0-9_]+$/),
       email: z.string().email(),
       password: z.string().min(8, "Password must be at least 8 characters long"),
     }),
   });
   ```

3. **Controller Remediation:** Replace `findOrCreate` with a strict atomic existence check returning standard RealWorld 422 error structures:
   ```typescript
   export async function registerUser(req: Request, res: Response) {
     const { username, email, password } = req.body.user;

     // 1. Check for existing email or username
     const existingUser = await db.user.findFirst({
       where: { OR: [{ email: email.toLowerCase() }, { username }] }
     });

     if (existingUser) {
       const field = existingUser.email.toLowerCase() === email.toLowerCase() ? 'email' : 'username';
       return res.status(422).json({
         errors: { [field]: ['has already been taken'] }
       });
     }

     // 2. Hash password with bcrypt (work factor 12)
     const hashedPassword = await bcrypt.hash(password, 12);

     // 3. Persist new user record atomically
     const newUser = await db.user.create({
       data: { username, email: email.toLowerCase(), password: hashedPassword }
     });

     // 4. Generate JWT token
     const token = generateJwt(newUser);
     return res.status(201).json({ user: formatUserResponse(newUser, token) });
   }
   ```

---

## 5. Strategic Recommendations for Non-Technical Stakeholders

1. **Implement Automated CI/CD Regression Gates:** Add Playwright end-to-end integration tests for the primary user lifecycle before releasing AI-generated features to staging.
2. **Deploy Continuous Uptime & Synthetic Monitoring:** Connect an automated monitor (such as the PulseQA n8n Uptime Monitor) to ping endpoints every 5 minutes and immediately notify the engineering team via Discord/Slack when DNS or HTTP failures occur.
3. **Establish Security Guardrails for AI Code Generation:** Mandate that all AI-assisted code undergoes static security analysis (SAST) with SonarQube or Snyk to catch missing schema constraints, unescaped HTML renders, and weak password validators before deployment.

---
*Report compiled by Abhishek Choudhari | Lead Automation & QA Developer Candidate | PulseQA Platform*

