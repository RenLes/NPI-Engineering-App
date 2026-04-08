import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.styles import page_title, section_header
from utils.project_store import ProjectStore
from utils.export import export_excel, export_pdf


def budget_page():
    store = ProjectStore(st.session_state)
    project = store.get_project(st.session_state.current_project)
    if not project:
        st.error("Project not found.")
        return

    page_title("Budget & Cost Management", f"{project['name']} — Tender estimates, project budgets, and NPI financials")

    tab_tender, tab_project, tab_npi = st.tabs(["Tender Estimation", "Project Budget", "NPI Financials"])

    # ================================================================
    # TAB 1: Tender Estimation
    # ================================================================
    with tab_tender:
        _tender_estimation_tab(store, project)

    # ================================================================
    # TAB 2: Project Budget Monitoring
    # ================================================================
    with tab_project:
        _project_budget_tab(store, project)

    # ================================================================
    # TAB 3: NPI Financials
    # ================================================================
    with tab_npi:
        _npi_financials_tab(store, project)


def _tender_estimation_tab(store: ProjectStore, project: dict):
    section_header("Preliminary Tender Cost Estimate")
    st.caption("Estimate hours, travel, accommodation, and other costs for tendering on this project.")

    pid = st.session_state.current_project
    hours_key = f"budget_hours_{pid}"
    if hours_key not in st.session_state:
        st.session_state[hours_key] = [
            {"Role": "Principal Engineer", "Discipline": "Feasibility", "Hours": 24, "Rate": 280.0},
            {"Role": "Senior Engineer", "Discipline": "Structural", "Hours": 80, "Rate": 220.0},
            {"Role": "Senior Engineer", "Discipline": "Geotechnical", "Hours": 60, "Rate": 220.0},
            {"Role": "Engineer", "Discipline": "Hydraulics", "Hours": 100, "Rate": 175.0},
            {"Role": "Graduate Engineer", "Discipline": "Drafting/CAD", "Hours": 40, "Rate": 120.0},
            {"Role": "Project Manager", "Discipline": "Management", "Hours": 30, "Rate": 250.0},
        ]

    # Hours table
    st.markdown("**Engineering Hours**")
    hours_df = pd.DataFrame(st.session_state[hours_key])
    edited_hours = st.data_editor(
        hours_df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Role": st.column_config.TextColumn("Role"),
            "Discipline": st.column_config.SelectboxColumn("Discipline",
                options=["Feasibility", "Structural", "Geotechnical", "Hydraulics", "Hydrology", "Management", "Drafting/CAD", "Budget", "Other"]),
            "Hours": st.column_config.NumberColumn("Hours", min_value=0),
            "Rate": st.column_config.NumberColumn("Rate ($/hr)", min_value=0, format="$%.2f"),
        },
        key="budget_hours_editor",
    )
    if not edited_hours.empty:
        edited_hours["Amount"] = edited_hours["Hours"] * edited_hours["Rate"]
        st.session_state[hours_key] = edited_hours.drop(columns=["Amount"], errors="ignore").to_dict("records")
        labour_total = edited_hours["Amount"].sum()
        total_hours = edited_hours["Hours"].sum()
    else:
        labour_total = 0.0
        total_hours = 0

    st.markdown(f"**Labour Subtotal: ${labour_total:,.2f}** ({total_hours:.0f} hours)")

    st.divider()

    # Travel & accommodation
    st.markdown("**Travel & Accommodation**")
    c1, c2 = st.columns(2)
    with c1:
        travel_trips = st.number_input("Number of Site Visits", min_value=0, value=4, key="budget_trips")
        travel_cost_per = st.number_input("Travel Cost per Trip ($)", min_value=0.0, value=850.0, step=50.0, key="budget_travel_cost")
    with c2:
        accom_nights = st.number_input("Accommodation Nights", min_value=0, value=6, key="budget_nights")
        accom_rate = st.number_input("Per Night Rate ($)", min_value=0.0, value=195.0, step=10.0, key="budget_accom_rate")

    travel_total = travel_trips * travel_cost_per
    accom_total = accom_nights * accom_rate
    st.markdown(f"Travel: ${travel_total:,.2f} | Accommodation: ${accom_total:,.2f}")

    st.divider()

    # Other costs
    st.markdown("**Other Costs**")
    c1, c2, c3 = st.columns(3)
    with c1:
        equipment = st.number_input("Equipment & Testing ($)", min_value=0.0, value=5000.0, step=500.0, key="budget_equip")
    with c2:
        subconsultants = st.number_input("Subconsultants ($)", min_value=0.0, value=15000.0, step=1000.0, key="budget_sub")
    with c3:
        contingency_pct = st.number_input("Contingency (%)", min_value=0.0, max_value=50.0, value=10.0, step=1.0, key="budget_cont")

    subtotal = labour_total + travel_total + accom_total + equipment + subconsultants
    contingency = subtotal * (contingency_pct / 100)
    grand_total = subtotal + contingency

    st.divider()

    # Summary
    section_header("Tender Estimate Summary")
    summary_data = {
        "Category": ["Engineering Labour", "Travel", "Accommodation", "Equipment & Testing", "Subconsultants", "Subtotal", f"Contingency ({contingency_pct:.0f}%)", "TOTAL"],
        "Amount": [labour_total, travel_total, accom_total, equipment, subconsultants, subtotal, contingency, grand_total],
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df["Amount"] = summary_df["Amount"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # Save & export
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Save Estimate", type="primary", key="budget_save_tender"):
            store.update_discipline(pid, "budget",
                inputs={"tender_total": f"${grand_total:,.2f}", "labour_hours": str(total_hours),
                        "travel_trips": str(travel_trips), "accom_nights": str(accom_nights)},
                status="Estimate Ready")
            st.success("Tender estimate saved.")
            st.rerun()
    with c2:
        export_df = edited_hours.copy() if not edited_hours.empty else pd.DataFrame()
        sheets = {"Hours": export_df, "Summary": pd.DataFrame(summary_data)}
        excel_buf = export_excel(f"{project['name']} Tender Estimate", sheets)
        st.download_button("Export (Excel)", excel_buf,
            file_name=f"{project['name']}_Tender_Estimate.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with c3:
        if st.button("Send to Coordinator", key="budget_coord_tender"):
            st.info("Coordinator will validate tender estimate against project scope and historical data. Available in Phase 2.")


def _project_budget_tab(store: ProjectStore, project: dict):
    section_header("Project Budget Tracking")

    pid = st.session_state.current_project
    budget_key = f"project_budget_{pid}"
    if budget_key not in st.session_state:
        st.session_state[budget_key] = {
            "total_budget": 250000.0,
            "categories": [
                {"Category": "Engineering Labour", "Budget": 120000, "Actual": 52000, "Committed": 18000},
                {"Category": "Travel & Accommodation", "Budget": 15000, "Actual": 6200, "Committed": 2400},
                {"Category": "Equipment & Testing", "Budget": 25000, "Actual": 8500, "Committed": 5000},
                {"Category": "Subconsultants", "Budget": 60000, "Actual": 22000, "Committed": 15000},
                {"Category": "Contingency", "Budget": 30000, "Actual": 0, "Committed": 0},
            ],
        }

    budget_data = st.session_state[budget_key]

    # Metrics row
    cat_df = pd.DataFrame(budget_data["categories"])
    total_budget = cat_df["Budget"].sum()
    total_actual = cat_df["Actual"].sum()
    total_committed = cat_df["Committed"].sum()
    total_remaining = total_budget - total_actual - total_committed
    burn_pct = (total_actual / total_budget * 100) if total_budget > 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Budget", f"${total_budget:,.0f}")
    with m2:
        st.metric("Spent to Date", f"${total_actual:,.0f}", delta=f"{burn_pct:.0f}% burned")
    with m3:
        st.metric("Committed", f"${total_committed:,.0f}")
    with m4:
        color = "normal" if total_remaining > 0 else "inverse"
        st.metric("Remaining", f"${total_remaining:,.0f}", delta_color=color)

    st.divider()

    # Budget vs Actual chart
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Budget", x=cat_df["Category"], y=cat_df["Budget"], marker_color="#1B3A5C"))
    fig.add_trace(go.Bar(name="Actual", x=cat_df["Category"], y=cat_df["Actual"], marker_color="#16A34A"))
    fig.add_trace(go.Bar(name="Committed", x=cat_df["Category"], y=cat_df["Committed"], marker_color="#D97706"))
    fig.update_layout(
        barmode="group",
        height=350,
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        font=dict(family="Calibri, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Editable budget table
    section_header("Budget Detail")
    edited_budget = st.data_editor(
        cat_df,
        use_container_width=True,
        column_config={
            "Category": st.column_config.TextColumn("Category"),
            "Budget": st.column_config.NumberColumn("Budget ($)", min_value=0, format="$%d"),
            "Actual": st.column_config.NumberColumn("Actual ($)", min_value=0, format="$%d"),
            "Committed": st.column_config.NumberColumn("Committed ($)", min_value=0, format="$%d"),
        },
        key="budget_detail_editor",
    )
    if not edited_budget.empty:
        edited_budget["Variance"] = edited_budget["Budget"] - edited_budget["Actual"] - edited_budget["Committed"]
        st.session_state[budget_key]["categories"] = edited_budget.drop(columns=["Variance"], errors="ignore").to_dict("records")

        # Variance display
        for _, row in edited_budget.iterrows():
            variance = row["Variance"]
            icon = "+" if variance >= 0 else ""
            color = "green" if variance >= 0 else "red"
            st.markdown(f"**{row['Category']}**: <span style='color:{color}'>{icon}${variance:,.0f}</span>", unsafe_allow_html=True)

    st.divider()

    # Burn rate over time (mock)
    section_header("Budget Burn Rate")
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    planned_burn = [15, 30, 50, 70, 85, 100]
    actual_burn = [12, 28, 48, 65, None, None]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=months, y=planned_burn, name="Planned", line=dict(color="#1B3A5C", dash="dash")))
    fig2.add_trace(go.Scatter(x=months[:4], y=actual_burn[:4], name="Actual", line=dict(color="#16A34A"), mode="lines+markers"))
    fig2.update_layout(
        yaxis_title="% of Budget Spent",
        height=300,
        margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Calibri, sans-serif"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Export
    c1, c2 = st.columns(2)
    with c1:
        if not edited_budget.empty:
            excel_buf = export_excel(f"{project['name']} Budget", {"Budget": edited_budget})
            st.download_button("Export Budget (Excel)", excel_buf,
                file_name=f"{project['name']}_Budget.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="budget_export_excel")
    with c2:
        sections = [
            {"heading": "Budget Summary", "body": f"Total Budget: ${total_budget:,.0f}\nSpent: ${total_actual:,.0f}\nCommitted: ${total_committed:,.0f}\nRemaining: ${total_remaining:,.0f}"},
            {"heading": "Budget Detail", "body": edited_budget.to_string(index=False) if not edited_budget.empty else "No data"},
        ]
        pdf_buf = export_pdf(f"{project['name']} - Budget Report", sections)
        st.download_button("Export Budget (PDF)", pdf_buf,
            file_name=f"{project['name']}_Budget.pdf", mime="application/pdf",
            key="budget_export_pdf")


def _npi_financials_tab(store: ProjectStore, project: dict):
    section_header("NPI Internal Financials")
    st.caption("Track revenue, expenses, and cash flow for NPI as a business — scoped to this project's contribution.")

    pid = st.session_state.current_project
    fin_key = f"npi_financials_{pid}"
    if fin_key not in st.session_state:
        st.session_state[fin_key] = {
            "revenue": [
                {"Month": "January", "Fee Income": 45000, "Milestone Payment": 0, "Other": 0},
                {"Month": "February", "Fee Income": 38000, "Milestone Payment": 25000, "Other": 1200},
                {"Month": "March", "Fee Income": 52000, "Milestone Payment": 0, "Other": 800},
                {"Month": "April", "Fee Income": 41000, "Milestone Payment": 30000, "Other": 500},
            ],
            "expenses": [
                {"Month": "January", "Staff Costs": 32000, "Travel": 3200, "Equipment": 1500, "Overhead": 8000},
                {"Month": "February", "Staff Costs": 35000, "Travel": 4100, "Equipment": 800, "Overhead": 8000},
                {"Month": "March", "Staff Costs": 38000, "Travel": 2800, "Equipment": 2200, "Overhead": 8000},
                {"Month": "April", "Staff Costs": 34000, "Travel": 3500, "Equipment": 1000, "Overhead": 8000},
            ],
        }

    fin_data = st.session_state[fin_key]

    # Revenue table
    st.markdown("**Revenue (this project)**")
    rev_df = pd.DataFrame(fin_data["revenue"])
    edited_rev = st.data_editor(rev_df, use_container_width=True, key="npi_rev_editor",
        column_config={
            "Fee Income": st.column_config.NumberColumn("Fee Income ($)", format="$%d"),
            "Milestone Payment": st.column_config.NumberColumn("Milestone ($)", format="$%d"),
            "Other": st.column_config.NumberColumn("Other ($)", format="$%d"),
        })
    if not edited_rev.empty:
        edited_rev["Total Revenue"] = edited_rev["Fee Income"] + edited_rev["Milestone Payment"] + edited_rev["Other"]
        fin_data["revenue"] = edited_rev.drop(columns=["Total Revenue"], errors="ignore").to_dict("records")

    st.divider()

    # Expenses table
    st.markdown("**Expenses (this project)**")
    exp_df = pd.DataFrame(fin_data["expenses"])
    edited_exp = st.data_editor(exp_df, use_container_width=True, key="npi_exp_editor",
        column_config={
            "Staff Costs": st.column_config.NumberColumn("Staff ($)", format="$%d"),
            "Travel": st.column_config.NumberColumn("Travel ($)", format="$%d"),
            "Equipment": st.column_config.NumberColumn("Equipment ($)", format="$%d"),
            "Overhead": st.column_config.NumberColumn("Overhead ($)", format="$%d"),
        })
    if not edited_exp.empty:
        edited_exp["Total Expenses"] = edited_exp["Staff Costs"] + edited_exp["Travel"] + edited_exp["Equipment"] + edited_exp["Overhead"]
        fin_data["expenses"] = edited_exp.drop(columns=["Total Expenses"], errors="ignore").to_dict("records")

    st.divider()

    # P&L chart
    section_header("Profit & Loss")
    if not edited_rev.empty and not edited_exp.empty:
        months = edited_rev["Month"].tolist()
        revenue_totals = edited_rev["Total Revenue"].tolist()
        expense_totals = edited_exp["Total Expenses"].tolist()
        profit = [r - e for r, e in zip(revenue_totals, expense_totals)]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Revenue", x=months, y=revenue_totals, marker_color="#16A34A"))
        fig.add_trace(go.Bar(name="Expenses", x=months, y=expense_totals, marker_color="#DC2626"))
        fig.add_trace(go.Scatter(name="Profit", x=months, y=profit, line=dict(color="#1B3A5C", width=3), mode="lines+markers"))
        fig.update_layout(
            barmode="group",
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            font=dict(family="Calibri, sans-serif"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary metrics
        total_rev = sum(revenue_totals)
        total_exp = sum(expense_totals)
        total_profit = total_rev - total_exp
        margin = (total_profit / total_rev * 100) if total_rev > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Revenue", f"${total_rev:,.0f}")
        with m2:
            st.metric("Total Expenses", f"${total_exp:,.0f}")
        with m3:
            st.metric("Net Profit", f"${total_profit:,.0f}")
        with m4:
            st.metric("Margin", f"{margin:.1f}%")

    st.divider()

    # Coordinator
    section_header("AI Processing")
    if st.button("Send to Coordinator", use_container_width=True, type="primary", key="budget_coord_npi"):
        st.info("Coordinator will analyse financial trends, forecast cash flow, and flag budget risks. Available in Phase 2.")

    # Export
    st.divider()
    section_header("Export Financials")
    c1, c2 = st.columns(2)
    with c1:
        sheets = {}
        if not edited_rev.empty:
            sheets["Revenue"] = edited_rev
        if not edited_exp.empty:
            sheets["Expenses"] = edited_exp
        if sheets:
            excel_buf = export_excel(f"{project['name']} Financials", sheets)
            st.download_button("Export Financials (Excel)", excel_buf,
                file_name=f"{project['name']}_Financials.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="npi_export_excel")
    with c2:
        sections = [
            {"heading": "Revenue Summary", "body": edited_rev.to_string(index=False) if not edited_rev.empty else "No data"},
            {"heading": "Expenses Summary", "body": edited_exp.to_string(index=False) if not edited_exp.empty else "No data"},
        ]
        pdf_buf = export_pdf(f"{project['name']} - Financial Report", sections)
        st.download_button("Export Financials (PDF)", pdf_buf,
            file_name=f"{project['name']}_Financials.pdf", mime="application/pdf",
            key="npi_export_pdf")
