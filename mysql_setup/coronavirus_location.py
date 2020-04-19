# Write location to SQL
import os
import pandas
import mysql_setup.jhu_data as jhu_data


table_name = "location"
output_name = "corona_location.sql"

def main():
    jhu_data.fetch_data()

    dir_prefix = os.path.join(os.getcwd(), "mysql_setup", "COVID-19", "csse_covid_19_data")
    daily_reports_dir = os.path.join(dir_prefix, "csse_covid_19_daily_reports")
    time_series_dir = os.path.join(dir_prefix, "csse_covid_19_time_series")

    out_file = open(os.path.join(os.getcwd(), "mysql_setup", output_name), "w")
    create_table = """CREATE TABLE {} (
     province_state VARCHAR (50),
     country_region VARCHAR (50) NOT NULL,
     latitude FLOAT NOT NULL,
     longitude FLOAT NOT NULL,
     KEY (province_state, country_region)
    );
    """.format(table_name).replace("\n", "")
    out_file.write(create_table + "\n")

    #######################################################################################################################
    # US states locations
    #######################################################################################################################
    data = pandas.read_csv(os.path.join(daily_reports_dir, "03-21-2020.csv"))
    us_data = data[data.get("Country/Region") == "US"]
    us_data = us_data[us_data.get("Province/State") != "US"]
    for ind in us_data.index:
        out_file.write("INSERT INTO {} VALUES ('{}', '{}', {}, {});\n".format(table_name, us_data.get("Province/State")[ind],
                                                                              us_data.get("Country/Region")[ind],
                                                                              us_data.Latitude[ind], us_data.Longitude[ind]))

    #######################################################################################################################
    # Global locations
    #######################################################################################################################
    confirmed_filename = os.path.join(time_series_dir, "time_series_covid19_confirmed_global.csv")
    confirmed_data = pandas.read_csv(confirmed_filename)

    for ind in confirmed_data.index:
        latitude = confirmed_data.Lat[ind]
        longitude = confirmed_data.Long[ind]
        country = confirmed_data.get("Country/Region")[ind]
        state = confirmed_data.get("Province/State")[ind]
        if pandas.isnull(state):
            state = "NULL"
        else:
            state = "'{}'".format(state)
        if not (latitude == 0 and longitude == 0):
            out_file.write("INSERT INTO {0} VALUES ({1}, '{2}', {3}, {4});\n".format(table_name, state,
                                                                                            country.replace("'", "\\'"),
                                                                                            latitude, longitude))
    out_file.close()
