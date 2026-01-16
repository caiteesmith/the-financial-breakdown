from __future__ import annotations
import streamlit as st
import pandas as pd
from tools.pf_state import sum_df

def compute_metrics() -> dict:
    income_df = st.session_state["pf_income_df"]
    fixed_df = st.session_state["pf_fixed_df"]
    essential_df = st.session_state["pf_essential_df"]
    nonessential_df = st.session_state["pf_nonessential_df"]
    saving_df = st.session_state["pf_saving_df"]
    investing_df = st.session_state["pf_investing_df"]
    debt_df = st.session_state["pf_debt_df"]
    assets_df = st.session_state["pf_assets_df"]
    liabilities_df = st.session_state["pf_liabilities_df"]

    total_income = sum_df(income_df, "Monthly Amount")

    manual_taxes = float(st.session_state.get("pf_manual_taxes", 0.0) or 0.0)
    manual_retirement = float(st.session_state.get("pf_manual_retirement", 0.0) or 0.0)
    manual_benefits = float(st.session_state.get("pf_manual_benefits", 0.0) or 0.0)
    manual_other_ssi = float(st.session_state.get("pf_manual_other_ssi", 0.0) or 0.0)
    employer_match = float(st.session_state.get("pf_manual_match", 0.0) or 0.0)

    manual_deductions_total = manual_taxes + manual_retirement + manual_benefits + manual_other_ssi
    use_breakdown = bool(st.session_state.get("pf_use_paycheck_breakdown", False))
    net_income = total_income - manual_deductions_total if use_breakdown else total_income

    est_tax = 0.0  # placeholder if you add tax-rate mode later

    fixed_total = sum_df(fixed_df, "Monthly Amount")
    essential_total = sum_df(essential_df, "Monthly Amount")
    nonessential_total = sum_df(nonessential_df, "Monthly Amount")
    expenses_total = fixed_total + essential_total + nonessential_total

    saving_total = sum_df(saving_df, "Monthly Amount")
    investing_total = sum_df(investing_df, "Monthly Amount")

    investing_cashflow = investing_total
    investing_display = investing_total + manual_retirement + employer_match

    total_monthly_debt_payments = sum_df(debt_df, "Monthly Payment")
    total_saving_and_investing_cashflow = saving_total + investing_cashflow

    total_outflow = expenses_total + total_saving_and_investing_cashflow + total_monthly_debt_payments
    remaining = net_income - total_outflow
    has_debt = total_monthly_debt_payments > 0

    total_assets = sum_df(assets_df, "Value")
    total_liabilities = sum_df(liabilities_df, "Value")
    net_worth = total_assets - total_liabilities

    employee_retirement = float(st.session_state.get("pf_manual_retirement", 0.0) or 0.0)
    company_match = float(st.session_state.get("pf_manual_match", 0.0) or 0.0)
    total_retirement_contrib = employee_retirement + company_match

    investing_rate_of_gross = (investing_display / total_income) * 100 if total_income > 0 else None
    investing_rate_of_net = (investing_display / net_income) * 100 if net_income > 0 else None

    debt_minimums = total_monthly_debt_payments
    emergency_minimum_monthly = fixed_total + essential_total + debt_minimums

    needs_total = emergency_minimum_monthly
    wants_total = nonessential_total
    save_invest_total = saving_total + investing_cashflow

    needs_pct = wants_pct = save_invest_pct = unallocated_pct = None
    if net_income > 0:
        needs_pct = (needs_total / net_income) * 100
        wants_pct = (wants_total / net_income) * 100
        save_invest_pct = (save_invest_total / net_income) * 100
        unallocated_pct = max(0.0, 100 - (needs_pct + wants_pct + save_invest_pct))

    variable_for_visuals = pd.concat(
        [essential_df.assign(Category="Essential"), nonessential_df.assign(Category="Non-Essential")],
        ignore_index=True,
        sort=False,
    )

    return {
        "income_df": income_df,
        "fixed_df": fixed_df,
        "essential_df": essential_df,
        "nonessential_df": nonessential_df,
        "saving_df": saving_df,
        "investing_df": investing_df,
        "debt_df": debt_df,
        "assets_df": assets_df,
        "liabilities_df": liabilities_df,

        "total_income": total_income,
        "net_income": net_income,
        "manual_deductions_total": manual_deductions_total,
        "est_tax": est_tax,

        "fixed_total": fixed_total,
        "essential_total": essential_total,
        "nonessential_total": nonessential_total,
        "expenses_total": expenses_total,

        "saving_total": saving_total,
        "investing_total": investing_total,
        "investing_cashflow": investing_cashflow,
        "investing_display": investing_display,

        "total_monthly_debt_payments": total_monthly_debt_payments,
        "total_outflow": total_outflow,
        "remaining": remaining,
        "has_debt": has_debt,

        "total_assets": total_assets,
        "total_liabilities": total_liabilities,
        "net_worth": net_worth,

        "employee_retirement": employee_retirement,
        "company_match": company_match,
        "total_retirement_contrib": total_retirement_contrib,
        "investing_rate_of_gross": investing_rate_of_gross,
        "investing_rate_of_net": investing_rate_of_net,

        "debt_minimums": debt_minimums,
        "emergency_minimum_monthly": emergency_minimum_monthly,

        "needs_pct": needs_pct,
        "wants_pct": wants_pct,
        "save_invest_pct": save_invest_pct,
        "unallocated_pct": unallocated_pct,

        "variable_for_visuals": variable_for_visuals,
    }