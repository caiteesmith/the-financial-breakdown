# pages/about.py
import streamlit as st


def render_about():
    left, center, right = st.columns([0.12, 0.76, 0.12])
    with center:
        st.title("About this Dashboard")

        with st.container(border=True):
            st.subheader("Why I built this")

            st.markdown(
                """
                In early 2025, I built a simple spreadsheet because I was tired of feeling vague about my money.
                I wanted one clear place to see:

                - What was coming in  
                - What was going out  
                - And how much was actually left  

                Using that spreadsheet, I paid off about $20,000 of debt by mid-2025, including 3 credit cards, a consolidation loan, an auto loan, a student loan, and my financed iPhone.

                That clarity helped me finally qualify for a solid mortgage and buy my home in August 2025.

                This dashboard is that spreadsheet, rebuilt as a cleaner, friendlier tool so you don't have to DIY it from scratch.
                """
            )

        st.subheader("What this dashboard helps you do")

        with st.container(border=True):
            st.markdown(
                """
                - **See your full month in one view**  
                Income, fixed bills, essentials, non-essentials, saving, investing, and consumer debt, all in one layout.

                - **Know your real “safe to spend” amount**  
                After bills, saving, and debt payments, you'll see what's realistically left per month, week, and day.

                - **Get honest about debt**  
                See payoff timelines, estimated interest, and whether any minimum payment isn't even covering the interest.

                - **Know your emergency minimum**  
                If your income stopped, this shows what you'd actually need to stay afloat based on your real numbers.
                """
            )

        st.subheader("Who this is for")

        with st.container(border=True):
            st.markdown(
                """
                This is for you if you've ever thought:

                - “I make okay money… so why does it never feel like enough?”  
                - “I'm paying my cards, but I don't know when this will realistically end.”  
                - “I just want to know if I'm okay (or not) without being judged.”  

                It's not a bank-connected app, not a strict budget, and not about perfection. It's a clear snapshot so you can make decisions with your eyes open instead of guessing.
                """
            )

        st.caption("Built by someone who needed this clarity in order to make the right moves.")


def main():
    render_about()