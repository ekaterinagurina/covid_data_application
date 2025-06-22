from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import (
    Base, WorldPopulation, Covid19Vaccine, CoronavirusDaily,
    Coronavirus2020, Coronavirus2021, Coronavirus2022, Coronavirus2023
)
from common.settings import database_settings
import pandas as pd

engine = create_engine(database_settings.uri)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def load_csv_to_db(session, model, path, parse_dates=None, lowercase_columns=True, transform_fn=None):
    df = pd.read_csv(path, parse_dates=parse_dates, low_memory=False)

    if lowercase_columns:
        df.columns = df.columns.str.lower().str.replace(" ", "_")

    if transform_fn:
        df = transform_fn(df)

    records = df.to_dict(orient="records")
    session.bulk_insert_mappings(model, records)
    session.commit()
    print(f"Loaded {len(records)} rows into {model.__tablename__}")
    return records


def transform_world_population(df):
    id_vars = ['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code']
    value_vars = [col for col in df.columns if col.isdigit()]

    df_long = df.melt(id_vars=id_vars, value_vars=value_vars, var_name="year", value_name="population")
    df_long['year'] = df_long['year'].astype(int)
    df_long['population'] = pd.to_numeric(df_long['population'], errors='coerce')

    df_long.rename(columns=lambda col: col.lower().replace(" ", "_"), inplace=True)

    return df_long


def load_data(session: Session):
    load_csv_to_db(
        session,
        WorldPopulation,
        'data/world_population.csv',
        lowercase_columns=False,
        transform_fn=transform_world_population
    )

    load_csv_to_db(
        session,
        Covid19Vaccine,
        'data/covid19_vaccine.csv',
        parse_dates=["date"]
    )

    corona_files = {
        Coronavirus2020: 'data/coronavirus_2020.csv',
        Coronavirus2021: 'data/coronavirus_2021.csv',
        Coronavirus2022: 'data/coronavirus_2022.csv',
        Coronavirus2023: 'data/coronavirus_2023.csv',
    }

    combined_records = []
    for model, path in corona_files.items():
        records = load_csv_to_db(
            session,
            model,
            path,
            parse_dates=["date"]
        )
        combined_records.extend(records)

    if combined_records:
        session.bulk_insert_mappings(CoronavirusDaily, combined_records)
        session.commit()
        print(f"Loaded combined {len(combined_records)} rows into coronavirus_daily")
