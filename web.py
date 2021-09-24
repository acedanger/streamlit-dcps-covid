import pandas as pd, streamlit as st, plotly.express as px, get_cases as cvd
from datetime import date
from os.path import exists
from re import template
from plotly.subplots import make_subplots

@st.cache(allow_output_mutation=True)
def get_covid_data():
    st.write("Cache miss: get_covid_data ran")
    return pd.DataFrame(cvd.getCovid())

st.set_page_config(
    page_title="DCPS Reported cases of COVID-19",
    page_icon=":school:",
    layout="wide"
)
st.title(f":school: Reported COVID-19 cases, as of {date.today().strftime('%m/%d/%Y')}")

df = get_covid_data()

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
fig.layout.xaxis.title = "Date"
fig.layout.yaxis.title = "Students"
fig.layout.yaxis2.title = "Staff"

# this somehow makes the legend show up, there has to be a better way to do this
fig['data'][0]['showlegend']=True
fig['data'][0]['name']='Students'
fig['data'][1]['showlegend']=True
fig['data'][1]['name']='Staff'

# change the location of the legend
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

cases_students = int(df.sum()[["students"]]) 
cases_staff = int(df.sum()[["staff"]])

df_last_change = df[['students','staff']].tail(1)
last_change = {
    'students': df_last_change['students'].values[0],
    'staff': df_last_change['staff'].values[0]
}
# mainpage
st.markdown("## 2021-2022 total cases")
col1, col2, col3 = st.columns(3)
with col1:
    "**Students**"
    st.markdown(f"{cases_students} (:arrow_up_small:{last_change['students']})")
with col2:
    "**Staff**"
    st.markdown(f"{cases_staff} (:arrow_up_small:{last_change['staff']})")
with col3:
    "**Total**"
    st.markdown(f"{cases_students + cases_staff} (:arrow_up_small:{last_change['students'] + last_change['staff']})")
st.markdown('---')
# chart and raw data
st.plotly_chart(fig)

df_selection=df_selection[['wk','date','day_of_week','students','staff']].sort_values(by=['wk','date'], ascending=[False, True])
df_selection=df_selection.rename(
        columns={
            'wk':'Week',
            'date':'Date',
            'day_of_week':'Weekday',
            'students':'Students',
            'staff':'Staff'
        })
st.dataframe(df_selection)
st.write("The [data](https://c19sitdash.azurewebsites.net/) is updated each weekday at around 8PM ET")