

import numpy as np

import matplotlib.pyplot as plt
from simuthermique.date_and_time import get_daterange
from simuthermique.solar_collector import (SolarCollector,
                                           ray_incidence_cos_theta)


sc = SolarCollector(
    latitude = 43.6,
    longitude =  1.34,
    surface_tilt_angle=90,
    surface_azimuth=-100
)

tims = get_daterange("01-01-2023", "02-01-2023")


clear_sky = sc.get_clear_sky_irad(tims)
solar_pos = sc.get_solar_position(tims)
surface_irad = sc.get_irradiance(tims)

fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)

plt.tick_params('x', labelsize=6)
axs[0].plot(tims, clear_sky['dni'], label="dni")
axs[0].plot(tims, clear_sky['dhi'], label="dhi")
axs[0].set_ylabel("Clear sky\n iradiance [W/m2]")
axs[0].legend()

axs[1].plot(tims, solar_pos['azimuth_south'], label="azimuth_south")
axs[1].plot(tims, solar_pos['altitude'], label="altitude")
axs[1].axhline(0, color="black", linewidth=1, zorder=-100)
axs[1].set_ylabel("Solar position [deg]")
axs[1].legend()

axs[2].plot(tims, surface_irad, label="surface irad [w/m2]")
# axs[2].set_ylabel("Solar position [deg]")
axs[2].legend()


plt.show()

# # share x only
# ax2 = plt.subplot(312, sharex=ax1)
# plt.plot(t, s2)
# # make these tick labels invisible
# plt.tick_params('x', labelbottom=False)


# print(I_rad)


# solar_pos = sc.get_solar_position(tims)
# print(solar_pos)
# plt.figure(figsize=(12, 3))
# plt.plot(sc.get_solar_position(tims)['azimuth_south'], label="azimuth_south")
# plt.plot(sc.get_solar_position(tims)['azimuth'], label="azimuth")

# # plt.plot(I_rad, label="ext")
# plt.legend()
# # plt.xlabel("time")
# # plt.xlabel("Irradiation [W/m2]")
# plt.show()


# clear_sky = sc.get_clear_sky_irad(tims)


# plt.figure(figsize=(12, 3))
# plt.plot(clear_sky['dni'], label="dni")

# plt.plot(I_rad, label="ext")
# plt.legend()
# plt.xlabel("time")
# plt.xlabel("Irradiation [W/m2]")
# plt.show()
