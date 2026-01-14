# tools/pf_visuals.py
from __future__ import annotations

import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def spending_mix_donut(expenses: float, debt: float, saving: float, investing: float, remaining: float):
    labels, values = [], []

    for label, val in [
        ("Living expenses", expenses),
        ("Debt payments", debt),
        ("Saving", saving),
        ("Investing", investing),
    ]:
        if val > 0:
            labels.append(label)
            values.append(val)

    if remaining > 0:
        labels.append("Remaining")
        values.append(remaining)

    fig = go.Figure(
        data=[go.Pie(labels=labels, values=values, hole=0.55,
                     hovertemplate="%{label}: $%{value:,.0f}<extra></extra>")]
    )

    fig.update_layout(
        title=dict(text="Monthly Cash Flow Breakdown", x=0, xanchor="left", font=dict(size=16)),
        height=280,
        margin=dict(t=50, b=20, l=20, r=20),
        showlegend=True,
    )
    return fig


def top_expenses_bar(fixed_df: pd.DataFrame, variable_df: pd.DataFrame):
    df = pd.concat(
        [fixed_df[["Expense", "Monthly Amount"]], variable_df[["Expense", "Monthly Amount"]]],
        ignore_index=True,
    )

    df = (
        df.groupby("Expense", as_index=False)["Monthly Amount"]
        .sum()
        .sort_values("Monthly Amount", ascending=False)
        .head(8)
    )

    fig = go.Figure(
        go.Bar(
            x=df["Monthly Amount"],
            y=df["Expense"],
            orientation="h",
            hovertemplate="%{y}: $%{x:,.0f}<extra></extra>",
        )
    )

    fig.update_layout(
        title=dict(text="Top Monthly Expenses", x=0, xanchor="left", font=dict(size=16)),
        height=300,
        margin=dict(l=120, r=20, t=50, b=20),
        xaxis=dict(tickprefix="$", separatethousands=True),
        yaxis=dict(autorange="reversed"),
    )
    return fig


def debt_payments_vs_balances(debt_df: pd.DataFrame):
    df = debt_df.copy()

    # Safer: handle missing columns gracefully (prevents KeyError if schema changes)
    needed = {"Debt", "Balance", "Monthly Payment"}
    missing = [c for c in needed if c not in df.columns]
    if missing:
        st.warning(f"Debt chart skipped: missing columns {missing}")
        return go.Figure()

    df["Balance"] = pd.to_numeric(df["Balance"], errors="coerce").fillna(0.0)
    df["Monthly Payment"] = pd.to_numeric(df["Monthly Payment"], errors="coerce").fillna(0.0)
    df = df[(df["Balance"] > 0) | (df["Monthly Payment"] > 0)]

    fig = go.Figure()

    fig.add_bar(
        x=df["Debt"],
        y=df["Monthly Payment"],
        name="Monthly Payment",
        hovertemplate="%{x}<br>Payment: $%{y:,.0f}<extra></extra>",
    )

    fig.add_bar(
        x=df["Debt"],
        y=df["Balance"],
        name="Balance",
        hovertemplate="%{x}<br>Balance: $%{y:,.0f}<extra></extra>",
    )

    fig.update_layout(
        title=dict(text="Debt Payments vs. Outstanding Balances", x=0, xanchor="left", font=dict(size=16)),
        barmode="group",
        height=300,
        margin=dict(l=20, r=20, t=50, b=40),
        yaxis=dict(tickprefix="$", separatethousands=True),
    )
    return fig


def render_visual_overview(
    *,
    expenses_total: float,
    total_monthly_debt_payments: float,
    saving_total: float,
    investing_cashflow: float,
    remaining: float,
    fixed_df: pd.DataFrame,
    variable_df: pd.DataFrame,
    debt_df: pd.DataFrame,
):
    st.subheader("Visual Overview")

    v1, v2 = st.columns(2, gap="large")

    with v1:
        st.plotly_chart(
            spending_mix_donut(
                expenses_total,
                total_monthly_debt_payments,
                saving_total,
                investing_cashflow,
                remaining,
            ),
            use_container_width=True,
        )

    with v2:
        st.plotly_chart(
            debt_payments_vs_balances(debt_df),
            use_container_width=True,
        )

    st.plotly_chart(
        top_expenses_bar(fixed_df, variable_df),
        use_container_width=True,
    )