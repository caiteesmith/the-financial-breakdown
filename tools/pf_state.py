# =========================================
# file: tools/pf_state.py
# =========================================
from __future__ import annotations

from datetime import datetime
from typing import Dict, List
import pandas as pd
import streamlit as st


# -------------------------
# Helpers
# -------------------------
def money(x: float) -> str:
    return f"${float(x or 0.0):,.2f}"


def pct(x: float | None) -> str:
    return "—" if x is None else f"{x:.1f}%"


def safe_float(x, default=0.0) -> float:
    try:
        return float(x)
    except Exception:
        return float(default)


def sum_df(df: pd.DataFrame, col: str) -> float:
    if df is None or df.empty or col not in df.columns:
        return 0.0
    return float(pd.to_numeric(df[col], errors="coerce").fillna(0).sum())


def ensure_df(key: str, default_rows: List[Dict]) -> pd.DataFrame:
    """
    Ensure st.session_state[key] is a DataFrame.
    If missing, seed it with default_rows.
    """
    if key not in st.session_state or not isinstance(st.session_state[key], pd.DataFrame):
        st.session_state[key] = pd.DataFrame(default_rows)
    return st.session_state[key]


def sanitize_editor_df(df: pd.DataFrame, expected_cols: List[str], numeric_cols: List[str]) -> pd.DataFrame:
    """
    Clean up a DataFrame coming from st.data_editor:
    - Drop auto-added index / id-ish columns
    - Ensure expected columns exist in the right order
    - Coerce numeric columns
    """
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(columns=expected_cols)

    drop_candidates = {"id", "_id", "__id", "row_id", "_row_id", "index", "__index__"}
    extra = [c for c in df.columns if str(c).strip().lower() in drop_candidates]
    if extra:
        df = df.drop(columns=extra, errors="ignore")

    for c in expected_cols:
        if c not in df.columns:
            df[c] = "" if c not in numeric_cols else 0.0

    df = df[expected_cols].copy()

    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    df = df.reset_index(drop=True)
    return df


# -------------------------
# Payload load/apply
# -------------------------
def apply_payload_to_state(payload: dict) -> None:
    """
    Apply a saved payload (from DB) into st.session_state.
    Payload structure matches what you store in Supabase (tables + settings).
    """
    if not isinstance(payload, dict):
        return

    # ---- Top-level ----
    st.session_state["pf_month_label"] = payload.get(
        "month_label",
        st.session_state.get("pf_month_label", datetime.now().strftime("%B %Y")),
    )

    # ---- Settings ----
    settings = payload.get("settings", {}) or {}

    st.session_state["pf_income_is"] = settings.get(
        "income_is",
        st.session_state.get("pf_income_is", "Net (after tax)"),
    )
    st.session_state["pf_gross_mode"] = settings.get(
        "gross_mode",
        st.session_state.get("pf_gross_mode", "Estimate (tax rate)"),
    )
    st.session_state["pf_tax_rate"] = safe_float(
        settings.get("tax_rate_pct", st.session_state.get("pf_tax_rate", 0.0))
    )

    # ---- Optional gross breakdown ----
    gb = payload.get("gross_breakdown_optional", {}) or {}
    st.session_state["pf_manual_taxes"] = safe_float(
        gb.get("taxes", st.session_state.get("pf_manual_taxes", 0.0))
    )
    st.session_state["pf_manual_retirement"] = safe_float(
        gb.get("retirement_employee", st.session_state.get("pf_manual_retirement", 0.0))
    )
    st.session_state["pf_manual_match"] = safe_float(
        gb.get("company_match", st.session_state.get("pf_manual_match", 0.0))
    )
    st.session_state["pf_manual_benefits"] = safe_float(
        gb.get("benefits", st.session_state.get("pf_manual_benefits", 0.0))
    )
    st.session_state["pf_manual_other_ssi"] = safe_float(
        gb.get("other_ssi", st.session_state.get("pf_manual_other_ssi", 0.0))
    )

    # (Optional) keep paycheck breakdown drafts in sync
    st.session_state["pf_use_paycheck_breakdown"] = bool(
        payload.get("monthly_cash_flow", {}).get(
            "paycheck_breakdown_enabled",
            st.session_state.get("pf_use_paycheck_breakdown", False),
        )
    )
    st.session_state["pf_draft_taxes"] = st.session_state["pf_manual_taxes"]
    st.session_state["pf_draft_retirement"] = st.session_state["pf_manual_retirement"]
    st.session_state["pf_draft_match"] = st.session_state["pf_manual_match"]
    st.session_state["pf_draft_benefits"] = st.session_state["pf_manual_benefits"]
    st.session_state["pf_draft_other_ssi"] = st.session_state["pf_manual_other_ssi"]

    # ---- Tables ----
    tables = payload.get("tables", {}) or {}

    def _set_table(key: str, records_key: str, expected_cols: list[str], numeric_cols: list[str]):
        records = tables.get(records_key) or []
        df = pd.DataFrame(records)
        st.session_state[key] = sanitize_editor_df(df, expected_cols, numeric_cols)

    _set_table("pf_income_df", "income", ["Source", "Monthly Amount", "Notes"], ["Monthly Amount"])
    _set_table("pf_fixed_df", "fixed_expenses", ["Expense", "Monthly Amount", "Notes"], ["Monthly Amount"])
    _set_table("pf_essential_df", "essential_expenses", ["Expense", "Monthly Amount", "Notes"], ["Monthly Amount"])
    _set_table("pf_nonessential_df", "nonessential_expenses", ["Expense", "Monthly Amount", "Notes"], ["Monthly Amount"])
    _set_table("pf_saving_df", "saving", ["Bucket", "Monthly Amount", "Notes"], ["Monthly Amount"])
    _set_table("pf_investing_df", "investing", ["Bucket", "Monthly Amount", "Notes"], ["Monthly Amount"])
    _set_table("pf_assets_df", "assets", ["Asset", "Value", "Notes"], ["Value"])
    _set_table("pf_liabilities_df", "liabilities", ["Liability", "Value", "Notes"], ["Value"])
    _set_table(
        "pf_debt_df",
        "debt_details",
        ["Debt", "Balance", "APR %", "Monthly Payment", "Notes"],
        ["Balance", "APR %", "Monthly Payment"],
    )


def build_payload_from_state(metrics: dict) -> dict:
    """
    Build a payload suitable for saving to Supabase from the current session_state + metrics.
    """
    month_label = st.session_state.get("pf_month_label", datetime.now().strftime("%B %Y"))
    tax_rate = float(st.session_state.get("pf_tax_rate", 0.0) or 0.0)
    income_is = st.session_state.get("pf_income_is", "Net (after tax)")

    return {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "month_label": month_label,
        "settings": {
            "income_is": income_is,
            "tax_rate_pct": float(tax_rate),
            "gross_mode": st.session_state.get("pf_gross_mode"),
        },
        "gross_breakdown_optional": {
            "taxes": float(st.session_state.get("pf_manual_taxes", 0.0) or 0.0),
            "retirement_employee": float(st.session_state.get("pf_manual_retirement", 0.0) or 0.0),
            "company_match": float(st.session_state.get("pf_manual_match", 0.0) or 0.0),
            "benefits": float(st.session_state.get("pf_manual_benefits", 0.0) or 0.0),
            "other_ssi": float(st.session_state.get("pf_manual_other_ssi", 0.0) or 0.0),
        },
        "monthly_cash_flow": {
            "total_income_entered": float(metrics.get("total_income", 0.0) or 0.0),
            "net_income": float(metrics.get("net_income", 0.0) or 0.0),
            "total_expenses": float(metrics.get("expenses_total", 0.0) or 0.0),
            "left_over": float(metrics.get("remaining", 0.0) or 0.0),
            "paycheck_breakdown_enabled": bool(st.session_state.get("pf_use_paycheck_breakdown", False)),
        },
        "tables": {
            "income": st.session_state["pf_income_df"].to_dict(orient="records"),
            "fixed_expenses": st.session_state["pf_fixed_df"].to_dict(orient="records"),
            "essential_expenses": st.session_state["pf_essential_df"].to_dict(orient="records"),
            "nonessential_expenses": st.session_state["pf_nonessential_df"].to_dict(orient="records"),
            "saving": st.session_state["pf_saving_df"].to_dict(orient="records"),
            "investing": st.session_state["pf_investing_df"].to_dict(orient="records"),
            "assets": st.session_state["pf_assets_df"].to_dict(orient="records"),
            "liabilities": st.session_state["pf_liabilities_df"].to_dict(orient="records"),
            "debt_details": st.session_state["pf_debt_df"].to_dict(orient="records"),
        },
    }