from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class CountryWiseLatest(Base):
    __tablename__ = 'country_wise_latest'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_region = Column(String, nullable=False)
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)
    new_cases = Column(Integer)
    new_deaths = Column(Integer)
    new_recovered = Column(Integer)
    deaths_per_100_cases = Column(Float)
    recovered_per_100_cases = Column(Float)
    deaths_per_100_recovered = Column(Float)
    confirmed_last_week = Column(Integer)
    one_week_change = Column(Integer)
    one_week_percent_increase = Column(Float)
    who_region = Column(String)

class WorldometerData(Base):
    __tablename__ = 'worldometer_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    country_region = Column(String, nullable=False)
    continent = Column(String)
    population = Column(Float)
    totalcases = Column(Integer)
    newcases = Column(Float)
    totaldeaths = Column(Float)
    newdeaths = Column(Float)
    totalrecovered = Column(Float)
    newrecovered = Column(Float)
    activecases = Column(Float)
    serious_critical = Column(Float)
    tot_cases_per_1m_pop = Column(Float)
    deaths_per_1m_pop = Column(Float)
    totaltests = Column(Float)
    tests_per_1m_pop = Column(Float)
    who_region = Column(String)

class Covid19CleanComplete(Base):
    __tablename__ = 'covid_19_clean_complete'
    id = Column(Integer, primary_key=True, autoincrement=True)
    province_state = Column(String)
    country_region = Column(String, nullable=False)
    lat = Column(Float)
    long = Column(Float)
    date = Column(Date)
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)
    who_region = Column(String)

class FullGrouped(Base):
    __tablename__ = 'full_grouped'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    country_region = Column(String, nullable=False)
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)
    new_cases = Column(Integer)
    new_deaths = Column(Integer)
    new_recovered = Column(Integer)
    who_region = Column(String)

class DayWise(Base):
    __tablename__ = 'day_wise'
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    confirmed = Column(Integer)
    deaths = Column(Integer)
    recovered = Column(Integer)
    active = Column(Integer)
    new_cases = Column(Integer)
    new_deaths = Column(Integer)
    new_recovered = Column(Integer)
    deaths_per_100_cases = Column(Float)
    recovered_per_100_cases = Column(Float)
    deaths_per_100_recovered = Column(Float)
    no_of_countries = Column(Integer)

class USACountyWise(Base):
    __tablename__ = 'usa_county_wise'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer)
    iso2 = Column(String)
    iso3 = Column(String)
    code3 = Column(Integer)
    fips = Column(Float)
    admin2 = Column(String)
    province_state = Column(String)
    country_region = Column(String, nullable=False)
    lat = Column(Float)
    long = Column(Float)
    combined_key = Column(String)
    date = Column(Date)
    confirmed = Column(Integer)
    deaths = Column(Integer)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
