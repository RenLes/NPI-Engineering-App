import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_word


def hydraulics_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    disc = project["disciplines"]["hydraulics"]
    page_title("Hydraulics & Water Systems", f"{project['name']} — Stormwater, drainage, and water reticulation")

    # --- Cross-discipline impact banner ---
    st.warning("📡 **Cross-discipline impact:** Data entered here automatically flows to:\n"
               "- **Geotechnical** (soil saturation estimates)\n"
               "- **Structural** (flood load calculations)\n"
               "- **Project Management** (Gantt risk updates)")

    # --- Input form ---
    section_header("Hydraulic Parameters")
    c1, c2 = st.columns(2)
    with c1:
        rainfall = st.text_input("Design Rainfall Intensity", value=disc["inputs"].get("rainfall_intensity", ""), placeholder="e.g. 180 mm/hr (1% AEP)")
        catchment = st.text_input("Catchment Area", value=disc["inputs"].get("catchment_area", ""), placeholder="e.g. 2.8 ha")
        runoff = st.text_input("Runoff Coefficient (C)", value=disc["inputs"].get("runoff_coefficient", ""), placeholder="e.g. 0.85")
    with c2:
        tc = st.text_input("Time of Concentration", value=disc["inputs"].get("time_of_concentration", ""), placeholder="e.g. 15 min")
        pipe_size = st.text_input("Proposed Pipe Size", value=disc["inputs"].get("pipe_size", ""), placeholder="e.g. 450mm RCP")
        aep = st.selectbox("Design AEP", ["1% (1 in 100)", "2% (1 in 50)", "5% (1 in 20)", "10% (1 in 10)", "20% (1 in 5)"], key="hyd_aep")

    detention = st.text_input("Detention Volume Required", value=disc["inputs"].get("detention", ""), placeholder="e.g. 350 m3")
    water_quality = st.selectbox("Water Quality Treatment", ["Bioretention Basin", "Constructed Wetland", "Gross Pollutant Trap", "Sediment Basin", "None Required", "Other"], key="hyd_wq")

    if st.button("Save Inputs", key="hyd_save"):
        store.update_discipline(st.session_state.current_project, "hydraulics",
            inputs={"rainfall_intensity": rainfall, "catchment_area": catchment, "runoff_coefficient": runoff,
                    "time_of_concentration": tc, "pipe_size": pipe_size, "aep": aep,
                    "detention": detention, "water_quality": water_quality},
            status="In Progress" if not disc["draft"] else disc["status"])
        # Cross-discipline update: add to project updates
        if rainfall:
            store.add_update(st.session_state.current_project,
                f"Hydraulics rainfall data updated ({rainfall}) — impacts Geotech & Structural", "hydraulics")
        st.success("Inputs saved. Cross-discipline data updated.")
        st.rerun()

    st.divider()

    # --- File upload ---
    section_header("Upload Hydrological Data")
    st.markdown('<div class="upload-zone">Drag and drop hydraulics files here<br><small>Rainfall IFD data, MUSIC models, drainage plans, flow calculations</small></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload hydraulics files", accept_multiple_files=True, key="hyd_upload", label_visibility="collapsed")
    if uploaded:
        new_files = disc["files"] + [f.name for f in uploaded]
        store.update_discipline(st.session_state.current_project, "hydraulics", files=new_files, status="Data Uploaded")
        st.success(f"{len(uploaded)} file(s) uploaded.")

    if disc["files"]:
        st.caption(f"Uploaded files: {', '.join(disc['files'])}")

    st.divider()

    # --- Coordinator ---
    section_header("AI Processing")
    if st.button("🤖 Send to Coordinator", use_container_width=True, type="primary", key="hyd_coord"):
        st.info("Coordinator will process hydraulic data, run flow calculations, and check cross-discipline impacts. Available in Phase 2.")

    st.divider()

    # --- Draft viewer ---
    section_header("Draft Output")
    if disc["draft"]:
        draft_text = st.text_area("Draft Hydraulics Report", value=disc["draft"], height=200, key="hyd_draft_edit")
        if draft_text != disc["draft"]:
            store.update_discipline(st.session_state.current_project, "hydraulics", draft=draft_text)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Approve", type="primary", key="hyd_approve"):
                store.update_discipline(st.session_state.current_project, "hydraulics", approved=True, status="Approved")
                st.success("Draft approved.")
                st.rerun()
        with c2:
            if st.button("🔄 Request Amendment", key="hyd_amend"):
                store.update_discipline(st.session_state.current_project, "hydraulics", approved=False, status="Amendment Requested")
                st.warning("Amendment requested.")
                st.rerun()
        with c3:
            sections = [{"heading": "Hydraulics & Water Systems Report", "body": disc["draft"]},
                        {"heading": "Hydraulic Parameters", "body": "\n".join(f"{k}: {v}" for k, v in disc["inputs"].items() if v)}]
            word_buf = export_word(f"{project['name']} – Hydraulics Report", sections)
            st.download_button("📥 Export (Word)", word_buf, file_name=f"{project['name']}_Hydraulics.docx")
    else:
        st.info("No draft available yet. Upload hydrological data and send to Coordinator to generate a draft.")

    st.divider()
    approved_icon = "✅" if disc["approved"] else "⏳"
    st.caption(f"Status: {disc['status']} {approved_icon}")
