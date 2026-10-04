"""
hf_propagation.py
-----------------
Real-time HF band propagation checker using live NOAA Space Weather data.

Fetches solar flux (SFI), planetary K-index (Kp), and X-ray flux
from NOAA SWPC JSON APIs and calculates estimated propagation
conditions for each HF amateur band (160m through 10m).

Built by JP Pacheco (KD9XXX) — Extra Class Ham Radio Operator
Field experience: FlexRadio Systems (2020–2022)
API source: NOAA Space Weather Prediction Center (swpc.noaa.gov)
"""
#-----------------------------------------------------------
# Must install tkinter to run the GUI version of this script
# Contributor for changes: Jeff Tubbenhauer VK5IU
#-----------------------------------------------------------

from turtle import st
import urllib.request
import json
import datetime
import logging
import argparse
import tkinter as tk
from tkinter import ttk

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("hf_propagation")

# ── NOAA SWPC JSON API Endpoints ───────────────────────────────────────────────
NOAA_SOLAR_WIND_URL  = "https://services.swpc.noaa.gov/products/summary/solar-wind-mag-field.json"
NOAA_KP_INDEX_URL    = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
NOAA_XRAY_URL        = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
NOAA_SFI_URL         = "https://services.swpc.noaa.gov/products/summary/10cm-flux.json"

# ── HF Bands ───────────────────────────────────────────────────────────────────
HF_BANDS = [
    {"name": "160m", "freq_mhz": 1.8,  "min_sfi": 0,   "kp_sensitive": True},
    {"name": "80m",  "freq_mhz": 3.5,  "min_sfi": 0,   "kp_sensitive": True},
    {"name": "40m",  "freq_mhz": 7.0,  "min_sfi": 0,   "kp_sensitive": True},
    {"name": "30m",  "freq_mhz": 10.1, "min_sfi": 70,  "kp_sensitive": False},
    {"name": "20m",  "freq_mhz": 14.0, "min_sfi": 80,  "kp_sensitive": False},
    {"name": "17m",  "freq_mhz": 18.1, "min_sfi": 90,  "kp_sensitive": False},
    {"name": "15m",  "freq_mhz": 21.0, "min_sfi": 100, "kp_sensitive": False},
    {"name": "12m",  "freq_mhz": 24.9, "min_sfi": 120, "kp_sensitive": False},
    {"name": "10m",  "freq_mhz": 28.0, "min_sfi": 150, "kp_sensitive": False},
]


# ── API Fetchers ───────────────────────────────────────────────────────────────

def fetch_json(url: str) -> dict | list | None:
    """Fetch JSON data from a URL. Returns parsed data or None on failure."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        log.warning(f"Failed to fetch {url}: {e}")
        return None


def get_solar_flux() -> float | None:
    """Fetch current 10.7cm solar flux index (SFI) from NOAA."""
    data = fetch_json(NOAA_SFI_URL)
    if isinstance(data, list) and data:
        data = data[-1]
    if isinstance(data, dict):
        try:
            return float(data.get("flux", data.get("Flux")))
        except (ValueError, TypeError):
            return None
    return None


def get_kp_index() -> float | None:
    """Fetch current planetary K-index (Kp) from NOAA."""
    data = fetch_json(NOAA_KP_INDEX_URL)
    if isinstance(data, list):
        for record in reversed(data):
            if isinstance(record, dict) and "Kp" in record:
                try:
                    return float(record["Kp"])
                except (ValueError, TypeError):
                    continue
    elif isinstance(data, dict) and "Kp" in data:
        try:
            return float(data["Kp"])
        except (ValueError, TypeError):
            return None
    return None


def get_xray_class() -> str:
    """Fetch current X-ray flux and return its flare class, e.g. 'C2.3'."""
    data = fetch_json(NOAA_XRAY_URL)
    if isinstance(data, list):
        for record in reversed(data):
            if not isinstance(record, dict) or record.get("energy") != "0.1-0.8nm":
                continue
            try:
                flux = float(record["flux"])
            except (KeyError, ValueError, TypeError):
                continue
            if flux >= 1e-4:
                letter, threshold = "X", 1e-4
            elif flux >= 1e-5:
                letter, threshold = "M", 1e-5
            elif flux >= 1e-6:
                letter, threshold = "C", 1e-6
            elif flux >= 1e-7:
                letter, threshold = "B", 1e-7
            else:
                letter, threshold = "A", 1e-8
            return f"{letter}{flux / threshold:.1f}"
    return "None"


# ── Propagation Scoring ────────────────────────────────────────────────────────

def score_band(band: dict, sfi: float, kp: float, xray_class: str) -> dict:
    """
    Estimate propagation quality for a single HF band.

    Scoring model based on:
    - SFI vs band minimum requirement
    - Kp index (geomagnetic disturbance)
    - X-ray flare class (D-layer absorption)
    - Day/night consideration (simplified)

    Returns a dict with score (0-100), rating label, and notes.
    """
    score = 100.0
    notes = []

    # ── SFI scoring ────────────────────────────────────────────────────────────
    min_sfi = band["min_sfi"]
    if sfi < min_sfi:
        deficit = min_sfi - sfi
        penalty = min(60, deficit * 1.5)
        score -= penalty
        notes.append(f"SFI {sfi:.0f} below {min_sfi} minimum for {band['name']}")
    elif sfi >= min_sfi + 50:
        score = min(score + 5, 100)
        notes.append("High SFI — excellent ionization")

    # ── Kp scoring ─────────────────────────────────────────────────────────────
    if kp >= 5:
        penalty = (kp - 4) * 15
        score -= penalty
        notes.append(f"Geomagnetic storm (Kp={kp:.1f}) — HF disruption likely")
    elif kp >= 3:
        score -= (kp - 2) * 8
        notes.append(f"Elevated Kp={kp:.1f} — minor HF degradation possible")
    elif kp <= 1:
        score = min(score + 5, 100)
        notes.append("Quiet geomagnetic conditions")

    # ── X-ray / flare absorption ───────────────────────────────────────────────
    if xray_class and xray_class[0] in ("M", "X"):
        score -= 25
        notes.append(f"Solar flare {xray_class} — D-layer absorption on sunlit side")
    elif xray_class and xray_class[0] == "C":
        score -= 10
        notes.append(f"C-class flare {xray_class} — minor HF absorption possible")

    score = max(0.0, min(100.0, score))

    # ── Rating label ───────────────────────────────────────────────────────────
    if score >= 80:
        rating = "EXCELLENT"
    elif score >= 60:
        rating = "GOOD"
    elif score >= 40:
        rating = "FAIR"
    elif score >= 20:
        rating = "POOR"
    else:
        rating = "CLOSED"

    return {
        "band": band["name"],
        "freq_mhz": band["freq_mhz"],
        "score": round(score, 1),
        "rating": rating,
        "notes": notes,
    }


# ── Report Formatter ───────────────────────────────────────────────────────────

def print_report(sfi: float, kp: float, xray: str, results: list[dict]):
    """Print a formatted propagation report to the console."""
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%MZ")

    print("\n" + "=" * 60)
    print(f"  HF PROPAGATION REPORT - {now}")
    print("=" * 60)
    print(f"  Solar Flux Index (SFI) : {sfi:.0f}")
    print(f"  Planetary K-index (Kp) : {kp:.1f}")
    print(f"  X-Ray Flare Class      : {xray}")
    print("=" * 60)
    print(f"  {'BAND':<8} {'FREQ':>8}  {'SCORE':>6}  RATING")
    print("-" * 60)
    for r in results:
        print(f"  {r['band']:<8} {r['freq_mhz']:>6.1f} MHz  {r['score']:>5.1f}  {r['rating']}")
    print("-" * 60)

    # Show notes for flagged bands
    flagged = [r for r in results if r["notes"]]
    if flagged:
        print("\n  NOTES:")
        for r in flagged:
            for note in r["notes"]:
                print(f"  [{r['band']}] {note}")

    print("=" * 60)
    print("  Data: NOAA Space Weather Prediction Center (swpc.noaa.gov)")
    print("=" * 60 + "\n")


def export_json(sfi: float, kp: float, xray: str, results: list[dict], path: str):
    """Export results to a JSON file."""
    output = {
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "solar_conditions": {
            "sfi": sfi,
            "kp": kp,
            "xray_class": xray,
        },
        "bands": results,
    }
    with open(path, "w") as f:
        json.dump(output, f, indent=2)
    log.info(f"Results exported to {path}")

def launch_display(sfi: float, kp: float, xray: str, results: list[dict]):
    root = tk.Tk()
    display(root, sfi, kp, xray, results)
    root.mainloop()
    



# ── Main ───────────────────────────────────────────────────────────────────────
class display:
    """Display the current HF propagation report in a Tkinter window."""

    def __init__(self, master, sfi: float, kp: float, xray: str, results: list[dict]):
        self.master = master
        self.sfi = sfi
        self.kp = kp
        self.xray = xray
        self.results = results
        self.create_widgets()

    def create_widgets(self):
        self.master.title("HF Propagation Report")
        self.master.geometry("900x380")
        self.master.minsize(00, 300)

        summary = ttk.LabelFrame(self.master, text="Current Solar Conditions", padding=10)
        summary.pack(fill="x", padx=10, pady=(10, 6))

        for column, (label, value) in enumerate((
            ("Solar Flux Index (SFI)", f"{self.sfi:.0f}"),
            ("Planetary K-index (Kp)", f"{self.kp:.1f}"),
            ("X-Ray Flare Class", self.xray),
        )):
            ttk.Label(summary, text=f"{label}: {value}").grid(
                row=0, column=column, padx=12, sticky="w"
            )

        table_frame = ttk.Frame(self.master)
        table_frame.pack(fill="both", expand=True, padx=10, pady=6)

        columns = ("band", "frequency", "score", "rating", "notes")
        table = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = {
            "band": ("Band", 70),
            "frequency": ("Frequency (MHz)", 120),
            "score": ("Score", 80),
            "rating": ("Rating", 100),
            "notes": ("Notes", 460),
        }
        for column, (heading, width) in headings.items():
            table.heading(column, text=heading)
            table.column(column, width=width, anchor="w")

        vertical_scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=table.yview
        )
        horizontal_scrollbar = ttk.Scrollbar(
            table_frame, orient="horizontal", command=table.xview
        )
        table.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )
        table.grid(row=0, column=0, sticky="nsew")
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        for result in self.results:
            table.insert(
                "",
                "end",
                values=(
                    result["band"],
                    f"{result['freq_mhz']:.1f}",
                    f"{result['score']:.1f}",
                    result["rating"],
                    "; ".join(result["notes"]) or "No notable issues",
                ),
            )

        ttk.Label(
            self.master,
            text="Data source: NOAA Space Weather Prediction Center (swpc.noaa.gov)",
        ).pack(anchor="w", padx=12, pady=(0, 10))


# ── Main ─────────────────────────────────────────────────────────────────────── 


def main():
    parser = argparse.ArgumentParser(
        description="HF Propagation Checker — Real-time NOAA data | JP Pacheco / jeypnet"
    )
    parser.add_argument("--json", metavar="FILE", help="Export results to JSON file")
    parser.add_argument("--band", metavar="BAND", help="Check a specific band only (e.g. 20m)")
    parser.add_argument("--sfi", type=float, help="Override SFI value (for testing)")
    parser.add_argument("--kp",  type=float, help="Override Kp value (for testing)")
    args = parser.parse_args()

    log.info("Fetching real-time solar data from NOAA SWPC...")

    sfi   = args.sfi if args.sfi is not None else get_solar_flux()
    kp    = args.kp  if args.kp  is not None else get_kp_index()
    xray  = get_xray_class()

    if sfi is None:
        log.warning("Could not fetch SFI — using default value of 120")
        sfi = 120.0
    if kp is None:
        log.warning("Could not fetch Kp — using default value of 2")
        kp = 2.0

    bands = HF_BANDS
    if args.band:
        bands = [b for b in HF_BANDS if b["name"].lower() == args.band.lower()]
        if not bands:
            log.error(f"Unknown band: {args.band}. Valid: {[b['name'] for b in HF_BANDS]}")
            return

    results = [score_band(b, sfi, kp, xray) for b in bands]
    #print_report(sfi, kp, xray, results)

    if args.json:
        export_json(sfi, kp, xray, results, args.json)

    launch_display(sfi, kp, xray, results)

if __name__ == "__main__":
    main()
