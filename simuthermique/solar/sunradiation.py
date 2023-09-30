import numpy as np
import pandas as pd

import datetime as dt

from numpy import genfromtxt

import pysolar


"""  Get the sun position and the solar flux
     Projected on a surface
     
     en utilisant la librairie Pysolar
"""

# """ Prend en compte le masquage par l'horizon

# """
# horizon_data = genfromtxt('horizon.csv', delimiter=',').T


def is_upper_horizon(azimuth, altitude_deg):
    return 1


# def isUpperHorizon( azimuth, altitude_deg ):
#     azimuth = -azimuth
#     h = np.interp(azimuth, horizon_data[0, :], horizon_data[1, :])

#     if h > altitude_deg:
#         return False
#     else:
#         return True


def get_flux_surface(coords, date, sigma, phi_C):
    """
    coords: gps deg  (  )
    date: datetime object
    Surface orientation :
    sigma : deg, vertical angle of the surface, ref. to the horizontal
    phi_C : deg, azimuth, relative to south, with positive values
            in the southeast direction and negative values in the southwest

    return: flux solaire (W/m2)
    """

    # Sun position
    phi_S_deg = pysolar.solar.get_azimuth(
        *coords, date
    )  # deg, azimuth of the sun,relative to south
    beta_deg = pysolar.solar.get_altitude(
        *coords, date
    )  # deg, altitude angle of the sun

    I0 = pysolar.radiation.get_radiation_direct(date, beta_deg)  # W/m2
    I0 = I0 * is_upper_horizon(phi_S_deg, beta_deg)

    # Projection:
    beta = beta_deg * np.pi / 180  # rad
    phi_S = phi_S_deg * np.pi / 180  # rad
    sigma = sigma * np.pi / 180
    phi_C = phi_C * np.pi / 180

    cosTheta = np.cos(beta) * np.cos(phi_S - phi_C) * np.sin(sigma) + np.cos(
        sigma
    ) * np.sin(beta)

    if cosTheta > 0:
        Isurf = I0 * cosTheta  # flux projeté, W/m2
    else:
        Isurf = 0  # mais diffuse... ?

    return Isurf


def get_flux_total(coords, date):
    # Sun position
    beta_deg = pysolar.solar.get_altitude(
        *coords, date
    )  # deg, altitude angle of the sun

    I0 = pysolar.radiation.get_radiation_direct(d, beta_deg)  # W/m2

    return I0


def sun_positionAndFlux(coords, date):
    """Obtient la position et le flux solaire pour une date particulière
    coords: tuple gps
    date: datetime object

    return: ( flux solaire (W/m2), sunAzimuth, sunAltitude )
    """

    # Sun position
    phi_S_deg = pysolar.solar.get_azimuth(
        *coords, date
    )  # deg, azimuth of the sun,relative to south
    beta_deg = pysolar.solar.get_altitude(
        *coords, date
    )  # deg, altitude angle of the sun

    if is_upper_horizon(phi_S_deg, beta_deg):
        I0 = pysolar.radiation.get_radiation_direct(date, beta_deg)  # W/m2
    else:
        I0 = 0

    return (I0, phi_S_deg, beta_deg)


def buildmultidayDF(coords, index, cloudCover=None):
    """Construit un dataframe avec le flux solaire, et la position du soleil
    index: pandas dataframe index
    coords: tuple, GPS coords

    return a dataframe
    """

    array = np.array([sun_positionAndFlux(coords, d) for d in index])

    cols = ["I0", "sunAzimuth", "sunAltitude"]

    df = pd.DataFrame(data=array, index=index, columns=cols)

    if isinstance(cloudCover, pd.Series):
        df["I0"] = df["I0"] * (1 - 0.75 * cloudCover ** (3.4))
        # see https://www.shodor.org/os411/courses/_master/tools/calculators/solarrad/index.html

    return df




def project(sigma: float, phi_C, I0, phi_S_deg, beta_deg):
    """Calcul le flux solaire vu par une surface ayant une certaine orientation

    ref.: http://www.a-ghadimi.com/files/Courses/Renewable%20Energy/REN_Book.pdf
    book "Renewable and Efficient Electric Power Systems", Gilbert M. Masters, 2004
    page 414

    sigma: tilt_angle, angle de la surface avec l'horizontal, deg
    phi_C: azimuth_angel, azimuth de la surface, deg, positive in the southeast direction

    I0: flux solaire
    phi_S: azimuth du soleil, deg
    beta: altitude du soleil, deg
    """

    # conversion en radian:
    sigma = sigma * np.pi / 180
    phi_C = phi_C * np.pi / 180

    beta = beta_deg * np.pi / 180  # rad
    phi_S = phi_S_deg * np.pi / 180  # rad

    cosTheta = np.cos(beta) * np.cos(phi_S - phi_C) * np.sin(sigma) + np.cos(
        sigma
    ) * np.sin(beta)

    if cosTheta > 0:
        Isurf = I0 * cosTheta  # flux projeté, W/m2
    else:
        Isurf = 0  # mais diffuse... ?

    return Isurf


def projectDF(sigma, phi_C, sundata):
    """build a dataframe with flux on a surface"""
    get_fluxsurface = lambda sundata, sigma, phi_C: project(
        sigma, phi_C, *sundata.values
    )
    df = sundata.apply(get_fluxsurface, axis=1, sigma=sigma, phi_C=phi_C)
    return df

    return df
