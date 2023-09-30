import pandas as pd




def get_daterange(start_date: str, end_date: str, freq: str="5min") -> pd.DatetimeIndex:

    start_dt = pd.to_datetime(start_date, yearfirst=True, dayfirst="False")
    end_dt = pd.to_datetime(end_date,  yearfirst=True, dayfirst="False")
    return pd.date_range(
        start_dt, end_dt, freq=freq, tz="UTC"
    )



