from simuthermique.solar_collector import ray_incidence_cos_theta, SolarCollector

import numpy as np
from pytest import approx

from simuthermique.date_and_time import get_daterange


def test_ray_incidence_cos_theta():
    assert ray_incidence_cos_theta(90, 0, 0, 0) == approx(1.0)
    assert ray_incidence_cos_theta(90, 0, 45, 0) == approx(np.sqrt(2) / 2)
    assert ray_incidence_cos_theta(90, 45, 0, 0) == approx(np.sqrt(2) / 2)
    assert ray_incidence_cos_theta(90, 45, 0, 45) == approx(1)

    assert ray_incidence_cos_theta(90, 0, 0, 100) == approx(0.0)


def test_SolarCollector():
    sc = SolarCollector(
        latitude=43.6, longitude=1.34, surface_tilt_angle=90, surface_azimuth=-20
    )

    tims = get_daterange("01/01/2023", "02/01/2023")
    I_rad = sc.get_irradiance(tims)

    print(I_rad)
