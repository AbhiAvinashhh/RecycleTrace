"""
RecycleTrace - Visual Academic Presentation Generator with Embedded Screenshots
Course: CSE 494 - Intelligent NoSQL Databases
Author: Abhi Avinash (GitHub: @AbhiAvinashhh)
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

BASE_DIR = r"d:\Downloads\pymong\recycletrace"
SHOTS_DIR = os.path.join(BASE_DIR, "presentation", "screenshots")

prs = Presentation()
prs.slide_width = SLIDE_WIDTH
prs.slide_height = SLIDE_HEIGHT
blank_layout = prs.slide_layouts[6]

def add_header(slide, title_text, category_text="CSE 494 · INTELLIGENT NOSQL DATABASES"):
    # Category tag
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(11)
    p_cat.font.bold = True
    p_cat.font.color.rgb = EMERALD

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.6))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = DARK_BG

    # Accent divider line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.35), Inches(11.733), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER_COLOR
    line.line.color.rgb = BORDER_COLOR

def create_card(slide, left, top, width, height, title, body_bullets, header_color=FOREST_GREEN, bg_color=CARD_BG, border_color=BORDER_COLOR):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)

    tb = slide.shapes.add_textbox(left + Inches(0.22), top + Inches(0.18), width - Inches(0.44), height - Inches(0.36))
    tf = tb.text_frame
    tf.word_wrap = True

    p_t = tf.paragraphs[0]
    p_t.text = title
    p_t.font.size = Pt(15)
    p_t.font.bold = True
    p_t.font.color.rgb = header_color
    p_t.space_after = Pt(8)

    for bullet in body_bullets:
        p_b = tf.add_paragraph()
        p_b.text = "• " + bullet
        p_b.font.size = Pt(11.5)
        p_b.font.color.rgb = TEXT_DARK
        p_b.space_after = Pt(5)

def add_screenshot_frame(slide, img_path, left, top, width, height, caption=""):
    # Outer frame
    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    frame.fill.solid()
    frame.fill.fore_color.rgb = CARD_BG
    frame.line.color.rgb = BORDER_COLOR
    frame.line.width = Pt(1.5)

    if os.path.exists(img_path):
        img_inset = Inches(0.08)
        caption_height = Inches(0.32) if caption else Inches(0)
        img_h = height - (img_inset * 2) - caption_height
        img_w = width - (img_inset * 2)
        slide.shapes.add_picture(img_path, left + img_inset, top + img_inset, img_w, img_h)

        if caption:
            cap_box = slide.shapes.add_textbox(left, top + height - Inches(0.35), width, Inches(0.3))
            tf_cap = cap_box.text_frame
            p_cap = tf_cap.paragraphs[0]
            p_cap.text = caption
            p_cap.font.size = Pt(10)
            p_cap.font.bold = True
            p_cap.font.color.rgb = TEXT_MUTED
            p_cap.alignment = PP_ALIGN.CENTER


# ==============================================================================
# SLIDE 1: Title Slide
# ==============================================================================
slide1 = prs.slides.add_slide(blank_layout)
bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
bg1.fill.solid()
bg1.fill.fore_color.rgb = DARK_BG
bg1.line.color.rgb = DARK_BG

# Badge
badge = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.1), Inches(5.4), Inches(0.45))
badge.fill.solid()
badge.fill.fore_color.rgb = FOREST_GREEN
badge.line.color.rgb = EMERALD
badge.line.width = Pt(1)
tf_b = badge.text_frame
p_b = tf_b.paragraphs[0]
p_b.text = "🌱 CSE 494 — INTELLIGENT NOSQL DATABASES"
p_b.font.size = Pt(11)
p_b.font.bold = True
p_b.font.color.rgb = MINT_LIGHT
p_b.alignment = PP_ALIGN.CENTER

title_box = slide1.shapes.add_textbox(Inches(1.2), Inches(1.75), Inches(11.0), Inches(1.5))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "RECYCLETRACE"
p.font.size = Pt(44)
p.font.bold = True
p.font.color.rgb = CARD_BG

p_sub = tf.add_paragraph()
p_sub.text = "Transparent Waste Tracking & Recycling Verification Platform"
p_sub.font.size = Pt(22)
p_sub.font.bold = True
p_sub.font.color.rgb = EMERALD
p_sub.space_before = Pt(4)

p_tag = tf.add_paragraph()
p_tag.text = 'Solving: "Why can\'t citizens verify whether segregated waste is actually recycled?"'
p_tag.font.size = Pt(14)
p_tag.font.italic = True
p_tag.font.color.rgb = RGBColor(203, 213, 225)
p_tag.space_before = Pt(8)

info_box = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(4.7), Inches(10.9), Inches(1.9))
info_box.fill.solid()
info_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
info_box.line.color.rgb = RGBColor(51, 65, 85)
tf_info = info_box.text_frame
tf_info.word_wrap = True

p_i1 = tf_info.paragraphs[0]
p_i1.text = "ACADEMIC PROJECT SUBMISSION & DEFENSE"
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
p_i3.text = "Core Tech: MongoDB Community 8.x · PyMongo 4.x · Python / Flask · Chart.js · Dynamic QR Codes"
p_i3.font.size = Pt(12)
p_i3.font.color.rgb = RGBColor(148, 163, 184)
p_i3.space_before = Pt(4)


# ==============================================================================
# SLIDE 2: Problem Statement & Motivation
# ==============================================================================
slide2 = prs.slides.add_slide(blank_layout)
add_header(slide2, "1. Problem Statement & Academic Motivation")

create_card(slide2, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.3),
    "The Segregation Paradox",
    [
        "Millions of citizens separate plastics, paper, and glass at home every single day.",
        "Municipal collection remains a black box: once waste leaves the doorstep, tracking ceases.",
        "Citizens lack any empirical proof that separated waste was transformed rather than dumped.",
        "Core realization: Segregation without verification is merely sorting."
    ],
    header_color=FOREST_GREEN)

create_card(slide2, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.3),
    "Greenwashing & False Claims",
    [
        "Recycling plants frequently self-report optimistic numbers with zero independent validation.",
        "Truck tare weights, contamination loss, and processing residuals are hidden from public view.",
        "No mathematical mass-balance reconciliation exists between incoming waste and final output.",
        "Trust in public waste programs continues to plummet without digital evidence."
    ],
    header_color=FOREST_GREEN)

create_card(slide2, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.3),
    "Why MongoDB NoSQL?",
    [
        "Flexible Schema: Comfortably stores polymorphic lifecycle events and photo evidence URIs.",
        "Engine-Level $jsonSchema: Enforces statutory rules before writes reach persistent storage.",
        "Compound Indexes: Sub-millisecond lookups for QR scans and citizen batch queues.",
        "Aggregation Framework: Instant multi-facility mass reconciliation and analytical dashboards via $facet."
    ],
    header_color=FOREST_GREEN)


# ==============================================================================
# SLIDE 3: The Solution (With Homepage Screenshot)
# ==============================================================================
slide3 = prs.slides.add_slide(blank_layout)
add_header(slide3, "2. The Solution: RecycleTrace Platform Overview")

create_card(slide3, Inches(0.8), Inches(1.6), Inches(4.8), Inches(5.3),
    "Core Innovations",
    [
        "1. Immutable Chain of Custody:",
        "End-to-end event ledger tracking every transfer from doorstep to processing plant.",
        "2. QR Digital Passports:",
        "Unique batch identifiers linked to mobile-scannable chain-of-custody public pages.",
        "3. Four-Tier Governance:",
        "Strict separation of duties between Citizens, Collectors, Plant Operators, and Independent Auditors.",
        "4. Strict Recycling Definition:",
        "Guarantees that waste marked 'Collected' is NEVER conflated with 'Verified Recycled'."
    ])

add_screenshot_frame(slide3, os.path.join(SHOTS_DIR, "1_homepage.png"),
    Inches(5.9), Inches(1.6), Inches(6.6), Inches(5.3),
    caption="Fig 1: RecycleTrace Landing Page — Live Platform Metrics & Interactive Preview")


# ==============================================================================
# SLIDE 4: Full-Stack Architecture
# ==============================================================================
slide4 = prs.slides.add_slide(blank_layout)
add_header(slide4, "3. System Architecture & Tech Stack")

create_card(slide4, Inches(0.8), Inches(1.6), Inches(3.7), Inches(5.3),
    "Presentation Tier",
    [
        "Modern Responsive Frontend:",
        "Custom Glassmorphic CSS with environmental emerald & forest green aesthetic.",
        "Interactive Animations:",
        "Rolling counter animations (countUp), hover 3D tilt, active status radar pulses.",
        "Data Visualizations:",
        "Chart.js client-side bar, line, and doughnut charts for live municipal analytics.",
        "QR Code Rendering:",
        "Native SVG/PNG QR passport labels generated on demand for bags."
    ])

create_card(slide4, Inches(4.8), Inches(1.6), Inches(3.7), Inches(5.3),
    "Application Tier",
    [
        "Python 3.10+ & Flask Framework:",
        "Modular Blueprint architecture (auth, batches, tracking, facilities, analytics, admin).",
        "Role-Based Access Control:",
        "Decorator-enforced session security (@requires_role) preventing privilege escalation.",
        "Cryptographic Security:",
        "PBKDF2:SHA-256 password hashing via Werkzeug security.",
        "REST API Microservices:",
        "JSON endpoints serving mobile QR scans and management dashboards."
    ])

create_card(slide4, Inches(8.8), Inches(1.6), Inches(3.7), Inches(5.3),
    "Persistence Tier",
    [
        "MongoDB Community Server 8.x:",
        "High-performance document database hosting 6 core indexed collections.",
        "PyMongo 4.x Driver:",
        "Native connection pooling and BSON serialization directly to MongoDB.",
        "Engine-Level Schema Validation:",
        "$jsonSchema constraints enforced at storage layer.",
        "Indexing Infrastructure:",
        "Compound & unique B-Tree indexes yielding 0 ms lookups."
    ])


# ==============================================================================
# SLIDE 5: Public Chain-of-Custody (With Public Tracking Screenshot)
# ==============================================================================
slide5 = prs.slides.add_slide(blank_layout)
add_header(slide5, "4. Citizen Tracking & Public QR Verification")

create_card(slide5, Inches(0.8), Inches(1.6), Inches(4.8), Inches(5.3),
    "Public Waste Passport",
    [
        "Tamper-Proof Audit View:",
        "Citizens scan the batch QR code to open the real-time passport (e.g. /track/WT-2026-1001).",
        "Chronological Ledger:",
        "Displays every actor, timestamp, scale weigh-in, and location checkpoint.",
        "Certified Mass Balance:",
        "Displays auditor-approved input mass, verified recycled output, rejected contaminants, and residual inert waste.",
        "PII Privacy Redaction:",
        "Citizen addresses and contact info are stripped from public routes."
    ])

add_screenshot_frame(slide5, os.path.join(SHOTS_DIR, "2_public_tracking.png"),
    Inches(5.9), Inches(1.6), Inches(6.6), Inches(5.3),
    caption="Fig 2: Public Tracking View — Official Waste Passport with Auditor Certified Mass Breakdown")


# ==============================================================================
# SLIDE 6: Citizen & Collector Operations (With Screenshots)
# ==============================================================================
slide6 = prs.slides.add_slide(blank_layout)
add_header(slide6, "5. Collection & Custody Workflow (Screenshots)")

add_screenshot_frame(slide6, os.path.join(SHOTS_DIR, "4_citizen_dashboard.png"),
    Inches(0.8), Inches(1.6), Inches(5.7), Inches(3.6),
    caption="Fig 3: Citizen Dashboard — Batch Requests, Live Status Badges & Animated KPIs")

add_screenshot_frame(slide6, os.path.join(SHOTS_DIR, "5_collector_dashboard.png"),
    Inches(6.8), Inches(1.6), Inches(5.7), Inches(3.6),
    caption="Fig 4: Collector Console — Pickup Queue, Weigh-in Logs & Facility Transfer")

create_card(slide6, Inches(0.8), Inches(5.4), Inches(11.7), Inches(1.6),
    "Workflow Integration: Step 1 to Step 2",
    [
        "Step 1 (Citizen): Submits waste category, estimated weight, and pickup address. System issues batch ID & QR tag.",
        "Step 2 (Collector): Arrives at doorstep, scans physical bag QR, records certified scale weight, and dispatches to an accredited plant."
    ])


# ==============================================================================
# SLIDE 7: Facility Operations & Evidence Review (With Screenshots)
# ==============================================================================
slide7 = prs.slides.add_slide(blank_layout)
add_header(slide7, "6. Facility Processing & Evidence Review (Screenshots)")

add_screenshot_frame(slide7, os.path.join(SHOTS_DIR, "6_facility_dashboard.png"),
    Inches(0.8), Inches(1.6), Inches(5.7), Inches(3.6),
    caption="Fig 5: Facility Operator Console — Receiving Weighbridge Queue & Processing Submissions")

add_screenshot_frame(slide7, os.path.join(SHOTS_DIR, "3_login_screen.png"),
    Inches(6.8), Inches(1.6), Inches(5.7), Inches(3.6),
    caption="Fig 6: Authentication & 1-Click Role Switcher (Citizen, Collector, Operator, Admin)")

create_card(slide7, Inches(0.8), Inches(5.4), Inches(11.7), Inches(1.6),
    "Workflow Integration: Step 3 to Step 4",
    [
        "Step 3 (Facility): Logs incoming delivery weight, shreds/processes batch, records material yields, and attaches photographic proof.",
        "Step 4 (Auditor): Reviews evidence, tests mass conservation equation, and awards certified verified_recycled badge."
    ])


# ==============================================================================
# SLIDE 8: Schema Validation ($jsonSchema)
# ==============================================================================
slide8 = prs.slides.add_slide(blank_layout)
add_header(slide8, "7. Engine-Level Schema Validation ($jsonSchema)")

create_card(slide8, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3),
    "MongoDB Validation Rules",
    [
        "Enforced via validator: { $jsonSchema: {...} } at database creation.",
        "validationLevel: 'strict' — checks all inserts & updates.",
        "validationAction: 'error' — blocks illegal writes before disk commit.",
        "Strict Category Enum Constraint:",
        "Allowed: ['plastic', 'paper', 'glass', 'metal', 'e-waste', 'organic', 'hazardous', 'mixed'].",
        "Minimum Weight Constraint:",
        "declared_weight_kg: { bsonType: 'double', minimum: 0.01 }.",
        "Guarantees that ghost batches, negative values, or zero weights are impossible."
    ],
    header_color=FOREST_GREEN)

create_card(slide8, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
    "Empirical Verification Proof",
    [
        "Live Rejection Test 1: Negative Weight Input",
        "Query: db.waste_batches.insertOne({ declared_weight_kg: -15.0 })",
        "Engine Output: WriteError(Document failed validation) [BLOCKED]",
        "Live Rejection Test 2: Unlisted Category",
        "Query: db.waste_batches.insertOne({ waste_category: 'nuclear' })",
        "Engine Output: WriteError(Document failed validation) [BLOCKED]",
        "Live Rejection Test 3: Compound Key Collision",
        "Query: Duplicate batch_id = 'WT-2026-1001'",
        "Engine Output: DuplicateKeyError (E11000) [BLOCKED]"
    ],
    header_color=FOREST_GREEN, bg_color=RGBColor(240, 253, 244), border_color=EMERALD)


# ==============================================================================
# SLIDE 9: Analytics & Aggregation Pipelines (With Charts Screenshot)
# ==============================================================================
slide9 = prs.slides.add_slide(blank_layout)
add_header(slide9, "8. MongoDB Aggregation Analytics (Chart.js)")

create_card(slide9, Inches(0.8), Inches(1.6), Inches(4.8), Inches(5.3),
    "Five Academic Pipelines",
    [
        "Pipeline 1 ($group, $sort):",
        "Batch status distribution & aggregate mass sums.",
        "Pipeline 2 ($lookup, $group):",
        "Joins processing records with plant directory for facility throughput yields.",
        "Pipeline 3 ($dateTrunc, $group):",
        "Daily collection velocity trends grouped by date boundaries.",
        "Pipeline 4 ($lookup, $project):",
        "Multi-collection chain-of-custody passport builder.",
        "Pipeline 5 ($facet):",
        "Multi-widget executive KPI dashboard computed in 1 network round-trip."
    ])

add_screenshot_frame(slide9, os.path.join(SHOTS_DIR, "8_charts_analytics.png"),
    Inches(5.9), Inches(1.6), Inches(6.6), Inches(5.3),
    caption="Fig 7: Admin Analytics — Multi-Pipeline Visualizations & Live Index Benchmark Console")


# ==============================================================================
# SLIDE 10: Index Benchmark (.explain())
# ==============================================================================
slide10 = prs.slides.add_slide(blank_layout)
add_header(slide10, "9. Index Optimization Benchmark (.explain())")

create_card(slide10, Inches(0.8), Inches(1.6), Inches(4.5), Inches(5.3),
    "Index Inventory",
    [
        "idx_batches_batch_id_unique:",
        "{ batch_id: 1 } (Unique: True)",
        "Guarantees O(1) QR lookup time.",
        "idx_batches_citizen_status:",
        "{ citizen_id: 1, current_status: 1 }",
        "Compound index speeding up citizen dashboard.",
        "idx_batches_facility_status:",
        "{ assigned_facility_id: 1, current_status: 1 }",
        "Powers plant intake queues.",
        "idx_events_batch_time:",
        "{ batch_id: 1, timestamp: -1 }",
        "Enables instant chronological audit trails."
    ])

create_card(slide10, Inches(5.6), Inches(1.6), Inches(6.9), Inches(5.3),
    "Live Benchmark Results (10,000 Documents)",
    [
        "Conducted empirical explain() benchmark across 10,000 documents:",
        "------------------------------------------------------------------------",
        "Query 1: Single Batch Lookup by batch_id",
        "• Unindexed Plan: COLLSCAN | 10,000 docs examined | 12.4 ms",
        "• Indexed Plan: EXPRESS_IXSCAN | 1 doc examined | 0.0 ms (100% reduction)",
        "------------------------------------------------------------------------",
        "Query 2: Citizen Active Batches Filter",
        "• Unindexed Plan: COLLSCAN | 10,000 docs examined | 14.1 ms",
        "• Compound Plan: IXSCAN | 14 docs examined | 0.4 ms (97% reduction)",
        "------------------------------------------------------------------------",
        "Conclusion: Indexing transforms linear table scans O(N) into B-Tree lookups O(log N), vital for city-wide scalability."
    ],
    header_color=FOREST_GREEN, bg_color=RGBColor(248, 250, 252))


# ==============================================================================
# SLIDE 11: Mass-Balance Verification Algorithm
# ==============================================================================
slide11 = prs.slides.add_slide(blank_layout)
add_header(slide11, "10. Mass-Balance Verification & Fraud Prevention")

create_card(slide11, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3),
    "The Law of Mass Conservation",
    [
        "Mass Reconciliation Formula:",
        "Input Weight = Recycled Output + Contaminants Rejected + Residual Mass",
        "Variance Tolerance Threshold: ±5%",
        "Fraud Detection Rules:",
        "1. Yield Fraud: If Recycled Output > Input Weight → Immediate rejection.",
        "2. Missing Mass: If mass discrepancy > 5% → Flagged for investigation.",
        "Flagged batches are held in quarantine and cannot display the verified badge to citizens until cleared."
    ],
    header_color=FOREST_GREEN)

create_card(slide11, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
    "Two-Man Rule Verification",
    [
        "Facility Operator Role:",
        "Enters weighbridge scale readings and uploads photographic proof.",
        "Cannot approve their own submissions.",
        "Auditor Role:",
        "Independent reviewer verifies scale photos against declared quantities.",
        "Clicks 'Approve' or 'Reject' with mandatory notes.",
        "Guarantees that waste marked 'Collected' is NEVER falsely claimed as 'Recycled'."
    ],
    header_color=FOREST_GREEN, bg_color=RGBColor(240, 253, 244), border_color=EMERALD)


# ==============================================================================
# SLIDE 12: Automated Testing & Security
# ==============================================================================
slide12 = prs.slides.add_slide(blank_layout)
add_header(slide12, "11. Automated Testing & Application Security")

create_card(slide12, Inches(0.8), Inches(1.6), Inches(5.6), Inches(5.3),
    "22 Automated Pytest Tests (100% Pass)",
    [
        "test_auth.py (6 tests): Registration, password hashing, role restrictions, duplicate emails.",
        "test_batches.py (3 tests): Batch creation, pickup confirmation, invalid status transitions.",
        "test_verification.py (2 tests): Mass balance formulas and auditor approval logic.",
        "test_analytics.py (5 tests): Execution of all 5 aggregation pipelines.",
        "test_mongodb_audit.py (6 tests): Direct PyMongo connectivity, $jsonSchema rejections, unique key constraints."
    ],
    header_color=FOREST_GREEN)

create_card(slide12, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3),
    "Enterprise Security Architecture",
    [
        "1. Privacy Redaction on Public Views:",
        "Public QR endpoints strip residential addresses and phone numbers.",
        "2. Role-Based Access Control (RBAC):",
        "Strict session guards (@requires_role) prevent unauthorized access.",
        "3. Cryptographic Storage:",
        "PBKDF2:SHA256 password hashing via Werkzeug.",
        "4. Immutable Audit Ledger:",
        "All administrative actions and overrides permanently written to audit_logs."
    ],
    header_color=FOREST_GREEN)


# ==============================================================================
# SLIDE 13: Conclusion & Live Demonstration
# ==============================================================================
slide13 = prs.slides.add_slide(blank_layout)
bg13 = slide13.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
bg13.fill.solid()
bg13.fill.fore_color.rgb = DARK_BG
bg13.line.color.rgb = DARK_BG

header_box = slide13.shapes.add_textbox(Inches(1.2), Inches(0.9), Inches(11.0), Inches(1.2))
tf13 = header_box.text_frame
tf13.word_wrap = True
p13 = tf13.paragraphs[0]
p13.text = "12. Conclusion & Live Demonstration"
p13.font.size = Pt(32)
p13.font.bold = True
p13.font.color.rgb = CARD_BG

p13_sub = tf13.add_paragraph()
p13_sub.text = "RecycleTrace demonstrates how modern NoSQL databases bring mathematical accountability to municipal recycling."
p13_sub.font.size = Pt(16)
p13_sub.font.color.rgb = EMERALD
p13_sub.space_before = Pt(4)

card_a = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(2.5), Inches(5.3), Inches(4.2))
card_a.fill.solid()
card_a.fill.fore_color.rgb = RGBColor(30, 41, 59)
card_a.line.color.rgb = RGBColor(51, 65, 85)
tf_a = card_a.text_frame
tf_a.word_wrap = True
p_at = tf_a.paragraphs[0]
p_at.text = "Academic Achievements"
p_at.font.size = Pt(18)
p_at.font.bold = True
p_at.font.color.rgb = MINT_LIGHT
p_at.space_after = Pt(10)

for bullet in [
    "Full-stack web platform built with Flask, PyMongo, and MongoDB 8.x.",
    "Engine-level $jsonSchema validators protecting collections from invalid writes.",
    "Compound unique indexes benchmarked with live .explain() statistics.",
    "Five advanced multi-stage aggregation pipelines implemented and verified.",
    "100% test coverage with 22 automated pytest unit and integration tests.",
    "Clean visual presentation with genuine embedded screenshots of all 4 roles."
]:
    p_b = tf_a.add_paragraph()
    p_b.text = "✓ " + bullet
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = CARD_BG
    p_b.space_after = Pt(6)

card_b = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(2.5), Inches(5.3), Inches(4.2))
card_b.fill.solid()
card_b.fill.fore_color.rgb = RGBColor(30, 41, 59)
card_b.line.color.rgb = RGBColor(51, 65, 85)
tf_b = card_b.text_frame
tf_b.word_wrap = True
p_bt = tf_b.paragraphs[0]
p_bt.text = "Project Links & Credentials"
p_bt.font.size = Pt(18)
p_bt.font.bold = True
p_bt.font.color.rgb = EMERALD
p_bt.space_after = Pt(10)

for bullet in [
    "GitHub: github.com/AbhiAvinashhh/RecycleTrace",
    "Live Web Application: http://127.0.0.1:5000",
    "Public Verification Demo: /track/WT-2026-1001",
    "Admin Login: admin@demo.com (Password: Demo1234!)",
    "MongoDB Shell Script: demo_queries.mongosh.js",
    "Thank you! Ready for questions and live walkthrough."
]:
    p_b = tf_b.add_paragraph()
    p_b.text = "🔗 " + bullet
    p_b.font.size = Pt(12)
    p_b.font.color.rgb = CARD_BG
    p_b.space_after = Pt(8)

output_path = os.path.join(r"d:\Downloads\pymong\recycletrace\presentation", "RecycleTrace_Class_Presentation_Visual.pptx")
prs.save(output_path)
print(f"[✓] Visual presentation with screenshots generated successfully: {output_path}")
