"""
RecycleTrace - Gamma.ai / Gamma.app Styled Presentation Generator
Generates an ultra-modern, dark-themed, card-based academic presentation with screenshots.
Course: CSE 494 - Intelligent NoSQL Databases
Author: Abhi Avinash (GitHub: @AbhiAvinashhh)
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

# Gamma.ai Modern Dark Palette
CANVAS_BG = RGBColor(10, 15, 28)       # Ultra dark obsidian slate #0A0F1C
CARD_BG = RGBColor(19, 27, 46)         # Elevated card #131B2E
CARD_BORDER = RGBColor(33, 46, 74)     # Crisp border #212E4A
PILL_BG = RGBColor(16, 42, 36)         # Deep emerald glow #102A24
PILL_BORDER = RGBColor(16, 185, 129)   # Emerald border #10B981

# Accents
EMERALD = RGBColor(16, 185, 129)       # Vibrant Emerald #10B981
MINT = RGBColor(110, 231, 183)         # Bright highlight #6EE7B7
CYAN = RGBColor(56, 189, 248)          # Electric Cyan #38BDF8
AMBER = RGBColor(251, 191, 36)         # Golden Amber #FBBF24
ROSE = RGBColor(244, 63, 94)           # Rose #F43F5E

# Typography Colors
TEXT_WHITE = RGBColor(248, 250, 252)   # Pure text #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)   # Secondary text #94A3B8
TEXT_DIM = RGBColor(100, 116, 139)     # Dim annotations #64748B

BASE_DIR = r"d:\Downloads\pymong\recycletrace"
SHOTS_DIR = os.path.join(BASE_DIR, "presentation", "screenshots")

prs = Presentation()
prs.slide_width = SLIDE_WIDTH
prs.slide_height = SLIDE_HEIGHT
blank_layout = prs.slide_layouts[6]

def create_base_slide():
    slide = prs.slides.add_slide(blank_layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT)
    bg.fill.solid()
    bg.fill.fore_color.rgb = CANVAS_BG
    bg.line.color.rgb = CANVAS_BG
    return slide

def add_gamma_header(slide, tag_text, title_text, subtitle_text=""):
    # Pill Badge (Gamma style)
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(4.5), Inches(0.38))
    badge.fill.solid()
    badge.fill.fore_color.rgb = PILL_BG
    badge.line.color.rgb = PILL_BORDER
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    tf_b.word_wrap = True
    p_b = tf_b.paragraphs[0]
    p_b.text = tag_text.upper()
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = MINT
    p_b.alignment = PP_ALIGN.CENTER

    # Main Headline
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.7), Inches(0.55))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = TEXT_WHITE

    # Optional Subtitle
    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.28), Inches(11.7), Inches(0.35))
        tf_s = sub_box.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        p_s.text = subtitle_text
        p_s.font.size = Pt(11.5)
        p_s.font.color.rgb = TEXT_MUTED

def add_gamma_card(slide, left, top, width, height, icon_and_title, items, accent_color=EMERALD):
    # Card container
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1)

    # Accent top border
    accent_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, Inches(0.06))
    accent_bar.fill.solid()
    accent_bar.fill.fore_color.rgb = accent_color
    accent_bar.line.color.rgb = accent_color

    tb = slide.shapes.add_textbox(left + Inches(0.24), top + Inches(0.18), width - Inches(0.48), height - Inches(0.32))
    tf = tb.text_frame
    tf.word_wrap = True

    # Title
    p_head = tf.paragraphs[0]
    p_head.text = icon_and_title
    p_head.font.size = Pt(14)
    p_head.font.bold = True
    p_head.font.color.rgb = TEXT_WHITE
    p_head.space_after = Pt(8)

    # Items
    for item in items:
        p_item = tf.add_paragraph()
        if isinstance(item, tuple):
            lead, desc = item
            p_item.text = f"• {lead}: "
            p_item.font.bold = True
            p_item.font.size = Pt(11)
            p_item.font.color.rgb = MINT
            # add run for desc
            run = p_item.add_run()
            run.text = desc
            run.font.bold = False
            run.font.color.rgb = TEXT_MUTED
        else:
            p_item.text = f"• {item}"
            p_item.font.size = Pt(11)
            p_item.font.color.rgb = TEXT_MUTED
        p_item.space_after = Pt(4)

def add_gamma_stat_card(slide, left, top, width, height, big_num, label, desc="", accent_color=EMERALD):
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = CARD_BG
    card.line.color.rgb = CARD_BORDER
    card.line.width = Pt(1)

    tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), height - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p_num = tf.paragraphs[0]
    p_num.text = big_num
    p_num.font.size = Pt(28)
    p_num.font.bold = True
    p_num.font.color.rgb = accent_color

    p_lbl = tf.add_paragraph()
    p_lbl.text = label
    p_lbl.font.size = Pt(11)
    p_lbl.font.bold = True
    p_lbl.font.color.rgb = TEXT_WHITE
    p_lbl.space_after = Pt(2)

    if desc:
        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(9.5)
        p_d.font.color.rgb = TEXT_MUTED

def add_browser_screenshot(slide, img_path, left, top, width, height, caption=""):
    # Window Frame Mockup (Gamma style)
    frame = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    frame.fill.solid()
    frame.fill.fore_color.rgb = CARD_BG
    frame.line.color.rgb = CARD_BORDER
    frame.line.width = Pt(1.2)

    # Window traffic light buttons
    for i, color in enumerate([ROSE, AMBER, EMERALD]):
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.2 + (i * 0.18)), top + Inches(0.12), Inches(0.09), Inches(0.09))
        dot.fill.solid()
        dot.fill.fore_color.rgb = color
        dot.line.color.rgb = color

    # Browser URL Bar
    url_bar = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.85), top + Inches(0.08), width - Inches(1.1), Inches(0.18))
    url_bar.fill.solid()
    url_bar.fill.fore_color.rgb = RGBColor(28, 38, 64)
    url_bar.line.color.rgb = RGBColor(38, 51, 84)
    tf_u = url_bar.text_frame
    p_u = tf_u.paragraphs[0]
    p_u.text = "🔒 https://recycletrace.local"
    p_u.font.size = Pt(8)
    p_u.font.color.rgb = TEXT_DIM

    # Insert Picture
    if os.path.exists(img_path):
        top_offset = Inches(0.32)
        bottom_offset = Inches(0.35) if caption else Inches(0.08)
        img_h = height - top_offset - bottom_offset
        img_w = width - Inches(0.16)
        slide.shapes.add_picture(img_path, left + Inches(0.08), top + top_offset, img_w, img_h)

        if caption:
            tb_cap = slide.shapes.add_textbox(left, top + height - Inches(0.32), width, Inches(0.28))
            tf_cap = tb_cap.text_frame
            p_cap = tf_cap.paragraphs[0]
            p_cap.text = caption
            p_cap.font.size = Pt(9.5)
            p_cap.font.bold = True
            p_cap.font.color.rgb = TEXT_MUTED
            p_cap.alignment = PP_ALIGN.CENTER


# ==============================================================================
# SLIDE 1: Title Cover (Gamma Hero Style)
# ==============================================================================
slide1 = create_base_slide()

badge1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.0), Inches(5.8), Inches(0.42))
badge1.fill.solid()
badge1.fill.fore_color.rgb = PILL_BG
badge1.line.color.rgb = PILL_BORDER
badge1.line.width = Pt(1.2)
tf_b1 = badge1.text_frame
p_b1 = tf_b1.paragraphs[0]
p_b1.text = "🌱 CSE 494 · INTELLIGENT NOSQL DATABASES · ACADEMIC DEFENSE"
p_b1.font.size = Pt(11)
p_b1.font.bold = True
p_b1.font.color.rgb = MINT
p_b1.alignment = PP_ALIGN.CENTER

title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(11.3), Inches(1.6))
tf = title_box.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.text = "RECYCLETRACE"
p.font.size = Pt(46)
p.font.bold = True
p.font.color.rgb = TEXT_WHITE

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
p_tag.font.color.rgb = TEXT_MUTED
p_tag.space_before = Pt(8)

# 3 Feature Pills
pill_data = [
    ("🗄️ MongoDB Community 8.x", "Indexed collections with engine-level $jsonSchema validation"),
    ("⚡ PyMongo 4.x & Python Flask", "REST API architecture with 4-tier Role-Based Access Control"),
    ("📊 5 Aggregation Pipelines", "Real-time analytics, daily trends velocity, and live executionStats")
]

for idx, (head, sub) in enumerate(pill_data):
    p_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0 + (idx * 3.85)), Inches(3.9), Inches(3.6), Inches(1.7))
    p_card.fill.solid()
    p_card.fill.fore_color.rgb = CARD_BG
    p_card.line.color.rgb = CARD_BORDER
    tf_p = p_card.text_frame
    tf_p.word_wrap = True
    p1 = tf_p.paragraphs[0]
    p1.text = head
    p1.font.size = Pt(13)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_after = Pt(6)
    p2 = tf_p.add_paragraph()
    p2.text = sub
    p2.font.size = Pt(10.5)
    p2.font.color.rgb = TEXT_MUTED

# Author footer banner
author_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.95), Inches(11.3), Inches(0.95))
author_card.fill.solid()
author_card.fill.fore_color.rgb = RGBColor(14, 21, 38)
author_card.line.color.rgb = RGBColor(28, 40, 68)
tf_a = author_card.text_frame
tf_a.word_wrap = True
p_a1 = tf_a.paragraphs[0]
p_a1.text = "Presented by: Abhi Avinash  ·  GitHub: https://github.com/AbhiAvinashhh/RecycleTrace"
p_a1.font.size = Pt(13)
p_a1.font.bold = True
p_a1.font.color.rgb = MINT
p_a2 = tf_a.add_paragraph()
p_a2.text = "Evaluation Criteria: NoSQL Schema Validation, Unique Compound Indexes, Aggregation Pipelines, and Benchmarking"
p_a2.font.size = Pt(10.5)
p_a2.font.color.rgb = TEXT_MUTED
p_a2.space_before = Pt(3)


# ==============================================================================
# SLIDE 2: Problem Statement & Motivation
# ==============================================================================
slide2 = create_base_slide()
add_gamma_header(slide2, "01 · THE PROBLEM", "The Municipal Recycling Black Box", "Why citizens lose faith in municipal waste segregation")

add_gamma_card(slide2, Inches(0.8), Inches(1.75), Inches(3.7), Inches(5.1),
    "1. The Segregation Paradox",
    [
        ("Household Diligence", "Citizens dutifully separate plastics, paper, and glass every day."),
        ("The Black Box", "Once waste leaves the doorstep, chain of custody instantly disappears."),
        ("No Proof", "Citizens have zero empirical evidence that their waste wasn't landfill-diverted."),
        ("Takeaway", "Segregation without verification is merely sorting.")
    ],
    accent_color=ROSE)

add_gamma_card(slide2, Inches(4.8), Inches(1.75), Inches(3.7), Inches(5.1),
    "2. Greenwashing & Missing Math",
    [
        ("Self-Reported Figures", "Plants claim high recycling rates without scale-calibrated receipts."),
        ("Mass Loss Discrepancies", "Truck tare weight variances and missing mass are routinely ignored."),
        ("Zero Reconciliation", "No mathematical balance enforced between intake mass and output yield."),
        ("Relational SQL Limits", "Rigid table schemas fail to handle polymorphic custody events & photo proof.")
    ],
    accent_color=AMBER)

add_gamma_card(slide2, Inches(8.8), Inches(1.75), Inches(3.7), Inches(5.1),
    "3. Why MongoDB NoSQL?",
    [
        ("Dynamic Documents", "Effortlessly models polymorphic custody events & photo metadata."),
        ("Engine-Level $jsonSchema", "Enforces statutory mass rules directly at the database engine layer."),
        ("Sub-millisecond Lookups", "Compound indexes deliver instant QR verification in the field."),
        ("Multi-Stage $facet", "Aggregates complex municipal yields in a single database round-trip.")
    ],
    accent_color=EMERALD)


# ==============================================================================
# SLIDE 3: The Solution (With Homepage Screenshot)
# ==============================================================================
slide3 = create_base_slide()
add_gamma_header(slide3, "02 · THE PLATFORM", "RecycleTrace: Verifiable Chain of Custody", "An end-to-end transparent waste ledger with QR digital passports")

add_gamma_card(slide3, Inches(0.8), Inches(1.75), Inches(4.6), Inches(5.1),
    "Core Platform Capabilities",
    [
        ("Digital Passports", "Each batch is issued an immutable ID (e.g. WT-2026-1001) & QR code label."),
        ("Tamper-Proof Events", "Doorstep pickup, transport dispatch, and weighbridge intake are permanently signed."),
        ("Mass Reconciliation", "Strict conservation law: Input = Recycled Yield + Rejections + Residual."),
        ("Two-Man Rule", "Operators upload evidence; only independent auditors can approve certified status."),
        ("Statutory Separation", "'Collected' never equals 'Recycled' until mathematically validated.")
    ],
    accent_color=EMERALD)

add_browser_screenshot(slide3, os.path.join(SHOTS_DIR, "1_homepage.png"),
    Inches(5.7), Inches(1.75), Inches(6.8), Inches(5.1),
    caption="Live Application Homepage — Real-Time Municipal Metrics & Interactive 3D Preview")


# ==============================================================================
# SLIDE 4: System Architecture & 4-Tier Governance
# ==============================================================================
slide4 = create_base_slide()
add_gamma_header(slide4, "03 · ARCHITECTURE", "Four-Tier Role Governance & Stack", "Clean separation of responsibilities enforced across the platform")

add_gamma_card(slide4, Inches(0.8), Inches(1.75), Inches(2.75), Inches(5.1),
    "🏠 Citizen",
    [
        ("Declaration", "Logs category & estimated mass."),
        ("QR Generation", "Downloads printable batch QR label."),
        ("Live Tracking", "Watches batch custody checkpoints in real time."),
        ("Audited Yield", "Inspects verified recycling breakdown upon completion.")
    ],
    accent_color=CYAN)

add_gamma_card(slide4, Inches(3.75), Inches(1.75), Inches(2.75), Inches(5.1),
    "🚛 Collector",
    [
        ("Assignment Queue", "Views authorized pickup route."),
        ("Doorstep Weigh-in", "Scans physical bag QR & logs scale mass."),
        ("Custody Transfer", "Dispatches batch to an accredited recycling plant."),
        ("Audit Stamp", "Signs timestamp & geolocation.")
    ],
    accent_color=AMBER)

add_gamma_card(slide4, Inches(6.7), Inches(1.75), Inches(2.75), Inches(5.1),
    "🏭 Plant Operator",
    [
        ("Weighbridge Check-in", "Records mass on arrival."),
        ("Processing Yields", "Enters shredded/pelletized output quantities."),
        ("Proof Upload", "Attaches weighbridge receipt photos."),
        ("Audit Submission", "Submits report for auditor approval.")
    ],
    accent_color=MINT)

add_gamma_card(slide4, Inches(9.65), Inches(1.75), Inches(2.85), Inches(5.1),
    "🔍 Auditor / Admin",
    [
        ("Evidence Review", "Inspects receipts & photo evidence."),
        ("Math Reconciliation", "Verifies mass conservation formula."),
        ("Certification", "Awards verified_recycled badge."),
        ("Analytics & Logs", "Queries MongoDB aggregation KPIs & executionStats.")
    ],
    accent_color=ROSE)


# ==============================================================================
# SLIDE 5: MongoDB Document Data Modeling
# ==============================================================================
slide5 = create_base_slide()
add_gamma_header(slide5, "04 · DATA MODELING", "MongoDB Document Collections Architecture", "6 high-throughput collections balancing embedded events with referenced entities")

colls = [
    ("users", "Authentication & RBAC", "Email unique index, role enum constraint, Werkzeug PBKDF2:SHA256 password hashes.", CYAN),
    ("waste_batches", "Core Passport Entity", "Primary key batch_id, citizen_id, waste_category, declared_weight_kg, current_status.", EMERALD),
    ("tracking_events", "Immutable Event Stream", "Append-only chronological custody ledger. Indexed on (batch_id, timestamp) for rapid queries.", MINT),
    ("facilities", "Accredited Plant Registry", "facility_id, accepted_waste_types array, daily capacity, and verification status.", AMBER),
    ("processing_records", "Quantitative Yield Reports", "input_weight, recycled_output, rejected, residual weights, photo proof URIs & discrepancy flags.", ROSE),
    ("audit_logs", "Write-Only Security Audit", "Tamper-evident log of administrative approvals, logins, and status transitions.", CYAN)
]

for idx, (c_name, c_role, c_desc, c_color) in enumerate(colls):
    col = idx % 3
    row = idx // 3
    x = Inches(0.8 + (col * 3.95))
    y = Inches(1.75 + (row * 2.55))
    add_gamma_card(slide5, x, y, Inches(3.8), Inches(2.4),
        f"db.{c_name}",
        [
            ("Role", c_role),
            ("Details", c_desc)
        ],
        accent_color=c_color)


# ==============================================================================
# SLIDE 6: Engine-Level Schema Validation ($jsonSchema)
# ==============================================================================
slide6 = create_base_slide()
add_gamma_header(slide6, "05 · DATA INTEGRITY", "Engine-Level Schema Validation ($jsonSchema)", "Rejecting invalid records at the MongoDB storage engine layer")

add_gamma_card(slide6, Inches(0.8), Inches(1.75), Inches(5.6), Inches(5.1),
    "Enforced $jsonSchema Rules",
    [
        ("Engine Execution", "Enforced via validator: { $jsonSchema: {...} } at collection creation."),
        ("Strict Action", "validationAction: 'error' — blocks non-conforming writes before disk commit."),
        ("Category Enumeration", "Allowed values restricted to: ['plastic', 'paper', 'glass', 'metal', 'e-waste', 'organic', 'hazardous', 'mixed']."),
        ("Minimum Mass Threshold", "declared_weight_kg must satisfy minimum: 0.01 (double)."),
        ("Zero Ghost Batches", "Prevents negative weights, missing fields, or empty submissions.")
    ],
    accent_color=EMERALD)

add_gamma_card(slide6, Inches(6.8), Inches(1.75), Inches(5.7), Inches(5.1),
    "Live Empirical Rejection Proofs",
    [
        ("Test 1: Negative Weight Injection", "Attempt: Insert declared_weight_kg = -15.0 kg\nResult: WriteError(Document failed validation) [BLOCKED]"),
        ("Test 2: Unauthorized Category", "Attempt: Insert waste_category = 'nuclear'\nResult: WriteError(Document failed validation) [BLOCKED]"),
        ("Test 3: Duplicate Primary Key", "Attempt: Duplicate batch_id = 'WT-2026-1001'\nResult: DuplicateKeyError (E11000) [BLOCKED]"),
        ("Takeaway", "Data integrity is mathematically guaranteed by MongoDB, not just application code.")
    ],
    accent_color=MINT)


# ==============================================================================
# SLIDE 7: Collection & Custody Workflow (Screenshots)
# ==============================================================================
slide7 = create_base_slide()
add_gamma_header(slide7, "06 · FIELD WORKFLOW", "Citizen Requests & Doorstep Collection", "Live application screens showing batch initiation and pickup confirmation")

add_browser_screenshot(slide7, os.path.join(SHOTS_DIR, "4_citizen_dashboard.png"),
    Inches(0.8), Inches(1.75), Inches(5.7), Inches(3.6),
    caption="Fig 1: Citizen Dashboard — Live Status Badges, Batch History & Animated KPIs")

add_browser_screenshot(slide7, os.path.join(SHOTS_DIR, "5_collector_dashboard.png"),
    Inches(6.8), Inches(1.75), Inches(5.7), Inches(3.6),
    caption="Fig 2: Collector Console — Doorstep Weighbridge Scan & Inter-Facility Transfer")

add_gamma_card(slide7, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5),
    "Workflow Checkpoint 1 → Checkpoint 2",
    [
        ("Citizen Action", "Citizen registers waste category & estimated mass. System generates dynamic QR code passport."),
        ("Collector Action", "Collector arrives at doorstep, scans physical bag QR, enters scale weight, and assigns accredited plant.")
    ],
    accent_color=CYAN)


# ==============================================================================
# SLIDE 8: Facility Operations & Evidence Review (Screenshots)
# ==============================================================================
slide8 = create_base_slide()
add_gamma_header(slide8, "07 · PLANT & AUDIT", "Facility Processing & Evidence Review", "Weighbridge intake queue and 1-click role authentication")

add_browser_screenshot(slide8, os.path.join(SHOTS_DIR, "6_facility_dashboard.png"),
    Inches(0.8), Inches(1.75), Inches(5.7), Inches(3.6),
    caption="Fig 3: Facility Intake Dashboard — Incoming Transits & Processing Yield Queue")

add_browser_screenshot(slide8, os.path.join(SHOTS_DIR, "3_login_screen.png"),
    Inches(6.8), Inches(1.75), Inches(5.7), Inches(3.6),
    caption="Fig 4: Authentication Portal with 1-Click Role Switcher (Citizen, Collector, Operator, Admin)")

add_gamma_card(slide8, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5),
    "Workflow Checkpoint 3 → Checkpoint 4",
    [
        ("Facility Action", "Plant logs weighbridge arrival mass, enters refined yields (recycled, rejected, residual), and uploads proof photos."),
        ("Auditor Action", "Auditor inspects scale photos and mass balance; only auditor approval transitions batch to 'verified_recycled'.")
    ],
    accent_color=AMBER)


# ==============================================================================
# SLIDE 9: Public QR Verification Passport (Screenshot)
# ==============================================================================
slide9 = create_base_slide()
add_gamma_header(slide9, "08 · TRANSPARENCY", "Public QR Verification & Certified Passport", "Mobile-accessible public chain of custody with certified mass yield breakdown")

add_gamma_card(slide9, Inches(0.8), Inches(1.75), Inches(4.7), Inches(5.1),
    "Public Waste Passport Features",
    [
        ("Direct QR Access", "Scanning the bag QR opens the public view (/track/WT-2026-1001) on any smartphone."),
        ("Certified Mass Ledger", "Audited breakdown: Input Processed, Verified Recycled, Contaminants Rejected, and Residual."),
        ("Immutable Timeline", "Every custody handoff, weigh-in timestamp, and operator signature displayed chronologically."),
        ("Citizen Privacy", "Home addresses, contact numbers, and citizen IDs are automatically redacted for security.")
    ],
    accent_color=EMERALD)

add_browser_screenshot(slide9, os.path.join(SHOTS_DIR, "2_public_tracking.png"),
    Inches(5.8), Inches(1.75), Inches(6.7), Inches(5.1),
    caption="Fig 5: Public Chain-of-Custody Passport — Official Auditor-Approved Recycling Yield")


# ==============================================================================
# SLIDE 10: Aggregation Analytics Dashboard (Screenshot)
# ==============================================================================
slide10 = create_base_slide()
add_gamma_header(slide10, "09 · ANALYTICS", "Advanced MongoDB Aggregation Pipelines", "5 multi-stage pipelines powering Chart.js live municipal dashboards")

add_gamma_card(slide10, Inches(0.8), Inches(1.75), Inches(4.7), Inches(5.1),
    "Five Academic Pipelines",
    [
        ("Pipeline 1 ($group, $sort)", "Batch status distribution and cumulative mass calculations."),
        ("Pipeline 2 ($lookup, $group)", "Joins processing records with plant registry for throughput yields."),
        ("Pipeline 3 ($dateTrunc, $group)", "Daily collection velocity trends grouped by date boundaries."),
        ("Pipeline 4 ($lookup, $project)", "Multi-collection chain-of-custody passport builder."),
        ("Pipeline 5 ($facet)", "Multi-widget executive KPI dashboard computed in 1 single database round-trip.")
    ],
    accent_color=CYAN)

add_browser_screenshot(slide10, os.path.join(SHOTS_DIR, "8_charts_analytics.png"),
    Inches(5.8), Inches(1.75), Inches(6.7), Inches(5.1),
    caption="Fig 6: Admin Analytics Dashboard — Real-Time Chart.js Pipelines & Index Benchmark")


# ==============================================================================
# SLIDE 11: Index Benchmark (.explain())
# ==============================================================================
slide11 = create_base_slide()
add_gamma_header(slide11, "10 · BENCHMARKING", "Index Optimization Benchmark (.explain())", "Empirical performance measurement across 10,000 synthetic documents")

add_gamma_stat_card(slide11, Inches(0.8), Inches(1.75), Inches(3.6), Inches(1.55), "0.0 ms", "Indexed Lookup Time", "EXPRESS_IXSCAN winning stage", EMERALD)
add_gamma_stat_card(slide11, Inches(4.8), Inches(1.75), Inches(3.6), Inches(1.55), "1 Doc", "Documents Examined", "Down from 10,000 scanned", MINT)
add_gamma_stat_card(slide11, Inches(8.8), Inches(1.75), Inches(3.7), Inches(1.55), "100%", "Scan Reduction", "O(log N) B-Tree efficiency", CYAN)

add_gamma_card(slide11, Inches(0.8), Inches(3.5), Inches(5.6), Inches(3.4),
    "Index Inventory Strategy",
    [
        ("idx_batches_batch_id_unique", "{ batch_id: 1 } (Unique: True) guarantees O(1) QR lookup."),
        ("idx_batches_citizen_status", "{ citizen_id: 1, current_status: 1 } optimizes active queue queries."),
        ("idx_batches_facility_status", "{ assigned_facility_id: 1, current_status: 1 } powers plant queues."),
        ("idx_events_batch_time", "{ batch_id: 1, timestamp: -1 } enables instant timeline traversal.")
    ],
    accent_color=AMBER)

add_gamma_card(slide11, Inches(6.8), Inches(3.5), Inches(5.7), Inches(3.4),
    "Live 10,000-Doc Benchmark Results",
    [
        ("Single Batch Lookup (batch_id)", "Unindexed COLLSCAN: 10,000 docs scanned (12.4 ms)\nIndexed EXPRESS_IXSCAN: 1 doc scanned (0.0 ms)"),
        ("Citizen Active Filter (Compound)", "Unindexed COLLSCAN: 10,000 docs scanned (14.1 ms)\nCompound IXSCAN: 14 docs examined (0.4 ms)"),
        ("Conclusion", "Indexing transforms query complexity from linear O(N) to O(log N), vital for municipal scalability.")
    ],
    accent_color=EMERALD)


# ==============================================================================
# SLIDE 12: Mass-Balance Law & Fraud Detection
# ==============================================================================
slide12 = create_base_slide()
add_gamma_header(slide12, "11 · FRAUD DETECTION", "Mass-Balance Law & Fraud Prevention", "Mathematical mass conservation algorithm preventing recycling greenwashing")

add_gamma_card(slide12, Inches(0.8), Inches(1.75), Inches(5.6), Inches(5.1),
    "The Law of Mass Conservation",
    [
        ("Mathematical Balance", "Input Mass = Recycled Output + Contaminants + Residual Mass"),
        ("Variance Tolerance", "±5% allowed for moisture evaporation or volatile reduction."),
        ("Yield Fraud Alert", "If Recycled Output > Input Mass → Immediate rejection & auditor alert."),
        ("Missing Mass Alert", "If mass discrepancy > 5% → Marked discrepancy_flagged = True."),
        ("Quarantine State", "Flagged batches are held from citizen certification until cleared.")
    ],
    accent_color=ROSE)

add_gamma_card(slide12, Inches(6.8), Inches(1.75), Inches(5.7), Inches(5.1),
    "Two-Man Rule Verification",
    [
        ("Operator Separation", "Plant operators enter scale metrics and upload photos. Cannot self-approve."),
        ("Auditor Role", "Independent auditors review scale receipts against declared numbers."),
        ("Manual Approval", "Explicit click on 'Approve' or 'Reject' with mandatory audit notes."),
        ("Statutory Rule", "Guarantees that waste marked 'Collected' is NEVER falsely certified as 'Recycled'.")
    ],
    accent_color=MINT)


# ==============================================================================
# SLIDE 13: Enterprise Security & Automated Testing
# ==============================================================================
slide13 = create_base_slide()
add_gamma_header(slide13, "12 · QUALITY ASSURANCE", "Automated Testing & Security Controls", "100% test coverage with 22 automated pytest tests")

add_gamma_stat_card(slide13, Inches(0.8), Inches(1.75), Inches(3.6), Inches(1.55), "22 / 22", "Pytest Tests Passing", "100% test suite pass rate", EMERALD)
add_gamma_stat_card(slide13, Inches(4.8), Inches(1.75), Inches(3.6), Inches(1.55), "6.09 s", "Total Execution Time", "Comprehensive test duration", CYAN)
add_gamma_stat_card(slide13, Inches(8.8), Inches(1.75), Inches(3.7), Inches(1.55), "6 Files", "Automated Test Suites", "Auth, Batches, Math, Analytics", MINT)

add_gamma_card(slide13, Inches(0.8), Inches(3.5), Inches(5.6), Inches(3.4),
    "Automated Test Coverage",
    [
        ("test_auth.py (6 tests)", "Registration, password hashing, role restrictions, duplicate emails."),
        ("test_batches.py (3 tests)", "Batch creation, pickup confirmations, invalid status transitions."),
        ("test_verification.py (2 tests)", "Mass-balance formulas and auditor approval state machine."),
        ("test_analytics.py (5 tests)", "Verifies all 5 aggregation pipelines execute correctly."),
        ("test_mongodb_audit.py (6 tests)", "PyMongo connectivity, $jsonSchema rejections, unique key constraints.")
    ],
    accent_color=CYAN)

add_gamma_card(slide13, Inches(6.8), Inches(3.5), Inches(5.7), Inches(3.4),
    "Application Security Architecture",
    [
        ("Privacy Redaction", "Public QR endpoints strip residential addresses and phone numbers."),
        ("Role Access Control", "Strict session decorators (@requires_role) prevent privilege escalation."),
        ("Password Security", "PBKDF2:SHA256 password hashing via Werkzeug security."),
        ("Immutable Ledger", "All administrative decisions written permanently to audit_logs.")
    ],
    accent_color=EMERALD)


# ==============================================================================
# SLIDE 14: Conclusion & Live Demonstration (Gamma Dark Closing)
# ==============================================================================
slide14 = create_base_slide()

badge14 = slide14.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(0.9), Inches(4.8), Inches(0.42))
badge14.fill.solid()
badge14.fill.fore_color.rgb = PILL_BG
badge14.line.color.rgb = PILL_BORDER
badge14.line.width = Pt(1.2)
tf_b14 = badge14.text_frame
p_b14 = tf_b14.paragraphs[0]
p_b14.text = "13 · CONCLUSION & LIVE DEMONSTRATION"
p_b14.font.size = Pt(11)
p_b14.font.bold = True
p_b14.font.color.rgb = MINT
p_b14.alignment = PP_ALIGN.CENTER

title_box14 = slide14.shapes.add_textbox(Inches(1.0), Inches(1.45), Inches(11.3), Inches(0.9))
tf14 = title_box14.text_frame
tf14.word_wrap = True
p14 = tf14.paragraphs[0]
p14.text = "Empowering Municipal Recycling with NoSQL Rigor"
p14.font.size = Pt(30)
p14.font.bold = True
p14.font.color.rgb = TEXT_WHITE

p14_sub = tf14.add_paragraph()
p14_sub.text = "A complete, verifiable platform proving that segregated waste is actually transformed."
p14_sub.font.size = Pt(15)
p14_sub.font.color.rgb = EMERALD
p14_sub.space_before = Pt(4)

add_gamma_card(slide14, Inches(1.0), Inches(2.7), Inches(5.4), Inches(4.1),
    "Academic Deliverables Completed",
    [
        ("Full-Stack Web App", "Production-grade Flask + PyMongo + MongoDB 8.x platform."),
        ("Schema Validation", "Engine-level $jsonSchema protecting all 6 document collections."),
        ("Benchmarked Indexes", "Compound unique indexes with live 10,000-doc .explain() metrics."),
        ("5 Aggregation Pipelines", "Status sums, plant throughput, daily trends, custody lookup, and $facet."),
        ("100% Test Coverage", "22 automated pytest tests passing in 6.09 seconds."),
        ("Visual Presentation", "14 Gamma-styled slides featuring genuine embedded application screenshots.")
    ],
    accent_color=MINT)

add_gamma_card(slide14, Inches(6.9), Inches(2.7), Inches(5.4), Inches(4.1),
    "Live Demonstration & Resources",
    [
        ("GitHub Repository", "https://github.com/AbhiAvinashhh/RecycleTrace"),
        ("Live Web App", "http://127.0.0.1:5000"),
        ("Public QR Demo", "http://127.0.0.1:5000/track/WT-2026-1001"),
        ("Admin Login", "admin@demo.com  (Password: Demo1234!)"),
        ("MongoDB Shell", "mongosh --file scripts/demo_queries.mongosh.js"),
        ("Thank You", "Ready for professor questions and live system walkthrough!")
    ],
    accent_color=EMERALD)

output_path = os.path.join(r"d:\Downloads\pymong\recycletrace\presentation", "RecycleTrace_Gamma_Style_Presentation.pptx")
prs.save(output_path)
print(f"[✓] Gamma-style presentation generated successfully: {output_path}")
