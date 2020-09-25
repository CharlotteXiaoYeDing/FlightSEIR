from pyflightdata.common_fr24 import FR24


class CustomFR24(FR24):

    def __init__(self):
        super(CustomFR24, self).__init__()

    def get_airport_departures_total_page(self, url):
        return self.get_raw_data_json(url, 'result.response.airport.pluginData.schedule.departures.page.total')[0]

    def get_airport_arrivals_total_page(self, url):
        return self.get_raw_data_json(url, 'result.response.airport.pluginData.schedule.arrivals.page.total')[0]

    def get_data(self, url, by_tail=False):
        response = self.get_raw_data_json(url, 'result.response')
        response = self.filter_and_get_data(response) or []
        return response

