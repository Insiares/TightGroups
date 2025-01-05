from os import wait
import streamlit as st 
import requests
import pandas as pd 
from streamlit_elements import elements,  mui, nivo, dashboard
from src.config import Config, logger
from datetime import datetime
from typing import Dict, List, Tuple

st.title("Analytics Dashboard")

logger.debug(f"Analytics Dashboard")

def load_data():
    """Fetch analytics data from backend"""
    try:
        backend_url = Config.BACKEND_URL
        headers = {"Content-Type": "application/json"}
        response = requests.get(
            f"{backend_url}/scores/{st.session_state.user_id}/",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Accessed analytics for user {st.session_state.user_id}")
            return pd.DataFrame(data)
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error: {e}")
        return pd.DataFrame()

def init_filters():
        """Initialize filter values"""
        if 'ammo_filter' not in st.session_state:
            st.session_state.ammo_filter = []
            st.session_state.gear_filter = []
            st.session_state.position_filter = []
            st.session_state.start_date = datetime(2023, 1, 1)
            st.session_state.end_date = datetime(2025, 12, 31)
            st.session_state.group_by = "Day"

def filter_data(df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to the dataframe"""
        df["created_at"] = pd.to_datetime(df["created_at"])
        return df[
            (df["name"].isin(st.session_state.ammo_filter)) &
            (df["gear"].isin(st.session_state.gear_filter)) &
            (df["position"].isin(st.session_state.position_filter)) &
            (df["created_at"].between(
                pd.to_datetime(st.session_state.start_date),
                pd.to_datetime(st.session_state.end_date)
            ))
        ]

def group_data_by_date(filtered_df: pd.DataFrame) -> pd.DataFrame:
        """Group data based on selected time period"""
        grouping_map = {
            "Day": "D",
            "Week": "W",
            "Month": "M"
        }
        
        grouped = filtered_df.groupby(
            pd.Grouper(key='created_at', freq=grouping_map[st.session_state.group_by])
        ).agg({
            'group_size': ['mean', 'min', 'max', 'count']
        }).reset_index()
        
        grouped.columns = ['created_at', 'mean_group_size', 'min_group_size', 'max_group_size', 'count']
        return grouped

def create_sidebar_filters(df: pd.DataFrame):
        """Create sidebar filters"""
        st.sidebar.header("Filters")
        
        st.session_state.ammo_filter = st.sidebar.multiselect(
            "Select ammo",
            options=df["name"].unique(),
            default=df["name"].unique()
        )

        st.session_state.gear_filter = st.sidebar.multiselect(
            "Select gear",
            options=df["gear"].unique(),
            default=df["gear"].unique()
        )

        st.session_state.position_filter = st.sidebar.multiselect(
            "Select position",
            options=df["position"].unique(),
            default=df["position"].unique()
        )

        st.session_state.start_date, st.session_state.end_date = st.sidebar.date_input(
            "Select Date Range",
            value=(df["created_at"].min(), df["created_at"].max())
        )

        st.session_state.group_by = st.sidebar.selectbox(
            "Group data by",
            options=["Day", "Week", "Month"],
            index=0
        )

init_filters()
df = load_data()
create_sidebar_filters(df)
filtered_df = filter_data(df)
formatted_df = filtered_df.copy()
formatted_df['created_at'] = formatted_df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

with elements("dashboard"):
    layout = [
        dashboard.Item("metrics", 0,0, 6, 2),
        dashboard.Item("line_chart", 6,0, 6, 2),
        dashboard.Item("box_plot", 0,2, 6, 2),
        dashboard.Item("details", 6,2, 6, 2)
    ]
    with dashboard.Grid(layout):
        with mui.Card(key="metrics", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
            # Display metrics cards
            mui.CardContent(
                mui.Stack(
                    mui.Typography(
                        f"Mean Group Size: {filtered_df['group_size'].mean():.2f}",
                        variant="h6"
                    ),
                    mui.Typography(
                        f"Total Shots: {len(filtered_df)}",
                        variant="h6"
                    ),
                    spacing=2
                )
            )
        #
        # with mui.Box(key="line_chart", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
        #
        #     line_chart_data = [
        #         {
        #             "id": "Group Size",
        #             "data": formatted_df.apply(
        #                 lambda row: {
        #                     "x": row["created_at"], "y": row["group_size"]},
        #                 axis=1
        #             ).tolist(),
        #         }
        #     ]
        #
        #     nivo.LineChart(
        #         data=line_chart_data,  # Ensure this is properly formatted
        #         xScale={"type": "time", "format": "%Y-%m-%d", "precision": "day"},
        #         yScale={"type": "linear", "min": "auto", "max": "auto"},
        #         axisBottom={"format": "%b %d", "legend": "Date", "legendPosition": "middle", "legendOffset": 36},
        #         axisLeft={"legend": "Group Size", "legendPosition": "middle", "legendOffset": -40},
        #         margin={"top": 50, "right": 110, "bottom": 50, "left": 60},
        #     )
        # with mui.Paper(key="box_plot", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
        #     nivo.BoxPlot(
        #         data=group_data_by_date(filtered_df),
        #         index="created_at",
        #         value="group_size"
        #     )
        with mui.Paper(key="details", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
            mui.DataGrid(
                columns=[
                    {"field": "created_at", "headerName": "Date", "flex": 1},
                    {"field": "group_size", "headerName": "Group Size", "flex": 1},
                    {"field": "name", "headerName": "Ammo", "flex": 1},
                    {"field": "gear", "headerName": "Gear", "flex": 1},
                    {"field": "position", "headerName": "Position", "flex": 1},
                ],
                rows=formatted_df.to_dict('records')
            )
