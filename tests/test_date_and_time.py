from simuthermique.date_and_time import get_daterange


def test_get_daterange():
    ra = get_daterange("2023-11-01", "2023-11-02")

    print(ra)

    assert len(ra) == 24 * 60 / 5 + 1
