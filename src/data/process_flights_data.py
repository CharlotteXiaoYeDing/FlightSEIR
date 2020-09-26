import pandas as pd
import argparse

NAME_CONVERSION = {"United States": "US",
                   "Trinidad And Tobago": "Trinidad and Tobago",
                   "Saint Pierre And Miquelon": "Saint Pierre and Miquelon",
                   "Antigua And Barbuda": "Antigua and Barbuda",
                   "South Korea": "Korea, South",
                   "Taiwan": "Taiwan*",
                   "Saint Vincent And The Grenadines": "Saint Vincent and the Grenadines",
                   "Saint Kitts And Nevis": "Saint Kitts and Nevis",
                   "Turks And Caicos Islands": "Turks and Caicos Islands",
                   "Sao Tome And Principe": "Sao Tome and Principe"}

BLACKLIST = []

use_country = False


def assert_country_in_flight_data_has_corresponding_entry_in_covid_data(df_flights, df_covid):
    for destination in pd.concat([df_flights['From'], df_flights['To']]).unique():
        if destination not in df_covid['Province/State'].unique() and destination not in df_covid['Country/Region'].unique():
            print("Not found:", destination)


# Remove country/regions in the blacklist from flights dataset
def remove_blacklist_countries(df_flights, initial_flight_count):
    for destination in pd.concat([df_flights['From'], df_flights['To']]).unique():
        if destination in BLACKLIST:
            df_flights = df_flights[df_flights['From'] != destination]
            df_flights = df_flights[df_flights['To'] != destination]
    print("removed # records", initial_flight_count - df_flights.shape[0])
    return df_flights


# Align country/region names in flights and covid dataset
def convert_country_region_names(df_flights):
    for key in NAME_CONVERSION.keys():
        df_flights = df_flights.replace({key: NAME_CONVERSION[key]})
    return df_flights


def process_flight_data():
    filename = "edge_list_all-Canada.txt" if use_country else "edge_list-Canada.txt"
    processed_filename = "edge_list_processed_all-Canada.txt" if use_country else "edge_list_processed-Canada.txt"
    df_flights_v3 = pd.read_csv("datasets/edge_lists/%s" % filename,
                                names=['date', 'From', 'To', 'number of flights'])
    df_flights_v3['date'] = pd.to_datetime(df_flights_v3['date'])
    df_covid = pd.read_csv("datasets/covid_SIR.csv")
    df_covid['date'] = pd.to_datetime(df_covid['date'])

    v3_initial_record_count = df_flights_v3.shape[0]
    print("v3 initial # records", v3_initial_record_count)
    print("v3 initial # flights", df_flights_v3['number of flights'].sum())

    df_flights_v3 = remove_blacklist_countries(df_flights_v3, v3_initial_record_count)
    df_flights_v3 = convert_country_region_names(df_flights_v3)
    print("v3 # records after name conversion and blacklist", df_flights_v3.shape[0])

    assert_country_in_flight_data_has_corresponding_entry_in_covid_data(df_flights_v3, df_covid)

    print("v3 # records before write to file", df_flights_v3.shape[0])
    print("v3 # flights before write to file", df_flights_v3['number of flights'].sum())
    df_flights_v3.to_csv("datasets/edge_lists/%s" % processed_filename, index=False, header=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--use_country', default=False, action='store_true')
    args = parser.parse_args()
    use_country = args.use_country
    print(use_country)
    process_flight_data()
