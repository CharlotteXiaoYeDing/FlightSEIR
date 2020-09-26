# FlightSEIR

A placeholder repo for paper `Incorporating Dynamic Flight Network in SEIR to Model Mobility between Populations`. Code to reproduce the experiments in the paper will be available soon.

# Prerequisites

This project leverages [pyflightdata](https://pyflightdata.readthedocs.io/en/latest/pyflightdata.html) API, a wrapper around [flightradar24](https://www.flightradar24.com/), to fetch flights data.

# Data Collection

1. Fetch all countries: `python src/data/fetch_countries.py`
2. Fetch all airports of all country: `python src/data/fetch_airports.py`
3. Collect a list of flights departing and arriving a the given country: `python src/data/fetch_unique_flights.py --countries Canada`
Note: due to limitations of `pyflightdata`, `fetch_unique_flights.py` can only fetch live flights. In order to obtain a comprehensive list of flights to and from Canada, one must run this script repeatly over a long period of time.
4. Fetches the historic flights of a given country: `python src/data/fetch_historic_flights.py --countries Canada`
Note: by default, `pyflightdata` only returns historic data for the past 7 days. In order to obtain 90/360 days of past flights, one must subscribe to the Silver/Gold plan on flightradar24 and login programmatically with `f.login("username", "password")`.
5. Download `owid-covid-data.csv` from [Total COVID-19 Tests Performed by Country](https://data.humdata.org/dataset/c87c4508-9caf-4959-bf06-6ab4855d84c6) and place it under `datasets` folder.
6. Download `can_covid19.csv` from [Coronavirus disease (COVID-19): Outbreak update](https://www.canada.ca/en/public-health/services/diseases/2019-novel-coronavirus-infection.html#a1) and place it under `datasets` folder.
7. Download `reported_flights_stats.csv` from [Domestic and international Itinerant movements](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2310000801) and place it under `datasets` folder.
8. Download `canada_population_by_prov.csv` and place it under `datasets` folder.

# Data Processing

1. Construct flight network edge list for Canada: `python src/data/construct_edge_list.py --country=Canada` followed by `python src/data/process_flights_data.py`
2. Construct flight network edge list for provinces: `python src/data/construct_edge_list.py --use_country --country=Canada` followed by `python src/data/process_flights_data.py --use_country`
3. To process test positive rates for the world, run `src/data/process_positive_rate_world.ipynb` to produce `test-rate-processed.csv`
4. To process test positive rates for provinces, run `src/data/process_positive_rate_can.ipynb` to produce `can_covid19_processed.csv`
5. To generate interpolated test positive rates, run `src/data/interpolate_positive_rate.ipynb` to produce `interpolated_positive_rates.csv`
6. To generate data used for experiments, run `src/data/flight-seir-Canada.ipynb`. The generated data will be saved in the `states` folder.

# Experiments

Run `src/model/early_time_prediction.ipynb` or `src/model/reopen_simulation.ipynb`.