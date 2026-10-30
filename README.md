# RecycleTrace — Waste Tracking & Recycling Verification Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Community%208.x-green.svg)](https://www.mongodb.com/)
[![PyMongo](https://img.shields.io/badge/PyMongo-4.x-brightgreen.svg)](https://pymongo.readthedocs.io/)
[![Test Suite](https://img.shields.io/badge/pytest-22%20passed-success.svg)](https://pytest.org/)

> **Academic Project** — *Intelligent NoSQL Databases Course*  
> An end-to-end, full-stack waste tracking and recycling verification platform that answers the fundamental question:  
> **“Why can’t citizens verify whether segregated waste is actually recycled?”**

---

## 1. Executive Summary & Problem Solved

Citizens diligently segregate waste into plastic, paper, metal, and organics, yet have zero visibility into what happens after curbside pickup. Traditional recycling claims are often self-reported by facilities without independent review or mass-balance reconciliation.

**RecycleTrace** introduces an immutable chain-of-custody model built upon **MongoDB Community Server 8.x**:
- Every batch is assigned a unique tracking ID (e.g. `WT-2026-1001`) and a cryptographically verifiable QR code linking to a public audit page.
- Every state transition is recorded in a chronological event ledger by authenticated actors.
- **Critical Verification Invariant**: Waste arriving at a facility or having a report submitted is **never** automatically marked as recycled. It transitions to `verification_pending` until an authorized auditor reviews mass balance reconciliation (`Input == Recycled + Rejected + Residual`) and evidence before granting `verified_recycled`.
- Unexplained weight discrepancies exceeding 5% are automatically flagged for fraud investigation.

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Inter typography, responsive sidebar/topbar |
| **Charts** | Chart.js 4.4.6 |
| **QR Code Engine**| Python `qrcode` 8.0 & `Pillow` 11.0 |
| **Backend** | Python 3.10+, Flask 3.1.0 |
| **Database** | MongoDB Community Server 8.0.28 (local or Atlas) |
| **Driver** | PyMongo 4.10.1 |
| **Security** | Werkzeug password hashing, Flask session cookies (HttpOnly, SameSite=Lax), RBAC |
| **Test Suite** | pytest 8.3.3, pytest-flask 1.3.0 (22 automated tests) |

---

## 3. Database Architecture & Collections

The application connects to database `recycletrace_db` and implements six collections with `$jsonSchema` validators and unique compound indexes:

```
recycletrace_db/
├── users               # RBAC credentials, hashed passwords, account statuses
├── waste_batches       # Master waste batch lifecycle documents
├── tracking_events     # Chronological ledger of custody handoffs
├── facilities          # Accredited recycling plants & sorting centers
├── processing_records  # Mass balance reconciliation & auditor decisions
└── audit_logs          # Tamper-evident administrative & security audit trail
```

### Schema Validation & Unique Indexes
- **`users`**: Email format regex, role enum (`citizen`, `collector`, `facility_operator`, `admin`), unique index on `email`.
- **`waste_batches`**: Unique index on `batch_id`, status enum (`registered` ... `verified_recycled`), minimum positive weight validator (`declared_weight_kg >= 0.01`), compound index `(citizen_id, current_status)`.
- **`tracking_events`**: Unique index on `event_id`, compound timeline index `(batch_id, timestamp)`.
- **`facilities`**: Unique index on `facility_id`, category enum arrays.
- **`processing_records`**: Unique index on `processing_id`, non-negative numeric fields, compound index `(batch_id, facility_id)`.
- **`audit_logs`**: Unique index on `audit_id`, indexed actor and timestamp.

---

## 4. Five Working MongoDB Aggregation Pipelines

The platform implements five distinct aggregation pipelines accessible through `/api/analytics/*` and visualised on the Admin Analytics dashboard:

1. **Batch Status Summary (`$group` + `$sort`)**:
   Groups all batches by `current_status`, calculates total declared weight per state, and sorts by count descending.
2. **Facility-Level Throughput Summary (`$match` + `$group` + `$lookup`)**:
   Performs a left outer join with `facilities` to calculate verified recycled output vs input for each facility.
3. **Daily Collection Trends (`$dateTrunc` + `$group`)**:
   Truncates UTC timestamps by day to provide daily volume trends over the past 30 days.
4. **Batch-to-Facility Reporting (`$lookup`)**:
   Joins `waste_batches`, `facilities`, and `processing_records` to build an integrated compliance view.
5. **Executive KPI Dashboard (`$facet`)**:
   Executes multi-faceted aggregation simultaneously computing category distribution, status totals, and total system weight in a single database round-trip.

---

## 5. Quickstart & Installation (Windows PowerShell)

### Prerequisites
- Python 3.10+ (Installed and on PATH)
- MongoDB Community Server 8.x running locally on port 27017 (or MongoDB Atlas connection string)

### 1. Clone & Enter Directory
```powershell
cd d:\Downloads\pymong\recycletrace
```

### 2. Activate Virtual Environment
```powershell
..\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Default `.env` configuration:
```env
FLASK_SECRET_KEY=dev-secret-key-recycletrace-academic-2026-supersecure
FLASK_ENV=development
FLASK_DEBUG=1
MONGO_URI=mongodb://localhost:27017/recycletrace_db
APP_HOST=127.0.0.1
APP_PORT=5000
BASE_URL=http://localhost:5000
WEIGHT_TOLERANCE_PERCENT=5.0
```

### 5. Seed Synthetic Demo Data
Populates realistic records across all waste lifecycle states, verified/unverified facilities, and discrepancy flags:
```powershell
python scripts/seed_demo_data.py
```

### 6. Run the Application
```powershell
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## 6. Preconfigured Demo Accounts

All demo accounts use password: **`Demo1234!`**

| Role | Email | Capabilities |
|---|---|---|
| **Citizen** | `citizen@demo.com` | Register waste, view batches, download QR codes, view public track page |
| **Collector** | `collector@demo.com` | View available pickups, confirm scale weight, dispatch to verified facility |
| **Operator** | `operator@demo.com` | Confirm facility arrival, submit mass-balance processing reports |
| **Administrator** | `admin@demo.com` | Review evidence, approve/reject claims, inspect discrepancies, view audit logs, run benchmarks |

---

## 7. Running the Automated Test Suite

Run the full pytest suite (22 unit, integration, and database tests):
```powershell
pytest -v
```
**Test Coverage Includes:**
- User registration, duplicate email rejection, role-based access restrictions.
- Controlled status transitions (`registered` → `collected` → `in_transit` → `received` → `processing` → `verification_pending` → `verified_recycled`).
- Rejection of invalid status skipping.
- Redaction of private citizen addresses from the public QR tracking page.
- Mass-balance weight reconciliation math and discrepancy flagging.
- MongoDB `$jsonSchema` rejection of negative weights and illegal categories.
- Unique index duplicate key error enforcement.
- Execution of all 5 aggregation pipelines.

---

## 8. Query Optimization & Index Benchmark

Run the live explain benchmark on 10,000 synthetic records:
```powershell
python scripts/benchmark_indexes.py
```

### Actual Measured MongoDB 8.0 Execution Statistics

#### Test 1: Single Field Lookup (`batch_id`)
```
--- [A] BEFORE INDEX (No Index on batch_id) ---
Winning Stage       : COLLSCAN
Total Docs Examined : 10000
Total Keys Examined : 0
Execution Time (ms) : 7 ms

--- [B] AFTER INDEX (Unique Index on batch_id) ---
Winning Stage       : EXPRESS_IXSCAN (MongoDB 8.x Engine)
Total Docs Examined : 1
Total Keys Examined : 1
Execution Time (ms) : 24 ms (Cold cache compile) / 0 ms (Subsequent)
```

#### Test 2: Compound Query (`citizen_id` + `current_status`)
```
--- [A] BEFORE COMPOUND INDEX ---
Winning Stage       : COLLSCAN
Total Docs Examined : 10000
Total Keys Examined : 0
Execution Time (ms) : 5 ms

--- [B] AFTER COMPOUND INDEX ---
Winning Stage       : FETCH -> IXSCAN
Total Docs Examined : 14
Total Keys Examined : 14
Execution Time (ms) : 9 ms
```
*Documents scanned dropped from 10,000 to 1 and 10,000 to 14, demonstrating the necessity of compound and unique indexing in high-volume waste tracking.*

---

## 9. Security & Privacy Controls

1. **Privacy Redaction**: The public endpoint (`/api/public/track/<batch_id>` and `/track/<batch_id>`) provides transparent event verification while explicitly redacting personal addresses, citizen phone numbers, and internal database IDs.
2. **Rate Limiting**: In-memory rate limiting defends authentication endpoints against brute force attempts.
3. **Audit Immutability**: All sensitive actions write audit records (`AUD-*`) documenting actor ID, UTC timestamp, entity type, and operation metadata.
4. **No Auto-Recycled State**: A processing report submission leaves the batch in `verification_pending`. Only an explicit admin/auditor review decision marks waste as `verified_recycled`.

