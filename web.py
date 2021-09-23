from re import template
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date
from os.path import exists
import get_cases as cvd

from plotly.subplots import make_subplots

# csv exists in the same dir as this script
csv = "dcps_dashboard_data.csv"
df = pd.read_csv(csv) if exists(f"{csv}") else pd.DataFrame(cvd.getCovid())

st.set_page_config(
    page_title="DCPS Reported cases of COVID-19",
    page_icon=":school:",
    layout="wide"
)
st.title(f":school: Reported COVID-19 cases, as of {date.today().strftime('%m/%d/%Y')}")
st.markdown("---")
st.markdown("##")

# mn_val = pd.DatetimeIndex(df['date']).month.unique().all()
# mn = st.sidebar.multiselect(
#     "Select the month:",
#     options=mn_val,
#     default=mn_val
# )
weekdays = df['day_of_week'].unique()
dy = st.sidebar.multiselect(
    "Select the day of week:",
    options=weekdays,
    default=weekdays
)

df['date_time'] = pd.to_datetime(df["date"], errors='coerce')
df['yr'] = df['date_time'].dt.year
df['mn'] = df['date_time'].dt.month
df['wk'] = df['date_time'].dt.isocalendar().week

# filtering based on what's selected in the sidebar
df_selection = df.query("day_of_week == @dy")

cases_by_student = df_selection.groupby(by=['date']).sum()[['students']].reset_index()

# create a line chart for the student data
fig_students = px.line(
    cases_by_student,
    x="date",
    y="students"
)

# create a line chart for the student data
cases_by_staff = df_selection.groupby(by=['date']).sum()[['staff']].reset_index()
fig_staff = px.line(
    cases_by_staff,
    x="date",
    y="staff"
)
fig_staff.update_traces(yaxis="y2")

# combine the two line charts
fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_traces(fig_students.data + fig_staff.data) 
fig['data'][0]['showlegend']=True
fig['data'][0]['name']='Students'
fig['data'][1]['showlegend']=True
fig['data'][1]['name']='Staff'
fig.layout.xaxis.title = "Date"
fig.layout.yaxis.title = "Students"
fig.layout.yaxis2.title = "Staff"
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1
))
fig.update_layout(showlegend = True, hovermode='x')
# change the color of each series
fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

# mainpage
st.plotly_chart(fig)
st.markdown("---")
st.title("Data")
st.dataframe(df_selection[['date','day_of_week','students','staff']])
st.markdown("---")