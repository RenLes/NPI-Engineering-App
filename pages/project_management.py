import streamlit as st
import pandas as pd
import plotly.express as px
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_excel, export_pdf


def project_management_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    page_title("Project Management", "Gantt chart, tasks, risks & resource allocation")

    tasks = project.get("tasks", [])
    if not tasks:
        st.info("No tasks created yet. Tasks are auto-generated when you create a project or add discipline data.")
        return

    # --- Gantt Chart ---
    section_header("Gantt Chart")
    df = pd.DataFrame(tasks)
    df["start"] = pd.to_datetime(df["start"])
    df["end"] = pd.to_datetime(df["end"])

    color_map = {
        "Complete": "#16A34A",
        "In Progress": "#2C5F8A",
        "In Review": "#D97706",
        "Not Started": "#CBD5E1",
    }

    fig = px.timeline(
        df,
        x_start="start",
        x_end="end",
        y="name",
        color="status",
        color_discrete_map=color_map,
        hover_data=["discipline", "assignee"],
        title="",
    )
    fig.update_yaxes(categoryorder="array", categoryarray=list(reversed(df["name"].tolist())))
    fig.update_layout(
        height=max(300, len(tasks) * 45),
        margin=dict(l=0, r=0, t=10, b=0),
        legend_title_text="Status",
        font=dict(family="Calibri, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Task table ---
    section_header("Task List")
    task_df = pd.DataFrame(tasks)
    display_cols = ["name", "discipline", "assignee", "start", "end", "status"]
    st.dataframe(
        task_df[display_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "name": st.column_config.TextColumn("Task"),
            "discipline": st.column_config.TextColumn("Discipline"),
            "assignee": st.column_config.TextColumn("Assignee"),
            "start": st.column_config.TextColumn("Start"),
            "end": st.column_config.TextColumn("End"),
            "status": st.column_config.TextColumn("Status"),
        },
    )

    # --- Add task ---
    with st.expander("Add New Task"):
        c1, c2 = st.columns(2)
        with c1:
            new_name = st.text_input("Task Name", key="pm_new_task")
            new_disc = st.selectbox("Discipline", ["Feasibility", "Structural", "Geotechnical", "Hydraulics", "Tenders", "General"], key="pm_new_disc")
        with c2:
            new_assignee = st.text_input("Assignee", key="pm_new_assignee")
            new_start = st.date_input("Start Date", key="pm_new_start")
            new_end = st.date_input("End Date", key="pm_new_end")

        if st.button("Add Task", type="primary"):
            if new_name:
                store.add_task(st.session_state.current_project, {
                    "name": new_name,
                    "discipline": new_disc,
                    "start": str(new_start),
                    "end": str(new_end),
                    "status": "Not Started",
                    "assignee": new_assignee or "Unassigned",
                })
                st.success(f"Task '{new_name}' added.")
                st.rerun()

    st.divider()

    # --- Risk Register ---
    section_header("Risk Register")
    risks = project.get("risks", [])
    if risks:
        risk_df = pd.DataFrame(risks)
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
    else:
        st.info("No risks logged yet.")

    with st.expander("Add Risk"):
        r1, r2, r3 = st.columns(3)
        with r1:
            risk_desc = st.text_input("Risk Description", key="pm_risk_desc")
        with r2:
            risk_like = st.selectbox("Likelihood", ["Low", "Medium", "High"], key="pm_risk_like")
        with r3:
            risk_impact = st.selectbox("Impact", ["Low", "Medium", "High"], key="pm_risk_imp")
        risk_mit = st.text_input("Mitigation Strategy", key="pm_risk_mit")
        if st.button("Add Risk", type="primary", key="pm_add_risk"):
            if risk_desc:
                project.setdefault("risks", []).append({
                    "risk": risk_desc,
                    "likelihood": risk_like,
                    "impact": risk_impact,
                    "mitigation": risk_mit,
                })
                st.success("Risk added.")
                st.rerun()

    st.divider()

    # --- Exports ---
    section_header("Export")
    e1, e2 = st.columns(2)
    with e1:
        excel_buf = export_excel("Project Schedule", {"Tasks": task_df, "Risks": pd.DataFrame(risks) if risks else pd.DataFrame()})
        st.download_button("📥 Export Schedule (Excel)", excel_buf, file_name=f"{project['name']}_Schedule.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with e2:
        sections = [{"heading": "Task Schedule", "body": task_df.to_string(index=False)}]
        if risks:
            sections.append({"heading": "Risk Register", "body": pd.DataFrame(risks).to_string(index=False)})
        pdf_buf = export_pdf(f"{project['name']} – Project Schedule", sections)
        st.download_button("📥 Export Schedule (PDF)", pdf_buf, file_name=f"{project['name']}_Schedule.pdf", mime="application/pdf")
