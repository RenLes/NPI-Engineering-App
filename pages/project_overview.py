import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore


def project_overview_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    page_title(project["name"], f"{project['client']} — {project['location']}")

    # --- Key metrics row ---
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Progress", f"{project['progress']}%")
    with m2:
        st.metric("Phase", project["phase"])
    with m3:
        pending = sum(1 for d in project["disciplines"].values() if d["status"] == "Draft Ready" and not d["approved"])
        st.metric("Drafts Pending", pending)
    with m4:
        total_files = sum(len(d["files"]) for d in project["disciplines"].values())
        st.metric("Files Uploaded", total_files)

    st.divider()

    # --- Two-column layout ---
    col_left, col_right = st.columns([3, 2])

    with col_left:
        section_header("Discipline Status")
        labels = {
            "feasibility": "Feasibility Studies",
            "structural": "Structural Engineering",
            "geotechnical": "Geotechnical Engineering",
            "hydraulics": "Hydraulics & Water Systems",
            "tenders": "Tenders & Bids",
            "budget": "Budget & Costs",
        }
        for key, label in labels.items():
            disc = project["disciplines"][key]
            status = disc["status"]
            icon = "✅" if disc["approved"] else {"Draft Ready": "📝", "In Progress": "🔄", "Data Uploaded": "📤", "Not Started": "⬜"}.get(status, "⬜")
            st.markdown(f"{icon} **{label}** — {status}")

    with col_right:
        section_header("Recent Updates")
        updates = project.get("updates", [])[:8]
        if updates:
            for u in updates:
                st.caption(f"🕐 {u['timestamp']}")
                st.markdown(f"&nbsp;&nbsp;&nbsp; {u['message']}")
        else:
            st.info("No updates yet.")

    st.divider()

    # --- Team & deadline ---
    section_header("Project Details")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Team:**")
        for member in project.get("team", []):
            st.markdown(f"- {member}")
    with c2:
        st.markdown(f"**Deadline:** {project['deadline']}")
        st.markdown(f"**Created:** {project['created_at']}")
        st.markdown(f"**Last Updated:** {project['updated_at']}")

    # --- Risk summary ---
    risks = project.get("risks", [])
    if risks:
        st.divider()
        section_header("Key Risks")
        for r in risks:
            likelihood_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(r["likelihood"], "⚪")
            st.markdown(f"{likelihood_color} **{r['risk']}** — Impact: {r['impact']} | Mitigation: {r['mitigation']}")
