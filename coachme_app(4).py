import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import date

# ReportLab imports for in-memory PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & APPLE/GOOGLE MINIMALIST CSS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CoachMe™ Universal Diagnostic",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apple/Google minimalist clean CSS
st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background-color: #F8F9FA;
        color: #1D1D1F;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Card Container */
    .coachme-card {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        border: 1px solid #E5E7EB;
    }
    
    .coachme-card-highlight {
        background: linear-gradient(135deg, #0071E3 0%, #147CE5 100%);
        color: #FFFFFF;
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 20px rgba(0, 113, 227, 0.15);
    }
    
    /* Badge styling */
    .badge-high {
        background-color: #E8F5E9;
        color: #1B5E20;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-mid {
        background-color: #FFF3E0;
        color: #E65100;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-low {
        background-color: #FFEBEE;
        color: #C62828;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        display: inline-block;
    }
    
    /* Headers & Typography */
    h1, h2, h3 {
        color: #1D1D1F;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Custom Progress Bar styling */
    .stProgress > div > div > div > div {
        background-color: #0071E3;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CVA & MODEL ROLES DATABASE
# -----------------------------------------------------------------------------
CVA_DATA = {
    1: {
        "name": "Societal Change",
        "tagline": "Influencing Opinions & Systemic Advocacy",
        "desc": "Focuses on public policy, systemic advocacy, cultural movements, and influencing opinions for the public good.",
        "superpower": "Systemic Advocacy: Unflinching drive to confront hypocrisy and advocate for justice.",
        "caution": "Institutional Friction: Frustration with slow bureaucracy and reluctance to compromise."
    },
    2: {
        "name": "Theoretical Discovery",
        "tagline": "Answering Questions & Objective Logic",
        "desc": "Driven by intellectual curiosity, deep analysis, objective logic, and discovering underlying core principles.",
        "superpower": "Root-Cause Analysis: Unlocks complex systems through objective logic and rigorous inquiry.",
        "caution": "Paralysis by Analysis: Over-thinking decisions and isolating from emotional realities."
    },
    3: {
        "name": "Strategic Decisions",
        "tagline": "Managing Plans & Executive Execution",
        "desc": "Focuses on direct leadership, resource allocation, tactical planning, and executing strategic goals.",
        "superpower": "Tactical Command: Decisive leadership that translates vision into measurable outcomes.",
        "caution": "Autocratic Pacing: Steamrolling relational nuance in pursuit of task completion."
    },
    4: {
        "name": "Human Development",
        "tagline": "Helping People & Pastoral Guidance",
        "desc": "Dedicated to individual mentorship, active listening, emotional healing, and nurturing personal potential.",
        "superpower": "Empathetic Mentorship: Creates deep psychological safety for individual transformation.",
        "caution": "The Messiah Trap: Carrying excessive emotional burdens and neglecting personal boundaries."
    },
    5: {
        "name": "Entrepreneurial Challenge",
        "tagline": "Taking Risks & Pioneering Ventures",
        "desc": "Thrives on pioneering new initiatives, calculated risk-taking, adaptability, and building in uncharted territory.",
        "superpower": "Pioneering Courage: Bold venture building and resilience under extreme uncertainty.",
        "caution": "Restless Churn: Abandoning operational stability for the thrill of the next new initiative."
    },
    6: {
        "name": "Production Efficiency",
        "tagline": "Maintaining Order & Systematic Execution",
        "desc": "Focuses on operational order, repeatable logistics, process optimization, and procedural discipline.",
        "superpower": "Systemic Order: Crafts flawless, repeatable workflows and structural reliability.",
        "caution": "Rigid Rule-Obsession: Resistance to necessary pivot points due to process attachment."
    },
    7: {
        "name": "Artistic Creativity",
        "tagline": "Designing Innovations & Visual Expression",
        "desc": "Driven by aesthetic design, narrative storytelling, creative innovation, and original visual expression.",
        "superpower": "Creative Innovation: Expresses deep truths through aesthetic design and compelling narrative.",
        "caution": "Hypersensitivity: Taking constructive operational criticism as a personal rejection."
    },
    8: {
        "name": "Natural Appreciation",
        "tagline": "Keeping Balance & Pattern Sanctuary",
        "desc": "Focuses on subtle pattern recognition, environmental stewardship, quiet contemplation, and contextual harmony.",
        "superpower": "Subtle Pattern Mapping: Senses underlying contextual connections and builds restorative sanctuary.",
        "caution": "Defensive Isolation: Retreating into silence and building emotional walls under stress."
    },
    9: {
        "name": "Motivational Energy",
        "tagline": "Energizing Others & Public Presence",
        "desc": "Focuses on public engagement, charismatic communication, inspiring team enthusiasm, and rallying collective action.",
        "superpower": "Catalytic Energy: Rallies communities and sparks enthusiasm through charismatic presence.",
        "caution": "Validation Dependence: Over-relying on external applause and immediate group approval."
    }
}

MODEL_ROLES_MAP = {
    (4, 1, 8): {
        "role": "The Advocate & Sanctuary Builder",
        "metaphor": "Public Servant & Community Sanctuary Builder",
        "theme": "Acting in the Public Interest",
        "desc": "You are hardwired to stand up for individuals, defend the vulnerable, and construct restorative, inclusive communities."
    },
    (4, 8, 1): {
        "role": "The Wise Life Coach & Defender",
        "metaphor": "Relational Counselor & Community Protector",
        "theme": "Restorative Human Wellness",
        "desc": "Blends deep individual empathy with subtle pattern recognition to guide people toward holistic growth and psychological safety."
    },
    (1, 3, 6): {
        "role": "The Public Welfare Manager",
        "metaphor": "Civic Executive & Policy Administrator",
        "theme": "Systemic Civic Stewardship",
        "desc": "Combines public advocacy with strategic planning and systematic execution to implement lasting societal reform."
    },
    (2, 8, 6): {
        "role": "The Special Intelligence Analyst",
        "metaphor": "Systems Researcher & Pattern Investigator",
        "theme": "Objective Systems Mapping",
        "desc": "Pairs objective analytical logic with subtle pattern mapping and disciplined execution to solve complex systemic challenges."
    },
    (2, 3, 6): {
        "role": "The Systems Architect & Technologist",
        "metaphor": "Technical Director & Operations Master",
        "theme": "Optimized Systemic Design",
        "desc": "Connects rigorous analytical investigation with executive strategy and systematic operational control."
    },
    (5, 9, 3): {
        "role": "The Pioneer Catalyst",
        "metaphor": "Venture Founder & Keynote Leader",
        "theme": "High-Impact Venture Expansion",
        "desc": "Drives rapid market expansion, high-energy networking, and competitive venture creation."
    },
    (7, 3, 5): {
        "role": "The Design Strategist",
        "metaphor": "Creative Director & Innovation Architect",
        "theme": "Visionary Brand Storytelling",
        "desc": "Merges aesthetic design and narrative innovation with executive planning and bold market risk-taking."
    }
}

DEFAULT_ROLE = {
    "role": "Relational Developer & Strategist",
    "metaphor": "Human-Centered Leader",
    "theme": "Empowered Leadership & Service",
    "desc": "You combine natural relational awareness with purposeful execution to help organizations and individuals thrive."
}

# -----------------------------------------------------------------------------
# 3. REPORTLAB PDF GENERATOR (IN-MEMORY)
# -----------------------------------------------------------------------------
def generate_pdf_report(participant_name, person_code_str, high_triad, mid_triad, low_triad, role_info):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=20, leading=24,
        textColor=colors.HexColor('#1D1D1F')
    )
    h2_style = ParagraphStyle(
        'SectionH2', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=12, leading=15,
        textColor=colors.HexColor('#1D1D1F'), spaceBefore=8, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#333336')
    )
    bold_body = ParagraphStyle(
        'BoldBodyCustom', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=12,
        textColor=colors.HexColor('#1D1D1F')
    )
    
    story = []
    
    # Header Banner Block
    part_info = f"Participant: {participant_name} | Date: {date.today().strftime('%b %d, %Y')}"
    code_info = f"<align=right><font size=13 color='#0071E3'><b>Code: {person_code_str}</b></font><br/><font size=8 color='#86868B'>{role_info['metaphor']}</font></align>"
    
    header_data = [
        [
            Paragraph(f"<b>CoachMe™ Personal Profile Report</b><br/><font size=8.5 color='#86868B'>{part_info}</font>", title_style),
            Paragraph(code_info, body_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E5E7EB'), spaceBefore=2, spaceAfter=8))
    
    # Vocational Theme Card
    theme_desc = role_info['desc']
    theme_title = role_info['theme']
    theme_text = f"<b>Core Theme:</b> {theme_title}<br/><i>{theme_desc}</i>"
    theme_table = Table([[Paragraph(theme_text, body_style)]], colWidths=[540])
    theme_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F5F5F7')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
    ]))
    story.append(theme_table)
    story.append(Spacer(1, 8))
    
    # Section 1: CVA Spectrum
    story.append(Paragraph("Core Value Areas (CVA) Alignment Spectrum", h2_style))
    
    cva_rows = [
        [Paragraph("<b>Alignment Tier</b>", bold_body), Paragraph("<b>Core Value Area</b>", bold_body), Paragraph("<b>Primary Focus & Driver</b>", bold_body)]
    ]
    
    for c_id in high_triad:
        c_info = CVA_DATA[c_id]
        cva_rows.append([
            Paragraph("<font color='#1B5E20'><b>HIGH ALIGNMENT</b></font>", body_style),
            Paragraph(f"<b>CVA {c_id}: {c_info['name']}</b>", body_style),
            Paragraph(c_info['tagline'], body_style)
        ])
    for c_id in mid_triad:
        c_info = CVA_DATA[c_id]
        cva_rows.append([
            Paragraph("<font color='#E65100'><b>MID ALIGNMENT</b></font>", body_style),
            Paragraph(f"CVA {c_id}: {c_info['name']}", body_style),
            Paragraph(c_info['tagline'], body_style)
        ])
    for c_id in low_triad:
        c_info = CVA_DATA[c_id]
        cva_rows.append([
            Paragraph("<font color='#C62828'><b>LOW ALIGNMENT</b></font>", body_style),
            Paragraph(f"CVA {c_id}: {c_info['name']}", body_style),
            Paragraph(c_info['tagline'], body_style)
        ])
        
    cva_table = Table(cva_rows, colWidths=[100, 170, 270])
    cva_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F5F5F7')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E5E7EB')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(cva_table)
    story.append(Spacer(1, 8))
    
    # Section 2: Superpowers vs Caution Areas
    story.append(Paragraph("Superpowers vs. Caution Areas", h2_style))
    
    superpowers_html = "<b>🌟 Natural Superpowers</b><br/><br/>"
    for c_id in high_triad:
        superpowers_html += f"• <b>{CVA_DATA[c_id]['name']}</b>: {CVA_DATA[c_id]['superpower']}<br/><br/>"
        
    caution_html = "<b>⚠️ Stress Caution Areas</b><br/><br/>"
    for c_id in high_triad:
        caution_html += f"• <b>{CVA_DATA[c_id]['name']}</b>: {CVA_DATA[c_id]['caution']}<br/><br/>"
        
    cards_table = Table([
        [Paragraph(superpowers_html, body_style), Paragraph(caution_html, body_style)]
    ], colWidths=[265, 265])
    cards_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), colors.HexColor('#E8F5E9')),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor('#FFEBEE')),
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor('#C8E6C9')),
        ('BOX', (1,0), (1,0), 0.5, colors.HexColor('#FFCDD2')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(cards_table)
    story.append(Spacer(1, 8))
    
    # Section 3: Action Plan
    story.append(Paragraph("Actionable Growth Roadmap", h2_style))
    action_html = """
    <b>1. Lean In:</b> Dedicate 70%+ of your daily energy to your High Triad drivers.<br/>
    <b>2. Protect Boundaries:</b> Establish hard boundaries to guard against stress caution areas.<br/>
    <b>3. Complementary Delegation:</b> Partner with teammates who hold strength in your Low Triad.
    """
    story.append(Paragraph(action_html, body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# -----------------------------------------------------------------------------
# 4. STREAMLIT INTERACTIVE APP & ASSESSMENT FLOW
# -----------------------------------------------------------------------------
st.title("🎯 CoachMe™ Universal Diagnostic")
st.caption("Minimalist, visual self-assessment to discover your Person Code, Model Roles, Key Traits, and Caution Areas.")

# Sidebar Navigation
st.sidebar.markdown("### **CoachMe™ Menu**")
app_mode = st.sidebar.radio(
    "Select Screen:",
    ["1. Take Assessment", "2. View Profile Dashboard", "3. Deployment Guide"]
)

if "answers" not in st.session_state:
    st.session_state.answers = {i: 3 for i in range(1, 10)}
if "participant_name" not in st.session_state:
    st.session_state.participant_name = "Guest Participant"

if app_mode == "1. Take Assessment":
    st.markdown("<div class='coachme-card'>", unsafe_allow_html=True)
    st.subheader("📋 Participant Information")
    st.session_state.participant_name = st.text_input("Enter Your Name:", value=st.session_state.participant_name)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='coachme-card'>", unsafe_allow_html=True)
    st.subheader("🧠 Diagnostic Questionnaire")
    st.write("Rate each scenario from **1 (Least Like Me)** to **5 (Most Like Me)** based on what gives you energy:")
    st.markdown("---")
    
    QUESTIONS = {
        1: "I am driven to speak out against social injustices, systemic gaps, and advocate for cultural change.",
        2: "I am energized by deep research, analyzing complex problems, and uncovering objective truth.",
        3: "I excel at strategic planning, direct team leadership, and executing tactical goals.",
        4: "I feel most fulfilled when mentoring individuals, active listening, and supporting personal growth.",
        5: "I love pioneering new ventures, taking calculated risks, and building in uncharted territory.",
        6: "I thrive when establishing repeatable systems, organizing logistics, and maintaining order.",
        7: "I am drawn to aesthetic design, original storytelling, and creative visual expression.",
        8: "I naturally notice subtle environmental patterns, value quiet reflection, and build sanctuary.",
        9: "I am energized by public speaking, inspiring group enthusiasm, and rallying people."
    }
    
    for i in range(1, 10):
        cva = CVA_DATA[i]
        col_q, col_s = st.columns([3, 2])
        with col_q:
            st.markdown(f"**CVA {i}: {cva['name']}**")
            st.caption(QUESTIONS[i])
        with col_s:
            st.session_state.answers[i] = st.slider(
                f"Rating CVA {i}", min_value=1, max_value=5,
                value=st.session_state.answers[i], key=f"q_{i}", label_visibility="collapsed"
            )
        st.markdown("<hr style='margin: 8px 0; border: none; border-top: 1px solid #F0F0F0;'/>", unsafe_allow_html=True)
        
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("🚀 Generate My CoachMe™ Profile", type="primary"):
        st.session_state.assessment_complete = True
        st.success("Assessment calculated successfully! Navigate to '2. View Profile Dashboard' in the sidebar.")

elif app_mode == "2. View Profile Dashboard":
    # Calculate Scores
    scores = st.session_state.answers
    sorted_cvas = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    high_triad = [x[0] for x in sorted_cvas[:3]]
    mid_triad = [x[0] for x in sorted_cvas[3:6]]
    low_triad = [x[0] for x in sorted_cvas[6:]]
    
    person_code_str = " · ".join(map(str, high_triad))
    
    # Lookup role
    triad_tuple = tuple(high_triad)
    role_info = MODEL_ROLES_MAP.get(triad_tuple, DEFAULT_ROLE)
    
    r_role = role_info['role']
    r_meta = role_info['metaphor']
    r_theme = role_info['theme']
    r_desc = role_info['desc']
    
    # Highlight Banner
    st.markdown(f"""
    <div class='coachme-card-highlight'>
        <h3 style='color: #FFFFFF; margin-bottom: 4px;'>Person Code: {person_code_str}</h3>
        <h2 style='color: #FFFFFF; margin-top: 0;'>{r_role}</h2>
        <p style='font-size: 1.1rem; opacity: 0.9;'><b>Identity Metaphor:</b> {r_meta}</p>
        <p style='font-size: 1.0rem; opacity: 0.85; margin-bottom: 0;'><b>Core Theme:</b> {r_theme} — {r_desc}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # PDF Download Section
    pdf_bytes = generate_pdf_report(
        st.session_state.participant_name, person_code_str,
        high_triad, mid_triad, low_triad, role_info
    )
    
    st.download_button(
        label="📄 Download Official CoachMe™ PDF Report",
        data=pdf_bytes,
        file_name=f"CoachMe_Profile_{st.session_state.participant_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="secondary"
    )
    st.markdown("<br/>", unsafe_allow_html=True)
    
    # CVA Spectrum Cards
    st.subheader("📊 Core Value Areas (CVA) Spectrum")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='coachme-card'>", unsafe_allow_html=True)
        st.markdown("<span class='badge-high'>HIGH ALIGNMENT</span>", unsafe_allow_html=True)
        st.markdown("#### Core Drivers")
        for cid in high_triad:
            c = CVA_DATA[cid]
            st.markdown(f"**CVA {cid}: {c['name']}**")
            st.caption(c['tagline'])
            st.progress(scores[cid] / 5.0)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        st.markdown("<div class='coachme-card'>", unsafe_allow_html=True)
        st.markdown("<span class='badge-mid'>MEDIUM ALIGNMENT</span>", unsafe_allow_html=True)
        st.markdown("#### Supporting Strengths")
        for cid in mid_triad:
            c = CVA_DATA[cid]
            st.markdown(f"**CVA {cid}: {c['name']}**")
            st.caption(c['tagline'])
            st.progress(scores[cid] / 5.0)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col3:
        st.markdown("<div class='coachme-card'>", unsafe_allow_html=True)
        st.markdown("<span class='badge-low'>LOW ALIGNMENT</span>", unsafe_allow_html=True)
        st.markdown("#### Higher Energy Drainers")
        for cid in low_triad:
            c = CVA_DATA[cid]
            st.markdown(f"**CVA {cid}: {c['name']}**")
            st.caption(c['tagline'])
            st.progress(scores[cid] / 5.0)
        st.markdown("</div>", unsafe_allow_html=True)
        
    # Superpowers vs Caution Areas
    st.subheader("⚡ Superpowers vs. ⚠️ Caution Areas")
    
    col_sp, col_ca = st.columns(2)
    
    with col_sp:
        st.markdown("<div class='coachme-card'>", unsafe_allow_html=True)
        st.markdown("### 🌟 Natural Superpowers")
        for cid in high_triad:
            c = CVA_DATA[cid]
            st.markdown(f"**• {c['name']}**: {c['superpower']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_ca:
        st.markdown("<div class='coachme-card'>", unsafe_allow_html=True)
        st.markdown("### ⚠️ Stress Caution Areas")
        for cid in high_triad:
            c = CVA_DATA[cid]
            st.markdown(f"**• {c['name']}**: {c['caution']}")
        st.markdown("</div>", unsafe_allow_html=True)

elif app_mode == "3. Deployment Guide":
    st.subheader("🚀 Streamlit Community Cloud Deployment")
    st.markdown("""
    To deploy **CoachMe™** online for free:
    1. Upload `coachme_app.py` to a public GitHub repository.
    2. Add a `requirements.txt` file containing:
       ```text
       streamlit>=1.30.0
       pandas>=2.0.0
       numpy>=2.0.0
       reportlab>=4.0.0
       ```
    3. Visit **share.streamlit.io**, log in with GitHub, and select `coachme_app.py`.
    """)
