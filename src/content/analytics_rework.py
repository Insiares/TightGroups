# pages/analytics_dashboard.py
import streamlit as st
from streamlit_elements import elements,  mui, nivo, dashboard
import requests
from src.config import Config, logger
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple

class AnalyticsDashboard:
    def __init__(self):
        self.layout = [
            # Metrics card
            {"i": "metrics", "x": 0, "y": 0, "w": 6, "h": 2},
            # Line chart
            {"i": "line_chart", "x": 6, "y": 0, "w": 6, "h": 4},
            # Box plot
            {"i": "box_plot", "x": 0, "y": 2, "w": 6, "h": 4},
            # Details table
            {"i": "details", "x": 0, "y": 6, "w": 12, "h": 4},
        ]

       

        self.init_filters()
        self.load_data()
        logger.debug(f"Loaded data for user {st.session_state.user_id}")

    def init_filters(self):
        """Initialize filter values"""
        if 'ammo_filter' not in st.session_state:
            st.session_state.ammo_filter = []
            st.session_state.gear_filter = []
            st.session_state.position_filter = []
            st.session_state.start_date = datetime(2023, 1, 1)
            st.session_state.end_date = datetime(2025, 12, 31)
            st.session_state.group_by = "Day"
            logger.debug(f"filter inited")

    def get_analytics(self) -> pd.DataFrame:
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

    def filter_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply filters to the dataframe"""
        logger.debug(f"Filtering data")
        return df[
            (df["name"].isin(st.session_state.ammo_filter)) &
            (df["gear"].isin(st.session_state.gear_filter)) &
            (df["position"].isin(st.session_state.position_filter)) &
            (df["created_at"].between(
                pd.to_datetime(st.session_state.start_date),
                pd.to_datetime(st.session_state.end_date)
            ))
        ]

    def group_data_by_date(self, filtered_df: pd.DataFrame) -> pd.DataFrame:
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
        logger.debug(f"Grouped data: {grouped}")
        return grouped

    def create_sidebar_filters(self, df: pd.DataFrame):
        """Create sidebar filters"""
        logger.debug(f"creating filter")
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

    def render_metrics_card(self, filtered_df: pd.DataFrame):
        """Render metrics card with mean group size"""
        mean_group_size = filtered_df["group_size"].mean()
        total_shots = len(filtered_df)
        
        return mui.Card(
            mui.CardContent(
                mui.Stack(
                    mui.Typography(
                        f"Mean Group Size: {mean_group_size:.2f}",
                        variant="h6"
                    ),
                    mui.Typography(
                        f"Total Shots: {total_shots}",
                        variant="h6"
                    ),
                    spacing=2
                )
            ),
            sx={"backgroundColor": "rgba(0, 0, 0, 0.1)"}
        )

    def render_line_chart(self, filtered_df: pd.DataFrame):
        """Render line chart for group size over time with grouping"""
        grouped_df = self.group_data_by_date(filtered_df)
        
        data = [
            {
                "id": "Mean Group Size",
                "data": [
                    {
                        "x": row["created_at"].strftime("%Y-%m-%d"),
                        "y": row["mean_group_size"],
                        "min": row["min_group_size"],
                        "max": row["max_group_size"],
                        "count": row["count"]
                    }
                    for _, row in grouped_df.iterrows()
                ]
            }
        ]
        
        return nivo.Line(
            data=data,
            margin={"top": 50, "right": 50, "bottom": 50, "left": 50},
            xScale={"type": "point"},
            yScale={"type": "linear"},
            axisBottom={
                "tickRotation": -45,
                "legend": "Date"
            },
            axisLeft={
                "legend": "Group Size"
            },
            pointSize=8,
            pointColor="white",
            pointBorderWidth=2,
            pointBorderColor={"from": "serieColor"},
            enableArea=True,
            areaOpacity=0.1,
            enableGridX=False,
            enableGridY=True,
            useMesh=True,
            tooltip=lambda point: (
                f"Date: {point['data']['x']}\n"
                f"Mean: {point['data']['y']:.2f}\n"
                f"Min: {point['data']['min']:.2f}\n"
                f"Max: {point['data']['max']:.2f}\n"
                f"Shots: {point['data']['count']}"
            ),
            theme={
                "background": "transparent",
                "textColor": "white",
                "grid": {"line": {"stroke": "#444"}}
            }
        )

    def render_box_plot(self, filtered_df: pd.DataFrame):
        """Render box plot for group sizes"""
        data = [
            {
                "group": gear,
                "values": filtered_df[filtered_df["gear"] == gear]["group_size"].tolist()
            }
            for gear in filtered_df["gear"].unique()
        ]

        return nivo.BoxPlot(
            data=data,
            margin={"top": 50, "right": 50, "bottom": 50, "left": 50},
            minValue=min(filtered_df["group_size"]),
            maxValue=max(filtered_df["group_size"]),
            theme={
                "background": "transparent",
                "textColor": "white",
                "grid": {"line": {"stroke": "#444"}}
            }
        )

    def load_data(self):
        """Load and process data"""
        self.df = self.get_analytics()
        if len(self.df) == 0:
            st.error("No data found")
            return False
        
        self.df["created_at"] = pd.to_datetime(self.df["created_at"])
        logger.debug(f"Loaded data for user {st.session_state.user_id}")
        return True

    def render_dashboard(self):
        """Render the complete dashboard"""
        if not hasattr(self, 'df') or len(self.df) == 0:
            st.error("No data found")
            logger.error("No data found")
            return

        self.create_sidebar_filters(self.df)
        filtered_df = self.filter_data(self.df)

        with elements("dashboard"):
            # Create dashboard with grid layout
            with dashboard.Grid(self.layout):
                # Metrics card
                with mui.Paper(key="metrics", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
                    self.render_metrics_card(filtered_df)
                
                # Line chart
                with mui.Paper(key="line_chart", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
                    self.render_line_chart(filtered_df)
                    logger.debug(f"Rendered line chart for user {st.session_state.user_id}")
                # Box plot
                with mui.Paper(key="box_plot", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
                    self.render_box_plot(filtered_df)
                 
                # Details table
                with mui.Paper(key="details", sx={"p": 2, "display": "flex", "flexDirection": "column"}):
                    formatted_df = filtered_df.copy()
                    formatted_df['created_at'] = formatted_df['created_at'].dt.strftime('%Y-%m-%d %H:%M:%S')

                    mui.DataGrid(
                    columns=[{"field": col, "headerName": col.title()} for col in formatted_df.columns],
                    rows=formatted_df.to_dict('records'),
                    pageSize=5,
                autoHeight=True
            )

st.title("Analytics Dashboard")
mu_dashboard = AnalyticsDashboard()
mu_dashboard.render_dashboard()
