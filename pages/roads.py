import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_word, export_excel


def roads_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    disc = project["disciplines"]["roads"]
    page_title("Roads & Pavements", f"{project['name']} - Sealed and unsealed road design")

    tab_sealed, tab_unsealed = st.tabs(["Sealed Roads", "Unsealed Roads"])

    with tab_sealed:
        _sealed_roads_tab(store, project, disc)

    with tab_unsealed:
        _unsealed_roads_tab(store, project, disc)


def _sealed_roads_tab(store: ProjectStore, project: dict, disc: dict):
    section_header("Sealed Road Design Parameters")

    pid = st.session_state.current_project
    sealed_key = f"roads_sealed_{pid}"
    if sealed_key not in st.session_state:
        st.session_state[sealed_key] = disc["inputs"].get("sealed", {})

    saved = st.session_state[sealed_key]

    c1, c2 = st.columns(2)
    with c1:
        road_class = st.selectbox("Road Classification",
            ["Arterial", "Sub-Arterial", "Collector", "Local Access", "Cul-de-sac", "Industrial Access"],
            index=0, key="rd_sealed_class")
        design_speed = st.text_input("Design Speed (km/h)", value=saved.get("design_speed", ""), placeholder="e.g. 60", key="rd_sealed_speed")
        lane_width = st.text_input("Lane Width (m)", value=saved.get("lane_width", ""), placeholder="e.g. 3.5", key="rd_sealed_lane")
        num_lanes = st.selectbox("Number of Lanes", ["1", "2", "4", "6"], index=1, key="rd_sealed_lanes")
    with c2:
        pavement_type = st.selectbox("Pavement Type",
            ["Flexible (Asphalt)", "Rigid (Concrete)", "Composite", "Full Depth Asphalt"],
            key="rd_sealed_pave")
        design_traffic = st.text_input("Design Traffic (ESA)", value=saved.get("design_traffic", ""), placeholder="e.g. 5 x 10^6 ESA", key="rd_sealed_esa")
        cbr = st.text_input("Subgrade CBR (%)", value=saved.get("cbr", ""), placeholder="e.g. 5", key="rd_sealed_cbr")
        design_life = st.selectbox("Design Life (years)", ["20", "30", "40"], index=0, key="rd_sealed_life")

    section_header("Pavement Composition")
    c1, c2 = st.columns(2)
    with c1:
        wearing_course = st.text_input("Wearing Course", value=saved.get("wearing_course", ""), placeholder="e.g. 40mm AC14 Asphalt", key="rd_sealed_wear")
        base_course = st.text_input("Base Course", value=saved.get("base_course", ""), placeholder="e.g. 200mm Type 2.1 Crushed Rock", key="rd_sealed_base")
    with c2:
        sub_base = st.text_input("Sub-base Course", value=saved.get("sub_base", ""), placeholder="e.g. 250mm Type 2.3 Crushed Rock", key="rd_sealed_subbase")
        geofabric = st.selectbox("Geotextile/Geofabric", ["Not Required", "Separation Layer", "Reinforcement Layer", "Both"], key="rd_sealed_geo")

    section_header("Geometric Design")
    c1, c2, c3 = st.columns(3)
    with c1:
        crossfall = st.text_input("Crossfall (%)", value=saved.get("crossfall", ""), placeholder="e.g. 3", key="rd_sealed_xfall")
        vertical_grade = st.text_input("Max Vertical Grade (%)", value=saved.get("vertical_grade", ""), placeholder="e.g. 8", key="rd_sealed_grade")
    with c2:
        min_radius = st.text_input("Min Horizontal Curve Radius (m)", value=saved.get("min_radius", ""), placeholder="e.g. 120", key="rd_sealed_radius")
        superelevation = st.text_input("Max Superelevation (%)", value=saved.get("superelevation", ""), placeholder="e.g. 6", key="rd_sealed_super")
    with c3:
        kerb_type = st.selectbox("Kerb Type", ["Barrier Kerb", "Semi-mountable", "Mountable", "No Kerb"], key="rd_sealed_kerb")
        footpath = st.selectbox("Footpath", ["Both Sides", "One Side", "None"], key="rd_sealed_foot")

    design_standard = st.selectbox("Design Standard",
        ["Austroads Guide to Pavement Technology", "QTMR MRTS", "AS 2150 (Hot Mix Asphalt)", "Local Council Standards", "Other"],
        key="rd_sealed_std")

    if st.button("Save Sealed Road Data", type="primary", key="rd_sealed_save"):
        sealed_data = {
            "road_class": road_class, "design_speed": design_speed, "lane_width": lane_width,
            "num_lanes": num_lanes, "pavement_type": pavement_type, "design_traffic": design_traffic,
            "cbr": cbr, "design_life": design_life, "wearing_course": wearing_course,
            "base_course": base_course, "sub_base": sub_base, "geofabric": geofabric,
            "crossfall": crossfall, "vertical_grade": vertical_grade, "min_radius": min_radius,
            "superelevation": superelevation, "kerb_type": kerb_type, "footpath": footpath,
            "design_standard": design_standard,
        }
        st.session_state[sealed_key] = sealed_data
        current_inputs = disc["inputs"].copy()
        current_inputs["sealed"] = sealed_data
        store.update_discipline(pid, "roads", inputs=current_inputs, status="In Progress")
        st.success("Sealed road data saved.")
        st.rerun()

    st.divider()

    # File upload
    section_header("Upload Drawings & Reports")
    st.markdown('<div class="upload-zone">Drag and drop road design files here<br><small>Alignment drawings, pavement designs, long sections, cross sections</small></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload sealed road files", accept_multiple_files=True, key="rd_sealed_upload", label_visibility="collapsed")
    if uploaded:
        new_files = disc["files"] + [f.name for f in uploaded]
        store.update_discipline(pid, "roads", files=new_files, status="Data Uploaded")
        st.success(f"{len(uploaded)} file(s) uploaded.")

    if disc["files"]:
        st.caption(f"Uploaded files: {', '.join(disc['files'])}")

    st.divider()

    # Coordinator + Draft
    _coordinator_and_draft(store, project, disc, "sealed")


def _unsealed_roads_tab(store: ProjectStore, project: dict, disc: dict):
    section_header("Unsealed Road Design Parameters")

    pid = st.session_state.current_project
    unsealed_key = f"roads_unsealed_{pid}"
    if unsealed_key not in st.session_state:
        st.session_state[unsealed_key] = disc["inputs"].get("unsealed", {})

    saved = st.session_state[unsealed_key]

    c1, c2 = st.columns(2)
    with c1:
        road_function = st.selectbox("Road Function",
            ["Rural Access", "Rural Collector", "Agricultural Access", "Mining/Haul Road", "Temporary Construction Road"],
            key="rd_uns_func")
        traffic_volume = st.text_input("Traffic Volume (vpd)", value=saved.get("traffic_volume", ""), placeholder="e.g. 150 vpd", key="rd_uns_vpd")
        heavy_vehicles = st.text_input("Heavy Vehicle % ", value=saved.get("heavy_vehicles", ""), placeholder="e.g. 25", key="rd_uns_hv")
    with c2:
        formation_width = st.text_input("Formation Width (m)", value=saved.get("formation_width", ""), placeholder="e.g. 8.0", key="rd_uns_width")
        carriageway_width = st.text_input("Carriageway Width (m)", value=saved.get("carriageway_width", ""), placeholder="e.g. 6.0", key="rd_uns_cway")
        shoulder_width = st.text_input("Shoulder Width (m)", value=saved.get("shoulder_width", ""), placeholder="e.g. 1.0", key="rd_uns_shoulder")

    section_header("Gravel Pavement")
    c1, c2 = st.columns(2)
    with c1:
        gravel_type = st.selectbox("Gravel Material",
            ["Natural Gravel", "Laterite", "Crushed Rock", "Quarry Waste", "Recycled Concrete", "Stabilised Gravel"],
            key="rd_uns_gravel")
        gravel_depth = st.text_input("Gravel Wearing Course Depth (mm)", value=saved.get("gravel_depth", ""), placeholder="e.g. 150", key="rd_uns_depth")
    with c2:
        pi_range = st.selectbox("Plasticity Index (PI) Range",
            ["4-9 (Low traffic)", "6-12 (Moderate traffic)", "10-15 (Heavy traffic)"],
            key="rd_uns_pi")
        grading = st.selectbox("Grading Specification",
            ["QTMR Type 3.3", "QTMR Type 3.5", "Austroads Class 3", "Custom Spec"],
            key="rd_uns_grade_spec")

    section_header("Drainage & Maintenance")
    c1, c2 = st.columns(2)
    with c1:
        crossfall_uns = st.text_input("Crossfall (%)", value=saved.get("crossfall", ""), placeholder="e.g. 4-6", key="rd_uns_xfall")
        table_drain = st.selectbox("Table Drain Type", ["V-Drain", "Trapezoidal", "Lined Channel", "Swale"], key="rd_uns_drain")
    with c2:
        culvert_spacing = st.text_input("Culvert Spacing (m)", value=saved.get("culvert_spacing", ""), placeholder="e.g. 200", key="rd_uns_culvert")
        regrade_freq = st.selectbox("Estimated Regrading Frequency",
            ["Monthly", "Quarterly", "Biannually", "Annually"],
            key="rd_uns_regrade")

    dust_suppression = st.selectbox("Dust Suppression",
        ["None Required", "Water Cart", "Chloride Treatment", "Bitumen Emulsion Seal", "Polymer Stabilisation"],
        key="rd_uns_dust")

    if st.button("Save Unsealed Road Data", type="primary", key="rd_uns_save"):
        unsealed_data = {
            "road_function": road_function, "traffic_volume": traffic_volume,
            "heavy_vehicles": heavy_vehicles, "formation_width": formation_width,
            "carriageway_width": carriageway_width, "shoulder_width": shoulder_width,
            "gravel_type": gravel_type, "gravel_depth": gravel_depth,
            "pi_range": pi_range, "grading": grading, "crossfall": crossfall_uns,
            "table_drain": table_drain, "culvert_spacing": culvert_spacing,
            "regrade_freq": regrade_freq, "dust_suppression": dust_suppression,
        }
        st.session_state[unsealed_key] = unsealed_data
        current_inputs = disc["inputs"].copy()
        current_inputs["unsealed"] = unsealed_data
        store.update_discipline(pid, "roads", inputs=current_inputs, status="In Progress")
        st.success("Unsealed road data saved.")
        st.rerun()

    st.divider()

    # File upload
    section_header("Upload Survey & Design Files")
    st.markdown('<div class="upload-zone">Drag and drop unsealed road files here<br><small>Survey data, gravel test results, alignment plans, maintenance records</small></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload unsealed road files", accept_multiple_files=True, key="rd_uns_upload", label_visibility="collapsed")
    if uploaded:
        new_files = disc["files"] + [f.name for f in uploaded]
        store.update_discipline(pid, "roads", files=new_files)
        st.success(f"{len(uploaded)} file(s) uploaded.")

    st.divider()

    # Coordinator + Draft
    _coordinator_and_draft(store, project, disc, "unsealed")


def _coordinator_and_draft(store: ProjectStore, project: dict, disc: dict, road_type: str):
    section_header("AI Processing")
    if st.button("Send to Coordinator", use_container_width=True, type="primary", key=f"rd_{road_type}_coord"):
        st.info(f"Coordinator will process {road_type} road data, check pavement design, and validate drainage. Available in Phase 2.")

    st.divider()

    section_header("Draft Output")
    if disc["draft"]:
        draft_text = st.text_area(f"Draft Roads Report", value=disc["draft"], height=200, key=f"rd_{road_type}_draft")
        if draft_text != disc["draft"]:
            store.update_discipline(st.session_state.current_project, "roads", draft=draft_text)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Approve", type="primary", key=f"rd_{road_type}_approve"):
                store.update_discipline(st.session_state.current_project, "roads", approved=True, status="Approved")
                st.success("Draft approved.")
                st.rerun()
        with c2:
            if st.button("Request Amendment", key=f"rd_{road_type}_amend"):
                store.update_discipline(st.session_state.current_project, "roads", approved=False, status="Amendment Requested")
                st.warning("Amendment requested.")
                st.rerun()
        with c3:
            sections = [{"heading": f"{road_type.title()} Road Report", "body": disc["draft"]},
                        {"heading": "Parameters", "body": "\n".join(f"{k}: {v}" for k, v in disc["inputs"].get(road_type, {}).items() if v)}]
            word_buf = export_word(f"{project['name']} - {road_type.title()} Roads Report", sections)
            st.download_button("Export (Word)", word_buf, file_name=f"{project['name']}_Roads_{road_type}.docx", key=f"rd_{road_type}_export")
    else:
        st.info("No draft available yet. Upload data and send to Coordinator to generate a draft.")

    st.divider()
    approved_icon = "approved" if disc["approved"] else "pending"
    st.caption(f"Status: {disc['status']} ({approved_icon})")
