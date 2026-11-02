import streamlit as st
import requests
import json
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hydrogrid Content Marketer Agent",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        color: #0E4268;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #4A5568;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #0E4268;
        color: white;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1A5276;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- GEMINI API CALL WITH RETRY/BACKOFF ---
def generate_content_with_gemini(api_key: str, prompt: str) -> str:
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 429:
                time.sleep(2 ** (attempt + 1))
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
                return ""
        except Exception as e:
            if attempt == max_retries - 1:
                st.error(f"Connection failed: {str(e)}")
                return ""
            time.sleep(2)
    return ""

# --- APP HEADER ---
st.markdown('<div class="main-header">🌊 Hydrogrid Content Marketer Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate B2B social media updates, WhatsApp broadcasts, and case studies for Underwater Drone Inspections & Manual Tank Cleaning/Maintenance.</div>', unsafe_allow_html=True)

# --- SIDEBAR: CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_key = ""
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("API Key loaded securely from Secrets! 🔒")
    else:
        api_key = st.text_input("Enter Gemini API Key:", type="password", help="Get your API key from Google AI Studio")
        
    st.divider()
    st.markdown("### 🏢 Business Profile")
    st.caption("**Company:** Hydrogrid Services (PG0570517-A)")
    st.caption("**Base:** UiTM-MTDC Technopreneur Centre, Shah Alam")
    st.caption("**Core Scope:**")
    st.markdown("- **Underwater Drone (ROV):** In-service live tank inspections.\n- **Manual Maintenance:** Traditional drain-and-clean, wall scrubbing, sediment removal & structural joint sealing.")

# --- MAIN INPUT SECTION ---
st.subheader("📝 Job & Field Operations Input")

preset = st.radio(
    "Load Quick Example Scenario:",
    ["Custom / Manual Entry", "Condo Strata (Drone Inspection + Manual Clean)", "Industrial Facility (Drone Audit + Manual Maintenance)"],
    horizontal=True
)

preset_data = {
    "Custom / Manual Entry": {
        "location": "Petaling Jaya, Selangor",
        "tank_type": "Reinforced Concrete Panel Tank",
        "services": ["Underwater Drone Live Inspection", "Manual Tank Cleaning & Scrubbing", "Traditional Drain-and-Clean Sanitation"],
        "challenge": "Management needed an initial live drone assessment before scheduling traditional manual cleaning to avoid unnecessary water shutdown.",
        "notes": "Deployed underwater drone to map silt levels and pinpoint joint wear. Followed up with scheduled manual drain-and-clean surface scrubbing for full hygiene compliance."
    },
    "Condo Strata (Drone Inspection + Manual Clean)": {
        "location": "Subang Jaya, Selangor",
        "tank_type": "High-Rise Roof Polyethylene/FRP Tank",
        "services": ["Underwater Drone Live Inspection", "Manual Tank Cleaning & Scrubbing", "Manual Sediment & Sludge Removal"],
        "challenge": "JMB chairman wanted visual proof of internal condition prior to approving manual cleaning budgets.",
        "notes": "Used underwater drone for live visual audit. Identified targeted grime areas, then performed manual tank washing and disinfection. Delivered complete digital report to JMB."
    },
    "Industrial Facility (Drone Audit + Manual Maintenance)": {
        "location": "Shah Alam, Selangor",
        "tank_type": "Industrial Stainless Steel / FRP Tank",
        "services": ["Underwater Drone Live Inspection", "Manual Structural Joint Repair & Waterproofing", "Manual Tank Sanitation"],
        "challenge": "High-capacity factory storage tank required leak detection and wall maintenance.",
        "notes": "Drone mapped internal lining defects under full water level. Maintenance crew then isolated the compartment for manual joint re-sealing and surface cleaning."
    }
}

active_preset = preset_data[preset]

col1, col2 = st.columns(2)

with col1:
    location = st.text_input("Location / Site", value=active_preset["location"])
    tank_type = st.selectbox(
        "Tank Type", 
        ["Reinforced Concrete Panel Tank", "High-Rise Roof Polyethylene/FRP Tank", "Industrial Stainless Steel Tank", "Underground Sump Tank"],
        index=0 if preset == "Custom / Manual Entry" else (0 if "Concrete" in active_preset["tank_type"] else 1)
    )
    selected_services = st.multiselect(
        "Services Provided in Job",
        [
            "Underwater Drone Live Inspection", 
            "Manual Tank Cleaning & Scrubbing", 
            "Traditional Drain-and-Clean Sanitation", 
            "Manual Sediment & Sludge Removal",
            "Manual Structural Joint Repair & Waterproofing",
            "Digital Integrity Audit Reporting"
        ],
        default=active_preset["services"]
    )

with col2:
    key_challenge = st.text_input("Key Client Challenge / Need", value=active_preset["challenge"])
    raw_notes = st.text_area("Raw Field Notes & Outcome", value=active_preset["notes"], height=110)

# --- PROMPT GENERATION ---
if st.button("🚀 Generate Marketing Assets"):
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar or via Streamlit Secrets (`GEMINI_API_KEY`).")
    else:
        services_str = ", ".join(selected_services)
        
        system_prompt = f"""
You are the B2B Marketing & Technical Copywriter Agent for Hydrogrid Services (Malaysia).
Company Scope: Specialized in Underwater Drone (ROV) live internal water tank inspections, as well as traditional manual water tank cleaning and maintenance services (manual surface scrubbing, drain-and-clean sanitation, sediment removal, and joint maintenance).

JOB DETAILS PROVIDED:
- Location: {location}
- Asset Type: {tank_type}
- Scope of Work Performed: {services_str}
- Client Challenge: {key_challenge}
- On-Site Field Notes: {raw_notes}

Generate 4 specific marketing assets in professional, engineering-grade English suitable for Malaysian B2B property managers, JMBs, MCs, and factory engineers.

Format your output using clear markdown titles as follows:

### 1. LinkedIn B2B Post
Focus on risk mitigation, non-disruptive underwater drone diagnostics paired with thorough manual cleaning, asset longevity, and compliance. Use professional hashtags.

### 2. Facebook / Community Post
Focus on resident hygiene, clean drinking water safety, transparent drone inspections, and thorough manual tank sanitation.

### 3. WhatsApp Direct Outreach Message
A concise, friendly, high-converting broadcast message (with relevant emojis) for JMB members and property managers.

### 4. Proposal / Website Case Study Block
A structured snapshot summary (Project Title, Problem, Solution, Outcome) ready to copy into formal PDF proposals or website updates.
"""

        with st.spinner("Analyzing field notes and generating marketing content..."):
            generated_text = generate_content_with_gemini(api_key, system_prompt)
            
            if generated_text:
                st.success("Content generated successfully!")
                st.divider()
                st.markdown(generated_text)
