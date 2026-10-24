import pandas as pd
import streamlit as st


def show_intro(report):
    st.title("Does my region produce what it consumes?")

    st.caption("Source: éCO2mix regional data (consolidated and definitive), RTE, data.gouv.fr. Licence Ouverte.")

    st.markdown(
        "France's electricity is often discussed as a single block, but it is not produced where it is consumed. "
        "Some regions generate far more than they use, others depend on their neighbours. "
        "Pick your region in the sidebar to see which side it is on."
    )

    with st.expander("About the data"):
        st.markdown(
            f"""
- **What it is:** éCO2mix is the electricity data service of RTE, the French grid operator. This dataset gives the production by source and the consumption of each region, every 30 minutes, from {pd.Timestamp(report['first_date']).year} to {pd.Timestamp(report['last_date']).strftime('%B %Y')}.
- **Definitive vs consolidated:** definitive data are final, consolidated data cover the most recent months and may still be revised.
- **Coverage rate (TCO):** share of a region's consumption covered by its own production of a given source.
- **Load factor (TCH):** ratio between what a source produces and what it could produce at full capacity.
"""
        )