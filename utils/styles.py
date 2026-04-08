import streamlit as st

NPI_BLUE = "#1B3A5C"
NPI_BLUE_LIGHT = "#2C5F8A"
NPI_GREY = "#F0F2F6"
NPI_GREY_DARK = "#6B7280"
NPI_GREEN = "#16A34A"
NPI_AMBER = "#D97706"
NPI_RED = "#DC2626"


def inject_custom_css():
    st.markdown(
        f"""
        <style>
        /* Top bar */
        header[data-testid="stHeader"] {{
            background-color: {NPI_BLUE};
        }}
        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background-color: #F8F9FB;
            border-right: 1px solid #E5E7EB;
        }}
        section[data-testid="stSidebar"] .stRadio label {{
            font-size: 0.95rem;
        }}
        /* Card-like containers */
        .project-card {{
            background: white;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 1.2rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            transition: box-shadow 0.2s;
        }}
        .project-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.10);
        }}
        .project-card h4 {{
            color: {NPI_BLUE};
            margin: 0 0 0.3rem 0;
        }}
        .project-card .meta {{
            color: {NPI_GREY_DARK};
            font-size: 0.85rem;
        }}
        .project-card .updates {{
            background: {NPI_GREY};
            border-radius: 6px;
            padding: 0.5rem 0.8rem;
            margin-top: 0.5rem;
            font-size: 0.82rem;
        }}
        /* Status badges */
        .badge {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-active {{ background: #DCFCE7; color: #166534; }}
        .badge-planning {{ background: #FEF3C7; color: #92400E; }}
        .badge-complete {{ background: #DBEAFE; color: #1E40AF; }}
        /* Section headers */
        .section-header {{
            color: {NPI_BLUE};
            font-size: 1.1rem;
            font-weight: 600;
            border-bottom: 2px solid {NPI_BLUE};
            padding-bottom: 0.3rem;
            margin: 1.2rem 0 0.8rem 0;
        }}
        /* Page title bar */
        .page-title {{
            background: linear-gradient(135deg, {NPI_BLUE}, {NPI_BLUE_LIGHT});
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }}
        .page-title h2 {{
            margin: 0;
            color: white;
        }}
        .page-title p {{
            margin: 0.2rem 0 0 0;
            opacity: 0.85;
            font-size: 0.9rem;
        }}
        /* Upload zone */
        .upload-zone {{
            border: 2px dashed #CBD5E1;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background: #FAFBFC;
            margin: 1rem 0;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_title(title: str, subtitle: str = ""):
    html = f'<div class="page-title"><h2>{title}</h2>'
    if subtitle:
        html += f"<p>{subtitle}</p>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)
