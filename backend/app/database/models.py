from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class WorldPopulation(Base):
    __tablename__ = "world_population"
    id = Column(Integer, primary_key=True)
    country_name = Column(String)
    country_code = Column(String)
    indicator_name = Column(String)
    indicator_code = Column(String)
    year = Column(Integer)
    population = Column(Float)


class Covid19Vaccine(Base):
    __tablename__ = "covid19_vaccine"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    country_region = Column(String)
    continent_name = Column(String)
    continent_code = Column(String)
    combined_key = Column(String)
    doses_admin = Column(Float)
    people_at_least_one_dose = Column(Float)
    population = Column(Float)
    uid = Column(Float)
    iso2 = Column(String)
    iso3 = Column(String)
    code3 = Column(Float)
    fips = Column(Float)
    lat = Column(Float)
    long = Column(Float)


class CoronavirusBaseMixin:
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    province = Column(String)
    country = Column(String)
    lat = Column(Float)
    long = Column(Float)
    type = Column(String)
    cases = Column(Integer)
    uid = Column(Float)
    iso2 = Column(String)
    iso3 = Column(String)
    code3 = Column(Float)
    combined_key = Column(String)
    population = Column(Float)
    continent_name = Column(String)
    continent_code = Column(String)


class CoronavirusDaily(Base, CoronavirusBaseMixin):
    __tablename__ = "coronavirus_daily"


class Coronavirus2020(Base, CoronavirusBaseMixin):
    __tablename__ = "coronavirus_2020"


class Coronavirus2021(Base, CoronavirusBaseMixin):
    __tablename__ = "coronavirus_2021"


class Coronavirus2022(Base, CoronavirusBaseMixin):
    __tablename__ = "coronavirus_2022"


class Coronavirus2023(Base, CoronavirusBaseMixin):
    __tablename__ = "coronavirus_2023"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
