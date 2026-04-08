import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_word


def geotechnical_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    disc = project["disciplines"]["geotechnical"]
    page_title("Geotechnical Engineering", f"{project['name']} — Soil investigation and foundation design")

    # --- Input form ---
    section_header("Geotechnical Parameters")
    c1, c2 = st.columns(2)
    with c1:
        soil_type = st.selectbox("Predominant Soil Type",
            ["Alluvial Clay", "Residual Clay", "Sandy Clay", "Silty Sand", "Gravelly Sand", "Rock", "Fill", "Other"],
            index=0, key="geo_soil")
        bearing_capacity = st.text_input("Allowable Bearing Capacity", value=disc["inputs"].get("bearing_capacity", ""), placeholder="e.g. 150 kPa")
        water_table = st.text_input("Water Table Depth", value=disc["inputs"].get("water_table", ""), placeholder="e.g. 2.5m BGL")
    with c2:
        rock_depth = st.text_input("Depth to Rock", value=disc["inputs"].get("rock_depth", ""), placeholder="e.g. 8-10m")
        plasticity = st.selectbox("Plasticity Index", ["Low (PI < 10)", "Medium (10 < PI < 20)", "High (PI > 20)"], key="geo_pi")
        foundation_rec = st.selectbox("Recommended Foundation Type",
            ["Strip Footings", "Pad Footings", "Raft Slab", "Bored Piles", "Driven Piles", "Screw Piles", "To Be Determined"],
            key="geo_found")

    reactive_class = st.selectbox("Reactive Site Classification (AS 2870)",
        ["A (Non-reactive)", "S (Slightly reactive)", "M (Moderately reactive)", "H1 (Highly reactive)", "H2 (Very highly reactive)", "E (Extremely reactive)"],
        key="geo_reactive")

    if st.button("Save Inputs", key="geo_save"):
        store.update_discipline(st.session_state.current_project, "geotechnical",
            inputs={"soil_type": soil_type, "bearing_capacity": bearing_capacity, "water_table": water_table,
                    "rock_depth": rock_depth, "plasticity": plasticity, "foundation_rec": foundation_rec,
                    "reactive_class": reactive_class},
            status="In Progress" if not disc["draft"] else disc["status"])
        st.success("Inputs saved.")
        st.rerun()

    st.divider()

    # --- File upload ---
    section_header("Upload Borehole Logs & Reports")
    st.markdown('<div class="upload-zone">Drag and drop geotechnical files here<br><small>Borehole logs, lab test results, previous geotech reports</small></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload geotechnical files", accept_multiple_files=True, key="geo_upload", label_visibility="collapsed")
    if uploaded:
        new_files = disc["files"] + [f.name for f in uploaded]
        store.update_discipline(st.session_state.current_project, "geotechnical", files=new_files, status="Data Uploaded")
        st.success(f"{len(uploaded)} file(s) uploaded.")

    if disc["files"]:
        st.caption(f"Uploaded files: {', '.join(disc['files'])}")

    st.divider()

    # --- Cross-discipline notice ---
    hydro = project["disciplines"]["hydraulics"]
    if hydro["inputs"].get("rainfall_intensity"):
        st.info(f"📡 **Hydraulics data linked:** Rainfall intensity {hydro['inputs']['rainfall_intensity']} may affect soil saturation and bearing capacity estimates.")

    # --- Coordinator ---
    section_header("AI Processing")
    if st.button("🤖 Send to Coordinator", use_container_width=True, type="primary", key="geo_coord"):
        st.info("Coordinator will process geotechnical data and generate investigation report. Available in Phase 2.")

    st.divider()

    # --- Draft viewer ---
    section_header("Draft Output")
    if disc["draft"]:
        draft_text = st.text_area("Draft Geotechnical Report", value=disc["draft"], height=200, key="geo_draft_edit")
        if draft_text != disc["draft"]:
            store.update_discipline(st.session_state.current_project, "geotechnical", draft=draft_text)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("✅ Approve", type="primary", key="geo_approve"):
                store.update_discipline(st.session_state.current_project, "geotechnical", approved=True, status="Approved")
                st.success("Draft approved.")
                st.rerun()
        with c2:
            if st.button("🔄 Request Amendment", key="geo_amend"):
                store.update_discipline(st.session_state.current_project, "geotechnical", approved=False, status="Amendment Requested")
                st.warning("Amendment requested.")
                st.rerun()
        with c3:
            sections = [{"heading": "Geotechnical Investigation Report", "body": disc["draft"]},
                        {"heading": "Soil Parameters", "body": "\n".join(f"{k}: {v}" for k, v in disc["inputs"].items() if v)}]
            word_buf = export_word(f"{project['name']} – Geotechnical Report", sections)
            st.download_button("📥 Export (Word)", word_buf, file_name=f"{project['name']}_Geotechnical.docx")
    else:
        st.info("No draft available yet. Upload borehole data and send to Coordinator to generate a draft.")

    st.divider()
    approved_icon = "✅" if disc["approved"] else "⏳"
    st.caption(f"Status: {disc['status']} {approved_icon}")
