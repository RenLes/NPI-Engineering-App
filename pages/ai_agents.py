import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore


def ai_agents_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    page_title("AI Coordinator", f"{project['name']} — Central AI processing hub")

    st.info("The Coordinator Agent is the single AI interface for all disciplines. "
            "It routes your requests to specialist agents and validates cross-discipline consistency.")

    # --- Coordinator request ---
    section_header("Send Request to Coordinator")

    request_type = st.selectbox("Request Type", [
        "Process all pending discipline data",
        "Generate feasibility assessment",
        "Run structural analysis",
        "Generate geotechnical report",
        "Run hydraulic calculations",
        "Compile tender package",
        "Update project schedule",
        "Generate consolidated report",
        "Custom request",
    ], key="ai_req_type")

    if request_type == "Custom request":
        custom_text = st.text_area("Describe your request", placeholder="e.g. Check if the updated rainfall data affects the structural load calculations and update the Gantt accordingly.", height=120, key="ai_custom")
    else:
        custom_text = ""

    if st.button("🤖 Send to Coordinator", use_container_width=True, type="primary", key="ai_send"):
        st.markdown("---")
        st.markdown(f"""
        <div style="background: #F0F2F6; border-radius: 10px; padding: 1.5rem; text-align: center;">
            <h3 style="color: #1B3A5C;">Coordinator Processing...</h3>
            <p style="color: #6B7280;">Request: <strong>{request_type}</strong></p>
            <p style="color: #6B7280; font-size: 0.9rem;">
                This feature will be fully operational in <strong>Phase 2</strong> when the trained
                Coordinator and Specialist agents are deployed.
            </p>
            <p style="color: #D97706; font-size: 0.85rem;">
                The Coordinator will route this to the relevant specialist agent(s),
                validate cross-discipline consistency, and return results to the originating page.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- Agent Architecture Overview ---
    section_header("Agent Architecture")
    st.markdown("""
    | Agent | Role | Status |
    |-------|------|--------|
    | **Coordinator** | Routes requests, validates cross-discipline consistency | Phase 2 |
    | Feasibility Study Agent | Site viability analysis, constraint mapping | Phase 2 |
    | Structural Analysis Agent | Load calculations, member sizing, code compliance | Phase 2 |
    | Geotechnical Agent | Soil analysis, foundation recommendations | Phase 2 |
    | Hydraulics & Fluid Dynamics Agent | Pipe sizing, flow calculations | Phase 2 |
    | Hydrology & Water Resources Agent | Rainfall analysis, flood modelling | Phase 2 |
    | Project Management Agent | Gantt updates, critical path, resource allocation | Phase 2 |
    | Tender & Procurement Agent | BOQ generation, spec writing, evaluation matrices | Phase 2 |
    | Report Compilation Agent | Branded Word/Excel/PDF assembly | Phase 2 |
    """)

    st.divider()

    # --- Activity log ---
    section_header("Agent Activity Log")
    updates = project.get("updates", [])[:10]
    if updates:
        for u in updates:
            st.markdown(f"**{u['timestamp']}** — {u['message']}")
    else:
        st.info("No agent activity recorded yet.")
