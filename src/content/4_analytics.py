import streamlit as st 
import requests
from src.config import Config, logger
import pandas as pd 
import altair as alt 
import datetime as dt

st.title("Analytics")

#initialize filters before callback
ammo_filter = []
gear_filter = []
position_filter = []
start_date = pd.to_datetime("2023-01-01")
end_date = pd.to_datetime("2025-12-31")

if "plot" not in st.session_state.keys():
    st.session_state.plot = False

#@st.cache_data TODO : find a way to add intelligence to the cache timeout/refresh
def get_analytics() -> pd.DataFrame:
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
        return pd.DataFrame()


# store filtered data in session state 

def filtering_data(df, ammo_filter, gear_filter, position_filter, start_date, end_date):
    logger.debug(f"Filtering data with {ammo_filter}, {gear_filter}, {position_filter}, {start_date}, {end_date}")
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_copied = df.copy()
    filt_df = df_copied[(df_copied["ammo"].isin(ammo_filter)) & (df_copied["gear"].isin(gear_filter)) & (df_copied["position"].isin(position_filter)) & (df_copied["created_at"].between(start_date, end_date))]
  
    mean_group_size = filt_df["group_size"].mean()
    logger.debug(f"Mean group size inside function: {mean_group_size}")
    logger.debug(f"length of filtered data : {len(filt_df)}")
    #st.write("Historic")
    #filtered_df["created_at"] = pd.to_datetime(filtered_df["created_at"])  # Ensure datetime format
    return filt_df
    '''
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
            )'''
    '''
    with plot_container:
        with st.container(border = True) :
            st.metric("Mean Group Size", value = f"{mean_group_size:.2f}")

        with st.container(border = True):
            st.altair_chart(chart, use_container_width=True)

    with st.expander("Details"):
        st.dataframe(filtered_df, use_container_width=True)'''

def create_boxplots(df: pd.DataFrame):
    box_plot = alt.Chart(df).mark_boxplot(
        #extent = 'min-max',
        size = 50,
        ticks={"color" : "white",
               "size" : 50},
        outliers={"color" : "red"},
        rule={"color" : "white"},


    ).encode(
        x = "name:N",
        y = "group_size:Q",
               #color = "id",
        tooltip = ["group_size", "name"]
    ).properties(
        title="Boxplot of Group Size by Setup",
        width=800,
        height=400
    )

    return box_plot


df = get_analytics()
logger.debug(f"Length of df : {len(df)}")
logger.debug(f"df columns : {df.columns}")
if len(df) == 0:
    st.error("No data found")
else:

    df["created_at"] = pd.to_datetime(df["created_at"])

    st.sidebar.header("Filter")
    ammo_filter = st.sidebar.multiselect(
        "Select ammo",
        options=df["ammo"].unique(),
        default=df["ammo"].unique(),
        #on_change = filtering_data(df, ammo_filter, gear_filter, position_filter, start_date, end_date)

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
        value= (dt.date(2023, 1, 1), dt.date(2025, 12, 31))

        #on_change = filtering_data

    )

    filtered_df = filtering_data(df, ammo_filter, gear_filter, position_filter, start_date, end_date)

    box_plot = create_boxplots(df)
    metrics_col, boxplot_col = st.columns([1,4], vertical_alignment="center")
    with metrics_col:
        metrics_container = st.empty()
    with boxplot_col:
        boxplot_container = st.empty()

    plot_container = st.empty()


# df_copied = df.copy()
# filtered_df = df_copied[(df_copied["name"].isin(ammo_filter)) & (df_copied["gear"].isin(gear_filter)) & (df_copied["position"].isin(position_filter)) & (df_copied["created_at"].between(pd.to_datetime(start_date), pd.to_datetime(end_date)))]
#
    mean_group_size = filtered_df["group_size"].mean()
    logger.debug(f"Mean group size outside function : {mean_group_size}")
#logger.debug(f"Filtered df : {filtered_df}")
    filtered_df["created_at"] = pd.to_datetime(filtered_df["created_at"])  # Ensure datetime format
    filtered_df["date"] = filtered_df["created_at"].dt.date
    # logger.debug(f"agg df : {filtered_df.groupby(['created_at']).mean().reset_index()}")
    logger.debug(f"date type : {filtered_df['date'].dtype}")
    logger.debug(f"filtered df head : {filtered_df.head()}")
    logger.debug(f"group size distinct values : {filtered_df['group_size'].nunique()}")
    logger.debug(f"grouped df : {filtered_df.groupby("date").agg({"group_size": "mean"}).reset_index()}")
    logger.debug(f"mean group size on the 2024 12 06 : {filtered_df["group_size"].loc[pd.to_datetime(filtered_df["date"]) == pd.to_datetime('2024-12-29')].mean()}")
    chart = (
                alt.Chart(filtered_df.groupby(filtered_df["date"]).agg({"group_size": "mean"}).reset_index())
                .mark_line(point=True)
                .encode(
                    x="date:T",
                    y="group_size:Q",
                    tooltip=["date", "group_size"] 
                )
                .properties(
                    width=800,
                    height=400,
                    title="Group Size Over Time"
                )
            )

    with metrics_container:
        st.metric("Mean Group Size", value = f"{mean_group_size:.2f}", delta =f"{mean_group_size - df['group_size'].mean():.2f}", delta_color="inverse", border = True)

    with boxplot_container:
        st.altair_chart(box_plot, use_container_width=True)
    with plot_container:

        st.altair_chart(chart, use_container_width=True)

    with st.expander("Details"):
        st.dataframe(filtered_df, use_container_width=True)

if st.button("Add a custom plot") or st.session_state.plot:
    st.session_state.plot = True
    x_axis = st.selectbox("Select X-axis:", options=df.columns)
    y_axis = st.selectbox("Select Y-axis:", options=df.columns)

# User selects a column to split data into series (optional)
    split_column = st.selectbox("Select a column to split data (optional):", options=["None"] + list(df.columns))

# Base chart
    base = alt.Chart(df).mark_point().encode(
        x=alt.X(x_axis, title=x_axis),
        y=alt.Y(y_axis, title=y_axis)
    )

# Add a split if selected
    if split_column != "None":
        chart = base.encode(color=alt.Color(split_column, title=split_column))
    else:
        chart = base

# Render the chart
    st.altair_chart(chart.interactive(), use_container_width=True)

    if st.button("Close"):
        st.session_state.plot = False
