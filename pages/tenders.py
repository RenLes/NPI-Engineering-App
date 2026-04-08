import streamlit as st
import pandas as pd
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_word, export_excel


def tenders_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    disc = project["disciplines"]["tenders"]
    page_title("Tenders & Bids", f"{project['name']} — BOQ, specifications, and bid packages")

    # --- BOQ Editor ---
    section_header("Bill of Quantities (BOQ)")

    # Initialize BOQ in session state
    boq_key = f"boq_{st.session_state.current_project}"
    if boq_key not in st.session_state:
        st.session_state[boq_key] = [
            {"Item": "1.1", "Description": "Site Preparation & Clearing", "Qty": 1, "Unit": "LS", "Rate": 25000.0, "Amount": 25000.0},
            {"Item": "1.2", "Description": "Bulk Earthworks", "Qty": 3500, "Unit": "m3", "Rate": 18.0, "Amount": 63000.0},
            {"Item": "2.1", "Description": "Concrete Foundations", "Qty": 120, "Unit": "m3", "Rate": 450.0, "Amount": 54000.0},
            {"Item": "2.2", "Description": "Reinforcement Steel", "Qty": 8500, "Unit": "kg", "Rate": 3.50, "Amount": 29750.0},
            {"Item": "3.1", "Description": "Stormwater Drainage (450mm RCP)", "Qty": 280, "Unit": "m", "Rate": 185.0, "Amount": 51800.0},
        ]

    boq_df = pd.DataFrame(st.session_state[boq_key])
    edited_df = st.data_editor(
        boq_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Item": st.column_config.TextColumn("Item No."),
            "Description": st.column_config.TextColumn("Description", width="large"),
            "Qty": st.column_config.NumberColumn("Quantity", min_value=0),
            "Unit": st.column_config.TextColumn("Unit"),
            "Rate": st.column_config.NumberColumn("Rate ($)", min_value=0, format="%.2f"),
            "Amount": st.column_config.NumberColumn("Amount ($)", min_value=0, format="%.2f"),
        },
        key="boq_editor",
    )

    # Recalculate amounts
    if not edited_df.empty:
        edited_df["Amount"] = edited_df["Qty"] * edited_df["Rate"]
        st.session_state[boq_key] = edited_df.to_dict("records")
        total = edited_df["Amount"].sum()
        st.markdown(f"**Total Estimate: ${total:,.2f}**")

    # Export BOQ
    c1, c2 = st.columns(2)
    with c1:
        if not edited_df.empty:
            excel_buf = export_excel(f"{project['name']} BOQ", {"BOQ": edited_df})
            st.download_button("📥 Export BOQ (Excel)", excel_buf, file_name=f"{project['name']}_BOQ.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.divider()

    # --- Tender Document Sections ---
    section_header("Tender Document Sections")

    tender_key = f"tender_sections_{st.session_state.current_project}"
    if tender_key not in st.session_state:
        st.session_state[tender_key] = {
            "scope": "This tender covers the complete civil engineering works for the project including earthworks, structural foundations, stormwater drainage, and associated infrastructure.",
            "specs": "All works shall comply with relevant Australian Standards including AS 3600 (Concrete), AS 4100 (Steel), and local council development conditions.",
            "evaluation": "Tenders will be assessed on: Price (40%), Experience (25%), Methodology (20%), Program (15%).",
        }

    sections = st.session_state[tender_key]
    sections["scope"] = st.text_area("Scope of Works", value=sections["scope"], height=100, key="tend_scope")
    sections["specs"] = st.text_area("Technical Specifications", value=sections["specs"], height=100, key="tend_specs")
    sections["evaluation"] = st.text_area("Evaluation Criteria", value=sections["evaluation"], height=80, key="tend_eval")

    if st.button("Save Tender Sections", key="tend_save"):
        store.update_discipline(st.session_state.current_project, "tenders",
            inputs=sections, status="In Progress")
        st.success("Tender sections saved.")

    st.divider()

    # --- File upload ---
    section_header("Upload Supporting Documents")
    uploaded = st.file_uploader("Upload tender documents", accept_multiple_files=True, key="tend_upload", label_visibility="collapsed")
    if uploaded:
        new_files = disc["files"] + [f.name for f in uploaded]
        store.update_discipline(st.session_state.current_project, "tenders", files=new_files)
        st.success(f"{len(uploaded)} file(s) uploaded.")

    if disc["files"]:
        st.caption(f"Uploaded files: {', '.join(disc['files'])}")

    st.divider()

    # --- Coordinator ---
    section_header("AI Processing")
    if st.button("🤖 Send to Coordinator", use_container_width=True, type="primary", key="tend_coord"):
        st.info("Coordinator will generate complete tender package from BOQ and specifications. Available in Phase 2.")

    # --- Export full tender document ---
    st.divider()
    section_header("Export Tender Package")
    word_sections = [
        {"heading": "Scope of Works", "body": sections["scope"]},
        {"heading": "Technical Specifications", "body": sections["specs"]},
        {"heading": "Evaluation Criteria", "body": sections["evaluation"]},
        {"heading": "Bill of Quantities Summary", "body": f"Total Estimate: ${total:,.2f}" if not edited_df.empty else "No BOQ items."},
    ]
    word_buf = export_word(f"{project['name']} – Tender Document", word_sections)
    st.download_button("📥 Export Full Tender (Word)", word_buf, file_name=f"{project['name']}_Tender.docx", use_container_width=True)
