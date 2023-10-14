from simuthermique.utils import get_daterange, interpolate_timeserie


def test_get_daterange():
    ra = get_daterange("2023-11-01", "2023-11-02")
    assert len(ra) == 24 * 60 / 5 + 1
