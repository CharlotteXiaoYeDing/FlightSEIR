import argparse
import logging
import os

import pandas as pd

from Constants import ERROR_LOG_FILE_NAME, AIRPORTS_FILE_PREFIX, UNIQUE_FLIGHTS_FILE_PREFIX, \
    AIRPORT_ATTRIBUTE_NAMES, INFO_LOG_FILE_NAME, UNIQUE_FLIGHTS_LOG_FLIE_NAME
from CustomFlightData import CustomFlightData
from InfoFilter import InfoFilter
from flight_converter import to_flight_number
from utils import get_logger


def get_unique_flights_logger(unique_flights_log_file_name):
    unique_flights_logger = logging.getLogger('unique_flights_logger')
    handler = logging.FileHandler(unique_flights_log_file_name, mode='a')
    handler.addFilter(InfoFilter())
    unique_flights_logger.addHandler(handler)
    unique_flights_logger.setLevel(logging.INFO)
    return unique_flights_logger


def fetch_unique_flights(countries,
                         unique_flights_file_prefix=UNIQUE_FLIGHTS_FILE_PREFIX,
                         airports_file_prefix=AIRPORTS_FILE_PREFIX):
    f = CustomFlightData()
    if not countries:
        default_logger.info("fetching countries")
        countries = [country['country'] for country in f.get_countries()]
    for country in countries:
        fetch_unique_flights_by_country(f, airports_file_prefix, unique_flights_file_prefix, country)
    f.logout()


def fetch_unique_flights_by_country(f, airports_file_prefix, unique_flights_file_prefix, country):
    default_logger.info("fetching the unique flights of: %s" % country)
    airports_file_name = "%s-%s.txt" % (airports_file_prefix, country)
    airports_file_name = airports_file_name
    unique_flights_filename = "%s-%s.txt" % (unique_flights_file_prefix, country)
    if os.path.exists(airports_file_name):
        default_logger.info("loading airports")
        airports = pd.read_csv(airports_file_name, names=AIRPORT_ATTRIBUTE_NAMES)
        default_logger.info("total airports: %d" % len(airports))
        new_flights = get_new_flights(f, airports)
        existing_flights_df = get_existing_flights(unique_flights_filename)
        flights_added, total_flights = append_new_flights(existing_flights_df, new_flights, unique_flights_filename)
        unique_flights_logger.info("%s, %s, %d, %d" % (pd.to_datetime('today'), country, flights_added, total_flights))
    else:
        default_logger.warning("airports file %s does not exist: " % airports_file_name)


def get_new_flights(f, airports):
    num_airports = len(airports)
    new_flights = set()
    for airport_idx, airport in enumerate(airports['iata']):
        if airport_idx % 100 == 0:
            default_logger.info("loading %s, %d/%d" % (airport, airport_idx, num_airports))
        fetch_unique_flights_by_airport(f, airport, new_flights)
    return new_flights


def fetch_unique_flights_by_airport(f, airport, new_flights):
    total_page = f.get_airport_departures_total_page(airport)
    for page in range(1, total_page + 1):
        for flight in f.get_airport_departures(airport, page=page, earlier_data=True):
            append_flight(flight, new_flights)

    total_page = f.get_airport_arrivals_total_page(airport)
    for page in range(1, total_page + 1):
        for flight in f.get_airport_arrivals(airport, page=page, earlier_data=True):
            append_flight(flight, new_flights)


def append_flight(flight, new_flights):
    flight_number = to_flight_number(flight)
    if flight_number is not None:
        new_flights.add(flight_number)


def get_existing_flights(unique_flights_filename):
    existing_flights_df = pd.DataFrame(columns=['flight', 'added'])
    if os.path.exists(unique_flights_filename):
        existing_flights_df = pd.read_csv(unique_flights_filename, names=['flight', 'added'])
        existing_flights_df.added = existing_flights_df.added.fillna(pd.to_datetime('today'))
    return existing_flights_df


def append_new_flights(existing_flights_df, new_flights, unique_flights_filename):
    default_logger.info("total new flights: %d" % len(new_flights))
    existing_flights = set(existing_flights_df['flight'].tolist())
    default_logger.info("total existing flights: %d" % len(existing_flights))
    flights_to_add = new_flights.difference(existing_flights)
    default_logger.info("total unique new flights: %d" % len(flights_to_add))
    flights_to_add_df = pd.DataFrame(flights_to_add, columns=['flight'])
    flights_to_add_df['added'] = pd.to_datetime('today')
    unique_flights_df = existing_flights_df.append(flights_to_add_df, ignore_index=True)
    unique_flights_df.to_csv(unique_flights_filename, header=False, index=False)
    return len(flights_to_add), len(unique_flights_df.index)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--countries', type=str, nargs='*', default=[])
    parser.add_argument('--unique_flights_file_prefix', type=str, default=UNIQUE_FLIGHTS_FILE_PREFIX)
    parser.add_argument('--airport_file_prefix', type=str, default=AIRPORTS_FILE_PREFIX)
    parser.add_argument('--error_log_file', type=str, default=ERROR_LOG_FILE_NAME)
    parser.add_argument('--info_log_file', type=str, default=INFO_LOG_FILE_NAME)
    parser.add_argument('--unique_flights_log_file', type=str, default=UNIQUE_FLIGHTS_LOG_FLIE_NAME)
    args = parser.parse_args()

    default_logger = get_logger(args.info_log_file, args.error_log_file)
    unique_flights_logger = get_unique_flights_logger(args.unique_flights_log_file)

    fetch_unique_flights(args.countries, args.unique_flights_file_prefix, args.airport_file_prefix)
