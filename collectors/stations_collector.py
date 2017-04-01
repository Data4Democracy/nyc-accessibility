import os
import requests
from models.station_pulls import StationPulls
from db.postgresql_connector import PostgreSQLConnector


def collect_stations_data():
    url = 'http://www.nycaccessible.com/api/v1/stations/'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return {}


def store_stations_to_postgres(stations_data, postgres_session):
    for station in stations_data:
        new_row = StationPulls(station_id=station['id'],
                               name=station['name'],
                               lines=station['lines'],
                               has_machines=station['has_machines'],
                               is_accessible=station['is_accessible'],
                               elevator_count_words=station['elevator_count_words'],
                               outages=station['outages'],
                               accessible_note=station['accessible_note'])
        postgres_session.add(new_row)
    postgres_session.commit()


if __name__ == '__main__':

    engine_string = os.environ.get('PG_ENGINE_STRING')
    if not engine_string:
        print('Please set variable PG_ENGINE_STRING to valid PostgreSQL connection')
        exit(8)

    db_session = PostgreSQLConnector().connect(engine_string=engine_string)
    data = collect_stations_data()
    store_stations_to_postgres(data, db_session)