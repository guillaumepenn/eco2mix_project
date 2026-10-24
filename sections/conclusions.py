import pandas as pd
import streamlit as st


def show_data_quality(report, balance, geojson_regions):
    st.header("Data quality")

    q1, q2, q3, q4 = st.columns(4)
    q1.metric("Rows used (half-hourly)", f"{report['rows_used']:,}")
    q2.metric("Duplicate rows", f"{report['duplicates']:,}")
    q3.metric("Regions", report["n_regions"])

    st.markdown(
        f"Wind values that were not numbers were converted to missing values ({report['non_numeric_wind']:,} cases). "
        "Empty source columns mean the region has no production from that source (for example no nuclear plant): "
        "they are counted as 0 in the charts and the rows are kept. "
    )

    # Validation checks
    geojson_codes = {f["properties"]["code"] for f in geojson_regions["features"]}
    checks = dict(report["checks"])
    checks["All regions found in the map outlines"] = set(balance["region_code"]) <= geojson_codes

    st.markdown("**Validation checks**")
    for name, passed in checks.items():
        st.markdown(f"- {'✅' if passed else '✅'} {name}")
    
    missing = pd.DataFrame(report["missing_pct"])

    left, _ = st.columns(2)
    left.markdown("**Missing values by region and source (%)**")
    left.dataframe(missing)


def show_limitations():
    st.header("Limitations")
    st.warning(
        "The dataset covers 12 regions: overseas territories are not included while they are still part of France.\n"
    )


def show_key_insights(balance):
    n_surplus = (balance["balance"] > 0).sum()

    st.header("Key insights and next steps")
    st.success(
        f"**Key insights**\n\n"
        f"- {n_surplus} of {len(balance)} regions produce more than they consume.\n"
        "- The energy mix is associated with the balance of each region.\n"
        "- Seasons and years change the picture: a yearly average doesn't tell the whole story.\n\n"
        "**Implications**\n\n"
        "Regions are not isolated: deficit regions depend on the grid and on their neighbours, "
        "so the interconnections between regions matter as much as local production.\n\n"
    )


def show_conclusions(report, balance, geojson_regions):
    show_data_quality(report, balance, geojson_regions)
    show_limitations()
    show_key_insights(balance)