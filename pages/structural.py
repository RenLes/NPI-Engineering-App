import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_word, export_pdf


def structural_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    disc = project["disciplines"]["structural"]
    page_title("Structural Engineering", f"{project['name']} — Structural analysis and design")

    # --- Input form ---
    section_header("Structural Parameters")
    c1, c2 = st.columns(2)
    with c1:
        structure_type = st.selectbox("Structure Type",
            ["Reinforced Concrete Frame", "Steel Frame", "Timber Frame", "Masonry", "Precast Concrete", "Other"],
            index=["Reinforced Concrete Frame", "Steel Frame", "Timber Frame", "Masonry", "Precast Concrete", "Other"].index(disc["inputs"].get("structure_type", "Reinforced Concrete Frame")) if disc["inputs"].get("structure_type") in ["Reinforced Concrete Frame", "Steel Frame", "Timber Frame", "Masonry", "Precast Concrete", "Other"] else 0,
            key="str_type")
        storeys = st.text_input("Number of Storeys", value=disc["inputs"].get("storeys", ""), placeholder="e.g. 6")
        floor_area = st.text_input("Typical Floor Area", value=disc["inputs"].get("floor_area", ""), placeholder="e.g. 800 m2")
    with c2:
        design_code = st.selectbox("Design Code",
            ["AS 3600-2018 (Concrete)", "AS 4100-2020 (Steel)", "AS 1720 (Timber)", "NZS 3101 (NZ Concrete)", "Other"],
            key="str_code")
        live_load = st.text_input("Design Live Load", value=disc["inputs"].get("live_load", ""), placeholder="e.g. 3.0 kPa")
        wind_region = st.selectbox("Wind Region", ["A", "B", "C", "D"], key="str_wind")

    seismic = st.text_input("Seismic Hazard Factor (kp)", value=disc["inputs"].get("seismic", ""), placeholder="e.g. 0.08")

    if st.button("Save Inputs", key="str_save"):
        store.update_discipline(st.session_state.current_project, "structural",
            inputs={"structure_type": structure_type, "storeys": storeys, "floor_area": floor_area,
                    "design_code": design_code, "live_load": live_load, "wind_region": wind_region, "seismic": seismic},
            status="In Progress" if not disc["draft"] else disc["status"])
        st.success("Inputs saved.")
        st.rerun()

    st.divider()

    # --- File upload ---
    section_header("Upload Drawings & Documents")
    st.markdown('<div class="upload-zone">Drag and drop structural files here<br><small>Architectural drawings, load schedules, previous structural reports</small></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload structural files", accept_multiple_files=True, key="str_upload", label_visibility="collapsed")
    if uploaded:
        new_files = disc["files"] + [f.name for f in uploaded]
        store.update_discipline(st.session_state.current_project, "structural", files=new_files, status="Data Uploaded")
        st.success(f"{len(uploaded)} file(s) uploaded.")

    if disc["files"]:
        st.caption(f"Uploaded files: {', '.join(disc['files'])}")

    st.divider()

    # --- Cross-discipline data notice ---
    hydro = project["disciplines"]["hydraulics"]
    geo = project["disciplines"]["geotechnical"]
    if hydro["inputs"] or geo["inputs"]:
        st.info("📡 **Cross-discipline data available:** "
                + ("Hydraulics rainfall data may affect load calculations. " if hydro["inputs"] else "")
                + ("Geotechnical bearing capacity informs foundation design." if geo["inputs"] else ""))

    # --- Coordinator ---
    section_header("AI Processing")
    if st.button("🤖 Send to Coordinator", use_container_width=True, type="primary", key="str_coord"):
        st.info("Coordinator will process structural parameters and generate analysis. Available in Phase 2.")

    st.divider()

    # --- Draft viewer ---
    section_header("Draft Output")
    if disc["draft"]:
        draft_text = st.text_area("Draft Structural Analysis", value=disc["draft"], height=200, key="str_draft_edit")
        if draft_text != disc["draft"]:
            store.update_discipline(st.session_state.current_project, "structural", draft=draft_text)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Approve", type="primary", key="str_approve"):
                store.update_discipline(st.session_state.current_project, "structural", approved=True, status="Approved")
                st.success("Draft approved.")
                st.rerun()
        with c2:
            if st.button("🔄 Request Amendment", key="str_amend"):
                store.update_discipline(st.session_state.current_project, "structural", approved=False, status="Amendment Requested")
                st.warning("Amendment requested.")
                st.rerun()
        with c3:
            sections = [{"heading": "Structural Analysis", "body": disc["draft"]},
                        {"heading": "Design Parameters", "body": "\n".join(f"{k}: {v}" for k, v in disc["inputs"].items() if v)}]
            word_buf = export_word(f"{project['name']} – Structural Report", sections)
            st.download_button("📥 Export (Word)", word_buf, file_name=f"{project['name']}_Structural.docx")
    else:
        st.info("No draft available yet. Upload data and send to Coordinator to generate a draft.")

    st.divider()
    approved_icon = "✅" if disc["approved"] else "⏳"
    st.caption(f"Status: {disc['status']} {approved_icon}")
