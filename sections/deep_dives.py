import pandas as pd
import plotly.express as px
import streamlit as st

from utils.prep import sources, renewable_sources, tco_cols
from utils.viz import source_colors


def compute_mix(period_df):
    """Monthly average power by region and source, in long format."""
    mix = period_df.groupby(["region", "month"])[sources].mean().reset_index()
    mix = mix.melt(id_vars=["region", "month"], var_name="source", value_name="power")
    mix["power"] = mix["power"].fillna(0)   
    return mix


def show_deep_dives(period_df, region_df, selected_region):
    st.subheader("Each region has its own energy signature")

    mix = compute_mix(period_df)

    # Chart 3: Prodction mix multiples by region
    fig_mix = px.area(
        mix, x="month", y="power", color="source", facet_col="region", facet_col_wrap=4,
        groupnorm="percent", color_discrete_map=source_colors,
        labels={"month": "Date", "power": "Share of the mix (%)", "source": "Source"},
        title="Production mix by region (share of each source, monthly average)",
    )
    fig_mix.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1])) 
    fig_mix.update_layout(height=700)
    st.plotly_chart(fig_mix)

    st.caption("Each panel shows the share of each source in a region's production, month by month.")

    st.markdown("Most of France's energy is from nuclear origin. Again, Île-de-France doesn't have any nuclear energy input as it has no nuclear plant.\n\n" \
    "The energy signature of each region may explain why some have a surplus of energy while others has a deficit. Regions like Normandy or Centre-Val de Loire have many nuclear facilities, giving them a high surplus of electricity.\n\n"
    "Regions like Bretagne or Pays de la Loire have a more mixed energetic origin, coming from different sources like solar, wind or water. These regions have an energetic deficit.\n\n"
    "**So it seems the more a region has a mixed energy signature, the bigger of an energy deficit it has.**")

    # Chart 5: coverage rate by source for the selected region
    tco = region_df[tco_cols].mean().fillna(0).reset_index() 
    tco.columns = ["source", "coverage"]
    tco["source"] = tco["source"].str.replace("tco_", "")

    # Headline insight, computed from the data
    best = tco.sort_values("coverage", ascending=False).iloc[0]
    st.markdown(f"**In {selected_region}, {best['source']} covers {best['coverage']:.0f} % of the consumption.**")

    fig_tco = px.bar(
        tco, x="source", y="coverage", color="source", color_discrete_map=source_colors,
        labels={"source": "Source", "coverage": "Share of the consumption covered (%)"},
        title=f"Coverage rate by source: {selected_region}",
    )
    st.plotly_chart(fig_tco)

    st.caption("Share of the selected region's consumption covered by each source, on average over the period. "
               "The bars can add up to more than 100 % in a region with a surplus.")

    st.info(
        "A region's energy mix is associated with its balance. Regions with a large nuclear or hydro base "
        "tend to show a surplus, while regions with little production of their own tend to show a deficit. "
        "No single source explains the result on its own."
    )


    st.subheader("Time changes the picture")

    st.markdown("From now, we've seen the energetic production of each region over years, but their production isn't constant." \
    " The season and the weather are strong factors that make the renewable energy production more unstable than you think.")

    # Renewable share by year and month for the selected region
    heat = region_df.groupby(["year", "month_num"])[["renewable", "production"]].sum().reset_index()
    heat["renewable_share"] = heat["renewable"] / heat["production"] * 100

    # Headline insight, computed from the data (average over the years, by month)
    by_month = heat.groupby("month_num")["renewable_share"].mean()
    low_month = pd.Timestamp(2021, int(by_month.idxmin()), 1).strftime("%B")
    high_month = pd.Timestamp(2021, int(by_month.idxmax()), 1).strftime("%B")
    st.markdown(
        f"**In {selected_region}, the renewable share goes from {by_month.min():.0f} % in {low_month} "
        f"to {by_month.max():.0f} % in {high_month} (average over the years).**"
    )

        # Chart 6: all renewable sources over time
    evolution = region_df.groupby("month")[renewable_sources].mean().fillna(0).reset_index()   # absent source = 0

    fig_evolution = px.line(
        evolution, x="month", y=renewable_sources,
        color_discrete_map=source_colors,
        labels={"month": "Date", "value": "Average power (MW)", "variable": "Source"},
        title=f"Renewable sources since {region_df['year'].min()}: {selected_region}",
    )
    st.plotly_chart(fig_evolution)

    st.caption("Monthly average power of wind, solar, hydro and bioenergy in the selected region.")

    st.info(
                "**Some observations** : How much a source produces powers depends of the weather and the time of the year. A region gets more power from wind in a season where the latter are strong and occur often." \
                " So we can observe that the power produced by wind is higher in winter, especially in january and february, each year. " \
                "The same observation goes for solar energy, it tends to be higher in summer, when sun coverage is higher and days are longer."
            )
    
    # Chart 7: heatmap of the renewable share (rows = years, columns = months)
    heat_table = heat.pivot(index="year", columns="month_num", values="renewable_share")

    fig_heat = px.imshow(
        heat_table, color_continuous_scale="Greens", aspect="auto",
        labels={"x": "Month (1 = January)", "y": "Year", "color": "Renewable share (%)"},
        title=f"Renewable share of the production by month: {selected_region}",
    )

    st.markdown("It is useful to get an insight of how much renewable energy is part of a region's energetic mix, as it can give us an idea of much the region or the country is investing in the fight against the climate change.")
    fig_heat.update_xaxes(type="category")   # show 1, 2, 3... instead of 1.5, 2.5...
    fig_heat.update_yaxes(type="category")
    st.plotly_chart(fig_heat)

    st.caption("Each cell is the renewable share (wind, solar, hydro and bioenergy) of the production for one month of one year.")

    st.info(
        "The renewable share changes with the season and the output of each renewable source varies from month to month, "
        "The renewable share changes with the season and wind and solar output varies from month to month, "
        "so a yearly average hides these swings."
    )