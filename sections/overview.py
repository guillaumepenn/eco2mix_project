import plotly.express as px
import streamlit as st


def show_overview(balance, region_df, selected_region, geojson_regions, start_year, end_year):
    region_balance = balance[balance["region"] == selected_region]["balance"].iloc[0]
    if region_balance > 0:
        st.success(f"{selected_region} produces on average {region_balance:,.0f} MW more than it consumes.")
    else:
        st.error(f"{selected_region} consumes on average {-region_balance:,.0f} MW more than it produces.")

    # KPIs of the selected region
    avg_production = region_df["production"].mean()
    avg_consumption = region_df["consumption"].mean()
    coverage_rate = avg_production / avg_consumption * 100
    renewable_share = region_df["renewable"].sum() / region_df["production"].sum() * 100

    st.caption(f"Selected period: {start_year}–{end_year}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Average production", f"{avg_production:,.0f} MW",
                help="Average power produced in the region, all sources combined, over the whole period.")
    col2.metric("Average consumption", f"{avg_consumption:,.0f} MW",
                help="Average power consumed in the region over the whole period.")
    col3.metric("Coverage rate", f"{coverage_rate:.0f} %",
                help="Average production divided by average consumption. Above 100 %, the region produces more than it consumes.")
    col4.metric("Renewable share", f"{renewable_share:.0f} %",
                help="Wind, solar, hydro and bioenergy as a share of the total production.")

    # Chart 1 : France's map
    st.subheader("Which regions produce more than they consume ?")
    fig_map = px.choropleth(
        balance, geojson=geojson_regions, locations="region_code",
        featureidkey="properties.code", color="balance", hover_name="region",
        color_continuous_scale="RdBu", color_continuous_midpoint=0,
        labels={"balance": "Production − consumption (MW)"},
    )
    fig_map.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
    fig_map.update_layout(height=600, margin=dict(l=0, r=0, t=10, b=0))
    map_col, _ = st.columns([1, 1])
    map_col.plotly_chart(fig_map)

    st.caption("Map: regions in blue produce more than they consume, regions in red consume more than they produce.")

    n_surplus = (balance["balance"] > 0).sum()
    st.markdown("What can be said about this map ? Around half of France's region consumes more energy than it produces. " \
    "The most blatant example is the Île-de-France region which, on average, consumes 7,445 MW more than what it produces. "
    "How can this be explained ?"
    )

    st.markdown(
        "- Île-de-France may be the smallest but the most populated region of France (over **12 millions inhabitants**), so the electricity in this region is pretty. Moreover, it is a region of high activity, with the presence of a megacity and a capital like Paris\n"
        "- Most of France's electricity is from nuclear origin, though Île-de-France has no nuclear plants, so it logically strugles to produce more energy\n"
    )

    # Label each region as surplus or deficit
    balance_sorted = balance.sort_values("balance", ascending=False)
    balance_sorted["type"] = "Deficit"
    balance_sorted.loc[balance_sorted["balance"] > 0, "type"] = "Surplus"

    # Chart 2 : Average produuction - consumption by region
    fig_rank = px.bar(
        balance_sorted, x="region", y="balance", color="type",
        color_discrete_map={"Surplus": "steelblue", "Deficit": "indianred"},
        labels={"region": "Region", "balance": "Production − consumption (MW)", "type": "Type"},
        title="Average production − consumption by region",
    )
    st.plotly_chart(fig_rank)

    st.caption("The same balance as the map, ranked from the largest surplus to the largest deficit.")

    top = balance_sorted.iloc[0]
    bottom = balance_sorted.iloc[-1]
    
    st.markdown("Again, regions such as Centre-Val de Loire or Auvergne-Rhône-Alpes have the largest surplus (around more than 6,000 MW on average) "
    "and Île-de-France the largest deficit (~7,000 MW)." \
    " Deficit regions rely on the grid and on exchanges with their neighbours to cover their consumption. So every region aren't equal in a matter of energetic independancy.")

    st.markdown("**But how to explain that these production differences ?**")