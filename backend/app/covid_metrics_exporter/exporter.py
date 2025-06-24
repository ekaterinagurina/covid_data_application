from prometheus_client import start_http_server, Gauge
import pandas as pd
import time
import os
import glob

cases_metric = Gauge('covid_cases_total', 'Total confirmed COVID-19 cases', ['country', 'lat', 'lon'])
deaths_metric = Gauge('covid_deaths_total', 'Total COVID-19 deaths', ['country', 'lat', 'lon'])
vaccinated_metric = Gauge('covid_vaccinated_total', 'People with at least one vaccine dose', ['country', 'lat', 'lon'])

DATA_DIR = os.environ.get("COVID_DATA_DIR", "./data")

def load_cases_and_deaths():
    pattern = os.path.join(DATA_DIR, "coronavirus_*.csv")
    files = glob.glob(pattern)

    all_data = []

    for file in files:
        try:
            df = pd.read_csv(file, low_memory=False, usecols=["country", "lat", "long", "type", "cases"])
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not all_data:
        return

    df_all = pd.concat(all_data)
    df_all = df_all.dropna(subset=["country", "lat", "long", "type", "cases"])

    confirmed = df_all[df_all["type"] == "confirmed"]
    deaths = df_all[df_all["type"] == "death"]

    confirmed_grouped = confirmed.groupby(["country", "lat", "long"])["cases"].sum().reset_index()
    deaths_grouped = deaths.groupby(["country", "lat", "long"])["cases"].sum().reset_index()

    for _, row in confirmed_grouped.iterrows():
        cases_metric.labels(
            country=row['country'], lat=str(float(row['lat'])), lon=str(float(row['long']))
        ).set(row['cases'])

    for _, row in deaths_grouped.iterrows():
        deaths_metric.labels(
            country=row['country'], lat=str(float(row['lat'])), lon=str(float(row['long']))
        ).set(row['cases'])

def load_vaccinations():
    path = os.path.join(DATA_DIR, "covid19_vaccine.csv")
    try:
        df = pd.read_csv(path, usecols=["country_region", "lat", "long", "people_at_least_one_dose"])
        df = df.dropna(subset=["country_region", "lat", "long", "people_at_least_one_dose"])
        grouped = df.groupby(["country_region", "lat", "long"])["people_at_least_one_dose"].max().reset_index()

        for _, row in grouped.iterrows():
            vaccinated_metric.labels(
                country=row['country_region'], lat=str(float(row['lat'])), lon=str(float(row['long']))
            ).set(row['people_at_least_one_dose'])

    except Exception as e:
        print(f"Error reading vaccine data: {e}")

def update_metrics():
    load_cases_and_deaths()
    load_vaccinations()

if __name__ == '__main__':
    start_http_server(9100)
    while True:
        update_metrics()
        time.sleep(60)
