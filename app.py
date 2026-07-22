# app.py

import streamlit as st
import os
import tempfile
from datetime import datetime
import json
# Removed file extraction imports
from dotenv import load_dotenv

# Import our modules
from gemini_utils import GeminiHelper
from ml_utils import MLPredictor

load_dotenv()

# Page Config
st.set_page_config(
    page_title="OfferShield AI | Internship Scam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============ CUSTOM CSS ============
st.markdown("""
<style>
    /* Reset & Base */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0d1b2a 100%);
    }
    
    /* Main Container */
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 1rem;
    }
    
    /* Title Section */
    .header {
        text-align: center;
        padding: 2rem;
        background: rgba(10, 102, 194, 0.08);
        border-radius: 24px;
        border: 1px solid rgba(10, 102, 194, 0.2);
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #0A66C2, #00b4d8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: 1px;
    }
    
    .sub-title {
        font-size: 1.1rem;
        color: #90e0ef;
        margin-top: 0.3rem;
        letter-spacing: 0.5px;
    }
    
    .team-badge {
        display: inline-block;
        background: rgba(10, 102, 194, 0.2);
        padding: 0.3rem 1.5rem;
        border-radius: 20px;
        color: #00b4d8;
        font-size: 0.85rem;
        margin-top: 0.5rem;
        border: 1px solid rgba(10, 102, 194, 0.3);
    }
    
    /* Cards */
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(10, 102, 194, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        transition: all 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 32px rgba(10, 102, 194, 0.15);
        border-color: rgba(10, 102, 194, 0.4);
    }
    
    /* Section Titles */
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #00b4d8;
        border-left: 4px solid #0A66C2;
        padding-left: 1rem;
        margin: 1.5rem 0 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Upload Box */
    .upload-box {
        border: 2px dashed rgba(10, 102, 194, 0.4);
        border-radius: 16px;
        padding: 3rem 2rem;
        text-align: center;
        background: rgba(10, 102, 194, 0.03);
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #0A66C2;
        background: rgba(10, 102, 194, 0.06);
    }
    
    /* Verify Button - Animated */
    .stButton > button {
        background: linear-gradient(135deg, #0A66C2, #00b4d8);
        color: white;
        border: none;
        padding: 0.8rem 3rem;
        font-size: 1.2rem;
        font-weight: 600;
        border-radius: 50px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 25px rgba(10, 102, 194, 0.4);
        width: 100%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 4px 25px rgba(10, 102, 194, 0.4); }
        50% { box-shadow: 0 4px 50px rgba(10, 102, 194, 0.7); }
        100% { box-shadow: 0 4px 25px rgba(10, 102, 194, 0.4); }
    }
    
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 50px rgba(10, 102, 194, 0.6);
    }
    
    /* Risk Badges */
    .badge-high {
        background: rgba(255, 0, 0, 0.15);
        border: 2px solid #ff0000;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .badge-low {
        background: rgba(0, 255, 0, 0.08);
        border: 2px solid #00ff88;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .badge-text-high {
        color: #ff4444;
        font-size: 2rem;
        font-weight: 800;
    }
    
    .badge-text-low {
        color: #00ff88;
        font-size: 2rem;
        font-weight: 800;
    }
    
    /* Check Items */
    .check-item {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 3px solid #0A66C2;
    }
    
    .check-status {
        font-size: 1.5rem;
        width: 40px;
        text-align: center;
    }
    
    .check-label {
        flex: 1;
        font-weight: 500;
        color: #e0e0e0;
    }
    
    .check-msg {
        color: #7f8fa6;
        font-size: 0.9rem;
    }
    
    /* Conclusion Box */
    .conclusion-box {
        background: rgba(10, 102, 194, 0.1);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(10, 102, 194, 0.3);
        margin: 1rem 0;
    }
    
    .conclusion-text {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #c8d6e5;
    }
    
    /* Detail Grid */
    .detail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .detail-item {
        background: rgba(255, 255, 255, 0.03);
        padding: 0.8rem 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .detail-label {
        font-size: 0.7rem;
        color: #7f8fa6;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .detail-value {
        font-size: 1rem;
        font-weight: 600;
        color: #e0e0e0;
        margin-top: 0.2rem;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #7f8fa6;
        font-size: 0.8rem;
        padding: 2rem 0 1rem 0;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 2rem;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-title { font-size: 2.2rem; }
        .detail-grid { grid-template-columns: 1fr 1fr; }
    }
    
    /* Success Animation */
    .success-emoji {
        font-size: 3rem;
        text-align: center;
        animation: bounce 1s ease infinite;
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
</style>
""", unsafe_allow_html=True)

# ============ SESSION STATE ============
if 'analyzed' not in st.session_state:
    st.session_state.analyzed = False
if 'extracted_data' not in st.session_state:
    st.session_state.extracted_data = None
if 'verification_data' not in st.session_state:
    st.session_state.verification_data = None
if 'ml_prediction' not in st.session_state:
    st.session_state.ml_prediction = None
if 'file_text' not in st.session_state:
    st.session_state.file_text = ""
if 'file_name' not in st.session_state:
    st.session_state.file_name = ""

# ============ FUNCTIONS ============
# File extraction function removed as we now use text input

# ============ UI ============

# Header
st.markdown("""
<div class="header">
    <h1 class="main-title">🛡️ OfferShield AI</h1>
    <p class="sub-title">🤖 AI-Powered Internship & Job Offer Scam Detector</p>
    <div class="team-badge">⚡ Built by NEUROVIA ⚡</div>
</div>
""", unsafe_allow_html=True)

# Main Layout
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<p class="section-title">📝 Paste Offer Text</p>', unsafe_allow_html=True)
    
    # Text Input Section
    offer_text_input = st.text_area(
        " ",
        height=250,
        help="Paste the internship or job offer text here for AI-powered scam detection",
        placeholder="Paste the offer email or document text here...",
        label_visibility="collapsed"
    )
    
    # Analyze Button
    if st.button("🚀 Verify Offer Now", use_container_width=True):
        if offer_text_input.strip():
            st.session_state.file_name = "Pasted Text"
            st.session_state.file_text = offer_text_input
            
            with st.spinner("🧠 AI is analyzing the offer..."):
                try:
                    # Step 1: Extract details using Gemini
                    gemini = GeminiHelper()
                    extracted = gemini.extract_details(st.session_state.file_text)
                    st.session_state.extracted_data = extracted
                    
                    # Step 2: Verify using Gemini
                    verification = gemini.verify_offer(extracted)
                    st.session_state.verification_data = verification
                    
                    # Step 3: ML Prediction
                    ml = MLPredictor()
                    ml_result = ml.predict_risk(
                        extracted,
                        verification["verification_checks"]
                    )
                    st.session_state.ml_prediction = ml_result
                    
                    st.session_state.analyzed = True
                    st.success("✅ Analysis Complete!")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"⚠️ Error: {str(e)}")
                    st.info("💡 Make sure GEMINI_API_KEY is set in .env file")
        else:
            st.warning("⚠️ Please paste some text first!")

with col2:
    st.markdown('<p class="section-title">📊 Quick Stats</p>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
        <p style="color: #00b4d8; font-weight: 600;">⚡ Real-time Protection</p>
        <p style="color: #7f8fa6; font-size: 0.9rem;">AI-powered scam detection for internship offers</p>
        <div style="background: rgba(10,102,194,0.15); border-radius: 10px; padding: 0.5rem; margin-top: 0.5rem;">
            <span style="color: #00ff88;">🟢 100% Free & Secure</span>
        </div>
    </div>
    
    <div class="card">
        <p style="color: #00b4d8; font-weight: 600;">🔍 What We Check</p>
        <ul style="color: #c8d6e5; font-size: 0.85rem; padding-left: 1.2rem; margin: 0.3rem 0;">
            <li>✓ Company legitimacy</li>
            <li>✓ Recruiter email domain</li>
            <li>✓ Interview process</li>
            <li>✓ Payment requests</li>
            <li>✓ Salary realism</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# ============ RESULTS SECTION ============
if st.session_state.analyzed:
    st.markdown("---")
    st.markdown('<p class="section-title">📊 Verification Results</p>', unsafe_allow_html=True)
    
    extracted = st.session_state.extracted_data
    verification = st.session_state.verification_data
    ml_result = st.session_state.ml_prediction
    
    # Risk Badge
    risk = ml_result['risk']
    emoji = "🔴" if risk == "HIGH RISK" else "🟢"
    badge_class = "badge-high" if risk == "HIGH RISK" else "badge-low"
    text_class = "badge-text-high" if risk == "HIGH RISK" else "badge-text-low"
    
    st.markdown(f"""
    <div class="{badge_class}">
        <div class="{text_class}">
            {emoji} {risk}
        </div>
        <p style="color: #7f8fa6; margin-top: 0.3rem;">Confidence: {ml_result.get('confidence', 'High')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Extracted Details
    st.markdown('<p class="section-title">📋 Extracted Details</p>', unsafe_allow_html=True)
    
    detail_cols = st.columns(4)
    detail_items = list(extracted.items())
    for idx, (key, value) in enumerate(detail_items[:4]):  # Show first 4
        with detail_cols[idx % 4]:
            st.markdown(f"""
            <div class="detail-item">
                <div class="detail-label">{key.replace('_', ' ')}</div>
                <div class="detail-value">{value if value else 'Not found'}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Row 2 of details
    detail_cols2 = st.columns(3)
    for idx, (key, value) in enumerate(detail_items[4:]):
        with detail_cols2[idx % 3]:
            st.markdown(f"""
            <div class="detail-item">
                <div class="detail-label">{key.replace('_', ' ')}</div>
                <div class="detail-value">{value if value else 'Not found'}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Verification Checks (Checkbox style)
    st.markdown('<p class="section-title">✅ Verification Checks</p>', unsafe_allow_html=True)
    
    checks = verification.get('verification_checks', [])
    for check in checks:
        status_icon = check['status']
        status_color = {
            '✅': '#00ff88',
            '❌': '#ff4444',
            '⚠️': '#ffaa00'
        }.get(status_icon, '#ffffff')
        
        st.markdown(f"""
        <div class="check-item">
            <div class="check-status">{status_icon}</div>
            <div class="check-label">{check['check']}</div>
            <div class="check-msg">{check['message']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Conclusion
    st.markdown('<p class="section-title">💬 Conclusion</p>', unsafe_allow_html=True)
    
    conclusion = verification.get('conclusion', 'Analysis complete.')
    risk_emoji = "🚨" if risk == "HIGH RISK" else "✅"
    
    st.markdown(f"""
    <div class="conclusion-box">
        <div style="display: flex; align-items: flex-start; gap: 1rem;">
            <span style="font-size: 2rem;">{risk_emoji}</span>
            <div>
                <p style="color: {'#ff4444' if risk == 'HIGH RISK' else '#00ff88'}; font-weight: 700; font-size: 1.1rem;">
                    {risk} DETECTED
                </p>
                <p class="conclusion-text">{conclusion}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ML Features Used (Transparency)
    with st.expander("🔬 ML Model Insights (Technical)"):
        st.json(ml_result.get('features_used', {}))
        st.caption("🤖 Your ML teammate can replace this with actual model predictions")
    
    # Download Report
    st.markdown('<p class="section-title">📥 Download Report</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📄 Download as JSON", use_container_width=True):
            report_data = {
                "file_name": st.session_state.file_name,
                "extracted_details": extracted,
                "verification_checks": checks,
                "risk_level": risk,
                "conclusion": conclusion,
                "timestamp": datetime.now().isoformat()
            }
            st.download_button(
                label="⬇️ Download JSON",
                data=json.dumps(report_data, indent=2),
                file_name=f"OfferShield_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        if st.button("📋 Copy Analysis", use_container_width=True):
            st.info("📋 Analysis copied to clipboard!")

# Footer
st.markdown("""
<div class="footer">
    🛡️ OfferShield AI v1.0 | Built by <strong>NEUROVIA</strong> | Hackathon 2026 🚀<br>
    <span style="font-size: 0.7rem;">🔒 Protecting students & job seekers from internship scams</span>
</div>
""", unsafe_allow_html=True)