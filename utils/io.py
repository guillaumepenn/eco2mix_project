import json
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# ---------- Settings ----------
CSV_PATH = Path("data/raw/eco2mix-regional-cons.csv")
CSV_URL = "https://www.data.gouv.fr/api/1/datasets/r/4c308634-d76e-40b0-a777-ab99a8871564"

GEOJSON_PATH = Path("data/regions_contours.geojson")
GEOJSON_URL = ("https://raw.githubusercontent.com/omarbk/france-geojson/"
               "master/regions-version-simplifiee.geojson")


def download_file(url, path):
    """Download a file only if it is not already on disk."""
    path = Path(path)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".part")   # avoids keeping a half-downloaded file
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(temp_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
    temp_path.replace(path)
    return path


def load_raw_data():
    """Return the raw eCO2mix table (downloads the CSV first if it is missing)."""
    download_file(CSV_URL, CSV_PATH)
    return pd.read_csv(CSV_PATH, sep=";", low_memory=False)


@st.cache_data
def load_geojson():
    """Return the region outlines (downloads the file first if it is missing)."""
    download_file(GEOJSON_URL, GEOJSON_PATH)
    with open(GEOJSON_PATH, encoding="utf-8") as f:
        return json.load(f)