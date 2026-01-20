# =========================================
# file: app.py
# =========================================
from __future__ import annotations

import streamlit as st

from tools.finance_dashboard import render_personal_finance_dashboard
from tools.mortgage_payoff import render_mortgage_payoff_calculator
from tools.about import render_about
from tools.supabase_client import get_supabase_client


def get_current_user():
    """
    Return the current Supabase user if logged in, otherwise None.

    We cache it in st.session_state["user"] so we don't call Supabase
    on every rerun.
    """
    if "user" in st.session_state:
        return st.session_state["user"]

    supabase = get_supabase_client()
    try:
        res = supabase.auth.get_user()
        st.session_state["user"] = res.user
    except Exception:
        st.session_state["user"] = None

    return st.session_state["user"]


def main():
    st.set_page_config(page_title="Financial Breakdown", layout="wide")

    supabase = get_supabase_client()
    user = get_current_user()

    # -------------------------
    # Sidebar
    # -------------------------
    with st.sidebar:
        st.title("Financial Breakdown")

        # Navigation
        page = st.radio(
            "Go to",
            ["About Financial Breakdown", "Personal Finance Dashboard", "Mortgage Payoff Calculator"],
            index=1,  # default to dashboard
            key="nav_page",
        )

        st.divider()

        # Account section
        if user is not None:
            email = getattr(user, "email", None)
            if email:
                st.caption(f"Logged in as **{email}**")
            else:
                st.caption("Logged in")

            if st.button("Log out", use_container_width=True):
                try:
                    supabase.auth.sign_out()
                except Exception:
                    # If sign_out fails, still clear local state
                    pass
                st.session_state["user"] = None
                st.session_state.pop("pf_loaded_from_db", None)
                st.rerun()
        else:
            st.caption(
                "You can use this tool without an account. "
                "If you want to save and come back later, log in or sign up below."
            )
            with st.expander("Login/Sign Up", expanded=False):

                tab_login, tab_signup = st.tabs(["Log in", "Sign up"])

                with tab_login:
                    st.subheader("Welcome back", anchor=False)
                    email = st.text_input("Email", key="login_email")
                    password = st.text_input("Password", type="password", key="login_password")
                    if st.button("Log in", use_container_width=True, key="login_btn"):
                        try:
                            res = supabase.auth.sign_in_with_password(
                                {"email": email, "password": password}
                            )
                            st.session_state["user"] = res.user
                            st.success("Logged in!")
                            # Clear any cached DB load flag so we pull their saved state
                            st.session_state.pop("pf_loaded_from_db", None)
                            st.rerun()
                        except Exception as e:
                            st.error(f"Login failed: {e}")

                with tab_signup:
                    st.subheader("Create an account", anchor=False)
                    email2 = st.text_input("Email ", key="signup_email")
                    password2 = st.text_input("Password ", type="password", key="signup_password")
                    if st.button("Sign up", use_container_width=True, key="signup_btn"):
                        try:
                            res = supabase.auth.sign_up(
                                {"email": email2, "password": password2}
                            )
                            st.success(
                                "Check your email to confirm your account, then log in above."
                            )
                        except Exception as e:
                            st.error(f"Signup failed: {e}")

    # -------------------------
    # Page routing
    # -------------------------
    if page == "Personal Finance Dashboard":
        render_personal_finance_dashboard(user)
    elif page == "Mortgage Payoff Calculator":
        render_mortgage_payoff_calculator(user)
    else:
        render_about()


if __name__ == "__main__":
    main()