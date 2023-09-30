from simuthermique.solar.sunradiation import _cos_theta

import numpy as np
from pytest import approx



def test_cos_theta():

    assert _cos_theta(90, 0, 0, 0) == approx(1.0)
    assert _cos_theta(90, 0, 45, 0) == approx(np.sqrt(2)/2)
    assert _cos_theta(90, 45, 0, 0) == approx(np.sqrt(2)/2)
    assert _cos_theta(90, 45, 0, 45) == approx(1)