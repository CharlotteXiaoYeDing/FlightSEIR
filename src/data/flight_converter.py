import datetime
import logging


def to_airport(airport_details):
    try:
        airport_dict = {
            'iata': airport_details['code']['iata'],
            'latitude': airport_details['position']['latitude'],
            'longitude': airport_details['position']['longitude'],
            'country': airport_details['position']['country']['name'],
            'city': airport_details['position']['region']['city']
        }
        return airport_dict
    except (KeyError, TypeError):
        logging.error("Error parsing airport %s", airport_details)
        return None


def to_flight_number(departure):
    try:
        flight_number = departure['flight']['identification']['number']['default']
        return flight_number
    except (KeyError, TypeError):
        logging.error("Error parsing flight_number %s", departure)
        return None


def to_has_more(history_by_flight_number):
    try:
        has_more = history_by_flight_number['page']['more']
        return has_more
    except (KeyError, TypeError):
        logging.error("Error parsing has_more %s", history_by_flight_number)
        return False


def get_departure_date(flight):
    if flight['time']['real']["departure"] != 'None':
        date = flight['time']['real']['departure_date']
    else:
        date = flight['time']['scheduled']['departure_date']
    datetime.datetime.strptime(date, '%Y%m%d')
    return date


def to_flight(flight):
    try:
        flight_dict = {
            'flight_number': flight['identification']['number']['default'],
            'status': flight['status']['generic']['status']['text'],
            'departure_airport': flight['airport']['origin']['code']['iata'],
            'arrival_airport': flight['airport']['destination']['code']['iata'],
            'departure_date': get_departure_date(flight),
            'time_updated': flight['time']['other']['updated']
        }
        return flight_dict
    except (KeyError, TypeError, ValueError):
        logging.error("Error parsing flight %s", flight)
        return None
