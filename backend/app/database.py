from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
from sqlalchemy.orm import Session
import pandas as pd
from models import CountryWiseLatest, WorldometerData, Covid19CleanComplete, FullGrouped, DayWise, USACountyWise

DATABASE_URI = "postgresql://postgres:password@db:5432/covid_database"

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def load_data(session: Session):
    csv_files = {
        CountryWiseLatest: 'data/country_wise_latest.csv',
        WorldometerData: 'data/worldometer_data.csv',
        Covid19CleanComplete: 'data/covid_19_clean_complete.csv',
        FullGrouped: 'data/full_grouped.csv',
        DayWise: 'data/day_wise.csv',
        USACountyWise: 'data/usa_county_wise.csv'
    }

    for model, file_path in csv_files.items():
        print(f"Loading data for {model.__tablename__} from {file_path}")
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("/", "_")
        records = df.to_dict(orient="records")
        session.bulk_insert_mappings(model, records)
        session.commit()