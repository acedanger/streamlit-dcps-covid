import json, sys, requests, pandas as pd, json
from datetime import date, datetime
from dateutil import rrule

def getCovid():
    first_day_of_school = date(2021, 8, 10) # first day of school
    last_day_of_school = date(2022, 5, 31) # last day of school
    end_dt = date.today() if last_day_of_school > date.today() else last_day_of_school

    sch_yr_total_cases = 0
    sch_yr_total_students = 0
    sch_yr_total_staff = 0

    all_data = []

    prv_total = 0
    for mon in rrule.rrule(rrule.MONTHLY, dtstart=first_day_of_school.replace(day=1), until=end_dt):
        mon_total_cases = 0
        mon_total_students = 0
        mon_total_staff = 0
        yr = mon.strftime('%Y')
        mn = mon.strftime('%m')
        print(f"Processing {mn}/{yr}")
        url_api = f"https://jrapi-dev-2006.azurewebsites.net/api/sitdash/dashboard/publicreport?rc=&month={mn}&year={yr}"

        resp = requests.get(url_api)
        resp.encoding = 'utf-8-sig'

        api_data = json.loads(resp.text)
        results = api_data['Results']
        for res in results:
            dat = results[res]
            data_date = res[0:10]
            data_students = dat['StudentPositiveCount']
            data_staff = dat['StaffPositiveCount']
            data_ttl = dat['Total']

            mon_total_cases += data_ttl
            mon_total_staff += data_staff
            mon_total_students += data_students
            if(data_ttl > 0):
                all_data.append(
                    {
                        'date': data_date,
                        'students': data_students,
                        'staff': data_staff,
                        'total': data_ttl,
                        'perc_diff': (data_ttl - prv_total) / data_ttl,
                        'day_of_week': datetime.strptime(data_date, '%Y-%m-%d').strftime('%A')
                    }
                )
                prv_total = data_ttl

        sch_yr_total_cases += mon_total_cases
        sch_yr_total_students += mon_total_students
        sch_yr_total_staff += mon_total_staff

    return all_data

if __name__ == "__main__":
    allTheCovids = getCovid()

    if len(sys.argv) == 1:
        sys.exit()

    if sys.argv[1].lower()[0] != 'y':
        sys.exit()
