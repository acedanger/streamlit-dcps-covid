import pandas as pd, streamlit as st, get_cases as cvd
import plotly.express as px, plotly.graph_objects as go
from datetime import date
from os.path import exists
from re import template
from plotly.subplots import make_subplots

@st.cache(allow_output_mutation=True)
def get_covid_data():
    return pd.DataFrame(cvd.getCovid())


def set_dataframe_style(dataframe):
    # styles of displayed data frames (df*)
    cell_hover = {  # for row hover use <tr> instead of <td>
        'selector': 'td:hover',
        'props': [('background-color', '#ffffb3')]
    }
    index_names = {
        'selector': '.index_name',
        'props': 'font-style: italic; color: darkgrey; font-weight:normal;'
    }
    headers = {
        'selector': 'th:not(.index_name)',
        'props': 'background-color: #000066; color: white;'
    }

    style_df = dataframe.style
    style_df.set_table_styles([cell_hover, index_names, headers])
    style_df.set_table_styles([
        {'selector': 'th.col_heading', 'props': 'text-align: center;'},
        {'selector': 'th.col_heading.level0', 'props': 'font-size: 1.5em;'},
        {'selector': 'td', 'props': 'text-align: center; font-weight: bold;'},
    ], overwrite=False)

    return

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

yr_mn_val = df['date_time'].dt.strftime("%Y-%m").unique().tolist()
yr_mn = st.sidebar.multiselect(
    "Select the month:",
    options=yr_mn_val,
    default=yr_mn_val
)
weekdays_val = df['day_of_week'].unique()
dy = st.sidebar.multiselect(
    "Select the day of week:",
    options=weekdays_val,
    default=weekdays_val
)

# filtering based on what's selected in the sidebar
df_selection = df.query("day_of_week == @dy and yr_mn == @yr_mn")

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

cases_students = int(df[['students']].sum()[["students"]]) 
cases_staff = int(df[['staff']].sum()[["staff"]])

df_last_change = df[['students','staff']].tail(1)
last_change = {
    'students': df_last_change['students'].values[0],
    'staff': df_last_change['staff'].values[0]
}

avg = {
    'students': df[['students']].tail(7).mean().sum(),
    'staff': df[['staff']].tail(7).mean().sum(),
    'total': df[['students','staff']].tail(7).mean().sum(), 
}

df_month_summary = df[['yr','mn','students','staff','total']].groupby(by=['yr','mn']).sum()[['students','staff','total']]
set_dataframe_style(df_month_summary)
df_month_summary.rename(
            columns={
                'wk':'Week',
                'date':'Date',
                'students':'Students',
                'staff':'Staff'
            })

# mainpage
st.markdown("## 2021-2022 total cases")
summary_col1, summary_col2, summary_col3 = st.columns(3)
with summary_col1:
    "**Students**"
    st.markdown(f"{cases_students} (:arrow_up_small:{last_change['students']})")
with summary_col2:
    "**Staff**"
    st.markdown(f"{cases_staff} (:arrow_up_small:{last_change['staff']})")
with summary_col3:
    "**Total**"
    st.markdown(f"{cases_students + cases_staff} (:arrow_up_small:{last_change['students'] + last_change['staff']})")

st.markdown('## Metrics')
st.markdown('### 7 day rolling average')
st.dataframe()
st.markdown('### Total cases by month')
st.dataframe(df_month_summary)

# chart and raw data
st.markdown('---')
st.write("The [data](https://c19sitdash.azurewebsites.net/) is updated each weekday at approximately 8PM ET")
st.plotly_chart(fig, use_container_width=True)

expander_data = st.expander(label="Toggle data", expanded=False)
with expander_data:
    df_selection=df_selection[['wk','date','day_of_week','students','staff']].sort_values(by=['wk','date'], ascending=[False, True])
    df_selection=df_selection.rename(
            columns={
                'wk':'Week',
                'date':'Date',
                'day_of_week':'Weekday',
                'students':'Students',
                'staff':'Staff'
            })

    set_dataframe_style(df_selection)
    st.dataframe(df_selection)
 