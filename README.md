## Data

- Dataset: éCO2mix regional data, consolidated and definitive (RTE)
- Source: https://www.data.gouv.fr/datasets/donnees-eco2mix-regionales-consolidees-et-definitives
- Licence: Open Licence 2.0
- Region outlines: france-geojson (IGN Admin Express and INSEE, Licence ouverte)

## To run the project :

python -m pip install -r requirements.txt
python -m streamlit run app.py

The raw data is downloaded automatically when needed. To rebuild the processed data, delete `data/processed/` and run the app again.# eco2mix_project
