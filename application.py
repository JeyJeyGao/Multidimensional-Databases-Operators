from flask import Flask
import threading
import visualization
import logging
import logging.handlers
from Backend import Backend
from bokeh.tile_providers import CARTODBPOSITRON, get_provider
import datetime
import time


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


def run_data_update():
    global corona_joined, county_cases
    try:
        backend = Backend()
        backend.start_connection()
        corona_joined = backend.get_cube("corona_joined")
        county_cases = backend.get_cube("county_cases")
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


@app.route("/")
def send_index():
    return app.send_static_file("index.html")


@app.route("/<path:path>")
def send_file(path):
    return app.send_static_file(path)


if __name__ == "__main__":
    app.run()
