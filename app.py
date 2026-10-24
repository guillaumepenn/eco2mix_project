import streamlit as st

from sections.conclusions import show_conclusions
from sections.deep_dives import show_deep_dives
from sections.intro import show_intro
from sections.overview import show_overview
from utils.io import load_geojson
from utils.prep import load_processed_data

st.set_page_config(page_title="Does my region produce what it consumes?", layout="wide")


# ---------- Data loading (cached: runs only once) ----------
@st.cache_data(show_spinner="Loading data...")
def load_data():
    return load_processed_data()

df, report = load_data()
geojson_regions = load_geojson()

# ---------- Sidebar: filters ----------
st.sidebar.header("Filters")

selected_region = st.sidebar.selectbox("Choose your region", sorted(df["region"].unique()))

min_year = int(df["year"].min())
max_year = int(df["year"].max())
start_year, end_year = st.sidebar.slider(
    "Period (years)", min_value=min_year, max_value=max_year, value=(min_year, max_year),
    help="Applies to the KPIs, the map, the ranking and all the charts.",
)

# Keep only the selected years, then the selected region
period_df = df[(df["year"] >= start_year) & (df["year"] <= end_year)]
region_df = period_df[period_df["region"] == selected_region]

# "balance" table: one row per region (average power in MW over the selected period)
balance = period_df.groupby(["region_code", "region"])[["production", "consumption"]].mean().reset_index()
balance["balance"] = balance["production"] - balance["consumption"]
balance["region_code"] = balance["region_code"].astype(str).str.zfill(2)   # 1 -> "01"

# ---------- Page ----------
show_intro(report)
show_overview(balance, region_df, selected_region, geojson_regions, start_year, end_year)
show_deep_dives(period_df, region_df, selected_region)
show_conclusions(report, balance, geojson_regions)