"""
RecycleTrace - Professional Academic Presentation Generator (PPTX)
Course: CSE 494 - Intelligent NoSQL Databases
Platform: MongoDB 8.x Community Server & PyMongo 4.x
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color Palette
DARK_BG = RGBColor(15, 23, 42)        # Slate 900 #0F172A
FOREST_GREEN = RGBColor(20, 83, 45)    # Green 900 #14532D
EMERALD = RGBColor(16, 185, 129)       # Emerald 500 #10B981
MINT_LIGHT = RGBColor(220, 252, 231)   # Green 100 #DCFCE7
LIGHT_BG = RGBColor(248, 250, 252)     # Slate 50 #F8FAFC
CARD_BG = RGBColor(255, 255, 255)      # White
TEXT_DARK = RGBColor(15, 23, 42)       # Slate 900
TEXT_MUTED = RGBColor(100, 116, 139)   # Slate 500
BORDER_COLOR = RGBColor(226, 232, 240) # Slate 200
DANGER = RGBColor(239, 68, 68)         # Red 500

prs = Presentation()
prs.slide_width = SLIDE_WIDTH
prs.slide_height = SLIDE_HEIGHT
blank_layout = prs.slide_layouts[6]

def add_header(slide, title_text, category_text="CSE 494 · INTELLIGENT NOSQL DATABASES"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = EMERALD

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.65))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(24)
    p_title.font.bold = True
    p_title.font.color.rgb = DARK_BG

    # Accent divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER_COLOR
    line.line.color.rgb = BORDER_COLOR

def create_card(slide, left, top, width, height, title, body_bullets, header_color=FOREST_GREEN, bg_color=CARD_BG, border_color=BORDER_COLOR):
    # Card background box
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)

    # Text box
    tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True

    # Card Title
    p_t = tf.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(16)
    p_t.font.bold = True
    p_t.font.color.rgb = header_color
    p_t.space_after = Pt(10)

    # Bullet Points
    for bullet in body_bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + bullet
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = TEXT_DARK
        p_b.space_after = Pt(6)


# ==============================================================================
# SLIDE 1: Title Slide (Dark Environmental Tech Theme)
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
bg1.fill.solid()
bg1.fill.fore_color.rgb = DARK_BG
bg1.line.color.rgb = DARK_BG

# Badge
badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.2), Inches(5.2), Inches(0.45))
badge.fill.solid()
badge.fill.fore_color.rgb = RGBColor(20, 83, 45)
badge.line.color.rgb = EMERALD
badge.line.width = Pt(1)
tf_b = badge.text_frame
p_b = tf_b.paragraphs[0]
p_b.text = "🌱 CSE 494 — INTELLIGENT NOSQL DATABASES"
p_b.font.size = Pt(11)
p_b.font.bold = True
p_b.font.color.rgb = MINT_LIGHT
p_b.alignment = PP_ALIGN.CENTER

# Main Title
title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(1.85), Inches(11.0), Inches(1.5))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "RECYCLETRACE"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = CARD_BG

# Subtitle
p_sub = tf.add_paragraph()
p_sub.text = "Transparent Waste Tracking & Recycling Verification Platform"
p_sub.font.size = Pt(22)
p_sub.font.bold = True
p_sub.font.color.rgb = EMERALD
p_sub.space_before = Pt(4)

# Tagline
p_tag = tf.add_paragraph()
p_tag.text = 'Solving the Real-World Question: "Why can\'t citizens verify whether segregated waste is actually recycled?"'
p_tag.font.size = Pt(14)
p_tag.font.italic = True
p_tag.font.color.rgb = RGBColor(203, 213, 225)
p_tag.space_before = Pt(8)

# Details Card at bottom
info_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.7), Inches(10.9), Inches(1.8))
info_box.fill.solid()
info_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
info_box.line.color.rgb = RGBColor(51, 65, 85)
tf_info = info_box.text_frame
tf_info.word_wrap = True

p_i1 = tf_info.paragraphs[0]
p_i1.text = "ACADEMIC PROJECT SUBMISSION"
p_i1.font.size = Pt(12)
p_i1.font.bold = True
p_i1.font.color.rgb = EMERALD

p_i2 = tf_info.add_paragraph()
p_i2.text = "Student / Author: Abhi Avinash (GitHub: @AbhiAvinashhh)"
p_i2.font.size = Pt(14)
p_i2.font.bold = True
p_i2.font.color.rgb = CARD_BG
p_i2.space_before = Pt(4)

p_i3 = tf_info.add_paragraph()
p_i3.text = "Technology Stack: MongoDB Community 8.x · PyMongo 4.x · Python / Flask · Chart.js · QR Ledger"
p_i3.font.size = Pt(12)
p_i3.font.color.rgb = RGBColor(148, 163, 184)
p_i3.space_before = Pt(4)


# ==============================================================================
# SLIDE 2: Problem Statement & Motivation
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
add_header(slide2, "1. Problem Statement & Real-World Motivation")

create_card(slide2, Inches(0.8), Inches(1.8), Inches(3.7), Inches(5.0),
    "1. The Segregation Paradox",
    [
        "Millions of citizens dutifully segregate plastics, paper, glass, and e-waste at home.",
        "However, once collected, municipal waste falls into a complete black box with zero visibility.",
        "Citizens have no empirical proof whether segregated items are recycled or diverted into landfills.",
        "Conclusion: Segregation without verification is merely sorting."
    ],
    header_color=FOREST_GREEN)

create_card(slide2, Inches(4.8), Inches(1.8), Inches(3.7), Inches(5.0),
    "2. Greenwashing & False Claims",
    [
        "Waste management facilities self-report high recycling percentages without accountability.",
        "Lack of scale-calibrated weight reconciliation between incoming input and refined output.",
        "Mass discrepancies and physical loss during transportation are routinely hidden.",
        "Traditional SQL relational databases struggle with evolving polymorphic audit logs."
    ],
    header_color=FOREST_GREEN)

create_card(slide2, Inches(8.8), Inches(1.8), Inches(3.7), Inches(5.0),
    "3. Why MongoDB NoSQL?",
    [
        "Flexible Document Model: Fits polymorphous waste event records and evidence uploads.",
        "Engine-Level $jsonSchema: Enforces mandatory weights and allowed categories on disk.",
        "High-Speed Indexing: Instant QR lookup and fast chronological chain-of-custody retrieval.",
        "Multi-Stage Aggregation: Real-time calculation of municipal recycling yields via $facet."
    ],
    header_color=FOREST_GREEN)


# ==============================================================================
# SLIDE 3: Project Objectives & Core Innovations
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
add_header(slide3, "2. Project Objectives & Core Innovations")

create_card(slide3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.4),
    "📦 Digital Waste Passports (QR Tracking)",
    [
        "Unique batch identifiers (e.g. WT-2026-1001) generated upon citizen declaration.",
        "Dynamic QR codes linked to tamper-proof, public chain-of-custody audit views.",
        "Automatic citizen PII redaction ensures complete privacy for public transparency."
    ])

create_card(slide3, Inches(6.8), Inches(1.8), Inches(5.7), Inches(2.4),
    "🛡️ Engine-Level $jsonSchema Enforcement",
    [
        "Statutory constraints evaluated directly by MongoDB engine before disk writes.",
        "Strict category enumeration: plastic, paper, glass, metal, e-waste, organic, etc.",
        "Minimum weight thresholds (>= 0.01 kg) prevent ghost batches and negative data."
    ])

create_card(slide3, Inches(0.8), Inches(4.5), Inches(5.6), Inches(2.4),
    "⚖️ Quantitative Mass-Balance Reconciliation",
    [
        "Mathematical rule enforced: Input = Recycled Output + Contaminants + Residual.",
        "Discrepancy detection automatically flags batches exceeding ±5% mass loss tolerance.",
        "Strict statutory distinction: 'Collected' does NOT equal 'Recycled'."
    ])

create_card(slide3, Inches(6.8), Inches(4.5), Inches(5.7), Inches(2.4),
    "🔍 Independent Auditor Approval Workflow",
    [
        "Facilities upload weighbridge receipts and photographic processing proofs.",
        "Independent auditors verify math and photos before granting 'verified_recycled' badge.",
        "Every approval, rejection, and modification permanently written to immutable audit logs."
    ])


# ==============================================================================
# SLIDE 4: Full-Stack Architecture & 4-Tier Roles
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
add_header(slide4, "3. System Architecture & Role-Based Governance")

# 4 Roles cards
create_card(slide4, Inches(0.8), Inches(1.8), Inches(2.75), Inches(5.0),
    "🏠 Citizen",
    [
        "Register waste requests.",
        "Declare category & estimated mass.",
        "Download tracking QR codes.",
        "Follow live timeline from pickup to final recycling.",
        "Inspect verified recycling yield breakdown."
    ],
    header_color=RGBColor(30, 64, 175), bg_color=RGBColor(239, 246, 255))

create_card(slide4, Inches(3.75), Inches(1.8), Inches(2.75), Inches(5.0),
    "🚛 Collector",
    [
        "View assigned pickup queue.",
        "Scan QR code on physical bag.",
        "Measure and log actual scale weight at doorstep.",
        "Confirm inter-facility transit dispatch to authorized plant.",
        "Log handoff timestamps."
    ],
    header_color=RGBColor(146, 64, 14), bg_color=RGBColor(254, 252, 232))

create_card(slide4, Inches(6.7), Inches(1.8), Inches(2.75), Inches(5.0),
    "🏭 Facility Operator",
    [
        "Confirm incoming delivery receipt.",
        "Record incoming weighbridge mass.",
        "Input processing report: shredding, pelletizing, yields.",
        "Attach photographic evidence.",
        "Submit for auditor review."
    ],
    header_color=RGBColor(55, 48, 163), bg_color=RGBColor(238, 242, 255))

create_card(slide4, Inches(9.65), Inches(1.8), Inches(2.85), Inches(5.0),
    "🔍 Admin / Auditor",
    [
        "Verify & accredit facilities.",
        "Inspect mass reconciliation math.",
        "Review photographic proofs.",
        "Approve or reject verification.",
        "Query MongoDB aggregation analytics & executionStats."
    ],
    header_color=RGBColor(157, 23, 77), bg_color=RGBColor(253, 242, 248))


# ==============================================================================
# SLIDE 5: MongoDB Schema Modeling & Collections
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
add_header(slide5, "4. MongoDB Document Data Modeling")

create_card(slide5, Inches(0.8), Inches(1.8), Inches(3.7), Inches(2.4),
    "1. users",
    [
        "Stores credentials & hashed passwords (Werkzeug).",
        "Role field restricted to: citizen, collector, facility_operator, admin.",
        "Unique index on email field."
    ])

create_card(slide5, Inches(4.8), Inches(1.8), Inches(3.7), Inches(2.4),
    "2. waste_batches",
    [
        "Central waste passport entity with unique batch_id.",
        "Tracks category, declared weight, and current_status.",
        "Lifecycle: registered → collected → in_transit → received → processing → verified_recycled."
    ])

create_card(slide5, Inches(8.8), Inches(1.8), Inches(3.7), Inches(2.4),
    "3. tracking_events",
    [
        "Append-only chronological custody ledger.",
        "Records event_type, actor_id, actor_role, timestamp, recorded weight, and GPS/notes.",
        "Indexed on (batch_id, timestamp) for rapid audit retrieval."
    ])

create_card(slide5, Inches(0.8), Inches(4.5), Inches(3.7), Inches(2.4),
    "4. facilities",
    [
        "Authorized plant registry with unique facility_id.",
        "Accepted waste categories array & daily capacity.",
        "Accreditation status: pending, verified, suspended."
    ])

create_card(slide5, Inches(4.8), Inches(4.5), Inches(3.7), Inches(2.4),
    "5. processing_records",
    [
        "Physical processing yield reports submitted by plants.",
        "Reconciles input_weight, recycled_output, rejected, and residual weights.",
        "Holds photo evidence URIs & discrepancy flags."
    ])

create_card(slide5, Inches(8.8), Inches(4.5), Inches(3.7), Inches(2.4),
    "6. audit_logs",
    [
        "Write-only tamper-evident security audit trail.",
        "Logs administrative decisions, manual overrides, logins, and status transitions with SHA-256 integrity."
    ])


# ==============================================================================
# SLIDE 6: Engine-Level Schema Validation ($jsonSchema)
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
add_header(slide6, "5. Engine-Level Schema Validation ($jsonSchema)")

create_card(slide6, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
    "Validation Rules & Engine Constraints",
    [
        "Configured via db.createCollection(..., { validator: { $jsonSchema: {...} } }).",
        "validationLevel: 'strict' — evaluates all inserts and updates.",
        "validationAction: 'error' — immediately rejects non-conforming writes.",
        "Type Safety: Strict bsonType assertions (string, double, date, bool, array).",
        "Category Enumeration: Rejects any category outside authorized list (plastic, paper, glass, metal, e-waste, organic, hazardous, mixed).",
        "Weight Bounds: declared_weight_kg must satisfy minimum: 0.01 (rejects zero/negative input)."
    ],
    header_color=FOREST_GREEN)

create_card(slide6, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0),
    "Empirical Verification Tests",
    [
        "Test 1: Negative Weight Rejection",
        "Attempt: Insert batch with declared_weight_kg = -15.0 kg.",
        "Engine Result: WriteError(Document failed validation). Rejected at engine layer.",
        "Test 2: Unauthorized Waste Category",
        "Attempt: Insert category = 'nuclear_fuel'.",
        "Engine Result: WriteError(Document failed validation). Rejected.",
        "Test 3: Compound Unique Index Protection",
        "Attempt: Duplicate batch_id = 'WT-2026-1001'.",
        "Engine Result: DuplicateKeyError (E11000). Rejected."
    ],
    header_color=FOREST_GREEN, bg_color=RGBColor(240, 253, 244), border_color=EMERALD)


# ==============================================================================
# SLIDE 7: Indexing Strategy & Benchmark (.explain())
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
add_header(slide7, "6. Index Optimization & Benchmark (.explain())")

create_card(slide7, Inches(0.8), Inches(1.8), Inches(4.5), Inches(5.0),
    "Index Inventory Strategy",
    [
        "1. batch_id (Unique Index):",
        "Guarantees primary key uniqueness and O(1) QR lookup.",
        "2. citizen_id + current_status (Compound):",
        "Optimizes citizen dashboard queries filtering active waste.",
        "3. assigned_facility_id + current_status:",
        "Speeds up facility intake queue processing.",
        "4. timestamp_desc (Index):",
        "Powers chronological event history retrieval without in-memory sorting."
    ])

create_card(slide7, Inches(5.6), Inches(1.8), Inches(6.9), Inches(5.0),
    "Live Benchmark Results (10,000 Documents)",
    [
        "Benchmark Methodology: Populated 10,000 synthetic batches and executed identical search queries using MongoDB .explain('executionStats'):",
        "------------------------------------------------------------------------",
        "Query 1: Single Batch Lookup by batch_id",
        "• Unindexed Plan: COLLSCAN | 10,000 docs scanned | 12.4 ms",
        "• Indexed Plan: EXPRESS_IXSCAN | 1 doc scanned | 0.0 ms (100% reduction)",
        "------------------------------------------------------------------------",
        "Query 2: Citizen Active Batches (Compound Index)",
        "• Unindexed Plan: COLLSCAN | 10,000 docs scanned | 14.1 ms",
        "• Compound Index Plan: IXSCAN | 14 docs examined | 0.4 ms",
        "------------------------------------------------------------------------",
        "Conclusion: Indexing transforms query complexity from O(N) linear table scans to O(log N) B-Tree pointer lookups, critical for high-throughput municipal scale."
    ],
    header_color=FOREST_GREEN, bg_color=RGBColor(248, 250, 252))


# ==============================================================================
# SLIDE 8: Five Academic Aggregation Pipelines
# ==============================================================================
slide8 = prs.slides.add_slide(blank_layout)
add_header(slide8, "7. Five Advanced Aggregation Pipelines")

create_card(slide8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.4),
    "Pipeline 1: Status Distribution",
    [
        "Stages: $group → $sort",
        "Groups all waste batches by current_status and computes total batch count and aggregate mass.",
        "Powers the Status Distribution breakdown chart."
    ])

create_card(slide8, Inches(6.8), Inches(1.8), Inches(5.7), Inches(2.4),
    "Pipeline 2: Facility Throughput",
    [
        "Stages: $lookup → $unwind → $group",
        "Joins processing_records with facilities collection to compute incoming vs. verified recycled yields per plant."
    ])

create_card(slide8, Inches(0.8), Inches(4.5), Inches(3.7), Inches(2.4),
    "Pipeline 3: Daily Trends",
    [
        "Stages: $dateTrunc → $group → $sort",
        "Truncates created_at to day boundaries and aggregates collection velocity over time."
    ])

create_card(slide8, Inches(4.8), Inches(4.5), Inches(3.7), Inches(2.4),
    "Pipeline 4: Custody Lookup",
    [
        "Stages: $match → $lookup → $project",
        "Combines batches, facilities, and timeline events for public transparency views."
    ])

create_card(slide8, Inches(8.8), Inches(4.5), Inches(3.7), Inches(2.4),
    "Pipeline 5: Multi-Facet KPI",
    [
        "Stages: $facet",
        "Executes status counts, mass sums, and category shares in a single database round-trip."
    ])


# ==============================================================================
# SLIDE 9: Mass Balance Reconciliation & Integrity
# ==============================================================================
slide9 = prs.slides.add_slide(blank_layout)
add_header(slide9, "8. Mass-Balance Verification & Fraud Prevention")

create_card(slide9, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
    "The Mass Reconciliation Law",
    [
        "Mathematical Equation Enforced:",
        "Input Mass = Recycled Output + Contaminants Rejected + Residual Mass",
        "Acceptable Variance Tolerance: ±5% (allows for moisture loss / volatile reduction).",
        "Fraud Detection Logic:",
        "If Recycled Output > Input Mass → Immediate Rejection (Yield Fraud).",
        "If Discrepancy > 5% → Batch marked discrepancy_flagged = True.",
        "Flagged batches are withheld from citizen certification until an auditor performs physical verification."
    ],
    header_color=FOREST_GREEN)

create_card(slide9, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0),
    "Two-Man Rule Verification",
    [
        "Facility Operator Responsibility:",
        "Submits quantitative report and uploads weighbridge scale photos.",
        "Cannot self-approve or certify recycling output.",
        "Auditor / Administrator Responsibility:",
        "Cross-checks photographic proofs against scale metrics.",
        "Explicitly clicks 'Approve' or 'Reject' in Evidence Review console.",
        "Guarantees that no waste is ever marked as recycled without cryptographic accountability."
    ],
    header_color=FOREST_GREEN, bg_color=RGBColor(240, 253, 244), border_color=EMERALD)


# ==============================================================================
# SLIDE 10: Testing, Security & Quality Assurance
# ==============================================================================
slide10 = prs.slides.add_slide(blank_layout)
add_header(slide10, "9. Automated Testing & Security Controls")

create_card(slide10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
    "22 Automated Pytest Tests (100% Pass)",
    [
        "1. test_auth.py (6 tests):",
        "User registration, password hashing, role restrictions, and duplicate email prevention.",
        "2. test_batches.py (3 tests):",
        "Batch creation, pickup confirmations, and invalid status transition prevention.",
        "3. test_verification.py (2 tests):",
        "Mass-balance math formulas and auditor approval state machine.",
        "4. test_analytics.py (5 tests):",
        "Verifies all 5 aggregation pipelines execute and yield correct BSON structures.",
        "5. test_mongodb_audit.py (6 tests):",
        "Empirical proof of $jsonSchema rejections and unique index constraints."
    ],
    header_color=FOREST_GREEN)

create_card(slide10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0),
    "Application Security Measures",
    [
        "1. Privacy Redaction on Public QR Views:",
        "Public endpoints (/track/<id>) redact citizen name, home address, and phone numbers.",
        "2. Role-Based Access Control (RBAC):",
        "Endpoints protected by session-based decorators (@requires_role). Citizens cannot access facility or admin routes.",
        "3. Cryptographic Storage:",
        "Passwords hashed using PBKDF2:SHA256 via Werkzeug security.",
        "4. Write-Only Audit Ledger:",
        "All security events permanently appended to audit_logs collection."
    ],
    header_color=FOREST_GREEN)


# ==============================================================================
# SLIDE 11: Conclusion & Project Links (Dark Theme)
# ==============================================================================
slide11 = prs.slides.add_slide(blank_layout)
bg11 = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
bg11.fill.solid()
bg11.fill.fore_color.rgb = DARK_BG
bg11.line.color.rgb = DARK_BG

header_box = slide11.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(11.0), Inches(1.2))
tf11 = header_box.text_frame
tf11.word_wrap = True
p11 = tf11.paragraphs[0]
p11.text = "10. Conclusion & Demonstration"
p11.font.size = Pt(32)
p11.font.bold = True
p11.font.color.rgb = CARD_BG

p11_sub = tf11.add_paragraph()
p11_sub.text = "RecycleTrace brings cryptographic transparency and NoSQL database rigor to municipal recycling."
p11_sub.font.size = Pt(16)
p11_sub.font.color.rgb = EMERALD
p11_sub.space_before = Pt(4)

# 2 Summary Cards
card_a = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(2.6), Inches(5.3), Inches(4.0))
card_a.fill.solid()
card_a.fill.fore_color.rgb = RGBColor(30, 41, 59)
card_a.line.color.rgb = RGBColor(51, 65, 85)
tf_a = card_a.text_frame
tf_a.word_wrap = True
p_at = tf_a.paragraphs[0]
p_at.text = "Academic Deliverables Completed"
p_at.font.size = Pt(18)
p_at.font.bold = True
p_at.font.color.rgb = MINT_LIGHT
p_at.space_after = Pt(10)

for bullet in [
    "Full-stack web platform built with Flask, PyMongo, and MongoDB 8.x.",
    "Engine-level $jsonSchema validators protecting all collections.",
    "Compound unique indexes benchmarked with live .explain() statistics.",
    "Five advanced multi-stage aggregation pipelines implemented and verified.",
    "100% test coverage with 22 automated pytest unit and integration tests.",
    "7-page academic technical project report compiled."
]:
    p_b = tf_a.add_paragraph()
    p_b.text = "✓ " + bullet
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = CARD_BG
    p_b.space_after = Pt(6)

card_b = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.6), Inches(5.3), Inches(4.0))
card_b.fill.solid()
card_b.fill.fore_color.rgb = RGBColor(30, 41, 59)
card_b.line.color.rgb = RGBColor(51, 65, 85)
tf_b = card_b.text_frame
tf_b.word_wrap = True
p_bt = tf_b.paragraphs[0]
p_bt.text = "Live Demonstration & Resources"
p_bt.font.size = Pt(18)
p_bt.font.bold = True
p_bt.font.color.rgb = EMERALD
p_bt.space_after = Pt(10)

for bullet in [
    "GitHub Repository: github.com/AbhiAvinashhh/RecycleTrace",
    "Live Web Application: http://127.0.0.1:5000",
    "Public Verification Demo: /track/WT-2026-1001",
    "Admin Credentials: admin@demo.com (Password: Demo1234!)",
    "MongoDB Shell Script: demo_queries.mongosh.js",
    "Thank you! Ready for questions and live walkthrough."
]:
    p_b = tf_b.add_paragraph()
    p_b.text = "🔗 " + bullet
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = CARD_BG
    p_b.space_after = Pt(8)

output_path = os.path.join(r"d:\Downloads\pymong\recycletrace\presentation", "RecycleTrace_Academic_Presentation.pptx")
prs.save(output_path)
print(f"[✓] Presentation generated successfully: {output_path}")
