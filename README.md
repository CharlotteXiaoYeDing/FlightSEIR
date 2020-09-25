# FlightSEIR

A placeholder repo for paper `Incorporating Dynamic Flight Network in SEIR to Model Mobility between Populations`. Code to reproduce the experiments in the paper will be available soon.

# Prerequisites

This project leverages [pyflightdata](https://pyflightdata.readthedocs.io/en/latest/pyflightdata.html) API, a wrapper around [flightradar24](https://www.flightradar24.com/), to fetch flights data.

# Data Collection

1. Fetch all countries: `python src/data/fetch_countries.py`
2. Fetch all airports of a given country: `python src/data/fetch_airports.py --countries Canada`
3. Collect a list of flights departing and arriving a the given country: `python src/data/fetch_unique_flights.py --countries Canada`
Note: due to limitations of `pyflightdata`, `fetch_unique_flights.py` can only fetch live flights. In order to obtain a comprehensive list of flights to and from Canada, one must run this script repeatly over a long period of time.
4. Fetches the historic flights of a given country: `python src/data/fetch_historic_flights.py --countries Canada`
Note: by default, `pyflightdata` only returns historic data for the past 7 days. In order to obtain 90/360 days of past flights, one must subscribe to the Silver/Gold plan on flightradar24 and login programmatically with `f.login("username", "password")`.