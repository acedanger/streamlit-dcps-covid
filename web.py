import pandas as pd, streamlit as st, get_cases as cvd
import plotly.express as px, plotly.graph_objects as go
from datetime import date
from os.path import exists
from re import template
from plotly.subplots import make_subplots

def get_covid_data():
    return pd.DataFrame(cvd.getCovid())

# dataframe styling
index_names = {
    'selector': '.index_name',
    'props': 'font-style: italic; color: darkgrey; font-weight:normal;'
}
headers = {
    'selector': 'th:not(.index_name)',
    'props': 'background-color: #000066; color: white;'
}

st.set_page_config(
    page_title="DCPS Reported cases of COVID-19",
    page_icon=":school:",
    # initial_sidebar_state="collapsed",  # Can be "auto", "expanded", "collapsed"
    layout="wide" # can be "wide", "centered"
)
st.title(f":school: Reported COVID-19 cases, as of {date.today().strftime('%m/%d/%Y')}")

df = get_covid_data()

df['date_time'] = pd.to_datetime(df["date"], errors='coerce')
df['yr'] = df['date_time'].dt.year
df['mn'] = df['date_time'].dt.month
df['wk'] = df['date_time'].dt.isocalendar().week
df['yr_mn'] = df['date_time'].dt.strftime("%Y-%m")

df_last_change = df[['students','staff']].tail(1)
last_change = {
    'students': df_last_change['students'].values[0],
    'staff': df_last_change['staff'].values[0]
}

rolling_average = {
    'Current': {'Students': df[['students']].tail(7).mean().sum(),
                'Staff': df[['staff']].tail(7).mean().sum()
    },
    # I want 7 of the last 8 dates so I can calculate the change in the 7 day rolling average 
    #   .tail(8) keeps the last 8 rows
    #   .loc[:-1] removes the last row
    'Previous': {'Students': df[['students']].tail(8).iloc[:-1].mean().sum(),
                'Staff': df[['staff']].tail(8).iloc[:-1].mean().sum()
    }
}

df_month_summary = df[['yr','mn','students','staff','total']].groupby(by=['yr','mn']).sum()[['students','staff','total']]
df_month_summary.rename(
            columns={
                'wk':'Week',
                'date':'Date',
                'students':'Students',
                'staff':'Staff'
            })

# mainpage
st.markdown("## 2021-2022 total cases")

cases_students = int(df[['students']].sum()[["students"]]) 
cases_staff = int(df[['staff']].sum()[["staff"]])

summary_col1, summary_col2, summary_col3 = st.columns(3)
with summary_col1:
    st.metric(label='Student cases', value=cases_students, delta=int(last_change['students']))
with summary_col2:
    st.metric(label='Staff cases', value=cases_staff, delta=int(last_change['staff']))
with summary_col3:
    st.metric(label='Total cases', value=cases_students + cases_staff, delta=int(last_change['students'] + last_change['staff']))

st.markdown('### 7 day rolling average')

df_rolling_average_curr = pd.DataFrame.from_dict(rolling_average['Current'], orient='index', columns=['Average'])
df_rolling_average_prev = pd.DataFrame.from_dict(rolling_average['Previous'], orient='index', columns=['Average'])

average_curr = round(float(df_rolling_average_curr[['Average']].sum()), 2)
average_prev = round(float(df_rolling_average_prev[['Average']].sum()), 2)

st.metric(label='Average', value=average_curr, delta=average_curr-average_prev)

st.markdown('### Total cases by month')
st.dataframe(
    df_month_summary.style.set_table_styles(
            [index_names, headers,
                {'selector': 'th.col_heading', 'props': 'text-align: center;'},
                {'selector': 'th.col_heading.level0', 'props': 'font-size: 1em;'},
                {'selector': 'td', 'props': 'text-align: center; font-weight: bold;'}
            ], overwrite=False)
)

# chart and raw data
st.markdown('---')

# filtering based on what's selected in the sidebar
container_filter = st.container()
select_all_yr_mn = st.checkbox('Select all months')
select_all_day = st.checkbox('Select all days')

yr_mn_all = df['date_time'].dt.strftime("%Y-%m").unique().tolist()
yr_mn_default = df['date_time'].tail(1).dt.strftime("%Y-%m").tolist()
sel_yr_mn = yr_mn_all if select_all_yr_mn else yr_mn_default
yr_mn = st.multiselect("Choose month:", options=yr_mn_all, default=sel_yr_mn)

day_of_week_options = df['day_of_week'].unique().tolist()
day_of_week = st.multiselect("Choose day of week:", options=day_of_week_options, default=day_of_week_options)


df_selection = df.query("yr_mn == @yr_mn and day_of_week == @day_of_week")

cases_by_student = df_selection.groupby(by=['date']).sum()[['students']].reset_index()
cases_by_staff = df_selection.groupby(by=['date']).sum()[['staff']].reset_index()

# create a line chart for the student and staff data
fig_students = px.line(cases_by_student, x="date", y="students")
fig_staff = px.line(cases_by_staff, x="date", y="staff")

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
fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
fig.update_layout(showlegend = True, hovermode='x') # hovermode='x' means to show values from both series

# change the color of each series
fig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))

st.write("The [data](https://c19sitdash.azurewebsites.net/) is updated each weekday at approximately 8PM ET")
st.plotly_chart(fig, use_container_width=True)

expander_data = st.expander(label="Toggle data", expanded=True)
with expander_data:
    df_selection=df_selection[['wk','day_of_week','date','students','staff','total']].sort_values(by=['wk','date'], ascending=[False, True])
    df_selection=df_selection.rename(
            columns={
                'wk':'Week',
                'date':'Date',
                'day_of_week':'Weekday',
                'students':'Students',
                'staff':'Staff',
                'total':'Total'
            })

    st.table(
        df_selection.style.set_table_styles(
            [index_names, headers,
                {'selector': 'th.col_heading.level0', 'props': 'font-size: 1em;'},
                {'selector': 'td', 'props': 'text-align: center; font-weight: bold;'}
            ], overwrite=False)
    )
 