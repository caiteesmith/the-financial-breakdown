import streamlit as st

def render_finance_theme_darkgreen():
    st.markdown(
    """
    <style>
      /* ---------- Cards ---------- */
      div[data-testid="stExpander"] > details,
      div[data-testid="metric-container"],
      div[data-testid="stDataFrame"] {
        border-radius: 14px;
        border: 1px solid rgba(230,240,236,.08);
        background: #16201C;
      }

      /* ---------- Buttons (squoval) ---------- */
      button[kind="primary"],
      button[kind="secondary"] {
        border-radius: 10px !important;
        padding: .45rem .85rem;
        font-weight: 500;
      }

      /* ---------- Tabs ---------- */
      button[data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: .35rem .75rem;
      }

      /* ---------- Inputs ---------- */
      .stTextInput input,
      .stNumberInput input,
      .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 10px !important;
        background-color: #0D1412 !important;
        border: 1px solid rgba(230,240,236,.10) !important;
      }

      /* ---------- Dividers ---------- */
      hr {
        border: none;
        height: 1px;
        background: rgba(230,240,236,.10);
      }
    </style>
    """,
    unsafe_allow_html=True,
)