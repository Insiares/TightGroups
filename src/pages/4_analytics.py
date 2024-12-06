import streamlit as st 
import requests
from src.config import Config, logger
import pandas as pd 
import altair as alt 


st.title("Analytics")

#initialize filters before callback
ammo_filter = []
gear_filter = []
position_filter = []

@st.cache_data
def get_analytics():
    try :
        backend_url = Config.BACKEND_URL
        headers = {"Content-Type": "application/json"}
        response = requests.get(f"{backend_url}/scores/{st.session_state.user_id}/", headers=headers)
        # analytics = response.json()
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Accessed analytics for user {st.session_state.user_id}")
            df = pd.DataFrame(data)
            return df 
        else : 
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error : {e}")


def filtering_data(df, ammo_filter, gear_filter, position_filter, start_date, end_date):
    logger.debug(f"Filtering data with {ammo_filter}, {gear_filter}, {position_filter}, {start_date}, {end_date}")

    filtered_df = df.copy()

    if ammo_filter:
        filtered_df = filtered_df[filtered_df["name"].isin(ammo_filter)]

    if gear_filter:
        filtered_df = filtered_df[filtered_df["gear"].isin(gear_filter)]

    if position_filter:
        filtered_df = filtered_df[filtered_df["position"].isin(position_filter)]

    if start_date is not None:
        filtered_df = filtered_df.loc[filtered_df["created_at"] >= pd.to_datetime(start_date)]

    if end_date is not None:
        filtered_df = filtered_df.loc[filtered_df["created_at"] <= pd.to_datetime(end_date)]

    mean_group_size = filtered_df["group_size"].mean()
    with st.container(border = True) :
        st.metric("Mean Group Size", value = f"{mean_group_size:.2f}")

    st.write("Historic")
    filtered_df["created_at"] = pd.to_datetime(filtered_df["created_at"])  # Ensure datetime format
    chart = (
                alt.Chart(filtered_df)
                .mark_line(point=True)
                .encode(
                    x="created_at:T",
                    y="group_size:Q",
                    tooltip=["created_at", "group_size", "name", "gear"]
                )
                .properties(
                    width=800,
                    height=400,
                    title="Group Size Over Time"
                )
            )

    with st.container(border = True):
        st.altair_chart(chart, use_container_width=True)

    with st.expander("Details"):
        st.dataframe(filtered_df, use_container_width=True)


df = get_analytics()
df["created_at"] = pd.to_datetime(df["created_at"])

st.sidebar.header("Filter")
ammo_filter = st.sidebar.multiselect(
    "Select ammo",
    options=df["name"].unique(),
    default=df["name"].unique(),
    #on_change = filtering_data

)

gear_filter = st.sidebar.multiselect(
    "Select gear",
    options=df["gear"].unique(),
    default=df["gear"].unique(),
    #on_change = filtering_data
)

position_filter = st.sidebar.multiselect(
    "Select position",
    options=df["position"].unique(),
    default=df["position"].unique(),
    #on_change = filtering_data
)

start_date, end_date = st.sidebar.date_input(
    "Select Date Range", 
    value=(df["created_at"].min(), df["created_at"].max()),

    #on_change = filtering_data

)

filtering_data(df, ammo_filter, gear_filter, position_filter, start_date, end_date)

