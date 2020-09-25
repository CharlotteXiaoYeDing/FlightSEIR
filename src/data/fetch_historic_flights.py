import argparse
import datetime
import logging
import os

import pandas as pd
from pandas.errors import EmptyDataError

from Constants import UNIQUE_FLIGHTS_FILE_PREFIX, \
    HISTORIC_FLIGHTS_FILE_PREFIX, FLIGHTS_ATTRIBUTE_NAMES
from CustomFlightData import CustomFlightData
from InfoFilter import InfoFilter
from flight_converter import to_flight, to_has_more
from utils import get_logger


def update_count_by_flight_status(flight, count_by_flight_status):
    status = flight['status']
    if status not in count_by_flight_status.keys():
        count_by_flight_status[status] = 0
    count_by_flight_status[status] += 1


def append_historic_flights(flight, historic_flights):
    if flight is not None:
        historic_flights.append(flight)


def is_departure_before_date(date, departure_date):
    date = datetime.datetime.strptime(date, '%Y%m%d')
    departure_date = datetime.datetime.strptime(departure_date, '%Y%m%d')
    return departure_date <= date


def is_departure_after_date(date, departure_date):
    date = datetime.datetime.strptime(date, '%Y%m%d')
    departure_date = datetime.datetime.strptime(departure_date, '%Y%m%d')
    return departure_date > date


def fetch_flight_history_by_flight_number(f, flight_number, date_start, count_by_flight_status):
    historic_flights = []
    has_more = True
    page = 1
    time_updated = int(pd.to_datetime('today').strftime('%s'))
    while has_more:
        response = f.get_historical_flight_number(flight_number, time_updated, page=page)
        if 'data' not in response:
            default_logger.warning("data not in response for flight number %s, page %d" % (flight_number, page))
            break
        has_more = to_has_more(response)
        page += 1
        for flight_response in response['data']:
            flight = to_flight(flight_response)
            if flight is not None:
                time_updated = flight['time_updated']
                departure_date = flight['departure_date']
                if is_departure_before_date(date_end, departure_date) and is_departure_after_date(date_start,
                                                                                                  departure_date):
                    historic_flights.append(flight)
                    update_count_by_flight_status(flight, count_by_flight_status)
                if is_departure_before_date(date_start, departure_date):
                    # default_logger.info("\t departure date: %s is before date start" % departure_date)
                    has_more = False
                    break
        if page > 10:
            break
    # default_logger.info("\t current count by flight status: %s" % count_by_flight_status)
    return historic_flights


def log_summary(flights_summary_logger, flight_number, new_flights):
    if not new_flights:
        return
    new_flights_df = pd.DataFrame(new_flights)
    groups = new_flights_df.groupby(['departure_airport', 'arrival_airport'])
    for keys, frame in groups:
        departure_dates = frame['departure_date'].to_list()
        flights_summary_logger.info("%s,%s,%s,%s,%d,%s,%s" % (
            pd.to_datetime('today'), flight_number, keys[0], keys[1], len(frame.index), departure_dates[-1],
            departure_dates[0]))


def get_start_date_by_flight_number(existing_summary, flight_number):
    if existing_summary is not None:
        summary = existing_summary[existing_summary[1] == flight_number]
        if not summary.empty:
            return str(sorted(summary[6].to_list(), reverse=True)[0])
    return '20200101'


def fetch_flight_history_by_country(f, unique_flights_file_prefix, historic_flights_file_prefix, country):
    default_logger.info("fetching flight history for country: %s" % country)
    unique_flights_filename = "%s-%s.txt" % (unique_flights_file_prefix, country)
    historic_flights_file_name = "%s-%s.txt" % (historic_flights_file_prefix, country)
    summary_file_name = "%s_summary-%s.txt" % (historic_flights_file_prefix, country)
    existing_summary = pd.read_csv(summary_file_name, usecols=[1, 6], header=None) if os.path.exists(
        summary_file_name) else None
    flights_summary_logger = get_flights_summary_logger(summary_file_name, country)
    if os.path.exists(unique_flights_filename):
        try:
            unique_flights = pd.read_csv(unique_flights_filename).iloc[:, 0].to_list()
            historic_flights = []
            count_by_flight_status = {}
            for f_idx, flight_number in enumerate(unique_flights):
                if f_idx % 100 == 0:
                    default_logger.info("loading %s, %d/%d" % (flight_number, f_idx, len(unique_flights)))
                date_start = get_start_date_by_flight_number(existing_summary, flight_number)
                new_flights = fetch_flight_history_by_flight_number(f, flight_number, date_start,
                                                                    count_by_flight_status)
                new_df = pd.DataFrame(new_flights, columns=FLIGHTS_ATTRIBUTE_NAMES)
                new_df.to_csv(historic_flights_file_name, mode='a', header=False, index=False)
                log_summary(flights_summary_logger, flight_number, new_flights)
                historic_flights.extend(new_flights)
        except EmptyDataError:
            default_logger.exception("file %s is empty" % unique_flights_filename)
    else:
        default_logger.warning("unique flights file %s does not exist: " % unique_flights_filename)


def get_flights_summary_logger(file_name, country):
    summary_logger = logging.getLogger('summary_logger_' + country)
    handler = logging.FileHandler(file_name, mode='a')
    handler.addFilter(InfoFilter())
    summary_logger.addHandler(handler)
    summary_logger.setLevel(logging.INFO)
    return summary_logger


def fetch_flight_history(countries,
                         unique_flights_file_prefix=UNIQUE_FLIGHTS_FILE_PREFIX,
                         historic_flights_file_prefix=HISTORIC_FLIGHTS_FILE_PREFIX):
    f = CustomFlightData()
    # f.login("username", "password")
    if not countries:
        default_logger.info("fetching countries")
        countries = [country['country'] for country in f.get_countries()]
    for country in countries:
        fetch_flight_history_by_country(f, unique_flights_file_prefix, historic_flights_file_prefix, country)
    f.logout()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--countries', type=str, nargs='*', default=[])
    parser.add_argument('--date_start', type=str)
    parser.add_argument('--date_end', type=str)
    parser.add_argument('--unique_flights_file_prefix', type=str, default=UNIQUE_FLIGHTS_FILE_PREFIX)
    parser.add_argument('--historic_flights_file_prefix', type=str, default=HISTORIC_FLIGHTS_FILE_PREFIX)
    parser.add_argument('--info_log_file', type=str, default='logs/h_info.log')
    parser.add_argument('--error_log_file', type=str, default='logs/h_error.log')
    args = parser.parse_args()

    default_logger = get_logger(args.info_log_file, args.error_log_file)
    date_end = datetime.date.today().strftime('%Y%m%d') if args.date_end is None else args.date_end

    fetch_flight_history(args.countries, args.unique_flights_file_prefix, args.historic_flights_file_prefix)
