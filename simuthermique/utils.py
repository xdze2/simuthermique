import numpy as np
import pandas as pd
from typing import Callable
from scipy import interpolate


def get_daterange(
    start_date: str, end_date: str, freq: str = "5min"
) -> pd.DatetimeIndex:
    """Create a Pandas datetime index.

    Example: `get_daterange("25-09-2023", "01-10-2023")`
    """
    start_dt = pd.to_datetime(start_date, yearfirst=True, dayfirst="False")
    end_dt = pd.to_datetime(end_date, yearfirst=True, dayfirst="False")
    return pd.date_range(start_dt, end_dt, freq=freq, tz="UTC")


def read_csv(filepath: str, serie_name: str = "data") -> pd.DataFrame:
    """Read Time serie data from csv file."""
    df = pd.read_csv(filepath, skiprows=2, names=["time", serie_name], index_col=0)
    df.index = pd.to_datetime(df.index, unit="ms")
    return df


def interpolate_timeserie(
    target_index: pd.DatetimeIndex, serie: pd.DataFrame
) -> pd.Series:
    """Use to regularize timeserie index."""
    target_time_sec = target_index.astype(np.int64) // 1e9
    index_sec = serie.index.astype(np.int64) // 1e9
    value = serie.iloc[:, 0].to_numpy()

    target_value = np.interp(target_time_sec, index_sec, value)
    return pd.Series(target_value, index=target_index)


def get_interpolation_function(serie: pd.Series) -> Callable:
    index_sec = serie.index.astype(np.int64) // 1e9
    value = serie.to_numpy()
    return interpolate.interp1d(
        index_sec, value, bounds_error=False, fill_value=(value[0], value[-1])
    )
