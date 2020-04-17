from flask import Flask, send_from_directory
import threading
import logging
import logging.handlers
from Backend import Backend
import sys
import datetime
import time


UPDATE_TIME = 3  # 3AM
HOST = "104-238-213-147.cloud-xip.io"

app = Flask(__name__, static_folder="web_app")
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


@app.route("/")
def index():
    return app.send_static_file('index.html')


@app.route('/js/<path:p>')
def send_js(p):
    return send_from_directory("web_app/js", p)


@app.route('/css/<path:p>')
def send_css(p):
    return send_from_directory("web_app/css", p)


@app.route("/api/map")
def get_map():
    logger.info("Get map ")
    return '<script src="https://cdn.bokeh.org/bokeh/release/bokeh-2.0.0.min.js"></script>' + js + div


def run_data_update():
    schedule = datetime.datetime.now()
    while True:
        if datetime.datetime.now() >= schedule:
            logger.info("Updating database.")
            global backend
            try:
                backend = Backend()
                backend.start_connection()
                backend.update_coronavirus_data()
                midnight_today = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
                schedule = midnight_today + datetime.timedelta(days=1, hours=UPDATE_TIME)
                logger.info("Update succeed. Scheduled for %s", schedule)
            except Exception as e:
                logger.error("Error updating database: %s", e)
        time.sleep(3600)


if __name__ == "__main__":
    try:
        backend = Backend()
        backend.start_connection()
        example_2d = backend.get_cube("example_2d", 1)
        js, div = example_2d.visualize()
    except Exception as e:
        logger.error("Error fetching database: %s", e)

    # creating thread
    t1 = threading.Thread(name="Database", target=run_data_update)
    if len(sys.argv) > 1 and sys.argv[1].lower() == "prod":
        t2 = threading.Thread(name="Server", target=lambda x: app.run(port=x, host=HOST), args=(80,))
    else:
        t2 = threading.Thread(name="Server", target=lambda x: app.run(port=x), args=(8080,))
    t1.start()
    t2.start()
