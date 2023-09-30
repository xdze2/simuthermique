import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pvlib


class SolarCollector:
    def __init__(
        self,
        latitude: float,
        longitude: float,
        surface_tilt_angle: float,
        surface_azimuth: float,
    ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.surface_tilt_angle = surface_tilt_angle
        self.surface_azimuth = surface_azimuth

        self.location = pvlib.location.Location(self.latitude, self.longitude)

    def get_clear_sky_irad(self, date_range: pd.DatetimeIndex) -> pd.DataFrame:
        return self.location.get_clearsky(date_range)

    def get_solar_position(self, date_range: pd.DatetimeIndex) -> pd.DataFrame:
        solar_pos = self.location.get_solarposition(date_range)
        solar_pos["altitude"] = 90 - solar_pos["zenith"]
        solar_pos["azimuth_south"] = (solar_pos["azimuth"] - 180)
        return solar_pos

    def get_irradiance(self, date_range: pd.DatetimeIndex) -> pd.DataFrame:
        irad = self.get_clear_sky_irad(date_range)
        solar_pos = self.get_solar_position(date_range)

        cos_theta = ray_incidence_cos_theta(
            self.surface_tilt_angle,
            self.surface_azimuth,
            solar_pos["altitude"],
            solar_pos["azimuth_south"],
        )
        direct_irad = cos_theta * irad['dni']
        sky_view_factor = np.cos(self.surface_tilt_angle*np.pi/180)/2 + 0.5
        diffuse_irad = sky_view_factor * irad['dhi']
        return  direct_irad + diffuse_irad


def deg_to_rad(angle_deg: float) -> float:
    return angle_deg * np.pi / 180.0


def ray_incidence_cos_theta(
    surface_tilt_angle_deg: float,
    surface_azimuth_angle_deg: float,
    solar_altitude_angle_deg: float,
    solar_azimuth_angle_deg: float,
) -> float:
    """Cosinus of the angle of incidence of the solar ray on a tilted surface.

    Azimuth angles are relative to the south, with positive values in the southeast direction

    ref.: http://www.a-ghadimi.com/files/Courses/Renewable%20Energy/REN_Book.pdf
    book "Renewable and Efficient Electric Power Systems", Gilbert M. Masters, 2004
    page 414
    """
    sigma = deg_to_rad(surface_tilt_angle_deg)
    phi_C = deg_to_rad(surface_azimuth_angle_deg)
    beta = deg_to_rad(solar_altitude_angle_deg)
    phi_S = deg_to_rad(solar_azimuth_angle_deg)

    cos_beta, sin_beta = np.cos(beta), np.sin(beta)
    cos_sigma, sin_sigma = np.cos(sigma), np.sin(sigma)

    cos_theta = cos_beta * np.cos(phi_S - phi_C) * sin_sigma + cos_sigma * sin_beta
    return np.clip(cos_theta, 0, None) 