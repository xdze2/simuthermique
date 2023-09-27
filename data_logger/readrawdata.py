import os
import numpy as np
import pandas as pd


def phpfina_feed(feed_id, data_path="./phpfina"):
    """
    Decode the .dat file storing feed data
    returns a pandas dataframe

    To get the raw data:
    - log on the raspberry, (pi, emonpi2016)
    - Feed data are stored in `/var/opt/emoncms/phpfina`

    time is in seconds (unixtime stamp)
    """
    # decode metadata
    meta_filename = f"{feed_id}.meta"
    path = os.path.join(data_path, meta_filename)

    with open(path, "rb") as f:
        read_data = f.read()

    meta = np.frombuffer(read_data, dtype="uint32")
    # print(meta)
    interval = meta[2]
    start_time = meta[3]

    # decode data
    meta_filename = f"{feed_id}.dat"
    path = os.path.join(data_path, meta_filename)

    with open(path, "rb") as f:
        data = np.frombuffer(f.read(), dtype="float32")

    # print(len(data))

    k = np.arange(len(data), dtype="int32")
    time = k * interval + start_time

    # filter out NaN
    mask = np.logical_not(np.isnan(data))
    time, data = time[mask], data[mask]

    time_index = pd.to_datetime(time, unit="s")
    df = pd.DataFrame(data, index=time_index)

    return df
