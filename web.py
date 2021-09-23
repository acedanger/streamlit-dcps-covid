from re import template
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date
from os.path import exists
import get_cases as cvd

# csv exists in the same dir as this script
csv = "dcps_dashboard_data.csv"
df = pd.read_csv(csv) if exists(f"{csv}") else pd.DataFrame(cvd.getCovid())

st.set_page_config(page_title="DCPS Reported cases of COVID-19",
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

cases_by_student = df.groupby(by=['date']).sum()[['students']]
cases_by_staff = df.groupby(by=['date']).sum()[['staff']]

figure_students = px.bar(
    cases_by_student,
    x=cases_by_student.index,
    y="students"
)

figure_staff = px.bar(
    cases_by_staff,
    x=cases_by_staff.index,
    y="staff",
    template="plotly_white"
)
figure_staff.update_traces(textposition="outside")

# mainpage
col_left, col_right = st.columns(2)
with col_left:
    st.subheader("Student cases")
    st.plotly_chart(figure_students)   

with col_left:
    st.subheader("Staff cases")
    st.plotly_chart(figure_staff) 

st.markdown("---")
st.title("[Filtered by sidebar] Raw data")
st.dataframe(df_selection[['date','day_of_week','students','staff']])
st.markdown("---")