import logging

from Constants import ERROR_LOG_FILE_NAME, COUNTRIES_FILE_NAME
from CustomFlightData import CustomFlightData
import pandas as pd


def write_countries():
    logging.basicConfig(filename=ERROR_LOG_FILE_NAME, level=logging.WARNING)
    f = CustomFlightData()
    countries = [country['country'] for country in f.get_countries()]
    df = pd.DataFrame(countries)
    df.to_csv(COUNTRIES_FILE_NAME, header=False, index=False)


if __name__ == '__main__':
    write_countries()
