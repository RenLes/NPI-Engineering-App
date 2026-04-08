import streamlit as st
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore, DISCIPLINE_KEYS, _date


def new_project_page():
    store = ProjectStore(st.session_state)
    page_title("Create New Project", "5-step project setup wizard")

    step = st.session_state.get("wizard_step", 1)

    # Progress bar
    st.progress(step / 5, text=f"Step {step} of 5")

    if step == 1:
        _step_basic_info()
    elif step == 2:
        _step_site_data()
    elif step == 3:
        _step_disciplines()
    elif step == 4:
        _step_team()
    elif step == 5:
        _step_review(store)


def _step_basic_info():
    section_header("Step 1: Basic Information")
    st.session_state.setdefault("wiz_name", "")
    st.session_state.setdefault("wiz_client", "")
    st.session_state.setdefault("wiz_location", "")
    st.session_state.setdefault("wiz_description", "")

    st.session_state.wiz_name = st.text_input("Project Name", value=st.session_state.wiz_name)
    st.session_state.wiz_client = st.text_input("Client Name", value=st.session_state.wiz_client)
    st.session_state.wiz_location = st.text_input("Site Location", value=st.session_state.wiz_location)
    st.session_state.wiz_description = st.text_area("Description", value=st.session_state.wiz_description, height=100)

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Next →", use_container_width=True, type="primary"):
            if st.session_state.wiz_name and st.session_state.wiz_client:
                st.session_state.wizard_step = 2
                st.rerun()
            else:
                st.error("Project name and client are required.")


def _step_site_data():
    section_header("Step 2: Upload Site Data")
    st.markdown('<div class="upload-zone">Drag and drop files here or click to browse<br><small>Accepted: PDF, DWG, XLSX, CSV, images</small></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload site files", accept_multiple_files=True, label_visibility="collapsed")
    if uploaded:
        st.session_state.wiz_files = [f.name for f in uploaded]
        st.success(f"{len(uploaded)} file(s) ready for upload.")
    else:
        st.session_state.setdefault("wiz_files", [])

    _nav_buttons(2)


def _step_disciplines():
    section_header("Step 3: Select Disciplines")
    st.info("Select the engineering disciplines required for this project.")

    labels = {
        "feasibility": "Feasibility Studies",
        "structural": "Structural Engineering",
        "geotechnical": "Geotechnical Engineering",
        "hydraulics": "Hydraulics & Water Systems",
        "tenders": "Tenders & Bids",
    }
    st.session_state.setdefault("wiz_disciplines", list(DISCIPLINE_KEYS))

    selected = []
    cols = st.columns(2)
    for i, key in enumerate(DISCIPLINE_KEYS):
        with cols[i % 2]:
            if st.checkbox(labels[key], value=key in st.session_state.wiz_disciplines, key=f"disc_{key}"):
                selected.append(key)
    st.session_state.wiz_disciplines = selected

    _nav_buttons(3)


def _step_team():
    section_header("Step 4: Assign Team Members")
    st.session_state.setdefault("wiz_team_raw", "")
    st.session_state.wiz_team_raw = st.text_area(
        "Team Members (one per line)",
        value=st.session_state.wiz_team_raw,
        placeholder="e.g.\nSarah Chen (Lead)\nJames Patel",
        height=120,
    )
    _nav_buttons(4)


def _step_review(store: ProjectStore):
    section_header("Step 5: Review & Create")

    st.markdown(f"**Project:** {st.session_state.get('wiz_name', '')}")
    st.markdown(f"**Client:** {st.session_state.get('wiz_client', '')}")
    st.markdown(f"**Location:** {st.session_state.get('wiz_location', '')}")
    st.markdown(f"**Description:** {st.session_state.get('wiz_description', '')}")
    st.markdown(f"**Files:** {', '.join(st.session_state.get('wiz_files', [])) or 'None'}")
    st.markdown(f"**Disciplines:** {', '.join(d.title() for d in st.session_state.get('wiz_disciplines', []))}")

    team_raw = st.session_state.get("wiz_team_raw", "")
    team = [t.strip() for t in team_raw.strip().split("\n") if t.strip()]
    st.markdown(f"**Team:** {', '.join(team) or 'None assigned'}")

    st.divider()

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = 4
            st.rerun()
    with col3:
        if st.button("Create Project", use_container_width=True, type="primary"):
            project = store.create_project(
                name=st.session_state.wiz_name,
                client=st.session_state.wiz_client,
                location=st.session_state.wiz_location,
                description=st.session_state.wiz_description,
                team=team,
                selected_disciplines=st.session_state.get("wiz_disciplines", []),
            )
            # Auto-generate initial tasks
            for disc in st.session_state.get("wiz_disciplines", []):
                store.add_task(project["id"], {
                    "name": f"{disc.title()} – Initial Assessment",
                    "discipline": disc.title(),
                    "start": _date(0),
                    "end": _date(14),
                    "status": "Not Started",
                    "assignee": team[0] if team else "Unassigned",
                })

            # Reset wizard
            st.session_state.wizard_step = 1
            for key in ["wiz_name", "wiz_client", "wiz_location", "wiz_description", "wiz_files", "wiz_disciplines", "wiz_team_raw"]:
                st.session_state.pop(key, None)

            # Go to new project
            st.session_state.current_project = project["id"]
            st.rerun()


def _nav_buttons(current_step):
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.wizard_step = current_step - 1
            st.rerun()
    with col2:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.wizard_step = current_step + 1
            st.rerun()
