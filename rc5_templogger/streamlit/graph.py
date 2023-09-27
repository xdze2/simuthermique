import streamlit as st
import pandas as pd
from glob import glob
import altair as alt

st.title("Temperature data")

files = glob("../data/data_*.csv")


@st.cache
def get_dataframe(filepath):
    df = pd.read_csv(filepath, delimiter=",", index_col="datetime", parse_dates=False)
    df.index = pd.to_datetime(df.index, utc=True)
    df["location"] = df.columns[0]
    df = df.rename(columns={df.columns[0]: "temperature"})
    return df


selected = st.multiselect(
    "Select data files",
    files,
    default=files,
    format_func=lambda x: x.split("/")[-1].replace(".csv", ""),
)

if len(selected) == 0:
    st.stop()

df = [get_dataframe(fn) for fn in selected]
df = pd.concat(df, axis=0)

daterange = st.date_input(
    "Select", [df.index[0], df.index[-1]], min_value=df.index[0], max_value=df.index[-1]
)
daterange = [pd.to_datetime(u, unit="ns", utc=True) for u in daterange]
if len(daterange) != 2:
    st.error("wrong range")
    st.stop()

# st.write([str(u) for u in daterange])

mask = (df.index > daterange[0]) & (df.index < daterange[1])
df_zoom = df.loc[mask]
# st.line_chart(data=df.loc[mask], use_container_width=True)

grpbyday = st.checkbox("group by day", value=False)

chart = (
    alt.Chart(df_zoom.reset_index())
    .mark_line()
    .encode(alt.X("datetime:T", title="day"), y="temperature:Q", color="location:N")
)

st.altair_chart(chart, use_container_width=True)
