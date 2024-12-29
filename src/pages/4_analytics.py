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
start_date = pd.to_datetime("2023-01-01")
end_date = pd.to_datetime("2025-12-31")


#@st.cache_data TODO : find a way to add intelligence to the cache timeout/refresh
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


# store filtered data in session state 

def filtering_data(df, ammo_filter, gear_filter, position_filter, start_date, end_date):
    logger.debug(f"Filtering data with {ammo_filter}, {gear_filter}, {position_filter}, {start_date}, {end_date}")
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    df_copied = df.copy()
    filt_df = df_copied[(df_copied["name"].isin(ammo_filter)) & (df_copied["gear"].isin(gear_filter)) & (df_copied["position"].isin(position_filter)) & (df_copied["created_at"].between(start_date, end_date))]
  
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
        x = "id:N",
        y = "group_size:Q",
               #color = "id",
        tooltip = ["group_size", "id"]
    ).properties(
        title="Boxplot of Group Size by Setup",
        width=800,
        height=400
    )

    return box_plot


df = get_analytics()
logger.debug(f"Length of df : {len(df)}")
logger.debug(f"df columns : {df.columns}")
df["created_at"] = pd.to_datetime(df["created_at"])

st.sidebar.header("Filter")
ammo_filter = st.sidebar.multiselect(
    "Select ammo",
    options=df["name"].unique(),
    default=df["name"].unique(),
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
    value=(df["created_at"].min(), df["created_at"].max()),

    #on_change = filtering_data

)

filtered_df = filtering_data(df, ammo_filter, gear_filter, position_filter, start_date, end_date)

box_plot = create_boxplots(df)
metrics_col, boxplot_col = st.columns(2)
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

with metrics_container:
    st.metric("Mean Group Size", value = f"{mean_group_size:.2f}")

with boxplot_container:
    st.altair_chart(box_plot, use_container_width=True)
with plot_container:

    st.altair_chart(chart, use_container_width=True)

with st.expander("Details"):
    st.dataframe(filtered_df, use_container_width=True)

