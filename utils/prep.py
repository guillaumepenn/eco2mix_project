import json
from pathlib import Path
import pandas as pd
from utils.io import load_raw_data

# ---------- Settings ----------
sources = ["thermal", "nuclear", "wind", "solar", "hydro", "bioenergy"]
renewable_sources = ["wind", "solar", "hydro", "bioenergy"]

# Original French column names -> short English names
new_names = {
    "Code INSEE région": "region_code", "Région": "region", "Nature": "status",
    "Date": "date", "Consommation (MW)": "consumption",
    "Thermique (MW)": "thermal", "Nucléaire (MW)": "nuclear",
    "Eolien (MW)": "wind", "Solaire (MW)": "solar",
    "Hydraulique (MW)": "hydro", "Bioénergies (MW)": "bioenergy",
    "TCO Thermique (%)": "tco_thermal", "TCH Thermique (%)": "tch_thermal",
    "TCO Nucléaire (%)": "tco_nuclear", "TCH Nucléaire (%)": "tch_nuclear",
    "TCO Eolien (%)": "tco_wind", "TCH Eolien (%)": "tch_wind",
    "TCO Solaire (%)": "tco_solar", "TCH Solaire (%)": "tch_solar",
    "TCO Hydraulique (%)": "tco_hydro", "TCH Hydraulique (%)": "tch_hydro",
    "TCO Bioénergies (%)": "tco_bioenergy", "TCH Bioénergies (%)": "tch_bioenergy",
}


def clean_data(raw):
    """Clean the raw eCO2mix table. Returns the clean table and a small quality report."""
    df = raw.rename(columns=new_names)
    df = df.drop(columns=["Column 30"], errors="ignore")   # empty unnamed column

    # Numbers for the data quality section
    report = {"raw_rows": len(df), "duplicates": int(df.duplicated().sum())}

    # "wind" is read as text: convert to numbers (invalid values become NaN)
    wind_missing_before = df["wind"].isna().sum()
    df["wind"] = pd.to_numeric(df["wind"], errors="coerce")
    report["non_numeric_wind"] = int(df["wind"].isna().sum() - wind_missing_before)

    # Date columns
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["month_num"] = df["date"].dt.month
    df["year"] = df["date"].dt.year

    # Only drop rows without consumption (NOT a global dropna: regions without
    # nuclear plants have empty nuclear columns and would disappear)
    rows_before = len(df)
    df = df.dropna(subset=["consumption"])
    report["rows_removed"] = rows_before - len(df)

    # min_count=1: empty sources are ignored, NaN only if all sources are empty
    df["production"] = df[sources].sum(axis=1, min_count=1)
    df["renewable"] = df[renewable_sources].sum(axis=1, min_count=1)
        # More numbers for the data quality section
    report["rows_used"] = len(df)
    report["n_regions"] = int(df["region"].nunique())
    report["first_date"] = str(df["date"].min())
    report["last_date"] = str(df["date"].max())
    report["status_counts"] = {k: int(v) for k, v in df["status"].value_counts().items()}
    report["missing_pct"] = (df[sources].isna().groupby(df["region"]).mean() * 100).round(1).to_dict()
    
    # Validation checks (True = passed)
    report["checks"] = {
        "No negative consumption": bool((df["consumption"] >= 0).all()),
        "No negative production": bool((df["production"].dropna() >= 0).all()),
        "Every region has data for every year": bool((df.groupby("region")["year"].nunique() == df["year"].nunique()).all()),
        "No duplicate rows": report["duplicates"] == 0,
    }
    return df, report



# ---------- Monthly aggregation and saved files ----------
tco_cols = ["tco_" + s for s in sources]

PROCESSED_DIR = Path("data/processed")
MONTHLY_PATH = PROCESSED_DIR / "monthly.parquet"
REPORT_PATH = PROCESSED_DIR / "report.json"


def aggregate_monthly(df):
    """One row per region and month: average power of each source."""
    group_cols = ["region_code", "region", "month", "year", "month_num"]
    value_cols = ["consumption", "production", "renewable"] + sources + tco_cols
    return df.groupby(group_cols)[value_cols].mean().reset_index()


def build_processed_data():
    """Read the raw CSV, clean it, aggregate it and save the small files."""
    raw = load_raw_data()
    df, report = clean_data(raw)
    monthly = aggregate_monthly(df)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    monthly.to_parquet(MONTHLY_PATH, index=False)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f)


def load_processed_data():
    """Return the monthly table and the quality report (built first if missing)."""
    if not MONTHLY_PATH.exists() or not REPORT_PATH.exists():
        build_processed_data()
    monthly = pd.read_parquet(MONTHLY_PATH)
    with open(REPORT_PATH, encoding="utf-8") as f:
        report = json.load(f)
    return monthly, report


if __name__ == "__main__":
    build_processed_data()   # run with: python -m utils.prep