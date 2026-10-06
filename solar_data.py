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


def get_hamqsl_data():
    """ the function fetches live HF propagation data from HAMQSL in XML format and returns it as a dictionary. """
    
    url = "https://www.hamqsl.com/solarxml.php"
    response = requests.get(url)
    response.raise_for_status()

    root = ET.fromstring(response.text)

    data = {
        "solar_flux": root.findtext(".//solarflux"),
        "sunspots": root.findtext(".//sunspots"),
        "a_index": root.findtext(".//aindex"),
        "k_index": root.findtext(".//kindex"),
        "xray": root.findtext(".//xray"),
        "muf_us": root.findtext(".//muf"),
        "muf_au": root.findtext(".//mufau"),
        "updated": root.findtext(".//updated")
    }

    return data

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
            tk.Label(self.master, text=f"{key.replace('_', ' ').title()}:").grid(row=row, column=0, sticky="w")
            tk.Label(self.master, text=value).grid(row=row, column=1, sticky="w")
            row += 1    



if __name__ == "__main__":
    
    info = get_hamqsl_data()
    root = tk.Tk()
    root.geometry("380x180")  # Set the window size
    app = display(root, info)
    root.mainloop()
