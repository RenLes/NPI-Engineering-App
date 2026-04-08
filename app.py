import os
import streamlit as st

st.set_page_config(
    page_title="NPI Engineering Platform",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.styles import inject_custom_css
from utils.project_store import ProjectStore

# --- JWT Auth Gate ---
NPI_JWT_SECRET = os.environ.get("NPI_JWT_SECRET", "npi-dev-secret-change-in-production")
CYCLONE_CERTIFY_URL = os.environ.get("CYCLONE_CERTIFY_URL", "http://localhost:3000")
AUTH_ENABLED = os.environ.get("NPI_AUTH_ENABLED", "false").lower() == "true"


def _validate_token(token: str) -> dict | None:
    """Validate a JWT token and return payload, or None if invalid."""
    try:
        import jwt
        payload = jwt.decode(token, NPI_JWT_SECRET, algorithms=["HS256"], options={"require": ["email", "exp", "iss"]})
        if payload.get("iss") != "cyclone-certify-npi":
            return None
        return payload
    except Exception:
        return None


def _check_auth():
    """Check authentication. Returns True if authenticated or auth is disabled."""
    if not AUTH_ENABLED:
        return True

    # Already authenticated in this session
    if st.session_state.get("npi_user"):
        return True

    # Check for token in URL params
    token = st.query_params.get("token")
    if token:
        payload = _validate_token(token)
        if payload:
            st.session_state.npi_user = payload["email"]
            # Clear token from URL for cleanliness
            st.query_params.clear()
            st.rerun()
            return True
        else:
            st.query_params.clear()

    # Not authenticated — show login prompt
    inject_custom_css()
    st.markdown(
        f"""
        <div style="display:flex;align-items:center;justify-content:center;min-height:70vh;">
            <div style="text-align:center;max-width:420px;">
                <div style="background:linear-gradient(135deg,#1B3A5C,#2C5F8A);padding:2rem;border-radius:12px;margin-bottom:1.5rem;">
                    <h1 style="color:white;margin:0;font-size:1.8rem;">NPI Engineering Portal</h1>
                    <p style="color:rgba(255,255,255,0.8);margin:0.3rem 0 0;font-size:0.9rem;">Netts Planning & Infrastructure</p>
                </div>
                <p style="color:#6B7280;margin-bottom:1.5rem;">Please log in through the Cyclone Certify portal to access the NPI Engineering Platform.</p>
                <a href="{CYCLONE_CERTIFY_URL}/npi/login"
                   style="display:inline-block;background:#1B3A5C;color:white;padding:0.75rem 2rem;border-radius:8px;text-decoration:none;font-weight:600;font-size:1rem;">
                    Go to Login
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()
    return False


# Run auth check
_check_auth()

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
from pages.budget import budget_page
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
            st.Page(budget_page, title="Budget & Costs", icon="💰"),
            st.Page(ai_agents_page, title="AI Coordinator", icon="🤖"),
            st.Page(reports_exports_page, title="Reports & Exports", icon="📄"),
        ]
    }

pg = st.navigation(pages)

# --- Sidebar branding & controls ---
with st.sidebar:
    st.markdown("### 🏛️ NPI Engineering")
    st.caption("Netts Planning & Infrastructure")

    # Show logged-in user if auth is enabled
    if AUTH_ENABLED and st.session_state.get("npi_user"):
        st.caption(f"Logged in: {st.session_state.npi_user}")
        if st.button("Logout", use_container_width=True):
            st.session_state.pop("npi_user", None)
            st.rerun()

    st.divider()

    if st.session_state.current_project is not None:
        if st.button("← Back to Dashboard", use_container_width=True):
            st.session_state.current_project = None
            st.rerun()

pg.run()
