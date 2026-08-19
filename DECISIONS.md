# DECISIONS.md — Ingestion Architecture & Design Analysis

## 1. Technical Analysis & Design Topics

### 1. Detection Surface
Automated scrapers on platforms like LinkedIn, Indeed, or Wellfound expose distinct detection vectors:
- **Headless Fingerprints**: `navigator.webdriver` flags, missing Chrome plugins, automated canvas/WebGL hashes, and default viewport sizes.
- **Request Timing & Behavioral Heuristics**: Uniform periodic request intervals, lack of scroll/mouse movement variance, and burst request spikes.
- **HTTP Header Anomalies**: Missing browser headers (`User-Agent`, `Accept-Language`, `Sec-Fetch-Dest`, `Sec-Ch-Ua`), default HTTP client signatures (e.g. `python-requests`, `httpx`), and missing cookie jars.

**Design Accounting**: Our architecture uses `ResilientHttpClient` with standardized browser headers, controlled request pacing, and isolates scraping targets to public API/RSS channels to avoid triggering TLS/JA3 bot signatures.

### 2. Ingestion Strategy & Plan B
- **Pacing & Session Management**: Paginated execution using configurable delay windows and session isolation.
- **Mid-Run Block Fallbacks**: Handles `429 Too Many Requests` responses by parsing `Retry-After` headers and applying exponential backoff with jitter.
- **Plan B Strategy**: If primary JSON API endpoints become blocked or deprecated, the architecture's modular `JobSource` abstraction seamlessly falls back to RSS/Atom feeds (e.g., RemoteOK feed adapter) or headless browser rendering engines (Playwright with stealth plugins) without modifying downstream database or deduplication code.

### 3. Resilience & Anti-Silent Failure
- **Markup & Payload Normalization**: Adaptive schema normalization (`_normalize_job`) sanitizes raw payloads and handles missing fields gracefully.
- **Telemetry & Error Persistence**: Failed page fetches log detailed error records (`status_code`, `attempts`, `error_type`, `occurred_at`) to `ingestion_errors` database tables and mark runs as `partial_failure` or `failed` rather than silently swallowing exceptions.

### 4. Terms of Service & Ethical Boundaries
- **Scope Guardrail Compliance**: Target ingestion runs exclusively against low-risk public job board APIs (Himalayas API), respecting `robots.txt` and avoiding authenticated private user account scraping.
- **Technical Line**: Strict avoidance of CAPTCHA-solving farms, credential stuffing, or bypassing paywalls.

---

## 2. Core Trade-Offs & AI Tool Audit

### Q1: Ingestion Strategy Rationale
We chose structured API/RSS payload ingestion with resilient retry mechanics over headless browser DOM scraping (Playwright/Puppeteer).
*Rationale*: API endpoints provide 10x faster execution, lower resource consumption, zero headless fingerprint exposure, and deterministically typed data schemas.

### Q2: Time-Limit Trade-Offs & 1-Week Roadmap
- **Time-Limit Trade-Off**: Used single-IP resilient HTTP fetching with exponential backoff rather than a distributed proxy rotation network.
- **1-Week Plan**: Implement automatic IP proxy pool rotation (BrightData/ScraperAPI), headless Playwright fallback adapters with TLS fingerprint spoofing, and automated alerts for schema drift detection.

### Q3: AI Tool Usage & Manual Verification
- **AI Tool Usage**: Assisted in generating initial boilerplate schema models, test client scaffolding, and Tailwind/Vanilla CSS glassmorphism styling tokens.
- **Manual Verification**: Personally verified line-by-line SQLite FTS5 trigger syntax, BM25 ranking SQL calculations, Jaccard similarity weights in the recommendation engine, bcrypt password security, and written architectural decisions.
