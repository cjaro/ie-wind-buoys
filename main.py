import csv
import numpy as np
import pandas as pd
import re
import requests

from bs4 import BeautifulSoup
from geopy.distance import geodesic
from scipy import spatial


def split_buoy_string(input_string):
    pattern = r"(\w+)\s*:\s*([\d.]+°[NS])\s*([\d.]+°[EW])"
    matches = re.findall(pattern, input_string)

    if matches:
        buoy_name, latitude, longitude = matches[0]
        print(buoy_name, latitude, longitude)
        return buoy_name, latitude, longitude
    else:
        print("No match found.")


def save_buoy_names():
    url = "https://www.marine.ie/site-area/data-services/real-time-observations/irish-weather-buoy-network-imos"
    res = requests.get(url)
    html = res.content.decode("utf-8")

    soup = BeautifulSoup(html, features="html.parser")

    table = soup.find("table", attrs={"class": None})

    headers = ["Buoy Name", "Latitude", "Longitude"]

    with open("data/buoys-lat-long.csv", "w") as f:
        wr = csv.writer(f)

        wr.writerow(headers)

        for td in table.select("tr td"):
            print("td:", td.text)

            wr.writerow(split_buoy_string(td.text))


def get_html_table():
    url = "https://webapps.marine.ie/observations/IWPData/default.aspx?ProjectID=2"
    res = requests.get(url)
    html = res.content.decode("utf-8")
    soup = BeautifulSoup(html, features="html.parser")
    table = soup.select_one("table.DataGrid")
    headers = []

    for td in table.select("tr.DataGridHeader td"):
        headers.append(td.text)

    with open("data/weather-buoys-data.csv", "w") as f:
        wr = csv.writer(f)
        wr.writerow(headers)
        wr.writerows(
            [
                [td.text.strip() for td in row.find_all("td")]
                for row in table.select("tr + tr")
            ]
        )


def find_buoy_name_in_csv(given_latitude, given_longitude):
    df = pd.read_csv("data/buoys-lat-long.csv")
    given_latitude = f"{abs(float(given_latitude)):.4f}"
    given_longitude = f"{abs(float(given_longitude)):.4f}"
    df["Latitude"] = df["Latitude"].astype(str)
    df["Longitude"] = df["Longitude"].astype(str)

    matching_row = df[(df["Latitude"] == f"{given_latitude}°N") & (df["Longitude"] == f"{given_longitude}°W")]

    if not matching_row.empty:
        buoy_name = matching_row.iloc[0]["Buoy Name"]
        print(f"The Buoy Name for coordinates {given_latitude},{given_longitude} is {buoy_name}")
        return buoy_name
    else:
        print("No matching coordinates found.")


def find_closest_buoy(coords):
    buoys = [
        ("53.1266", "-11.2000"),
        ("53.4800", "-05.4250"),
        ("51.2166", "-10.5500"),
        ("55.0000", "-10.0000"),
        ("51.6900", "-06.7040"),
        ("53.0605", "-15.9300"),
    ]

    tree = spatial.KDTree(buoys)
    buoyindex = tree.query([coords])
    index_convert = buoyindex[1].astype(np.int64)
    buoy_coords = index_convert[0].item()
    closest_buoy = buoys[buoy_coords]
    print(f"closest buoy coordinates: {closest_buoy}")

    distance_between = geodesic(coords, closest_buoy).meters / 1000
    closest_buoy_name = find_buoy_name_in_csv(closest_buoy[0], closest_buoy[1])

    print(f"Buoy '{closest_buoy_name}' is the closest buoy to the query coordinates at {distance_between} kilometers away.")

    return closest_buoy_name


def get_wind_speed(buoy_name):
    df = pd.read_csv("data/weather-buoys-data.csv")
    wind_speed = df.loc[df["Site"] == "Wind Speed (kn)", buoy_name].values[0]
    data_date = df.loc[df["Site"] == "Date", buoy_name].values[0]
    print(f"The corresponding Wind Speed for '{buoy_name}' at {data_date} is {wind_speed} knots")


if __name__ == "__main__":
    # uncomment to get top of hour updates to data table
    # get_html_table()
    # uncomment and run once to get CSV file, then comment out
    # save_buoy_names()
    test_coords = ("55.2151", "-8.1539")
    print(f"Looking for nearest buoy to {test_coords}")

    try:
        buoy = find_closest_buoy(test_coords)
        get_wind_speed(buoy)
    except KeyError as ke:
        print("Error:", ke)
