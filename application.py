from flask import Flask
import threading
import visualization
import logging
import logging.handlers
from Backend import Backend
import mysql_setup.coronavirus_location as coronavirus_location
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
import datetime
import time
import json
import copy

UPDATE_TIME = 10  # 10AM UTC

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handler
LOG_FILE = 'web_app/log/application'
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILE, when="midnight", interval=1)
handler.suffix = "%Y-%m-%d.log"
handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

# cubes
corona_joined = None
county_cases = None
country_location_cube = None
location_cube = None
sex = None
age = None



def run_data_update():
    global corona_joined, county_cases, location_cube, country_location_cube, sex, age
    try:
        backend = Backend()
        backend.start_connection()
        corona_joined = backend.get_cube("corona_joined")
        county_cases = backend.get_cube("county_cases")
        location_cube = backend.get_cube(coronavirus_location.table_name)
        country_location_cube = country_location()
        sex = backend.get_cube("sex")
        age = backend.get_cube("age")
    except Exception as e:
        logger.error("Error fetching database: %s", e)
    schedule = datetime.datetime.now()
    while True:
        if datetime.datetime.now() >= schedule:
            logger.info("Updating database.")
            try:
                backend = Backend()
                backend.start_connection()
                backend.update_coronavirus_data()
                midnight_today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
                schedule = midnight_today + datetime.timedelta(days=1, hours=UPDATE_TIME)
                corona_joined = backend.get_cube("corona_joined")
                county_cases = backend.get_cube("county_cases")
                location_cube = backend.get_cube(coronavirus_location.table_name)
                country_location_cube = country_location()
                sex = backend.get_cube("sex")
                age = backend.get_cube("age")
                logger.info("Update succeed. Scheduled for %s UTC", schedule)
            except Exception as e:
                logger.error("Error updating database: %s", e)
        time.sleep(3600)


t1 = threading.Thread(name="Database", target=run_data_update)
t1.start()
app = Flask(__name__, static_folder="web_app/dist")

@app.route("/api/map")
def get_map():
    logger.info("Get map")
    tile_provider = get_provider(CARTODBPOSITRON)
    html = corona_joined.restriction("date", lambda x: x == datetime.date(2020, 4, 18)).destroy("date") \
        .restriction("country_region", lambda x: x == "Australia").restriction("longitude", lambda x: x != 0) \
        .visualize("map_html", "confirmed", tile_provider, False)
    return html

@app.route("/api/map/<date>/countries")
def get_country_map(date):
    tile_provider = get_provider(CARTODBPOSITRON)
    c = country_data(date)
    c = c.join(country_location_cube).pull("confirmed").pull("death")
    html = c.visualize("map_html", "confirmed", tile_provider, True)
    return html

@app.route("/api/map/<date>/<country_region>")
def get_state_map(date, country_region):
    tile_provider = get_provider(CARTODBPOSITRON)
    YY, MM, DD = date.split("-")
    c = corona_joined.restriction("date", lambda x:x==datetime.date(int(YY), int(MM), int(DD))).destroy("date")
    c = c.restriction("country_region", lambda x: x==country_region) 
    html = c.visualize("map_html", "confirmed", tile_provider, False)
    return html

@app.route("/api/map/<date>/<country_region>/<province_state>")
def get_county_map(date, country_region, province_state):
    tile_provider = get_provider(CARTODBPOSITRON)
    YY, MM, DD = date.split("-")
    if country_region == "US":
        c = county_cases.restriction("date", lambda x:x==datetime.date(int(YY), int(MM), int(DD))).destroy("date").restriction("longitude", lambda x: x != 0)
        c = c.restriction("province_state", lambda x:x==province_state)
    else:
        c = corona_joined.restriction("date", lambda x:x==datetime.date(int(YY), int(MM), int(DD))).destroy("date")
        c = c.restriction("country_region", lambda x: x==country_region).restriction("province_state", lambda x:x==province_state)
    html = c.visualize("map_html", "confirmed", tile_provider, False)
    return html

@app.route("/api/map/<date>/US/<province_state>/<county>")
def get_single_county_map(date, province_state, county):
    tile_provider = get_provider(CARTODBPOSITRON)
    YY, MM, DD = date.split("-")
    c = county_cases.restriction("date", lambda x:x==datetime.date(int(YY), int(MM), int(DD))).destroy("date").restriction("longitude", lambda x: x != 0)
    c = c.restriction("province_state", lambda x:x==province_state).restriction("county", lambda x:x==county)
    html = c.visualize("map_html", "confirmed", tile_provider, False)
    return html


def country_data(date):
    YY, MM, DD = date.split("-")
    c = corona_joined.restriction("date", lambda x:x==datetime.date(int(YY), int(MM), int(DD)))
    c = c.push("confirmed").push("death")
    c.cube = c.cube.drop(columns=["province_state", "date","latitude", "longitude","confirmed", "death"])
    # merge
    dimension_name = {"country_region":"country_region"}
    f = [
        lambda x: [x],
    ]
    felem = lambda x : x.sum()
    c = c.merge(felem, dimension_name, f)
    return c

def country_location():
    dimension_name = {"country_region":"country_region"}
    f = [
        lambda x: [x],
    ]
    felem = lambda x : x.mean()
    location = copy.deepcopy(location_cube)
    location = location.push("latitude").push("longitude")
    location.cube = location.cube.drop(columns=["province_state", "latitude", "longitude"])
    c = location.merge(felem, dimension_name, f)
    c = c.pull("latitude").pull("longitude")
    return c

@app.route("/api/daterange")
def date_range():
    return {"min": str(min(corona_joined.cube["date"])), "max": str(max(corona_joined.cube["date"]))}

@app.route("/api/<date>/countries")
def get_country_data(date):
    c = country_data(date)
    c = c.push("country_region")
    data = c.element.values.tolist()
    res = {}
    for confirmed, death, country in data:
        res[country] = {"confirmed":confirmed, "death":death}
    return json.dumps(res)

@app.route("/api/<date>/<country_region>")
def get_state_data(date, country_region):
    YY, MM, DD = date.split("-")
    c = corona_joined.restriction("date", lambda x:x==datetime.date(int(YY), int(MM), int(DD)))
    c = c.restriction("country_region", lambda x:x==country_region)
    c = c.push("confirmed").push("death").push("province_state")
    data = c.element.values.tolist()
    res = {}
    for confirmed, death, state in data:
        res[state] = {"confirmed":confirmed, "death":death}
    return json.dumps(res)

@app.route("/api/<date>/<country_region>/<province_state>")
def get_county_data(date, country_region,province_state):
    YY, MM, DD = date.split("-")
    c = county_cases.restriction("date", lambda x:x==datetime.date(int(YY), int(MM), int(DD)))
    c = c.restriction("province_state", lambda x:x==province_state)
    c = c.push("confirmed").push("death").push("county")
    data = c.element.values.tolist()
    res = {}
    for confirmed, death, county in data:
        res[county] = {"confirmed":confirmed, "death":death} 
    return json.dumps(res)

@app.route("/api/sex")
def get_sex():
    return {"data": [{s: d} for s, d in sex.cube.values]}

@app.route("/api/age")
def get_age():
    return {"data": [{s: d} for s, d in age.cube.values]}


@app.route("/")
def send_index():
    return app.send_static_file("index.html")


@app.route("/<path:path>")
def send_file(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    app.run()
