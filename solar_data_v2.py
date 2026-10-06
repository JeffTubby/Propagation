# Solar Data Viewer using Tkinter and online XML data
# Displays current solar-terrestrial data fetched from HAMQSL.
# Author: Jeff VK5IU
# Version: 2.0
# Last Updated: 03/10/2026


import requests
import xml.etree.ElementTree as ET
import tkinter as tk
import webbrowser

from tkinter import *

from urllib.request import urlopen

# URL for the solar-terrestrial XML data from HAMQSL.
# URL: The URL for fetching the solar-terrestrial XML data.
URL = "https://www.hamqsl.com/solarxml.php"

def fetch_solar_data():
    """Fetch solar-terrestrial data from HAMQSL and return it as a structured dictionary."""
    # Send a GET request to the URL and parse the XML response.
    # Fetch the XML data from the URL.
    # Send a GET request to the URL and parse the XML response.
    # Raise an exception if the request was unsuccessful.
    # Fetch the XML data from the URL and parse it into an ElementTree object.
    # Send a GET request to the URL and parse the XML response.
    # Send a GET request to the URL and parse the XML response into an ElementTree object.
    # Perform the HTTP GET request to fetch the XML data.
    # Perform the HTTP GET request to fetch the XML data from the URL.
    # Fetch the XML data from the URL and parse it into an ElementTree object.
    # Perform the HTTP GET request to fetch the XML data from the URL and parse it into an ElementTree object.
    # Perform the HTTP GET request to fetch the XML data from the URL and parse it into an ElementTree object.
    # Perform the HTTP GET request to fetch the XML data from the URL and parse it into an ElementTree object.

    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    solar_data = root.find("solardata")
    if solar_data is None:
        raise ValueError("Solar data response is missing the solardata element")

    solar = {}
    for element in solar_data:
        if element.tag == "calculatedconditions":
            solar[element.tag] = [
                {
                    **band.attrib,
                    "value": (band.text or "").strip(),
                }
                for band in element.findall("band")
            ]
        elif element.tag == "calculatedvhfconditions":
            solar[element.tag] = [
                {
                    **phenomenon.attrib,
                    "value": (phenomenon.text or "").strip(),
                }
                for phenomenon in element.findall("phenomenon")
            ]
        else:
            solar[element.tag] = (element.text or "").strip()

    return {"solardata": [solar]}

def print_solar_data(data):
    solar = data["solardata"][0]

    print("Solar Data")
    print("-----------")
    print(f"Source: {solar.get('source')}")
    print(f"Updated: {solar.get('updated')}")
    print(f"Solar Flux: {solar.get('solarflux')}")
    print(f"A-index: {solar.get('aindex')}")
    print(f"K-index: {solar.get('kindex')}")
    print(f"K-index NT: {solar.get('kindexnt')}")
    print(f"X-ray: {solar.get('xray')}")
    print(f"Sunspots: {solar.get('sunspots')}")
    print(f"Helium Line: {solar.get('heliumline')}")
    print(f"Proton Flux: {solar.get('protonflux')}")
    print(f"Electron Flux: {solar.get('electonflux')}")
    print(f"Aurora: {solar.get('aurora')}")
    print(f"Normalization: {solar.get('normalization')}")
    print(f"Latitude Degree: {solar.get('latdegree')}")
    print(f"Solar Wind: {solar.get('solarwind')}")
    print(f"Magnetic Field: {solar.get('magneticfield')}")
    print()

    print("Calculated HF Conditions")
    print("------------------------")
    for band in solar.get("calculatedconditions", []):
        print(f"{band['name']} ({band['time']}): {band['value']}")

    print()

    print("Calculated VHF Conditions")
    print("-------------------------")
    for ph in solar.get("calculatedvhfconditions", []):
        print(f"{ph['name']} ({ph['location']}): {ph['value']}")

    print()

    print("Other Data")
    print("----------")
    print(f"Geomagnetic Field: {solar.get('geomagfield')}")
    print(f"Signal Noise: {solar.get('signalnoise')}")
    print(f"foF2: {solar.get('fof2')}")
    print(f"MUF Factor: {solar.get('muffactor')}")
    print(f"MUF: {solar.get('muf')}")

class display:
    """Class to display live HF propagation data in a Tkinter window."""
    
    def __init__(self, master, info):
        self.master = master
        self.info = info
        self.create_widgets()

    def create_widgets(self):
        self.master.title("Live HF Propagation Data (HAMQSL)")

        row = 0
        for key, value in self.info.items():
            label = {
                "calculatedconditions": "Calculated HF Conditions:",
                "calculatedvhfconditions": "Calculated VHF Conditions:",
            }.get(key, f"{key.replace('_', ' ').title()}:")
            tk.Label(self.master, text=label).grid(row=row, column=0, sticky="nw")

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        name = item.get("name", "")
                        qualifier = item.get("time", item.get("location", ""))
                        detail = item.get("value", "")
                        text = f"{name} ({qualifier}): {detail}".strip()
                    else:
                        text = str(item)
                    tk.Label(self.master, text=text).grid(row=row, column=1, sticky="w")
                    row += 1
                if not value:
                    row += 1
            else:
                tk.Label(self.master, text=value).grid(row=row, column=1, sticky="w")
                row += 1



def main():
    try:
        data = fetch_solar_data()
        # print the fetched solar data for debugging purposes
        #print_solar_data(data)
    except Exception as e:
        print("Error fetching solar data:", e)

    info = fetch_solar_data().get("solardata", [{}])[0]  # Get the first solardata entry
    root = tk.Tk()
    root.geometry("450x750")  # Set the window size
    app = display(root, info)
    root.mainloop()


if __name__ == "__main__":
    main()
