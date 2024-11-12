import pandas as pd
from sqlalchemy import create_engine, text

user = "postgres"
password = "password"
host = "db"
port = "5432"
db_name = "covid_database"

def create_tables(engine):
    table_creation_queries = [
        """
        CREATE TABLE IF NOT EXISTS country_wise_latest (
            country_region VARCHAR,
            confirmed INT,
            deaths INT,
            recovered INT,
            active INT,
            new_cases INT,
            new_deaths INT,
            new_recovered INT,
            deaths_per_100_cases FLOAT,
            recovered_per_100_cases FLOAT,
            deaths_per_100_recovered FLOAT,
            confirmed_last_week INT,
            one_week_change INT,
            one_week_percent_increase FLOAT,
            who_region VARCHAR
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS worldometer_data (
            country_region VARCHAR,
            continent VARCHAR,
            population FLOAT,
            totalcases INT,
            newcases FLOAT,
            totaldeaths FLOAT,
            newdeaths FLOAT,
            totalrecovered FLOAT,
            newrecovered FLOAT,
            activecases FLOAT,
            serious_critical FLOAT,
            tot_cases_per_1m_pop FLOAT,
            deaths_per_1m_pop FLOAT,
            totaltests FLOAT,
            tests_per_1m_pop FLOAT,
            who_region VARCHAR
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS covid_19_clean_complete (
            province_state VARCHAR,
            country_region VARCHAR,
            lat FLOAT,
            long FLOAT,
            date DATE,
            confirmed INT,
            deaths INT,
            recovered INT,
            active INT,
            who_region VARCHAR
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS full_grouped (
            date DATE,
            country_region VARCHAR,
            confirmed INT,
            deaths INT,
            recovered INT,
            active INT,
            new_cases INT,
            new_deaths INT,
            new_recovered INT,
            who_region VARCHAR
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS day_wise (
            date DATE,
            confirmed INT,
            deaths INT,
            recovered INT,
            active INT,
            new_cases INT,
            new_deaths INT,
            new_recovered INT,
            deaths_per_100_cases FLOAT,
            recovered_per_100_cases FLOAT,
            deaths_per_100_recovered FLOAT,
            no_of_countries INT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS usa_county_wise (
            uid INT,
            iso2 VARCHAR,
            iso3 VARCHAR,
            code3 INT,
            fips FLOAT,
            admin2 VARCHAR,
            province_state VARCHAR,
            country_region VARCHAR,
            lat FLOAT,
            long FLOAT,
            combined_key VARCHAR,
            date DATE,
            confirmed INT,
            deaths INT
        );
        """
    ]

    with engine.connect() as conn:
        for query in table_creation_queries:
            conn.execute(text(query))
    print("All tables are created.")


def load_data(engine):
    csv_files = {
        'country_wise_latest': 'data/country_wise_latest.csv',
        'worldometer_data': 'data/worldometer_data.csv',
        'covid_19_clean_complete': 'data/covid_19_clean_complete.csv',
        'full_grouped': 'data/full_grouped.csv',
        'day_wise': 'data/day_wise.csv',
        'usa_county_wise': 'data/usa_county_wise.csv'
    }

    for table_name, file_path in csv_files.items():
        print(f"Loading data into table '{table_name}' from '{file_path}'")
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("/", "_")

        try:
            df.to_sql(table_name, engine, if_exists='append', index=False)
            print(f"Data successfully loaded into '{table_name}'.")
        except Exception as e:
            print(f"Error loading data into table '{table_name}': {e}")


# Main execution
if __name__ == "__main__":
    DATABASE_URI = f'postgresql://{user}:{password}@{host}:{port}/{db_name}'
    engine = create_engine(DATABASE_URI)
    create_tables(engine)
    load_data(engine)
    print("Database setup and data loading completed.")