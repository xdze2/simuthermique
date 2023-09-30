import pandas as pd
import matplotlib.pyplot as plt

import pvlib



# # arrays = [
# #     pv.pvsystem.Array(
# #         pv.pvsystem.FixedMount(30, 270), name="West-Facing Array",
# #     ),
# #     pv.pvsystem.Array(
# #         pv.pvsystem.FixedMount(30, 90), name="East-Facing Array",
# #     ),
# # ]

class Loc:
    latitude = 43.6
    longitude = 1.34

loc = pvlib.location.Location(Loc.latitude, Loc.longitude)



times = pd.date_range(
    "2023-01-01 00:00", "2023-01-02 00:00", freq="5min", tz="UTC"
)
 

weather = loc.get_clearsky(times)

print(weather)
# arry = pvlib.pvsystem.Array(
#     pvlib.pvsystem.FixedMount(30, 270), name="West-Facing Array",
# )
# print(arry.get_irradiance(weather))
# system = pvsystem.PVSystem(arrays=arrays)
# mc = modelchain.ModelChain(system, loc, aoi_model="physical", spectral_model="no_loss")

# mc.run_model(weather)

fig, ax = plt.subplots()

plt.plot(weather)
# for array, pdc in zip(system.arrays, mc.results.dc):
#     pdc.plot(label=f"{array.name}")
# mc.results.ac.plot(label="Inverter")
# plt.ylabel("System Output")
# plt.legend()
plt.show()
