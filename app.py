# =========================================
# file: app.py
# =========================================
from __future__ import annotations

import streamlit as st

from tools.finance_dashboard import render_personal_finance_dashboard
from tools.mortgage_payoff import render_mortgage_payoff_calculator


def main():
    st.set_page_config(page_title="Personal Finance Dashboard", layout="wide")

    # Sidebar navigation (new)
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Go to",
        ["💸 Dashboard", "🏡 Mortgage Payoff"],
        index=0,
    )

    if page == "💸 Dashboard":
        render_personal_finance_dashboard()
    else:
        render_mortgage_payoff_calculator()


if __name__ == "__main__":
    main()