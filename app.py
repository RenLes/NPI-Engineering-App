import streamlit as st

st.set_page_config(
    page_title="NPI Engineering Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import inject_custom_css
from utils.project_store import ProjectStore

# --- Initialise state ---
if "current_project" not in st.session_state:
    st.session_state.current_project = None
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1
if "show_new_project" not in st.session_state:
    st.session_state.show_new_project = False

store = ProjectStore(st.session_state)
inject_custom_css()

# --- Import pages ---
from pages.dashboard import dashboard_page
from pages.new_project import new_project_page
from pages.project_overview import project_overview_page
from pages.project_management import project_management_page
from pages.feasibility import feasibility_page
from pages.structural import structural_page
from pages.geotechnical import geotechnical_page
from pages.hydraulics import hydraulics_page
from pages.tenders import tenders_page
from pages.ai_agents import ai_agents_page
from pages.reports_exports import reports_exports_page

# --- Build navigation ---
if st.session_state.current_project is None:
    # Dashboard mode
    pages = {
        "NPI Platform": [
            st.Page(dashboard_page, title="Dashboard", icon="🏠", default=True),
            st.Page(new_project_page, title="New Project", icon="➕"),
        ]
    }
else:
    project = store.get_project(st.session_state.current_project)
    proj_name = project["name"] if project else "Project"

    pages = {
        proj_name: [
            st.Page(project_overview_page, title="Project Overview", icon="📊", default=True),
            st.Page(project_management_page, title="Project Management", icon="📅"),
            st.Page(feasibility_page, title="Feasibility Studies", icon="🔍"),
            st.Page(structural_page, title="Structural Engineering", icon="🏗️"),
            st.Page(geotechnical_page, title="Geotechnical Engineering", icon="⛏️"),
            st.Page(hydraulics_page, title="Hydraulics & Water Systems", icon="💧"),
            st.Page(tenders_page, title="Tenders & Bids", icon="📋"),
            st.Page(ai_agents_page, title="AI Coordinator", icon="🤖"),
            st.Page(reports_exports_page, title="Reports & Exports", icon="📄"),
        ]
    }

pg = st.navigation(pages)

# --- Sidebar branding & controls ---
with st.sidebar:
    st.markdown("### 🏛️ NPI Engineering")
    st.caption("Netts Planning & Infrastructure")
    st.divider()

    if st.session_state.current_project is not None:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_project = None
            st.rerun()

pg.run()
