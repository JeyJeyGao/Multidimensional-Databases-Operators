# Reorganize Coronavirus data and write data to SQL
# Before running the code, make sure clone the JHU Coronavirus data
# git clone https://github.com/CSSEGISandData/COVID-19.git

import os
from datetime import date, timedelta
from states import states_dict
import pandas

table_name = "cases"
output_name = "corona.sql"

out_file = open(output_name, "w")
print("Writing data to SQL...")

create_table = """CREATE TABLE {} (
 province_state VARCHAR (50),
 country_state VARCHAR (50) NOT NULL,
 date DATE NOT NULL,
 confirmed INT NOT NULL,
 death INT NOT NULL,
 PRIMARY KEY (province_state, country_state, date)
);
""".format(table_name)
out_file.write(create_table + "\n")

dir_prefix = os.path.join("COVID-19", "csse_covid_19_data")

# used to retrieve US result
daily_reports_dir = os.path.join(dir_prefix, "csse_covid_19_daily_reports")
print("Writing US data...")
#######################################################################################################################
# US Data from 2020-01-22 to 2020-01-31
#######################################################################################################################
cur_date = date(2020, 1, 22)
while cur_date <= date(2020, 1, 31):
    f = os.path.join(daily_reports_dir, cur_date.strftime("%m-%d-%Y") + ".csv")
    data = pandas.read_csv(f)
    us_data = data[data.get("Country/Region") == "US"]
    for ind in us_data.index:
        if cur_date != date(2020, 1, 24):
            "Date: {}, State: {}, Confirmed: {}, Death: {}".format(cur_date, us_data.get("Province/State")[ind],
                                                                         int(us_data.Confirmed[ind]),
                                                                         us_data.Deaths[ind] if \
                                                                             not pandas.isnull(us_data.Deaths[ind]) else 0)
            out_file.write("INSERT INTO {4} VALUES ('{1}', 'US', '{0}', {2}, {3});\n".format(cur_date, us_data.get("Province/State")[ind],
                                                                                  int(us_data.Confirmed[ind]),
                                                                                  us_data.Deaths[ind] if \
                                                                                      not pandas.isnull(us_data.Deaths[ind]) else 0, table_name))
        else:
            out_file.write("INSERT INTO {4} VALUES ('{1}', 'US', '{0}', {2}, {3});\n".format(cur_date, us_data.get("Province/State")[ind] if \
                us_data.get("Province/State")[ind] != "Chicago" else "Illinois",
                                                                         int(us_data.Confirmed[ind]),
                                                                         us_data.Deaths[ind] if \
                                                                             not pandas.isnull(us_data.Deaths[ind]) else 0, table_name))

    cur_date += timedelta(1)

#######################################################################################################################
# US Data from 2020-02-01 to 2020-03-09
#######################################################################################################################
cur_date = date(2020, 2, 1)
while cur_date <= date(2020, 3, 9):
    f = os.path.join(daily_reports_dir, cur_date.strftime("%m-%d-%Y") + ".csv")
    data = pandas.read_csv(f)
    us_data = data[data.get("Country/Region") == "US"]
    reorder = {"Diamond Princess": [0, 0], "Grand Princess": [0, 0]}
    for ind in us_data.index:
        state = us_data.get("Province/State")[ind]
        if "Diamond Princess" in state:
            reorder["Diamond Princess"][0] += us_data.Confirmed[ind]
            reorder["Diamond Princess"][1] += us_data.Deaths[ind]
        elif "Grand Princess" in state:
            reorder["Grand Princess"][0] += us_data.Confirmed[ind]
            reorder["Grand Princess"][1] += us_data.Deaths[ind]
        else:
            state_name = states_dict[state.replace(".", "").strip()[-2:].upper()]
            if state_name in reorder:
                reorder[state_name][0] += us_data.Confirmed[ind]
                reorder[state_name][1] += us_data.Deaths[ind]
            else:
                reorder[state_name] = [us_data.Confirmed[ind], us_data.Deaths[ind]]
    for s in reorder:
        out_file.write("INSERT INTO {4} VALUES ('{1}', 'US', '{0}', {2}, {3});\n".format(cur_date, s, reorder[s][0], reorder[s][1], table_name))
    cur_date += timedelta(1)

#######################################################################################################################
# US Data from 2020-03-10 to 2020-03-21
#######################################################################################################################
cur_date = date(2020, 3, 10)
while cur_date <= date(2020, 3, 21):
    f = os.path.join(daily_reports_dir, cur_date.strftime("%m-%d-%Y") + ".csv")
    data = pandas.read_csv(f)
    us_data = data[data.get("Country/Region") == "US"]
    us_data = us_data[us_data.get("Province/State") != "US"]
    for state in us_data.index:
        out_file.write("INSERT INTO {4} VALUES ('{1}', 'US', '{0}', {2}, {3});\n".format(cur_date, us_data.get("Province/State")[state],
                                                                     us_data.Confirmed[state],us_data.Deaths[state], table_name))
    cur_date += timedelta(1)

#######################################################################################################################
# US Data from 2020-03-22 to yesterday
#######################################################################################################################
cur_date = date(2020, 3, 22)
while cur_date < date.today():
    f = os.path.join(daily_reports_dir, cur_date.strftime("%m-%d-%Y") + ".csv")
    data = pandas.read_csv(f)
    us_data = data[data.get("Country_Region") == "US"]
    us_data = us_data[us_data.get("Province_State") != "Recovered"]
    us_data = us_data.groupby(["Province_State"]).sum()

    for state in us_data.index:
        out_file.write("INSERT INTO {4} VALUES ('{1}', 'US', '{0}', {2}, {3});\n".format(cur_date, state, us_data.Confirmed[state],
                                                                     us_data.Deaths[state], table_name))
    cur_date += timedelta(1)

#######################################################################################################################
# Global Data
#######################################################################################################################
print("Writing global data...")
time_series_dir = os.path.join(dir_prefix, "csse_covid_19_time_series")
confirmed_filename = os.path.join(time_series_dir, "time_series_covid19_confirmed_global.csv")
death_filename = os.path.join(time_series_dir, "time_series_covid19_deaths_global.csv")

confirmed_data = pandas.read_csv(confirmed_filename)
death_data = pandas.read_csv(death_filename)

for ind in confirmed_data.index:
    cur_date = date(2020, 1, 22)
    while cur_date < date.today():
        d = cur_date.strftime("%m/%d/%y").lstrip("0").replace("/0", "/")
        confirmed = confirmed_data.get(d)[ind]
        death = death_data.get(d)[ind]
        country = confirmed_data.get("Country/Region")[ind]
        if not (confirmed == 0 and death == 0):
            state = confirmed_data.get("Province/State")[ind]
            if pandas.isnull(state):
                state = "NULL"
            else:
                state = "'{}'".format(state)
            out_file.write("INSERT INTO {0} VALUES ({1}, '{2}', '{3}', {4}, {5});\n".format(table_name, state, country.replace("'", "\\'"),
                                                                                     cur_date, confirmed, death))
        cur_date += timedelta(1)

out_file.close()
print("Finished writing.")