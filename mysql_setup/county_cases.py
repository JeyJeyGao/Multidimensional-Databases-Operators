import os
from datetime import date, timedelta
import pandas


table_name = "county_cases"
output_name = "county_cases.sql"


def main():
    out_file = open(os.path.join(os.getcwd(), "mysql_setup", output_name), "w")

    create_table = """CREATE TABLE {} (
     county VARCHAR (50) NOT NULL,
     province_state VARCHAR (50) NOT NULL,
     date DATE NOT NULL,
     confirmed INT NOT NULL,
     death INT NOT NULL,
     longitude FLOAT NOT NULL,
     latitude FLOAT NOT NULL,
     KEY (county, province_state, date)
    );
    """.format(table_name).replace("\n", "")
    out_file.write(create_table + "\n")

    dir_prefix = os.path.join(os.getcwd(), "mysql_setup", "COVID-19", "csse_covid_19_data")

    # used to retrieve US result
    daily_reports_dir = os.path.join(dir_prefix, "csse_covid_19_daily_reports")
    cur_date = date(2020, 3, 22)
    while cur_date < date.today():
        f = os.path.join(daily_reports_dir, cur_date.strftime("%m-%d-%Y") + ".csv")
        data = pandas.read_csv(f)
        us_data = data[data.get("Country_Region") == "US"]
        us_data = us_data[us_data.get("Province_State") != "Recovered"]
        us_data = us_data[pandas.notnull(us_data.get("Admin2"))]

        for county in us_data.index:
            out_file.write(
                "INSERT INTO {0} VALUES ('{1}', '{2}', '{3}', {4}, {5}, {6}, {7});\n"
                    .format(table_name, us_data["Admin2"][county].replace("'", "\\'"),
                            us_data["Province_State"][county], cur_date, us_data["Confirmed"][county],
                            us_data["Deaths"][county],
                            us_data["Long_"][county] if pandas.notnull(us_data["Long_"][county]) else 0,
                            us_data["Lat"][county] if pandas.notnull(us_data["Lat"][county]) else 0))
        cur_date += timedelta(1)
    out_file.close()
