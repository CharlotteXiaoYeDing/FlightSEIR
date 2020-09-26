import argparse
import datetime
import logging

import pandas as pd

from fetch_historic_flights import update_count_by_flight_status
from Constants import AIRPORTS_FILE_PREFIX, HISTORIC_FLIGHTS_FILE_PREFIX, AIRPORT_ATTRIBUTE_NAMES, \
    FLIGHTS_ATTRIBUTE_NAMES, COUNTRIES_FILE_NAME
from InfoFilter import InfoFilter
from utils import get_logger

use_country = False


def to_node_id(airport):
    node = airports.loc[(airports['iata'] == airport).idxmax()]
    return node.city if not use_country and node.country == 'Canada' else node.country


def append_flight_to_network(flight):
    if flight['status'] == 'landed' or flight['status'] == 'diverted':
        if flight['departure_date'] not in flight_network_by_date.keys():
            flight_network_by_date[flight['departure_date']] = {}
        adj = flight_network_by_date[flight['departure_date']]
        srcId = to_node_id(flight['departure_airport'])
        desId = to_node_id(flight['arrival_airport'])
        edge = (srcId, desId)
        if edge not in adj:
            adj[edge] = 0
        adj[edge] = adj[edge] + 1


def build_flight_network():
    total_flights = len(historic_flights.index)
    for idx, flight in historic_flights.iterrows():
        append_flight_to_network(flight)
        update_count_by_flight_status(flight, count_by_flight_status)
        if idx % 1000 == 0:
            default_logger.info("loading %s, %d/%d" % (flight['flight_number'], idx, total_flights))


def write_flight_network_to_file():
    edge_list = []
    for date in sorted(flight_network_by_date.keys()):
        formatted_date = datetime.datetime.strptime(str(date), '%Y%m%d')
        adj = flight_network_by_date[date]
        for edge in adj.keys():
            edge_list.append([formatted_date.strftime('%Y-%m-%d'), edge[0], edge[1], adj[edge]])
    edge_list = pd.DataFrame(edge_list)
    if use_country:
        edge_list.to_csv("datasets/edge_lists/edge_list_all-%s.txt" % args.country, header=False, index=False)
    else:
        edge_list.to_csv("datasets/edge_lists/edge_list-%s.txt" % args.country, header=False, index=False)


def flight_by_status_logger(unique_flights_log_file_name):
    unique_flights_logger = logging.getLogger('flight_by_status_logger')
    handler = logging.FileHandler(unique_flights_log_file_name, mode='a')
    handler.addFilter(InfoFilter())
    unique_flights_logger.addHandler(handler)
    unique_flights_logger.setLevel(logging.INFO)
    return unique_flights_logger


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--use_country', default=False, action='store_true')
    parser.add_argument('--country', type=str, default='Canada')
    parser.add_argument('--info_log_file', type=str, default='logs/e_info.log')
    parser.add_argument('--error_log_file', type=str, default='logs/e_error.log')
    args = parser.parse_args()
    use_country = args.use_country
    print(use_country)

    default_logger = get_logger(args.info_log_file, args.error_log_file)
    flight_by_status_logger = flight_by_status_logger("datasets/edge_lists/flight_by_status.txt")

    # read all airports
    countries = pd.read_csv(COUNTRIES_FILE_NAME, header=None)
    airports = []
    for c in countries[0]:
        airport_file_name = "%s-%s.txt" % (AIRPORTS_FILE_PREFIX, c)
        airport = pd.read_csv(airport_file_name, names=AIRPORT_ATTRIBUTE_NAMES)
        airports.append(airport)
    airports = pd.concat(airports, axis=0, ignore_index=True)
    historic_flights_file_name = "%s-%s.txt" % (HISTORIC_FLIGHTS_FILE_PREFIX, args.country)
    historic_flights = pd.read_csv(historic_flights_file_name, names=FLIGHTS_ATTRIBUTE_NAMES)
    flight_network_by_date = {}
    count_by_flight_status = {}
    build_flight_network()
    flight_by_status_logger.info(count_by_flight_status)
    write_flight_network_to_file()
