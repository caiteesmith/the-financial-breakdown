import streamlit as st
from tools.pf_state import sanitize_editor_df

def render_expenses_tab():
    with st.expander("Quick reality check to help your numbers be accurate", expanded=False):
        st.caption(
            "Before you enter numbers, scan the last 1-2 months of statements so your totals match real life."
        )
        st.markdown(
            """
            **Where to look**
            - **Bank & credit card statements:** Search common merchants & watch for fees/interest
            - **Amazon:** Subscribe & Save, recurring household orders, repeat purchases
            - **Apple/Google:** Storage plans, app subscriptions, in-app purchases
            - **Streaming:** Netflix, Hulu, HBO Max, Disney+, Spotify, YouTube Premium, etc.
            - **Subscriptions & memberships:** Amazon Prime, gym, apps, clubs, Patreon, etc.
            - **Gaming:** Xbox/PlayStation/Nintendo Online, game passes, in-game purchases
            """
        )

    with st.form("pf_expenses_form", border=False):
        st.markdown("**Fixed Expenses**")
        fixed_edit = st.data_editor(
            st.session_state["pf_fixed_df"],
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            key="pf_fixed_editor",
            column_config={"Monthly Amount": st.column_config.NumberColumn(min_value=0.0, step=25.0, format="%.2f")},
        )

        st.markdown("**Essential Expenses**")
        essential_edit = st.data_editor(
            st.session_state["pf_essential_df"],
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            key="pf_essential_editor",
            column_config={"Monthly Amount": st.column_config.NumberColumn(min_value=0.0, step=25.0, format="%.2f")},
        )

        st.markdown("**Non-Essential Expenses**")
        nonessential_edit = st.data_editor(
            st.session_state["pf_nonessential_df"],
            num_rows="dynamic",
            hide_index=True,
            width="stretch",
            key="pf_nonessential_editor",
            column_config={"Monthly Amount": st.column_config.NumberColumn(min_value=0.0, step=25.0, format="%.2f")},
        )

        submitted = st.form_submit_button("Save expenses", type="primary", width="stretch")

    if submitted:
        st.session_state["pf_fixed_df"] = sanitize_editor_df(
            fixed_edit, expected_cols=["Expense", "Monthly Amount", "Notes"], numeric_cols=["Monthly Amount"]
        )
        st.session_state["pf_essential_df"] = sanitize_editor_df(
            essential_edit, expected_cols=["Expense", "Monthly Amount", "Notes"], numeric_cols=["Monthly Amount"]
        )
        st.session_state["pf_nonessential_df"] = sanitize_editor_df(
            nonessential_edit, expected_cols=["Expense", "Monthly Amount", "Notes"], numeric_cols=["Monthly Amount"]
        )
        st.rerun()