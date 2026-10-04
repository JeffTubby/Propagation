# Band Conditions Display using Tkinter
# Displays real-time band conditions using images from HAMQSL and other sources.
# Author: Jeff Tubbenhauer VK5IU
# Date: 04/10/2026

import tkinter as tk
from tkinter import *
import webbrowser
import ssl
from urllib.request import urlopen
from io import BytesIO
from PIL import Image, ImageTk
   
# Constants for URLs and link titles

HREF_URL = "https://www.hamqsl.com/solar.html"
IMAGE_URL_1 = (
    "https://www.hamqsl.com/solarn0nbh.php"
)
LINK_TITLE = "Click to add Solar-Terrestrial Data to your website!"
IMAGE_URL_2 = (
    "https://www.hamqsl.com/solargraph.php"
)
IMAGE_URL_3 = (
    "https://www.sws.bom.gov.au/Images/HF%20Systems/Global%20HF/"
    "Ionospheric%20Map/East/fof2_maps.png"
)
def display_band_conditions():
    """Display the band conditions window using Tkinter."""

    root = tk.Tk()
    root.title("Band Conditions")

    root.geometry("1200x750")
    root.resizable(False, False)

    # Create a label with a hyperlink
    link_label = tk.Label(root, text=LINK_TITLE, fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
    link_label.pack(pady=10)
    link_label.bind("<Button-1>", lambda event: webbrowser.open(HREF_URL))

    # Load both images from their URLs.
    image_frame = tk.Frame(root)
    image_frame.pack(fill="both", expand=True)
    image_references = []
    unverified_context = ssl._create_unverified_context()

    for image_url in (IMAGE_URL_1, IMAGE_URL_2, IMAGE_URL_3):
        try:
            with urlopen(image_url, context=unverified_context, timeout=20) as response:
                image_data = response.read()
                image = Image.open(BytesIO(image_data))
                image.thumbnail((480, 740), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_references.append(photo)
                tk.Label(image_frame, image=photo).pack(side=tk.LEFT, padx=8, pady=10)
        except Exception as error:
            tk.Label(
                image_frame,
                text=f"Image failed to load:\n{image_url}\n({error})",
                fg="red",
                justify="center",
                wraplength=460,
            ).pack(side=tk.LEFT, padx=8, pady=10)

    root.mainloop()
    return


def main():
    
    display_band_conditions()

if __name__ == "__main__":
    main()