# =========================================
# file: tools/finance_dashboard.py
# =========================================
from __future__ import annotations

from datetime import datetime
import pandas as pd
import streamlit as st

from tools.pf_state import (
    money,
    ensure_df,
    sanitize_editor_df,
    apply_payload_to_state,
    build_payload_from_state,
)
from tools.pf_persistence import load_pf_state, upsert_pf_state
from tools.pf_calcs import compute_metrics
from tools.pf_ui_income import render_income_tab
from tools.pf_ui_expenses import render_expenses_tab
from tools.pf_ui_saveinvest import render_saveinvest_tab
from tools.pf_ui_summary import render_summary_panel

from tools.pf_visuals import (
    render_visual_overview,
    debt_burden_indicator,
    debt_payoff_order_chart,
)

# -------------------------
# Defaults
# -------------------------
DEFAULT_INCOME = [
    {"Source": "Paycheck 1", "Monthly Amount": 0.0, "Notes": ""},
    {"Source": "Paycheck 2", "Monthly Amount": 0.0, "Notes": ""},
]

DEFAULT_FIXED = [
    {"Expense": "Mortgage/Rent", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Car payment", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Car insurance", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Phone", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Internet", "Monthly Amount": 0.0, "Notes": ""},
]

DEFAULT_ESSENTIAL = [
    {"Expense": "Utilities", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Groceries", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Gas/Transit", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Healthcare/Prescriptions", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Childcare", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Car maintenance", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Home maintenance", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Pet Expenses", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Other essential", "Monthly Amount": 0.0, "Notes": ""},
]

DEFAULT_NON_ESSENTIAL = [
    {"Expense": "Dining out", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Subscriptions", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Gym/Fitness", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Entertainment", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Shopping", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Makeup/Skincare", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Travel", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Gifts", "Monthly Amount": 0.0, "Notes": ""},
    {"Expense": "Other non-essential", "Monthly Amount": 0.0, "Notes": ""},
]

DEFAULT_SAVING = [
    {"Bucket": "Emergency fund", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Big goal", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Down payment fund", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Annual/Irregular bills", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Travel", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Gifts", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Cash savings", "Monthly Amount": 0.0, "Notes": ""},
]

DEFAULT_INVESTING = [
    {"Bucket": "Brokerage", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "401k", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "403b", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Traditional/Rollover IRA", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Roth IRA", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "529/College Fund", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "HSA (Invested)", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Employer stock / ESPP", "Monthly Amount": 0.0, "Notes": ""},
    {"Bucket": "Other long-term investing", "Monthly Amount": 0.0, "Notes": ""},
]

DEFAULT_DEBT = [
    {"Debt": "Car loan", "Balance": 0.0, "APR %": 0.0, "Monthly Payment": 0.0, "Notes": ""},
    {"Debt": "Credit card", "Balance": 0.0, "APR %": 0.0, "Monthly Payment": 0.0, "Notes": ""},
    {"Debt": "Student loan", "Balance": 0.0, "APR %": 0.0, "Monthly Payment": 0.0, "Notes": ""},
    {"Debt": "Personal loan", "Balance": 0.0, "APR %": 0.0, "Monthly Payment": 0.0, "Notes": ""},
    {"Debt": "Medical debt", "Balance": 0.0, "APR %": 0.0, "Monthly Payment": 0.0, "Notes": ""},
]

DEFAULT_ASSETS = [
    {"Asset": "Checking", "Value": 0.0, "Notes": ""},
    {"Asset": "Savings", "Value": 0.0, "Notes": ""},
    {"Asset": "HYSA", "Value": 0.0, "Notes": ""},
    {"Asset": "Brokerage", "Value": 0.0, "Notes": ""},
    {"Asset": "Retirement", "Value": 0.0, "Notes": ""},
    {"Asset": "Value of Home (minus debt)", "Value": 0.0, "Notes": ""},
    {"Asset": "Value of Vehicle (minus debt)", "Value": 0.0, "Notes": ""},
]

DEFAULT_LIABILITIES = [
    {"Liability": "Mortgage", "Value": 0.0, "Notes": ""},
    {"Liability": "Home Equity Loan/HELOC", "Value": 0.0, "Notes": ""},
    {"Liability": "Car loan", "Value": 0.0, "Notes": ""},
    {"Liability": "Tax Liability", "Value": 0.0, "Notes": ""},
]


# -------------------------
# UI helpers
# -------------------------
def _dashboard_header(net_income, total_outflow, remaining, emergency_minimum_monthly, net_worth, debt_payments):
    with st.container(border=True):
        st.markdown("**Monthly Outlook**")
        a, b, c, d, e, f = st.columns(6, gap="medium")
        a.metric("Net Income", money(net_income))
        b.metric("Expenses", money(total_outflow))
        c.metric("Leftover", money(remaining))
        d.metric("Emergency Min", money(emergency_minimum_monthly))
        e.metric("Net Worth", money(net_worth))
        f.metric("Debt Min", money(debt_payments))


# -------------------------
# Main UI
# -------------------------
def render_personal_finance_dashboard(user):
    # user may be None (guest mode)
    user_id = getattr(user, "id", None)

    # -------------------------
    # LOAD FROM DATABASE (only if logged in)
    # -------------------------
    if user_id and st.session_state.get("pf_loaded_from_db") is not True:
        saved = load_pf_state(user_id)
        if isinstance(saved, dict):
            apply_payload_to_state(saved)
        st.session_state["pf_loaded_from_db"] = True
        st.rerun()
    elif st.session_state.get("pf_loaded_from_db") is not True:
        # First load for guest mode—no DB to pull from
        st.session_state["pf_loaded_from_db"] = True

    st.title("💸 Financial Breakdown")

    # ---- Widget defaults ----
    st.session_state.setdefault("pf_month_label", datetime.now().strftime("%B %Y"))
    st.session_state.setdefault("pf_tax_rate", 0.0)
    st.session_state.setdefault("pf_income_is", "Net (after tax)")

    # Paycheck breakdown toggle
    st.session_state.setdefault("pf_use_paycheck_breakdown", False)

    # Optional gross-income breakdown defaults
    st.session_state.setdefault("pf_gross_mode", "Estimate (tax rate)")
    st.session_state.setdefault("pf_manual_taxes", 0.0)
    st.session_state.setdefault("pf_manual_retirement", 0.0)
    st.session_state.setdefault("pf_manual_match", 0.0)
    st.session_state.setdefault("pf_manual_benefits", 0.0)
    st.session_state.setdefault("pf_manual_other_ssi", 0.0)

    # ---- Persisted tables ----
    ensure_df("pf_income_df", DEFAULT_INCOME)
    ensure_df("pf_fixed_df", DEFAULT_FIXED)
    ensure_df("pf_essential_df", DEFAULT_ESSENTIAL)
    ensure_df("pf_nonessential_df", DEFAULT_NON_ESSENTIAL)
    ensure_df("pf_saving_df", DEFAULT_SAVING)
    ensure_df("pf_investing_df", DEFAULT_INVESTING)
    ensure_df("pf_debt_df", DEFAULT_DEBT)
    ensure_df("pf_assets_df", DEFAULT_ASSETS)
    ensure_df("pf_liabilities_df", DEFAULT_LIABILITIES)

    # -------------------------
    # CALCULATIONS
    # -------------------------
    metrics = compute_metrics()

    # -------------------------
    # HEADER
    # -------------------------
    _dashboard_header(
        net_income=metrics["net_income"],
        total_outflow=metrics["total_outflow"],
        remaining=metrics["remaining"],
        emergency_minimum_monthly=metrics["emergency_minimum_monthly"],
        net_worth=metrics["net_worth"],
        debt_payments=metrics["total_monthly_debt_payments"],
    )

    # -------------------------
    # EDITORS
    # -------------------------
    left, right = st.columns([1.1, 0.9], gap="large")

    with left:
        st.subheader("Your Monthly Cash Flow")
        tab_income, tab_exp, tab_save = st.tabs(["Income", "Expenses", "Saving/Investing"])

        with tab_income:
            render_income_tab()

        with tab_exp:
            render_expenses_tab()

        with tab_save:
            render_saveinvest_tab()

    # -------------------------
    # EMERGENCY MINIMUM
    # -------------------------
    st.divider()
    st.subheader("🆘 Emergency Minimum")

    e1, e2, e3, e4 = st.columns(4, gap="large")
    e1.metric("Monthly", money(metrics["emergency_minimum_monthly"]))
    e2.metric("3 mo", money(metrics["emergency_minimum_monthly"] * 3))
    e3.metric("6 mo", money(metrics["emergency_minimum_monthly"] * 6))
    e4.metric("12 mo", money(metrics["emergency_minimum_monthly"] * 12))

    with st.expander("What this includes", expanded=False):
        fixed_df = st.session_state.get("pf_fixed_df", pd.DataFrame())
        ess_df = st.session_state.get("pf_essential_df", pd.DataFrame())
        debt_df = st.session_state.get("pf_debt_df", pd.DataFrame())

        col1, col2, col3 = st.columns(3)

        # ---------- helper to render a category column ----------
        def render_list_column(title, df, name_col, amount_col):
            st.markdown(f"### {title}")

            if df is None or df.empty:
                st.caption("No items entered")
                return

            # --- strip out zero values ---
            df = df.copy()
            df[amount_col] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0)
            df = df[df[amount_col] > 0]

            if df.empty:
                st.caption("No expenses added for this category yet")
                return

            # Sort largest > smallest
            df = df.sort_values(by=amount_col, ascending=False)

            # List each item
            for _, row in df.iterrows():
                name = str(row.get(name_col, ""))
                amount = float(row.get(amount_col, 0.0))
                st.markdown(f"- **{name}**: {money(amount)}")

            # Total
            total = df[amount_col].sum()
            st.markdown(f"**Total:** {money(total)}")


        # ---------- Fixed Bills ----------
        with col1:
            render_list_column(
                "Fixed Bills",
                fixed_df,
                name_col="Expense",
                amount_col="Monthly Amount"
            )

        # ---------- Essentials ----------
        with col2:
            render_list_column(
                "Essential Expenses",
                ess_df,
                name_col="Expense",
                amount_col="Monthly Amount"
            )

        # ---------- Minimum Debt ----------
        with col3:
            render_list_column(
                "Minimum Debt Payments",
                debt_df,
                name_col="Debt",
                amount_col="Monthly Payment"
            )

    st.divider()

    # -------------------------
    # VISUAL OVERVIEW
    # -------------------------
    render_visual_overview(
        expenses_total=metrics["expenses_total"],
        total_monthly_debt_payments=metrics["total_monthly_debt_payments"],
        saving_total=metrics["saving_total"],
        investing_cashflow=metrics["investing_cashflow"],
        remaining=metrics["remaining"],
        fixed_df=metrics["fixed_df"],
        variable_df=metrics["variable_for_visuals"],
        debt_df=metrics["debt_df"],
    )

    # -------------------------
    # RIGHT PANEL SUMMARY
    # -------------------------
    with right:
        showed_empty = render_summary_panel(metrics)
        if showed_empty:
            return

    st.divider()

    # -------------------------
    # NET WORTH
    # -------------------------
    st.subheader("Your Net Worth")
    a_col, l_col = st.columns([1, 1], gap="large")

    with a_col:
        st.markdown("**Assets**")
        with st.form("pf_assets_form", border=False):
            assets_edit = st.data_editor(
                st.session_state["pf_assets_df"],
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                key="pf_assets_editor",
                column_config={"Value": st.column_config.NumberColumn(min_value=0.0, step=100.0, format="%.2f")},
            )
            assets_submitted = st.form_submit_button("Save assets", type="primary", width="stretch")

        if assets_submitted:
            st.session_state["pf_assets_df"] = sanitize_editor_df(
                assets_edit,
                expected_cols=["Asset", "Value", "Notes"],
                numeric_cols=["Value"],
            )
            st.rerun()

    with l_col:
        st.markdown("**Liabilities**")
        with st.form("pf_liabilities_form", border=False):
            liabilities_edit = st.data_editor(
                st.session_state["pf_liabilities_df"],
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                key="pf_liabilities_editor",
                column_config={"Value": st.column_config.NumberColumn(min_value=0.0, step=100.0, format="%.2f")},
            )
            liabilities_submitted = st.form_submit_button("Save liabilities", type="primary", width="stretch")

        if liabilities_submitted:
            st.session_state["pf_liabilities_df"] = sanitize_editor_df(
                liabilities_edit,
                expected_cols=["Liability", "Value", "Notes"],
                numeric_cols=["Value"],
            )
            st.rerun()

    with st.container(border=True):
        n1, n2, n3 = st.columns(3, gap="large")
        n1.metric("Total Assets", money(metrics["total_assets"]))
        n2.metric("Total Liabilities", money(metrics["total_liabilities"]))
        n3.metric("Net Worth", money(metrics["net_worth"]))

    st.divider()

    # -------------------------
    # DEBT DETAILS
    # -------------------------
    st.subheader("Consumer Debt Details")
    st.caption("This doesn't affect net worth beyond the liability values, it's here for clarity and payoff planning.")

    debt_df = st.session_state["pf_debt_df"]

    total_monthly_debt_payments = float(metrics.get("total_monthly_debt_payments", 0.0) or 0.0)
    total_debt_balance = float(metrics.get("total_debt_balance", 0.0) or 0.0)
    net_income = float(metrics.get("net_income", 0.0) or 0.0)

    debt_burden_pct = metrics.get("debt_burden_pct")
    payoff_rows = metrics.get("debt_payoff_rows") or []
    overall_months = metrics.get("debt_overall_months")
    overall_interest = metrics.get("debt_overall_interest")
    overall_payoff_date = metrics.get("debt_overall_payoff_date")
    has_non_amortizing = bool(metrics.get("debt_has_non_amortizing", False))

    # ---- Debt Details ---- #
    c1, c2, c3 = st.columns([1.2, 0.75, 0.75], gap="medium")

    with c1:
        with st.form("pf_debt_form", border=False):
            debt_edit = st.data_editor(
                debt_df,
                num_rows="dynamic",
                hide_index=True,
                width="stretch",
                key="pf_debt_editor",
                column_config={
                    "Balance": st.column_config.NumberColumn(min_value=0.0, step=100.0, format="%.2f"),
                    "APR %": st.column_config.NumberColumn(min_value=0.0, max_value=60.0, step=0.01, format="%.2f"),
                    "Monthly Payment": st.column_config.NumberColumn(min_value=0.0, step=10.0, format="%.2f"),
                },
            )
            debt_submitted = st.form_submit_button("Save debt details", type="primary", width="stretch")

        if debt_submitted:
            st.session_state["pf_debt_df"] = sanitize_editor_df(
                debt_edit,
                expected_cols=["Debt", "Balance", "APR %", "Monthly Payment", "Notes"],
                numeric_cols=["Balance", "APR %", "Monthly Payment"],
            )
            st.rerun()

    with c2:
        # 1) Payoff Timeline
        with st.container(border=True):
            st.markdown("#### Payoff Timeline")

            if total_debt_balance <= 0 or total_monthly_debt_payments <= 0:
                st.caption("Add balances and monthly payments on the left to see estimated payoff dates.")
            else:
                if has_non_amortizing:
                    st.warning(
                        "**⚠️ At your current payment level, at least one debt will never be paid off.** "
                        "That happens when your payment is less than the interest charged each month."
                    )
                elif overall_months is not None and overall_payoff_date is not None:
                    years = overall_months / 12.0
                    st.markdown(
                        f"**At your current payment level, you're on track to be debt-free around "
                        f"{overall_payoff_date}** (_≈{years:.1f} years_)."
                    )
                    if overall_interest is not None:
                        st.caption(
                            f"Estimated interest remaining: **{money(overall_interest)}** "
                            "(Assumes payments & APRs stay steady; simple approximation)."
                        )

                if payoff_rows:
                    st.markdown("**Per-debt estimates**")

                    for row in payoff_rows[:6]:
                        status = row.get("status")
                        if status == "paid_off":
                            st.markdown(
                                f"- **{row['Debt']}**: **{row['payoff_date']}** ({row['months']} mo)"
                            )
                        elif status == "non_amortizing":
                            st.markdown(
                                f"- **{row['Debt']}** → **No payoff at current payment** "
                                f"(interest ≈ {money(row['monthly_interest']).replace('$', '\\$')}/mo, "
                                f"payment {money(row['payment']).replace('$', '\\$')}; "
                                f"needs > {money(row['min_payment_to_amortize']).replace('$', '\\$')})"
                            )
                        elif status == "no_payment":
                            st.markdown(
                                f"- **{row['Debt']}** → **No payment entered** "
                                f"(interest ≈ {money(row['monthly_interest'])}/mo)"
                            )
                        else: 
                            st.markdown(
                                f"- **{row['Debt']}** → **Payoff estimate exceeds 600 months** "
                                "(try increasing payment)"
                            )

                    if len(payoff_rows) > 6:
                        st.caption(f"+ {len(payoff_rows) - 6} more…")

    with c3:
        # 2) Debt Check-In 
        with st.container(border=True):
            st.markdown("#### Debt Check-In")

            if total_debt_balance <= 0:
                st.markdown("🎉 **You're free of consumer debt.**")
                st.markdown(
                    "- Build/top off your emergency fund\n"
                    "- Increase retirement contributions\n"
                    "- Invest toward long-term goals\n"
                    "- Create sinking funds for upcoming expenses"
                )
            else:
                if debt_burden_pct is None:
                    st.caption("Add your income to see what % of take-home pay goes to minimum debt payments.")
                else:
                    burden_text = f"**{debt_burden_pct:.1f}%** of your take-home pay is going to minimum debt payments."

                    if debt_burden_pct < 10:
                        st.success(f"Light debt burden. {burden_text}")
                        st.caption("Plenty of flexibility. Extra payments are optional but powerful.")
                    elif debt_burden_pct < 20:
                        st.info(f"Manageable debt burden. {burden_text}")
                        st.caption("Solid, but extra payments toward high-APR debt buy flexibility fast.")
                    elif debt_burden_pct < 30:
                        st.warning(f"Heavy debt burden. {burden_text}")
                        st.caption("Consider prioritizing highest APR & trimming non-essentials temporarily.")
                    else:
                        st.error(f"Very heavy debt burden. {burden_text}")
                        st.caption("Focus on stabilizing cash flow & exploring payoff/consolidation options carefully.")

        # ---- Debt charts ---- #
    has_any_debt = (total_debt_balance > 0) or (total_monthly_debt_payments > 0)

    with st.expander("Debt Summary", expanded=has_any_debt):
        c1, c2, c3 = st.columns([0.55, 0.85, 1.2], gap="large")

        with c1:
            with st.container(border=True):
                st.metric("Total Monthly Debt Payments", money(total_monthly_debt_payments))

        with c2:
            st.caption(
                "**Debt Burden** shows what % of your take-home pay goes to minimum debt payments each month. "
                "Under ~15% feels light, 15-30% is moderate, 30%+ is heavy."
            )
            fig_burden, _ = debt_burden_indicator(
                net_income=net_income,
                debt_payments=total_monthly_debt_payments,
            )
            st.plotly_chart(fig_burden, width="stretch", key="pf_debt_burden_chart")

        with c3:
            st.caption(
                "**Payoff Order** ranks your debts for where to focus extra payments. "
                "Bars show **balance**, and the label on each bar is the **APR**."
            )
            strategy = st.radio(
                "Payoff strategy",
                ["Avalanche (APR)", "Snowball (Balance)"],
                horizontal=True,
                key="pf_debt_strategy",
            )
            fig_order = debt_payoff_order_chart(
                st.session_state["pf_debt_df"],
                strategy=strategy,
            )
            st.plotly_chart(fig_order, width="stretch", key="pf_debt_order_chart")

    st.divider()

    # -------------------------
    # SAVE, PRIVACY & RESET
    # -------------------------

    p0, p1, p2 = st.columns([1, 1, 1], gap="medium")
    with p0:
        st.subheader("Save")
        with st.expander("Save to your account", expanded=False):
            st.caption(
                "You can use this dashboard without an account. "
                "If you want to come back to these exact numbers later, save them to your login."
            )

            pf_payload = build_payload_from_state(metrics)
            user_id = getattr(user, "id", None)

            save_col = st.columns(1)[0]
            with save_col:
                save_disabled = user_id is None
                btn_label = "Save my data"

                if save_disabled:
                    st.caption(
                        "To enable saving, log in or sign up from the **sidebar** under "
                        "**“Login/Sign Up”**."
                    )

                if st.button(btn_label, type="primary", width="stretch", disabled=save_disabled):
                    try:
                        upsert_pf_state(user_id, pf_payload)
                        st.success("Saved to your account.")
                    except Exception as e:
                        st.error(f"Save failed: {e}")
    with p1:
        st.subheader("Privacy")
        with st.expander("Privacy & data notice", expanded=False):
            st.markdown(
                """
                - Your data is stored in this app's database **only when you click "Save my data."**
                - It's tied to your email login so you can come back to it later.
                - This app is **not** connected to your bank and does not pull transactions automatically.
                - You can clear your inputs anytime using **Reset all data** below (this clears them from this session; database-stored data is separate).
                """
            )

    with p2:
        st.subheader("Reset")
        with st.expander("Reset all data", expanded=False):
            st.warning("This clears the tool's saved tables in this session.")
            if st.button("Reset now", type="primary", key="pf_reset_btn", width="stretch"):
                for k in list(st.session_state.keys()):
                    if k.startswith("pf_"):
                        del st.session_state[k]
                st.rerun()