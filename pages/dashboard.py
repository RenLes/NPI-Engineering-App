import streamlit as st
from utils.styles import page_title
from utils.project_store import ProjectStore


def dashboard_page():
    store = ProjectStore(st.session_state)
    page_title("NPI Project Dashboard", "Your active projects at a glance")

    # --- Top bar: search + new project ---
    col_search, col_filter, col_new = st.columns([3, 2, 1.5])
    with col_search:
        search = st.text_input("Search projects", placeholder="Search by name, client, or location...", label_visibility="collapsed")
    with col_filter:
        phase_filter = st.selectbox("Filter by phase", ["All", "Active", "Planning", "Complete"], label_visibility="collapsed")
    with col_new:
        if st.button("➕ New Project", use_container_width=True, type="primary"):
            st.session_state.show_new_project = True
            st.switch_page(st.Page("pages/new_project.py", title="New Project"))

    st.divider()

    # --- Project cards ---
    projects = store.list_projects()

    # Apply filters
    if search:
        q = search.lower()
        projects = [p for p in projects if q in p["name"].lower() or q in p["client"].lower() or q in p["location"].lower()]
    if phase_filter != "All":
        projects = [p for p in projects if p["phase"] == phase_filter]

    if not projects:
        st.info("No projects found. Create your first project to get started.")
        return

    # Render in 3-column grid
    cols = st.columns(3)
    for idx, project in enumerate(projects):
        with cols[idx % 3]:
            _render_project_card(project)


def _render_project_card(project: dict):
    phase = project["phase"]
    badge_class = {"Active": "badge-active", "Planning": "badge-planning", "Complete": "badge-complete"}.get(phase, "badge-planning")

    # Build "What's been added" summary
    updates_html = ""
    recent = project.get("updates", [])[:3]
    if recent:
        items = "".join(f"<div>• {u['message']}</div>" for u in recent)
        updates_html = f'<div class="updates"><strong>What\'s been added:</strong>{items}</div>'

    card_html = f"""
    <div class="project-card">
        <h4>{project['name']}</h4>
        <div class="meta">
            <span class="badge {badge_class}">{phase}</span>
            &nbsp; {project['progress']}% complete &nbsp;|&nbsp; {project['client']}
        </div>
        <div class="meta" style="margin-top:4px;">
            📍 {project['location']} &nbsp;|&nbsp; 📅 Deadline: {project['deadline']}
        </div>
        {updates_html}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

    if st.button("Open Project", key=f"open_{project['id']}", use_container_width=True):
        st.session_state.current_project = project["id"]
        st.rerun()
