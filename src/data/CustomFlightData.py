import datetime

from pyflightdata import FlightData
from pyflightdata.common_fr24 import AIRPORT_DATA_BASE, AIRPORT_DATA_BASE_EARLIER

from CustomFR24 import CustomFR24


class CustomFlightData(FlightData):

    _fr24 = CustomFR24()
    _FLT_BASE = 'https://api.flightradar24.com/common/v1/flight/list.json?query={0}&fetchBy=flight&filterBy=historic&page={2}&limit={3}&token={1}&timestamp={4}'

    def __init__(self, email=None, password=None):
        super(CustomFlightData, self).__init__(email, password)

    def get_airport_details(self, iata, page=1, limit=100):
        url = AIRPORT_DATA_BASE.format(iata, str(self.AUTH_TOKEN), page, limit)
        details = self._fr24.get_airport_details(url)
        return details

    def get_airport_departures_total_page(self, iata, page=1, limit=100):
        date = datetime.date.today()
        url = AIRPORT_DATA_BASE_EARLIER.format(iata, str(self.AUTH_TOKEN), page, limit, int(date.strftime('%s')))
        return self._fr24.get_airport_departures_total_page(url)

    def get_airport_arrivals_total_page(self, iata, page=1, limit=100):
        date = datetime.date.today()
        url = AIRPORT_DATA_BASE_EARLIER.format(iata, str(self.AUTH_TOKEN), page, limit, int(date.strftime('%s')))
        return self._fr24.get_airport_arrivals_total_page(url)

    def get_airport_departures(self, iata, page=1, limit=100, earlier_data=False):
        date = datetime.date.today()
        url = AIRPORT_DATA_BASE_EARLIER.format(iata, str(self.AUTH_TOKEN), page, limit, int(date.strftime('%s')))
        return self._fr24.get_airport_departures(url)

    def get_airport_arrivals(self, iata, page=1, limit=100, earlier_data=False):
        date = datetime.date.today()
        url = AIRPORT_DATA_BASE_EARLIER.format(iata, str(self.AUTH_TOKEN), page, limit, int(date.strftime('%s')))
        return self._fr24.get_airport_arrivals(url)

    def get_historical_flight_number(self, flight_number, last_updated, page=1, limit=100):
        url = self._FLT_BASE.format(flight_number, str(self.AUTH_TOKEN), page, limit, last_updated)
        return self._fr24.get_data(url)
