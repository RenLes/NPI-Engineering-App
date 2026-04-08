import streamlit as st
import pandas as pd
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_word, export_excel, export_pdf


def reports_exports_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    page_title("Reports & Exports", f"{project['name']} — Generate and download deliverables")

    # --- Discipline Reports ---
    section_header("Discipline Reports")

    labels = {
        "feasibility": "Feasibility Study",
        "structural": "Structural Engineering",
        "geotechnical": "Geotechnical Investigation",
        "hydraulics": "Hydraulics & Water Systems",
        "tenders": "Tender Package",
        "budget": "Budget & Cost Report",
    }

    for key, label in labels.items():
        disc = project["disciplines"][key]
        status_icon = "✅" if disc["approved"] else {"Draft Ready": "📝", "In Progress": "🔄", "Data Uploaded": "📤", "Approved": "✅"}.get(disc["status"], "⬜")

        with st.expander(f"{status_icon} {label} — {disc['status']}"):
            if disc["draft"] or disc["inputs"]:
                sections = []
                if disc["draft"]:
                    sections.append({"heading": f"{label} Report", "body": disc["draft"]})
                if disc["inputs"]:
                    params = "\n".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in disc["inputs"].items() if v)
                    sections.append({"heading": "Parameters", "body": params})

                c1, c2, c3 = st.columns(3)
                with c1:
                    word_buf = export_word(f"{project['name']} – {label}", sections)
                    st.download_button(f"📥 Word", word_buf, file_name=f"{project['name']}_{key}.docx", key=f"rep_word_{key}")
                with c2:
                    pdf_buf = export_pdf(f"{project['name']} – {label}", sections)
                    st.download_button(f"📥 PDF", pdf_buf, file_name=f"{project['name']}_{key}.pdf", key=f"rep_pdf_{key}", mime="application/pdf")
                with c3:
                    if disc["inputs"]:
                        df = pd.DataFrame([disc["inputs"]])
                        excel_buf = export_excel(f"{project['name']} {label}", {label: df})
                        st.download_button(f"📥 Excel", excel_buf, file_name=f"{project['name']}_{key}.xlsx", key=f"rep_excel_{key}", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                st.info(f"No data available for {label}. Enter data on the discipline page first.")

    st.divider()

    # --- Consolidated Project Report ---
    section_header("Consolidated Project Report")
    st.markdown("Generate a single document covering all disciplines for this project.")

    all_sections = [
        {"heading": "Project Summary", "body": f"Project: {project['name']}\nClient: {project['client']}\nLocation: {project['location']}\nPhase: {project['phase']}\nProgress: {project['progress']}%\nDeadline: {project['deadline']}"},
    ]

    for key, label in labels.items():
        disc = project["disciplines"][key]
        body_parts = []
        if disc["inputs"]:
            body_parts.append("Parameters:\n" + "\n".join(f"  {k.replace('_', ' ').title()}: {v}" for k, v in disc["inputs"].items() if v))
        if disc["draft"]:
            body_parts.append(f"Draft:\n{disc['draft']}")
        body_parts.append(f"Status: {disc['status']} | Approved: {'Yes' if disc['approved'] else 'No'}")
        all_sections.append({"heading": label, "body": "\n\n".join(body_parts)})

    # Tasks section
    tasks = project.get("tasks", [])
    if tasks:
        task_text = "\n".join(f"  {t['name']} ({t['discipline']}) — {t['status']} — {t['assignee']}" for t in tasks)
        all_sections.append({"heading": "Task Schedule", "body": task_text})

    # Risks section
    risks = project.get("risks", [])
    if risks:
        risk_text = "\n".join(f"  {r['risk']} — L: {r['likelihood']} I: {r['impact']} — {r['mitigation']}" for r in risks)
        all_sections.append({"heading": "Risk Register", "body": risk_text})

    c1, c2, c3 = st.columns(3)
    with c1:
        word_buf = export_word(f"{project['name']} – Consolidated Report", all_sections)
        st.download_button("📥 Full Report (Word)", word_buf, file_name=f"{project['name']}_Full_Report.docx", use_container_width=True)
    with c2:
        pdf_buf = export_pdf(f"{project['name']} – Consolidated Report", all_sections)
        st.download_button("📥 Full Report (PDF)", pdf_buf, file_name=f"{project['name']}_Full_Report.pdf", use_container_width=True, mime="application/pdf")
    with c3:
        # Excel with one sheet per discipline
        dfs = {}
        for key, label in labels.items():
            disc = project["disciplines"][key]
            if disc["inputs"]:
                dfs[label[:31]] = pd.DataFrame([disc["inputs"]])
        if tasks:
            dfs["Tasks"] = pd.DataFrame(tasks)
        if risks:
            dfs["Risks"] = pd.DataFrame(risks)
        if dfs:
            excel_buf = export_excel(f"{project['name']} Data", dfs)
            st.download_button("📥 Full Data (Excel)", excel_buf, file_name=f"{project['name']}_Data.xlsx", use_container_width=True, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.divider()

    # --- Export history (mock) ---
    section_header("Export History")
    st.caption("Recent exports from this project:")
    history = [
        {"Date": "2026-04-08 14:30", "Document": "Feasibility Study (Word)", "User": "Sarah Chen"},
        {"Date": "2026-04-07 09:15", "Document": "Geotechnical Report (PDF)", "User": "James Patel"},
        {"Date": "2026-04-06 16:45", "Document": "Project Schedule (Excel)", "User": "Sarah Chen"},
    ]
    st.dataframe(pd.DataFrame(history), use_container_width=True, hide_index=True)
