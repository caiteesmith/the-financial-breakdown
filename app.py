from __future__ import annotations

import streamlit as st

from tools.finance_dashboard import render_personal_finance_dashboard

st.set_page_config(
    page_title="Personal Finance Dashboard",
    page_icon="assets/favicon.png",
    layout="wide",
)

st.markdown(
    """
    <style>
        div[data-testid="stExpander"] {
            border-radius: 16px;
            border: 1px solid #E6E9ED;
            background-color: #F1F3F5;
        }

        button[kind="primary"] {
            border-radius: 999px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def main():
    render_personal_finance_dashboard()


if __name__ == "__main__":
    main()