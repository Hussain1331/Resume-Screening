import streamlit as st
import pandas as pd
import io
import plotly.express as px

# Advanced UI components
import streamlit_antd_components as sac
from streamlit_card import card

# Core internal processing modules
from data_preprocessing import clean_resume_text
from skill_matcher import load_skills_dictionary
from screener_engine import rank_candidates

# -----------------------------------------------------------------------------
# 1. PAGE SETUP & THEME CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="TalentScreen Enterprise AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #fafafa; }
        h1, h2, h3 { font-family: 'Segoe UI', sans-serif; color: #0f172a !important; }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FILE PARSING PIPELINE
# -----------------------------------------------------------------------------
def parse_uploaded_file(uploaded_file):
    extracted_text = ""
    file_extension = uploaded_file.name.split('.')[-1].lower()
    file_bytes = io.BytesIO(uploaded_file.read())

    if file_extension == 'pdf':
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(file_bytes)
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text: extracted_text += page_text + " "
    elif file_extension == 'docx':
        import docx
        doc = docx.Document(file_bytes)
        for paragraph in doc.paragraphs: extracted_text += paragraph.text + " "
    return extracted_text

# -----------------------------------------------------------------------------
# 3. INTERACTIVE NAVIGATION & SCHEMA LOADING
# -----------------------------------------------------------------------------
st.title("🤖 TalentScreen Enterprise AI")
st.caption("Production-grade multi-candidate screening pipeline dashboard framework.")

current_tab = sac.tabs([
    sac.TabsItem(label='Screening Terminal', icon='terminal-split'),
    sac.TabsItem(label='System Knowledge Base', icon='database-fill-gear'),
], align='start', variant='light', index=0)

st.markdown("<br>", unsafe_allow_html=True)

# Load categorized skill configurations
skills_data_dictionary = load_skills_dictionary()

# =============================================================================
# VIEW 1: SCREENING TERMINAL
# =============================================================================
if current_tab == 'Screening Terminal':
    
    st.subheader("🎯 Step 1: Define Role Profile Framework")
    selected_role_profile = st.selectbox(
        "Select Target Domain Taxonomy:",
        options=list(skills_data_dictionary.keys()),
        help="Filters evaluation parsing metrics to specifically isolate keywords relative to this profile segment."
    )
    
    active_role_skills = skills_data_dictionary[selected_role_profile]
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([5, 5], gap="large")
    
    with col_left:
        st.subheader("📋 Role Vector Specification Input")
        raw_job_description = st.text_area(
            label="Mandate Spec Input", label_visibility="collapsed", height=230,
            placeholder=f"Paste requirements here. System will emphasize your selected domain: {selected_role_profile}..."
        )
        
    with col_right:
        st.subheader("📂 Target Applicant Document Assets")
        submitted_resumes = st.file_uploader(
            label="File Upload Gateway", label_visibility="collapsed",
            type=["pdf", "docx"], accept_multiple_files=True
        )

    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("⚡ Trigger Match Matrix Engine", type="primary", use_container_width=True):
        if not raw_job_description.strip():
            st.error("Execution Aborted: Job profile specifications field cannot be blank.")
        elif not submitted_resumes:
            st.error("Execution Aborted: Document gateway expects at least one resume asset file target.")
        else:
            with st.spinner("Processing token mappings, resolving taxonomy intersections..."):
                
                cleaned_job_spec = clean_resume_text(raw_job_description)
                
                candidate_payload = []
                for file_asset in submitted_resumes:
                    raw_text_stream = parse_uploaded_file(file_asset)
                    normalized_text = clean_resume_text(raw_text_stream)
                    candidate_payload.append({"name": file_asset.name, "text": normalized_text})
                
                screening_metrics = rank_candidates(cleaned_job_spec, candidate_payload, active_role_skills)
                
                # Check if backend returned a string error message instead of parsed data
                if isinstance(screening_metrics, str):
                    st.error(f"🔍 Pipeline Warning: {screening_metrics}")
                    st.info(f"💡 Try adding keywords matching your text layout into the '{selected_role_profile}' block inside your skills.json file.")
                else:
                    st.markdown("---")
                    st.subheader("📊 Executive Screening Intelligence")
                    
                    total_candidates = len(submitted_resumes)
                    top_candidate_node = screening_metrics[0]
                    
                    card_col, metric_col = st.columns([4, 6], gap="medium")
                    
                    with card_col:
                        card(
                            title=f"{top_candidate_node['Match Score (%)']}% Match",
                            text=f"Top Match: {top_candidate_node['Candidate Name']}",
                            image="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400",
                            styles={
                                "card": {"width": "100%", "height": "140px", "border-radius": "12px", "box-shadow": "none"},
                                "title": {"font-size": "1.7rem", "font-weight": "800"},
                                "text": {"font-size": "0.95rem"}
                            }
                        )
                        
                    with metric_col:
                        m_col1, m_col2 = st.columns(2)
                        m_col1.metric("Evaluation Pool Size", f"{total_candidates} Profiles")
                        m_col2.metric("Active Screening Track", selected_role_profile)
                        st.caption(f"**Identified Competencies for {top_candidate_node['Candidate Name']}:** {', '.join(top_candidate_node['Matched Skills']).upper()}")

                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    presentation_df = pd.DataFrame(screening_metrics)
                    
                    # Chart rendering using new Hybrid scores
                    chart_df = presentation_df.sort_values(by="Match Score (%)", ascending=True)
                    fig = px.bar(
                        chart_df, 
                        x="Match Score (%)", 
                        y="Candidate Name", 
                        orientation='h',
                        title="Talent Pool Hybrid Convergence Distribution Index",
                        text="Match Score (%)",
                        color="Match Score (%)",
                        color_continuous_scale=px.colors.sequential.Blugrn
                    )
                    fig.update_layout(yaxis_title="Candidate Profile Identifier", xaxis_title="Hybrid Match Score (%)", height=300, margin=dict(t=40, b=20, l=10, r=10))
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Clean up data framing presentation tables safely
                    if "All Skills" in presentation_df.columns:
                        presentation_df.drop(columns=["All Skills"], inplace=True)
                    
                    # Convert list objects to clean strings for display
                    presentation_df["Matched Skills"] = presentation_df["Matched Skills"].apply(lambda s: " • ".join(s).upper() if s else "⚠️ ZERO TARGETS FOUND")
                    presentation_df["Missing Skills (Gaps)"] = presentation_df["Missing Skills (Gaps)"].apply(lambda g: ", ".join(g).upper() if g else "✅ CRITERIA SATISFIED")
                    
                    # Dynamically map names based on what the backend actually sent
                    column_mapping = {
                        "Candidate Name": "Filename",
                        "Match Score (%)": "Hybrid Fit Score (%)",
                        "Keyword Match (%)": "Exact Keyword Fit (%)",
                        "Semantic Fit (%)": "AI Semantic Fit (%)",
                        "Matched Skills": "Matching Indicators",
                        "Missing Skills (Gaps)": "Delta Skill Gaps"
                    }
                    
                    # Rename only the columns that exist to prevent any length mismatch crashes
                    presentation_df.rename(columns=column_mapping, inplace=True)
                    presentation_df.index = presentation_df.index + 1
                    
                    st.subheader("📋 Analytical Talent Matrix Ledger")
                    st.dataframe(
                        presentation_df, use_container_width=True,
                        column_config={
                            "Hybrid Fit Score (%)": st.column_config.ProgressColumn(
                                "Hybrid Fit Score (%)", help="Combined 60% exact skill checklist intersection + 40% contextual neural net semantic mapping.",
                                format="%f%%", min_value=0, max_value=100
                            )
                        }
                    )

# =============================================================================
# VIEW 2: KNOWLEDGE BASE CONFIGURATION OVERVIEW
# =============================================================================
elif current_tab == 'System Knowledge Base':
    st.subheader("⚙️ System Core Domain Schema Mapping Definitions")
    st.markdown("Active lexicon terms categorized by corporate hiring track domains:")
    st.json(skills_data_dictionary)