import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_word, export_pdf


def feasibility_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    disc = project["disciplines"]["feasibility"]
    page_title("Feasibility Studies", f"{project['name']} — Site viability and constraints analysis")

    # --- Input form ---
    section_header("Site Data Inputs")
    c1, c2 = st.columns(2)
    with c1:
        site_area = st.text_input("Site Area", value=disc["inputs"].get("site_area", ""), placeholder="e.g. 12,500 m2")
        zoning = st.text_input("Zoning Classification", value=disc["inputs"].get("zoning", ""), placeholder="e.g. Commercial B2")
    with c2:
        constraints = st.text_area("Known Constraints", value=disc["inputs"].get("constraints", ""), placeholder="e.g. Flood overlay, heritage adjacent", height=80)
        environmental = st.text_input("Environmental Considerations", value=disc["inputs"].get("environmental", ""), placeholder="e.g. Koala habitat, riparian buffer")

    if st.button("Save Inputs", key="feas_save"):
        store.update_discipline(st.session_state.current_project, "feasibility",
            inputs={"site_area": site_area, "zoning": zoning, "constraints": constraints, "environmental": environmental},
            status="In Progress" if not disc["draft"] else disc["status"])
        st.success("Inputs saved.")
        st.rerun()

    st.divider()

    # --- File upload ---
    section_header("Upload Documents")
    st.markdown('<div class="upload-zone">Drag and drop feasibility files here<br><small>Site surveys, zoning certificates, environmental reports</small></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload feasibility files", accept_multiple_files=True, key="feas_upload", label_visibility="collapsed")
    if uploaded:
        new_files = disc["files"] + [f.name for f in uploaded]
        store.update_discipline(st.session_state.current_project, "feasibility", files=new_files, status="Data Uploaded")
        st.success(f"{len(uploaded)} file(s) uploaded.")

    if disc["files"]:
        st.caption(f"Uploaded files: {', '.join(disc['files'])}")

    st.divider()

    # --- Coordinator button ---
    section_header("AI Processing")
    if st.button("🤖 Send to Coordinator", use_container_width=True, type="primary", key="feas_coord"):
        st.info("Coordinator will process feasibility data and generate draft assessment. This feature will be available in Phase 2.")

    st.divider()

    # --- Draft viewer ---
    section_header("Draft Output")
    if disc["draft"]:
        draft_text = st.text_area("Draft Feasibility Assessment", value=disc["draft"], height=200, key="feas_draft_edit")
        if draft_text != disc["draft"]:
            store.update_discipline(st.session_state.current_project, "feasibility", draft=draft_text)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Approve", type="primary", key="feas_approve"):
                store.update_discipline(st.session_state.current_project, "feasibility", approved=True, status="Approved")
                st.success("Draft approved.")
                st.rerun()
        with c2:
            if st.button("🔄 Request Amendment", key="feas_amend"):
                store.update_discipline(st.session_state.current_project, "feasibility", approved=False, status="Amendment Requested")
                st.warning("Amendment requested.")
                st.rerun()
        with c3:
            sections = [{"heading": "Feasibility Assessment", "body": disc["draft"]},
                        {"heading": "Site Parameters", "body": "\n".join(f"{k}: {v}" for k, v in disc["inputs"].items() if v)}]
            word_buf = export_word(f"{project['name']} – Feasibility Study", sections)
            st.download_button("📥 Export (Word)", word_buf, file_name=f"{project['name']}_Feasibility.docx")
    else:
        st.info("No draft available yet. Upload data and send to Coordinator to generate a draft.")

    # Status badge
    st.divider()
    approved_icon = "✅" if disc["approved"] else "⏳"
    st.caption(f"Status: {disc['status']} {approved_icon}")
