"""
Streamlit Dashboard - Frontend for AI Freelancing Automation
"""
import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# API Configuration
API_BASE_URL = "http://localhost:8000/api"

# Page config
st.set_page_config(
    page_title="AI Freelancing Agency",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .job-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .proposal-box {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🤖 AI Freelancing Automation Agency</div>', unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Run Workflow", "Jobs", "Proposals"])

# Dashboard Page
if page == "Dashboard":
    st.header("📊 Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", "0", help="Total jobs scraped")
    
    with col2:
        st.metric("Relevant Jobs", "0", help="Jobs filtered as relevant")
    
    with col3:
        st.metric("Proposals", "0", help="Proposals generated")
    
    with col4:
        st.metric("Ready to Submit", "0", help="Proposals ready for submission")
    
    st.info("👈 Use the sidebar to navigate and run the workflow")

# Run Workflow Page
elif page == "Run Workflow":
    st.header("🚀 Run Automation Workflow")
    
    st.write("""
    This will run the complete automation workflow:
    1. **Scout** jobs from free sources (RemoteOK, We Work Remotely, Adzuna)
    2. **Filter** relevant jobs using AI
    3. **Generate** custom proposals
    4. **Suggest** competitive pricing
    5. **Store** in vector memory
    6. **Prepare** for manual submission
    """)
    
    if st.button("🚀 Run Workflow", type="primary"):
        with st.spinner("Running workflow... This may take a few minutes."):
            try:
                response = requests.post(f"{API_BASE_URL}/workflow/run", timeout=300)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Workflow completed successfully!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Jobs Found", result.get('total_jobs', 0))
                    with col2:
                        st.metric("Relevant Jobs", result.get('relevant_jobs', 0))
                    with col3:
                        st.metric("Proposals Generated", result.get('proposals_generated', 0))
                    
                    st.info("✅ Jobs and proposals saved to database. Check the Jobs and Proposals pages.")
                else:
                    st.error(f"❌ Error: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the backend is running:\n\n`python -m uvicorn backend.main:app --reload`")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Jobs Page
elif page == "Jobs":
    st.header("💼 Jobs")
    
    # Filters
    col1, col2 = st.columns([3, 1])
    with col1:
        relevant_only = st.checkbox("Show only relevant jobs", value=True)
    with col2:
        limit = st.number_input("Limit", min_value=10, max_value=500, value=50)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/jobs",
            params={"relevant_only": relevant_only, "limit": limit}
        )
        
        if response.status_code == 200:
            jobs = response.json()
            
            if jobs:
                st.success(f"Found {len(jobs)} jobs")
                
                for job in jobs:
                    with st.expander(f"📌 {job['title']} - {job['company']} ({job['source']})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Company:** {job['company']}")
                            st.write(f"**Source:** {job['source']}")
                            if job.get('source_url'):
                                st.write(f"**URL:** [{job['source_url']}]({job['source_url']})")
                        
                        with col2:
                            if job.get('is_relevant'):
                                st.success(f"✅ Relevant")
                                if job.get('relevance_score'):
                                    st.write(f"Score: {job['relevance_score']:.2f}")
            else:
                st.info("No jobs found. Run the workflow first!")
        else:
            st.error(f"Error fetching jobs: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Proposals Page
elif page == "Proposals":
    st.header("📝 Proposals")
    
    limit = st.number_input("Limit", min_value=10, max_value=500, value=50, key="proposal_limit")
    
    try:
        response = requests.get(f"{API_BASE_URL}/proposals", params={"limit": limit})
        
        if response.status_code == 200:
            proposals = response.json()
            
            if proposals:
                st.success(f"Found {len(proposals)} proposals")
                
                for proposal in proposals:
                    with st.expander(f"📄 Proposal #{proposal['id']} (Job ID: {proposal['job_id']})"):
                        st.markdown('<div class="proposal-box">', unsafe_allow_html=True)
                        st.write(proposal['content'])
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if proposal.get('suggested_price'):
                                st.write(f"💰 **Suggested Price:** ${proposal['suggested_price']:.2f}")
                        with col2:
                            st.write(f"📅 **Created:** {proposal['created_at']}")
                        
                        if st.button(f"Copy Proposal #{proposal['id']}", key=f"copy_{proposal['id']}"):
                            st.code(proposal['content'], language=None)
                            st.success("✅ Proposal text displayed above - copy it manually")
            else:
                st.info("No proposals found. Run the workflow first!")
        else:
            st.error(f"Error fetching proposals: {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API. Make sure the backend is running.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("""
**AI Freelancing Agency**

Multi-agent system for automating:
- Job discovery from free sources
- AI-powered filtering
- Proposal generation
- Price suggestions
""")
