## Data

- Dataset: éCO2mix regional data, consolidated and definitive (RTE)
- Source: https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives
- Licence: Licence ouverte
- Region outlines: france-geojson (IGN Admin Express and INSEE, Licence ouverte)

## To run the project :

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The raw data is downloaded automatically when needed. To rebuild the processed data, delete `data/processed/` and run the app again.

## Repo links
- Github : https://github.com/guillaumepenn/eco2mix_project
- Streamlit Community Cloud : https://eco2mixproject-xlxcwm9snhwcc5xmqhea8c.streamlit.app/s