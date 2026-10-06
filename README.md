## Propagation

The Band_Conditions.py shows the latest propagation from hamsql.com and Australian Bureau of Meteorology (BOM)

solar_data.py show solar data

install tkinker

## Changes made to hf_propagation.py and hf_propagation_tkinker.py

Modifications done on 06/10/2026 by Jeff Tubbenhauer VK5IU

Here's what changed, across hf_propagation.py and hf_propagation_tkinker.py.

1. Stale data (original request, hf_propagation.py)
•	NOAA changed its feeds. The SFI feed now returns a list with a lowercase flux key, and the old Kp and X-ray summary URLs returned 404 errors.
•	The fetchers now use the working URLs and take the newest record by time_tag.
•	The Kp URL is now noaa-planetary-k-index.json.
•	I removed the unused NOAA_GEOMAG_URL.
•	The utcnow() calls are now datetime.now(timezone.utc).

2. Windows console crash
•	The report crashed on Unicode box characters and emoji in a cp1252 console.
•	It now prints plain ASCII: =, -, and text-only ratings such as EXCELLENT.
3. Wrong band scores and ratings (both scripts, identical logic)

•	SFI: only bands with a minimum SFI are affected. The penalty shrinks as SFI rises above the minimum, up to 50 points above it, and grows faster below it. Low bands no longer get the "High SFI" bonus.
•	Kp: the penalty now rises smoothly instead of jumping at Kp 5. The kp_sensitive bands (160m, 80m and 40m) are penalised 1.5× as much.
•	Flares: C, M and X flares cost less on higher-frequency bands, and X-class now has its own, larger penalty.
•	Bonus removed: the quiet-conditions score bonus is gone, but the note remains.

4. X-ray class made consistent
•	hf_propagation.py now works out the class from live 0.1–0.8nm flux in xrays-1-day.json, as the Tkinter script does.
•	Both scripts returned B9.7 on the same live data.
5. Tkinter script cleanup
•	I removed the stray from turtle import st import.
The scoring is still a simplified heuristic with no day/night or path modelling.


