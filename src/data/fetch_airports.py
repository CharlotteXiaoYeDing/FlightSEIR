import argparse
import logging
import os

from Constants import ERROR_LOG_FILE_NAME, AIRPORTS_FILE_PREFIX
from CustomFlightData import CustomFlightData
from flight_converter import to_airport
import pandas as pd


def get_airport_by_iata(f, iata):
    print(iata)
    airport_details = f.get_airport_details(iata)
    return to_airport(airport_details)


def fetch_airports_by_country(f, airports_file_prefix, country):
    print("fetching the airports of: ", country)
    filename = "%s-%s.txt" % (airports_file_prefix, country)
    if not os.path.exists(filename):
        airports = []
        for airport in f.get_airports(country):
            if airport['iata']:
                airport_dict = get_airport_by_iata(f, airport['iata'])
                if airport_dict is not None:
                    airports.append(airport_dict)
            else:
                logging.warning("IATA not found for airport: %s", airport)
        print("writing airports to file: ", filename)
        df = pd.DataFrame(airports)
        df.to_csv(filename, header=False)
    else:
        logging.warning("airports file %s already exists: " % filename)


def fetch_airports(countries,
                   airports_file_prefix=AIRPORTS_FILE_PREFIX,
                   error_log_file_name=ERROR_LOG_FILE_NAME):
    logging.basicConfig(filename=error_log_file_name, level=logging.WARNING)
    f = CustomFlightData()
    if not countries:
        print("fetching countries")
        countries = [country['country'] for country in f.get_countries()]
    for country in countries:
        fetch_airports_by_country(f, airports_file_prefix, country)
    f.logout()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--countries', type=str, nargs='*', default=[])
    parser.add_argument('--airport_file_prefix', type=str, default=AIRPORTS_FILE_PREFIX)
    parser.add_argument('--error_log_file', type=str, default=ERROR_LOG_FILE_NAME)
    args = parser.parse_args()
    fetch_airports(args.countries, args.airport_file_prefix, args.error_log_file)

